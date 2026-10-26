// 第9章　尼罗河 / 刀、磁铁与影子（规划 §6.8；原著 193–210 话，游戏内第 32–35 天）
//   2026-10-20 按游玩脚本 ch9_尼罗河.md 整章重写（实施文档 06_第9章.md）。初版的机关全部沿用，写法照第5章：
//   记招（memory + moves_ch06_09.js 的 onHitBy）、射出剑身、卡恩加速、夹刀（AN_THRUST_P.onParried）、
//   磁化 / 相吸 / 废铁 / 插座 / 火车 / 合击、躲猫猫 + 伏击（KIDPOL_AMBUSH）、S.setPlayer 换小孩 + finally 还原。
//   这一版补：自由走动（神殿 / 河岸 / 卢克索）、象形文字问答、打水漂、理发摊、扔刀进河、碎片小孩、
//   两段场地（街道 → 铁路）、躲猫猫的家具框 / 帽子尖 / 影子、求饶选项、结尾恢复五人 + 花京院灰；
//   所有写死的 x 都改成背景锚点（bgA），背景挪了位置剧情跟着走。
//
//   流程：篇章卡 → 航线（第 32 天）→ 科翁坡神殿（自由走动 + 问答）→ 恰卡（第 18 战段 1）→ 扔刀进河 → 航线（第 33 天）
//   → 河岸（自由走动 + 打水漂）→ 理发摊（第 18 战段 2）→ 被附身的波鲁纳雷夫（段 3）→ 碎片小孩 / 伊奇 → 航线（第 34 天）
//   → 卢克索（自由走动）→ 插座 → 第 19 战（街道 → 铁路）→ 夹扁 → 影子（第 20 战段 1 躲猫猫）→ 小学生承太郎（段 2）
//   → 了、了不起哟 → 航线（第 35 天）→ TBC
//
//   台词照脚本逐字（脚本里的「（说出正确答案）」由代码填正确答案）；克制处理照脚本：斧头只砍家具、砍到人只白闪 +「咚」+ 哭声，
//   碎片小孩被绊倒只演喜剧，夹刀只扣血不画伤口，恰卡 / 卡恩 / 玛丽亚 / 阿莱西被打只演倒地或飞出画面。
'use strict';
(function () {
  const G = window.G, M = G.MID, T = G.TPL, W = G.world, I = G.input, J = G.J25, px = G.px, F = () => G.flags, X = G.EXTRA;
  // 关卡工厂登记表由各章各自初始化；trial_stages.js 只按 id 引用，避免加载顺序问题
  G.TRIAL_SRC = G.TRIAL_SRC || {};
  // 剧情路径的 o：wrap 是恒等函数，trial 为假；抽配置时用它区分「要不要夹带剧情演出」
  const STORY = { trial: false, wrap: s => s };
  const crew = ['jotaro', 'joseph', 'avdol', 'polnareff', 'iggy'];
  const lines = async (S, rows) => { for (const [who, text, expr] of rows) await S.say(who, text, expr ? { expr } : {}); };
  const pick = (key, arr) => arr[(T.count(key) - 1) % arr.length];
  const sayBy = (S, p, map) => S.say(p.cid, T.by(p, map));
  // 音效：名字照素材总表；本章新合成的还没进数据包时用现成的顶上（直接播不存在的名字会记 missingSfx）
  const hasSnd = n => !!(G.audio && G.audio.has && G.audio.has(n));
  const snd = (name, alt, o = {}) => { if (hasSnd(name)) G.audio.sfx(name, o); else if (alt) G.audio.sfx(alt, o); };
  const amb = (S, name, alt, vol) => { if (hasSnd(name)) S.ambient(name, vol); else if (alt) S.ambient(alt, vol * .6); };
  const calmStands = () => { for (const a of (G.party && G.party.members) || []) if (a.stand && a.stand.visible && a.stand.mode !== 'recall') a.stand.recall({ sfx: false }); };
  const follow = () => { if (G.party && G.party.rebuildFollow) G.party.rebuildFollow(); };
  // 放水（脚本“受伤 ×0.6”）：引擎的 assist 已经乘了 CFG.assistMul（0.7），这里把剩下的一档折算进 dmgScale
  const assistScale = (c, want = .6) => { if (c && c.assist) c.spec.dmgScale = want / G.combat.CFG.assistMul; };
  // 输了的台词（脚本给了具体的话）：引擎的通用失败（HP 0）不带文字，这里把无参的 c.fail 补上这一句
  function failLine(c, text) { if (!c || c.data.failLine) return; const f0 = c.fail.bind(c); c.data.failLine = text; c.fail = t => f0(t || text); }

  // ---------------------------------------------------------------- 背景锚点（没有就用素材总表里的默认值）
  const bgA = (bg, k, d) => { const b = G.D && G.D.bg && G.D.bg[bg]; const v = b && b.anchors ? b.anchors[k] : null; return v != null ? v : d; };
  const TPd = { arrive: [40, 164], guide: [96, 160], colonnade: [180, 120], hieroglyph: [250, 150], tourists: [320, 162], sword_rack: [410, 152],
    statue: [500, 140], statue_base: [506, 162], sanctum: [585, 156], nile_view: [612, 128], exit: [626, 162],
    gods: { anubis: [251, 81], horus: [271, 81], sobek: [291, 81] } };
  const NBd = { arrive: [40, 164], fisher: [130, 162], river: [220, 140], skip_spot: [190, 166], boat: [200, 150], nets: [262, 150],
    barber_chair: [330, 158], barber: [356, 160], mirror: [330, 112], tea: [470, 156], reeds: [560, 160], felucca: [520, 120], exit: [626, 162],
    skip_line: [[220, 140], [238, 140], [256, 140], [274, 140], [292, 140], [310, 140], [328, 140]], water_y: 84, embankment: 144 };
  const LTd = { arrive: [40, 164], socket: [210, 140], socket_stand: [212, 162], mariah: [260, 160], cafe: [400, 152], cafe_owner: [420, 158],
    scaffold: [560, 120], washer: [560, 162], alley: [700, 156], station_road: [930, 162], house_door: [640, 146], sugar: [434, 152], sun_dir: -1 };
  const ERd = { platform: [90, 156], tracks: [320, 168], rail_band: [0, 164, 640, 172], signal: [580, 140], bench: [60, 152], platform_edge: 158 };
  const LHd = { arrive: [40, 166], door: [320, 156], lamp: [300, 96], floor_back: 146,
    hide_curtain: [58, 156], hide_curtain_box: [42, 40, 76, 146], hide_wardrobe: [155, 156], hide_wardrobe_box: [136, 76, 174, 146],
    hide_aquarium: [249, 156], hide_aquarium_box: [224, 82, 274, 146], hide_bed: [418, 160], hide_bed_box: [388, 104, 450, 146],
    hide_crate: [506, 160], hide_crate_box: [490, 116, 524, 146], hide_cupboard: [570, 156], hide_cupboard_box: [552, 86, 590, 146] };
  const TP = k => bgA('egypt_temple', k, TPd[k]);
  const NB = k => bgA('nile_bank', k, NBd[k]);
  const LT = k => bgA('luxor_town', k, LTd[k]);
  const RP = k => bgA('egypt_rail', k, ERd[k]);
  const LH = k => bgA('luxor_house', k, LHd[k]);
  const footY = (id, y) => { const st = G.STAGES[id]; return G.clamp(y, st.yMin + 2, st.yMax - 2); };
  // 战斗里画的像素层（影子 / 铁轨闪红）：重试会再跑一次 init，M.pixel 的 _midFight 是同一个 id、clean() 不会收掉，
  //   不先去重就会一层层叠上去（而且旧那层的闭包还指着上一场战斗对象）。同 id 的先摘掉再挂。
  const pixelOnce = (id, draw) => {
    const st = G.world.stage;
    st.props = (st.props || []).filter(p => p.id !== id);
    return M.pixel(id, draw);
  };

  function place(S, cid, x, y = 164, facing = 1) {
    const a = S.actor(cid); if (!a) return null;
    a.visible = true; a.follow = null; a.x = x; a.y = y; a.facing = facing; a.alpha = 1; a.scale = 1; a.z = 0; S.unpose(a);
    delete a.mem.partyHidden;
    return a;
  }
  function party(S, leader = 'jotaro') { S.party(crew, { leader }); for (const a of G.party.members) { a.scale = 1; a.alpha = 1; a.hold = false; a.visible = true; a.speed = kidSafeSpeed(a); delete a.mem.partyHidden; } }
  // 换小孩期间把大人的移动速度留在 kit 里（重试 / 换回大人时不至于变成 0）
  const kidSafeSpeed = a => (a.kit && a.kit.speed) || a.speed || 60;
  // 自由走动：过场里写旗标，这里等它（自由走动必须在 S.run 外面跑，S.run 里 S.busy 一直为真会挡住 E / U）
  async function explore(S, flag, hint, dur, goal) {
    S.free(true);
    if (goal) T.goal(S, Object.assign({ done: () => !!F()[flag] }, goal));
    S.hint(hint, dur == null ? 10 : dur);
    await S.until(() => !!F()[flag] && !S.busy);
    S.free(false);
  }
  // 伊奇不说话：只有「汪」和动作描写
  const iggySay = async (S, text) => { S.sfx('dog_bark'); await S.say(null, text); };

  // ---------------------------------------------------------------- 纪念品（story\extras.js；找到的存在 jojo-extras）
  X.souvenir({ id: 'ch9_scarab', chapter: 'ch9', name: '圣甲虫护身符',
    desc: '科翁坡神殿雕像底座里找到的。古埃及人相信，它能推着太阳升起来。', hint: '科翁坡神殿，残缺雕像的底座' });
  // 扁石的说明要写“最好的一次跳了几下”（脚本纪念品表），登记时还不知道成绩，用 getter 现读旗标
  X.souvenir({ id: 'ch9_flat_stone', chapter: 'ch9', name: '尼罗河的扁石',
    get desc() { return '打水漂用的扁石头。最好的一次，跳了 ' + (F().ch9Skip || 0) + ' 下。'; },
    hint: '河岸打水漂，跳到 5 下以上' });
  X.souvenir({ id: 'ch9_sugar', chapter: 'ch9', name: '卢克索咖啡馆的方糖',
    desc: '伊奇从桌子底下叼出来的。……它没吃，大概是想留着。', hint: '卢克索的咖啡馆（要鼻子灵的）' });

  // ================================================================ 象形文字问答（9-02，阿布德尔讲解，不挡主线）
  //   三题各三个选项、每次随机排序；测试器读 dbg.ev('quiz', { id, answer })，answer = 正确选项在（洗过牌的）选项里的序号
  const QUIZ = [
    { id: 'ch9_q1', text: '哪一个是死者的守护神？', right: '豺狼头的神', options: ['豺狼头的神', '鹰头的神', '鳄鱼头的神'] },
    { id: 'ch9_q2', text: '这座神殿祭祀的是哪两位神？', right: '索贝克和荷鲁斯', options: ['索贝克和荷鲁斯', '阿努比斯和托特', '拉和奥西里斯'] },
    { id: 'ch9_q3', text: '阿努比斯在审判死者时做什么？', right: '用天平称死者的心脏', options: ['用天平称死者的心脏', '在尼罗河上划船', '守着金字塔的大门'] },
  ];
  async function quiz(S) {
    const av = S.actor('avdol');
    const say = t => S.say('avdol', t, av ? { actor: av } : {});
    if (!F().ch9QuizSeen) {
      F().ch9QuizSeen = true;
      await say('豺狼头的是阿努比斯，守护死者的神。鹰头的是荷鲁斯，鳄鱼头的是索贝克——这座神殿祭祀的就是他们两个。阿努比斯还会在审判的时候，用天平称量死者的心脏。');
    }
    await say('……我来考考你们？');
    const go = await S.choice(['好', '下次吧'], '象形文字');
    if (go !== 0) { await say('随时可以。'); return; }
    let all = true;
    for (const q of QUIZ) {
      const opts = q.options.slice();
      // 洗牌（每次随机；测试器按 dbg.ev 里的 answer 选对的）
      for (let i = opts.length - 1; i > 0; i--) {
        const j = Math.floor(G.rand(0, i + .999));
        const t = opts[i]; opts[i] = opts[j]; opts[j] = t;
      }
      const answer = opts.indexOf(q.right);
      if (G.dbg && G.dbg.ev) G.dbg.ev('quiz', { id: q.id, answer });
      const i = await S.choice(opts, q.text);
      if (i === answer) {
        const h = TP('hieroglyph');
        S.fx('sparkles', { x: h[0], y: h[1] - 12, n: 5, radius: 10 }, { life: .3 });
        snd('sparkle', 'ding', { vol: .5 });
        await say('没错。');
      } else {
        all = false;
        // 脚本写的是「不对。是——（说出正确答案）。」：括号是舞台指示，这里填正确答案
        await say('不对。是——' + q.right + '。');
      }
    }
    if (all) {
      F().ch9Quiz = true;
      await say('全对！……记住这个名字，阿努比斯。说不定马上就会用上。');
      if (S.player.cid === 'polnareff') await S.say('polnareff', '哼哼，我的记性可是很好的！');
    } else await say('……再来一次也可以。');
  }

  // ================================================================ 9-02 科翁坡神殿（temple_ch9，egypt_temple 640 宽）
  const GUIDE_LINES = ['这里是科翁坡神殿，祭祀鳄鱼神索贝克和鹰神荷鲁斯。', '请不要碰后面的旧刀架。', '以前这里住着一位刀匠……后来，就没人见过他了。'];
  const TOURIST_LINES = ['壁画里的神，手里拿着什么？', '拍照要给小费吗？'];
  function setupTemple(st) {
    const [gx, gy] = TP('guide'), [tx, ty] = TP('tourists');
    st.state = Object.assign({}, st.state);
    st.npcs = [
      T.npc('npc_merchant', 'c9_guide', gx, footY('temple_ch9', gy), { facing: 1, label: '导游', name: '导游', talk: async S => {
        const a = S.actor('c9_guide');
        if (S.player.cid === 'iggy') { S.sfx('dog_bark'); await S.say('npc_merchant', '小狗不能进神殿！……算了，别乱咬东西。', { name: '导游', actor: a }); return; }
        await S.say('npc_merchant', pick('c9guide', GUIDE_LINES), { name: '导游', actor: a });
      } }),
      T.npc('npc_hk_passer_b', 'c9_tourist_a', tx, footY('temple_ch9', ty), { facing: -1, label: '游客', name: '游客', talk: async S => {
        await S.say('npc_hk_passer_b', pick('c9tour', TOURIST_LINES), { name: '游客', actor: S.actor('c9_tourist_a') });
      } }),
      T.npc('npc_townsfolk', 'c9_tourist_b', tx + 22, footY('temple_ch9', ty + 2), { facing: -1, label: '游客', name: '游客', talk: async S => {
        await S.say('npc_townsfolk', pick('c9tour', TOURIST_LINES), { name: '游客', actor: S.actor('c9_tourist_b') });
      } }),
    ];
    const H = (id, k, label, tags, use, look, o = {}) => { const v = TP(k); return J.hot(id, v[0], footY('temple_ch9', v[1]), label, tags, use, look, Object.assign({ ly: v[1] - 26, r: 22 }, o)); };
    st.hotspots = [
      H('c9_colonnade', 'colonnade', '柱廊', [], async (S, h, p) => sayBy(S, p, {
        polnareff: '这么粗的柱子……要几个人才抱得过来？', _: '一排刻满花纹的石柱，顶上是纸莎草形状的柱头。' })),
      H('c9_hieroglyph', 'hieroglyph', '象形文字墙', ['life'],
        async (S, h, p) => {
          const av = G.party.get('avdol');
          if (av && !av.mem.away) { await quiz(S); return; }
          await S.say(p.cid, '墙上刻着豺狼头、鹰头和鳄鱼头的神。');
        },
        async (S, h, p) => { if (p.cid === 'avdol') await S.say('avdol', '……墙后面没有生命。只是很古老的石头。'); }, { r: 26 }),
      H('c9_sword_rack', 'sword_rack', '刀匠的旧刀架', ['nensha', 'scent'],
        async (S, h, p) => sayBy(S, p, { jotaro: '……刀架上少了一把。', _: '木头刀架，上面挂着几把锈刀。' }),
        async (S, h, p) => {
          if (p.cid === 'joseph') {
            await S.photo({ frames: [0, 1, 2], hold: 1.2 });
            await S.say('joseph', '照片里……一个刀匠的背影。他手里拿着一把弯刀。');
          } else if (p.cid === 'iggy') await iggySay(S, '（伊奇对着神殿深处低吼。）');
        }),
      H('c9_statue', 'statue', '残缺的雕像', [], async S => S.say(null, '一尊缺了头的神像。'), null, { ly: TP('statue')[1] - 20 }),
      H('c9_sanctum', 'sanctum', '内殿', ['life'], async S => { F().ch9Sanctum = true; },
        async (S, h, p) => { if (p.cid === 'avdol') await S.say('avdol', '里面……有一个很淡的生命。'); }),
      // 纪念品：雕像底座的缝里卡着圣甲虫护身符（E）
      X.hot('ch9_scarab', TP('statue_base')[0], footY('temple_ch9', TP('statue_base')[1]),
        { label: '雕像的底座', found: S => S.say(null, '雕像底座的缝里，卡着一个小东西') }),
    ];
    st.onLook = async (S, p) => { if (p.cid === 'iggy') await iggySay(S, '（伊奇嗅了嗅，打了个喷嚏。石头的味道。）'); else await S.say(p.cid, '……很安静。'); };
  }
  async function templeIntro(S) {
    calmStands(); party(S);
    await M.scene(S, 'temple_ch9', setupTemple, TP('arrive')[0] + 30, 'jotaro');
    amb(S, 'wind_loop', 'wind', .08);
    S.location('kom_ombo');
    await S.wait(.5);
    await lines(S, [['avdol', '科翁坡神殿。两千多年前，这里同时祭祀着两位神明。'],
      ['polnareff', '观光是不错……可九荣神还剩六个，不知道下一个会从哪里冒出来。'],
      ['joseph', '所以——谁都不许一个人乱跑！听见没有，波鲁纳雷夫？'],
      ['polnareff', '为什么只点我的名？！']]);
    T.memberTalk({
      joseph: async s => s.say('joseph', pick('c9tpJo', ['荷莉在等我们，参观就到这里吧。', '这么热的天，石头里倒是凉快。'])),
      avdol: async s => s.say('avdol', pick('c9tpAv', ['埃及的神明，大多是人身兽头。', '九荣神……是借了神的名字。'])),
      polnareff: async s => s.say('polnareff', pick('c9tpPo', ['这里有厕所吗？', '我就去看一眼，马上回来。'])),
      iggy: async s => {
        const t = pick('c9tpIg', ['（伊奇在柱子的阴影里趴着。）', '……汪。']);
        if (t === '……汪。') await iggySay(s, t); else await s.say(null, t);
      },
      jotaro: async s => s.say('jotaro', pick('c9tpJt', ['……', '……别走散了。'])),
    });
    follow();
  }
  async function templeExplore(S) {
    const sn = TP('sanctum');
    await explore(S, 'ch9Sanctum', '神殿：E 调查、搭话；阿布德尔能讲解墙上的象形文字。', 10,
      { x: sn[0], y: footY('temple_ch9', sn[1] + 4), h: 52, label: '内殿', delay: 60, every: 25, text: '神殿深处还没看过。' });
  }

  // ================================================================ 记招（三段阿努比斯共用，跨段保留）
  //   memory 是整章一个数组：类型名 J1 / J2 / J3 / 连打 / U / 格挡反击（和 prop:anubis_icons 的帧号一一对应）
  const memory = [];
  const MEM_FRAME = { J1: 0, J2: 1, J3: 2, '连打': 3, 'U': 4, '格挡反击': 5 };
  // HUD：3 个 22×22 的格子（画在 UI 层，和 Boss 条同一比例），被挡开的那一格 0.3 s 变金色
  //   位置在右上角（Boss 条 170–470 的右边、y 4–26）：下面 y 44 起的三行说明文字右对齐到 630，
  //   格子放在上面才不会被长句盖住；本章两场阿努比斯战都不开计时 / 环境槽，那一块是空的
  function memoryHUD(S, c, rows, y) {
    const at = G.atlas('prop:anubis_icons');
    M.ui(S, g => {
      for (let i = 0; i < 3; i++) {
        const x = 630 - (3 - i) * 24 + 2, yy = 4;
        const hot = c.data.flashI === i && c.t < c.data.flashUntil;
        g.fillStyle = '#0c0a14'; g.fillRect(x, yy, 22, 22);
        g.fillStyle = hot ? '#e8c440' : '#3a3348'; g.fillRect(x + 2, yy + 2, 18, 18);
        const type = (c.data.memory || [])[i];
        // 图标是 9×9 的小图，×2 放大后脚点贴在格子底边往上两像素
        if (type && MEM_FRAME[type] != null && at) at.draw(g, 'idle', MEM_FRAME[type], x + 11, yy + 20, { scale: 2 });
      }
      M.hud(g, rows(), y == null ? 44 : y);
    });
  }
  // 被挡开那一格闪一下：类型 = 玩家刚被挡的那一招（格挡反击 / 连打 / 招式槽）
  function flashSlot(c, type) {
    const i = (c.data.memory || []).indexOf(type);
    if (i >= 0) { c.data.flashI = i; c.data.flashUntil = c.t + .3; }
  }
  // 记招的三段共用一套：kit 的 onHitBy 挡开时自己补的那一拳是 att = 妖刀、t = 玩家，
  //   所以从这一条反推被挡的是哪一招（格挡反击 / 连打 / 招式槽），给图标格闪金
  function memoryWatch(S, c, e) {
    c.on('parry', h => { if (h.who === c.player) c.player.mem.anubisCounterUntil = c.t + 1; });
    c.on('hit', h => {
      if (h.att !== e || h.t !== c.player || !(h.dmg > 0)) return;
      const p = c.player;
      const type = p.mem.anubisCounterUntil >= c.t ? '格挡反击' : p.atk && p.atk.slot === 'rush' ? '连打'
        : p.atk && p.atk.slot === 'special' ? 'U' : p.atk && p.atk.slot ? p.atk.slot : null;
      if (type) flashSlot(c, type);
    });
    // 放水：记招只记 2 种（脚本 §9-04），引擎的 kit 只记 3 种，这里从外面裁掉最早的
    c.data.trim = () => { if (c.assist && c.data.memory.length > 2) c.data.memory.splice(0, c.data.memory.length - 2); };
  }

  // ================================================================ 9-03 / 9-04 恰卡（b18a_anubis）
  async function polWanders(S) {
    calmStands();
    const rack = TP('sword_rack'), guide = TP('guide');
    // 队长强制换成波鲁纳雷夫，在 @sword_rack−60、朝右；其他人留在 @guide 附近，隐身
    S.setLeader('polnareff', { force: true, silent: true });
    const po = place(S, 'polnareff', rack[0] - 60, footY('temple_ch9', rack[1] + 4), 1);
    for (const [cid, dx] of [['jotaro', 0], ['joseph', 18], ['avdol', -18], ['iggy', -34]]) {
      const a = S.actor(cid);
      if (!a || a === po) continue;
      a.x = guide[0] + dx; a.y = footY('temple_ch9', guide[1] + 2); a.visible = false; a.follow = null; a.hold = false;
    }
    await lines(S, [['polnareff', '……那个，我去去就来！神殿里总该有厕所吧！'], ['joseph', '喂！说了不许一个人——']]);
    // 恰卡背对着他站在刀架前，手里握着一把弯刀
    const chaka = S.spawn('chaka', rack[0], footY('temple_ch9', rack[1] + 2), { id: 'c9_chaka', team: 'npc', name: '恰卡' });
    chaka.facing = -1; chaka.standReact = false; chaka.talk = null;
    const sword = T.prop(S, 'anubis_sword', rack[0] - 12, footY('temple_ch9', rack[1] + 2) - 18, { id: 'c9_chaka_sword', z: 18 });
    S.camera('polnareff');
    await S.wait(.4);
    await S.say('polnareff', '喂，小子。这里是禁止触摸的地方哦。');
    S.sfx('menacing', .5);
    chaka.facing = 1; chaka.tint = { color: '#b568f2', k: .35 };
    await S.say('chaka', '这把刀……在对我说话。', { actor: chaka });
    await S.say('chaka', '它说……砍了你。', { actor: chaka });
    await S.say('polnareff', '……把刀放下。那可不是玩具。');
    S.nameCard('chaka');
    await S.title('god_anubis');
    // 妖刀（名字显示「妖刀」，没有头像——图集里没有 anubis 这个角色，用无名牌的对白框 + name）
    await S.say(null, '我是阿努比斯。……我砍过的东西，我全都记得。', { name: '妖刀' });
    if (sword) sword.remove = true;
    S.mark('b18a_anubis');
  }
  async function fightChaka(S, o = STORY) {
    const rack = TP('sword_rack'), ar = TP('arrive');
    const spec = J.base('b18a_anubis', 'polnareff', [0, 640], {
      vs: 'anubis', music: 'battle_egypt', par: 90, dmgScale: .5, energy: { start: F().ch9Quiz ? 100 : 0 }, bench: 'hide',
      // 复用 9-03 摆在场上的恰卡（actor 复用：重试时身份不变，也不会同时站着两个恰卡）
      // 节奏（2026-10-20 实测校准）：引擎的记招（onHitBy）对同一类型第 2 次起一律挡开，而且它是按“每一段”
      //   判定的——连打和 U 的 6 段围刺只有第 1 段算数，玩家裸输出只有 ~5 dmg/s，110 血压根磨不完 900。
      //   所以这里给玩家加输出（dmgOut）、给对手减伤（dmgScale），并在玩家掉到半血时开放收尾窗口，
      //   保证两次重试以内一定能打出「射出剑身」的收尾演出，而不是被记招机制卡死。
      waves: [[{ actor: 'c9_chaka', cid: 'chaka', boss: true, hp: 900, poiseMax: 60, x: rack[0], y: footY('temple_ch9', rack[1] + 2) }]],
      kitOverride: { polnareff: { special: J.special(0, '用它没见过的招！U 射出剑身',
        c => !!(c.boss && (c.boss.hp <= c.boss.maxHp * .15 || (c.player.hp <= c.player.maxHp * .5 && c.boss.hp <= c.boss.maxHp * .55))),
        async (s, p, c) => {
          const e = c.boss; if (!e || !J.valid(c)) return;
          S.sfx('stab'); S.fx('slash_arc', { x: e.x, y: e.y - 24, size: 30 });
          // 不算进记招（unseen），必定破防命中
          G.combat.hit(p, e, { dmg: 120, slot: 'special', unseen: true, guard: 'none', reach: [0, 999], push: 12 });
          await S.wait(.5);
          if (J.valid(c)) c.end();
        }, 2) } },
      onWave(S2, i, es, a, c) {
        const e = es[0];
        c.data.memory = memory;
        Object.assign(c.data, { flashI: -1, flashUntil: 0 });
        assistScale(c);
        failLine(c, '……这把刀……越砍越快……');
        e.mem.counterAt = 0;
        c.player.x = ar[0] + 70; c.player.y = footY('temple_ch9', ar[1]); c.player.facing = 1;
        c.player.dmgOut = 3.5;   // 见上：记招把多段招砍成 1 段，靠输出倍率把战斗拉回可打的长度
        memoryWatch(S2, c, e);
        memoryHUD(S2, c, () => {
          const rows = ['刀记住的招', '同一种招第二次会被挡开反击——换着用'];
          if (F().ch9Quiz && c.t < 4) rows.push('记住了这把刀的名字：能量满');
          return rows;
        });
        S2.hint('白光能挡，紫光只能闪（K）。', 6);
      },
      tick(c) { if (c.data.trim) c.data.trim(); },
      after: async (s, es) => {
        if (o.trial) return;    // 试炼里只结算胜负，剑身飞出的过场与旗标都不演
        const b = es[0];
        s.insertUI(null);
        if (b && !b.dead && !b.remove) {
          // 剑身射穿刀光：弯刀从恰卡手里飞出，插在地上
          s.sfx('slash1', .8);
          const sw = T.prop(s, 'anubis_sword', b.x + 6, b.y - 32, { id: 'c9_flying_sword', z: 30 });
          if (sw) {
            await s.animate(.5, k => { sw.x = b.x + 6 + 34 * k; sw.z = 30 * (1 - k) + 14 * Math.sin(Math.PI * k); });
            sw.z = 0; sw.rot = Math.PI * .5;
          }
          s.pose(b, 'down');
          s.sfx('stab', .7);
        }
        await s.title('saiki');
        F().ch9Anubis = 1;
        const po = G.party.get('polnareff'); if (po) po.dmgOut = 1;
      },
      testHint: c => ({ memory: (c.data.memory || []).slice(), projectile: !!(c.boss && c.boss.hp <= c.boss.maxHp * .15), bossHp: c.boss && c.boss.hp }),
    });
    await S.fight(o.wrap(spec));
  }

  // ================================================================ 9-05 扔进尼罗河
  async function throwNile(S) {
    calmStands();
    const ar = TP('arrive'), ex = TP('exit'), nv = TP('nile_view'), rack = TP('sword_rack');
    const chaka = S.actor('c9_chaka');
    const sword = S.actor('c9_flying_sword');
    if (chaka && !chaka.remove) {
      S.pose(chaka, 'down'); chaka.tint = null;
      await S.say('chaka', '……我、我刚才在做什么？', { actor: chaka });
      // 爬起来往左跑出画面，移除
      S.unpose(chaka);
      S.walk(chaka, -40, footY('temple_ch9', ar[1]), { speed: 120, anim: 'walk' }).catch(G.cancelIgnore);
    }
    // 众人从左边跑过来：乔瑟夫、阿布德尔、伊奇，承太郎走在最后
    //   阿布德尔的图集没有 run（只有 walk），照抄 run 会一路滑过去
    for (const [cid, dx] of [['joseph', 0], ['avdol', -30], ['iggy', -56], ['jotaro', 26]]) {
      const a = place(S, cid, Math.max(10, ar[0] + dx), footY('temple_ch9', ar[1] + 2), 1);
      if (a) S.walk(a, ar[0] + 130 + dx, footY('temple_ch9', ar[1] + 2), { speed: 150, anim: cid === 'avdol' ? 'walk' : 'run' }).catch(G.cancelIgnore);
    }
    await S.wait(.9);
    S.camera('polnareff');
    await lines(S, [['joseph', '波鲁纳雷夫！又一个人乱跑！'], ['polnareff', '我、我只是去找厕所……结果找到了这个。']]);
    const po = S.actor('polnareff');
    if (po) {
      await S.walk(po, ex[0] - 20, footY('temple_ch9', ex[1]), { speed: 90 });
      po.facing = 1;
    }
    if (sword) sword.remove = true;
    // 弯刀被扔出去：弧线飞向 @nile_view（越飞越小）
    const fly = T.prop(S, 'anubis_sword', ex[0] - 22, footY('temple_ch9', ex[1]) - 18, { id: 'c9_thrown_sword', z: 16 });
    await S.say('polnareff', '再也不会有人碰它了。');
    if (fly) {
      const x0 = fly.x, y0 = fly.y;
      await S.animate(.8, k => {
        fly.x = G.lerp(x0, nv[0], k); fly.y = G.lerp(y0, nv[1], k);
        fly.z = 16 * (1 - k) + 26 * Math.sin(Math.PI * k);
        fly.scale = G.lerp(1, .3, k); fly.rot = k * 6;
      });
      fly.remove = true;
    }
    await S.wait(.2); S.sfx('splash', .4); await S.wait(.4);
    await lines(S, [['avdol', '……妖刀阿努比斯。被刀附身的人，会变成另一个人。'], ['jotaro', '……沉下去就好。']]);
    S.camera(null);
    if (chaka) chaka.remove = true;
  }

  // ================================================================ 9-06 河岸（nile_ch9，nile_bank 640 宽）
  const FISH_LINES = ['刚从河里捞起一把很漂亮的刀，卖给理发师了。', '尼罗河里什么都有。……昨天还捞到一只鞋。'];
  const KHAN_LINES = ['客人，要不要修修鬓角？', '我的剃刀，是新买的。……很快哦。'];
  const SPL = [];   // 打水漂的水花圈（世界坐标 + 出生时刻）
  function setupNile(st) {
    st.state = Object.assign({}, st.state, { chair_cut: 0 });   // 重来 / 再进图时椅子恢复完整
    const [fx0, fy0] = NB('fisher'), [bx, by] = NB('barber'), [cx, cy] = NB('barber_chair');
    st.npcs = [
      T.npc('npc_sailor', 'c9_fisher', fx0, footY('nile_ch9', fy0), { facing: -1, label: '渔夫', name: '渔夫', talk: async S => {
        const a = S.actor('c9_fisher');
        if (S.player.cid === 'iggy') { S.sfx('dog_bark'); await S.say('npc_sailor', '狗？别偷我的鱼。', { name: '渔夫', actor: a }); return; }
        await S.say('npc_sailor', pick('c9fish', FISH_LINES), { name: '渔夫', actor: a });
      } }),
      T.npc('khan', 'c9_khan', bx, footY('nile_ch9', by), { facing: -1, label: '理发师卡恩', name: '理发师', talk: async S => {
        const a = S.actor('c9_khan');
        if (S.player.cid === 'iggy') { S.sfx('dog_bark'); await S.say('khan', '狗的毛，我可不剪。', { name: '理发师', actor: a }); return; }
        await S.say('khan', pick('c9khan', KHAN_LINES), { name: '理发师', actor: a });
      } }),
    ];
    const H = (id, k, label, tags, use, look, o = {}) => { const v = NB(k); return J.hot(id, v[0], footY('nile_ch9', v[1]), label, tags, use, look, Object.assign({ ly: v[1] - 26, r: 24 }, o)); };
    st.hotspots = [
      H('c9_river', 'river', '尼罗河', ['nensha'],
        async (S, h, p) => sayBy(S, p, { polnareff: '……我扔下去的刀，应该沉到底了吧。', avdol: '尼罗河是埃及的命。没有它，就没有这片土地。', _: '宽阔的河面，缓缓往北流。' }),
        async (S, h, p) => { if (p.cid === 'joseph') { await S.photo({ frames: [0, 1, 2], hold: 1.2 }); await S.say('joseph', '……念写出来的是河底。可是……刀不在那里。'); } },
        { ly: NB('river')[1] - 20 }),
      H('c9_boat', 'boat', '渔夫的小船', [], async S => S.say(null, '一条小木船，船底积着一点水。'), null, { ly: NB('boat')[1] - 18 }),
      H('c9_nets', 'nets', '晒着的渔网', [], async (S, h, p) => sayBy(S, p, { polnareff: '渔网里缠着水草……还有一只鞋。', _: '木架上晒着渔网。' })),
      // 打水漂：河边，任何队长（伊奇叼石头跑掉，不开小游戏）
      J.hot('c9_skip', NB('skip_spot')[0], footY('nile_ch9', NB('skip_spot')[1]), '河边', [], async S => skipStones(S, S.player), null,
        { ly: NB('skip_spot')[1] - 20, r: 26 }),
      H('c9_mirror', 'mirror', '理发摊的镜子', ['detail'],
        async S => S.say(null, '一面挂在木架上的圆镜。'),
        async (S, h, p) => { if (p.cid === 'jotaro') { F().ch9Mirror = true; await S.say('jotaro', '……镜子里，剃刀的反光是紫色的。'); } },
        { ly: NB('mirror')[1] - 16, y: footY('nile_ch9', NB('mirror')[1] + 44) }),
      H('c9_tea', 'tea', '小茶摊', [], async (S, h, p) => sayBy(S, p, { joseph: '来四杯薄荷茶！……这次不会有毒吧？', _: '小茶摊上冒着热气。' })),
      H('c9_reeds', 'reeds', '芦苇丛', ['hole'],
        async S => S.say(null, '芦苇比人还高，风一吹沙沙响。'),
        async (S, h, p) => { if (p.cid === 'iggy') { S.sfx('dog_bark'); await S.say(null, '（伊奇钻进芦苇丛，叼出一只鞋。）'); await S.say(null, '……又是一只鞋。'); } }),
    ];
    // 理发椅（出口）：队长不是承太郎时，队长先劝一句，强制换承太郎
    const chair = NB('barber_chair');
    st.hotspots.push(J.hot('c9_chair', chair[0], footY('nile_ch9', chair[1]), '理发椅', [], async S => {
      const p = S.player;
      if (p.cid !== 'jotaro') {
        await S.say(p.cid, '承太郎，坐上去吧。');
        S.setLeader('jotaro', { force: true, silent: true });
      }
      F().ch9Barber = true;
    }, null, { ly: chair[1] - 14, r: 26 }));
    st.onLook = async (S, p) => { if (p.cid === 'iggy') await iggySay(S, '（伊奇对着河面嗅了嗅，耳朵竖了起来。）'); else await S.say(p.cid, '……河风很舒服。'); };
  }
  // 打水漂：三投，每投一段 rhythm（7 拍、间隔从 0.5 s 缩到 0.25 s）；按中几拍就跳几下
  async function skipStones(S, p) {
    if (p.cid === 'iggy') { S.sfx('dog_bark'); await S.say(null, '（伊奇叼起一块扁石头跑掉了。）'); return; }
    const intro = { jotaro: '……', joseph: '打水漂？年轻的时候我能打十下！', avdol: '……这是孩子的游戏。好吧，就一次。', polnareff: '我在塞纳河边可是冠军！' };
    await S.say(p.cid, intro[p.cid] || '……');
    const line = NB('skip_line').slice();
    const peb = T.prop(S, 'pebble', p.x + p.facing * 8, p.y - 16, { id: 'c9_pebble', z: 16 });
    const dots = M.pixel('c9_splash', P => drawSplash(P));
    let best = F().ch9Skip || 0;
    for (let r = 0; r < 3; r++) {
      const q = await S.rhythm({ label: '石子跳起来的一瞬间按 J', notes: [.5, .95, 1.35, 1.7, 2.02, 2.3, 2.55], window: .14, pass: 0 });
      const hits = q && q.hits != null ? q.hits : 0;
      await skipThrow(S, peb, hits, line);
      await S.say(null, hits + ' 下！');
      best = Math.max(best, hits);
    }
    F().ch9Skip = best;
    if (peb) peb.remove = true;
    if (dots) { dots.hidden = true; W.stage.props = W.stage.props.filter(x => x !== dots); }
    if (best >= 5) await X.give(S, 'ch9_flat_stone', { x: p.x, y: p.y - 20 });
    // 队长的评价：承太郎只在 7 下时说；波鲁纳雷夫另有冠军 / 河水两句
    if (p.cid === 'jotaro') { if (best === 7) await S.say('jotaro', '……七下。'); }
    else await S.say(p.cid, best + ' 下。');
    if (p.cid === 'polnareff') await S.say('polnareff', best >= 5 ? '看到了吧？冠军！' : '……今天的河水不对劲。');
  }
  function drawSplash(P) {
    const t = G.clk.world, cx = G.cam.x || 0, cy = G.cam.y || 0;
    for (const s of SPL) {
      const u = (t - s.t0) / .3;
      if (u < 0 || u > 1) continue;
      const r = Math.round(2 + u * 7), a = 1 - u;
      const x = Math.round(s.x - cx), y = Math.round(s.y - cy);
      px.ellipse(P, x - r, y - 1, x + r, y + 1, null, '#e8f8ff', 1, a);
    }
    if (SPL.length > 40) SPL.splice(0, SPL.length - 40);
  }
  async function skipThrow(S, peb, hits, line) {
    const p = S.player;
    const st = [p.x + p.facing * 10, p.y - 16];
    const first = line[0];
    if (peb) {
      peb.alpha = 1; peb.scale = 1; peb.rot = 0;
      await S.animate(.22, k => {
        peb.x = G.lerp(st[0], first[0], k); peb.y = G.lerp(st[1], first[1], k);
        peb.z = 10 * Math.sin(Math.PI * k);
      });
    }
    const n = Math.min(hits, line.length);
    for (let i = 0; i < n; i++) {
      const a = line[Math.min(i, line.length - 1)], b = line[Math.min(i + 1, line.length - 1)];
      if (peb) {
        await S.animate(.16, k => {
          peb.x = G.lerp(a[0], b[0], k); peb.y = G.lerp(a[1], b[1], k);
          peb.z = 8 * Math.sin(Math.PI * k);
        });
      } else await S.wait(.16);
      SPL.push({ x: b[0], y: b[1], t0: G.clk.world });
      snd('splash', 'water_splash', { vol: .2 });
    }
    // 没跳满的那一拍：石子沉下去（小水花 + 不再前进）
    const sink = line[Math.min(n, line.length - 1)];
    SPL.push({ x: sink[0], y: sink[1], t0: G.clk.world });
    snd('splash', 'water_splash', { vol: .15 });
    if (peb) {
      await S.animate(.25, k => { peb.x = sink[0]; peb.y = sink[1] + 4 * k; peb.z = 0; peb.alpha = 1 - k; });
      peb.alpha = 0;
    }
  }
  async function nileIntro(S) {
    calmStands(); party(S);
    await M.scene(S, 'nile_ch9', setupNile, NB('arrive')[0] + 20, 'jotaro');
    amb(S, 'river_loop', 'sea_loop', .16);
    S.location('nile_town');
    await S.wait(.5);
    await lines(S, [['joseph', '去卢克索的火车，下午才有。先在这里歇一会儿。'],
      ['polnareff', '那边有个露天的理发摊！承太郎，你的鬓角也该修修了。'], ['jotaro', '……不用。']]);
    T.memberTalk({
      joseph: async s => s.say('joseph', pick('c9niJo', ['到了卢克索，再坐车去开罗。', '理发？我的头发还用不着。'])),
      avdol: async s => s.say('avdol', pick('c9niAv', ['……这条河，看着我长大。', '刀沉下去就好。'])),
      polnareff: async s => s.say('polnareff', pick('c9niPo', ['承太郎！修鬓角！', '我在塞纳河边，打水漂可是冠军！'])),
      iggy: async s => {
        const t = pick('c9niIg', ['（伊奇在河边追一只水鸟。）', '……汪。']);
        if (t === '……汪。') await iggySay(s, t); else await s.say(null, t);
      },
      jotaro: async s => s.say('jotaro', pick('c9niJt', ['……不修。', '……'])),
    });
    follow();
  }
  async function nileExplore(S) {
    const chair = NB('barber_chair');
    await explore(S, 'ch9Barber', '河岸：E 调查、搭话；在河边可以打水漂。', 10,
      { x: chair[0], y: footY('nile_ch9', chair[1] + 4), h: 48, label: '理发摊', delay: 60, every: 25, text: '波鲁纳雷夫一直在劝承太郎去修鬓角。' });
  }

  // ================================================================ 9-07 / 9-08 理发摊与卡恩（b18b_anubis）
  async function barber(S) {
    calmStands();
    const chair = NB('barber_chair'), bar = NB('barber'), mir = NB('mirror'), tea = NB('tea');
    // 承太郎坐上理发椅（sit，朝右）；卡恩站在他身后，朝左；其余人在 @tea 一带
    const jt = place(S, 'jotaro', chair[0], footY('nile_ch9', chair[1]), 1);
    if (jt) S.pose(jt, 'sit', { freeze: 0 });
    const kh = S.actor('c9_khan');
    if (kh) { kh.x = bar[0]; kh.y = footY('nile_ch9', bar[1]); kh.facing = -1; kh.visible = true; kh.follow = null; }
    for (const [cid, dx] of [['joseph', -40], ['avdol', -14], ['polnareff', 12], ['iggy', 34]]) {
      const a = S.actor(cid);
      if (!a || a === jt) continue;
      a.x = tea[0] + dx; a.y = footY('nile_ch9', tea[1]); a.facing = -1; a.visible = true; a.follow = null; a.hold = false;
    }
    S.camera(chair[0] - 60);
    await S.say('khan', '客人的鬓角，我帮您修得整整齐齐。', { name: '理发师', actor: kh });
    // 卡恩举起剃刀：弯刀的刀柄从袖子里露出来；镜子里一道紫光闪过
    S.fx('glint', { x: mir[0], y: mir[1], size: 7 });
    snd('mirror_flash', 'glint', { vol: .6 });
    await S.wait(.5);
    await S.say('jotaro', F().ch9Mirror ? '……果然。' : '……你的剃刀。');
    S.sfx('menacing', .5);
    if (kh) kh.tint = { color: '#b568f2', k: .35 };
    await S.say('khan', '……上一场的招式，我都记得！', { name: '理发师', actor: kh });
    S.nameCard('khan');
    await S.wait(.3);
    S.camera(null);     // 镜头交还给队长（接下来的战斗要跟着玩家）
    S.mark('b18b_anubis');
  }
  async function fightKhan(S, o = STORY) {
    const chair = NB('barber_chair'), bar = NB('barber'), tea = NB('tea');
    // 同伴在 @tea 一带当观众（bench stay），朝左
    const benchAt = {};
    for (const [cid, dx] of [['joseph', -40], ['avdol', -14], ['polnareff', 12], ['iggy', 34]]) benchAt[cid] = [tea[0] + dx, footY('nile_ch9', tea[1])];
    const spec = J.base('b18b_anubis', 'jotaro', [0, 640], {
      vs: 'anubis', music: 'battle_egypt', par: 100, dmgScale: .75, bench: { mode: 'stay', at: benchAt },
      // 复用 9-06 站在理发摊上的卡恩（actor 复用：重试时身份不变，也不会同时站着两个卡恩）
      // 同 9-04：记招把多段招砍成 1 段，1200 血实测打不完；300 血 + 卡恩越砍越快的节奏，2 次重试内可过
      waves: [[{ actor: 'c9_khan', cid: 'khan', boss: true, hp: 320, poiseMax: 70, x: bar[0] + 40, y: footY('nile_ch9', bar[1]) }]],
      onWave(S2, i, es, a, c) {
        const e = es[0];
        // 9-07 让承太郎「坐」在理发椅上（S.pose 会把 hold 置真，战斗中会冻住玩家），开打前必须放开
        for (const m of G.party.members) { m.hold = false; m.frozen = null; }
        S2.unpose(c.player);
        // 9-07 第 6 拍：承太郎从椅子上闪开，理发椅被劈成两半（背景 pick 层 chair_cut 1 → 2，木屑）
        S2.state('chair_cut', 1);
        S2.sfx('slash1', .8);
        S2.fx('slash_arc', { x: chair[0], y: footY('nile_ch9', chair[1]) - 22, size: 26 });
        S2.fx('dust', { x: chair[0], y: footY('nile_ch9', chair[1]) - 2, n: 12, colour: '#d8b888' });
        c.data.memory = memory;
        Object.assign(c.data, { flashI: -1, flashUntil: 0 });
        assistScale(c);
        failLine(c, '……这把刀……还在学……');
        const base = e.speed; let hits = 0;
        e.mem.counterAt = 0;
        c.player.x = chair[0] - 40; c.player.y = footY('nile_ch9', chair[1]); c.player.facing = 1;
        // 越打越快：每被打中一次速度 +5%（放水时上限 +25%，否则 +50%）
        c.on('hit', h => {
          if (h.t !== e || !(h.dmg > 0)) return;
          const cap = c.assist ? .25 : .5;
          const pct = Math.min(cap, (hits += 1) * .05);
          e.speed = base * (1 + pct);
        });
        memoryWatch(S2, c, e);
        memoryHUD(S2, c, () => ['刀记住的招',
          '卡恩每挨一下快 5%（已 +' + Math.round((e.speed / base - 1) * 100) + '%）：速战速决']);
        S2.hint('白光能挡，紫光只能闪（K）。', 6);
      },
      tick(c) { if (c.data.trim) c.data.trim(); },
      after: async (s, es) => {
        if (o.trial) return;    // 试炼不演「再会」标题与旗标
        s.insertUI(null);
        if (es[0] && !es[0].dead && !es[0].remove) s.pose(es[0], 'down');
        await s.title('saiki');
        F().ch9Anubis = 2;
      },
      testHint: c => ({ memory: (c.data.memory || []).slice(), speed: c.boss ? Math.round((c.boss.speed || 0) * 100) / 100 : 0, bossHp: c.boss && c.boss.hp }),
    });
    await S.fight(o.wrap(spec));
  }

  // ================================================================ 9-09 / 9-10 被附身的波鲁纳雷夫（b18c_anubis）
  async function possessed(S) {
    calmStands();
    const bar = NB('barber');
    const kh = S.actor('c9_khan');
    if (kh) { kh.tint = null; S.pose(kh, 'down'); }
    const tgt = S.actor('polnareff');
    if (!tgt) return;
    tgt.facing = 1; tgt.visible = true; S.unpose(tgt);
    // 弯刀从他手里飞出，在空中转了几圈，插在波鲁纳雷夫脚边（起点 y 用理发摊锚点，不写死像素）
    const sw = T.prop(S, 'anubis_sword', bar[0], footY('nile_ch9', bar[1] - 10), { id: 'c9_sword_fall', z: 26 });
    if (sw) {
      await S.animate(.5, k => { sw.x = G.lerp(bar[0], tgt.x + 10, k); sw.z = 26 * (1 - k) + 40 * Math.sin(Math.PI * k); sw.rot = Math.PI * 4 * k; });
      sw.z = 0; sw.rot = Math.PI * .5;
      snd('stab', .7);
    }
    await S.say('polnareff', '……这把刀，我来收拾。这次我要把它——');
    await S.say('jotaro', '别碰！');
    S.sfx('sting_shock', .6); S.shake(2, .3);
    // 换成 polnareff_possessed（银色战车也召出来，手里多了一把刀）
    tgt.visible = false;
    const pol = S.spawn('polnareff_possessed', tgt.x, tgt.y, { id: 'c9_pol_possessed', team: 'npc', name: '波鲁纳雷夫？', stand: 'chariot' });
    pol.facing = -1; pol.standReact = false; pol.talk = null;
    if (pol.stand) pol.stand.summon({ instant: true });
    S.menacing({ x: pol.x, y: pol.y - 30, dur: 1.2 });
    await S.wait(.4);
    await S.say('jotaro', '……已经晚了。');
    await S.say('polnareff_possessed', '承太郎……我要砍的，是你。', { name: '波鲁纳雷夫？', actor: pol });
    // 卡恩倒地这一幕演完就撤掉（他留在场上会跟着后面的自由走动一起出现）
    if (kh) kh.remove = true;
    S.mark('b18c_anubis');
  }
  // 夹刀：精准格挡紫色突刺（引擎 AN_THRUST_P.onParried 的同一套演出：扣 25 血 → 连按 J → shatter → c.end）。
  //   招式表保持字符串 id：测试器和引擎都按 id 读（e.tele.move / moveCd 的键），塞对象进去就读不到了。
  //   放水的“对拼更容易”交给引擎自己的 clashFails 放宽（失败一次 push ×1.3）。
  async function fightPossessed(S, o = STORY) {
    const ar = NB('arrive');
    const spec = J.base('b18c_anubis', 'jotaro', [0, 640], {
      vs: 'anubis', music: 'battle_egypt', par: 100, dmgScale: .7,
      // 用 9-09 已经摆在场上的那个“被附身的波鲁纳雷夫”（actor 复用：重试时身份不变，也不会同时出现两个）
      waves: [[{ actor: 'c9_pol_possessed', cid: 'polnareff_possessed', boss: true, hp: 1400, minHp: 280, poiseMax: 80,
        x: ar[0] + 390, y: footY('nile_ch9', ar[1] - 4) }]],
      onWave(S2, i, es, a, c) {
        const e = es[0];
        // 9-09 的剧情里有 S.pose 把承太郎的 hold 置成真（战斗中会冻住玩家）：真实路线开打时玩家一动不动，
        //   90 s 内谁也打不到谁（2026-10-20 用 autowin 直达 b18c 抓到 hold:true）。开打前必须放开，写法同 fightKhan。
        for (const m of G.party.members) { m.hold = false; m.frozen = null; }
        S2.unpose(c.player);
        c.data.memory = memory;
        Object.assign(c.data, { flashI: -1, flashUntil: 0, bladeBusy: false });
        assistScale(c);
        e.mem.counterAt = 0;
        // 他是同伴，打不倒（minHp 280 = 20%）；夹刀才是结局
        c.player.x = ar[0] + 70; c.player.y = footY('nile_ch9', ar[1]); c.player.facing = 1;
        memoryWatch(S2, c, e);
        memoryHUD(S2, c, () => ['刀记住的招', '他是同伴，打不倒：等紫色突刺', '刺到的那一刻按 L 用身体夹住刀，再连按 J']);
        S2.hint('紫色突刺只能精准格挡（L）：夹住刀再连按 J。', 8);
      },
      tick(c) { if (c.data.trim) c.data.trim(); },
      after: async (s, es) => {
        if (o.trial) return;    // 试炼不演倒地 / 插刀回收，胜负由战斗直接结算
        s.insertUI(null);
        // 刀在夹刀演出里被 shatter 打碎了，地上那截插着的模型也撤掉（T.prop 生成的是 actor，用 S.remove 收）
        s.remove('c9_sword_fall');
        if (es[0] && !es[0].dead && !es[0].remove) s.pose(es[0], 'down');
        await s.title('saiki');
        F().ch9Anubis = 3;
      },
      testHint: c => ({ memory: (c.data.memory || []).slice(), bladeBusy: !!c.data.bladeBusy, bossHp: c.boss && c.boss.hp }),
    });
    await S.fight(o.wrap(spec));
  }

  // ================================================================ 9-11 碎片、小孩和伊奇
  async function kidTrip(S) {
    calmStands();
    const ar = NB('arrive'), river = NB('river');
    const possessed = S.actor('c9_pol_possessed');
    const po = S.actor('polnareff');
    if (possessed) possessed.remove = true;
    if (po) {
      po.visible = true; po.x = possessed ? possessed.x : ar[0] + 300; po.y = footY('nile_ch9', 162); po.facing = 1;
      po.tint = null; S.pose(po, 'kneel', { freeze: 0 });
      await S.say('polnareff', '……我……刚才……');
      S.unpose(po);
      await S.say('jotaro', '……没事了。');
    } else await lines(S, [['polnareff', '……我……刚才……'], ['jotaro', '……没事了。']]);
    // 承太郎转身背对河岸
    const jt = S.actor('jotaro');
    if (jt) { jt.facing = -1; jt.follow = null; }
    // 刀的碎片里最大的一片落在一个小孩脚边；小孩捡起来，眼睛发紫光，从承太郎背后一步步走近
    const kidX = (jt ? jt.x : ar[0] + 40) + 60;
    const kid = S.spawn('npc_kid', kidX, footY('nile_ch9', 164), { id: 'c9_kid', team: 'npc' });
    kid.facing = -1; kid.standReact = false; kid.talk = null;
    const shard = T.prop(S, 'anubis_sword', kidX - 8, footY('nile_ch9', 164) - 4, { id: 'c9_shard', z: 2, scale: .5 });
    await S.wait(.4);
    S.sfx('heartbeat', .4);
    if (shard) { shard.x = kid.x - 6; shard.y = kid.y - 10; shard.z = 10; }
    kid.tint = { color: '#b568f2', k: .4 };
    if (jt) {
      const step = (jt.x - kid.x) / 4;
      for (let i = 0; i < 4; i++) await S.walk(kid, kid.x + step, kid.y, { speed: 26 });
    }
    // 伊奇从左边追着一只水鸟冲过来，从小孩脚边穿过：140 px/s
    const ig = S.actor('iggy');
    if (ig) {
      S.sfx('dog_bark');
      ig.visible = true; ig.follow = null;
      const y = footY('nile_ch9', 166);
      ig.x = Math.max(8, kid.x - 200); ig.y = y;
      S.walk(ig, kid.x, y, { speed: 140, anim: 'run' }).catch(G.cancelIgnore);
      await S.wait(.45);
    }
    // 小孩被绊倒：down；碎片飞出去，弧线落进河里
    S.pose(kid, 'down'); kid.tint = null;
    if (shard) {
      const x0 = shard.x, y0 = shard.y;
      S.animate(.5, k => {
        shard.x = G.lerp(x0, river[0], k); shard.y = G.lerp(y0, river[1], k);
        shard.z = 16 * Math.sin(Math.PI * k); shard.rot = k * 5;
      }).catch(G.cancelIgnore);
    }
    await S.wait(.5);
    S.sfx('splash', .5);
    if (shard) shard.remove = true;
    await S.wait(.3);
    S.unpose(kid);
    S.sfx('kid_cry', .4);
    S.walk(kid, kid.x + 80, kid.y, { speed: 90, anim: 'run' }).catch(G.cancelIgnore);
    await S.wait(.5);
    kid.remove = true;
    await S.say('jotaro', '……？');
    // 伊奇叼着水鸟的一根羽毛，若无其事地走开了
    if (ig) S.walk(ig, ig.x - 120, ig.y + 4, { speed: 45 }).catch(G.cancelIgnore);
    await S.say(null, '（伊奇叼着水鸟的一根羽毛，若无其事地走开了。）');
    await lines(S, [['polnareff', '……我又一个人行动了，对吧。'], ['joseph', '对。'], ['avdol', '对。'], ['polnareff', '…………']]);
    for (const a of G.party.members) a.tint = null;
  }

  // ================================================================ 9-12 卢克索（luxor_ch9，luxor_town 960 宽）
  const MARIAH_LINES = ['试试这只插座？很特别哦。', '碰一下就知道了……嘻嘻。'];
  const OWNER_LINES = ['咖啡要加几块糖？', '水烟？一口一个故事。'];
  const WASHER_LINES = ['小孩子……咳，今天天气真好。', '我最喜欢……小孩子了。'];
  function setupLuxor(st) {
    st.state = Object.assign({}, st.state);
    const [mx, my] = LT('mariah'), [wx, wy] = LT('washer'), [ox, oy] = LT('cafe_owner');
    st.npcs = [
      T.npc('mariah', 'c9_mariah', mx, footY('luxor_ch9', my), { facing: -1, label: '卖插座的女人', name: '卖插座的女人', talk: async S => {
        const a = S.actor('c9_mariah');
        if (S.player.cid === 'iggy') { S.sfx('dog_bark'); await S.say('mariah', '好可爱的小狗～……别咬我的裙子。', { name: '卖插座的女人', actor: a }); return; }
        await S.say('mariah', pick('c9mariah', MARIAH_LINES), { name: '卖插座的女人', actor: a });
      } }),
      T.npc('alessi', 'c9_washer', wx, footY('luxor_ch9', wy), { facing: -1, label: '擦窗工人', name: '擦窗工人', talk: async S => {
        await S.say('alessi', pick('c9washer', WASHER_LINES), { name: '擦窗工人', actor: S.actor('c9_washer') });
      } }),
      T.npc('npc_townsfolk', 'c9_owner', ox, footY('luxor_ch9', oy), { facing: -1, label: '咖啡馆老板', name: '咖啡馆老板', talk: async S => {
        const a = S.actor('c9_owner');
        if (S.player.cid === 'iggy') { S.sfx('dog_bark'); await S.say('npc_townsfolk', '你要方糖？……就一块。', { name: '咖啡馆老板', actor: a }); return; }
        await S.say('npc_townsfolk', pick('c9owner', OWNER_LINES), { name: '咖啡馆老板', actor: a });
      } }),
    ];
    const H = (id, k, label, tags, use, look, o = {}) => { const v = LT(k); return J.hot(id, v[0], footY('luxor_ch9', v[1]), label, tags, use, look, Object.assign({ ly: v[1] - 26, r: 24 }, o)); };
    // 墙上的插座 = 出口：任何队长先看一眼，乔瑟夫自动走过来
    //   标签写「墙上插座」：第9章自动测试在 luxor_ch9 用这个字符串找出口（'墙上插座' / '插座'），
    //   写成「墙上的插座」会让它找不到热点、卡在自由走动里直到超时。
    const sock = LT('socket_stand'), sockY = LT('socket')[1];
    st.hotspots = [
      J.hot('c9_socket', sock[0], footY('luxor_ch9', sock[1]), '墙上插座', ['detail'],
        async S => {
          const p = S.player;
          await S.say(p.cid, '位置很低、很新的插座。');
          const jo = S.actor('joseph');
          if (jo && jo !== p) { jo.follow = null; await S.walk(jo, sock[0] - 14, footY('luxor_ch9', sock[1]), { speed: 120 }); }
          await S.say('joseph', '哦？这里有插座！我的剃须刀正好没电了——');
          F().ch9Socket = true;
        },
        async (S, h, p) => { if (p.cid === 'jotaro') await S.say('jotaro', '……这面墙是旧的，插座是新的。'); },
        { ly: sockY - 8, r: 26 }),
      H('c9_cafe', 'cafe', '咖啡馆', [], async (S, h, p) => sayBy(S, p, { joseph: '土耳其咖啡！……伊奇，这个你不能喝。', _: '露天咖啡馆，几个老人抽着水烟。' })),
      // 方糖（纪念品）：伊奇的鼻子才找得到
      X.hot('ch9_sugar', LT('sugar')[0], footY('luxor_ch9', LT('sugar')[1]), { look: ['scent'],
        found: S => S.say(null, '（伊奇从桌底下叼出一块方糖。）') }),
      H('c9_scaffold', 'scaffold', '脚手架', ['detail'],
        async S => S.say(null, '脚手架上挂着水桶和抹布。'),
        async (S, h, p) => { if (p.cid === 'jotaro') { F().ch9Shadow = true; await S.say('jotaro', '擦窗的家伙……影子比他本人长得多。'); } },
        { ly: LT('scaffold')[1] - 10, y: footY('luxor_ch9', LT('washer')[1]) }),
      H('c9_alley', 'alley', '小巷', ['hole'],
        async S => S.say(null, '窄巷里晾着衣服。'),
        async (S, h, p) => { if (p.cid === 'iggy') { S.sfx('dog_bark'); await S.say(null, '（伊奇钻进巷子，又钻了出来，嘴里叼着一块饼。）'); } }),
      H('c9_station', 'station_road', '去车站的路', [], async S => S.say(null, '去火车站的路。……还不能走，乔瑟夫在找什么东西。')),
    ];
    st.onLook = async (S, p) => { if (p.cid === 'iggy') await iggySay(S, '（伊奇对着脚手架低吼。）'); else await S.say(p.cid, '……街上很热闹。'); };
  }
  async function luxorIntro(S) {
    calmStands(); party(S);
    await M.scene(S, 'luxor_ch9', setupLuxor, LT('arrive')[0] + 20, 'jotaro');
    amb(S, 'bazaar_loop', 'crowd_loop', .14);
    S.location('luxor');
    await S.wait(.5);
    await lines(S, [['joseph', '卢克索！离开罗只剩一段路了。'], ['avdol', '九荣神……已经倒下四个了。']]);
    T.memberTalk({
      joseph: async s => s.say('joseph', pick('c9lxJo', ['我的剃须刀没电了……这一路上胡子长得好快。', '开罗就在前面！'])),
      avdol: async s => s.say('avdol', pick('c9lxAv', ['卢克索有很多神殿。……可惜没时间看。', '小心，人多的地方最容易下手。'])),
      polnareff: async s => s.say('polnareff', pick('c9lxPo', ['那个擦窗的大叔，一直在看我们。', '别再让我一个人行动了……我是说真的！'])),
      iggy: async s => {
        const t = pick('c9lxIg', ['（伊奇在咖啡馆的桌子底下打瞌睡。）', '……汪。']);
        if (t === '……汪。') await iggySay(s, t); else await s.say(null, t);
      },
      jotaro: async s => s.say('jotaro', pick('c9lxJt', ['……', '……那个女人在笑什么。'])),
    });
    follow();
  }
  async function luxorExplore(S) {
    const sock = LT('socket_stand');
    await explore(S, 'ch9Socket', '卢克索：E 调查、搭话。', 8,
      { x: sock[0], y: footY('luxor_ch9', sock[1] + 2), h: 50, label: '插座？', delay: 60, every: 25, text: '墙上有个奇怪的插座。' });
  }
  // 出过场以后把用掉的人物 / 出口从地图定义里摘掉（再进图不会重新长出来）
  function luxorPrune(S, ids) {
    const st = G.STAGES.luxor_ch9;
    if (ids.npcs && ids.npcs.length) st.npcs = (st.npcs || []).filter(n => ids.npcs.indexOf(n.id) < 0);
    if (ids.hotspots && ids.hotspots.length) st.hotspots = (st.hotspots || []).filter(h => ids.hotspots.indexOf(h.id) < 0);
  }

  // ================================================================ 9-13 / 9-14 插座与巴斯特女神（b19_bast，街道 → 铁路）
  async function socketScare(S) {
    calmStands();
    const sock = LT('socket_stand');
    luxorPrune(S, { hotspots: ['c9_socket'] });
    const jo = place(S, 'joseph', sock[0] - 10, footY('luxor_ch9', sock[1]), 1);
    place(S, 'avdol', sock[0] + 44, footY('luxor_ch9', sock[1] + 2), 1);
    // 卖插座的女人（用地图上的 NPC，进战斗时她就是 Boss）
    const mariah = S.actor('c9_mariah');
    if (mariah) { mariah.talk = null; mariah.standReact = false; mariah.facing = -1; }
    // 乔瑟夫插上剃须刀
    snd('zap', 'sparkle', { vol: .7 }); S.flash(.2, .8, '#ffffff'); S.shake(2, .25);
    if (jo) { S.pose(jo, 'shock', { freeze: 0 }); }
    await S.wait(.5);
    await S.say('joseph', '哇啊——！……这、这是什么插座？！', jo ? { actor: jo } : {});
    if (jo) S.unpose(jo);
    // 路边一只罐头“嗖”地飞过来粘在乔瑟夫身上
    snd('magnet_clack', 'metal_drop', { vol: .6 });
    if (jo) { const can = T.prop(S, 'metal_junk', jo.x + 40, jo.y - 20, { id: 'c9_can', z: 14, frame: 0 }); if (can) S.arc(can, jo.x + 2, jo.y - 14, 10, .3).catch(G.cancelIgnore); }
    await S.say('mariah', '碰过它的人，都会变成磁铁哦。……慢慢地，变成一块大磁铁。', mariah ? { actor: mariah } : {});
    S.nameCard('mariah');
    await S.title('god_bast');
    snd('magnet_clack', 'metal_drop', { vol: .5 });
    await S.say('avdol', '乔斯达先生！……我刚才扶了你一下——');
    await S.say('joseph', '承太郎、波鲁纳雷夫，你们先去车站！这个女人，我们来对付！');
    // 承太郎、波鲁纳雷夫、伊奇往右走出画面（分头：队伍只剩乔瑟夫、阿布德尔）
    //   波鲁纳雷夫的图集没有 run（只有 walk），照抄 run 会一路滑过去
    for (const cid of ['jotaro', 'polnareff', 'iggy']) {
      const a = S.actor(cid);
      if (!a) continue;
      a.follow = null;
      S.walk(a, a.x + 220, a.y, { speed: 150, anim: cid === 'polnareff' ? 'walk' : 'run' }).catch(G.cancelIgnore);
    }
    await S.say('jotaro', '……别输。');
    await S.wait(.6);
    for (const cid of ['jotaro', 'polnareff', 'iggy']) { const a = S.actor(cid); if (a) a.visible = false; }
    S.party(['joseph', 'avdol'], { leader: 'joseph' });
    S.mark('b19_bast');
  }
  async function fightBast(S, o = STORY) {
    const sock = LT('socket_stand'), mx = LT('mariah'), pf = RP('platform'), tk = RP('tracks'), railBand = RP('rail_band');
    // 试炼可能不带乔瑟夫 / 阿布德尔：两人不齐就没有 J＋L 合击，改成打光血条即胜
    const both = !o.trial || !!(G.party.get('joseph') && G.party.get('avdol'));
    // 合击 J＋L：登记成引擎原生组合键（不占 U）。条件满足才真正出 JA_MAGNET_CLAP（它的 onStart
    // 会喊「合击！」、撒废铁、结束战斗）；不满足时照脚本让她闪开（拟声字「嘻嘻～」）。
    // 注意不能写在 tick 里用 I.chord() 自己读：updatePlayer 先结算 chords 再 take('attack')，
    // tick 里先 take 会把按键吃掉，合击永远按不出来（章末 clap 检查失败）。
    const clapChord = { run(S2, a, c2) {
      const e = c2 && c2.boss;
      if (!e) return;
      if (c2.data && c2.data.clap) { c2.data.clapDone = true; F().ch9Clap = true; G.combat.startMove(a, 'JA_MAGNET_CLAP'); }
      else { S2.word('嘻嘻～', e); S2.hint('先打到半血，再分站她左右，J＋L 合击。', 4); }
    } };
    const spec = {
      id: 'b19_bast', lead: 'joseph', swap: true, allies: ['avdol'], bench: 'hide',
      vs: 'bast', music: 'battle_egypt', par: 120, dmgScale: .6, losable: true, playerMinHp: 0,
      arena: [0, G.STAGES.luxor_ch9.x1], coverage: false,
      kitOverride: both ? Object.fromEntries(['joseph', 'avdol'].map(cid => [cid, { chords: { 'attack+guard': clapChord } }])) : {},
      // 老板是地图上的那个 NPC（actor 复用同一个对象，重试时身份不变）
      waves: [[{ actor: 'c9_mariah', cid: 'mariah', boss: true, hp: 1300, minHp: both ? 650 : 0, poiseMax: 60, x: mx[0], y: footY('luxor_ch9', mx[1]), brain: mariahBrain }]],
      tick(c, dt) { bastTick(S, c, dt, railBand, o, both); },
      after: async (s, es, a, c) => { if (!o.trial) await squeeze(s, es[0], c); },
      testHint: c => {
        const d = c.data || {};
        return { phase: d.phase, magnets: Object.assign({}, d.magnets), stuck: !!d.stuck,
          train: Math.max(0, Math.round((d.trainAt || 0) - c.t)), clap: !!d.clap,
          mariahX: c.boss ? Math.round(c.boss.x) : 0, mariahHp: c.boss ? c.boss.hp : 0 };
      },
      onRetry: async (s, attempt, c) => {
        // 重试从街道段开始（磁化 0、废铁清空、玛丽亚回 @mariah）
        c.spec.arena = [0, G.STAGES.luxor_ch9.x1];
        S.state('rumble', 0);
        await s.setStage('luxor_ch9', { x: sock[0] - 40, y: footY('luxor_ch9', 162), fade: false, music: null });
      },
    };
    await M.objectFight(S, o.wrap(spec), c => {
      // 每次尝试（含重试）都从这里开始
      const p = c.player, mate = G.party.get(p.cid === 'joseph' ? 'avdol' : 'joseph');
      Object.assign(c.data, {
        phase: 'street', magnets: { joseph: 0, avdol: 0 }, stuck: false, clap: false, clapDone: false, dragged: false,
        trainAt: 0, trainWarnUntil: 0, trainHitAt: 0, trainOn: false, trainProp: null, dirAt: 0, dirUntil: 0, dirSide: 1,
        socketAt: c.t + 3, socketShot: null, junkAt: c.t + .8, speeds: { joseph: p.speed, avdol: mate ? mate.speed : 60 },
      });
      assistScale(c);
      failLine(c, '……全身都是罐头……动不了了……');
      S.state('rumble', 0);
      p.x = sock[0] - 20; p.y = footY('luxor_ch9', 162); p.facing = 1;
      if (mate) { mate.x = sock[0] + 130; mate.y = footY('luxor_ch9', 164); mate.facing = -1; mate.hold = false; }
      pixelOnce('c9_bast', P => drawBast(P, c, railBand));
      S.insertUI(null);
      M.ui(S, g => bastHUD(g, c));
      S.hint('废铁会被吸过来：别让两个人贴在一起。', 6);
    });
    for (const a of G.party.members) { a.hold = false; a.script = null; a.speed = kidSafeSpeed(a); }
  }
  // 玛丽亚：不主动进攻，被追近就跑开；跑到场地边上就“跑出画面再回来”（换到玩家另一侧）
  //   跑开的速度要比玩家慢一点（0.8×）：她 62，乔瑟夫 64 —— 原来写 1.5× 谁都追不上，
  //   血打不到 50%，合击窗口永远不开，这一战就卡死。
  function mariahBrain(e, dt, c) {
    if (!dt) return true;
    const p = c.player, arena = c.spec.arena;
    e.facing = p.x > e.x ? 1 : -1;
    const dx = p.x - e.x;
    if (!e.atk && !e.tele) {
      if (Math.abs(dx) < 70) {
        const back = e.x - Math.sign(dx) * 60;
        if (back < arena[0] + 12 || back > arena[1] - 12) {
          G.combat.fxAt('dust', { x: e.x, y: e.y, n: 8 }, e, .4);
          e.x = G.clamp(p.x + (p.x > (arena[0] + arena[1]) / 2 ? -1 : 1) * 150, arena[0] + 14, arena[1] - 14);
          G.combat.fxAt('dust', { x: e.x, y: e.y, n: 8 }, e, .4);
        } else G.combat.walkTo(e, back, e.y, dt, e.speed * .8);
        return true;
      }
      if (e.cool <= 0 && Math.abs(dx) < 54 && Math.abs(p.y - e.y) < 14) { G.AI.tele(e, 'MARIAH_KICK'); e.cool = 1.6; return true; }
    }
    G.AI.approach(e, p, 96, dt);
    return true;
  }
  function drawBast(P, c, railBand) {
    const d = c.data, e = c.boss, cx = G.cam.x || 0, cy = G.cam.y || 0;
    // 火车预警：铁轨带闪红（rumble 一个 key 开铁轨震动 + 信号机红灯，闪红由剧情画）
    if (d.trainWarnUntil > c.t) {
      const y0 = railBand[1] - cy, y1 = railBand[3] - cy;
      if (Math.floor(c.t * 12) % 2) { px.rect(P, 0, y0, 320, 1, '#ff4438', .8); px.rect(P, 0, y1 - 1, 320, 1, '#ff4438', .8); }
    }
    if (e && !e.remove) {
      const x = Math.round(e.x - cx), y = Math.round(e.y - cy);
      px.ellipse(P, x - 8, y - 2, x + 8, y + 2, '#2a1c14', null, 1, .35);
    }
  }
  function bastHUD(g, c) {
    const d = c.data, p = c.player;
    if (!d.magnets) return;    // 重试的第一帧 c.data 刚被清空，UI 还在旧闭包上画一帧
    const mate = G.party.get(p.cid === 'joseph' ? 'avdol' : 'joseph');
    const rows = ['磁化　乔瑟夫 ' + Math.floor(d.magnets.joseph) + '%　阿布德尔 ' + Math.floor(d.magnets.avdol) + '%',
      d.clap ? '现在！J＋L 一起按，两人把她夹住！' : '打到半血后两人分站她左右，J＋L 合击'];
    if (d.phase === 'rail') rows.push('火车来时离开铁轨（Q 换人）');
    M.hud(g, rows, 44);
    // 方向提示：屏幕边缘的箭头（3 s）
    if (d.dirUntil > c.t) {
      const right = d.dirSide > 0, y = 150, x = right ? 618 : 22;
      g.fillStyle = Math.floor(c.t * 8) % 2 ? '#ffd83c' : '#ffffff';
      g.beginPath();
      if (right) { g.moveTo(x + 14, y); g.lineTo(x, y - 10); g.lineTo(x, y + 10); }
      else { g.moveTo(x - 14, y); g.lineTo(x, y - 10); g.lineTo(x, y + 10); }
      g.closePath(); g.fill();
      if (G.f12 && mate) G.f12.draw(g, mate.cid === 'avdol' ? '阿布德尔' : '乔瑟夫', x, y - 24, '#ffe9a8', { align: 'center', outline: '#1a1020' });
    }
  }
  async function bastTick(S, c, dt, railBand, o = STORY, both = true) {
    const d = c.data, p = c.player, e = c.boss;
    if (!e || e.remove) return;
    const other = p.cid === 'joseph' ? 'avdol' : 'joseph';
    const mate = G.party.get(other);
    // ---- 磁化槽：60 s 从 0 涨到 100（放水 90 s）
    const rate = 100 / (c.assist ? 90 : 60);
    for (const cid of ['joseph', 'avdol']) d.magnets[cid] = Math.min(100, d.magnets[cid] + dt * rate);
    // ---- 两人相吸：距离 < 40 就黏在一起（速度 ×0.7，互相往中间拉）
    d.stuck = !!(mate && Math.abs(p.x - mate.x) < 40);
    p.speed = d.speeds.joseph * (d.stuck ? .7 : 1);
    if (mate) {
      mate.speed = d.speeds.avdol * (d.stuck ? .7 : 1);
      if (d.stuck) {
        const pull = (40 - Math.abs(p.x - mate.x)) * dt * 2.4;
        W.move(p, Math.sign(mate.x - p.x) * pull, 0);
        W.move(mate, Math.sign(p.x - mate.x) * pull, 0);
      }
    }
    // ---- 废铁：每 0.8 s 每人身边飞来一件（速度 = 磁化 × 1.2 px/s，伤 3–6）
    if (c.t >= d.junkAt) {
      d.junkAt = c.t + .8;
      for (const a of [p, mate]) {
        if (!a) continue;
        const mag = d.magnets[a.cid] || 0;
        if (mag < 8) continue;
        const side = Math.sin(c.t * 2.3 + (a.cid === 'joseph' ? 0 : 2)) > 0 ? 1 : -1;
        c.shoot(e, { kind: 'img', image: { cid: 'prop:metal_junk', logical: 'idle' }, x: a.x + side * 95, y: a.y,
          vx: -side * mag * 1.2, vy: 0, dmg: 3 + Math.floor(mag / 34), slot: 'enemy', life: 3.2, guard: 'normal',
          hitR: [6, 8, 20], z: 14 });
      }
    }
    // ---- 扔插座：每 3 s，黄色警示线 0.5 s，然后插座沿直线飞 180 px/s，碰到磁化 +15
    if (d.phase === 'street' && c.t >= d.socketAt) {
      d.socketAt = c.t + 3;
      const sign = p.x < e.x ? -1 : 1;
      S.fx('warn_line', { pts: [[e.x, p.y], [e.x + sign * 190, p.y]], dur: .5, colour: '#ffd45a' });
      snd('metal_scrape', null, { vol: .4 });
      d.socketShot = { at: c.t + .5, sign, y: p.y };
    }
    if (d.socketShot && c.t >= d.socketShot.at) {
      const q = d.socketShot; d.socketShot = null;
      c.shoot(e, { kind: 'img', image: { cid: 'prop:socket', logical: 'idle' }, x: e.x, y: q.y, vx: q.sign * 180, vy: 0,
        dmg: 0, slot: 'enemy', life: 4, guard: 'none', hitR: [6, 8, 18], z: 12,
        onHit(shot, t2) { if (d.magnets[t2.cid] != null) { d.magnets[t2.cid] = Math.min(100, d.magnets[t2.cid] + 15); snd('magnet_clack', 'metal_drop', { vol: .5 }); } } });
    }
    // ---- 第一段 → 第二段：磁化到 50% 或开战 30 s（过场，不出战斗）
    if (d.phase === 'street' && !d.dragged && (d.magnets.joseph >= 50 || d.magnets.avdol >= 50 || c.t >= 30)) {
      d.dragged = true;
      M.task(c, async () => {
        // 被吸着往后滑：两人 0.8 s 往左滑 60 px。
        //   ⚠ 这里不能用 S.animate：world.update 用 filter 收 ticks，战斗 tick 里新压进去的 tick
        //   会被这一轮的 filter 丢掉（动画永远等不到第一帧）。改成按世界时钟分段等，每段自己插值。
        const x0 = p.x, m0 = mate ? mate.x : 0, N = 12;
        for (let i = 1; i <= N; i++) {
          await S.wait(.8 / N);
          if (!J.valid(c)) return;
          const k = i / N;
          p.x = G.lerp(x0, x0 - 60, k);
          if (mate) mate.x = G.lerp(m0, m0 - 60, k);
        }
        if (!o.trial) {
          await S.say('joseph', '撤退！逃跑是乔斯达家的传统战术！……可是脚不听使唤啊！', { pos: 'bottom' });
          await S.say('avdol', '乔斯达先生，是磁力！我们被吸向铁轨了！', { pos: 'bottom' });
        }
        if (!J.valid(c)) return;
        // 换图（照第5章恋人战 streetTask 的 J.transfer）：HP、磁化、玛丽亚 HP 都不重置
        c.spec.arena = [0, 640];
        await J.transfer(c, 'rail_ch9', pfX(), tkX());
        if (!J.valid(c)) return;
        // 像素层挂在“当前这张图的 props”上：换图以后旧那层留在 luxor_ch9，新图上得再挂一次
        //   （铁轨带闪红 / 玛丽亚脚下那块影子，铁路段还要用）
        pixelOnce('c9_bast', P => drawBast(P, c, RP('rail_band')));
        p.x = pfX(); p.y = footY('rail_ch9', 154); p.facing = 1;
        if (mate) { mate.x = pfX() + 120; mate.y = footY('rail_ch9', 154); mate.facing = -1; }
        if (c.boss) { c.boss.x = tkX(); c.boss.y = footY('rail_ch9', 164); c.boss.remove = false; }
        d.phase = 'rail';
        d.trainAt = c.t + (c.assist ? 20 : 15);
        S.hint('火车来时离开铁轨（Q 换人）。', 6);
      });
    }
    // ---- 方向提示：没在操作的那个人每 20 s 喊一次（3 s + 屏幕边缘箭头）
    if (!d.cine && c.t >= d.dirAt) {
      d.dirAt = c.t + 20;
      const isRight = e.x > p.x;
      d.dirSide = isRight ? 1 : -1;
      d.dirUntil = c.t + 3;
      S.bark(mate ? mate.cid : other, isRight ? '她在右边！→' : '← 她在左边！', { dur: 3 });
    }
    // ---- 合击：玛丽亚 HP ≤ 50%、两人分站她左右、距离 ≤ 120、她在中线 ±14
    //   按键走引擎原生 chords（spec.kitOverride 里登记 'attack+guard' → JA_MAGNET_CLAP）：
    //   updatePlayer 先结算 chords 再 take('attack')，在这里自己 I.chord() 会把按键吃掉，
    //   合击就永远触发不了（章末 clap 检查会失败）。这里只负责判定条件 + 提示。
    const half = e.hp <= e.maxHp * .5 + .5;
    if (both) {
      // 玛丽亚为躲玩家会瞬移到玩家另一侧，同伴（引擎的 updateAlly）只从自己那一侧靠近 ——
      //   两人一旦被躲成同侧，合击就再也合不上。照引擎自己的 G.AI.blink 给同伴也来一次瞬移
      //   （残影靠 dust，引擎的 blink 也是这么做的），每 2 s 最多一次。
      if (half && mate && !d.cine && (p.x - e.x) * (mate.x - e.x) > 0 && c.t >= (d.flipAt || 0)) {
        d.flipAt = c.t + 2;
        const side = Math.sign(p.x - e.x) || 1;
        const want = G.clamp(e.x - side * 46, arenaX0(c) + 12, arenaX1(c) - 12);
        G.combat.fxAt('dust', { x: mate.x, y: mate.y, n: 6 }, mate, .25);
        mate.x = want; mate.y = e.y;
        G.combat.fxAt('dust', { x: mate.x, y: mate.y, n: 6 }, mate, .25);
      }
      d.clap = !!(half && mate && (p.x - e.x) * (mate.x - e.x) < 0 && Math.abs(p.x - mate.x) <= 120 && Math.abs((p.x + mate.x) / 2 - e.x) <= 14);
      // 她一直在跑、同伴也在跟：条件真正同时成立往往只有几帧，玩家（和自动测试的下一帧轮询）来不及按。
      //   成立过一次就留 2.5 s 的窗口，期间 J＋L 都算数（JA_MAGNET_CLAP 的 onStart 先读 c.data.clap）
      if (d.clap) d.clapUntil = c.t + 2.5;
      d.clap = d.clap || c.t < (d.clapUntil || 0);
      if (d.clap && !d.prompt) { d.prompt = true; S.hint('现在！J＋L 合击！', 4); }
      if (!d.clap) d.prompt = false;
      // 合击真的按出来了才记旗标（JA_MAGNET_CLAP.onStart 自己 c.end()，这里只读招式 id）
      if (p.atk && p.atkId === 'JA_MAGNET_CLAP' && !d.clapDone) { d.clapDone = true; F().ch9Clap = true; }
    }
    // ---- 第二段：火车（每 15 s，放水 20 s；预警 1.5 s → 0.45 s 冲过，伤 40，不能挡）
    if (d.phase === 'rail') {
      if (c.t >= d.trainAt && !d.trainOn) {
        d.trainOn = true;
        d.trainWarnUntil = c.t + 1.5;
        d.trainHitAt = c.t + 1.5;
        snd('train_horn', null, { vol: .8 });
        S.shake(1, 1.5);
        S.state('rumble', 1);
      }
      if (d.trainOn && d.trainHitAt && c.t >= d.trainHitAt) {
        d.trainHitAt = 0;
        // 车从右往左冲过 0.45 s：铁轨带上碰到就是伤 40，不能挡
        const tr = c.spawn({ cid: 'prop:train', x: 720, y: footY('rail_ch9', 172), team: 'object', untargetable: true });
        d.trainProp = tr; d.trainPassAt = c.t;
        // 放水可叠加：手工减免统一走 G.combat.assistK，第 1 档与原系数一致
        // 放水时这类剧情危险区没有 owner，引擎的放水倍率不会作用，所以这里手工乘
        c.hazard({ shape: 'rect', x0: arenaX0(c), x1: arenaX1(c), y0: railBand[1], y1: railBand[3], warn: 0, dur: .45, dmg: Math.round(40 * G.combat.assistK(c, .6)), once: true, guard: 'none' });
      }
      // 火车冲过（tick 里不能压 S.animate 的新 tick，自己按 c.t 插值）
      if (d.trainProp && d.trainPassAt) {
        const u = Math.min(1, (c.t - d.trainPassAt) / .45);
        if (!d.trainProp.remove) d.trainProp.x = G.lerp(720, -90, u);
        if (u >= 1) { d.trainProp.remove = true; d.trainProp = null; d.trainPassAt = 0; }
      }
      if (d.trainOn && d.trainWarnUntil && c.t >= d.trainWarnUntil + .5) {
        d.trainWarnUntil = 0;
        d.trainOn = false;
        d.trainAt = c.t + (c.assist ? 20 : 15);
        S.state('rumble', 0);
        if (d.trainProp) { d.trainProp.remove = true; d.trainProp = null; }
      }
    }
  }
  const pfX = () => RP('platform')[0], tkX = () => RP('tracks')[0];
  const arenaX0 = c => c.spec.arena[0], arenaX1 = c => c.spec.arena[1];
  // 9-15 夹扁：两人身上的废铁同时脱离，从两边飞向中间（metal_junk ×8）→ 玛丽亚 hurt → down → saiki
  async function squeeze(S, mariah, c) {
    calmStands();
    const e = mariah || (c && c.boss) || S.actor('c9_mariah');
    // 铁路段的像素层（铁轨闪红 / 影子）留在 rail_ch9 的 props 上，战斗结束就收掉，别让它跟着下一张图
    const railStage = G.STAGES.rail_ch9;
    if (railStage) railStage.props = (railStage.props || []).filter(q => q.id !== 'c9_bast');
    // 她被夹扁以后不再站在街上：从地图定义里摘掉（后面 9-16 还要回 luxor_ch9，不摘会再长出来）
    luxorPrune(S, { npcs: ['c9_mariah'] });
    const p = S.player;
    const mid = e ? e.x : p.x + 60;
    // 8 个废铁从两边飞向中间
    for (let i = 0; i < 8; i++) {
      const fromLeft = i % 2 === 0;
      const junk = T.prop(S, 'metal_junk', mid + (fromLeft ? -90 : 90), (e ? e.y : p.y) - 10 - (i % 3) * 4, { id: 'c9_junk' + i, z: 12, frame: i % 4 });
      if (junk) S.arc(junk, mid + (fromLeft ? 2 : -2), (e ? e.y : p.y) - 12, 10, .35).catch(G.cancelIgnore);
      if (i % 3 === 2) snd('magnet_clack', 'metal_drop', { vol: .55 });
    }
    await S.wait(.5);
    snd('magnet_clack', 'metal_drop', { vol: .6 });
    if (e) {
      S.pose(e, 'hurt');
      S.fx('burst', { x: e.x, y: e.y - 22, n: 18, colours: ['#d8d0b8', '#8c8478'] });
      S.shake(3, .3);
      await S.wait(.25);
      S.pose(e, 'down');
    }
    await S.title('saiki');
    await S.say('mariah', '怎么可能……把我的磁力反过来……', e ? { actor: e } : {});
    for (const a of G.world.stage.actors) if (a.cid === 'prop:metal_junk' && String(a.id).indexOf('c9_junk') === 0) a.remove = true;
    if (e) e.remove = true;
    await lines(S, [['joseph', '……两个大男人把一位女士夹在中间……这一幕，可千万不能让荷莉看见。'],
      ['avdol', '……乔斯达先生，请先把你身上的罐头拿下来。'],
      ['joseph', '脚终于听使唤了！']]);
  }

  // ================================================================ 9-16 影子（同一时间）
  async function shadowScare(S) {
    calmStands();
    // 分头：卢克索组只剩承太郎、波鲁纳雷夫、伊奇
    S.party(['jotaro', 'polnareff', 'iggy'], { leader: 'jotaro' });
    for (const a of G.party.members) { a.visible = true; a.alpha = 1; a.scale = 1; a.hold = false; a.speed = kidSafeSpeed(a); }
    const washer = LT('washer'), door = LT('house_door');
    await S.setStage('luxor_ch9', { x: washer[0] - 160, y: footY('luxor_ch9', 164), music: 'tension' });
    // 承太郎 @washer−80、波鲁纳雷夫 −50（走在前面）、伊奇 −100
    const y = footY('luxor_ch9', washer[1]);
    for (const [cid, dx, dy] of [['jotaro', -80, 0], ['polnareff', -50, 0], ['iggy', -100, 3]]) place(S, cid, washer[0] + dx, y + dy, 1);
    // 擦窗工人在 @washer，背对着阳光（光从右边来，影子往左拉得很长）
    const al = S.actor('c9_washer');
    if (al) { al.x = washer[0]; al.y = y; al.facing = 1; al.talk = null; al.standReact = false; al.visible = true; }
    const sh = pixelOnce('c9_longshadow', P => {
      const x = Math.round(washer[0] - (G.cam.x || 0)), yy = Math.round(y - (G.cam.y || 0));
      px.poly(P, [[x - 6, yy], [x + 6, yy], [x - 90, yy + 3], [x - 84, yy - 2]], '#16101e', .5);
    });
    S.camera(washer[0] - 80);
    await S.say(null, '同一时间——');
    await S.say('polnareff', '乔斯达先生他们不会有事吧……喂，大叔，让一让！');
    S.camera(null);
    // 一脚踩进影子里：倒卷 + 画面横向抖 + 去色
    snd('rewind', 'time_resume', { vol: .7 });
    S.filter('gray', .7, { dur: .3 });
    S.shake(3, .3);
    await S.wait(.35);
    // 波鲁纳雷夫变成小孩
    const po = S.actor('polnareff');
    const px0 = po ? po.x : washer[0] - 50;
    if (po) { po.visible = false; po.follow = null; }
    const kid = S.spawn('polnareff_kid', px0, y + 2, { id: 'c9_kid_intro', team: 'npc', name: '波鲁纳雷夫' });
    kid.facing = 1; kid.standReact = false; kid.talk = null;
    S.pose(kid, 'shock', { freeze: 0 });
    await S.wait(.2);
    await S.say('polnareff_kid', '……咦？我的声音怎么……？！', { name: '波鲁纳雷夫', actor: kid });
    S.unpose(kid);
    if (al) { al.facing = -1; al.speed = 30; }
    await S.say('alessi', '了、了不起哟……小孩子，最可爱了。', { name: '擦窗工人', actor: al });
    if (al) al.facing = 1;
    S.nameCard('alessi');
    await S.title('god_seth');
    await S.say('polnareff_kid', '哇啊啊啊！', { name: '波鲁纳雷夫', actor: kid });
    S.filter(null);
    // 往右跑进民宅的门，跑到门口渐隐
    if (sh) { sh.hidden = true; W.stage.props = W.stage.props.filter(q => q !== sh); }
    S.walk(kid, door[0], footY('luxor_ch9', door[1]), { speed: 120, anim: 'run' }).catch(G.cancelIgnore);
    await S.animate(.75, k => { kid.alpha = 1 - Math.max(0, (k - .7) / .3); });
    kid.remove = true;
    // 承太郎追上去的时候也踩进了影子
    await S.say('jotaro', '波鲁纳雷夫！');
    snd('rewind', 'time_resume', { vol: .7 }); S.shake(3, .3); S.filter('gray', .7, { dur: .3 });
    await S.wait(.4);
    S.filter(null);
    const jt = S.actor('jotaro');
    if (jt) { jt.visible = false; jt.follow = null; }
    if (al) al.remove = true;
    S.mark('b20a_seth');
  }
  // 藏身点（框 = 家具的框，画砍痕 / 帽子尖用）
  //   顺序照第9章自动测试的 HIDE_ORDER（wardrobe / aquarium / bed / curtain / crate / cupboard）：
  //   testHint.search 是这里的下标，测试器按 HIDE_ORDER[search] 走到“阿莱西正在搜的那一处”，顺序不一致就站错地方。
  function hides() {
    return [
      { key: 'wardrobe', name: '衣柜', x: LH('hide_wardrobe')[0] },
      { key: 'aquarium', name: '鱼缸', x: LH('hide_aquarium')[0] },
      { key: 'bed', name: '床底', x: LH('hide_bed')[0] },
      { key: 'curtain', name: '窗帘', x: LH('hide_curtain')[0] },
      { key: 'crate', name: '木箱', x: LH('hide_crate')[0] },
      { key: 'cupboard', name: '橱柜', x: LH('hide_cupboard')[0] },
    ];
  }
  // 9-17 段 1：小孩波鲁纳雷夫的躲猫猫（b20a_seth）
  async function fightKidPol(S) {
    const HS = hides();
    // 进民宅：这一段在家里打
    await M.scene(S, 'house_ch9', null, LH('arrive')[0], 'jotaro');
    const kid = S.setPlayer('polnareff_kid', { hp: 100, speed: 70, x: LH('hide_aquarium')[0] + 60, y: footY('house_ch9', 160), kit: 'polnareff_kid' });
    kid.facing = 1;
    try {
      await M.objectFight(S, {
        id: 'b20a_seth', swap: false, bench: 'hide', arena: [0, 640], coverage: false, music: 'tension', par: 90, dmgScale: 1,
        testHint: c => ({ hides: HS.map(h => [h.key, h.x]), hidden: c.data.hidden || null, ambush: c.data.ambush,
          age: Math.round((c.data.age || 0) * 10) / 10, search: c.data.search, backTurned: !!c.data.backTurned }),
        tick(c, dt) { sethTick(S, c, dt, HS); },
        after: async (s, es) => { s.insertUI(null); if (es[0]) es[0].remove = true; F().ch9Ambush = 2; },
      }, c => {
        const p = c.player;
        Object.assign(c.data, {
          hidden: null, ambush: 0, age: 9, i: 0, search: 0, backTurned: false,
          phase: 'walk', until: 0, warnUntil: 0, searchBox: null, aqTip: false, speeds: 70,
        });
        for (const h of HS) S.state('axe_' + h.key, 0);   // 重来时家具复原
        failLine(c, '呜……');
        p.x = LH('hide_aquarium')[0] + 60; p.y = footY('house_ch9', 160); p.alpha = 1; p.speed = 70;
        // 阿莱西：这一段只按顺序搜藏身点（brain 停掉，走位 / 举斧 / 砍都在 tick 里）
        const e = c.spawn({ cid: 'alessi', boss: true, hp: 1300, minHp: 1000, armor: true, brain: () => true,
          x: LH('hide_cupboard')[0] + 40, y: footY('house_ch9', 160) });
        e.facing = -1;
        pixelOnce('c9_house', P => drawHouse(P, c, HS));
        M.ui(S, g => M.hud(g, ['年龄 ' + Math.ceil(c.data.age) + ' 岁　伏击 ' + c.data.ambush + '/2',
          c.data.hidden ? '躲好了：等他背对你走近，K＋J 偷袭！' : 'E 躲进藏身处（鱼缸最好），避开他的斧头'], 44));
        S.hint('E 躲进藏身处（鱼缸最好）；他砍过来之前先躲好。', 8);
      });
    } finally {
      const adult = G.party.get('jotaro');
      for (const a of G.world.stage.actors) if (a.cid === 'polnareff_kid' || a.cid === 'jotaro_kid') a.remove = true;
      for (const a of G.world.stage.actors) if (a.cid === 'alessi' && a.team === 'enemy') a.remove = true;
      if (adult) { W.player = adult; adult.team = 'player'; adult.follow = null; adult.visible = false; adult.hold = false; }
    }
  }
  function drawHouse(P, c, HS) {
    const d = c.data, e = c.boss, cx = G.cam.x || 0, cy = G.cam.y || 0;
    // 影子：从天花板吊灯 @lamp 的方向往外拉长（40–90 px，随他离灯的距离变）
    if (e && !e.remove) {
      const lamp = LH('lamp');
      const len = G.clamp(40 + Math.abs(e.x - lamp[0]) * .45, 40, 90);
      const dir = e.x >= lamp[0] ? 1 : -1;
      const x = Math.round(e.x - cx), y = Math.round(e.y - cy);
      px.poly(P, [[x - 5, y], [x + 5, y], [x + dir * (len + 6), y + 4], [x + dir * len, y - 1]], '#120e1c', .55);
    }
    // 举斧预警：家具框闪红
    if (d.searchBox && c.t < d.warnUntil) {
      const box = d.searchBox, x0 = box[0] - cx, x1 = box[2] - cx, y0 = box[1] - cy, y1 = box[3] - cy;
      const col = Math.floor(c.t * 15) % 2 ? '#ff5040' : '#a81c18';
      px.line(P, x0, y0, x1, y0, col, .9); px.line(P, x1, y0, x1, y1, col, .9);
      px.line(P, x0, y1, x1, y1, col, .9); px.line(P, x0, y0, x0, y1, col, .9);
    }
    // 躲着时家具框里露出两三个像素的帽子尖（波鲁纳雷夫小孩的发色）
    if (d.hidden) {
      const h = HS.find(z => z.key === d.hidden);
      if (h) {
        const box = LH('hide_' + h.key + '_box');
        const x = Math.round((box[0] + box[2]) / 2 - cx), y = Math.round(box[3] - 2 - cy);
        px.rect(P, x - 1, y - 2, 3, 2, '#e8e8f2');
        px.rect(P, x - 1, y, 3, 1, '#c8c8dc');
      }
    }
  }
  function sethTick(S, c, dt, HS) {
    const d = c.data, p = c.player, e = c.boss;
    if (!e || e.remove) return;
    const walkSpd = 38;
    // ---- 躲藏：26 px 内按 E 进去 / 再按 E 出来
    if (I.okHit()) {
      I.consumeOk();
      if (d.hidden) d.hidden = null;
      else {
        const near = HS.find(h => Math.abs(h.x - p.x) < 26);
        if (near) {
          d.hidden = near.key;
          p.x = near.x; p.y = footY('house_ch9', 160);
          if (near.key === 'aquarium' && !d.aqTip) { d.aqTip = true; S.hint('他背对鱼缸走近时，K＋J 偷袭！', 6); }
        }
      }
    }
    p.alpha = d.hidden ? .25 : 1;
    p.speed = d.hidden ? 0 : d.speeds;
    // ---- 年龄：站进影子里每秒 −5 岁（放水 −3），到 4 岁失败
    //   只在“站着不动”时才变老：跑动 / 出招 / 闪避 / 挨打中的那一下不算（真人也是站定了才被影子吃到）。
    //   照原来“只要在影子里就掉”的写法，去鱼缸的路上路过阿莱西脚边 1 s 就直接变成婴儿，
    //   躲猫猫根本来不及躲（2026-10-20 路线实测）。
    const lamp = LH('lamp');
    const len = G.clamp(40 + Math.abs(e.x - lamp[0]) * .45, 40, 90);
    const dir = e.x >= lamp[0] ? 1 : -1;
    const inShadow = !d.hidden && (p.x - e.x) * dir > 0 && Math.abs(p.x - e.x) <= len && Math.abs(p.y - e.y) <= 12;
    const busy = !!p.atk || p.state === 'walk' || p.state === 'dodge' || p.state === 'hurt' || p.state === 'special';
    d.stillT = inShadow && !busy ? (d.stillT || 0) + dt : 0;
    if (d.stillT > .35) d.age = Math.max(0, d.age - dt * (c.assist ? 3 : 5));
    if (d.age <= 4) { c.fail('变成小婴儿了……'); return; }
    // ---- 阿莱西按顺序一处处搜：走到藏身点前 38 px/s → 举斧预警 45f（放水 70f）→ 砍 → 3.5 s 后下一处
    d.search = d.i || 0;
    const H = HS[d.search];
    d.searchBox = LH('hide_' + H.key + '_box');
    if (d.phase === 'walk') {
      const dx = H.x - e.x;
      if (Math.abs(dx) > 8) { W.move(e, G.clamp(dx, -walkSpd * dt, walkSpd * dt), 0); e.facing = dx > 0 ? 1 : -1; e.play('walk'); }
      else {
        e.facing = dx >= 0 ? 1 : -1;
        d.phase = 'warn';
        d.warnUntil = c.t + (c.assist ? 70 / 60 : 45 / 60);
        e.play('axe');
        c.hazard({ owner: e, shape: 'rect', x0: H.x - 26, x1: H.x + 26, y0: 145, y1: 178,
          warn: c.assist ? 70 / 60 : 45 / 60, dur: .12, dmg: 16, once: true, guard: 'none', sfx: 'axe_chop',
          onActive: () => { S.state('axe_' + H.key, 1); },
          onHit: (h, t2, r) => {
            if (t2 !== p || !r.dmg) return;
            S.flash(2 / 60, 1, '#ffffff'); S.sfx('thud', .8); S.sfx('kid_cry', .4); S.word('咚', p);
            if (d.hidden) d.hidden = null;
          } });
      }
    } else if (d.phase === 'warn') {
      if (c.t >= d.warnUntil) { d.phase = 'wait'; d.until = c.t + 3.5; d.warnUntil = 0; e.play('idle'); }
    } else if (c.t >= d.until) {
      d.i = (d.search + 1) % HS.length;
      d.phase = 'walk';
    }
    // ---- 背对鱼缸：伏击条件（KIDPOL_AMBUSH 自己判定，这里只给测试器读）
    const aqX = LH('hide_aquarium')[0];
    d.backTurned = (aqX - e.x) * e.facing < 0 && Math.abs(aqX - e.x) <= 90;
    if (d.ambush >= 2) c.end();
  }

  // ================================================================ 9-18 小学生承太郎（b20b_seth）
  async function kidJotaro(S) {
    calmStands();
    const door = LH('door'), aq = LH('hide_aquarium');
    // 阿莱西捂着鼻子退到门口
    const al = S.spawn('alessi', door[0] + 30, footY('house_ch9', 158), { id: 'c9_alessi_door', team: 'npc', name: '阿莱西' });
    al.facing = 1; al.standReact = false; al.talk = null;
    al.tint = { color: '#b568f2', k: .3 };
    await S.say('alessi', '好、好痛……！小鬼，竟敢——', { actor: al });
    // 门被一脚踢开：小学生承太郎站在门口，背着书包
    S.sfx('door', .7); S.shake(2, .2);
    const kid = S.setPlayer('jotaro_kid', { hp: 130, speed: 64, x: door[0], y: footY('house_ch9', 160), kit: 'jotaro_kid' });
    kid.facing = 1; kid.z = 0;
    // 小孩波鲁纳雷夫躲在鱼缸后面
    const pol = S.spawn('polnareff_kid', aq[0] + 6, footY('house_ch9', 158), { id: 'c9_kid_hide', team: 'npc', name: '波鲁纳雷夫' });
    pol.facing = 1; pol.standReact = false; pol.talk = null;
    S.pose(pol, 'hide', { freeze: 0 });
    await S.say('jotaro_kid', '……你就是把大人变成小孩的家伙？', { name: '小学生承太郎', actor: kid });
    await S.say('alessi', '了、了不起哟……没有替身的小学生，能拿我怎么样？', { actor: al });
    await S.say('jotaro_kid', '……试试看。', { name: '小学生承太郎', actor: kid });
    al.remove = true;
    S.mark('b20b_seth');
  }
  async function fightKidJotaro(S) {
    // 段 2 直接用 kidJotaro 里换好的小学生（开发入口没有那一步，这里补一次）
    if (!W.player || W.player.cid !== 'jotaro_kid') S.setPlayer('jotaro_kid', { hp: 130, speed: 64, x: LH('door')[0], y: footY('house_ch9', 160), kit: 'jotaro_kid' });
    W.player.facing = 1;
    try {
      await M.objectFight(S, {
        id: 'b20b_seth', swap: false, bench: 'hide', arena: [0, 640], coverage: false, music: 'battle_egypt', par: 70, dmgScale: 1,
        testHint: c => ({ age: Math.round((c.data.age || 0) * 10) / 10, begged: !!c.data.begged, hp: c.boss ? c.boss.hp : 0 }),
        tick(c, dt) { sethTick2(S, c, dt); },
        after: async (s, es) => { s.insertUI(null); if (es[0]) es[0].remove = true; },
      }, c => {
        const p = c.player;
        Object.assign(c.data, { age: 9, begged: false });
        assistScale(c);
        failLine(c, '……还……没完……');
        p.x = LH('door')[0] - 10; p.y = footY('house_ch9', 160); p.alpha = 1;
        const e = c.spawn({ cid: 'alessi', boss: true, hp: 1000, minHp: 390, x: LH('door')[0] + 60, y: footY('house_ch9', 160) });
        e.facing = -1;
        pixelOnce('c9_house2', P => drawHouse2(P, c));
        M.ui(S, g => M.hud(g, ['年龄 ' + Math.ceil(c.data.age) + ' 岁', '小学生承太郎：没有替身也照样揍人', 'J 三连，K 闪开斧头；别站进他的影子'], 44));
        S.hint('J 三连，K 闪开斧头；别站进他的影子。', 8);
      });
    } finally {
      const adult = G.party.get('jotaro');
      for (const a of G.world.stage.actors) if (a.cid === 'polnareff_kid' || a.cid === 'jotaro_kid') a.remove = true;
      for (const a of G.world.stage.actors) if (a.cid === 'alessi' && a.team === 'enemy') a.remove = true;
      if (adult) { W.player = adult; adult.team = 'player'; adult.follow = null; adult.visible = false; adult.hold = false; }
    }
  }
  function drawHouse2(P, c) {
    const e = c.boss, cx = G.cam.x || 0, cy = G.cam.y || 0;
    if (e && !e.remove) {
      const lamp = LH('lamp');
      const len = G.clamp(40 + Math.abs(e.x - lamp[0]) * .45, 40, 90);
      const dir = e.x >= lamp[0] ? 1 : -1;
      const x = Math.round(e.x - cx), y = Math.round(e.y - cy);
      px.poly(P, [[x - 5, y], [x + 5, y], [x + dir * (len + 6), y + 4], [x + dir * len, y - 1]], '#120e1c', .55);
    }
  }
  function sethTick2(S, c, dt) {
    const d = c.data, p = c.player, e = c.boss;
    if (!e || e.remove) return;
    // 影子：同段 1（年龄 9 → 4 失败）
    const lamp = LH('lamp');
    const len = G.clamp(40 + Math.abs(e.x - lamp[0]) * .45, 40, 90);
    const dir = e.x >= lamp[0] ? 1 : -1;
    d.inShadow = (p.x - e.x) * dir > 0 && Math.abs(p.x - e.x) <= len && Math.abs(p.y - e.y) <= 12;
    // 同段 1：只在站着不动时才变老（出招 / 走位 / 闪避 / 挨打的那一下不算）
    const busy = !!p.atk || p.state === 'walk' || p.state === 'dodge' || p.state === 'hurt' || p.state === 'special';
    d.stillT = d.inShadow && !busy ? (d.stillT || 0) + dt : 0;
    if (d.stillT > .35) d.age = Math.max(0, d.age - dt * (c.assist ? 3 : 5));
    if (d.age <= 4) { c.fail('变成小婴儿了……'); return; }
    // 求饶（只一次）：HP ≤ 700
    if (e.hp <= 700 && !d.begged) {
      d.begged = true;
      M.task(c, async () => {
        e.atk = null; e.tele = null; e.play('beg');
        S.sfx('metal_drop', .5);
        await S.say('alessi', '饶了我……我不会再做坏事了！', { actor: e, pos: 'bottom' });
        const pick2 = await S.choice(['不信', '相信他'], '阿莱西跪下了');
        if (pick2 === 0) await S.say(null, '小承太郎握紧了拳头。', { pos: 'bottom' });
        else {
          S.flash(.2, .7, '#ffffff');
          snd('knife_hit', 'stab', { vol: .6 });
          M.drain(c, 16);
          await S.say(null, '……他根本没打算悔改。', { pos: 'bottom' });
        }
        if (J.valid(c)) { e.play('idle'); e.cool = .8; }
      });
    }
    if (e.hp <= 390) c.end();
  }

  // ================================================================ 9-19 了、了不起哟
  async function finale(S) {
    calmStands();
    const door = LT('house_door');
    luxorPrune(S, { npcs: ['c9_washer'] });
    await S.setStage('luxor_ch9', { x: door[0] - 60, y: footY('luxor_ch9', 162), music: 'tension' });
    // 阿莱西跌坐在街上
    const al = S.spawn('alessi', door[0] + 20, footY('luxor_ch9', 164), { id: 'c9_alessi_down', team: 'npc', name: '阿莱西' });
    al.facing = 1; al.standReact = false; al.talk = null;
    S.pose(al, 'down');
    // 影子缩回去：倒卷的音效再放一次（时间正过来）
    snd('rewind', 'time_resume', { vol: .7 }); S.shake(2, .3);
    // 承太郎、波鲁纳雷夫恢复原样
    for (const a of G.world.stage.actors) if (a.cid === 'jotaro_kid' || a.cid === 'polnareff_kid') a.remove = true;
    S.party(crew, { leader: 'jotaro' });
    for (const a of G.party.members) { a.visible = true; a.alpha = 1; a.scale = 1; a.hold = false; a.follow = null; a.speed = kidSafeSpeed(a); S.unpose(a); }
    place(S, 'jotaro', door[0] - 40, footY('luxor_ch9', 162), 1);
    place(S, 'polnareff', door[0] - 16, footY('luxor_ch9', 164), 1);
    await S.wait(.4);
    await S.say('polnareff', '恢复了！承太郎！');
    await S.say('alessi', '等、等一下！我们好好商量——', { actor: al });
    await S.say('jotaro', '欧拉。');
    // 白金之星欧拉连打 + 银色战车千本刺（自动演出 1 s）
    S.sfx('ora_rush'); S.sfx('slash1', .7);
    S.fx('rush', { x: al.x - 20, y: al.y - 20, fist: 'starplat', dur: 1 });
    S.shake(3, .6);
    await S.wait(.5);
    S.pose(al, 'hurt');
    S.arc(al, al.x + 220, al.y - 10, 60, .7).catch(G.cancelIgnore);
    await S.wait(.8);
    al.remove = true;
    await S.say('alessi', '了、了不起哟……！');
    await S.title('saiki');
    // 乔瑟夫、阿布德尔从左边走过来，身上还挂着几只罐头；伊奇跟在后面
    for (const [cid, dx] of [['joseph', -150], ['avdol', -118], ['iggy', -96]]) {
      const a = S.actor(cid);
      if (!a) continue;
      a.visible = true; a.follow = null; a.speed = kidSafeSpeed(a);
      a.x = door[0] + dx; a.y = footY('luxor_ch9', 164);
      S.walk(a, door[0] + dx + 90, footY('luxor_ch9', 164), { speed: 70 }).catch(G.cancelIgnore);
    }
    await S.wait(.9);
    // 身上还挂着几只罐头
    for (const cid of ['joseph', 'avdol']) {
      const a = S.actor(cid); if (!a) continue;
      for (let i = 0; i < 2; i++) T.prop(S, 'metal_junk', a.x - 4 + i * 6, a.y - 16 - i * 4, { id: 'c9_endcan', z: 12, frame: i });
    }
    await lines(S, [['joseph', '你们那边也打完了？……波鲁纳雷夫，你怎么一身木屑？'], ['polnareff', '……别问。']]);
    // 队伍恢复五人 + 花京院灰
    S.party([...crew, 'kakyoin'], { leader: 'jotaro' });
    const ky = G.party.get('kakyoin');
    if (ky) { ky.mem.bandage = true; ky.talk = null; }
    G.party.remove('kakyoin', { look: 'gray' });
    follow();
    await S.setStage('map_ch9', { x: 100, y: 160, music: 'travel' });
    await S.route(['卢克索', '开罗'], { vehicle: 'car', day: 35, left: 16,
      history: ['东京', '香港', '新加坡', '加尔各答', '瓦拉纳西', '卡拉奇', '红海', '阿斯旺', '卢克索'] });
  }

  // ================================================================ 本章入口
  G.STORY.ch9 = async S => {
    T.resetCounters();
    for (const key of ['ch9Quiz', 'ch9QuizSeen', 'ch9Sanctum', 'ch9Barber', 'ch9Mirror', 'ch9Socket', 'ch9Shadow', 'ch9Skip',
      'ch9Anubis', 'ch9Clap', 'ch9Ambush']) delete F()[key];
    memory.length = 0;
    await M.ensureBg('_ch9');
    party(S, 'jotaro');
    // 篇章卡 → 航线（阿斯旺 → 科翁坡，第 32 天）
    await S.run(async s => {
      await s.chapterCard('ch9');
      await s.setStage('map_ch9', { x: 100, y: 160, music: 'travel' });
      await s.route(['阿斯旺', [46, 78]], { vehicle: 'car', day: 32, left: 19,
        history: ['东京', '香港', '新加坡', '加尔各答', '瓦拉纳西', '卡拉奇', '红海'] });
      await templeIntro(s);
    });
    await templeExplore(S);
    await S.run(async s => {
      await polWanders(s);
      await fightChaka(s);
      await throwNile(s);
      // 科翁坡 → 下一个镇（第 33 天）
      await s.setStage('map_ch9', { x: 100, y: 160, music: 'travel' });
      await s.route([[46, 78], [47, 74]], { vehicle: 'car', day: 33, left: 18,
        history: ['东京', '香港', '新加坡', '加尔各答', '瓦拉纳西', '卡拉奇', '红海', '阿斯旺'] });
      await nileIntro(s);
    });
    await nileExplore(S);
    await S.run(async s => {
      await barber(s);
      await fightKhan(s);
      await possessed(s);
      await fightPossessed(s);
      await kidTrip(s);
      // 下一个镇 → 卢克索（第 34 天）
      await s.setStage('map_ch9', { x: 100, y: 160, music: 'travel' });
      await s.route([[47, 74], '卢克索'], { vehicle: 'car', day: 34, left: 17,
        history: ['东京', '香港', '新加坡', '加尔各答', '瓦拉纳西', '卡拉奇', '红海', '阿斯旺'] });
      await luxorIntro(s);
    });
    await luxorExplore(S);
    await S.run(async s => {
      await socketScare(s);
      await fightBast(s);
      await shadowScare(s);
      await fightKidPol(s);
      await kidJotaro(s);
      await fightKidJotaro(s);
      await finale(s);
    });
    await M.end(S, 'ch9_complete');
  };

  // ================================================================ 单战入口（开发调参 G.DEV / 标题「挑战」）
  G.DEV = G.DEV || {};
  G.DEV.ch9Anubis = async S => {
    await M.ensureBg('_ch9');
    party(S, 'polnareff');
    // 试炼的挑战入口与工厂共用同一条三段流程（布景、换图、Actor 复用都在工厂里）
    await G.TRIAL_SRC['b18a_anubis'].run(S, STORY);
  };
  // 只开第三段（被附身的波鲁纳雷夫）：调测试器打法时不必每次先打完前两段（那要十分钟）；记招从空开始，所以不是通关证据
  G.DEV.ch9Possessed = async S => {
    await M.ensureBg('_ch9');
    memory.length = 0;
    party(S, 'jotaro');
    await S.run(async s => {
      // 和真实流程一样用 setupNile 摆这张图（渔夫等探索阶段的 NPC 都在场），否则复现不了“NPC 挡在开场玩家旁边”
      await M.scene(S, 'nile_ch9', setupNile, NB('arrive')[0] + 70, 'jotaro');
      const pol = S.spawn('polnareff_possessed', NB('arrive')[0] + 390, footY('nile_ch9', 162), { id: 'c9_pol_possessed', team: 'npc', name: '波鲁纳雷夫？', stand: 'chariot' });
      pol.facing = -1; pol.standReact = false; pol.talk = null;
      await fightPossessed(s);
      if (pol) pol.remove = true;
    });
  };
  G.DEV.ch9Bast = async S => {
    await M.ensureBg('_ch9');
    S.party(['joseph', 'avdol'], { leader: 'joseph' });
    await S.setStage('luxor_ch9', { x: LT('socket_stand')[0] - 40, y: footY('luxor_ch9', 162), music: 'battle' });
    await G.TRIAL_SRC['b19_bast'].run(S, STORY);
  };
  G.DEV.ch9Seth = async S => {
    await M.ensureBg('_ch9');
    party(S, 'jotaro');
    await S.run(async s => {
      await fightKidPol(s);
      await kidJotaro(s);
      await fightKidJotaro(s);
    });
  };
  // ================================================================ 星尘试炼关卡工厂（挑战入口与剧情路径共用）
  G.TRIAL_SRC['b18a_anubis'] = {
    chapter: 'ch9', pack: '_ch9',
    run: async (S, o) => {
      await M.ensureBg('_ch9');
      memory.length = 0;    // 记招数组三段共享：每次进关都从空开始，否则上一轮的招会带进来
      await S.run(async s => {
        await s.setStage('temple_ch9', { x: TP('arrive')[0] + 70, y: footY('temple_ch9', 164), music: 'battle' });
        if (!o.trial) S.setLeader('polnareff', { force: true, silent: true });
        await fightChaka(s, o);
        await s.setStage('nile_ch9', { x: NB('barber_chair')[0] - 40, y: footY('nile_ch9', 162), music: 'battle' });
        S.state('chair_cut', 1);
        await fightKhan(s, o);
        // 被附身的是独立的 NPC Actor：试炼队伍里可能本来就有 polnareff，不能拿队伍成员当 Boss
        const pol = S.spawn('polnareff_possessed', NB('arrive')[0] + 390, footY('nile_ch9', 162), { id: 'c9_pol_possessed', team: 'npc', name: '波鲁纳雷夫？', stand: 'chariot' });
        pol.facing = -1; pol.standReact = false; pol.talk = null;
        await fightPossessed(s, o);
        if (pol) pol.remove = true;
      });
    },
  };
  G.TRIAL_SRC['b19_bast'] = {
    chapter: 'ch9', pack: '_ch9',
    run: async (S, o) => {
      await M.ensureBg('_ch9');
      // 剧情 / 挑战路径的布景由调用方负责；试炼自己从卢克索街道的插座前开打
      if (o.trial) await S.setStage('luxor_ch9', { x: LT('socket_stand')[0] - 40, y: footY('luxor_ch9', 162), music: 'battle' });
      await S.run(async s => { await fightBast(s, o); });
    },
  };
  X.challenge({ id: 'b18a_anubis', chapter: 'ch9', title: 'VS 阿努比斯神（三段）', par: 90, run: S => G.DEV.ch9Anubis(S) });
  X.challenge({ id: 'b19_bast', chapter: 'ch9', title: 'VS 巴斯特女神（乔瑟夫 / 阿布德尔）', par: 120, run: S => G.DEV.ch9Bast(S) });
  X.challenge({ id: 'b20a_seth', chapter: 'ch9', title: 'VS 塞特神（小孩波鲁纳雷夫 → 小学生承太郎）', par: 90, run: S => G.DEV.ch9Seth(S) });
})();
