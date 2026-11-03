// 第2章　葡萄丘高中 / 锁与表面（开发脚本 第四部/docs/第2章_开发脚本.md；地图后缀 _ch2）。整章流程：
//   节拍 1 篇章卡 → 日历地图（「康一家」「葡萄丘高中」）→ 2 插入：电话里的声音 → 3 自行车和纸袋（锁）→ 4 拆穿骗局
//   → 5 康一家（回音孵化）→ 第 3 战「锁」→ 收尾（剪影、相信我）→ 玉美投降 → 6 第二天校门（照片）
//   → 7 学校自由走动（康一 U 听储物柜）→ 8 木偶 → 第 4 战段 A → 9 公用电话、亿泰离队、长发女生
//   → 10 商店街（康一 U 引开女学生）→ 老酒铺门口 → 第 4 战段 B → 道口（康一 U 假警报）→ 酒店门口段 C「抗拒」
//   → 11 飙车族、救护车、承太郎、电线上的小影子 → To Be Continued
//   克制（第三部 D10 + 设计文档 4.6）：纸袋里是黑墨水和布偶猫；玉美自伤嫁祸只给剪影 + 旁白（在 p4_ch2_fights.js 的收尾里）；
//   康一妈妈只挂锁、哭；仗助拿笔刺自己只给黑屏和声音；表面的手是木头；美工刀只是喜剧化的小刀片，比划不出血；
//   间田住院只用一句旁白带过。战斗和战斗里的演出在 story/p4_ch2_fights.js（G.P4CH2）。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const R = () => G.P4CH2;
  const F = () => G.flags;
  const now = () => (G.clk ? G.clk.world : 0);
  const NAME_TOP = 100;          // 名牌、替身卡、地点卡的 UI y：对白框在上面，卡片放在它正下方（同序章）
  const pool = (cid) => G.party._actor(cid);
  // 队伍池里的那个人摆到地图上当 NPC（以后入队还是同一个 Actor：不会出现两个康一）
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
  // 跟着某人走的道具（钱包、照片、笔、美工刀片）：换图 / 道具删掉 / o.until() 为真就停
  function stick(prop, a, dx, dz, o = {}) {
    if (!prop) return;
    T().tick(() => {
      if (!prop || prop.remove || !a || a.remove || (o.until && o.until())) return true;
      prop.x = a.x + dx * (a.facing || 1); prop.y = a.y + 0.5; prop.z = (a.z || 0) + dz;
      prop.visible = a.visible !== false;
      return false;
    });
  }
  const free = (S) => { G.world.free = true; void S; };
  // 自由走动里按过 U 的替身还浮在身边：过场开始前都收回去
  const recallAll = () => { for (const m of G.party.members) if (m.stand) m.stand.recall(); };

  // ================================================================ 地图（背景元数据里有 w、walk、anchors；这里只写墙和开关层）
  const { base, walls } = G.p4Stage;
  const ST = G.STAGES;
  // 节拍 1：日历地图（只是让世界有个地方站）
  ST.map_ch2 = base('map_ch2', 'morioh_map', 320, { yMin: 160, yMax: 170, music: null, obstacles: [] });
  // 节拍 2：酒店外景，傍晚（pm 罩色）。只闻其声
  ST.hotelphone_ch2 = base('hotelphone_ch2', 'morioh_grand_hotel', 480, { music: 'tension', state: { pm: 1.4 } });
  // 节拍 3–4：上学路，早上
  ST.road_ch2 = base('road_ch2', 'morioh_road', 960, { state: { pm: 0 } });
  // 节拍 5、第 3 战：康一家客厅（可走 x 52–312；state.door 1 = 左边的门开着）
  ST.home_ch2 = base('home_ch2', 'hirose_living', 320, { music: 'tension', state: { door: 0 }, obstacles: walls(52, 312, 320) });
  // 节拍 6：第二天的校门
  ST.gate_ch2 = base('gate_ch2', 'budou_gate', 640);
  // 节拍 7–9、第 4 战段 A：学校走廊（state.locker 1 = 间田的柜子开着）
  ST.school_ch2 = base('school_ch2', 'budogaoka_hall', 640, { state: { locker: 0 } });
  // 第 4 战段 B：商店街，傍晚（pm 罩色慢慢变浓）
  ST.arcade_ch2 = base('arcade_ch2', 'morioh_shopping_street', 960, { music: 'tension', state: { pm: 1 } });
  // 段 B 结尾、节拍 11 的电线：铁路道口（gate 栏杆 / alarm 红灯这一章都不开：「当当当当」只有声音）
  ST.crossing_ch2 = base('crossing_ch2', 'rail_crossing', 320, { music: 'tension', state: { gate: 0, alarm: 0, pm: 1 } });
  // 段 C、节拍 11：杜王大酒店门口 + 街角咖啡馆
  ST.hotel_ch2 = base('hotel_ch2', 'morioh_grand_hotel', 480, { music: 'tension', state: { pm: 1.2 } });

  // 对话框上的短名
  Object.assign(G.NAMES, {
    okuyasu: '亿泰', thehand: '轰炸空间', echoes1: '回音', tamami: '玉美', thelock: '锁', hazamada: '间田', surface: '表面',
    surface_doll: '表面', hirose_mom: '康一妈妈', ayana: '绫那', biker_a: '飙车族A', biker_b: '飙车族B', classmate: '同学',
  });

  // 日历地图：这一章的两枚图钉（序章的两枚自动变灰）。康一家在住宅区南边那条路下面的房子上（morioh_map 320×180 的坐标）
  P4().CAL.ch2 = { pins: [{ at: 'hirose_home', label: '康一家' }, { at: 'school', label: '葡萄丘高中' }], stamp: 'stamp' };
  if (G.D && G.D.bg && G.D.bg.morioh_map) {
    const an = (G.D.bg.morioh_map.anchors = G.D.bg.morioh_map.anchors || {});
    if (!an.hirose_home) an.hirose_home = [150, 150];
  }

  // ================================================================ 节拍 1 篇章卡 → 日历地图
  async function beatCalendar(S) {
    S.player.visible = false;
    await S.setStage('map_ch2', { x: 160, y: 165, music: null });
    const cal = await P4().calendar(S, 'ch2', { hold: 1.8 });
    S.mark('ch2_calendar');
    await S.fadeOut(0.45);
    if (cal) cal.close();
  }

  // ================================================================ 节拍 2 插入：电话（酒店外景，傍晚）。只闻其声，不出现说话的人
  const PHONE_WIN = [110, 32];   // 酒店高处一扇窗（远景层 k 0.5，镜头停在 0 才对得上）
  async function beatPhone(S) {
    const p = S.player;
    await S.setStage('hotelphone_ch2', { x: 160, y: 160, music: 'tension', fade: false });
    p.visible = false;
    snapTo({ x: 160 });
    await S.fadeIn(0.6);
    await S.zoom(2.2, PHONE_WIN[0], PHONE_WIN[1] + 14, 1.2);
    S.fx('glint', { x: PHONE_WIN[0], y: PHONE_WIN[1], size: 6 }, { life: 0.5 });
    // 电话铃（两下），接起来是一阵电流杂音
    S.sfx('ding', 0.6, 1.5); G.defer(0.18, () => S.sfx('ding', 0.6, 1.5));
    await S.wait(0.9);
    S.sfx('ding', 0.6, 1.5); G.defer(0.18, () => S.sfx('ding', 0.6, 1.5));
    await S.wait(0.9);
    S.sfx('card_flip', 0.5);
    for (let i = 0; i < 4; i++) G.defer(i * 0.09, () => S.sfx('blip', 0.35, 0.55 + i * 0.1));
    S.mark('ch2_phone');
    await S.say('phone_voice', '空条承太郎……离开杜王町。', { name: '电话里的声音' });
    await S.say('phone_voice', '这里没有你要找的东西。再不走，下一个就是你。', { name: '电话里的声音' });
    await S.say('jotaro4', '……你是谁？', { name: '承太郎' });
    // 杂音变大，啪的一声断线，窗里的灯闪了一下
    for (let i = 0; i < 7; i++) G.defer(i * 0.07, () => S.sfx('blip', 0.5, 0.5 + Math.random() * 0.6));
    S.shake(1, 0.4);
    await S.wait(0.55);
    S.sfx('clang', 0.6, 1.6);
    S.flash(0.12, 0.45, '#ffe9a8');
    S.fx('glint', { x: PHONE_WIN[0], y: PHONE_WIN[1], size: 10 }, { life: 0.4 });
    await S.wait(0.6);
    await S.say('jotaro4', '电线里……有什么东西。', { name: '承太郎' });
    await S.fadeOut(0.6);
    await S.zoom(1, null, null, 0);
    focus(null);
  }

  // ================================================================ 节拍 3 上学路（早上）：自行车和纸袋
  const BAG = [312, 161];
  async function beatBike(S) {
    const p = S.player;
    await S.setStage('road_ch2', { x: 940, y: 158, facing: -1, music: 'daily', fade: false });
    S.state('pm', 0);
    p.visible = false;              // 仗助节拍 4 才和亿泰一起走进来
    const bag = T().prop(S, 'paper_bag', BAG[0], BAG[1], { id: 'bag', frame: 0 });
    const bike = S.spawn('koichi_bike', 70, 160, { id: 'koichi_bike', facing: 1, name: '康一' });
    snapTo({ x: 200 });
    await S.fadeIn(0.6);
    S.location('morioh', { y: NAME_TOP });
    focus(bike);
    S.walk(bike, 228, 160, { speed: 38, anim: 'ride' }).catch(G.cancelIgnore);
    await S.narrate('上高中以后，我终于买了新自行车。', { pos: 'top' });
    S.sfx('ding', 0.5, 1.8);
    await S.narrate('……那天早上，我心情好极了。', { pos: 'top' });
    await S.until(() => !bike.script);
    // 压过路中间的纸袋：「喵——！」，纸袋底下渗出一摊黑色的液体
    await S.walk(bike, BAG[0] + 4, 160, { speed: 46, anim: 'ride' });
    if (bag) T().setFrame(bag, 1);
    S.sfx('thud', 0.7); S.sfx('sting_shock', 0.7);
    S.sfxText('喵——！', { wx: BAG[0], wy: BAG[1], wz: 18 }, { dur: 1.0 });
    S.shake(2, 0.2);
    const ink = T().prop(S, 'ink', BAG[0] + 2, BAG[1] + 0.2, { id: 'ink', frame: 0 });
    S.mark('ch2_bike');
    for (let i = 1; i < 3; i++) { await S.wait(0.25); if (ink) T().setFrame(ink, i); }
    // 康一跳下车，自行车倒在一边
    bike.remove = true;
    const parked = T().prop(S, 'bike_koichi', BAG[0] + 22, 162, { id: 'bike_parked', frame: 1 });
    void parked;
    const ko = place(S, 'koichi', BAG[0] - 12, 162, 1);
    focus({ x: 360 });
    S.sfx('crash', 0.4);
    await S.say('koichi', '诶？！纸袋里……有猫？！', { expr: 'shock' });
    // 玉美从公交站牌后面跳出来
    const tm = S.spawn('tamami', 430, 148, { id: 'tamami', facing: -1, name: '小林玉美' });
    S.sfx('whoosh', 0.7);
    await S.arc(tm, BAG[0] + 34, 159, 14, 0.4, { anim: 'run' });
    tm.play('idle');
    S.face(tm, ko);
    await S.say('tamami', '啊啊啊！我的小咪！你这家伙，把我家的猫压死了！', { expr: 'rage' });
    await S.say('tamami', '这可是名种猫。赔钱，五十万日元，一分都不能少！', { expr: 'rage' });
    await S.say('koichi', '五、五十万？！对不起，我真的没看见……', { expr: 'shock' });
    // 咔嚓：康一胸口挂上一把锁
    R().hangLock(S, ko, 'lock_s');
    S.mark('ch2_lock_koichi');
    S.pose(ko, 'bow');
    await S.wait(0.5);
    S.nameCard('tamami', { y: NAME_TOP });
    S.standCard('thelock', { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.wait(1.0);
    await S.narrate('好重……胸口像压了一块石头。我真的……做了很过分的事。', { pos: 'top' });
    await S.say('tamami', '明天放学前把钱准备好。你家住哪我可是知道的哦～', { expr: 'smile' });
  }

  // ================================================================ 节拍 4 拆穿骗局：亿泰被挂锁、布偶猫、疯狂钻石修好“断了”的胳膊
  async function beatScam(S) {
    const p = S.player, ko = S.actor('koichi'), tm = S.actor('tamami');
    // 仗助和亿泰从右边走过来
    Object.assign(p, { x: 600, y: 156, facing: -1, visible: true });
    const ok = place(S, 'okuyasu', 626, 162, -1);
    S.walk(ok, BAG[0] + 96, 162, { speed: 54 }).catch(G.cancelIgnore);
    await S.walk(p, BAG[0] + 74, 156, { speed: 54 });
    await S.until(() => !ok.script);
    S.face(ko, 1);
    await S.say('josuke', '早啊康一。……你脸色怎么这么差？');
    await S.say('okuyasu', '那个大叔是谁？看着就不像好人。');
    await S.say('koichi', '仗助君，我压死了他的猫……', { expr: 'shock' });
    await S.say('okuyasu', '什么猫，我看他是在讹人！', { expr: 'rage' });
    // 亿泰一把揪住玉美的领子 → 玉美顺势倒在地上抱着胳膊
    await S.walk(ok, tm.x + 16, tm.y + 1, { speed: 70 });
    S.face(ok, tm);
    ok.play('point');
    S.sfx('whoosh', 0.6);
    await S.wait(0.25);
    S.face(tm, ok);
    await S.arc(tm, tm.x - 10, tm.y + 2, 6, 0.3, { anim: 'hurt' });
    S.pose(tm, 'fall');
    S.sfx('thud', 0.7);
    ok.play('idle');
    await S.say('tamami', '哎哟！打人了！高中生打人了！我的胳膊断了！', { expr: 'shock' });
    S.pose(ok, 'shock');
    await S.say('okuyasu', '诶？我、我就碰了一下……', { expr: 'shock' });
    R().hangLock(S, ok, 'lock_s');
    await S.wait(0.6);
    S.unpose(ok);
    await S.say('okuyasu', '……完了，我是不是下手太重了。', { expr: 'shock' });
    // 仗助蹲下翻开纸袋：拎出一只湿漉漉的布偶猫
    await S.walk(p, BAG[0] + 10, BAG[1] + 1, { speed: 50 });
    S.face(p, -1);
    S.pose(p, 'sit');
    S.sfx('pop', 0.6);
    const cat = T().prop(S, 'toy_cat', BAG[0], BAG[1] + 0.3, { id: 'toy_cat', z: 2 });
    if (cat) await S.arc(cat, p.x - 6, p.y + 0.5, 16, 0.4, { z1: 16 });
    await S.say('josuke', '……喂。这只猫是布做的。');
    S.unpose(p);
    if (cat) stick(cat, p, -6, 16);
    S.mark('ch2_scam_broken');
    await S.say('josuke', '黑水是墨水。还有大叔，你的胳膊——');
    S.face(p, tm);
    await S.summon(p, { dur: 0.12, rise: 4 });
    S.standAct(p, 'reach', { dx: 18, z: 4, dur: 0.8 });
    P4().fixGlow(S, tm.x, tm.y - 8);
    await S.wait(0.6);
    S.recall(p);
    await S.say('josuke', '修好了。根本没断吧？', { expr: 'smile' });
    // 两把锁「咔」地松开、消失
    S.sfx('clang', 0.5, 1.4);
    await Promise.all([R().breakLock(S, ko), R().breakLock(S, ok)]);
    S.unpose(ko);
    S.unpose(tm);
    await S.say('tamami', '锁、锁怎么没了……', { expr: 'shock' });
    // 抓起掉在地上的康一的钱包就跑
    const wl = T().prop(S, 'wallet', BAG[0] - 20, 165, { id: 'wallet' });
    await S.walk(tm, BAG[0] - 18, 164, { speed: 90, anim: 'run' });
    S.sfx('pop', 0.6);
    if (wl) stick(wl, tm, 6, 14);
    await S.say('tamami', '这个就当精神损失费！', { expr: 'smile' });
    S.walk(tm, -60, 168, { speed: 130, anim: 'run' }).then(() => { tm.remove = true; if (wl) wl.remove = true; }, G.cancelIgnore);
    await S.wait(0.4);
    S.face(ko, -1);
    await S.say('koichi', '啊！我的钱包！里面有七千日元！', { expr: 'shock' });
    await S.say('josuke', '……追不上了。下次再见到他，让他连本带利吐出来。', { expr: 'rage' });
    await S.narrate('那时我以为事情就这样过去了。', { pos: 'top' });
    await S.fadeOut(0.6);
    if (cat) cat.remove = true;
    focus(null);
  }

  // ================================================================ 节拍 5 康一家（下午 4 点 07 分）：两把锁、回音孵化
  const HOME = { sofa: 164 };
  async function beatHome(S) {
    // 这一段只有康一（仗助、亿泰不在）
    S.party(['koichi'], { leader: 'koichi' });
    await S.setStage('home_ch2', { x: 30, y: 154, facing: 1, music: 'tension', fade: false });
    S.state('door', 1);
    const ko = S.player;
    ko.visible = true;
    const mom = S.spawn('hirose_mom', HOME.sofa, 150, { id: 'hirose_mom', facing: -1 });
    const tm = S.spawn('tamami', HOME.sofa + 20, 148, { id: 'tamami', facing: -1, name: '小林玉美' });
    snapTo({ x: 160 });
    await S.fadeIn(0.6);
    S.location('hirose', { y: NAME_TOP });
    tm.play('bow');
    await S.walk(ko, 74, 156, { speed: 50 });
    S.state('door', 0); S.sfx('door', 0.6);
    S.mark('ch2_home');
    await S.narrate('下午 4 点 07 分。', { pos: 'top' });
    await S.say('koichi', '我回来了——');
    await S.say('tamami', '啊，康一君回来啦。', { expr: 'smile' });
    tm.play('idle');
    await S.say('koichi', '你、你怎么会在我家？！', { expr: 'shock' });
    await S.say('tamami', '今天早上捡到你的钱包，特地送过来嘛。', { expr: 'smile' });
    await S.say('tamami', '不过啊，钱包好像被掉包了。我原来那个钱包里，可是装着五十万日元呢。', { expr: 'smile' });
    S.face(mom, ko);
    await S.say('hirose_mom', '康一，这是真的吗？你拿了人家的钱？', { expr: 'shock' });
    // 绫那从门口探出头
    S.state('door', 1); S.sfx('door', 0.5);
    const aya = S.spawn('ayana', 22, 160, { id: 'ayana', facing: 1 });
    await S.walk(aya, 46, 160, { speed: 50 });
    await S.say('ayana', '康一偷东西了？！', { expr: 'shock' });
    // 咔嚓、咔嚓：妈妈和姐姐胸口都挂上锁，比康一早上那把还大
    R().hangLock(S, mom, 'lock_m', { dz: 2 });
    await S.wait(0.35);
    R().hangLock(S, aya, 'lock_m');
    mom.play('cry'); aya.play('cry');
    await S.wait(0.6);
    ko.play('cmd');
    await S.say('koichi', '别……别把她们扯进来！', { expr: 'rage' });
    // 康一把妈妈和姐姐推出门外，关上门
    await S.walk(mom, 58, 152, { speed: 60 });
    S.face(ko, -1);
    S.walk(aya, 8, 162, { speed: 60 }).catch(G.cancelIgnore);
    await S.walk(mom, 10, 152, { speed: 60 });
    mom.remove = true; aya.remove = true;
    S.state('door', 0); S.sfx('door', 0.9);
    S.shake(1, 0.15);
    await S.walk(ko, 112, 160, { speed: 50 });
    S.face(ko, 1); S.face(tm, ko);
    await S.say('tamami', '哎呀，这下你家的人都要被罪恶感压垮了哦。', { expr: 'smile' });
    await S.narrate('我从来没有这么生气过。', { pos: 'top' });
    // 书包里那颗蛋发出声音，裂开一道缝 → 绿色的小东西钻出来，尾巴上挂着一个「咚！」字
    S.music(null);
    S.sfx('heartbeat', 0.8);
    const egg = T().prop(S, 'echoes_egg', ko.x - 6, ko.y + 0.5, { id: 'egg', frame: 0, z: 14 });
    if (egg) await S.arc(egg, ko.x + 18, ko.y + 0.5, 10, 0.4, { z1: 0 });
    for (let i = 1; i <= 3; i++) {
      await S.wait(0.4);
      if (egg) T().setFrame(egg, i);
      S.sfx('glass_break', 0.35, 1.6 + i * 0.1); S.shake(1, 0.12);
    }
    await S.summon(ko, { dur: 0.1, rise: 2 });
    S.standAct(ko, 'hatch', { dx: 18, z: 0, dur: 1.1 });
    if (egg) egg.remove = true;
    S.flash(0.15, 0.5, '#d8ffb0');
    S.sfx('sparkle', 0.9);
    await S.wait(0.8);
    S.standAct(ko, 'shoot', { dx: 14, z: 12, dur: 0.6 });
    S.sfx('whoosh', 0.6, 1.4);
    await S.wait(0.2);
    S.sfx('punch', 0.8);
    S.sfxText('咚！', tm, { dur: 1.0 });
    tm.play('cover_ears');
    S.shake(2, 0.2);
    S.mark('ch2_hatch');
    S.nameCard('koichi', { y: NAME_TOP });
    S.standCard('echoes1', { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.wait(1.2);
    tm.play('idle');
    await S.say('tamami', '替、替身？！你这个小不点也有？！', { expr: 'shock' });
    S.music('battle', 0.3);
    await S.vs({ key: 'thelock', hero: 'koichi', enemy: { cid: 'tamami', anim: 'idle' } });
    G.uifx.vsTag('thelock');
  }

  // ================================================================ 第 3 战收尾以后：玉美投降
  async function beatMinion(S) {
    const ko = S.player, tm = S.actor('tamami'), mom = S.actor('hirose_mom'), aya = S.actor('ayana');
    S.music('victory', 0.6);
    if (tm) { S.face(tm, ko); S.pose(tm, 'kneel'); }
    await S.say('tamami', '我认输！我小林玉美以后就是康一大哥的小弟！', { expr: 'shock' });
    await S.say('koichi', '谁要你当小弟啊！', { expr: 'shock' });
    S.mark('ch2_minion');
    if (mom) { S.face(mom, ko); mom.play('idle'); }
    if (aya) aya.play('cheer');
    await S.say('hirose_mom', '康一……刚才是妈妈不好。', { expr: 'smile' });
    await S.fadeOut(0.7);
  }

  // ================================================================ 节拍 6 第二天（校门）：玉美当跟班、间田的照片
  async function beatGate(S) {
    S.party(['josuke', 'okuyasu', 'koichi'], { leader: 'josuke' });
    await S.setStage('gate_ch2', { x: 300, y: 156, facing: -1, music: 'daily', fade: false });
    const p = S.player, ok = S.actor('okuyasu'), ko = S.actor('koichi');
    Object.assign(ok, { x: 326, y: 162, facing: -1, follow: null });
    Object.assign(ko, { x: -10, y: 160, facing: 1, follow: null });
    const tm = S.spawn('tamami', -34, 156, { id: 'tamami', facing: 1, name: '玉美' });
    snapTo({ x: 240 });
    await S.narrate('第二天。', { onBlack: true, auto: 1.4 });
    await S.fadeIn(0.6);
    S.walk(tm, 222, 156, { speed: 44 }).catch(G.cancelIgnore);
    await S.walk(ko, 246, 160, { speed: 44 });
    await S.until(() => !tm.script);
    S.mark('ch2_gate');
    tm.play('bow');
    await S.say('tamami', '康一大哥，书包我来拿！', { expr: 'smile' });
    tm.play('idle');
    await S.say('josuke', '……昨天发生了什么？', { expr: 'shock' });
    await S.say('okuyasu', '那个讹人的大叔怎么变成跟班了？', { expr: 'shock' });
    await S.say('koichi', '说来话长……');
    await S.say('tamami', '对了大哥，给你一个情报。');
    // 掏出一张照片：一个瘦瘦的三年级生
    const ph = T().prop(S, 'photo_hz', tm.x + 6, tm.y + 0.5, { id: 'photo_hz', z: 14 });
    if (ph) {
      S.sfx('card_flip', 0.6);
      await S.arc(ph, tm.x + 8, tm.y + 0.5, 6, 0.3, { z1: 24 });
      await S.zoom(3.2, ph.x, ph.y - 26, 0.3);
    }
    S.mark('ch2_photo');
    await S.say('tamami', '三年级的间田敏和，也是替身使者。我亲眼见过他的木偶自己会动。');
    await S.zoom(1, null, null, 0.25);
    if (ph) ph.remove = true;
    await S.say('josuke', '木偶？');
    await S.say('tamami', '他跟谁都合不来，最近好像在打听你们的事。小心点。');
    await S.narrate('替身使者……原来这个小镇上，还有这么多吗？', { pos: 'top' });
    await S.fadeOut(0.5);
    focus(null);
  }

  // ================================================================ 节拍 7 学校自由走动：康一 U 听储物柜（Q 换队长）
  const HALL = { lockers: 133, hzLocker: 147, board: 271, hydrant: 314, window: 468, seat: [507, 74], stairs: 628, phone: [338, 145] };
  function checked(id) {
    const c = (F().checked = F().checked || {});
    if (!c[id]) { c[id] = true; F().checks = (F().checks || 0) + 1; }
  }
  async function useBoard(S) {
    checked('board');
    await S.say(null, '新生欢迎会、漫画社招新……还有一张“寻找走失的猫”。');
    await S.say('koichi', '……猫的事就别提了。', { expr: 'shock' });
  }
  async function useWindow(S) {
    checked('window');
    await S.say(null, '3-A 的教室。靠窗那张桌子空着。');
    await S.say('classmate', '间田？他好几天没来上课了。', { name: '3-A 的学长' });
  }
  async function useLockers(S) {
    checked('lockers');
    await S.say(null, '一排储物柜。……都锁着。');
    if (!F().listened) S.hint('按 Q 换成康一，对着储物柜按 U：听听里面', 5);
  }
  async function lookLockers(S, h, p) {
    if (p.cid === 'okuyasu') {
      checked('erase');
      await S.say('okuyasu', '我削开不就完了？');
      await S.say('koichi', '不行！那是学校的柜子！', { expr: 'shock' });
      return;
    }
    if (F().listened) { await S.say('koichi', '……左数第七个。还在动。'); return; }
    // 回音的尾巴贴到柜门上：「……咔哒、咔哒。」
    checked('lockers');
    S.sfxText('咔哒', { wx: HALL.hzLocker, wy: 146, wz: 40 }, { dur: 0.8 });
    S.sfx('doll_scurry', 0.6);
    await S.wait(0.5);
    S.sfxText('咔哒', { wx: HALL.hzLocker + 4, wy: 146, wz: 46 }, { dur: 0.8 });
    S.sfx('doll_scurry', 0.5);
    await S.wait(0.4);
    await S.say(null, '……咔哒、咔哒。');
    await S.say('koichi', '左数第七个柜子里……有东西在动。', { expr: 'shock' });
    F().listened = true;
    S.mark('ch2_listen');
    S.fx('glint', { x: HALL.hzLocker, y: 104, size: 8 }, { life: 0.6 });
  }
  async function useHzLocker(S) {
    checked('hz_locker');
    if (!F().listened) { await S.say(null, '左数第七个柜子。……锁着。'); return; }
    F().lockerOpen = true;
  }
  async function lookHydrant(S) {
    checked('hydrant');
    await S.say('josuke', '……这个本来就是好的。');
  }
  async function talkTamamiSchool(S, me) {
    checked('tamami');
    if (F().listened) { await T().say(S, me, '大哥，就是那个柜子！我在这儿给您望风！', { expr: 'smile' }); return; }
    await T().say(S, me, '大哥，间田的柜子在左边那排，左数第七个。', { expr: 'smile' });
  }
  async function talkClassA(S, me) {
    checked('cls_a');
    await T().say(S, me, '仗助君，那个总跟着康一的大叔是谁？');
  }
  async function talkClassB(S, me) {
    checked('cls_b');
    await T().say(S, me, '三年级的间田学长？听说他总是一个人在教室里玩木偶。');
  }
  function setupSchool(S) {
    const st = G.world.stage;
    S.spawn('tamami', 214, 162, { id: 'tamami', facing: -1, name: '玉美', label: '玉美', talk: talkTamamiSchool });
    S.spawn('fan_a', 410, 150, { id: 'cls_a', facing: -1, name: '同学', label: '同学', talk: talkClassA });
    S.spawn('fan_b', 432, 162, { id: 'cls_b', facing: -1, name: '同学', label: '同学', talk: talkClassB });
    st.hotspots.push(
      { id: 'board', x: HALL.board, y: 150, r: 18, label: '告示板', use: useBoard },
      { id: 'window', x: HALL.window, y: 150, r: 22, label: '3-A 的窗', use: useWindow },
      { id: 'lockers', x: HALL.lockers - 12, y: 150, r: 14, label: '储物柜', use: useLockers },
      { id: 'lockers_look', x: HALL.lockers, y: 150, r: 22, lx: HALL.lockers, ly: 110, label: '储物柜', tags: ['listen', 'erase', 'pull'], look: lookLockers },
      { id: 'hz_locker', x: HALL.hzLocker, y: 150, r: 10, label: '左数第七个柜子', use: useHzLocker },
      { id: 'hydrant', x: HALL.hydrant, y: 150, r: 16, label: '消火栓', tags: ['fix'], fx: HALL.hydrant, fy: 112, look: lookHydrant,
        use: async (S2) => { checked('hydrant'); await S2.say(null, '红色的消火栓箱。'); } },
    );
    T().memberTalk({
      koichi: async (S2) => { await S2.say('koichi', '间田学长……为什么要打听我们？'); },
      okuyasu: async (S2) => { await S2.say('okuyasu', '学校的走廊真长啊。我老是走错教室。'); },
    });
    const t0 = now();
    // 调查过 3 处或者 60 s 以后，箭头指向储物柜；听过以后指向间田的柜子
    T().goal(S, { x: HALL.lockers, y: 150, label: '储物柜', when: () => (F().checks || 0) >= 3 || now() - t0 > 60, done: () => !!F().listened,
      every: 15, text: '储物柜那边好像有声音：按 Q 换成康一，走过去按 U' });
    T().goal(S, { x: HALL.hzLocker, y: 150, label: '间田的柜子', when: () => !!F().listened, done: () => !!F().lockerOpen,
      every: 15, text: '间田的柜子（左数第七个）：走过去按 E' });
  }
  async function schoolIn(S) {
    await S.setStage('school_ch2', { x: 44, y: 158, facing: 1, music: 'daily' });
    S.state('locker', 0);
    S.mark('ch2_school');
    S.hint('按 Q 换队长：康一的 U 能听见墙后的声音　E 调查', 8);
  }

  // ================================================================ 节拍 8 储物柜里的木偶 → 第 4 战段 A
  async function beatDoll(S) {
    T().memberTalk({});
    S.hint(null);
    recallAll();
    if (S.player.cid !== 'josuke') G.party.setLeader('josuke', { force: true, silent: true });
    const p = S.player, ko = S.actor('koichi'), ok = S.actor('okuyasu'), tm = S.actor('tamami');
    for (const a of [ko, ok]) if (a) { a.follow = null; a.hold = false; a.script = null; }
    if (tm) tm.talk = null;
    focus({ x: 230 });
    S.walk(ok, 118, 160, { speed: 70 }).catch(G.cancelIgnore);
    S.walk(ko, 150, 162, { speed: 70 }).catch(G.cancelIgnore);
    await S.walk(p, 172, 156, { speed: 70 });
    await S.until(() => !ok.script && !ko.script);
    S.face(p, -1); S.face(ko, 1); S.face(ok, 1);
    // 柜门弹开，一只木偶扑出来扒在仗助脸上
    S.state('locker', 1);
    S.sfx('door', 0.8); S.sfx('creak', 0.6);
    const doll = S.spawn('surface_doll', HALL.hzLocker, 147, { id: 'surface_doll', facing: 1, name: '表面' });
    doll.z = 34;
    S.sfx('doll_scurry', 0.8);
    await S.arc(doll, p.x - 3, p.y + 0.5, 10, 0.35, { anim: 'jump', z1: 26 });
    doll.hold = true; doll.z = 26;
    S.mark('ch2_doll');
    S.pose(p, 'shock');
    S.shake(2, 0.2);
    await S.say('josuke', '什么东西——', { expr: 'shock' });
    // 仗助把它甩开，它落在右边 → 一碰到仗助就变形：木头的纹路褪掉，变成第二个仗助
    S.sfx('whoosh', 0.8);
    await S.arc(doll, 252, 158, 22, 0.45, { anim: 'jump', z1: 0 });
    S.unpose(p);
    S.face(p, 1);
    S.sfx('doll_voice', 0.7);
    S.fx('burst', { x: 252, y: 140, n: 12, speed: 34, colours: ['#c89a5a', '#8a5a2a', '#e8c890'], gravity: 120, life: 0.7 });
    S.flash(0.12, 0.5, '#e8c890');
    const sf = S.spawn('surface', 252, 158, { id: 'surface', facing: -1, name: '表面' });
    doll.remove = true;
    await S.wait(0.3);
    S.standCard('surface', { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.wait(0.9);
    sf.play('pose');
    await S.say('surface', 'Great～我也是东方仗助哦。', { expr: 'smile' });
    sf.play('idle');
    // 间田从走廊尽头走出来
    if (tm) S.walk(tm, 700, 164, { speed: 110, anim: 'run' }).then(() => { tm.remove = true; }, G.cancelIgnore);
    const hz = S.spawn('hazamada', 660, 146, { id: 'hazamada', facing: -1, name: '间田敏和' });
    focus({ x: 330 });
    await S.walk(hz, 452, 143, { speed: 46 });
    hz.play('smirk');
    await S.say('hazamada', '表面碰到谁，就能变成谁。', { expr: 'smile' });
    S.nameCard('hazamada', { y: NAME_TOP });
    await S.wait(0.6);
    await S.say('hazamada', '而且它面对着你的时候，你就只能照它的样子动。', { expr: 'smile' });
    // 示范：表面挥手，仗助也照着挥手——一胳膊把旁边的康一扫倒
    S.face(sf, p);
    sf.play('point');
    p.hold = true; p.play('point');
    S.face(p, -1);
    S.sfx('punch', 0.8); S.shake(2, 0.2);
    S.sfxText('咚', ko, { dur: 0.6 });
    ko.flash = 1;
    await S.arc(ko, 112, 162, 8, 0.35, { anim: 'hurt' });
    S.pose(ko, 'down');
    S.sfx('thud', 0.7);
    await S.wait(0.3);
    sf.play('idle'); p.hold = false; p.play('idle');
    S.face(p, ko);
    await S.say('josuke', '（身体……自己动了？！）康一！', { expr: 'shock' });
    S.face(ok, sf);
    await S.say('okuyasu', '装神弄鬼的，我来——', { expr: 'rage' });
    await S.say('hazamada', '轮不到你。', { expr: 'smile' });
    // 亿泰被同学们围住问东问西，挤不进来
    const ca = S.actor('cls_a'), cb = S.actor('cls_b');
    if (ca) { ca.talk = null; S.walk(ca, 96, 156, { speed: 120 }).catch(G.cancelIgnore); }
    if (cb) { cb.talk = null; S.walk(cb, 70, 166, { speed: 120 }).catch(G.cancelIgnore); }
    await S.walk(ok, 80, 160, { speed: 80 });
    if (ca) await S.until(() => !ca.script);
    if (ca) { S.face(ca, ok); ca.play('cheer'); S.emote(ca, '亿泰君！那是什么魔术？', 1.8); }
    if (cb) { S.face(cb, ok); S.emote(cb, '再变一个！', 1.8); }
    S.pose(ok, 'shock');
    await S.say('okuyasu', '让、让开！我不是变魔术的！', { expr: 'shock' });
    // 站到开打的位置：仗助在走廊中间，表面在他右边
    S.walk(sf, 384, 158, { speed: 60 }).catch(G.cancelIgnore);
    await S.walk(p, 300, 158, { speed: 60 });
    await S.until(() => !sf.script);
    S.face(p, 1); S.face(sf, -1);
    S.music('battle', 0.3);
    await S.vs({ key: 'surface', hero: 'josuke', enemy: { cid: 'hazamada', anim: 'smirk' } });
    G.uifx.vsTag('surface');
  }

  // ================================================================ 段 A 以后：间田带着表面走掉 → 节拍 9 公用电话、亿泰离队、长发女生
  async function afterSegA(S) {
    const pen = S.actor('ch2_pen');
    if (pen) pen.remove = true;
    G.party.setLeader('josuke', { force: true, silent: true });
    recallAll();
    const p = S.player, ko = S.actor('koichi'), ok = S.actor('okuyasu'), sf = S.actor('surface'), hz = S.actor('hazamada');
    S.unpose(p);
    if (ko) { S.unpose(ko); ko.follow = null; }
    if (sf) { sf.team = 'npc'; sf.brain = null; sf.atk = null; sf.tele = null; sf.state = 'idle'; sf.hold = false; sf.play('idle'); }
    if (hz) { hz.play('smirk'); S.face(hz, p); }
    S.music('tension', 0.6);
    await S.say('hazamada', '承太郎那家伙，就交给‘仗助’去收拾吧。', { expr: 'smile' });
    if (hz) S.walk(hz, 700, 146, { speed: 70 }).then(() => { hz.remove = true; }, G.cancelIgnore);
    if (sf) { S.face(sf, 1); await S.walk(sf, 700, 152, { speed: 70 }); sf.remove = true; }
    if (hz) await S.until(() => hz.remove || !hz.script);
    // 亿泰挤出来，同学们散开
    for (const id of ['cls_a', 'cls_b']) { const c = S.actor(id); if (c) S.walk(c, id === 'cls_a' ? 40 : 20, 150, { speed: 70 }).then(() => { c.remove = true; }, G.cancelIgnore); }
    if (ok) { S.unpose(ok); S.walk(ok, 250, 162, { speed: 80 }).catch(G.cancelIgnore); }
    if (ko) await S.walk(ko, 270, 162, { speed: 60 });
    S.face(ko, 1);
    await S.say('koichi', '他要带着假仗助去找承太郎先生！', { expr: 'shock' });
    // 走廊的公用电话
    const phone = T().prop(S, 'payphone', HALL.phone[0], HALL.phone[1], { id: 'payphone' });
    void phone;
    focus({ x: 320 });
    await S.walk(p, HALL.phone[0] - 10, 152, { speed: 70 });
    S.face(p, 1);
    p.hold = true; p.play('point');
    S.sfx('coin', 0.6);
    await S.wait(0.3);
    for (let i = 0; i < 3; i++) G.defer(i * 0.12, () => S.sfx('blip', 0.4, 1.2));
    await S.wait(0.5);
    S.mark('ch2_call');
    await S.say('josuke', '……喂，杜王大酒店吗？我找空条承太郎。');
    await S.say('hotel_front', '空条先生刚出门了。说是东方仗助先生约他在附近的咖啡馆见面。', { name: '酒店前台' });
    p.hold = false; p.play('idle');
    S.face(p, -1);
    await S.say('josuke', '我才没约！', { expr: 'rage' });
    if (ok) { await S.until(() => !ok.script); S.face(ok, 1); }
    await S.say('okuyasu', '我去车站那边堵！你们追上去！', { expr: 'rage' });
    // 亿泰退出队伍（这一章不再回来）
    S.leave('okuyasu', { drop: true, stay: true });
    if (ok) await S.walk(ok, -40, 160, { speed: 120, anim: 'run' });
    if (ok) ok.remove = true;
    // 出校门的路上：一个长发女生站在走廊拐角，看着康一的背影（第3章由花子的伏笔：不出名牌，只停 1 s）
    const yk = S.spawn('yukako_sil', 612, 144, { id: 'yukako', facing: -1, name: '？？？', alpha: 0 });
    yk.alpha = 0;
    S.walk(ko, 700, 160, { speed: 90 }).catch(G.cancelIgnore);
    focus({ x: 520 });
    await S.animate(0.4, (k) => { yk.alpha = k; });
    await S.walk(p, 700, 156, { speed: 90 });
    await S.until(() => !ko.script);
    S.emote(yk, '……', 1.2, '#ff9ab8');
    S.mark('ch2_yukako');
    await S.wait(1.0);
    await S.animate(0.4, (k) => { yk.alpha = 1 - k; });
    yk.remove = true;
    await S.fadeOut(0.5);
    focus(null);
  }

  // ================================================================ 段 B 前：商店街（康一 U 把女学生引去理发店）→ 老酒铺门口
  const ARC = { girls: [[336, 148], [348, 164], [360, 156]], barber: 300, liquor: 400, hz: [430, 146], sf: [410, 156], bikeA: [486, 147], bikeB: [528, 145],
    bkA: [470, 152], bkB: [508, 162] };
  let girlWall = null;
  async function talkGirl(S, me) {
    const lines = ['仗助君！放学一起走吧～', '仗助君，刚才你是不是从这边跑过去了？', '今天的发型也好帅！'];
    await T().say(S, me, lines[['girl1', 'girl2', 'girl3'].indexOf(me.id)] || lines[0], { expr: 'smile' });
  }
  async function girlsBlock(S) {
    F().girlsSeen = true;
    for (const id of ['girl1', 'girl2', 'girl3']) { const g = S.actor(id); if (g) { g.play('cheer'); S.face(g, S.player); } }
    await S.say('fan_a', '仗助君！放学一起走吧～', { name: '女学生', expr: 'smile' });
    await S.say('fan_b', '诶？可是仗助君刚才不是往前面去了吗？', { name: '女学生' });
    await S.say('josuke', '（那是假的我……）让一下，我赶时间！', { expr: 'shock' });
    for (const id of ['girl1', 'girl2', 'girl3']) { const g = S.actor(id); if (g) g.play('idle'); }
    S.hint('女学生把路堵住了：按 Q 换康一，对着理发店按 U', 8);
  }
  async function lookBarber(S) {
    if (F().girlsGone) { await S.say('koichi', '……她们还在里面找呢。'); return; }
    // 回音往理发店门口贴一句「仗助君在这边～」
    S.sfx('blip', 0.5, 1.3);
    S.sfxText('仗助君在这边～', { wx: ARC.barber, wy: 146, wz: 44 }, { dur: 1.8 });
    await S.wait(0.6);
    const gs = ['girl1', 'girl2', 'girl3'].map((id) => S.actor(id)).filter(Boolean);
    for (const g of gs) { g.play('cheer'); S.face(g, -1); }
    await S.say('fan_a', '诶？仗助君在理发店？！', { name: '女学生', expr: 'shock' });
    await S.say('fan_b', '他要换发型了吗？！快去看！', { name: '女学生', expr: 'smile' });
    S.mark('b04b_girls');
    await Promise.all(gs.map((g, i) => S.walk(g, ARC.barber - 6 + i * 6, 143, { speed: 100 }).then(() => S.animate(0.3, (k) => { g.alpha = 1 - k; })).then(() => { g.remove = true; }, G.cancelIgnore)));
    const st = G.world.stage;
    if (girlWall) st.obstacles = st.obstacles.filter((o) => o !== girlWall);
    girlWall = null;
    F().girlsGone = true;
    await S.say('koichi', '（……对不起了，大家。）', { expr: 'shock' });
    S.hint('路通了：往前走，追上间田！', 5);
  }
  function setupArcade(S) {
    const st = G.world.stage;
    ARC.girls.forEach(([x, y], i) => {
      S.spawn(i === 1 ? 'fan_b' : 'fan_a', x, y, { id: 'girl' + (i + 1), facing: -1, name: '女学生', label: '女学生', talk: talkGirl });
    });
    // 女学生围在前面：走不过去（她们走了才拆）
    girlWall = { x0: 322, x1: 372, y0: 0, y1: 240 };
    st.obstacles.push(girlWall);
    // 间田和表面在老酒铺门口，旁边是两个飙车族和他们的摩托
    T().prop(S, 'motorbike_a', ARC.bikeA[0], ARC.bikeA[1], { id: 'moto_a', frame: 0 });
    T().prop(S, 'motorbike_b', ARC.bikeB[0], ARC.bikeB[1], { id: 'moto_b', frame: 0 });
    S.spawn('biker_a', ARC.bkA[0], ARC.bkA[1], { id: 'biker_a', facing: -1, name: '飙车族A' });
    S.spawn('biker_b', ARC.bkB[0], ARC.bkB[1], { id: 'biker_b', facing: -1, name: '飙车族B' });
    S.spawn('hazamada', ARC.hz[0], ARC.hz[1], { id: 'hazamada', facing: 1, name: '间田' });
    S.spawn('surface', ARC.sf[0], ARC.sf[1], { id: 'surface', facing: 1, name: '表面' });
    st.hotspots.push(
      { id: 'barber', x: ARC.barber, y: 150, r: 26, lx: ARC.barber, ly: 104, label: '理发店', tags: ['sound'], look: lookBarber,
        use: async (S2) => { await S2.say(null, '理发店。门口的转灯一圈一圈地转。'); } },
    );
    st.triggers.push(
      { x0: 270, x1: 330, run: girlsBlock },
      { x0: 362, x1: 960, cond: () => !!F().girlsGone, run: async () => { F().liquor = true; } },
    );
    T().memberTalk({ koichi: async (S2) => { await S2.say('koichi', '回音能把声音贴在东西上……对了，贴到她们想去的地方！'); } });
    T().goal(S, { x: ARC.barber, y: 150, label: '理发店', h: 52, when: () => !!F().girlsSeen, done: () => !!F().girlsGone, every: 15,
      text: '按 Q 换康一，对着理发店按 U：让回音贴一句“仗助君在这边～”' });
    T().goal(S, { x: ARC.liquor, y: 156, label: '老酒铺', when: () => !!F().girlsGone, done: () => !!F().liquor, every: 15, text: '往前走，追上间田！' });
  }
  async function arcadeIn(S) {
    S.party(['josuke', 'koichi'], { leader: 'josuke' });
    await S.setStage('arcade_ch2', { x: 24, y: 158, facing: 1, music: 'tension' });
    S.state('pm', 1);
    S.location('shopping', { y: NAME_TOP });
    S.hint('追上间田和假仗助！', 5);
    // 天色慢慢暗下来（pm 罩色 1 → 1.7）
    T().tick((dt) => { const st = G.world.stage; st.state.pm = Math.min(1.7, (st.state.pm || 1) + dt * 0.006); return false; });
  }
  // 老酒铺门口：间田把汽水洒在摩托上 → 表面打倒飙车族 → 美工刀（喜剧化的小刀片，只比划）
  async function beatLiquor(S) {
    const p = S.player, ko = S.actor('koichi'), hz = S.actor('hazamada'), sf = S.actor('surface');
    const ba = S.actor('biker_a'), bb = S.actor('biker_b'), moto = S.actor('moto_a');
    S.hint(null);
    T().memberTalk({});
    if (p.cid !== 'josuke') G.party.setLeader('josuke', { force: true, silent: true });
    recallAll();
    const jo = S.player;
    if (ko) { ko.follow = null; S.walk(ko, 300, 162, { speed: 70 }).catch(G.cancelIgnore); }
    await S.walk(jo, 330, 156, { speed: 70 });
    S.face(jo, 1);
    focus({ x: 440 });
    // 汽水
    const soda = T().prop(S, 'bottle', hz.x + 6, hz.y + 0.5, { id: 'soda', z: 14 });
    hz.play('point');
    await S.wait(0.3);
    if (soda) { soda.rot = 1.6; await S.arc(soda, ARC.bikeA[0] - 6, ARC.bikeA[1], 6, 0.3, { z1: 18 }); }
    S.sfx('splash', 0.6);
    if (moto) T().setFrame(moto, 1);
    await S.say('hazamada', '这摩托真碍事。', { expr: 'smile' });
    if (soda) soda.remove = true;
    S.face(ba, hz); S.face(bb, hz);
    ba.play('point');
    await S.say('biker_a', '喂！你小子往我车上倒什么？！', { expr: 'rage' });
    await S.say('hazamada', '……表面。');
    // 表面一拳打倒飙车族A，按住飙车族B
    await S.walk(sf, ba.x - 16, ba.y, { speed: 90 });
    S.face(sf, 1);
    sf.play('kick');
    S.sfx('punch_heavy', 0.8); S.shake(3, 0.25);
    S.sfxText('DORA!', ba, { dur: 0.7 });
    await S.arc(ba, 572, 154, 14, 0.4, { anim: 'hurt' });
    S.pose(ba, 'down');
    S.sfx('thud', 0.8);
    sf.play('idle');
    await S.walk(sf, bb.x - 14, bb.y, { speed: 90 });
    S.pose(bb, 'hurt');
    // 美工刀：小小的刀片，只是比划
    const cut = T().prop(S, 'cutter', hz.x + 7, hz.y + 0.5, { id: 'cutter', z: 18 });
    if (cut) stick(cut, hz, 7, 18);
    hz.play('point');
    S.sfx('razor', 0.5, 1.4);
    S.sfxText('咔咔', { wx: hz.x + 8, wy: hz.y, wz: 30 }, { dur: 0.6 });
    await S.say('hazamada', '谁让你们挡路。', { expr: 'rage' });
    await S.say('biker_b', '那、那刀片也太短了吧……', { expr: 'normal' });
    await S.say('hazamada', '闭嘴！', { expr: 'rage' });
    sf.play('kick');
    S.sfx('punch', 0.8);
    await S.arc(bb, 600, 162, 10, 0.4, { anim: 'hurt' });
    S.pose(bb, 'down');
    S.sfx('thud', 0.7);
    if (cut) cut.remove = true;
    hz.play('idle');
    S.face(hz, -1); S.face(sf, -1);
    await S.say('josuke', '间田！', { expr: 'rage' });
    await S.say('hazamada', '……追来了啊。表面，交给你了。', { expr: 'smile' });
    S.walk(hz, 456, 144, { speed: 60 }).catch(G.cancelIgnore);
    await S.walk(sf, 470, 156, { speed: 60 });
    S.face(sf, jo);
    focus(null);
  }
  async function afterSegB(S) {
    const p = S.player, ko = S.actor('koichi');
    if (p.cid !== 'josuke') G.party.setLeader('josuke', { force: true, silent: true });
    recallAll();
    if (ko) { ko.follow = null; S.walk(ko, S.player.x - 26, 162, { speed: 70 }).catch(G.cancelIgnore); }
    S.music('tension', 0.6);
    await S.say('koichi', '他们往道口那边跑了！', { expr: 'shock' });
    await S.say('josuke', '走小巷，抄近路！');
    await S.fadeOut(0.5);
  }

  // ================================================================ 段 B 结尾：道口（康一 U 对着警报灯贴「当当当当」，只有声音）
  const CROSS = { lampL: [112, 84], lampR: [208, 84] };
  async function lookLamp(S, h) {
    if (F().alarm) { await S.say('koichi', '……他们已经走了。'); return; }
    F().alarm = true;
    const at = { wx: h.lx, wy: 150, wz: 150 - h.ly + 6 };
    S.sfxText('当当当当', at, { dur: 2.2 });
    for (let i = 0; i < 8; i++) G.defer(i * 0.3, () => S.sfx('ding', 0.55, i % 2 ? 0.92 : 0.86));
    await S.wait(0.8);
    S.mark('b04b_crossing');
    const hz = S.actor('hazamada'), sf = S.actor('surface');
    if (hz) { hz.play('shock'); S.face(hz, 1); }
    await S.say('hazamada', '火车来了？！……等不了了，绕路！', { expr: 'shock' });
    if (sf) S.walk(sf, -40, 158, { speed: 110, anim: 'run' }).then(() => { sf.remove = true; }, G.cancelIgnore);
    if (hz) await S.walk(hz, -40, 152, { speed: 110, anim: 'run' });
    if (hz) hz.remove = true;
    await S.say('koichi', '（……成功了！他们去绕远路了。）', { expr: 'smile' });
    await S.say('josuke', '干得好，康一！趁现在，我们先去酒店！', { expr: 'smile' });
    F().crossDone = true;
  }
  async function crossingIn(S) {
    await S.setStage('crossing_ch2', { x: 296, y: 158, facing: -1, music: 'tension' });
    S.state('pm', 1.3);
    const p = S.player;
    // 间田和表面从左边跑过来，在道口前面喘气
    const hz = S.spawn('hazamada', -30, 150, { id: 'hazamada', facing: 1, name: '间田' });
    const sf = S.spawn('surface_cut', -46, 158, { id: 'surface', facing: 1, name: '表面' });
    S.walk(sf, 66, 158, { speed: 50, anim: 'run' }).catch(G.cancelIgnore);
    await S.walk(hz, 84, 150, { speed: 50, anim: 'run' });
    await S.until(() => !sf.script);
    hz.play('idle');
    await S.say('hazamada', '呼……呼……过了道口，就是酒店了。', { expr: 'normal' });
    S.face(p, -1);
    await S.say('josuke', '（追上了……可是这样冲过去，表面又会操纵我。）', { expr: 'shock' });
    // 换成康一
    S.setLeader('koichi');
    await S.wait(0.4);
    S.hint('康一的 U：对着警报灯贴字', 8);
    const st = G.world.stage;
    st.hotspots.push(
      { id: 'lamp_r', x: CROSS.lampR[0], y: 150, r: 26, ry: 30, lx: CROSS.lampR[0], ly: CROSS.lampR[1], label: '警报灯', tags: ['sound'], look: lookLamp,
        use: async (S2) => { await S2.say(null, '道口的警报灯。现在没亮。'); } },
      { id: 'lamp_l', x: CROSS.lampL[0], y: 150, r: 26, ry: 30, lx: CROSS.lampL[0], ly: CROSS.lampL[1], label: '警报灯', tags: ['sound'], look: lookLamp },
    );
    T().memberTalk({ josuke: async (S2) => { await S2.say('josuke', '康一，用回音想想办法！'); } });
    T().goal(S, { x: CROSS.lampR[0], y: 150, label: '警报灯', h: 74, delay: 8, every: 15, done: () => !!F().alarm, text: '康一的 U：对着警报灯贴字' });
    // 15 s 没贴：玉美·画外
    const t0 = now();
    T().tick(() => {
      if (F().alarm) return true;
      if (now() - t0 < 15 || S.busy || !G.world.free) return false;
      S.run(async (S2) => { await S2.say('tamami', '大哥，用你的声音骗他！', { name: '玉美（画外）', expr: 'smile' }); }).catch(G.cancelIgnore);
      return true;
    });
  }

  // ================================================================ 段 C：酒店门口（被隔着橱窗操纵，连按 J 抗拒）
  const HOTEL = { jt: [344, 150], sf: [414, 154], hz: [446, 146], jo: 274, ko: [196, 162], endX: 318 };
  async function hotelIn(S) {
    T().memberTalk({});
    if (S.player.cid !== 'josuke') G.party.setLeader('josuke', { force: true, silent: true });
    recallAll();
    await S.setStage('hotel_ch2', { x: 150, y: 156, facing: 1, music: 'tension', fade: false });
    S.state('pm', 1.3);
    const p = S.player, ko = S.actor('koichi');
    if (ko) Object.assign(ko, { x: 120, y: 162, facing: 1, follow: null });
    const jt = S.spawn('jotaro4', HOTEL.jt[0], HOTEL.jt[1], { id: 'jotaro4', facing: 1, name: '空条承太郎' });
    const sf = S.spawn('surface_cut', HOTEL.sf[0], HOTEL.sf[1], { id: 'surface', facing: -1, name: '表面' });
    const hz = S.spawn('hazamada', HOTEL.hz[0], HOTEL.hz[1], { id: 'hazamada', facing: -1, name: '间田' });
    // 镜头钉在地图右半边（左缘 160）：表面和间田站在咖啡店门口（414 / 446），钉在 240 时他俩正好出了画面，
    //   玩家抗拒的时候看不到是谁在操纵仗助。仗助和康一从画面左边走进来
    snapTo({ x: 320 });
    await S.fadeIn(0.6);
    S.location('grand_hotel', { y: NAME_TOP });
    hz.play('smirk');
    S.walk(ko, HOTEL.ko[0], HOTEL.ko[1], { speed: 60 }).catch(G.cancelIgnore);
    await S.walk(p, 240, 156, { speed: 60 });
    await S.say('koichi', '承太郎先生在那里！……可是，间田学长他们怎么已经到了？！', { expr: 'shock' });
    await S.say('surface', '绕远路也比你们快一步哦～', { expr: 'smile' });
    await S.say('surface', '来吧，‘仗助’。走到他背后去。', { expr: 'smile' });
    // 隔着橱窗操纵：仗助手里多了一支笔
    sf.play('point');
    p.hold = true; p.play('point');
    const pen = T().prop(S, 'pen', p.x + 7, p.y + 0.5, { id: 'ch2_pen_c', z: 21 });
    if (pen) stick(pen, p, 7, 21);
    S.sfx('heartbeat', 0.8);
    await S.walk(p, HOTEL.jo, 156, { speed: 30 });
    S.face(p, 1);
    await S.say('josuke', '（又来了……身体自己在动！）', { expr: 'shock' });
    S.face(jt, 1);
    S.mark('b04c_start');
    S.hint('连按 J：抗拒！别让手靠近承太郎！', 6);
    const r = await R().resistRun(S, {
      dur: 6, endX: HOTEL.endX, speed: 8,
      lines: [
        { at: 0.8, run: () => S.emote(ko, '仗助君！别过去！', 2.2) },
        { at: 3.4, run: () => S.emote(ko, '他在橱窗里！', 2.2) },
      ],
    });
    S.hint(null);
    p.hold = true; p.play('point');
    if (!r.held) {
      // 撑不住：承太郎压了压帽檐，按住仗助的手腕
      S.face(jt, p);
      S.pose(jt, 'pose');
      await S.summon(jt, { dur: 0.1, rise: 4 });
      S.standAct(jt, 'block', { dx: -14, z: 4, dur: 1.0 });
      S.sfx('guard', 0.8);
      await S.say('jotaro4', '……', { expr: 'normal' });
      S.recall(jt);
      S.unpose(jt);
    }
    return { pen };
  }

  // ================================================================ 节拍 11 收尾：飙车族、救护车、承太郎、电线上的小影子
  async function beatEnding(S, o) {
    const p = S.player, ko = S.actor('koichi'), jt = S.actor('jotaro4'), sf = S.actor('surface'), hz = S.actor('hazamada');
    // 两个飙车族冲进来：一个把间田撞翻，一个扯住他的领子
    const ba = S.spawn('biker_a', 530, 152, { id: 'biker_a', facing: -1, name: '飙车族A' });
    const bb = S.spawn('biker_b', 556, 160, { id: 'biker_b', facing: -1, name: '飙车族B' });
    S.sfx('skid', 0.7);
    focus({ x: 360 });
    S.walk(bb, hz.x + 22, hz.y + 4, { speed: 120, anim: 'run' }).catch(G.cancelIgnore);
    await S.walk(ba, hz.x + 12, hz.y, { speed: 130, anim: 'run' });
    S.mark('ch2_bikers');
    S.sfx('punch_heavy', 0.8); S.shake(3, 0.25);
    S.pose(hz, 'knocked');
    S.sfxText('砰', hz, { dur: 0.6 });
    await S.say('biker_a', '就是这小子！弄脏我们摩托的家伙！', { expr: 'rage' });
    bb.play('point');
    await S.say('biker_b', '还拿美工刀吓唬人？跟我们走一趟！', { expr: 'rage' });
    await S.say('hazamada', '等、等一下！表面——', { expr: 'shock' });
    // 表面变回木偶，啪嗒倒在地上；仗助的手松开了，笔掉在地上
    S.flash(0.12, 0.4, '#e8c890');
    S.sfx('doll_voice', 0.5); S.sfx('thud', 0.6);
    const doll = S.spawn('surface_doll', sf.x, sf.y, { id: 'surface_doll2', facing: -1, name: '表面' });
    sf.remove = true;
    S.pose(doll, 'fall');
    if (o && o.pen) { o.pen.remove = true; }
    const pen2 = T().prop(S, 'pen', p.x + 7, p.y + 0.5, { id: 'pen_drop', z: 21 });
    if (pen2) S.arc(pen2, p.x + 12, p.y + 2, 4, 0.3, { z1: 0, spin: 2 }).catch(G.cancelIgnore);
    p.hold = false; p.play('idle');
    S.unpose(p);
    // 画面外一阵乱响 → 救护车开过画面
    S.unpose(hz);
    S.walk(ba, 560, 150, { speed: 90 }).catch(G.cancelIgnore);
    S.walk(hz, 560, 148, { speed: 90 }).catch(G.cancelIgnore);
    await S.walk(bb, 570, 158, { speed: 90 });
    for (const a of [ba, bb, hz]) a.remove = true;
    for (let i = 0; i < 5; i++) G.defer(0.2 + i * 0.16, () => { S.sfx(i % 2 ? 'punch' : 'thud', 0.5); S.shake(1, 0.12); });
    await S.wait(1.2);
    const amb = T().prop(S, 'ambulance', -40, 174, { id: 'ambulance' });
    if (amb) { amb.frozen = null; amb.hold = false; }
    S.sfx('sub_alarm', 0.5, 1.2); S.sfx('car_engine', 0.6);
    focus({ x: 240 });
    if (amb) await S.animate(2.2, (k) => { amb.x = G.lerp(-40, 540, k); });
    else await S.wait(1.2);
    if (amb) amb.remove = true;
    S.mark('ch2_ambulance');
    await S.narrate('间田学长被送进了医院。听说要住一个月。', { pos: 'top' });
    // 承太郎
    S.music('victory', 0.8);
    S.face(jt, p); S.face(p, jt);
    if (ko) { await S.walk(ko, p.x - 30, 162, { speed: 60 }); S.face(ko, 1); }
    await S.say('jotaro4', '……原来是这么回事。');
    await S.say('josuke', '承太郎先生，你差点就被我……被那个假的我捅了。', { expr: 'shock' });
    await S.say('jotaro4', '你握着笔走过来的时候，手在抖。');
    await S.say('jotaro4', '真想害我的人，手是不会抖的。');
    await S.say('koichi', '玉美、间田学长……为什么替身使者一个接一个地冒出来？');
    await S.say('jotaro4', '替身使者和替身使者，迟早会碰到一起。');
    S.pose(jt, 'pose');
    await S.say('jotaro4', '就像有什么东西在把他们拉向彼此。');
    S.unpose(jt);
    if (pen2) pen2.remove = true;
    if (doll) doll.remove = true;
    await S.fadeOut(0.7);
    focus(null);
    // 镜头摇到画面外：远处道口那边的电线上，蹲着一个发光的小影子，眨了一下就钻进了电线
    await S.setStage('crossing_ch2', { x: 160, y: 160, music: null, fade: false });
    S.state('pm', 1.6);
    p.visible = false;
    for (const m of G.party.members) m.visible = false;
    snapTo({ x: 160 });
    const W0 = [150, 72];
    const glow = T().prop(S, 'wire_glow', W0[0], 150, { id: 'wire_glow', z: 150 - W0[1] });
    if (glow) { glow.frozen = null; glow.hold = false; }
    await S.fadeIn(0.8);
    S.sfx('wind', 0.3);
    await S.zoom(2.6, W0[0], W0[1] - 4, 0.8);
    await S.wait(0.6);
    if (glow) {
      // 眨一下
      glow.alpha = 0.2; await S.wait(0.12); glow.alpha = 1; await S.wait(0.5);
      S.mark('ch2_wire');
      S.sfx('blip', 0.5, 1.6);
      const z0 = glow.z;
      await S.animate(0.5, (k) => { glow.x = W0[0] + 18 * k; glow.z = z0 + 2 * k; glow.alpha = 1 - k; glow.scale = 1 - 0.5 * k; });
      glow.remove = true;
    } else S.mark('ch2_wire');
    await S.wait(0.6);
    await S.zoom(1, null, null, 0.3);
    S.stopMusic(0.6);
    await S.tbc({ hold: 2.0 });
    S.mark('ch2_tbc');
  }

  // ================================================================ 第2章主流程
  G.STORY.ch2 = async function (S) {
    if (T().resetCounters) T().resetCounters();
    P4().clearOverlays();
    R().dropLocks();
    girlWall = null;
    await S.chapterCard('ch2');
    S.party(['josuke'], { leader: 'josuke' });
    // 节拍 1–5（过场）→ 第 3 战 → 收尾 → 玉美投降 → 节拍 6
    await S.run(async (S2) => {
      await beatCalendar(S2);
      await beatPhone(S2);
      await beatBike(S2);
      await beatScam(S2);
      await beatHome(S2);
      S2.mark('b03_start');
      await R().fightTamami(S2);
      await R().tamamiFinale(S2);
      await beatMinion(S2);
      R().dropLocks();
      await beatGate(S2);
    }, { keepLocked: true });
    // 节拍 7 学校自由走动：康一 U 听储物柜 → E 打开间田的柜子
    await S.run(async (S2) => { await schoolIn(S2); setupSchool(S2); });
    free(S);
    await S.until(() => !!F().lockerOpen && !S.busy);
    // 节拍 8 → 第 4 战段 A → 节拍 9
    await S.run(async (S2) => {
      await beatDoll(S2);
      S2.mark('b04a_start');
      await R().fightSurfaceA(S2);
      await afterSegA(S2);
    }, { keepLocked: true });
    // 段 B：商店街自由走动（康一 U 引开女学生）→ 老酒铺门口
    await S.run(async (S2) => { await arcadeIn(S2); setupArcade(S2); });
    free(S);
    await S.until(() => !!F().liquor && !S.busy);
    await S.run(async (S2) => {
      await beatLiquor(S2);
      await R().fightSurfaceB(S2);
      await afterSegB(S2);
    }, { keepLocked: true });
    // 道口：康一 U 对着警报灯贴字
    await S.run(crossingIn);
    free(S);
    await S.until(() => !!F().crossDone && !S.busy);
    // 段 C → 节拍 11 → To Be Continued
    await S.run(async (S2) => {
      await S2.fadeOut(0.5);
      const o = await hotelIn(S2);
      await beatEnding(S2, o);
    }, { keepLocked: true });
  };
  // 整章测试（tools/dev/p4_play.js）对照的剧情标记：打一遍下来这些都要出现，缺了就算没通过
  G.STORY.ch2.marks = ['ch2_calendar', 'ch2_phone', 'ch2_bike', 'ch2_lock_koichi', 'ch2_scam_broken', 'ch2_home', 'ch2_hatch', 'b03_start',
    'b03_trust', 'ch2_minion', 'ch2_gate', 'ch2_photo', 'ch2_school', 'ch2_listen', 'ch2_doll', 'b04a_start', 'b04a_pen', 'ch2_call',
    'ch2_yukako', 'b04b_girls', 'b04b_bottle', 'b04b_crossing', 'b04c_start', 'ch2_bikers', 'ch2_ambulance', 'ch2_wire', 'ch2_tbc'];
})();
