// 第10章　开罗 / 赌局与看门鸟（原著 211–226 话，游戏内第 36–48 天）
//   2026-10-20 照游玩脚本 ch10 整章重写（规划方出脚本与素材，实施方只写代码）。
//   初版（10 月初，15 KB）能跑的机关沿用改造：soul()（改成“头像缩成光吸进筹码”的新演出）、
//   catchCheat()（抓发牌小哥多抽一张牌）、poker() 的冷汗循环（选项顺序照脚本）、
//   holhorseSpec()（三个预言共用一个打不死的荷尔·荷斯）、prophecy()、birdFight()（反咬 + 冻平台）、
//   章末 G.res.loadPack('bg_ch11')。
//   这一版补上：咖啡馆 / 开罗的自由走动、找馆三条线索 + 推理小游戏、屋顶与 DIO 的回忆（灰一帧不点破时停）、
//   伊奇钻进下水道、尼罗河边孩子包扎，台词逐字照脚本，坐标全部取背景导出的 anchors（bgA 带默认值）。
//
//   流程：篇章卡 → 航线（卢克索 → 开罗郊外，第36天）→ 咖啡馆（三回合赌局：猫 · 出千 · 扑克）→ 空筹码
//   → 开罗（三条线索 → 推理圈城北）→ 屋顶 / 回忆 → 第 22 战三个托特预言 → 荷尔·荷斯退休
//   → 第 47 天伊奇溜出去 → 第 23 战荷鲁斯神（街道 → 下水道）→ 伊奇记住那栋馆 → 第 48 天馆外，TBC。
//
//   克制处理（脚本“克制处理”）：灵魂只画头像吸进筹码；子弹擦过帽子不见血；DIO 不露脸、时停只灰一帧；
//   佩特夏普只交代“再也没飞起来”+ 水面一根羽毛；伊奇的伤只画绷带、走路一瘸。
'use strict';
(function () {
  const G = window.G, W = G.world, L = G.LATE, T = G.TPL, M = G.MID, X = G.EXTRA;
  G.TRIAL_SRC = G.TRIAL_SRC || {};   // 星尘试炼的关卡工厂（本文件末尾登记）
  const F = () => G.flags;
  const crew = ['jotaro', 'joseph', 'avdol', 'polnareff', 'iggy'];
  const pick = (key, arr) => arr[(T.count(key) - 1) % arr.length];
  // 音效：新合成的音效还没进数据包时用现成的顶上（直接播不存在的名字会记 missingSfx）
  const hasSnd = n => !!(G.audio && G.audio.has && G.audio.has(n));
  const snd = (name, alt, o = {}) => { if (hasSnd(name)) G.audio.sfx(name, o); else if (alt) G.audio.sfx(alt, o); };
  const amb = (S, name, alt, vol) => { if (hasSnd(name)) S.ambient(name, vol); else if (alt) S.ambient(alt, vol * .6); };

  // ---------------------------------------------------------------- 背景锚点（没有就用背景规格里的默认值）
  const bgA = (bg, k, d) => { const b = G.D && G.D.bg && G.D.bg[bg]; const v = b && b.anchors ? b.anchors[k] : null; return v != null ? v : d; };
  const Cd = {
    table: [104, 118, 216, 132], cafe_table: [160, 132], seat_left: [82, 150], seat_right: [238, 150], dealer: [160, 127],
    cat: [36, 164], bar: [280, 146], window: [60, 70], chips: [160, 124], painting: [124, 74], door: [12, 160],
    meat: [[132, 168], [160, 168], [188, 168]], dealer_talk: [160, 152],
  };
  const CDd = {
    arrive: [40, 164], bakery: [150, 152], asker: [230, 160], hotel: [290, 150], hotel_roof: [300, 64], kids: [360, 164],
    mirror_stand: [410, 160], fruit_stand: [470, 160], oil_drum: [520, 162], road_sign: [580, 150], crossroad: [640, 162],
    alley: [700, 152], sewer_grate: [760, 170], corner: [860, 150], exit: [940, 162], rooftop: [860, 70], road_sign_top: [580, 123],
  };
  const SWd = {
    arrive: [40, 160], platforms: [[0, 150, 140], [170, 152, 300], [330, 150, 470], [500, 152, 640]],
    grates: [[120, 20], [400, 20]], exit_grate: [610, 40], ladder: [610, 148], water_y: 170,
    gaps: [[140, 170], [300, 330], [470, 500]],
  };
  const MHd = { dio_seat: [306, 143], stairs_up: [300, 160], pillar_shaft: [27, 142], beam_x: [250, 166] };
  const PKd = {
    j_cards: [[128, 126], [144, 126], [160, 126], [176, 126], [192, 126]],
    d_cards: [[128, 56], [144, 56], [160, 56], [176, 56], [192, 56]],
    pot: [160, 96], face: [287, 39], face_foot: [287, 55], sweat: [262, 26],
    sweat_list: [[262, 26], [260, 34], [262, 42]],
  };
  const CMd = { north: [176, 34], south: [176, 148], old_town: [190, 96], west_bank: [52, 96], cards: [[282, 36], [282, 88], [282, 140]] };
  // 章末借第 11 章的馆外远景（mansion_exterior）：铁门与来路的锚点
  const MEd = { arrive: [60, 164], gate: [160, 160], door: [160, 138], steps: [200, 162], tree: [262, 160], crow: [240, 60] };
  const CA = k => bgA('cafe_interior', k, Cd[k]);
  const CD = k => bgA('cairo_day', k, CDd[k]);
  const SW = k => bgA('cairo_sewer', k, SWd[k]);
  const MH = k => bgA('mansion_hall', k, MHd[k]);
  const ME = k => bgA('mansion_exterior', k, MEd[k]);
  const PK = k => bgA('poker_table', k, PKd[k]);
  const CM = k => bgA('cairo_map', k, CMd[k]);
  // 世界地图上本章要用的“开罗郊外”（CITIES 里只有大城市，这里补一个坐标给航线用，同第 8 章的“埃及东部沙漠”）
  if (!T.CITIES['开罗郊外']) T.CITIES['开罗郊外'] = [46, 66];
  // 站人的锚点 y 夹进可走带（物件锚点给的是物件底，人要站在它前面）
  const footY = (id, y) => { const st = G.STAGES[id]; return G.clamp(y, st.yMin + 2, st.yMax - 2); };

  function place(S, cid, x, y, facing = 1) {
    const a = S.actor(cid); if (!a) return null;
    a.visible = true; a.follow = null; a.x = x; a.y = footY(W.stage.id, y); a.facing = facing; a.alpha = 1; a.scale = 1; S.unpose(a);
    return a;
  }
  function sit(S, cid, x, y, facing = 1) {
    const a = place(S, cid, x, y, facing);
    if (a) S.pose(a, 'sit', { freeze: 0 });
    return a;
  }
  // 角色原地播一段动作（不挡剧情）
  function act(a, anim, ms) {
    if (!a) return;
    a.hold = true; a.frozen = null; a.play(anim, { restart: true });
    G.defer((ms || 600) / 1000, () => { if (a && !a.remove) { a.hold = false; a.play(a.idleAnim || 'idle'); } }, 'world');
  }
  // 道具图集直接画（图集还没载入时安静跳过，不报错）
  const propAt = (g, id, frame, x, y, o = {}) => {
    const A = G.propAtlas(id);
    if (A && A.ready && A.ready()) A.draw(g, 'idle', frame, x, y, o);
  };
  // 第 8 章样式的漫画格：帧 6/7、8/9、10/11，第三格 12 = 大问号
  const comicCell = (g, frame, x, y) => propAt(g, 'comic_panel', frame, x + 34, y + 56, { scale: 1 });

  // ---------------------------------------------------------------- 纪念品（story\extras.js）
  X.souvenir({ id: 'ch10_empty_chip', chapter: 'ch10', name: '达比的空筹码', desc: '曾经装过一个灵魂的筹码。现在，它只是一枚普通的筹码了。', hint: '咖啡馆的牌桌（赌局之后，要会念写的人）' });
  X.souvenir({ id: 'ch10_circled_map', chapter: 'ch10', name: '画了圈的开罗地图', desc: '乔瑟夫用红笔圈出城北的那张地图。', hint: '开罗，三条线索都找到以后的推理' });
  X.souvenir({ id: 'ch10_bandage', chapter: 'ch10', name: '伊奇的绷带', desc: '尼罗河边一个孩子给伊奇包的。伊奇一直没让人拆。', hint: '剧情获得' });

  // ================================================================ 灵魂吸进筹码（新演出）
  // 克制：不画灵魂离体的过程，只画头像被拉成一道光、收进一枚筹码；筹码上浮出一张小小的脸。
  async function soul(S, cid, frame = 0) {
    snd('soul_drain', 'drain', { vol: .7 });
    const h = T.show(S, { bg: '#0b0a12', draw(g, t) {
      const k = G.clamp(t / 1.0, 0, 1);
      if (t < 1.0) {
        // 头像 ×4 在中间 → 1.0 s 内缩成一道光（alpha 降、往筹码的位置收）
        T.part(g, { kind: 'head', cid, scale: 4 + k * 1.6, x: 160, y: G.lerp(92, 116, k), alpha: 1 - k * .9, jitter: 1.4 });
        g.fillStyle = 'rgba(255,238,170,' + (.8 * k).toFixed(3) + ')';
        g.fillRect(160 - Math.round(30 * (1 - k)), G.lerp(96, 112, k), Math.max(1, Math.round(60 * (1 - k))), 3);
      } else {
        // 筹码在画面中间（scale 4）浮起来，脸上带着一点点表情
        const up = G.clamp((t - 1.0) / .5, 0, 1);
        propAt(g, 'soul_chip', frame, 160, G.lerp(134, 116, up), { scale: 4 });
      }
    } });
    try { await S.wait(1.6); } finally { h.close(); }
  }
  G.LATE.soul = soul;

  // ================================================================ 抓出千（沿用初版：1.05–1.26 s 多抽一张牌，那一瞬按 J）
  async function catchCheat(S, sweat, round) {
    const q = { type: 'dealer', caught: false, tooEarly: false, sweat, round,
      touch: { buttons: ['j'], captions: { j: '抓出千' } } };
    await L.game(S, q, s => {
      s.extra = s.t >= 1.05 && s.t <= 1.26;
      if (L.hit('attack')) { if (s.extra && !s.tooEarly) { s.caught = true; S.sfx('card_flip'); } else s.tooEarly = true; }
      if (s.t >= 2) { s.done = true; s.win = s.caught; }
    }, (g, s) => {
      g.fillStyle = '#154538'; g.fillRect(0, 0, 320, 180);
      T.sprite(g, 'darby', 'sit', 0, 259, 170, { scale: 2 });
      for (let n = 0; n < 4; n++) { g.fillStyle = '#eadbb6'; g.fillRect(48 + n * 27, 100, 20, 29); }
      g.fillStyle = '#dba57e'; g.fillRect(112 + Math.sin(s.t * 5) * 15, 81, 34, 13);
      if (s.extra) { g.fillStyle = '#ffdc63'; g.fillRect(146, 92, 20, 28); }
    }, (g, s) => {
      L.label(g, '盯住发牌的手', '多抽一张牌的瞬间按 J；提前动手会打草惊蛇');
      const drops = Math.min(3, Math.floor(s.sweat / 25)); L.text(g, '汗滴 ' + '●'.repeat(drops), 450, 278, '#8ccaff');
      if (s.caught) L.text(g, '抓到了！', 320, 315, '#ffe174', 'center');
    }); return q.caught;
  }

  // ================================================================ 牌桌插画（poker_table + 锚点）
  function drawPoker(g, st) {
    const jc = PK('j_cards'), dc = PK('d_cards'), pot = PK('pot'), face = PK('face');
    // 承太郎的 5 张一直扣着，开牌时才翻（帧 0 = 背面，1 = 正面）
    jc.forEach(p => propAt(g, 'card', st.reveal ? 1 : 0, p[0], p[1], { scale: 1 }));
    // 达比的 5 张
    dc.forEach(p => propAt(g, 'card', st.reveal ? 1 : 0, p[0], p[1], { scale: 1 }));
    // 底池：每押一次多叠一枚（每三枚里有一枚是装灵魂的筹码）
    for (let n = 0; n < st.pot; n++) {
      const x = pot[0] - 9 + (n % 3) * 9, y = pot[1] - Math.floor(n / 3) * 4;
      propAt(g, n % 3 === 2 ? 'soul_chip' : 'chip', n % 2, x, y, { scale: 1 });
    }
    // 右上达比的头像（冷汗 ≥ 70 换 sweat 表情）+ 汗滴 0–3 颗
    T.part(g, { kind: 'head', cid: 'darby', expr: st.sweat >= 70 ? 'sweat' : null, x: face[0], y: face[1] });
    const drops = Math.min(3, Math.floor(st.sweat / 25)), list = PK('sweat_list');
    for (let n = 0; n < drops; n++) { g.fillStyle = '#8ccaff'; g.fillRect(list[n][0], list[n][1], 2, 3); }
    // 开牌后：筹码裂开，两道光飞回左右两边（波鲁纳雷夫 / 乔瑟夫）
    if (st.reveal) {
      const k = st.glow || 0;
      g.fillStyle = 'rgba(255,240,180,' + (.65 * (1 - k)).toFixed(3) + ')';
      for (const side of [-1, 1]) {
        const x0 = pot[0], y0 = pot[1];
        g.fillRect(side < 0 ? x0 - k * 110 : x0, y0 - k * 34, k * 110, 2);
      }
    }
  }

  // ================================================================ 回合 3：扑克（冷汗 0–100，连看两手判负重来这一手）
  async function poker(S) {
    const st = { sweat: 0, looks: 0, bluff: false, pot: 0, hand: 0, reveal: false, glow: 0 };
    const ins = T.show(S, { bg: 'poker_table', draw(g) { drawPoker(g, st); } });
    S.insertUI(g => L.hud(g, ['赌局 · 扑克　第 ' + (st.hand + 1) + ' 手', '冷汗 ' + st.sweat]));
    try {
      for (;;) {
        // 选项顺序照脚本：第一个“不看牌，直接加注”是推进剧情的那个
        const opts = ['不看牌，直接加注', '押同伴的灵魂', '押母亲的灵魂'];
        if (!st.bluff) opts.push('「我已经换过牌了。你要看吗？」');
        opts.push('看牌');
        const i = await S.choice(opts, '承太郎的下注');
        const what = opts[i];
        if (what === '看牌') { st.looks++; st.sweat = Math.max(0, st.sweat - 10); }
        else {
          st.looks = 0;
          st.sweat += what === '不看牌，直接加注' ? 20 : what === '押同伴的灵魂' ? 25 : what === '押母亲的灵魂' ? 40 : 50;
          if (what.charAt(0) === '「') st.bluff = true;
          st.pot = Math.min(12, st.pot + 1);
        }
        G.dbg.ev('poker', { sweat: st.sweat, looks: st.looks, bluffUsed: st.bluff, hand: st.hand });
        if (st.looks >= 2) {
          // 连看两手：这一手判负，冷汗清零重来（必败段不伪装成玩家失败）
          await S.say('darby', '看牌了？……那我就加注到底！');
          st.pot = 12;
          await S.say('jotaro', '……');
          await S.narrate('看牌反而暴露了想法。重来这一手。');
          st.sweat = 0; st.looks = 0; st.pot = 0;
          continue;
        }
        if (st.sweat >= 100) break;
        // 每一手选完（冷汗还不到 100）抓一次出千：抓到 +15
        if (await catchCheat(S, st.sweat, st.hand)) st.sweat += 15;
        await S.say('darby', st.sweat >= 70 ? '这……这不可能。他到底换了什么牌？！'
          : st.sweat >= 40 ? '……你在虚张声势。我看得出来。' : '你连牌都不看……到底有什么把握？');
        st.hand++;
        G.dbg.ev('poker', { sweat: st.sweat, looks: st.looks, bluffUsed: st.bluff, hand: st.hand });
      }
    } finally { ins.close(); S.insertUI(null); }
    F().darbySweat = Math.min(100, st.sweat);
    return st;
  }

  // 开牌：5 张散牌翻开、筹码裂开、两道光飞回
  async function pokerReveal(S) {
    const st = { sweat: 100, pot: 0, reveal: true, glow: 0 };
    const ins = T.show(S, { bg: 'poker_table', draw(g) { drawPoker(g, st); } });
    try {
      S.sfx('card_flip', .8);
      await S.wait(.6);
      await S.animate(.7, k => { st.glow = k; });
      S.sfx('sparkle', .6);
      await S.wait(.5);
    } finally { ins.close(); }
  }

  // ================================================================ 第 22 战：三个托特预言
  // 三个预言在同一张地图上连着打：荷尔·荷斯打不死、每场用 c.end() 收尾，敌人不会被移走。
  // 每场新建一份敌人写法会留下上一场的荷尔·荷斯（第 3 个预言时场上三个人一起开枪），
  // 所以同一章里三场共用一份写法 → fight.spawn 按 e._obj 复用同一个角色。
  const holhorseSpec = () => ({ cid: 'holhorse', kit: 'e_holhorse_late', boss: true, hp: 99999, x: 620, y: 160 });

  // 预言 3 的荷尔·荷斯：追着伊奇走 40 px/s，但停在伊奇右边 65 px。
  //   kit 的 brain 是“保持 65 px”，按当前所在的那一侧停——玩家从左边跑过去以后他会停在玩家左边（离路口 638 很远）；
  //   脚本要的是“把荷尔·荷斯引到发光的路口”，所以固定停在他右边：玩家站 578 时他正好停在 643（路口 638 ± 35 内）。
  function holhorseChase() {
    return function (e, dt, c) {
      if (!dt) return true;
      const p = c.player;
      e.facing = p.x >= e.x ? 1 : -1;
      const wantX = G.clamp(p.x + 65, c.spec.arena[0] + 20, c.spec.arena[1] - 20);
      e.x += G.clamp(wantX - e.x, -40 * dt, 40 * dt);
      e.y += G.clamp(p.y - e.y, -40 * dt, 40 * dt);
      e.mem.fire = (e.mem.fire || 0) + dt;
      const every = c.assist ? 2.2 : 1.5;   // 放水：子弹 2.2 s 一发
      if (e.mem.fire >= every) { e.mem.fire %= every; G.combat.shoot(e, G.MOVES.HH_LATE_BULLET.shot); G.S.sfx('gunshot'); }
      return true;
    };
  }

  async function comicPanel(S, index) {
    const frames = [[6, 7], [8, 9], [10, 11]][index];
    const h = T.show(S, { bg: 'black', letterbox: 16, draw(g) {
      comicCell(g, frames[0], 40, 60);
      comicCell(g, frames[1], 150, 60);
      comicCell(g, 12, 260, 60);   // 第三格：大问号
    } });
    try { await S.wait(1.5); } finally { h.close(); S.letterbox(false); }
  }

  async function prophecy(S, index, hh = holhorseSpec()) {
    const xMirror = CD('mirror_stand')[0], xDrum = CD('oil_drum')[0], target = CD('crossroad')[0];
    S.mark('ch10_prophecy_' + (index + 1));
    await comicPanel(S, index);
    await S.say('boingo', ['十五秒后，镜子前面……子弹会打中头！', '十五秒后，油桶旁边，有人滑倒、被子弹打中！',
      '十五秒后，路口正中间，有人被子弹打中！'][index]);
    await S.fight({ id: 'b22_prophecy' + (index + 1), lead: 'iggy', swap: true, arena: [300, 700], vs: index === 0 ? 'emperor_thoth' : null,
      allies: ['polnareff'], bench: 'hide', finish: 'none', music: 'battle_egypt', par: 30, waves: [[hh]],
      steps: { label: '让预言落到荷尔·荷斯身上', n: 3, total: 3, done: index },
      timer: { label: '预言', until: 15 },
      testHint: c => ({ phase: index + 1, targetX: index === 0 ? xMirror : index === 1 ? c.data.drumX : target,
        rotated: c.data.rotated, drumX: c.data.drumX, oil: c.data.oil, hhX: c.boss ? c.boss.x : null, left: Math.max(0, (c.data.limit || 15) - c.t) }),
      onWave(s, n, es, attempt, c) {
        W.stage.props = W.stage.props.filter(p => !String(p.id || '').startsWith('late_'));
        // 街景里的镜子 / 油桶（id street_*）在这一战由 late_* 顶替：留着会和可转、可推的那两个重叠，
        //   转镜子、推油桶时就只动一份，另一份停在原地
        W.stage.actors = W.stage.actors.filter(a => !a.lateProp && !/^street_/.test(String(a.id || '')));
        c.player.x = 360; c.player.y = 160; c.data.rotated = false; c.data.drumX = xDrum; c.data.oil = false;
        // 倒计时：脚本 15 s；放水（assist）每个预言 20 s
        c.data.limit = c.assist ? 20 : 15;
        if (G.hud && G.hud.timer) G.hud.timer.until = c.data.limit;
        if (index === 2 && c.boss) c.boss.brain = holhorseChase();
        const mirror = T.prop(s, 'mirror_stand', xMirror, footY('cairo_day_ch10', CD('mirror_stand')[1]), { id: 'late_mirror' });
        const drum = T.prop(s, 'oil_drum', xDrum, footY('cairo_day_ch10', CD('oil_drum')[1]), { id: 'late_drum' });
        c.data.mirror = mirror; c.data.drum = drum;
        if (mirror) mirror.lateProp = true;
        if (drum) drum.lateProp = true;
        s.insertUI(g => L.hud(g, ['托特神 · 第' + (index + 1) + '个预言　' + Math.ceil(Math.max(0, (c.data.limit || 15) - c.t)) + ' 秒',
          ['靠近镜子按 E 转向，反射他的子弹', '靠近油桶按 E，把它推到路中央',
            '把荷尔·荷斯引到发光的路口（伊奇在前面跑，他会追）'][index]]));
        // 路口发黄光（半透明 30×25 黄框）
        L.pixel(P => G.px.rect(P, target - 15 - G.cam.x, 148, 30, 25, '#eecf68', .33));
        if (index === 1) L.pixel(P => { if (c.data.oil) G.px.rect(P, c.data.drumX - 8 - G.cam.x, 168, 46, 4, '#2c2620', .9); });
      },
      tick(c, dt) {
        if (L.hit('ok')) {
          if (index === 0 && Math.abs(c.player.x - xMirror) < 30) { c.data.rotated = true; if (c.data.mirror) c.data.mirror.facing = -1; S.sfx('clang'); }
          if (index === 1 && Math.abs(c.player.x - c.data.drumX) < 35) {
            c.data.drumX += 30; if (c.data.drum) c.data.drum.x = c.data.drumX;
            c.data.oil = c.data.drumX >= target - 40; S.sfx('thud');
          }
        }
        // 预言 3 的追击在 onWave 里换了 brain（holhorseChase）：固定在伊奇右边 65 px，见那个函数的说明
        if (c.t >= (c.data.limit || 15)) {
          const win = index === 0 ? c.data.rotated : index === 1 ? c.data.oil : Math.abs(c.boss.x - target) <= 35;
          if (win) { c.boss.play('hurt'); S.sfx('gunshot'); S.impact('invert', 2 / 60); c.step(index + 1); c.end(); }
          else {
            // 子弹擦过操作角色的头：白闪 + 帽子 / 头发弹起来（不见血）
            L.damage(c, 40); S.flash(.16, .7);
            const hat = c.spawn({ cid: 'prop:hat', x: c.player.x, y: c.player.y - 26, team: 'object', untouchable: true, id: 'c10_hat' });
            if (hat) { hat.vy = -70; hat.vx = 26; hat.fly = true; }
            c.fail('预言落到了自己身上……只重来当前预言。');
          }
        }
      }, after(s) { s.insertUI(null); },
      onRetry(s) { s.hint('这个预言重新开始；前面的兑现结果保留。', 4); },
    });
    F()['ch10Prophecy' + (index + 1)] = true;   // 章末自检：三个预言各兑现一次
  }

  // ================================================================ 第 23 战：荷鲁斯神（街道 → 下水道）
  // 荷鲁斯神两段共用一份战斗配置：剧情（birdFight）和试炼（下面的 run）都从这里取，不复制。
  //   trial 时 lead / swap / allies / bench / vs 由试炼的 wrap 覆盖；伊奇的反咬格挡只在伊奇当队长时给，
  //   其他角色当队长也能靠 L.clash 反咬（那是战斗里写死的，不依赖伊奇）。
  function petshopSpec(S, first, hp, o, seg) {
    const lead = G.world && G.world.player ? G.world.player.cid : null;
    return { id: first ? 'b23a_petshop' : 'b23b_petshop', lead: o.trial ? undefined : 'iggy',
      swap: false, vs: first ? 'horus' : null,
      arena: first ? [300, 700] : [20, 610], bench: 'hide', finish: 'none', music: 'battle_egypt', par: 90,
      kitOverride: !o.trial || lead === 'iggy' ? { iggy: { parryWin: 8 / 60 } } : {},
      waves: [[{ cid: 'petshop', kit: 'e_petshop', hp, boss: true, x: first ? 590 : 430, y: 160 }]],
      testHint: c => ({ phase: first ? 1 : 2, bossHp: c.data.bossHp, perch: c.boss && c.boss.mem && c.boss.mem.perch,
        // frozen 给的是冻掉平台的左端 x（测试器按 x 判断“这块站不得”），不是下标
        frozen: c.data.frozen ? c.data.frozen.slice() : [], warningX: c.data.warningX,
        walls: c.data.walls ? c.data.walls.length : 0 }),
      onWave(s, n, es, attempt, c) {
        W.stage.props = W.stage.props.filter(p => !String(p.id || '').startsWith('late_'));
        W.stage.obstacles = W.stage.obstacles.filter(o => !o.lateIce);
        s.mark(first ? 'ch10_bird_street' : 'ch10_bird_sewer');
        c.data.bites = 0; c.data.walls = []; c.data.frozen = []; c.data.freezeT = 0; c.data.warningX = null;
        // 重试当前段时平台要复原：背景按 state('frost') 换贴图，不写回 0 会带着上一把冻裂的水面重开
        if (!first) s.state('frost', 0);
        s.insertUI(g => L.hud(g, [first ? '荷鲁斯神 · 街道' : '荷鲁斯神 · 下水道', '俯冲咬来的瞬间按 L，再连按 J 反咬；高处打不到',
          first ? null : '白霜出现一秒后平台冻结；水面会冻住脚步']));
        c.on('birdBite', ({ e }) => L.task(c, async () => {
          e.mem.locked = true;
          const win = await L.clash(s, { label: '咬住不放！（连按 J）', time: 4, a: 'fool', b: 'horus' });
          if (win) { e.hp = Math.max(1, e.hp - 300); c.data.bites++; s.sfx('punch_heavy'); G.dbg.ev('petshop_bite', { hp: e.hp }); }
          else L.damage(c, 18);
          e.mem.locked = false; e.cool = .8; e.mem.perch = false;
          c.data.bossHp = e.hp;
          if (e.hp <= 1 || first && e.hp <= 750) { seg.remaining = e.hp <= 1 ? 0 : e.hp; c.end(); }
        }));
        c.on('iceWall', () => {
          if (c.data.walls.filter(a => !a.dead && !a.remove).length >= 2) return;
          const x = G.clamp(c.player.x + 45, c.spec.arena[0] + 25, c.spec.arena[1] - 25);
          const wall = c.spawn({ cid: 'prop:ice_wall', id: 'ice_' + c.t, team: 'object', x, y: 160, hp: 2, bodyW: 12,
            dmgMul: (t, a, m) => m.dmg ? 1 / m.dmg : 0, onHitBy(t, a, m, info) { return ['J1', 'J2', 'J3', 'rush'].includes(info.slot) ? null : 'evade'; } });
          wall.breakable = { anim: 'broken', onBreak() { s.sfx('ice'); const i = W.stage.obstacles.indexOf(wall.mem.ob); if (i >= 0) W.stage.obstacles.splice(i, 1); } };
          wall.mem.ob = { x0: x - 10, x1: x + 10, y0: 147, y1: 174, lateIce: true }; W.stage.obstacles.push(wall.mem.ob); c.data.walls.push(wall);
        });
        if (!first) {
          // 白霜条对齐平台：平台从 @platforms 读（x0、y、x1）；c.data.frozen 存冻掉平台的 x0，
          //   数量写进背景 state('frost')（0–3，背景按这个值换冻裂的水面 / 平台贴图）
          const plats = SW('platforms');
          const platAt = x => plats.find(p => p[0] === x);
          L.pixel(P => {
            for (const x of c.data.frozen) {
              const pl = platAt(x); if (!pl) continue;
              G.px.rect(P, pl[0] - G.cam.x, pl[1] - 3, pl[2] - pl[0], 3, '#c9f1ff');
            }
            if (c.data.warningX != null) G.px.rect(P, c.data.warningX - G.cam.x, 151, 45, 3, Math.floor(G.clk.ui * 12) % 2 ? '#8bcbdf' : '#edf9ff');
          });
        }
      },
      tick(c, dt) {
        if (!c.boss) return;
        // 每帧把 Boss 血量写进 c.data.bossHp：HUD 和自动测试都读这一份（段 2 也要有）
        c.data.bossHp = c.boss.hp;
        // 段 1 的血线：反咬之外，普通攻击 / 大招也掉血；磨到 750 就进过场
        if (first) {
          if (!c.data.segDone && c.boss.hp <= 750) { c.data.segDone = true; seg.remaining = Math.max(1, c.boss.hp); c.end(); }
          return;
        }
        c.data.freezeT += dt;
        // 平台定时冻掉一块：1 s 前白霜闪烁预警；放水时 14 s 一块（脚本 10-12「放水」），最多 3 块
        const every = c.assist ? 14 : 10;
        if (c.data.freezeT >= every - 1 && c.data.warningX == null) {
          const pl = SW('platforms').find(p => c.data.frozen.indexOf(p[0]) < 0);
          if (pl) c.data.warningX = pl[0] + 10;
        }
        if (c.data.freezeT >= every) {
          c.data.freezeT %= every;
          if (c.data.warningX != null) {
            const pl = SW('platforms').find(p => p[0] + 10 === c.data.warningX);
            if (pl && c.data.frozen.length < 3) { c.data.frozen.push(pl[0]); S.state('frost', c.data.frozen.length); }
          }
          c.data.warningX = null; S.sfx('ice');
        }
        const plats = SW('platforms');
        const onFrozen = c.data.frozen.some(x => { const pl = plats.find(p => p[0] === x); return pl && c.player.x >= pl[0] && c.player.x <= pl[2]; });
        const water = c.player.y >= SW('water_y') || onFrozen;
        // 水面 / 冻平台上站久了脚被冻住：每 2.2 s 最多一次
        if (water && c.t >= (c.data.rootNext || 0)) { c.player.rootT = 1; c.data.rootNext = c.t + 2.2; }
      }, after(s) { s.insertUI(null); },
    };
  }
  async function birdFight(S, stage, hp, first, o = { trial: false, wrap: s => s }) {
    await S.setStage(stage, { x: first ? 380 : SW('arrive')[0] + 20, y: first ? 160 : footY('sewer_ch10', SW('arrive')[1]) });
    const seg = { remaining: 0 };
    await S.fight(o.wrap(petshopSpec(S, first, hp, o, seg)));
    F()[first ? 'ch10PetshopStreet' : 'ch10PetshopSewer'] = true;   // 章末自检：两段各打完一次
    return seg.remaining;
  }
  // 星尘试炼：街道 1500 → 磨到 750 切下水道（剩余血继承）。剧情里两段之间的下水道过场（钻栅栏 / 提示）
  //   不带进试炼，只保留换图和战斗；每次进关先把霜冻复位，免得上一轮冻掉的平台留到下一轮。
  const PetShopSrc = {
    chapter: 'ch10', pack: '_ch10',
    setup: async S => {
      await M.ensureBg('_ch10');
      S.state('frost', 0);
    },
    run: async (S, o) => {
      await PetShopSrc.setup(S);
      const remain = await birdFight(S, 'cairo_day_ch10', 1500, true, o);
      // 剧情里钻排水口的过场（走过去 / 淡出 / 提示）保留；试炼只换图，不带过场
      if (!o.trial) await sewerEnter(S);
      await birdFight(S, 'sewer_ch10', remain > 0 ? remain : 750, false, o);
    },
  };

  // ================================================================ 10-01 篇章卡与航线（过场）
  async function opening(S) {
    await S.chapterCard('ch10');
    S.party(crew, { leader: 'polnareff' });
    await S.setStage('map_ch10', { x: 100, y: 160, music: 'travel' });
    await S.route(['卢克索', '开罗郊外'], { vehicle: 'car', day: 36, left: 15,
      history: ['东京', '香港', '新加坡', '加尔各答', '瓦拉纳西', '卡拉奇', '阿拉伯沙漠', '红海', '卢克索'] });
  }

  // ================================================================ 10-02 郊外的咖啡馆（过场）
  async function cafeArrive(S) {
    const st = G.STAGES.cafe_ch10;
    st.props = []; st.npcs = []; st.hotspots = []; st.triggers = []; st.onLook = null;
    const door = CA('door'), seat = CA('seat_right');
    S.party(crew, { leader: 'polnareff' });
    await S.setStage('cafe_ch10', { x: door[0] + 60, y: footY('cafe_ch10', door[1]), music: 'tension' });
    amb(S, 'fan_loop', 'wind_loop', .08);
    S.state('bar', 1);   // 老板站在吧台后：吧台前沿画到人前面
    for (const [cid, dx] of [['polnareff', 60], ['joseph', 40], ['jotaro', 20], ['avdol', 80], ['iggy', 94]])
      place(S, cid, door[0] + dx, footY('cafe_ch10', door[1]), 1);
    // 达比坐在右侧椅子上朝左（他的 sit 帧自带一截小桌面，朝左才和主牌桌连上）
    const darby = S.spawn('darby', seat[0], footY('cafe_ch10', seat[1]), { id: 'darby', name: '丹尼尔·J·达比', team: 'npc', facing: -1 });
    if (darby) S.pose(darby, 'sit', { freeze: 0 });
    // 发牌小哥站在牌桌后面（y 127）：前景牌桌按 fgDepth 148 盖住他下半身，只露头和肩
    S.spawn('npc_dealer', CA('dealer')[0], CA('dealer')[1], { id: 'dealer', name: '发牌小哥', team: 'npc', facing: 1 });
    S.spawn('npc_cat', CA('cat')[0], CA('cat')[1], { id: 'bet_cat', name: '猫', team: 'npc', facing: 1 });
    S.spawn('npc_townsfolk', CA('bar')[0], CA('bar')[1], { id: 'boss', name: '老板', team: 'npc', facing: -1 });
    // 桌上的筹码 / 牌：depth ≥ 149，不然会被前景牌桌（地图 fgDepth 148）整个盖住
    const chipsAt = CA('chips');
    for (let i = 0; i < 3; i++) S.prop({ type: 'sprite', sprite: 'chip', x: chipsAt[0] + i - 1, y: chipsAt[1] + 8 - i, frame: i % 2, depth: 149 });
    S.prop({ type: 'sprite', sprite: 'card', x: chipsAt[0] - 16, y: chipsAt[1] + 12, frame: 0, depth: 149 });
    S.prop({ type: 'sprite', sprite: 'card', x: chipsAt[0] + 22, y: chipsAt[1] + 13, frame: 0, depth: 149 });
    S.location('cairo_outskirts');
    await S.narrate('第三十六天，开罗郊外。听说这家咖啡馆里，有个人知道那栋馆在哪里。');
    // 名牌放左上（后面紧跟底部对话框，默认 y 264 会被对话框盖住）；先等地点卡收走，两张卡不叠在同一个角
    await S.until(() => !G.uifx.cards.some(k => k.kind === 'loc'));
    S.nameCard('darby', { y: 24 });
    await S.say('darby', '欢迎。我是丹尼尔·J·达比。……你们在找一栋房子，对吧？');
    S.mark('ch10_darby');
  }

  // 咖啡馆的自由走动（10-02 与 10-06 共用；after = 赌局之后）
  function setupCafe(S, after) {
    const st = G.STAGES.cafe_ch10;
    st.props = []; st.npcs = []; st.hotspots = []; st.triggers = [];
    const chips = CA('chips'), seat = CA('seat_right'), window = CA('window'), painting = CA('painting');
    const boss = S.actor('boss');
    const bossTalk = async s => s.say('npc_townsfolk', pick('c10boss', ['……要喝什么？', '那个人在这里坐了一个星期了。每天都在等人。']),
      { name: '老板', actor: boss });
    // 老板是第一段过场里 spawn 出来的，自由走动不再重建地图（不重新 setStage），
    //   所以搭话要直接挂在现有角色上；只写进 st.npcs 的话，得等下次换图才会生成带 talk 的 NPC
    if (boss) { boss.talk = bossTalk; boss.label = '老板'; boss.name = '老板'; }
    st.npcs = boss ? [T.npc('npc_townsfolk', 'boss', boss.x, boss.y, { facing: -1, label: '老板', name: '老板', talk: bossTalk })] : [];
    const H = (id, x, label, tags, use, look, y = 160) => ({ id, x, y, label, tags, r: 24, ry: 90, use, look });
    st.hotspots = [
      H('cafe_window', window[0], '窗户', [], async (S, h, p) => S.say(p.cid, '窗外是沙漠，再远一点，就是开罗。')),
      H('cafe_painting', painting[0], '墙上的画', ['life', 'detail'],
        async (S, h, p) => S.say(p.cid, T.by(p, {
          avdol: '……画的是天平和羽毛。奥西里斯的审判。', _: '一幅褪色的画：一架天平，一边放着心脏，一边放着羽毛。' })),
        async (S, h, p) => S.say(p.cid, '阿布德尔：画的是天平和羽毛。奥西里斯的审判。')),
      H('cafe_cat', CA('cat')[0], '猫的窝', [], async (S, h, p) => {
        if (p.cid === 'joseph') return S.say('joseph', '这猫看起来比我们都悠闲。');
        if (p.cid === 'iggy') return S.say(null, '（伊奇和猫对视了三秒，各自转开了头。）');
        return S.say(p.cid, '一只花猫蜷在篮子里。');
      }),
      after ? H('cafe_darby', seat[0] - 30, '达比', [], async (S, h, p) => S.say('darby', '……啊……啊……'))
        : H('cafe_darby', seat[0] - 30, '坐下（达比）', ['life'], async S => { F().ch10Bet = true; },
          async S => S.say('avdol', '……他身边的筹码，每一枚都有一点点生命的气息。')),
    ];
    if (!after) {
      st.hotspots.push(H('cafe_dealer', CA('dealer_talk')[0], '发牌小哥', [], async (S, h, p) => {
        if (p.cid === 'iggy') { await S.say(null, '（小哥往后缩了一下。）'); return S.say('npc_dealer', '……狗不能上桌。'); }
        return S.say('npc_dealer', pick('c10dealer', ['……请坐。', '……']));
      }));
      st.hotspots.push(H('cafe_chips', chips[0], '桌上的筹码', ['nensha', 'detail'],
        async S => S.say(null, '桌上摞着一叠筹码，每一枚都磨得发亮。'),
        async S => { await S.say('joseph', '……照片里的筹码上，隐约有人脸？'); }));
    } else {
      // 赌局之后：发牌小哥已经跑了
      const dl = S.actor('dealer'); if (dl) dl.remove = true;
      // 赌局之后：筹码变成纪念品点（要会念写的人 U 才看得见）
      st.hotspots.push(X.hot('ch10_empty_chip', chips[0], footY('cafe_ch10', 160), { look: ['nensha'],
        found: async S => S.say('joseph', '……照片里，这枚筹码已经空了。') }));
      st.hotspots.push(H('cafe_door', CA('door')[0], '门（去开罗）', null,
        async S => { F().ch10Cairo = true; }));
    }
    st.onLook = async (S, p) => S.say(p.cid, T.by(p, {
      iggy: '（伊奇嗅了嗅，皱起鼻子：烟草和咖啡的味道。）', _: '……很安静。' }));
  }

  async function cafeExplore(S, after) {
    setupCafe(S, after);
    // setupCafe 改的是地图定义（G.STAGES），而活地图是 setStage 时拷贝出来的：把调查点搬到活地图上，
    // 不然自由走动时一个 E 点也没有（坐不到达比对面 = 卡死）
    if (W.stage && W.stage.id === 'cafe_ch10') {
      const def = G.STAGES.cafe_ch10;
      W.stage.hotspots = (def.hotspots || []).map(h => Object.assign({}, h));
      W.stage.onLook = def.onLook;
    }
    if (!after) {
      place(S, 'polnareff', CA('door')[0] + 60, footY('cafe_ch10', CA('door')[1]), 1);
      place(S, 'jotaro', CA('door')[0] + 20, footY('cafe_ch10', CA('door')[1]), 1);
      place(S, 'joseph', CA('door')[0] + 40, footY('cafe_ch10', CA('door')[1]), 1);
      place(S, 'avdol', CA('door')[0] + 80, footY('cafe_ch10', CA('door')[1]), 1);
      place(S, 'iggy', CA('door')[0] + 94, footY('cafe_ch10', CA('door')[1]), 1);
      T.memberTalk({
        joseph: async s => s.say('joseph', pick('c10tj', ['赌徒……我年轻的时候也赌过几把。', '别被他牵着鼻子走。'])),
        avdol: async s => s.say('avdol', pick('c10ta', ['这个人身上……有替身的气息。', '小心他说的每一句话。'])),
        polnareff: async s => s.say('polnareff', pick('c10tp', ['赌就赌！我可没那么容易输！', '他知道馆在哪里，那就赢下来！'])),
        iggy: s => s.say(null, '（伊奇趴在门口，不肯进来。）'),
        jotaro: async s => s.say('jotaro', pick('c10tt', ['……', '……他在笑。'])),
      });
      S.free(true);
      S.hint('咖啡馆：E 调查、搭话；准备好了就坐到达比对面。', 8);
      T.goal(S, { x: CA('seat_right')[0] - 30, y: footY('cafe_ch10', CA('seat_right')[1]) - 44, label: '达比', delay: 40, every: 25,
        done: () => !!F().ch10Bet, text: '那个赌徒在等你们坐下。' });
      await S.until(() => !!F().ch10Bet && !S.busy);
    } else {
      place(S, 'jotaro', CA('door')[0] + 40, footY('cafe_ch10', CA('door')[1]), 1);
      place(S, 'joseph', CA('door')[0] + 20, footY('cafe_ch10', CA('door')[1]), 1);
      place(S, 'avdol', CA('door')[0] + 60, footY('cafe_ch10', CA('door')[1]), 1);
      place(S, 'polnareff', CA('door')[0] + 80, footY('cafe_ch10', CA('door')[1]), 1);
      place(S, 'iggy', CA('door')[0] + 96, footY('cafe_ch10', CA('door')[1]), 1);
      T.memberTalk({});
      S.free(true);
      S.hint('出门去开罗。', 6);
      T.goal(S, { x: CA('door')[0], y: footY('cafe_ch10', CA('door')[1]) - 44, label: '门', delay: 20, every: 20,
        done: () => !!F().ch10Cairo, text: '出门去开罗。' });
      await S.until(() => !!F().ch10Cairo && !S.busy);
    }
    S.free(false);
  }

  // ================================================================ 10-03 回合 1：猫先吃哪块肉（必输）
  async function catBet(S) {
    S.mark('ch10_cat_bet');
    const seat = CA('seat_left'), meat = CA('meat');
    let eaten = -1;   // 被吃掉的那块肉：画的时候跳过它
    const pol = sit(S, 'polnareff', seat[0], seat[1], 1);
    for (const [cid, dx] of [['joseph', -20], ['jotaro', 0], ['avdol', 18], ['iggy', 36]])
      place(S, cid, seat[0] + dx, footY('cafe_ch10', 168), 1);
    // 三块肉（剧情画的小肉块）；吃完就撤掉，不然一直到赌局结束都摆在桌上
    const meatPx = L.pixel(P => {
      for (let n = 0; n < meat.length; n++) {
        if (n === eaten) continue;
        G.px.rect(P, meat[n][0] - G.cam.x, meat[n][1] - 4, 7, 4, '#bd795b');
      }
    });
    // 猫被老板抱到中间那块肉前面
    const cat = S.actor('bet_cat');
    if (cat) { cat.visible = true; cat.hold = false; cat.facing = -1; cat.x = meat[1][0] - 30; cat.y = footY('cafe_ch10', meat[1][1]); }
    await S.say('joseph', '你是九荣神的人吧。');
    await S.say('darby', '我只是个赌徒。想知道那栋房子在哪里——就跟我赌一把。赌注嘛……灵魂。');
    await S.say('polnareff', '灵魂？哈，有意思！那就赌——那只猫，先吃哪块肉！');
    await S.say('darby', '好啊。你先选。');
    const i = await S.choice(['左边的肉', '中间的肉', '右边的肉'], '猫会先吃哪块？');
    // 猫绕过他选的那块，吃了另一块
    const other = (i + 1) % 3;
    eaten = other;
    if (cat) {
      await S.walk(cat, meat[other][0], footY('cafe_ch10', meat[other][1]), { speed: 42, anim: 'walk' });
      cat.play('eat', { restart: true });
    }
    snd('cat_meow', null, { vol: .4 });   // cat_meow 已在音效包里，不需要备胎名
    S.mark('ch10_cat');
    await S.wait(.8);
    if (cat) cat.remove = true;
    if (meatPx) meatPx.remove = true;   // 肉收走：后面两回合桌上不该还摆着肉
    await S.say('darby', '你的选择，我早就知道了。');
    await S.say('polnareff', '这、这不可能——');
    await soul(S, 'polnareff', 0);
    S.mark('ch10_soul_pol');
    // 波鲁纳雷夫伏在桌上不动：队伍条里他的头像灰掉（筹码图标用灰头像代替，交付记录里写明）
    if (pol) S.pose(pol, 'down', { freeze: 0 });
    S.leave('polnareff', { look: 'gray' });
    await S.say('avdol', '波鲁纳雷夫！');
    await S.say('darby', '下一位？');
  }

  // ================================================================ 10-04 回合 2：揭穿出千（必输）
  async function cheatBet(S) {
    S.mark('ch10_joseph_cheat');
    S.setLeader('joseph', { force: true });
    sit(S, 'joseph', CA('seat_left')[0], CA('seat_left')[1], 1);
    await S.say('joseph', '……你出千了。这一把，我一定会揭穿你。');
    await S.say('darby', '请便。被识破的出千才叫出千。');
    // 达比洗牌、发牌小哥发牌：两人的手各动 2 s
    const dealer = S.actor('dealer'), darby = S.actor('darby');
    await S.animate(2, k => {
      if (dealer) dealer.x = CA('dealer')[0] + Math.sin(k * 22) * 6;
      if (darby) darby.frame = Math.floor(k * 12) % 2;
    });
    if (dealer) dealer.x = CA('dealer')[0];
    const i = await S.choice(['发牌小哥', '袖口藏牌', '洗牌手法'], '揭穿一次出千');
    F().darbyCheatFound = i === 0;
    if (i === 0) {
      await S.say('joseph', '是你！发牌的那个小鬼！');
      if (dealer) act(dealer, 'shock', 700);
      await S.say('darby', '……猜对了一半。');
    } else if (i === 1) {
      await S.say(null, '（达比抖了抖袖子：什么都没有。）');
      await S.say('darby', '袖口？请看。');
    } else {
      await S.say('darby', '我洗牌的时候，你一直盯着。……看到什么了吗？');
    }
    await S.say('darby', '可惜——我在你看不到的地方，又出了一次千。');
    await S.say('joseph', 'OH MY GOD……承太郎……这家伙……！');
    await soul(S, 'joseph', 1);
    S.mark('ch10_soul_jo');
    S.leave('joseph', { look: 'gray' });
  }

  // ================================================================ 10-05 / 10-06 扑克与开牌
  async function pokerScene(S) {
    S.mark('ch10_poker');
    S.setLeader('jotaro', { force: true });
    // 脚本 10-05 的顺序：先把“我来 / 赌什么 / 两个灵魂”说完，再放神名卡和 VS 卡
    await S.say('jotaro', '……我来。');
    await S.say('darby', '你？好啊。这次赌什么？');
    await S.say('jotaro', '两个灵魂。……再加上我的。');
    await S.title('god_osiris');
    // 直接放的 VS 卡退场时会自动挂左上角小标签（S.fight 结束时才摘）；赌局有自己的顶栏，放完就摘掉
    await S.vs({ key: 'osiris', hero: 'jotaro', enemy: { cid: 'darby', anim: 'sit', scale: 2 } }); G.uifx.vsTag(null);
    await poker(S);
    await S.say('jotaro', '开牌啊。你不是赌上了一切吗？');
    await S.say('darby', '啊……啊……', { expr: 'sweat' });
    await pokerReveal(S);
    S.mark('ch10_reveal');
    // 灵魂回来：队伍恢复
    S.party(crew, { leader: 'jotaro' });
    await S.say('joseph', '……承太郎！你的牌……一对都没有啊！');
    await S.say('jotaro', '……他输给了他自己。');
    await S.say('polnareff', 'Mon dieu……我还以为要在筹码里过一辈子了。');
    await S.say('avdol', '那么——房子在哪里？');
    await S.narrate('达比抱着空筹码，不回答。');
    await S.say('joseph', '……看来，只能自己去找了。');
    const darby = S.actor('darby');
    if (darby) S.pose(darby, 'sit', { freeze: 0 });
  }

  // ================================================================ 10-07 开罗（航线 → 自由走动）
  async function cairoIntro(S) {
    // 注意：setStage 的 fade:false 会连「淡入」一起跳过。前面已经 fadeOut 到全黑时再写 fade:false，
    //   画面就永远是黑的（对白、卡片都罩在黑幕下面，玩家只看得到黑屏）。所以这里交给 setStage 自己淡入。
    await S.fadeOut(.4);
    await S.setStage('map_ch10', { x: 100, y: 160, music: 'travel' });
    await S.route(['开罗郊外', '开罗'], { vehicle: 'car', day: 40, left: 11,
      history: ['东京', '香港', '新加坡', '加尔各答', '瓦拉纳西', '卡拉奇', '阿拉伯沙漠', '红海', '卢克索'] });
    const ar = CD('arrive');
    S.party(crew, { leader: 'jotaro' });
    await S.setStage('cairo_day_ch10', { x: ar[0] + 20, y: footY('cairo_day_ch10', ar[1]), music: 'daily' });
    amb(S, 'bazaar_loop', null, .18);
    for (const [cid, dx] of [['jotaro', 20], ['joseph', 40], ['avdol', 60], ['polnareff', 80], ['iggy', 4]])
      place(S, cid, ar[0] + dx, footY('cairo_day_ch10', ar[1]), 1);
    // 镜子摊和油桶是街景的一部分（第 22 战用同一套位置）
    T.prop(S, 'mirror_stand', CD('mirror_stand')[0], footY('cairo_day_ch10', CD('mirror_stand')[1]), { id: 'street_mirror' });
    T.prop(S, 'oil_drum', CD('oil_drum')[0], footY('cairo_day_ch10', CD('oil_drum')[1]), { id: 'street_drum' });
    S.location('cairo');
    await S.narrate('第四十天。开罗。拿着照片问遍了整条街，没有一个人认得那栋房子。');
    await S.say('joseph', '……念写只拍得到一角。这样下去，荷莉她——');
    await S.say('avdol', '乔斯达先生，别急。线索一定就在附近。');
    S.mark('ch10_cairo_search');
  }

  function setupCairo(S) {
    const st = G.STAGES.cairo_day_ch10;
    st.props = []; st.npcs = []; st.hotspots = []; st.triggers = [];
    const H = (id, x, label, tags, use, look, y = 160) => ({ id, x, y, label, tags, r: 24, ry: 90, use, look });
    const gy = y => footY('cairo_day_ch10', y);
    st.npcs = [
      T.npc('npc_dealer', 'bakery', CD('bakery')[0], gy(CD('bakery')[1]), { facing: -1, label: '卖烤饼的', name: '卖烤饼的',
        talk: async s => s.say('npc_dealer', pick('c10bakery', ['这个屋顶？没见过。来块烤饼吗？', '刚出炉的！']), { name: '卖烤饼的' }) }),
      T.npc('npc_townsfolk', 'asker', CD('asker')[0], gy(CD('asker')[1]), { facing: -1, label: '问路的人', name: '问路的人',
        talk: async s => s.say('npc_townsfolk', pick('c10asker', ['你们也在找这栋房子？……我找了三天了，没人认得。', '奇怪，明明有人说就在开罗。']), { name: '问路的人' }) }),
      T.npc('npc_townsfolk', 'hotel', CD('hotel')[0], gy(CD('hotel')[1]), { facing: -1, label: '旅馆老板', name: '旅馆老板',
        talk: async s => s.say('npc_townsfolk', pick('c10hotel', ['这栋房子？没见过。', '你们住几晚？房间还有。']), { name: '旅馆老板' }) }),
      T.npc('npc_kid', 'kids', CD('kids')[0], gy(CD('kids')[1]), { facing: -1, label: '小孩们', name: '小孩',
        talk: async s => s.say('npc_kid', pick('c10kids', ['外国人！有口香糖吗？', '那只狗是你们的？']), { name: '小孩' }) }),
    ];
    st.hotspots = [
      // 三条线索：屋檐（鸟）、路牌（照片）、转角楼（气味）
      H('clue_bird', CD('hotel')[0] + 22, '旅馆的屋檐', ['life'], async S => S.say(null, '屋檐上停着一只鸟。'),
        async S => { F().mansionBird = true; await S.say('avdol', '这条街上……有一只鸟一直在盯着我们。不是普通的鸟。'); }, gy(CD('hotel_roof')[1])),
      // 路牌兼任推理入口：三条线索齐了、地图还没圈对时按 E 重新摊开地图（脚本 10-07 的补救入口）
      H('clue_photo', CD('road_sign')[0], '路牌', ['nensha'], async S => {
        if (F().mansionPhoto && F().mansionBird && F().mansionScent && !F().ch10North) { F().ch10QuizGo = true; return; }
        await S.say(null, '路牌上写着阿拉伯文和英文。');
      }, async S => { F().mansionPhoto = true; await S.say('joseph', '……屋顶的一角。尖顶，铁栏杆。这条线索还不够。'); }),
      H('clue_scent', CD('corner')[0], '转角楼', ['scent'], async S => S.say(null, '一栋转角的老楼。'),
        async S => { F().mansionScent = true; await S.say(null, '（气味线从伊奇鼻尖一直延伸到画面右上——城北。）'); await S.narrate('气味一直延伸到城北。'); }),
      H('cairo_mirror', CD('mirror_stand')[0], '镜子摊', [], async S => S.say(null, '卖镜子的摊子，镜子立在木架上，可以转。')),
      H('cairo_fruit', CD('fruit_stand')[0], '水果摊', [], async S => S.say(null, '西瓜、石榴、无花果。')),
      H('cairo_drum', CD('oil_drum')[0], '油桶', [], async S => S.say(null, '路边一只油桶，桶底在漏油。')),
      H('cairo_cross', CD('crossroad')[0], '路口', [], async S => S.say(null, '四条路在这里交汇。')),
      H('cairo_alley', CD('alley')[0], '窄巷', [], async S => S.say(null, '窄巷里晾着衣服。')),
      // 排水口是伏笔（不设旗标）
      H('cairo_grate', CD('sewer_grate')[0], '排水口栅栏', ['scent'], async S => S.say(null, '路边的排水口，铁栅栏锈住了。'),
        async S => { await S.say(null, '（伊奇对着栅栏嗅了嗅，背上的毛竖了起来。）'); await S.narrate('下水道里有奇怪的味道。'); }),
      H('cairo_exit', CD('exit')[0], '往城北', null,
        async S => { F().ch10North = true; }),
    ];
    st.onLook = async (S, p) => S.say(p.cid, T.by(p, {
      iggy: '（伊奇抬头嗅了嗅：香料、尘土……还有一点点，鸟的味道。）', _: '……人太多了。' }));
  }

  // 找馆推理：三题选项顺序随机，全对才圈城北；答错红圈画到别处，可以回来看
  async function mapQuiz(S) {
    const st = { circle: null, cardLit: 0 };
    const ins = T.show(S, { bg: 'cairo_map', draw(g) {
      const names = [['north', '城北'], ['south', '城南'], ['old_town', '老城'], ['west_bank', '西岸']];
      for (const [k, label] of names) { const p = CM(k); M.text(g, label, p[0] - 8, p[1] - 5, '#3b2a1e'); }
      // 右边三张线索卡（照片 / 羽毛 / 鼻子），在纸外的桌面上
      const cards = CM('cards');
      ['照片', '羽毛', '鼻子'].forEach((t, i) => {
        g.fillStyle = i < st.cardLit ? '#f3e6c4' : '#cbb891'; g.fillRect(cards[i][0] - 18, cards[i][1] - 16, 36, 32);
        g.strokeStyle = '#6b543a'; g.lineWidth = 1; g.strokeRect(cards[i][0] - 18, cards[i][1] - 16, 36, 32);
        M.text(g, t, cards[i][0] - 12, cards[i][1] - 6, '#3b2a1e');
      });
      if (st.circle) {
        const p = CM(st.circle);
        g.strokeStyle = '#d8343e'; g.lineWidth = 2;
        g.beginPath(); g.ellipse(p[0], p[1], 26, 16, 0, 0, Math.PI * 2); g.stroke();
      }
    } });
    try {
      await S.say('joseph', '三条线索都有了。……来，摊开地图。');
      st.cardLit = 3;
      const qs = [
        { id: 'roof', q: '照片里的屋顶是什么样的？', opts: ['尖顶', '平顶', '圆顶'], right: 0 },
        { id: 'bird', q: '那只鸟是从哪边飞来的？', opts: ['北边', '南边', '河边'], right: 0 },
        { id: 'scent', q: '伊奇闻到的气味指向哪里？', opts: ['城北', '城南', '西岸'], right: 0 },
      ];
      let all = true;
      for (const q of qs) {
        const order = [0, 1, 2].sort(() => Math.random() - .5);
        const i = await S.choice(order.map(n => q.opts[n]), q.q);
        const answer = order[i];
        G.dbg.ev('quiz', { id: q.id, answer });
        if (answer !== q.right) all = false;
      }
      S.mark('ch10_map_quiz');
      if (all) {
        st.circle = 'north';
        await S.say('joseph', '城北！……就在这一带！');
        await X.give(S, 'ch10_circled_map');
        return true;
      }
      // 答错：红圈画到别处，之后可以回来看
      st.circle = ['south', 'west_bank', 'old_town'][Math.floor(Math.random() * 3)];
      await S.say('joseph', '……不对，再想想。');
      return false;
    } finally { ins.close(); }
  }

  async function cairoExplore(S) {
    setupCairo(S);
    const ar = CD('arrive');
    // NPC 是地图数据（st.npcs）里的：setupCairo 设完要重换一次地图才会生成带 talk 的 NPC（同第 8 章海岸）
    await S.setStage('cairo_day_ch10', { x: ar[0] + 20, y: footY('cairo_day_ch10', ar[1]), music: 'daily' });
    // 镜子摊、油桶是街景的一部分（第 22 战用同一套位置；换图后要重新摆，不然街上就空了）
    T.prop(S, 'mirror_stand', CD('mirror_stand')[0], footY('cairo_day_ch10', CD('mirror_stand')[1]), { id: 'street_mirror' });
    T.prop(S, 'oil_drum', CD('oil_drum')[0], footY('cairo_day_ch10', CD('oil_drum')[1]), { id: 'street_drum' });
    place(S, 'jotaro', ar[0] + 20, footY('cairo_day_ch10', ar[1]), 1);
    place(S, 'joseph', ar[0] + 40, footY('cairo_day_ch10', ar[1]), 1);
    place(S, 'avdol', ar[0] + 60, footY('cairo_day_ch10', ar[1]), 1);
    place(S, 'polnareff', ar[0] + 80, footY('cairo_day_ch10', ar[1]), 1);
    place(S, 'iggy', ar[0] + 4, footY('cairo_day_ch10', ar[1]), 1);
    T.memberTalk({});
    S.free(true);
    S.hint('开罗：换队长用替身找线索（照片、鸟、气味）。', 10);
    // 目标箭头：还没拿全三条线索时指向第一个没拿的，拿全后指 @exit
    let goal = null;
    const clueSpots = [['mansionPhoto', 'road_sign'], ['mansionBird', 'hotel'], ['mansionScent', 'corner']];
    const aim = () => {
      if (goal) goal.stop();
      const miss = clueSpots.find(([flag]) => !F()[flag]);
      const k = miss ? miss[1] : 'exit';
      goal = T.goal(S, { x: CD(k)[0], y: footY('cairo_day_ch10', CD(k)[1]) - 44,
        label: miss ? '线索' : '往城北', delay: 60, every: 30, done: () => !!F().ch10North,
        text: miss ? '还没找齐：照片、鸟、气味。' : '去城北。' });
    };
    aim();
    try {
      while (!F().ch10North) {
        // 三条线索齐了自动摊开地图；答错之后不再自动弹，要回 @road_sign 按 E 才会重开（脚本 10-07）
        const all = () => !!(F().mansionPhoto && F().mansionBird && F().mansionScent);
        await S.until(() => F().ch10North || (!S.busy && (F().ch10QuizGo || (!F().ch10QuizDone && all()))));
        if (F().ch10North) break;
        F().ch10QuizGo = false; F().ch10QuizDone = true;
        S.free(false);
        await mapQuiz(S);
        S.free(true);
        aim();
      }
    } finally { if (goal) goal.stop(); S.free(false); }
  }

  // ================================================================ 10-08 屋顶上的两个人 → 回忆
  async function rooftop(S) {
    const roof = CD('rooftop');
    S.camera(roof[0] - 300);   // 镜头移到屋顶那一带
    const hh = S.spawn('holhorse', roof[0] - 22, roof[1], { id: 'hol_roof', team: 'npc', hold: true, facing: 1 });
    const bo = S.spawn('boingo', roof[0] + 8, roof[1], { id: 'boingo_roof', team: 'npc', hold: true, facing: -1 });
    if (hh) S.pose(hh, 'down', { freeze: 0 });
    if (bo) S.pose(bo, 'scared', { freeze: 0 });   // boingo 没有 down / run，只有 idle / scared / portrait
    await S.say('joseph', '分头找。我和承太郎、阿布德尔去城南问问。波鲁纳雷夫、伊奇——你们去城北看看。');
    await S.say('polnareff', '又让我和这只狗一组？！');
    await S.say(null, '（伊奇打了个哈欠。）');
    S.mark('ch10_rooftop');
    await S.say('holhorse', '……喂，小鬼。你哥哥的仇，你想报吧？');
    await S.say('boingo', '我、我只是……漫画上画的，一定会应验……');
    await S.say('holhorse', '那就好。这次有你的预言，加上我的皇帝……');
    await S.say('holhorse', '……我可不想再站到那个人背后了。');
  }

  async function flashback(S) {
    await S.fadeOut(.4);
    // mansion_hall 的图在第 11 章的背景包里（packs.json）：从选章直接进第 10 章时页面里只有 bg_ch10，
    //   不先补载，回忆整段会是一片黑（章末 10-14 的馆外远景同理）
    await G.res.loadPack('bg_ch11');
    await S.setStage('flashback_ch10', { x: MH('stairs_up')[0] - 100, y: 160, music: 'ominous' });
    S.filter('sepia', 1);   // 回忆：全屏 sepia
    const seat = MH('dio_seat'), up = MH('stairs_up');
    const dio = S.spawn('dio', seat[0], seat[1], { id: 'dio_mem', team: 'npc', hold: true, facing: -1 });
    if (dio) S.pose(dio, 'sit_back', { freeze: 0 });
    const hh = S.spawn('holhorse', up[0] - 60, footY('flashback_ch10', up[1]), { id: 'hol_mem', team: 'npc', facing: 1 });
    if (hh) S.pose(hh, 'shoot', { freeze: 0 });
    await S.wait(.5);
    await S.say('holhorse', '……只要在背后开一枪……');
    S.nameCard('dio');
    await S.say('dio', '你的呼吸很平稳，荷尔·荷斯。……想开枪的话，就开吧。');
    S.sfx('gunshot');
    // 灰一帧：DIO 的座位空了，子弹嵌在台阶上，他站在荷尔·荷斯身后（不点破时停）
    // 只用 0.1 s 的灰度滤镜：冲击帧是黑白高反差闪，看起来像“被打中”，不像“时间停了一下”
    S.filter('gray', 1);
    await S.wait(.1);
    S.filter('gray', null);
    if (dio) {
      S.unpose(dio);
      if (hh) { dio.x = hh.x - 20; dio.y = hh.y; }
      dio.facing = 1; dio.play('idle', { restart: true });
    }
    // 子弹嵌在台阶上：位置从 @stairs_up 读（台阶的 y 就是站立线，往上 8 px 画在踏面上）
    L.pixel(P => G.px.rect(P, MH('stairs_up')[0] - 40 - G.cam.x, MH('stairs_up')[1] - 8, 3, 3, '#d8c088'));
    S.mark('ch10_gray_frame');
    await S.say('dio', '……再给你一次机会。要不要，站到我这边来？');
    if (hh) S.pose(hh, 'down', { freeze: 0 });
    await S.say('holhorse', '……是、是……DIO 大人。我发誓，永远效忠您。');
    await S.fadeOut(.4);
    S.filter('sepia', null);
    await S.setStage('cairo_day_ch10', { x: CD('crossroad')[0] - 120, y: footY('cairo_day_ch10', CD('crossroad')[1]), music: 'ominous' });
    await S.say('holhorse', '……那个人，比怪物还可怕。所以——我要先把你们收拾掉！');
  }

  async function prophecies(S) {
    S.party(['iggy', 'polnareff'], { leader: 'iggy' });
    // 开场站位：路口左边 280 px（三个预言的机关都在路口那一带，从这里出发才看得全）
    await S.setStage('cairo_day_ch10', { x: CD('crossroad')[0] - 280, y: 160 });
    const hh = holhorseSpec();
    for (let n = 0; n < 3; n++) await prophecy(S, n, hh);
    if (hh._obj) hh._obj.play('down');
  }

  // ================================================================ 10-10 当 No.2 果然最好
  async function holhorseRetire(S) {
    S.mark('ch10_holhorse_down');
    await S.say('holhorse', '……再低一厘米……');
    await S.say('holhorse', '……当 No.2……果然最好……');
    const bo = S.spawn('boingo', CD('rooftop')[0], CD('rooftop')[1], { id: 'boingo_peek', team: 'npc', hold: true, facing: -1 });
    await S.say('boingo', '预、预言怎么全落到我们身上了？！');
    S.sfx('dog_bark');
    if (bo) { bo.y = footY('cairo_day_ch10', 162); S.walk(bo, CD('exit')[0] + 80, footY('cairo_day_ch10', 162), { speed: 180, anim: 'scared' }).catch(G.cancelIgnore); }
    await S.wait(.8);
    if (bo) bo.remove = true;
    await S.narrate('波因哥抱着漫画跑了。');
    await S.say('polnareff', '……喂，荷尔·荷斯？……还活着吧？');
    await S.say('holhorse', '……我什么都没听见。我已经退休了。');
    await S.narrate('从那天起，荷尔·荷斯再也没有出现在他们面前。');
  }

  // ================================================================ 10-11 第 47 天：伊奇溜出去
  async function falconIntro(S) {
    S.party(['iggy'], { leader: 'iggy' });
    const hotel = CD('hotel'), sign = CD('road_sign');
    await S.setStage('cairo_day_ch10', { x: hotel[0] - 30, y: footY('cairo_day_ch10', hotel[1]), music: 'daily' });
    await S.narrate('第四十七天。一个星期过去了，还是没有找到那栋馆。');
    const ig = S.player;
    if (ig) {
      await S.walk(ig, sign[0] - 30, footY('cairo_day_ch10', sign[1]), { speed: 34, anim: 'walk' });
      ig.facing = 1;
    }
    // 路牌顶上停着一只隼（@road_sign_top = 路牌红圆顶）
    const pet = S.spawn('petshop', CD('road_sign_top')[0], CD('road_sign_top')[1], { id: 'petshop', team: 'npc', hold: true, facing: -1 });
    if (pet) S.pose(pet, 'perch', { freeze: 0 });
    snd('bird_screech', null, { vol: .4 });
    await S.wait(.5);
    // 伊奇抬头（没有专门的抬头动作，保持 idle 不硬套 hurt / shock）
    // 伊奇抬头，口香糖从嘴里掉出来（脚本 10-11 第 4 步）：落地后留在脚边，不进背包、不弹提示
    const gy = ig ? ig.y : footY('cairo_day_ch10', sign[1]);
    const gx = (ig ? ig.x : sign[0] - 30) + 8;
    const gum = S.spawn('prop:gum', gx, gy - 16, { id: 'c10_gum', team: 'object', untouchable: true, shadow: false });
    if (gum) { const y0 = gy - 16; await S.animate(.32, k => { gum.y = G.lerp(y0, gy, k); gum.x = gx + k * 5; }); }
    S.mark('ch10_falcon');
    await S.wait(.4);
    S.nameCard('petshop');
    await S.title('god_horus');
    await S.vs({ key: 'horus', hero: 'iggy', enemy: { cid: 'petshop', anim: 'perch', scale: 1.6 } });
    G.uifx.vsTag(null);
  }

  // 街道 → 下水道：伊奇被冰矛逼到排水口，钻进栅栏
  async function sewerEnter(S) {
    const ig = S.player;
    if (ig) {
      await S.walk(ig, CD('sewer_grate')[0], footY('cairo_day_ch10', CD('sewer_grate')[1]), { speed: 150, anim: 'run' });
      S.sfx('metal_scrape', .4);
      await S.animate(.4, k => { ig.y = footY('cairo_day_ch10', CD('sewer_grate')[1]) + k * 10; ig.alpha = 1 - k; });
    }
    await S.fadeOut(.35);
    await S.setStage('sewer_ch10', { x: SW('arrive')[0] + 20, y: footY('sewer_ch10', SW('arrive')[1]), music: 'battle_egypt' });
    S.state('frost', 0);
    S.hint('白霜出现一秒后平台冻结；水面会冻住脚步', 6);
  }

  // ================================================================ 10-13 伊奇记住了那栋馆
  async function iggyRemembers(S) {
    await S.title('saiki');
    await S.narrate('（佩特夏普掉进水里，再也没有飞起来）');    // 只画水面的一根羽毛（不画尸体）
    // 羽毛落在水面的缺口里（缺口 x 从 @gaps 读，不写死坐标）
    const gaps = SW('gaps') || [], gap = gaps[1] || gaps[0] || [300, 330];
    const fx = Math.round((gap[0] + gap[1]) / 2), wy = SW('water_y');
    L.pixel(P => { G.px.rect(P, fx - G.cam.x, wy - 2, 7, 2, '#f2f6ff'); G.px.rect(P, fx + 3 - G.cam.x, wy - 4, 3, 2, '#dfe8f5'); });
    S.mark('ch10_sewer_frost');
    const ladder = SW('ladder'), grate = SW('exit_grate');
    const ig = S.player;
    if (ig) {
      ig.x = ladder[0] - 40; ig.y = footY('sewer_ch10', SW('arrive')[1]);
      S.pose(ig, 'limp_walk', { freeze: 0 });
      await S.walk(ig, ladder[0], footY('sewer_ch10', ladder[1]), { speed: 26, anim: 'limp_walk' });
      // 沿梯子爬出去：@exit_grate 的 y 是 40（可走带外），只能当高度用 z 抬，不能改成站位
      await S.animate(1.2, k => { ig.z = (ladder[1] - grate[1]) * k; if (k > .85) ig.alpha = 1 - (k - .85) / .15; });
      ig.remove = true;
    }
    // 插入：暮色里的大宅剪影（第 11 章的远景，压暗）
    const h = T.show(S, { bg: 'mansion_exterior', letterbox: 16, draw(g) {
      g.fillStyle = 'rgba(12,10,22,.55)'; g.fillRect(0, 0, 640, 360);
    } });
    S.music('ominous');
    try { await S.wait(1.8); } finally { h.close(); S.letterbox(false); }
    S.mark('ch10_mansion_glimpse');
    await S.narrate('……尖顶。铁栏杆。');
    // 尼罗河边：一个孩子蹲下来给伊奇包前腿（白绷带像素）
    const b = T.show(S, { bg: 'cairo_day', letterbox: 16, parts: [
      { kind: 'sprite', cid: 'iggy', anim: 'down', x: 190, y: 168, scale: 2 },
      { kind: 'sprite', cid: 'npc_kid', anim: 'idle', x: 150, y: 166, scale: 2, flip: true }], draw(g) {
      g.fillStyle = '#eef2f8'; g.fillRect(200, 158, 10, 4);
    } });
    try {
      await S.wait(.6);
      await S.say('npc_kid', '……你受伤了？别怕，我帮你包好。', { name: '孩子' });
      await X.give(S, 'ch10_bandage');
      await S.narrate('伊奇记住了那栋馆的位置。');
    } finally { b.close(); S.letterbox(false); }
  }

  // ================================================================ 10-14 第 48 天：DIO 的馆
  async function mansion(S) {
    S.party(crew, { leader: 'iggy' });
    // 馆外背景在第 11 章的背景包里（packs.json），从选章直接进第 10 章时还没插进页面：先加载再换图（同第 1 章结尾预载第 2 章）
    await G.res.loadPack('bg_ch11');
    const arr = ME('arrive'), gate = ME('gate');
    await S.setStage('mansion_ext_ch11', { x: arr[0] + 30, y: footY('mansion_ext_ch11', arr[1]), music: 'ominous' });
    const ig = S.player;
    // 伊奇一瘸一拐走到铁门前（@gate）停下
    if (ig) { ig.x = arr[0]; ig.facing = 1; await S.walk(ig, gate[0] - 12, footY('mansion_ext_ch11', arr[1]), { speed: 26, anim: 'limp_walk' }); }
    for (const [cid, dx] of [['jotaro', 40], ['joseph', 20], ['avdol', 60], ['polnareff', 80]])
      place(S, cid, gate[0] - 12 - dx, footY('mansion_ext_ch11', arr[1]), 1);
    await S.narrate('第四十八天。伊奇带着众人，找到了 DIO 的馆。');
    await S.say('joseph', '……就是这里。念写里的屋顶。');
    await S.say('avdol', '伊奇……你是怎么找到的？');
    await S.say(null, '（伊奇别过头，嚼起了口香糖。）');
    await S.say('jotaro', '……明天。太阳最高的时候，进去。');
    S.mark('ch10_mansion');
    await M.end(S, 'ch10_complete');
  }

  // ================================================================ 本章入口
  G.STORY.ch10 = async S => {
    T.resetCounters();
    for (const k of ['ch10Bet', 'ch10Cairo', 'ch10North', 'ch10QuizDone', 'ch10QuizGo', 'mansionPhoto', 'mansionBird',
      'mansionScent', 'darbySweat', 'darbyCheatFound', 'ch10End', 'ch10Prophecy1', 'ch10Prophecy2', 'ch10Prophecy3',
      'ch10PetshopStreet', 'ch10PetshopSewer', 'ch10CatPick']) delete F()[k];
    await S.run(async s => {
      await opening(s);                                          // 10-01 篇章卡 + 航线
      await cafeArrive(s); });                                   // 10-02 咖啡馆
    await cafeExplore(S, false);
    await S.run(async s => { await catBet(s); await cheatBet(s); await pokerScene(s); });   // 10-03 ~ 10-06
    await cafeExplore(S, true);
    await S.run(async s => { await cairoIntro(s); });          // 10-07
    await cairoExplore(S);
    await S.run(async s => {
      await rooftop(s); await flashback(s); await prophecies(s);   // 10-08 ~ 10-10
      await holhorseRetire(s); await falconIntro(s);               // 10-11
      await birdFight(s, 'cairo_day_ch10', 1500, true);
      await sewerEnter(s);
      await birdFight(s, 'sewer_ch10', 750, false);                // 10-12
      await iggyRemembers(s); await mansion(s);                    // 10-13 ~ 10-14
    });
  };

  // ================================================================ 单战入口（开发调参 G.DEV / 标题「挑战」）
  G.DEV = G.DEV || {};
  G.DEV.ch10Prophecy = async S => {
    S.party(['iggy', 'polnareff'], { leader: 'iggy' });
    await S.setStage('cairo_day_ch10', { x: CD('crossroad')[0] - 280, y: 160, music: 'battle_egypt' });
    await S.run(async s => { await prophecies(s); });
  };
  G.DEV.ch10Horus = async S => {
    S.party(['iggy'], { leader: 'iggy' });
    await PetShopSrc.setup(S);
    await S.setStage('cairo_day_ch10', { x: CD('crossroad')[0] - 260, y: 160, music: 'battle_egypt' });
    await S.run(async s => { await PetShopSrc.run(s, { trial: false, wrap: q => q }); });
  };
  // 扑克不做挑战（选项赌局、不评价）
  X.challenge({ id: 'b22_prophecy1', chapter: 'ch10', title: 'VS 皇帝 + 托特神（伊奇 / 波鲁纳雷夫）', par: 90, run: S => G.DEV.ch10Prophecy(S) });
  X.challenge({ id: 'b23a_petshop', chapter: 'ch10', title: 'VS 荷鲁斯神（伊奇）', par: 90, run: S => G.DEV.ch10Horus(S) });
  // 星尘试炼第 15 关（两段连打；试炼自己设队伍，工厂里不碰 S.party）
  G.TRIAL_SRC['b23a_petshop'] = PetShopSrc;
  // 战斗录屏工具（tools\dev\full\rb_dev_late.py 的 birds / prophecy 入口）和后面章节借用的小游戏函数：
  //   这里必须导出，脚本重写时别删（rb_dev_late 直接调 G.LATE.ch10.birdFight / .prophecy）
  G.LATE.ch10 = { catchCheat, poker, prophecy, birdFight };
})();
