// 第9章　国道隧道 / 宇宙人、公路之星与猫草（开发脚本 第四部/docs/第9章_开发脚本.md；地图后缀 _ch9）。整章流程：
//   节拍 1 篇章卡 → 2 上学路边的宇宙人（未起隆变鞋、入队、自由走动）→ 3 露伴宅的骰子（小游戏）→ 4 骰子说话了、客厅着火
//   → 5 几天后的国道隧道（第 14 战段 1）→ 段 2 海边国道追车 → 6 医院走廊找 304（自由走动）→ 7 病房（段 3 Boss）、修好裕也的腿
//   → 插曲 阁楼的猫草（早人当队长）→ To Be Continued。
//   借别章的人（亿泰 第2章、露伴 第5章、川尻浩作 第7章）还没合进来时用剪影占位：同一个 id，图集到了自动用正式的（cast()）。
//   战斗和小游戏在 story/p4_ch9_fights.js（G.P4CH9）。克制：着火只烧窗帘；吸养分只有数字和剪影；打裕也是喜剧式飞进枕头堆。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const FT = () => G.P4CH9;
  const F = () => G.flags;
  const now = () => (G.clk ? G.clk.world : 0);
  const NAME_TOP = 100;
  const { base, walls } = G.p4Stage;

  Object.assign(G.NAMES, { mikitaka: '未起隆', yuya: '裕也', highway: '公路之星', hayato: '早人', straycat: '猫草',
    okuyasu: '亿泰', rohan: '露伴', kosaku: '爸爸', nurse9: '护士' });
  // 早人只在插曲里走路（不打架）：走速照开发脚本
  if (!G.KITS.hayato) G.KITS.hayato = { hp: 60, speed: 58 };
  if (!G.KITS.mikitaka) G.KITS.mikitaka = { hp: 100, speed: 64 };

  // ---------------------------------------------------------------- 借别章的人：图集还没合进来就用剪影
  //   [正式 cid, 占位用的底子]；占位版身上打一层深紫剪影色，名字照常显示
  const BORROW = { okuyasu: 'thug_b', rohan: 'flirt', kosaku: 'robber' };
  const has = (cid) => !!(G.D && G.D.chars && G.D.chars[cid]);
  function cast(S, cid, x, y, o = {}) {
    const real = has(cid);
    const a = S.spawn(real ? cid : BORROW[cid], x, y, Object.assign({ id: cid, name: G.NAMES[cid] }, o));
    if (!real || o.silhouette) a.tint = { color: '#160c24', k: real ? 0.9 : 0.82 };
    return a;
  }
  G.P4CH9_cast = cast;
  // 对话：借来的人还没头像时不出头像框（S.say 自己会判断），只出名字
  const say = (S, who, text, o = {}) => S.say(who, text, Object.assign({ name: G.NAMES[who] }, o));

  const ST = G.STAGES;
  ST.road_ch9 = base('road_ch9', 'morioh_road', 960, { state: { pm: 1 } });
  ST.parlor_ch9 = base('parlor_ch9', 'rohan_parlor', 480, { state: { fire: 0 }, obstacles: walls(10, 470, 480) });
  ST.tunnel_ch9 = base('tunnel_ch9', 'route_tunnel', 960, { music: 'tension', state: { room: 0 } });
  ST.highway_ch9 = base('highway_ch9', 'national_road', 960, { music: 'battle', state: { speed: 1, pm: 1 } });
  ST.corridor_ch9 = base('corridor_ch9', 'hospital_corridor', 640, { music: 'tension', state: { pm: 1 } });
  ST.ward_ch9 = base('ward_ch9', 'hospital_room', 320, { music: 'tension', obstacles: walls(54, 312, 320) });
  ST.attic_ch9 = base('attic_ch9', 'kawajiri_attic', 320, { music: 'tension', state: { lamp: 0 }, obstacles: walls(16, 304, 320) });

  const pool = (cid) => G.party._actor(cid);
  function place(S, cid, x, y, facing) {
    const a = pool(cid), W = G.world;
    Object.assign(a, { x, y, z: 0, facing: facing || 1, follow: null, hold: false, script: null, state: 'idle', remove: false, rot: 0, alpha: 1, visible: true });
    if (W.player !== a) a.team = 'npc';
    a.play(a.idleAnim || 'idle');
    W.stage.add(a);
    return a;
  }
  const snapTo = (o) => { G.world.focus = o; G.world.snapCamera(); };
  const focus = (o) => { G.world.focus = o; };
  const smoke = (S, x, y) => { S.sfx('pop', 0.8); S.fx('smoke', { x, y, n: 8, rise: 10, life: 0.6, colour: '#e8e8f0' }, { life: 0.8 }); };

  // ================================================================ 节拍 2 宇宙人（road_ch9，傍晚）
  async function beatAlien(S) {
    const p = S.player;
    await S.setStage('road_ch9', { x: 200, y: 160, facing: 1, music: 'daily', fade: false });
    S.state('pm', 1);
    const ok = cast(S, 'okuyasu', 176, 154, { facing: 1 });
    const mk = S.spawn('mikitaka', 300, 150, { id: 'mikitaka', facing: -1, name: '支仓未起隆' });
    S.pose(mk, 'guard');                    // 抱着膝盖蹲着
    snapTo({ x: 250 });
    await S.fadeIn(0.6);
    S.location('morioh', { y: NAME_TOP });
    await say(S, 'okuyasu', '仗助，你看路边那家伙。抱着膝盖盯着天看了一个钟头了。', { expr: 'shock' });
    await S.say('josuke', '……是在等什么人吧。');
    S.unpose(mk);
    S.face(mk, -1);
    await S.walk(mk, 262, 156, { speed: 40 });
    S.mark('ch9_alien');
    await S.say('mikitaka', '你们好。我是从麦哲伦星云来的宇宙人。');
    S.nameCard('mikitaka', { y: NAME_TOP });
    await S.wait(0.6);
    await S.say('josuke', '……哈？', { expr: 'shock' });
    await say(S, 'okuyasu', '宇宙人！真的假的！', { expr: 'smile' });
    await S.say('mikitaka', '我今年 216 岁。飞船坏了，回不去。');
    await S.say('josuke', '这年头连骗子都这么有想象力啊。');
    await S.say('mikitaka', '不信的话，我变给你们看。');
    // 一团烟：人不见了，地上多了一只运动鞋；再一团烟，变回来
    smoke(S, mk.x, mk.y - 12);
    mk.visible = false;
    const shoe = T().prop(S, 'ch9_sneaker', mk.x, mk.y + 1, { id: 'shoe', frame: 0 });
    S.mark('ch9_sneaker');
    await S.wait(0.9);
    await say(S, 'okuyasu', '变、变成鞋了！', { expr: 'shock' });
    await S.say('josuke', '……这不是替身？', { expr: 'shock' });
    smoke(S, mk.x, mk.y - 6);
    if (shoe) shoe.remove = true;
    mk.visible = true;
    await S.say('mikitaka', '替身是什么？我只是会变形而已。');
    await S.say('josuke', '喂，宇宙人。……你能变成骰子吗？', { expr: 'smile' });
    await S.say('mikitaka', '骰子？那种小方块？三秒钟就行。');
    await S.say('josuke', '我知道一个有钱又讨厌的漫画家。咱们去跟他玩一把。', { expr: 'smile' });
    await say(S, 'okuyasu', '我得回家给老爸做饭了。你们小心点啊。');
    S.walk(ok, -30, 154, { speed: 70 }).then(() => { ok.remove = true; }, G.cancelIgnore);
    await S.wait(0.6);
    // 未起隆入队：跟着走，不能当队长（他不会打架）
    mk.remove = true;
    const m2 = place(S, 'mikitaka', 262, 156, -1);
    void m2;
    S.party(['josuke', 'mikitaka'], { leader: 'josuke' });
    S.leadable('mikitaka', false, { msg: '未起隆：「打架？我只会变形。」' });
    S.mark('ch9_join');
    focus(null);
    p.visible = true;
  }
  function setupRoadFree(S) {
    const st = G.world.stage;
    st.hotspots.push(
      { id: 'sky', x: 300, y: 150, r: 20, label: '天空', use: async (S2) => { await S2.say('mikitaka', '我的飞船就停在那片云后面。……开玩笑的。'); F().sky = true; } },
      { id: 'vending', x: 531, y: 150, r: 18, label: '自动售货机', use: async (S2) => { await S2.say(null, '未起隆盯着售货机看了半天。'); await S2.say('mikitaka', '这台机器在说话。'); F().vend = true; } },
      { id: 'busstop', x: 452, y: 150, r: 14, label: '公交站牌', use: async (S2) => { await S2.say(null, '去露伴老师家的那条路，在右边。'); } },
    );
    T().memberTalk({ mikitaka: async (S2) => { await S2.say('mikitaka', '我变的骰子，点数想要几就是几。'); } });
    st.triggers.push({ x0: 920, x1: 1000, run: async () => { F().toRohan = true; } });
    T().goal(S, { x: 930, y: 158, label: '露伴宅', delay: 45, every: 15, done: () => !!F().toRohan, text: '往右走，去露伴宅' });
  }

  // ================================================================ 节拍 3 露伴宅的骰子
  async function beatParlor(S) {
    T().memberTalk({});
    await S.setStage('parlor_ch9', { x: 60, y: 160, facing: 1, music: 'daily' });
    S.state('fire', 0);
    const mk = S.actor('mikitaka');
    const rh = cast(S, 'rohan', 318, 150, { facing: -1 });
    T().prop(S, 'ch9_candle', 280, 150, { id: 'candle', frame: 0, z: 22 });
    S.location('rohan9', { y: NAME_TOP });
    const p = S.player;
    await S.walk(p, 238, 156, { speed: 60 });
    if (mk) { mk.follow = null; await S.walk(mk, 210, 160, { speed: 60 }); }
    S.face(p, 1);
    S.mark('ch9_parlor');
    await say(S, 'rohan', '东方仗助？稀客。……来道歉的？', { expr: 'smile' });
    await S.say('josuke', '来跟老师玩一把。三颗骰子比大小，输的人掏钱。', { expr: 'smile' });
    await say(S, 'rohan', '赌博？我对钱没兴趣。不过——');
    await say(S, 'rohan', '你输了，就让我把你从头到脚“读”一遍。', { expr: 'smile' });
    await S.say('josuke', '行啊。我赢了，老师出十万日元。');
    // 未起隆钻进仗助口袋，变成第三颗骰子
    if (mk) { smoke(S, mk.x, mk.y - 10); mk.visible = false; }
    await S.say('mikitaka', '（小声）准备好了。我是那颗有点亮的。', { name: '口袋里的声音' });
    S.music('tension', 0.5);
    await S.vs({ key: 'dice9', hero: 'josuke', enemy: { cid: rh.cid, anim: 'idle' } });
    G.uifx.vsTag('dice9');
    return rh;
  }

  // ================================================================ 节拍 4 骰子说话了 → 着火
  async function beatFire(S) {
    const p = S.player, rh = S.actor('rohan'), mk = S.actor('mikitaka');
    G.uifx.vsTag(null);
    S.music('tension', 0.4);
    await say(S, 'rohan', '……第三颗骰子。刚才自己翻了个身。', { expr: 'rage' });
    await S.say('josuke', '老、老师看错了吧？', { expr: 'shock' });
    S.sfx('pop', 0.6);
    S.sfxText('啊', { wx: 282, wy: 150, wz: 26 }, { dur: 0.8 });
    S.mark('ch9_dice_talk');
    await say(S, 'rohan', '骰子……说话了？！', { expr: 'shock' });
    if (mk) { mk.x = 300; mk.y = 160; mk.visible = true; smoke(S, mk.x, mk.y - 8); }
    await S.say('mikitaka', '被捏得太疼了。', { expr: 'shock' });
    await S.say('josuke', '糟了！', { expr: 'shock' });
    await say(S, 'rohan', '东方仗助！你这个骗子——', { expr: 'rage' });
    // 扭成一团：撞翻茶几上的蜡烛
    if (rh) S.walk(rh, p.x + 14, p.y, { speed: 120 }).catch(G.cancelIgnore);
    await S.wait(0.3);
    S.sfx('thud', 0.9); S.shake(3, 0.4);
    S.sfxText('咚！', p, { dur: 0.7 });
    const cd = S.actor('candle');
    if (cd) { T().setFrame(cd, 2); await S.arc(cd, 260, 152, 10, 0.4, { z1: 0 }); }
    S.sfx('fire_burst', 0.8);
    for (let i = 1; i < 4; i++) G.defer(i * 0.7, () => S.sfx('fire', 0.5));
    await S.animate(1.0, (k) => S.state('fire', k));
    S.mark('ch9_fire');
    await say(S, 'rohan', '我的房子！', { expr: 'shock' });
    await S.say('josuke', '我能修！……可是火太大了，先跑！', { expr: 'shock' });
    S.walk(mk, -20, 160, { speed: 110 }).catch(G.cancelIgnore);
    await S.walk(p, 10, 158, { speed: 110, anim: 'run' });
    await S.narrate('后来，露伴老师家的客厅烧掉了一半。……那十万日元，我一分也没拿到。', { pos: 'top' });
    await S.fadeOut(0.6);
  }

  // ================================================================ 节拍 5 几天后的国道隧道
  async function beatTunnel(S) {
    S.leave('mikitaka', { drop: true });
    S.party(['josuke'], { leader: 'josuke' });
    await S.setStage('tunnel_ch9', { x: 40, y: 160, facing: 1, music: 'tension', fade: false });
    S.state('room', 0);
    snapTo(S.player);
    await S.fadeIn(0.5);
    await S.title('days9', { y: 110 });
    S.location('tunnel9', { y: NAME_TOP });
    await S.narrate('露伴老师从那天起就没回过家。最后有人看见他，是在国道的隧道里。', { pos: 'top' });
    const p = S.player;
    await S.walk(p, 380, 158, { speed: 56 });
    S.mark('ch9_tunnel');
    S.sfx('rumble', 0.5);
    await S.animate(0.8, (k) => S.state('room', k));
    S.state('room', 1);
    S.mark('ch9_room');
    await say(S, 'rohan', '……别进来……这是陷阱……', { name: '门里的声音' });
    await S.say('josuke', '露伴老师？！墙上怎么会有个房间……', { expr: 'shock' });
    // 脚印一串串朝仗助走过来
    for (let i = 0; i < 5; i++) {
      G.defer(i * 0.25, () => { T().prop(S, 'ch9_foot', 600 - i * 22, 160 - (i % 2) * 4, { id: 'ft' + i }); S.sfx('footstep' + (i % 4), 0.6); });
    }
    await S.wait(1.4);
    S.standCard('highway', { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.say('josuke', '脚印……在动？！', { expr: 'shock' });
    for (let i = 0; i < 5; i++) { const f = S.actor('ft' + i); if (f) f.remove = true; }
  }

  // ================================================================ 节拍 6 医院走廊（自由走动）
  const ROOMS = {
    door_301: '病房里，一个老爷爷正在打呼噜。',
    door_302: '小孩躺在床上看电视。「哥哥，你的头发好酷！」',
    door_303: '空床。被子叠得整整齐齐。',
    door_305: '门锁着。门上挂着「请勿打扰」。',
  };
  function setupCorridor(S) {
    const st = G.world.stage, an = (G.D.bg.hospital_corridor && G.D.bg.hospital_corridor.anchors) || {};
    const at = (k, d) => (an[k] ? an[k][0] : d);
    for (const [k, line] of Object.entries(ROOMS)) {
      st.hotspots.push({ id: k, x: at(k, 100), y: 150, r: 18, label: k.slice(5) + ' 号病房', use: async (S2) => { await S2.say(null, line); F()['seen_' + k] = true; } });
    }
    st.hotspots.push({ id: 'door_304', x: at('door_304', 417), y: 150, r: 18, label: '304 号病房',
      use: async (S2) => { await S2.say(null, '门牌上写着「噴上」。'); await S2.say('josuke', '……就是这里。'); F().door304 = true; } });
    st.hotspots.push({ id: 'wheelchair', x: at('wheelchair', 374), y: 152, r: 16, label: '轮椅', tags: ['fix'], fx: at('wheelchair', 374), fy: 136,
      use: async (S2) => { await S2.say(null, '轮椅的一个轮子歪了。'); },
      look: async (S2) => { if (F().chair) { await S2.say('josuke', '……已经修好了。'); return; } F().chair = true; await S2.say('josuke', '……顺手。'); } });
    S.spawn('nurse9', at('nurse_station', 605) - 10, 152, { id: 'nurse9', facing: -1, name: '护士', label: '护士',
      talk: async (S2) => { await S2.say(null, '304 的病人？前几天骑摩托摔的，可他总说自己“在跑步”。', { name: '护士' }); F().nurse = true; } });
    T().goal(S, { x: at('door_304', 417), y: 152, label: '304', delay: 30, every: 15, done: () => !!F().door304, text: '找到裕也的病房：门牌上写着名字' });
  }
  async function corridorIn(S) {
    await S.setStage('corridor_ch9', { x: 30, y: 160, facing: 1, music: 'tension' });
    S.location('hospital9', { y: NAME_TOP });
    S.mark('ch9_corridor');
    await S.say('josuke', '它是闻着气味追过来的。……本体一定躺在附近哪家医院里，一动不动。');
    S.hint('一间一间看门牌（E 调查）', 6);
  }

  // ================================================================ 节拍 7 病房
  async function beatWard(S) {
    S.mark('ch9_door304');
    await S.setStage('ward_ch9', { x: 60, y: 160, facing: 1, music: 'tension' });
    const yu = S.spawn('yuya', 168, 151, { id: 'yuya', facing: 1, name: '喷上裕也' });
    S.pose(yu, 'down');
    yu.z = 30;          // 躺在床上（床面比地面高 30 px 左右）
    T().prop(S, 'ch9_flowers', 106, 140, { id: 'fl1', z: 30 });
    T().prop(S, 'ch9_flowers', 214, 150, { id: 'fl2', z: 18 });
    T().prop(S, 'ch9_flowers', 280, 158, { id: 'fl3' });
    const p = S.player;
    await S.walk(p, 110, 160, { speed: 50 });
    S.face(p, 1);
    await S.say('yuya', '来了啊，东方仗助。', { expr: 'smile' });
    S.nameCard('yuya', { y: NAME_TOP });
    S.mark('ch9_yuya');
    await S.say('yuya', '我摔断了腿，躺在这儿动不了。可公路之星能替我去“吃”。');
    await S.say('yuya', '吃够了别人的养分，我的伤就能好。你的养分最多了。', { expr: 'smile' });
    await S.say('josuke', '……拿露伴老师当饭吃的就是你啊。', { expr: 'rage' });
    S.music('battle', 0.4);
    await S.vs({ key: 'highway', hero: 'josuke', enemy: { cid: 'highway', anim: 'idle' } });
    G.uifx.vsTag('highway');
  }
  async function afterWard(S) {
    const p = S.player, yu = S.actor('yuya');
    G.uifx.vsTag(null);
    S.music('victory', 0.6);
    // 喜剧收尾：连人带枕头打进被子堆里
    await S.walk(p, 128, 158, { speed: 70 });
    S.face(p, 1);
    await S.summon(p, { dur: 0.1, rise: 4 });
    S.standAct(p, 'rush', { dx: 18, z: 10, hold: true, jitter: 1 });
    for (let i = 0; i < 8; i++) G.defer(i * 0.08, () => S.sfx('punch', 0.5));
    S.sfxText('DORARARA', { wx: 150, wy: 151, wz: 34 }, { dur: 0.8 });
    S.shake(3, 0.7);
    await S.wait(0.7);
    S.standAct(p, 'punch', { dx: 22, z: 10, dur: 0.5 });
    S.sfx('punch_heavy', 1);
    if (yu) await S.arc(yu, 206, 151, 16, 0.4, { z1: 30 });
    S.sfx('thud', 0.7);
    S.sfxText('噗', { wx: 186, wy: 151, wz: 30 }, { dur: 0.7 });
    S.recall(p);
    S.mark('ch9_yuya_down');
    await S.say('yuya', '……我认输。你的养分我一口都不碰了。', { expr: 'shock' });
    await S.say('josuke', '把吸走的还给露伴老师。');
    await S.say('yuya', '我已经放开了。他马上就能醒。');
    await S.say('josuke', '顺便……你的腿我给你修好吧。省得你再去吃人。');
    await S.summon(p, { dur: 0.12, rise: 4 });
    S.standAct(p, 'reach', { dx: 20, z: 10, dur: 0.9 });
    P4().fixGlow(S, yu ? yu.x : 186, 132);
    await S.wait(0.7);
    S.recall(p);
    S.mark('ch9_yuya_fix');
    await S.say('yuya', '……你这家伙，真是个怪人。以后有事找我，我的鼻子很灵。', { expr: 'smile' });
    await S.fadeOut(0.8);
  }

  // ================================================================ 插曲 阁楼的猫草（早人）
  async function interludeIn(S) {
    S.party(['hayato'], { leader: 'hayato' });
    await S.setStage('attic_ch9', { x: 60, y: 164, facing: 1, music: 'tension', fade: false });
    S.state('lamp', 0);
    T().prop(S, 'ch9_dish', 150, 158, { id: 'dish', frame: 0 });
    S.spawn('straycat', 169, 156, { id: 'straycat', facing: -1, name: '猫草' });
    snapTo(S.player);
    await S.fadeIn(0.6);
    await S.title('interlude9', { y: 110 });
    S.location('kawajiri9', { y: NAME_TOP });
    S.nameCard('hayato', { y: NAME_TOP });
    S.mark('ch9_attic');
    await S.narrate('爸爸最近变了。他会在半夜，一个人爬上阁楼。', { pos: 'top' });
    S.hint('太暗了。先把梁上的灯泡拉亮（E）', 6);
  }
  async function useBulb(S) {
    if (F().lamp) { await S.say(null, '灯泡亮着，晃来晃去。'); return; }
    F().lamp = true;
    S.sfx('blip', 0.8);
    S.state('lamp', 1);
    S.mark('ch9_lamp');
    await S.say('hayato', '……那是什么？光斑那里，有一盆草。');
  }
  async function catShoot(S) {
    if (F().catShot) return;
    F().catShot = true;
    const p = S.player, cat = S.actor('straycat');
    if (cat) { cat.facing = p.x > cat.x ? 1 : -1; S.pose(cat, 'puff'); }
    S.sfx('sting_shock', 0.6);
    await S.wait(0.5);
    if (cat) S.pose(cat, 'shoot');
    S.sfx('whoosh', 0.8);
    const b = T().prop(S, 'ch9_bubble', cat ? cat.x : 169, 156, { id: 'bubble', z: 14 });
    if (b) S.arc(b, p.x, p.y, 4, 0.6, { z1: 14 }).catch(G.cancelIgnore);
    const r = await S.press({ key: 'dodge', window: 0.6, label: '按 K 闪开！' });
    if (b) b.remove = true;
    if (r === 'miss') {
      S.sfx('thud', 0.8); S.shake(2, 0.3);
      S.sfxText('砰', p, { dur: 0.7 });
      S.pose(p, 'hurt');
      await S.wait(0.6);
      S.unpose(p);
      await S.say('hayato', '好、好痛……空气？它朝我吐了一团空气？', { expr: 'shock' });
    } else {
      S.sfx('dodge', 0.8);
      await S.arc(p, p.x - p.facing * 18, p.y, 6, 0.25);
      await S.say('hayato', '……它朝我吐了什么东西！', { expr: 'shock' });
    }
    if (cat) S.unpose(cat);
  }
  async function useCat(S) {
    if (!F().lamp) { await S.say(null, '太暗了，看不清。'); return; }
    if (!F().catShot) await catShoot(S);
    if (F().catSeen) { await S.say('straycat', '喵。'); return; }
    F().catSeen = true;
    S.mark('ch9_cat');
    await S.say('hayato', '……草，长着猫的脸？', { expr: 'shock' });
    await S.say('straycat', '喵——', { expr: 'rage' });
  }
  function setupAttic(S) {
    const st = G.world.stage, an = (G.D.bg.kawajiri_attic && G.D.bg.kawajiri_attic.anchors) || {};
    const at = (k, d) => (an[k] ? an[k][0] : d);
    st.hotspots.push(
      { id: 'bulb', x: at('bulb', 200), y: 154, r: 18, label: '灯泡的拉绳', use: useBulb },
      { id: 'window', x: at('window', 160), y: 148, r: 14, label: '小窗', use: async (S2) => { await S2.say(null, '窗外是邻居家的屋顶。'); } },
      { id: 'birdcage', x: at('chest', 230), y: 150, r: 16, label: '鸟笼', use: async (S2) => { await S2.say(null, '空鸟笼。以前养过一只鹦鹉。'); } },
      { id: 'boxes', x: at('boxes', 30) + 6, y: 152, r: 20, label: '纸箱',
        use: async (S2) => { if (F().hideNow) { F().hidden = true; S2.mark('ch9_hide'); await S2.say('hayato', '（躲好了……别出声。）'); } else await S2.say(null, '旧纸箱，写着「浩作 大学」。'); } },
      { id: 'cat', x: 169, y: 158, r: 22, label: '奇怪的草', use: useCat },
    );
    // 靠近光斑就吐空气弹（灯亮以后）
    st.triggers.push({ x0: 120, x1: 220, cond: () => !!F().lamp && !F().catShot, run: catShoot });
  }
  async function fatherScene(S) {
    const p = S.player;
    S.hint(null);
    S.sfx('creak', 0.8);
    await S.wait(0.4);
    S.sfx('footstep1', 0.6);
    await S.say('hayato', '有人上来了！', { expr: 'shock' });
    F().hideNow = true;
    S.hint('躲到纸箱后面（走过去按 E）', 8);
  }
  async function fatherCome(S) {
    const p = S.player;
    S.hint(null);
    if (!F().hidden) {
      // 没躲：爸爸背对着他，没发现。早人缩到墙角
      await S.walk(p, 24, 156, { speed: 70 });
      S.face(p, 1);
    } else { p.x = 22; p.y = 154; p.facing = 1; }
    const fa = cast(S, 'kosaku', 60, 164, { facing: 1, silhouette: true });
    fa.alpha = 0;
    S.sfx('creak', 0.7);
    await S.animate(0.5, (k) => { fa.alpha = k; });
    await S.walk(fa, 150, 158, { speed: 34 });
    S.mark('ch9_father');
    await S.say('kosaku', '好孩子。……今天也晒到太阳了吗？', { name: '爸爸', portrait: false });
    S.sfx('drip', 0.6);
    await S.say('kosaku', '你吃掉的那个，是谁都不会知道的。', { name: '爸爸', portrait: false });
    S.sfx('menacing', 0.5);
    await S.wait(0.8);
    await S.walk(fa, 60, 164, { speed: 34 });
    await S.animate(0.4, (k) => { fa.alpha = 1 - k; });
    fa.remove = true;
    await S.narrate('那个人……真的是我爸爸吗？', { pos: 'top' });
    S.music('sad', 1.0);
    S.stopMusic(1.2);
    await S.tbc({ hold: 2.0 });
    S.mark('ch9_tbc');
  }

  // ================================================================ 第9章主流程
  G.STORY.ch9 = async function (S) {
    if (T().resetCounters) T().resetCounters();
    P4().clearOverlays();
    await S.chapterCard('ch9');
    S.party(['josuke'], { leader: 'josuke' });
    await S.run(async (S2) => { await beatAlien(S2); }, { keepLocked: true });
    // 节拍 2 自由走动 → 右端去露伴宅
    setupRoadFree(S);
    await S.run(async (S2) => { S2.hint('E 调查、和未起隆说话；往右走去露伴宅', 6); });
    await S.until(() => !!F().toRohan && !S.busy);
    await S.run(async (S2) => {
      await beatParlor(S2);
      await FT().dice(S2);
      await beatFire(S2);
      await beatTunnel(S2);
      await FT().tunnel(S2);
      await FT().road(S2);
    }, { keepLocked: true });
    // 节拍 6 医院走廊（自由走动）
    await S.run(async (S2) => { await corridorIn(S2); setupCorridor(S2); });
    await S.until(() => !!F().door304 && !S.busy);
    await S.run(async (S2) => {
      await beatWard(S2);
      await FT().ward(S2);
      await afterWard(S2);
      await interludeIn(S2);
      setupAttic(S2);
    });
    // 插曲：亮灯 → 看猫草 → 有人上来 → 躲 → 爸爸
    await S.until(() => !!F().catSeen && !S.busy);
    await S.run(fatherScene);
    const tHide = now();
    await S.until(() => (F().hidden || now() - tHide > 8) && !S.busy);
    await S.run(fatherCome, { keepLocked: true });
  };
  G.STORY.ch9.marks = ['ch9_alien', 'ch9_sneaker', 'ch9_join', 'ch9_parlor', 'b_dice_start', 'b_dice_win', 'ch9_dice_talk', 'ch9_fire',
    'ch9_tunnel', 'ch9_room', 'b14a_rohan', 'b14a_exit', 'b14b_start', 'b14b_truck', 'ch9_corridor', 'ch9_door304',
    'ch9_yuya', 'b14c_start', 'ch9_yuya_down', 'ch9_yuya_fix', 'ch9_attic', 'ch9_lamp', 'ch9_cat', 'ch9_hide', 'ch9_father', 'ch9_tbc'];
  G.STORY.ch9.packs = ['bg_prologue'];
})();
