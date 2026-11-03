// 第4章　杜王港 / 辣妹与透明宝宝（G.STORY.ch4，地图 id 后缀 _ch4）。开发脚本 第四部/docs/第4章_开发脚本.md，规矩见 第四部/docs/分章开发约定.md。
//   节拍 1 篇章卡 → 日历 → 2 东方家夜里（自由走动，电视里伸出发光的手）→ 3 杜王大酒店 → 4 远离电线的空地（偷听）→ 第 6 战段 A
//   → 5 亿泰被拖进电缆、修好 → 6 杜王港（自由走动 → 音石明、小指）→ 段 B → 7 → 段 C（船上）→ 8 乔瑟夫下船 → 9 箭交给 SPW
//   → 10 几天后（父子散步，自由走动 + 解谜透明宝宝 1–3 步）→ 公园池塘（第 4 步）→ 11 静、To Be Continued
//   克制（第三部 D10）：亿泰被拖进电缆只用剪影和电光；音石明只是再起不能；乔瑟夫咬破手指只画动作，水里只是一圈淡红。
//   三段战斗在 story/p4_ch4_fights.js（G.P4CH4）。亿泰、康一的招式组和替身调查是第2章写的公共的（engine/p4_moves.js、story/p4_common.js）。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const CH = () => G.P4CH4;
  const F = () => G.flags;
  const now = () => (G.clk ? G.clk.world : 0);
  const { base, walls } = G.p4Stage;
  const NAME_TOP = 100;
  const OKU = () => CH().OKU();

  Object.assign(G.NAMES, {
    okuyasu: '亿泰', thehand: '轰炸空间', joseph_old: '乔瑟夫', hermit: '隐者之紫',
    otoishi: '音石明', rhcp: '辣妹', shizuka: '静', spw_a: 'SPW', crew_a: '船员', crew_b: '船员', crew_c: '船员', crew_oto: '船员',
    captain: '船长', fisher: '渔民',
  });

  // ================================================================ 地图
  const ST = G.STAGES;
  ST.map_ch4 = base('map_ch4', 'morioh_map', 320, { yMin: 160, yMax: 170, music: null, obstacles: [] });
  ST.living_ch4 = base('living_ch4', 'higashikata_tvnight', 480, { music: 'daily', state: { snow: 0, lamp: 0 }, obstacles: walls(10, 470, 480) });
  ST.hotel_ch4 = base('hotel_ch4', 'morioh_grand_hotel', 480, { music: 'tension', state: { pm: 0 } });
  ST.field_ch4 = base('field_ch4', 'open_field', 640, { music: 'tension', state: { cable: 0 } });
  ST.harbor_ch4 = base('harbor_ch4', 'morioh_harbor', 960, { music: 'tension', state: { tyre: 0, forklift: 0, ship: 0 } });
  ST.ship_ch4 = base('ship_ch4', 'spw_ship', 640, { music: 'battle', state: { gen: 0 } });
  ST.street_ch4 = base('street_ch4', 'morioh_road', 960, { music: 'daily', state: { pm: 0 } });
  ST.pond_ch4 = base('pond_ch4', 'park_pond', 480, { music: 'daily', state: { ring: 0, red: 0 } });

  // 日历地图：东方家、杜王港
  P4().CAL.ch4 = { pins: [{ at: 'home', label: '东方家' }, { at: 'sea', label: '杜王港' }], stamp: 'stamp' };

  // 康一的“听”（U）：第2章有回音以后用正式的；这里没有才补一份
  G.LOOK.koichi = G.LOOK.koichi || {
    tags: ['listen'], cd: 1, miss: '……什么也没听到。',
    run: async (S, p) => { S.emote(p, '……', 0.8); S.sfx('blip', 0.4); await S.wait(0.5); },
  };
  // 乔瑟夫（79 岁）的念写：照第三部的乔瑟夫（藤蔓砸电视 → 拍立得）
  if (!G.LOOK.joseph_old && G.LOOK.joseph) G.LOOK.joseph_old = Object.assign({}, G.LOOK.joseph);

  // ================================================================ 小工具
  const pool = (cid) => G.party._actor(cid);
  function place(S, cid, x, y, facing, o = {}) {
    const a = pool(cid), W = G.world;
    Object.assign(a, { x, y, z: 0, facing: facing || 1, follow: null, hold: false, script: null, state: 'idle', remove: false, rot: 0, alpha: 1 });
    a.visible = o.visible !== false;
    if (W.player !== a) a.team = 'npc';
    a.play(a.idleAnim || 'idle');
    W.stage.add(a);
    return a;
  }
  const focus = (o) => { G.world.focus = o; };
  const snapTo = (o) => { G.world.focus = o; G.world.snapCamera(); };
  const zap = (S, x0, y0, x1, y1, life) => CH().zap(S, x0, y0, x1, y1, life);
  function stick(prop, a, dx, dz, o = {}) {
    T().tick(() => {
      if (!prop || prop.remove || !a || a.remove) return true;
      prop.x = a.x + dx * (a.facing || 1); prop.y = a.y + (o.dy || 0.5); prop.z = (a.z || 0) + dz;
      return false;
    });
  }

  // ================================================================ 节拍 1 篇章卡 → 日历地图
  async function beatCalendar(S) {
    S.player.visible = false;
    await S.setStage('map_ch4', { x: 160, y: 165, music: null });
    const cal = await P4().calendar(S, 'ch4', { hold: 1.8 });
    S.mark('ch4_calendar');
    await S.fadeOut(0.45);
    if (cal) cal.close();
  }

  // ================================================================ 节拍 2 东方家，夜里（自由走动）
  async function livingIn(S) {
    const p = S.player;
    p.visible = true;
    await S.setStage('living_ch4', { x: 300, y: 156, facing: 1, music: 'daily', fade: false });
    const tm = S.spawn('tomoko', 420, 150, { id: 'tomoko', facing: -1, label: '妈妈', talk: talkTomoko });
    void tm;
    S.sfx('tv_game', 0.5);
    G.world.snapCamera();
    await S.fadeIn(0.5);
    await S.title('night_tv', { y: 110 });
    S.location('higashikata', { y: NAME_TOP });
    await S.say('tomoko', '都几点了还打游戏！明天还要上学！', { expr: 'rage' });
    await S.say('josuke', '就最后一关嘛……');
    S.hint('自由走动：E 调查。电视好像有点不对劲', 6);
  }
  async function talkTomoko(S, me) {
    await T().say(S, me, F().tvHand ? '真是的，大半夜的吓我一跳。' : '打完这一关就去睡！听见没有？', { expr: F().tvHand ? 'normal' : 'rage' });
  }
  function setupLiving() {
    Object.assign(ST.living_ch4, {
      npcs: [], triggers: [],
      hotspots: [
        { id: 'console', x: 296, y: 156, r: 16, label: '游戏机', use: async (S) => { await S.say('josuke', '存档还没存……'); } },
        { id: 'switch', x: 159, y: 150, r: 16, label: '灯开关', use: async (S) => {
          const on = !(G.world.stage.state && G.world.stage.state.lamp);
          S.state('lamp', on ? 1 : 0); S.sfx('blip', 0.6);
          await S.say(null, on ? '开了灯。' : '关了灯。电视的光照在墙上。');
        } },
        { id: 'window', x: 98, y: 150, r: 18, label: '窗', use: async (S) => { await S.say(null, '外面的电线在风里嗡嗡响。'); } },
        { id: 'tv', x: 322, y: 150, r: 18, label: '电视', use: async () => { F().tvGo = true; } },
      ],
    });
  }
  async function beatTvHand(S) {
    const p = S.player, tm = S.actor('tomoko');
    T().memberTalk({});
    S.hint(null);
    if (Math.abs(p.x - 322) > 6) await S.walk(p, 312, 156, { speed: 60 });
    S.face(p, 1);
    await S.say('josuke', '换个台吧……');
    S.sfx('blip', 0.6);
    S.state('lamp', 0);
    S.state('snow', 1);
    S.sfx('rumble', 0.4);
    await S.wait(0.6);
    // 屏幕里伸出一只发光的手
    const hand = S.spawn('rhcp', 325, 150, { id: 'tv_hand', facing: -1, alpha: 0 });
    hand.z = 58; hand.shadow = false;
    S.pose(hand, 'hand');
    S.sfx('sting_shock', 0.8);
    zap(S, 325, 84, 316, 92, 0.4);
    await S.animate(0.3, (k) => { hand.alpha = k; hand.x = 325 - 8 * k; });
    S.mark('ch4_tv_hand');
    const r = await S.press({ key: 'attack', window: 0.7, label: '按 J！' });
    if (r !== 'miss') {
      await S.summon(p, { dur: 0.08, rise: 4 });
      S.standAct(p, 'punch', { dx: 18, z: 20, dur: 0.4 });
      S.sfx('punch', 0.8);
      S.sfxText('DORA!', hand, { dur: 0.6 });
      await S.wait(0.12);
      S.sfx('clang', 0.8);
      S.fx('hit_spark', { x: 316, y: 92, size: 12, accent: '#ffe060' });
      await S.say('josuke', '弹开了？！好快……', { expr: 'shock' });
    }
    // 被打飞，撞到沙发（喜剧）
    S.sfx('punch_heavy', 0.9);
    S.shake(4, 0.3);
    S.recall(p);
    await S.arc(p, 236, 152, 18, 0.45, { anim: 'hurt' });
    S.sfx('thud', 0.8);
    S.fx('smoke', { x: 236, y: 150, n: 5, rise: 8, life: 0.5 }, { life: 0.6 });
    S.pose(p, 'down');
    // 发光的小东西钻出半个身子 → 钻进插座
    S.unpose(hand); hand.hold = true; hand.play('idle');
    await S.animate(0.3, (k) => { hand.z = 58 - 20 * k; });
    await S.say('rhcp', '嘿嘿……比你的替身快吧？', { expr: 'smile' });
    S.sfx('whoosh', 0.7);
    await S.animate(0.3, (k) => { hand.x = 317 - 28 * k; hand.z = 38 - 8 * k; hand.scale = 1 - 0.7 * k; });
    zap(S, 289, 124, 289, 132, 0.3);
    hand.remove = true;
    S.mark('ch4_socket');
    for (let i = 0; i < 2; i++) { S.state('lamp', 1); S.sfx('blip', 0.5); await S.wait(0.12); S.state('lamp', 0); await S.wait(0.12); }
    S.state('snow', 0);
    S.unpose(p);
    if (tm) { await S.walk(tm, 280, 150, { speed: 90 }); S.face(tm, p); }
    await S.say('tomoko', '怎么了？！停电了？', { expr: 'shock' });
    S.face(p, 1);
    await S.say('josuke', '……没事。电视坏了，我修好了。');
    F().tvHand = true;
    await S.say('josuke', '（电线里有东西。……它在找我们。）', { expr: 'rage' });
    await S.fadeOut(0.6);
  }

  // ================================================================ 节拍 3 杜王大酒店
  async function beatHotel(S) {
    const p = S.player;
    await S.setStage('hotel_ch4', { x: 200, y: 158, facing: 1, music: 'tension', fade: false });
    const jt = place(S, 'jotaro4', 250, 154, -1);
    snapTo({ x: 240 });
    await S.fadeIn(0.5);
    S.mark('ch4_hotel');
    await S.say('jotaro4', '……电视里出来的手？', { actor: jt });
    await S.say('josuke', '一下子就钻进插座了。比疯狂钻石还快。');
    await S.say('jotaro4', '应该就是抢走形兆那支箭的替身。它能在电线里跑。', { actor: jt });
    const sp = S.spawn('spw_a', 470, 152, { id: 'spw_a', facing: -1, name: 'SPW 的工作人员' });
    await S.walk(sp, 300, 152, { speed: 60 });
    await S.say('spw_a', '空条先生，乔斯达先生的船明天下午到杜王港。', { name: 'SPW 的工作人员', actor: sp });
    await S.say('jotaro4', '……老头子要来了。', { actor: jt });
    await S.say('josuke', '乔、乔瑟夫·乔斯达？我那个……老爸？', { expr: 'shock' });
    await S.say('jotaro4', '找个静一点的地方商量。离电线远一点的。', { actor: jt });
    void p;
    await S.fadeOut(0.5);
    focus(null);
  }

  // ================================================================ 节拍 4 远离电线的空地
  let bikeProp = null;
  async function beatField(S) {
    await S.setStage('field_ch4', { x: 206, y: 160, facing: 1, music: 'tension', fade: false });
    const p = S.player;
    const ko = place(S, 'koichi', 186, 150, 1);
    const ok = place(S, OKU(), 244, 162, -1);
    const jt = place(S, 'jotaro4', 262, 148, -1);
    bikeProp = T().prop(S, 'ebike', 300, 150.5, { id: 'ebike_f', frame: 0 });
    snapTo({ x: 240 });
    await S.fadeIn(0.5);
    S.location('field', { y: NAME_TOP });
    S.mark('ch4_field');
    await S.say('jotaro4', '辣妹靠电活动。电线、插座、电池，它都能钻。', { actor: jt });
    await S.say('koichi', '那这里应该安全吧？四周一根电线都没有。', { actor: ko });
    await S.say(OKU(), '它要是敢来，我就用轰炸空间把它削了。……虽然我脑子不好使。', { actor: ok });
    await S.say('jotaro4', '明天老头子到港。他的念写能找到辣妹的本体，对方一定会先对他下手。', { actor: jt });
    // 摩托的电瓶闪了一下
    T().setFrame(bikeProp, 1);
    S.sfx('blip', 0.7);
    zap(S, 300, 142, 304, 132, 0.3);
    await S.wait(0.3);
    await S.say('rhcp', '嘿嘿，听到了听到了。乔瑟夫·乔斯达，明天下午，杜王港！', { expr: 'smile', name: '？？？' });
    S.mark('ch4_eavesdrop');
    S.face(p, 1); S.face(ko, 1); S.face(ok, 1); S.face(jt, 1);
    const rh = S.spawn('rhcp', 300, 150, { id: 'rhcp_show', facing: -1, alpha: 0 });
    rh.z = 8;
    zap(S, 300, 146, 300, 126, 0.4);
    await S.animate(0.3, (k) => { rh.alpha = k; });
    S.standCard('rhcp', { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.wait(1.2);
    await S.say(OKU(), '站住！', { expr: 'rage', actor: ok });
    rh.remove = true;
    bikeProp.remove = true; bikeProp = null;
    // 段 A：亿泰一个人追
    S.party([OKU()], { leader: OKU() });
    place(S, 'josuke', 150, 156, 1);
    place(S, 'koichi', 126, 150, 1);
    place(S, 'jotaro4', 104, 148, 1);
    S.music('battle', 0.3);
  }
  // ================================================================ 节拍 5 段 A 收尾：亿泰被拖进电缆 → 修好
  async function beatCable(S) {
    const ok = S.player, st = G.world.stage;
    focus({ x: 430 });
    await S.say('rhcp', '电力满格！', { expr: 'smile', name: '辣妹（电缆里）' });
    // 亿泰伸手去抓 → 被一起拖进去（剪影 + 白光 + 电弧）
    await S.walk(ok, 430, 160, { speed: 80, anim: 'run' });
    S.face(ok, 1);
    ok.tint = { color: '#04020a', k: 1 };
    S.sfx('thunder', 1);
    for (let i = 0; i < 4; i++) zap(S, 450, 160, 430 + (i % 2 ? 8 : -6), 130 + i * 4, 0.2);
    S.flash(0.8, 1, '#ffffff');
    await S.animate(0.8, (k) => { ok.y = 160 + 2 * k; ok.alpha = 1 - 0.5 * k; });
    await S.fadeOut(0.2);
    await S.wait(0.4, 'ui');
    // 下一镜：仗助已经在电缆沟边修
    ok.tint = null; ok.alpha = 1;
    S.party(['josuke'], { leader: 'josuke' });
    const p = S.player;
    Object.assign(p, { x: 404, y: 160, facing: 1, visible: true });
    const okn = place(S, OKU(), 430, 162, -1);
    S.pose(okn, 'down');
    const ko = place(S, 'koichi', 370, 150, 1);
    const jt = place(S, 'jotaro4', 340, 148, 1);
    void st; void ko;
    snapTo({ x: 420 });
    await S.fadeIn(0.3);
    await S.summon(p, { dur: 0.12, rise: 4 });
    S.standAct(p, 'reach', { dx: 18, z: 2, dur: 1.2 });
    P4().fixGlow(S, 430, 150, { n: 9, r: 16 });
    await S.wait(0.9);
    S.recall(p);
    S.unpose(okn);
    S.mark('ch4_okuyasu_fixed');
    await S.say(OKU(), '我……我刚才是不是被吸进去了？', { expr: 'shock', actor: okn });
    await S.say('josuke', '被吸进去一半。剩下那一半我给你修回去了。');
    await S.say('rhcp', '明天下午见啦——', { expr: 'smile', name: '辣妹（越来越远）' });
    S.state('cable', 0);
    await S.say('jotaro4', '……它要先去港口。明天我们分头守。', { actor: jt });
    await S.fadeOut(0.6);
    focus(null);
  }

  // ================================================================ 节拍 6 杜王港（自由走动 → 音石明）
  function setupHarbor() {
    Object.assign(ST.harbor_ch4, {
      npcs: [
        T().npc('spw_a', 'spw_h', 250, 152, { facing: 1, label: 'SPW 的工作人员', talk: async (S, me) => { await T().say(S, me, '船三点靠岸。承太郎先生他们已经坐快艇过去了。', { name: 'SPW 的工作人员' }); } }),
        T().npc('fisher', 'fisher', 770, 156, { facing: -1, label: '渔民', talk: async (S, me) => { await T().say(S, me, '岬那边最近夜里有怪声，像有人在弹吉他。'); } }),
      ],
      hotspots: [
        { id: 'lamp2', x: 411, y: 150, r: 18, label: '路灯', tags: ['listen'], use: async (S) => { await S.say(null, '路灯的灯头在白天也嗡嗡地响。'); },
          look: async (S, h, p) => { if (p.cid !== 'koichi') return; await S.say('koichi', '嗡——电线里的声音……在往船那边跑！', { expr: 'shock' }); F().otoGo = true; } },
        { id: 'lamp1', x: 151, y: 150, r: 18, label: '路灯', tags: ['listen'], use: async (S) => { await S.say(null, '路灯。电线从地下接上来。'); },
          look: async (S) => { await S.say('koichi', '这一根……没什么声音。'); } },
        { id: 'forklift', x: 628, y: 152, r: 20, label: '叉车', use: async (S) => { await S.say(null, '一台电瓶叉车。钥匙还插着。'); } },
        { id: 'fishbox', x: 770, y: 150, r: 14, label: '鱼箱', use: async (S) => { await S.say('josuke', '……好腥。'); } },
      ],
      triggers: [{ x0: 560, x1: 980, run: async () => { F().otoGo = true; } }],
    });
  }
  async function harborIn(S) {
    S.party(['josuke', 'koichi'], { leader: 'josuke' });
    await S.setStage('harbor_ch4', { x: 120, y: 160, facing: 1, music: 'tension', fade: false });
    G.world.snapCamera();
    await S.fadeIn(0.5);
    S.location('harbor', { y: NAME_TOP });
    S.mark('ch4_harbor');
    await S.say('koichi', '承太郎先生和亿泰君坐快艇去接船了。我们守在码头……', { expr: 'normal' });
    await S.say('josuke', '辣妹一定会来。到处看看。');
    S.hint('Q 换成康一，对着路灯按 U：康一的耳朵好，能听电线里的声音', 8);
  }
  async function talkKoichiHarbor(S) { await S.say('koichi', '仗助君，路灯那边……好像一直在嗡嗡响。'); }
  async function talkJosukeHarbor(S) { await S.say('josuke', '康一，你耳朵灵，听听那些电线。'); }
  async function beatOtoishi(S) {
    T().memberTalk({});
    S.hint(null);
    if (S.player.cid !== 'josuke') S.setLeader('josuke', { force: true, silent: true });
    const p = S.player, ko = S.actor('koichi');
    if (ko) { ko.follow = null; }
    const ot = S.spawn('otoishi', Math.max(40, p.x - 150), 154, { id: 'otoishi', facing: 1, name: '音石明' });
    const gt = T().prop(S, 'guitar', ot.x - 4, ot.y + 0.5, { id: 'guitar', z: 12 });
    stick(gt, ot, -4, 12);
    S.face(p, -1);
    if (ko) { await S.walk(ko, p.x + 24, 150, { speed: 70 }); S.face(ko, -1); }
    focus({ x: p.x - 70 });
    await S.walk(ot, p.x - 60, 156, { speed: 50 });
    S.music('tension', 0.4);
    await S.say('otoishi', '哟，就是你们俩啊。东方仗助，广濑康一。', { expr: 'smile' });
    S.nameCard('otoishi', { y: NAME_TOP });
    S.mark('ch4_otoishi');
    await S.wait(0.8);
    await S.say('otoishi', '我是辣妹的本体。你的手啊，我用一根小指头就能废掉。', { expr: 'smile' });
    S.music('battle', 0.3);
    await S.vs({ key: 'rhcp', hero: 'josuke', enemy: { cid: 'otoishi', anim: 'guitar' } });
    G.uifx.vsTag('rhcp');
    // QTE：一拳打断他伸出来的小指（喜剧）
    await S.press({ key: 'attack', window: 0.8, label: '按 J！' });
    await S.summon(p, { dur: 0.08, rise: 4 });
    S.standAct(p, 'punch', { dx: 22, z: 4, dur: 0.5 });
    S.sfx('punch', 0.9);
    S.sfxText('咔', ot, { dur: 0.8 });
    S.recall(p);
    ot.play('hurt');
    await S.say('otoishi', '我的小指——！', { expr: 'shock' });
    S.mark('ch4_pinky');
    // 掏出吉他弹一段 solo，小指“咔”地复位
    S.pose(ot, 'guitar');
    S.sfx('sax_melody', 0.5, 1.6);
    S.fx('sparkles', { x: ot.x, y: ot.y - 24, n: 6, radius: 14, colour: '#ffe060', period: 0.4, size: 2 }, { life: 1.2 });
    await S.wait(1.2);
    S.sfxText('咔', ot, { dur: 0.6 });
    await S.say('otoishi', '……开玩笑的。', { expr: 'smile' });
    await S.say('otoishi', '替身能在电线里跑，本体当然也得会点特技。去吧，辣妹！', { expr: 'smile' });
    S.unpose(ot);
    // 他转身跑进仓库
    S.walk(ot, -40, 148, { speed: 110, anim: 'run' }).then(() => { ot.remove = true; gt.remove = true; }, G.cancelIgnore);
    await S.wait(0.6);
    G.uifx.vsTag(null);
    focus(null);
    // 段 B：仗助；康一在旁边喊方位（不参战）
    S.party(['josuke'], { leader: 'josuke' });
    place(S, 'koichi', p.x - 60, 146, 1);
  }
  // ================================================================ 节拍 7 段 B 收尾 → 船上
  async function beatAfterHarbor(S) {
    const p = S.player, ko = S.actor('koichi');
    await S.wait(0.4);
    if (ko) { S.walk(ko, p.x - 30, 150, { speed: 70 }).catch(G.cancelIgnore); }
    await S.say('koichi', '……音石明呢？刚才还在仓库那边！', { expr: 'shock' });
    const boat = T().prop(S, 'boat', 870, 112, { id: 'boat', z: 0 });
    focus({ x: 800 });
    await S.wait(0.8);
    await S.say('koichi', '他要是混上了那艘船……', { expr: 'shock' });
    await S.say('josuke', '承太郎先生和亿泰在船上。……亿泰，看你的了。');
    boat.remove = true;
    await S.fadeOut(0.5);
    focus(null);
  }
  async function shipIn(S) {
    S.party([OKU()], { leader: OKU() });
    await S.setStage('ship_ch4', { x: 120, y: 156, facing: 1, music: 'battle', fade: false });
    place(S, 'jotaro4', 610, 148, -1);
    place(S, 'joseph_old', 588, 150, -1);
    G.world.snapCamera();
    await S.fadeIn(0.4);
    S.location('ship', { y: NAME_TOP });
    await S.say('jotaro4', '亿泰。辣妹在这条船上，本体也是。……老头子交给你了。');
    await S.say(OKU(), '交、交给我？！……好！', { expr: 'shock' });
  }

  // ================================================================ 节拍 8 乔瑟夫下船 → 节拍 9 箭交给 SPW
  async function beatJoseph(S) {
    await S.setStage('harbor_ch4', { x: 690, y: 160, facing: 1, music: null, fade: false });
    S.party(['josuke'], { leader: 'josuke' });
    S.stopMusic(0.4);
    S.state('ship', 1);
    const p = S.player;
    Object.assign(p, { x: 700, y: 160, facing: 1 });
    const ko = place(S, 'koichi', 660, 150, 1);
    const ok = place(S, OKU(), 640, 164, 1);
    const jt = place(S, 'jotaro4', 820, 148, -1, { visible: false });
    const sp = S.spawn('spw_a', 840, 150, { id: 'spw_b', facing: -1, name: 'SPW 的工作人员', visible: false });
    const ot = S.spawn('otoishi', 860, 152, { id: 'oto_tied', facing: -1, visible: false });
    snapTo({ x: 760 });
    await S.fadeIn(0.6);
    S.sfx('ship_horn', 0.6);
    await S.wait(0.8);
    // SPW 押着音石明下船（只是垂着头）
    sp.visible = true; ot.visible = true;
    S.pose(ot, 'hurt');
    sp.x = 780; sp.y = 150; ot.x = 796; ot.y = 152;
    await S.walk(sp, 860, 146, { speed: 40 });
    sp.visible = false; ot.visible = false;
    // 乔瑟夫拄着拐杖，一步一顿走下舷梯
    const jo = place(S, 'joseph_old', 800, 140, -1);
    for (let i = 0; i < 4; i++) { await S.walk(jo, 800 - (i + 1) * 9, 140 + (i + 1) * 2.5, { speed: 18 }); await S.wait(0.25); }
    S.nameCard('joseph_old', { y: NAME_TOP });
    S.mark('ch4_joseph');
    await S.wait(0.6);
    jt.visible = true; jt.x = 800; jt.y = 146;
    await S.say('joseph_old', '哦哦，这就是日本的港口啊。……嗯？', { expr: 'smile', actor: jo });
    S.face(jo, ko);
    await S.say('joseph_old', '承太郎，你什么时候缩得这么小了？', { expr: 'smile', actor: jo });
    await S.say('koichi', '诶？我、我是广濑康一……', { expr: 'shock' });
    await S.say('jotaro4', '……老头子，你认错人了。我在你后面。', { actor: jt });
    await S.say('joseph_old', '哈？你说什么？', { actor: jo });
    // 仗助站在舷梯下一动不动 → 乔瑟夫脚下一滑 → 一言不发地扶住
    await S.wait(0.8);
    S.sfx('whoosh', 0.6);
    jo.play('hurt');
    await S.animate(0.25, (k) => { jo.rot = -0.4 * k; });
    await S.walk(p, jo.x - 14, jo.y + 4, { speed: 120, anim: 'run' });
    S.face(p, 1);
    jo.rot = 0; jo.play('idle');
    S.mark('ch4_support');
    await S.wait(1.0);
    await S.say('joseph_old', '……谢谢你，小伙子。', { actor: jo });
    await S.say('josuke', '……走路看着点脚下。');
    S.walk(p, 690, 162, { speed: 50 }).catch(G.cancelIgnore);
    await S.wait(1.5);
    S.music('sad', 1.0);
    await S.narrate('那天仗助君一句话也没多说。', { pos: 'top' });
    // 节拍 9：箭交给 SPW
    await S.say('jotaro4', '从音石明那里拿回来的箭，交给 SPW 保管。', { actor: jt });
    const sp2 = S.spawn('spw_a', 860, 150, { id: 'spw_c', facing: -1, name: 'SPW 的工作人员' });
    await S.walk(sp2, jt.x + 22, 150, { speed: 60 });
    const box = T().prop(S, 'arrowcase', jt.x + 8, jt.y + 0.5, { id: 'arrowcase', z: 14 });
    await S.animate(0.4, (k) => { box.x = jt.x + 8 + 12 * k; });
    S.sfx('pop', 0.6);
    await S.notice({ title: '弓与箭的下落', text: '第一支箭 → SPW 财团保管' });
    S.mark('ch4_arrow_spw');
    box.remove = true;
    void ok;
    await S.fadeOut(0.8);
  }

  // ================================================================ 节拍 10 几天后（自由走动 + 解谜透明宝宝）
  const BOX = [470, 152], CLERK = [600, 152];
  let baby = null;
  async function streetIn(S) {
    S.party(['josuke', 'joseph_old'], { leader: 'josuke' });
    await S.setStage('street_ch4', { x: 120, y: 160, facing: 1, music: 'daily', fade: false });
    const jo = S.actor('joseph_old');
    if (jo) { Object.assign(jo, { x: 90, y: 156, facing: 1 }); }
    T().prop(S, 'box', BOX[0], BOX[1] + 0.5, { id: 'box', frame: 1 });
    T().prop(S, 'tv', 252, 146, { id: 'tv_shop', z: 18 });
    G.world.snapCamera();
    await S.fadeIn(0.6);
    await S.title('days_later', { y: 110 });
    S.mark('ch4_walk');
    await S.say('joseph_old', '仗助君，你……今年几岁了？');
    await S.say('josuke', '十六。');
    await S.say('joseph_old', '哈？你说什么？');
    await S.say('josuke', '……十六！');
    await S.say('joseph_old', '我给你买点什么吧。想要什么？', { expr: 'smile' });
    await S.say('josuke', '真的？……不、不用了。', { expr: 'smile' });
    S.hint('Q 换成乔瑟夫：按 U 念写（对着电视）', 7);
    trailWatch();
  }
  async function talkJosephStreet(S) { await S.say('joseph_old', F().photo ? '得往她身上抹点什么，才能看见。' : '仗助君，走慢一点……老头子跟不上啦。'); }
  async function talkJosukeStreet(S) { await S.say('josuke', '老爷子，别走丢了。'); }
  async function useBox(S) {
    const p = S.player;
    if (!F().boxSeen) {
      F().boxSeen = true;
      await S.say('josuke', '哭声就在这里……可箱子是空的？', { expr: 'shock' });
      S.hint('Q 换成乔瑟夫，对着纸箱按 U：念写', 8);
      return;
    }
    if (!F().photo) { await S.say(p.cid, '……空的纸箱。哭声却是从里面出来的。'); return; }
    if (!F().compact) { await S.say('joseph_old', '得往她身上抹点什么……药妆店应该有粉底。'); S.hint('往右走：找药妆店的店员', 5); return; }
    if (F().makeup) { await S.say(null, '纸箱空了。'); return; }
    // 往宝宝脸上抹粉底 → 显形一半
    F().makeup = true;
    S.sfx('sparkle', 0.6);
    S.fx('smoke', { x: BOX[0], y: BOX[1] - 10, colour: '#f4d4b4', n: 6, rise: 6, life: 0.6 }, { life: 0.8 });
    baby = S.spawn('shizuka', BOX[0], BOX[1] + 1, { id: 'shizuka', facing: -1, alpha: 0 });
    baby.z = 6;
    await S.animate(0.6, (k) => { baby.alpha = 0.55 * k; });
    S.mark('pz_baby_makeup');
    await S.say('joseph_old', '是个女孩子。', { expr: 'smile' });
    await S.say('josuke', '……真的有个婴儿。', { expr: 'shock' });
    // 打了个喷嚏，粉底蹭掉，又不见了 → 手印往右
    S.sfxText('啊嚏！', baby, { dur: 0.8 });
    S.sfx('pop', 0.7);
    await S.animate(0.3, (k) => { baby.alpha = 0.55 * (1 - k); });
    baby.remove = true; baby = null;
    await S.say('josuke', '又不见了！……地上有小手印！', { expr: 'shock' });
    F().trail = 0;
    trailNext(S);
    S.hint('跟着地上的小手印往右走', 6);
  }
  // 地上的手印：走到一个，下一个在前方 70 px 出现；到地图右端换到公园
  const TRAIL = [520, 590, 660, 730, 800, 870];
  function trailNext(S) {
    const i = F().trail;
    if (i >= TRAIL.length) return;
    T().prop(S, 'shizuka_hand', TRAIL[i], 156 + (i % 2 ? 6 : -2), { id: 'hand' + i, frame: 0 });
    if (i === 0) S.mark('pz_baby_trail');
  }
  function setupStreet() {
    Object.assign(ST.street_ch4, {
      npcs: [
        T().npc('clerk', 'clerk_d', CLERK[0], CLERK[1], { facing: -1, label: '药妆店的店员', talk: talkClerk }),
      ],
      hotspots: [
        { id: 'tv_shop', x: 252, y: 152, r: 18, label: '电器店的电视', tags: ['nensha'], photo: { image: 'props/photo_starfish' },
          use: async (S) => { await S.say(null, '电器店橱窗里摆着一台电视。'); },
          look: async (S) => { await S.say('joseph_old', '……是海星。承太郎这孩子，又跑去海边了。'); await S.say('josuke', '念写……就是这么用的？', { expr: 'shock' }); } },
        { id: 'box', x: BOX[0], y: BOX[1], r: 18, label: '纸箱', tags: ['nensha'], photo: { image: 'props/photo_baby' }, cameraAt: { x: BOX[0] + 14, y: BOX[1], z: 0 },
          cond: () => !F().makeup, use: useBox, look: lookBox },
        { id: 'vending', x: 531, y: 152, r: 14, label: '自动售货机', use: async (S) => { await S.say(null, '自动售货机。'); } },
      ],
      triggers: [
        { x0: 420, x1: 470, run: async (S) => { if (F().cry) return; F().cry = true; S.sfxText('哇——', { wx: BOX[0], wy: BOX[1], wz: 20 }, { dur: 1.2 }); await S.say('josuke', '……婴儿的哭声？', { expr: 'shock' }); } },
        { x0: 920, x1: 1000, cond: () => F().trail >= TRAIL.length, run: async () => { F().toPond = true; } },
      ],
    });
  }
  function trailWatch() {
    // 手印：走到一个，就出下一个
    T().tick(() => {
      const p = G.world.player;
      if (F().toPond) return true;
      const i = F().trail;
      if (i == null || i >= TRAIL.length || !p) return false;
      if (p.x >= TRAIL[i] - 12) { F().trail = i + 1; if (i + 1 < TRAIL.length) trailNext(G.S); }
      return false;
    });
  }
  async function lookBox(S, h, p) {
    if (p.cid !== 'joseph_old') return;
    F().photo = true;
    S.mark('pz_baby_photo');
    await S.say('joseph_old', 'OH MY GOD！是个看不见的婴儿！', { expr: 'shock' });
    await S.say('joseph_old', '得往她身上抹点什么，才能看见。');
    S.hint('往右走：药妆店的店员那里能买到粉底', 6);
  }
  async function talkClerk(S, me) {
    if (!F().photo) { await T().say(S, me, '欢迎光临～'); return; }
    if (F().compact) { await T().say(S, me, '谢谢惠顾～'); return; }
    await S.say('josuke', '那个……请给我一盒粉底。');
    await T().say(S, me, '好的，这一款三千日元。', { expr: 'smile' });
    await S.say('josuke', '三千日元？！', { expr: 'shock' });
    await S.say('joseph_old', '哈哈，这个我来！', { expr: 'smile' });
    S.sfx('coin', 0.8);
    T().floater(S, 'prop:compact', S.player.x, S.player.y + 0.5, { z: 40, rise: 10, dur: 0.9 });
    await S.say(null, '乔瑟夫掏出一张一万日元的大钞。');
    F().compact = true;
    S.hint('拿到粉底：回到纸箱那里按 E', 6);
  }

  // ================================================================ 透明宝宝第 4 步：公园池塘
  async function pondIn(S) {
    await S.setStage('pond_ch4', { x: 24, y: 160, facing: 1, music: 'daily', fade: true });
    const jo = S.actor('joseph_old');
    if (jo) Object.assign(jo, { x: 8, y: 154, facing: 1 });
    S.location('park', { y: NAME_TOP });
    const marks = [[60, 160, 0], [150, 164, 1], [220, 158, 0], [270, 166, 0], [330, 170, 1]];
    marks.forEach(([x, y, fr], i) => T().prop(S, 'shizuka_hand', x, y, { id: 'phand' + i, frame: fr }));
    await S.say('josuke', '手印压在落叶和水洼上……一路通到池塘！');
  }
  function setupPond() {
    Object.assign(ST.pond_ch4, {
      npcs: [], triggers: [{ x0: 280, x1: 500, run: async () => { F().pondGo = true; } }],
      hotspots: [
        { id: 'pond_edge', x: 320, y: 148, r: 22, label: '池边', tags: ['nensha'], lookOnly: true, cond: () => !!F().splash && !F().blood,
          use: async (S) => { await S.say(null, '水面上一圈一圈的涟漪。'); }, look: bite },
        { id: 'splash', x: 322, y: 148, r: 20, label: '水花', cond: () => !!F().blood && !F().saved, use: rescue },
        { id: 'bench', x: 82, y: 150, r: 16, label: '长椅', use: async (S) => { await S.say(null, '公园的长椅。'); } },
        { id: 'sign', x: 177, y: 150, r: 14, label: '牌子', use: async (S) => { await S.say(null, '「池塘危险　禁止游泳」'); } },
      ],
    });
  }
  let pondTimer = null;
  async function pondSplash(S) {
    F().splash = true;
    S.sfx('splash', 1);
    S.sfxText('扑通', { wx: 322, wy: 124, wz: 0 }, { dur: 1.0 });
    S.state('ring', 1);
    S.mark('pz_baby_pond');
    await S.say('josuke', '掉进池塘里了！', { expr: 'shock' });
    await S.say('joseph_old', '看不见她在哪儿……得想个办法！', { expr: 'shock' });
    S.hint('Q 换成乔瑟夫，走到池边按 U', 10);
    const t0 = now();
    if (pondTimer) pondTimer.close();
    pondTimer = P4().overlay((g) => {
      if (F().saved || !G.world || G.world.insert) return;
      const left = Math.max(0, 30 - (now() - t0));
      const x0 = 220, y0 = 14, w = 200;
      g.fillStyle = '#1a1020'; g.fillRect(x0 - 2, y0 - 2, w + 4, 12);
      g.fillStyle = '#2a4a6a'; g.fillRect(x0, y0, w, 8);
      g.fillStyle = left < 10 ? '#ff6050' : '#7ad0ff'; g.fillRect(x0, y0, Math.round(w * left / 30), 8);
      P4().text(g, '静在水里　' + Math.ceil(left) + ' s', 320, y0 + 12, '#e0f6ff', 12, 'center');
    }, { z: 2 });
    F().pondT0 = t0;
  }
  async function bite(S, h, p) {
    if (p.cid !== 'joseph_old' || F().blood) return;
    await doBite(S, p);
  }
  async function doBite(S, jo) {
    F().blood = true;
    S.pose(jo, 'point');
    S.sfx('teeth_crunch', 0.5);
    await S.say('joseph_old', '……用这个。', { expr: 'rage' });
    S.sfx('drip', 0.8);
    S.fx('glint', { x: 322, y: 124, size: 6 }, { life: 0.4 });
    S.state('red', 1);
    S.mark('pz_baby_blood');
    S.unpose(jo);
    await S.say('joseph_old', '一滴血，就能勾出她的轮廓！仗助君，就在那里！', { expr: 'shock' });
    if (S.player.cid !== 'josuke') S.setLeader('josuke', { force: true, silent: true });
    S.hint('走到水花那里按 E：把她捞起来', 8);
  }
  async function rescue(S) {
    if (!F().blood || F().saved) return;
    const p = S.player;
    if (p.cid !== 'josuke') S.setLeader('josuke', { force: true, silent: true });
    F().saved = true;
    S.hint(null);
    S.sfx('splash', 0.9);
    S.fx('water_splash', { x: 322, y: 130, size: 1.0 }, { life: 0.6 });
    S.state('ring', 0);
    S.state('red', 0);
    S.mark('pz_baby_saved');
    if (pondTimer) { pondTimer.close(); pondTimer = null; }
  }

  // ================================================================ 节拍 10 结尾 → 节拍 11
  async function beatShizuka(S) {
    const p = S.player;
    T().memberTalk({});
    const jo = S.actor('joseph_old');
    if (jo) { jo.follow = null; await S.walk(jo, p.x - 24, p.y - 2, { speed: 50 }); S.face(jo, p); }
    S.face(p, jo);
    await S.say('josuke', '捞上来了！……抱着是软软的，可什么也看不见。', { expr: 'smile' });
    if (jo) S.pose(jo, 'hold');
    await S.say('joseph_old', '这孩子的父母，大概是被她的替身吓坏了吧。……没人来找她。');
    await S.say('joseph_old', '我来养她。名字嘛……她哭够了，就安安静静的。叫“静”吧。', { expr: 'smile' });
    await S.say('joseph_old', '静·乔斯达。', { expr: 'smile' });
    S.nameCard('shizuka', { y: NAME_TOP });
    S.standCard('achtung', { y: NAME_TOP });
    S.cue('sting_reveal');
    S.mark('ch4_shizuka');
    await S.wait(1.6);
    S.music('victory', 1.0);
    await S.say('joseph_old', '仗助君，我这个老头子，没为你做过什么。', { expr: 'smile' });
    await S.say('joseph_old', '以后……能让我偶尔来看看你吗？');
    await S.wait(1.0);
    await S.say('josuke', '……老爷子，先把手上的伤修好吧。', { expr: 'smile' });
    await S.summon(p, { dur: 0.12, rise: 4 });
    S.standAct(p, 'reach', { dx: 16, z: 2, dur: 0.8 });
    if (jo) P4().fixGlow(S, jo.x + 6, jo.y - 18);
    await S.wait(0.7);
    S.recall(p);
    S.mark('ch4_smile');
    await S.narrate('那是我第一次看见，仗助君对他的父亲笑。', { pos: 'top' });
    S.stopMusic(0.6);
    await S.tbc({ hold: 2.0 });
    S.mark('ch4_tbc');
  }

  // ================================================================ 第4章主流程
  G.STORY.ch4 = async function (S) {
    if (T().resetCounters) T().resetCounters();
    P4().clearOverlays();
    baby = null; pondTimer = null; bikeProp = null;
    await S.chapterCard('ch4');
    S.party(['josuke'], { leader: 'josuke' });
    setupLiving();
    await S.run(async (S2) => { await beatCalendar(S2); await livingIn(S2); }, { keepLocked: true });
    // 节拍 2 自由走动：电视 E，或 40 s 后自动
    await S.run(async () => {});
    const t2 = now();
    await S.until(() => (F().tvGo || now() - t2 > 40) && !S.busy);
    await S.run(async (S2) => {
      await beatTvHand(S2);
      await beatHotel(S2);
      await beatField(S2);
      await CH().fightA(S2);
      await beatCable(S2);
    }, { keepLocked: true });
    // 节拍 6 杜王港自由走动：康一 U 听路灯 / 往右走到 560 / 45 s
    setupHarbor();
    await S.run(harborIn);
    T().memberTalk({ koichi: talkKoichiHarbor, josuke: talkJosukeHarbor });
    T().goal(S, { x: 411, y: 150, label: '路灯', delay: 20, every: 15, done: () => !!F().otoGo, text: 'Q 换成康一，走到路灯下按 U' });
    const t6 = now();
    await S.until(() => (F().otoGo || now() - t6 > 45) && !S.busy);
    Object.assign(ST.harbor_ch4, { npcs: [], hotspots: [], triggers: [] });
    for (const id of ['spw_h', 'fisher']) { const a = S.actor(id); if (a) a.remove = true; }
    await S.run(async (S2) => {
      await beatOtoishi(S2);
      await CH().fightB(S2);
      await beatAfterHarbor(S2);
      await shipIn(S2);
      await CH().fightC(S2);
      S2.mark('b06c_ko');
      await beatJoseph(S2);
    }, { keepLocked: true });
    // 节拍 10 几天后：父子散步 + 透明宝宝 1–3 步
    setupStreet();
    await S.run(streetIn);
    T().memberTalk({ joseph_old: talkJosephStreet, josuke: talkJosukeStreet });
    T().goal(S, { x: BOX[0], y: BOX[1], label: '纸箱', delay: 25, every: 20, done: () => !!F().boxSeen, text: '往右走：好像有婴儿的哭声' });
    T().goal(S, { x: CLERK[0], y: CLERK[1], label: '店员', delay: 15, every: 20, when: () => !!F().photo, done: () => !!F().compact, text: '药妆店的店员（右边）能买到粉底' });
    T().goal(S, { x: BOX[0], y: BOX[1], label: '纸箱', delay: 8, every: 20, when: () => !!F().compact, done: () => !!F().makeup, text: '回到纸箱那里，按 E 给她抹粉底' });
    T().goal(S, { x: 940, y: 158, label: '手印', delay: 15, every: 20, when: () => !!F().makeup, done: () => !!F().toPond, text: '跟着地上的小手印往右走' });
    await S.until(() => !!F().toPond && !S.busy);
    // 第 4 步：池塘
    setupPond();
    await S.run(async (S2) => { await pondIn(S2); }, { keepLocked: true });
    await S.run(async () => {});
    T().memberTalk({ joseph_old: async (S2) => { await S2.say('joseph_old', F().splash ? '池边……让我到池边去！' : '手印往池塘那边去了！'); } });
    await S.until(() => !!F().pondGo && !S.busy);
    await S.run(pondSplash);
    T().goal(S, { x: 320, y: 150, label: '池边', delay: 10, every: 15, done: () => !!F().blood, text: 'Q 换成乔瑟夫，走到池边按 U' });
    // 30 s 到了还没做：乔瑟夫自己扑到池边做完前半
    await S.until(() => (F().blood || now() - (F().pondT0 || now()) > 30) && !S.busy);
    if (!F().blood) {
      await S.run(async (S2) => {
        const jo = S2.actor('joseph_old');
        if (jo) { jo.follow = null; await S2.walk(jo, 320, 148, { speed: 70 }); S2.face(jo, 1); }
        await S2.say('joseph_old', '来不及了！让开！', { expr: 'rage' });
        await doBite(S2, jo || S2.player);
      });
    }
    T().goal(S, { x: 322, y: 150, label: '水花', delay: 6, every: 15, done: () => !!F().saved, text: '走到水花那里按 E' });
    await S.until(() => !!F().saved && !S.busy);
    await S.run(beatShizuka, { keepLocked: true });
  };
  G.STORY.ch4.marks = ['ch4_calendar', 'ch4_tv_hand', 'ch4_socket', 'ch4_hotel', 'ch4_field', 'ch4_eavesdrop', 'b06a_start', 'b06a_pull3',
    'b06a_bike_down', 'b06a_cable', 'ch4_okuyasu_fixed', 'ch4_harbor', 'ch4_otoishi', 'ch4_pinky', 'b06b_start', 'b06b_sticky', 'b06b_flash',
    'b06b_tyre', 'b06b_sea', 'b06c_start', 'b06c_save_joseph', 'b06c_found', 'b06c_ko', 'ch4_joseph', 'ch4_support', 'ch4_arrow_spw',
    'ch4_walk', 'pz_baby_photo', 'pz_baby_makeup', 'pz_baby_trail', 'pz_baby_pond', 'pz_baby_blood', 'pz_baby_saved', 'ch4_shizuka',
    'ch4_smile', 'ch4_tbc'];
})();
