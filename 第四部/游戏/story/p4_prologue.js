// 序章　杜王町 / 仗助登场（开发脚本 第四部/docs/序章_开发脚本.md；地图后缀 _pro）。整章流程：
//   节拍 1 篇章卡 → 日历地图（两枚图钉 + 红章）→ 2 上学路（康一旁白、白衣男人问路）→ 3 公交站（学长、发型记录 1、疯狂钻石）
//   → 4 上学路自由走动（U 修复教学）→ 5 校门（承太郎、遗产、发型记录 2、误会 VS）→ 6 序1 承太郎的试探（六步教学）
//   → 7 时停躲开、念写照片 → 8 下午（朋子过肩摔、良平）→ 9 超市（清单、劫匪、发型记录 3、水槽里的脸）
//   → 10 傍晚送奶工 → 11 那天夜里（剪影、警帽）→ 12 三天后的雨（自由走动、承太郎看水洼）→ 客厅水汽
//   → 13 序2 段 1 水中项链 / 段 2 雨中追本体 → 14 招供、弓与箭、小学生、安杰罗岩 → 15 雨停、To Be Continued
//   克制（第三部 D10）：不见血、不画伤口；良平的死只用剪影 + 落下的警帽 + 留白；安杰罗岩只是一块隐约有张脸的岩石；劫匪的刀是喜剧刀柄。
//   三场战斗在 story/p4_pro_fights.js（G.P4PRO）。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const PRO = () => G.P4PRO;
  const F = () => G.flags;
  const now = () => (G.clk ? G.clk.world : 0);
  const f = (n) => n / 60;
  const NAME_TOP = 100;          // 名牌、替身卡、地点卡的 UI y：对白框在上面（y 12–92），卡片放在它正下方，不互相压
  const KO_MSG = '康一：「诶？我？我不行啦……」';
  // 队伍池里的那个人（以后入队还是同一个 Actor：不会出现两个康一）
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
  // 镜头直接对准（换图后黑幕还没掀开时用：不让观众看到镜头横扫）
  const snapTo = (o) => { G.world.focus = o; G.world.snapCamera(); };
  // 跟着某人走的道具（警车、牛奶瓶、伞、刀柄）：换图 / 道具删掉就停
  function stick(prop, a, dx, dz, o = {}) {
    T().tick(() => {
      if (!prop || prop.remove || !a || a.remove) return true;
      prop.x = a.x + (o.flip === false ? dx : dx * (a.facing || 1)); prop.y = a.y + (o.dy || 0.5); prop.z = (a.z || 0) + dz;
      if (o.face) prop.facing = a.facing;
      return false;
    });
  }

  // ================================================================ 节拍 1 篇章卡 → 日历地图
  async function beatCalendar(S) {
    S.player.visible = false;
    await S.setStage('map_pro', { x: 160, y: 165, music: null });
    const cal = await P4().calendar(S, 'prologue', { hold: 1.8 });
    S.mark('pro_calendar');
    await S.fadeOut(0.45);
    if (cal) cal.close();
  }

  // ================================================================ 节拍 2 上学路（早上，樱花）：康一的旁白、白衣男人
  const ROAD = { thugA: [412, 158], thugB: [424, 149], crouch: [396, 147], josukeIn: [548, 157] };
  async function beatRoadMorning(S) {
    const p = S.player;
    await S.setStage('road_pro', { x: ROAD.josukeIn[0], y: ROAD.josukeIn[1], facing: -1, music: 'daily', fade: false });
    p.visible = false;           // 仗助先藏在公交站那边，节拍 3 才走出来
    const ko = place(S, 'koichi', 64, 160, 1);
    S.spawn('thug_a', ROAD.thugA[0], ROAD.thugA[1], { id: 'thug_a', facing: -1, name: '学长A' });
    S.spawn('thug_b', ROAD.thugB[0], ROAD.thugB[1], { id: 'thug_b', facing: -1, name: '学长B' });
    snapTo(ko);
    await S.fadeIn(0.6);
    S.location('morioh', { y: NAME_TOP });
    S.walk(ko, 186, 160, { speed: 30 }).catch(G.cancelIgnore);
    await S.narrate('1999 年 4 月。我叫广濑康一，今天是我上高中的第一天。', { pos: 'top' });
    await S.narrate('我住的小镇叫杜王町。平平凡凡，什么事也不会发生——那时我是这么想的。', { pos: 'top' });
    await S.until(() => !ko.script);
    // 白衣男人从右边走进画面
    const jt = S.spawn('jotaro4', 372, 156, { id: 'jotaro4_road', facing: -1, name: '空条承太郎' });
    await S.walk(jt, 226, 157, { speed: 42 });
    S.face(ko, 1);
    S.mark('pro_road_jotaro');
    await S.say('jotaro4', '……你是葡萄丘高中的学生？', { actor: jt });
    await S.say('koichi', '是、是的！我是今天刚入学的新生……', { expr: 'shock' });
    await S.narrate('白色的大衣，白色的帽子。……好高。', { pos: 'top' });
    await S.say('jotaro4', '我在找一个叫东方仗助的人。', { actor: jt });
    await S.say('koichi', '对不起，我谁都还不认识……');
    await S.say('jotaro4', '……是吗。打扰了。', { actor: jt });
    // 从康一身后那条道走出画面
    await S.walk(jt, 200, 148, { speed: 44 });
    S.face(ko, -1);
    await S.walk(jt, -30, 148, { speed: 44 });
    jt.remove = true;
    await S.narrate('那个人走过去的时候，带着一点海水的味道。', { pos: 'top' });
  }

  // ================================================================ 节拍 3 公交站：学长、发型记录 1、疯狂钻石
  async function punchThug(S, p, ta) {
    S.face(p, ta);
    await S.summon(p, { dur: 0.1, rise: 4 });
    S.standAct(p, 'punch', { dx: 20, z: 4, dur: 0.5 });
    S.sfx('whoosh', 0.7);
    await S.wait(0.08);
    S.sfx('punch_heavy', 1);
    S.sfxText('DORA!', ta, { dur: 0.9 });
    S.impact('invert', f(2));
    S.shake(4, 0.3);
    S.fx('hit_spark', { x: ta.x + 4, y: ta.y - 22, size: 16, accent: '#ffb0d8' });
    await S.arc(ta, ta.x - 38, ta.y, 14, 0.42, { anim: 'hurt' });
    S.pose(ta, 'down');
    S.sfx('thud', 0.8);
    S.fx('smoke', { x: ta.x, y: ta.y, n: 6, rise: 8, life: 0.6 }, { life: 0.8 });
    await S.wait(0.35);
    S.recall(p);
  }
  async function beatBusStop(S) {
    const p = S.player, ko = S.actor('koichi'), ta = S.actor('thug_a'), tb = S.actor('thug_b');
    S.face(ko, 1);
    await S.walk(ko, 372, 160, { speed: 40 });
    focus({ x: 430 });
    await S.say('thug_a', '喂，小个子。书包拿来，学长帮你检查检查。', { expr: 'rage' });
    await S.say('koichi', '诶？为、为什么……', { expr: 'shock' });
    // 仗助从公交站那边走过来
    p.x = 560; p.y = 158; p.facing = -1;
    await S.walk(p, 470, 159, { speed: 50 });
    S.mark('pro_josuke_enter');
    await S.say('josuke', '学长，大清早的，别为难人家。');
    S.face(ta, 1); S.face(tb, 1);
    await S.say('thug_b', '哈？又一个乱改校服的新生。', { expr: 'rage' });
    await S.walk(ta, 446, 159, { speed: 50 });
    await S.say('thug_a', '顶着这么个过时的鸡冠头，还以为自己很帅？', { expr: 'smile' });
    await P4().hair.show(S, 1);
    S.mark('pro_hair1');
    await S.say('josuke', '……你刚才说，我的头发怎么样？', { expr: 'rage' });
    await punchThug(S, p, ta);
    S.nameCard('josuke', { y: NAME_TOP });
    S.standCard('crazyd', { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.wait(0.8);
    await S.say('josuke', '啊……打过头了。');
    // 疯狂钻石一抹：鼻子回到原处——可整张脸比原来更歪了一点
    await S.walk(p, ta.x + 30, ta.y, { speed: 50 });
    S.face(p, -1);
    await S.summon(p, { dur: 0.12, rise: 4 });
    S.standAct(p, 'reach', { dx: 18, z: 2, dur: 0.8 });
    P4().fixGlow(S, ta.x, ta.y - 8);
    await S.wait(0.7);
    S.recall(p);
    S.unpose(ta);
    S.face(ta, 1);
    S.mark('pro_nose_fixed');
    await S.say('thug_a', '鼻子好了？……可怎么觉得哪里不对劲？', { expr: 'shock' });
    await S.say('thug_b', '走、走了走了！', { expr: 'shock' });
    S.walk(tb, 720, 149, { speed: 96 }).then(() => { tb.remove = true; }, G.cancelIgnore);
    await S.walk(ta, ROAD.crouch[0], ROAD.crouch[1], { speed: 70 });
    S.pose(ta, 'guard');                // 蹲在路边
    S.face(ta, 1);
    await S.say('koichi', '（学长的鼻子……刚才是自己变回去的？）', { expr: 'shock' });
    await S.walk(p, 400, 160, { speed: 50 });
    S.face(p, -1); S.face(ko, 1);
    await S.say('josuke', '没事吧？我叫东方仗助，也是一年级。', { expr: 'smile' });
    S.nameCard('koichi', { y: NAME_TOP });
    await S.say('koichi', '我、我叫广濑康一。谢谢你！', { expr: 'smile' });
    await S.say('josuke', '走吧，第一天就迟到可不行。', { expr: 'smile' });
    // 康一入队，但他是普通人：灰着，Q 换不过去
    S.party(['josuke', 'koichi'], { leader: 'josuke' });
    S.leadable('koichi', false, { msg: KO_MSG });
    focus(null);
  }

  // ================================================================ 节拍 4 上学路自由走动：疯狂钻石的修复（U）
  async function usePot(S) {
    if (F().potFixed) { await S.say(null, '窗台上的花盆，花开得正好。'); return; }
    await S.say(null, '窗台下摔碎了一个花盆。……要是能修好就好了。');
    if (!F().potHinted) { F().potHinted = true; S.hint('按 U：让疯狂钻石修好它', 5); }
  }
  async function fixPot(S) {
    if (F().potFixed) { await S.say('josuke', '……已经修好了。'); return; }
    F().potFixed = true;
    const pot = S.actor('pot');
    T().setFrame(pot, 0);
    S.sfx('whoosh', 0.6);
    // 碎片飞回窗台（窗台比路面高 44 px）
    if (pot) await S.animate(0.45, (k) => { pot.z = Math.round(44 * (1 - (1 - k) * (1 - k))); });
    P4().fixGlow(S, 332, 104);
    S.mark('pro_pot');
    await S.say('granny', '哎呀，谢谢你啊。', { name: '窗里的老奶奶' });
    await S.say('josuke', 'Great～', { expr: 'smile' });
  }
  async function fixThugAgain(S) {
    const ta = S.actor('thug_a');
    if (F().thugFix) { await S.say('josuke', '……还是别再修了。'); return; }
    F().thugFix = true;
    await S.say('josuke', '再修一次……');
    if (ta) P4().fixGlow(S, ta.x, ta.y - 18, { n: 5 });
    await S.wait(0.5);
    await S.say('thug_a', '……', { expr: 'shock' });
    await S.say('josuke', '……修好了，大概。');
  }
  async function talkThug(S, me) {
    await T().say(S, me, F().thugFix ? '……别、别再碰我的脸了！' : '别、别过来！', { expr: 'shock' });
  }
  async function useVending(S) {
    if (!F().coin) {
      F().coin = true;
      S.sfx('coin', 0.8);
      await S.say(null, '找零口里……有 10 日元！');
      await S.say('josuke', '今天运气不错。', { expr: 'smile' });
      return;
    }
    await S.say(null, '自动售货机。找零口已经空了。');
  }
  async function talkFans(S, me) {
    if (F().fans) { await T().say(S, me, me.id === 'fan_a' ? '仗助君，放学见～' : '今天也要加油哦！'); return; }
    F().fans = true;
    const a = S.actor('fan_a'), b = S.actor('fan_b');
    if (a) a.play('cheer');
    if (b) b.play('cheer');
    await T().say(S, 'fan_a', '仗助君～早上好！');
    await T().say(S, 'fan_b', '今天的发型也好帅！');
    await S.say('josuke', '……这句我爱听。', { expr: 'smile' });
    if (a) a.play('idle');
    if (b) b.play('idle');
  }
  function setupRoadFree(S) {
    const st = G.world.stage, ta = S.actor('thug_a');
    T().prop(S, 'pot', 332, 150, { id: 'pot', frame: 1 });
    S.spawn('fan_a', 594, 151, { id: 'fan_a', facing: -1, label: '女生', talk: talkFans });
    S.spawn('fan_b', 614, 157, { id: 'fan_b', facing: -1, label: '女生', talk: talkFans });
    if (ta) { ta.talk = talkThug; ta.label = '学长A'; }
    const tx = ta ? ta.x : ROAD.crouch[0], ty = ta ? ta.y : ROAD.crouch[1];
    st.hotspots.push(
      { id: 'pot', x: 332, y: 152, r: 20, ry: 16, label: '花盆', tags: ['fix'], fx: 332, fy: 144, use: usePot, look: fixPot },
      { id: 'thug', x: tx, y: ty, r: 20, ry: 16, label: '学长A', tags: ['fix'], fx: tx, fy: ty - 20, look: fixThugAgain },
      { id: 'vending', x: 531, y: 150, r: 18, label: '自动售货机', use: useVending },
      { id: 'busstop', x: 452, y: 150, r: 14, label: '公交站牌', use: async (S2) => { await S2.say(null, '去住宅区的车，二十分钟一班。'); } },
      { id: 'sakura', x: 808, y: 150, r: 26, label: '樱花树', use: async (S2) => { await S2.say('josuke', '今年开得真早啊。'); } },
    );
    st.triggers.push({ x0: 920, x1: 1000, run: async () => { F().toGate = true; } });
    // 45 s 后出箭头：指到画面右端（校门那边）
    T().goal(S, { x: 930, y: 158, label: '学校', delay: 45, every: 15, done: () => !!F().toGate, text: '往右走，去葡萄丘高中' });
  }

  // ================================================================ 节拍 5 校门：承太郎、遗产、发型记录 2、误会
  async function beatGate(S) {
    const p = S.player;
    T().memberTalk({});
    await S.setStage('gate_pro', { x: 30, y: 160, facing: 1, music: 'daily' });
    const ko = S.actor('koichi');
    const jt = S.spawn('jotaro4', 262, 150, { id: 'jotaro4', facing: -1, name: '空条承太郎' });
    const fan = S.spawn('fan_a', 430, 156, { id: 'fan_a', facing: -1 });
    S.location('budou', { y: NAME_TOP });
    if (ko) { ko.follow = null; S.walk(ko, 190, 162, { speed: 62 }).catch(G.cancelIgnore); }
    await S.walk(p, 214, 158, { speed: 62 });
    S.face(p, 1);
    if (ko) S.face(ko, 1);
    S.mark('pro_gate');
    await S.say('jotaro4', '东方仗助。');
    await S.say('josuke', '我是。……大叔，你哪位？');
    await S.say('jotaro4', '空条承太郎。按辈分算，我是你的外甥。');
    S.nameCard('jotaro4', { y: NAME_TOP });
    await S.say('josuke', '外甥？你看起来比我大了一轮啊！', { expr: 'shock' });
    await S.say('jotaro4', '你的父亲叫乔瑟夫·乔斯达，住在纽约，今年 79 岁。');
    await S.say('jotaro4', '律师整理他的遗产时查到了你。将来乔斯达家的遗产，有三分之一归你。');
    await S.say('koichi', '（三、三分之一……？）', { expr: 'shock' });
    await S.say('josuke', '……我不要。我和妈妈两个人过得挺好。');
    await S.say('josuke', '帮我跟那位老人家说一声：别担心我们，他自己多保重。');
    S.pose(jt, 'pose');              // 压帽檐
    await S.say('jotaro4', '……');
    await S.say('jotaro4', '……知道了。');
    S.unpose(jt);
    await S.walk(fan, 296, 160, { speed: 74 });
    await S.say('fan_a', '仗助君！这个大叔是谁呀？');
    S.face(jt, p);
    await S.say('jotaro4', '……那样的头发，在镇上找起来倒是方便。');
    await P4().hair.show(S, 2);
    S.mark('pro_hair2');
    await S.say('josuke', '……喂。你刚才说我的头发怎么了？', { expr: 'rage' });
    await S.say('jotaro4', '……？');
    await S.say('koichi', '（他说的是“方便”吧……？）', { expr: 'shock' });
    // 让开场地：女生躲到右边，康一退到左边
    S.walk(fan, 540, 150, { speed: 100 }).catch(G.cancelIgnore);
    if (ko) S.walk(ko, 112, 150, { speed: 90 }).catch(G.cancelIgnore);
    await S.walk(jt, 300, 158, { speed: 50 });
    S.face(jt, p);
    S.music('battle', 0.3);
    await S.vs({ key: 'misunderstand', hero: 'josuke', enemy: { cid: 'jotaro4', anim: 'pose' } });
    G.uifx.vsTag('misunderstand');
  }

  // ================================================================ 节拍 7 时停躲开 → 念写照片
  async function beatPhoto(S) {
    const p = S.player, jt = S.actor('jotaro4'), ko = S.actor('koichi');
    await S.say('jotaro4', '……冷静下来了？');
    S.face(p, jt);
    await S.say('josuke', '诶？！你什么时候跑到我后面的？', { expr: 'shock' });
    await S.say('josuke', '……抱歉。一说到头发，我就收不住手。');
    if (ko) { ko.follow = null; await S.walk(ko, Math.min(p.x, jt.x) - 34, 160, { speed: 80 }); }
    S.music('tension', 0.8);
    await S.say('jotaro4', '我来杜王町，还有一件事。');
    await S.say('jotaro4', '片桐安十郎，外号安杰罗。杀过人，也教唆别人杀人。');
    await S.say('jotaro4', '他被判了绞刑，吊了二十分钟却没死。两个星期前，他越狱了。');
    await S.say('jotaro4', '这张照片是那位老人家用替身“念写”的。看他身边。');
    // 特写：照片里安杰罗身边有一团水，水里隐约有一张脸（红箭头指着那团水）
    await S.photo({ hold: 2.2, arrow: { x: 39, y: 20, angle: 180 } });
    S.mark('pro_photo');
    await S.say('josuke', '水……做的替身？');
    await S.say('jotaro4', '他就在这个镇上。你自己小心。');
    await S.narrate('替身。那天我第一次听到这个词。……虽然完全听不懂。', { pos: 'top' });
    await S.fadeOut(0.5);
  }

  // ================================================================ 节拍 8 下午的上学路：朋子过肩摔、良平
  async function beatRoadPm(S) {
    const p = S.player;
    S.leave('koichi', { drop: true });
    await S.setStage('road_pro', { x: 940, y: 156, facing: -1, music: 'daily', fade: false });
    p.visible = false;
    S.state('pm', 1);
    const tm = S.spawn('tomoko', 520, 158, { id: 'tomoko', facing: 1 });
    const fl = S.spawn('flirt', 556, 158, { id: 'flirt', facing: -1 });
    snapTo({ x: 556 });
    await S.fadeIn(0.5);
    await S.say('flirt', '小姐，一个人？一起喝杯茶吧。', { expr: 'smile' });
    await S.say('tomoko', '没空。', { expr: 'rage' });
    // 过肩摔：抓住 → 甩过头顶 → 背后着地（白光、「砰」）
    tm.play('wave');
    S.sfx('whoosh', 0.9);
    await S.arc(fl, 488, 160, 34, 0.42, { spin: -Math.PI, anim: 'hurt' });
    fl.rot = 0;
    S.pose(fl, 'down');
    S.flash(0.12, 0.8);
    S.sfx('thud', 1); S.sfx('punch_heavy', 0.6);
    S.sfxText('砰', { wx: 488, wy: 160, wz: 18 }, { dur: 0.8 });
    S.shake(4, 0.3);
    S.face(tm, -1);
    tm.play('idle');
    S.mark('pro_tomoko_throw');
    S.nameCard('tomoko', { y: NAME_TOP });
    await S.wait(0.9);
    S.unpose(fl);
    await S.say('flirt', '警、警察先生！这个女人打人！', { expr: 'shock' });
    const ry = S.spawn('ryohei', 400, 160, { id: 'ryohei', facing: 1 });
    focus({ x: 500 });
    await S.walk(ry, 456, 162, { speed: 46 });
    await S.say('ryohei', '哦？……那是我女儿。', { expr: 'smile' });
    S.nameCard('ryohei', { y: NAME_TOP });
    await S.say('flirt', '……打扰了！', { expr: 'shock' });
    S.walk(fl, 760, 166, { speed: 110 }).then(() => { fl.remove = true; }, G.cancelIgnore);
    await S.walk(tm, 480, 158, { speed: 50 });
    S.face(tm, -1);
    await S.say('tomoko', '爸，下班了？今晚来家里吃饭吧。', { expr: 'smile' });
    await S.say('ryohei', '改天。最近镇上不太平，我想多巡一圈。');
    await S.say('ryohei', '仗助四岁那年发高烧，大雪天车子陷在路上。');
    await S.say('ryohei', '帮忙推车的，是个不认识的高中生。');
    await S.say('tomoko', '仗助那个发型，就是照着那个人梳的。', { expr: 'smile' });
    await S.say('tomoko', '对了，今天让仗助去超市买东西了。那孩子别又光买零食……');
    await S.fadeOut(0.5);
    focus(null);
  }

  // ================================================================ 节拍 9 超市：清单、劫匪、发型记录 3、水槽里的脸
  let shop = null;
  async function takeItem(S, name, icon, line) {
    if (!shop) return;
    if (!shop.check(name)) { await S.say(null, '清单上的' + name + '已经拿过了。'); return; }
    const p = S.player;
    S.sfx('pop', 0.7);
    T().floater(S, 'prop:' + icon, p.x, p.y + 0.5, { z: 40, rise: 10, dur: 0.9 });
    await S.say(null, line);
    if (shop.all()) S.hint('清单上的东西都齐了', 4);
  }
  async function takeSnack(S) {
    if (shop && shop.extra) { await S.say('josuke', '……一包就够了。'); return; }
    const p = S.player;
    S.sfx('pop', 0.7);
    T().floater(S, 'prop:item_snack', p.x, p.y + 0.5, { z: 40, rise: 10, dur: 0.9 });
    await S.say('josuke', '……就一包，妈不会发现的。', { expr: 'smile' });
    if (shop) shop.extra = '零食（妈会发现）';
  }
  function setupMarket() {
    Object.assign(G.STAGES.market_pro, {
      npcs: [
        T().npc('clerk', 'clerk', 606, 152, { facing: -1, label: '店员', talk: async (S, me) => { await T().say(S, me, '欢迎光临～', { expr: 'smile' }); } }),
        T().npc('robber', 'robber', 566, 162, { facing: -1, label: '戴帽子的男人', talk: async (S, me) => { await T().say(S, me, '……看什么看。'); } }),
      ],
      hotspots: [
        { id: 'soy', x: 130, y: 152, r: 18, label: '酱油', use: (S) => takeItem(S, '酱油', 'item_soy', '拿了一瓶酱油。') },
        { id: 'snack', x: 288, y: 152, r: 18, label: '零食货架', use: takeSnack },
        { id: 'soap', x: 394, y: 152, r: 18, label: '洗洁精', use: (S) => takeItem(S, '洗洁精', 'item_soap', '拿了一瓶洗洁精。') },
        { id: 'tofu', x: 474, y: 152, r: 18, label: '冷柜·豆腐', use: (S) => takeItem(S, '豆腐', 'item_tofu', '拿了一盒豆腐。') },
        { id: 'sink', x: 535, y: 150, r: 14, label: '水槽', use: async (S) => { S.sfx('drip', 0.7); await S.say(null, '水龙头在滴水。'); } },
      ],
      triggers: [],
    });
  }
  async function marketIn(S) {
    const p = S.player;
    p.visible = true;
    await S.setStage('market_pro', { x: 34, y: 160, facing: 1, music: 'daily' });
    S.location('market', { y: NAME_TOP });
    shop = P4().shopList(['酱油', '豆腐', '洗洁精']);
    S.hint('把妈妈清单上的东西拿齐（走到货架前按 E）', 7);
  }
  async function robberScene(S) {
    const p = S.player, rb = S.actor('robber'), ck = S.actor('clerk');
    S.hint(null);
    rb.talk = null; ck.talk = null;
    // 劫匪挟持店员：一把夸张的喜剧刀
    S.sfx('sting_shock', 0.7);
    S.music('tension', 0.4);
    focus({ x: 540 });
    await S.walk(rb, 588, 156, { speed: 96 });
    S.face(rb, -1); S.face(ck, -1);
    const knife = T().prop(S, 'knife', rb.x - 11, rb.y + 1, { id: 'knife', frame: 0, z: 17 });
    knife.facing = -1;
    await S.say('robber', '都别动！把收银台的钱装进来！', { expr: 'rage' });
    await S.say('clerk', '救、救命……', { expr: 'shock' });
    if (Math.abs(p.x - 536) > 160) { p.x = 380; p.y = 160; }
    await S.walk(p, 536, 158, { speed: 90 });
    S.face(p, 1);
    await S.say('josuke', '喂喂，大白天的……');
    await S.say('robber', '看什么看！顶着个怪头的小鬼，滚开！', { expr: 'rage' });
    await P4().hair.show(S, 3);
    S.mark('pro_hair3');
    await S.say('josuke', '……你说谁的头怪？', { expr: 'rage' });
    // 这一章第一次 QTE：失败也照样往下走，只是劫匪多骂一句
    const r = await S.press({ key: 'attack', window: 0.8, label: '按 J！' });
    if (r === 'miss') await S.say('robber', '哈？你一个小鬼想干嘛——', { expr: 'rage' });
    // 疯狂钻石 DORARARA：劫匪飞出去撞上店员，刀飞起来
    await S.summon(p, { dur: 0.1, rise: 4 });
    S.standAct(p, 'rush', { dx: 18, z: 4, hold: true, jitter: 1 });
    rb.play('hurt');
    for (let i = 0; i < 9; i++) G.defer(i * 0.09, () => { S.sfx('punch', 0.55); if (i % 3 === 0) S.sfxText('DORA', rb, { dur: 0.5, dx: (i % 2 ? 10 : -10) }); });
    S.shake(2, 0.8);
    await S.wait(0.85);
    S.standAct(p, 'punch', { dx: 22, z: 4, dur: 0.5 });
    S.sfx('punch_heavy', 1);
    S.sfxText('DORA!!', rb, { dur: 0.9 });
    S.impact('invert', f(2));
    S.shake(4, 0.3);
    S.arc(knife, 572, 166, 40, 0.7, { spin: 14 }).then(() => { knife.rot = 0.3; }, G.cancelIgnore);
    await S.arc(rb, 606, 158, 16, 0.4, { anim: 'hurt' });
    S.pose(rb, 'down');
    // 店员被撞倒
    ck.rot = -Math.PI / 2; ck.x = 622; ck.hold = true;
    S.sfx('thud', 0.9);
    S.recall(p);
    await S.wait(0.4);
    S.mark('pro_robber_down');
    await S.say('josuke', '啊，店员姐姐被碰到了……修一下。');
    await S.walk(p, 590, 152, { speed: 60 });
    S.face(p, 1);
    await S.summon(p, { dur: 0.1, rise: 4 });
    S.standAct(p, 'reach', { dx: 18, z: 2, dur: 0.8 });
    P4().fixGlow(S, ck.x - 6, ck.y - 8);
    await S.wait(0.45);
    ck.rot = 0; ck.x = 612; ck.hold = false; ck.play('idle');
    await S.wait(0.3);
    await S.say('josuke', '这家伙也顺便修一下吧。');
    S.standAct(p, 'reach', { dx: 14, z: 0, dur: 0.8 });
    P4().fixGlow(S, rb.x, rb.y - 10);
    // 刀柄被“修”进了劫匪的额头：像长了一只角（喜剧，不见血）
    await S.arc(knife, rb.x, rb.y + 0.5, 20, 0.35, { z1: 26 });
    T().setFrame(knife, 1);
    knife.rot = 0;
    S.recall(p);
    S.unpose(rb);
    S.face(rb, -1);
    stick(knife, rb, -3, 27, { face: true });
    S.sfx('pop', 0.8);
    S.mark('pro_knife_horn');
    await S.say('robber', '我、我的额头上……这是什么？！', { expr: 'shock' });
    // 劫匪张大嘴的一瞬间：嘴里闪过照片上那张水做的脸（0.3 s 特写）
    await T().closeup4(S, { heads: [{ cid: 'aqua' }], dur: 0.32, bg: 'menace', sfx: 'sting_shock' });
    // 「咕噜」一声，一道水顺着水槽流走
    S.sfx('bubbles', 0.9); S.sfx('drip', 0.7);
    S.sfxText('咕噜', { wx: 535, wy: 146, wz: 34 }, { dur: 0.9 });
    S.fx('water_splash', { x: 535, y: 118, size: 0.8 }, { life: 0.6 });
    S.face(p, -1);
    await S.wait(0.5);
    S.mark('pro_sink_face');
    await S.say('josuke', '……刚才那个，是照片上的……！', { expr: 'shock' });
    S.face(p, 1);
    await S.say('clerk', '谢谢你！……那个，你的头发真好看。', { expr: 'smile' });
    S.sfx('sparkle', 0.6);
    await S.say('josuke', 'Great～', { expr: 'smile' });
    if (shop && shop.h) shop.h.close();
    shop = null;
    await S.fadeOut(0.5);
    focus(null);
  }

  // ================================================================ 节拍 10 东方家门口（晴，傍晚）：送奶工
  async function beatMilkman(S) {
    const p = S.player;
    await S.setStage('house_pro', { bg: 'higashikata_eve', x: 376, y: 148, facing: 1, music: 'daily', fade: false });
    p.visible = false;
    const tm = S.spawn('tomoko', 372, 152, { id: 'tomoko', facing: 1 });
    const mk = S.spawn('angelo', 406, 155, { id: 'milkman', facing: -1, name: '送奶工' });
    const milk = T().prop(S, 'milk', 400, 155, { id: 'milk', frame: 0, z: 12 });
    snapTo({ x: 390 });
    await S.fadeIn(0.5);
    S.location('higashikata', { y: NAME_TOP });
    S.sfx('ding', 0.6);
    await S.say('angelo', '您好，送牛奶的。', { name: '送奶工' });
    await S.say('tomoko', '我们家订的不是这个牌子……而且瓶盖松了。换一瓶吧。');
    await S.say('angelo', '……真是失礼了。', { name: '送奶工' });
    // 他转身。只给玩家看的特写：嘴角咧开一下又收回去，瓶子里的牛奶晃了一下，像有东西在游
    S.face(mk, 1);
    stick(milk, mk, 6, 12);
    await T().closeup4(S, { heads: [{ cid: 'angelo', expr: 'smile' }], dur: 0.7, bg: 'menace', sfx: 'menacing' });
    T().setFrame(milk, 1);
    S.sfx('bubbles', 0.6);
    S.mark('pro_milk');
    await S.wait(0.7);
    T().setFrame(milk, 0);
    S.walk(mk, 720, 157, { speed: 46 }).then(() => { mk.remove = true; milk.remove = true; }, G.cancelIgnore);
    await S.wait(1.2);
    // 仗助从屋里出来
    p.x = 376; p.y = 149; p.facing = 1; p.visible = true;
    await S.walk(p, 352, 160, { speed: 50 });
    S.face(tm, p); S.face(p, tm);
    await S.say('josuke', '妈，刚才是谁？');
    await S.say('tomoko', '新来的送奶工吧，没见过。');
    await S.fadeOut(0.6);
  }

  // ================================================================ 节拍 11 那天夜里：剪影、警帽、留白
  async function beatRyoheiNight(S) {
    const p = S.player;
    await S.setStage('house_pro', { bg: 'higashikata_night', x: 372, y: 152, facing: 1, music: null, fade: false });
    S.stopMusic(0.3);
    const ry = S.spawn('ryohei', 600, 160, { id: 'ryohei', facing: -1 });
    const bike = T().prop(S, 'police_bike', 586, 160, { id: 'pbike' });
    stick(bike, ry, -16, 0, { face: true });
    snapTo({ x: 440 });
    await S.fadeIn(0.6);
    await S.walk(ry, 430, 160, { speed: 40 });
    await S.say('ryohei', '路过，来看看外孙。', { expr: 'smile' });
    await S.say('josuke', '外公！今晚值班？', { expr: 'smile' });
    await S.say('ryohei', '嗯。那个越狱犯可能就在镇上。你晚上别出门。');
    await S.say('josuke', '外公你才要小心，都快退休了。');
    await S.say('ryohei', '这个镇子我守了三十多年，还没守够呢。', { expr: 'smile' });
    // 良平骑车离开，画面停在空空的路口
    S.face(ry, 1);
    await S.walk(ry, 720, 160, { speed: 72 });
    ry.remove = true; bike.remove = true;
    p.visible = false;
    focus({ x: 500 });
    await S.wait(1.2);
    await S.title('night', { y: 110 });
    S.mark('pro_night');
    // 远处一声闷响
    await S.wait(0.5);
    S.sfx('thud', 0.35);
    S.shake(1, 0.2);
    await S.wait(0.9);
    // 仗助冲出门：路灯下一个人影倒下的剪影；警帽落在地上，滚了半圈，停住
    const sil = S.spawn('ryohei', 506, 150, { id: 'ry_sil', facing: -1 });
    sil.tint = { color: '#04020a', k: 1 };
    sil.shadow = false;
    const cap = T().prop(S, 'cap', 500, 150, { id: 'cap', z: 30 });
    p.x = 376; p.y = 150; p.visible = true; p.facing = 1;
    await S.walk(p, 446, 158, { speed: 96, anim: 'run' });
    S.sfx('heartbeat', 0.5);
    await S.animate(0.55, (k) => { sil.rot = (Math.PI / 2) * k * k; });
    S.sfx('thud', 0.5);
    await S.arc(cap, 486, 156, 8, 0.4, { z1: 0 });
    await S.animate(0.45, (k) => { cap.rot = Math.PI * k; cap.x = 486 - 8 * k; });
    S.mark('pro_silhouette');
    // 留白 2 s，没有音乐
    await S.wait(2.0);
    await S.say('josuke', '外公……！');
    await S.summon(p, { dur: 0.14, rise: 4 });
    S.standAct(p, 'reach', { dx: 20, z: 0, dur: 1.4 });
    P4().fixGlow(S, sil.x, sil.y - 6, { n: 5, life: 0.5, vol: 0.5 });
    await S.wait(0.6);
    await S.animate(0.6, (k) => { sil.alpha = 1 - 0.2 * k; });
    await S.wait(0.4);
    S.recall(p);
    S.music('sad', 1.2);
    await S.narrate('疯狂钻石能修好坏掉的东西。……却修不回已经离开的人。', { pos: 'top' });
    await S.walk(p, cap.x + 12, cap.y + 2, { speed: 30 });
    S.face(p, -1);
    cap.remove = true;
    await S.say('josuke', '外公守了三十年的这个镇子……以后换我来守。');
    S.mark('pro_ryohei_cap');
    await S.fadeOut(0.8);
    sil.remove = true;
    focus(null);
  }

  // ================================================================ 节拍 12 三天后，雨（自由走动）：承太郎看水洼 → 进屋
  async function lookPuddle(S, h, p) {
    if (p.cid !== 'jotaro4') return;
    S.sfx('splash', 0.4);
    await T().closeup4(S, { heads: [{ cid: 'aqua' }], dur: 0.35, bg: '#0a1a2a', sfx: 'sting_shock' });
    S.mark('pro_puddle_face');
    await S.say('jotaro4', '……它在这里。');
    F().puddle = true;
  }
  function setupHouseRain() {
    Object.assign(G.STAGES.house_pro, {
      npcs: [], triggers: [],
      hotspots: [
        { id: 'umbrella', x: 400, y: 152, r: 14, label: '伞架', use: async (S) => { await S.say(null, '良平的旧伞。'); await S.say('josuke', '……外公的伞。'); } },
        { id: 'mailbox', x: 292, y: 152, r: 14, label: '邮箱', use: async (S) => { await S.say(null, '邮箱里湿漉漉的，像有人刚打开过。'); } },
        { id: 'puddle', x: 250, y: 168, r: 18, ry: 12, label: '水洼', tags: ['detail'],
          use: async (S) => { await S.say(null, '门口积了一大片水洼。雨点打在上面，一圈一圈的。'); }, look: lookPuddle },
        { id: 'window', x: 219, y: 150, r: 16, label: '客厅的窗', use: async (S) => { await S.say(null, '窗玻璃里面起了一层白雾。'); } },
      ],
    });
  }
  async function rainVisit(S) {
    await S.setStage('house_pro', { bg: 'higashikata_rain', x: 352, y: 160, facing: -1, music: 'tension', fade: false });
    S.state('rain', 1);
    S.ambient('rain_loop', 0.35);
    const p = S.player, jt = S.actor('jotaro4'), ko = S.actor('koichi');
    if (jt) Object.assign(jt, { x: 316, y: 158, facing: 1 });
    if (ko) Object.assign(ko, { x: 290, y: 164, facing: 1 });
    G.world.snapCamera();
    await S.fadeIn(0.6);
    await S.title('rain3', { y: 110 });
    S.mark('pro_rain3');
    await S.say('koichi', '仗助君这几天没来学校，我把笔记带来了……');
    await S.say('josuke', '……谢了，康一。');
    await S.say('jotaro4', '……这雨下得不对劲。四处看看。');
    S.face(p, -1);
    S.hint('Q 换队长（承太郎）：承太郎按 U，白金之星能看清细节', 8);
  }
  async function talkKoichi12(S) { await S.say('koichi', '笔记我放在这儿了……仗助君，你还好吧？'); }
  async function talkJotaro12(S) { await S.say('jotaro4', '……别大意。'); }

  // ================================================================ 客厅：烧水、水汽、水里浮出一张脸 → 序2
  async function livingIntro(S) {
    const p = S.player, ko = S.actor('koichi');
    T().memberTalk({});
    if (p.cid !== 'josuke') S.setLeader('josuke', { force: true, silent: true });
    await S.say('josuke', '先进屋吧，我去烧水。');
    if (ko) await S.say('koichi', '那、那我把笔记放下就先回去了……');
    S.leave('koichi', { drop: true });
    S.ambient(null);
    await S.setStage('living_pro', { x: 236, y: 160, facing: 1, music: 'tension' });
    const pl = S.player, jt = S.actor('jotaro4');
    if (jt) { jt.follow = null; Object.assign(jt, { x: 200, y: 156, facing: 1 }); }
    S.state('fog', 0.04);
    await S.walk(pl, 420, 150, { speed: 64 });
    S.face(pl, 1);
    S.sfx('blip', 0.8);
    S.sfxText('嘀——', { wx: 431, wy: 92, wz: 0 }, { dur: 1.4 });
    S.fx('smoke', { x: 431, y: 86, colour: '#f4f8fc', loop: true, rise: 30, t1: 2.6, life: 1.6 }, { life: 3.2 });
    S.animate(2.6, (k) => S.state('fog', 0.04 + 0.42 * k)).catch(G.cancelIgnore);
    await S.wait(1.4);
    await S.say('jotaro4', '……仗助。别靠近水汽。');
    S.face(pl, -1);
    // 水汽里浮出一张脸，咧嘴笑
    const aq = S.spawn('aqua', 300, 154, { id: 'aqua', facing: 1, alpha: 0 });
    aq.z = 14;
    S.sfx('bubbles', 0.6);
    await S.animate(0.8, (k) => { aq.alpha = 0.85 * k; });
    S.sfx('sting_shock', 0.6);
    S.mark('pro_vapor_face');
    await S.say('angelo', '嘿嘿……你就是那个警察的外孙？', { name: '安杰罗（水汽里的声音）', expr: 'smile' });
    S.nameCard('angelo', { y: NAME_TOP });
    S.standCard('aqua', { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.wait(1.6);
    await S.vs({ key: 'aqua', hero: 'josuke', enemy: { cid: 'aqua', anim: 'idle' } });
    G.uifx.vsTag('aqua');
  }
  // 段 1 打完：项链困在手套里，拼命往本体那边挣
  async function afterTrap(S) {
    const p = S.player;
    S.hint(null);
    S.sfx('pop', 0.8);
    await S.wait(0.4);
    await S.say('josuke', '抓到了！……喂，这只手套在往外挣！', { expr: 'shock' });
    S.fx('water_splash', { x: p.x + p.facing * 10, y: p.y - 20, size: 0.6 }, { life: 0.5 });
    await S.say('jotaro4', '它想回本体那里。……跟着它。');
    await S.fadeOut(0.5);
  }
  // 段 2 开场：雨里的海边路，安杰罗回头看见仗助
  async function chaseIntro(S) {
    await S.setStage('rain_pro', { x: 70, y: 160, facing: 1, music: 'battle', fade: false });
    S.state('rain', 1);
    S.ambient('rain_loop', 0.35);
    T().prop(S, 'rock', 1068, 150, { id: 'rock', frame: 0 });
    const an = S.spawn('angelo', 250, 160, { id: 'angelo', facing: -1, name: '安杰罗' });
    G.world.snapCamera();
    await S.fadeIn(0.5);
    await S.say('angelo', '项链被抓住了？！……那个小鬼！', { expr: 'shock' });
    S.face(an, 1);
    S.unpose(an);
  }

  // ================================================================ 节拍 14 招供、弓与箭、小学生、安杰罗岩
  async function beatAngeloRock(S) {
    const p = S.player, an = S.actor('angelo'), rock = S.actor('rock');
    an.mem.hold = true;
    an.team = 'npc'; an.brain = null;
    S.pose(an, 'hurt');
    S.face(an, p);
    S.face(p, an);
    // 承太郎和康一冒雨追上来（康一回来了）
    const jt = S.actor('jotaro4') || place(S, 'jotaro4', p.x - 140, 156, 1);
    Object.assign(jt, { x: Math.max(20, p.x - 150), y: 154, visible: true, follow: null });
    const ko = place(S, 'koichi', Math.max(10, p.x - 190), 164, 1);
    S.walk(jt, p.x - 56, 154, { speed: 80 }).catch(G.cancelIgnore);
    S.walk(ko, p.x - 84, 166, { speed: 80 }).catch(G.cancelIgnore);
    focus({ x: (p.x + an.x) / 2 - 20 });
    await S.say('angelo', '等、等等！我把知道的都说！', { expr: 'shock' });
    await S.say('josuke', '……说。', { expr: 'rage' });
    await S.say('angelo', '我在牢里的时候，来过一个穿学生服的男人。');
    await S.say('angelo', '他拿着一张弓和一支箭，一箭射中了我……我就有了替身。');
    await S.say('angelo', '他说他是杜王町的人！我只知道这些！', { expr: 'shock' });
    S.mark('pro_bow_arrow');
    // 一个打着伞的小学生路过；安杰罗偷偷让水中项链从水洼溜出去，扑向他
    const kid = S.spawn('kid', p.x - 40, 170, { id: 'kid', facing: 1 });
    const umb = T().prop(S, 'umbrella', kid.x, kid.y + 0.5, { id: 'umb', z: 24 });
    stick(umb, kid, 0, 24, { flip: false });
    await S.walk(kid, p.x + 30, 170, { speed: 30 });
    const aq = S.spawn('aqua', an.x - 10, 172, { id: 'aqua_sneak', facing: -1, alpha: 0 });
    aq.z = 2;
    S.sfx('bubbles', 0.5);
    await S.animate(0.4, (k) => { aq.alpha = 0.85 * k; aq.z = 2 + 10 * k; });
    await S.say('angelo', '哈哈！不想这小鬼出事就——', { expr: 'smile' });
    S.walk(aq, kid.x + 14, 170, { speed: 90 }).catch(G.cancelIgnore);
    // QTE：J 0.6 s（失败：承太郎挡下，再来一次）
    for (let tries = 0; ; tries++) {
      const r = await S.press({ key: 'attack', window: 0.6, label: '按 J！' });
      if (r !== 'miss') break;
      S.summon(jt, { dur: 0.1, rise: 4 });
      S.standAct(jt, 'block', { dx: 16, z: 2, dur: 0.8 });
      S.sfx('guard', 0.8);
      aq.x = kid.x + 40; aq.script = null;
      S.fx('water_splash', { x: aq.x, y: aq.y - 12, size: 0.8 }, { life: 0.5 });
      await S.say('jotaro4', '……再来。');
      if (tries >= 3) break;
    }
    // 疯狂钻石一拳打散项链
    aq.script = null;
    await S.summon(p, { dur: 0.08, rise: 4 });
    S.standAct(p, 'punch', { dx: 20, z: 4, dur: 0.5 });
    S.sfx('punch_heavy', 0.9);
    S.sfxText('DORA!', aq, { dur: 0.8 });
    S.fx('water_splash', { x: aq.x, y: aq.y - 14, size: 1.2 }, { life: 0.7 });
    S.sfx('splash', 0.9);
    aq.remove = true;
    S.recall(p);
    S.face(p, an);
    await S.say('josuke', '……你啊。', { expr: 'rage' });
    // 一拳，然后“修”：安杰罗和旁边的大岩石合在一起
    await S.walk(p, an.x - 26, an.y, { speed: 70 });
    S.face(p, 1);
    await S.summon(p, { dur: 0.08, rise: 4 });
    S.standAct(p, 'rush', { dx: 18, z: 4, hold: true, jitter: 1 });
    for (let i = 0; i < 8; i++) G.defer(i * 0.08, () => S.sfx('punch', 0.5));
    S.sfxText('DORARARA', an, { dur: 0.8 });
    an.play('hurt');
    S.shake(3, 0.7);
    await S.wait(0.7);
    S.standAct(p, 'reach', { dx: 20, z: 4, dur: 1.0 });
    P4().fixGlow(S, an.x + 8, an.y - 12, { n: 9, r: 18 });
    S.sfx('sparkle', 0.9);
    await S.wait(0.3);
    S.flash(0.7, 1, '#ffffff');
    S.sfx('crash', 0.6);
    await S.wait(0.25);
    an.remove = true;
    if (rock) T().setFrame(rock, 1);
    S.recall(p);
    await S.wait(0.8);
    S.mark('pro_angelo_rock');
    S.face(kid, p);
    await S.say('kid', '哥哥谢谢你！', { expr: 'smile' });
    S.walk(kid, p.x + 300, 170, { speed: 70 }).then(() => { kid.remove = true; umb.remove = true; }, G.cancelIgnore);
    await S.narrate('后来，那块石头成了杜王町的名胜。大家叫它“安杰罗岩”。', { pos: 'top' });
    await S.fadeOut(0.8);
  }

  // ================================================================ 节拍 15 雨停 → To Be Continued
  async function beatAfterRain(S) {
    const p = S.player;
    S.ambient(null);
    await S.setStage('rain_pro', { bg: 'angelo_after', x: 1000, y: 160, facing: 1, music: null, fade: false });
    S.state('rain', 0);
    T().prop(S, 'rock', 1068, 150, { id: 'rock', frame: 1 });
    const jt = S.actor('jotaro4');
    if (jt) Object.assign(jt, { x: 960, y: 154, facing: 1, visible: true, follow: null });
    const ko = place(S, 'koichi', 930, 164, 1);
    Object.assign(p, { x: 1012, y: 162, facing: 1 });
    snapTo({ x: 1000 });
    await S.fadeIn(0.8);
    S.music('victory', 1.0);
    await S.say('jotaro4', '穿学生服的男人，弓和箭……');
    await S.say('jotaro4', '仗助。这个镇上的替身使者，恐怕不止他一个。');
    S.face(p, -1);
    await S.say('josuke', '……那就一个一个来。');
    await S.say('koichi', '替、替身使者？还不止一个？', { expr: 'shock' });
    S.face(ko, 1);
    S.stopMusic(0.6);
    await S.tbc({ hold: 2.0 });
    S.mark('pro_tbc');
  }

  // ================================================================ 序章主流程
  G.STORY.prologue = async function (S) {
    if (T().resetCounters) T().resetCounters();
    P4().clearOverlays();
    shop = null;
    await S.chapterCard('prologue');
    // 节拍 1–3（过场）
    S.party(['josuke'], { leader: 'josuke' });
    await S.run(async (S2) => {
      await beatCalendar(S2);
      await beatRoadMorning(S2);
      await beatBusStop(S2);
    }, { keepLocked: true });
    // 节拍 4 自由走动：U 修复教学（45 s 后箭头指去学校）
    setupRoadFree(S);
    await S.run(async (S2) => { S2.hint('按 U：疯狂钻石的修复（对着坏掉的东西按）　E 调查', 8); });
    await S.until(() => !!F().toGate && !S.busy);
    // 节拍 5 → 序1 → 节拍 7 → 节拍 8
    await S.run(async (S2) => {
      await beatGate(S2);
      await PRO().fightJotaro(S2);
      await beatPhoto(S2);
      await beatRoadPm(S2);
    }, { keepLocked: true });
    // 节拍 9 超市（清单拿齐、或者 60 s → 劫匪）
    setupMarket();
    await S.run(marketIn);
    const t9 = now();
    await S.until(() => ((shop && shop.all()) || now() - t9 > 60) && !S.busy);
    // 劫匪 → 节拍 10 送奶工 → 节拍 11 那天夜里
    await S.run(async (S2) => {
      await robberScene(S2);
      await beatMilkman(S2);
      await beatRyoheiNight(S2);
    }, { keepLocked: true });
    // 节拍 12 三天后的雨：仗助 / 承太郎（Q 换），康一灰着
    S.party(['josuke', 'jotaro4', 'koichi'], { leader: 'josuke' });
    S.leadable('koichi', false, { msg: KO_MSG });
    setupHouseRain();
    await S.run(rainVisit);
    T().memberTalk({ koichi: talkKoichi12, jotaro4: talkJotaro12 });
    const t12 = now();
    T().goal(S, { x: 250, y: 168, h: 30, label: '水洼', delay: 18, every: 15, done: () => !!F().puddle,
      text: '门口的水洼有点怪：按 Q 换成承太郎，走过去按 U' });
    await S.until(() => (F().puddle || now() - t12 > 40) && !S.busy);
    Object.assign(G.STAGES.house_pro, { hotspots: [], npcs: [], triggers: [] });
    // 进屋 → 序2 段 1 → 段 2 → 节拍 14 → 节拍 15
    await S.run(async (S2) => {
      await livingIntro(S2);
      await PRO().fightAqua(S2);
      await afterTrap(S2);
      await chaseIntro(S2);
      await PRO().chaseAngelo(S2);
      PRO().closeGlove();
      await beatAngeloRock(S2);
      await beatAfterRain(S2);
    }, { keepLocked: true });
  };
  // 整章测试（tools/dev/p4_play.js）对照的剧情标记：打一遍下来这些都要出现，缺了就算没通过
  G.STORY.prologue.marks = ['pro_calendar', 'pro_road_jotaro', 'pro_josuke_enter', 'pro_hair1', 'pro_nose_fixed', 'pro_pot', 'pro_gate',
    'pro_hair2', 'pro_ts_dodge', 'pro_photo', 'pro_tomoko_throw', 'pro_hair3', 'pro_robber_down', 'pro_knife_horn', 'pro_sink_face',
    'pro_milk', 'pro_night', 'pro_silhouette', 'pro_ryohei_cap', 'pro_rain3', 'pro_puddle_face', 'pro_vapor_face', 'pro_glove',
    'pro_aqua_trapped', 'pro_angelo_caught', 'pro_bow_arrow', 'pro_angelo_rock', 'pro_tbc'];
})();
