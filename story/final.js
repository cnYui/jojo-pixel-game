// 终章　DIO 的世界 / 直到黎明（照游玩脚本 `fin_终章.md` + 实施文档 `09_终章.md` 整章重写）
//   初版的机关写法沿用：楼梯（台阶读 @steps）、卡车逃亡（L.runner 的骨架改成三条车道 + 绿宝石）、
//   布网 / 钟面瞄准、传讯息、时停（stopDio / stopTick）、手指动了（startGrowth / growthTick）、
//   装死（canPlayDead / playDead）、压路机（roadroller）、最终对冲（finalClash）、DIO 三段（dioFight）。
//   这一版按脚本补齐：出馆分头、黎明自由走动、荷莉、机场自由走动、告别与片尾；台词逐字照脚本。
//   过场一律在场景里演（不再用黑底 L.view 插画），坐标全部从背景导出的 anchors 取（缺了才用默认值）。
//
//   流程：篇章卡 → 大楼梯（F-02）→ 出馆分头（F-03）→ 卡车逃亡（F-04）→ 屋顶布网（F-05）
//   → 传讯息（F-06）→ 对走（F-07）→ DIO 段 1/2/3（F-08~F-10）→ 终结（F-11）
//   → 黎明过场 + 自由走动（F-12）→ 荷莉（F-13）→ 机场过场 + 自由走动（F-14）→ 告别（F-15）→ 片尾
'use strict';
(function () {
  const G = window.G, W = G.world, S = G.S, L = G.LATE, T = G.TPL, M = G.MID, X = G.EXTRA;
  G.TRIAL_SRC = G.TRIAL_SRC || {};   // 星尘试炼的关卡工厂（本文件末尾登记）
  const F = () => G.flags, I = G.input;
  const fallen = ['avdol', 'iggy'];
  function party(active, leader, lost = fallen) { S.party([...active, ...lost], { leader }); lost.forEach(cid => S.leave(cid)); }
  // 新合成的音效还没进数据包时用现成的顶上（直接播不存在的名字会记 missingSfx）
  const hasSnd = n => !!(G.audio && G.audio.has && G.audio.has(n));
  const snd = (n, alt, o = {}) => { if (hasSnd(n)) G.audio.sfx(n, o); else if (alt) G.audio.sfx(alt, o); };

  // ---------------------------------------------------------------- 背景锚点（没有就用实施文档里的默认值）
  const DEF = {
    mansion_stairs: { steps: [[40, 160], [52, 154], [64, 148], [76, 142], [88, 136], [100, 130], [112, 124], [124, 118],
      [136, 112], [148, 106], [160, 100], [172, 94], [184, 88], [196, 82], [208, 76]],
    bottom: [18, 166], top: [266, 76], landing: [214, 76], moon_window: [236, 40], wall_break: [300, 140], exit: [267, 76] },
    cairo_street_night: { arrive: [40, 164], hotel_windows: [[265, 99], [287, 99], [309, 99], [331, 99]], truck_lot: [120, 164],
      senator_stop: [760, 162], lanes: [154, 163, 172], road_sign: [580, 150], alley: [700, 152], corner: [860, 150],
      crossroad: [640, 162], fruit_stand: [470, 160], exit: [940, 162], lane_back: 146, curb: 153, truck_crash: [862, 146] },
    cairo_street_dawn: { arrive: [40, 164], hotel_windows: [[265, 99], [287, 99], [309, 99], [331, 99]], truck_lot: [120, 164],
      senator_stop: [760, 162], lanes: [154, 163, 172], road_sign: [580, 150], alley: [700, 152], corner: [860, 150],
      crossroad: [640, 162], fruit_stand: [470, 160], exit: [940, 162], lane_back: 146, curb: 153, clock_tower: [300, 40] },
    cairo_rooftops: { arrive: [40, 160], nodes: [[58, 117], [118, 92], [204, 111], [262, 88], [334, 133], [380, 116], [452, 120], [560, 100]],
      clock: [155, 105], clock_face: [155, 105, 7], chimney: [380, 118], tank: [492, 146], edge: [620, 150], dio_air: [320, 90] },
    kujo_bedroom_morning: { bed: [193, 153], window: [209, 74], door: [30, 156], arrive: [60, 164] },
    airport: { arrive: [40, 164], board: [96, 84], benches: [[140, 162], [200, 162]], window: [180, 80], plane_door: [238, 112],
      gate: [276, 156], gate_paris: [24, 156] },
  };
  const A = (bg, k) => {
    const b = G.D && G.D.bg && G.D.bg[bg];
    const v = b && b.anchors ? b.anchors[k] : null;
    return v != null ? v : (DEF[bg] || {})[k];
  };
  // 背景里的物件锚点有时给的是物件底（比可走带高 / 低），站人前先夹进可走带
  const footY = (stage, y) => { const st = G.STAGES[stage]; return G.clamp(y, st.yMin + 2, st.yMax - 2); };
  const at = (stage, bg, k) => { const v = A(bg, k); return [v[0], footY(stage, v[1])]; };

  function place(S, cid, x, y = 164, facing = 1) {
    const a = S.actor(cid); if (!a) return null;
    a.visible = true; a.follow = null; a.x = x; a.y = y; a.facing = facing; a.alpha = 1; a.scale = 1; S.unpose(a);
    return a;
  }
  function act(a, anim, ms) {
    if (!a) return;
    a.hold = true; a.frozen = null; a.play(anim, { restart: true });
    G.defer((ms || 600) / 1000, () => { if (a && !a.remove) { a.hold = false; a.play(a.idleAnim || 'idle'); } }, 'world');
  }

  // ---------------------------------------------------------------- 纪念品（story\extras.js）
  X.souvenir({ id: 'fin_clock_hand', chapter: 'final', name: '钟楼的指针', desc: '花京院最后打碎的那面钟上的指针。它停在了时间被看穿的那一刻。', hint: '剧情获得' });
  X.souvenir({ id: 'fin_road_sign_bolt', chapter: 'final', name: '路牌上的螺丝', desc: '那块路牌被拔走以后，留在坑边的一颗螺丝。', hint: '黎明的开罗街，路牌原来的地方' });
  X.souvenir({ id: 'fin_boarding_pass', chapter: 'final', name: '飞往东京的登机牌', desc: '开罗 → 东京。……五十天的旅程，到这里结束。', hint: '开罗机场的长椅（要眼力好的人）' });

  // ================================================================ F-02　28A 大楼梯
  async function stairs() {
    const st = 'stairs_fin', bg = 'mansion_stairs';
    const steps = A(bg, 'steps'), bottom = A(bg, 'bottom'), landing = A(bg, 'landing'), wall = A(bg, 'wall_break');
    party(['jotaro', 'joseph', 'kakyoin', 'polnareff'], 'polnareff');
    await S.setStage(st, { x: bottom[0], y: footY(st, bottom[1]), music: 'ominous' });
    S.state('wall_broken', 0);
    // DIO 站在平台上、逆光剪影：alpha .7，背后大窗里是一轮满月（背景画好了）。
    //   @landing 的 y（76）在可走带（146–174）上方：这里不能走 footY，夹进可走带他就站到楼下的地板上了（玩家反馈“DIO 在最下面”）
    const dio = S.spawn('dio', landing[0], landing[1], { id: 'fin_dio', team: 'npc', label: 'DIO' });
    if (dio) { dio.alpha = .7; dio.facing = -1; dio.hold = true; dio.play('idle'); }
    S.mark('fin_stairs');
    await S.say('polnareff', '……DIO！你终于肯露面了！');
    await S.say('dio', '波鲁纳雷夫……再上一步，就到我这边来了。');

    const barks = ['你妹妹的仇，你已经报了。……那么，你现在为了什么而战？', '站在我这边，你就再也不用失去任何人。',
      '累了吧？……在我身边，可以安心地休息。', '来吧。只要再上一级。'];
    const q = { type: 'stairs', step: 0, resets: 0, flash: 0, acc: 0, touch: { buttons: ['pad'], captions: {} } };
    const me = W.player; if (me) me.visible = false;
    try {
      await L.game(S, q, (s, dt) => {
        s.flash = Math.max(0, s.flash - dt);
        if (I.isDown('right') || I.isDown('up')) s.acc += dt; else s.acc = 0;
        if (s.acc >= .18) {
          s.acc = 0; s.step++; S.sfx('footstep0');
          // 第 2 / 4 / 6 / 8 级各一句：用 bark，不停下玩家的操作
          if (s.step % 2 === 0 && s.step <= 8) S.bark('dio', barks[s.step / 2 - 1], { dur: 1.6 });
        }
        if (s.step >= 10) {
          // 第 10 级：咋瓦鲁多不预警——只去色一眨眼、很轻的一声，人已经回到楼下
          s.resets++; s.step = 0; s.flash = .1;
          S.filter('gray', 1); G.defer(.12, () => S.filter('gray', null), 'world');
          snd('timestop_hum', null, { vol: .25 });
          G.dbg.ev('fin_stairs_stop', { n: s.resets });
          if (s.resets === 1) S.bark('dio', '……怎么了？你不是在上楼吗？', { dur: 1.6 });
          if (s.resets >= 2) { s.done = true; s.win = true; }
        }
      }, (g, s) => {
        T.drawBg(g, bg, s.t);
        const p = steps[Math.min(s.step, steps.length - 1)];
        T.sprite(g, 'polnareff', 'walk', Math.floor(s.t * 8) % 4, p[0], p[1]);
        T.sprite(g, 'dio', 'idle', 0, landing[0], landing[1], { alpha: .7, flip: true });
        if (s.flash > 0) { g.fillStyle = '#9a9ca4aa'; g.fillRect(0, 0, 320, 180); }
      }, (g, s) => L.label(g, '爬上楼梯　' + s.step + ' / 15', '按住 → 或 ↑ 往上爬'));
    } finally {
      if (me) { me.visible = true; me.x = bottom[0]; me.y = footY(st, bottom[1]); me.play('idle'); }
    }

    S.mark('fin_pol_shock');
    await T.closeup4(S, { cid: 'polnareff', expr: 'shock', bg: 'menace' });
    await S.say('polnareff', '我刚才明明在上楼梯，回过神来却在下楼……');
    await S.say('polnareff', '催眠术？超高速？……不对，那种东西根本不是这个层次……');
    await S.say('dio', '再给你一次机会。上来吧，波鲁纳雷夫。');
    await S.summon('polnareff', { dur: .2 });
    await S.say('polnareff', '我的剑……不会对着我的伙伴！');

    // 破墙：三人从洞口冲进来。@wall_break 的 y（140）在可走带外，落点取可走带顶（150）
    S.mark('fin_wall_break');
    S.state('wall_broken', 1); S.sfx('crash'); S.shake(4, .4);
    S.fx('crack', { x: wall[0], y: wall[1] }, { life: 1.4 });
    for (let n = 0; n < 24; n++) S.fx('dust', { x: wall[0] - 4 + (n % 6) * 3, y: wall[1] + (n % 4) * 4, size: 5 }, { life: .8 });
    const inY = footY(st, 150);
    for (const [cid, dx] of [['jotaro', 0], ['joseph', 14], ['kakyoin', 28]]) place(S, cid, wall[0] - 20 + dx, inY, -1);
    await S.say('jotaro', '……波鲁纳雷夫。');
    await S.say('joseph', 'DIO！');
    await S.say('dio', '……人都到齐了。也好。');
    if (dio) await S.animate(1, k => { dio.alpha = .7 * (1 - k); });
    if (dio) { dio.visible = false; dio.remove = true; }
    await S.say('kakyoin', '……他去外面了。窗户！');
  }

  // ================================================================ F-03　出馆 · 分头
  async function escape() {
    const st = 'chase_fin', bg = 'cairo_street_night';
    const win = A(bg, 'hotel_windows'), lot = A(bg, 'truck_lot'), stop = A(bg, 'senator_stop');
    // 这一段镜头跟着承太郎走（楼梯那边队长是波鲁纳雷夫）
    party(['jotaro', 'joseph', 'kakyoin', 'polnareff'], 'jotaro');
    await S.setStage(st, { x: lot[0] + 60, y: footY(st, 164), music: 'tension' });
    S.state('crashed', 0); S.state('stand_wrecked', 0); S.state('scroll', 0);
    const ground = footY(st, 164);
    // 四人从旅馆二楼的四扇窗翻下来（窗脚 y 99 → 街面 y 164，0.5 s），落地后走到卡车一带站定
    const crew = [['jotaro', 0, 80], ['joseph', 1, 40], ['kakyoin', 2, 60], ['polnareff', 3, 100]];
    for (const [cid, i, dx] of crew) {
      const a = place(S, cid, win[i][0], footY(st, win[i][1]), 1);
      if (a) S.arc(a, lot[0] + dx, ground, 6, .5, { anim: 'walk' }).catch(G.cancelIgnore);
    }
    await S.wait(.6);
    for (const [cid, i, dx] of crew) {
      const a = S.actor(cid); if (a) S.walk(a, lot[0] + dx, ground, { speed: 110, anim: 'walk' }).catch(G.cancelIgnore);
    }
    await S.wait(1);
    await S.say('polnareff', '我先追上去！他跑不远！');
    await S.say('joseph', '等等，一个人——');
    await S.say('jotaro', '……两路一起追也好。');
    const pol = S.actor('polnareff');
    // 波鲁纳雷夫图集没有 run，只有 walk：写 run 会走「run→walk」兜底并记一条 fallback（验收算素材问题）
    if (pol) { pol.facing = 1; S.walk(pol, 980, ground, { speed: 190, anim: 'walk' }).catch(G.cancelIgnore); }
    await S.wait(.5);
    if (pol) pol.visible = false;

    // 卖卡车的人 + 卡车（pivot 底中，就像停在路边）
    S.mark('fin_truck_buy');
    const seller = S.spawn('npc_townsfolk', lot[0] + 14, ground, { id: 'fin_seller', team: 'npc', label: '卖卡车的人' });
    T.prop(S, 'truck', lot[0], ground, { id: 'fin_truck' });
    await S.say('joseph', '这些够不够？不够记在 SPW 财团的账上！');
    await S.say('npc_townsfolk', '……够、够了！钥匙给你！', { name: '卖卡车的人', actor: seller });
    await S.say('kakyoin', '乔斯达先生，我坐副驾。');
    // 摩托：帧 0 停 / 帧 1 发动
    S.mark('fin_bike');
    const bike = T.prop(S, 'motorbike', lot[0] + 150, ground, { id: 'fin_bike', frame: 0 });
    const jt = S.actor('jotaro');
    if (jt) { jt.x = lot[0] + 150; jt.y = ground; }
    await S.summon('jotaro', { dur: .2 });
    S.standAct('jotaro', 'punch', { dx: 12, dur: .4 });
    S.sfx('car_engine', .7);
    if (bike) bike.frozen = 1;
    S.shake(1, .2);
    await S.say('jotaro', '……我从另一边绕过去。');
    if (bike) S.walk(bike, 980, ground, { speed: 190, anim: 'idle' }).catch(G.cancelIgnore);
    if (jt) S.walk(jt, 980, ground, { speed: 190, anim: 'run' }).catch(G.cancelIgnore);
    await S.wait(.6);
    if (jt) jt.visible = false;
    if (bike) bike.remove = true;

    // 上议员的车：DIO 站在车头前，然后坐进去
    S.mark('fin_senator');
    S.camera(stop[0] - 160);
    const car = T.prop(S, 'senator_car', stop[0], footY(st, stop[1]), { id: 'fin_car' });
    const dio = S.spawn('dio', stop[0] - 34, footY(st, stop[1]), { id: 'fin_dio2', team: 'npc', label: 'DIO' });
    if (dio) dio.facing = 1;
    await S.wait(.4);
    S.nameCard('wilson');
    await S.say('wilson', '你、你是什么人？！我可是美国的上议员——');
    await S.say('dio', '威尔逊·菲利普斯。开车，追上那辆卡车。');
    await S.say('wilson', '是、是……');
    if (dio) { dio.visible = false; dio.remove = true; }
    if (car) car.frozen = 1;
    S.camera(null);
    S.fx('smoke', { x: stop[0] - 20, y: footY(st, stop[1]) - 8, size: 10 });
    S.sfx('car_engine', .5);
  }

  // ================================================================ F-04　卡车逃亡（小游戏，不会 Game Over）
  async function truckChase() {
    const st = 'chase_fin', bg = 'cairo_street_night';
    const lanes = A(bg, 'lanes'), back = A(bg, 'lane_back'), curb = A(bg, 'curb');
    await S.setStage(st, { x: 300, y: footY(st, 164), music: 'battle' });
    // 三层卷动：往右开（背景交付前没有这个 state 也不报错）
    S.state('scroll', 1);
    S.mark('fin_chase');
    const q = { type: 'chase', lane: 1, hp: 100, left: 60, ramIn: 8, ramLane: 2, obstacleLane: 0,
      nextObs: 2.5, warn: 0, warnLane: -1, ramWarn: 0, slowT: 0, cool: 0, hits: 0, ramHits: 0,
      touch: { buttons: ['pad', 'j'], captions: { j: '绿宝石' } } };
    for (let attempt = 0; ; attempt++) {
      q.lane = 1; q.hp = 100; q.left = 60; q.ramIn = 8; q.nextObs = 2.5; q.warn = 0; q.ramWarn = 0; q.slowT = 0; q.cool = 0;
      const r = await L.game(S, q, (s, dt) => {
        s.left -= dt; s.cool = Math.max(0, s.cool - dt); s.slowT = Math.max(0, s.slowT - dt);
        const lo = L.hit('left') || L.hit('up'), hi = L.hit('right') || L.hit('down');
        if (lo) s.lane = Math.max(0, s.lane - 1);
        if (hi) s.lane = Math.min(lanes.length - 1, s.lane + 1);
        // 路障每 2.5 s 一个：先亮 0.6 s 黄光，再从右往左来
        s.nextObs -= dt;
        if (s.nextObs <= 0) { s.nextObs = 2.5; s.warnLane = (s.obstacleLane + 1) % lanes.length; s.warn = .6; s.obstacleLane = s.warnLane; }
        if (s.warn > 0) { s.warn -= dt; if (s.warn <= 0 && s.lane === s.obstacleLane) { s.hp -= 10; s.hits++; S.sfx('thud'); S.shake(2, .15); G.dbg.ev('fin_obstacle_hit', { lane: s.lane, hp: s.hp }); } }
        // 上议员的车每 8 s 从后面撞一次：红色直线预警 0.6 s
        s.ramIn -= dt;
        if (s.ramIn <= .6 && s.ramIn > 0) s.ramWarn = 1;
        if (s.ramIn <= 0) {
          s.ramIn = 8; s.ramWarn = 0;
          if (s.lane === s.ramLane && s.slowT <= 0) { s.hp -= 15; s.ramHits++; S.shake(3, .25); S.sfx('thud'); G.dbg.ev('fin_ram_hit', { lane: s.lane, hp: s.hp }); }
          s.ramLane = (s.ramLane + 1) % lanes.length;
        }
        // 花京院的绿宝石：每 0.5 s 一发；射中车头 → 那辆车减速 2 s（这 2 s 里不会撞）
        if (L.hit('attack') && s.cool <= 0) { s.cool = .5; S.sfx('emerald_shot'); S.fx('gem', { x: 190, y: 152 }); s.slowT = 2; G.dbg.ev('fin_emerald', { lane: s.lane }); }
        if (s.hp <= 0) { s.done = true; s.win = false; }
        if (s.left <= 0) { s.done = true; s.win = true; }
      }, (g, s) => {
        T.drawBg(g, bg, s.t, 0);
        // 路面：从 @lane_back 到画面底；车道中线按 @lanes 的上沿取（三条车道的行距就是透视间距）
        g.fillStyle = '#15111d'; g.fillRect(0, back, 320, 180 - back);
        g.fillStyle = '#2a2433'; g.fillRect(0, back, 320, 1);
        for (let i = 1; i < lanes.length; i++) {
          g.fillStyle = '#4a4256';
          for (let x = -((s.t * 90) % 24); x < 320; x += 24) g.fillRect(x, Math.round((lanes[i - 1] + lanes[i]) / 2), 10, 1);
        }
        const ly = i => lanes[G.clamp(i, 0, lanes.length - 1)];
        // 路障：先亮那条车道的黄光（0.6 s），同时从右边迎面过来
        if (s.warn > 0) {
          g.fillStyle = '#ffde7377'; g.fillRect(0, ly(s.obstacleLane) - 9, 320, 4);
          T.sprite(g, 'prop:trash_can', 'idle', 0, 340 - (1 - G.clamp(s.warn / .6, 0, 1)) * 260, ly(s.obstacleLane), { scale: .8 });
        }
        // 上议员的黑车跟在后面（画面左边）+ 车顶的 DIO；撞之前那条车道亮红色直线
        T.sprite(g, 'prop:senator_car', 'idle', 0, 62, ly(s.ramLane), { scale: .9 });
        if (s.ramWarn) { g.fillStyle = '#ff574999'; g.fillRect(0, ly(s.ramLane) - 9, 320, 2); }
        T.sprite(g, 'dio', 'idle', 0, 66, ly(s.ramLane) - 8, { scale: .55 });
        // 卡车固定在画面 x 200：乔瑟夫开车、花京院坐在后面往左射
        T.sprite(g, 'prop:truck', 'idle', 0, 200, ly(s.lane), { scale: 1.1 });
        T.sprite(g, 'joseph', 'sit', 0, 194, ly(s.lane) - 4, { scale: .5 });
        T.sprite(g, 'kakyoin', 'cast', 0, 214, ly(s.lane) - 6, { scale: .5, flip: true });
      }, (g, s) => {
        L.label(g, '车况 ' + Math.max(0, Math.round(s.hp)) + '　逃 ' + Math.max(0, Math.ceil(s.left)) + ' 秒',
          '↑↓ 换车道；J 往后射绿宝石，能让他们减速');
        if (s.slowT > 0) L.text(g, '上议员的黑车被甩远了！', 320, 300, '#9fe9ff', 'center');
      });
      if (r && r.win) break;
      // 车况 0：急刹 + 画面一歪 → 这一段从头再来
      S.sfx('skid'); S.shake(4, .5); S.bump(.12, .3);
      await S.say('joseph', '险些失控……');
    }

    // 结尾过场：DIO 跳上卡车 → 一拳 → 后窗黑影 → 卡车撞楼
    S.mark('fin_rear_window');
    await S.say('dio', '……逃得了吗？');
    S.sfx('punch_heavy');
    await S.say('joseph', '花京院！');
    S.sfx('glass_break'); S.sfx('crash', .6);
    await S.narrate('……上议员没能逃出来。');
    S.mark('fin_truck_crash');
    S.state('crashed', 1); S.state('stand_wrecked', 1);
    S.sfx('crash'); S.shake(6, .6);
    for (let n = 0; n < 6; n++) S.fx('dust', { x: 560 + n * 8, y: 152, size: 12 }, { life: 1.2 });
    await S.crash(5, 6);
    G.flags.crash = 6;   // 章末检查读“坠毁记录 6”
    await S.say('joseph', '……这一次，可以不算吗？');
    await S.say('kakyoin', '……不算。这次是 DIO 的错。');
    await S.say('joseph', '他上了屋顶。……花京院，还能动吗？');
    await S.say('kakyoin', '当然。');
  }

  // ================================================================ F-05　28B 屋顶：半径 20 米
  async function roofWeb() {
    const st = 'roof_fin', bg = 'cairo_rooftops';
    const arrive = at(st, bg, 'arrive'), nodes = A(bg, 'nodes'), air = A(bg, 'dio_air'), tank = at(st, bg, 'tank');
    party(['joseph', 'kakyoin'], 'kakyoin', fallen);
    await S.setStage(st, { x: arrive[0], y: arrive[1], music: 'boss' });
    S.state('red_sky', 0); S.state('clock_broken', 0); S.state('tank_burst', 0); S.state('chimney_broken', 0);
    place(S, 'kakyoin', arrive[0], arrive[1]);
    place(S, 'joseph', arrive[0] - 20, arrive[1]);
    const dio = S.spawn('dio', air[0], air[1], { id: 'fin_dio3', team: 'npc', label: 'DIO' });
    if (dio) { dio.facing = -1; dio.alpha = .85; }
    await S.say('dio', '花京院典明。……你的替身，能逃到哪里去？');
    await S.say('kakyoin', '我不逃。……这一次，换我来设陷阱。');

    for (let attempt = 0; ; attempt++) {
      S.mark('fin_web');
      const q = { type: 'web', nodes: nodes.map(p => ({ x: p[0], y: p[1], set: false })), warn: 0, kind: 'knife',
        next: 5, cuts: 0, targetX: 0, evaded: false, touch: { buttons: ['pad', 'j', 'k'], captions: { j: '布网', k: '闪避' } } };
      const r = await L.game(S, q, (s, dt) => {
        L.move(W.player, dt, 95);
        if (L.hit('attack')) {
          const n = s.nodes.find(n => !n.set && Math.abs(n.x - W.player.x) < 22);
          if (n) { n.set = true; S.sfx('hiero_tentacle'); G.dbg.ev('fin_web_node', { n: s.nodes.filter(v => v.set).length }); }
        }
        // DIO 每 5 s 二选一：甩一把飞刀（24f 红线，伤 12）或俯冲切一根已经布好的丝（40f）
        if (s.t >= s.next && s.warn <= 0) {
          s.kind = s.cuts % 2 ? 'knife' : 'cut'; s.warn = (s.kind === 'knife' ? 24 : 40) / 60;
          s.targetX = W.player.x; s.next += 5; s.evaded = false;
        }
        if (s.warn > 0) {
          s.warn -= dt;
          if (L.hit('dodge')) { W.player.x = G.clamp(W.player.x + (I.isDown('left') ? -1 : 1) * 44, 15, 615); s.evaded = true; }
          if (s.warn <= 0) {
            if (s.kind === 'knife') {
              if (!s.evaded && Math.abs(W.player.x - s.targetX) < 24) { L.damage({ player: W.player }, 12); S.sfx('knife_volley'); G.dbg.ev('fin_web_hit', { kind: 'knife' }); }
            } else {
              const n = s.nodes.find(n => n.set);
              if (n) { n.set = false; s.cuts++; S.sfx('hiero_tentacle'); G.dbg.ev('fin_web_hit', { kind: 'cut' }); }
            }
            s.warn = 0;
          }
        }
        if (s.nodes.every(n => n.set)) { s.done = true; s.win = true; }
        if (s.t >= 30 && !s.done) { s.done = true; s.win = false; }
      }, (g, s) => {
        T.drawBg(g, bg, s.t, G.cam.x);
        // 节点：屋顶边缘 / 天线 / 水塔 / 钟楼脚下（背景给的 8 个点）
        for (const n of s.nodes) {
          const x = n.x - G.cam.x;
          g.fillStyle = n.set ? '#50ff99' : '#bfd6c566'; g.fillRect(x - 2, n.y, 4, 10);
          if (n.set) { g.strokeStyle = '#4ebc77'; g.beginPath(); g.moveTo(x, n.y + 4); g.lineTo(air[0] - G.cam.x, air[1]); g.stroke(); }
        }
        T.sprite(g, 'kakyoin', 'walk', Math.floor(s.t * 7) % 4, W.player.x - G.cam.x, W.player.y);
        T.sprite(g, 'joseph', 'idle', 0, arrive[0] - 20 - G.cam.x, arrive[1]);
        T.sprite(g, 'dio', s.warn > 0 ? 'punch' : 'idle', 0, air[0] - G.cam.x, air[1], { alpha: .85 });
        if (s.warn > 0) { g.fillStyle = s.kind === 'knife' ? '#ff5749' : '#ffde73'; g.fillRect(s.targetX - G.cam.x - 16, 158, 32, 2); }
      }, (g, s) => {
        L.label(g, '半径二十米 · 触须网', '走到节点 20 px 内按 J 布网；红线出现时 K 闪离');
        L.text(g, '触须网 ' + s.nodes.filter(n => n.set).length + ' / 8', 22, 314, '#86ffb9');
        L.text(g, '剩 ' + Math.ceil(Math.max(0, 30 - s.t)) + ' 秒', 610, 314, '#ffe174', 'right');
      });
      if (r && r.win) break;
      await S.say('kakyoin', '还差一点……重新布下这张网。');
      W.player.x = arrive[0];
    }

    // 网满：全方位绿宝石 → 咋瓦鲁多（黄）→ 剪丝 → 一拳（反色 → 黑白 ×2 + ドン!!）→ 水塔
    S.mark('fin_radius20');
    await S.say('kakyoin', '半径 20 米——绿宝石水花！');
    S.fx('emerald_splash', { x0: air[0] - 40, y0: air[1] + 40, x1: air[0], y1: air[1] }, { life: .9 });
    S.sfx('emerald_shot');
    const dio2 = S.actor('fin_dio3') || dio;
    if (dio2) { G.time.stop(dio2, { tint: 'yellow', burst: .4, dur: 1.2, lines: { start: 'dio_ts', end: 'dio_resume' } }); }
    await S.wait(2.6, 'ui');
    S.mark('fin_cut');
    S.sfx('slash0', .6);
    await S.wait(.3);
    S.impact('invert', 2 / 60); S.filter('gray', 1); S.shake(5, .3);
    S.word('ドン!!', { x: 320, y: 150 });
    await S.wait(.5, 'ui');
    S.filter('gray', null);
    S.mark('fin_tank');
    S.state('tank_burst', 1); S.sfx('water_gush', .7);
    S.fx('water_gush', { x: tank[0], y: tank[1] - 20 }, { life: 2.4 });
    place(S, 'kakyoin', tank[0] - 16, tank[1]);
    if (W.player) W.player.play('down');
    await S.wait(.6);
    // 钟楼“跳一格”：背景只画了表盘 + 时针，分针由剧情在 @clock_face 上画
    const face = A(bg, 'clock_face');
    S.mark('fin_clock_jump');
    snd('clock_tick', 'clock_tick', { vol: .9 });
    const hand = L.pixel(P => {
      const a = -Math.PI / 2 + (Math.floor(G.clk.world * 2) % 2) * (Math.PI / 6);
      G.px.line(P, face[0] - G.cam.x, face[1], face[0] - G.cam.x + Math.cos(a) * (face[2] + 5), face[1] + Math.sin(a) * (face[2] + 5), '#2a2030', 1, 2);
    });
    await S.say('kakyoin', '……钟……刚才……跳了？', { expr: 'weak' });

    // 最后一发：打偏只重来这一下（布网不重来）
    for (let attempt = 0; ; attempt++) {
      S.mark('fin_aim');
      const win = await S.aim({ label: '方向键把准星移到钟面，J 射出最后的绿宝石', throw: true, time: 4, r: 7,
        start: [30, 20], drift: 0, jitter: 2 });
      if (win) { S.sfx('emerald_shot'); break; }
      await S.narrate('准星晃开了。只重试最后一发。');
    }
    S.mark('fin_clock_break');
    S.state('clock_broken', 1); S.word('パリン!', { x: 320, y: 130 }); S.sfx('glass_break');
    if (hand) { hand.hidden = true; W.stage.props = W.stage.props.filter(p => p !== hand); }
    S.mark('fin_kak_rest');
    await S.say('kakyoin', '乔斯达先生……他的替身的秘密……是「时间」……');
    await L.view(S, { bg: 'black', parts: [{ cid: 'scene:s15_kak_rest', x: 160, y: 178, scale: 2 }] }, 1.2);
    await S.leave('kakyoin');
    S.music('sad');
    await S.fadeOut(1.5); await S.fadeIn(.5);
  }

  // ================================================================ F-06　28C 乔瑟夫：讯息
  async function message() {
    const st = 'roof_fin', bg = 'cairo_rooftops';
    const chimney = A(bg, 'chimney'), ground = footY(st, 160);
    S.setLeader('joseph', { force: true });
    place(S, 'joseph', chimney[0] - 60, ground);
    const dio = S.spawn('dio', chimney[0] + 40, ground, { id: 'fin_dio4', team: 'npc', label: 'DIO' });
    if (dio) dio.facing = -1;
    S.mark('fin_message');
    await S.say('joseph', '……花京院。');
    await S.say('joseph', '时间……是时间！承太郎，DIO 的能力是让时间停止！');
    // 藤蔓缠住 DIO、波纹顺着藤蔓过去
    S.summon('joseph', { dur: .2 });
    // 隐者之紫只有 vine 一个动作（kind:'vine'，没有 cast），pose 写 cast 会解析不到
    S.standAct('joseph', 'vine', { dur: .6 });
    S.fx('vines', { x0: chimney[0] - 50, y0: ground - 20, x1: chimney[0] + 40, y1: ground - 16 }, { life: 2.2 });
    S.sfx('hamon', .6);
    await S.say('dio', '……老头子，你想干什么？');
    // 讯息进度条：一定成功——自己数按键，按得少也按时间涨满；不出现成功 / 失败字样
    const q = { type: 'message', value: 0, presses: 0, bonus: false, touch: { buttons: ['j'], captions: { j: '传讯' } } };
    await L.game(S, q, (s, dt) => {
      if (L.hit('attack')) { s.presses++; s.value = Math.min(1, s.value + .07); }
      s.value = Math.min(1, s.value + dt / 3);
      if (s.value >= 1) s.bonus = s.presses >= 12;
      if (s.t >= 3) { s.done = true; s.win = true; }
    }, (g, s) => {
      T.drawBg(g, bg, s.t, G.cam.x);
      T.sprite(g, 'joseph', 'point', 0, chimney[0] - 60 - G.cam.x, ground, { scale: 1.4 });
      T.sprite(g, 'dio', 'idle', 0, chimney[0] + 40 - G.cam.x, ground, { scale: 1.4, flip: true });
      g.strokeStyle = '#c9a2ff'; g.lineWidth = 1;
      for (let n = 0; n < 3; n++) { g.beginPath(); g.moveTo(chimney[0] - 52 - G.cam.x, ground - 26 + n * 4); g.lineTo(chimney[0] + 36 - G.cam.x, ground - 22 + n * 3); g.stroke(); }
    }, (g, s) => {
      L.label(g, '把讯息传给承太郎', '连按 J 加快藤蔓里的讯息');
      g.fillStyle = '#3a294e'; g.fillRect(100, 302, 440, 8);
      g.fillStyle = '#d9b0f5'; g.fillRect(100, 302, 440 * s.value, 8);
    });
    if (q.bonus) await S.say('joseph', '……还有！他停时间的时候，自己也只能动几秒！');
    // 插入 0.6 s：远处骑着摩托的承太郎抬头（只看剪影和一道灯光）
    await L.view(S, { bg: '#1b1626', parts: [{ cid: 'jotaro', anim: 'idle', x: 150, y: 170, scale: 2, alpha: .55 }],
      draw(g) { g.fillStyle = '#9a86ff'; g.fillRect(150, 24, 2, 88); g.fillStyle = '#ffe9a855'; g.fillRect(120, 148, 70, 3); } }, .6);
    await S.say('dio', '啰嗦的老头。');
    await S.say('dio', '咋瓦鲁多！');
    if (dio) G.time.stop(dio, { tint: 'yellow', dur: 1.2, lines: { start: 'dio_ts', end: 'dio_resume' } });
    await S.wait(2.6, 'ui');
    S.state('chimney_broken', 1); S.sfx('crash'); S.shake(5, .4);
    S.fx('dust', { x: chimney[0], y: chimney[1], size: 18 }, { life: 1.2 });
    // 剪影：乔瑟夫从屋顶边缘落下，天空变成血红
    S.mark('fin_red_sky');
    S.state('red_sky', 1);
    const jos = S.actor('joseph');
    if (jos) {
      jos.facing = 1;
      S.walk(jos, chimney[0] + 120, ground, { speed: 60, anim: 'run' }).catch(G.cancelIgnore);
      await S.wait(.5);
      await S.animate(.7, k => { jos.y = ground + k * 40; jos.alpha = 1 - k; });
      jos.visible = false;
    }
    await S.say('joseph', '承太郎……别靠近他……');
    await S.leave('joseph');
    S.mark('fin_walk');
    await S.narrate('摩托停在楼下。屋顶上只站着 DIO 一个人的剪影。');
    await S.say('jotaro', '…………');
  }

  // ================================================================ F-07　28D 对走
  async function walkToward() {
    const st = 'street_fin', bg = 'cairo_street_night';
    const arrive = at(st, bg, 'arrive'), exit = at(st, bg, 'exit'), sign = at(st, bg, 'road_sign');
    party(['jotaro'], 'jotaro', ['avdol', 'iggy', 'kakyoin', 'joseph']);
    await S.setStage(st, { x: 300, y: footY(st, 162), music: 'boss' });
    S.state('dark', 1); S.state('crashed', 1); S.state('stand_wrecked', 1); S.state('sign_gone', 0);
    S.mark('fin_walk');
    await S.vs({ key: 'theworld', hero: 'jotaro', enemy: 'dio' });
    if (G.uifx && G.uifx.vsTag) G.uifx.vsTag(null);
    const jt = place(S, 'jotaro', arrive[0], arrive[1], 1);
    const dio = S.spawn('dio', exit[0], exit[1], { id: 'fin_dio5', team: 'npc', label: 'DIO' });
    if (dio) dio.facing = -1;
    S.camera(sign[0] - 160);
    // 两人各走 3 s，镜头在两人中间
    if (jt) S.walk(jt, sign[0] - 30, footY(st, 162), { speed: 170, anim: 'walk' }).catch(G.cancelIgnore);
    if (dio) S.walk(dio, sign[0] + 30, footY(st, 162), { speed: 170, anim: 'walk' }).catch(G.cancelIgnore);
    await S.wait(3);
    await S.say('dio', '哦？你竟然主动靠近我？');
    await S.say('jotaro', '不靠近的话，怎么揍你。');
  }

  // ================================================================ F-08~F-10　DIO 三段
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
    // 〔四格头像特写 · DIO 发现承太郎在时停里动了〕：bark 不锁操作，四格特写走 L.task，别让时停时间轴等它
    S.mark('fin_growth');
    S.bark('dio', '……什么？！你……在停止的时间里动了？！', { dur: 2.2 });
    L.task(c, async () => {
      S.mark('fin_dio_shock');
      await T.closeup4(S, { cid: 'dio', expr: 'shock', bg: 'menace', dur: .9 });
    });
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
          // 第三段的 +30% 由这一场的 dmgScale 1.3 统一乘（排队伤害结算时同样乘）；这里再写 39 就等于 ×1.69，一拳 51
          st.attacked = true; e.stand.act('punch', { dur: .4 }); ts.queueHit(p, e, { dmg: 30, push: 24, slot: 'enemy', guard: 'normal', sfxHit: 'punch_heavy' });
        }
      } else {
        if (!st.knifeBuilt) {
          st.knifeBuilt = true;
          for (let n = 0; n < 16; n++) { const a = n * Math.PI / 8; st.knives.push({ x: st.x + Math.cos(a) * 62, y: st.y + Math.sin(a) * 13, a, dead: false }); }
          S.sfx('knife_freeze');
          S.mark('fin_knife_ring');
          if (d.magazines > 0) S.mark('fin_magazine');
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
    const d = c.data, p = c.player, e = c.boss;
    d.playDead = true; G.time.clear(); d.stop = null; e.mem.locked = true;
    p.play('down'); S.sfx('flatline');
    // G.ui.insertUI 存的是 { draw, t0 } 对象，S.insertUI 只收绘制函数：按对象身份原样放回，取消 / 重来时也要放回。
    const oldUI = G.ui.insertUI;
    S.insertUI(g => { L.hud(g, ['心跳停止……', '等待破绽']); g.strokeStyle = '#72e7a0'; g.beginPath(); g.moveTo(120, 308); g.lineTo(520, 308); g.stroke(); });
    const mine = G.ui.insertUI;
    let sign = null, v = null;
    try {
      await S.wait(.9, 'ui');
      // DIO 走到路牌前把它连根拔起（背景 sign_gone = 1，手里多一块路牌）
      S.mark('fin_sign');
      S.state('sign_gone', 1); sign = T.prop(S, 'road_sign', e.x + 14, e.y - 30, { id: 'late_road_sign' });
      await S.say('dio', '心跳真的停了……那就彻底结束吧。');
      await S.say('dio', '用你的头，给这场旅行画上句号。');
      S.mark('fin_pol_stab');
      v = T.show(S, { bg: 'cairo_street_night', parts: [{ cid: 'chariot', anim: 'punch', x: 140, y: 167, scale: 2 }, { cid: 'dio', anim: 'hurt', x: 193, y: 162, scale: 2 }],
        draw(g) { g.fillStyle = '#fff9ba'; g.fillRect(168, 72, 3, 20); } });
      S.sfx('glint'); S.sfx('stab', .8); await S.wait(.45, 'ui'); v.close(); v = null;
      await S.say('polnareff', '赶上了！');
      await S.say('dio', '……你这只苍蝇。');
      S.sfx('punch_heavy');
      const pol = S.actor('polnareff');
      if (pol) { pol.x = e.x + 70; pol.y = e.y; pol.play('down'); }
    } finally {
      if (v) v.close();
      if (sign) sign.remove = true;
      if (G.ui.insertUI === mine) G.ui.insertUI = oldUI;
    }
    p.play('idle'); p.state = 'idle'; p.dmgOut = 2; d.counterUntil = c.t + 1.5;
    e.mem.locked = false; e.stunT = 1.5; d.nextStop = c.t + 5;
    S.hint('现在！白金之星反击——一秒半内伤害翻倍。', 3); G.dbg.ev('dio_play_dead');
  }
  async function roadroller(c) {
    const d = c.data, e = c.boss;
    d.roller = true; G.time.clear(); d.stop = null;
    S.mark('fin_roller');
    await S.title('roadroller'); S.sfx('roadroller');
    const v = T.show(S, { bg: 'cairo_street_night', draw(g, t) {
      g.fillStyle = '#09060dbb'; g.fillRect(70, 145, 180, 10);
      T.sprite(g, 'prop:roadroller', 'idle', Math.min(2, Math.floor(t * 2)), 160, 72 + Math.min(60, t * 55), { scale: 2 });
      T.sprite(g, 'jotaro', 'cmd', 0, 160, 175, { scale: 2 });
    } }); await S.wait(1, 'ui');
    G.time.stop(e, { tint: 'yellow', prewarn: false, dur: 5, burst: .4, lines: { start: 'dio_ts', end: 'dio_resume' } });
    let win = false;
    for (let attempt = 0; !win; attempt++) {
      win = await S.clash({ label: '顶回去——！（连按 J）', time: 4, rate: attempt ? .14 : .2, id: 'roadroller' });
      // 输：吃 60 伤，只重来这个 QTE（第 2 次起推力 −30%）
      if (!win) { L.damage(c, 60); }
    }
    v.close();
    // 〔眼部条带特写：承太郎的眼睛 + 「ギロッ」〕
    S.word('ギロッ', { x: 320, y: 118 });
    await S.eyeStrip('jotaro', { dur: .4 });
    S.standCard('starplat_world', { y: 6 });
    S.mark('fin_sp_world');
    G.time.stop(c.player, { tint: 'blue', prewarn: false, dur: 2, burst: .4, lines: { start: 'jotaro_ts', end: 'jotaro_resume' } });
    c.player.x = e.x + 30; c.player.facing = -1; c.player.play('kick'); e.play('hurt'); S.sfx('punch_heavy'); S.shake(5, .3);
    e.hp = Math.max(e.maxHp * .18, e.hp - 350); await S.wait(2.8, 'ui'); G.flags.starWorld = true;
    d.nextStop = c.t + 7; G.dbg.ev('dio_roadroller');
  }
  async function finalClash(c) {
    const d = c.data; d.final = true; G.time.clear(); d.stop = null;
    for (let attempt = 0; ; attempt++) {
      S.mark('fin_final_clash');
      const win = await L.clash(S, { label: '欧拉——！！（连按 J）', time: 5, rate: attempt ? .14 : .2, id: 'dio_final' });
      if (win) { c.end(); return; }
      const min = c.player.minHp; c.player.minHp = 1;
      G.combat.hit(c.boss, c.player, { dmg: 60, push: 0, slot: 'enemy', guard: 'none', sfxHit: 'thud' }, { queued: true }); c.player.minHp = min;
      await S.say('jotaro', '还没结束。最后这一拳，再来！');
    }
  }
  // DIO 三段的配置：剧情（dioFight）和试炼（DioAllSrc）共用一份。
  //   trial 时只跳过开场台词；觉醒 / 装死 / 压路机 / 最终对冲这些机制演出保留（台词很短，是机制的一部分）。
  function dioSpec(o, phase) {
    const kitOverride = phase === 2 ? { jotaro: { chords: { 'guard+dodge': { hold: 3, run(s, p, c) {
      if (canPlayDead(c)) L.task(c, () => playDead(c));
      else { const held = p._chordHold['guard+dodge']; held.t = 0; held.done = false; }
    } } } } } : phase === 3 ? { jotaro: { special: G.SPTW.storyU } } : {};
    // 试炼整轮把承太郎的 kit 换成了 SPTW；段 1/2 的 U 必须显式换回欧拉欧拉（这一关不套 TRIAL.kitOverride）。
    //   kitOverride 只能覆盖 kitOf，改不了 p.kit，所以 combat.special 仍会把这份 special 当“剧情型”调用；
    //   这里补一层 (S,p,c,C) 适配，并补回剧情型分支会跳过的出招姿势。
    if (o.trial && phase < 3) {
      const ora = G.KITS.jotaro.special;
      kitOverride.jotaro = Object.assign({}, kitOverride.jotaro, { special: Object.assign({}, ora, {
        run: (s, p, c, C) => { p.play(ora.pose || 'special'); return ora.run(p, C); },
      }) });
    }
    return { id: 'b28d' + phase + '_dio', lead: 'jotaro', swap: false, bench: 'hide', arena: [400, 760], finish: 'none', music: 'boss',
      dmgScale: phase === 3 ? 1.3 : 1,
      waves: [[{ cid: 'dio', kit: 'e_dio', boss: true, minHp: 1, x: 690, y: footY('street_fin', 162) }]],
      kitOverride,
      onWave(s, n, es, attempt, c) {
        dropGrowth();
        c.data.stops = 0; c.data.nextStop = 7; c.data.stop = null; c.data.magazines = phase === 2 ? 3 : 0; c.data.hold = 0; c.data.clashNext = 0;
        c.data.playDead = false; c.data.roller = false; c.data.final = false; c.data.growing = false; c.data.growthStarted = false;
        W.stage.props = W.stage.props.filter(p => !String(p.id || '').startsWith('late_'));
        // 重试复原：路牌回来（装死那段的 sign_gone 也复原）
        S.state('sign_gone', 0);
        // 杂志只挡时停后的刀阵（脚本：前 3 把刀不扣血）；平时的三连飞刀（TW_KNIFE）不消耗杂志
        if (phase === 2) c.player.onHitBy = (t, a, m, info) => {
          if (m.tag === 'dio_ring' && c.data.magazines > 0) { c.data.magazines--; if (info.shot) info.shot.dead = true; s.sfx('guard'); G.dbg.ev('magazine_block', { left: c.data.magazines }); return 'evade'; }
          return null;
        };
        L.pixel(P => {
          const stop = c.data.stop;
          if (stop && G.time.phase === 'warn') G.px.line(P, c.boss.x - G.cam.x, c.boss.y, stop.x - G.cam.x, stop.y, '#ffe174', .75, 2);
          if (stop && G.time.active && !stop.launched) for (const k of stop.knives) if (!k.dead) G.px.line(P, k.x - G.cam.x - 3, k.y - 20, k.x - G.cam.x + 3, k.y - 20, '#f2eefc');
        });
        s.insertUI(g => L.hud(g, phase === 1 ? ['DIO · 第1段', '黄光一闪就按住 L——停止的时间里挨的打会少很多', '时停中精准格挡无效',
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
          // 正在“停止心跳”：承太郎倒在地上，DIO 不出新招、不发动时停，只慢慢走近确认；松手就恢复。
          if (d.hold > 0) {
            if (!d.holdLock) { d.holdLock = true; e.mem.locked = true; e.tele = null; p.play('down'); G.dbg.ev('dio_play_dead_hold'); }
            if (!e.atk && !e.mem.dash) { const side = p.x >= e.x ? -1 : 1; G.combat.walkTo(e, p.x + side * 34, p.y, dt, 24); }
          } else if (d.holdLock) { d.holdLock = false; if (!G.time.active) e.mem.locked = false; if (p.anim === 'down') p.play('idle'); }
          // DIO 只会被打到 1 HP；玩家一直没掉到 35% 以下时也要能进装死（波鲁纳雷夫的一剑是这一段的收尾），提示一次。
          if (e.hp <= 1 && !d.deadHint) { d.deadHint = true; S.hint('DIO 不会就这样倒下……停止心跳引他靠近：按住 L + K 三秒', 6); }
        }
        if (phase === 3 && !d.roller && (e.hp / e.maxHp <= .7 || c.t >= 12)) { L.task(c, () => roadroller(c)); return; }
        if (phase === 3 && d.roller && !d.final && e.hp / e.maxHp <= .15) { L.task(c, () => finalClash(c)); return; }
        if (!G.time.active && c.t >= d.nextStop && !d.busy && !d.holdLock) stopDio(c, phase);
        if (phase === 1 && !G.time.active && c.t >= d.clashNext && e.atkId === 'TW_RUSH' && e.atk && p.rush && Math.abs(e.x - p.x) < 65) {
          d.clashNext = c.t + 6;
          L.task(c, async () => {
            e.atk = null;
            // 对冲：承太郎这边画「欧拉欧拉」，DIO 那边画「木大木大」
            S.word('欧拉欧拉', { x: 250, y: 120 }); S.word('木大木大', { x: 430, y: 120 });
            const win = await L.clash(S, { label: '欧拉欧拉欧拉！（连按 J）', time: 4 });
            if (win) e.stunT = 1; else L.damage(c, 60);
          });
        }
        // 第一段必须经历第二次时停的“手指动了”：DIO 先被打到 1 HP 时把下一次时停提前，觉醒之后才结束这一段。
        if (e.hp <= 1 && phase === 1) { if (G.flags.dioGrowth) c.end(); else if (!G.time.active && d.nextStop > c.t + 1) d.nextStop = c.t + 1; }
        if (e.hp <= 1 && phase === 2 && d.playDead && !d.busy) c.end();
      }, after(s, es, attempt, c) { dropGrowth(); s.insertUI(null); c.player.onHitBy = null; c.player.dmgOut = 1; } };
  }
  async function dioFight(S, phase, o = { trial: false, wrap: s => s }) {
    if (!o.trial) party(['jotaro', 'polnareff'], 'jotaro', ['avdol', 'iggy', 'kakyoin', 'joseph']);
    await S.setStage('street_fin', { x: 450, y: footY('street_fin', 162) }); S.mark('final_dio_' + phase);
    // 试炼没有过场，而 setStage 会把 state 清回默认：每段补回夜景（剧情由过场自己设，保持原样）
    if (o.trial) S.state('dark', 1);
    if (!o.trial) {
      // 段 2 的开场：DIO 对“半秒”的反应
      if (phase === 2) await S.say('dio', '半秒？……区区半秒，能做什么。');
      // 段 3 的开场：DIO 从屋顶落下来（落地时地面裂开）、笑声、大字 WRYYY
      if (phase === 3) {
        S.mark('fin_wryyy');
        const dio = S.spawn('dio', 690, footY('street_fin', 162), { id: 'fin_dio_open', team: 'npc', label: 'DIO' });
        if (dio) { dio.play('laugh'); S.fx('crack', { x: 690, y: footY('street_fin', 162), size: 30 }, { life: 1.4 }); }
        S.fx('dust', { x: 690, y: footY('street_fin', 162) - 4, size: 18 }, { life: 1.1 });
        S.sfx('roar', .8);
        await S.title('wryyy');
        await S.say('dio', '这具身体，终于完全属于我了。……承太郎，你的半秒，我已经不放在眼里了。');
        if (dio) dio.remove = true;
      }
    }
    // 三段用同一套 DIO（kit e_dio 的生命池 1500）；段 3 的敌人伤害 ×1.3（脚本要求的一拳 30 × 1.3 = 39）
    await S.fight(o.wrap(dioSpec(o, phase)));
  }

  // 段 2 → 段 3 之间：DIO 要血（吸血只用剪影 + 音效，不画）
  async function bloodInterlude() {
    const st = 'street_fin', bg = 'cairo_street_night';
    await S.setStage(st, { x: 520, y: footY(st, 162), music: 'boss' });
    S.state('dark', 1); S.state('crashed', 1); S.state('stand_wrecked', 1);
    place(S, 'jotaro', 480, footY(st, 162), 1);
    const dio = S.spawn('dio', 560, footY(st, 162), { id: 'fin_dio7', team: 'npc', label: 'DIO' });
    if (dio) dio.facing = 1;
    await S.say('dio', '……够了。我需要血。');
    if (dio) { dio.visible = false; dio.remove = true; }
    S.mark('fin_saikou');
    await L.view(S, { bg: '#641e37', parts: [
      { cid: 'joseph', anim: 'lie', x: 140, y: 168, scale: 2, alpha: .3 },
      { cid: 'dio', anim: 'laugh', x: 190, y: 168, scale: 2.4, alpha: .3 }] }, 1.2);
    S.sfx('drain', .7);
    await S.say('dio', '最高哒！');
  }

  // 星尘试炼第 18 关：三段连战，承太郎单挑（试炼的 wrap 按 solo 处理：无队友、bench hide、swap false）。
  //   剧情路径由 interlude 决定要不要在段 2 → 段 3 之间演“DIO 要血”（挑战入口不演，和原来一致）。
  const DIO_RUN = { trial: false, wrap: s => s };
  const DioAllSrc = {
    chapter: 'final', pack: '_fin',
    setup: async S => {
      await M.ensureBg('_fin');
      // 每轮进关从头开始：觉醒（dioGrowth）和时停半秒（starWorld）不能从上一轮带进来
      delete G.flags.dioGrowth; delete G.flags.starWorld;
      S.state('dark', 1);
    },
    run: async (S, o) => {
      await DioAllSrc.setup(S);
      for (let phase = 1; phase <= 3; phase++) {
        await S.run(async () => { await dioFight(S, phase, o); });
        if (phase === 2 && !o.trial && o.interlude) await S.run(bloodInterlude);
      }
    },
  };

  // ================================================================ F-11　终结（在 street_fin 里演）
  async function finish() {
    const st = 'street_fin', bg = 'cairo_street_night';
    await S.setStage(st, { x: 520, y: footY(st, 162), music: 'boss' });
    S.state('dark', 1); S.state('crashed', 1); S.state('stand_wrecked', 1);
    const jt = place(S, 'jotaro', 500, footY(st, 162), 1);
    // dio 不是主角表里的角色，数据包 heroes 里没有他的 stand 映射，
    // 不显式给 stand:'theworld' 的话 S.summon(dio) 会走 stand 缺失兜底（验收算 api_missing）
    const dio = S.spawn('dio', 570, footY(st, 162), { id: 'fin_dio6', team: 'npc', label: 'DIO', stand: 'theworld' });
    if (dio) dio.facing = -1;
    S.camera(520);
    await S.summon('jotaro', { dur: .2 });
    if (dio) S.summon(dio, { dur: .2 });
    S.standAct('jotaro', 'rush', { dx: 24, dur: .8 });
    if (dio) S.standAct(dio, 'punch', { dx: -24, dur: .8 });
    // 1. 紫色定格 0.5 s：两人最后一击撞在一起
    S.mark('fin_crack');
    // insert 会整屏替掉世界渲染（world.js 看到 insert 就直接 return），所以先把两人这一帧画回来再罩紫色，
    // 否则「定格」只剩一块纯紫色。画布是世界层 320×180，不是 UI 层的 640×360。
    S.insert(g => { L.underWorld(g); g.fillStyle = '#4a1a5ecc'; g.fillRect(0, 0, 320, 180); });
    await S.wait(.5); S.insert(null);
    // 2. 世界的腿先碎、整个替身开裂碎裂
    S.fx('shatter', { src: 'theworld', logical: 'idle', x: 570, y: 130, pieces: 40, dur: .9 }, { life: 1.2 });
    S.fx('crack', { x: 570, y: 120, size: 26 }, { life: 1.2 });
    S.sfx('glass_break', .7);
    // 3. DIO 的身体裂开、透出光（画几道发光的裂缝，不画血）
    const cracks = L.pixel(P => {
      if (!dio || dio.remove) return;
      const x = dio.x - G.cam.x, y = dio.y;
      for (const [ax, ay, bx, by, c] of [[-5, -44, 3, -20, '#fff8d0'], [3, -20, -2, 2, '#ffe9a8'], [-2, 2, 5, 20, '#fff8d0'], [-7, -10, -1, -30, '#ffe9a8']])
        G.px.line(P, x + ax, y + ay, x + bx, y + by, c, .9, 1);
    });
    S.fx('glint', { x: 570, y: 120, size: 12 });
    await S.wait(.5);
    await S.say('dio', '怎么可能……我是……DIO……');
    // 4. 光散开，DIO 倒下
    S.flash(.35, .8, '#ffe9b0');
    if (dio) { dio.play('down'); }
    await S.animate(.7, k => { if (dio) dio.alpha = 1 - k; });
    if (cracks) { cracks.hidden = true; W.stage.props = W.stage.props.filter(p => p !== cracks); }
    if (dio) dio.visible = false;
    S.sfx('thud', .6);
    // 5. 承太郎背影 + 台词
    S.mark('fin_back');
    await L.view(S, { bg: 'black', parts: [{ cid: 'scene:s18_final2_jotaro_back', x: 160, y: 178, scale: 2 }] }, .8);
    if (jt) { jt.facing = 1; jt.play('idle'); }
    await S.say('jotaro', '你的失败只有一个原因……就是你惹我生气了。');
    await S.fadeOut(.6);
  }

  // ================================================================ F-12　黎明（过场 + 自由走动）
  async function dawnIntro() {
    const st = 'dawn_fin', bg = 'cairo_street_dawn';
    const sign = at(st, bg, 'road_sign'), cross = at(st, bg, 'crossroad'), corner = at(st, bg, 'corner'), alley = at(st, bg, 'alley');
    party(['jotaro'], 'jotaro', ['avdol', 'iggy', 'kakyoin', 'joseph', 'polnareff']);
    await S.setStage(st, { x: sign[0] - 40, y: footY(st, 162), music: 'sad' });
    S.state('rise', 0);
    await S.animate(2, k => S.state('rise', k));
    S.mark('fin_dawn');
    place(S, 'jotaro', sign[0] - 40, footY(st, 162), 1);
    // 两辆 SPW 的车停在十字路口
    T.prop(S, 'spw_jeep', cross[0] - 30, footY(st, 162), { id: 'fin_jeep1' });
    T.prop(S, 'spw_jeep', cross[0] + 30, footY(st, 164), { id: 'fin_jeep2' });
    const med = S.spawn('npc_spw', cross[0] + 10, footY(st, 164), { id: 'fin_medic', team: 'npc', label: 'SPW 医护' });
    const jos = S.spawn('joseph', cross[0] + 30, footY(st, 164), { id: 'fin_joseph', team: 'npc', label: '乔瑟夫' });
    if (jos) { jos.play('lie'); jos.hold = true; }
    await S.narrate('天亮了。');
    // 阳光照到 @corner：布下的轮廓化成灰，往上飘散（远景）
    S.mark('fin_ash');
    S.fx('shatter', { src: 'prop:blanket', logical: 'idle', x: corner[0], y: corner[1] - 6, pieces: 48, dur: 1.4, tint_to: '#c9bda6' }, { life: 2.2 });
    S.fx('dust', { x: corner[0], y: corner[1] - 10, size: 16 }, { life: 2 });
    await S.wait(1.4);
    await S.say('npc_spw', '乔斯达先生没有心跳了！……但是，血还来得及。', { name: 'SPW 医护', actor: med });
    await S.say('jotaro', '……白金之星。');
    await S.summon('jotaro', { dur: .2 });
    S.standAct('jotaro', 'punch', { dx: 18, dur: .5 });
    S.sfx('heartbeat', .7);
    await S.narrate('心跳，再次响起。');
    S.mark('fin_joke');
    if (jos) { jos.play('idle'); jos.hold = false; }
    S.nameCard('joseph');
    await S.say('joseph', '你以为是乔瑟夫吗？是我 DIO 哒！', { expr: 'evil_tall' });
    await S.say('jotaro', '……再开这种玩笑，我真的会揍你。');
    await S.say('joseph', '哈、哈哈……开、开玩笑的嘛……');
    // 乔瑟夫回到队伍（黎明复活后不再战斗）；倒下时的 NPC 演员换成交给队伍的真实演员，别留下两个乔瑟夫
    const jx = jos ? jos.x : cross[0] + 30, jy = jos ? jos.y : footY(st, 164);
    if (jos) jos.remove = true;
    await S.join('joseph');
    place(S, 'joseph', jx, jy, 1);
    // 波鲁纳雷夫一瘸一拐走过来
    const pol = S.spawn('polnareff', alley[0], footY(st, 160), { id: 'fin_polnareff', team: 'npc', label: '波鲁纳雷夫' });
    if (pol) {
      pol.play('walk'); S.walk(pol, sign[0] - 70, footY(st, 162), { speed: 40, anim: 'walk' }).catch(G.cancelIgnore);
      // 自由走动时站在原地能搭话（⟳ 轮换两句）
      pol.talk = async s => s.say('polnareff', T.count('fin_pol') % 2
        ? '我的头被他打得好痛……不过，活着就好。'
        : '……阿布德尔、伊奇、花京院。我们，赢了。');
    }
    await S.wait(1.2);
    await S.say('polnareff', '……喂。你们两个，都还活着吧。');
    await S.say('jotaro', '……嗯。');
    // SPW 工作人员把钟楼指针交给承太郎（纪念品）
    const staff = S.spawn('npc_spw', sign[0] - 100, footY(st, 162), { id: 'fin_staff', team: 'npc', label: 'SPW 工作人员' });
    await S.say('npc_spw', '承太郎先生，这是从钟楼上找到的指针。……花京院先生最后打碎的那面钟。', { name: 'SPW 工作人员', actor: staff });
    await X.give(S, 'fin_clock_hand', { x: sign[0] - 100, y: footY(st, 162) - 20 });
  }

  // 自由走动：L.explore 会先 setStage（换图会清掉上一张图的演员），所以黎明 / 机场的 NPC 和道具
  //   必须在 setStage 之后才摆。这里照 L.explore 的流程重写一遍，多一个 place(S) 回调。
  async function exploreAt(S, stage, o = {}) {
    const st = G.STAGES[stage], flag = 'exit_' + stage; G.flags[flag] = false;
    st.hotspots = o.hotspots || []; st.npcs = [];
    st.onLook = o.onLook || (async (s, p) => s.say(p.cid, '……这里什么都没有。'));
    st.triggers = [{ x0: o.exitX != null ? o.exitX : st.x1 - 24, x1: st.x1 + 16, y0: 0, y1: 180,
      once: true, run: async () => { G.flags[flag] = true; } }];
    await S.setStage(stage, { x: o.x != null ? o.x : 48, y: 160 });
    if (o.place) await o.place(S);
    if (o.location) S.location(o.location, { y: 50 });
    T.memberTalk(o.talk || {});
    S.free(true); S.hint(o.hint || 'Q 切换队长，E 搭话，U 调查；沿路向右。', 8);
    await S.until(() => G.flags[flag] && !S.busy); S.free(false);
  }

  async function dawnExplore() {
    const st = 'dawn_fin', bg = 'cairo_street_dawn';
    const sign = at(st, bg, 'road_sign'), cross = at(st, bg, 'crossroad'), corner = at(st, bg, 'corner'), alley = at(st, bg, 'alley'), tower = A(bg, 'clock_tower');
    // 只有承太郎当队长；乔瑟夫 / 波鲁纳雷夫站着能搭话（不跟随、不再战斗）
    S.leadable('joseph', false, { look: 'gray', msg: '乔瑟夫站着休息。' });
    await exploreAt(S, st, {
      exitX: A(bg, 'exit')[0], x: sign[0] - 40, location: 'cairo',
      place: async () => {
        // 标记放在换图之后：放在 setStage 之前的话，截图/记录落在上一场（夜街）的收尾黑幕里
        S.mark('fin_explore');
        place(S, 'joseph', cross[0] + 30, footY(st, 164), -1);
        const pol = S.spawn('polnareff', sign[0] - 70, footY(st, 162), { id: 'fin_polnareff2', team: 'npc', label: '波鲁纳雷夫' });
        if (pol) pol.talk = async s => s.say('polnareff', T.count('fin_pol2') % 2
          ? '我的头被他打得好痛……不过，活着就好。'
          : '……阿布德尔、伊奇、花京院。我们，赢了。');
        T.prop(S, 'spw_jeep', cross[0] - 30, footY(st, 162), { id: 'fin_jeep3' });
        T.prop(S, 'spw_jeep', cross[0] + 30, footY(st, 164), { id: 'fin_jeep4' });
        const medic = S.spawn('npc_spw', cross[0] + 10, footY(st, 164), { id: 'fin_medic2', team: 'npc', label: 'SPW 医护' });
        if (medic) medic.talk = async s => s.say('npc_spw', '血已经输进去了。……他命真硬。', { name: 'SPW 医护', actor: medic });
      },
      talk: {
        joseph: s => s.say('joseph', T.count('fin_jos') % 2 ? '……我们，赢了啊。' : '荷莉……荷莉怎么样了？！快打电话！'),
      },
      onLook: async (s, p) => s.say(p.cid, '……太阳出来了。'),
      hotspots: [
        L.hot('sign_hole', sign[0], '路牌被拔走的地方', [], async s => s.narrate('路牌被拔走的地方，只剩一个坑。')),
        X.hot('fin_road_sign_bolt', sign[0] + 12, footY(st, 156), { label: '坑边掉着一颗螺丝', r: 16 }),
        L.hot('truck_wreck', corner[0] - 40, '撞进楼里的卡车', [], async s => s.narrate('卡车的车头整个扎进了墙里。')),
        L.hot('clock_tower', tower[0], '远处的钟楼', ['detail'],
          async s => s.narrate('钟面碎了。指针，停在那一刻。'),
          async s => s.say('jotaro', '……花京院。')),
      ],
      hint: '……该回家了。按住方向键走到右边，SPW 的车在那里。',
    });
  }

  // ================================================================ F-13　日本 · 第 50 天
  async function holly() {
    const st = 'bedroom_fin', bg = 'kujo_bedroom_morning';
    const bed = at(st, bg, 'bed'), win = A(bg, 'window');
    await S.setStage(st, { x: bed[0] - 40, y: footY(st, 164), music: 'ending' });
    S.location('kujo_day50');
    const hol = S.spawn('holly', bed[0], bed[1], { id: 'fin_holly', team: 'npc', label: '荷莉' });
    if (hol) S.pose(hol, 'bed', { freeze: 0 });
    S.mark('fin_holly');
    await S.wait(1.2);
    // 背上的荆棘化作光点从窗口散去
    for (let n = 0; n < 14; n++) S.fx('sparkles', { x: bed[0] - 8 + (n % 5) * 4, y: bed[1] - 30 - n * 3, size: 5 }, { life: 1.4 });
    S.sfx('sparkle', .5);
    await S.animate(1.2, k => { if (hol) hol.alpha = 1; });
    if (hol) { S.unpose(hol); hol.play('idle'); }
    await S.wait(.4);
    await S.say('holly', '承太郎……');
  }

  // ================================================================ F-14　开罗机场（最后一次自由走动）
  async function airportIntro() {
    const st = 'airport_fin', bg = 'airport';
    const arrive = at(st, bg, 'arrive'), bench = A(bg, 'benches'), win = at(st, bg, 'window');
    party(['jotaro', 'joseph', 'polnareff'], 'jotaro', ['avdol', 'iggy', 'kakyoin']);
    await S.setStage(st, { x: arrive[0], y: arrive[1], music: 'daily' });
    S.location('cairo_airport');
    place(S, 'jotaro', arrive[0], arrive[1], 1);
    place(S, 'joseph', bench[0][0], footY(st, bench[0][1]), -1);
    place(S, 'polnareff', win[0], footY(st, win[1]), 1);
    S.mark('fin_airport');
    await S.say('joseph', '荷莉已经醒了！刚才 SPW 打来电话——她醒了！我们回家！');
    await S.say('polnareff', '……太好了。');
  }

  async function airportExplore() {
    const st = 'airport_fin', bg = 'airport';
    const bench = A(bg, 'benches'), board = A(bg, 'board'), win = A(bg, 'window'), gate = A(bg, 'gate'), paris = A(bg, 'gate_paris');
    S.leadable('joseph', false, { look: 'gray', msg: '乔瑟夫在长椅上等。' });
    S.leadable('polnareff', false, { look: 'gray', msg: '波鲁纳雷夫在看停机坪。' });
    S.mark('fin_airport_free');
    await exploreAt(S, st, {
      exitX: gate[0], x: A(bg, 'arrive')[0], location: 'cairo_airport',
      // 三人站位照脚本：承太郎在门口、乔瑟夫坐 @benches[0]、波鲁纳雷夫在 @window 下面
      place: async () => {
        place(S, 'jotaro', A(bg, 'arrive')[0], footY(st, 164), 1);
        place(S, 'joseph', bench[0][0], footY(st, bench[0][1]), -1);
        place(S, 'polnareff', win[0], footY(st, win[1]), 1);
      },
      talk: {
        joseph: s => s.say('joseph', T.count('fin_air_j') % 3 === 1 ? '回到日本，第一件事——吃荷莉做的饭！'
          : T.count('fin_air_j2') % 2 ? '荷莉已经醒了！我们回家！' : '……五十天。说长也长，说短也短啊。'),
        polnareff: s => s.say('polnareff', T.count('fin_air_p') % 3 === 1 ? '阿布德尔、伊奇、花京院……这五十天，我一辈子都不会忘。'
          : T.count('fin_air_p2') % 2 ? '我回法国了。……先去看看雪莉，告诉她，哥哥做到了。' : '承太郎，你可别忘了我啊！'),
      },
      onLook: async (s, p) => s.say(p.cid, '……五十天。说长也长，说短也短啊。'),
      hotspots: [
        L.hot('board', board[0], '航班显示板', ['detail'],
          async s => { S.sfx('card_flip'); await s.narrate('东京、巴黎。两个方向，同一次告别。'); },
          async s => s.say('jotaro', '飞往东京的航班，开始登机了。')),
        X.hot('fin_boarding_pass', bench[1][0], footY(st, bench[1][1]), { look: ['detail'], label: '长椅上的登机牌',
          found: async s => s.say('jotaro', '……是我的。') }),
        L.hot('apron', win[0], '停机坪', ['detail'],
          async s => s.narrate('跑道另一端，飞机缓缓转向。'),
          async s => s.say('jotaro', '太阳升起来了。')),
        L.hot('gate_paris', paris[0], '往巴黎的登机口', [], async s => s.narrate('飞往巴黎的登机口。')),
      ],
      hint: '按 E 搭话，U 用替身调查；向右走到登机口（东京）。',
    });
  }

  // ================================================================ F-15　告别 + 片尾
  async function farewell() {
    const st = 'airport_fin', bg = 'airport';
    const gate = at(st, bg, 'gate'), paris = A(bg, 'gate_paris');
    await S.setStage(st, { x: gate[0] - 40, y: footY(st, 160), music: 'ending' });
    S.mark('fin_farewell');
    place(S, 'jotaro', gate[0] - 40, footY(st, 160), 1);
    place(S, 'joseph', gate[0] - 20, footY(st, 162), 1);
    place(S, 'polnareff', gate[0] - 60, footY(st, 162), 1);
    await S.say('polnareff', '那么——Au revoir！');
    await S.say('joseph', '波鲁纳雷夫，有空来纽约！……不，来日本也行！');
    await L.view(S, { bg: 'black', parts: [{ cid: 'scene:s20_hand', x: 160, y: 176, scale: 2 }] }, .9);
    await S.say('polnareff', '……谢谢你们。真的。');
    const pol = S.actor('polnareff');
    if (pol) {
      S.walk(pol, paris[0], footY(st, 162), { speed: 60, anim: 'walk' }).catch(G.cancelIgnore);
      await S.wait(1.2);
      pol.facing = 1; act(pol, 'idle', 800);
    }
    await L.view(S, { bg: 'black', parts: [{ cid: 'scene:s20_joseph_wave', x: 160, y: 176, scale: 2 }] }, .8);
    await S.say('joseph', '保重——！');
    await L.view(S, { bg: 'black', parts: [{ cid: 'scene:s20_jotaro_smile', x: 160, y: 176, scale: 2 }] }, .8);
    await S.say('jotaro', '……呀嘞呀嘞。');
    // 片尾：素材包没有独立的 ending.webm，结局由录制器录这一段，这里直接进制作名单 + 同人声明
    S.mark('fin_credits');
    await S.notice({ text: '星尘斗士的旅途，到此结束。\n原作：荒木飞吕彦《JOJO的奇妙冒险》\n同人游戏，仅供交流。角色、故事与音乐版权归原权利人。\n制作：悠一 × AI 协作。', minT: 3, auto: false });
    G.flags.completed = true;
    G.progress.finish();
    await S.tbc();
  }

  // ================================================================ 本章入口
  G.STORY.final = async function () {
    T.resetCounters();
    for (const key of ['dioGrowth', 'starWorld', 'completed']) delete F()[key];
    await M.ensureBg('_fin');
    S.party(['jotaro', 'joseph', 'kakyoin', 'polnareff', 'avdol', 'iggy'], { leader: 'jotaro' });
    await S.chapterCard('final');
    await S.run(async () => { await S.narrate('第四十九天，夜。'); });
    await S.run(stairs);
    await S.run(escape);
    await S.run(truckChase);
    await S.run(roofWeb);
    await S.run(message);
    await S.run(walkToward);
    // 三段连战走和试炼同一个工厂；剧情仍按每段一次 S.run，段 2 → 段 3 之间演“DIO 要血”
    await DioAllSrc.run(S, { trial: false, wrap: s => s, interlude: true });
    await S.run(finish);
    await S.run(dawnIntro);
    await dawnExplore();
    await S.run(holly);
    await S.run(airportIntro);
    await airportExplore();
    await S.run(farewell);
  };

  // ================================================================ 单战入口（G.DEV / 标题「挑战」）
  G.DEV = G.DEV || {};
  const devFight = phase => async S => {
    await M.ensureBg('_fin');
    S.party(['jotaro', 'polnareff', 'avdol', 'iggy'], { leader: 'jotaro' });
    await S.run(async () => { await dioFight(S, phase, DIO_RUN); });
  };
  G.DEV.finDio1 = devFight(1);
  G.DEV.finDio2 = devFight(2);
  G.DEV.finDio3 = devFight(3);
  G.DEV.finDioAll = async S => {
    await M.ensureBg('_fin');
    S.party(['jotaro', 'polnareff', 'avdol', 'iggy'], { leader: 'jotaro' });
    await DioAllSrc.run(S, DIO_RUN);
  };
  X.challenge({ id: 'b28d1_dio', chapter: 'final', title: 'VS DIO · 段 1（承太郎）', par: 150, run: S => G.DEV.finDio1(S) });
  X.challenge({ id: 'b28d2_dio', chapter: 'final', title: 'VS DIO · 段 2（承太郎）', par: 150, run: S => G.DEV.finDio2(S) });
  X.challenge({ id: 'b28d3_dio', chapter: 'final', title: 'VS DIO · 段 3（承太郎）', par: 180, run: S => G.DEV.finDio3(S) });
  // 通关后才出现的「DIO 连战」：extras 的 unlocked() 还不认 needClear，本轮只允许改本章文件，
  // 所以在这里给 unlocked 包一层（其它挑战照旧走原逻辑）。
  const unlocked0 = X.unlocked.bind(X);
  X.unlocked = def => (def && def.needClear ? !!(G.progress && G.progress.clear) : unlocked0(def));
  X.challenge({ id: 'b28d_all', chapter: 'final', title: 'DIO 连战', par: 420, needClear: true, run: S => G.DEV.finDioAll(S) });
  // 星尘试炼第 18 关（三段连战；队伍的 solo / 无队友由试炼的 wrap 处理）
  G.TRIAL_SRC['b28d_all'] = DioAllSrc;
})();
