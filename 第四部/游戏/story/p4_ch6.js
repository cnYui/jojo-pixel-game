// 第6章　幽灵小路 / 丰收与纽扣（G.STORY.ch6，地图 id 后缀 _ch6）。开发脚本：第四部/docs/第6章_开发脚本.md
//   节拍 1 篇章卡 → 日历地图 → 2 幽灵小路（露伴 ⇄ 康一、铃美）→ 探索「不能回头」→ 3 吉良视角 → 4 几天后：售货机、重清
//   → 小游戏「捡硬币」→ 5 中奖 → 6 银行（仗助修彩票）→ 7 门口吵翻 → 第 9 战 → 8 和好 → 9 拿错纸袋 → 10 体育仓库
//   → 第 10 战（三段，目标段）→ 11 纽扣 → 12 幽灵小路（承太郎、乔瑟夫、线索板）→ 13 擦肩而过 → To Be Continued
//   克制：吉良纸袋里的东西不画；铃美和阿诺德的死只用旁白；硬币炸弹只有白光；重清之死只给白光、丰收一只只消失和剪影。
//   战斗、探索、小游戏在 story/p4_ch6_fights.js（G.P4CH6）。
'use strict';
(function () {
  const G = window.G, { base, walls } = G.p4Stage;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const F6 = () => G.P4CH6;
  const F = () => G.flags;
  const now = () => (G.clk ? G.clk.world : 0);
  const NAME_TOP = 100;
  // 别章画的人：正式图合进来了就用正式的，没有才用本章的临时图（第6章开发脚本 §0）
  const has = (cid) => !!(G.D && G.D.chars && G.D.chars[cid]);
  const OKU = () => (has('okuyasu') ? 'okuyasu' : 'tmp6_okuyasu');
  const JOS = () => (has('joseph_old') ? 'joseph_old' : 'tmp6_joseph');
  const ROHAN = 'rohan';
  G.P4CH6CID = { OKU, JOS };

  Object.assign(G.NAMES, {
    shigechi: '重清', harvest: '丰收', kira: '吉良', killerqueen: '杀手皇后', reimi: '铃美', arnold: '阿诺德',
    tmp6_okuyasu: '亿泰', okuyasu: '亿泰', rohan: '露伴', tmp6_joseph: '乔瑟夫', joseph_old: '乔瑟夫',
  });

  // ================================================================ 地图（交接说明 docs/第6章_背景.md）
  const ST = G.STAGES;
  ST.map_ch6 = base('map_ch6', 'morioh_map', 320, { yMin: 160, yMax: 170, music: null, obstacles: [] });
  ST.alley_ch6 = base('alley_ch6', 'ghost_alley', 640, { music: 'tension', state: { dark: 0, hands: 0 }, obstacles: walls(8, 632, 640) });
  ST.deli_ch6 = base('deli_ch6', 'st_gentleman', 480, { music: 'tension', obstacles: walls(8, 472, 480) });
  ST.road_ch6 = base('road_ch6', 'morioh_road', 960, { music: 'daily', state: { pm: 0 } });
  ST.town_ch6 = base('town_ch6', 'morioh_blocks', 320, { music: 'battle', yMin: 160, yMax: 170, obstacles: [] });
  ST.bank_ch6 = base('bank_ch6', 'budogaoka_bank', 320, { music: 'daily', obstacles: walls(8, 312, 320) });
  // 第 9 战两屏：外墙（0–320）和楼顶（320–640）是同一张图，舞台用 x0 / x1 把镜头卡在一屏里
  ST.wall_ch6 = base('wall_ch6', 'rooftops', 640, { x0: 0, x1: 320, yMin: 150, yMax: 150, music: 'battle', obstacles: walls(16, 292, 640) });
  ST.roof_ch6 = base('roof_ch6', 'rooftops', 640, { x0: 320, x1: 640, camX: 320, music: 'battle', obstacles: walls(330, 632, 640),
    state: { brk1: 0, brk2: 0, brk3: 0, brk4: 0 } });
  ST.jhs_ch6 = base('jhs_ch6', 'middle_school', 640, { music: 'tension', state: { pm: 0 }, obstacles: walls(8, 628, 640) });

  // ================================================================ 日历地图：三枚新图钉 + 1999年6月（p4_common.js 的 CAL）
  P4().CAL.ch6 = {
    pins: [{ at: 'ch6_alley', label: '幽灵小路', xy: [190, 96] }, { at: 'ch6_bank', label: '葡萄丘银行', xy: [222, 82] },
      { at: 'ch6_jhs', label: '葡萄丘中学', xy: [138, 58] }],
    stamp: 'stamp_199906',
  };

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
  const ghost = (a) => { if (a) { a.alpha = 0.78; a.shadow = false; } return a; };

  // ================================================================ 节拍 1
  async function beatCalendar(S) {
    S.player.visible = false;
    await S.setStage('map_ch6', { x: 160, y: 165, music: null });
    const cal = await P4().calendar(S, 'ch6', { hold: 1.8 });
    S.mark('ch6_calendar');
    await S.fadeOut(0.45);
    if (cal) cal.close();
  }

  // ================================================================ 节拍 2 幽灵小路：露伴、康一、铃美
  const AL = { reimi: [300, 152], arnold: [318, 158], start: 330, exit: 600 };
  async function beatAlley(S) {
    S.party([ROHAN, 'koichi'], { leader: ROHAN });
    await S.setStage('alley_ch6', { x: 22, y: 156, facing: 1, music: 'tension', fade: false });
    const p = S.player, ko = S.actor('koichi') || place(S, 'koichi', 6, 160, 1);
    Object.assign(ko, { x: 4, y: 160, facing: 1 });
    S.state('dark', 0); S.state('hands', 0);
    const rm = ghost(S.spawn('reimi', AL.reimi[0], AL.reimi[1], { id: 'reimi', facing: -1, name: '少女' }));
    const ar = ghost(S.spawn('arnold', AL.arnold[0], AL.arnold[1], { id: 'arnold', facing: -1, name: '狗' }));
    rm.visible = false; ar.visible = false;
    snapTo(p);
    await S.fadeIn(0.6);
    S.location('ghost_alley', { y: NAME_TOP });
    S.mark('ch6_alley');
    S.walk(ko, 60, 160, { speed: 40 }).catch(G.cancelIgnore);
    await S.walk(p, 92, 156, { speed: 40 });
    await S.say('koichi', '露伴老师，说好的“取材”……就是在大街上走来走去？');
    await S.say(ROHAN, '漫画家的眼睛不能离开现实。你走你的，别出声。');
    await S.say('koichi', '……诶？这两栋楼中间，以前有这么一条小巷吗？', { expr: 'shock' });
    await S.say(ROHAN, '没有。所以才要进去看看。', { expr: 'smile' });
    S.walk(ko, 170, 160, { speed: 40 }).catch(G.cancelIgnore);
    await S.walk(p, 208, 154, { speed: 40 });
    // 巷子深处慢慢浮出一个少女和一条狗
    rm.visible = true; ar.visible = true; rm.alpha = 0; ar.alpha = 0;
    S.sfx('glint', 0.5);
    await S.animate(0.8, (k) => { rm.alpha = 0.78 * k; ar.alpha = 0.78 * k; });
    S.sfx('dog_bark', 0.5);
    await S.say('reimi', '……你们，能看见我？', { actor: rm, name: '少女' });
    S.nameCard('reimi', { y: NAME_TOP });
    await S.say('reimi', '我叫杉本铃美。这条狗是阿诺德。', { actor: rm, name: '铃美', expr: 'smile' });
    await S.say('koichi', '（她的脚……没有影子。）', { expr: 'shock' });
    rm.name = '铃美'; ar.name = '阿诺德';
  }
  // 自由走动：铃美、阿诺德能搭话，露伴 U 读不了幽灵
  async function talkReimi(S) {
    if (F().ch6TalkReimi) { await T().say(S, 'reimi', '你们想知道的，我都会告诉你们。'); return; }
    F().ch6TalkReimi = true;
    S.mark('ch6_reimi');
    await T().say(S, 'reimi', '这条小巷，只有被它选中的人才能进来。');
    await T().say(S, 'reimi', '我有一件事……想拜托能看见我的人。');
  }
  async function readReimi(S, h, p) {
    if (p.cid !== ROHAN) return;
    if (F().ch6ReadGhost) { await S.say(ROHAN, '……还是读不了。'); return; }
    F().ch6ReadGhost = true;
    S.mark('ch6_read_ghost');
    await S.say(ROHAN, '天堂之门！……');
    await S.say(ROHAN, '……读不了。她的身体里一页纸都没有。有意思。', { expr: 'smile' });
    await T().say(S, 'reimi', '我已经不是活人了。书……大概也跟着一起没了吧。', { expr: 'smile' });
  }
  function setupAlleyFree(S) {
    const st = G.world.stage, rm = S.actor('reimi'), ar = S.actor('arnold');
    if (rm) { rm.talk = talkReimi; rm.label = '铃美'; }
    if (ar) {
      ar.label = '阿诺德';
      ar.talk = async (S2) => { S2.sfx('dog_bark', 0.5); await S2.say(null, '阿诺德摇了摇尾巴。……摸上去什么也碰不到。'); };
    }
    st.hotspots.push(
      { id: 'reimi_read', x: AL.reimi[0], y: AL.reimi[1], r: 22, ry: 14, label: '铃美', tags: ['read'], fx: AL.reimi[0], fy: 128,
        use: talkReimi, look: readReimi },
      { id: 'ac', x: 163, y: 150, r: 14, label: '空调外机', use: async (S2) => { await S2.say(null, '空调外机在转。……可巷子里一点风也没有。'); } },
      { id: 'door', x: 192, y: 148, r: 12, label: '铁后门', use: async (S2) => { S2.sfx('creak', 0.5); await S2.say(null, '铁门锁着。门牌上的字被磨掉了。'); } },
      { id: 'bike', x: 273, y: 150, r: 14, label: '自行车', use: async (S2) => { await S2.say(null, '一辆很旧的儿童自行车，铃铛锈死了。'); } },
      { id: 'plants', x: 400, y: 148, r: 16, label: '盆栽', use: async (S2) => { await S2.say(null, '一排盆栽。花开着，却全是灰色的。'); } },
    );
    S.hint('和铃美说话（E）。露伴按 U：天堂之门“阅读”', 7);
  }
  async function beatPromise(S) {
    const p = S.player, rm = S.actor('reimi'), ko = S.actor('koichi');
    if (p.cid !== ROHAN) S.setLeader(ROHAN, { force: true, silent: true });
    const pl = S.player;
    await S.walk(pl, AL.reimi[0] - 30, 154, { speed: 50 });
    S.face(pl, 1);
    if (ko) { ko.follow = null; await S.walk(ko, AL.reimi[0] - 54, 162, { speed: 50 }); S.face(ko, 1); }
    S.music('sad', 1.0);
    await T().say(S, 'reimi', '十五年前的一个夜里，有人闯进了我家。');
    await S.narrate('那天夜里，铃美和阿诺德再也没有醒来。凶手是谁，到今天也没人知道。', { pos: 'top' });
    await T().say(S, 'reimi', '那天晚上，隔壁家的小男孩住在我家。我把他从窗口推了出去。');
    await T().say(S, 'reimi', '他活下来了。……后脑勺上，大概会留一道疤吧。');
    await S.say(ROHAN, '……！', { expr: 'shock' });
    await S.say(ROHAN, '四岁那年的事，我什么都不记得。只有后脑这道疤。', { expr: 'shock' });
    await S.say('koichi', '露伴老师，难道那个小孩就是……', { expr: 'shock' });
    await T().say(S, 'reimi', '那个人现在还住在这个镇上，过着很平静的日子。', { expr: 'rage' });
    await T().say(S, 'reimi', '我想拜托你们，找出他。', { expr: 'normal' });
    await S.say(ROHAN, '……我拒绝——欠人一条命还装作没听见这种事。', { expr: 'rage' });
    await S.say(ROHAN, '这个委托，我接了。');
    S.mark('ch6_promise');
    await T().say(S, 'reimi', '谢谢。……还有，出去的时候千万别回头。', { expr: 'smile' });
    await T().say(S, 'reimi', '在这条巷子里回头的人，会被带到“那边”去。', { expr: 'normal' });
    if (rm) { S.animate(0.8, (k) => { rm.alpha = 0.78 * (1 - k); }).catch(G.cancelIgnore); }
    const ar = S.actor('arnold');
    if (ar) S.animate(0.8, (k) => { ar.alpha = 0.78 * (1 - k); }).catch(G.cancelIgnore);
    await S.wait(0.9);
    if (rm) rm.remove = true;
    if (ar) ar.remove = true;
    S.music('tension', 0.8);
  }
  async function afterAlley(S) {
    const p = S.player;
    S.state('dark', 0); S.state('hands', 0);
    S.flash(0.3, 0.6, '#ffffff');
    await S.wait(0.3);
    await S.say('koichi', '……出、出来了。', { expr: 'shock' });
    await S.say(ROHAN, '回头看看。', { expr: 'smile' });
    S.face(p, -1);
    await S.say('koichi', '……墙。小巷不见了。', { expr: 'shock' });
    await S.say(ROHAN, '一个住在镇上的杀人魔。……这可是一辈子也画不完的好素材。', { expr: 'smile' });
    await S.fadeOut(0.6);
  }

  // ================================================================ 节拍 3 吉良视角
  async function beatKiraPov(S) {
    S.party(['josuke'], { leader: 'josuke' });
    await S.setStage('deli_ch6', { x: 20, y: 160, facing: 1, music: null, fade: false });
    S.player.visible = false;
    const kr = S.spawn('kira', 336, 150, { id: 'kira_pov', facing: -1, name: '西装男人' });
    const bag = T().prop(S, 'paperbag', 352, 150, { id: 'kbag', z: 8 });
    snapTo({ x: 330 });
    S.filter('vignette', 0.55, { colour: '#3a1a4a', inner: 0.5 });
    await S.fadeIn(0.8);
    await S.title('kira_pov', { y: 60 });
    S.music('tension', 1.2);
    S.mark('ch6_kira_pov');
    const say = (t, o = {}) => S.say('kira', t, Object.assign({ actor: kr, name: '西装男人' }, o));
    await say('……我的名字无关紧要。我只想过平静的生活。');
    await say('不抽烟，酒浅尝即止。晚上十一点睡下，一觉睡足八个小时。');
    await say('不想赢，也不想输。像一株植物那样，安安静静地活着。');
    S.face(kr, 1);
    await say('……可指甲长得太快的时候，就没办法了。', { expr: 'smile' });
    await say('嗯，不用担心。今天也一起去公园吧。', { expr: 'smile' });
    S.sfx('menacing', 0.6);
    await S.wait(0.8);
    await S.fadeOut(0.7);
    S.filter('vignette', null);
    kr.remove = true;
    if (bag) bag.remove = true;
  }

  // ================================================================ 节拍 4 几天后：售货机、重清
  const RD = { vending: [531, 150], start: [320, 158] };
  async function beatDaysLater(S) {
    S.party(['josuke', OKU()], { leader: 'josuke' });
    await S.setStage('road_ch6', { x: RD.start[0], y: RD.start[1], facing: 1, music: 'daily', fade: false });
    S.state('pm', 0.5);
    const p = S.player;
    snapTo(p);
    await S.fadeIn(0.6);
    await S.title('days_later', { y: 110 });
    S.mark('ch6_days_later');
    await S.say(OKU(), '仗助，借我一百日元。我想买罐果汁。');
    await S.say('josuke', '我比你还惨。考试考砸了，老妈把我这个月的零花钱扣光了。', { expr: 'shock' });
    await S.say('josuke', '全部家当：三百日元。', { expr: 'shock' });
    await S.say(OKU(), '……我脑子不好使，可这个数我算得出来。不够两个人花。', { expr: 'shock' });
    S.hint('四处看看（E）。仗助好像很在意那台自动售货机', 6);
  }
  async function useVending(S) {
    if (F().ch6Vending) { await S.say(null, '售货机底下黑漆漆的。'); return; }
    F().ch6Vending = true;
    const p = S.player;
    S.face(p, 1);
    await S.say('josuke', '自动售货机底下，经常有人掉零钱……', { expr: 'smile' });
    await S.say(null, '仗助趴下去往底下看——');
    S.mark('ch6_vending');
    await S.say('josuke', '……里面有什么东西在动。', { expr: 'shock' });
  }
  function setupRoadFree(S) {
    const st = G.world.stage;
    st.hotspots.push(
      { id: 'vending', x: RD.vending[0], y: RD.vending[1], r: 18, label: '自动售货机', use: useVending },
      { id: 'busstop', x: 452, y: 150, r: 14, label: '公交站牌', use: async (S2) => { await S2.say(OKU(), '坐车也要钱啊……'); } },
      { id: 'sakura', x: 808, y: 150, r: 26, label: '树', use: async (S2) => { await S2.say(null, '樱花早就谢了，树上一片绿。'); } },
    );
    T().goal(S, { x: RD.vending[0], y: 156, label: '售货机', delay: 25, every: 15, done: () => !!F().ch6Vending, text: '去看看自动售货机底下（E）' });
  }
  async function beatShigechi(S) {
    const p = S.player, ok = S.actor(OKU());
    // 一只小东西扛着一枚 10 日元，从售货机底下钻出来
    const h0 = S.spawn('harvest', RD.vending[0] + 4, 162, { id: 'hv0', facing: -1, shadow: false });
    h0.play('carry');
    S.sfx('doll_scurry', 0.6);
    await S.walk(h0, RD.vending[0] - 40, 166, { speed: 30, anim: 'carry' });
    await S.say(OKU(), '虫……虫扛着钱在走？！', { expr: 'shock' });
    // 路边的重清，后面跟着一串扛硬币的丰收
    const sg = S.spawn('shigechi', 640, 160, { id: 'shigechi', facing: -1, name: '矢安宫重清' });
    const hs = [];
    for (let i = 0; i < 9; i++) {
      const h = S.spawn('harvest', 660 + i * 9, 154 + (i % 3) * 6, { id: 'hvr' + i, facing: -1, shadow: false });
      h.play('carry'); hs.push(h);
    }
    focus({ x: 560 });
    S.sfx('doll_scurry', 0.8);
    for (const [i, h] of hs.entries()) S.walk(h, 586 + (i % 5) * 8, 160 + (i % 3) * 5, { speed: 40, anim: 'carry' }).catch(G.cancelIgnore);
    S.walk(h0, 580, 166, { speed: 40, anim: 'carry' }).catch(G.cancelIgnore);
    await S.walk(sg, 600, 158, { speed: 34 });
    await S.say('shigechi', '你们两个，别抢我的钱哦。这条街的零钱都归我。', { actor: sg });
    S.nameCard('shigechi', { y: NAME_TOP });
    S.standCard('harvest', { y: NAME_TOP });
    S.cue('sting_reveal');
    S.mark('ch6_shigechi');
    await S.wait(1.0);
    await S.say('josuke', '那么多小东西……全是你的替身？', { expr: 'shock' });
    await S.say('shigechi', '丰收，一共五百只。镇上掉的零钱，它们都捡得到。', { actor: sg, expr: 'smile' });
    await S.say('shigechi', '捡了一年，存了五万多日元呢。', { actor: sg, expr: 'smile' });
    await S.say(OKU(), '五万？！仗助，我们跟他合伙吧！', { expr: 'shock' });
    await S.say('josuke', '我们帮你出主意，去哪儿捡、怎么捡。捡到的三个人分，怎么样？', { expr: 'smile' });
    await S.say('shigechi', '……嗯——好吧！就当交朋友了！', { actor: sg, expr: 'smile' });
    for (const h of hs) h.remove = true;
    h0.remove = true;
    await S.fadeOut(0.4);
    sg.remove = true;
  }

  // ================================================================ 节拍 5 中奖
  async function beatLottery(S) {
    S.party(['josuke', OKU()], { leader: 'josuke' });
    await S.setStage('road_ch6', { x: 640, y: 158, facing: 1, music: 'daily', fade: false });
    S.state('pm', 1);
    const p = S.player, ok = S.actor(OKU());
    const sg = S.spawn('shigechi', 672, 158, { id: 'shigechi', facing: -1, name: '重清' });
    const np = T().prop(S, 'newspaper', 672, 158, { id: 'paper', z: 14 });
    snapTo({ x: 660 });
    await S.fadeIn(0.5);
    await S.say('shigechi', '一万三千日元……再加上这张彩票。号码我对一下。', { actor: sg });
    await S.wait(0.6);
    S.sfx('sting_shock', 0.7);
    await S.say('shigechi', '……五、五、五百万日元？！', { actor: sg, expr: 'shock' });
    await S.say('josuke', '中、中奖了？！', { expr: 'shock' });
    S.mark('ch6_lottery');
    for (const a of [p, ok, sg]) if (a) S.arc(a, a.x, a.y, 14, 0.35).catch(G.cancelIgnore);
    S.sfx('ding', 0.8);
    await S.wait(0.5);
    await S.say(OKU(), '一人一百六十多万！我要买……买……我想不出来！', { expr: 'smile' });
    if (np) np.remove = true;
    await S.fadeOut(0.5);
    sg.remove = true;
  }

  // ================================================================ 节拍 6 银行：仗助把彩票背面的字“修”成别的
  const BK = { counter: [243, 146], teller: [243, 140] };
  async function beatBank(S) {
    S.party(['josuke', OKU()], { leader: 'josuke' });
    await S.setStage('bank_ch6', { x: 40, y: 160, facing: 1, music: 'daily', fade: false });
    const p = S.player;
    const tl = S.spawn('clerk', 243, 140, { id: 'teller', facing: 1, name: '柜员' });
    tl.facing = -1;
    const sg = place(S, 'shigechi', 14, 164, 1);
    sg.team = 'npc'; sg.name = '重清';
    T().prop(S, 'lottery', BK.counter[0] - 8, 144, { id: 'ticket', frame: 1, z: 30 });
    snapTo({ x: 160 });
    await S.fadeIn(0.5);
    S.location('bank', { y: NAME_TOP });
    S.mark('ch6_bank');
    await S.walk(p, 220, 152, { speed: 60 });
    await S.say('clerk', '中奖了呢，恭喜。不过五百万日元以上要登记本人……', { actor: tl, name: '柜员', expr: 'smile' });
    await S.say('clerk', '这张彩票背面，写着买的人的名字和电话。不是这位同学的名字呢。', { actor: tl, name: '柜员' });
    await S.say('shigechi', '那、那是我捡的嘛……', { expr: 'shock', actor: sg });
    await S.say('clerk', '那就要先联系这位买主了。请稍等。', { actor: tl, name: '柜员' });
    S.walk(tl, 296, 140, { speed: 30 }).catch(G.cancelIgnore);
    await S.say(OKU(), '……完了，五百万飞了。', { expr: 'shock' });
    await S.say('josuke', '……背面的字，是“写上去”的吧。', { expr: 'smile' });
  }
  async function useTicket(S) {
    if (F().ch6Fixed) { await S.say(null, '背面写着“矢安宫重清”和他家的电话。'); return; }
    await S.say(null, '彩票背面写着别人的名字和电话，是圆珠笔写的。');
    if (!F().ch6TicketHint) { F().ch6TicketHint = true; S.hint('仗助按 U：疯狂钻石把字迹“修”回去——修成别的样子', 6); }
  }
  async function fixTicket(S, h, p) {
    if (F().ch6Fixed) { await S.say('josuke', '……已经修好了。'); return; }
    F().ch6Fixed = true;
    S.mark('ch6_fix_ticket');
    await S.say('josuke', '墨水本来就是从笔里出来的。……把它“修”回笔画，再拼成另一个名字。', { expr: 'smile' });
    S.sfx('sparkle', 0.8);
    await S.wait(0.4);
    await S.say(null, '字迹一笔一笔地挪动，拼成了“矢安宫重清”。');
    await S.say(OKU(), '……仗助，你这是犯罪吧？', { expr: 'shock' });
    await S.say('josuke', '彩票是重清捡的，失主早就扔了。……大概。', { expr: 'smile' });
  }
  async function eraseTicket(S) {
    await S.say(OKU(), '我把背面的字削掉不就好了？', { expr: 'smile' });
    await S.say('josuke', '削掉就连纸带字一起没了！五百万也没了！', { expr: 'rage' });
  }
  function setupBankFree(S) {
    const st = G.world.stage;
    st.hotspots.push(
      { id: 'ticket', x: BK.counter[0], y: 150, r: 22, ry: 14, label: '彩票', tags: ['fix', 'erase'], fx: BK.counter[0] - 8, fy: 114,
        use: useTicket, look: async (S2, h, p) => { if (p.cid === 'josuke') await fixTicket(S2, h, p); else await eraseTicket(S2); } },
      { id: 'number', x: 71, y: 150, r: 12, label: '取号机', use: async (S2) => { S2.sfx('blip', 0.6); await S2.say(null, '取号机吐出一张小票：2-041。'); } },
      { id: 'sofa', x: 116, y: 150, r: 14, label: '沙发', use: async (S2) => { await S2.say(OKU(), '银行的沙发软乎乎的……五百万……'); } },
      { id: 'poster', x: 115, y: 150, r: 6, label: '海报', use: async (S2) => { await S2.say(null, '海报：「为了孩子的将来，现在开始储蓄」。'); } },
      { id: 'clock', x: 296, y: 150, r: 10, label: '挂钟', use: async (S2) => { await S2.say(null, '两点五十。三点关门。'); } },
    );
    T().goal(S, { x: BK.counter[0], y: 152, label: '彩票', delay: 30, every: 15, done: () => !!F().ch6Fixed, text: '柜台上的彩票：仗助走过去按 U' });
    S.hint('Q 换队长；仗助对着柜台上的彩票按 U', 6);
  }
  async function beatCheck(S) {
    const p = S.player, tl = S.actor('teller'), sg = S.actor('shigechi');
    if (tl) await S.walk(tl, 243, 140, { speed: 40 });
    await S.say('clerk', '……咦？名字是“矢安宫重清”呢。是我看错了。', { actor: tl, name: '柜员', expr: 'shock' });
    await S.say('clerk', '好的，矢安宫先生。这是五百万日元的汇票。', { actor: tl, name: '柜员', expr: 'smile' });
    T().prop(S, 'check', 236, 150, { id: 'check', frame: 0, z: 30 });
    S.sfx('ding', 0.8);
    S.mark('ch6_check');
    const ck = S.actor('check');
    if (sg) {
      await S.walk(sg, 226, 160, { speed: 60 });
      if (ck) ck.remove = true;
      await S.say('shigechi', '汇、汇票！五百万！', { actor: sg, expr: 'smile' });
    }
    await S.fadeOut(0.4);
  }

  // ================================================================ 节拍 7 银行门口：吵翻 → 第 9 战
  async function beatQuarrel(S) {
    await S.setStage('bank_ch6', { x: 70, y: 160, facing: -1, music: 'tension', fade: false });
    const p = S.player, ok = S.actor(OKU());
    const sg = place(S, 'shigechi', 34, 160, 1);
    sg.team = 'npc'; sg.name = '重清';
    if (ok) Object.assign(ok, { x: 96, y: 166, facing: -1, follow: null });
    S.face(p, sg);
    snapTo({ x: 80 });
    await S.fadeIn(0.4);
    await S.say('shigechi', '这张汇票我先收着了。你们两个……一人两万日元，够了吧？', { actor: sg, expr: 'smile' });
    await S.say('josuke', '……哈？说好的三个人分呢？', { expr: 'rage' });
    await S.say('shigechi', '彩票是我捡的！丰收也是我的！你们什么都没干！', { actor: sg, expr: 'rage' });
    await S.say(OKU(), '你这家伙——拿来！', { expr: 'rage' });
    // 亿泰一拳把汇票抢回来；丰收从他耳朵边偷走，一路扛上外墙
    S.sfx('whoosh', 0.8);
    await S.walk(ok, sg.x + 18, sg.y, { speed: 120 });
    S.sfx('punch_heavy', 0.8); S.shake(2, 0.2);
    S.sfxText('啪', sg, { dur: 0.6 });
    S.mark('ch6_quarrel');
    await S.say(OKU(), '抢回来了！……诶？', { expr: 'smile' });
    const hs = [];
    for (let i = 0; i < 6; i++) { const h = S.spawn('harvest', ok.x + 6, ok.y - 1, { id: 'hvq' + i, shadow: false }); h.z = 30; h.play('carry'); hs.push(h); }
    S.sfx('doll_scurry', 0.9);
    for (const [i, h] of hs.entries()) S.arc(h, -20 - i * 10, 150, 30, 0.7).catch(G.cancelIgnore);
    await S.wait(0.7);
    for (const h of hs) h.remove = true;
    await S.say(OKU(), '耳朵边一痒……汇票没了！', { expr: 'shock' });
    S.walk(sg, -30, 158, { speed: 90 }).catch(G.cancelIgnore);
    await S.say('shigechi', '嘿嘿，追得上就来呀！', { expr: 'smile', actor: sg });
    await S.say('josuke', '……重清。你这样，可就不是朋友了。', { expr: 'rage' });
    sg.remove = true;
    await S.vs({ key: 'harvest', hero: 'josuke', enemy: { cid: 'shigechi', anim: 'idle' } });
    G.uifx.vsTag('harvest');
  }

  // ================================================================ 节拍 8 和好
  async function beatMakeup(S) {
    const p = S.player, ok = S.actor(OKU());
    const sg = S.actor('shigechi_roof') || S.spawn('shigechi', p.x + 30, 156, { id: 'shigechi_roof', facing: -1, name: '重清' });
    const ck = T().prop(S, 'check', p.x + 8, p.y + 0.5, { id: 'check2', frame: 0, z: 22 });
    await S.say('josuke', '……重清。看好了。', { expr: 'rage' });
    S.sfx('glass_break', 0.4); S.sfx('card_flip', 0.9);
    T().setFrame(ck, 1);
    S.sfxText('嘶啦', ck, { dur: 0.8 });
    S.mark('b09_tear');
    await S.say('shigechi', '啊啊啊！五百万！你、你撕了它？！', { actor: sg, expr: 'shock' });
    // 丰收一只只散去
    for (const a of G.world.stage.actors) if (a.cid === 'harvest' && !a.remove) S.animate(0.6, (k) => { a.alpha = 1 - k; }).then(() => { a.remove = true; }, G.cancelIgnore);
    await S.wait(0.6);
    await S.say('josuke', '钱是三个人一起赢的。少了谁，这张纸都到不了银行。', { expr: 'rage' });
    await S.say('josuke', '一人三分之一。你答应，我就把它修好。', { expr: 'normal' });
    await S.say('shigechi', '……呜……我……对不起……', { actor: sg, expr: 'shock' });
    await S.summon(p, { dur: 0.12, rise: 4 });
    S.standAct(p, 'reach', { dx: 16, z: 4, dur: 0.7 });
    P4().fixGlow(S, ck.x, ck.y - 22);
    T().setFrame(ck, 0);
    await S.wait(0.6);
    S.recall(p);
    S.mark('ch6_makeup');
    await S.say(OKU(), '……我脑子不好使，可刚才那一下，挺帅的。', { expr: 'smile' });
    ck.remove = true;
    await S.fadeOut(0.5);
    // 三天后分钱：重清又想多要一份（喜剧）
    await S.setStage('bank_ch6', { x: 110, y: 160, facing: 1, music: 'daily', fade: false });
    const sg2 = place(S, 'shigechi', 150, 160, -1);
    sg2.team = 'npc'; sg2.name = '重清';
    if (ok) Object.assign(ok, { x: 176, y: 164, facing: -1, follow: null });
    snapTo({ x: 150 });
    await S.fadeIn(0.4);
    await S.title('three_days', { y: 110 });
    await S.say('shigechi', '一人一百六十六万……那、那个零头，能不能归我？', { actor: sg2, expr: 'smile' });
    await S.say(OKU(), '按住他！', { expr: 'rage' });
    S.sfx('sting_comedy', 0.8);
    S.shake(2, 0.3);
    await S.say('shigechi', '开玩笑的！开玩笑的啦！', { actor: sg2, expr: 'shock' });
    await S.fadeOut(0.5);
  }

  // ================================================================ 节拍 9 某个中午：拿错纸袋
  const BENCH = [336, 150];
  async function beatBags(S) {
    S.party(['josuke'], { leader: 'josuke' });
    await S.setStage('deli_ch6', { x: 20, y: 160, facing: 1, music: 'daily', fade: false });
    S.player.visible = false;
    const sg = S.spawn('shigechi', BENCH[0] - 14, 150, { id: 'shigechi', facing: 1, name: '重清' });
    const b1 = T().prop(S, 'paperbag', BENCH[0] - 2, 150, { id: 'bag_s', z: 8 });
    snapTo({ x: 320 });
    await S.fadeIn(0.5);
    await S.title('one_noon', { y: 110 });
    await S.say('shigechi', '三明治买好了！给仗助和亿泰也带了一份。', { actor: sg, expr: 'smile' });
    // 西装男人坐到长椅另一头，放下一只一模一样的纸袋
    const kr = S.spawn('kira', 500, 154, { id: 'kira', facing: -1, name: '西装男人' });
    await S.walk(kr, BENCH[0] + 22, 150, { speed: 36 });
    const b2 = T().prop(S, 'paperbag', BENCH[0] + 8, 150, { id: 'bag_k', z: 8 });
    S.face(kr, -1);
    S.sfx('menacing', 0.4);
    await S.wait(0.6);
    S.mark('ch6_bags');
    await S.say('shigechi', '啊，要迟到了！', { actor: sg, expr: 'shock' });
    // 重清顺手拿起的，是右边那只（男人的）
    b2.remove = true;
    S.walk(sg, -30, 160, { speed: 60 }).then(() => { sg.remove = true; }, G.cancelIgnore);
    await S.wait(1.0);
    S.face(kr, -1);
    await S.say('kira', '……', { actor: kr, name: '西装男人' });
    await S.say(null, '男人拿起剩下的那只纸袋，往里看了一眼。');
    await S.say('kira', '……三明治？', { actor: kr, name: '西装男人', expr: 'shock' });
    S.sfx('heartbeat', 0.6);
    await S.say('kira', '刚才那个小鬼……穿的是葡萄丘中学的校服。', { actor: kr, name: '西装男人', expr: 'rage' });
    if (b1) b1.remove = true;
    await S.fadeOut(0.6);
    kr.remove = true;
  }

  // ================================================================ 节拍 10 体育仓库
  const JH = { sit: [322, 150], hanger: [374, 82], shedDoor: 232, window: 528 };
  async function beatShed(S) {
    S.party(['josuke', OKU()], { leader: 'josuke' });
    await S.setStage('jhs_ch6', { x: 300, y: 158, facing: 1, music: 'daily', fade: false });
    S.state('pm', 0.6);
    const p = S.player, ok = S.actor(OKU());
    if (ok) Object.assign(ok, { x: 280, y: 164, facing: 1, follow: null });
    const sg = S.spawn('shigechi', 340, 156, { id: 'shigechi', facing: -1, name: '重清' });
    const bag = T().prop(S, 'paperbag', 352, 156, { id: 'bag', z: 0 });
    snapTo({ x: 320 });
    await S.fadeIn(0.5);
    S.location('jhs', { y: NAME_TOP });
    S.mark('ch6_shed');
    await S.say('shigechi', '这是我的秘密基地！来，三明治，一人一个！', { actor: sg, expr: 'smile' });
    await S.say('josuke', '谢了，重清。不过我和亿泰下午还有课，得回去了。', { expr: 'smile' });
    await S.say(OKU(), '留着你自己吃吧。下次请我们吃烤肉！', { expr: 'smile' });
    S.walk(ok, -40, 164, { speed: 60 }).catch(G.cancelIgnore);
    await S.walk(p, -40, 160, { speed: 60 });
    p.visible = false;
    await S.say('shigechi', '嘿嘿，那我就不客气啦。', { actor: sg, expr: 'smile' });
    S.face(sg, 1);
    await S.say(null, '重清打开纸袋——');
    S.sfx('sting_shock', 0.8);
    S.flash(0.1, 0.3);
    await S.say('shigechi', '……这、这是什么？！', { actor: sg, expr: 'shock' });
    await S.say('shigechi', '不是我的三明治……得、得去告诉仗助！', { actor: sg, expr: 'shock' });
    await S.walk(sg, 200, 156, { speed: 70 });
    sg.visible = false;
    if (bag) bag.remove = true;
    T().prop(S, 'paperbag', 330, 150, { id: 'bag2', z: 0 });
    // 吉良视角：男人溜进仓库，用墙上的铁丝衣架把纸袋钩走
    S.filter('vignette', 0.55, { colour: '#3a1a4a', inner: 0.5 });
    await S.title('kira_pov', { y: 60 });
    const kr = S.spawn('kira', 620, 156, { id: 'kira', facing: -1, name: '西装男人' });
    focus({ x: 380 });
    await S.walk(kr, JH.hanger[0] + 4, 150, { speed: 50 });
    S.face(kr, -1);
    S.sfx('metal_scrape', 0.6);
    const b2 = S.actor('bag2');
    if (b2) { await S.arc(b2, kr.x - 4, kr.y + 0.5, 20, 0.5); b2.z = 20; }
    S.mark('ch6_hanger');
    await S.say('kira', '……找到了。', { actor: kr, name: '西装男人', expr: 'smile' });
    S.filter('vignette', null);
    // 一只丰收在门口看见了
    const hv = S.spawn('harvest', 240, 164, { id: 'hv_watch', facing: 1, shadow: false });
    S.sfx('doll_scurry', 0.6);
    S.emote(hv, '！', 1.0);
    await S.wait(0.8);
    if (b2) b2.remove = true;
    await S.fadeOut(0.5);
    hv.remove = true; kr.remove = true;
    focus(null);
  }

  // ================================================================ 节拍 11 纽扣交到仗助手心
  async function beatButton(S) {
    S.party(['josuke', OKU()], { leader: 'josuke' });
    await S.setStage('jhs_ch6', { x: 70, y: 158, facing: 1, music: null, fade: false });
    S.state('pm', 1);
    const p = S.player, ok = S.actor(OKU());
    if (ok) Object.assign(ok, { x: 46, y: 164, facing: 1, follow: null });
    const hv = S.spawn('harvest', 130, 162, { id: 'hv_last', facing: -1, shadow: false });
    hv.play('carry');
    const bt = T().prop(S, 'button', 130, 162, { id: 'btn', z: 16 });
    snapTo({ x: 100 });
    await S.fadeIn(0.6);
    await S.walk(hv, p.x + 10, p.y + 1, { speed: 26, anim: 'carry' });
    S.face(p, 1);
    await S.say('josuke', '……丰收？就你一只？', { expr: 'shock' });
    S.sfx('pop', 0.6);
    await S.arc(bt, p.x + 6, p.y + 0.5, 10, 0.4);
    bt.z = 24;
    await S.animate(1.0, (k) => { hv.alpha = 1 - k; });
    hv.remove = true;
    S.music('sad', 1.4);
    S.mark('ch6_button');
    await S.say('josuke', '一颗……纽扣？', { expr: 'shock' });
    await S.say(OKU(), '重清的丰收……怎么不见了？', { expr: 'shock' });
    await S.say('josuke', '……重清？', { expr: 'shock' });
    await S.narrate('那天下午，重清没有回家。', { pos: 'top' });
    bt.remove = true;
    await S.fadeOut(0.8);
  }

  // ================================================================ 节拍 12 幽灵小路：承太郎、乔瑟夫、线索板
  async function beatAlleyAgain(S) {
    S.party(['josuke', OKU(), 'koichi', ROHAN], { leader: 'josuke' });
    await S.setStage('alley_ch6', { x: 230, y: 156, facing: 1, music: 'sad', fade: false });
    S.state('dark', 0.35);
    const p = S.player;
    const ms = { [OKU()]: [206, 164], koichi: [184, 160], [ROHAN]: [254, 150] };
    for (const [cid, xy] of Object.entries(ms)) { const a = S.actor(cid); if (a) Object.assign(a, { x: xy[0], y: xy[1], facing: 1, follow: null }); }
    const rm = ghost(S.spawn('reimi', 300, 152, { id: 'reimi', facing: -1, name: '铃美' }));
    const ar = ghost(S.spawn('arnold', 320, 158, { id: 'arnold', facing: -1, name: '阿诺德' }));
    snapTo({ x: 260 });
    await S.fadeIn(0.8);
    await T().say(S, 'reimi', '……那个男孩，已经不在了。');
    await T().say(S, 'reimi', '他最后看见的，就是那个人。和十五年前一样的人。');
    S.mark('ch6_reimi_again');
    await S.say(OKU(), '……可恶！', { expr: 'rage' });
    // 承太郎、乔瑟夫赶到
    const jt = S.spawn('jotaro4', -20, 156, { id: 'jotaro4', facing: 1, name: '空条承太郎' });
    const js = S.spawn(JOS(), -44, 162, { id: 'joseph', facing: 1, name: '乔瑟夫' });
    S.walk(js, 120, 162, { speed: 26 }).catch(G.cancelIgnore);
    await S.walk(jt, 150, 156, { speed: 44 });
    await S.say('jotaro4', '……听说了。重清的事。', { actor: jt });
    await S.say(JOS(), '哈？什么？这巷子里还有个女孩子？', { actor: js, name: '乔瑟夫', expr: 'shock' });
    await S.say('koichi', '乔、乔斯达先生，您看得见？', { expr: 'shock' });
    await S.say(JOS(), '看不见。……可我知道她在。年纪大了，就是会知道。', { actor: js, name: '乔瑟夫' });
    await S.say('josuke', '重清的丰收，最后把这个交给了我。', { expr: 'normal' });
    await F6().clueCard(S, '纽扣');
    S.mark('ch6_clue_button');
    await S.say('jotaro4', '西装外套上的纽扣。凶手的衣服，现在少了一颗。', { actor: jt });
    await S.say(ROHAN, '一个穿西装的男人。镇上有几千个。', { expr: 'rage' });
    await S.say('josuke', '那就一个一个看。……外公守的镇子，我不会让他躲下去。', { expr: 'rage' });
    await S.say(OKU(), '我脑子不好使……可我知道该揍谁。', { expr: 'rage' });
    await T().say(S, 'reimi', '……拜托你们了。', { expr: 'smile' });
    await S.fadeOut(0.8);
    for (const a of [rm, ar, jt, js]) if (a) a.remove = true;
  }

  // ================================================================ 节拍 13 擦肩而过 → To Be Continued
  async function beatPassBy(S) {
    S.party(['josuke', 'koichi'], { leader: 'josuke' });
    await S.setStage('road_ch6', { x: 300, y: 158, facing: 1, music: null, fade: false });
    S.state('pm', 1);
    const p = S.player, ko = S.actor('koichi');
    if (ko) Object.assign(ko, { x: 274, y: 164, facing: 1, follow: null });
    const kr = S.spawn('kira', 700, 154, { id: 'kira', facing: -1, name: '西装男人' });
    snapTo({ x: 420 });
    await S.fadeIn(0.8);
    S.walk(ko, 520, 164, { speed: 36 }).catch(G.cancelIgnore);
    S.walk(p, 546, 158, { speed: 36 }).catch(G.cancelIgnore);
    await S.say('koichi', '仗助君，你说那个人……现在会在做什么？');
    await S.say('josuke', '大概在吃饭、上班、睡觉吧。和我们一样。');
    await S.walk(kr, 420, 152, { speed: 34 });
    S.mark('ch6_passby');
    focus({ x: 420 });
    S.walk(p, 640, 158, { speed: 36 }).catch(G.cancelIgnore);
    S.walk(ko, 614, 164, { speed: 36 }).catch(G.cancelIgnore);
    await S.walk(kr, 300, 152, { speed: 34 });
    // 男人停了一下
    S.sfx('heartbeat', 0.6);
    await S.wait(0.9);
    S.menacing({ x: 300, y: 120 });
    await S.say('kira', '……东方仗助。', { actor: kr, name: '西装男人' });
    S.nameCard('kira', { y: NAME_TOP });
    await S.wait(1.4);
    await S.walk(kr, 200, 152, { speed: 34 });
    await S.tbc({ hold: 2.0 });
    S.mark('ch6_tbc');
  }

  // ================================================================ 第6章主流程
  G.STORY.ch6 = async function (S) {
    if (T().resetCounters) T().resetCounters();
    P4().clearOverlays();
    for (const k of Object.keys(F())) if (/^ch6/.test(k)) delete F()[k];
    await S.chapterCard('ch6');
    S.party(['josuke'], { leader: 'josuke' });
    await S.run(async (S2) => { await beatCalendar(S2); await beatAlley(S2); }, { keepLocked: true });
    // 自由走动：铃美（40 s 后剧情自己往下走）
    setupAlleyFree(S);
    await S.run(async () => {});
    T().goal(S, { x: AL.reimi[0], y: 156, label: '铃美', delay: 20, every: 15, done: () => !!F().ch6TalkReimi, text: '去和铃美说话（E）' });
    const t2 = now();
    await S.until(() => (F().ch6TalkReimi || now() - t2 > 40) && !S.busy);
    if (!F().ch6TalkReimi) S.mark('ch6_reimi');
    if (!F().ch6ReadGhost) S.mark('ch6_read_ghost');
    G.world.stage.hotspots.length = 0;
    await S.run(beatPromise, { keepLocked: true });
    // 探索「不能回头」
    await F6().exAlley(S);
    await S.run(async (S2) => {
      await afterAlley(S2);
      await beatKiraPov(S2);
      await beatDaysLater(S2);
    }, { keepLocked: true });
    // 自由走动：售货机（40 s 后自己往下走）
    setupRoadFree(S);
    await S.run(async () => {});
    const t4 = now();
    await S.until(() => (F().ch6Vending || now() - t4 > 40) && !S.busy);
    if (!F().ch6Vending) S.mark('ch6_vending');
    G.world.stage.hotspots.length = 0;
    await S.run(async (S2) => {
      await beatShigechi(S2);
      await F6().coins(S2);
      await beatLottery(S2);
      await beatBank(S2);
    }, { keepLocked: true });
    // 自由走动：银行里修彩票（75 s 后柜员自己“看错”）
    setupBankFree(S);
    await S.run(async () => {});
    const t6 = now();
    await S.until(() => (F().ch6Fixed || now() - t6 > 75) && !S.busy);
    if (!F().ch6Fixed) { S.mark('ch6_fix_ticket'); F().ch6Fixed = true; }
    G.world.stage.hotspots.length = 0;
    await S.run(async (S2) => {
      await beatCheck(S2);
      await beatQuarrel(S2);
      await F6().harvestWall(S2);
      await F6().harvestRoof(S2);
      await beatMakeup(S2);
      await beatBags(S2);
      await beatShed(S2);
      await F6().killerQueen(S2);
      await beatButton(S2);
      await beatAlleyAgain(S2);
      await beatPassBy(S2);
    }, { keepLocked: true });
  };
  G.STORY.ch6.marks = ['ch6_calendar', 'ch6_alley', 'ch6_reimi', 'ch6_read_ghost', 'ch6_promise', 'ex_alley_start', 'ch6_dragged', 'ch6_alley_out',
    'ch6_kira_pov', 'ch6_days_later', 'ch6_vending', 'ch6_shigechi', 'mg_coins_start', 'ch6_lottery', 'ch6_bank', 'ch6_fix_ticket', 'ch6_check',
    'ch6_quarrel', 'b09a_start', 'b09b_start', 'b09_pipe_fixed', 'b09_drunk', 'b09_apology', 'b09_tear', 'ch6_makeup', 'ch6_bags', 'ch6_shed',
    'ch6_hanger', 'b10_start', 'b10_coin_bomb', 'b10_crawl', 'b10_window', 'b10c_start', 'ch6_button', 'ch6_reimi_again', 'ch6_clue_button',
    'ch6_passby', 'ch6_tbc'];
  G.STORY.ch6.packs = ['bg_prologue'];
})();
