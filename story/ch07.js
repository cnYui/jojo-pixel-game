// 第七章区分泥偶、灯中本体、伪装调查和牙齿机关，避免把女教皇做成普通敌人。
'use strict';
(function () {
  const G = window.G, M = G.MID, T = G.TPL, W = G.world, I = G.input, px = G.px;
  const metal = ['pressure_gauge', 'valve', 'wrench', 'metal_cup', 'razor', 'binoculars', 'pipe_elbow', 'radio', 'diving_boot', 'oxygen_tank', 'compass', 'hatch_handle'];
  const labels = ['压力表', '阀门', '扳手', '金属杯', '剃刀', '望远镜', '弯管', '收音机', '潜水靴', '氧气瓶', '罗盘', '舱门把手'];
  // 同伴退到沙滩左边当观众（面朝右边的战斗）：原地留着会和泥偶、审判挤在灯旁边一小块地方，玩家前后被夹、没有地方周旋
  const SPECTATORS = { jotaro: [30, 152], joseph: [54, 149], kakyoin: [78, 153], polnareff: [102, 150] };
  const faceFight = c => { for (const a of G.party.members) if (a !== c.player && SPECTATORS[a.cid]) a.facing = 1; };
  async function judgement(S, lampProp) {
    S.mark('ch7_wishes');
    const wish = await S.choice(['让雪莉回来', '要一座金山', '让自己再强一点'], '三个愿望……先说哪一个？');
    const rows = wish === 0 ? [['polnareff', '雪莉……如果能再见你一面……'], [null, '泥土塑成了一张熟悉的面孔。']]
      : wish === 1 ? [['polnareff', '一座金山？……这也太夸张了！'], [null, '泥金散开，另一具泥偶站了起来。']]
        : [['polnareff', '另一个我？……这不是我的愿望！'], [null, '泥偶朝波鲁纳雷夫伸出了手。']];
    await M.lines(S, rows); await S.say('judgement', 'HAIL 2 U！愿望已经实现了！');
    // 灯神已经从灯里出来：探索时擦的那盏旧灯不再留在沙滩上（第二段另有一盏要打碎的灯，两盏同时在场分不清）
    if (lampProp) lampProp.remove = true;
    await M.objectFight(S, { id: 'b14a_judgement', lead: 'polnareff', swap: false, coverage: false, timer: {until:45,label:'坚持'},
      bench: { mode: 'stay', at: { jotaro: SPECTATORS.jotaro, joseph: SPECTATORS.joseph, kakyoin: SPECTATORS.kakyoin } },
      tick(c, dt) { const d = c.data;
        d.kneel = Math.max(0, d.kneel - dt);
        if (d.kneel > 0) { c.player.speed = 0; c.player.dmgIn = 1.5; c.player.play('kneel'); }
        else { c.player.speed = d.speed; c.player.dmgIn = 1; }
        if (c.t >= 45) c.end();
      }, testHint: c => ({ shaken: c.data.shaken, kneel: c.data.kneel })
    }, c => {
      c.data.shaken = 0; c.data.kneel = 0; c.data.speed=c.player.speed;
      // 玩家站在中间偏左、泥偶和审判都在右边：开场两边都有空地可以走位（以前三人挤在灯旁 x 390–430，第一秒就被前后夹击）
      c.player.x = 200; c.player.y = 162; c.player.facing = 1; faceFight(c);
      const mud = c.spawn({ cid: wish === 0 ? 'clay_sherry' : wish === 1 ? 'clay_gold' : 'clay_pol', kit: 'clay', x: 320, y: 162, hp: 9999, boss: true });
      c.spawn({ cid: 'judgement', x: 400, y: 156, hp: 9999, minHp: 9999 });
      c.on('hit', h => { if (h.t === mud && h.att === c.player) { c.data.shaken += 10;
        if (c.data.shaken >= 100) { c.data.shaken = 0; c.data.kneel = 3; S.word('动摇！', c.player); }
      } });
      M.ui(S, g => M.hud(g, ['动摇 ' + c.data.shaken + '%', '撑住 45 秒；泥偶是假的，别打它'], 40));
    });
    S.player.dmgIn = 1;
    await S.say('polnareff', '不是真的……可我还是下不了手……');
    const av = await S.join('avdol', { notice: false }); av.hp = av.maxHp; S.setLeader('avdol', { force: true });
    await T.fullbody3(S, { cid: 'avdol', behind: { cid: 'magred' }, aura: '#ff953f' });
    await M.lines(S, [['avdol', '波鲁纳雷夫！我回来了。'], ['polnareff', '阿布德尔？！你……还活着？！'], ['avdol', '后面再解释。先打碎那盏灯。']]);
    S.mark('b14b_judgement');
    await M.objectFight(S, { id: 'b14b_judgement', lead: 'avdol', swap: false, arena: [0, 480],
      bench: { mode: 'stay', at: SPECTATORS },
      tick(c) { if (c.data.body && (c.data.body.dead || c.data.body.hp <= 0)) c.end(); },
      testHint: c => ({ lampHits: c.data.lampHits, body: !!c.data.body })
    }, c => {
      c.data.lampHits = 0; c.data.body = null;
      c.player.x = 170; c.player.y = 160; c.player.facing = 1; faceFight(c);
      for (const [i, cid] of ['clay_sherry', 'clay_pol'].entries()) c.spawn({ cid, kit: 'clay', x: 250 + i * 80,
        y: 160, hp: 200, dmgMul: (a, p, m) => m.fire || p && p.cid === 'avdol' ? 2 : 1 });
      const lamp = c.spawn({ cid: 'prop:genie_lamp', id: 'judgement_lamp', x: 390, y: 164, hp: 9999, team: 'object' });
      lamp.breakable = { filter: () => false, onHit(s, b, info) {
        if (!['J3', 'rush', 'special'].includes(info.slot) || c.data.body) return;
        if (++c.data.lampHits >= 3) { lamp.remove = true; S.fx('shatter', { src: 'prop:genie_lamp', logical: 'idle', x: lamp.x, y: lamp.y });
          c.data.body = c.spawn({ cid: 'judgement', x: 350, y: 160, hp: 1000, boss: true });
          S.word('本体！', c.data.body);
        }
      } };
      M.ui(S, g => M.hud(g, c.data.body ? ['审判本体出现了！'] : ['神灯 ' + c.data.lampHits + '/3', '对灯用 J 三连第三下（火球）/ 连打 / U']));
    });
    await M.lines(S, [['avdol', '当时只是擦过头和胸口。养伤期间，我父亲帮忙隐瞒。'], ['polnareff', '……以后别再这样吓人了！']]);
  }
  async function disguises(S) {
    await M.scene(S, 'sub_ch7', st => { st.hotspots = metal.map((id, i) => M.hot('metal_' + i, 36 + i * 50, labels[i],
      ['detail', 'peek', 'life'], '普通的金属用品。', async s => { s.flags['metal_seen_' + i] = true; await s.say(null, labels[i] + '：看上去没有异常。'); }));
      st.hotspots.push(M.exit('dive', 620, '控制台', 'ch7Dive'));
    }, 36);
    const deco = metal.map((id, i) => M.prop(S, 'disguise_' + id, 36 + i * 50, 162));
    await M.explore(S, 'ch7Dive', 'E 预先观察十二件金属物品，右侧控制台 E 继续。');
    // 战斗里会在同样的位置生成 12 个可攻击的物件：探索用的摆设要先拿掉，不然真身“现形消失”和“眨眼”都被摆设挡住
    for (const a of deco) if (a) a.remove = true;
    W.stage.props=[];
    await S.say('joseph', '潜艇这次总安全了吧？……这杯子，刚刚眨了眼？'); S.mark('b15a_highpriestess');
    let penalty = false;
    // 同伴不做 AI 战友：他们会去打 12 个物件（可攻击的道具），把“打错扣 10 秒”和现形判定搅乱；留在原地当观众
    await M.objectFight(S, { id: 'b15a_highpriestess', lead: 'jotaro', swap: false, bench: 'stay',
      arena: [0, 640], coverage: false,
      tick(c, dt) { const d = c.data;
        if (!d.body) M.every(d, 'shift', dt, 5, () => { d.target = (d.target + 5) % 12; S.sfx('metal_scrape'); });
        M.every(d, 'hint', dt, 20, () => S.hint('阿布德尔：它在' + (36 + d.target * 50 > c.player.x ? '右边！' : '左边！'), 4));
        for (let i = 0; i < d.props.length; i++) d.props[i].frozen = !d.body && i === d.target && c.t % 1.5 < .22 ? 1 : 0;
        if (I.okHit()) { I.consumeOk(); const pick = Math.round((c.player.x - 36) / 50);
          if (pick >= 0 && pick < 12 && Math.abs(c.player.x - (36 + pick * 50)) < 24) {
            S.hint(labels[pick] + (pick === d.target && !d.body ? '……刚才眨了眼！面朝它按 J！' : '：暂时看不出破绽。'), 3);
          }
        }
        M.every(d, 'alarm', dt, 12, () => S.sfx('sub_alarm'));
        if (d.found >= 3 || c.t + d.penalty >= 90) { penalty = d.found < 3; c.end(); }
      }, testHint: c => ({ target: c.data.target, found: c.data.found, exposed: !!c.data.body, hits: c.data.hits, penalty: c.data.penalty, left: Math.max(0, 90 - c.t - c.data.penalty) })
    }, c => { Object.assign(c.data, { target: 3, found: 0, penalty: 0, props: [], body: null, hits: 0, strike: null });
      for (const [i, id] of metal.entries()) {
        const a = c.spawn({ cid: 'prop:disguise_' + id, x: 36 + i * 50, y: 164, team: 'object', hp: 9999 });
        c.data.props.push(a);
        a.breakable = { filter: () => false, onHit() {
          const d = c.data, p = c.player, strike = p.atk || p.rush;
          if (d.body || !strike || d.strike === strike) return;
          // 相邻物件间距小于拳头范围；一招只检查玩家面前最接近拳心的物件。
          const aim = p.x + p.facing * 30;
          const near = d.props.filter(o => (o.x - p.x) * p.facing >= -8).sort((u, v) => Math.abs(u.x - aim) - Math.abs(v.x - aim))[0];
          if (near !== a) return;
          d.strike = strike;
          if (i !== d.target) { d.penalty += 10; S.sfx('metal_crunch'); S.hint('打错了！艇体受损，少了十秒。', 3); return; }
          a.visible = false; d.hits = 0;
          d.body = c.spawn({ cid: 'highpriestess', kit: 'highpriestess', x: a.x, y: 164, hp: 9999 });
          S.word('现形！', d.body); S.hint('女教皇现形了！K / L 躲扑击，J 打中三下。', 4);
        } };
      }
      c.on('hit', h => { const d = c.data; if (h.t !== d.body || h.att !== c.player || h.dmg <= 0) return;
        if (++d.hits < 3) return;
        d.body.remove = true; d.body = null; d.found++; d.shift = 0; d.target = (d.target + 7) % 12;
        for (const a of d.props) a.visible = true;
        S.sfx('metal_scrape'); S.word('缩回去了！', c.player);
      });
      M.ui(S, g => M.hud(g, ['识破 ' + c.data.found + '/3　漏水 ' + Math.ceil(Math.max(0, 90 - c.t - c.data.penalty)) + ' 秒',
        c.data.body ? '现形了！再打中 ' + (3 - c.data.hits) + ' 下' : '盯住会眨眼的金属，面朝它按 J；E 只观察']));
    });
    await S.say('jotaro', '义手被咬住了。……还给你。');
    const ins = T.show(S, { bg: 'black', parts: [{ cid: 'prop:joseph_hand', x: 160, y: 120, scale: 3 }] });
    S.sfx('metal_crunch'); await S.wait(1); ins.close(); await S.crash(4, 5);
    await S.say('joseph', '第五次了……大家穿好潜水服！');
    await mouth(S, penalty);
  }
  async function mouth(S, penalty) {
    await M.scene(S, 'seabed_ch7', null, 200, 'jotaro');
    S.mark('b15b_highpriestess'); await S.say('jotaro', '坚硬如钻石？……那就一颗颗打碎。');
    await M.objectFight(S, { id: 'b15b_highpriestess', lead: 'jotaro', swap: false, coverage: false,
      tick(c, dt) { const d = c.data;
        d.oxygen = Math.max(0, d.oxygen - dt); c.player.x = Math.max(8, c.player.x - 40 * dt);
        M.every(d, 'bite', dt, 2.5, () => c.hazard({ shape: 'rect', x0: 0, x1: 320, y0: 145, y1: 176,
          warn: 45 / 60, dur: .12, dmg: 20, once: true, guard: 'normal', parry: true, tag: 'upper_bite', sfx: 'teeth_crunch' }));
        d.broken = d.teeth.filter(a => a.dead || a.hp <= 0).length;
        if (d.broken === 12) c.end();
        else if (d.oxygen <= 0) c.fail('氧气耗尽了……再来一次。');
      }, testHint: c => ({ broken: c.data.broken, oxygen: c.data.oxygen })
    }, c => {
      Object.assign(c.data, { oxygen: 120, broken: 0, teeth: [] }); if (penalty) c.player.hp -= 20;
      for (let i = 0; i < 12; i++) { const upper = i < 6, x = 36 + (i % 6) * 48;
        const a = c.spawn({ cid: upper ? 'prop:upper_tooth' : 'prop:lower_tooth', id: 'tooth_' + i, x, y: 164,
          hp: 80, team: 'object', z: upper ? 64 : 0 });
        a.breakable = { anim:'idle',frames:[0,1],upward: upper, filter: m => !upper && ['J3', 'rush', 'special'].includes(m.slot) };
        c.data.teeth.push(a);
      }
      c.on('parry', h => { if (h.move && h.move.tag === 'upper_bite' && !c.data.cine) M.task(c, async () => {
        const t = c.data.teeth.slice(0, 6).filter(a => a.hp > 0).sort((a, b) => Math.abs(a.x - c.player.x) - Math.abs(b.x - c.player.x))[0];
        const ok = await S.timing({ label: '顶住上颚，J 击碎牙齿！', zone: [.38, .62], limit: 3 });
        if (ok && t) M.toothHit(c, t); else M.drain(c, 20);
      }); });
      M.ui(S, g => M.hud(g, ['牙齿 ' + c.data.broken + '/12　氧气 ' + Math.ceil(c.data.oxygen) + ' 秒',
        '上排：咬下来那一刻按 L 顶住，再按 J', '下排：J 三连第三下 / 连打 / U']));
      M.pixel('mouth_ceiling', (P) => { px.rect(P, 0, 64, 320, 10, '#795353'); });
      M.pixel('dive_helmets', P => {
        for (const a of W.stage.actors) if (['jotaro', 'joseph', 'avdol', 'kakyoin', 'polnareff'].includes(a.cid) && !a.remove && a.visible !== false)
          px.blitFrame(P, 'prop:dive_helmet', 'idle', 0, a.x - G.cam.x, a.headY() + 14 - G.cam.y);
      });
    });
    S.sfx('water_splash'); await M.scene(S, 'coast_ch7');
    await S.say(null, '女教皇再起不能。岸边只留下背影。'); S.spawn('midler_back', 270, 164, { facing: -1 });
    // 潜艇图标开到 42% 沉没（规划照分镜 s11）；地图图标名是 map_sub
    await S.route(['红海', '阿斯旺'], { vehicle: 'sub', cut: .42, day: 29, left: 22 });
    await S.say('joseph', '第29天。终于到了埃及。Holly，等着我们。');
  }
  G.STORY.ch7 = async S => {
    await M.ensureBg('_ch7');
    S.party(M.crew, { leader: 'polnareff' }); await M.scene(S, 'island_ch7', st => {
      st.npcs = [M.npc('npc_islander', 'islander', 110, '岛民', '小屋里住着一个老人。先别打扰他。')];
      st.hotspots = [M.hot('crab', 190, '螃蟹', ['detail', 'cut'], '螃蟹横着走远了。'),
        M.hot('hut', 330, '小屋', ['life', 'peek'], '屋里有人。'),
        M.hot('lamp', 410, '旧灯', ['cut'], '一盏旧灯。', async s => { s.flags.ch7Lamp = true; s.sfx('metal_scrape'); })];
    }); await S.chapterCard('ch7'); const lamp = M.prop(S, 'genie_lamp', 410);
    await M.explore(S, 'ch7Lamp', 'E 和岛民搭话、观察小屋；到右边擦灯。');
    await judgement(S, lamp); await disguises(S); await M.end(S, 'ch7_complete');
  };
})();
