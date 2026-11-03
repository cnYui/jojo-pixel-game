// 终章　杜王町 / 钻石是不会碎的（G.STORY.final，地图 id 后缀 _fin；开发脚本 第四部/docs/终章_开发脚本.md）。整章流程：
//   节拍 1 篇章卡 → 日历地图（图钉「住宅区」+ 红章 7月16日）→ 2 8:29 的街口（早人、吉良说出名字、露伴还活着）→ 段 A
//   → 3 亿泰倒下、早人身上的炸弹、修好两个人 → 4 空房子：段 B（烟灰）、段 C（碎片与电话）→ 5 走出空房子：段 D（亿泰归来、梦）
//   → 6 救护车旁：段 E（3 FREEZE、白金之星·世界）→ 7 冷色的小路（吉良的最后）→ 8 天亮的小路（铃美和阿诺德）
//   → 9 傍晚（等人回家的人）→ 10 1999 年夏末（红章 + 五张小卡）→ 11 杜王港（钱包）→「完」→ 职员表。
//   克制：亿泰被打中、早人身上的炸弹只有白光和剪影；吉良之死 = 救护车倒车 → 黑屏 + 刹车声；被拖进小路只画手的影子。
//   第 19 战五段的战斗部分在 story/p4_final_fights.js（G.P4FIN）。人物用 R.cast()：正式版进了 G.D.chars 就用正式版，没有就用 fin_ 暂代版。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const R = () => G.P4FIN;
  const F = () => G.flags;
  const now = () => (G.clk ? G.clk.world : 0);
  const uiNow = () => (G.clk ? G.clk.ui : 0);
  const NAME_TOP = 100;
  const C = (k) => R().cast(k);
  const HAYATO_MSG = '早人：「我、我不行……我只是个小学生。」';

  // 对话框名字（各章共用的 G.NAMES 只往上加，不改别章的）
  Object.assign(G.NAMES, {
    fin_kira: '吉良', kira: '吉良', fin_kq: '杀手皇后', killerqueen: '杀手皇后', fin_okuyasu: '亿泰', okuyasu: '亿泰',
    fin_hayato: '早人', hayato: '早人', fin_rohan: '露伴', rohan: '露伴', fin_reimi: '铃美', reimi: '铃美', fin_keicho: '形兆', keicho: '形兆',
    fin_shinobu: '忍', shinobu: '忍', paramedic: '急救员', fin_arnold: '阿诺德', arnold: '阿诺德', fin_joseph: '乔瑟夫', joseph4: '乔瑟夫',
    yoshihiro: '吉广', neighbor: '邻居',
  });

  // ================================================================ 地图
  const { base, walls } = G.p4Stage;
  const ST = G.STAGES;
  ST.map_fin = base('map_fin', 'morioh_map', 320, { yMin: 160, yMax: 170, music: null, obstacles: [] });
  ST.corner_fin = base('corner_fin', 'morning_corner_rain', 640, { music: 'tension', state: { clock: 509 } });
  ST.emptyhouse_fin = base('emptyhouse_fin', 'empty_house', 480, { music: 'battle', state: { ash: 0, vase: 0, glass: 0, ring: 0 }, obstacles: walls(10, 470, 480) });
  ST.street_fin = base('street_fin', 'residential_street', 960, { music: 'battle', state: { ambulance: 0, siren: 0, pm: 0 } });
  ST.dream_fin = base('dream_fin', 'afterlife_dream', 320, { music: null, state: { fade: 0 } });
  ST.alley_fin = base('alley_fin', 'ghost_alley_cold', 640, { music: 'sad' });
  ST.harbor_fin = base('harbor_fin', 'morioh_harbor_late', 960, { music: 'title', state: { ship: 1 } });
  // 换背景用到的变体（ghost_alley_dawn）也在本章的包里：main.js 只看地图 id 的背景，这里补上
  const PACKS = ['bg_final'];

  // 日历地图：本章一枚图钉（住宅区），红章换成本章的「1999年7月16日」；尾声再盖一次「1999年夏末」
  P4().CAL.final = { pins: [{ at: 'fin_home', label: '杜王町·住宅区' }] };
  P4().CAL.final_late = { pins: [] };
  async function calendar(S, key, stamp) {
    const bgm = G.D.bg.morioh_map;
    if (bgm && bgm.anchors && !bgm.anchors.fin_home) bgm.anchors.fin_home = [140, 104];
    const m = G.D.ui.map || {}, old = m.stamp;
    if (m[stamp]) m.stamp = m[stamp];
    try {
      const h = await P4().calendar(S, key, { hold: 1.8 });
      return { close() { if (h) h.close(); m.stamp = old; } };
    } catch (e) { m.stamp = old; throw e; }
  }

  // ================================================================ 小工具
  const pool = (cid) => G.party._actor(cid);
  function place(S, cid, x, y, facing, o = {}) {
    const a = pool(cid), W = G.world;
    Object.assign(a, { x, y, z: 0, facing: facing || 1, follow: null, hold: false, script: null, state: 'idle', remove: false, rot: 0, alpha: 1, frozen: null });
    a.visible = o.visible !== false;
    if (W.player !== a) a.team = 'npc';
    a.play(a.idleAnim || 'idle');
    if (W.stage.actors.indexOf(a) < 0) W.stage.add(a);
    return a;
  }
  const focus = (o) => { G.world.focus = o; };
  const snapTo = (o) => { G.world.focus = o; G.world.snapCamera(); };
  function spawnKira(S, x, y, facing) {
    const k = S.spawn(C('kira'), x, y, { id: 'kira', name: '吉良吉影', facing: facing || 1, stand: C('kq') });
    if (!k.stand && k.setStand) k.setStand(C('kq'));
    return k;
  }
  // 白光 + 剪影（亿泰被打中、早人身上的炸弹：只演光，不演伤）
  async function whiteBurst(S, a, o = {}) {
    S.sfx('explosion', o.vol || 0.9);
    S.flash(o.dur || 0.6, 1, '#ffffff');
    S.shake(4, 0.4);
    if (a) { a.flash = 1; S.fx('glint', { x: a.x, y: a.y - 24, size: 16 }, { life: 0.5 }); }
    await S.wait(0.5);
  }
  // 黑底小卡（一句话）：T().show 画黑底，旁白放中间
  async function blackCard(S, text, o = {}) {
    const h = T().show(S, { bg: '#08060c', parts: o.parts || [] });
    await S.narrate(text, { pos: o.pos || 'top' });
    if (o.hold) await S.wait(o.hold);
    h.close();
  }

  // ================================================================ 节拍 1 篇章卡 → 日历地图
  async function beatCalendar(S) {
    S.player.visible = false;
    await S.setStage('map_fin', { x: 160, y: 165, music: null });
    const cal = await calendar(S, 'final', 'stamp_0716');
    S.mark('fin_calendar');
    await S.fadeOut(0.45);
    cal.close();
  }

  // ================================================================ 节拍 2 8:29 的街口（下雨）
  const CORNER = { hayato: [330, 160], kira: [250, 158], josukeIn: [636, 158] };
  async function beatCorner(S) {
    const p = S.player, hc = C('hayato'), oc = C('okuyasu');
    await S.setStage('corner_fin', { x: CORNER.josukeIn[0], y: CORNER.josukeIn[1], facing: -1, music: null, fade: false });
    S.ambient('rain_loop', 0.35);
    p.visible = false;
    const hy = place(S, hc, CORNER.hayato[0], CORNER.hayato[1], -1);
    const kira = spawnKira(S, CORNER.kira[0], CORNER.kira[1], 1);
    snapTo({ x: 300 });
    await S.fadeIn(0.6);
    S.mark('fin_corner');
    await S.narrate('7 月 16 日，早上 8 点 29 分。下着雨的街口。', { pos: 'top' });
    S.emote(hy, '……', 1.2);
    await S.say(C('kira'), '早人，回家吧。你一个小孩子，能做什么呢。', { expr: 'smile', actor: kira });
    S.music('tension', 0.6);
    // 仗助从右边跑进来
    p.visible = true; p.x = 640; p.y = 158; p.facing = -1;
    await S.walk(p, 392, 158, { speed: 96 });
    await S.say('josuke', '……喂，大叔。');
    await S.say('josuke', '这孩子刚才喊住我，说你是杀人魔。……你刚才说，你叫什么？');
    S.mark('fin_name');
    S.sfx('heartbeat_loop', 0.5);
    await S.say(C('kira'), '（……听到了？就因为我自己说出了名字？）', { expr: 'shock', actor: kira });
    const oku = place(S, oc, 640, 160, -1);
    await S.walk(oku, 420, 162, { speed: 100 });
    await S.say(oc, '仗助！我也听见了。“吉良吉影”。', { expr: 'rage' });
    await S.say(C('kira'), '败者食尘……只要早人身上还挂着它，我就会被拉进去。……收回来。', { expr: 'normal', actor: kira });
    S.sfx('glint', 0.6);
    S.fx('sparkles', { x: hy.x, y: hy.y - 20, n: 6, radius: 10, colour: '#ffb0d8', period: 0.5, size: 2 }, { life: 0.8 });
    await S.wait(0.6);
    // 小卡：露伴家门口
    const rh = T().show(S, { bg: '#3a4a5a', parts: [{ kind: 'sprite', cid: C('rohan'), anim: 'idle', x: 160, y: 150, scale: 2 }] });
    await S.say(C('rohan'), '……今天早上，总觉得哪里不对劲。');
    await S.narrate('那天早上，露伴老师好好地活着。', { pos: 'top' });
    rh.close();
    S.mark('fin_rohan_alive');
    // 早人躲到仗助身后
    S.walk(hy, 470, 158, { speed: 80 }).catch(G.cancelIgnore);
    S.face(kira, 1);
    S.nameCard(R().card('namecards', 'kira'), { y: NAME_TOP });
    S.standCard(R().card('standcards', 'kq'), { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.wait(1.0);
    S.music('battle', 0.3);
    await S.vs({ key: 'kq_final', hero: 'josuke', enemy: { cid: C('kira'), anim: 'point' } });
    G.uifx.vsTag('kq_final');
    // 段 A：仗助 + 亿泰（AI），早人跟着（灰）
    S.party(['josuke', oc, hc], { leader: 'josuke' });
    S.leadable(oc, false, { msg: '亿泰在帮你牵制他！' });
    S.leadable(hc, false, { msg: HAYATO_MSG });
    Object.assign(hy, { x: 520, y: 150 });
    focus(null);
    S.mark('b19a_start');
  }

  // ================================================================ 节拍 3 段 A 之后：亿泰倒下、早人身上的炸弹
  async function beatAfterA(S) {
    const p = S.player, oc = C('okuyasu'), hc = C('hayato');
    const kira = S.actor('kira'), oku = S.actor(oc), hy = S.actor(hc);
    S.hint(null);
    S.stopMusic(0.6);
    if (kira) { kira.team = 'npc'; kira.hold = true; kira.state = 'idle'; kira.play('idle'); }
    // 亿泰冲上去，看不见的泡泡贴到他胸口 → 白光
    if (oku) {
      oku.follow = null;
      await S.walk(oku, (kira ? kira.x : 300) + 44, kira ? kira.y : 158, { speed: 110 });
      await S.say(oc, '你这家伙——', { expr: 'rage' });
      await whiteBurst(S, oku);
      S.pose(oku, 'down');
      S.sfx('thud', 0.8);
    }
    S.mark('b19a_okuyasu_down');
    await S.say('josuke', '亿泰！！', { expr: 'rage' });
    // 吉良躲进雨里
    if (kira) { S.walk(kira, -30, 150, { speed: 70 }).then(() => { kira.remove = true; }, G.cancelIgnore); }
    S.leave(oc, { drop: true, stay: true });
    if (oku) { oku.remove = false; oku.visible = true; }
    S.leadable(hc, false, { msg: HAYATO_MSG });
    if (hy) { hy.follow = null; }
  }
  async function beatHayatoBomb(S) {
    const p = S.player, oc = C('okuyasu'), hc = C('hayato');
    const oku = S.actor(oc), hy = S.actor(hc);
    S.hint(null);
    focus({ x: oku.x + 20 });
    S.walk(hy, oku.x + 40, oku.y, { speed: 70 }).catch(G.cancelIgnore);
    await S.say('josuke', '……等等，他身上有东西。', { expr: 'shock' });
    await S.say(hc, '别碰他！他身上……被装了炸弹。', { expr: 'shock' });
    await S.say(hc, '那家伙一次只能留一个炸弹。……我碰了它，它就会在我身上响。');
    await S.say('josuke', '你说什么——', { expr: 'shock' });
    await S.walk(hy, oku.x + 10, oku.y, { speed: 90 });
    S.mark('fin_hayato_bomb');
    await whiteBurst(S, hy, { vol: 1 });
    S.pose(hy, 'down');
    // 仗助冲过去，疯狂钻石一抹，两个人一起修好
    await S.walk(p, oku.x + 30, oku.y, { speed: 120 });
    S.face(p, -1);
    await S.summon(p, { dur: 0.1, rise: 4 });
    S.standAct(p, 'reach', { dx: 18, z: 2, dur: 1.0 });
    P4().fixGlow(S, hy.x, hy.y - 10, { n: 9, r: 14 });
    G.defer(0.3, () => P4().fixGlow(S, oku.x, oku.y - 8, { n: 7 }));
    await S.wait(0.9);
    S.recall(p);
    S.unpose(hy);
    S.mark('fin_heal');
    await S.say(hc, '……我还活着？', { expr: 'shock' });
    await S.say('josuke', '我在旁边，谁都别想死。');
    await S.say('josuke', '……亿泰？喂，亿泰！', { expr: 'shock' });
    await S.wait(0.6);
    await S.say('josuke', '早人，跟紧我。先找个地方躲一下。');
    S.ambient(null);
    await S.fadeOut(0.6);
  }

  // ================================================================ 节拍 4 空房子 → 段 B、段 C
  async function beatHouse(S) {
    const p = S.player, oc = C('okuyasu'), hc = C('hayato');
    await S.setStage('emptyhouse_fin', { x: 40, y: 152, facing: 1, music: null, fade: false });
    const oku = place(S, oc, 237, 148, 1);
    S.pose(oku, 'down');
    const hy = S.actor(hc) || place(S, hc, 30, 158, 1);
    Object.assign(hy, { x: 26, y: 158, follow: null });
    Object.assign(p, { x: 210, y: 154, facing: 1 });
    snapTo({ x: 200 });
    await S.fadeIn(0.5);
    S.mark('fin_house');
    S.sfx('thud', 0.5);
    S.sfxText('砰', { wx: 26, wy: 150, wz: 30 }, { dur: 0.6 });
    await S.walk(hy, 170, 158, { speed: 60 });
    S.face(p, -1);
    await S.say(hc, '他在外面……看不见的炸弹会追过来吗？', { expr: 'shock' });
    await S.say('josuke', '会。泡泡是看不见的……可它总得在什么东西上留下痕迹。');
    S.face(p, -1);
    await S.walk(p, 150, 152, { speed: 60 });
    focus(null);
  }
  async function afterB(S) {
    await S.say('josuke', '（他在外面看着。窗外……那家伙就在外面。）');
    const hy = S.actor(C('hayato'));
    if (hy) Object.assign(hy, { x: 180, y: 158 });
  }

  // ================================================================ 节拍 5 走出空房子（雨停）→ 段 D
  async function beatStreet(S) {
    const p = S.player, hc = C('hayato');
    await S.setStage('street_fin', { x: 304, y: 152, facing: 1, music: null, fade: false });
    const hy = S.actor(hc);
    if (hy) Object.assign(hy, { x: 296, y: 146, follow: null, facing: 1 });
    const kira = spawnKira(S, 520, 156, -1);
    snapTo({ x: 420 });
    await S.fadeIn(0.6);
    S.mark('fin_street');
    await S.walk(p, 420, 156, { speed: 60 });
    S.fx('smoke', { x: kira.x, y: kira.y - 26, n: 4, rise: 12, life: 1.0, colour: '#5a5460' }, { life: 1.2 });
    await S.say(C('kira'), '……你一定要把我逼到这一步吗。', { expr: 'rage', actor: kira });
    await S.say('josuke', '你在这个镇上杀了多少人，自己记得清吗？', { expr: 'rage' });
    focus(null);
    S.mark('b19d_start');
  }
  // 亿泰的梦（段 D 中途，R.okuyasuBack 调）：一片白，远处有光，形兆背对着光
  R().dream = async function (S) {
    const kc = C('keicho'), oc = C('okuyasu');
    S.sfx('sparkle', 0.6);
    S.flash(0.5, 1, '#ffffff');
    const parts = [
      { kind: 'sprite', cid: kc, anim: 'idle', x: 204, y: 150, flip: true, alpha: 1 },
      { kind: 'sprite', cid: oc, anim: 'idle', x: 120, y: 158, alpha: 1 },
    ];
    const hudWas = G.hud.on;
    G.hud.on = false;
    const h = T().show(S, { bg: 'afterlife_dream', parts });
    S.mark('fin_dream');
    await S.wait(0.6);
    await S.say(oc, '哥……？你在这里啊。我是不是……也要过去了？', { expr: 'shock' });
    await S.say(kc, '你想去哪里？');
    await S.say(oc, '我脑子不好使，你说去哪我就去哪。');
    await S.say(kc, '……这次你自己决定。');
    await S.say(oc, '……那我要回杜王町。', { expr: 'normal' });
    await S.animate(0.8, (k) => { parts[0].alpha = 1 - k; });
    S.flash(0.6, 1, '#ffffff');
    await S.wait(0.4);
    h.close();
    G.hud.on = hudWas;
  };
  // 段 D 赢：吉良跪在地上，承太郎、康一、露伴从岔路赶来
  async function beatSurround(S) {
    const p = S.player, kira = S.actor('kira');
    S.hint(null);
    if (p.cid !== 'josuke') S.setLeader('josuke', { force: true, silent: true });
    const j = S.player;
    if (kira) { kira.team = 'npc'; kira.hold = true; S.pose(kira, 'hurt', { freeze: 0 }); }
    S.mark('b19d_done');
    S.music('tension', 0.8);
    const kx = kira ? kira.x : 600, ky = kira ? kira.y : 156;
    const jt = place(S, 'jotaro4', 560, 146, 1);
    const ko = place(S, 'koichi', 548, 150, 1);
    const rh = S.spawn(C('rohan'), 572, 148, { id: 'rohan', name: '岸边露伴', facing: 1 });
    S.walk(ko, kx - 40, ky + 6, { speed: 80 }).catch(G.cancelIgnore);
    S.walk(rh, kx + 44, ky - 6, { speed: 80 }).catch(G.cancelIgnore);
    await S.walk(jt, kx + 30, ky + 4, { speed: 70 });
    S.face(jt, kira); S.face(ko, kira); S.face(rh, kira); S.face(j, kira);
    S.mark('fin_surround');
    await S.say('jotaro4', '……吉良吉影。到此为止了。');
    S.nameCard(R().card('namecards', 'rohan'), { y: NAME_TOP });
    await S.say(C('rohan'), '你知道我为了找你，在这个镇上走了多少条小路吗。', { expr: 'rage' });
    S.face(ko, j);
    await S.say('koichi', '仗助君！亿泰君！你们没事吧！', { expr: 'shock' });
  }

  // ================================================================ 节拍 6 救护车旁 → 段 E
  async function beatAmbulance(S) {
    const kira = S.actor('kira'), hc = C('hayato'), hy = S.actor(hc);
    await S.say('neighbor', '出什么事了？', { name: '邻居' });
    await S.say('neighbor', '快叫救护车！', { name: '邻居' });
    S.sfx('car_engine', 0.6);
    focus({ x: Math.min(700, (kira ? kira.x : 600) + 90) });
    await S.wait(0.8);
    S.state('ambulance', 1); S.state('siren', 1);
    S.sfx('skid', 0.4);
    S.mark('fin_ambulance');
    await S.wait(0.6);
    const pm = S.spawn('paramedic', 730, 150, { id: 'paramedic', name: '女急救员', facing: -1 });
    await S.walk(pm, (kira ? kira.x : 640) + 22, kira ? kira.y : 156, { speed: 90 });
    S.face(pm, kira);
    S.nameCard('paramedic', { y: NAME_TOP });
    await S.say('paramedic', '请问您叫什么名字？能听见我说话吗？', { name: '女急救员' });
    S.mark('fin_name_paramedic');
    await S.say(C('kira'), '……我叫，吉良吉影。', { expr: 'normal', actor: kira });
    if (hy) { hy.follow = null; S.walk(hy, (kira ? kira.x : 600) - 70, 156, { speed: 90 }).catch(G.cancelIgnore); }
    await S.say(hc, '不对！他要把那个姐姐变成新的炸弹！败者食尘……他想再来一次！', { expr: 'shock' });
    await S.say('jotaro4', '……太远了。');
  }

  // 段 E：康一（ACT3 FREEZE）→ 承太郎（白金之星·世界）。目标段，不会输
  async function segE(S) {
    const kira = S.actor('kira'), ko = S.actor('koichi'), jt = S.actor('jotaro4'), pm = S.actor('paramedic');
    S.stopMusic(0.6);
    S.ambient('heartbeat_loop', 0.4);
    focus({ x: kira.x });
    // 1. 吉良的手慢慢抬起：身边一圈红圈在缩
    let ringT0 = uiNow(), ringDur = 3, ringOn = true;
    const rh = P4().overlay((g) => {
      if (!ringOn || !kira || kira.remove) return;
      const u = Math.min(1, (uiNow() - ringT0) / ringDur), at = G.cam.w2u(kira.x, kira.y - 18, 0), r = 60 * (1 - u) + 10;
      g.save(); g.fillStyle = '#ff3040';
      for (let i = 0; i < 40; i++) { const a = (i / 40) * Math.PI * 2; g.fillRect(Math.round(at.x + Math.cos(a) * r) - 1, Math.round(at.y + Math.sin(a) * r * 0.8) - 1, 3, 3); }
      g.restore();
    }, { z: 2 });
    S.face(ko, kira);
    await S.say('koichi', '（他的手……在往“开关”那边抬！）', { expr: 'shock' });
    for (let tries = 0; ; tries++) {
      ringT0 = uiNow();
      const r = await S.press({ key: 'special', window: ringDur, label: '按 U：回音 ACT3！' });
      if (r !== 'miss' || tries >= 3) break;
      ringDur = 4.5;
      await S.say('koichi', '（还来得及……再来！）', { expr: 'shock' });
    }
    ringOn = false; rh.close();
    if (ko.setStand) ko.setStand(C('echoes3'));
    await S.summon(ko, { dur: 0.15, rise: 6 });
    S.standCard(R().card('standcards', 'echoes3'), { y: NAME_TOP });
    S.standAct(ko, 'punch', { dx: 30, z: 6, dur: 0.8 });
    S.sfx('punch_heavy', 1); S.sfx('thud', 0.9);
    S.sfxText('3 FREEZE！', kira, { dur: 1.2 });
    S.shake(4, 0.4);
    S.fx('sparkles', { x: kira.x, y: kira.y - 4, n: 10, radius: 18, colour: '#ffd040', period: 0.4, size: 3 }, { life: 1.0 });
    S.pose(kira, 'down');
    S.mark('b19e_freeze');
    await S.say(C('kira'), '……放开！这点重量——', { expr: 'rage', actor: kira });
    // 2. 维持重量：连按 J 6 s（按得慢不会输，只是多演两句）
    const ok = await S.mash({ need: 30, time: 6, label: '连按 J：维持重量！' });
    if (!ok) { S.unpose(kira); await S.say(C('kira'), '（手……抬起来了……）', { expr: 'smile', actor: kira }); S.pose(kira, 'down'); S.sfx('thud', 0.8); }
    await S.say('koichi', '承太郎先生！！', { expr: 'rage' });
    // 3. 承太郎：时停
    for (let tries = 0; ; tries++) {
      const r = await S.press({ key: 'special', window: 2.5, label: '按 U：白金之星·世界！' });
      if (r !== 'miss' || tries >= 3) break;
    }
    const ts = S.timestop(jt, { tint: 'blue', sfx: 'timestop_sp', burst: 0.4, dur: 2.4, resume: 0.36, words: false, lines: { start: 'jotaro_ts', end: 'jotaro_resume' } });
    await S.until(() => !G.time.active || G.time.phase === 'stopped');
    S.mark('b19e_timestop');
    jt.x = kira.x + 22; jt.y = kira.y; jt.facing = -1;
    S.standAct(jt, 'rush', { dx: 18, z: 4, hold: true, jitter: 1 });
    const t0 = uiNow();
    const tk = setInterval(() => { if (uiNow() - t0 > 2) clearInterval(tk); else S.sfx('punch', 0.4); }, 90);
    await S.mash({ need: 14, time: 1.6, label: '连按 J：欧拉欧拉！' });
    clearInterval(tk);
    S.standAct(jt, 'punch', { dx: 22, z: 4, dur: 0.5 });
    S.sfx('punch_heavy', 1);
    await ts;
    S.sfxText('ORA!', kira, { dur: 0.9 });
    S.shake(5, 0.4);
    S.unpose(kira);
    if (pm) S.walk(pm, pm.x + 40, pm.y, { speed: 120 }).catch(G.cancelIgnore);
    await S.arc(kira, 682, 150, 30, 0.6, { anim: 'hurt' });
    S.pose(kira, 'down');
    S.sfx('thud', 1);
    await S.wait(0.4);
    // 救护车倒车 → 黑屏 + 刹车声（克制：不演）
    S.state('ambulance', 2);
    S.sfx('car_engine', 0.8);
    await S.wait(0.7);
    S.ambient(null);
    await S.fadeOut(0.15);
    S.sfx('skid', 1);
    await S.wait(1.4);
  }

  // ================================================================ 节拍 7 冷色的小路：吉良的最后
  async function beatAlleyCold(S) {
    const p = S.player;
    S.leave(C('hayato'), { drop: true });
    await S.setStage('alley_fin', { x: 30, y: 150, facing: 1, music: null, fade: false });
    p.visible = false;
    for (const m of G.party.members) if (m !== p) m.visible = false;
    const kira = spawnKira(S, 200, 152, 1);
    const rm = S.spawn(C('reimi'), 300, 152, { id: 'reimi', name: '杉本铃美', facing: 1 });
    const ar = S.spawn(C('arnold'), 318, 156, { id: 'arnold', name: '阿诺德', facing: 1 });
    S.pose(ar, 'sit');
    snapTo({ x: 250 });
    S.flash(0.8, 1, '#ffffff');
    await S.fadeIn(0.4);
    S.ambient('clock_tick', 0.3);
    S.mark('fin_alley');
    await S.say(C('kira'), '……成功了。时间倒回去了。', { expr: 'smile', actor: kira });
    S.emote(kira, '……？', 1.2);
    await S.narrate('他看了看手表。秒针一动不动。', { pos: 'top' });
    S.ambient(null);
    S.music('sad', 1.0);
    S.nameCard(R().card('namecards', 'reimi'), { y: NAME_TOP });
    await S.say(C('reimi'), '你已经死了，吉良吉影。', { actor: rm });
    await S.say(C('kira'), '……什么？', { expr: 'shock', actor: kira });
    // 回忆：剪影三格（黑底）
    const ghost = (cid, anim, x, y, flip) => ({ kind: 'sprite', cid, anim, x, y, flip, alpha: 0.55 });
    const fl = T().show(S, { bg: '#16141c', parts: [ghost(C('kira'), 'down', 150, 150), ghost(C('echoes3'), 'punch', 176, 132, true)] });
    S.sfx('thud', 0.6);
    await S.wait(0.9);
    fl.parts.length = 0; fl.parts.push(ghost('jotaro4', 'pose', 190, 150, true), ghost(C('kira'), 'hurt', 130, 146));
    S.sfx('punch_heavy', 0.6);
    await S.wait(0.9);
    fl.parts.length = 0;
    S.sfx('car_engine', 0.5);
    await S.wait(0.6);
    S.sfx('skid', 0.7);
    await S.wait(0.6);
    fl.close();
    await S.say(C('reimi'), '急救员只知道你的名字。她没有看见你的脸。', { actor: rm });
    await S.say(C('kira'), '那又怎样……我只是想过安静的日子。你回头看看我。', { expr: 'rage', actor: kira });
    await S.walk(kira, 284, 152, { speed: 50 });
    // 阿诺德咬住他的袖子一甩
    S.unpose(ar);
    S.pose(ar, 'bite');
    S.sfx('dog_bark', 0.9);
    S.sfxText('汪！', ar, { dur: 0.8 });
    S.face(kira, -1);
    await S.wait(0.5);
    S.mark('fin_hands');
    // 小路深处的一群手的影子
    const t0 = uiNow();
    const hands = P4().overlay((g) => {
      const u = Math.min(1, (uiNow() - t0) / 1.6), at = G.cam.w2u(kira.x, kira.y, 0);
      g.save(); g.fillStyle = 'rgba(8,4,16,0.85)';
      for (let i = 0; i < 9; i++) {
        const y = at.y - 120 + i * 16, len = 40 + 300 * u * (0.6 + 0.4 * Math.sin(i * 1.7));
        const x0 = Math.max(0, at.x - len);
        g.fillRect(x0, y, len, 7);
        g.fillRect(x0 + len - 4, y - 4, 10, 14);
        for (let k = 0; k < 4; k++) g.fillRect(x0 + len + 4, y - 4 + k * 4, 8, 2);
      }
      g.restore();
    }, { z: 2 });
    await S.say(C('kira'), '等等——我——', { expr: 'shock', actor: kira });
    await S.walk(kira, -20, 152, { speed: 140, backward: true });
    kira.remove = true;
    await S.fadeOut(0.6);
    hands.close();
    rm.remove = true; ar.remove = true;
  }

  // ================================================================ 节拍 8 天亮的小路：铃美和阿诺德
  async function beatAlleyDawn(S) {
    const p = S.player, oc = C('okuyasu');
    await S.setStage('alley_fin', { bg: 'ghost_alley_dawn', x: 150, y: 154, facing: 1, music: 'sad', fade: false });
    p.visible = true;
    Object.assign(p, { x: 150, y: 156, facing: 1 });
    const ko = place(S, 'koichi', 190, 158, 1);
    const jt = place(S, 'jotaro4', 100, 150, 1);
    const ok = place(S, oc, 124, 162, 1);
    const rh = S.spawn(C('rohan'), 170, 148, { id: 'rohan', facing: 1 });
    const rm = S.spawn(C('reimi'), 300, 152, { id: 'reimi', facing: -1 });
    const ar = S.spawn(C('arnold'), 318, 156, { id: 'arnold', facing: -1 });
    snapTo({ x: 220 });
    await S.fadeIn(0.8);
    await S.say(C('reimi'), '谢谢你们。十五年了，我终于可以走了。', { expr: 'smile', actor: rm });
    await S.say('koichi', '铃美小姐……');
    await S.say(C('reimi'), '康一君，你一开始就相信我的话。', { expr: 'smile', actor: rm });
    await S.say(C('rohan'), '……那时候我没能救你。这次总算还上了。', { actor: rh });
    await S.say('josuke', '替我们跟良平爷爷问个好。');
    await S.say(oc, '要是在那边看到我哥，跟他说我过得挺好。', { expr: 'smile' });
    S.pose(jt, 'pose');
    await S.say('jotaro4', '……一路走好。');
    S.unpose(jt);
    // 化成光升上天
    S.sfx('sparkle', 1);
    S.fx('sparkles', { x: 308, y: 130, n: 14, radius: 24, colour: '#fff4c0', period: 0.5, size: 3 }, { life: 2.4 });
    if (ar) S.pose(ar, 'idle');
    await S.animate(2.0, (k) => { for (const a of [rm, ar]) if (a) { a.z = 80 * k * k; a.alpha = 1 - k; } });
    S.flash(0.5, 0.8, '#ffffff');
    rm.remove = true; ar.remove = true;
    S.mark('fin_farewell');
    void ko; void ok;
    await S.wait(0.8);
    await S.fadeOut(0.8);
  }

  // ================================================================ 节拍 9 傍晚：等人回家的人
  async function beatDusk(S) {
    const p = S.player;
    await S.setStage('street_fin', { x: 100, y: 156, facing: 1, music: 'sad', fade: false });
    p.visible = false;
    for (const m of G.party.members) if (m !== p) m.visible = false;
    S.state('pm', 1); S.state('ambulance', 0); S.state('siren', 0);
    const hy = S.spawn(C('hayato'), 640, 156, { id: 'hayato_d', facing: 1 });
    const sh = S.spawn(C('shinobu'), 686, 147, { id: 'shinobu', facing: -1 });
    snapTo({ x: 660 });
    await S.fadeIn(0.8);
    S.emote(hy, '……', 2);
    await S.say(C('shinobu'), '早人，爸爸今天又晚了呢。', { actor: sh });
    S.mark('fin_dusk');
    await S.narrate('这个镇上，还有很多人在等一个不会回来的人。', { pos: 'top' });
    await S.narrate('早人什么都没有说。他把那件事，一个人扛下来了。', { pos: 'top' });
    await S.fadeOut(0.8);
  }

  // ================================================================ 节拍 10 1999 年夏末
  async function beatEpilogue(S) {
    await S.setStage('map_fin', { x: 160, y: 165, music: null, fade: false });
    S.player.visible = false;
    S.music('victory', 1.0);
    await S.fadeIn(0.5);
    const cal = await calendar(S, 'final_late', 'stamp_late');
    await S.fadeOut(0.4);
    cal.close();
    S.mark('fin_epilogue');
    await S.fadeIn(0.2);
    const lines = [
      '乔瑟夫收养了静。「……这孩子总有一天会长成一个了不起的人。」',
      '承太郎写完了杜王町海边那只海星的论文，拿到了博士学位。',
      '康一和由花子在海边约会，被由花子拽着走。',
      '东尼欧的店门口排起了队。',
      '安杰罗岩还在老地方，有人在旁边放了一束花。',
    ];
    for (let i = 0; i < lines.length; i++) {
      if (i === 3) S.music('daily', 1.0);
      await blackCard(S, lines[i]);
    }
    await S.fadeOut(0.4);
  }

  // ================================================================ 节拍 11 杜王港：钱包 → 完 → 职员表
  async function beatHarbor(S) {
    const p = S.player, oc = C('okuyasu');
    await S.setStage('harbor_fin', { x: 520, y: 156, facing: 1, music: 'title', fade: false });
    for (const m of G.party.members) if (m !== p) m.visible = false;
    p.visible = true;
    const jt = place(S, 'jotaro4', 742, 150, -1);
    const jo = S.spawn(C('joseph'), 764, 156, { id: 'joseph', name: '乔瑟夫', facing: -1 });
    Object.assign(p, { x: 420, y: 156, facing: 1 });
    snapTo({ x: 640 });
    await S.fadeIn(0.8);
    S.mark('fin_harbor');
    await S.walk(p, 712, 156, { speed: 100 });
    await S.say('josuke', '承太郎先生！老爷子！', { expr: 'smile' });
    await S.say('josuke', '……保重。');
    await S.say('jotaro4', '你也是，仗助。');
    await S.say(C('joseph'), '仗助，有空到纽约来——嗯？我的钱包呢？', { expr: 'shock', actor: jo });
    // 仗助挥着钱包往回跑
    const wl = T().prop(S, 'fin_wallet', p.x, p.y + 0.5, { id: 'wallet', frame: 0, z: 26 });
    T().tick(() => { if (!wl || wl.remove) return true; wl.x = p.x + p.facing * 6; wl.y = p.y + 0.5; wl.z = 26 + Math.round(Math.abs(Math.sin(now() * 10)) * 4); return false; });
    S.mark('fin_wallet');
    S.walk(p, 560, 156, { speed: 130 }).catch(G.cancelIgnore);
    await S.say('josuke', 'Great～ 当作零花钱啦！', { expr: 'smile' });
    await S.say(C('joseph'), '喂！还给我！', { expr: 'rage', actor: jo });
    S.pose(jt, 'pose');
    await S.say('jotaro4', '……呀嘞呀嘞。');
    await S.until(() => !p.script);
    if (wl) wl.remove = true;
    // 三个人走在港口的路上
    const ok = place(S, oc, 520, 160, -1);
    const ko = place(S, 'koichi', 540, 164, -1);
    S.walk(ok, 300, 160, { speed: 40 }).catch(G.cancelIgnore);
    S.walk(ko, 320, 164, { speed: 40 }).catch(G.cancelIgnore);
    focus(p);
    await S.walk(p, 340, 156, { speed: 40 });
    S.face(p, 1);
    S.pose(p, 'pose');
    S.sfx('glint', 0.8);
    S.fx('glint', { x: p.x, y: p.y - 40, size: 9 }, { life: 0.5 });
    await S.wait(1.2);
    await S.fadeOut(0.6);
    S.unpose(p);
    // 地图拉远到整个杜王町
    await S.setStage('map_fin', { x: 160, y: 165, music: undefined, fade: false });
    S.player.visible = false;
    S.zoom(2.6, 140, 104, 0);
    await S.fadeIn(0.5);
    await S.zoom(1, null, null, 2.4);
    await S.title('fin_end', { dur: 2.4 });
    S.mark('fin_end');
    await credits(S);
  }
  // 职员表：黑底往上滚
  async function credits(S) {
    const rows = [
      ['JoJo 的奇妙冒险 第四部', 16], ['不灭钻石', 16], ['', 12],
      ['原作　荒木飞吕彦', 12], ['', 12],
      ['剧情 · 关卡 · 像素美术 · 程序', 12], ['Claude', 12], ['', 12],
      ['出品　LQM', 12], ['', 12],
      ['本作为同人游戏，与原作版权方无关', 12], ['', 12], ['谢谢游玩', 16],
    ];
    const t0 = uiNow(), dur = 9;
    const h = P4().overlay((g) => {
      const t = uiNow() - t0;
      g.save(); g.fillStyle = '#08060c'; g.fillRect(0, 0, 640, 360);
      let y = 380 - (t / dur) * 520;
      for (const [s, size] of rows) { if (s && y > -20 && y < 380) P4().text(g, s, 320, Math.round(y), '#fff4d6', size, 'center'); y += size === 16 ? 30 : 22; }
      g.restore();
    }, { z: 6 });
    await S.wait(dur + 0.6, 'ui');
    h.close();
  }

  // ================================================================ 段 A 之后的自由走动（10 s 以内）：走近亿泰会被提示
  async function roamOkuyasu(S) {
    const oku = S.actor(C('okuyasu')), p = S.player;
    S.hint('亿泰倒在雨里……走过去看看', 6);
    const t0 = now();
    await S.until(() => !S.busy && ((oku && Math.abs(p.x - oku.x) < 48) || now() - t0 > 10));
  }

  // ================================================================ 终章主流程
  G.STORY.final = async function (S) {
    if (T().resetCounters) T().resetCounters();
    P4().clearOverlays();
    R().okuBack = false; R().kiraHp = null; R().catSeen = false;
    await S.chapterCard('final');
    S.party(['josuke'], { leader: 'josuke' });
    // 节拍 1–2 → 段 A → 节拍 3
    await S.run(async (S2) => {
      await beatCalendar(S2);
      await beatCorner(S2);
      await R().fightA(S2, S2.actor('kira'));
      await beatAfterA(S2);
    }, { keepLocked: false });
    await roamOkuyasu(S);
    // 节拍 3 → 节拍 4 → 段 B → 段 C → 节拍 5 → 段 D → 节拍 6 → 段 E → 节拍 7–11
    await S.run(async (S2) => {
      await beatHayatoBomb(S2);
      await beatHouse(S2);
      await R().fightB(S2);
      await afterB(S2);
      await R().fightC(S2);
      await S2.fadeOut(0.6);
      await beatStreet(S2);
      await R().fightD(S2, S2.actor('kira'));
      await beatSurround(S2);
      await beatAmbulance(S2);
      await segE(S2);
      await beatAlleyCold(S2);
      await beatAlleyDawn(S2);
      await beatDusk(S2);
      await beatEpilogue(S2);
      await beatHarbor(S2);
    }, { keepLocked: true });
    P4().clearOverlays();
  };
  G.STORY.final.packs = PACKS;
  // 整章测试（tools/dev/p4_play.js）对照的剧情标记
  G.STORY.final.marks = ['fin_calendar', 'fin_corner', 'fin_name', 'fin_rohan_alive', 'b19a_start', 'b19a_cat', 'b19a_okuyasu_down',
    'fin_hayato_bomb', 'fin_heal', 'fin_house', 'b19b_ash', 'b19b_done', 'b19c_vase', 'b19c_shard_hit', 'b19c_lighter', 'b19c_phone',
    'b19c_photo_boom', 'fin_street', 'b19d_start', 'b19d_okuyasu_back', 'fin_dream', 'b19d_pull', 'b19d_done', 'fin_surround',
    'fin_ambulance', 'fin_name_paramedic', 'b19e_freeze', 'b19e_timestop', 'fin_alley', 'fin_hands', 'fin_farewell', 'fin_dusk',
    'fin_epilogue', 'fin_harbor', 'fin_wallet', 'fin_end'];
})();
