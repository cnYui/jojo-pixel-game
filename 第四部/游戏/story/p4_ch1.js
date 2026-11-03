// 第1章　虹村家 / 弓与箭（开发脚本 第四部/docs/第1章_开发脚本.md；地图后缀 _ch1）。整章流程：
//   节拍 1 篇章卡 → 日历地图（「虹村家」）→ 2 放学路上、铁门摔上 → 3 箭射穿康一、亿泰拦路 → 第 1 战 轰炸空间
//   → 4 花盆砸晕亿泰、承太郎讲弓与箭 → 5 前院自由走动（进屋）→ 6 走廊：形兆、亿泰被打、仗助救他、康一被拉回来治好 → 第 2 战段 1
//   → 7 蛋、形兆的命令 → 第 2 战段 2（楼梯）→ 8 形兆倒下 → 9 阁楼的父亲 → 10 往事 → 11 全家福（自由走动 C）
//   → 12 辣妹、形兆被拉进电线 → 13 亿泰入队 → 14 回家路上、蛋、To Be Continued
//   克制（第三部 D10 + 设计文档 4.6）：康一中箭只画箭和一道光；形兆被拉进电线只给电光和剪影；父亲只给剪影；往事只用剪影和旁白。
//   亿泰 / 轰炸空间 / 蛋归第2章画：第2章的图还没合进来时，这里在运行时借现成的图顶上（ensureCast），合进来以后自动用正式的。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const CH1 = () => G.P4CH1;
  const F = () => G.flags;
  const now = () => (G.clk ? G.clk.world : 0);
  const NAME_TOP = 100;
  const KO_MSG = '康一：「我、我还动不了……」';
  const { base, walls } = G.p4Stage;

  Object.assign(G.NAMES, { okuyasu: '亿泰', keicho: '形兆', thehand: '轰炸空间', nijimura_dad: '？？？', rhcp: '电线里的声音' });

  const ST = G.STAGES;
  ST.map_ch1 = base('map_ch1', 'morioh_map', 320, { yMin: 160, yMax: 170, music: null, obstacles: [] });
  ST.yard_ch1 = base('yard_ch1', 'nijimura_yard', 640, { music: 'tension', state: { gate: 1, pots_gone: 0, figure: 0, pm: 0 }, obstacles: walls(8, 632, 640) });
  ST.hall_ch1 = base('hall_ch1', 'nijimura_hall', 640, { music: 'tension', state: { holes: 0 }, obstacles: walls(8, 632, 640) });
  ST.stairs_ch1 = base('stairs_ch1', 'nijimura_stairs', 480, { music: 'tension', state: { holes: 0 }, obstacles: walls(8, 472, 480) });
  ST.attic_ch1 = base('attic_ch1', 'nijimura_attic', 320, { music: 'tension', state: { spark: 0 }, obstacles: walls(24, 296, 320) });

  // ================================================================ 第2章的人还没画好时的替身（运行时借图，不写文件）
  function ensureCast() {
    const D = G.D;
    if (!D) return;
    const C = D.chars;
    if (!C.okuyasu && C.thug_b) {
      C.okuyasu = Object.assign({}, C.thug_b, { name: '虹村亿泰（占位）', amap: Object.assign({}, C.thug_b.amap, { cmd: 'idle', pose: 'idle', dizzy: 'hurt', sit: 'idle' }) });
      G.dbg && G.dbg.ev && G.dbg.ev('ch1_placeholder', { cid: 'okuyasu' });
    }
    if (!C.thehand && C.crazyd) C.thehand = Object.assign({}, C.crazyd, { name: '轰炸空间（占位）', amap: Object.assign({}, C.crazyd.amap, { erase: 'punch', pull: 'upper' }) });
    if (D.stands && !D.stands.thehand && D.stands.crazyd) D.stands.thehand = Object.assign({}, D.stands.crazyd, { cn: '轰炸空间', en: 'THE HAND', owner: 'okuyasu', aura: '#7a9ae8', card: '#a8c0f0' });
    if (D.heroes && !D.heroes.okuyasu) D.heroes.okuyasu = { cid: 'okuyasu', cn: '虹村亿泰', short: '亿泰', rn: 'NIJIMURA OKUYASU', stand: 'thehand',
      burst: ['#1a2a6a', '#3a4aa8', '#6a8ae0'], panel: '#0a1030', accent: '#8aa8ff', nameColor: '#4a64b0', blipHz: 360, grunt: null };
    // 康一的图集没有 down：躺着用鞠躬那一帧转 90°（和引擎的通用回退一样，只是写明了，不算缺图）
    const ka = G.atlas('koichi');
    if (ka && ka.anims && !ka.anims.down && !ka.amap.down) ka.amap.down = { a: 'bow', rot: -90, dy: -8 };
    const oa = C.okuyasu && C.okuyasu.name && C.okuyasu.name.indexOf('占位') >= 0 ? G.atlas('okuyasu') : null;
    if (oa && !oa.anims.sit && !oa.amap.sit) oa.amap.sit = 'idle';
    // 日历地图上「虹村家」的图钉位置（住宅区西边）：序章的 bg.json 不改，运行时补一个锚点
    const mm = D.bg && D.bg.morioh_map;
    if (mm) { mm.anchors = mm.anchors || {}; if (!mm.anchors.nijimura) mm.anchors.nijimura = [70, 140]; }
    if (P4().CAL && !P4().CAL.ch1) P4().CAL.ch1 = { pins: [{ at: 'nijimura', label: '虹村家' }], stamp: 'stamp' };
  }
  const hasCard = (sec, k) => !!(G.D && G.D.ui && G.D.ui[sec] && G.D.ui[sec][k]);

  const pool = (cid) => G.party._actor(cid);
  function place(S, cid, x, y, facing, o = {}) {
    const a = pool(cid), W = G.world;
    Object.assign(a, { x, y, z: 0, facing: facing || 1, follow: null, hold: false, script: null, state: 'idle', remove: false, rot: 0, alpha: 1, tint: null });
    a.visible = o.visible !== false;
    if (W.player !== a) a.team = 'npc';
    a.play(a.idleAnim || 'idle');
    W.stage.add(a);
    return a;
  }
  const focus = (o) => { G.world.focus = o; };
  const snapTo = (o) => { G.world.focus = o; G.world.snapCamera(); };
  const AN = (key) => (G.D.bg[key] && G.D.bg[key].anchors) || {};

  // 回音的蛋：第2章画 echoes_egg 之前，用像素画一颗带花纹的绿蛋顶着
  function egg(S, x, y, z) {
    if (S.exists('prop:echoes_egg')) return T().prop(S, 'echoes_egg', x, y, { id: 'ch1_egg', z: z || 0 });
    const st = G.world.stage;
    const p = { type: 'pixel', x, y, z: z || 0, id: 'ch1_egg', draw: (P, sx, sy, t) => {
      const px = G.px, yy = sy - (p.z || 0);
      px.rect(P, sx - 3, yy - 9, 6, 9, '#c8e8a0', 1); px.rect(P, sx - 2, yy - 10, 4, 1, '#c8e8a0', 1); px.rect(P, sx - 4, yy - 7, 8, 5, '#c8e8a0', 1);
      px.rect(P, sx - 3, yy - 6, 2, 2, '#5aa040', 1); px.rect(P, sx + 1, yy - 8, 2, 2, '#5aa040', 1); px.rect(P, sx, yy - 4, 2, 2, '#5aa040', 1);
      px.rect(P, sx - 2, yy - 9, 1, 2, '#ffffff', 0.8);
      if (Math.floor(t * 2) % 4 === 0) px.rect(P, sx - 4, yy - 10, 8, 10, '#e8ffd0', 0.25);
    } };
    st.props.push(p);
    return p;
  }

  // ================================================================ 节拍 1 篇章卡 → 日历地图
  async function beatCalendar(S) {
    S.player.visible = false;
    await S.setStage('map_ch1', { x: 160, y: 165, music: null });
    for (const a of G.world.stage.actors) a.visible = false;      // 日历地图上不站人（跟着的康一也藏起来）
    const cal = await P4().calendar(S, 'ch1', { hold: 1.6 });
    S.mark('ch1_calendar');
    await S.fadeOut(0.45);
    if (cal) cal.close();
  }

  // ================================================================ 节拍 2 放学路上、铁门摔上
  async function beatGate(S) {
    const p = S.player, an = AN('nijimura_yard');
    await S.setStage('yard_ch1', { x: 30, y: 158, facing: 1, music: 'daily', fade: false });
    S.state('gate', 1); S.state('figure', 0); S.state('pots_gone', 0); S.state('pm', 0);
    p.visible = true;
    const ko = place(S, 'koichi', 6, 162, 1);
    snapTo({ x: 160 });
    await S.fadeIn(0.6);
    S.location('nijimura', { y: NAME_TOP });
    S.walk(ko, 74, 162, { speed: 40 }).catch(G.cancelIgnore);
    await S.walk(p, 54, 157, { speed: 42 });
    await S.narrate('入学一个星期。我和仗助君已经是每天一起回家的朋友了。', { pos: 'top' });
    await S.until(() => !ko.script);
    S.face(ko, 1);
    await S.say('koichi', '仗助君，这栋房子好像一直没人住呢。');
    await S.say('josuke', '听说要拆了吧。……院子里的草都比你高了。');
    await S.say('koichi', '才没有那么夸张！', { expr: 'smile' });
    const gx = (an.gate || [110, 146])[0];
    await S.walk(ko, gx, 150, { speed: 40 });
    S.face(ko, 1);
    // 二楼窗帘后一个人影一闪
    S.state('figure', 1);
    focus({ x: 200 });
    S.sfx('creak', 0.5);
    await S.wait(0.8);
    S.state('figure', 0);
    // 铁门“哐”地被摔上，撞在康一脸上
    const ok = place(S, 'okuyasu', gx + 18, 138, -1);
    S.state('gate', 0);
    S.sfx('metal_crunch', 1); S.shake(4, 0.3);
    S.sfxText('哐！', { wx: gx, wy: 146, wz: 22 }, { dur: 0.8 });
    S.arc(ko, gx - 22, 158, 8, 0.35, { anim: 'hurt' }).catch(G.cancelIgnore);
    S.mark('ch1_gate');
    await S.wait(0.4);
    await S.say('koichi', '好痛！', { expr: 'shock' });
    await S.say('okuyasu', '看什么看？这里是我家。', { expr: 'rage', name: '？？？' });
    if (hasCard('namecards', 'okuyasu')) S.nameCard('okuyasu', { y: NAME_TOP });
    await S.walk(p, gx - 34, 160, { speed: 60 });
    S.face(p, 1);
    await S.say('josuke', '喂，门撞到人了，道个歉总可以吧。');
    await S.say('okuyasu', '你这发型……算了。我脑子不好使，懒得跟你吵。', { name: '亿泰' });
    void ok;
  }

  // ================================================================ 节拍 3 箭
  async function beatArrow(S) {
    const p = S.player, ko = S.actor('koichi'), ok = S.actor('okuyasu'), an = AN('nijimura_yard');
    const win = an.window || [225, 60];
    S.sfx('creak', 0.6);
    await S.wait(0.3);
    S.sfx('whoosh', 1);
    // 一道光从二楼窗口直射到康一胸口：只画箭和一道光
    const ar = T().prop(S, 'arrow', win[0], 150, { id: 'ch1_arrow', frame: 1, z: 150 - win[1] });
    if (ar) ar.facing = ko.x < win[0] ? -1 : 1;
    S.fx('light_beam', { x0: win[0], y0: win[1], x1: ko.x, y1: ko.y - 18, colour: '#fff4c0', w: 2 }, { life: 0.3 });
    if (ar) await S.animate(0.18, (k) => { ar.x = G.lerp(win[0], ko.x + 2, k); ar.y = G.lerp(150, ko.y + 0.5, k); ar.z = G.lerp(150 - win[1], 18, k); });
    S.flash(0.2, 0.9, '#ffffff');
    S.sfx('knife_hit', 1);
    S.impact('invert', 1 / 30);
    S.mark('ch1_arrow');
    await S.wait(0.4);
    S.pose(ko, 'down');
    S.sfx('thud', 0.7);
    if (ar) { ar.x = ko.x + 3; ar.y = ko.y + 1; ar.z = 4; ar.rot = -0.6; }
    await S.wait(0.6);
    await S.say('keicho', '哦？射中的是个小鬼……可惜，这小子大概撑不过去。', { name: '窗口里的声音' });
    S.music('tension', 0.4);
    await S.say('josuke', '康一！', { expr: 'rage' });
    S.walk(p, ko.x - 6, 160, { speed: 90 }).catch(G.cancelIgnore);
    // 亿泰推开铁门，站到路中间
    S.state('gate', 1);
    S.sfx('metal_scrape', 0.7);
    await S.walk(ok, ko.x + 60, 158, { speed: 70 });
    S.face(ok, -1);
    p.script = null;
    S.face(p, 1);
    await S.say('okuyasu', '哥说了，不许外人插手。', { name: '亿泰' });
    await S.say('okuyasu', '你也有替身吧？那正好。', { name: '亿泰', expr: 'smile' });
    if (ok.setStand && !ok.stand) ok.setStand('thehand');
    if (ok.stand) ok.stand.summon();
    S.sfx('stand_summon_purple', 0.7);
    if (hasCard('standcards', 'thehand')) S.standCard('thehand', { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.wait(0.6);
    await S.say('okuyasu', '我的右手抹过去的东西，会从这个世界上消失。', { name: '亿泰' });
    // 康一被拖到铁门口（不参战）
    if (ar) ar.remove = true;
    Object.assign(ko, { x: 112, y: 168 });
    S.music('battle', 0.3);
    await S.vs({ key: 'thehand', hero: 'josuke', enemy: { cid: 'okuyasu', anim: 'pose' } });
    G.uifx.vsTag('thehand');
  }

  // ================================================================ 节拍 4 花盆、承太郎
  async function beatAfterHand(S) {
    const p = S.player, ok = S.actor('okuyasu');
    if (ok) {
      ok.team = 'npc'; ok.brain = null; ok.atk = null; ok.tele = null;
      if (ok.stand) ok.stand.recall({ instant: true });
      ok.play('dizzy');
      S.emote(ok, '@_@', 1.2);
      await S.animate(0.8, (k) => { ok.facing = Math.floor(k * 6) % 2 ? 1 : -1; });
      S.pose(ok, 'down');
      S.sfx('thud', 0.8);
    }
    S.mark('ch1_okuyasu_down');
    await S.wait(0.4);
    S.face(p, ok);
    await S.say('josuke', '……自己把花盆拉过来砸自己。这家伙真的脑子不好使。');
    // 黑底，承太郎的头像
    const h = T().show(S, { bg: '#05040a', parts: [{ kind: 'head', cid: 'jotaro4', x: 160, y: 88, scale: 3 }] });
    S.sfx('ding', 0.4);
    await S.say('jotaro4', '仗助，你记好。那支箭，叫弓与箭。', { name: '承太郎（之前在酒店说的话）' });
    await S.say('jotaro4', '五十年前，一个叫恩雅的老太婆用它造出了一群替身使者。');
    S.mark('ch1_jotaro_call');
    await S.say('jotaro4', 'DIO 的替身，也是从那支箭来的。……那东西必须毁掉。');
    h.close();
    // 回到前院：康一不见了
    const ko = S.actor('koichi');
    if (ko) { ko.visible = false; ko.x = -40; }
    S.music('tension', 0.6);
    S.face(p, -1);
    await S.say('josuke', '康一呢？！', { expr: 'shock' });
    await S.say(null, '铁门口只剩一道拖痕，一直通到门廊。');
  }

  // ================================================================ 节拍 5 前院自由走动 A：进屋
  function setupYardFree(S) {
    const st = G.world.stage, an = AN('nijimura_yard'), ok = S.actor('okuyasu');
    const door = an.door || [421, 146];
    if (ok) { ok.talk = async (S2) => { await S2.say(null, '亿泰仰面躺着……还在转圈。'); }; ok.label = '亿泰'; }
    st.hotspots.push(
      { id: 'plate', x: (an.gate || [110])[0] - 26, y: 150, r: 16, label: '门牌', use: async (S2) => { await S2.say(null, '门柱上的门牌写着「虹村」。'); } },
      { id: 'window', x: (an.window || [225])[0], y: 150, r: 18, label: '二楼的窗', tags: ['fix'], fx: (an.window || [225, 60])[0], fy: (an.window || [225, 60])[1],
        use: async (S2) => { await S2.say(null, '刚才射箭的窗口。窗帘又拉上了。'); },
        look: async (S2) => { await S2.say('josuke', '……那不是坏掉的东西。'); F().ch1Window = true; } },
      { id: 'grass', x: 520, y: 160, r: 30, label: '杂草', use: async (S2) => { await S2.say(null, '草比膝盖还高。……好久没人打理了。'); } },
      { id: 'trail', x: 300, y: 154, r: 20, label: '拖痕', use: async (S2) => { await S2.say(null, '拖痕一直通到门廊。'); } },
      { id: 'door', x: door[0], y: 150, r: 18, label: '正门', use: async () => { F().ch1Door = true; } },
    );
    T().goal(S, { x: door[0], y: 152, label: '正门', delay: 45, every: 15, done: () => !!F().ch1Door, text: '康一被拖进屋里了：走到正门按 E' });
  }

  // ================================================================ 节拍 6 走廊：形兆、亿泰、康一
  async function beatHall(S) {
    const p = S.player;
    T().memberTalk({});
    S.hint(null);
    await S.setStage('hall_ch1', { x: 180, y: 158, facing: 1, music: 'tension' });
    S.mark('ch1_enter');
    const kc = S.spawn('keicho', 450, 150, { id: 'keicho', facing: -1, name: '虹村形兆' });
    focus({ x: 330 });
    await S.walk(p, 300, 158, { speed: 50 });
    await S.say('keicho', '我叫虹村形兆。刚才那个蠢货，是我弟弟。');
    S.nameCard('keicho', { y: NAME_TOP });
    await S.say('keicho', '那个小鬼被箭射中了。被选中的人会觉醒替身，没被选中的……就那样死掉。');
    await S.say('josuke', '把他还给我！', { expr: 'rage' });
    // 亿泰冲进来
    const ok = place(S, 'okuyasu', 130, 160, 1);
    await S.walk(ok, 250, 160, { speed: 96 });
    await S.say('okuyasu', '哥！我还没输！', { expr: 'rage', name: '亿泰' });
    // “哒哒哒”：亿泰身上冒出一排小火花，跪倒（看不见的东西在打他）
    for (let i = 0; i < 8; i++) G.defer(i * 0.07, () => { S.sfx('gunshot', 0.3); S.fx('hit_spark', { x: ok.x + (i % 3) * 3 - 3, y: ok.y - 10 - (i % 4) * 5, size: 6, accent: '#ffe080' }, { life: 0.2 }); });
    S.sfxText('哒哒哒', ok, { dur: 0.9 });
    ok.play('hurt');
    await S.wait(0.7);
    S.pose(ok, 'down');
    S.mark('ch1_okuyasu_shot');
    await S.say('keicho', '输了就是输了。没用的东西，用不着留着。');
    // 仗助挡到亿泰前面
    await S.walk(p, ok.x + 22, 160, { speed: 90 });
    S.face(p, 1);
    S.pose(p, 'guard');
    for (let i = 0; i < 5; i++) G.defer(i * 0.08, () => { S.sfx('guard', 0.4); S.fx('hit_spark', { x: p.x + 10, y: p.y - 16 - (i % 3) * 4, size: 5, accent: '#ffb0d8' }, { life: 0.2 }); });
    await S.wait(0.5);
    S.unpose(p);
    await S.say('josuke', '……你对亲弟弟也下得去手？', { expr: 'rage' });
    S.face(p, -1);
    await S.summon(p, { dur: 0.12, rise: 4 });
    S.standAct(p, 'reach', { dx: 16, z: 2, dur: 0.8 });
    P4().fixGlow(S, ok.x, ok.y - 10);
    await S.wait(0.6);
    S.recall(p);
    S.unpose(ok);
    S.face(ok, 1);
    await S.say('okuyasu', '你……为什么要救我？', { expr: 'shock', name: '亿泰' });
    await S.say('josuke', '我就是看不惯。');
    S.face(ok, -1);
    await S.say('okuyasu', '……谢了。', { name: '亿泰' });
    // 轰炸空间朝里屋一抹：康一“咻”地被拉到仗助脚边
    S.face(ok, 1);
    if (ok.setStand && !ok.stand) ok.setStand('thehand');
    if (ok.stand) { ok.stand.summon(); ok.stand.act('erase', { dx: 14, dur: 0.6 }); }
    S.sfx('void_eat', 0.9);
    const ko = place(S, 'koichi', (AN('nijimura_hall').side_door || [284])[0], 156, 1);
    S.pose(ko, 'down');
    G.combat.ghostBurst(ko, 3);
    await S.animate(0.18, (k) => { ko.x = G.lerp((AN('nijimura_hall').side_door || [284])[0], p.x + 18, k); });
    S.mark('ch1_koichi_pulled');
    if (ok.stand) ok.stand.recall();
    await S.wait(0.3);
    await S.say('josuke', '康一！……撑住，我这就修好你。', { expr: 'shock' });
    S.face(p, 1);
    await S.summon(p, { dur: 0.12, rise: 4 });
    S.standAct(p, 'reach', { dx: 16, z: 0, dur: 1.0 });
    P4().fixGlow(S, ko.x, ko.y - 6, { n: 9, r: 16 });
    await S.wait(0.9);
    S.recall(p);
    S.mark('ch1_koichi_healed');
    S.unpose(ko);
    S.face(ko, 1);
    await S.say('koichi', '……我、我怎么了？', { expr: 'shock' });
    // 康一第一次看见：满地的小兵
    const show = [];
    for (let i = 0; i < 8; i++) show.push(S.spawn('badco_soldier', 380 + (i % 4) * 14 + (i > 3 ? 7 : 0), 150 + (i > 3 ? 8 : 0), { id: 'show_' + i, facing: -1 }));
    focus({ x: 360 });
    S.sfx('footstep0', 0.5);
    await S.wait(0.6);
    await S.say('koichi', '这、这些是什么……军队？', { expr: 'shock' });
    await S.say('keicho', '看得见了？那你就是被选中的。');
    S.standCard('badcompany', { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.wait(0.8);
    await S.say('keicho', '我的坏公司：步兵六十人，坦克七辆，阿帕奇四架。');
    for (const a of show) a.remove = true;
    // 亿泰退到墙边（这一战他不参与）；形兆退进拱门
    S.walk(ok, 140, 146, { speed: 60 }).catch(G.cancelIgnore);
    await S.walk(kc, 640, 150, { speed: 60 });
    kc.remove = true;
    ok.visible = false;
    S.party(['josuke', 'koichi'], { leader: 'josuke' });
    S.leadable('koichi', false, { msg: KO_MSG });
    S.music('battle', 0.3);
    await S.vs({ key: 'badcompany', hero: 'josuke', enemy: { cid: 'keicho', anim: 'point' } });
    G.uifx.vsTag('badcompany');
  }

  // ================================================================ 节拍 7 蛋、形兆的命令
  async function beatEgg(S) {
    const p = S.player, ko = S.actor('koichi');
    S.state('holes', 1);
    focus(null);
    await S.say('keicho', '哼。走廊挡不住你……那就换个地方。', { name: '形兆（拱门里）' });
    await S.say('keicho', '让我看看，那个小鬼会觉醒成什么。', { name: '形兆（拱门里）' });
    // 康一身上一亮，胸口冒出一颗带花纹的蛋
    S.face(ko, 1);
    S.flash(0.15, 0.5, '#e8ffd0');
    S.sfx('sparkle', 0.9);
    const e = egg(S, ko.x + 6, ko.y + 1, 22);
    S.mark('ch1_egg');
    if (e) await S.animate(0.5, (k) => { e.z = 22 - 22 * k * k; });
    await S.say('koichi', '这是……什么？', { expr: 'shock' });
    // 仗助一脚把蛋踢开，站到康一前面
    await S.walk(p, ko.x + 16, ko.y, { speed: 70 });
    S.face(p, -1);
    p.play('kick');
    S.sfx('whoosh', 0.7);
    if (e) await S.animate(0.5, (k) => { e.x = G.lerp(ko.x + 6, ko.x - 40, k); e.z = 18 * Math.sin(Math.PI * k); });
    await S.say('josuke', '别碰它。不管那是什么，等这边打完再说。');
    S.face(p, 1);
    await S.say('josuke', '康一，躲到我后面。');
    await S.fadeOut(0.5);
    if (e) { if (e.remove !== undefined && e.cid) e.remove = true; else S.unprop(e); }
  }
  async function beatStairs(S) {
    const p = S.player;
    await S.setStage('stairs_ch1', { x: 250, y: 160, facing: 1, music: 'battle', fade: false });
    const ko = S.actor('koichi');
    if (ko) { ko.follow = null; Object.assign(ko, { x: 214, y: 162, facing: 1 }); }
    const kc = S.spawn('keicho', 400, 80, { id: 'keicho', facing: -1, name: '虹村形兆' });
    kc.shadow = false;
    snapTo({ x: 320 });
    await S.fadeIn(0.5);
    kc.play('point');
    await S.say('keicho', '先打腿，再打手，最后打头。', { expr: 'rage' });
    await S.say('keicho', '……按这个顺序，全军进攻。');
    S.mark('ch1_order');
    focus(null);
    void p;
  }

  // ================================================================ 节拍 8 形兆倒下
  async function beatKeichoDown(S) {
    const p = S.player, kc = S.actor('keicho'), ko = S.actor('koichi');
    S.state('holes', 1);
    if (kc) { kc.team = 'npc'; kc.brain = null; kc.play('hurt'); await S.wait(0.4); kc.play('sit'); }
    S.mark('ch1_keicho_down');
    await S.say('keicho', '……被我自己的导弹。', { expr: 'shock' });
    await S.say('josuke', '箭在哪？交出来，我把它毁掉。');
    if (ko) { S.face(ko, 1); await S.say('koichi', '仗助君，楼上……阁楼里有声音。', { expr: 'shock' }); }
    S.sfx('creak', 0.6);
    await S.fadeOut(0.5);
    void p;
  }

  // ================================================================ 节拍 9–10 阁楼的父亲、往事
  async function beatAttic(S) {
    const p = S.player, an = AN('nijimura_attic');
    const box = an.box || [219, 146];
    await S.setStage('attic_ch1', { x: 52, y: 160, facing: 1, music: null, fade: false });
    S.state('spark', 0);
    S.stopMusic(0.4);
    const ko = S.actor('koichi');
    if (ko) { ko.follow = null; Object.assign(ko, { x: 36, y: 166, facing: 1, visible: true }); }
    const dad = S.spawn('nijimura_dad', box[0] - 8, 152, { id: 'dad', facing: 1, name: '？？？' });
    T().prop(S, 'photo_torn', box[0] + 4, 150, { id: 'scraps', frame: 0 });
    snapTo({ x: 160 });
    await S.fadeIn(0.6);
    S.sfx('heartbeat', 0.4);
    await S.wait(0.6);
    await S.walk(p, 110, 158, { speed: 40 });
    S.mark('ch1_father');
    S.sfxText('呜……', dad, { dur: 1.0 });
    await S.say('koichi', '怪、怪物……！', { expr: 'shock' });
    S.music('sad', 0.8);
    const kc = place(S, 'keicho', 40, 152, 1);
    await S.walk(kc, 74, 152, { speed: 40 });
    await S.say('keicho', '别碰他。……那是我爸。');
    // 往事：黑底剪影 + 形兆的旁白
    const sil = T().show(S, { bg: '#060a08', parts: [
      { kind: 'sprite', cid: 'nijimura_dad', anim: 'idle', x: 150, y: 150, scale: 3 },
    ] });
    await S.title('ch1_past', { y: 70 });
    await S.narrate('十年前，家里欠了很多债。老爸替一个叫 DIO 的人做事，换来了钱。', { pos: 'top' });
    await S.narrate('DIO 往他身体里种了一样东西。', { pos: 'top' });
    await S.narrate('后来 DIO 死了，那东西在老爸身体里失控了。他变成了这样，记不得我们，也死不了。', { pos: 'top' });
    S.mark('ch1_past');
    await S.narrate('所以我到处用箭射人，找一个替身能杀死他的人。……让他解脱。', { pos: 'top' });
    sil.close();
  }

  // ================================================================ 节拍 11 自由走动 C：全家福
  async function fixPhoto(S) {
    if (F().ch1Photo) { await S.say('josuke', '……已经拼好了。'); return; }
    F().ch1Photo = true;
    const sc = S.actor('scraps'), dad = S.actor('dad'), an = AN('nijimura_attic');
    const box = an.box || [219, 146];
    S.sfx('whoosh', 0.6);
    for (let i = 0; i < 8; i++) S.fx('sparkles', { x: box[0] - 10 + i * 3, y: 138 - (i % 3) * 4, n: 2, radius: 4, colour: '#f4ecd8', period: 0.4, size: 2 }, { life: 0.6 });
    if (sc) sc.remove = true;
    P4().fixGlow(S, box[0], 136, { n: 9, r: 14 });
    await S.wait(0.5);
    await S.photo({ image: 'props/photo_family', hold: 1.8 });
    S.mark('ch1_photo');
    if (dad) { dad.play('hug'); S.sfxText('……呜', dad, { dur: 1.0 }); }
    await S.wait(0.6);
    await S.say('josuke', '他一直想拼回来的，是这个。');
    await S.say('josuke', '与其找人杀他，不如找个能治好他的人吧。');
    await S.say('josuke', '我的替身治不好他……可总会有办法的。');
    await S.say('keicho', '……');
  }
  function setupAtticFree(S) {
    const st = G.world.stage, an = AN('nijimura_attic'), box = an.box || [219, 146];
    st.hotspots.push(
      { id: 'box', x: box[0], y: 152, r: 18, label: '木箱', tags: ['fix'], fx: box[0], fy: 136,
        use: async (S2) => { await S2.say(null, '箱子里是一堆撕碎的纸片。父亲每天都在拼它。'); if (!F().ch1BoxHint) { F().ch1BoxHint = true; S2.hint('按 U：让疯狂钻石把碎纸修好', 5); } },
        look: fixPhoto },
      { id: 'window', x: (an.window || [160])[0], y: 152, r: 16, label: '小圆窗', use: async (S2) => { await S2.say(null, '外面的天开始暗了。'); } },
      { id: 'trunk', x: (an.trunk || [138])[0], y: 152, r: 14, label: '旧皮箱', use: async (S2) => { await S2.say(null, '皮箱上落满了灰。'); } },
    );
    const dad = S.actor('dad');
    if (dad) { dad.label = '父亲'; dad.talk = async (S2) => { await S2.say(null, '他背对着我们，一直在翻那只箱子。'); }; }
    const kc = S.actor('keicho');
    if (kc) { kc.label = '形兆'; kc.talk = async (S2) => { await S2.say('keicho', '……那堆纸，他拼了十年也没拼好。'); }; }
    T().goal(S, { x: box[0], y: 152, label: '木箱', delay: 20, every: 15, done: () => !!F().ch1Photo, text: '父亲在翻的那只木箱：走过去按 U' });
  }

  // ================================================================ 节拍 12 辣妹、形兆被拉进电线
  async function beatChili(S) {
    const p = S.player, kc = S.actor('keicho'), an = AN('nijimura_attic');
    const out = an.outlet || [262, 118];
    await S.say('josuke', '箭呢？');
    const ok = place(S, 'okuyasu', 40, 150, 1);
    const bow = T().prop(S, 'bow_arrow', ok.x + 6, ok.y + 0.5, { id: 'bow', z: 12 });
    T().tick(() => { if (!bow || bow.remove || ok.remove) return true; bow.x = ok.x + ok.facing * 6; bow.y = ok.y + 0.5; return false; });
    await S.walk(ok, 150, 152, { speed: 70 });
    S.face(ok, 1);
    await S.say('okuyasu', '在、在我这儿。哥，这次就听他的吧！', { name: '亿泰', expr: 'shock' });
    S.face(kc, ok);
    await S.say('keicho', '把箭给我！', { expr: 'rage' });
    await S.say('okuyasu', '不给！老爸都那样了，你还要射多少人？！', { name: '亿泰', expr: 'rage' });
    // 插座“啪”地冒出电火花，一道黄光沿电线窜出来，一只发光的手伸向箭
    S.state('spark', 1);
    S.stopMusic(0.2);
    S.sfx('thunder', 0.6); S.sfx('crossfire', 0.4);
    S.fx('lightning', { x0: out[0], y0: out[1], x1: ok.x + 8, y1: ok.y - 14, colour: '#ffe060' }, { life: 0.5 });
    S.flash(0.1, 0.6, '#fff4a0');
    S.mark('ch1_spark');
    await S.wait(0.4);
    // 形兆推开亿泰
    await S.walk(kc, ok.x + 4, ok.y, { speed: 120 });
    S.face(kc, 1);
    await S.say('keicho', '亿泰，让开！', { expr: 'rage' });
    S.arc(ok, ok.x - 40, 158, 10, 0.35, { anim: 'hurt' }).catch(G.cancelIgnore);
    bow.remove = true;
    // 电光吞住形兆：白光、电弧、剪影被拉长、钻进插座
    kc.tint = { color: '#120a04', k: 1 };
    for (let i = 0; i < 6; i++) G.defer(i * 0.12, () => { S.fx('lightning', { x0: out[0], y0: out[1], x1: kc.x + (i % 2 ? 6 : -6), y1: kc.y - 10 - i * 3, colour: '#ffe060' }, { life: 0.25 }); S.sfx('crossfire', 0.3); });
    S.flash(0.6, 0.8, '#fffbe0');
    S.shake(3, 0.8);
    await S.wait(0.5);
    const x0 = kc.x, y0 = kc.y;
    await S.animate(0.7, (k) => { kc.x = G.lerp(x0, out[0], k * k); kc.y = G.lerp(y0, out[1] + 30, k * k); kc.z = 30 * k * k; kc.scale = 1 - 0.8 * k; kc.alpha = 1 - k * 0.6; });
    kc.remove = true;
    S.flash(0.3, 1, '#ffffff');
    S.sfx('thunder', 0.9);
    S.mark('ch1_keicho_gone');
    await S.wait(0.8);
    await S.say('rhcp', '我叫辣妹。箭我拿走了……这里也不会再有人用它了。', { name: '电线里的声音' });
    S.fx('lightning', { x0: out[0], y0: out[1], x1: out[0] - 4, y1: out[1] + 10, colour: '#ffe060' }, { life: 0.3 });
    S.sfx('crossfire', 0.4);
    await S.wait(0.4);
    S.state('spark', 0);
    await S.wait(0.6);
    // 节拍 13 亿泰入队
    S.music('sad', 1.0);
    await S.walk(ok, out[0] - 30, 156, { speed: 50 });
    S.face(ok, 1);
    S.pose(ok, 'sit');
    await S.say('okuyasu', '……哥。', { name: '亿泰' });
    await S.walk(p, ok.x - 18, 158, { speed: 40 });
    S.face(p, 1);
    await S.wait(0.6);
    await S.say('okuyasu', '我脑子不好使，不知道接下来该干什么。', { name: '亿泰' });
    await S.say('josuke', '那就先跟我们一起。把那个电线里的家伙找出来。');
    S.unpose(ok);
    S.face(ok, -1);
    await S.say('okuyasu', '……嗯。', { name: '亿泰' });
    const canLead = !!(G.KITS && G.KITS.okuyasu);
    S.party(canLead ? ['josuke', 'okuyasu', 'koichi'] : ['josuke', 'koichi', 'okuyasu'], { leader: 'josuke' });
    S.leadable('koichi', false, { msg: KO_MSG });
    if (!canLead) S.leadable('okuyasu', false, { msg: '亿泰：「……让我先静一静。」' });
    S.mark('ch1_okuyasu_join');
    await S.fadeOut(0.8);
  }

  // ================================================================ 节拍 14 回家路上
  async function beatHome(S) {
    const p = S.player;
    await S.setStage('yard_ch1', { x: 200, y: 158, facing: -1, music: 'sad', fade: false });
    S.state('pm', 1); S.state('gate', 1); S.state('pots_gone', 0);
    const ko = S.actor('koichi'), ok = S.actor('okuyasu');
    if (ko) { ko.follow = null; Object.assign(ko, { x: 160, y: 164, facing: -1, visible: true }); }
    if (ok) { ok.follow = null; Object.assign(ok, { x: 236, y: 154, facing: -1, visible: true }); }
    snapTo({ x: 160 });
    await S.fadeIn(0.8);
    await S.title('ch1_home', { y: 110 });
    await S.narrate('那天回家的路上，天已经快黑了。', { pos: 'top' });
    if (ko) {
      const e = egg(S, ko.x - 5, ko.y + 0.5, 14);
      S.sfx('sparkle', 0.4);
      await S.say('koichi', '……我是不是也，变得和他们一样了？');
      // 蛋的特写（蛋上的花纹微微一亮）
      await S.zoom(2.6, ko.x - 5, ko.y - 22, 0.4);
      S.fx('glint', { x: ko.x - 5, y: ko.y - 22, size: 6 }, { life: 0.5 });
      S.sfx('glint', 0.6);
      await S.wait(1.2);
      await S.zoom(1, null, null, 0.3);
      void e;
    }
    S.stopMusic(0.6);
    await S.tbc({ hold: 2.0 });
    S.mark('ch1_tbc');
    void p;
  }

  // ================================================================ 第1章主流程
  G.STORY.ch1 = async function (S) {
    if (T().resetCounters) T().resetCounters();
    P4().clearOverlays();
    ensureCast();
    await S.chapterCard('ch1');
    S.party(['josuke', 'koichi'], { leader: 'josuke' });
    S.leadable('koichi', false, { msg: KO_MSG });
    await S.run(async (S2) => {
      await beatCalendar(S2);
      await beatGate(S2);
      await beatArrow(S2);
      await CH1().fightOkuyasu(S2);
      await beatAfterHand(S2);
    }, { keepLocked: true });
    // 节拍 5 前院自由走动 A（康一不在队里：被拖进屋了）
    S.leave('koichi', { drop: true });
    setupYardFree(S);
    await S.run(async (S2) => { S2.hint('E 调查　U 疯狂钻石　走到正门进屋', 6); });
    await S.until(() => !!F().ch1Door && !S.busy);
    Object.assign(G.STAGES.yard_ch1, { hotspots: [], npcs: [], triggers: [] });
    await S.run(async (S2) => {
      await beatHall(S2);
      await CH1().fightCompanyA(S2);
      await beatEgg(S2);
      await beatStairs(S2);
      await CH1().fightCompanyB(S2);
      await beatKeichoDown(S2);
      await beatAttic(S2);
    }, { keepLocked: true });
    // 节拍 11 自由走动 C：全家福
    setupAtticFree(S);
    await S.run(async (S2) => { S2.hint('父亲在翻的那只木箱……', 5); });
    const t11 = now();
    await S.until(() => (F().ch1Photo || now() - t11 > 60) && !S.busy);
    if (!F().ch1Photo) await S.run(fixPhoto, { keepLocked: true });
    Object.assign(G.STAGES.attic_ch1, { hotspots: [], npcs: [], triggers: [] });
    await S.run(async (S2) => {
      await beatChili(S2);
      await beatHome(S2);
    }, { keepLocked: true });
  };
  G.STORY.ch1.marks = ['ch1_calendar', 'ch1_gate', 'ch1_arrow', 'ch1_pot_hit', 'ch1_okuyasu_down', 'ch1_jotaro_call', 'ch1_enter', 'ch1_okuyasu_shot',
    'ch1_koichi_pulled', 'ch1_koichi_healed', 'ch1_wave_clear', 'ch1_egg', 'ch1_order', 'ch1_debris_fixed', 'ch1_keicho_down', 'ch1_father',
    'ch1_past', 'ch1_photo', 'ch1_spark', 'ch1_keicho_gone', 'ch1_okuyasu_join', 'ch1_tbc'];
})();
