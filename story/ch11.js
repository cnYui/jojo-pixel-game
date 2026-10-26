// 第11章　DIO 的馆 / 日落之前（规划 §6.10；原著 227–246 话，游戏内第 49 天下午 → 日落）
//   2026-10-20 照 `游玩脚本\ch11_DIO的馆.md` 整章重写。初版的 lightSoul / baseball / labyrinth / creamHidden /
//   creamSun / L.runner 规则沿用，画面和台词按脚本重做，写死的坐标全部换成背景锚点（背景挪位置剧情跟着走）。
//
//   流程：馆门口（花京院归队）→ 威压 → 自由走动 → 走廊（泰伦斯带路、地板翻开）→ 海中小岛 → F-MEGA 赛车（CRT 伪 3D）
//   → 棒球（三振 4 次赢）→ 游戏室 → 幻觉走廊（假墙三个变体）→ 大厅（阿布德尔、奶油）→ 塔顶（努凯萨克、开棺）
//
//   克制处理：瓦尼拉献头只有一滴落下的声音；阿布德尔被抹消用光（白色碎片往上飘，不画手）；伊奇之死用灵魂上升；
//   瓦尼拉化灰只有灰往上飘；努凯萨克在棺材里只给一顶帽子的空镜。
//
//   背景（10-19 / 10-20 已接入）：mansion_exterior、mansion_corridor、game_room、illusion_corridor、mansion_hall、
//   mansion_tower、crt_baseball。背景 key 在数据包的 layers 里（night / trap / crt / hole / variant / cracked / open /
//   menace / breach / beam），剧情只改 stage.state，图层由背景自己挑。
'use strict';
(function () {
  const G = window.G, W = G.world, T = G.TPL, L = G.LATE, F = () => G.flags, X = G.EXTRA;
  G.TRIAL_SRC = G.TRIAL_SRC || {};   // 星尘试炼的关卡工厂（本文件末尾登记）
  const I = G.input;
  // A 队：承太郎 / 乔瑟夫 / 花京院（第 24 战）；B 队：阿布德尔 / 波鲁纳雷夫 / 伊奇（第 25、26 战）
  const ALL = ['jotaro', 'joseph', 'kakyoin', 'avdol', 'polnareff', 'iggy'];
  const TEAM_A = ['jotaro', 'joseph', 'kakyoin'];
  const TEAM_B = ['avdol', 'polnareff', 'iggy'];
  const lines = (S, rows) => L.lines(S, rows);
  // 音效名都过一遍白名单：数据包里没有的名字直接播会记 missingSfx（验收里算错误）
  //   注意 crack / punch / sand_wind 这几个在数据包里没有，别写进白名单，否则等于没兜底
  const SND = new Set(('baseball_hit bird_screech car_engine clang crash door drip emerald_shot explosion ' +
    'fire_burst glass_break glint gunshot heat_beam ice knife_volley ko_hit menacing metal_crunch muda_loop ' +
    'punch0 punch1 punch_heavy sand sand_storm sax_melody skid soul_drain sparkle stand_summon_fool sting_reveal ' +
    'teeth_crunch thud thunder time_resume timestop tv_game vine void_eat wall_slam water_splash whoosh wind_loop ' +
    'zap crowd coin card_flip coin').split(' '));
  const snd = (name, alt, o = {}) => {
    const n = SND.has(name) ? name : (SND.has(alt) ? alt : null);
    if (n) G.audio.sfx(n, o);
  };
  const amb = (S, name, alt, vol = .2) => {
    const n = SND.has(name) ? name : (SND.has(alt) ? alt : null);
    if (n) S.ambient(n, vol);
  };

  // ---------------------------------------------------------------- 背景锚点（没有就用默认值）
  const bgA = (bg, k, d) => { const b = G.D && G.D.bg && G.D.bg[bg]; const v = b && b.anchors ? b.anchors[k] : null; return v != null ? v : d; };
  const footY = (id, y) => { const st = G.STAGES[id]; return G.clamp(y, st.yMin + 2, st.yMax - 2); };
  const EXd = { arrive: [60, 164], gate: [160, 160], door: [160, 138], windows: [[100, 90], [220, 90]], tree: [262, 160],
    crow: [240, 60], steps: [200, 162], spw_car: [24, 166] };
  const COd = { arrive: [40, 164], portraits: [[120, 100], [260, 100], [400, 100]], candles: [[80, 96], [190, 96], [330, 96], [470, 96]],
    locked_door: [200, 152], telence: [340, 160], trapdoor: [480, 166], exit: [626, 162] };
  const GMd = { screen: [122, 58, 196, 110], tv: [160, 120], player: [89, 156], opponent: [239, 156], dolls: [282, 96],
    arcade: [30, 150], wall_hole: [300, 120], door: [12, 160], doll_slots: [[270, 96], [282, 96], [294, 96]] };
  const ILd = { arrive: [40, 164], fake_walls: [[285, 140], [430, 140], [180, 140]], exit: [626, 162] };
  const HLd = { pillar_a: [30, 154], pillar_b: [118, 154], pillar_c: [202, 154], pillar_d: [290, 154], beam_x: [250, 166],
    beam_center: [274, 164], breach: [290, 100], portrait: [160, 80], stairs_up: [300, 160],
    pillar_shaft: [27, 142], void_path: [152, 160, 168] };
  const TWd = { stairs: [30, 160], coffin: [160, 150], window: [160, 85], arrive: [50, 164], landing: [236, 156] };
  const EX = k => bgA('mansion_exterior', k, EXd[k]);
  const CO = k => bgA('mansion_corridor', k, COd[k]);
  const GM = k => bgA('game_room', k, GMd[k]);
  const IL = k => bgA('illusion_corridor', k, ILd[k]);
  const HL = k => bgA('mansion_hall', k, HLd[k]);
  const TW = k => bgA('mansion_tower', k, TWd[k]);
  // crt_baseball 是 CRT 电视里的球场（背景本身就是屏幕里的画面）：画完再盖 prop:crt_bezel
  const CBd = { mound: [146, 102], plate: [146, 148], outfield: [100, 56], score: [188, 26], score_box: [128, 21, 248, 31],
    bases: [[214, 108], [146, 68], [78, 108]], screen: [40, 18, 252, 162] };
  const CB = k => bgA('crt_baseball', k, CBd[k]);
  // 电视机屏幕区（crt_bezel 的窗口）：[x, y, w, h]。赛车 / 棒球的透视画在这里面。
  const CRT = [40, 18, 212, 144];

  function place(S, cid, x, y = 164, facing = 1) {
    const a = S.actor(cid); if (!a) return null;
    a.visible = true; a.follow = null; a.x = x; a.y = y; a.facing = facing; a.alpha = 1; a.scale = 1; S.unpose(a);
    return a;
  }
  function party(S, ids, leader, lost = []) {
    S.party([...ids, ...lost], { leader });
    lost.forEach(id => S.leave(id, { look: 'gray' }));
    for (const a of G.party.members) a.scale = 1;
  }

  // ---------------------------------------------------------------- 纪念品（story\extras.js）
  X.souvenir({ id: 'ch11_crow_feather', chapter: 'ch11', name: '乌鸦的羽毛', desc: '树根下捡到的一根黑羽毛。馆门口那只乌鸦，一直没叫过。', hint: '馆门口的枯树下' });
  X.souvenir({ id: 'ch11_last_gum', chapter: 'ch11', name: '最后一粒口香糖', desc: '咖啡味的，只剩一粒。伊奇一直没舍得吃。', hint: '光柱旁边的地上' });
  X.souvenir({ id: 'ch11_telence_pad', chapter: 'ch11', name: 'F-MEGA 的手柄', desc: '被藤蔓缠过的塑料手柄。按键上还留着汗。', hint: '游戏室的街机旁边' });

  // ================================================================ 灵魂演出
  // 光柱里的灵魂：白色碎片往上飘（不画伤口，也不画手）
  // holder：把这块整屏插入交给调用方保管。T.show 走 S.insert，而 W.insert 一设上世界层就整个不画了
  //   （engine\world.js 的 draw 看到 insert 直接 return），所以战斗里触发的灵魂演出如果不能被外部收回，
  //   就会连同黑底一起盖住战后的台词——第11章阳光飞踢那段（波鲁纳雷夫吐槽吸血鬼）整屏只剩一句对白。
  async function soulLight(S, cid, seconds = 1.6, holder = null) {
    snd('glass_break');
    const v = T.show(S, { bg: '#161126', draw(g, t) {
      const k = Math.min(1, t / seconds);
      T.sprite(g, cid, 'idle', 0, 160, 164 - k * 80, { scale: 2, alpha: 1 - k });
      for (let n = 0; n < 64; n++) {
        const a = n * 2.399, r = 8 + k * (20 + n % 15);
        g.fillStyle = n % 2 ? '#ffffff' : '#fff0b6';
        g.fillRect(Math.round(160 + Math.cos(a) * r), Math.round(144 - k * 65 + Math.sin(a) * r), 1, 2);
      }
    } });
    if (holder) holder.view = v;
    try { await S.wait(seconds); } finally { v.close(); if (holder && holder.view === v) holder.view = null; }
  }

  // 灵魂被吸进人偶（第 10 章达比那种演出的筹码版）：黑底头像 → 一道光 → 人偶落在玻璃柜的搁板上
  async function soulToDoll(S, cid, dollId, x, y) {
    const v = T.show(S, { bg: 'black', lines: true, parts: [{ kind: 'head', cid, scale: 3, x: 160, y: 92, jitter: 1 }] });
    await S.wait(.9);
    v.close();
    snd('soul_drain', 'sting_reveal', { vol: .7 });
    S.fx('glint', { x: 160, y: 120, size: 10 }, { space: 'canvas' });
    await S.wait(.4);
    const d = T.prop(S, dollId, x, y, { id: 'ch11_doll_' + cid });
    snd('glass_break', null, { vol: .4 });
    await S.wait(.4);
    return d;
  }

  // ================================================================ 11-01 篇章卡 · 馆门口
  async function mansionArrive(S) {
    party(S, ALL, 'jotaro');
    await S.setStage('mansion_ext_ch11', { x: EX('arrive')[0] + 20, y: footY('mansion_ext_ch11', EX('arrive')[1]), music: 'ominous' });
    S.state('night', 0);
    amb(S, 'wind_loop', 'wind', .1);
    await S.chapterCard('ch11');
    S.location('dio_mansion');
    await S.wait(.6);
    await S.say(null, '第四十九天，下午。');
    // SPW 的吉普开过来：花京院从车上下来。
    //   吉普是静态道具（只有两帧停着的画面，没有 walk 动作），所以走的时候指定 idle 帧，别让它记一条动作回退
    const ar = EX('arrive'), car = EX('spw_car');
    const jy = footY('mansion_ext_ch11', car[1]);
    const jeep = T.prop(S, 'spw_jeep', -40, jy, { id: 'ch11_jeep' });
    snd('car_engine');
    if (jeep) S.walk(jeep, car[0], jy, { speed: 120, anim: 'idle' }).catch(G.cancelIgnore);
    await S.wait(1.4);
    if (jeep) T.setFrame(jeep, 0);
    const kk = S.spawn('kakyoin', car[0] + 6, jy, { id: 'ch11_kakyoin_in', team: 'npc' });
    if (kk) { kk.facing = 1; kk.standReact = false; }
    if (kk) await S.walk(kk, ar[0] - 20, footY('mansion_ext_ch11', ar[1]), { speed: 62 });
    await S.say('kakyoin', '我说过会在这里等你们。', { name: '花京院', actor: kk || undefined });
    await S.say('polnareff', '花京院！你的眼睛——');
    await S.say('kakyoin', '看得见。……留了点疤而已。', { name: '花京院', actor: kk || undefined });
    await S.say('joseph', '欢迎回来。……这一次，六个人一起进去。');
    if (kk) kk.remove = true;
    await S.join('kakyoin', { notice: true });
    // 站位：承太郎 / 乔瑟夫 / 阿布德尔 / 波鲁纳雷夫 / 伊奇，朝右
    const bx = ar[0], by = footY('mansion_ext_ch11', ar[1] + 2);
    for (const [cid, dx] of [['jotaro', 20], ['joseph', 0], ['avdol', 40], ['polnareff', 60], ['iggy', 76]])
      place(S, cid, bx + dx, by, 1);
    S.follow();
  }

  // ================================================================ 11-02 威压（黑）
  async function menace(S) {
    S.music('ominous');
    // 黑底插入：跪在黑暗里的剪影 + 一滴落下的声音（不画）
    const v = T.show(S, { bg: 'black', draw(g, t) {
      if (t < 1.4) T.sprite(g, 'vanilla', 'kneel', 0, 160, 150, { scale: 1, alpha: .28 });
    } });
    await S.say('vanilla', '为了 DIO 大人，我的一切都可以献出。');
    snd('drip', 'water_splash', { vol: .5 });
    await S.wait(.9);
    v.close();
    await S.say('dio', '……起来吧，瓦尼拉。');
    await S.nameCard('vanilla', { y: 24 });
    await S.wait(1.2);
  }

  // ================================================================ 11-03 馆门口（自由走动）
  function setupMansionExt() {
    const st = G.STAGES.mansion_ext_ch11;
    st.props = []; st.npcs = []; st.hotspots = []; st.triggers = []; st.onLook = null;
    st.state = Object.assign({}, st.state, { night: 0 });
    const ar = EX('arrive'), gate = EX('gate'), win = EX('windows'), tree = EX('tree'), crow = EX('crow'), car = EX('spw_car');
    // 带 U 标签的调查点如果没有单独的 look，就复用 E 的那段话：
    //   party.js 在标签命中却没有 look 时会说「……这里好像有什么。」并记一条 look_missing（验收算错误）
    const H = (id, x, y, label, tags, use, look) => ({ id, x, y: footY('mansion_ext_ch11', y), r: 24, ry: 90, label, tags, use,
      look: look || (tags && tags.length ? use : undefined) });
    const all = ['detail', 'nensha', 'life', 'peek', 'cut', 'scent'];
    st.npcs = [
      T.npc('npc_spw', 'ch11_driver', car[0] + 26, footY('mansion_ext_ch11', car[1]), { facing: 1, label: 'SPW 的司机',
        name: 'SPW 的司机', talk: async S => { await S.say('npc_spw', '日落之前，我一直在这儿等着。', { name: 'SPW 的司机', actor: S.actor('ch11_driver') }); } }),
    ];
    st.hotspots = [
      // 铁门 = 出口（用热点触发，右边的枯树 / 乌鸦还要能走到）。
      //   出口不要挂 U 标签：标签命中却没有 look 会记 look_missing，而且 U 一按就过门会跳过内容
      H('gate', gate[0], gate[1], '铁门', [],
        async S => { await S.say('jotaro', '……到了。'); F().ch11Gate = true; }),
      H('windows', win[0][0], 164, '窗户', ['life', 'scent'],
        async S => { await S.say(null, '窗帘拉得严严实实，一点光都透不进去。'); },
        async (S, h, p) => {
          if (p && p.cid === 'avdol') await S.say('avdol', '里面有好几个生命。……还有一个，很冷，像死的一样。');
          else if (p && p.cid === 'iggy') { snd('sand', null); await S.say(null, '（气味线钻进门缝；伊奇夹着尾巴往后退了两步。）'); }
          else await S.say(p ? p.cid : null, '窗帘拉得严严实实，一点光都透不进去。');
        }),
      H('tree', tree[0], tree[1], '枯树', all, async S => { await S.say(null, '一棵枯死的树，树枝像手指一样伸着。'); }),
      H('crow', crow[0], 164, '乌鸦', all, async S => { await S.say(null, '树上停着一只乌鸦，一动不动地看着你们。'); }),
      H('steps', EX('steps')[0], EX('steps')[1], '石阶', ['detail'],
        async S => { await S.say('polnareff', '……走吧。为了荷莉女士。'); }),
      H('jeep', car[0], car[1], 'SPW 的车', all, async S => { await S.say('kakyoin', '……司机说，日落之前会一直在这里等。'); }),
      // 纪念品：乌鸦的羽毛（树根下）
      X.hot('ch11_crow_feather', tree[0] + 10, footY('mansion_ext_ch11', tree[1]), {
        label: '树根下', r: 20, ry: 80, found: async S => S.say(null, '树根下有一根黑羽毛。') }),
    ];
    st.onLook = async (S, p) => S.say(p ? p.cid : null, p && p.cid === 'kakyoin' ? '……法皇的触须，不想靠近这栋房子。' : '……好冷。明明是下午。');
  }
  async function mansionExplore(S) {
    setupMansionExt();
    await S.setStage('mansion_ext_ch11', { x: EX('arrive')[0], y: footY('mansion_ext_ch11', EX('arrive')[1]), music: 'ominous' });
    S.state('night', 0);
    amb(S, 'wind_loop', 'wind', .1);
    S.location('dio_mansion');
    T.memberTalk({
      joseph: async S => S.say('joseph', '荷莉……再等一天。'),
      avdol: async S => S.say('avdol', '这里的空气，比开罗还要冷。'),
      polnareff: async S => S.say('polnareff', '我的头发都竖不起来了。'),
      kakyoin: async S => S.say('kakyoin', '……眼睛看得见。这就够了。'),
    });
    S.free(true);
    S.hint('馆门口：阿布德尔 / 伊奇可以用 U 探查；准备好了就推开铁门。', 10);
    T.goal(S, { x: EX('gate')[0], y: footY('mansion_ext_ch11', EX('gate')[1]), h: 56, label: '铁门', delay: 50, every: 25,
      done: () => !!F().ch11Gate, text: '太阳还高，现在进去。' });
    await S.until(() => !!F().ch11Gate && !S.busy);
    S.free(false);
    S.insertUI(null);
  }

  // ================================================================ 11-04 走廊（泰伦斯带路、地板触发区）
  function setupCorridor() {
    const st = G.STAGES.corridor_ch11;
    st.props = []; st.npcs = []; st.hotspots = []; st.triggers = []; st.onLook = null;
    st.state = Object.assign({}, st.state, { trap: 0 });
    const tel = CO('telence'), trap = CO('trapdoor'), ld = CO('locked_door');
    const H = (id, x, y, label, tags, use, look) => ({ id, x, y: footY('corridor_ch11', y), r: 24, ry: 90, label, tags, use,
      look: look || (tags && tags.length ? use : undefined) });
    const all = ['detail', 'nensha', 'life', 'peek', 'cut', 'scent'];
    st.npcs = [
      T.npc('telence', 'ch11_telence', tel[0], footY('corridor_ch11', tel[1]), { facing: -1, label: '管家',
        name: '泰伦斯·T·达比',
        talk: async S => { await S.say('telence', '客人，这边请。主人还在休息。', { name: '泰伦斯·T·达比', actor: S.actor('ch11_telence') }); } }),
    ];
    st.hotspots = [
      H('portrait_0', CO('portraits')[0][0], 164, '画像', all, async S => { await S.say(null, '画上的眼睛，好像一直在跟着你。'); }),
      H('portrait_1', CO('portraits')[1][0], 164, '画像', all, async S => { await S.say(null, '烛火一动不动。这里没有风。'); }),
      H('portrait_2', CO('portraits')[2][0], 164, '画像', all, async S => { await S.say('joseph', '这些人……都是 DIO 的手下吧。'); }),
      H('candle_0', CO('candles')[0][0], 164, '烛台', ['detail', 'life', 'cut'], async S => { await S.say(null, '烛火不晃。'); }),
      H('candle_1', CO('candles')[1][0], 164, '烛台', ['detail', 'life', 'cut'], async S => { await S.say(null, '烛火不晃。'); }),
      H('locked_door', ld[0], ld[1], '上锁的门', all, async S => { await S.say('jotaro', '……没有锁孔。'); }),
      H('trapdoor', trap[0], trap[1], '地板', all, async S => { await S.say(null, '地板上有一圈很细的缝。'); }),
    ];
    st.onLook = async (S, p) => S.say(p ? p.cid : null, '走廊很深，蜡烛一直亮到尽头。');
    // 地板触发区：走到翻板前就把自由走动交回剧情（不靠玩家按 E）
    st.triggers = [{ x0: trap[0] - 20, x1: trap[0] + 20, y0: 0, y1: 180, once: true,
      run: async () => { F().ch11Trap = true; } }];
  }
  async function corridorWalk(S) {
    setupCorridor();
    await S.setStage('corridor_ch11', { x: CO('arrive')[0], y: footY('corridor_ch11', CO('arrive')[1]), music: 'ominous' });
    S.location('dio_mansion');
    // 脚本 11-04：名牌 → 管家的迎客台词（逐字）→ 花京院对画像的感想
    await S.run(async s => {
      // 对白框占 y14–90、左上地点卡占 y92–152，队伍从 y≈265 起；196 正好落在墙面空带，既不挡字也不压人
      s.nameCard('telence', { y: 196 });
      await s.say('telence', '欢迎光临。主人还在休息。……请随我来。');
      await s.say('kakyoin', '……画像的眼睛，在跟着我们转。');
    });
    T.memberTalk({
      joseph: async S => S.say('joseph', '这栋房子……比想象的大。'),
      avdol: async S => S.say('avdol', '别走散。'),
      polnareff: async S => S.say('polnareff', '喂，前面那位——'),
    });
    // 泰伦斯保持在队长前方 80 px（只往右走）；队长 2 秒没往右走就回头招呼
    let still = 0, barkI = 0;
    const barkAt = ['客人，这边请。', '主人等的是承太郎先生。'];
    T.tick(dt => {
      const tel = S.actor('ch11_telence'), p = W.player;
      if (!tel || !p || !W.free) return false;
      if (p.x + 80 > tel.x) { tel.facing = 1; tel.x = Math.min(W.stage.x1 - 10, tel.x + 60 * dt); tel.play('walk'); }
      else { tel.play('idle'); tel.facing = -1; }
      still = I.isDown('right') ? 0 : still + dt;
      if (still > 2 && !S.busy) { still = 0; S.bark('telence', barkAt[barkI++ % barkAt.length], { dur: 1.4 }); }
      return false;
    });
    S.free(true);
    S.hint('跟着管家走。地板上有东西，别踩上去。', 10);
    T.goal(S, { x: CO('trapdoor')[0], y: footY('corridor_ch11', CO('trapdoor')[1]), h: 56, label: '走廊深处', delay: 45, every: 25,
      done: () => !!F().ch11Trap, text: '管家在前面等着。' });
    await S.until(() => !!F().ch11Trap && !S.busy);
    S.free(false);
    S.insertUI(null);
    const tel = S.actor('ch11_telence'); if (tel) tel.play('idle');
  }

  // ================================================================ 11-05 地板翻开 · 海中小岛
  async function trapdoor(S) {
    S.state('trap', 1);
    snd('door');
    S.shake(2, .3);
    await S.say('jotaro', '……地板！');
    // A 队三人往下 40 px、渐隐 0.6 s；B 队留在原地
    const y0 = footY('corridor_ch11', CO('arrive')[1]);
    for (const cid of TEAM_A) {
      const a = S.actor(cid); if (!a) continue;
      S.animate(.6, k => { a.y = y0 + 40 * k; a.alpha = 1 - k; });
    }
    await S.wait(.8);
    for (const cid of TEAM_A) { const a = S.actor(cid); if (a) { a.visible = false; a.alpha = 1; a.y = y0; } }
    // 小岛插入：两个泰伦斯
    const v = T.show(S, { bg: 'redsea_island', parts: [
      { kind: 'sprite', cid: 'telence', anim: 'idle', x: 120, y: 168, scale: 2 },
      { kind: 'sprite', cid: 'telence', anim: 'walk', x: 214, y: 168, scale: 2 }] });
    await S.wait(1.4);
    v.close();
    snd('glass_break'); S.impact('invert', 2 / 24);
    await S.wait(.2);
    // 进游戏室
    party(S, TEAM_A, 'jotaro');
    await S.setStage('game_ch11', { x: GM('player')[0], y: footY('game_ch11', GM('player')[1]), music: 'battle' });
    S.state('crt', 1); S.state('hole', 0);
    await S.title('god_atum');
    await S.vs({ key: 'atum', hero: 'jotaro', enemy: 'telence' });
    G.uifx.vsTag(null);
    await S.say('telence', '这里是游戏室。阿图姆神会问你们的灵魂。', { name: '泰伦斯·T·达比' });
    await S.say('joseph', '问灵魂？……你在说什么？');
    await S.say('telence', '很简单：你们赢了，我就带路；你们输了——灵魂留下。', { name: '泰伦斯·T·达比' });
  }

  // ================================================================ 11-06 F-MEGA 赛车（CRT 里的伪 3D）
  // 屏幕区：CRT = [40,18,212,144]。透视画在插入画面（320×180），HUD 走 UI 层（640×360），字才清楚。
  function raceDraw(g, s) {
    const [ox, oy, w, h] = CRT, cx = ox + w / 2, hor = oy + h * .42, bot = oy + h;
    g.save();
    g.beginPath(); g.rect(ox, oy, w, h); g.clip();
    // 天空：三条色带
    g.fillStyle = '#101a3a'; g.fillRect(ox, oy, w, h * .30);
    g.fillStyle = '#1b2a55'; g.fillRect(ox, oy + h * .16, w, h * .18);
    g.fillStyle = '#2b3f70'; g.fillRect(ox, oy + h * .30, w, h * .12);
    // 远山
    g.fillStyle = '#33254a'; g.beginPath(); g.moveTo(ox, hor); g.lineTo(ox + w * .22, hor - 26);
    g.lineTo(ox + w * .40, hor - 8); g.lineTo(ox + w * .58, hor - 30); g.lineTo(ox + w * .78, hor - 10);
    g.lineTo(ox + w, hor - 22); g.lineTo(ox + w, hor); g.closePath(); g.fill();
    // 路面：上窄下宽的梯形
    g.fillStyle = '#3a3348'; g.beginPath();
    g.moveTo(cx - 13, hor); g.lineTo(cx + 13, hor); g.lineTo(cx + 100, bot); g.lineTo(cx - 100, bot); g.closePath(); g.fill();
    // 横向分隔线往近处滚（速度随车速）
    const scroll = (s.distance || 0) * .0022;
    for (let n = 0; n < 10; n++) {
      const k = ((n / 10 + scroll) % 1), y = hor + (bot - hor) * k * k;
      g.fillStyle = k < .5 ? '#4a4160' : '#554a6c';
      g.fillRect(Math.round(cx - (13 + k * 87)), Math.round(y), Math.round((13 + k * 87) * 2), 1 + Math.round(k * 2));
    }
    // 车道分界虚线
    for (const side of [-1, 1]) for (let n = 0; n < 10; n++) {
      const k = ((n / 10 + scroll) % 1), y = hor + (bot - hor) * k * k;
      g.fillStyle = '#d8cfa8';
      g.fillRect(Math.round(cx + side * (4 + k * 30)), Math.round(y), 1 + Math.round(k * 2), 2 + Math.round(k * 5));
    }
    // 路边标牌：从远处往近处放大、往两边飞出去
    for (let n = 0; n < 4; n++) {
      const k = ((n / 4 + scroll * .7) % 1), y = hor + (bot - hor) * k * k;
      const sc = .4 + k * 1.6, x = cx + (n % 2 ? 1 : -1) * (10 + k * 96);
      T.sprite(g, 'prop:race_sign', 'idle', Math.floor(k * 8) % 2, x, y, { scale: sc });
    }
    // 对手车（远的按透视缩小）
    const ex = cx + (((s.enemyLane == null ? 1 : s.enemyLane) - 1) * 34);
    const ey = Math.max(hor + 8, bot - 20 - Math.max(0, s.enemyAhead || 0) * 1.1);
    T.sprite(g, 'prop:race_car', 'idle', 2 + (Math.floor(s.t * 8) % 2), ex, ey,
      { scale: .55 + (ey - hor) / (bot - hor) * .45 });
    // 自己的车（花京院）
    const px = cx + ((s.lane == null ? 1 : s.lane) - 1) * 34;
    T.sprite(g, 'prop:race_car', 'idle', Math.floor(s.t * 8) % 2, px, bot - 8, { scale: 1 });
    g.restore();
    // 电视机外框（屏幕区以外是不透明的机身，正好挡住出画的部分）
    T.sprite(g, 'prop:crt_bezel', 'idle', 0, 0, 0);
  }
  function raceUI(g, s) {
    const pct = Math.min(100, Math.floor((s.distance || 0) / 24));
    L.text(g, 'LAP 3 / 3', 96, 46, '#ffe174');
    L.text(g, '赛程 ' + pct + '%', 492, 46, '#ffffff', 'right');
    L.text(g, '名次 ' + (s.enemyAhead > 0 ? '2 / 2' : '1 / 2'), 96, 62, '#b7e6ff');
    if (s.finalBend) L.text(g, '最后的弯道……他提前封住了路线！', 320, 150, '#ffad94', 'center');
    L.text(g, '按住 J 加速；← → 换道', 320, 320, '#ffe3a0', 'center');
  }
  async function race(S) {
    let led = false;
    for (let attempt = 0; attempt < 4; attempt++) {
      S.mark('ch11_race');
      const q = await L.runner(S, { race: true, draw: raceDraw, ui: raceUI });
      if (!led && q.leading > .5) { led = true; await S.say('kakyoin', '承太郎，我领先了！'); }
      if (q.win) break;
    }
    // 输了：灵魂吸进人偶（不画伤口）
    await S.say('telence', '最后一个弯道——你的灵魂，我收下了。', { name: '泰伦斯·T·达比' });
    const slot = GM('doll_slots')[0];
    await soulToDoll(S, 'kakyoin', 'atum_doll_b', slot[0], footY('game_ch11', slot[1]));
    await S.say('jotaro', '……花京院！');
    S.leave('kakyoin', { look: 'gray' });
    await S.wait(.6);
  }

  // ================================================================ 11-07 棒球（CRT，三振 4 次赢）
  //   计分：泰伦斯先拿到 9 分 = 输；承太郎先三振 4 次 = 赢。第 3 局按 Q 把输入交给藤蔓 → 读中率 0（他读的是手柄）。
  function baseballDraw(g, s) {
    T.drawBg(g, 'crt_baseball', s.t, 0, {});
    const mound = CB('mound'), plate = CB('plate'), out = CB('outfield');
    // 球：读中飞向外野，读不中进本垒
    if (s.phase === 'result') {
      const k = Math.min(1, (.8 - s.reveal) / .8);
      const to = s.read ? out : plate;
      T.sprite(g, 'prop:bb_sprites', 'idle', 4, plate[0] + (to[0] - plate[0]) * k, plate[1] - 6 + (to[1] - plate[1]) * k, { scale: 1 });
    }
    // 投手 / 打者：结果帧交替
    T.sprite(g, 'prop:bb_sprites', 'idle', Math.floor(s.t * 6) % 2, mound[0], mound[1], { scale: 1 });
    T.sprite(g, 'prop:bb_sprites', 'idle', s.phase === 'result' ? 3 : 2, plate[0] + 16, plate[1], { scale: 1 });
    if (s.delegated) { g.fillStyle = '#ae78c5'; for (let n = 0; n < 4; n++) g.fillRect(52 + n * 3, 150 + n * 3, 42, 1); }
    // 最上层：CRT 外框
    T.sprite(g, 'prop:crt_bezel', 'idle', 0, 0, 0);
  }
  function baseballUI(g, s) {
    L.text(g, '第 ' + Math.min(3, s.inning) + ' 局　球 ' + s.ball, 96, 46, '#ffe174');
    if (s.phase === 'result') L.text(g, s.read ? 'YES！我读到了你的灵魂。' : 'NO？！灵魂与输入不同……', 320, 120, s.read ? '#ffb0a0' : '#91ffbb', 'center');
    L.text(g, s.inning >= 3 && !s.delegated ? '第 3 局：按 Q，把手柄交给藤蔓！' : 'J / E 投球', 320, 320, '#ffe3a0', 'center');
  }
  async function baseball(S) {
    party(S, ['jotaro', 'joseph'], 'jotaro');
    let delegated = false;
    for (let attempt = 0; attempt < 4; attempt++) {
      S.mark('ch11_baseball');
      const q = { type: 'baseball', inning: 1, ball: 0, runs: 0, ks: 0, phase: 'select', reveal: 0, delegated: false, read: false,
        touch: { buttons: ['pad', 'j', 'e', 'swap'], captions: { j: '投球', e: '投球', swap: '藤蔓' } } };
      await L.game(S, q, (s, dt) => {
        if (s.phase === 'result') {
          s.reveal -= dt;
          if (s.reveal > 0) return;
          s.ball++;
          if (s.runs >= 9) { s.done = true; s.win = false; return; }
          if (s.ks >= 4) { s.done = true; s.win = true; return; }
          // 每两球一局：第 5 球就进第 3 局，玩家来得及在被打到 9 分之前把手柄交给藤蔓
          s.inning = Math.min(3, Math.floor(s.ball / 2) + 1);
          s.phase = 'select';
          return;
        }
        // 第 3 局：按 Q 交给藤蔓（之后读中率 0）
        if (s.inning >= 3 && !s.delegated && L.hit('swap')) { s.delegated = true; snd('vine'); }
        if (!(L.hit('attack') || L.hit('ok'))) return;
        s.read = G.rand(0, 1) < (s.delegated ? 0 : .8);
        if (s.read) { s.runs++; snd('baseball_hit'); } else { s.ks++; snd('tv_game'); }
        s.phase = 'result'; s.reveal = .8;
        G.dbg.ev('baseball_pitch', { inning: s.inning, runs: s.runs, ks: s.ks, delegated: s.delegated, read: s.read });
      }, baseballDraw, baseballUI);
      delegated = delegated || q.delegated;
      if (q.win) break;
      if (attempt < 3) await S.say('joseph', '他只能读取拿手柄的人。把第三局的输入交给藤蔓！这几局再来一次。');
    }
    F().baseballDelegated = delegated;
    // 赢：白金之星打穿墙
    await S.say('jotaro', '……读得到我的灵魂？那我就不用手柄了。');
    const hole = GM('wall_hole');
    S.fx('burst', { x: hole[0], y: hole[1], n: 26 });
    snd('wall_slam'); S.shake(3, .3);
    S.state('hole', 1);
    await S.title('saiki');
    // 玻璃柜里的人偶裂开，一道光回花京院
    const doll = S.actor('ch11_doll_kakyoin');
    if (doll) { S.fx('shatter', { src: 'prop:atum_doll_b', logical: 'idle', x: doll.x, y: doll.y - 8, pieces: 16, dur: .8 }); doll.remove = true; }
    snd('glass_break');
    await S.join('kakyoin', { notice: true });
    await S.say('kakyoin', '……回来了。多谢，承太郎。');
    await S.say('telence', '……我的游戏，居然输了。', { name: '泰伦斯·T·达比' });
    await S.wait(.5);
  }

  // ================================================================ 11-08 游戏室（自由走动）
  function setupGameRoom() {
    const st = G.STAGES.game_ch11;
    st.props = []; st.npcs = []; st.hotspots = []; st.triggers = []; st.onLook = null;
    st.state = Object.assign({}, st.state, { crt: 1, hole: 1 });
    const slots = GM('doll_slots');
    // 三个人偶里花京院那个已经裂了 → 只留两个摆回玻璃柜的搁板。
    //   sprite 必须写道具名（drawProp 读 p.sprite || p.id），id 只是给剧情找对象用的
    st.props = [
      { type: 'sprite', id: 'ch11_doll_a', sprite: 'atum_doll_a', frame: 0, x: slots[1][0], y: footY('game_ch11', slots[1][1]), z: 0, shadow: false },
      { type: 'sprite', id: 'ch11_doll_c', sprite: 'atum_doll_c', frame: 0, x: slots[2][0], y: footY('game_ch11', slots[2][1]), z: 0, shadow: false },
    ];
    const arc = GM('arcade'), tv = GM('tv'), hole = GM('wall_hole'), door = GM('door');
    const H = (id, x, y, label, tags, use, look) => ({ id, x, y: footY('game_ch11', y), r: 24, ry: 90, label, tags, use,
      look: look || (tags && tags.length ? use : undefined) });
    const all = ['detail', 'nensha', 'life', 'peek', 'cut', 'scent'];
    st.hotspots = [
      H('tv', tv[0], tv[1], '电视', all, async S => { await S.say(null, '屏幕里还在循环播放赛车的画面。'); }),
      H('dolls', GM('dolls')[0], GM('dolls')[1], '玻璃柜', all, async S => { await S.say(null, '玻璃柜里摆着几个人偶。……其中一个已经裂了。'); }),
      H('arcade', arc[0], arc[1], '街机', all, async S => { await S.say('polnareff', '这种机器，我在巴黎见过。'); }),
      H('hole', hole[0], hole[1], '墙上的洞', all, async S => { await S.say('jotaro', '……墙是空的。'); }),
      X.hot('ch11_telence_pad', arc[0] + 16, footY('game_ch11', arc[1]), {
        label: '街机旁', r: 20, ry: 80, found: async S => S.say(null, '街机旁边扔着一只被藤蔓缠过的手柄。') }),
      H('door', door[0] + 6, door[1], '门', [], async S => { F().ch11GameOut = true; }),
    ];
    st.onLook = async (S, p) => S.say(p ? p.cid : null, '……电视的声音，一直没停。');
  }
  async function gameRoomExplore(S) {
    setupGameRoom();
    await S.setStage('game_ch11', { x: GM('player')[0], y: footY('game_ch11', GM('player')[1]), music: 'ominous' });
    S.state('crt', 1); S.state('hole', 1);
    T.memberTalk({
      joseph: async S => S.say('joseph', '这些游戏……都是他做的？'),
      kakyoin: async S => S.say('kakyoin', '……别再玩第二局了。'),
      polnareff: async S => S.say('polnareff', '我可不想再赌灵魂。'),
    });
    S.free(true);
    S.hint('游戏室：E 调查；从门口出去继续往里走。', 9);
    T.goal(S, { x: GM('door')[0], y: footY('game_ch11', GM('door')[1]), h: 56, label: '门口', delay: 40, every: 22,
      done: () => !!F().ch11GameOut, text: '该往里走了。' });
    await S.until(() => !!F().ch11GameOut && !S.busy);
    S.free(false);
    S.insertUI(null);
  }

  // ================================================================ 11-09 幻觉走廊（b25_tenoresax）
  async function labyrinth(S) {
    party(S, TEAM_B, 'avdol');
    await S.setStage('illusion_ch11', { x: IL('arrive')[0] + 30, y: footY('illusion_ch11', IL('arrive')[1]), music: 'tension' });
    S.state('variant', 0); S.state('cracked', 0); S.state('open', 0); S.state('menace', 0);
    await lines(S, [['avdol', '……又是走廊。'], ['polnareff', '刚才那段，我们不是走过了吗？'], ['iggy', '汪！']]);
    await S.vs({ key: 'tenoresax', hero: 'avdol', enemy: 'kennyg' });
    G.uifx.vsTag(null);
    await S.say('kennyg', '欢迎来到我的演奏厅。', { name: '肯尼·G' });
    const bark = ['喂……这里刚才是不是来过？', '我的头发都乱了！', '阿布德尔，你确定方向吗？'];
    for (let attempt = 0; attempt < 3; attempt++) {
      S.mark('ch11_labyrinth');
      const limit = attempt > 0 && F().ch11LabAssist ? 90 : 60;
      const walls = IL('fake_walls');
      const q = { type: 'labyrinth', variant: 0, found: false, hits: 0, wallX: walls[0][0], loop: 20, limit, left: limit, menace: 0,
        touch: { buttons: ['pad', 'j', 'u', 'swap'], captions: { j: '敲墙', u: '调查', swap: '队长' } } };
      S.state('variant', 0); S.state('cracked', 0); S.state('open', 0); S.state('menace', 0);
      let enemy = null, barkI = 0, barkAt = 12;
      await L.game(S, q, (s, dt) => {
        const p = W.player; L.move(p, dt);
        if (L.hit('swap')) G.party.next();
        // 紫色幻觉每 15 秒加深一档
        const m = Math.min(3, Math.floor(s.t / 15));
        if (m !== s.menace) { s.menace = m; S.state('menace', m); }
        // 走到两端 / 20 秒 → 换一个变体的假墙（裂缝和缺口归零）
        if (p.x > 610 || p.x < 25 || s.t >= s.loop) {
          if (enemy) { enemy.remove = true; enemy = null; }
          p.x = 65; s.variant = (s.variant + 1) % 3; s.wallX = walls[s.variant][0];
          s.found = false; s.hits = 0; s.loop = s.t + 20;
          S.state('variant', s.variant); S.state('cracked', 0); S.state('open', 0);
          snd('sax_melody');
        }
        // 阿布德尔 / 伊奇按 U 指出假墙
        if (L.hit('special')) {
          if (p.cid === 'avdol' || p.cid === 'iggy') { s.found = true; snd(p.cid === 'iggy' ? 'dog_bark' : 'fire_burst'); }
          else S.hint('这里刚才是不是来过？换阿布德尔或伊奇调查。', 2);
        }
        // 靠近假墙按 J 敲：三下裂开，第四下把本体打出来
        if (s.found && Math.abs(p.x - s.wallX) < 35 && L.hit('attack')) {
          s.hits++;
          S.state('cracked', Math.min(3, s.hits));
          snd(s.hits < 3 ? 'punch1' : 'ko_hit'); S.shake(2, .12);
          if (s.hits === 3) {
            S.state('open', 1);
            enemy = S.spawn('kennyg', s.wallX, footY('illusion_ch11', 160), { id: 'ch11_kennyg', hold: true });
            if (enemy) { enemy.facing = -1; enemy.play('sax'); }
          }
          if (s.hits >= 4) { s.done = true; s.win = true; }
        }
        // 波鲁纳雷夫每隔 12 秒抱怨一句
        if (s.t >= barkAt) { barkAt = s.t + 12; S.bark('polnareff', bark[barkI++ % bark.length], { dur: 1.6 }); }
        if (s.t >= s.limit) { s.done = true; s.win = false; }
      }, (g, s) => {
        // 幻觉色是「叠在走廊上」的滤镜，不是整屏换皮：insert 会替掉世界渲染，先把走廊画回来再叠
        L.underWorld(g);
        const camX = G.cam ? G.cam.x : 0;
        // 假墙本身由背景换 key（variant / cracked / open）；这里只画一条指向假墙的线和敲击进度。
        // 插入画面的画布是 320×180（世界层），不是 UI 层的 640×360——坐标写大了会画到画面外。
        if (s.found) {
          const p = W.player, x = s.wallX - camX;
          g.strokeStyle = p.cid === 'iggy' ? '#e8c070' : '#ff9d40'; g.lineWidth = 1;
          g.beginPath(); g.moveTo(p.x - camX, 150); g.lineTo(x, 143); g.stroke();
          L.text(g, s.hits >= 3 ? '肯尼·G 暴露了！再按 J！' : '假墙 ' + s.hits + ' / 3', x, 128, '#ffe174', 'center');
        }
        g.fillStyle = 'rgba(83,25,117,' + (.06 + .2 * Math.min(1, s.t / s.limit)) + ')';
        g.fillRect(0, 0, 320, 180);
      }, (g, s) => {
        L.label(g, '次中音萨克斯 · 幻觉走廊', 'Q 换队长；阿布德尔 / 伊奇按 U 指向假墙，靠近后 J 敲三下，再打本体');
        L.text(g, '剩余 ' + Math.ceil(Math.max(0, s.limit - s.t)) + ' 秒', 22, 313, '#ffe174');
        L.text(g, '假墙变体 ' + (s.variant + 1) + ' / 3', 610, 313, '#c9a8ff', 'right');
      });
      if (q.win) {
        if (enemy) enemy.remove = true;
        await S.title('saiki');
        await S.nameCard('kennyg');
        await S.say('kennyg', '……我的演奏，还没结束……', { name: '肯尼·G' });
        return;
      }
      if (enemy) enemy.remove = true;
      F().ch11LabAssist = true;
      await S.say('avdol', '幻觉又把我们送回了原处。只有这段走廊重来。');
      W.player.x = IL('arrive')[0] + 30;
    }
  }

  // ================================================================ 11-10 大厅：阿布德尔与奶油
  // 柱子上的半圆缺口：光柱里被虚空咬掉的一块（黑洞 + 一圈亮边）
  function pillarNotch(S, x, y, r = 7) {
    return G.MID.pixel('ch11_notch_' + Math.round(x) + '_' + Math.round(y), (P) => {
      const sx = Math.round(x - ((G.cam ? G.cam.x : 0) || 0)), sy = Math.round(y);
      G.px.disc(P, sx, sy, r, '#0a0712', 1);
      G.px.disc(P, sx, sy, Math.max(1, r - 3), '#140c1e', 1);
      G.px.ring(P, sx, sy, r, 1, '#8f7a5a', .8);
    });
  }
  async function gaon(S) {
    party(S, TEAM_B, 'polnareff');
    await S.setStage('hall_ch11', { x: HL('pillar_a')[0] + 10, y: footY('hall_ch11', HL('pillar_a')[1]), music: 'ominous' });
    S.state('breach', 0); S.state('beam', 0);
    S.location('dio_mansion');
    await lines(S, [['avdol', '……这里就是大厅。'], ['polnareff', '光是从上面照下来的。']]);
    // 第 3 根柱子上出现半圆缺口 + 拟声字
    const pc = HL('pillar_c');
    pillarNotch(S, pc[0], HL('pillar_shaft')[1] + 20, 7);
    S.sfxText('ガオン', { x: pc[0], y: 120 });
    snd('metal_crunch', 'teeth_crunch', { vol: .7 });
    await S.say('avdol', '……柱子被咬掉了一块。');
    await S.say('polnareff', '什么东西？！');
    // 阿布德尔把波鲁纳雷夫推开
    const av = S.actor('avdol'), po = S.actor('polnareff');
    if (av) S.pose(av, 'push');
    if (po) { S.pose(po, 'hurt'); S.arc(po, po.x + 60, po.y, 14, .4).catch(G.cancelIgnore); }
    snd('whoosh'); S.shake(2, .2);
    await S.wait(.5);
    await T.closeup4(S, { heads: [{ cid: 'avdol', expr: 'grave' }, { cid: 'polnareff', expr: 'shock' }], dur: 1.0 });
    await S.say('avdol', '波鲁纳雷夫！退后——它的目标是我。');
    // 白光：阿布德尔被抹消（白色碎片往上飘，不画手）
    S.flash(.5, .9);
    snd('void_eat');
    await soulLight(S, 'avdol');
    S.leave('avdol', { look: 'gray' });
    await S.say('polnareff', '阿布德尔——！！');
    await S.standCard('cream', { sfx: 'sting_reveal' });
    await S.say('vanilla', '为了 DIO 大人……');
    await S.nameCard('vanilla');
    if (po) S.unpose(po);
  }

  // ================================================================ 11-11 虚空在走廊里冲刺（b26b_cream）
  // 剧情和试炼共用这份配置；trial 的 lead / swap / allies / bench / vs 由试炼的 wrap 覆盖。
  const STORY_RUN = { trial: false, wrap: s => s };
  function creamHiddenSpec(S, o) {
    return {
      id: 'b26b_cream', lead: 'polnareff', swap: false, allies: ['iggy'], bench: 'hide', finish: 'none',
      arena: [12, 308], vs: 'cream', music: 'battle', losable: true, par: 100,
      waves: [[{ cid: 'vanilla', kit: 'e_vanilla', boss: true, hp: 300, minHp: 1, x: HL('pillar_d')[0], y: footY('hall_ch11', HL('pillar_d')[1]) }]],
      onWave(s, n, es, attempt, c) {
        const d = c.data;
        Object.assign(d, { phase: 'warn', phaseT: 0, rushes: 0, sand: 0, sandNext: c.assist ? 5 : 8,
          cuts: [], voidX: null, voidY: 160, dir: 1, sandX: null, sandUntil: 0, hitCool: 0 });
        const e = c.boss;
        if (e) {
          e.brain = () => true; e.alpha = 0; e.untargetable = true;
          e.onHitBy = () => (d.phase === 'expose' ? null : 'evade');
          e.dmgMul = () => 4;
        }
        S.state('breach', 0); S.state('beam', 0);
        // 虚空：会移动的黑圆 + 边缘白齿；冲过的柱子留半圆缺口（存 d.cuts，重试清空）
        // 重试会再插一层像素道具，先把上一轮的清掉，否则旧闭包会按旧坐标继续画黑圆
        W.stage.props = W.stage.props.filter(p => p.id !== 'ch11_void');
        d.pix = G.MID.pixel('ch11_void', (P, _sx, _sy, t) => {
          for (const cut of d.cuts) {
            const cx = Math.round(cut.x - ((G.cam ? G.cam.x : 0) || 0));
            G.px.disc(P, cx, Math.round(cut.y), cut.r, '#0a0712', 1);
            G.px.ring(P, cx, Math.round(cut.y), cut.r, 1, '#8f7a5a', .8);
          }
          if (d.voidX != null && d.phase !== 'expose') {
            const x = Math.round(d.voidX - ((G.cam ? G.cam.x : 0) || 0)), y = Math.round(d.voidY);
            G.px.disc(P, x, y, 11, '#080510', 1);
            G.px.disc(P, x, y, 7, '#000000', 1);
            for (let k = 0; k < 6; k++) {
              const a = k * 1.05 + t * 6;
              G.px.plot(P, Math.round(x + Math.cos(a) * 11), Math.round(y + Math.sin(a) * 11), '#e8e4f0', 1);
            }
          }
          if (d.sandX != null && d.sandUntil > t) {
            const x = Math.round(d.sandX - ((G.cam ? G.cam.x : 0) || 0));
            G.px.ellipse(P, x - 10, 168, x + 10, 174, '#c8b48a', null, 1, .5);
          }
        });
        G.MID.ui(S, (g, t, fight) => {
          if (!fight) return;
          L.hud(g, ['冲撞 ' + d.rushes, d.phase === 'expose' ? '探头了！按 U 阳光飞踢' : '等它冲过来，别站着不动']);
          L.text(g, '瓦尼拉·艾斯', 630, 24, '#ff9d8a', 'right');
        });
        S.hint('虚空冲刺时上下闪（K）；它探头时按 U 用阳光飞踢', 10);
      },
      tick(c, dt) {
        const d = c.data, e = c.boss;
        if (!e) return;
        const x0 = HL('pillar_a')[0] - 8, x1 = HL('pillar_d')[0];
        if (d.phase === 'warn') {
          d.phaseT += dt;
          e.alpha = 0; e.untargetable = true;
          if (d.phaseT > .34) {
            d.phase = 'dash'; d.phaseT = 0;
            d.voidX = x0; d.voidY = HL('void_path')[d.rushes % 3]; d.dir = 1; d.cutT = 0;
            snd('void_eat');
          }
        } else if (d.phase === 'dash') {
          d.phaseT += dt;
          d.voidX += d.dir * 120 * dt;
          // 虚空的“等价字段”：vx 是速度方向、targetY 是这次冲过的高度（玩家往另一边上下闪）。
          // 测试器和 AI 都按 vx / targetY / e.x 判断，所以这里同步一份，别只留在 d.voidX 里。
          d.vx = d.dir * 120; d.targetY = d.voidY;
          e.x = d.voidX; e.y = d.voidY;
          // 冲过柱子就刻一个缺口
          if (d.cutT <= 0) {
            for (const k of ['pillar_a', 'pillar_b', 'pillar_c', 'pillar_d']) {
              const px = HL(k)[0];
              if (Math.abs(d.voidX - px) < 7 && !d.cuts.some(q => q.k === k + '_' + d.rushes)) {
                d.cuts.push({ k: k + '_' + d.rushes, x: px, y: d.voidY, r: 6 });
                snd('crack', 'clang', { vol: .4 }); d.cutT = .2;
              }
            }
          }
          d.cutT -= dt;
          // 撞到玩家：伤 40%（放水 25%）
          const p = c.player;
          if (d.hitCool <= 0 && Math.abs(p.x - d.voidX) < 12 && Math.abs(p.y - d.voidY) < 13) {
            d.hitCool = .6;
            L.damage(c, Math.round(p.maxHp * (c.assist ? .25 : .4)));
            S.shake(3, .2); snd('thud');
          }
          d.hitCool -= dt;
          if (d.voidX >= x1) {
            d.rushes++; d.voidX = null;
            // 每 3 次冲撞探头一次
            if (d.rushes % 3 === 0) {
              d.phase = 'expose'; d.phaseT = 0;
              e.alpha = 1; e.untargetable = false;
              e.x = G.clamp(HL('pillar_c')[0], 24, 296); e.y = footY('hall_ch11', 160);
              snd('glint', 'sparkle');
            } else { d.phase = 'warn'; d.phaseT = 0; }
          }
        } else if (d.phase === 'expose') {
          d.phaseT += dt;
          if (d.phaseT > 40 / 60) { d.phase = 'warn'; d.phaseT = 0; e.alpha = 0; e.untargetable = true; }
        }
        // 沙尘：每 8 秒（放水 5 秒）地上出现 1.5 秒的轮廓
        d.sand += dt;
        if (d.sand >= d.sandNext) {
          d.sand %= d.sandNext;
          d.sandX = c.player.x + (G.rand(0, 1) < .5 ? -60 : 60);
          d.sandUntil = c.t + 1.5;
          snd('sand_storm', 'sand', { vol: .4 });
        }
        if (e.hp <= 1) c.end();
      },
      after: async (S, es) => {
        S.insertUI(null);
        const e = es[0]; if (e) { e.alpha = 1; e.untargetable = false; }
      },
      testHint: c => ({ phase: c.data.phase, rushes: c.data.rushes, cuts: c.data.cuts.length,
        voidX: c.data.voidX == null ? null : Math.round(c.data.voidX), voidY: c.data.voidY || null }),
    };
  }
  async function creamHidden(S, o = STORY_RUN) {
    S.mark('ch11_cream_hidden');
    await S.fight(o.wrap(creamHiddenSpec(S, o)));
  }

  // ================================================================ 11-12 阳光（b26c_sunlight）
  //   段 3 瓦尼拉是「实体」：站着挨打（不再 evade），HP 800。打到 400 以下演伊奇的牺牲（只一次），
  //   光柱开后只有两种赢法：J3 把他击退进光柱 18 px 内，或者他在光柱 40 px 内时按 U 阳光飞踢。
  //   注意别把「光柱前打不中」写成 evade —— 那样血根本掉不下来，400 永远不会到，这一段会死锁。
  async function creamSun(S, o = STORY_RUN) {
    S.mark('ch11_cream_sun');
    const bc = HL('beam_center')[0];
    // 伊奇灵魂上升是一块**整屏插入**（灵魂演出里有说明）：战斗结束后必须由我们自己收掉，
    //   否则黑底会压在战后台词上。soulH 存着那块插入，soulPending 记「伊奇死了但演出还没播」。
    const soulH = { view: null };
    let soulPending = false;
    // 试炼里波鲁纳雷夫只当队长时才给阳光飞踢（当 AI 队友不塞剧情专用 U）；剧情里他一直是队长。
    const lead = G.world && G.world.player ? G.world.player.cid : null;
    await S.fight(o.wrap({
      id: 'b26c_sunlight', lead: 'polnareff', swap: false, allies: ['iggy'], bench: 'hide',
      finish: o.trial ? 'ko' : 'none',
      arena: [12, 308], vs: 'cream', music: 'battle', losable: true, par: 80,
      // 试炼去 minHp，血打光即胜（finish 'ko'）；剧情仍靠光柱 / 阳光飞踢收尾。
      waves: [[Object.assign({ cid: 'vanilla', kit: 'e_vanilla', boss: true, hp: 800,
        x: G.clamp(bc - 66, 24, 296), y: footY('hall_ch11', HL('beam_center')[1]) }, o.trial ? {} : { minHp: 1 })]],
      kitOverride: !o.trial || lead === 'polnareff' ? { polnareff: { special: { name: '阳光飞踢', need: 0, prompt: '他靠近阳光了！按 U 飞踢！',
        window: c => !!(c.data.beam && c.boss && Math.abs(c.boss.x - bc) <= (c.assist ? 60 : 40)),
        run: async (S2, p, c) => {
          const d = c.data, e = c.boss;
          if (!e) return;
          snd('heat_beam', 'fire_burst'); S2.fx('fire_burst', { x: e.x, y: e.y - 20, n: 18 });
          e.stunT = 1.2; S2.shake(3, .3); d.sunWin = true;
          // 飞踢把他踢进光柱（不是打掉血）：位置一进 18 px 就判定胜利
          e.x = bc; c.end();
        } } } } : {},
      onWave(s, n, es, attempt, c) {
        const d = c.data;
        const gone = !!F().ch11IggyGone;   // 伊奇事件只演一次：重试时光柱直接开着
        Object.assign(d, { beam: gone ? 1 : 0, breach: gone ? 1 : 0, kicked: false, sunWin: false, j3Until: 0 });
        S.state('beam', d.beam); S.state('breach', d.breach);
        S.hint(gone ? '伊奇留下的光……把他推进去！'
          : o.trial ? '先把他打到 400 以下：阳光会照进来' : '先把他打到 400 以下：伊奇会撞开墙壁', 10);
        G.MID.ui(S, (g, t, fight) => {
          if (!fight) return;
          L.hud(g, [d.beam ? '光柱开了：J3 把他击退进光柱，或按 U 阳光飞踢' : '先逼出他的吸血鬼本性',
            d.beam ? '靠近阳光时按 U' : '他站着挨打，别停']);
        });
      },
      tick(c, dt) {
        const d = c.data, e = c.boss;
        if (!e) return;
        // HP ≤ 400：光柱打开（伊奇牺牲的演出只在剧情里放；试炼不删队友、不播灵魂上升）
        if (!d.beam && e.hp <= 400) {
          d.breach = 1; d.beam = 1; S.state('breach', 1); S.state('beam', 1);
          snd('glass_break'); S.shake(3, .3);
          S.fx('burst', { x: HL('breach')[0], y: HL('breach')[1], n: 22 });
          // 瓦尼拉被震退到光柱左边，硬直 1 s（脚本：震退到 x 238）
          e.x = Math.min(bc - 36, 238); e.stunT = 1;
          if (!o.trial) {
            if (!F().ch11IggyGone) {
              F().ch11IggyGone = true;
              // 脚本：被打断的腿会复原 → 波鲁纳雷夫先喊破他是吸血鬼，伊奇再牺牲
              S.bark('polnareff', '腿又复原了……他已经是吸血鬼！', { dur: 2 });
              const ig = G.party.get('iggy');
              if (ig) { ig.visible = true; ig.x = HL('breach')[0] - 20; ig.y = footY('hall_ch11', 160); ig.play('bite'); }
              S.bark('polnareff', '伊奇——！！', { dur: 2 });
              // 伊奇之死：灵魂上升（不画伤口）
              //   1 s 后画面可能已经因为「赢法一 / 赢法二」结束了（把瓦尼拉推进光柱只要一下），
              //   所以先看战斗还在不在：已经结束就记一笔，等 after 之后由剧情自己 await 补放，
              //   绝对不能让这块插入活到战后（否则 35_story_c11_sun_kick 那种整屏黑就是这么来的）。
              G.defer(1.0, () => { if (W.fight === c) soulLight(S, 'iggy', 1.2, soulH); else soulPending = true; });
              G.defer(2.4, () => { const a = G.party.get('iggy'); if (a) { a.visible = false; S.leave('iggy', { look: 'gray' }); } });
            } else S.bark('polnareff', '伊奇留下的光……把他推进去！', { dur: 2 });
          }
        }
        // 赢法一：他在光柱 18 px 内（被 J3 击退进去）
        if (d.beam && Math.abs(e.x - bc) < 18) c.end();
        // 赢法二：剧情里血被 minHp 卡在 1 时收尾；试炼改成打光血（finish 'ko'，不在这里提前结束）
        if (!o.trial && e.hp <= 1) c.end();
      },
      after: async (S2) => {
        S2.insertUI(null); S2.state('beam', 1);
        // 灵魂演出如果还开着，先收掉：战后要回到大厅本体，不能让黑底继续盖着
        if (soulH.view) { soulH.view.close(); soulH.view = null; soulPending = true; }
      },
      testHint: c => ({ beam: c.data.beam, breach: c.data.breach, iggyGone: !!F().ch11IggyGone,
        bossX: c.boss ? Math.round(c.boss.x) : null, j3Until: c.data.j3Until || 0, sunWin: !!c.data.sunWin }),
    }));
    // 胜利：他被推进光柱 → 化灰（shatter 染深灰 + 灰往上飘，不画血）
    const bx = HL('beam_center')[0], by = footY('hall_ch11', HL('beam_center')[1]);
    S.fx('shatter', { src: 'vanilla', logical: 'idle', x: bx, y: by - 20, pieces: 26, dur: 1.1, tint_to: '#3a3030' });
    snd('glass_break', null, { vol: .7 });
    await S.wait(.6);
    // 伊奇的灵魂上升如果在战斗里没来得及播（战斗结束得太快），在这里补放一次，播完再说话
    if (soulPending) { soulPending = false; await soulLight(S, 'iggy', 1.2); }
    if (!o.trial) await S.say('polnareff', '你那么想变成 DIO 那样的吸血鬼？……那就好好晒晒太阳吧！');
  }

  // 星尘试炼：b26b（300，探头窗口）→ b26c（800，去 minHp）两段连打。
  //   剧情里 b26b 前有阿布德尔的过场（gaon），b26c 后接两只灵魂（twoSouls）；试炼只保留两场战斗，
  //   台本和伊奇牺牲都在 spec 里按 trial 跳过。
  const CreamSrc = {
    chapter: 'ch11', pack: '_ch11',
    setup: async S => {
      await G.MID.ensureBg('_ch11');
      S.state('breach', 1); S.state('beam', 1);
    },
    run: async (S, o) => {
      // 剧情入口自己已经换过图（staged），试炼/单独进关才在这里布景
      if (!o.staged) await S.setStage('hall_ch11', { x: HL('pillar_a')[0] + 10, y: footY('hall_ch11', HL('pillar_a')[1]), music: 'battle' });
      await CreamSrc.setup(S);
      await creamHidden(S, o);
      await creamSun(S, o);
    },
  };

  // ================================================================ 11-13 两个人的灵魂
  async function twoSouls(S) {
    party(S, ['jotaro', 'joseph', 'kakyoin', 'polnareff'], 'jotaro', ['avdol', 'iggy']);
    await S.setStage('hall_ch11', { x: HL('pillar_a')[0] + 10, y: footY('hall_ch11', HL('pillar_a')[1]), music: 'sad' });
    S.state('breach', 1); S.state('beam', 1);
    // 光柱里两个人的 idle 往上飘 20 px 并渐隐
    const bx = HL('beam_center')[0], by = footY('hall_ch11', HL('beam_center')[1]);
    const av = S.spawn('avdol', bx - 8, by, { id: 'ch11_avdol_ghost', hold: true, shadow: false, standReact: false });
    const ig = S.spawn('iggy', bx + 8, by, { id: 'ch11_iggy_ghost', hold: true, shadow: false, standReact: false });
    S.animate(2.2, k => {
      if (av) { av.z = 20 * k; av.alpha = 1 - k; }
      if (ig) { ig.z = 20 * k; ig.alpha = 1 - k; }
    });
    await lines(S, [['polnareff', '阿布德尔……伊奇……'], ['jotaro', '……他们替我们开了路。']]);
    await S.wait(1.6);
    if (av) av.remove = true;
    if (ig) ig.remove = true;
    await S.say('polnareff', '我一定……会给你们一个交代。');
  }

  // ================================================================ 11-14 大厅（自由走动）
  function setupHall() {
    const st = G.STAGES.hall_ch11;
    st.props = []; st.npcs = []; st.hotspots = []; st.triggers = []; st.onLook = null;
    st.state = Object.assign({}, st.state, { breach: 1, beam: 1 });
    const beam = HL('beam_x'), stUp = HL('stairs_up'), po = HL('portrait');
    const H = (id, x, y, label, tags, use, look) => ({ id, x, y: footY('hall_ch11', y), r: 24, ry: 90, label, tags, use,
      look: look || (tags && tags.length ? use : undefined) });
    const all = ['detail', 'nensha', 'life', 'peek', 'cut', 'scent'];
    st.hotspots = [
      H('portrait', po[0], 164, '肖像画', all, async S => { await S.say(null, '画上的男人，笑得很安静。'); }),
      H('pillar_a', HL('pillar_a')[0], 164, '柱子', all, async S => { await S.say(null, '柱子上有一块被咬掉的缺口。'); }),
      H('pillar_b', HL('pillar_b')[0], 164, '柱子', all, async S => { await S.say(null, '柱子上有一块被咬掉的缺口。'); }),
      H('pillar_c', HL('pillar_c')[0], 164, '柱子', all, async S => { await S.say('polnareff', '阿布德尔就是在这里……'); }),
      H('beam', beam[0], beam[1], '光柱', all, async S => { await S.say(null, '阳光从破掉的天窗直直落下来。'); }),
      X.hot('ch11_last_gum', beam[0] - 30, footY('hall_ch11', beam[1]), {
        label: '光柱旁', r: 20, ry: 80, found: async S => S.say(null, '地上有一粒没拆开的咖啡味口香糖。') }),
      H('stairs', stUp[0] - 6, stUp[1], '楼梯（上楼）', [], async S => { F().ch11Stairs = true; }),
    ];
    st.onLook = async (S, p) => S.say(p ? p.cid : null, '……大厅里只剩下光。');
  }
  async function hallExplore(S) {
    setupHall();
    await S.setStage('hall_ch11', { x: HL('pillar_a')[0] + 10, y: footY('hall_ch11', HL('pillar_a')[1]), music: 'sad' });
    S.state('breach', 1); S.state('beam', 1);
    T.memberTalk({
      joseph: async S => S.say('joseph', '……上去吧。'),
      kakyoin: async S => S.say('kakyoin', '他们在看着我们。'),
    });
    S.free(true);
    S.hint('大厅：往右走，从楼梯上塔顶。', 9);
    T.goal(S, { x: HL('stairs_up')[0], y: footY('hall_ch11', HL('stairs_up')[1]), h: 56, label: '楼梯', delay: 40, every: 22,
      done: () => !!F().ch11Stairs, text: 'DIO 就在上面。' });
    await S.until(() => !!F().ch11Stairs && !S.busy);
    S.free(false);
    S.insertUI(null);
  }

  // ================================================================ 11-15 塔顶 · 努凯萨克
  async function towerMeet(S) {
    party(S, ['jotaro', 'joseph', 'kakyoin', 'polnareff'], 'jotaro', ['avdol', 'iggy']);
    await S.setStage('tower_ch11', { x: TW('arrive')[0], y: footY('tower_ch11', TW('arrive')[1]), music: 'ominous' });
    S.state('night', 0);
    S.location('dio_mansion');
    await lines(S, [['joseph', '……就是这里了。'], ['kakyoin', '太阳还没落。'], ['polnareff', 'DIO 在哪儿？']]);
    // 努凯萨克背对着站在楼梯平台上
    const land = TW('landing');
    const nk = S.spawn('nukesaku', land[0], footY('tower_ch11', land[1]), { id: 'ch11_nukesaku', team: 'npc' });
    if (nk) { nk.facing = -1; nk.standReact = false; S.pose(nk, 'reverse'); }
    await S.say('polnareff', '喂，那边的女人——');
    await S.wait(.4);
    await S.choice(['搭话', '动手'], '楼梯上背对着的“女人”');
    await S.say('jotaro', '你的脸和身体……是反的！');
    if (nk) { S.unpose(nk); nk.facing = 1; }
    await S.nameCard('nukesaku');
    await S.say('nukesaku', '呜哇！被、被发现了！', { name: '努凯萨克' });
  }
  // 努凯萨克：200 HP 的搞笑热身，KO 收尾。战后带路台词在 spec 外，试炼不播。
  const NukesakuSrc = {
    chapter: 'ch11', pack: '_ch11',
    setup: async S => {
      await G.MID.ensureBg('_ch11');
      await S.setStage('tower_ch11', { x: TW('arrive')[0], y: footY('tower_ch11', TW('arrive')[1]), music: 'battle' });
    },
    spec: o => ({
      id: 'b27_nukesaku', lead: o.trial ? undefined : 'jotaro', swap: false, bench: 'hide', finish: 'ko',
      // 剧情原 par 30；试炼关卡表是 40，评分按试炼表走
      par: o.trial ? 40 : 30,
      arena: [20, 300], music: 'battle', losable: true,
      waves: [[{ cid: 'nukesaku', kit: 'e_nukesaku', boss: true, hp: 200, x: 235, y: footY('tower_ch11', 160) }]],
      onWave(s, n, es, attempt, c) {
        const e = c.boss; if (e) { e.facing = -1; e.name = '努凯萨克'; }
      },
      testHint: c => c.boss ? {
        bossHp: c.boss.hp,
        // 出招时 facing 会临时转向身体方向，mem.faceDir 保存的是稳定的“脸朝向”
        faceDir: c.boss.mem && c.boss.mem.faceDir != null ? c.boss.mem.faceDir : c.boss.facing,
        bodyDir: Math.sign(c.player.x - c.boss.x) || 1,
      } : { bossHp: 0, faceDir: 0, bodyDir: 0 },
    }),
  };
  async function nukesaku(S, o = STORY_RUN) {
    const nk = S.actor('ch11_nukesaku');
    if (nk) nk.remove = true;
    await S.fight(o.wrap(NukesakuSrc.spec(o)));
    if (!o.trial) {
      const nk2 = S.spawn('nukesaku', TW('landing')[0], footY('tower_ch11', TW('landing')[1]), { id: 'ch11_nukesaku2', team: 'npc' });
      if (nk2) { nk2.facing = -1; S.pose(nk2, 'down'); }
      await S.say('nukesaku', '我带路！主人就在棺材里！', { name: '努凯萨克' });
      if (nk2) nk2.remove = true;
    }
  }

  // ================================================================ 11-16 开棺
  async function coffin(S) {
    S.mark('ch11_coffin');
    snd('door');
    // 开棺：全黑 + 拟声字 → 空镜（棺材里只有一顶帽子）
    const v = T.show(S, { bg: 'black', draw(g, t) {
      if (t > .3 && t < 1.5) T.sprite(g, 'nukesaku', 'reverse', 0, 160, 168, { scale: 2, alpha: .9 });
    } });
    S.sfxText('ゴゴゴゴ', { x: 160, y: 60 });
    await S.wait(1.2);
    v.close();
    const co = TW('coffin');
    const box = T.prop(S, 'coffin', co[0], footY('tower_ch11', co[1]), { id: 'ch11_coffin' });
    if (box) T.setFrame(box, 2);
    await S.wait(.6);
    // 空镜：棺材里只有一顶帽子
    T.prop(S, 'hat', co[0], footY('tower_ch11', co[1]) - 6, { id: 'ch11_hat' });
    await S.say(null, '棺材里，只有一顶帽子。');
    // 日落：背景换夜
    S.state('night', 1);
    S.music('ominous');
    await S.say('dio', '……醒得正好。');
    await S.say('jotaro', 'DIO……！');
    S.mark('ch11_end');
    await S.tbc();
  }

  // ================================================================ 本章入口
  G.STORY.ch11 = async S => {
    T.resetCounters();
    for (const key of ['ch11Gate', 'ch11Trap', 'ch11GameOut', 'ch11Stairs', 'ch11IggyGone', 'ch11LabAssist',
      'baseballDelegated']) delete F()[key];
    await G.MID.ensureBg('_ch11');
    await S.run(async s => { await mansionArrive(s); await menace(s); });
    await mansionExplore(S);
    await corridorWalk(S);
    await S.run(async s => { await trapdoor(s); await race(s); await baseball(s); });
    await gameRoomExplore(S);
    await S.run(async s => { await labyrinth(s); await gaon(s); await creamHidden(s); await creamSun(s); await twoSouls(s); });
    await hallExplore(S);
    await S.run(async s => { await towerMeet(s); await nukesaku(s); await coffin(s); });
  };

  // ================================================================ 单战入口（开发调参 G.DEV / 标题「挑战」）
  G.DEV = G.DEV || {};
  G.DEV.ch11Sax = async S => {
    await G.MID.ensureBg('_ch11');
    party(S, TEAM_B, 'avdol');
    await S.setStage('illusion_ch11', { x: IL('arrive')[0] + 30, y: footY('illusion_ch11', IL('arrive')[1]), music: 'battle' });
    await S.run(async s => { await labyrinth(s); });
  };
  G.DEV.ch11Cream = async S => {
    await G.MID.ensureBg('_ch11');
    party(S, ['polnareff', 'iggy'], 'polnareff');
    await S.setStage('hall_ch11', { x: HL('pillar_a')[0] + 10, y: footY('hall_ch11', HL('pillar_a')[1]), music: 'battle' });
    S.state('breach', 1); S.state('beam', 1);
    await S.run(async s => { await CreamSrc.run(s, { trial: false, wrap: q => q, staged: true }); });
  };
  G.DEV.ch11Nukesaku = async S => {
    await G.MID.ensureBg('_ch11');
    party(S, ['jotaro', 'joseph', 'kakyoin', 'polnareff'], 'jotaro', ['avdol', 'iggy']);
    await NukesakuSrc.setup(S);
    await S.run(s => nukesaku(s));
  };
  X.challenge({ id: 'b25_tenoresax', chapter: 'ch11', title: 'VS 次中音萨克斯（阿布德尔 / 伊奇）', par: 45, run: S => G.DEV.ch11Sax(S) });
  X.challenge({ id: 'b26b_cream', chapter: 'ch11', title: 'VS 瓦尼拉·艾斯 · 虚空冲刺（波鲁纳雷夫）', par: 100, run: S => G.DEV.ch11Cream(S) });
  X.challenge({ id: 'b27_nukesaku', chapter: 'ch11', title: 'VS 努凯萨克（承太郎）', par: 40, run: S => G.DEV.ch11Nukesaku(S) });
  // 星尘试炼第 16、17 关
  G.TRIAL_SRC['b26b_cream'] = CreamSrc;
  G.TRIAL_SRC['b27_nukesaku'] = NukesakuSrc;
})();
