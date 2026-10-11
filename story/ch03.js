// 第3章　新加坡 / 新加坡的恶意（规划 §6.2；原著 133–139 话，第 5–6 天）
//   2026-10-11 按序章 / 第1章体验版、第2章重做版的精度重做（用户：“第二章做完之后再做第三章”）：剧情、自由走动、过场全部重写，
//   两场战斗的招式沿用 engine\moves_ch02_05.js（e_devo / e_doll / e_yellow），机关、提示、演出和手感重做。
//
//   流程：新加坡骑楼街（自由：到达，警察、樱桃摊、鱼尾狮海报 → 酒店门口）→ 入住（波鲁纳雷夫要单人间）→ 夜里的单人间
//   （只有波鲁纳雷夫，自由：查房间）→ 冰箱门自己开了，诅咒的迪波 → 第 5 战 黑檀木恶魔（迪波本人 → 玩偶，镜子碎片找玩偶）
//   → 大家冲进来，房间一片狼藉 → 第 6 天早上（自由：“花京院”很怪，收集破绽 ≥ 2）→ 缆车站分头 → 缆车外景 → 车厢里指认他
//   → 拉巴索 / 黄色节制 → 第 6 战（车厢：黏液吸收伤害，把他打到窗边撞出去 → 外景：两人掉进海里 → 水下限时）
//   → 海面：拉巴索求饶，供出荷尔·荷斯和 J·凯尔（两只右手）→ 选“饶 / 不饶”都挨一拳 → 去印度的火车：
//   波鲁纳雷夫听到“两只右手”、真花京院回来了，rerorero → TBC（第4章的地图从新加坡坐火车到加尔各答，第 9 天）
//
//   台词都是新写的（规划 §1.4 第 1 条：不冒充原句）。“rerorero”、“这是我的自由”沿用旧版本章的写法。
//   克制处理（规划 §6.2）：迪波的死只交代“再也没醒来”；黄色节制吃东西（原著吃狗）不画，改成“黏液吞掉了路边的垃圾桶”；
//   真花京院“一大早出门买樱桃，被人从背后打晕，关在酒店的储物间里”，火车上本人一句带过。
//   安妮（规划 §6.1：跟到第5章送上飞机）：火车上乔瑟夫说 SPW 联系上她爸爸了，人在外地回不来，到了印度送她上回家的飞机。
//   背景：tools\bg_new\singapore_street.py / singapore_hotel.py / cable_car.py / cable_view.py（2026-10-11 重画），
//   坐标都从背景导出的 anchors 取（bgA），背景挪了位置剧情跟着走。
//   注意：进图时 Stage 会把定义里的 props / hotspots 各复制一份（world.js Stage 构造），进图以后再改 G.STAGES 的定义不影响现场——
//   所以地图的定义都在 setStage 之前写好，显示与否、说什么都读 G.flags；要跟着人走的调查点改现场那一份（G.world.stage.hotspots）。
'use strict';
(function () {
  const G = window.G, T = G.TPL, J = G.J25, F = () => G.flags;
  const crew = ['jotaro', 'joseph', 'avdol', 'kakyoin', 'polnareff'];
  const lines = async (S, rows) => { for (const [who, text, expr] of rows) await S.say(who, text, expr ? { expr } : {}); };
  const hot = (id, x, y, label, tags, use, look, o = {}) => Object.assign({ id, x, y, label, tags, r: 22, ry: 120, use, look }, o);
  const sayBy = (S, p, map) => S.say(p.cid, T.by(p, map));
  const pick = (key, arr) => arr[(T.count(key) - 1) % arr.length];
  const follow = () => { if (G.party && G.party.rebuildFollow) G.party.rebuildFollow(); };
  // 第3章专用音效（tools\game_sfx.py 2026-10-11 新合成：razor / doll_voice / doll_scurry / fridge / slime / slime_absorb /
  //   fan_loop / city_loop / cable_loop / train_loop）：还没进数据包时用现成的顶上（直接播不存在的名字会记 missingSfx）
  const hasSnd = n => !!(G.audio && G.audio.has && G.audio.has(n));
  const snd = (name, alt, o = {}, ao = o) => { if (hasSnd(name)) G.audio.sfx(name, o); else if (alt) G.audio.sfx(alt, ao); };
  const amb = (S, name, alt, vol) => { if (hasSnd(name)) S.ambient(name, vol); else if (alt) S.ambient(alt, vol * .6); };
  // 过场开始前把亮着的替身都收回去（第2章同样的问题：自由走动时亮出来的替身，剧情一跑起来不会自己收）
  const calmStands = () => { for (const a of (G.party && G.party.members) || []) if (a.stand && a.stand.visible && a.stand.mode !== 'recall') a.stand.recall({ sfx: false }); };
  const place = (S, cid, x, y, facing = 1) => { const a = S.actor(cid); if (a) { a.visible = true; a.follow = null; a.x = x; a.y = y; a.facing = facing; a.alpha = 1; S.unpose(a); } return a; };
  const addLive = (...ps) => { const st = G.world.stage; const ids = new Set(ps.map(p => p.id)); st.props = st.props.filter(p => !ids.has(p.id)).concat(ps); };
  const dropLive = (...ids) => { const st = G.world.stage; st.props = st.props.filter(p => !ids.includes(p.id)); };
  // 图集里有没有这个动作（皮肤动作 armor_idle / fake_idle 由 tools\art 新烘焙；没有就退回旧画法）
  const hasAnim = (cid, name) => { if (!(G.D && G.D.chars && G.D.chars[cid])) return false; const A = G.atlas && G.atlas(cid); return !!(A && !A.missing && A._try && A._try(name)); };
  // 道具图（G.D.props）画在 (sx, sy) 脚底居中；没有图返回 false，调用方自己画兜底
  function drawProp(g, id, sx, sy, frame = 0, alpha = 1) {
    const pm = G.D && G.D.props && G.D.props[id], im = pm && G.image ? G.image(pm.image) : null;
    if (!im || !(G.ready && G.ready(im))) return false;
    const w = pm.size ? pm.size[0] : im.width, h = pm.size ? pm.size[1] : im.height, n = pm.frames || 1, f = Math.max(0, Math.min(n - 1, frame | 0));
    const ga = g.globalAlpha; g.globalAlpha = ga * alpha;
    g.drawImage(im, f * w, 0, w, h, Math.round(sx - w / 2), Math.round(sy - h), w, h);
    g.globalAlpha = ga;
    return true;
  }

  // ---------------------------------------------------------------- 背景锚点（没有就用默认值）
  const bgA = (bg, k, d) => { const b = G.D && G.D.bg && G.D.bg[bg]; const v = b && b.anchors ? b.anchors[k] : null; return v != null ? v : d; };
  const SSd = { arrive: [70, 164], police: [150, 164], merlion_poster: [280, 150], trash: [336, 152], cherry_stall: [420, 160], vendor: [440, 152],
    hotel_door: [612, 152], doorman: [660, 156], trishaw: [490, 150], tourist: [780, 164], cable_station: [890, 152] };
  const HDd = { door: [22, 156], bed: [100, 152], hide_bed: [100, 170], mirror: [176, 152], hide_cabinet: [175, 168], luggage: [222, 160],
    fridge: [263, 152], hide_fridge: [263, 170], window: [294, 152] };
  const CCd = { win_l: [60, 152], win_r: [260, 152], door: [160, 152], seat_l: [100, 150], seat_r: [220, 150], anne_corner: [268, 160] };
  const CVd = { car: [170, 70], car_win: [191, 63], splash: [191, 150] };
  const SS = k => bgA('singapore_street', k, SSd[k]);
  const HD = k => bgA('singapore_hotel', k, HDd[k]);
  const CC = k => bgA('cable_car', k, CCd[k]);
  const CV = k => bgA('cable_view', k, CVd[k]);

  // ---------------------------------------------------------------- 说话的人
  const sayAnne = (S, text, o = {}) => S.say('anne', text, Object.assign({ name: '安妮', actor: S.actor('anne') }, o));
  const sayDevo = (S, text, o = {}) => S.say('devo', text, Object.assign({ name: '被诅咒的迪波', actor: S.actor('devo_cut') || S.actor('devo_body') }, o));
  // 假花京院：头像、名字都是花京院（玩家还不知道），说话粗声粗气
  const sayFake = (S, text, o = {}) => S.say('kakyoin', text, Object.assign({ name: '花京院', actor: S.actor('fakeK') || S.actor('kakyoin') }, o));
  const sayRS = (S, text, o = {}) => S.say('rubbersoul', text, Object.assign({ name: '拉巴索', actor: S.actor('rs_cut') }, o));

  // ---------------------------------------------------------------- 安妮（不是队员：换图不会被带过去，每张图自己放）
  function anneAt(S, x, y, o = {}) {
    let a = S.actor('anne');
    if (!a) a = S.spawn('anne', x, y, { id: 'anne', team: 'npc', label: '安妮', name: '安妮' });
    a.visible = true; a.alpha = 1; a.follow = null; a.x = x; a.y = y; a.facing = o.facing || 1;
    S.unpose(a);
    return a;
  }
  // 跟队：排在最后（跟随槽 6），不能当队长；搭话按队长、按时段不同；第二天早上第一次搭话说出“踢猫”（破绽之一）
  function anneFollow(S) {
    if (!F().anneJoined || F().anneLeft) return null;
    const a = anneAt(S, S.player.x - 34, S.player.y, { facing: S.player.facing });
    S.follow(a, S.player); a.followSlot = 6; a.leadable = false;
    a.talk = async (S2, me, p) => {
      const L = p && p.cid;
      if (F().c3Morning && !(F().c3Clues || {}).cat) {
        await S2.say('anne', '……喂。那个红头发的哥哥，刚才在后巷踢了一只猫！', { name: '安妮', actor: a });
        await S2.say('anne', '他以前不是这样的。他昨天还把樱桃分给我吃呢。', { name: '安妮', actor: a });
        clue(S2, 'cat');
        return;
      }
      const t = F().c3Morning
        ? (L === 'jotaro' ? pick('c3anJoM', ['……你也觉得他怪怪的吧？', '缆车！我要坐靠窗的位子！'])
          : L === 'polnareff' ? pick('c3anPolM', ['你的头发今天也立得好高。', '……你昨晚一个人在房间里大喊大叫，吵死了。'])
            : L === 'joseph' ? pick('c3anJosM', ['老爷爷，SPW 找到我爸爸了吗？', '我不要一个人回家。……我是说，现在还不要。'])
              : pick('c3anAvM', ['今天的花京院哥哥，眼睛好吓人。', '算命的，你今天抽到什么牌了？']))
        : (L === 'jotaro' ? pick('c3anJo', ['……新加坡好热。你的衣服不热吗？', '我爸爸……应该就在这座城市的某个地方。'])
          : L === 'polnareff' ? pick('c3anPol', ['别看那些阿姨了，色狼。', '你要单人间？……你是怕晚上被人听见说梦话吧。'])
            : L === 'joseph' ? pick('c3anJos', ['老爷爷，你说 SPW 能帮我找到爸爸？说话算话哦。', '那个警察一直在看我……'])
              : L === 'avdol' ? pick('c3anAv', ['那个狮子头鱼身子的东西是什么？', '你身上有香料的味道。'])
                : L === 'kakyoin' ? pick('c3anKak', ['那边有卖樱桃的。……你是不是一直在看？', '你说话总是好客气。'])
                  : '……');
      await S2.say('anne', t, { name: '安妮', actor: a });
    };
    return a;
  }

  // ================================================================ 第 5 战：黑檀木恶魔（酒店单人间）
  //   段 1 迪波本人：故意挨打，恨意槽满 100 → 倒地狂笑 → 段 2 玩偶（强度 = 1 + 段 1 打掉的血 / 600，最多 ×1.5）。
  //   段 2 玩偶：每 4 s 钻进家具底下看不见（e_doll 的 brain），出招时露出来；看不见的时候只有两样东西指路——
  //   ① 三块镜子碎片：玩偶在碎片左右 70 px 以内时，碎片里映出它从家具底下探头（peek）、碎片闪一下；② 它脚下冒灰 + 沙沙声。
  //   J3 贯穿突刺 / U 千本刺打到藏着的它 → 逼出来（e_doll 的 onHitBy）。
  const SHARDS = [[100, 170, 0], [175, 128, 1], [292, 112, 1]];   // [x, y, 挂在柜门 / 窗玻璃上=1（不落地，画在墙上）]
  let shardProp = null;
  function makeShards() {
    shardProp = { type: 'custom', id: 'mirror_shards', x: 0, y: 0, depth: 150, draw(g, ox, oy, t) {
      const c = G.world.fight;
      if (!c || c.id !== 'b05_devo' || c.wave !== 1) return;
      const doll = c.boss;
      for (const [x, y] of SHARDS) {
        const sx = Math.round(x + ox), sy = Math.round(y + oy);
        const near = doll && doll.mem && doll.mem.hidden && Math.abs(doll.x - x) < 70;
        const glint = near ? (Math.floor(t * 6) % 2) : (Math.floor(t * .7 + x) % 5 === 0 ? 1 : 0);
        if (!drawProp(g, 'mirror_piece', sx, sy, glint)) {
          g.fillStyle = '#5578a6'; g.beginPath(); g.moveTo(sx - 6, sy); g.lineTo(sx + 2, sy - 13); g.lineTo(sx + 6, sy - 2); g.closePath(); g.fill();
          g.fillStyle = glint ? '#ffffff' : '#d0f8ff'; g.fillRect(sx - 2, sy - 7, 3, 1);
        }
        if (near && G.atlas) {
          // 倒影：玩偶从家具底下探出半个脑袋（只在碎片的镜面里），离得越近越清楚
          const A = G.atlas('devo_doll'), k = 1 - Math.abs(doll.x - x) / 70;
          const anim = hasAnim('devo_doll', 'peek') ? 'peek' : 'idle';
          g.save(); g.beginPath(); g.rect(sx - 5, sy - 13, 11, 12); g.clip();
          if (A && A.draw) A.draw(g, anim, Math.floor(t * 4) % 2, sx + G.clamp((doll.x - x) * .05, -3, 3), sy - 1, { scale: .5, alpha: .45 + .5 * k, flip: doll.x < x });
          g.restore();
        }
      }
    } };
    return shardProp;
  }
  // 迪波的身体（段 2 一直躺在地上）
  const removeBody = () => { const b = G.S && G.S.actor('devo_body'); if (b) b.remove = true; };
  const DEVO_TAUNT = ['嘿嘿……再用力点……', '好痛……好恨啊……', '对……就是这样……再恨我一点……', '嘿嘿嘿……'];
  const DOLL_TAUNT = ['你这只法国公鸡！', '剃刀先生想你啦～', '嘻嘻嘻！在这儿哦！', '抓不到～抓不到～', '头发立那么高，是天线吗？'];
  G.BOSS25.devo = () => J.base('b05_devo', 'polnareff', [30, 290], {
    vs: 'devo', music: 'battle', gauge: { label: '恨意', max: 100, value: 0 }, bench: 'hide',
    waves: [[{ actor: 'devo', kit: 'e_devo', boss: true, hp: 300, minHp: 1, x: 236, y: 164 }],
      [{ actor: 'devo_doll', kit: 'e_doll', boss: true, hp: 400, x: HD('hide_bed')[0], y: 166 }]],
    onWave: async (S, i, es, a, c) => {
      const d = c.data, b = es[0];
      if (i === 0) {
        removeBody();
        Object.assign(d, { devo: b, strength: 1, devoX: 236, tauntAt: 0, dollTaunt: 6, scurry: 0, dust: 0 });
        G.world.stage.state.fridge = 1; G.world.stage.state.mess = 0;
        c.on('hit', e => {
          if (e.t !== d.devo || e.guard) return;
          c.gauge.add(20); d.strength = Math.min(1.5, 1 + (300 - e.t.hp) / 600);
          if (c.t >= d.tauntAt) { d.tauntAt = c.t + 2.2; S.emote(d.devo, DEVO_TAUNT[Math.floor(Math.random() * DEVO_TAUNT.length)], 1.1, '#ff8aa0'); }
        });
        S.hint(a > 0 ? '恨意满了玩偶就会出来——打得越狠，玩偶越凶。'
          : '他在故意挨打！恨意满了玩偶就会动——打得越狠，玩偶越凶。', 12);
        return;
      }
      // 段 2：迪波倒在地上狂笑，玩偶从床底下钻出来
      const body = S.spawn('devo', d.devoX, 166, { id: 'devo_body', team: 'npc', name: '被诅咒的迪波' });
      body.facing = -1; S.pose(body, 'down'); body.talk = null; body.standReact = false;
      await S.say('devo', '嘿嘿嘿……恨够了……去吧，我的恶魔……', { name: '被诅咒的迪波', actor: body });
      b.dmgOut = d.strength;
      c.gauge.label = '玩偶强度'; c.gauge.max = 1.5; c.gauge.value = d.strength;
      snd('doll_scurry', 'whoosh', { vol: .8 }, { vol: .4, rate: 2 }); snd('doll_voice', 'sting_comedy', { vol: .8 }, { vol: .5, rate: 1.6 });
      S.emote(b, '嘻嘻嘻嘻！', 1.4, '#ff8aa0');
      S.hint(a > 0 ? '碎片在闪 = 玩偶在附近，冒灰 = 它就在那儿。J3 / U 逼出来。'
        : '玩偶藏起来了！碎片闪 = 在附近，冒灰 = 就在那儿。J3 / U 逼出来！', 14);
    },
    tick(c, dt) {
      const d = c.data, b = c.boss;
      if (c.wave === 0) {
        c.gauge.add(2 * dt);
        if (c.gauge.value >= 100 && b && !b.remove) { d.devoX = b.x; b.remove = true; G.audio.sfx('sting_reveal'); }
        return;
      }
      if (!b) return;
      // 藏着：脚下冒灰 + 沙沙声；露出来：隔一阵骂一句
      if (b.mem.hidden) {
        d.dust -= dt; d.scurry -= dt;
        if (d.dust <= 0) { d.dust = .55; G.combat.fxAt('dust', { x: b.x, y: b.y, n: 3, life: .25 }, b, .25); }
        if (d.scurry <= 0) { d.scurry = 1.3; snd('doll_scurry', null, { vol: .55 }); }
      } else if (c.t >= d.dollTaunt) {
        d.dollTaunt = c.t + 6 + Math.random() * 3;
        G.S.emote(b, DOLL_TAUNT[Math.floor(Math.random() * DOLL_TAUNT.length)], 1.4, '#ff8aa0');
        snd('doll_voice', null, { vol: .7 });
      }
    },
    after: async (s, es, a, c) => {
      const b = es[0], x = b ? b.x : 160;
      // 千本刺把玩偶剁成棉絮
      s.fx('burst', { x, y: 150, n: 40, colours: ['#ffffff', '#e0dcff', '#c8b8a0'], speed: 100 });
      s.sfx('slash'); s.shake(2, .3);
      T.prop(s, 'doll_razor', x + 6, 168, { id: 'doll_razor' });
      G.world.stage.state.mess = 1;
    },
    testHint: c => ({ phase: c.wave, hate: c.gauge.value, strength: c.data.strength, hidden: !!(c.boss && c.boss.mem && c.boss.mem.hidden), shards: SHARDS.map(s => [s[0], s[1]]) }),
  });

  // ================================================================ 第 6 战：黄色节制（缆车车厢 → 海里）
  //   车厢：黏液把伤害吸收到 ×0.1（kit e_yellow 的 dmgMul），但吸收不了冲力——每一下都把他往后推（J3 推得最远）。
  //   把他推到端窗 28 px 以内：J3 / 连打打中 → 撞破窗户；或者贴近按 U「抱住他跳窗」。→ 外景：两人掉进海里 → 水下：
  //   黏液维持不住，伤害 ×1.5、他只会乱抓；限时 24 s，没打完他爬回车厢（窗户已经碎了，再推一次）。
  //   身上的黏液：碰到他、被他打中 +1 层（最多 5），每层每秒 −0.5 HP，K 闪避甩掉 1 层；地上的黏液水洼走速 ×0.6。
  //   2026-10-11：原来每层每秒 −1、推不动他，整章自动测试在车厢里连输 4 次（站在窗边干等他过来）
  const nearWin = c => {
    const b = c.boss;
    if (!b || c.data.water) return null;
    if (Math.abs(b.x - CC('win_l')[0]) <= 28) return 'l';
    if (Math.abs(b.x - CC('win_r')[0]) <= 28) return 'r';
    return null;
  };
  async function intoWater(c, side) {
    const d = c.data, S = G.S, b = c.boss;
    if (!b || d.water || d.shifting || d.falling) return;
    d.falling = true;
    side = side || nearWin(c) || (b.x < 160 ? 'l' : 'r');
    const key = 'win_' + side;
    G.world.stage.state[key] = 1; if (G.STAGES.cable_ch3) G.STAGES.cable_ch3.state[key] = 1;
    G.audio.sfx('glass_break'); G.audio.sfx('punch_heavy', { vol: .7 }); G.shake(5, .5);
    G.combat.fxAt('burst', { x: CC(key)[0], y: 100, n: 24, speed: 120, colours: ['#d8f4ff', '#ffffff', '#ffe040'] }, c.player, .5);
    const old = G.world.cine;
    G.world.cine = { by: 'battle-transition' };
    try {
      // 外景（cable_view，窗碎了）：承太郎抱着拉巴索从车厢里掉出去，掉进海里
      const [cx, cy] = CV('car_win'), [sx, sy] = CV('splash');
      const parts = [{ kind: 'sprite', cid: 'jotaro', anim: 'hurt', x: cx, y: cy + 10, scale: .5 },
        { kind: 'sprite', cid: 'rubbersoul', anim: 'hurt', x: cx + 7, y: cy + 10, scale: .5 }];
      let splashOn = false, splashT0 = null;
      const h = T.show(S, { bg: 'cable_view', bgState: { win: 1 }, parts, draw: (wg, t) => {
        if (!splashOn) return;
        if (splashT0 == null) splashT0 = t;
        const k = Math.min(1, (t - splashT0) / .5), hgt = Math.round(26 * Math.sin(k * Math.PI));
        wg.fillStyle = '#e6f4ff';
        for (let i = -6; i <= 6; i++) wg.fillRect(sx + i * 2, sy - Math.round(hgt * (1 - Math.abs(i) / 7)), 2, Math.max(1, Math.round(hgt * (1 - Math.abs(i) / 7))));
      } });
      if (d.falls) { await S.wait(.15); } else await S.wait(.35);
      await S.animate(d.falls ? .7 : 1.0, k => { parts[0].x = cx + k * 8; parts[1].x = cx + 7 + k * 10; parts[0].y = parts[1].y = cy + 10 + k * k * (sy - cy - 10); });
      parts[0].hidden = parts[1].hidden = true;
      splashOn = true;
      G.audio.sfx('splash'); G.audio.sfx('water_splash', { vol: .7 });
      await S.wait(.55);
      h.close();
    } finally { if (J.valid(c)) G.world.cine = old; }
    if (!J.valid(c)) return;
    d.falls = (d.falls || 0) + 1;
    d.falling = false; d.water = true; d.slime = 0; d.waterUntil = c.t + 24; c.spec.arena = [30, 290]; G.world.hazards = [];
    b.skin = null; b.outline = null;
    await J.transfer(c, 'sea_ch3', 120, 205);
    if (J.valid(c)) G.ui.hint(d.falls > 1 ? '又掉进海里了！趁黏液撑不住——J 三连接着连按，欧拉连打！' : '海水里黏液撑不住了！伤害 ×1.5——J 三连接着连按，欧拉连打！（限时）', 4);
  }
  const armorOn = b => { if (!b) return; if (hasAnim('rubbersoul', 'armor_idle')) { b.skin = 'armor'; b.outline = null; } else b.outline = '#ffe040'; };
  G.BOSS25.yellow = () => J.base('b06_yellowtemperance', 'jotaro', [40, 280], {
    vs: 'yellowtemperance', bench: 'hide', music: 'battle', gauge: { label: '身上的黏液', max: 5, value: 0 },
    // HP 600 → 500（几乎所有伤害都在海里打：24 s 内打完 600 太难；420 时测试器一次落水就打完了，500 大概要逼他下水两次；2026-10-11 规划 §6.2 同步改）
    waves: [[{ actor: 'rubbersoul', kit: 'e_yellow', boss: true, hp: 500, x: 200, y: 160, poiseMax: 0,
      phases: [{ at: .5, run: async (S, e, c) => {
        if (c.attempt > 0) return;
        await S.say('rubbersoul', '咕……咳咳！海水……我的黏液……！', { name: '拉巴索' });
        await S.say('jotaro', '……在水里，你什么都吃不下。');
      } }] }]],
    kitOverride: { jotaro: { special: J.special(0, '抱住他跳窗：U', c => !!nearWin(c) && Math.abs(c.player.x - c.boss.x) <= 34, async (S, p, c) => {
      G.uifx.sfx('ガシッ', p); await intoWater(c);
    }) } },
    onWave: async (S, i, es, a, c) => {
      if (G.world.stage.id !== 'cable_ch3') await J.transfer(c, 'cable_ch3', 120, 220);
      c.spec.arena = [40, 280]; G.world.stage.x0 = 40; G.world.stage.x1 = 280;
      const d = c.data, b = es[0];
      Object.assign(d, { slime: 0, water: false, falling: false, falls: 0, carry: 0, contactAt: 0, absorbAt: 0, glintAt: 0, winHint: false, drip: 0, baseSpeed: c.player.speed });
      armorOn(b);
      d.engulf = () => {
        if (d.qteBusy) return;
        d.slime = Math.min(5, d.slime + 3);
        J.qte(c, async () => {
          snd('slime', 'drain', { vol: .9 }, { rate: .6 });
          const ok = await S.mash({ need: 12, time: 2.4, decay: 0, label: '黏液包住全身！连按 J 挣脱' });
          if (!ok && J.valid(c)) J.harm(c, 10);
          return ok;
        }).catch(G.cancelIgnore);
      };
      c.on('hit', e => {
        const p = c.player;
        if (e.att === c.boss && e.t === p && !e.guard && !d.water) d.slime = Math.min(5, d.slime + 1);
        if (e.t !== c.boss || d.water || d.falling) return;
        // 被吸收了，但冲力还在：往后推（J3 最远）
        const push = e.slot === 'J3' ? 30 : e.slot === 'rush' ? 4 : e.slot === 'special' ? 0 : 7;
        if (push) c.boss.x = G.clamp(c.boss.x + Math.sign(c.boss.x - p.x || p.facing) * push, 44, 276);
        if (c.t >= d.absorbAt) { d.absorbAt = c.t + .35; snd('slime_absorb', 'drain', { vol: .7 }, { vol: .5, rate: 1.4 }); G.S.emote(c.boss, '吸收了！', .6, '#ffe040'); }
        if ((e.slot === 'J3' || e.slot === 'rush') && nearWin(c)) { intoWater(c).catch(G.cancelIgnore); return; }
        if (c.t >= d.contactAt) { d.contactAt = c.t + .5; d.slime = Math.min(5, d.slime + 1); }
      });
      const [ax, ay] = CC('anne_corner');
      const anne = S.spawn('anne', ax, ay, { id: 'anne_battle', team: 'npc', name: '安妮' }); anne.facing = -1; S.pose(anne, 'idle'); anne.standReact = false;
      S.hint(a > 0 ? '用 J3 把他推到窗边，再撞出去 / 贴近按 U。K 甩掉黏液。'
        : '打不痛他，但打得退：J3 把他推到窗边撞出去，或贴近按 U。K 甩黏液。', 14);
    },
    tick(c, dt) {
      const d = c.data, p = c.player, b = c.boss;
      if (!b) return;
      if (d.water) {
        c.gauge.label = '海里剩余（秒）'; c.gauge.max = 24; c.gauge.value = Math.max(0, d.waterUntil - c.t); p.speed = d.baseSpeed;
        if (c.t >= d.waterUntil && !d.shifting) {
          d.water = false; d.slime = 0; c.spec.arena = [40, 280]; armorOn(b);
          J.transfer(c, 'cable_ch3', 120, 220).then(() => { if (J.valid(c)) { G.world.stage.x0 = 40; G.world.stage.x1 = 280; } }).catch(G.cancelIgnore);
          G.ui.hint('他爬回车厢了！窗户已经碎了——再把他推过去。', 4);
        }
        return;
      }
      if (d.falling) return;
      if (G.input.hit('dodge') && d.slime) { d.slime = Math.max(0, d.slime - 1); G.combat.fxAt('burst', { x: p.x, y: p.y - 18, n: 8, speed: 60, colours: ['#ffe040', '#c8a018'] }, p, .3); snd('slime', null, { vol: .4, rate: 1.3 }); }
      c.gauge.label = '身上的黏液'; c.gauge.max = 5; c.gauge.value = d.slime;
      if (Math.abs(p.x - b.x) < 15 && Math.abs(p.y - b.y) < 9 && c.t >= d.contactAt) { d.contactAt = c.t + .65; d.slime = Math.min(5, d.slime + 1); }
      d.carry += d.slime * .5 * dt;
      while (d.carry >= 1) { d.carry--; J.harm(c, 1); }
      // 身上的黏液往下滴
      if (d.slime) { d.drip -= dt; if (d.drip <= 0) { d.drip = .5; G.combat.fxAt('burst', { x: p.x, y: p.y - 22, n: d.slime, speed: 18, colours: ['#ffe040', '#c8a018'] }, p, .3); } }
      const slow = G.world.hazards.some(h => !h.dead && h.phase === 'active' && h.tag === 'slime' && p.x >= h.x0 && p.x <= h.x1 && p.y >= h.y0 && p.y <= h.y1);
      p.speed = d.baseSpeed * (slow ? .6 : 1);
      // 他被逼到窗边：窗户闪光 + 第一次提示
      const w = nearWin(c);
      if (w && c.t >= d.glintAt) {
        d.glintAt = c.t + .6;
        G.combat.fxAt('glint', { x: CC('win_' + w)[0], y: 96, size: 12 }, p, .3);
        if (!d.winHint) { d.winHint = true; G.ui.hint('他被逼到窗边了！J3 把他撞出去，或者贴近按 U！', 4); }
      }
    },
    after: async (s, es, a, c) => { const b = es[0]; if (b) { b.skin = null; b.outline = null; } },
    testHint: c => ({ water: c.data.water, slime: c.data.slime, waterLeft: c.data.waterUntil - c.t, window: !!nearWin(c), falling: !!c.data.falling,
      bossX: c.boss && c.boss.x, winL: CC('win_l')[0], winR: CC('win_r')[0] }),
  });

  // ================================================================ 骑楼街（sg_street_ch3，singapore_street，960 宽）
  const clueN = () => Object.keys(F().c3Clues || {}).length;
  const hasClue = k => !!(F().c3Clues || {})[k];
  function clue(S, k) { const n = J.unique('c3Clues', k); if (n === 2) S.hint('破绽够了。去街尽头的缆车站，当面戳穿他。', 6); return n; }
  // 路边的垃圾桶：到达那天立在那儿；第二天早上不见了，只剩一滩黄色黏液（黄色节制吃掉的——原著吃狗，这里改成垃圾桶）
  function trashProp() {
    const [x, y] = SS('trash');
    return { type: 'custom', id: 'trash', x, y, depth: y - 2, draw(g, sx, sy, t) {
      if (!F().c3Morning) {
        if (!drawProp(g, 'trash_can', sx, sy)) { g.fillStyle = '#4a6a52'; g.fillRect(sx - 6, sy - 16, 12, 16); g.fillStyle = '#6a8a72'; g.fillRect(sx - 7, sy - 18, 14, 3); }
        return;
      }
      if (!drawProp(g, 'slime_pool', sx, sy + 2, Math.floor(t * 2) % 2)) { g.fillStyle = '#e8c830'; g.fillRect(sx - 10, sy - 3, 20, 4); g.fillStyle = '#fff6a0'; g.fillRect(sx - 5, sy - 3, 4, 1); }
    } };
  }
  function memberTalkArrival() {
    T.memberTalk({
      joseph: async S => S.say('joseph', pick('c3joA', ['新加坡！……空气里都是咖喱和海风的味道。', '火车票的事交给 SPW。今晚先好好睡一觉。', '那个警察一直盯着我们。……五个大男人带着一个小姑娘，是挺可疑的。'])),
      avdol: async S => S.say('avdol', pick('c3avA', ['从这里坐火车北上，穿过马来半岛，就是印度。', '这座城市的人，生命之火都烧得很旺。……是座好城市。'])),
      kakyoin: async S => S.say('kakyoin', pick('c3kakA', ['那边的摊子在卖樱桃。……等安顿好了再去买。', '新加坡比我想的干净。地上一张纸屑都没有。'])),
      polnareff: async S => S.say('polnareff', pick('c3polA', ['终于踩到不晃的地面了！地面万岁！', '今晚我要一个人住。谁也别想跟我抢单人间。'])),
      jotaro: async S => S.say('jotaro', pick('c3joA', ['……热。', '……'])),
    });
  }
  function memberTalkMorning() {
    T.memberTalk({
      joseph: async S => S.say('joseph', pick('c3joM', ['花京院今天话真少。……昨晚没睡好？', '火车中午开。别走散了。'])),
      avdol: async S => S.say('avdol', pick('c3avM', ['今天早上抽到的牌是『节制』。……可这张牌，是倒着的。', '花京院身上的气息……说不上来，有点黏。'])),
      polnareff: async S => S.say('polnareff', pick('c3polM', ['我跟花京院打招呼，他瞪了我一眼。……我做错什么了？', '昨晚那个娃娃……我现在看见娃娃就想拔剑。'])),
      jotaro: async S => S.say('jotaro', pick('c3joM', ['……', '……那家伙，从早上起就不对劲。'])),
      // 假花京院（队伍里灰着，不能当队长）：说话很冲
      kakyoin: async S => sayFake(S, pick('c3fakeTalk', ['……早。', '那个小鬼，烦死了。', '……看什么看。', '缆车？……随便。'])),
    });
  }
  function setupArrival() {
    const st = G.STAGES.sg_street_ch3;
    st.props = [trashProp()];
    st.triggers = [];
    const [px, py] = SS('police'), [vx, vy] = SS('vendor'), [tx, ty] = SS('tourist'), [dx, dy] = SS('doorman');
    const bell = hasAnim('npc_bellhop', 'idle') ? 'npc_bellhop' : 'npc_townsfolk';
    st.npcs = [
      T.npc('npc_police', 'police_sg', px, py, { facing: 1, label: '警察', name: '警察', talk: async (S, me) => {
        me = S.actor('police_sg') || me;
        const anne = S.actor('anne'), jos = S.actor('joseph');
        if (!F().c3Morning && T.count('c3police') === 1 && anne && anne.visible && jos) {
          await S.say('npc_police', '那边那个小姑娘。……你的护照呢？', { name: '警察', actor: me });
          anne.follow = null; anne.facing = me.x > jos.x ? -1 : 1;
          await S.walk(anne, jos.x - (me.x > jos.x ? 10 : -10), jos.y + 3, { speed: 130, anim: 'run' });
          S.emote(anne, '……', 1);
          await S.say('joseph', '我孙女。我们是来观光的。');
          S.emote(me, '？', .8);
          await S.say('npc_police', '……孙女？', { name: '警察', actor: me });
          await S.wait(.4);
          await S.say('npc_police', '……偷渡者？没看见，没看见。……乱扔垃圾在这儿可是要罚款的，你们别乱扔就行。', { name: '警察', actor: me });
          anneFollow(S);
          return;
        }
        await S.say('npc_police', pick('c3pol2', F().c3Morning
          ? ['早。……街那头的垃圾桶不见了。谁会偷一个垃圾桶？', '缆车站往前走到头就是。']
          : ['乱扔垃圾要罚款。吐口香糖也是。', '酒店就在前面，白色的那栋。']), { name: '警察', actor: me });
      } }),
      T.npc('npc_townsfolk', 'vendor_sg', vx, vy, { facing: -1, label: '小贩', name: '小贩', talk: async (S, me, p) => {
        me = S.actor('vendor_sg') || me; p = p || S.player;
        if (F().c3Morning) {
          await S.say('npc_townsfolk', '红头发的小哥？天刚亮就来买过一大袋，往酒店后巷那边走了。', { name: '小贩', actor: me });
          await S.say('npc_townsfolk', '……奇怪的是，刚才他又来了一趟，问我“樱桃是什么东西”。', { name: '小贩', actor: me });
          clue(S, 'vendor');
          return;
        }
        await S.say('npc_townsfolk', '樱桃！新鲜的樱桃！从澳洲运来的！', { name: '小贩', actor: me });
        if (p.cid === 'kakyoin') await S.say('kakyoin', '……（咽口水）等安顿好了，再来买。');
      } }),
      T.npc('npc_hk_passer_a', 'tourist_sg', tx, ty, { facing: -1, label: '游客', name: '游客', talk: async (S, me) => {
        await S.say('npc_hk_passer_a', pick('c3tour', F().c3Morning
          ? ['早啊。你们也去坐缆车？从山上一直坐到对面的岛，海是绿色的！', '昨晚那家酒店好像出了什么事，半夜吵吵闹闹的。']
          : ['你们也是来旅游的？鱼尾狮一定要去看看！……什么，赶时间？', '山上那个缆车，可以坐到对面的岛上。明天我也要去。']), { name: '游客', actor: S.actor('tourist_sg') || me });
      } }),
      T.npc(bell, 'bellhop', dx, dy, { facing: -1, label: '门童', name: '门童', talk: async (S, me) => {
        await S.say(bell, F().c3Morning ? '早上好。……昨晚 712 号房的事，经理说不用担心，SPW 的先生们已经处理好了。' : '欢迎光临。SPW 财团的乔斯达先生？房间已经准备好了，请进。',
          { name: '门童', actor: S.actor('bellhop') || me });
        if (!F().c3Morning) F().sgHotel = true;
      } }),
      // 第二天早上：一只猫冲着“花京院”炸毛（第一次搭话算安妮那条破绽的补充，不单独计数）
      T.npc('npc_cat', 'cat_sg', SS('trash')[0] + 16, SS('trash')[1] + 14, { facing: -1, label: '猫', name: '猫', cond: () => !!F().c3Morning, talk: async (S, me, p) => {
        me = S.actor('cat_sg') || me;
        snd('cat_hiss', 'sting_comedy', { vol: .5 }, { vol: .3, rate: 1.8 }); S.emote(me, '！', .8);
        await S.say(null, '猫冲着“花京院”弓起背，全身的毛都炸开了。');
        await sayBy(S, p || S.player, { avdol: '……动物比人敏感。它怕的是他身上的东西。', jotaro: '……', _: '这猫……刚才被谁欺负过？' });
      } }),
    ];
    st.hotspots = [
      hot('merlion', SS('merlion_poster')[0], SS('merlion_poster')[1], '鱼尾狮海报', [],
        async (S, h, p) => {
          if (p.cid === 'polnareff') {
            await S.say('polnareff', 'Magnifique！谁来给我拍一张？');
            S.sfx('camera_shutter'); S.flash(.12, .25, '#ffffff');
            await S.say('polnareff', '……乔斯达先生，你的念写照片能不能把我拍帅一点？');
            return;
          }
          await sayBy(S, p, { joseph: '上半身是狮子，下半身是鱼。……跟我们这群人一样，凑在一起什么都不像。', avdol: '狮子守着港口。……是个好兆头。',
            kakyoin: '鱼尾狮嘴里在喷水。……原来是喷泉的广告。', jotaro: '……', _: '鱼尾狮的海报。' });
        }, null, { ly: 70 }),
      hot('cherry', SS('cherry_stall')[0], SS('cherry_stall')[1], '樱桃摊', [],
        async (S, h, p) => {
          if (!F().c3Morning) {
            await sayBy(S, p, { kakyoin: '……樱桃。红得发亮。……一会儿再来。', polnareff: '樱桃？那是花京院的最爱吧。', _: '一筐红得发亮的樱桃。' });
            return;
          }
          // 第二天：假花京院抓了一把，整颗嚼碎咽下去
          const fk = S.actor('kakyoin');
          if (fk && fk.visible) { fk.follow = null; await S.walk(fk, h.x + 12, h.y + 4, { speed: 110 }); fk.facing = -1; }
          await S.say('npc_townsfolk', '樱桃！小哥，又来啦？', { name: '小贩', actor: S.actor('vendor_sg') });
          await sayFake(S, '……给我。');
          S.sfx('teeth_crunch', { vol: .7 }); S.shake(1, .15); await S.wait(.35); S.sfx('teeth_crunch', { vol: .6, rate: .9 });
          await S.say(null, '“花京院”一把抓起樱桃塞进嘴里，连核一起嚼得咯吱作响，咽了下去。');
          await sayBy(S, p, { jotaro: '……花京院吃樱桃，会先在舌头上转半天。', polnareff: '……喂，花京院，核！核也吃了？', joseph: '……花京院平时吃樱桃，可不是这么吃的。',
            avdol: '……他平时会把樱桃在舌头上转着玩。今天像饿狼一样。', _: '……' });
          follow();
          clue(S, 'cherry');
        }, null, { ly: 104 }),
      hot('trash', SS('trash')[0], SS('trash')[1], '垃圾桶', ['detail', 'life'],
        async (S, h, p) => {
          if (!F().c3Morning) { await sayBy(S, p, { polnareff: '……在新加坡乱扔垃圾要罚款。我忍着。', _: '路边的垃圾桶。干干净净的。' }); return; }
          await S.say(p.cid, '昨天这里的垃圾桶……不见了？地上只剩一滩黄色的、黏糊糊的东西。');
          clue(S, 'trash');
        },
        async (S, h, p) => {
          if (!F().c3Morning) { await S.say(p.cid, '……没什么特别的。'); return; }
          await sayBy(S, p, { jotaro: '……黏液还在动。像是活的。', avdol: '这滩东西……有生命的气息。', _: '……这东西在动。' });
          clue(S, 'trash');
        }, { ly: 112 }),
      hot('trishaw', SS('trishaw')[0], SS('trishaw')[1], '三轮车', [],
        async (S, h, p) => sayBy(S, p, { joseph: '坐这个去酒店？……算了，走两步就到。年轻的时候我在纽约也拉过——……没有，开玩笑的。',
          polnareff: '三轮车！坐上去兜一圈，一定很有情调。……司机呢？', avdol: '车夫去吃饭了吧。座位上还放着一顶草帽。', kakyoin: '这种三轮车，在日本已经很少见了。',
          jotaro: '……', _: '路边停着一辆三轮车。' }), null, { ly: 100 }),
      hot('cable_station', SS('cable_station')[0], SS('cable_station')[1], '缆车站', [],
        async (S, h, p) => {
          if (!F().c3Morning) {
            await S.say(p.cid, '去山上缆车站的楼梯。……从山上能坐缆车到对面的岛。');
            const a = S.actor('anne');
            if (a && a.visible) { await sayAnne(S, '我想坐那个！'); await S.say('joseph', '明天吧。今天先去酒店。'); }
            return;
          }
          if (clueN() < 2) { await S.say('jotaro', '……先弄清楚，他到底哪里不对劲。'); return; }
          F().toCable = true;
        }, null, { ly: 96 }),
      hot('hotel_door', SS('hotel_door')[0], SS('hotel_door')[1], '酒店', [],
        async (S, h, p) => {
          if (F().c3Morning) { await S.say(p.cid, '酒店。……昨晚的事，SPW 已经处理好了。'); return; }
          F().sgHotel = true;
        }, null, { ly: 100 }),
    ];
  }
  async function arrivalIntro(S) {
    calmStands();
    const [ax, ay] = SS('arrive');
    // 左边 x < 24 是前景的雨树树干：人从 x 44 往右排，安妮在最前排
    const order = [['jotaro', 48], ['joseph', 28], ['avdol', 10], ['kakyoin', -8], ['polnareff', -26]];
    for (const [cid, dx] of order) place(S, cid, ax + dx, ay - 4 + (dx % 3), 1);
    anneAt(S, ax - 36, ay + 8);
    S.location('singapore');
    await S.wait(.6);
    S.pose('polnareff', 'kneel'); await S.wait(.3);
    await lines(S, [['polnareff', '终于踩到不晃的地面了！……地面万岁！'], ['joseph', 'SPW 在前面订好了酒店。今晚好好睡一觉，明天坐火车去印度。']]);
    S.unpose('polnareff');
    await lines(S, [['avdol', '从新加坡坐火车北上，穿过马来半岛，就是印度。']]);
    await sayAnne(S, '……我爸爸就在新加坡。我自己去找他。');
    await lines(S, [['joseph', '这么大的城市，你一个小姑娘怎么找？明天让 SPW 帮你查。今晚先跟着我们。']]);
    await sayAnne(S, '……哼。那就再跟你们一天。');
    await lines(S, [['jotaro', '……呀嘞呀嘞。']]);
  }
  // 入住：酒店门口（街上）
  async function checkIn(S) {
    calmStands(); S.hint(null);
    const [hx, hy] = SS('hotel_door'), [dx, dy] = SS('doorman');
    const pos = [['jotaro', -10, 4], ['joseph', -30, 0], ['avdol', -50, 6], ['kakyoin', -70, 2], ['polnareff', 14, 8]];
    for (const [cid, ox, oy] of pos) { const a = S.actor(cid); if (a) { a.follow = null; S.walk(a, hx + ox, hy + oy, { speed: 120 }).catch(G.cancelIgnore); } }
    const anne = S.actor('anne'); if (anne) { anne.follow = null; S.walk(anne, hx - 88, hy + 8, { speed: 120 }).catch(G.cancelIgnore); }
    await S.wait(.8);
    for (const [cid] of pos) { const a = S.actor(cid); if (a) a.facing = a.x < dx ? 1 : -1; }
    const bell = S.actor('bellhop');
    await lines(S, [['joseph', 'SPW 帮我们订了房间。两人一间，安妮跟——'], ['polnareff', '我要单人间！']]);
    S.emote('polnareff', '！', .6);
    await lines(S, [['avdol', '这种时候单独行动，太危险了。'], ['polnareff', '敌人要来就来，我一个人就够了。……再说，跟你们挤一间，我会失眠的。'],
      ['kakyoin', '……你是怕自己打呼噜被我们听见吧。'], ['polnareff', '花京院！']]);
    await sayAnne(S, '我要有空调的房间！');
    await lines(S, [['joseph', '……行行行。都依你们。']]);
    await S.fadeOut(.6);
  }

  // ================================================================ 酒店单人间（sg_hotel_ch3，singapore_hotel，320 单屏，夜里）
  function setupHotel() {
    const st = G.STAGES.sg_hotel_ch3;
    st.npcs = []; st.triggers = [];
    st.props = [makeShards()];
    st.state = Object.assign({}, st.state, { fridge: 0, mess: 0 });
    const reg = id => { J.unique('hotelClues', id); };
    st.hotspots = [
      hot('fridge', HD('fridge')[0], HD('fridge')[1], '冰箱', ['cut'],
        async (S, h, p) => {
          reg('fridge');
          const n = T.count('c3fridge');
          if (n === 1) await S.say('polnareff', '冰箱……嗯？好像比刚才搬进来的时候重？');
          else { await S.say('polnareff', '……里面有东西在动？——不，是压缩机的声音吧。'); F().fridgeKnock = true; }
        },
        async (S, h, p) => { reg('fridge'); await S.say('polnareff', '剑尖敲了敲冰箱门。……咚。里面是实的，不像是空的。'); F().fridgeKnock = true; }, { ly: 120 }),
      hot('bed', HD('bed')[0], HD('bed')[1], '床', ['cut'],
        async (S, h, p) => { reg('bed'); await S.say('polnareff', '床挺软。……睡之前先检查一下。床底下，黑漆漆的。'); },
        async (S, h, p) => { reg('bed'); await S.say('polnareff', '剑尖挑起床单……什么都没有。'); }, { ly: 112 }),
      hot('mirror', HD('mirror')[0], HD('mirror')[1], '梳妆镜', [],
        async (S, h, p) => {
          reg('mirror');
          await S.say('polnareff', T.count('c3mirror') === 1 ? '……我真帅。' : '……嗯？镜子里，床底下好像有什么东西反了一下光。');
        }, null, { ly: 70 }),
      hot('window', HD('window')[0], HD('window')[1], '窗户', [],
        async (S, h, p) => { reg('window'); await S.say('polnareff', '新加坡的夜景，Magnifique！……雪莉要是能看到就好了。'); }, null, { ly: 80 }),
      hot('luggage', HD('luggage')[0], HD('luggage')[1], '旅行箱', [],
        async (S, h, p) => {
          reg('luggage');
          await S.say('polnareff', '旅行箱的最底下，压着一张妹妹的照片。');
          await S.say('polnareff', '……雪莉。再等等。哥哥一定会找到那个两只右手的男人。');
        }, null, { ly: 120 }),
      hot('door', HD('door')[0], HD('door')[1], '房门', [],
        async (S, h, p) => { reg('door'); await S.say('polnareff', '门链挂好了。这下谁也进不来。'); }, null, { ly: 100 }),
    ];
  }
  async function hotelIntro(S) {
    const [dx, dy] = HD('door');
    const pol = place(S, 'polnareff', dx + 8, dy + 6, 1);
    S.sfx('door', { vol: .6 });
    await S.wait(.4);
    if (pol) await S.walk(pol, dx + 70, dy + 8, { speed: 70 });
    await lines(S, [['polnareff', '单人间，万岁。……没有乔斯达先生的呼噜，没有阿布德尔念经。'], ['polnareff', '不过——小心驶得万年船。睡觉之前，先把房间检查一遍。']]);
  }
  async function devoAppear(S) {
    calmStands(); S.hint(null);
    const pol = S.player, [fx, fy] = HD('fridge');
    snd('fridge', 'door', { vol: .9 }, { vol: .6, rate: .7 });
    S.state('fridge', 1);
    S.flash(.06, .2, '#d8f0ff');
    pol.facing = fx > pol.x ? 1 : -1;
    S.emote(pol, '！', .8);
    await lines(S, [['polnareff', '……冰箱门，自己开了？']]);
    S.music('ominous');
    const dv = S.spawn('devo', fx, fy + 6, { id: 'devo_cut', team: 'npc', name: '被诅咒的迪波' });
    dv.facing = -1; dv.alpha = 0; dv.standReact = false; dv.talk = null;
    S.sfx('drain', { vol: .5, rate: .6 });
    await S.animate(.8, k => { dv.alpha = k; dv.x = fx - k * 18; });
    S.pose(dv, 'idle');
    await sayDevo(S, '嘿……嘿嘿嘿。想不到我会在冰箱里吧。');
    await lines(S, [['polnareff', '你、你是怎么塞进去的！？', 'shock']]);
    await sayDevo(S, '我是被诅咒的迪波。DIO 出了一大笔钱，买你们的命。');
    await sayDevo(S, '来，打我啊。……你越恨我，我的恶魔就越强。');
    await lines(S, [['polnareff', '……这家伙脑子不正常。'], ['polnareff', '不过——既然你这么想挨打，就让你尝尝银色战车的剑！']]);
    S.nameCard('devo');
    await S.wait(1.2);
    S.standCard('ebonydevil');
    await S.wait(1.0);
    dv.remove = true;
  }
  async function devoAfter(S) {
    calmStands();
    await S.title('saiki');
    await S.say(null, '诅咒的迪波倒在地上，再也没有醒来。');
    // 大家冲进来
    const [dx, dy] = HD('door');
    S.party(crew, { leader: 'polnareff' });
    S.sfx('door', { vol: .9, rate: .8 }); S.shake(2, .2);
    const pol = place(S, 'polnareff', 150, 164, -1);
    for (const [cid, ox, oy] of [['avdol', 34, 2], ['joseph', 14, 10], ['jotaro', 54, 8], ['kakyoin', 4, 0]]) {
      const a = place(S, cid, dx - 10, dy + oy, 1);
      if (a) S.walk(a, dx + ox + 20, dy + oy, { speed: 150, anim: 'run' }).catch(G.cancelIgnore);
    }
    await S.wait(.6);
    await lines(S, [['avdol', '波鲁纳雷夫！刚才那声音是——'], ['joseph', 'OH MY GOD……这房间是被台风刮过吗？', 'shock']]);
    if (pol) S.pose(pol, 'kneel');
    await lines(S, [['polnareff', '……没事。一个拿剃刀的娃娃而已。'], ['kakyoin', '被子都被割成这样了。……今晚你睡哪？'], ['polnareff', '……'],
      ['polnareff', '我一个人就够了。……下次也是。']]);
    const av = S.actor('avdol'); if (av) S.emote(av, '……', 1);
    await lines(S, [['avdol', '……唉。'], ['joseph', '迪波就交给 SPW 吧。明天中午的火车，都早点睡。'], ['kakyoin', '那我明天一早先去买点樱桃。路上吃。']]);
    if (pol) S.unpose(pol);
    await S.fadeOut(.6);
  }

  // ================================================================ 第二天早上（sg_street_ch3，tint morning）：“花京院”很怪
  // 跟着假花京院走的调查点：U 看他（阿布德尔 生命探测、承太郎 细节、乔瑟夫 念写），E 跟他说话。现场那一份每帧挪到他身上
  function fakeHot() {
    return hot('fake_kak', 0, 0, '花京院', ['life', 'detail', 'nensha', 'cut'],
      async S => sayFake(S, pick('c3fakeE', ['……早。', '那个小鬼，烦死了。', '……干嘛。'])),
      async (S, h, p) => {
        if (p.cid === 'avdol') { await S.say('avdol', '他的生命之火……是两层的。外面裹着的那一层，不是他的。'); clue(S, 'life'); }
        else if (p.cid === 'jotaro') { await S.say('jotaro', '……他的影子，边缘在蠕动。'); clue(S, 'shadow'); }
        else if (p.cid === 'joseph') { await S.say('joseph', '念写出来的照片上……花京院的脸，是一团黄色的东西！？'); clue(S, 'photo'); }
        else await S.say('polnareff', '……拿剑尖戳他一下？算了，会被他骂死。');
      }, { r: 16, ry: 14, ly: 40 });
  }
  function followFakeHot() {
    T.tick(() => {
      const st = G.world.stage, k = st && st.actors.find(a => a.cid === 'kakyoin' && !a.remove), h = st && st.hotspots.find(x => x.id === 'fake_kak');
      if (!k || !h) return !h;
      h.x = k.x; h.y = k.y; h.hidden = !k.visible;
      return false;
    });
  }
  function setupMorning() {
    setupArrival();
    G.STAGES.sg_street_ch3.hotspots.push(fakeHot());
  }
  async function morningIntro(S) {
    calmStands();
    const [hx, hy] = SS('hotel_door');
    const pos = [['jotaro', -20, 6], ['joseph', -40, 2], ['avdol', -58, 8], ['polnareff', 4, 10]];
    for (const [cid, ox, oy] of pos) place(S, cid, hx + ox, hy + oy, 1);
    anneAt(S, hx - 76, hy + 10, { facing: 1 });
    const fk = place(S, 'kakyoin', hx + 120, hy + 8, -1);
    if (fk) { await S.walk(fk, hx + 30, hy + 8, { speed: 60 }); fk.facing = -1; }
    await sayFake(S, '……早。');
    await lines(S, [['polnareff', '花京院！樱桃呢？不是一大早去买了吗？']]);
    await sayFake(S, '……吃完了。');
    await lines(S, [['polnareff', '一个人全吃了！？', 'shock'], ['joseph', '我和阿布德尔去火车站买票，波鲁纳雷夫去 SPW 那边拿钱。中午火车站见。']]);
    await sayAnne(S, '我想坐缆车！昨天在山上看见的那个！');
    await sayFake(S, '……我带她去。承太郎，你也一起。');
    const jo = S.actor('jotaro'); if (jo) S.emote(jo, '……', 1.2);
    await lines(S, [['jotaro', '……'], ['joseph', '缆车站在这条街的尽头。一起走过去，到了再分头。']]);
  }
  async function cableIntro(S) {
    calmStands(); S.hint(null);
    const [cx, cy] = SS('cable_station');
    await lines(S, [['joseph', '那我们去买票了。中午火车站见。'], ['polnareff', '花京院，别把人家小姑娘弄哭了。']]);
    await sayFake(S, '……少啰嗦。');
    for (const cid of ['joseph', 'avdol', 'polnareff']) { const a = S.actor(cid); if (a) { a.follow = null; S.walk(a, a.x - 160, a.y, { speed: 90 }).catch(G.cancelIgnore); } }
    await S.wait(1.2);
    await S.fadeOut(.5);
    // 外景：缆车离开山上的车站，挂在海面上
    await S.setStage('cableview_ch3', { x: 160, y: 160, fade: false, music: 'tension' });
    for (const a of G.world.stage.actors) a.visible = false;
    amb(S, 'cable_loop', 'wind_loop', .35);
    await S.fadeIn(.5);
    S.sfx('wind', { vol: .4 });
    await S.wait(1.8);
    await S.fadeOut(.4);
  }
  async function cableReveal(S) {
    S.party(['jotaro'], { leader: 'jotaro' });
    await S.setStage('cable_ch3', { x: 150, y: 160, fade: false, music: 'tension' });
    amb(S, 'cable_loop', 'wind_loop', .3);
    const [lx, ly] = CC('win_l'), [rx, ry] = CC('win_r');
    const jo = place(S, 'jotaro', 150, 160, 1);
    const anne = anneAt(S, lx + 6, ly + 6, { facing: -1 });
    const fk = S.spawn('kakyoin', rx - 40, 158, { id: 'fakeK', team: 'npc', name: '花京院' });
    fk.facing = -1; fk.standReact = false; fk.talk = null;
    if (hasAnim('kakyoin', 'fake_idle')) fk.skin = 'fake';
    await S.fadeIn(.5);
    await sayAnne(S, '好高！海是绿色的！');
    await sayFake(S, '……小鬼，别趴在窗户上。掉下去我可不管。');
    await sayAnne(S, '你凶什么！昨天你还给我讲笑话呢。……你今天好奇怪。');
    S.emote(fk, '……', 1);
    await sayFake(S, '……');
    if (jo) { jo.facing = 1; S.emote(jo, '……', 1); }
    for (;;) {
      const n = await S.choice(['指认他', '……再看看'], '承太郎要怎么做？');
      if (n === 0) break;
      await sayFake(S, '……看什么看。');
    }
    await lines(S, [['jotaro', '……你不是花京院。']]);
    const TELL = { cherry: '花京院吃樱桃，不会连核一起嚼碎咽下去。', trash: '路边的垃圾桶，被一滩黄色的东西吞掉了。', vendor: '卖樱桃的说，你连樱桃是什么都要问。',
      cat: '安妮说，你在后巷踢了一只猫。', life: '阿布德尔说，你的生命之火有两层。', shadow: '你的影子，边缘一直在动。', photo: '老头子念写出来的照片上，你的脸是一团黄色的东西。' };
    const got = Object.keys(F().c3Clues || {}).filter(k => TELL[k]).slice(0, 2);
    for (const k of got) await S.say('jotaro', TELL[k]);
    await lines(S, [['jotaro', '……还有。花京院叫我，从来不会用那种语气。']]);
    await sayFake(S, '……哈。');
    await sayFake(S, '哈哈哈哈哈！');
    // 脸像融化的蜡一样剥落 → 拉巴索
    S.music('tension');
    snd('slime', 'drain', { vol: .9 }, { rate: .6 }); S.shake(2, .6);
    S.fx('tendrils', { pts: [[[fk.x - 6, fk.y - 6], [fk.x - 30, fk.y - 50]], [[fk.x, fk.y - 4], [fk.x + 18, fk.y - 56]], [[fk.x + 6, fk.y - 6], [fk.x + 30, fk.y - 20]]], colour: '#ffee40', wiggle: 2 });
    const rs = S.spawn('rubbersoul', fk.x, fk.y, { id: 'rs_cut', team: 'npc', name: '拉巴索' });
    rs.facing = -1; rs.alpha = 0; rs.standReact = false; rs.talk = null; armorOn(rs);
    await S.animate(1.0, k => { fk.alpha = 1 - k; rs.alpha = k; if (Math.floor(k * 12) % 3 === 0) S.fx('burst', { x: fk.x, y: fk.y - 24, n: 3, speed: 30, colours: ['#ffe040', '#c8a018'] }); });
    fk.remove = true;
    if (!hasAnim('rubbersoul', 'armor_idle')) { rs.outline = null; }
    await sayRS(S, '被看穿了啊。……没错，我是拉巴索。真正的花京院，这会儿正在酒店的储物间里睡大觉呢。');
    if (anne) { S.emote(anne, '！！', .8); S.sfx('sting_shock', { vol: .6 }); await S.walk(anne, CC('anne_corner')[0], CC('anne_corner')[1], { speed: 130, anim: 'run' }); anne.facing = -1; }
    armorOn(rs);
    await sayRS(S, '我的「黄色节制」，可以变成任何人，也可以吃掉任何东西。');
    await sayRS(S, '你的拳头……只会被我吃掉！');
    await lines(S, [['jotaro', '……废话真多。']]);
    S.nameCard('rubbersoul');
    await S.wait(1.2);
    S.standCard('yellowtemperance');
    await S.wait(1.0);
    rs.remove = true;
    if (anne) anne.remove = true;
  }

  // ---------------------------------------------------------------- 水里的人：水线以上照常画，以下只画淡影（第2章同一个画法）
  function swimmer(id, cid, o) {
    return Object.assign({ type: 'custom', id, x: 0, y: 0, depth: 150, anim: 'idle', frame: 0, flip: false, wl: 20, under: 0.28, alpha: 1, hidden: false, foam: 9,
      draw(g, sx, sy, t) {
        if (this.hidden || !G.atlas) return;
        const A = G.atlas(cid);
        if (!A || !A.draw) return;
        const bob = Math.round(Math.sin((t || 0) * 3 + this.x * 0.05));
        const x = sx, y = sy + bob, wly = y - Math.round(this.wl);
        const ga = g.globalAlpha;
        g.save(); g.beginPath(); g.rect(x - 70, wly, 140, 80); g.clip();
        g.globalAlpha = ga * this.alpha * this.under;
        A.draw(g, this.anim, this.frame, x, y, { flip: this.flip });
        g.restore();
        g.save(); g.beginPath(); g.rect(x - 70, wly - 90, 140, 90); g.clip();
        g.globalAlpha = ga * this.alpha;
        A.draw(g, this.anim, this.frame, x, y, { flip: this.flip });
        g.restore();
        g.globalAlpha = ga * this.alpha * 0.9;
        g.fillStyle = '#e6f4ff';
        const half = this.foam, ft = Math.floor((t || 0) * 6);
        for (let i = -half; i <= half; i++) if ((i + ft) % 3) g.fillRect(x + i, wly + (Math.abs(i) > half - 3 ? 1 : 0), 1, 1);
        g.globalAlpha = ga;
      } }, o);
  }
  // 海面（surface_ch3，sea_day）：拉巴索求饶，供出荷尔·荷斯和 J·凯尔 → 饶 / 不饶都挨一拳
  async function surfaceScene(S) {
    calmStands();
    await S.fadeOut(.4);
    S.party(['jotaro'], { leader: 'jotaro' });
    await S.setStage('surface_ch3', { x: 210, y: 170, fade: false, music: null });
    amb(S, 'sea_loop', 'wind_loop', .3);
    const jo = place(S, 'jotaro', 210, 170, -1);
    if (jo) S.pose(jo, 'float');
    const rs = swimmer('rs_swim', 'rubbersoul', { x: 120, y: 172, wl: 15, under: .14, anim: hasAnim('rubbersoul', 'beg') ? 'beg' : 'hurt', depth: 168, flip: false });
    addLive(rs);
    await S.fadeIn(.5);
    await S.say('rubbersoul', '等、等一下！我投降！我什么都说！', { name: '拉巴索' });
    await lines(S, [['jotaro', '……先把你知道的说出来。']]);
    await S.say('rubbersoul', '接下来来找你们的，是荷尔·荷斯，还有 J·凯尔！', { name: '拉巴索' });
    await S.say('rubbersoul', 'J·凯尔那家伙……两只手，都是右手！', { name: '拉巴索' });
    await lines(S, [['jotaro', '……两只右手。']]);
    await S.say('rubbersoul', '我全说了！饶了我吧！我再也不敢了！', { name: '拉巴索' });
    const n = await S.choice(['饶他', '不饶'], '拉巴索在水里求饶');
    if (n === 0) {
      await lines(S, [['jotaro', '……好。']]);
      await S.say('rubbersoul', '真、真的？', { name: '拉巴索' });
      await lines(S, [['jotaro', '——这一拳，就当是饶过你了。']]);
    } else {
      await lines(S, [['jotaro', '你吞了路边的垃圾桶，踢了猫，把花京院关进储物间，还装成他的样子吓唬一个小姑娘。'], ['jotaro', '……我不打算饶你。']]);
    }
    // 欧拉欧拉：一拳把他打出水面
    if (jo) { S.summon(jo, { dur: .12, rise: 4 }); S.standAct(jo, 'rush', { dx: -24, dur: .9 }); }
    S.sfx('ora_rush', { vol: .8 }); S.sfxText('オラオラ', { x: 300, y: 200 });
    for (let i = 0; i < 6; i++) { S.fx('hit_spark', { x: rs.x + 4 + (i % 3) * 3, y: 140 - (i % 2) * 8, size: 12 }); S.shake(2, .1); await S.wait(.12); }
    S.impact(['invert', 'purple']); S.sfx('punch_heavy'); S.sfxText('ORA!!!', { x: Math.round(rs.x * 2), y: 240 });
    await S.animate(.7, k => { rs.x = 120 - k * 70; rs.wl = 15 + Math.sin(k * Math.PI) * 50; rs.under = .14 + .8 * Math.sin(k * Math.PI); });
    rs.hidden = true;
    S.sfx('splash'); S.fx('water_splash', { x: 40, y: 150, size: .9 });
    if (jo) S.recall(jo);
    await S.title('saiki');
    await lines(S, [['jotaro', '……呀嘞呀嘞daze。']]);
    S.sfxText('呀嘞呀嘞daze', jo || 'player');
    await S.narrate('SPW 的快艇把承太郎捞了上来。真正的花京院，在酒店的储物间里被找到了。', { pos: 'center' });
    await S.fadeOut(.5);
    dropLive('rs_swim');
    if (jo) S.unpose(jo);
  }
  // 去印度的火车（train_ch3）：两只右手 → 真花京院 rerorero → TBC
  async function trainScene(S) {
    S.party(crew, { leader: 'jotaro' });
    await S.setStage('train_ch3', { x: 120, y: 166, fade: false, music: 'travel' });
    amb(S, 'train_loop', 'wind_loop', .3);
    const pos = [['joseph', 52, 166, 1], ['avdol', 84, 160, 1], ['jotaro', 122, 168, 1], ['polnareff', 176, 164, -1], ['kakyoin', 246, 162, -1]];
    for (const [cid, x, y, f] of pos) place(S, cid, x, y, f);
    anneAt(S, 214, 170, { facing: -1 });
    await S.fadeIn(.6);
    await S.narrate('当天中午，一行人登上了北上去印度的火车。', { pos: 'center' });
    await lines(S, [['joseph', '花京院，伤怎么样？'], ['kakyoin', '一大早出门买樱桃，被人从背后打晕……醒过来就在酒店的储物间里了。'],
      ['kakyoin', '……幸亏你们认出了他。'], ['polnareff', '承太郎，那个黏液混蛋都说了什么？']]);
    await lines(S, [['jotaro', '下一个是荷尔·荷斯。还有一个，叫 J·凯尔。'], ['jotaro', '……J·凯尔的两只手，都是右手。']]);
    const pol = S.actor('polnareff');
    S.sfx('sting_shock');
    await T.closeup4(S, { cid: 'polnareff', expr: 'shock', dur: 1.2 });
    await lines(S, [['polnareff', '……两只右手？', 'shock'], ['polnareff', '……是他。杀了雪莉的，就是那个两只右手的男人。']]);
    if (pol) { pol.facing = 1; S.emote(pol, '……', 1.4); }
    await lines(S, [['avdol', '波鲁纳雷夫……'], ['polnareff', '……没什么。我去窗边吹吹风。']]);
    await S.wait(.4);
    await lines(S, [['joseph', '对了，安妮。SPW 联系上你爸爸了。他人在外地，一时回不来。'], ['joseph', '到了印度，我们送你上回家的飞机。']]);
    await sayAnne(S, '……哼。那我就再陪你们一段。');
    await S.wait(.5);
    const kak = S.actor('kakyoin');
    if (kak) S.pose(kak, 'cherry');
    S.sfx('rero');
    await lines(S, [['kakyoin', 'rerorero……']]);
    S.sfx('rero', { rate: 1.1 });
    await lines(S, [['polnareff', '……你能不能别这样吃樱桃。'], ['kakyoin', '这是我的自由。']]);
    await sayAnne(S, '……噗。');
    await lines(S, [['jotaro', '……呀嘞呀嘞daze。']]);
    if (kak) S.unpose(kak);
    await S.narrate('火车一路向北。下一站——印度。', { pos: 'center' });
    await J.end(S, 'ch3_tbc');
  }

  // ================================================================ 章节流程
  G.STORY.ch3 = async S => {
    T.resetCounters();
    for (const k of ['sgHotel', 'hotelClues', 'fridgeKnock', 'c3Morning', 'c3Clues', 'toCable', 'yellowClues', 'yellowCaught']) delete F()[k];
    // 安妮从第2章跟过来（从“选择章节”直接进第3章也一样）
    Object.assign(F(), { anneJoined: true, anneNamed: true, anneLeft: false });
    S.party(crew, { leader: 'jotaro' });
    await S.chapterCard('ch3');
    // 到达：骑楼街（下午）
    setupArrival();
    await S.setStage('sg_street_ch3', { x: SS('arrive')[0] + 30, y: 164, music: 'daily' });
    S.state('morning', 0);
    amb(S, 'city_loop', 'crowd_loop', .3);
    await S.run(arrivalIntro);
    follow(); anneFollow(S);
    memberTalkArrival();
    S.hint('往右走，去白色的酒店（路上可以 E 搭话、调查）。', 10);
    T.goal(S, { x: SS('hotel_door')[0], y: SS('hotel_door')[1], h: 60, label: '酒店', delay: 45, every: 25, done: () => !!F().sgHotel, text: '白色的那栋就是酒店。' });
    await S.until(() => F().sgHotel && !S.busy);
    await S.run(checkIn);
    // 夜里：单人间，只有波鲁纳雷夫
    setupHotel();
    S.party(['polnareff'], { leader: 'polnareff' });
    await S.setStage('sg_hotel_ch3', { x: HD('door')[0] + 20, y: 164, fade: false, music: 'ominous' });
    amb(S, 'fan_loop', 'wind_loop', .25);
    await S.fadeIn(.5);
    await S.run(hotelIntro);
    S.hint('睡前把房间检查一遍（E 调查，U 剑尖挑开看）。', 10);
    T.goal(S, { x: HD('fridge')[0], y: HD('fridge')[1], h: 46, label: '冰箱', delay: 45, every: 25, when: () => Object.keys(F().hotelClues || {}).length >= 2, done: () => !!F().fridgeKnock, text: '那台冰箱……好像有点不对劲。' });
    const t0 = G.clk.world;
    await S.until(() => !S.busy && G.world.free && (Object.keys(F().hotelClues || {}).length >= 3 || F().fridgeKnock || G.clk.world - t0 > 80));
    await S.run(async s => {
      await devoAppear(s);
      await s.fight(G.BOSS25.devo());
      await devoAfter(s);
    });
    // 第 6 天早上：骑楼街（晨光），“花京院”很怪
    F().c3Morning = true;
    setupMorning();
    S.party(crew, { leader: 'jotaro' });
    G.party.setLeadable('kakyoin', false, { look: 'gray', msg: '……我今天不想走在前面。' });
    await S.setStage('sg_street_ch3', { x: SS('hotel_door')[0] - 20, y: 164, fade: false, music: 'daily' });
    S.state('morning', 1);
    amb(S, 'city_loop', 'crowd_loop', .25);
    { const k = S.actor('kakyoin'); if (k && hasAnim('kakyoin', 'fake_idle')) k.skin = 'fake'; }
    await S.fadeIn(.5);
    await S.narrate('第六天，早上。', { pos: 'center' });
    await S.run(morningIntro);
    follow(); anneFollow(S); followFakeHot();
    memberTalkMorning();
    S.hint('“花京院”很怪：找出两处破绽（樱桃摊、路边、安妮……也可以换人用 U 看他）。', 14);
    T.goal(S, { x: SS('cherry_stall')[0], y: SS('cherry_stall')[1], h: 50, label: '樱桃摊', delay: 35, every: 25, done: () => hasClue('cherry'), text: '花京院最爱吃樱桃。……去樱桃摊看看他怎么吃。' });
    T.goal(S, { x: SS('cable_station')[0], y: SS('cable_station')[1], h: 60, label: '缆车站', delay: 5, every: 25, when: () => clueN() >= 2, done: () => !!F().toCable, text: '破绽够了。去缆车站。' });
    const t1 = G.clk.world;
    let helped = false;
    await S.until(() => {
      if (F().toCable && !S.busy) return true;
      // 卡住太久（100 s）：替玩家看出两处破绽——换阿布德尔看他的生命之火、换承太郎看他的影子
      if (!helped && !S.busy && G.world.free && G.clk.world - t1 > 100 && clueN() < 2) {
        helped = true;
        S.run(async s => {
          const fk = s.actor('kakyoin');
          for (const [cid, k, text] of [['avdol', 'life', '他的生命之火……是两层的。外面裹着的那一层，不是他的。'], ['jotaro', 'shadow', '……他的影子，边缘在蠕动。']]) {
            if (hasClue(k) || clueN() >= 2) continue;
            s.setLeader(cid, { force: true });
            if (fk) await G.LOOK[cid].run(s, s.player, { x: fk.x, y: fk.y - 30 });
            await s.say(cid, text); clue(s, k);
          }
        }).catch(G.cancelIgnore);
      }
      return false;
    });
    await S.run(async s => {
      await cableIntro(s);
      await cableReveal(s);
      await s.fight(G.BOSS25.yellow());
      await surfaceScene(s);
      G.party.setLeadable('kakyoin', true);
      await trainScene(s);
    });
  };

  // 开发调参入口（只给 tools\dev\full\dev_fight.py 用，正常游戏不调用）：直接开打这一章的某一战，战斗配置和正式剧情是同一份。
  //   验收一律跑整章（test_mid_early.py），这个入口的结果不当通关证据
  G.DEV = G.DEV || {};
  G.DEV.ch3Devo = async S => { setupHotel(); S.party(['polnareff'], { leader: 'polnareff' }); await S.setStage('sg_hotel_ch3', { x: 145, y: 164, music: 'tension' }); await S.run(async s => { await s.fight(G.BOSS25.devo()); }); };
  G.DEV.ch3Yellow = async S => { S.party(['jotaro'], { leader: 'jotaro' }); await S.setStage('cable_ch3', { x: 125, y: 160, music: 'tension' }); await S.run(async s => { await s.fight(G.BOSS25.yellow()); }); };
})();
