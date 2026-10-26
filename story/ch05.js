// 第5章　巴基斯坦 / 公路、浓雾与卡拉奇（规划 §6.4；原著 150–165 话，第 12–16 天）
//   2026-10-18 按体验版精度重写（用户：“继续把整个 jojo 游戏做完……场景画面精细一些，玩法也多做一些”）。
//   10-14 的初版（压成一行一行的密写法）机关沿用：命运之轮（三车道追车 → 汽油雨 + 挖地）、正义（雾 + 伤口洞 + 反吸）、
//   恋人（脑内 / 街头交替三轮 + 账单）；这一版改回第4章的可读写法，补自由走动、过场、演出和两个可选小游戏。
//
//   流程：世界地图 → 边境公路（后车一直贴着、不超车）→ 第 9 战段 1 追车 → 悬崖路肩：车顺着岩壁爬下来、汽油雨 → 段 2 命运之轮
//   → ZZ 现形、承太郎从地底钻出来 → SPW 来接安妮（第 13 天，一个个道别）→ 地图 → 雾之镇（自由走动：至少两样不同的异常才进旅馆）
//   → 旅馆大堂（自由走动：落地钟、鹿头、登记簿、钥匙板、荷尔·荷斯装住客）→ 波鲁纳雷夫去厕所（黑场留白）→ 恩雅：「我的儿子」
//   → 第 10 战 正义 → 雾散，恩雅被绑，荷尔·荷斯逃走 → 地图（第 15 天）→ 卡拉奇街市（自由走动 + 拉茶 / 砍价小游戏）
//   → 斯蒂利·丹：恩雅之死（剪影）→ 第 11 战 恋人（脑内 ⇄ 街头三轮）→ 账单结清 → 荷尔·荷斯偷走吉普 → TBC
//
//   台词都是新写的（规划 §1.4 第 1 条）；「ギクッ」「再起不能」这类拟声 / 定型字幕沿用前几章。
//   克制处理（规划 §4.6 / §6.4）：厕所只有关上的门、黑场、水声和「（此处省略）」；雾镇居民只写“没有脉搏”“影子不动”，雾散后倒下只用旁白；
//   恩雅之死只用剪影 + 触手的影子 + 黑场；斯蒂利·丹的“屈辱”只做趴下当桥、挠背、偷手镯；ZZ、丹被打只演拳影和飞出画面。
//   背景：tools\bg_new\desert_highway.py / mountain_road.py / fog_town.py / enya_inn.py / karachi_street.py / brain_inside.py（2026-10-18 重画），
//   坐标都从背景导出的 anchors 取（bgA，带默认值 = 背景规格里的值），背景挪了位置剧情跟着走。
'use strict';
(function () {
  const G = window.G, J = G.J25, T = G.TPL, F = () => G.flags, X = G.EXTRA;
  G.TRIAL_SRC = G.TRIAL_SRC || {};   // 各章末尾登记；试炼加载在 ch*.js 之后，这里只准备容器
  const crew = ['jotaro', 'joseph', 'avdol', 'kakyoin', 'polnareff'];
  const lines = async (S, rows) => { for (const [who, text, expr] of rows) await S.say(who, text, expr ? { expr } : {}); };
  const pick = (key, arr) => arr[(T.count(key) - 1) % arr.length];
  const sayBy = (S, p, map) => S.say(p.cid, T.by(p, map));
  // 音效：本章新合成的还没进数据包时用现成的顶上（直接播不存在的名字会记 missingSfx）
  const hasSnd = n => !!(G.audio && G.audio.has && G.audio.has(n));
  const snd = (name, alt, o = {}) => { if (hasSnd(name)) G.audio.sfx(name, o); else if (alt) G.audio.sfx(alt, o); };
  const amb = (S, name, alt, vol) => { if (hasSnd(name)) S.ambient(name, vol); else if (alt) S.ambient(alt, vol * .6); };
  const calmStands = () => { for (const a of (G.party && G.party.members) || []) if (a.stand && a.stand.visible && a.stand.mode !== 'recall') a.stand.recall({ sfx: false }); };
  const follow = () => { if (G.party && G.party.rebuildFollow) G.party.rebuildFollow(); };

  // ---------------------------------------------------------------- 背景锚点（没有就用背景规格里的默认值）
  const bgA = (bg, k, d) => { const b = G.D && G.D.bg && G.D.bg[bg]; const v = b && b.anchors ? b.anchors[k] : null; return v != null ? v : d; };
  const HWd = { party_car: [80, 160], lanes: [152, 160, 168], wheel_start: [140, 160], road_vx: 360 };
  const MRd = { cliff_top: [70, 32], wheel: [96, 160], party_car: [282, 168], arrive: [196, 162], tunnel: [150, 169],
    puddles: [[128, 170], [178, 172], [228, 168]], spw_car: [140, 166], sign: [300, 138] };
  const FTd = { arrive: [40, 163], gate: [60, 150], lamp: [110, 149], resident: [150, 160], well: [222, 152], graves: [300, 150],
    resident2: [380, 162], board: [356, 150], clock: [420, 90], tree: [470, 150], guest: [500, 162], inn: [575, 160],
    inn_door: [575, 148], inn_sign: [575, 92] };
  const EId = { door: [30, 162], coat: [16, 150], stairs: [70, 150], wc_door: [104, 152], sofa: [150, 154], guest: [150, 163],
    clock: [196, 110], counter: [272, 161], counter_box: [240, 118, 316, 150], counter_behind: [272, 147], bell: [258, 124], keys: [292, 96], skull: [220, 76] };
  const KSd = { arrive: [40, 163], fruit: [86, 153], fruit_vendor: [100, 160], tea: [170, 155], dan: [232, 162], command: [232, 162],
    bracelet: [300, 155], vendor: [318, 160], girl: [356, 164], bridge: [420, 170], bridge_box: [407, 166, 433, 174], bus: [496, 150],
    jeep: [596, 161] };
  const BRd = { arrive: [80, 150], center: [160, 150], nodes: [[60, 140], [130, 160], [200, 138], [262, 166], [290, 146]] };
  const HW = k => bgA('desert_highway', k, HWd[k]);
  const MR = k => bgA('mountain_road', k, MRd[k]);
  const FT = k => bgA('fog_town', k, FTd[k]);
  const EI = k => bgA('enya_inn', k, EId[k]);
  const KS = k => bgA('karachi_street', k, KSd[k]);
  const BR = k => bgA('brain_inside', k, BRd[k]);
  // 地图宽度跟背景走：fog_town 2026-10-18 重画成 640 宽（旧画法 480），新背景接进来以前也能跑
  function fitStage(id) {
    const st = G.STAGES[id], b = G.D && G.D.bg && G.D.bg[st.bg];
    if (b && b.w && b.w !== st.x1) {
      st.x1 = b.w;
      st.obstacles = [{ x0: -40, x1: 8, y0: 0, y1: 240 }, { x0: b.w - 8, x1: b.w + 40, y0: 0, y1: 240 }];
    }
    return st;
  }
  // 站人的锚点 y 夹进可走带（背景的物件锚点有时给的是物件底，人要站在它前面）
  const footY = (id, y) => { const st = G.STAGES[id]; return G.clamp(y, st.yMin + 2, st.yMax - 2); };
  // spw_jeep 是 2 帧静态道具（帧 0 / 1 = 轮毂转半格）：开动时每 0.125 s 换一次帧，停下换回 0。
  //   返回一个 stop()，在 walk 结束后调用；道具被 remove 时 tick 自己退出。
  function roll(a) {
    if (!a) return () => {};
    let on = true;
    T.tick(() => {
      if (a.remove) return true;
      if (!on) { a.frozen = 0; return true; }
      a.frozen = Math.floor(G.clk.world * 8) % 2;
      return false;
    });
    return () => { on = false; };
  }

  function place(S, cid, x, y = 164, facing = 1) {
    const a = S.actor(cid); if (!a) return null;
    a.visible = true; a.follow = null; a.x = x; a.y = y; a.facing = facing; a.alpha = 1; a.scale = 1; S.unpose(a);
    return a;
  }
  // 阿布德尔还是“？”（第4章假死），队里能换的是承太郎 / 乔瑟夫 / 花京院 / 波鲁纳雷夫
  function party(S, leader = 'jotaro') {
    S.party(crew, { leader }); G.party.remove('avdol', { look: 'unknown' });
    for (const a of G.party.members) a.scale = 1;
  }

  // ---------------------------------------------------------------- 纪念品（story\extras.js；找到的存在 jojo-extras）
  X.souvenir({ id: 'ch5_postcard', chapter: 'ch5', name: '雾之镇的明信片', desc: '褪了色的风景照。背面的邮戳，是好多年以前的。', hint: '雾之镇的公告板脚下' });
  X.souvenir({ id: 'ch5_room13', chapter: 'ch5', name: '13 号房的钥匙', desc: '旅馆钥匙板上剩下的最后一把。……还好没住进去。', hint: '旅馆的钥匙板挂得高，要会用剑的人' });
  X.souvenir({ id: 'ch5_bangle', chapter: 'ch5', name: '玻璃手镯', desc: '卡拉奇的手镯摊，砍价砍下来的。叮当作响。', hint: '卡拉奇的手镯摊，跟老板砍砍价' });

  // ================================================================ 第 9 战 段 1：公路追车（road_ch5，desert_highway 自动卷）
  //   三车道（↑↓ 换道）、车况 100；撑 45 s 或者“并排时”J 揍中对方的车 6 下。路面往左卷 = 车往右开，后车在左边（后面）。
  //   2026-10-18 重做节奏（原来对方一直在身边，6 下 J 五秒就打完了，没有追车的味道）：对方一轮一轮地来——
  //     ① 贴在后面跟着你换道 → 车头灯连闪（预警 0.55 s）→ 冲上来撞你这条道（伤 15）：换道躲开；
  //     ② 开到旁边一条道和你并排 2.2 s（“并排了！”）：这段时间里 J 才算揍中（隔 0.45 s 一下，一次并排最多两下，第二下把它揍开）；
  //     ③ 并排完往你这条道一别（预警 0.5 s，伤 12）：换到它不在的那条道。
  //   碎石：撞上去自己车况 -3、打滑 1 s；对方撞上去 1 s 不能动（这一轮的并排会晚一点）。选了「放水再来」：受伤 ×0.6、并排时间 ×1.4。
  const LANE_N = 3;
  function roadPass(c) {
    const d = c.data, others = [0, 1, 2].filter(i => i !== d.lane);
    // 并排的那条道：挑和玩家相邻的（玩家在中间就随机一边）
    const side = d.lane === 1 ? others[Math.floor(G.rand(0, 1.99))] : 1;
    d.pass = { step: 'tail', t: 0, side, target: d.lane, hits: 0 };
  }
  G.BOSS25.wheelroad = () => J.base('b09a_wheelroad', 'jotaro', [20, 300], {
    vs: 'wheeloffortune', music: 'battle', bench: 'hide', par: 45,
    gauge: { label: '车况', max: 100, value: 100 }, timer: { label: '逃脱 ', until: 45 },
    waves: [[{ actor: 'wheel', kit: 'e_wheelroad', boss: true, hp: 900, x: 34, y: 160, bodyW: 22 }]],
    onWave: async (S, i, es, a, c) => {
      const d = c.data, lanes = HW('lanes'), p = c.player, b = es[0];
      Object.assign(d, { lanes, lane: 1, bossLane: 1, hits: 0, carHp: 100, rockAt: 3, rocks: [], inputAt: 0, skidUntil: 0, joltUntil: 0,
        shards: [], hornAt: 2, pass: null, window: false, rootUntil: 0 });
      p.x = HW('party_car')[0]; p.y = lanes[1]; p.visible = false; p.hold = true; if (p.stand) p.stand.hide();
      d.car = T.prop(S, 'car', p.x, p.y, { id: 'party_car' }); if (d.car) d.car.hold = true;
      // 对方的车由这一战自己开（kit 的 brain 停掉）：位置 / 车道 / 出招都在 tick 里按“一轮”的步骤走
      b.brain = () => true; b.x = 34; b.y = lanes[1]; b.skin = 'car';
      roadPass(c);
      // 撞车伤害自己判：玩家坐在车里是隐身的，combat 的危险区不打隐身的人（初版的冲撞 / 别车因此一下都撞不到车）。
      //   危险区只用来画红色预警（伤害 0），到点时这一条道上有车就扣车况
      // 放水可叠加：手工减免统一走 G.combat.assistK，第 1 档与原系数一致
      d.carHit = (n, sfx) => {
        n = Math.round(n * G.combat.assistK(c, .6));
        d.carHp = Math.max(0, d.carHp - n); c.gauge.value = d.carHp; d.joltUntil = c.t + .3;
        G.S.shake(2, .2); snd(sfx, 'crash', { vol: .6 }); snd('glass_break', 'crash', { vol: .45 });
        for (let k = 0; k < 6; k++) d.shards.push({ x: p.x + G.rand(-8, 8), y: p.y - 14, vx: G.rand(-60, 60), vy: G.rand(-70, -20), born: c.t });
        G.ui.hint('车况 -' + n, 1.5);
        if (d.carHp <= 0) c.fail('车已经不能动了……');
      };
      d.draw = (P, ctx) => {
        const px = G.px, cx = G.cam.x || 0, bb = ctx.boss;
        // 碎石：两块灰石头 + 一点阴影（路面在卷，石头跟着往后退）
        for (const r of d.rocks) { const x = Math.round(r.x - cx); px.ellipse(P, x - 4, r.y - 1, x + 4, r.y + 2, '#3a3028', null, 1, .5); px.rect(P, x - 3, r.y - 4, 4, 3, '#bdad92'); px.rect(P, x, r.y - 3, 3, 2, '#8c7c64'); }
        // 预警：对方车头灯连闪（冲撞 / 别车的前摇）
        if (bb && d.pass && (d.pass.step === 'ramWarn' || d.pass.step === 'swerveWarn') && Math.floor(ctx.t * 12) % 2 === 0) {
          const x = Math.round(bb.x - cx); px.rect(P, x + 18, bb.y - 12, 3, 2, '#fff6b0'); px.rect(P, x + 18, bb.y - 7, 3, 2, '#fff6b0'); px.ring(P, x + 20, bb.y - 10, 5, 1, '#ffe070');
        }
        // 并排：两车之间一道金色的“够得着”提示
        if (bb && d.window && Math.floor(ctx.t * 6) % 2 === 0) { const x = Math.round(p.x - cx); px.line(P, x, p.y - 16, Math.round(bb.x - cx), bb.y - 16, '#ffd640', .8); }
        // 撞击溅出的碎玻璃（0.6 s）
        for (const s2 of d.shards) { const u = ctx.t - s2.born; if (u > .6) continue; px.rect(P, Math.round(s2.x + s2.vx * u - cx), Math.round(s2.y + s2.vy * u + 120 * u * u), 1, 1, '#d8f4ff'); }
      };
      S.hint('↑↓ 换车道躲开冲撞和别车；对方开到旁边并排时按 J 揍它', 10);
    },
    tick(c, dt) {
      const d = c.data, p = c.player, b = c.boss, I = G.input, A = c.assist;
      if (I.hit('up')) d.lane = Math.max(0, d.lane - 1);
      if (I.hit('down')) d.lane = Math.min(LANE_N - 1, d.lane + 1);
      p.x = HW('party_car')[0]; p.y = d.lanes[d.lane];
      if (d.car) { d.car.x = p.x; d.car.y = p.y; d.car.z = Math.sin(c.t * 28) * (d.skidUntil > c.t ? 2 : .35) + (d.joltUntil > c.t ? 1 : 0); }
      // 路面卷动跟车况：撞到 / 打滑的那一下慢下来（背景 wrap 层乘 state.speed）
      G.world.stage.state.speed = d.joltUntil > c.t ? .35 : d.skidUntil > c.t ? .6 : 1;
      if (c.t >= d.hornAt) { d.hornAt = c.t + G.rand(5, 8); snd('car_horn', 'car_engine', { vol: .35 }); }
      // ---- 对方的一轮
      const q = d.pass;
      d.window = false;
      if (b && q) {
        q.t += dt;
        const rooted = d.rootUntil > c.t;
        const goX = x => { if (!rooted) b.x += G.clamp(x - b.x, -90 * dt, 90 * dt); };
        const goLane = (lane, rate = 1) => { if (rooted) return; d.bossLane = lane; const y = d.lanes[lane]; b.y += G.clamp(y - b.y, -60 * rate * dt, 60 * rate * dt); };
        if (q.step === 'tail') {
          // 贴在后面，慢一拍跟着玩家换道
          goX(34); if (q.t > .45) goLane(d.lane, .8);
          if (q.t >= 1.5 && Math.abs(b.y - d.lanes[d.bossLane]) < 1) {
            // 冲撞：它这条道亮 0.55 s 红色预警（车头灯连闪），然后冲上来
            q.step = 'ramWarn'; q.t = 0; snd('car_horn', 'car_engine', { vol: .45 });
            const ly = d.lanes[d.bossLane];
            c.hazard({ owner: b, shape: 'rect', x0: p.x - 20, x1: p.x + 20, y0: ly - 4, y1: ly + 4, warn: .55, dur: J.f(8), dmg: 0, guard: 'none', push: 0 });
            q.hitLane = d.bossLane; q.hitAt = c.t + .55; q.hitDmg = 15; q.hitSfx = 'crash';
          }
        } else if (q.step === 'ramWarn') {
          if (q.t >= .55) { q.step = 'ram'; q.t = 0; }
        } else if (q.step === 'ram') {
          b.x += 220 * dt; if (q.t >= .25) { q.step = 'back'; q.t = 0; }
        } else if (q.step === 'back') {
          // 并排的那条道按“现在”玩家在哪条道重新挑（贴车那段玩家可能换过道）：玩家在中间就靠它现在所在的那边
          goX(20); if (q.t >= .6) { q.step = 'pull'; q.t = 0; q.side = d.lane !== 1 ? 1 : (d.bossLane === 2 ? 2 : 0); }
        } else if (q.step === 'pull') {
          // 开到旁边那条道，和玩家并排
          goLane(q.side, 1.4); goX(p.x + 4);
          if ((Math.abs(b.x - (p.x + 4)) < 3 && Math.abs(b.y - d.lanes[q.side]) < 1) || q.t > 3) { q.step = 'side'; q.t = 0; G.ui.hint('并排了！J 揍它的车！', 2); }
        } else if (q.step === 'side') {
          goX(p.x + 4); goLane(q.side, 1.4);
          d.window = Math.abs(d.bossLane - d.lane) === 1 && Math.abs(b.x - p.x) < 28;
          if (q.t >= 2.2 * (A ? 1.4 : 1)) {
            q.step = 'swerveWarn'; q.t = 0; q.target = d.lane;
            const ly = d.lanes[q.target];
            c.hazard({ owner: b, shape: 'rect', x0: p.x - 18, x1: p.x + 18, y0: ly - 4, y1: ly + 4, warn: .5, dur: J.f(6), dmg: 0, guard: 'none', push: 0 });
            q.hitLane = q.target; q.hitAt = c.t + .5; q.hitDmg = 12; q.hitSfx = 'metal_crunch';
          }
        } else if (q.step === 'swerveWarn') {
          goX(p.x + 4);
          if (q.t >= .5) { q.step = 'swerve'; q.t = 0; }
        } else if (q.step === 'swerve') {
          goLane(q.target, 3); if (q.t >= .3) { q.step = 'drop'; q.t = 0; }
        } else if (q.step === 'drop') {
          goX(30); if (q.t >= .9) roadPass(c);
        }
        b.skin = 'car';
        // 冲撞 / 别车到点：那一条道上有车就撞上（换道躲开就没事）
        if (q.hitAt && c.t >= q.hitAt) { q.hitAt = 0; if (d.lane === q.hitLane) d.carHit(q.hitDmg, q.hitSfx); }
      }
      if (I.hit('attack') && b && c.t >= d.inputAt) {
        d.inputAt = c.t + .45;
        if (d.window) {
          d.hits++; G.audio.sfx('punch'); G.combat.fxAt('hit_spark', { x: b.x, y: b.y - 18 }, p, .2); G.S.shake(1, .1);
          // 一次并排最多揍中两下：第二下把它揍得歪出去、退到后面（这一轮不别车了）——6 下至少要三轮
          if (q && ++q.hits >= 2) { q.step = 'drop'; q.t = 0; b.x -= 14; G.uifx.sfx('バキィ', b); G.ui.hint('并排反击 ' + d.hits + '/6　揍开了！'); }
          else G.ui.hint('并排反击 ' + d.hits + '/6');
        }
      }
      // ---- 碎石
      if (c.t >= d.rockAt) { d.rockAt = c.t + 3; d.rocks.push({ x: 330, y: d.lanes[Math.floor(G.rand(0, 2.99))] }); }
      // 碎石跟着路面往后退：速度 = 背景路面的卷动速度 × 当前车速（不然石头看起来在路上往前滑）
      const roadV = (HW('road_vx') || 360) * (G.world.stage.state.speed == null ? 1 : G.world.stage.state.speed);
      for (const r of d.rocks) {
        r.x -= roadV * dt;
        if (!r.used && Math.abs(r.x - p.x) < 9 && r.y === p.y) { r.used = true; d.skidUntil = c.t + 1; d.carHp = Math.max(0, d.carHp - 3); G.audio.sfx('skid'); }
        if (b && !r.hitB && Math.abs(r.x - b.x) < 18 && Math.abs(r.y - b.y) < 3) { r.hitB = true; d.rootUntil = c.t + 1; G.audio.sfx('skid'); G.combat.fxAt('dust', { x: b.x, y: b.y, n: 8 }, b, .4); }
      }
      d.rocks = d.rocks.filter(r => r.x > -10);
      c.gauge.value = d.carHp;
      if (d.carHp <= 0) c.fail('车已经不能动了……');
      if (c.t >= 45 || d.hits >= 6) c.end();
    },
    after: async (S, es, a, c) => { c.player.hold = false; c.player.visible = true; if (c.data.car) c.data.car.remove = true; G.world.stage.state.speed = 1; },
    testHint: c => ({ lane: c.data.lane, hits: c.data.hits, carHp: c.data.carHp, bossLane: c.data.bossLane, window: c.data.window,
      step: c.data.pass ? c.data.pass.step : null, side: c.data.pass ? c.data.pass.side : null }),
  });

  // ================================================================ 第 9 战 段 2：命运之轮（cliff_ch5，mountain_road）
  //   900 HP、打车身 ×0.5；WF_DIVE（从岩壁冲下）、WF_CHARGE、WF_RAIN 汽油雨（背景 key oil）→ WF_SPARK 车头打火 90f：
  //   这个窗口里 U「挖地」→ 白金之星钻进地底、从车底一记上勾拳掀翻（之后 5 s 伤害 ×1.5）；第二次掀翻且 HP ≤ 30% 时挖地成功即胜。
  //   没挖 → 起火伤 40（背景 key scorch）。场地两边各收 24 px：车身半宽约 29，贴墙时整辆车出画（地图 320 宽、镜头不动）。
  // 试炼和剧情 / 挑战共用这一份配置：o.trial 时去掉保底 minHp 和关卡自带的挖地 U（试炼的 U 由试炼统一注入）
  const wheelSpec = o => J.base('b09b_wheeloffortune', 'jotaro', [44, 276], {
    vs: 'wheeloffortune', music: 'battle', bench: 'hide', par: 75,
    waves: [[{ actor: 'wheel', kit: 'e_wheel', boss: true, hp: 900, ...(o.trial ? {} : { minHp: 1 }), poiseMax: 0, bodyW: 24, x: G.clamp(MR('wheel')[0], 70, 250), y: 160 }]],
    ...(o.trial ? {} : { kitOverride: { jotaro: { special: J.special(0, '汽油打火！U 挖地', c => c.data.sparkUntil > c.t, async (S, p, c, C) => {
      const d = c.data, b = c.boss;
      d.dug = true; d.flips++; d.flippedUntil = c.t + 5; d.sparkUntil = 0;
      d.holes.push({ x: p.x, y: p.y + 2 });
      C.fx('dust', { x: p.x, y: p.y, n: 20 }); S.fx('crack', { x: p.x, y: p.y, w: 35 }, { life: 1.2 }); S.sfx('rumble', .6);
      p.alpha = .2; await C.wait(.4);
      p.x = G.clamp(b.x - 25, 50, 270); p.facing = 1; p.alpha = 1; b.rot = Math.PI;
      C.fx('dust', { x: p.x, y: p.y, n: 14 }); C.fx('hit_spark', { x: b.x, y: b.y - 20, size: 18 });
      J.fire(p, 70, 90); S.sfx('punch_heavy'); S.shake(4, .3);
      await C.rush(.5, { dmg: 3 });
      if (d.flips >= 2 && b.hp <= b.maxHp * .3) c.end();
    }, 2) } } }),
    onWave: async (S, i, es, a, c) => {
      Object.assign(c.data, { flips: 0, dug: false, flippedUntil: 0, sparkUntil: 0, sparkAt: null, oil: false, holes: [], scorched: false });
      es[0].skin = 'car'; S.state('oil', 0); S.state('scorch', 0); S.state('hole', 0);
      // 起火没挖地：背景烧黑一片（WF_SPARK 打中玩家时 combat 会发 hurt）
      c.on('hurt', e => { if (e.move && e.move.sfx === 'wheel_ignite' && !c.data.scorched) { c.data.scorched = true; S.state('scorch', 1); } });
      c.data.draw = (P, ctx) => {
        const px = G.px, cx = G.cam.x || 0;
        for (const h of c.data.holes) { const x = Math.round(h.x - cx); px.ellipse(P, x - 11, h.y - 2, x + 11, h.y + 3, '#2a1c14'); px.ellipse(P, x - 8, h.y - 1, x + 8, h.y + 2, '#120c08'); }
        // 车头打火：火星在车头一闪一闪（90f 窗口里一直有）
        if (c.data.sparkUntil > ctx.t && ctx.boss && Math.floor(ctx.t * 14) % 2 === 0) { const b = ctx.boss, x = Math.round(b.x - cx + b.facing * 20); px.rect(P, x, b.y - 14, 2, 2, '#ffe070'); px.rect(P, x + 2, b.y - 17, 1, 1, '#ff9040'); }
      };
      if (!o.trial) S.hint('汽油雨后车头打火时按 U 挖地，从车底掀翻它', 10);   // 挖地 U 试炼里没有，这句提示不能留
    },
    tick(c, dt) {
      if (c.data.oil) { if (!G.world.stage.state.oil) G.S.state('oil', 1); if (c.boss) G.combat.fxAt('glint', { x: c.player.x, y: c.player.y - 26, size: 3, dur: .12 }, c.player, .12); }
    },
    after: async (S, es) => { const b = es[0]; b.rot = Math.PI; if (!o.trial) await S.title('saiki'); },
    testHint: c => ({ spark: c.data.sparkUntil > c.t, flips: c.data.flips, flipped: c.data.flippedUntil > c.t, oil: c.data.oil }),
  });
  G.BOSS25.wheel = () => wheelSpec({});   // 兼容旧的直调入口；剧情 / 挑战 / 试炼都走工厂

  // ================================================================ 第 10 战：正义（inn_ch5，enya_inn）
  //   雾（浓度 0.3–0.9、40 s 一个周期）、被操纵的尸体（最多 4 个，HP 30，倒下后被雾吊起来再动一次）、伤口 = 洞（≥3 个时雾拉线，K 挣脱）、
  //   恩雅躲在柜台后每 5 s 现身 40f（能打）、骷髅 15 s 张嘴（W6 切入）→ U 反吸（心跳 8 拍，过关线 0.4 + 0.4 × 恩雅剩余 HP 比）。
  //   2026-10-18 补：背景 key fog；尸体起身时雾拉起的白线；恩雅现身时柜台后一声笑；反吸成功时雾整团吸进去。
  async function skullWarning(c) {
    const d = c.data;
    if (d.warning || !J.valid(c)) return;
    d.warning = true;
    await J.qte(c, async () => {
      await G.uifx.cutin({ portrait: 'enya', title: '正义 · 吸雾', dur: .6 });
      if (J.valid(c)) { d.inhaleUntil = c.t + 1; d.inhaleHitAt = d.inhaleUntil; G.audio.sfx('wind'); G.ui.hint('骷髅张嘴！现在按 U 反吸！'); }
    });
    d.warning = false;
  }
  // 试炼和剧情 / 挑战共用这一份配置：o.trial 时去掉保底 minHp 和反吸 U（试炼改成打光血条，U 由试炼统一注入）
  const justiceSpec = o => J.base('b10_justice', 'jotaro', [20, 300], {
    vs: 'justice', music: 'battle', bench: 'hide', par: 110,
    waves: [[{ actor: 'enya', kit: 'e_enya', boss: true, hp: 800, ...(o.trial ? {} : { minHp: 1 }), x: EI('counter')[0], y: footY('inn_ch5', EI('counter')[1]) }]],
    ...(o.trial ? {} : { kitOverride: { jotaro: { special: J.special(0, '骷髅张嘴！U 反吸', c => c.data.inhaleUntil > c.t, async (S, p, c, C) => {
      const d = c.data, b = c.boss, sk = EI('skull');
      d.inhaleUntil = 0; d.inhaleHitAt = 0;
      const ok = await S.rhythm({ label: '跟着心跳吸气（J）', notes: Array.from({ length: 8 }, (_, i) => .5 + i * .5), window: .16, pass: .4 + .4 * b.hp / b.maxHp });
      if (!J.valid(c)) return;
      if (ok) {
        C.fx('inhale_stream', { x: p.x, y: p.y - 28, cx: sk[0], cy: sk[1], dur: 1.2 }); S.sfx('wind', .8);
        await C.wait(1.2); S.state('fog', 0); c.end();
      } else { J.harm(c, 20); d.nextSkull = c.t + 15; G.ui.hint('反吸失败，先趁恩雅现身削弱她；下次节拍更容易。'); }
    }, 1) } } }),
    onWave: async (S, i, es, a, c) => {
      const d = c.data;
      Object.assign(d, { holes: 0, enyaOpen: 0, nextOpen: 5, nextSkull: 15, inhaleUntil: 0, inhaleHitAt: 0, zombies: [], spawnAt: 1, pullAt: 0, pullUntil: 0,
        warning: false, revives: 0, laughAt: 0 });
      // 前景柜台（key counter）会盖住从柜台前走过的人：战斗里一律关掉
      S.state('fog', 1); S.state('counter', 0);
      c.on('hit', e => { if (e.t === c.player && !e.guard && e.att && e.att.cid === 'zombie') d.holes++; if (e.t === c.boss) { d.enyaOpen = 0; c.boss.alpha = .12; } });
      // 雾：几团横向漂移的雾气（浓度 0.3–0.9、40 s 一个周期）；骷髅挂在天花板下（背景锚点 skull）
      d.draw = (P, ctx) => {
        const px = G.px, amount = .3 + .3 * (1 + Math.sin(ctx.t * Math.PI / 20)), sk = EI('skull');
        for (let k = 0; k < 7; k++) {
          const w = 70 + (k % 3) * 24, y = 116 + k * 8, x = ((k * 97 + ctx.t * (6 + (k % 3) * 3)) % (320 + w)) - w;
          px.ellipse(P, Math.round(x), y, Math.round(x + w), y + 10 + (k % 2) * 6, '#c4d1d5', null, 1, amount * (.2 + .05 * (k % 3)));
        }
        px.blitFrame(P, 'justice', 'skull', Math.floor(ctx.t * 2) % 2, sk[0] + 10, sk[1] + 14, { alpha: .7, scale: 1 });
        if (d.inhaleUntil > ctx.t) px.ring(P, sk[0] + 10, sk[1] + 2, 22 + Math.sin(ctx.t * 30) * 5, 2, '#f6e8ff');
        // 恩雅现身：柜台后面一团暗影 + 两点眼光
        if (d.enyaOpen > ctx.t && ctx.boss) { const b = ctx.boss, x = Math.round(b.x - (G.cam.x || 0)); px.ellipse(P, x - 14, b.y - 30, x + 14, b.y - 2, '#1a1424', null, 1, .35); }
      };
      if (!o.trial) S.hint('趁恩雅现身揍她，骷髅张嘴时按 U 反吸', 10);   // 反吸 U 试炼里没有
    },
    hazards: [{ every: 5, make: c => {
      const b = c.boss;
      return { owner: b, shape: 'rect', x0: c.player.x - 4, x1: c.player.x + 4, y0: 148, y1: 178, warn: .4, dur: J.f(4), dmg: 4, consume: true,
        onHit: (h, t, r) => { if (t === c.player && r.dmg && !r.guard) c.data.holes++; } };
    } }],
    tick(c, dt) {
      const d = c.data, p = c.player, b = c.boss;
      if (!b) return;
      if (c.t >= d.nextOpen) { d.nextOpen = c.t + 5; d.enyaOpen = c.t + J.f(40); G.audio.sfx('grunt_enemy'); if (c.t >= d.laughAt) { d.laughAt = c.t + 12; G.uifx.sfx('嘿嘿嘿……', b); } }
      b.alpha = d.enyaOpen > c.t ? 1 : .12; b.untargetable = d.enyaOpen <= c.t;
      if (c.t >= d.spawnAt) {
        d.spawnAt = c.t + 4;
        if (d.zombies.filter(a => !a.dead && !a.remove).length < 4) {
          const z = c.spawn({ actor: 'zombie', kit: 'e_zombie', hp: 30, x: 30 + G.rand(0, 200), y: 160 }); z.mem.lives = 2; d.zombies.push(z); G.audio.sfx('zombie_moan');
        }
      }
      for (const z of d.zombies) {
        if (z.dead && !z.mem.reviveAt && z.mem.lives > 1) z.mem.reviveAt = c.t + 1.2;
        if (z.mem.reviveAt && c.t >= z.mem.reviveAt) {
          G.combat.resetActor(z); z.mem.lives = 1; z.mem.reviveAt = 0; z.remove = false; d.revives++; G.world.stage.add(z);
          // 雾从天花板垂下两根白线，把倒下的尸体吊起来
          G.combat.fxAt('tendrils', { pts: [[[z.x - 14, z.y], [z.x + 4, z.y - 34]], [[z.x + 14, z.y], [z.x - 4, z.y - 30]]], colour: '#c7d5d0' }, z, .5);
        }
      }
      if (d.holes >= 3 && c.t >= d.pullAt) { d.pullAt = c.t + 6; d.pullUntil = c.t + 1.5; d.pullSide = p.x < 160 ? 20 : 300; G.ui.hint('雾拉住了伤口！K 挣脱。'); }
      if (d.pullUntil > c.t) { p.x += Math.sign(d.pullSide - p.x) * 70 * dt; if (G.input.hit('dodge')) d.pullUntil = Math.min(d.pullUntil, c.t + .75); }
      // 骷髅张嘴只在反吸 U 存在时有意义：试炼去掉反吸，连这个切入和 20 点惩罚一起跳过
      if (!o.trial && c.t >= d.nextSkull && !d.warning) { d.nextSkull = c.t + 15; skullWarning(c).catch(G.cancelIgnore); }
      if (d.inhaleHitAt && c.t >= d.inhaleHitAt) { d.inhaleHitAt = 0; d.inhaleUntil = 0; J.harm(c, 20); }
    },
    after: async (S, es, a, c) => {
      F().ch5ZombieRevives = c.data.revives;
      for (const z of c.data.zombies) z.remove = true;
      if (!o.trial) {
        const sk = EI('skull');
        S.fx('inhale_stream', { x: 150, y: 120, cx: sk[0] + 10, cy: sk[1] + 4, dur: 1.2 });
        await S.say('enya', 'ハッ……ハッ……我的雾……！'); await S.title('saiki');
      }
    },
    testHint: c => ({ holes: c.data.holes, open: c.data.enyaOpen > c.t, inhale: c.data.inhaleUntil > c.t, skullIn: c.data.nextSkull - c.t, revives: c.data.revives,
      zombies: c.data.zombies.map(a => ({ dead: a.dead, lives: a.mem.lives })) }),
  });
  G.BOSS25.justice = () => justiceSpec({});   // 兼容旧的直调入口；剧情 / 挑战 / 试炼都走工厂

  // ================================================================ 第 11 战：恋人（brain_ch5 ⇄ karachi_ch5）
  //   顶部乔瑟夫 HP 100（= 输赢）；线 A 脑内（人物 ×0.5，Q 换人；恋人 600 HP + 3 个假身，只有真身有光点；每 10 s 乔瑟夫 −3，被打中 −1）；
  //   线 B 街头（承太郎不能攻击，按 J = 伤害 ×2 打在乔瑟夫身上）：①「趴下当桥」按住 L 3 秒（趴在排水沟上，丹踩着走过去）、
  //   ②「挠背」←→ 交替 16 次 / 4 s、③「偷手镯」老板转身时走、看着时停，走到摊前按 E；每完成一项账单 +1，失败乔瑟夫 −10。
  //   2026-10-18 补：命令都在背景的位置上做（丹站 command、桥 = 背景的排水沟 bridge、手镯摊 bracelet / 老板 vendor），
  //   脑内背景 key pulse（乔瑟夫受伤时泛红一下）、神经节 nodes 上有光点闪。
  // 脑内场地。镜头在战斗里按 fight.spec.arena 取景（场地不到一屏就锁在场地中心），街头 / 账单结清的站位在 x 300–420，
  //   还用脑内的 [20, 300] 镜头会停在最左边，承太郎、丹、女孩全在画面外 → 去街上时先把 arena 换成整条街，回脑内再换回来。
  const BRAIN_ARENA = [20, 300];
  const streetArena = () => [0, G.STAGES.karachi_ch5.x1];
  function josephDamage(c, n) {
    const d = c.data;
    d.joHp = Math.max(0, d.joHp - n); c.gauge.value = d.joHp; d.pulseUntil = c.t + .5;
    if (G.world.stage.id === 'brain_ch5') G.S.state('pulse', 1);
    if (!d.joHp) c.fail('恋人伤到了乔瑟夫……');
  }
  function loversHUD(c) {
    G.MID.ui(G.S, g => G.MID.hud(g, [
      '账单 ' + c.data.bill + '/3　' + (c.data.phase === 'street' ? '承太郎 · 街头' : '花京院 / 波鲁纳雷夫 · 脑内'),
      c.data.phase === 'street' ? '按 J 会伤害乔瑟夫' : '光点是真身；Q 换人',
    ]));
  }
  const DAN_ORDERS = ['趴下，当我的桥。', '给我挠背，快一点。', '去偷那个手镯。敢动手，你的爷爷就完了。'];
  async function streetTask(c, index) {
    const d = c.data;
    if (d.transition || !J.valid(c)) return;
    d.transition = true; d.phase = 'street'; d.command = index; c.swap = false;
    await J.qte(c, async () => {
      const S = G.S, cmdA = KS('command'), br = KS('bridge'), bra = KS('bracelet'), ven = KS('vendor');
      // 每项命令在街上不同的位置做：桥在排水沟、挠背在丹站的地方、偷手镯从摊子左边 184 px 处走过去
      const startX = index === 0 ? br[0] - 26 : index === 1 ? cmdA[0] - 24 : bra[0] - 186;
      S.party(['jotaro'], { leader: 'jotaro' });
      c.spec.arena = streetArena();
      await J.transfer(c, 'karachi_ch5', startX, null);
      if (!J.valid(c)) return;
      loversHUD(c);
      for (const e of c.enemies()) e.visible = false;
      // 承太郎开打时被 bench:'hide' 藏起来了：换他上场要重新显示
      const pl = G.world.player; pl.visible = true; pl.alpha = 1; pl.scale = 1; pl.x = startX; pl.y = 164;
      G.world.snapCamera();
      const dan = S.spawn('steelydan', index === 0 ? br[0] - 60 : cmdA[0], 162, { id: 'dan_command', team: 'npc' });
      dan.facing = index === 0 ? 1 : -1; dan.standReact = false; dan.talk = null;
      let ok = false;
      await S.say('steelydan', DAN_ORDERS[index], { pos: 'bottom' });
      d.streetAttack = () => {
        if (G.input.hit('attack')) {
          G.input.consume('attack'); G.input.take('attack');
          josephDamage(c, (G.MOVES.SP_J1.dmg || 10) * 2); G.ui.hint('打他 = 伤害 ×2 打到乔瑟夫身上！');
        }
      };
      if (index === 0) {
        // 趴在排水沟上当桥：按住 L 三秒；松手就从头算。丹在第 1.5 秒起踩着走过去
        let held = 0, last = G.clk.ui, walked = false;
        pl.x = br[0]; pl.y = Math.min(br[1], 172); pl.facing = 1;
        G.ui.hint('按住 L 三秒趴下当桥；按 J 会伤到乔瑟夫', 12);
        ok = await J.inputTask(c, { time: 8, tick: ctx => {
          d.streetAttack();
          const now = G.clk.ui, down = G.input.isDown('guard');
          held = down ? held + now - last : 0; last = now;
          ctx.player.play(down ? 'down' : 'idle');
          // 丹走过“桥”：用 steelydan.walk（4 帧 6 fps），走完自动回 idle
          if (held >= 1.5 && !walked) { walked = true; S.walk(dan, br[0] + 40, 162, { speed: 40, anim: 'walk', endAnim: 'idle' }).catch(G.cancelIgnore); }
          d.commandProgress = held / 3;
          return held >= 3;
        } });
        if (ok) await S.say('steelydan', '嗯～这座桥踩着真舒服。', { pos: 'bottom' });
      } else if (index === 1) {
        let count = 0, lastKey = 'right';
        pl.x = dan.x - 14; pl.facing = 1; dan.facing = -1;
        G.ui.hint('四秒内 ←→ 交替 16 次给他挠背', 8);
        ok = await J.inputTask(c, { time: 4, tick: ctx => {
          d.streetAttack();
          for (const key of ['left', 'right']) if (G.input.hit(key) && key !== lastKey) { lastKey = key; count++; ctx.player.play('point', { restart: true }); }
          ctx.player.facing = 1;
          d.commandProgress = count / 16;
          return count >= 16;
        } });
        if (ok) await S.say('steelydan', '左边一点……对对对，就是那里。', { pos: 'bottom' });
      } else {
        // 偷手镯：老板 2 秒看着你、2 秒背过身；看着你的时候还在走 = 被发现，这一项立刻算失败（不用干等 60 秒）
        let x = startX, last = G.clk.ui;
        const vendor = S.spawn('npc_townsfolk', ven[0], footY('karachi_ch5', ven[1] + 2), { id: 'bracelet_vendor', team: 'npc' });
        vendor.standReact = false; vendor.talk = null;
        G.ui.hint('老板转过来就停，背过身再走，到柜台按 E', 15);
        ok = await J.inputTask(c, { time: 60, fail: () => d.caught, tick: (ctx, t) => {
          d.streetAttack();
          const now = G.clk.ui, dt = now - last; last = now;
          const watching = t % 4 < 2;
          d.vendorWatching = watching; d.vendorTurnIn = 2 - t % 2; vendor.facing = watching ? -1 : 1;
          const moving = G.input.isDown('right') || G.input.isDown('left');
          if (watching && moving) { d.caught = true; G.uifx.sfx('！？', vendor); return false; }
          if (d.caught) return false;
          if (moving) { x = G.clamp(x + (G.input.isDown('right') ? 1 : -1) * 55 * dt, startX - 20, startX + 192); ctx.player.facing = G.input.isDown('right') ? 1 : -1; }
          ctx.player.x = x; ctx.player.play(moving ? 'walk' : 'idle');
          d.commandProgress = (x - startX) / 184;
          return x >= startX + 178 && G.input.okHit();
        } });
        vendor.remove = true;
        if (d.caught) G.ui.hint('被老板发现了！', 3);
      }
      if (!J.valid(c)) return;
      d.streetResults.push(ok);
      if (ok) { d.bill++; snd('invoice_stamp', 'ding', { vol: .6 }); G.ui.hint('账单 +1（共 ' + d.bill + ' 笔）'); }
      else { josephDamage(c, 10); G.ui.hint('命令失败，乔瑟夫 -10。'); }
      dan.remove = true; d.round = index + 1; d.streetAttack = null; d.caught = false;
      S.party(['kakyoin', 'polnareff'], { leader: 'kakyoin' });
      c.spec.arena = BRAIN_ARENA.slice();
      await J.transfer(c, 'brain_ch5', BR('arrive')[0], null);
      for (const e of c.enemies()) e.visible = true;
      for (const a of G.party.members) a.scale = .5;
      d.phase = 'brain'; d.nextStreet = c.t + 35; d.nextDrain = c.t + 10; d.spentSince = null; c.swap = true; loversHUD(c);
      if (d.round >= 3 && c.boss) {
        c.boss.minHp = 0;
        // 血条早就打空（一直卡在最低 1 HP）：三项命令做完就直接收尾，不让玩家再补一下才能出来
        if (c.boss.hp <= 1) { c.boss.hp = 0; G.combat.ko(c.boss, G.world.player); }
      }
    });
    d.transition = false;
  }
  G.BOSS25.lovers = () => J.base('b11_lovers', 'kakyoin', BRAIN_ARENA.slice(), {
    // 规划：输 = 乔瑟夫 HP 0（不是脑内操作角色倒下）。操作角色最低 1 HP，脑内每被打中一下乔瑟夫 -1
    vs: 'lovers', music: 'battle', swap: true, allies: ['polnareff'], bench: 'hide', playerMinHp: 1, losable: true, par: 150,
    gauge: { label: '乔瑟夫生命', max: 100, value: 100 },
    waves: [[{ actor: 'lovers', kit: 'e_lovers', boss: true, hp: 600, minHp: 1, x: BR('center')[0] + 50, y: BR('center')[1], pivot: 'center', fly: { z: 6, bob: 2 } }]],
    onWave: async (S, i, es, a, c) => {
      // 重试可能从街头阶段失败回来：spec 上的 arena 还是街的，先换回脑内再传送
      c.spec.arena = BRAIN_ARENA.slice();
      if (G.world.stage.id !== 'brain_ch5') await J.transfer(c, 'brain_ch5', BR('arrive')[0], BR('center')[0] + 50);
      const d = c.data;
      Object.assign(d, { joHp: 100, bill: 0, round: 0, phase: 'brain', nextStreet: 35, nextDrain: 10, transition: false, commandProgress: 0, streetResults: [], pulseUntil: 0, spentSince: null });
      // 重试：上一轮的假身不归战斗管理，先清掉
      for (const o of G.world.stage.actors) if (o._cloneOf) o.remove = true;
      S.party(['kakyoin', 'polnareff'], { leader: 'kakyoin' });
      for (const m of G.party.members) m.scale = .5;
      // onWave 时还没开打（W.combat 假），party.set 会把波鲁纳雷夫设成 npc：Q 换人只认 player / ally，这里改回 ally
      const pol = G.party.get('polnareff'); if (pol) { pol.team = 'ally'; pol.visible = true; }
      const b = es[0];
      d.clones = G.AI.clones(b, 3, { word: '是假身！' }); d.trueLover = b;
      // 假身只负责混淆（绕着真身转、挨打时“是假身！”），不出招：AI.clones 默认的 brain 返回 false 会走通用 AI，四只一起放孢子
      for (const e of d.clones) { e.alpha = 1; e.brain = () => true; }
      d.draw = (P, ctx) => {
        if (d.phase !== 'brain') return;
        const px = G.px, cx = G.cam.x || 0;
        // 神经节：电信号走到那里时亮一下（背景 nodes）
        for (const [k, n] of BR('nodes').entries()) { const on = (ctx.t * 1.3 + k * .37) % 1 < .18; if (on) px.ring(P, n[0] - cx, n[1] - 10, 4, 1, '#fff2a8'); }
        if (ctx.boss) { const e = ctx.boss; G.FX.glint(P, e.x - cx, e.y - e.z - 4, ctx.t % 1, 0, { size: 4, dur: 1 }); }
      };
      S.hint('只打带光点的真身，Q 换人；被打中乔瑟夫也会痛', 12);
      loversHUD(c);
      c.on('hurt', e => { if (d.phase === 'brain' && e.dmg) josephDamage(c, 1); });
    },
    tick(c, dt) {
      const d = c.data;
      if (d.pulseUntil && c.t >= d.pulseUntil) { d.pulseUntil = 0; if (G.world.stage.id === 'brain_ch5') G.S.state('pulse', 0); }
      if (d.phase !== 'brain' || d.transition) return;
      if (d.round >= 3 && (!d.trueLover || d.trueLover.dead || d.trueLover.remove)) { for (const e of d.clones) e.remove = true; c.end(); return; }
      for (const [i, e] of d.clones.entries()) if (c.boss) { e.x = c.boss.x + Math.sin(c.t * 1.4 + i * 2.1) * 26; e.y = c.boss.y + Math.cos(c.t + i * 2) * 12; }
      if (c.t >= d.nextDrain) { d.nextDrain = c.t + 10; josephDamage(c, 3); }
      // 前三轮真身最低 1 HP（打不死）。血条打空了还干等 35 s 计时，玩家会以为卡在乔瑟夫脑子里：见底 1.5 s 后直接开下一项命令
      const b = c.boss, spent = !!b && b.hp <= (b.minHp || 0) + 1;
      if (!spent) d.spentSince = null; else if (d.spentSince == null) d.spentSince = c.t;
      if (d.round < 3 && (c.t >= d.nextStreet || spent && c.t - d.spentSince >= 1.5)) streetTask(c, d.round).catch(G.cancelIgnore);
    },
    after: async (S, es, a, c) => {
      F().ch5Bill = c.data.bill; F().ch5StreetResults = c.data.streetResults.slice();
      for (const e of c.data.clones) e.remove = true;
      // after 里 W.combat 还开着，镜头仍按脑内场地取景：账单结清的站位在街上 x 246–392，要先换成整条街的场地
      c.spec.arena = streetArena();
      S.insertUI(null); G.hud.reset(); G.uifx.vsTag(null);
      await billSettled(S, c.data.bill);
    },
    failWhen: c => c.data.joHp <= 0,
    testHint: c => ({ phase: c.data.phase, round: c.data.round, joHp: c.data.joHp, bill: c.data.bill, streetIn: c.data.nextStreet - c.t, command: c.data.command,
      progress: c.data.commandProgress, vendorWatching: c.data.vendorWatching, vendorTurnIn: c.data.vendorTurnIn, trueX: c.boss && c.boss.x }),
  });

  // 恋人被逐出 → 想钻女孩的耳朵、被法皇的触须捆住 → 丹让它钻承太郎的耳朵 → L 捏住 → 丹求饶 → 账单一笔一笔演欧拉 → 账单结清
  async function billSettled(S, bill) {
    party(S);
    // 开打时 bench:'hide' 把承太郎 / 乔瑟夫藏了，而 after 在战斗收尾恢复现场之前就跑：转场淡入这段先让所有人显示，不然要等下面 place 才冒出来
    for (const a of G.party.members) { a.visible = true; a.alpha = 1; }
    await S.setStage('karachi_ch5', { x: KS('girl')[0] - 40, y: 164, music: 'battle' });
    const gx = KS('girl')[0];
    for (const [cid, dx] of [['jotaro', -40], ['joseph', -110], ['kakyoin', -78], ['polnareff', -60]]) place(S, cid, gx + dx, 164, 1);
    const jos = S.actor('joseph'); if (jos) S.pose(jos, 'lie');
    const girl = S.spawn('npc_kid', gx, footY('karachi_ch5', KS('girl')[1]), { id: 'c5_girl_end', team: 'npc', name: '女孩' }); girl.facing = -1; girl.standReact = false; girl.talk = null;
    const dan = S.spawn('steelydan', gx + 36, 162, { id: 'dan_finish', team: 'npc' }); dan.facing = -1; dan.standReact = false; dan.talk = null;
    if (jos) S.unpose(jos);
    await lines(S, [['joseph', '……呼。脑袋里那只虫子，被赶出来了！'], ['kakyoin', '它想钻进旁边那个女孩的耳朵！法皇之绿——抓住它！']]);
    S.fx('tendrils', { pts: [[[gx - 60, 150], [gx - 6, 128]], [[gx - 60, 156], [gx - 2, 132]]], colour: '#40d060' }, { life: 1.2 });
    S.sfx('hiero_tentacle', .7); await S.wait(.5);
    await lines(S, [['steelydan', '啧……那就钻进承太郎的耳朵！'], ['joseph', '承太郎，小心！']]);
    const press = await S.press({ key: 'guard', window: .5, failOk: true, label: 'L 捏住恋人' });
    S.sfx('punch', .5);
    await S.say('jotaro', press === 'miss' ? '……早就看见了。' : '白金之星。捏住它。');
    await lines(S, [['steelydan', '好、好啦好啦……刚才都是玩笑。我请你们吃饭，怎么样？'], ['jotaro', '你的账单……我来结。']]);
    // 账单：每完成一项命令一笔，一笔 30 拳（规划）；同伴 AI 不出手，只演拳数
    const hits = Math.max(1, bill) * 30;
    await S.title('invoice');
    const C = G.combat.createC(S.player);
    await C.rush(Math.max(.6, hits / 60), { dmg: false });
    S.pose(dan, 'down'); S.fx('burst', { x: dan.x, y: 130, n: 32 }); snd('invoice_stamp', 'punch_heavy');
    S.arc(dan, dan.x + 220, 160, 70, .8).catch(G.cancelIgnore);
    await S.wait(.4);
    await S.say(null, '账单结清（' + bill + ' 笔，' + hits + ' 拳）');
    dan.remove = true; girl.remove = true;
    await S.title('saiki');
  }

  // ================================================================ 公路（road_ch5）
  async function roadIntro(S) {
    calmStands();
    await S.setStage('road_ch5', { x: HW('party_car')[0], y: 160, music: 'travel' });
    amb(S, 'wind_loop', 'wind', .16);
    for (const a of G.party.members) a.visible = false;
    const car = T.prop(S, 'car', HW('party_car')[0], HW('lanes')[1], { id: 'intro_car' });
    const chase = S.spawn('wheel', HW('wheel_start')[0] + 40, HW('lanes')[1], { id: 'chase_car', team: 'npc' });
    chase.skin = 'car'; chase.standReact = false; chase.talk = null; chase.alpha = 0;
    T.tick(() => { if (car && !car.remove) car.z = Math.sin(G.clk.world * 26) * .4; return !car || car.remove; });
    await lines(S, [['joseph', '再往西，就是巴基斯坦。安妮，后座坐稳一点。'], ['anne', '我又不是小孩子。……倒是后面那辆车，怎么一直贴着我们？']]);
    await S.animate(.8, k => { chase.alpha = k; chase.x = HW('wheel_start')[0] + 40 - k * 40; });
    await lines(S, [['polnareff', '喂——！要超车就超过去啊！'], ['polnareff', '……它就是不超。']]);
    snd('car_horn', 'car_engine', { vol: .5 }); S.shake(1, .2);
    await lines(S, [['kakyoin', '刚才已经是第二次了。驾驶座的玻璃太脏，看不清是谁在开。'], ['jotaro', '……老头子，看路。我来盯住它。']]);
    chase.remove = true; if (car) car.remove = true;
    await S.fight(G.BOSS25.wheelroad());
  }

  // ================================================================ 悬崖路肩（cliff_ch5）：车顺着岩壁爬下来 → 第 9 战段 2 → ZZ → 安妮道别
  async function cliffBattle(S) {
    calmStands(); party(S);
    await S.setStage('cliff_ch5', { x: MR('arrive')[0], y: 162, music: 'tension' });
    amb(S, 'wind_loop', 'wind', .1);
    S.state('oil', 0); S.state('hole', 0); S.state('scorch', 0);
    const pc = MR('party_car'), ar = MR('arrive');
    const car = T.prop(S, 'car', pc[0], pc[1], { id: 'stopped_car' });
    for (const [cid, dx, dy] of [['jotaro', -10, 0], ['joseph', 30, 4], ['kakyoin', 12, -6], ['polnareff', -30, 6]]) place(S, cid, ar[0] + dx, footY('cliff_ch5', ar[1] + dy), -1);
    const anne = S.actor('anne') || S.spawn('anne', pc[0] - 24, footY('cliff_ch5', pc[1] + 2), { id: 'anne', team: 'npc', name: '安妮' });
    anne.follow = null; anne.x = pc[0] - 24; anne.y = footY('cliff_ch5', pc[1] + 2); anne.facing = -1; anne.visible = true;
    await lines(S, [['joseph', '可恶……被它逼到悬崖边上来了。'], ['anne', '那、那辆车呢？刚才明明在后面……']]);
    // 车从崖顶顺着岩壁爬下来（世界 y 留在落地点、用 z 当高度：影子和前后遮挡都按落地点算）
    const top = MR('cliff_top'), land = MR('wheel');
    const wheel = S.spawn('wheel', top[0], land[1], { id: 'wheel_climb', team: 'npc', shadow: false });
    wheel.standReact = false; wheel.talk = null; wheel.z = land[1] - top[1]; S.pose(wheel, 'climb');
    snd('car_engine', null, { vol: .6 }); S.sfx('rumble', .5);
    await S.animate(2.2, k => { wheel.x = top[0] + (land[0] - top[0]) * k; wheel.z = (land[1] - top[1]) * (1 - k); if (Math.random() < .2) S.fx('dust', { x: wheel.x, y: wheel.y - wheel.z, n: 2 }); });
    wheel.z = 0; S.unpose(wheel); wheel.skin = 'car'; S.shake(3, .3); S.fx('dust', { x: land[0], y: land[1], n: 14 });
    await lines(S, [['polnareff', '这不是普通汽车！它竟然沿着岩壁爬下来了！']]);
    S.standCard('wheeloffortune');
    await S.wait(1.2);
    S.pose(wheel, 'spray'); snd('gas_rain', 'drip', { vol: .6 }); S.state('oil', 1);
    await lines(S, [['anne', '下、下雨了？'], ['jotaro', '……不对。这不是雨。'], ['jotaro', '是汽油。'], ['kakyoin', '它想把火引到你身上——别让车头对着你！']]);
    S.unpose(wheel); wheel.remove = true;
    anne.visible = false;
    await S.fight(wheelSpec({ trial: false, wrap: s => s }));
    await zzReveal(S, car);
  }
  // ZZ 现形：车门打开，爬出一个小个子、两条手臂粗得吓人的男人 → 地面裂开，承太郎从坑里爬出来 → ZZ 求饶被一拳打飞
  async function zzReveal(S, car) {
    party(S);
    const land = MR('wheel'), tn = MR('tunnel');
    const ar = MR('arrive');
    for (const [cid, dx] of [['joseph', 60], ['kakyoin', 40], ['polnareff', 20]]) place(S, cid, ar[0] + dx, footY('cliff_ch5', ar[1]), -1);
    const jt = S.actor('jotaro'); if (jt) { jt.visible = false; jt.follow = null; }
    for (const a of G.world.stage.actors) if (a.cid === 'wheel') a.remove = true;
    const flipped = S.spawn('wheel', land[0], land[1], { id: 'wheel_flipped', team: 'npc' }); flipped.skin = 'car'; flipped.rot = Math.PI; flipped.standReact = false; flipped.talk = null;
    const zz = S.spawn('zz', land[0] + 26, footY('cliff_ch5', land[1] + 4), { id: 'zz_reveal', team: 'npc', name: 'ZZ' }); zz.facing = 1; zz.standReact = false; zz.talk = null; zz.alpha = 0;
    S.sfx('door', .7);
    await S.animate(.5, k => { zz.alpha = k; });
    S.nameCard('zz');
    await lines(S, [['zz', '嘿嘿嘿……烧成灰了吧？命运之轮的车轮下面，可从来没有活人！'], ['polnareff', '……承太郎呢？刚才明明还在火里——']]);
    // 地面裂开：背景 key hole（在锚点 tunnel）；旧背景没画坑就用裂纹顶上
    S.state('hole', 1); S.fx('crack', { x: tn[0], y: tn[1], w: 30 }, { life: 2 }); S.sfx('rumble', .8); S.shake(3, .5);
    await S.wait(.5);
    if (jt) { jt.visible = true; jt.x = tn[0]; jt.y = footY('cliff_ch5', tn[1] - 2); jt.facing = -1; jt.z = -10; jt.alpha = 1; }
    S.fx('dust', { x: tn[0], y: tn[1], n: 18 });
    if (jt) await S.animate(.5, k => { jt.z = -10 + 10 * k; });
    S.sfxText('ギクッ!', { x: 220, y: 150 });
    await lines(S, [['zz', '你、你不是已经被烧掉了吗？！'], ['jotaro', '火往上烧。……地底下，它追不上来。']]);
    await T.fullbody3(S, { cid: 'jotaro', anim: 'pose', cap: true, dur: 1.2 });
    await lines(S, [['zz', '饶、饶命！我只是收钱开车的！车、车坏了我也要赔钱的啊！'], ['jotaro', '……']]);
    S.impact('invert'); S.sfx('punch_heavy'); S.sfxText('ORA!', { x: 300, y: 140 });
    S.pose(zz, 'down'); S.arc(zz, zz.x - 160, zz.y, 60, .7).catch(G.cancelIgnore);
    await S.wait(.8); zz.remove = true;
    await lines(S, [['joseph', '……轮胎都朝天了。这辆车，以后是没法再追我们了。']]);
    flipped.remove = true;
  }
  // SPW 的车来接安妮（第 13 天）：一个个道别
  async function anneFarewell(S) {
    calmStands(); party(S);
    S.state('oil', 0);
    const sp = MR('spw_car'), ar = MR('arrive');
    const bx = Math.max(ar[0], sp[0] + 76);   // 众人站在 SPW 的车右边，中间留给安妮走过去
    // 2026-10-20：四人往左收 14–36 px（原来是 0/26/48/70，波鲁纳雷夫正好压在车身 x 263–301 上）
    for (const [cid, dx] of [['jotaro', -14], ['joseph', 4], ['kakyoin', 20], ['polnareff', 36]]) place(S, cid, bx + dx, footY('cliff_ch5', ar[1] + 2), -1);
    await S.say(null, '第十三天。SPW 财团的车，顺着山路开了过来。');
    const spwCar = T.prop(S, 'spw_jeep', -40, footY('cliff_ch5', sp[1]), { id: 'spw_car' });
    if (spwCar) { const stopRoll = roll(spwCar); await S.walk(spwCar, sp[0], footY('cliff_ch5', sp[1]), { speed: 120, anim: 'idle', endAnim: 'idle' }); stopRoll(); }
    const staff = S.spawn('npc_spw', sp[0] + 22, footY('cliff_ch5', sp[1] - 2), { id: 'spw_staff', team: 'npc', name: 'SPW 财团' }); staff.facing = 1; staff.standReact = false; staff.talk = null;
    const anne = S.actor('anne') || S.spawn('anne', ar[0] - 40, footY('cliff_ch5', ar[1]), { id: 'anne', team: 'npc', name: '安妮' });
    anne.follow = null; anne.visible = true; anne.alpha = 1; anne.x = bx - 26; anne.y = footY('cliff_ch5', ar[1] + 4); anne.facing = 1;
    await S.say('npc_spw', '乔斯达先生，这位小姐由我们送去机场。家里人已经联系上了。', { name: 'SPW 财团', actor: staff });
    await lines(S, [['joseph', '这次是真的回家了。别再躲进别人的船里，听见没有？'], ['anne', '知道啦……别用那种哄小孩的口气。']]);
    const bye = async (cid, mine, theirs) => {
      const m = S.actor(cid); if (m) anne.facing = m.x > anne.x ? 1 : -1;
      await S.say('anne', mine, { name: '安妮', actor: anne }); await S.say(cid, theirs);
    };
    await bye('joseph', '老爷爷，以后别再开车撞东西了。……飞机也少坐。', '哈哈哈！这、这个嘛……我尽量！');
    await bye('polnareff', '你的头发，下次见面还会竖得这么高吗？', '当然！这可是我的骄傲！');
    await bye('kakyoin', '樱桃……别再在别人面前那样舔了，好恶心。', '……我会注意的。');
    await bye('jotaro', '空条……承太郎。我念对了吧？', '……嗯。');
    S.pose(anne, 'wave');
    await S.say('anne', '你们要活着回来哦。我长大以后，会变成大美女的！', { name: '安妮', actor: anne });
    await S.say('jotaro', '……呀嘞呀嘞。');
    S.unpose(anne);
    await S.walk(anne, sp[0] + 4, footY('cliff_ch5', sp[1]), { speed: 70 });
    anne.remove = true; staff.remove = true; F().anneLeft = true;
    if (spwCar) { const stopRoll = roll(spwCar); await S.walk(spwCar, -60, footY('cliff_ch5', sp[1]), { speed: 110, anim: 'idle', endAnim: 'idle' }); stopRoll(); }
    if (spwCar) spwCar.remove = true;
    await lines(S, [['polnareff', '……突然安静下来了。'], ['joseph', '走吧。车还能开——这次我会小心的。']]);
  }

  // ================================================================ 雾之镇（fog_ch5，fog_town 640 宽）
  //   至少两样不同的异常才能找恩雅进旅馆。线索：花京院 U 触须碰居民手腕“没有脉搏”、承太郎 U“影子不会动”、乔瑟夫 U 念写公告板
  //   “整个镇子罩在骷髅形状的雾里”、墓地新坟、停住的钟、公告板寻人启事、井里没有水声、路灯四周没有虫子。
  //   波鲁纳雷夫 U 剑挑牌坊上生锈的铁丝：手背划了一道小口子（第一个“洞”，伏笔，不挡推进）。
  function memberTalkFog() {
    T.memberTalk({
      joseph: async S => S.say('joseph', pick('c5foJo', ['这雾……连三步外的人都看不清。', '镇上的人一直在笑。……笑得我后背发凉。'])),
      kakyoin: async S => S.say('kakyoin', pick('c5foKa', ['太安静了。连狗叫都没有。', '这么大的雾，地面却是干的。'])),
      polnareff: async S => S.say('polnareff', pick('c5foPo', ['我先说好，今晚我要一个人睡一间！', '……啊，好想上厕所。'])),
      jotaro: async S => S.say('jotaro', pick('c5foJt', ['……', '……这镇子，不对劲。'])),
    });
  }
  function clue(S, key, who, text) {
    return (async () => {
      const n = J.unique('fogClues', key);
      await S.say(who, text);
      S.hint('发现异常 ' + Math.min(n, 2) + '/2' + (n >= 2 ? '，去旅馆找恩雅婆婆。' : '，再调查一处不同的异常。'), 7);
    })();
  }
  function setupFog() {
    const st = fitStage('fog_ch5');
    st.props = []; st.triggers = [];
    st.state = Object.assign({}, st.state, { mist: 1, night: 0 });
    const [rx, ry] = FT('resident'), [r2x, r2y] = FT('resident2'), [gx, gy] = FT('guest'), [ix, iy] = FT('inn');
    const say = (S, cid, text, name, id) => S.say(cid, text, { name, actor: S.actor(id) });
    st.npcs = [
      T.npc('npc_townsfolk', 'fog_resident', rx, footY('fog_ch5', ry), { facing: 1, label: '居民', name: '居民', talk: S => say(S, 'npc_townsfolk', pick('c5res', ['欢迎……欢迎……', '欢迎来到……我们的镇子……']), '居民', 'fog_resident') }),
      T.npc('npc_villager_f', 'fog_resident2', r2x, footY('fog_ch5', r2y), { facing: -1, label: '居民', name: '居民', talk: S => say(S, 'npc_villager_f', pick('c5res2', ['旅馆……在那边……欢迎……', '……欢迎。']), '居民', 'fog_resident2') }),
      T.npc('holhorse', 'guest_holhorse', gx, footY('fog_ch5', gy), { facing: -1, label: '抽烟的男人', name: '荷尔·荷斯', talk: S => say(S, 'holhorse', pick('c5hh', ['别看我。我只是路过，找个地方躲雾。', '……当 No.2 的诀窍？就是别站在最前面。']), '荷尔·荷斯', 'guest_holhorse') }),
      T.npc('enya', 'enya_inn', ix, footY('fog_ch5', iy), { facing: -1, label: '旅馆的老婆婆', name: '恩雅婆婆', talk: async S => {
        if (Object.keys(F().fogClues || {}).length < 2) { await say(S, 'enya', pick('c5enya', ['嘿嘿……旅馆就在这儿。别在雾里站着，进来歇歇。', '客人们，雾大，别乱走哟。']), '恩雅婆婆', 'enya_inn'); return; }
        await lines(S, [['jotaro', '没有脉搏，影子也不会动。你这个镇上的人……住得太久了。']]);
        await say(S, 'enya', '……嘿嘿嘿。想知道？那就进来看看。', '恩雅婆婆', 'enya_inn');
        F().justiceStart = true;
      } }),
    ];
    const H = (id, k, label, tags, use, look, o = {}) => { const v = FT(k); return J.hot(id, v[0], footY('fog_ch5', v[1] + 10), label, tags, use, look, Object.assign({ ly: v[1] - 30, r: 22 }, o)); };
    st.hotspots = [
      // 居民（测试器按这个标签找人：花京院 U 摸脉搏、承太郎 U 看影子）
      J.hot('townsfolk', rx, footY('fog_ch5', ry), '居民', ['peek', 'detail'],
        S => clue(S, 'shadow', S.player.cid, '他一直在说欢迎，可脚下的影子一点都不动。'),
        (S, h, p) => p.cid === 'kakyoin' ? clue(S, 'pulse', 'kakyoin', '触须碰到他的手腕……没有脉搏。') : clue(S, 'shadow', p.cid, '雾在流动，他的影子却一点都不动。'),
        { r: 20 }),
      H('gate', 'gate', '镇口的牌坊', ['cut'],
        async (S, h, p) => sayBy(S, p, { joseph: '牌坊上的字被雾遮了一半……「……镇」。连镇名都看不清。', _: '生锈的铁牌坊，牌子歪歪地挂着。' }),
        async S => {
          F().ch5PolCut = true;
          await S.say('polnareff', '牌子快掉下来了，我帮它——嘶。……被铁丝划了一下。');
          await S.say('polnareff', '小口子而已，不痛。……奇怪，怎么连一滴血都没流？');
        }),
      H('lamp', 'lamp', '路灯', [], async (S, h, p) => clue(S, 'lamp', p.cid, '灯亮着，四周却连一只虫子都没有，也听不到一点风声。')),
      H('well', 'well', '井', [], async (S, h, p) => {
        S.sfx('whoosh', .2);   // 只有丢出去的风声——井里没有落水声，才是这条线索
        await clue(S, 'well', p.cid, T.by(p, { joseph: '丢颗石子下去……听不到落水声。这口井，是干的？', _: '石子丢下去，听不到落水的声音。' }));
      }),
      H('graves', 'graves', '墓地', [], async (S, h, p) => clue(S, 'graves', p.cid, '土还是新翻的。这么小的镇子，怎么会有这么多新坟？')),
      H('board', 'board', '公告板', ['nensha'],
        async (S, h, p) => clue(S, 'board', p.cid, '贴满了寻人启事。……一张、两张……全是来旅游的外地人。'),
        async S => {
          await S.photo({ frames: [0, 1, 2], hold: 1.2 });
          await clue(S, 'photo', 'joseph', '念写出来的照片上……整个镇子，罩在一团骷髅形状的雾里！');
        }),
      H('clock', 'clock', '钟楼', [], async (S, h, p) => clue(S, 'clock', p.cid, '钟停在三点十分。……停了很久了，可钟摆还在晃。'), null, { ly: FT('clock')[1] + 10 }),
      H('tree', 'tree', '枯树', [], async (S, h, p) => sayBy(S, p, { kakyoin: '树干上全是抓痕……像是有人被吊在这里过。', polnareff: '这棵树怎么看都不吉利，我们绕过去吧。', _: '一棵枯死的老树，枝杈伸进雾里。' })),
      H('inn_sign', 'inn_sign', '旅馆招牌', [], async (S, h, p) => sayBy(S, p, { joseph: 'HOTEL……这么小的镇子，旅馆倒是挺气派。', _: 'HOTEL。招牌下的门缝里，也全是雾。' }), null, { ly: FT('inn_sign')[1] + 10 }),
      // 纪念品：公告板脚下掉着一张旧明信片（E）
      X.hot('ch5_postcard', FT('board')[0] + 18, footY('fog_ch5', FT('board')[1] + 12), { label: '掉在地上的明信片' }),
    ];
    st.onLook = async (S, p) => S.say(p.cid, T.by(p, { kakyoin: '雾里有东西……但离得太远了。', jotaro: '……没什么特别的。', _: '雾太浓了，看不清。' }));
  }

  // ================================================================ 旅馆大堂（inn_ch5，enya_inn）
  function memberTalkInn() {
    T.memberTalk({
      joseph: async S => S.say('joseph', pick('c5inJo', ['这么偏的镇子，旅馆倒是收拾得很干净。', '老婆婆一个人开旅馆？……不容易啊。'])),
      kakyoin: async S => S.say('kakyoin', pick('c5inKa', ['登记簿上的名字，全被划掉了。', '外面的雾……从门缝里钻进来了。'])),
      polnareff: async S => S.say('polnareff', pick('c5inPo', ['我、我先去一下厕所！马上回来！', '那个鹿头……是不是在看我？'])),
      jotaro: async S => S.say('jotaro', pick('c5inJt', ['……', '……别离开大家太远。'])),
    });
  }
  function setupInn() {
    const st = G.STAGES.inn_ch5;
    st.props = []; st.triggers = [];
    // 恩雅一开始站在柜台后面（counter_behind + 前景柜台 key counter 挡住下半身），打过招呼再从柜台后面走出来
    st.state = Object.assign({}, st.state, { fog: 0, counter: 1 });
    const [gx, gy] = EI('guest'), [cx, cy] = EI('counter_behind');
    st.npcs = [
      T.npc('holhorse', 'inn_guest', gx, footY('inn_ch5', gy), { facing: 1, label: '沙发上的住客', name: '荷尔·荷斯', talk: async S => {
        await S.say('holhorse', pick('c5inHH', ['……别看我。我只是住店的。', '劝你们一句：这家店的厕所，最好别去。']), { name: '荷尔·荷斯', actor: S.actor('inn_guest') });
      } }),
      T.npc('enya', 'inn_host', cx, cy, { facing: -1, label: '恩雅婆婆', name: '恩雅婆婆', talk: async S => {
        await S.say('enya', pick('c5inEn', ['嘿嘿……客人，住几晚都行。房钱嘛，好说好说。', '楼上的房间都空着。……都空着哟。']), { name: '恩雅婆婆', actor: S.actor('inn_host') });
      } }),
    ];
    const H = (id, k, label, tags, use, look, o = {}) => { const v = EI(k); return J.hot(id, v[0], footY('inn_ch5', v[1] + 8), label, tags, use, look, Object.assign({ ly: v[1] - 28, r: 20 }, o)); };
    st.hotspots = [
      H('coat', 'coat', '衣帽架', [], async (S, h, p) => sayBy(S, p, { joseph: '挂着好几顶帽子……主人们都去哪儿了？', _: '衣帽架上挂满了旧帽子和外套。' })),
      H('stairs', 'stairs', '楼梯', [], async (S, h, p) => sayBy(S, p, { kakyoin: '楼上一点声音都没有。', _: '去二楼的楼梯。楼上黑漆漆的。' })),
      H('clock', 'clock', '落地钟', [], async (S, h, p) => sayBy(S, p, { jotaro: '……钟摆不动。可是，听得到滴答声。', _: '钟摆停着，滴答声却从钟里传出来。' }), null, { ly: EI('clock')[1] + 4 }),
      H('register', 'bell', '登记簿', ['detail'],
        async (S, h, p) => { F().ch5Register = true; await S.say(p.cid, '登记簿上的名字……一个不剩，全被划掉了。'); },
        async S => { F().ch5Register = true; await S.say('jotaro', '划掉名字的墨水……是同一支笔，同一天。'); }),
      H('keys', 'keys', '钥匙板', ['cut'],
        async (S, h, p) => S.say(p.cid, X.has('ch5_room13') ? '钥匙全都不见了。……被住进去的人带走了？' : '一排挂钩都空了，只有最上面还挂着一把 13 号房的钥匙。'),
        async (S, h, p) => {
          if (X.has('ch5_room13')) { await S.say('polnareff', '已经拿下来了。……还是别住 13 号房吧。'); return; }
          await S.say('polnareff', '挂得这么高？……银色战车，剑尖一挑——Voilà！');
          await X.give(S, 'ch5_room13', { x: h.x, y: h.y - 40 });
          await S.say('polnareff', '13 号房……听着就不吉利。这个当纪念吧。');
        }, { ly: EI('keys')[1] + 4 }),
      H('deer', 'skull', '鹿头标本', [], async (S, h, p) => sayBy(S, p, { polnareff: '它、它的眼睛刚才是不是动了？！', joseph: '这对鹿角真漂亮……就是眼神有点吓人。', _: '墙上挂着一只鹿头标本，玻璃眼珠亮亮的。' }), null, { ly: EI('skull')[1] + 24 }),
      // 厕所门：波鲁纳雷夫要去厕所（本段的出口）
      H('wc', 'wc_door', '厕所（WC）', [], async S => { F().ch5Wc = true; }),
    ];
    st.onLook = async (S, p) => S.say(p.cid, T.by(p, { kakyoin: '雾钻进来了……顺着地板，往我们脚边爬。', _: '……这屋子里的雾，越来越浓了。' }));
  }
  async function innIntro(S) {
    calmStands(); setupInn();
    await S.setStage('inn_ch5', { x: EI('door')[0] + 20, y: 164, music: 'tension' });
    amb(S, 'wind_loop', 'wind', .09);
    party(S);
    const d0 = EI('door')[0];
    for (const [cid, dx] of [['jotaro', 40], ['joseph', 20], ['kakyoin', 60], ['polnareff', 80]]) place(S, cid, d0 + dx, footY('inn_ch5', 164 + (dx % 3)), 1);
    S.nameCard('enya');
    await S.say('enya', '欢迎、欢迎！远道而来的客人，嘿嘿嘿……先在大堂歇歇脚。', { name: '恩雅婆婆', actor: S.actor('inn_host') });
    await lines(S, [['joseph', '老婆婆一个人照看这么大的旅馆？'], ['polnareff', '啊……抱歉，厕所在哪里？']]);
    // 恩雅从柜台后面绕出来（走到柜台右端再关掉前景柜台，免得她走到一半露出整个身子）
    const host = S.actor('inn_host'), cb = EI('counter_box');
    if (host) {
      await S.say('enya', '嘿嘿……就在楼梯底下，WC。客人请便～', { name: '恩雅婆婆', actor: host });
      await S.walk(host, cb[2] + 4, host.y, { speed: 50 });
      S.state('counter', 0);
      await S.walk(host, EI('counter')[0] + 14, footY('inn_ch5', EI('counter')[1]), { speed: 50 });
      host.facing = -1;
    } else S.state('counter', 0);
    memberTalkInn(); follow();
  }
  // 大堂自由走动：必须在 S.run 外面跑（S.run 里 S.busy 一直为真，E / U 调查全被挡住）
  async function innExplore(S) {
    S.free(true);
    S.hint('在大堂里看看，再陪波鲁纳雷夫去厕所（WC）。', 8);
    const wc = EI('wc_door');
    T.goal(S, { x: wc[0], y: footY('inn_ch5', wc[1] + 8), h: 50, label: 'WC', delay: 30, every: 20, done: () => !!F().ch5Wc, text: '波鲁纳雷夫快憋不住了。' });
    await S.until(() => F().ch5Wc && !S.busy);
    S.free(false);
  }
  async function innWc(S) {
    calmStands();
    const wc = EI('wc_door');
    // 厕所：只有关上的门、黑场、一声水声和「（此处省略）」（规划 §6.4 克制处理）
    const pol = S.actor('polnareff');
    if (pol) { pol.follow = null; await S.walk(pol, wc[0], footY('inn_ch5', wc[1] + 6), { speed: 90 }); pol.visible = false; }
    S.sfx('door', .6);
    await S.fadeOut(.3); S.sfx('water_gush', .5); await S.say(null, '（此处省略）'); await S.fadeIn(.3);
    if (pol) { pol.visible = true; S.pose(pol, 'shock'); }
    await lines(S, [['polnareff', '……我再也不想进这间旅馆了。'], ['polnareff', '手上什么时候划了一道口子？不痛，可是怎么也甩不掉这层雾……'],
      F().ch5PolCut ? ['kakyoin', '是刚才在牌坊那里被铁丝划的？……不对，伤口里在冒雾！'] : ['kakyoin', '伤口里……在冒雾！']]);
    if (pol) S.unpose(pol);
    const enya = S.actor('inn_host');
    if (enya) { enya.talk = null; S.pose(enya, 'cast'); }
    S.state('fog', 1);
    await S.say('enya', '我的儿子……J·凯尔！你们杀了他——就该用身上的每一个洞来还！', { name: '恩雅婆婆', actor: enya });
    await S.say('polnareff', '儿子……难道你是 J·凯尔的母亲？！');
    const sk = EI('skull');
    S.fx('tendrils', { pts: [[[sk[0] - 80, 151], [sk[0] - 40, 100]], [[sk[0] - 30, 149], [sk[0] - 50, 96]]], colour: '#bdcfc9' }, { life: 1 });
    S.standCard('justice');
    await lines(S, [['kakyoin', '她的雾钻进了伤口，所以能把人当成提线木偶。'], ['jotaro', '那就让这团雾，换个地方待着。']]);
    if (enya) enya.remove = true;
    const hh = S.actor('inn_guest'); if (hh) hh.remove = true;
    await S.fight(justiceSpec({ trial: false, wrap: s => s }));
  }
  // 雾散了：街上的“居民”一个个倒下（只写字、不画尸体）；恩雅被绑；荷尔·荷斯说出她是 J·凯尔的母亲，然后往镇外跑
  async function afterJustice(S) {
    calmStands(); party(S);
    const st = fitStage('fog_ch5'); st.npcs = []; st.hotspots = [];
    st.state = Object.assign({}, st.state, { mist: 0, night: 1 });
    const [ix] = FT('inn');
    await S.setStage('fog_ch5', { x: ix - 30, y: 164, music: 'sad' });
    S.state('mist', 0); S.state('night', 1);
    for (const [cid, dx] of [['jotaro', -30], ['joseph', -56], ['kakyoin', 10], ['polnareff', 30]]) place(S, cid, ix + dx, 164, 1);
    await S.say(null, '雾散了。街上那些一直在说“欢迎”的居民，一个接一个，静静地倒了下去。');
    const enya = S.spawn('enya', ix - 4, 166, { id: 'enya_captive', team: 'npc', name: '恩雅婆婆' }); enya.standReact = false; enya.talk = null; S.pose(enya, 'down');
    const hh = S.spawn('holhorse', ix + 60, 164, { id: 'holhorse_flees', team: 'npc', name: '荷尔·荷斯' }); hh.facing = -1; hh.standReact = false; hh.talk = null;
    await lines(S, [['holhorse', '……那位婆婆，是 J·凯尔的母亲。她从头到尾，都是冲着你们来报仇的。'],
      ['joseph', '先带她离开。我们还需要知道 DIO 的替身究竟是什么。'], ['enya', 'DIO 大人……不会输的……嘿嘿……']]);
    await S.say('holhorse', '那么，我就——先走一步啦！');
    hh.facing = 1;
    const ch = await S.choice(['放他走', '追'], '荷尔·荷斯往镇外跑');
    if (ch === 1) {
      const pol = S.actor('polnareff');
      S.walk(hh, ix + 220, 164, { speed: 170, anim: 'flee' }).catch(G.cancelIgnore);
      if (pol) await S.walk(pol, ix + 120, 164, { speed: 150, anim: 'walk' });
      await S.say('holhorse', '当 No.2……就是要跑得快！');
      await S.wait(.4);
      await S.say('polnareff', '……哈、哈……那家伙，逃跑的时候比谁都快！');
    } else {
      S.walk(hh, ix + 220, 164, { speed: 150, anim: 'flee' }).catch(G.cancelIgnore);
      await S.wait(.8);
      await S.say('polnareff', '……又让这家伙跑了。');
    }
    hh.remove = true;
    await S.say('jotaro', '……走吧。去卡拉奇。');
    await S.setStage('map_ch5', { x: 100, y: 160, music: 'travel' });
    await S.route(['瓦拉纳西', '卡拉奇'], { vehicle: 'car', day: 15, left: 36, history: ['东京', '香港', '新加坡', '加尔各答', '瓦拉纳西'] });
  }

  // ================================================================ 卡拉奇街市（karachi_ch5，karachi_street 640 宽）
  //   自由走动：水果摊（买芒果）、茶摊（拉茶小游戏）、手镯摊（砍价小游戏 → 纪念品）、屋檐下的女孩、排水沟、花纹巴士、停车位的吉普、
  //   被绑着的恩雅；去问路 → 斯蒂利·丹。
  function memberTalkKarachi() {
    T.memberTalk({
      joseph: async S => S.say('joseph', pick('c5kaJo', ['卡拉奇！港口城市，什么都买得到。', '芒果我请客！……别都挑最大的。'])),
      kakyoin: async S => S.say('kakyoin', pick('c5kaKa', ['恩雅还在我们手上。别以为换了城市，就没有替身使者。', '这么热闹的地方，最容易混进人。'])),
      polnareff: async S => S.say('polnareff', pick('c5kaPo', ['这里总算有人正常说话了。', '那边的巴士画得真花……比我的发型还显眼。'])),
      jotaro: async S => S.say('jotaro', pick('c5kaJt', ['……吵。', '……'])),
    });
  }
  // 拉茶：茶摊老板把热茶从高处倒进杯子；看准时机按 J（不影响剧情，只是好玩）
  //   5-12：每次 timing 时在茶摊上方画茶线——壶在 @tea 上方 34 px、杯在 @tea 上方 6 px，
  //   棕色竖线长度随 QTE 进度（q.m）从 0 拉满；成功后杯口一团白泡沫，0.6 s 消失。
  function chaiLine(S) {
    const t = KS('tea');
    return G.MID.pixel('ch5_chai_line', P => {
      const q = G.ui.qte, k = q && q.type === 'timing' ? G.clamp(q.m || 0, 0, 1) : 0;
      const x = Math.round(t[0] - (G.cam.x || 0)), y = Math.round(footY('karachi_ch5', t[1]));
      G.px.rect(P, x - 7, y - 40, 14, 9, '#c9c3b4');        // 壶身
      G.px.rect(P, x - 5, y - 37, 10, 6, '#8a5a2e');         // 壶里的茶
      G.px.rect(P, x - 5, y - 8, 11, 8, '#efe8d8');          // 杯
      G.px.rect(P, x - 5, y - 8, 11, 1, '#c8bfa8');
      if (k > 0) G.px.rect(P, x, y - 31, 1, Math.round(23 * k), '#8a5a2e');
    });
  }
  function chaiFoam(S) {
    const t = KS('tea');
    const p = G.MID.pixel('ch5_chai_foam', P => {
      const x = Math.round(t[0] - (G.cam.x || 0)), y = Math.round(footY('karachi_ch5', t[1]));
      G.px.disc(P, x - 2, y - 9, 2, '#fffef4', .9); G.px.disc(P, x + 2, y - 10, 2, '#fffef4', .9);
      G.px.disc(P, x, y - 12, 1, '#fffef4', .8);
    });
    G.defer(.6, () => S.unprop(p));
  }
  async function chaiGame(S, p) {
    const vend = S.actor('karachi_chai');
    const sayV = t => S.say('npc_merchant', t, { name: '茶摊老板', actor: vend });
    if (F().ch5ChaiDone) { await sayV(pick('c5chai2', ['再来一杯？今天的茶，特别香。', '拉得好的茶，泡沫才厚。'])); return; }
    await sayV('Chai！热奶茶！……客人，要不要自己试试“拉茶”？');
    const c = await S.choice(['试试', '直接喝一杯'], '茶摊');
    if (c !== 0) { S.sfx('splash', .3); await sayBy(S, p, { joseph: '这么热的天喝热奶茶……巴基斯坦人真了不起。', _: '甜得发腻，可是很解乏。' }); return; }
    let good = 0;
    const line = chaiLine(S);
    try {
      for (let r = 0; r < 2; r++) {
        const ok = await S.timing({ label: (r ? '再来一次：' : '') + '壶抬到最高时倒（J）', zone: [.46 - r * .02, .58 - r * .03], speed: 1.2 + r * .2 });
        S.sfx('splash', ok ? .5 : .3);
        if (ok) { good++; chaiFoam(S); }
        await sayV(ok ? '好！一滴都没洒！' : '哎呀，洒了一地……');
      }
    } finally { S.unprop(line); }
    F().ch5ChaiDone = true;
    await sayBy(S, p, good === 2
      ? { joseph: '哈哈！看到没有，这就叫手艺！', polnareff: 'Magnifique！我在巴黎也没见过这种倒法！', kakyoin: '……原来泡沫是这样拉出来的。', _: '……还行。' }
      : { joseph: '嗯……茶的味道，不受影响嘛！', polnareff: '我的衣服……全是奶茶……', _: '……下次再说。' });
  }
  // 砍价：手镯一只 50 卢比，三轮看准时机开价（每成一次 −13），砍到 24 以下成交 → 纪念品「玻璃手镯」
  async function bargain(S, p) {
    F().ch5BraceletSeen = true;
    const vend = S.actor('karachi_vendor');
    const sayV = t => S.say('npc_townsfolk', t, { name: '手镯摊老板', actor: vend });
    if (X.has('ch5_bangle')) { await sayV(pick('c5bang2', ['戴着好看吧？我这儿的玻璃，全卡拉奇最亮。', '只看不买也欢迎！'])); return; }
    await sayV('玻璃手镯！一只五十卢比，叮当作响！');
    const c = await S.choice(['砍价', '只是看看'], '手镯摊');
    if (c !== 0) { await sayV('看看也好，看看不要钱。'); return; }
    let price = 50;
    const said = [['四十！不能再多了！', '三十！我们是远道来的！', '二十！不卖我就走了！'], ['五十就五十……不不不，四十！', '三十五！', '二十五！']];
    for (let r = 0; r < 3; r++) {
      const ok = await S.timing({ label: '老板分神的一瞬间开价（J）', zone: [.42, .58 - r * .03], speed: 1.05 + r * .25 });
      await S.say(p.cid, said[p.cid === 'joseph' ? 0 : 1][r]);
      if (ok) { price -= 13; S.sfx('coin', .5); await sayV(['……好吧好吧。', '你这个人真会讲价！', '哎呀，算我倒霉！'][r] + '　' + price + ' 卢比！'); }
      else await sayV(['不行不行，' + price + ' 卢比，一分都不能少。', '我的手镯可是手工的！', '你看这光泽！'][r]);
    }
    if (price > 24) { await sayV(price + ' 卢比，这是底价了。'); await sayBy(S, p, { joseph: '……今天就算了。下次一定拿下！', _: '……下次再来。' }); return; }
    await sayV('成交！' + price + ' 卢比，拿去吧！');
    await X.give(S, 'ch5_bangle', { x: KS('bracelet')[0], y: KS('bracelet')[1] - 10 });
    await sayBy(S, p, { joseph: '哈哈！做生意，我可是专业的！', polnareff: '送给……嗯，先替雪莉收着。', kakyoin: '……买到了。安妮要是还在就好了。', _: '……叮当响。' });
  }
  function setupKarachi() {
    const st = fitStage('karachi_ch5');
    st.props = []; st.triggers = [];
    st.state = Object.assign({}, st.state);
    const [fx, fy] = KS('fruit_vendor'), [tx, ty] = KS('tea'), [vx, vy] = KS('vendor'), [gx, gy] = KS('girl'), [dx, dy] = KS('dan'), [jx, jy] = KS('jeep');
    st.npcs = [
      T.npc('npc_merchant', 'karachi_fruit', fx, footY('karachi_ch5', fy), { facing: -1, label: '水果摊', name: '水果摊老板', talk: async S => {
        await S.say('npc_merchant', pick('c5fruit', ['芒果！石榴！刚从信德运来的！', '先喝口水吧。今天的路够热的，水果给你们挑新鲜的。']), { name: '水果摊老板', actor: S.actor('karachi_fruit') });
        if (S.player.cid === 'joseph') { S.sfx('coin', .5); await S.say('joseph', '一人一个芒果，我请客！……别都挑最大的！'); }
      } }),
      T.npc('npc_merchant', 'karachi_chai', tx + 14, footY('karachi_ch5', ty + 6), { facing: -1, label: '茶摊', name: '茶摊老板', talk: S => chaiGame(S, S.player) }),
      T.npc('npc_townsfolk', 'karachi_vendor', vx, footY('karachi_ch5', vy), { facing: -1, label: '手镯摊', name: '手镯摊老板', talk: S => bargain(S, S.player) }),
      T.npc('npc_kid', 'karachi_girl', gx, footY('karachi_ch5', gy), { facing: -1, label: '屋檐下的女孩', name: '女孩', talk: async S => {
        await S.say('npc_kid', pick('c5girl', ['我在等妈妈买完东西。……你们是外国人？', '那边那个叔叔，一直在笑。']), { name: '女孩', actor: S.actor('karachi_girl') });
      } }),
      T.npc('enya', 'karachi_enya', jx - 40, footY('karachi_ch5', jy + 4), { facing: 1, label: '被绑着的恩雅', name: '恩雅婆婆', talk: async S => {
        await S.say('enya', pick('c5enyaK', ['DIO 大人……DIO 大人会来救我的……', '嘿嘿……你们什么都不会知道的。']), { name: '恩雅婆婆', actor: S.actor('karachi_enya') });
      } }),
      T.npc('steelydan', 'karachi_guide', dx, footY('karachi_ch5', dy), { facing: -1, label: '问路', name: '热心的男人', talk: async S => {
        await S.say('steelydan', '几位从远处来？我对这一带熟得很。……连你们身边这位婆婆，我也认识。', { name: '热心的男人', actor: S.actor('karachi_guide') });
        F().ch5DanStart = true;
      } }),
    ];
    const H = (id, k, label, tags, use, look, o = {}) => { const v = KS(k); return J.hot(id, v[0], footY('karachi_ch5', v[1] + 8), label, tags, use, look, Object.assign({ ly: v[1] - 30, r: 22 }, o)); };
    st.hotspots = [
      H('fruit_stall', 'fruit', '水果摊', [], async (S, h, p) => sayBy(S, p, { kakyoin: '石榴、芒果、西瓜……樱桃倒是没有。', polnareff: '这么大的西瓜！', _: '堆成小山的芒果和石榴。' })),
      H('bracelet_stall', 'bracelet', '手镯摊', ['detail'],
        async S => { F().ch5BraceletSeen = true; await S.say(S.player.cid, '竖杆上挂满了玻璃手镯，五颜六色。老板的视线一直跟着客人的手。'); },
        async S => { F().ch5BraceletSeen = true; await S.say('jotaro', '……老板每过两秒就转一次身。'); }),
      H('drain', 'bridge', '排水沟', [], async (S, h, p) => sayBy(S, p, { joseph: '盖板缺了一块。小心别踩进去！', _: '路中间的排水沟，盖板缺了一块。' })),
      H('bus', 'bus', '花纹巴士', [], async (S, h, p) => sayBy(S, p, { polnareff: '车身画满了花和孔雀……连保险杠都挂着铃铛！', joseph: '这车顶上的行李，堆得比车还高！', _: '画满花纹的巴士，车顶堆着行李。' })),
      H('jeep', 'jeep', 'SPW 的吉普', ['nensha', 'detail'],
        async S => { F().ch5JeepSeen = true; await S.say('joseph', '钥匙当然在我这里！这一次，车总不能自己跑了吧。'); },
        async S => { F().ch5JeepSeen = true; await S.say(S.player.cid, '……油加满了，车况不错。'); }),
    ];
    st.onLook = async (S, p) => S.say(p.cid, T.by(p, { kakyoin: '人太多了……替身的气息混在人群里。', _: '……热闹得很。' }));
  }
  async function karachiIntro(S) {
    calmStands(); setupKarachi();
    await S.setStage('karachi_ch5', { x: KS('arrive')[0] + 20, y: 164, music: 'daily' });
    amb(S, 'bazaar_loop', 'crowd_loop', .16);
    party(S);
    const ar = KS('arrive');
    for (const [cid, dx] of [['jotaro', 40], ['joseph', 20], ['kakyoin', 0], ['polnareff', 60]]) place(S, cid, ar[0] + dx, 164 + (dx % 4), 1);
    T.prop(S, 'spw_jeep', KS('jeep')[0], footY('karachi_ch5', KS('jeep')[1]), { id: 'parked_jeep' });
    S.location('karachi');
    await S.wait(.6);
    await lines(S, [['joseph', '卡拉奇。先停下喝口水，谁也别离开太远。'], ['polnareff', '这里总算有人正常说话了。那边还有卖手镯的！'],
      ['kakyoin', '恩雅还在我们手里。别以为换了城市，就不会有替身使者。']]);
    memberTalkKarachi(); follow();
  }
  async function loversIntro(S) {
    calmStands();
    const dan = S.actor('karachi_guide');
    await lines(S, [['steelydan', '我叫斯蒂利·丹。DIO 大人托我，向恩雅婆婆道声谢。'], ['joseph', '你也是他的手下！退后，别碰她！']]);
    S.nameCard('steelydan');
    // 恩雅之死：剪影 + 触手的影子 + 黑场（规划 §6.4 克制处理），她到最后也没说出 DIO 的能力
    await S.say('enya', 'DIO 大人……我、我什么都没说——', { name: '恩雅婆婆', actor: S.actor('karachi_enya') });
    const h = T.show(S, { bg: 'black', parts: [{ kind: 'sprite', cid: 'enya', anim: 'hurt', x: 160, y: 160, scale: 2, alpha: .35 }] });
    S.fx('tendrils', { pts: [[[130, 65], [170, 130]], [[190, 65], [152, 150]]], colour: '#332238' }, { space: 'canvas' });
    S.sfx('heartbeat', .6);
    await S.wait(.9); h.close();
    const ey = S.actor('karachi_enya'); if (ey) ey.remove = true;
    await S.say(null, '恩雅倒下了。她到最后，也没有说出 DIO 的能力。');
    const jos = S.actor('joseph'); if (jos) { jos.follow = null; S.pose(jos, 'shock'); }
    await lines(S, [['joseph', '头……有东西在我脑子里！'], ['steelydan', '是我的“恋人”。你们打在我身上的痛，它会加倍送给乔斯达先生。'],
      ['kakyoin', '我们把替身缩小，进去找它。波鲁纳雷夫，跟着我的光点。'], ['jotaro', '……我留在外面。欠下的账，最后再算。']]);
    if (jos) S.unpose(jos);
    if (dan) dan.talk = null;
    const st = G.STAGES.karachi_ch5; st.npcs = []; st.hotspots = [];
    S.standCard('lovers');
    await S.setStage('brain_ch5', { x: BR('arrive')[0], y: 150, music: 'battle' });
    S.state('pulse', 0);
    await S.fight(G.BOSS25.lovers());
  }
  async function ending(S) {
    S.insertUI(null); calmStands(); party(S);
    const jp = KS('jeep');
    await S.setStage('karachi_ch5', { x: jp[0] - 80, y: 164, music: 'daily' });
    for (const [cid, dx] of [['jotaro', -82], ['joseph', -48], ['kakyoin', -106], ['polnareff', -126]]) place(S, cid, jp[0] + dx, 164, 1);
    const jeep = T.prop(S, 'spw_jeep', jp[0], footY('karachi_ch5', jp[1]), { id: 'stolen_jeep' });
    const hh = S.spawn('holhorse', jp[0] + 40, 164, { id: 'holhorse_driver', team: 'npc', name: '荷尔·荷斯' }); hh.facing = -1; hh.standReact = false; hh.talk = null;
    await S.walk(hh, jp[0], 160, { speed: 140, anim: 'flee' });
    await lines(S, [['holhorse', '你们忙着结账，这吉普我就先借走啦！'], ['joseph', '我、我的车！钥匙明明还在我这里！']]);
    S.sfx('car_engine');
    if (jeep) { const stopRoll = roll(jeep); S.walk(jeep, jp[0] + 160, footY('karachi_ch5', jp[1]), { speed: 150, anim: 'idle', endAnim: 'idle' }).then(stopRoll).catch(G.cancelIgnore); }
    S.walk(hh, jp[0] + 160, 150, { speed: 150, anim: 'idle' }).catch(G.cancelIgnore);
    const jos = S.actor('joseph'); if (jos) S.walk(jos, jp[0] - 10, 164, { speed: 110, anim: 'run' }).catch(G.cancelIgnore);
    await S.wait(1.0);
    if (jeep) jeep.remove = true; hh.remove = true;
    await lines(S, [['polnareff', '至少这一次，车是被偷的，不是被你撞坏的。'], ['joseph', '这种安慰，我一点都不需要！'], ['jotaro', '……走吧。天还没黑。']]);
    await J.end(S, 'ch5_tbc');
  }

  // ================================================================ 本章入口
  G.STORY.ch5 = async S => {
    T.resetCounters();
    for (const key of ['fogClues', 'justiceStart', 'ch5DanStart', 'ch5BraceletSeen', 'ch5JeepSeen', 'ch5Bill', 'ch5StreetResults', 'ch5ZombieRevives',
      'ch5Wc', 'ch5PolCut', 'ch5Register', 'ch5ChaiDone']) delete F()[key];
    Object.assign(F(), { anneJoined: true, anneNamed: true, anneLeft: false });
    await G.MID.ensureBg('_ch5'); party(S);
    await S.chapterCard('ch5');
    await S.setStage('map_ch5', { x: 100, y: 160, music: 'travel' });
    await S.run(async s => {
      await s.route(['瓦拉纳西', '卡拉奇'], { vehicle: 'car', day: 12, left: 39, cut: .6, history: ['东京', '香港', '新加坡', '加尔各答', '瓦拉纳西'] });
      await roadIntro(s); await cliffBattle(s); await anneFarewell(s);
      await s.setStage('map_ch5', { x: 100, y: 160, music: 'travel' });
      await s.say(null, '第十三天。巴基斯坦，边境的小镇。……雾，漫了上来。');
    });
    // 雾之镇：自由走动，至少两样不同的异常，再找旅馆门口的恩雅
    setupFog();
    await S.setStage('fog_ch5', { x: FT('arrive')[0], y: 163, music: 'tension' });
    party(S); memberTalkFog(); follow();
    S.state('mist', 1); S.state('night', 0);
    amb(S, 'wind_loop', 'wind', .1);
    S.location('fog_town');
    // 5-07 线索栏：右上两行「异常 n / 2」+ 已发现的名字（10-20 按脚本新增；进旅馆后收起）
    const CLUE_NAME = { pulse: '脉搏', shadow: '影子', lamp: '路灯', well: '井', grave: '墓地', board: '告示', photo: '照片', clock: '钟' };
    G.MID.ui(S, g => {
      if (F().justiceStart) return;
      const keys = Object.keys(F().fogClues || {}).filter(k => CLUE_NAME[k]);
      G.MID.hud(g, ['异常 ' + Math.min(keys.length, 2) + ' / 2', keys.map(k => CLUE_NAME[k]).join('、')]);
    });
    S.free(true);
    S.hint('先调查两个不同的异常，再找旅馆门口的恩雅婆婆。', 10);
    const inn = FT('inn');
    T.goal(S, { x: inn[0], y: footY('fog_ch5', inn[1]), h: 56, label: '旅馆', delay: 45, every: 20, done: () => !!F().justiceStart, text: '这里的居民不对劲，调查之后再进旅馆。' });
    await S.until(() => F().justiceStart && !S.busy);
    S.free(false);
    S.insertUI(null);   // 线索栏收起（进旅馆以后不再画）
    await S.run(async s => { await innIntro(s); });
    await innExplore(S);
    await S.run(async s => { await innWc(s); await afterJustice(s); await karachiIntro(s); });
    // 卡拉奇：自由走动，再向街上的斯蒂利·丹问路
    S.free(true);
    S.hint('逛逛卡拉奇的街市，再向街上那个热心的男人问路。', 10);
    const dan = KS('dan');
    T.goal(S, { x: dan[0], y: footY('karachi_ch5', dan[1]), h: 56, label: '问路', delay: 40, every: 20, done: () => !!F().ch5DanStart, text: '那个男人好像认识恩雅。' });
    await S.until(() => F().ch5DanStart && !S.busy);
    S.free(false);
    await S.run(async s => { await loversIntro(s); await ending(s); });
  };

  // ================================================================ 星尘试炼关卡工厂（剧情 / 挑战 / 试炼共用同一份配置）
  //   setup 只布景，不含 S.party；只有剧情路线显式传 o.trial = false（原来的位置补上队伍），
  //   试炼不传 / 传 true 都不会碰队伍
  G.TRIAL_SRC['b09b_wheeloffortune'] = {
    chapter: 'ch5', pack: '_ch5',
    setup: async (S, o = {}) => {
      await G.MID.ensureBg('_ch5');
      if (o.trial === false) party(S);
      await S.setStage('cliff_ch5', { x: MR('arrive')[0], y: 162, music: 'battle' });
      // 每次进关都复位：上一轮的汽油 / 烧黑 / 地洞不能留到下一轮
      S.state('oil', 0); S.state('scorch', 0); S.state('hole', 0);
    },
    spec: o => wheelSpec(o),
  };
  G.TRIAL_SRC['b10_justice'] = {
    chapter: 'ch5', pack: '_ch5',
    setup: async (S, o = {}) => {
      await G.MID.ensureBg('_ch5');
      if (o.trial === false) party(S);
      await S.setStage('inn_ch5', { x: 75, y: 164, music: 'battle' });
      // 雾与前景柜台：onWave 里也会设，这里负责重复进入时先复位
      S.state('fog', 1); S.state('counter', 0);
    },
    spec: o => justiceSpec(o),
  };

  // ================================================================ 单战入口（开发调参 G.DEV / 标题「挑战」，战斗配置和正式剧情是同一份）
  G.DEV = G.DEV || {};
  G.DEV.ch5WheelRoad = async S => { await G.MID.ensureBg('_ch5'); party(S); await S.setStage('road_ch5', { x: 80, y: 160, music: 'battle' }); await S.run(s => s.fight(G.BOSS25.wheelroad())); };
  G.DEV.ch5Wheel = async S => { const src = G.TRIAL_SRC['b09b_wheeloffortune']; await src.setup(S, { trial: false }); await S.run(s => s.fight(src.spec({ trial: false, wrap: x => x }))); };
  G.DEV.ch5Justice = async S => { const src = G.TRIAL_SRC['b10_justice']; await src.setup(S, { trial: false }); await S.run(s => s.fight(src.spec({ trial: false, wrap: x => x }))); };
  // 旅馆大堂的自由走动 → 正义（调剧情 / 查卡住用）
  G.DEV.ch5Inn = async S => { await G.MID.ensureBg('_ch5'); party(S); await S.run(async s => { await innIntro(s); }); await innExplore(S); await S.run(async s => { await innWc(s); }); };
  G.DEV.ch5Lovers = async S => { await G.MID.ensureBg('_ch5'); S.party(['kakyoin', 'polnareff'], { leader: 'kakyoin' }); await S.setStage('brain_ch5', { x: 80, y: 150, music: 'battle' }); await S.run(s => s.fight(G.BOSS25.lovers())); };
  X.challenge({ id: 'b09a_wheelroad', chapter: 'ch5', title: 'VS 命运之轮 · 公路追车（承太郎）', run: S => G.DEV.ch5WheelRoad(S) });
  X.challenge({ id: 'b09b_wheeloffortune', chapter: 'ch5', title: 'VS 命运之轮（承太郎）', run: S => G.DEV.ch5Wheel(S) });
  X.challenge({ id: 'b10_justice', chapter: 'ch5', title: 'VS 正义（承太郎）', run: S => G.DEV.ch5Justice(S) });
  X.challenge({ id: 'b11_lovers', chapter: 'ch5', title: 'VS 恋人（花京院 / 波鲁纳雷夫）', run: S => G.DEV.ch5Lovers(S) });
})();
