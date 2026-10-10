// 妖刀跨三战记招，磁力用双人夹击，影子战用真实藏点与背向伏击。
'use strict';
(function () {
  const G = window.G, M = G.MID, T = G.TPL, W = G.world, I = G.input;
  const crew = ['jotaro', 'joseph', 'avdol', 'polnareff', 'iggy'];
  async function anubis(S) {
    const memory = [];
    await M.scene(S, 'temple_ch9', st => {
      // 图集里没有 npc_guide / npc_tourist / npc_fisherman：借现成的路人图（名牌照旧写导游 / 游客 / 渔夫）
      st.npcs = [M.npc('npc_merchant', 'guide', 120, '导游', '这里是科翁坡神殿。请不要碰旧刀架。'), M.npc('npc_hk_passer_b', 'tourist', 330, '游客', '壁画里的神，手里拿着什么？')];
      st.hotspots = [M.hot('hieroglyph', 240, '壁画', ['life', 'detail'], '阿努比斯，死者的守护神。'),
        M.hot('sword_rack', 410, '旧刀架', ['nensha', 'scent'], '照片里，有一个刀匠的背影。'), M.exit('deeper', 610, '神殿深处', 'ch9Temple')];
    }, 50); M.prop(S, 'anubis_sword', 410);
    await M.explore(S, 'ch9Temple', '调查壁画 / 旧刀架，神殿右侧 E。');
    S.setLeader('polnareff', { force: true }); await S.say('polnareff', '我去去就来！'); await S.say('chaka', '这把刀……在对我说话。');
    S.mark('b18a_anubis');
    await S.fight({ id: 'b18a_anubis', lead: 'polnareff', swap: false, arena: [0, 640], energy: { start: 100 },
      waves: [[{ cid: 'chaka', x: 490, y: 164, hp: 900, poiseMax: 60, boss: true }]],
      kitOverride: { polnareff: { special: { need: 0, prompt: 'U 射出剑身：它没见过这一招！', window: c => c.boss && c.boss.hp <= 135,
        async run(s, p, c) { const e = c.boss; if (!e) return; s.sfx('stab'); s.fx('slash_arc', { x: e.x, y: e.y - 22, size: 28 });
          G.combat.hit(p, e, { dmg: 120, slot: 'special', unseen: true, guard: 'none', reach: [0, 999], push: 12 }); } } } },
      onWave(s, i, enemies, attempt, c) { c.data.memory = memory; c.player.x = 110;
        c.on('parry', h => { if (h.who === c.player) c.player.mem.anubisCounterUntil = c.t + 1; });
        M.ui(s, g => M.hud(g, ['刀记住的招：' + (memory.join(' / ') || '无'), '同一种招第二次会被挡开反击——换着用']));
},
      testHint: c => ({ memory: c.data.memory, projectile: c.boss && c.boss.hp <= 135 })
    }); S.insertUI(null);
    await S.say('polnareff', '把刀扔进河里，再也不会有人碰它了。'); S.sfx('splash');
    await M.scene(S, 'nile_ch9', st => {
      st.npcs = [M.npc('khan', 'barber', 260, '理发师卡恩', '客人，要不要修修鬓角？'), M.npc('npc_sailor', 'fisher', 450, '渔夫', '刚捞起一把很漂亮的刀。')];
      st.hotspots = [M.hot('river', 150, '尼罗河', ['detail', 'nensha', 'cut'], '扔下去的刀，应该沉底了吧。'), M.exit('barbershop', 610, '理发摊', 'ch9Barber')];
    }, 60, 'jotaro'); await M.explore(S, 'ch9Barber', 'E 理发 / 和渔夫搭话，到右侧理发摊 E。');
    await S.say('khan', '上一场的招式……我都记得！'); S.mark('b18b_anubis');
    await S.fight({ id: 'b18b_anubis', lead: 'jotaro', swap: false, arena: [0, 640], energy: { start: 100 },
      waves: [[{ cid: 'khan', x: 480, y: 164, hp: 1200, poiseMax: 70, boss: true }]],
      onWave(s, i, enemies, attempt, c) { c.data.memory = memory; c.player.x = 100; const e = enemies[0], base = e.speed; let hits = 0;
        c.on('parry', h => { if (h.who === c.player) c.player.mem.anubisCounterUntil = c.t + 1; });
        c.on('hit', h => { if (h.t === e && h.dmg > 0) { hits++; e.speed = base * (1 + Math.min(.5, hits * .05)); } });
        M.ui(s, g => M.hud(g, ['刀记住的招：' + (memory.join(' / ') || '无'), '卡恩每挨一下快 5%（已 +' + Math.round((e.speed / base - 1) * 100) + '%）：速战速决']));
},
      testHint: c => ({ memory: c.data.memory, speed: c.boss && c.boss.speed })
    }); S.insertUI(null);
    await M.lines(S, [['polnareff', '这把刀……我来收拾。'], ['jotaro', '别碰！……已经晚了。']]); S.mark('b18c_anubis');
    await S.fight({ id: 'b18c_anubis', lead: 'jotaro', swap: false, arena: [0, 640], energy: { start: 100 },
      waves: [[{ cid: 'polnareff_possessed', x: 430, y: 162, hp: 1400, minHp: 280, poiseMax: 80, boss: true, stand: 'chariot' }]],
      onWave(s, i, enemies, attempt, c) { c.data.memory = memory; c.player.x = 110;
        c.on('parry', h => { if (h.who === c.player) c.player.mem.anubisCounterUntil = c.t + 1; });
        M.ui(s, g => M.hud(g, ['他是同伴，打不倒：等紫色突刺', '刺到的那一刻按 L 用身体夹住刀，再连按 J']));
},
      testHint: c => ({ memory: c.data.memory, bladeBusy: !!c.data.bladeBusy })
    }); S.insertUI(null);
    await M.lines(S, [[null, '碎片落到一个小孩身边。伊奇从他脚边穿过。'], ['polnareff', '……我又一个人行动了，对吧。']]);
    S.sfx('dog_bark'); S.sfx('splash');
  }
  async function magnet(S) {
    S.party(['joseph', 'avdol'], { leader: 'joseph' }); await M.scene(S, 'rail_ch9', null, 100);
    await M.lines(S, [['joseph', '撤退！逃跑是乔斯达家的传统战术！'], ['avdol', '脚被磁力吸住了。分站她的两边！']]); S.mark('b19_bast');
    await M.objectFight(S, { id: 'b19_bast', lead: 'joseph', swap: true, allies: ['avdol'], arena: [0, 640],
      music: 'battle', kitOverride: Object.fromEntries(['joseph', 'avdol'].map(cid => [cid, { chords: { 'attack+guard': 'JA_MAGNET_CLAP' } }])),
      testHint: c => ({ magnets: c.data.magnets, stuck: c.data.stuck, train: c.data.train, clap: c.data.clap }),
      tick(c, dt) {
        const d = c.data, p = c.player, mate = G.party.get(p.cid === 'joseph' ? 'avdol' : 'joseph'), e = d.boss;
        for (const cid of ['joseph', 'avdol']) d.magnets[cid] = Math.min(100, d.magnets[cid] + dt * 100 / 60);
        d.stuck = Math.abs(p.x - mate.x) < 40;
        p.speed = d.speeds[p.cid] * (d.stuck ? .7 : 1); mate.speed = d.speeds[mate.cid] * (d.stuck ? .7 : 1);
        // 同伴走向另一侧才能形成可操作的夹击；普通近战 AI 会把两人永远挤在同一边。
        if (mate.hp > 0 && !mate.atk && !mate.tele) {
          const target = e.x + (p.x < e.x ? 1 : -1) * 48;
          mate.hold = true; W.move(mate, G.clamp(target - mate.x, -mate.speed * dt, mate.speed * dt), (p.y - mate.y) * dt * 2);
          mate.facing = e.x > mate.x ? 1 : -1; mate.play('walk');
        }
        if (d.stuck) { const delta = (p.x - mate.x) * dt * .8; W.move(p, -delta, 0); W.move(mate, delta, 0); }
        M.every(d, 'junkT', dt, .8, () => {
          for (const a of [p, mate]) { const mag = d.magnets[a.cid]; if (mag < 10) continue;
            const side = Math.sin(c.t * 2 + a.uid) > 0 ? 1 : -1;
            c.shoot(e, { kind: 'img', image: { cid: 'prop:metal_junk', logical: 'idle' }, x: a.x + side * 95, y: a.y,
              vx: -side * mag * 120, vy: 0, dmg: 3 + Math.floor(mag / 34), slot: 'enemy', life: 1.5, guard: 'normal' }); }
        });
        M.every(d, 'socketT', dt, 3, () => {
          d.socket = { at: c.t + .5, x: e.x, y: p.y, sign: p.x < e.x ? -1 : 1 };
          S.fx('warn_line', { pts: [[e.x, p.y], [e.x + d.socket.sign * 200, p.y]], dur: .5, colour: '#ffd45a' });
        });
        if (d.socket && c.t >= d.socket.at) {
          const q = d.socket; d.socket = null;
          c.shoot(e, { kind: 'img', image: { cid: 'prop:socket', logical: 'idle' }, x: q.x, y: q.y, vx: q.sign * 180,
            dmg: 1, life: 3, guard: 'normal', onHit(shot, a) { if (d.magnets[a.cid] != null) d.magnets[a.cid] = Math.min(100, d.magnets[a.cid] + 15); } });
        }
        d.train = c.t % 15;
        if (d.train >= 13.5 && !d.trainWarn) { d.trainWarn = true; S.sfx('train_horn'); S.shake(1, 1.5);
          c.hazard({ shape: 'rect', x0: 0, x1: 640, y0: 164, y1: 172, warn: 1.5, dur: .45,
            dmg: 40, once: true, guard: 'none', fxActive: 'train_pass' }); }
        if (d.train < 1) d.trainWarn = false;
        M.every(d, 'hintT', dt, 20, () => { S.hint((mate.cid === 'avdol' ? '阿布德尔：' : '乔瑟夫：') + (e.x > p.x ? '她在右边！ →' : '← 她在左边！'), 3); });
        d.clap = e.hp <= e.maxHp * .5 && (p.x - e.x) * (mate.x - e.x) < 0 && Math.abs(p.x - mate.x) <= 120 && Math.abs((p.x + mate.x) / 2 - e.x) <= 10;
        if (d.clap && !d.prompt) { d.prompt = true; S.hint('现在！J＋L 合击！', 4); } if (!d.clap) d.prompt = false;
      }
    }, c => {
      const a = G.party.get('avdol'); c.player.x = 100; c.player.y = 155; a.x = 220; a.y = 155;
      Object.assign(c.data, { magnets: { joseph: 0, avdol: 0 }, stuck: false, train: 0, trainWarn: false,
        speeds: { joseph: G.party.get('joseph').speed, avdol: a.speed }, clap: false });
      c.data.boss = c.spawn({ cid: 'mariah', x: 400, y: 155, boss: true, hp: 1300, minHp: 650, poiseMax: 60 });
      M.ui(S, g => M.hud(g, ['磁化　乔瑟夫 ' + Math.floor(c.data.magnets.joseph) + '%　阿布德尔 ' + Math.floor(c.data.magnets.avdol) + '%',
        c.data.clap ? '现在！J＋L 一起按，两人把她夹住！' : '打到半血后两人分站她左右，J＋L 合击', '火车来时离开铁轨（Q 换人）']));
    });
    for (const a of G.party.members) a.hold = false;
    await M.lines(S, [['mariah', '怎么可能……把我的磁力反过来……'], ['joseph', '脚终于听使唤了！']]);
  }
  const hides = [
    ['wardrobe', 'hide_wardrobe', '衣柜', 155, 144], ['aquarium', 'aquarium', '鱼缸', 249, 144],
    ['bed', 'hide_bed', '床底', 418, 144], ['curtain', 'hide_curtain', '窗帘', 58, 112],
    ['crate', 'hide_crate', '木箱', 506, 144], ['cupboard', 'hide_cupboard', '橱柜', 570, 144]
  ];
  async function seth(S) {
    await S.say(null, '同一时间，波鲁纳雷夫踩进了擦窗人的影子。');
    S.party(['jotaro', 'polnareff'], { leader: 'polnareff' }); await M.scene(S, 'house_ch9', null, 180);
    await S.say('alessi', '了、了不起哟……现在还敢打吗？');
    const oldParty = G.party.members.slice(), oldPlayer = W.player;
    try {
      S.setPlayer('polnareff_kid', { hp: 100, speed: 70, x: 180, y: 158, kit: 'polnareff_kid' }); S.mark('b20a_seth');
      await M.objectFight(S, { id: 'b20a_seth', swap: false, bench: 'hide', arena: [0, 640], coverage: false, music: 'tension',
        testHint: c => ({ hidden: c.data.hidden, ambush: c.data.ambush, age: c.data.age, search: c.data.search }),
        tick(c, dt) {
          const d = c.data, p = c.player, e = d.boss;
          const shadow = (p.x - e.x) * e.facing < 0 && Math.abs(p.x - e.x) < 40 + (Math.sin(c.t) + 1) * 25;
          if (shadow) d.age = Math.max(7, d.age - dt * 5);
          if (I.okHit()) { I.consumeOk(); const h = hides.find(z => Math.abs(z[3] - p.x) < 27);
            if (h) { d.hidden = d.hidden === h[0] ? null : h[0]; if (d.hidden) { p.x = h[3]; p.y = 158; } }
          }
          p.alpha = d.hidden ? .25 : 1; p.speed = d.hidden ? 0 : 70;
          for (const [i, h] of hides.entries()) d.furniture[i].frozen = d.hidden === h[0] ? 1 : 0;
          d.clock += dt;
          if (d.clock >= 3.5) { d.clock = 0; d.search = (d.search + 1) % hides.length; d.chopped = false; }
          const target = hides[d.search], delta = target[3] - e.x;
          if (Math.abs(delta) > 12) { e.facing = Math.sign(delta); W.move(e, Math.sign(delta) * 38 * dt, 0); e.play('walk'); }
          else if (!d.chopped) {
            d.chopped = true; e.play('axe');
            c.hazard({ shape: 'rect', x0: target[3] - 24, x1: target[3] + 24, y0: 145, y1: 178,
              warn: 45 / 60, dur: .12, dmg: 16, once: true, guard: 'none', sfx: 'axe_chop',
              onHit() { S.flash(2 / 60, 1, '#ffffff'); S.sfx('thud'); d.hidden = null; } });
          }
          if (d.ambush >= 2) c.end();
        }
      }, c => {
        Object.assign(c.data, { hidden: null, ambush: 0, age: 9, search: 0, clock: 0, chopped: false, furniture: [] });
        c.player.x = 180; c.player.y = 158; c.player.alpha = 1;
        c.data.boss = c.spawn({ cid: 'alessi', x: 480, y: 158, boss: true, hp: 1300, minHp: 1000, brain: () => true });
        for (const h of hides) c.data.furniture.push(c.spawn({ cid: 'prop:' + h[1], x: h[3], y: h[4], team: 'object', untargetable: true }));
        M.pixel('seth_shadow', P => { const e = c.data.boss, x = e.x - G.cam.x, len = 40 + (Math.sin(c.t) + 1) * 25;
          G.px.poly(P, [[x - 6, 160], [x + 6, 160], [x - e.facing * len, 171], [x - e.facing * len - 12, 164]], '#16101e', .65); });
        M.ui(S, g => M.hud(g, ['年龄 ' + Math.ceil(c.data.age) + ' 岁　伏击 ' + c.data.ambush + '/2',
          c.data.hidden ? '躲好了：等他背对你走近，K＋J 偷袭！' : 'E 躲进藏身处（鱼缸最好），避开他的斧头']));
      });
      await S.say(null, '另一边，承太郎也变成了小学生。');
      S.setPlayer('jotaro_kid', { hp: 130, speed: 64, x: 130, y: 158, kit: 'jotaro_kid' }); S.mark('b20b_seth');
      await M.objectFight(S, { id: 'b20b_seth', swap: false, bench: 'hide', arena: [0, 640], music: 'battle',
        testHint: c => ({ age: c.data.age, begged: c.data.begged, hp: c.data.boss.hp }),
        tick(c, dt) {
          const d = c.data, p = c.player, e = d.boss;
          if ((p.x - e.x) * e.facing < 0 && Math.abs(p.x - e.x) < 80) d.age = Math.max(7, d.age - dt * 5);
          if (e.hp <= 700 && !d.begged && !d.cine) { d.begged = true; M.task(c, async () => {
            e.play('beg'); const pick = await S.choice(['不信', '相信他'], '饶了我……我不会再做坏事了！');
            if (pick === 1) { S.flash(2 / 60, 1, '#ffffff'); M.drain(c, 16); S.sfx('thud'); }
            await S.say(null, '小承太郎握紧了拳头。');
          }); }
          if (e.hp <= 390) c.end();
        }
      }, c => { c.player.x = 130; c.player.y = 158; c.player.alpha = 1;
        Object.assign(c.data, { age: 9, begged: false });
        c.data.boss = c.spawn({ cid: 'alessi', x: 400, y: 158, hp: 1300, boss: true, minHp: 390 }); c.data.boss.hp = 1000;
        M.ui(S, g => M.hud(g, ['小学生承太郎：没有替身也照样揍人', 'J 三连，K 闪开斧头；别站进他的影子']));
      });
    } finally {
      if (W.player && !oldParty.includes(W.player)) W.player.remove = true;
      for (const a of oldParty) { a.visible = true; a.remove = false; a.alpha = 1; a.hold = false; }
      W.player = oldPlayer; S.party(['jotaro', 'polnareff'], { leader: 'jotaro' });
    }
    await M.lines(S, [['polnareff', '恢复了！承太郎！'], ['jotaro', '欧拉。'], ['alessi', '了、了不起哟……！']]);
    S.sfx('ora_rush'); S.sfx('slash'); S.fx('rush', { x: 210, y: 140, fist: 'starplat', dur: 1 }); await S.wait(1);
  }
  G.STORY.ch9 = async S => {
    // 篇章卡 → 地图（科翁坡在世界地图上没有城市名，用阿斯旺北边一点的坐标）→ 神殿
    await M.ensureBg('_ch9'); S.party(crew, { leader: 'jotaro' });
    await S.chapterCard('ch9'); await S.route(['阿斯旺', [46, 78]], { vehicle: 'car', day: 32, left: 19 }); await anubis(S);
    await M.scene(S, 'luxor_ch9', st => {
      st.npcs = [M.npc('mariah', 'socket_seller', 420, '卖插座的女人', '试试这只插座？很特别哦。'), M.npc('alessi', 'window_cleaner', 720, '擦窗工人', '小孩子……咳，今天天气真好。')];
      st.hotspots = [M.hot('socket', 470, '墙上插座', ['detail', 'nensha'], '位置很突兀的插座。', async (s, h, p) => {
        if (p.cid === 'joseph') { s.flags.ch9Socket = true; s.sfx('magnet_clack'); } else await s.say(p.cid === 'iggy' ? null : p.cid, '乔瑟夫去看看这只插座。');
      }), M.hot('long_shadow', 720, '长影子', ['detail', 'scent'], '擦窗人的影子，比本人长得多。')];
    }, 55); M.prop(S, 'socket', 470);
    await M.explore(S, 'ch9Socket', '乔瑟夫 E 碰插座；承太郎 U 调查长影子。');
    await magnet(S); await seth(S); S.party(crew, { leader: 'jotaro' });
    await S.route(['卢克索', '开罗'], { vehicle: 'car', day: 35, left: 16 }); await M.end(S, 'ch9_complete');
  };
})();
