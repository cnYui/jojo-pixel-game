// 第6章　阿拉伯 / 沙漠的太阳与梦（规划 §6.5；原著 166–173 话，第 17–21 天）
//   2026-10-18 按体验版精度重写（用户：“继续把整个 jojo 游戏做完……场景画面精细一些，玩法也多做一些”）。节拍表：docs\章节素材调研\ch6_阿拉伯_节拍表.md
//   机关沿用初版：骑骆驼（平衡）、太阳（热量 + 阴影 + 远处镜子穹顶的反光 → 弹石子）、死神13（梦 1 没有替身找小刀刻字 / 梦 2 带法皇入梦）；
//   这一版补自由走动（沙漠边、亚普林村、夜营）、过场、买飞机的砍价对话、三件纪念品，坐标都读重画后的背景 anchors。
//
//   流程：世界地图 → 沙漠边（车换骆驼；短暂自由走动）→ 骑骆驼 → 第二个太阳 → 第 12 战 → 阿拉伯·法兹「再起不能」→ 傍晚
//   → 亚普林村（自由走动：妇人托付婴儿、和商人砍价买塞斯纳）→ 机舱 → 第 13 战梦 1 → 惊醒、BABY STAND、坠机（坠毁章 3 → 4）
//   → 夜营（自由走动：没人信花京院；和三人都说过话后到篝火边带法皇入睡）→ 第 13 战梦 2 → 面具碎裂、婴儿交给 SPW → TBC
//
//   台词都是新写的（规划 §1.4）。克制处理（D10）：刻字只显示字；不做婴儿辅食“加料”；梦里被镰刀扫到只掉血。
'use strict';
(function () {
  const G = window.G, M = G.MID, T = G.TPL, W = G.world, I = G.input, px = G.px, F = () => G.flags, X = G.EXTRA;
  G.TRIAL_SRC = G.TRIAL_SRC || {};   // 各章末尾登记；试炼加载在 ch*.js 之后，这里只准备容器
  const pick = (key, arr) => arr[(T.count(key) - 1) % arr.length];
  const sayBy = (S, p, map) => S.say(p.cid, T.by(p, map));
  const lines = async (S, rows) => { for (const [who, text, expr] of rows) await S.say(who, text, expr ? { expr } : {}); };
  const hasSnd = n => !!(G.audio && G.audio.has && G.audio.has(n));
  const snd = (name, alt, o = {}) => { if (hasSnd(name)) G.audio.sfx(name, o); else if (alt) G.audio.sfx(alt, o); };
  const amb = (S, name, alt, vol) => { if (hasSnd(name)) S.ambient(name, vol); else if (alt) S.ambient(alt, vol * .6); };
  const calmStands = () => { for (const a of (G.party && G.party.members) || []) if (a.stand && a.stand.visible && a.stand.mode !== 'recall') a.stand.recall({ sfx: false }); };
  const follow = () => { if (G.party && G.party.rebuildFollow) G.party.rebuildFollow(); };
  function place(S, cid, x, y = 164, facing = 1) {
    const a = S.actor(cid); if (!a) return null;
    a.visible = true; a.follow = null; a.x = x; a.y = y; a.facing = facing; a.alpha = 1; a.scale = 1; a.z = 0; S.unpose(a);
    return a;
  }
  function party(S, leader = 'jotaro') { S.party(M.crew, { leader }); for (const a of G.party.members) a.scale = 1; }
  // 自由走动：M.explore 的提示固定 12 s，而脚本给这一章的提示是 8 / 10 s，所以照 M.explore 自己走一遍
  const roam = async (S, flag, hint, sec = 12) => { S.free(true); S.hint(hint, sec); await S.until(() => !!S.flags[flag] && !S.busy); S.free(false); };
  // 音乐：新曲没接进数据包就退回老曲（梦一要用 10-19 新加的 dream，没有就 tension）
  const hasMus = n => !!(G.D && G.D.audio && G.D.audio.music && G.D.audio.music[n]);
  const mus = (S, name, alt, fade = .5) => { if (hasMus(name)) S.music(name, fade); else if (alt) S.music(alt, fade); };

  // ---------------------------------------------------------------- 背景锚点（没有就用背景规格里的默认值）
  const bgA = (bg, k, d) => { const b = G.D && G.D.bg && G.D.bg[bg]; const v = b && b.anchors ? b.anchors[k] : null; return v != null ? v : d; };
  const DNd = { arrive: [60, 164], car: [30, 168], rocks: [[100, 166], [330, 166], [570, 166]],
    shade: [[86, 120, 140, 176], [316, 120, 370, 176], [556, 120, 610, 176]], skull: [210, 166], camels: [[250, 172], [450, 172]],
    // 10-19 新布局：第一块平沙地（法兹藏身处）在 x 160，第二块（逃过去的地方）在 x 530，骑骆驼终点在岩石 3 的影子里
    dome: [160, 147], dome2: [530, 147], ride_end: [560, 166] };
  const YVd = { arrive: [40, 164], camel_pen: [80, 156], stall: [160, 152], kids: [230, 164], mother: [292, 160], well: [350, 154], mosque: [410, 120],
    merchant: [470, 160], hangar: [500, 140], cessna: [585, 162], exit: [626, 162] };
  const CCd = { pilot: [64, 164], copilot: [96, 164], seats: [[150, 166], [196, 166], [242, 166], [288, 166]], baby: [270, 158],
    // 坐姿：脚点取椅子框的中心、y = 地板 153（sit 动作的锚点在脚下，屁股自然落在坐垫高度）
    seat_boxes: [[138, 116, 165, 153], [184, 116, 211, 153], [230, 116, 257, 153], [276, 116, 303, 153]],
    cockpit_seats: [[52, 118, 79, 153], [84, 118, 111, 153]] };
  const DCd = { arrive: [60, 160], toys: [[90, 162], [170, 162], [250, 162]], carousel: [56, 150], wheel: [98, 151], tent: [265, 134] };
  const NTd = { arrive: [60, 164], tent: [176, 156], cradle: [214, 164], campfire: [300, 162],
    // 10-19 背景验收：石凳拆成火两边两块，[3] 空着给花京院（6-14 坐下）
    seats: [[262, 166], [340, 166], [322, 174], [278, 174]], wreck: [540, 158] };
  const DN = k => bgA('desert_noon', k, DNd[k]);
  const YV = k => bgA('yaprin_village', k, YVd[k]);
  const CC = k => bgA('cessna_cabin', k, CCd[k]);
  const DC = k => bgA('dream_carnival', k, DCd[k]);
  const NT = k => bgA('desert_night', k, NTd[k]);
  const footY = (id, y) => { const st = G.STAGES[id]; return G.clamp(y, st.yMin + 2, st.yMax - 2); };
  // 背景还是旧画法（没有 shade 框）时，阴影就按“离岩石 21 px 以内”算（初版的判法）
  const shadeBoxes = () => { const b = G.D && G.D.bg && G.D.bg.desert_noon; return b && b.anchors && b.anchors.shade ? b.anchors.shade : null; };

  // ---------------------------------------------------------------- 纪念品
  X.souvenir({ id: 'ch6_desert_rose', chapter: 'ch6', name: '沙漠玫瑰', desc: '沙子和石膏结成的花瓣形结晶。沙漠里的人说，它是风开的花。', hint: '沙漠边，牛头骨旁的沙里（要眼力好的人）' });
  X.souvenir({ id: 'ch6_camel_bell', chapter: 'ch6', name: '驼铃', desc: '亚普林村骆驼栏里捡的铜铃。摇起来，声音能传很远。', hint: '亚普林村的骆驼栏' });
  X.souvenir({ id: 'ch6_altimeter', chapter: 'ch6', name: '停住的高度计', desc: '从坠毁的塞斯纳上拆下来的。指针停在 0。……乔瑟夫坠毁记录　4。', hint: '夜营，坠毁的塞斯纳旁边' });

  // ================================================================ 骑骆驼（小游戏，不会失败）
  //   骆驼每走一步身体晃一下：平衡条左右摆，在中间区按 J 稳住；偶尔一阵风（摆得更快、中间区更窄）；
  //   连续 3 次没稳住就摔下来（喜剧：thud，承太郎面无表情地爬回去），重来那一小段；走完到岩石 3 的影子里（@ride_end）。
  async function camelRide(S) {
    S.mark('ch6_camel');
    calmStands();
    // 6-04：先把队长放到 @camels[0]（自由走动时人可能停在任意位置，骑骆驼要从驼队那儿出发）
    const start = DN('camels')[0];
    const p = place(S, S.player.cid, start[0], footY('desert_ch6', start[1]), 1) || S.player;
    const others = M.crew.filter(c => c !== p.cid).map(c => S.actor(c)).filter(Boolean);
    others.forEach((a, i) => { a.x = Math.max(8, p.x - 24 - i * 22); a.y = footY('desert_ch6', start[1]); a.z = 0; a.follow = null; });
    const camel = M.prop(S, 'camel', p.x + 2, footY('desert_ch6', p.y + 1), { id: 'ride_camel' });
    const herd = others.map((a, i) => { const c2 = M.prop(S, 'camel', a.x, footY('desert_ch6', a.y + 1), { id: 'herd_camel' + i }); a.follow = null; a.z = 13; return c2; });
    p.z = 13;
    // 骆驼跟着人走（人坐在驼峰上，z 13）；每帧对齐，换图 / 结束就停
    let riding = true;
    T.tick(() => {
      if (!riding) return true;
      if (camel) { camel.x = p.x + 2; camel.y = footY('desert_ch6', p.y + 1); camel.facing = p.facing; }
      others.forEach((a, i) => { const c2 = herd[i]; if (c2) { c2.x = a.x; c2.y = footY('desert_ch6', a.y + 1); c2.facing = a.facing; } });
      return false;
    });
    await lines(S, [['joseph', '骆驼要坐稳！身体跟着它的步子晃……我也是第一次。'], ['polnareff', '你也是第一次？！']]);
    // 终点是 @ride_end（岩石 3 的影子里）；一步 62 px，从 @camels[0] 正好五步
    const goal = DN('ride_end')[0];
    let misses = 0, falls = 0, step = 0;
    while (p.x < goal) {
      const gust = step > 0 && step % 3 === 2;
      if (gust) { S.sfx('sand', .5); S.fx('dust', { x: p.x + 30, y: p.y - 8, n: 14 }); }
      // QTE 框放到画面上方（y 24），别挡住骑在骆驼上的人
      const ok = await S.timing({ label: gust ? '起风了！稳住（J）' : '跟着骆驼的步子保持平衡（J）', zone: gust ? [.40, .60] : [.36, .64], speed: gust ? 1.2 : .9, tries: 3, y: 24 });
      if (ok) {
        misses = 0; step++;
        const nx = Math.min(goal, p.x + 62);
        await Promise.all([S.walk(p, nx, p.y, { speed: 120 }), ...others.map((a, i) => S.walk(a, nx - 24 - i * 22, a.y, { speed: 120 }))]);
      } else if (++misses >= 3) {
        misses = 0; falls++;
        S.sfx('thud'); S.shake(2, .25); p.z = 0; S.pose(p, 'down');
        await S.wait(.5);
        await S.say(p.cid, T.by(p, { jotaro: '……', joseph: 'OH MY GOD！这骆驼在故意摔我！', kakyoin: '……失礼了。', polnareff: '哇啊！我的发型——！' }));
        S.unpose(p); p.z = 13;
        if (falls === 1) await S.say('polnareff', '……刚才那一小段，再来！');
      }
    }
    riding = false;
    p.z = 0; for (const a of others) a.z = 0;
    if (camel) camel.remove = true; for (const c2 of herd) if (c2) c2.remove = true;
    F().ch6CamelFalls = falls;
  }

  // ================================================================ 第 12 战：太阳（desert_ch6，desert_noon）
  //   两段（脚本 6-06）：第一段走到看得见 @dome 的地方、等反光投第一颗石子；第二段穹顶长腿跑到 @dome2，再投一颗结束。
  //   热量槽（不在阴影里每秒 +6%，阴影里 −18%；满 100 每秒掉 3 HP）；阴影 = 三块岩石的影子（背景 shade 框）、
  //   两头慢慢走的骆驼、车影、花京院撑的影；太阳每 3 s（第二段 2.5 s）射热线，每 12 s（第二段 8 s）来一次热浪；
  //   穹顶每 3 s（第二段 2 s）反光 1.2 s，反光且穹顶在画面里才能按 U 投石。
  // 放水可叠加：手工减免统一走 G.combat.assistK，第 1 档与原系数一致
  const sunHurt = (c, n) => M.damage(c, Math.round(n * G.combat.assistK(c, .6)));
  const sunHeat = (c, n) => { c.data.heat = G.clamp(c.data.heat + n * (c.assist ? .7 : 1), 0, 100); };
  function drawSun(P, d, t) {
    const cx = G.cam.x || 0, k = Math.floor(t * 12);
    // 第二个太阳（贴在天上不随镜头走），光芒 12 fps 步进
    const sx = 222, sy = 28;
    for (let i = 0; i < 12; i++) {
      const a = i * Math.PI / 6 + (k % 2) * .13, r0 = 14, r1 = 21 + ((i + k) % 3) * 2;
      px.line(P, sx + Math.cos(a) * r0, sy + Math.sin(a) * r0, sx + Math.cos(a) * r1, sy + Math.sin(a) * r1, '#fff1a0', .9);
    }
    px.disc(P, sx, sy, 12, '#ffcf3a'); px.disc(P, sx, sy, 8, '#fff6c8');
    // 镜子穹顶本体是道具（prop:mirror_dome，帧 0 平时 / 1 反光 / 2 裂开 / 3、4 跑），这里只画射向承太郎的细光束和第二段的白色十字
    if (d.flash > 0) {
      const dx = Math.round(d.domeX - cx), dy = DN('dome')[1];
      if (dx > -30 && dx < 350) {
        px.line(P, dx - 4, dy - 6, Math.round(d.px - cx), d.py - 30, '#fff8d0', .35);
        if (d.phase >= 2) {
          const b = Math.floor(t * 20) % 2;
          px.rect(P, dx - 1, dy - 13, 3, 9, '#ffffff', b ? .9 : .45);
          px.rect(P, dx - 5, dy - 10, 11, 3, '#ffffff', b ? .9 : .45);
        }
      }
    }
    for (const xx of d.camels) px.ellipse(P, xx - cx - 22, 156, xx - cx + 22, 175, '#493434', null, 1, .45);
    if (!d.boxes) for (const xx of [30, ...DN('rocks').map(r => r[0])]) px.ellipse(P, xx - cx - 22, 156, xx - cx + 22, 175, '#493434', null, 1, .55);
    if (d.cover > t) { const x = Math.round(d.px - cx); px.ellipse(P, x - 16, d.py - 4, x + 16, d.py + 6, '#2a5a3a', null, 1, .5); }
    for (const z of d.scorches) px.ellipse(P, z.x - cx - 12, 155, z.x - cx + 12, 176, '#5a2917', null, 1, .7);
    if (d.heat > 50 && G.FX.heat_haze) G.FX.heat_haze(P, t, 96, 150, { amp: (d.heat - 50) / 35 });
    // 热浪预警：画面四边一圈 4 px 黄光，alpha 在 .2–.5 之间按 0.5 s 一次呼吸
    if (d.waveWarn > 0) {
      const a = .2 + .3 * (.5 + .5 * Math.sin(t * Math.PI * 4));
      px.rect(P, 0, 0, P.w, 4, '#ffe08a', a); px.rect(P, 0, P.h - 4, P.w, 4, '#ffe08a', a);
      px.rect(P, 0, 0, 4, P.h, '#ffe08a', a); px.rect(P, P.w - 4, 0, 4, P.h, '#ffe08a', a);
    }
  }
  const inShade = (d, p, c) => {
    const boxes = d.boxes;
    if (boxes && boxes.some(b => p.x >= b[0] && p.x <= b[2] && p.y >= b[1] && p.y <= b[3])) return true;
    if (!boxes && [30, ...DN('rocks').map(r => r[0])].some(x => Math.abs(p.x - x) < 21)) return true;
    if (d.camels.some(x => Math.abs(p.x - x) < 18) || Math.abs(p.x - DN('car')[0]) < 22) return true;
    return d.cover > c.t;
  };
  // 投中一次：第一颗石子让镜子裂开、穹顶长腿跑到 @dome2；第二颗石子把镜子打碎（= 胜）
  async function sunHit(s, c) {
    const d = c.data, dy = DN('dome')[1];
    d.hits = (d.hits || 0) + 1;
    d.flash = 0;
    if (d.hits === 1) {
      s.fx('crack', { x: d.domeX, y: dy - 9, size: 18 }, { life: 1.6 });
      snd('glass_break', null, { vol: .6 });
      s.word('ピシッ', d.dome);
      s.bark(null, '哇啊啊啊！被、被发现了？！', { name: '？？？', dur: 2.4 });
      d.phase = 2; d.domeMoving = 1;
      let puff = -1;
      await s.animate(3.5, k => {
        if (!d.dome) return;
        d.dome.x = G.lerp(DN('dome')[0], DN('dome2')[0], k);
        d.domeX = d.dome.x;
        // 帧 3 / 4 每 0.15 s 交替（跑），一路扬尘
        const n = Math.floor(k * 3.5 / .15);
        d.dome.frozen = n % 2 ? 4 : 3;
        if (n !== puff) { puff = n; s.fx('dust', { x: d.domeX - 8, y: dy - 2, n: 3 }); }
      });
      d.domeMoving = 0; d.domeX = DN('dome2')[0];
      if (d.dome) { d.dome.x = d.domeX; d.dome.frozen = 2; }
      return;
    }
    // 第二颗石子：碎掉的镜子（帧 2 是裂开的镜子）
    s.fx('shatter', { src: 'prop:mirror_dome', logical: 'idle', frame: 2, x: d.domeX, y: dy - 9, pieces: 26 }, { life: 1.1 });
    snd('glass_break', null, { vol: .8 });
    s.shake(3, .3);
    if (d.dome) d.dome.visible = false;
    c.end();
  }
  const sunSpec = () => ({ id: 'b12_sun', lead: 'jotaro', swap: false, par: 60, coverage: false,
    arena: [0, 640], music: 'battle', vs: 'sun',
    // 6-05 站位：乔瑟夫、波鲁纳雷夫、花京院留在岩石 3 后面（不参战，只喊热）
    bench: { mode: 'stay', at: { joseph: [DN('rocks')[2][0] - 4, 166], polnareff: [DN('rocks')[2][0] + 14, 166], kakyoin: [DN('rocks')[2][0] + 30, 166] } },
    failText: '……太阳……太近了……',
    kitOverride: Object.fromEntries(M.crew.map(cid => [cid, {
      special: { need: 0, prompt: '反光！U 找准方向，J 投石', window: c => c.data.flash > 0 && c.data.domeSeen,
        async run(s, p, c) { await M.busy(c, async () => {
          const d = c.data;
          // 第二段穹顶在跑的时候准星会晃（drift 18），停下后不晃；放水时瞄准圈 +4
          const ok = await s.aim({ label: '方向键对准反光，J 投石', throw: true, time: 2.5,
            r: 12 + (c.assist ? 4 : 0), start: [36, -20], drift: d.domeMoving ? 18 : 0, jitter: 0 });
          if (ok) await sunHit(s, c);
          else { d.flash = 0; s.hint('投偏了！先躲进阴影，等下次反光。', 4); sunHurt(c, 14); }
        }); } },
    }])),
    testHint: c => ({ heat: c.data.heat, shaded: c.data.shaded, phase: c.data.phase, flash: c.data.flash,
      domeX: c.data.domeX, mirrorX: c.data.domeX, domeSeen: c.data.domeSeen, domeMoving: !!c.data.domeMoving,
      waveIn: c.data.waveIn, hits: c.data.hits }),
    tick(c, dt) {
      const d = c.data, p = c.player;
      d.px = p.x; d.py = p.y;
      if (d.flash > 0) {
        d.flash = Math.max(0, d.flash - dt);
        // 反光窗口一过就回到「平时」的帧（第二段是裂开的帧 2）
        if (d.flash === 0 && d.dome) d.dome.frozen = d.phase >= 2 ? 2 : 0;
      }
      const cam = DN('camels');
      d.camels = [cam[0][0] + Math.sin(c.t * .4) * 70, cam[1][0] + Math.cos(c.t * .45) * 70];
      d.camelActors.forEach((a, i) => { if (a) { const nx = d.camels[i]; a.facing = nx > a.x ? 1 : -1; a.x = nx; } });
      const cx = G.cam.x || 0;
      d.domeSeen = d.domeX >= cx + 10 && d.domeX <= cx + 310;
      d.shaded = inShade(d, p, c);
      d.heat = G.clamp(d.heat + (d.shaded ? -18 : 6) * dt, 0, 100);
      // 背景热浪层从开战起就开着（6-06 重试复原 heat = 1），热量到 50% 只是加强画面里的 heat_haze
      if (d.heat >= 50) G.S.state('heat', 1);
      M.every(d, 'drain', dt, 1, () => { if (d.heat >= 100) M.drain(c, 3); });
      // 热线：第一段每 3 s 一道；第二段每 2.5 s 两道（脚下 + 前方 30 px）
      M.every(d, 'ray', dt, d.phase >= 2 ? 2.5 : 3, () => {
        const beam = x => {
          c.hazard({ shape: 'rect', x0: x - 8, x1: x + 8, y0: 142, y1: 179, warn: 40 / 60, dur: .5,
            dmg: Math.round(14 * G.combat.assistK(c, .6)), once: true, guard: 'none', fxActive: 'sun_ray',
            sfx: hasSnd('heat_beam') ? 'heat_beam' : 'fire_burst' });
          d.scorches.push({ x, born: c.t + 40 / 60 });
        };
        beam(p.x);
        if (d.phase >= 2) beam(G.clamp(p.x + p.facing * 30, 8, 632));
      });
      // 热浪：到点前 2 s 预警（四边黄光 + 大字 + 预警声），到点不在阴影里就吃伤害
      M.every(d, 'waveT', dt, d.phase >= 2 ? 8 : 12, () => {
        d.waveWarn = 2;
        G.ui.hint('热浪！躲进阴影！', 2);
        snd('heat_wave', 'fire_burst', { vol: .3 });
      });
      if (d.waveWarn > 0) {
        d.waveWarn = Math.max(0, d.waveWarn - dt);
        if (d.waveWarn === 0) {
          if (inShade(d, p, c)) G.ui.hint('躲过去了。', 1.5);
          else { sunHurt(c, 18); sunHeat(c, 30); snd('heat_wave', 'fire_burst', { vol: .8 }); G.S.shake(2, .3); }
        }
      }
      d.waveIn = d.waveWarn > 0 ? d.waveWarn : Math.max(0, (d.phase >= 2 ? 8 : 12) - d.waveT);
      // 反光：穹顶换帧 1，0.5 s 内画光束（drawSun），1.2 s 内可以按 U；跑动途中不闪（帧 3/4 是腿）
      M.every(d, 'flashT', dt, d.phase >= 2 ? 2 : 3, () => {
        if (d.domeMoving) return;
        d.flash = 1.2;
        if (d.dome) d.dome.frozen = 1;
        G.S.fx('glint', { x: d.domeX, y: DN('dome')[1] - 6, size: 12 });
      });
      M.every(d, 'coverT', dt, 20, () => { d.cover = c.t + 3; G.S.word('法皇撑影！', G.party.get('kakyoin')); });
      M.every(d, 'shout', dt, 9, () => { const who = G.party.get(d.shoutI++ % 2 ? 'polnareff' : 'joseph'); if (who) G.uifx.sfx(d.shoutI % 2 ? '好热！！' : '要化了……', who); });
      d.scorches = d.scorches.filter(z => c.t - z.born < 5);
      M.every(d, 'scorchDmg', dt, 1, () => { if (d.scorches.some(z => c.t >= z.born && Math.abs(p.x - z.x) < 14)) M.drain(c, 2); });
    },
  });
  async function sunFight(S) {
    const spec = sunSpec();
    await M.objectFight(S, spec, c => {
      // 所有机关状态都在这里复原（重试从头开始：穹顶回到 @dome、第一段、热量 0、焦地清空）
      Object.assign(c.data, { phase: 1, heat: 0, flash: 0, cover: 0, camels: DN('camels').map(v => v[0]), scorches: [],
        domeX: DN('dome')[0], domeMoving: 0, hits: 0, waveWarn: 0, waveIn: 12, shaded: false, domeSeen: false,
        boxes: shadeBoxes(), shoutI: 0, px: 0, py: 0 });
      // 新背景把车和岩石画进底图（导出了 shade 框），旧背景才摆道具
      if (!c.data.boxes) {
        for (const [x, y] of DN('rocks')) c.spawn({ cid: 'prop:rock', x, y, team: 'object', hp: 9999, untargetable: true });
        c.spawn({ cid: 'prop:car', x: DN('car')[0], y: DN('car')[1], team: 'object', hp: 9999, untargetable: true });
      }
      c.data.camelActors = DN('camels').map(([x, y]) => c.spawn({ cid: 'prop:camel', x, y, team: 'object', hp: 9999, untargetable: true }));
      // 镜子穹顶：5 帧道具（0 平时 / 1 反光 / 2 裂开 / 3、4 跑）
      c.data.dome = c.spawn({ cid: 'prop:mirror_dome', x: DN('dome')[0], y: DN('dome')[1], team: 'object', hp: 9999, untargetable: true });
      if (c.data.dome) c.data.dome.frozen = 0;
      G.S.state('heat', 1);
      M.pixel('sun_sky', P => drawSun(P, c.data, c.t));
      M.ui(S, g => {
        const d = c.data;
        const line2 = d.phase >= 2
          ? (d.domeMoving ? '穹顶跑了！追上去！' : 'U 瞄准那面破镜子！')
          : (d.domeSeen ? '反光！U 瞄准！' : '找到反光的地方……');
        M.hud(g, ['热量 ' + Math.round(d.heat) + '%　' + (d.shaded ? '在阴影里' : '快找阴影！'), line2]);
      });
      S.hint('躲进阴影避开热浪；看到反光就按 U 投石。', 6);
    });
  }

  // ================================================================ 第 13 战：死神13（dream_ch6，dream_carnival）
  //   梦 1（目标段）：没有替身（J 伤 0）；3 个玩具箱里随机一个有小刀（6-11），E 刻字；40 s 内没找到也会自动刻字醒来。
  //   梦 2：带着法皇；HP 1000；每 10 s 换一次梦（棋盘陷阱 key checker / 木马冲撞）；J3 触须网缠住它 0.5 s；四拍「LA」后横扫。
  // 梦一的小刀随机放在三个玩具箱之一（6-11）；重试重抽，所以放在模块变量里、由 init 每回合重掷
  let dreamKnifeBox = 0;
  const dream1Spec = () => ({ id: 'b13a_death13', lead: 'kakyoin', swap: false, playerMinHp: 1, losable: false, coverage: false, bench: 'hide', rank: false,
    music: hasMus('dream') ? 'dream' : 'tension',
    kitOverride: { kakyoin: { combo: ['DREAM_FIST', 'DREAM_FIST', 'DREAM_FIST'], special: null, rush: null } },
    tick(c) {
      const p = c.player, h = W.stage.hotspots.find(z => Math.abs(z.x - p.x) < 25);
      // 找到小刀后在哪儿按 E 都能刻字；没找到时 E 查身边的玩具箱
      if (I.hit('ok') && !c.data.cine) {
        if (G.S.flags.dreamKnife) { I.consume('ok'); M.task(c, async () => { G.S.flags.engraved = true; snd('slash', 'metal_scrape', { vol: .7 }); await G.S.say(null, 'BABY STAND'); }); }
        else if (h) { I.consume('ok'); M.task(c, () => h.use(G.S, h, p)); }
      }
      if (G.S.flags.engraved) c.end();
      // 梦一按设计是目标段；超时刻字醒来，梦二才承担可失败的战斗。
      if (c.t >= 40 && !G.S.flags.engraved && !c.data.cine) M.task(c, async () => {
        G.S.flags.dreamKnife = true; G.S.flags.engraved = true; await G.S.say(null, 'BABY STAND'); c.end();
      });
    },
    testHint: () => ({ knife: !!G.S.flags.dreamKnife, engraved: !!G.S.flags.engraved, knifeBox: dreamKnifeBox }),
  });
  async function dreamOne(S) {
    S.party(['kakyoin'], { leader: 'kakyoin' });
    await M.scene(S, 'dream_ch6', st => {
      st.state = Object.assign({}, st.state, { checker: 0, dark: 0 });
      st.hotspots = DC('toys').map(([x], i) => M.hot('toy' + i, x, '玩具箱', ['detail', 'peek'], '只有玩具。', async s => {
        if (i === dreamKnifeBox) { s.flags.dreamKnife = true; s.sfx('metal_scrape'); await s.say('kakyoin', '一把小刀……趁醒来之前，在手臂上留下记号！（再按 E）'); }
        else await s.say('kakyoin', pick('c6toy', ['箱子里只有玩具。另找一只。', '……全是小丑的玩偶。不是这个。']));
      }));
    }, DC('arrive')[0], 'kakyoin');
    mus(S, 'dream', 'tension', .4);
    await lines(S, [['kakyoin', '这里是……游乐园？法皇……召不出来？'], ['death13', 'LALI-HO！欢迎光临！这里是我的梦！']]);
    S.mark('b13a_death13');
    await M.objectFight(S, dream1Spec(), c => {
      S.flags.dreamKnife = false; S.flags.engraved = false;
      // 梦一没有替身：有替身就收起来（重试时 resetActor 可能又建出来）
      if (c.player.stand) c.player.stand.hide();
      dreamKnifeBox = Math.floor(Math.random() * 3);
      for (const [x, y] of DC('toys')) c.spawn({ cid: 'prop:toy_box', x, y, team: 'object', hp: 9999, untargetable: true });
      c.spawn({ cid: 'death13', boss: true, hp: 9999, x: 240, y: 158, minHp: 9999 });
      M.ui(S, g => M.hud(g, [S.flags.dreamKnife ? '拿到小刀了：按 E 在手臂上刻字！' : 'E 查玩具箱，找出小刀', '四拍「LA」之后镰刀横扫：L 挡 / K 闪']));
    });
  }
  // 棋盘陷阱：读背景导出的深格矩形（@checker_dark，x1 / y1 不含；覆盖 y 135–177），
  //   只取落在可走带里的（y1 > 140，y0 夹到 140 —— 陷阱紫光也从 140 起）
  function checkerTraps(c) {
    const rects = bgA('dream_carnival', 'checker_dark', null);
    const list = Array.isArray(rects) ? rects.filter(r => r[3] > 140) : [];
    if (!list.length) {
      // 旧数据没有深格表：退回 8 个方块（机关不能整个消失）
      // 放水时这类剧情危险区没有 owner，引擎的放水倍率不会作用，所以这里手工乘
      for (let i = 0; i < 8; i++) c.hazard({ shape: 'rect', x0: i * 40, x1: i * 40 + 20, y0: 145 + (i % 2) * 15, y1: 160 + (i % 2) * 15, warn: .6, dur: .25, dmg: Math.round(6 * G.combat.assistK(c, .6)), once: true, guard: 'none' });
      return;
    }
    // 放水时这类剧情危险区没有 owner，引擎的放水倍率不会作用，所以这里手工乘
    for (const [x0, y0, x1, y1] of list) c.hazard({ shape: 'rect', x0, x1, y0: Math.max(140, y0), y1, warn: .6, dur: .25, dmg: Math.round(6 * G.combat.assistK(c, .6)), once: true, guard: 'none' });
  }
  // 木马冲撞：在花京院那一行（y ± 7）预警 0.6 s，然后木马道具从画面左边 0.5 s 冲到右边
  function carouselRush(c) {
    const y = c.player.y;
    // 放水时这类剧情危险区没有 owner，引擎的放水倍率不会作用，所以这里手工乘
    c.hazard({ shape: 'rect', x0: 0, x1: 320, y0: y - 7, y1: y + 7, warn: .6, dur: .5, dmg: Math.round(14 * G.combat.assistK(c, .6)), once: true, guard: 'none' });
    M.task(c, async () => {
      await G.wait(.6);
      const h = c.spawn({ cid: 'prop:carousel_horse', x: -18, y, team: 'object', hp: 9999, untargetable: true });
      if (!h) return;
      let puff = -1;
      await G.S.animate(.5, k => {
        if (h.remove) return;
        h.x = G.lerp(-18, 338, k);
        h.frozen = Math.min(2, Math.floor(k * 5));      // 3 帧跑动 ≈ 10 fps
        const n = Math.floor(k * 5);
        if (n !== puff) { puff = n; G.S.fx('dust', { x: h.x - 10, y: y - 2, n: 2 }); }
      });
      h.remove = true;
    });
  }
  // 梦境塌缩：两边变黑色虚空，站在 x < 68 / x > 252 里每秒 −4（背景 dark 同时亮）
  function startCollapse(c) {
    const d = c.data;
    d.collapse = true;
    G.S.state('dark', 1);
    G.S.word('梦要醒了……！', c.boss);
    G.S.shake(2, .4);
  }
  // K.death13.brain 的两处改动（塌缩后只在 100–220 之间飘、放水时四拍改五拍）按实施文档本该在引擎里做；
  //   实施方只改本章文件，所以这里照同一套节拍重写一份。规划方在引擎里改好后可以删掉这段覆盖。
  function death13Brain(e, dt, c) {
    if (!dt) return true;
    const p = c.player, d = e.mem, amp = c.data && c.data.collapse ? 60 : 104, need = c.assist ? 5 : 4;
    e.x = 160 + Math.sin(c.t * .65) * amp; e.z = 12 + Math.sin(c.t * 2) * 8;
    if (e.rootT > 0) return true;
    d.beat = (d.beat || 0) + dt;
    if (d.beat >= .3556 && (d.n || 0) < need) { d.beat -= .3556; d.n = (d.n || 0) + 1; G.S.word('LA', e); }
    if (d.n === need) {
      d.after = (d.after || 0) + dt;
      if (d.after >= .2) {
        c.hazard({ shape: 'rect', x0: 0, x1: 320, y0: p.y - 9, y1: p.y + 9, warn: 0, dur: .1, dmg: 18, once: true,
          guard: 'normal', parry: true, fxActive: 'scythe_sweep', owner: e });
        e.play('swing'); d.n = 0; d.after = 0; d.beat = -1.3;
      }
    }
    return true;
  }
  const dream2Spec = () => ({ id: 'b13b_death13', lead: 'kakyoin', swap: false, bench: 'hide', par: 90, vs: 'death13', music: 'battle',
    arena: [8, 312], failText: '……梦里……也会痛……',
    testHint: c => ({ phase: c.data.room, rooted: !!(c.boss && c.boss.rootT > 0), collapse: !!c.data.collapse,
      roomIn: Math.max(0, 10 - (c.data.tRoom || 0)) }),
    tick(c, dt) {
      const d = c.data;
      d.tRoom = (d.tRoom || 0) + dt;
      if (d.tRoom >= 10) {
        d.tRoom = 0;
        d.room = (d.room + 1) % 2;
        G.S.word(d.room ? '木马！' : '棋盘！', c.boss);
        G.S.state('checker', d.room ? 0 : 1);
        if (d.room) carouselRush(c); else checkerTraps(c);
      }
      if (!d.collapse && c.boss && !c.boss.dead && c.boss.hp <= c.boss.maxHp * .3) startCollapse(c);
      if (d.collapse) M.every(d, 'voidT', dt, 1, () => { const p = c.player; if (p.x < 68 || p.x > 252) M.drain(c, 4); });
      if (d.boss && (d.boss.dead || d.boss.hp <= 0)) c.end();
    },
  });
  // o 由工厂传：只有剧情路线显式传 o.trial = false（原来的队伍 / 台词 / 赢后演出全保留）；
  // 其余情况队伍由试炼统一设置，这里只布景 + 打这一场，不演台词
  async function death(S, o = {}) {
    const story = o.trial === false;
    if (story) S.party(['kakyoin'], { leader: 'kakyoin' });
    await M.scene(S, 'dream_ch6', st => { st.state = Object.assign({}, st.state, { checker: 0, dark: 0 }); }, DC('arrive')[0], story ? 'kakyoin' : null);
    if (story) {
      await S.summon('kakyoin');
      await lines(S, [['death13', 'LALI-HO？……那、那是什么？！'], ['kakyoin', '这次，我带着法皇进入了梦。']]);
      S.mark('b13b_death13');
    }
    let boss = null;
    await M.objectFight(S, o.wrap ? o.wrap(dream2Spec()) : dream2Spec(), c => {
      // 重试复原：换梦计时、塌缩、背景 checker / dark 全部归零
      c.data.room = 0; c.data.tRoom = 0; c.data.collapse = false;
      G.S.state('checker', 0); G.S.state('dark', 0);
      boss = c.data.boss = c.spawn({ cid: 'death13', boss: true, hp: 1000, x: 230, y: 160 });
      // 引擎 K.death13 的 brain 写死了漂移 104 px；梦境塌缩后要改成 100–220（±60）、放水时横扫前多一拍。
      //   这属于引擎改动（不在本章可改范围），这里按同一套节拍覆盖一份，规划方改进引擎后可以删掉。
      if (c.data.boss) c.data.boss.brain = death13Brain;
      // 塌缩的黑边：两边各 60 px 的黑色虚空，边缘抖 1 px
      M.pixel('dream_void', P => {
        const d = c.data;
        if (!d.collapse) return;
        const j = Math.floor(c.t * 12) % 2;
        px.rect(P, 0, 0, 60 + j, P.h, '#0a0612', .85);
        px.rect(P, P.w - 60 - j, 0, 60 + j, P.h, '#0a0612', .85);
      });
      M.ui(S, g => M.hud(g, ['J 三下第三下铺触须网，缠住它再打', c.data.collapse ? '梦在塌缩：别站到黑暗里！' : '四拍「LA」之后镰刀横扫：L 挡 / K 闪']));
      c.on('hit', info => { if (info.t === c.boss && info.move && info.move.tag === 'net') c.boss.rootT = .5; });
    });
    // 6-14 赢：触须缠满死神13 → 面具裂开 → 淡出
    //   （boss 打完会被引擎收掉 remove，但坐标还在，特效照它最后的位置放）
    if (boss && story) {
      // 法皇的丝线从花京院手上缠到死神13身上（绿色触须特效 + 音效）
      const me = S.actor('kakyoin') || boss;
      S.fx('tendrils', { pts: [[[me.x, me.y - 24], [boss.x - 10, boss.y - 30]], [[me.x, me.y - 20], [boss.x + 8, boss.y - 22]]], colour: '#50e890', grow: .3, wiggle: 1 }, { life: 1.2 });
      snd('hiero_tentacle', 'vine', { vol: .7 });
      await S.say('kakyoin', '梦里也好，现实也好——法皇之绿，捆住它！');
      S.fx('crack', { x: boss.x, y: boss.y - 30, size: 20 });
      await S.fadeOut(.4);
    }
    S.state('checker', 0); S.state('dark', 0);
  }
  // 6-14 第 1 步：篝火边召出法皇、入睡（挑战入口从梦二开始，所以单独拿出来）
  async function campSleep(S) {
    // 四个人都在场（夜营刚结束），花京院站起来走到空着的那块石凳坐下再召法皇
    party(S, 'kakyoin');
    const seats = NT('seats');
    const me = place(S, 'kakyoin', seats[3][0], footY('camp_ch6', seats[3][1]), 1);
    if (me) { me.z = 0; S.pose(me, 'sit'); }
    for (const [cid, at, f] of [['jotaro', seats[0], 1], ['joseph', seats[1], -1], ['polnareff', seats[2], -1]]) {
      const a = place(S, cid, at[0], footY('camp_ch6', at[1]), f);
      if (a) { a.z = 0; S.pose(a, 'sit'); }
    }
    await S.say('kakyoin', '法皇之绿……这一次，跟我一起睡。');
    await S.summon('kakyoin');
    await S.fadeOut(.6);
    // 淡出以后才解除坐姿：不然进梦的地图时 hold 还在，队长动不了
    if (me) S.unpose(me);
  }

  // ================================================================ 沙漠边（desert_ch6）：车换骆驼
  async function desertArrive(S) {
    party(S);
    // 新背景把车画进底图了（导出过 shade 框就算新背景），旧背景才摆车道具
    const bgCar = !!shadeBoxes();
    await M.scene(S, 'desert_ch6', st => {
      st.state = Object.assign({}, st.state, { heat: 0, dusk: 0 });
      const [kx, ky] = DN('skull'), [cx2, cy2] = DN('car'), [dx2] = DN('dome');
      // 顺序按 x 排：平沙地 160 → 牛头骨 210 → 骆驼 250（出口紧跟在旁边）→ 车 38（只是闲聊，放最后）。
      //   测试器按这个顺序挨个走过去按 E，出口前面不留长距离，免得半路「盲按」把出口记成已完成。
      st.hotspots = [
        // 平沙地（6-03 新）：太阳战的伏笔。E 是旁白，U 按队长分两句，两句都算「看见了」→ ch6DomeHint（不必须）
        Object.assign(M.hot('flat_sand', dx2, '平沙地', ['detail', 'peek'], '',
          async s => s.say(null, '地平线前的一小块平沙地。'),
          async (s, h, p) => {
            s.flags.ch6DomeHint = true;
            if (p.cid === 'kakyoin') await s.say('kakyoin', '触须伸过去之前……沙子的反光，晃了一下。');
            else await s.say('jotaro', '……这块沙地的后沿，直得像用尺子画的。');
          }), { y: footY('desert_ch6', 150) }),
        M.hot('skull', kx, '牛头骨', ['nensha'], '', async (s, h, p) => sayBy(s, p, { joseph: '……沙漠里的标志。前面的路，不好走啊。', _: '被太阳晒白的牛头骨。' }),
          async s => { await s.photo({ frames: [0, 1, 2], hold: 1 }); await s.say('joseph', '念写……照片上只有沙子。太阳太亮了，什么都看不清。'); }, footY('desert_ch6', ky)),
        X.hot('ch6_desert_rose', kx + 16, footY('desert_ch6', ky + 2), { look: ['detail'], found: async s => s.say('jotaro', '……沙里有东西。石头开成了花的样子。') }),
        // 出口不挂替身调查标签：U 在这里没用，挂了只会让人多跑几趟 U
        Object.assign(M.exit('camels', DN('camels')[0][0], '骆驼（出发）', 'ch6Ride'), { tags: [] }),
        M.hot('car', cx2 + 8, '车', [], '', async (s, h, p) => sayBy(s, p, { joseph: '车就留在这里，有人会来取。……这次一点都没撞坏！', _: '众人开来的车，停在沙漠边上。' }), null, footY('desert_ch6', cy2)),
      ];
      st.onLook = async (S2, p) => S2.say(p.cid, T.by(p, { jotaro: '……热。', _: '……太阳太亮了，看不清远处。' }));
    }, DN('arrive')[0], 'jotaro');
    S.location('arabia');
    const camels = DN('camels').map(([x, y], i) => M.prop(S, 'camel', x, footY('desert_ch6', y), { id: 'wait_camel' + i }));
    if (!bgCar) M.prop(S, 'car', DN('car')[0], footY('desert_ch6', DN('car')[1]), { id: 'parked_car' });
    await lines(S, [['joseph', '阿拉伯沙漠！车开不进去了，从这里开始换骆驼。'], ['joseph', '这回用骆驼，绝对不会坠机！'], ['polnareff', '……骆驼也会摔的吧？'], ['kakyoin', '水和地图都备好了。天黑之前，要赶到下一片绿洲。']]);
    T.memberTalk({
      joseph: async s => s.say('joseph', pick('c6deJo', ['骆驼可是沙漠之舟！', '帽子戴好，正午的太阳会把人晒晕。'])),
      kakyoin: async s => s.say('kakyoin', pick('c6deKa', ['这么大的沙漠……连一只鸟都没有。', '脚印一会儿就被风吹平了。'])),
      polnareff: async s => s.say('polnareff', pick('c6dePo', ['热死了……我的发胶要化了。', '骆驼在冲我吐口水！'])),
      jotaro: async s => s.say('jotaro', pick('c6deJt', ['……热。', '……'])),
    });
    follow();
    T.goal(S, { x: DN('camels')[0][0], y: footY('desert_ch6', DN('camels')[0][1]), h: 56, label: '骆驼', delay: 40, every: 20, done: () => !!F().ch6Ride, text: '骆驼在等着出发。' });
    await roam(S, 'ch6Ride', '沙漠边：E 调查，U 替身调查；走到骆驼旁边按 E 出发。', 8);
    for (const c2 of camels) if (c2) c2.remove = true;
  }
  async function sunScene(S) {
    calmStands();
    await S.wait(.4);
    // 6-05 站位：骆驼趴下、众人下来；队长在 @ride_end，另外三人在岩石 3 的阴影里
    const re = DN('ride_end'), r3 = DN('rocks')[2];
    place(S, S.player.cid, re[0], footY('desert_ch6', re[1]), 1);
    place(S, 'joseph', r3[0] - 4, footY('desert_ch6', r3[1]), 1);
    place(S, 'polnareff', r3[0] + 14, footY('desert_ch6', r3[1]), 1);
    place(S, 'kakyoin', r3[0] + 30, footY('desert_ch6', r3[1]), 1);
    S.sfx('sting_shock', .6);
    await lines(S, [['joseph', '……怎么回事？温度一下子升上去了！'], ['kakyoin', '太阳……没有落下。天上有两个太阳！'], ['jotaro', '附近一定有人在操纵。……看反光。']]);
    // 6-03 调查过平沙地：承太郎多一句（主线不加条件，只多一句伏笔回收）
    if (F().ch6DomeHint) await S.say('jotaro', '……还有刚才那块直得古怪的沙地。');
    S.state('heat', 1);
    S.mark('b12_sun');
    await sunFight(S);
    // 6-07 阿拉伯·法兹：碎掉的穹顶里蹲着一个人（分镜 s10 现成）——全篇最短的 Boss 战，喜剧收尾
    //   @dome2.x − 160 = 370 超出地图，所以镜头推到最右（穹顶落在屏幕 x 210）
    const dome = DN('dome2');
    S.camera(320);
    const guy = S.exists('scene:s10_sunguy') ? S.spawn('scene:s10_sunguy', dome[0], dome[1] + 5, { id: 'sunguy', team: 'npc' }) : null;
    S.sfx('glass_break'); S.shake(2, .3); await S.wait(.6);
    S.sfxText('ギクッ!', { x: 320, y: 140 });
    if (guy) S.word('！？', guy);
    S.nameCard('arabiafats');
    await S.wait(.5);
    await lines(S, [['arabiafats', '等、等一下！我只是……在这里乘凉——'], ['jotaro', '……乘凉？']]);
    // 反色冲击帧 + 法兹倒地 + 大字「saiki」（s10_sunguy 只有 2 帧待机，倒地用旋转演）
    S.sfx('punch_heavy', .7); S.impact(); S.shake(2, .25);
    if (guy) await S.animate(.3, k => { guy.rot = -1.2 * k; });
    S.title('saiki');
    S.camera(null);
    await lines(S, [['polnareff', '就这？……一个躲在镜子里的家伙？'], ['joseph', '哈哈哈哈！被两颗石子打倒的替身使者！'], ['jotaro', '……走吧。']]);
    if (guy) guy.remove = true;
    S.state('heat', 0); S.state('dusk', 1);
    await S.say(null, '傍晚。驼铃声里，四个人继续往西。');
  }

  // ================================================================ 亚普林村（village_ch6，yaprin_village 640 宽）
  //   自由走动：骆驼栏（纪念品驼铃）、杂货摊、小孩、抱婴儿的妇人（托付）、井、小清真寺、卖飞机的商人（砍价买塞斯纳）；
  //   两件事都办完，塞斯纳的停机位才出现登机点。
  async function bargainPlane(S) {
    const say = t => S.say('npc_townsfolk', t, { name: '卖飞机的商人', actor: S.actor('plane_merchant') });
    if (F().ch6PlaneBought) {
      // 买过以后：第一句看加没加油（脚本 6-09「已买」，只有一句 ⟳）
      await say(F().ch6Fuel ? '塞斯纳已经加满油了，随时能飞。' : '油泵在铁皮棚下面，油要自己加。');
      await say('飞的时候小心沙暴！');
      return;
    }
    await say('这架塞斯纳？……五千美元。一分都不能少。');
    let price = 5000;
    const r1 = await S.choice(['太贵了！', '五千就五千'], '跟商人谈价钱');
    if (r1 === 0) { price -= 500; await say('那……四千五？'); } else { await S.say('joseph', '……我、我还是再想想。'); price -= 200; await say('爽快！那就四千八。'); }
    const r2 = await S.choice([F().ch6Baby ? '这孩子病了，要赶去城里看医生' : '我们在赶时间，有人在等我们', '我可是房地产大亨！'], '跟商人谈价钱');
    if (r2 === 0) { price -= 1000; await say(F().ch6Baby ? '……孩子？唉，那就再便宜一千。' : '……谁不赶时间呢。好吧，便宜一千。'); }
    else { price += 1000; await say('大亨？那就……再加一千！'); await S.say('joseph', 'OH MY GOD！嘴快了！'); }
    const r3 = await S.choice(['再加上四头骆驼', '付现金'], '跟商人谈价钱');
    if (r3 === 0) { price -= 1500; await say('四头骆驼？……好骆驼！成交！'); } else await say('现金最好！成交！');
    S.sfx('coin', .6);
    F().ch6PlaneBought = true; F().ch6PlanePrice = price;
    await S.say('joseph', price <= 2500 ? '哈哈哈！' + price + ' 美元！做生意，我可是专业的！' : price + ' 美元……算了，反正 SPW 财团会报销。');
    await lines(S, [['joseph', '那么，飞机我来开！'], ['polnareff', '不行。'], ['kakyoin', '不行。'], ['jotaro', '……不行。'], ['joseph', '……可是除了我，没人会开啊。']]);
    await say('对了，油要自己加。泵在铁皮棚下面。');
  }
  // M.scene 进图前会清空 props / npcs / hotspots，所以这一套必须当 M.scene 的 setup 传进去
  // 加油小游戏的状态：进行中（on）、压中的拍数（画油量条用）。结果落在 F().ch6Fuel
  const fuel = { on: false, hits: 0, total: 8 };
  // 油量条：铁皮棚上方一个 18×4 的框，压中几拍填几格（1 拍 2 px）
  function fuelBar(P) {
    if (!fuel.on && !F().ch6Fuel) return;
    const x = Math.round(YV('hangar')[0] - 20 - (G.cam.x || 0)), y = 104;
    px.rect(P, x, y, 18, 4, '#1a1020', .8);
    const w = Math.round(16 * Math.min(1, fuel.hits / fuel.total));
    if (w > 0) px.rect(P, x + 1, y + 1, w, 2, '#ffd257', .95);
  }
  // 手摇泵加油（6-09 新）：跟着 8 拍压 J，压中 ≥ 6 拍算加满
  async function pumpFuel(S, p) {
    await S.say(p.cid, T.by(p, { jotaro: '……压就行了？', joseph: '手摇泵！年轻的时候我可是压过不少！',
      kakyoin: '跟着节奏压，油才不会打空。', polnareff: '交给我！我的手臂可是练过的！' }));
    fuel.on = true; fuel.hits = 0;
    // 每一拍压中都补一声油泵声：引擎的节拍 QTE 只在命中时放 pop，这里看着 notesState 另外数
    let done = false;
    T.every(.04, () => {
      const q = G.ui && G.ui.qte;
      if (!q || q.type !== 'rhythm' || !q.notesState) return;
      const n = q.notesState.filter(v => v === 1).length;
      if (n > fuel.hits) { fuel.hits = n; snd('pump', null, { vol: .4 }); }
    }, () => done);
    const r = await S.rhythm({ label: '跟着节拍压油泵（J）', notes: [0.6, 1.15, 1.7, 2.25, 2.8, 3.35, 3.9, 4.45], window: .16, pass: .6 });
    done = true;
    fuel.on = false;
    const full = !!(r && r.total && r.hits >= r.total * .6);
    if (full) fuel.hits = fuel.total;
    F().ch6Fuel = full ? 'full' : 'half';
    if (full) await S.say('joseph', '满了！这下飞到哪儿都不怕！');
    else { await S.say('joseph', '……只加了一半。算了，够飞了吧？'); await S.say('polnareff', '“够飞了吧”这几个字，我听着就害怕。'); }
  }
  function setupVillage(st) {
    const [mx, my] = YV('mother'), [kx, ky] = YV('kids'), [ex, ey] = YV('merchant'), [px2, py2] = YV('camel_pen');
    // 村民只当“画面上的人”摆着，不挂 talk：跟着队长走的伙伴也有 talk，找最近可搭话对象时
    //   （world.findNear）伙伴会抢在村民前面，E 就变成跟伙伴闲聊、买飞机/托付婴儿的旗标永远设不上。
    //   所以三个村民的 E 交互放在下面的调查点上（坐标和名字都与村民一致，玩家看不出区别）。
    st.npcs = [
      T.npc('npc_villager_f', 'baby_mother', mx, footY('village_ch6', my), { facing: -1, label: '抱着婴儿的妇人', name: '妇人' }),
      T.npc('npc_kid', 'village_kid', kx, footY('village_ch6', ky), { facing: 1, label: '村里的小孩', name: '小孩' }),
      T.npc('npc_townsfolk', 'plane_merchant', ex, footY('village_ch6', ey), { facing: -1, label: '卖飞机的商人', name: '商人' }),
    ];
    const talkMother = async (S, h, p) => {
      const say = t => S.say('npc_villager_f', t, { name: '妇人', actor: S.actor('baby_mother') });
      if (F().ch6Baby) { await say('拜托你们了……城里的医生会照顾他的。'); return; }
      await say('几位要穿过沙漠？……这孩子病了，村里没有医生。求求你们，带他去城里吧。');
      const c = await S.choice(['交给我们吧', '……我们路上很危险'], '妇人抱着婴儿');
      if (c !== 0) await S.say('kakyoin', '……路上很危险。可是，也不能丢下一个生病的孩子。');
      await S.say('joseph', '交给我们吧。SPW 的人在城里，会照顾好他的。');
      F().ch6Baby = true; S.sfx('sparkle', .4);
      await say('谢谢……谢谢你们。');
    };
    const H = (id, k, label, tags, use, look, o = {}) => { const v = YV(k); return Object.assign(M.hot(id, v[0], label, tags, '', use, look, footY('village_ch6', v[1] + 8)), { ly: v[1] - 30 }, o); };
    // 调查点按 x 从小到大排（骆驼栏 80 → 登机 585）：测试器是按这个顺序挨个走过去按 E 的，
    //   每一步都在 2.5 s 内走得到，才不会在半路「盲按」把关键调查点记成已完成（那样买飞机/加油就再也按不到了）。
    st.hotspots = [
      H('camel_pen', 'camel_pen', '骆驼栏', [], async (S, h, p) => sayBy(S, p, { joseph: '骆驼们一边嚼草一边看着我们……是在嘲笑我吗？', polnareff: '离它远点，它会吐口水！', _: '木栏里趴着两头骆驼，慢吞吞地嚼着草。' })),
      X.hot('ch6_camel_bell', px2 + 20, footY('village_ch6', py2 + 8), { label: '草堆里的铜铃' }),
      H('stall', 'stall', '杂货摊', [], async (S, h, p) => sayBy(S, p, { kakyoin: '水罐、布匹、椰枣……樱桃果然没有。', _: '草席棚下摆着水罐和布匹。' })),
      // 三个村民的 E 交互（见上面 st.npcs 的注释）：位置、名字都和站着的人对齐
      M.hot('kid', kx, '村里的小孩', [], '', async (S, h, p) => S.say('npc_kid', pick('c6kid', ['那个婴儿……有时候会自己笑。我的妹妹可不会那样笑。', '你们是开飞机来的吗？……不是？那你们要开飞机走？']), { name: '小孩', actor: S.actor('village_kid') }), null, footY('village_ch6', ky)),
      Object.assign(M.hot('mother', mx, '抱着婴儿的妇人', [], '', talkMother, null, footY('village_ch6', my)), { ly: my - 26 }),
      H('well', 'well', '井', [], async (S, h, p) => { S.sfx('splash', .3); await sayBy(S, p, { joseph: '这口井是真的有水。……第5章那个镇子，我到现在还发毛。', _: '石砌的井台，木架上吊着水桶。' }); }),
      H('mosque', 'mosque', '小清真寺', [], async (S, h, p) => sayBy(S, p, { kakyoin: '土坯的宣礼塔……傍晚会有人上去唱经吧。', _: '土坯砌成的小清真寺。' }), null, { ly: YV('mosque')[1] + 10, y: footY('village_ch6', 156) }),
      M.hot('merchant', ex, '卖飞机的商人', [], '', (S, h, p) => bargainPlane(S), null, footY('village_ch6', ey)),
      // 铁皮棚：买飞机之前不出现（调查点按顺序只按一次，先亮着就会被提前按掉、加不上油）。
      //   买完以后出现：没加油 → 加油小游戏；加过 → 一句收尾
      H('hangar', 'hangar', '铁皮棚', [], async (S, h, p) => {
        if (F().ch6Fuel) { await S.say(null, '油泵上还滴着汽油。'); return; }
        await pumpFuel(S, p);
      }, null, { cond: () => !!F().ch6PlaneBought }),
      // 登机：飞机买好、加过油、婴儿托付好以后才出现（测试器和真人都按出现的顺序走）。
      //   出口不挂替身调查标签：U 调查在这里没用，挂了只会让人多跑几趟 U。
      Object.assign(M.exit('cessna', YV('cessna')[0], '塞斯纳（登机）', 'ch6Plane'), { y: footY('village_ch6', YV('cessna')[1]), tags: [],
        cond: () => !!(F().ch6PlaneBought && F().ch6Baby && F().ch6Fuel) }),
      // 婴儿：承太郎 U「刚才对我笑了一下」、花京院 U「摇篮里有一把小镰刀的玩具？」（伏笔）
      Object.assign(M.hot('baby', mx + 18, '婴儿', ['detail', 'peek'], '', async (S, h, p) => sayBy(S, p, { joseph: '小家伙睡得真香。', polnareff: '照顾小孩我很拿手！……大概。', _: '婴儿在妇人怀里睡着。' }),
        async (S, h, p) => {
          if (p.cid === 'kakyoin') { F().ch6Scythe = true; await S.say('kakyoin', '……婴儿的手里，攥着一把小镰刀的玩具？'); }
          else if (p.cid === 'jotaro') await S.say('jotaro', '……这婴儿，刚才对我笑了一下。');
          else await S.say(p.cid, '睡得很香。');
        }, footY('village_ch6', my)), { ly: my - 26 }),
    ];
    st.onLook = async (S, p) => S.say(p.cid, T.by(p, { kakyoin: '……村子很安静。这里没有替身使者的气息。', _: '……一个普通的小村子。' }));
  }
  async function village(S) {
    calmStands(); party(S);
    await M.scene(S, 'village_ch6', setupVillage, YV('arrive')[0] + 20, 'jotaro');
    S.location('yaprin');
    // 加油槽每次进村都从头显示（本章只来一次，重进也不会残留半格）
    fuel.on = false; fuel.hits = F().ch6Fuel ? fuel.total : 0;
    M.pixel('fuel_gauge', fuelBar);
    const cessna = M.prop(S, 'cessna', YV('cessna')[0], footY('village_ch6', YV('cessna')[1] - 4), { id: 'yaprin_cessna' });
    if (cessna) cessna.frozen = 0;
    await lines(S, [['joseph', '第二十天。亚普林村……从这里坐小飞机，一口气穿过沙漠！'], ['kakyoin', '先去找卖飞机的人吧。']]);
    T.memberTalk({
      joseph: async s => s.say('joseph', pick('c6viJo', ['飞机我来开！……你们那是什么眼神？', '这次的飞机，我一定好好开。'])),
      kakyoin: async s => s.say('kakyoin', pick('c6viKa', ['……那个婴儿，我总觉得在哪里见过。', '这村子的井水，很甜。'])),
      polnareff: async s => s.say('polnareff', pick('c6viPo', ['总算有屋顶了！', '要坐乔斯达先生开的飞机……我先去祈祷一下。'])),
      jotaro: async s => s.say('jotaro', pick('c6viJt', ['……', '……别让老头子开。'])),
    });
    follow();
    const [ex, ey] = YV('merchant'), [hx, hy] = YV('hangar'), [mx2, my2] = YV('mother');
    const bought = () => !!F().ch6PlaneBought;
    // 4 个箭头按脚本的顺序出现：买飞机 → 加油 → 妇人 → 登机
    T.goal(S, { x: ex, y: footY('village_ch6', ey), h: 56, label: '买飞机', delay: 50, every: 25, done: bought, text: '去找卖飞机的商人。' });
    T.goal(S, { x: hx, y: footY('village_ch6', hy), h: 56, label: '加油', when: bought, delay: 10, every: 25, done: () => !!F().ch6Fuel, text: '油泵在铁皮棚下面。' });
    T.goal(S, { x: mx2, y: footY('village_ch6', my2), h: 56, label: '妇人', when: () => bought() && !F().ch6Baby, delay: 30, every: 25, done: () => !!F().ch6Baby, text: '村里有人在找去城里的飞机。' });
    T.goal(S, { x: YV('cessna')[0], y: footY('village_ch6', YV('cessna')[1]), h: 56, label: '登机', delay: 10, every: 25,
      when: () => !!(F().ch6PlaneBought && F().ch6Fuel && F().ch6Baby), done: () => !!F().ch6Plane, text: '飞机准备好了。' });
    await roam(S, 'ch6Plane', '亚普林村：E 搭话、调查；买飞机、加满油、接上婴儿以后去塞斯纳登机。', 10);
  }

  // ================================================================ 塞斯纳机舱（cessna_ch6）
  //  6-10 / 6-12 坐姿：脚点 = 椅子框 seat_boxes / cockpit_seats 的中心、y = 地板 153、z = 0（sit 的锚点在脚下，屁股自然落在坐垫上）
  function seatCrew(S) {
    const ck = CC('cockpit_seats'), sb = CC('seat_boxes');
    const seat = (cid, box) => {
      const a = place(S, cid, Math.round((box[0] + box[2]) / 2), 153, -1);
      if (a) { a.z = 0; S.pose(a, 'sit'); }
      return a;
    };
    seat('joseph', ck[0]); seat('jotaro', ck[1]); seat('polnareff', sb[0]); seat('kakyoin', sb[1]);
    const bb = CC('baby');
    return M.prop(S, 'baby_cradle', bb[0], footY('cessna_ch6', bb[1] + 6), { id: 'cabin_cradle' });
  }
  async function cessnaTakeoff(S) {
    party(S);
    await M.scene(S, 'cessna_ch6', st => { st.state = Object.assign({}, st.state, { alarm: 0, night: 0 }); }, CC('pilot')[0], 'joseph');
    seatCrew(S);
    S.sfx('plane_engine', .6); amb(S, 'plane_engine_loop', 'wind_loop', .2);
    await lines(S, [['joseph', '安全带都系好了吗？起飞！'], ['polnareff', '婴儿也带上？……好吧，照顾小孩我很拿手！'], ['kakyoin', '……对不起，我有点困。就眯一会儿。']]);
    S.shake(1, .4);
    await S.fadeOut(.5); await S.fadeIn(.3);
  }
  async function wakeCrash(S) {
    party(S, 'kakyoin');
    await M.scene(S, 'cessna_ch6', st => { st.state = Object.assign({}, st.state, { alarm: 0, night: 0 }); }, CC('seats')[1][0], 'kakyoin');
    seatCrew(S);
    const k = S.actor('kakyoin');
    if (k) S.pose(k, 'possessed');
    S.sfx('sting_shock', .6); S.shake(2, .3);
    await S.say(null, '——花京院的手臂上，刻着一行字：「BABY STAND」。');
    await lines(S, [['kakyoin', '是……是那个婴儿！他是替身使者！'], ['polnareff', '花京院，你做噩梦了！'], ['joseph', '按住他！别让他碰到操纵杆——']]);
    // 花京院醒过来，坐回椅子上（possessed 是站姿，直接 unpose 会变成站着）
    if (k) S.pose(k, 'sit');
    S.state('alarm', 1); S.sfx('sub_alarm', .5); S.shake(4, .8);
    await S.say('joseph', 'OH MY GOD！操纵杆——！');
    S.sfx('crash'); S.shake(6, .6);
    // 坠毁记录牌和后面两句都在 UI 层，黑幕（G.fadeA）画在 UI 层之上：先 fadeOut 再放牌，
    //   玩家看到的是几秒纯黑，牌子和台词全被盖住。所以这里不淡出，牌子直接盖在机舱上。
    await S.crash(3, 4);
    await S.say('joseph', '……这次是花京院的错！我的坠毁记录可是一直干干净净的！');
    // 6-12：油只加了一半的时候，波鲁纳雷夫多损一句
    await S.say('polnareff', F().ch6Fuel === 'half' ? '哪里干净了……油也只加了一半。' : '哪里干净了……');
    // 机舱戏到此为止：坐姿是 hold（换图不会解除），不解除的话下一张图队长一步都走不动。
    for (const cid of M.crew) { const a = S.actor(cid); if (a) S.unpose(a); }
  }

  // ================================================================ 夜营（camp_ch6，desert_night 640 宽）
  //   花京院当队长：和承太郎、乔瑟夫、波鲁纳雷夫都说过话（没人信他）以后，到篝火 E：召出法皇再睡。
  // 婴儿篮 U「偷看」（6-13 新，只演一次）
  async function peekBaby(s) {
    if (s.flags.ch6Peek) { await s.say('kakyoin', '……它不会再上当了。'); return; }
    s.flags.ch6Peek = true;
    const cr = NT('cradle');
    await s.say('kakyoin', '触须碰到篮子……');
    const baby = s.exists('mannish') ? s.spawn('mannish', cr[0], footY('camp_ch6', cr[1] - 2), { id: 'peek_baby', team: 'npc', name: '婴儿' }) : null;
    if (baby) {
      baby.standReact = false; baby.talk = null; baby.facing = 1;
      snd('baby_laugh', 'sparkle', { vol: .6 });
      await s.act(baby, 'laugh', { max: .8 });
    } else await s.wait(.8);
    await s.say('kakyoin', '——大家，看！它醒着，它在笑！');
    // 三个人一起回头；婴儿已经躺回去（道具移除，篮子照旧）
    for (const cid of ['jotaro', 'joseph', 'polnareff']) { const a = s.actor(cid); if (a) a.facing = cr[0] > a.x ? 1 : -1; }
    if (baby) baby.remove = true;
    await s.wait(.3);
    await s.say('polnareff', '……睡得正香啊。花京院，你也快去睡吧。');
    await s.say('kakyoin', '…………');
  }
  async function camp(S) {
    party(S, 'kakyoin');
    await M.scene(S, 'camp_ch6', st => {
      st.state = Object.assign({}, st.state, { dawn: 0 });
      const [fx, fy] = NT('campfire'), [wx, wy] = NT('wreck'), [cx3, cy3] = NT('cradle'), [tx, ty] = NT('tent');
      st.hotspots = [
        Object.assign(M.hot('sleep', fx, '篝火', ['life'], '带着替身入睡。', async s => {
          if ((s.flags.campTalk || 0) >= 3) s.flags.ch6Sleep = true;
          else await s.say('kakyoin', '……我不能再睡着了。先把事情告诉大家。');
        }), { y: footY('camp_ch6', fy) }),
        Object.assign(M.hot('cradle', cx3, '婴儿篮', ['peek'], '', async s => { snd('baby_laugh', 'sparkle', { vol: .5 }); await s.say('kakyoin', '……它在笑。就像什么都知道一样。'); },
          s => peekBaby(s)), { y: footY('camp_ch6', cy3) }),
        Object.assign(M.hot('tent', tx, '帐篷', [], '', async s => s.say('kakyoin', '临时搭的帐篷。今晚大家轮流守夜。')), { y: footY('camp_ch6', ty + 8) }),
        Object.assign(M.hot('wreck', wx, '坠毁的塞斯纳', [], '', async s => s.say('kakyoin', '机头扎进了沙里，螺旋桨也弯了。……大家都还活着，已经是奇迹了。')), { y: footY('camp_ch6', wy + 6) }),
        X.hot('ch6_altimeter', wx - 26, footY('camp_ch6', wy + 8), { label: '掉出来的仪表' }),
      ];
    }, NT('arrive')[0] + 40, 'kakyoin');
    // 兜底：进营地时把队长身上的姿势解除（上一场是机舱坐姿，hold 会跟着人换图），
    //   否则自由走动一开始就动不了，卡死在出生点。
    S.unpose(S.player);
    const cr = NT('cradle');
    M.prop(S, 'baby_cradle', cr[0], footY('camp_ch6', cr[1]), { id: 'camp_cradle' });
    // 篝火已经画在新背景里了（10-19 背景验收），不再补像素火
    const seats = NT('seats');
    // 石凳在背景里：脚点 = @seats[i]、sit 锚点在脚下（z = 0）；[2] 波鲁纳雷夫朝左（火的右前方）、[3] 空着给花京院
    for (const [cid, at, f] of [['jotaro', seats[0], 1], ['joseph', seats[1], -1], ['polnareff', seats[2], -1]]) {
      const a = place(S, cid, at[0], footY('camp_ch6', at[1]), f);
      if (a) { a.z = 0; S.pose(a, 'sit'); }
    }
    amb(S, 'fire_loop', 'wind_loop', .14);
    await lines(S, [['joseph', '……总之，今晚就在这里过夜。'], ['kakyoin', '（必须让大家相信……那个婴儿，就是替身使者。）']]);
    T.memberTalk(Object.fromEntries(['jotaro', 'joseph', 'polnareff'].map(cid => [cid, async s => {
      const key = 'camp_' + cid;
      if (!s.flags[key]) { s.flags[key] = true; s.flags.campTalk = (s.flags.campTalk || 0) + 1; }
      await s.say(cid, cid === 'jotaro' ? '……你手臂上的字，我看见了。你留下了记号——我相信你。'
        : cid === 'joseph' ? '花京院，别逞强。坠机吓到你了吧？今晚大家轮流守夜。'
          : '你又要睡？花京院！别吓我啊！……那个婴儿？哈哈，你是真累坏了。');
    }])));
    // 三个人都说过话以后，篝火才亮箭头
    T.goal(S, { x: NT('campfire')[0], y: footY('camp_ch6', NT('campfire')[1]), h: 44, label: '篝火', delay: 5, every: 20,
      when: () => (F().campTalk || 0) >= 3, done: () => !!F().ch6Sleep, text: '带着法皇入梦。' });
    await roam(S, 'ch6Sleep', '和三位伙伴说过话后，到篝火边按 E 入睡。', 10);
  }
  async function ending(S) {
    party(S, 'kakyoin');
    await M.scene(S, 'camp_ch6', st => { st.hotspots = []; st.state = Object.assign({}, st.state, { dawn: 1 }); }, NT('cradle')[0] - 30, 'kakyoin');
    S.state('dawn', 1);
    const cr = NT('cradle');
    const cradle = M.prop(S, 'baby_cradle', cr[0], footY('camp_ch6', cr[1]), { id: 'end_cradle' });
    const baby = S.exists('mannish') ? S.spawn('mannish', cr[0] + 2, footY('camp_ch6', cr[1] + 1), { id: 'baby_end', team: 'npc', name: '婴儿' }) : null;
    if (baby) { baby.standReact = false; baby.talk = null; S.pose(baby, 'cry'); }
    snd('baby_cry', 'sting_comedy', { vol: .5 });
    await S.say(null, '死神13 的面具碎了。婴儿哇哇大哭起来。');
    const seats = NT('seats');
    // 6-15：三个人还坐在原处（和 6-13 一样的坐姿）
    for (const [cid, at, f] of [['jotaro', seats[0], 1], ['joseph', seats[1], -1], ['polnareff', seats[2], -1]]) {
      const a = place(S, cid, at[0], footY('camp_ch6', at[1]), f);
      if (a) { a.z = 0; S.pose(a, 'sit'); }
    }
    await lines(S, [['polnareff', '……花京院？你一直在说梦话，现在又醒着发呆。'], ['kakyoin', '……没什么。只是做了一个很长的梦。']]);
    if (baby) S.unpose(baby);
    await lines(S, [['kakyoin', '……这孩子，交给 SPW 吧。'], ['jotaro', '……嗯。'], ['joseph', '天快亮了。SPW 的车，应该快到了。']]);
    if (baby) baby.remove = true;
    if (cradle) cradle.remove = true;
  }

  // ================================================================ 本章入口
  G.STORY.ch6 = async S => {
    T.resetCounters();
    for (const key of ['ch6Ride', 'ch6Plane', 'ch6PlaneBought', 'ch6PlanePrice', 'ch6Baby', 'ch6Scythe', 'ch6Sleep', 'campTalk', 'camp_jotaro', 'camp_joseph', 'camp_polnareff',
      'dreamKnife', 'engraved', 'ch6CamelFalls', 'ch6Fuel', 'ch6Peek', 'ch6DomeHint']) delete F()[key];
    await M.ensureBg('_ch6');
    party(S);
    await S.chapterCard('ch6');
    await S.setStage('map_ch6', { x: 100, y: 160, music: 'travel' });
    await S.route(['卡拉奇', '阿拉伯沙漠'], { vehicle: 'car', day: 17, left: 34, history: ['东京', '香港', '新加坡', '加尔各答', '瓦拉纳西', '卡拉奇'] });
    await desertArrive(S);
    await S.run(async s => { await camelRide(s); await sunScene(s); });
    await S.run(async s => { await s.setStage('map_ch6', { x: 100, y: 160, music: 'travel' }); await s.say(null, '第二十天。沙漠边缘的小村——亚普林。'); });
    await village(S);
    await S.run(async s => { await cessnaTakeoff(s); await dreamOne(s); await wakeCrash(s); });
    await camp(S);
    await S.run(async s => { await campSleep(s); await death(s, { trial: false, wrap: x => x }); await ending(s); });
    await M.end(S, 'ch6_complete');
  };

  // ================================================================ 单战入口（开发调参 G.DEV / 标题「挑战」）
  G.DEV = G.DEV || {};
  G.DEV.ch6Sun = async S => { await M.ensureBg('_ch6'); party(S); await M.scene(S, 'desert_ch6', null, 72, 'jotaro'); await S.run(async () => sunFight(S)); };
  // ================================================================ 星尘试炼关卡工厂（剧情 / 挑战 / 试炼共用同一份配置）
  //   梦二自带布景（场景状态复位）和开场 / 赢后演出；用 run 而不是 setup + spec，
  //   因为开场的出生点写在 M.objectFight 的 init 里，不能拆出去
  G.TRIAL_SRC['b13b_death13'] = {
    chapter: 'ch6', pack: '_ch6',
    run: async (S, o) => { await M.ensureBg('_ch6'); await S.run(async () => death(S, o)); },
  };
  G.DEV.ch6Death = async S => G.TRIAL_SRC['b13b_death13'].run(S, { trial: false, wrap: s => s });
  X.challenge({ id: 'b12_sun', chapter: 'ch6', title: 'VS 太阳（承太郎）', run: S => G.DEV.ch6Sun(S) });
  X.challenge({ id: 'b13b_death13', chapter: 'ch6', title: 'VS 死神13 · 梦二（花京院）', run: S => G.DEV.ch6Death(S) });
})();
