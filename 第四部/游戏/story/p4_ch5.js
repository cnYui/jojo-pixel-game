// 第5章　露伴宅 / 漫画家与猎鼠（开发脚本 第四部/docs/第5章_开发脚本.md；地图后缀 _ch5）。整章流程：
//   节拍 1 篇章卡 → 日历地图 → 2 间田拉康一拜访露伴（天堂之门、写命令）→ 3 第二天（门外自由走动）→ 4 亿泰翻窗、仗助闭眼
//   → 第 7 战 → 6 发型的来历（雪夜剪影）、工作室自由走动（U 修墙）→ 7 几天后：承太郎、水渠 → 8 水渠自由走动（承太郎 U）
//   → 9 牧场外：打空罐教学、空狗屋 → 第 8 战段 1 → 11 冰箱、承太郎的手套、虫食、两发子弹 → 12 池塘、捕鼠夹、时停 → 段 2 → 13 「……干得好。」
//   克制：被融在一起的老鼠、牧场主人不画（冰箱门一开就黑屏 + 音效）；“溶解”只用颜色和冒烟；承太郎的手只画手套冒烟。
//   两场战斗在 story/p4_ch5_fights.js（G.P4CH5）；露伴当队长时的 U 演出 G.LOOK.rohan 也在这里。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const C5 = () => G.P4CH5;
  const F = () => G.flags;
  const now = () => (G.clk ? G.clk.world : 0);
  const NAME_TOP = 100;
  const { base, walls } = G.p4Stage;
  const ST = G.STAGES;

  // ================================================================ 名字、地图
  const N = G.NAMES;
  const name = (k, v) => { if (!N[k]) N[k] = v; };
  name('rohan', '露伴'); name('heavensdoor', '天堂之门'); name('hazamada', '间田'); name('okuyasu', '亿泰');
  name('mushikui', '虫食'); name('rat_a', '老鼠'); name('spw_phone', 'SPW');

  ST.map_ch5 = base('map_ch5', 'morioh_map', 320, { yMin: 160, yMax: 170, music: null, obstacles: [] });
  ST.rohan_out_ch5 = base('rohan_out_ch5', 'rohan_house', 480, { music: 'daily', state: { window: 0 } });
  ST.rohan_in_ch5 = base('rohan_in_ch5', 'rohan_studio', 480, { music: 'tension', state: { pages: 0, hole: 0 }, obstacles: walls(44, 472, 480) });
  ST.ditch_ch5 = base('ditch_ch5', 'irrigation_ditch', 640, { music: 'tension' });
  ST.farm_out_ch5 = base('farm_out_ch5', 'farm_out', 480, { music: 'tension', state: { cans: 0 } });
  ST.farm_ch5 = base('farm_ch5', 'farmhouse', 480, { music: 'tension', state: { pan: 0 }, obstacles: walls(44, 472, 480) });
  ST.hill_ch5 = base('hill_ch5', 'hillside', 960, { music: 'tension' });

  // 日历地图：两枚图钉（morioh_map 上没有这两个锚点，开章时补上：只在内存里加，不改背景元数据）
  const PIN_XY = { rohan_house: [228, 48], farm: [58, 70] };
  function ensurePins() {
    const bg = G.D && G.D.bg && G.D.bg.morioh_map;
    if (!bg) return;
    bg.anchors = bg.anchors || {};
    for (const k in PIN_XY) if (!bg.anchors[k]) bg.anchors[k] = PIN_XY[k];
  }
  if (G.P4 && G.P4.CAL) G.P4.CAL.ch5 = { pins: [{ at: 'rohan_house', label: '露伴宅' }, { at: 'farm', label: '牧场' }], stamp: 'stamp' };
  // 发型记录第 4 次：露伴（第 3、4 章要加的话从 5 往后排）
  if (G.P4 && G.P4.hair) G.P4.hair.ROWS[4] = { who: '岸边露伴', where: '露伴宅', said: '“过时的发型”（故意的）', result: '被打穿了墙' };

  // 露伴当队长时按 U：天堂之门把对方“翻开成书”读一读（tags 'read'）。读的内容由调查点自己的 look 演
  G.LOOK.rohan = {
    tags: ['read'], cd: 1, miss: '……这个没什么好读的。',
    run: async (S, p, h) => {
      if (h) S.face(p, h.x > p.x ? 1 : h.x < p.x ? -1 : p.facing);
      await S.summon(p, { dur: 0.14, rise: 4 });
      S.standAct(p, 'write', { dx: 16, z: 4, dur: 0.7 });
      S.sfx('card_flip', 0.8);
      if (h) S.fx('glint', { x: h.x, y: h.y - 14, size: 7 }, { life: 0.4 });
      await S.wait(0.5);
    },
  };

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
  // 还没画的人（亿泰、间田归第2章画）：先拿现成的人顶上，名字照常
  const FALLBACK = { okuyasu: 'thug_b', hazamada: 'thug_a' };
  function npc(S, cid, x, y, o = {}) {
    const real = S.exists(cid) ? cid : FALLBACK[cid] || cid;
    const a = S.spawn(real, x, y, Object.assign({ id: cid, facing: -1, name: G.NAMES[cid] || cid }, o));
    a.speaker = cid;
    return a;
  }
  // 说话：如果说话的人是顶替的，名字用本名、头像不画
  const say = (S, cid, text, o = {}) => {
    const a = S.actor(cid);
    if (a && a.cid !== cid) return S.say(a.cid, text, Object.assign({ name: G.NAMES[cid] || cid, actor: a, portrait: false }, o));
    return S.say(cid, text, o);
  };
  const book = (a, sec) => { if (a) C5().bookOn(a, sec); };
  const unbook = (a) => { if (a && a.mem) a.mem.bookUntil = 0; };
  async function rohanWrite(S, rh, target) {
    S.face(rh, target);
    rh.play('write');
    await S.summon(rh, { dur: 0.14, rise: 4 });
    S.standAct(rh, 'write', { dx: 14, z: 4, dur: 1.0 });
    for (let i = 0; i < 3; i++) { S.sfx('card_flip', 0.6, 1.2 + i * 0.1); await S.wait(0.22); }
    S.fx('glint', { x: target.x, y: target.y - 26, size: 6 }, { life: 0.4 });
    await S.wait(0.3);
    S.recall(rh);
    rh.play('idle');
  }

  // ================================================================ 节拍 1 篇章卡 → 日历地图
  async function beatCalendar(S) {
    ensurePins();
    S.player.visible = false;
    await S.setStage('map_ch5', { x: 160, y: 165, music: null });
    // 日历地图的红章是读 ui.map.stamp 的：这一章临时换成「1999年6月」那枚，演完换回去
    const mp = (G.D && G.D.ui && G.D.ui.map) || {}, old = mp.stamp;
    if (mp.stamp_ch5) mp.stamp = mp.stamp_ch5;
    let cal = null;
    try {
      cal = await P4().calendar(S, 'ch5', { hold: 1.8 });
      S.mark('ch5_calendar');
      await S.fadeOut(0.45);
    } finally {
      if (cal) cal.close();
      mp.stamp = old;
    }
  }

  // ================================================================ 节拍 2 拜访漫画家
  async function beatVisit(S) {
    const p = S.player;      // 这一段的队长是康一
    await S.setStage('rohan_out_ch5', { x: 40, y: 160, facing: 1, music: 'daily', fade: false });
    p.visible = true;
    const hz = npc(S, 'hazamada', 70, 156, { facing: 1 });
    snapTo({ x: 200 });
    await S.fadeIn(0.6);
    S.location('rohan_house', { y: NAME_TOP });
    S.walk(hz, 214, 152, { speed: 46 }).catch(G.cancelIgnore);
    await S.narrate('1999 年 6 月。出院的间田学长非要拉我来见一位漫画家。', { pos: 'top' });
    await S.walk(p, 186, 158, { speed: 46 });
    await S.until(() => !hz.script);
    S.face(hz, -1);
    S.mark('ch5_visit');
    await say(S, 'hazamada', '岸边露伴老师就住在这儿！《粉红暗黑少年》的作者！', { expr: 'smile' });
    await S.say('koichi', '我只在杂志上翻过几页……这样突然上门，真的好吗？', { expr: 'shock' });
    S.sfx('creak', 0.8);
    await S.wait(0.5);
    const rh = S.spawn('rohan', 240, 130, { id: 'rohan', facing: 1, name: '岸边露伴' });
    rh.mem = rh.mem || {};
    await S.walk(rh, 240, 146, { speed: 36 });
    S.face(hz, rh); S.face(p, rh);
    await S.say('rohan', '两位请进。我刚画完一份原稿，正想找人看看。');
    S.nameCard('rohan', { y: NAME_TOP });
    await S.wait(0.6);
    await S.say('koichi', '（……他好像早就知道我们会来。）');
    // 进工作室
    await S.setStage('rohan_in_ch5', { x: 200, y: 160, facing: 1, music: 'tension' });
    Object.assign(hz, { x: 168, y: 156, facing: 1, remove: false });
    G.world.stage.add(hz);
    Object.assign(rh, { x: 300, y: 152, facing: -1, remove: false });
    G.world.stage.add(rh);
    focus({ x: 250 });
    await say(S, 'hazamada', '这、这是真正的生原稿……！', { expr: 'shock' });
    await S.say('koichi', '画得好细……连汗珠都在动一样。');
    // 读原稿 → 白闪 → 两人脸上翻开书页
    S.sfx('card_flip', 0.9);
    S.flash(0.3, 1, '#fff8e0');
    S.shake(2, 0.2);
    book(p, 30); book(hz, 30);
    p.hold = true; p.play('shock'); hz.play('idle');
    S.mark('ch5_book');
    await S.summon(rh, { dur: 0.16, rise: 6 });
    S.standCard('heavensdoor', { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.wait(0.9);
    await S.say('rohan', '天堂之门。看过我原稿的人，会像书一样翻开。');
    await S.walk(rh, p.x + 26, p.y, { speed: 40 });
    S.face(rh, p);
    S.sfx('card_flip', 0.7);
    await S.say('rohan', '“替身：回音”……从蛋里孵出来的？太有意思了。', { expr: 'smile' });
    await rohanWrite(S, rh, p);
    S.mark('ch5_write');
    await S.say('rohan', '写上“不能攻击岸边露伴”。再借几页当素材。');
    S.sfx('card_flip', 1, 0.8);
    S.fx('glint', { x: p.x, y: p.y - 30, size: 8 }, { life: 0.5 });
    await S.walk(rh, hz.x + 24, hz.y, { speed: 40 });
    await S.say('rohan', '你嘛……没什么可读的。“回家，忘了今天”。');
    await rohanWrite(S, rh, hz);
    unbook(hz);
    await S.walk(hz, 20, 156, { speed: 30 });
    hz.remove = true;
    S.recall(rh);
    unbook(p);
    p.hold = false; p.play('idle');
    await S.fadeOut(0.5);
    await S.narrate('……等我回过神，已经站在自己家门口了。', { pos: 'top' });
    await S.narrate('我刚才，是不是睡着了？', { pos: 'top' });
    rh.remove = true;
  }

  // ================================================================ 节拍 3 第二天（门外自由走动）
  async function talkHazamada(S, me) {
    if (F().hz1) { await say(S, 'hazamada', '我是来送慰问信的！……老师就是不开门。'); return; }
    F().hz1 = true;
    await say(S, 'hazamada', '老师今天不见客。我在这儿站了一个钟头了。');
    await S.say('josuke', '……间田，你是不是也被写了什么？', { expr: 'shock' });
    await say(S, 'hazamada', '写？写什么？我只是忠实的读者！');
  }
  async function talkOkuyasu(S) {
    await say(S, 'okuyasu', '康一那家伙，进去的时候跟丢了魂似的。');
    await say(S, 'okuyasu', '……右边那扇窗好像没锁。');
  }
  function setupDoor(S) {
    const st = G.world.stage;
    npc(S, 'hazamada', 200, 152, { facing: 1, label: '间田', talk: talkHazamada });
    npc(S, 'okuyasu', 120, 160, { facing: 1, label: '亿泰', talk: talkOkuyasu });
    st.hotspots.push(
      { id: 'window', x: 317, y: 150, r: 18, ry: 14, label: '一楼的窗', use: async () => { F().window = true; } },
      { id: 'gate', x: 240, y: 150, r: 14, label: '铁门', use: async (S2) => { S2.sfx('creak', 0.5); await S2.say('josuke', '锁上了。……门铃按了也没人应。'); } },
      { id: 'plate', x: 202, y: 150, r: 10, label: '门牌', use: async (S2) => { await S2.say(null, '门牌上写着「岸辺」。'); } },
    );
    T().goal(S, { x: 317, y: 150, label: '窗', delay: 45, every: 15, done: () => !!F().window, text: '右边那扇窗没锁：走过去按 E' });
  }
  async function beatNextDay(S) {
    const p = S.player;
    await S.setStage('rohan_out_ch5', { x: 40, y: 162, facing: 1, music: 'tension', fade: false });
    p.visible = false;
    snapTo({ x: 200 });
    await S.title('next_day', { y: 110 });
    await S.fadeIn(0.5);
    S.mark('ch5_next_day');
    // 康一一个人走过去，比昨天小了一圈
    const ko = place(S, 'koichi', 20, 158, 1);
    ko.scale = 0.94;
    p.x = -20; p.visible = true;
    const ok = npc(S, 'okuyasu', -40, 162, { facing: 1 });
    S.walk(ko, 150, 156, { speed: 30 }).catch(G.cancelIgnore);
    await S.wait(1.2);
    S.walk(ok, 60, 162, { speed: 50 }).catch(G.cancelIgnore);
    await S.walk(p, 90, 160, { speed: 50 });
    await S.say('josuke', '喂，康一！……你是不是瘦了？', { expr: 'shock' });
    S.face(ko, -1);
    await say(S, 'okuyasu', '手上全是墨水啊。你昨天到底干嘛去了？');
    await S.say('koichi', '露伴老师说……今天要画到二十页。我得去帮忙。', { expr: 'smile' });
    S.face(ko, 1);
    await S.walk(ko, 240, 148, { speed: 34 });
    S.sfx('creak', 0.7);
    await S.walk(ko, 240, 132, { speed: 30 });
    ko.visible = false;
    ok.remove = true;
    await S.say('josuke', '……不对劲。那家伙从来不会那样笑。');
  }

  // ================================================================ 节拍 4 翻窗 → 闭眼
  async function beatWindow(S) {
    const p = S.player, ok = S.actor('okuyasu'), hz = S.actor('hazamada');
    S.hint(null);
    if (hz) hz.talk = null;
    if (ok) ok.talk = null;
    S.mark('ch5_window');
    if (ok) {
      await S.walk(ok, 304, 150, { speed: 60 });
      S.face(ok, -1);
    }
    await say(S, 'okuyasu', '我从窗户进去看看。仗助，你守着门口！');
    S.state('window', 1);
    S.sfx('creak', 0.8);
    if (ok) { await S.arc(ok, 318, 140, 18, 0.4); ok.visible = false; }
    await S.wait(0.6);
    for (let i = 0; i < 3; i++) { S.sfx('card_flip', 0.7, 0.9 + i * 0.15); await S.wait(0.25); }
    await S.wait(0.8);
    await S.say('josuke', '……亿泰？喂，亿泰！', { expr: 'shock' });
    await S.walk(p, 240, 148, { speed: 80 });
    S.sfx('creak', 0.9);
    // 工作室：亿泰、康一站着不动，脸上翻开书页
    await S.setStage('rohan_in_ch5', { x: 110, y: 160, facing: 1, music: 'tension' });
    const ok2 = npc(S, 'okuyasu', 70, 150, { facing: 1 });
    const ko = place(S, 'koichi', 62, 168, 1);
    ko.scale = 0.94;
    const rh = S.spawn('rohan', 380, 156, { id: 'rohan', facing: -1, name: '岸边露伴' });
    book(ok2, 999); book(ko, 999);
    focus({ x: 240 });
    await S.say('rohan', '又来一个。你也看看原稿吧，东方仗助。', { expr: 'smile' });
    S.pose(rh, 'pose');
    await S.wait(0.3);
    await S.say('josuke', '……看了就会变成书，对吧。');
    // 闭上眼：画面暗下去
    S.sfx('whoosh', 0.6);
    S.filter('tint', 1, { colour: '#000000' });
    await S.wait(0.4);
    await S.say('josuke', '那我就闭着眼睛打。', { expr: 'rage' });
    S.filter('tint', null);
    S.unpose(rh);
    focus(null);
    S.music('battle', 0.3);
    await S.vs({ key: 'heavensdoor', hero: 'josuke', enemy: { cid: 'rohan', anim: 'pose' } });
    G.uifx.vsTag('heavensdoor');
  }

  // ================================================================ 节拍 6 发型的来历（雪夜剪影）、工作室自由走动
  function snowLayer() {
    const flakes = [];
    for (let i = 0; i < 90; i++) flakes.push({ x: Math.random() * 640, y: Math.random() * 360, v: 20 + Math.random() * 40, r: Math.random() < 0.3 ? 2 : 1 });
    return P4().overlay((g, t) => {
      const a = Math.min(1, t / 0.6);
      g.save();
      g.globalAlpha = a;
      g.fillStyle = '#0c1424'; g.fillRect(0, 0, 640, 360);
      g.fillStyle = '#e8eef8'; g.fillRect(0, 280, 640, 80);                // 积雪的路
      // 车灯（两道光）
      g.fillStyle = 'rgba(255,240,180,0.22)';
      g.beginPath(); g.moveTo(170, 262); g.lineTo(640, 200); g.lineTo(640, 330); g.closePath(); g.fill();
      // 车的剪影（陷在雪里）
      g.fillStyle = '#05070c';
      g.fillRect(70, 236, 110, 34); g.fillRect(92, 214, 64, 24);
      g.fillStyle = '#fff4c0'; g.fillRect(172, 246, 8, 8);
      // 推车的少年：只有背影，飞机头的轮廓
      const sx = 196 + Math.sin(t * 2) * 2;
      g.fillStyle = '#05070c';
      g.fillRect(sx, 226, 16, 40);
      g.fillRect(sx + 2, 210, 13, 16);
      g.fillRect(sx - 6, 204, 20, 7);                                           // 头发往前探出去
      g.fillRect(sx - 8, 236, 10, 5);                                           // 手撑在车上
      g.fillRect(sx + 1, 266, 5, 14); g.fillRect(sx + 10, 266, 5, 14);
      // 雪
      g.fillStyle = '#ffffff';
      for (const f of flakes) { const y = (f.y + t * f.v) % 360; g.fillRect(Math.round((f.x + Math.sin(t + f.y) * 6 + 640) % 640), Math.round(y), f.r, f.r); }
      g.restore();
    }, { z: 3 });
  }
  async function beatAfter(S) {
    const p = S.player, rh = S.actor('rohan'), ok = S.actor('okuyasu'), ko = S.actor('koichi');
    // 打完站回场地里（暴走冲过去时可能出了右墙）
    Object.assign(p, { x: 360, y: 160, z: 0, facing: 1 });
    if (rh) { Object.assign(rh, { x: 430, y: 156, z: 0, atk: null, tele: null }); S.pose(rh, 'down'); }
    focus(null);
    S.music('daily', 0.8);
    await S.wait(0.6);
    unbook(ok); unbook(ko);
    S.sfx('card_flip', 0.7, 0.7);
    await S.wait(0.4);
    await say(S, 'okuyasu', '……呃？我怎么站在这儿？', { expr: 'shock' });
    if (ko) S.face(ko, 1);
    await S.say('koichi', '仗助君……对不起，我好像一直在做梦。');
    await S.say('josuke', '没事了。……那家伙的书页，我替你撕回来了。', { expr: 'smile' });
    await say(S, 'okuyasu', '不过仗助，你一听人说头发就跟换了个人似的。');
    await S.say('koichi', '我听仗助君的妈妈说过……那是有原因的。');
    // 剪影回忆
    S.music('sad', 0.8);
    await S.title('snow_memory', { y: 110 });
    const h = snowLayer();
    S.sfx('wind', 0.5);
    await S.narrate('仗助四岁那年冬天，他发高烧。妈妈开车送他去医院，车却陷在了雪里。', { pos: 'top' });
    await S.narrate('一个留着飞机头的少年，一声不响地帮忙把车推了出来。', { pos: 'top' });
    S.mark('ch5_hair_story');
    await S.narrate('他没留下名字。仗助只记住了那个背影，和那个发型。', { pos: 'top' });
    h.close();
    await S.wait(0.3);
    S.music('daily', 0.6);
    await S.say('josuke', '所以，谁敢说这个发型，我都不会放过他。');
    if (rh) { S.face(rh, p); }
    await S.say('rohan', '……这个素材，我就收下了。', { expr: 'smile' });
    await S.say('josuke', '你还没被打够啊？', { expr: 'rage' });
  }
  function setupStudio(S) {
    const st = G.world.stage;
    st.hotspots.push(
      { id: 'hole', x: 398, y: 150, r: 22, ry: 14, label: '墙上的洞', tags: ['fix'], fx: 398, fy: 66,
        use: async (S2) => { await S2.say('josuke', '露伴撞出来的。……准确说是我打出来的。'); },
        look: async (S2) => {
          if (F().holeFixed) return;
          F().holeFixed = true;
          S2.state('hole', 0);
          S2.mark('ch5_hole_fix');
          await S2.say('josuke', '……这家伙的墙倒是我打坏的。修好就两清了。');
        } },
      { id: 'desk', x: 234, y: 150, r: 18, label: '画桌', use: async (S2) => { await S2.say(null, 'G 笔、墨水瓶、网点纸。桌角还压着一张康一的速写。'); } },
      { id: 'cabinet', x: 396, y: 150, r: 14, label: '原稿柜', use: async (S2) => { await S2.say('josuke', '原稿堆到天花板了……这人到底画了多少。'); } },
      { id: 'shelves', x: 98, y: 150, r: 18, label: '书架', use: async (S2) => { await S2.say(null, '一整排画集和解剖图鉴。蜘蛛那一本翻得最旧。'); } },
      { id: 'bust', x: 448, y: 150, r: 14, label: '石膏像', use: async (S2) => { await S2.say('josuke', '……这个石膏像的眼神，跟主人一个样。'); } },
    );
    st.triggers.push({ x0: -20, x1: 52, run: async () => { if (F().holeFixed) F().leaveStudio = true; } });
    T().goal(S, { x: 398, y: 150, label: '墙洞', delay: 20, every: 15, done: () => !!F().holeFixed, text: '墙上被打出个洞：走过去按 U 修好' });
    T().goal(S, { x: 50, y: 160, label: '出门', delay: 5, every: 15, when: () => !!F().holeFixed, done: () => !!F().leaveStudio, text: '从左边的门出去' });
  }

  // ================================================================ 节拍 7 几天后：承太郎、水渠
  async function beatJotaro(S) {
    const p = S.player;
    await S.setStage('ditch_ch5', { x: 60, y: 160, facing: 1, music: 'tension', fade: false });
    const jt = S.actor('jotaro4');
    if (jt) Object.assign(jt, { x: 150, y: 156, facing: -1, follow: null });
    snapTo({ x: 160 });
    await S.title('days_later', { y: 110 });
    await S.fadeIn(0.5);
    S.mark('ch5_jotaro');
    await S.say('jotaro4', '仗助。音石明以前用箭射过一只老鼠。');
    await S.say('josuke', '老鼠？……被箭射中的老鼠，也会有替身？', { expr: 'shock' });
    await S.say('jotaro4', '它跑了。放着不管，这个镇上迟早会出事。');
    await S.say('jotaro4', '脚印顺着水渠往上游去。……仔细看。');
    if (G.party.rebuildFollow) G.party.rebuildFollow();
    void p;
  }
  function setupDitch(S) {
    const st = G.world.stage;
    st.hotspots.push(
      { id: 'tracks', x: 300, y: 150, r: 18, ry: 12, label: '脚印', tags: ['detail'], use: async (S2) => { await S2.say('josuke', '小小的爪印……一路往右边去了。'); },
        look: async (S2) => { F().tracks = true; S2.mark('ch5_ditch'); await S2.say('jotaro4', '脚印往上游去了。步子很稳，不像是在逃。'); } },
      { id: 'trap', x: 362, y: 152, r: 14, label: '捕鼠笼', tags: ['detail'], use: async (S2) => { await S2.say('josuke', '捕鼠笼，空的。'); },
        look: async (S2) => { await S2.say('jotaro4', '笼子是新放的。有人专门在抓它。'); } },
      { id: 'camera', x: 528, y: 152, r: 14, label: '摄像机', tags: ['detail'], use: async (S2) => { await S2.say('josuke', '谁在田边架摄像机啊？'); },
        look: async (S2) => { await S2.say('jotaro4', '对着水渠拍的。……牧场那边的人放的。'); } },
      { id: 'drain', x: 474, y: 150, r: 14, label: '排水口', use: async (S2) => {
        S2.sfx('drip', 0.6);
        await S2.say('josuke', '排水口旁边那一团是……', { expr: 'shock' });
        await S2.say('josuke', '……不，还是别看了。');
      } },
      { id: 'sluice', x: 120, y: 150, r: 14, label: '水闸', use: async (S2) => { await S2.say(null, '小水闸。手轮锈住了。'); } },
    );
    st.triggers.push({ x0: 612, x1: 680, run: async () => { if (F().tracks) F().toFarm = true; else if (!F().tracksHint) { F().tracksHint = true; S.hint('先看看脚印往哪去（Q 换承太郎，对着脚印按 U）', 6); } } });
    T().goal(S, { x: 300, y: 150, label: '脚印', delay: 25, every: 15, done: () => !!F().tracks, text: 'Q 换成承太郎，对着桥边的脚印按 U' });
    T().goal(S, { x: 626, y: 160, label: '上游', delay: 4, every: 15, when: () => !!F().tracks, done: () => !!F().toFarm, text: '顺着脚印往右走' });
  }

  // ================================================================ 节拍 9 牧场外：打空罐
  const CANS = [[318, 118], [334, 118], [350, 118], [366, 118], [382, 118], [398, 118]];
  async function ballAt(S, a, cx, cy, hit) {
    S.face(a, 1);
    await S.summon(a, { dur: 0.1, rise: 4 });
    S.standAct(a, 'punch', { dx: 14, z: 6, dur: 0.4 });
    S.sfx('ricochet', 0.6, 1.4);
    await S.wait(0.12);
    if (hit) { S.sfx('clang', 0.8); S.fx('hit_spark', { x: cx, y: cy - 6, size: 8, accent: '#ffffff' }); S.sfxText('叮', { wx: cx, wy: 150, wz: 150 - cy + 8 }, { dur: 0.5 }); }
    else { S.fx('dust', { x: cx, y: cy + 10, n: 3 }, { life: 0.5 }); }
    await S.wait(0.25);
    S.recall(a);
  }
  async function beatCans(S) {
    const p = S.player;
    await S.setStage('farm_out_ch5', { x: 40, y: 160, facing: 1, music: 'tension' });
    S.location('farm', { y: NAME_TOP });
    const jt = S.actor('jotaro4');
    if (jt) { jt.follow = null; await S.walk(jt, 270, 152, { speed: 50 }); S.face(jt, 1); }
    await S.walk(p, 240, 160, { speed: 50 });
    S.face(p, 1);
    await S.say('jotaro4', '老鼠又小又快。拳头够不着它，得会打远的。');
    await S.say('jotaro4', '看好了。', {});
    await ballAt(S, jt, CANS[0][0], CANS[0][1], true);
    await S.say('josuke', '弹钢珠……？疯狂钻石也能这么干？', { expr: 'shock' });
    S.hint('按 J：疯狂钻石弹钢珠，打篱笆上的空罐', 6);
    const outs = [];
    for (let i = 1; i <= 3; i++) {
      const r = await S.press({ key: 'attack', window: 1.4, label: '按 J 弹钢珠！' });
      const hit = r !== 'miss' && i !== 3;
      outs.push(hit);
      await ballAt(S, p, CANS[i][0], CANS[i][1], hit);
    }
    S.hint(null);
    await S.say('jotaro4', '……偏了一点。');
    await S.say('josuke', '两发里中了两发，不算差吧！', { expr: 'smile' });
    // 承太郎把剩下的一口气打穿
    await S.summon(jt, { dur: 0.1, rise: 4 });
    S.standAct(jt, 'punch', { dx: 14, z: 6, dur: 0.6 });
    for (let i = 0; i < 3; i++) { S.sfx('ricochet', 0.5, 1.5); S.sfx('clang', 0.6); await S.wait(0.1); }
    S.state('cans', 1);
    S.recall(jt);
    S.mark('ch5_cans');
    await S.say('jotaro4', '它可不会站着等你打。');
    void outs;
  }
  function setupFarmOut(S) {
    const st = G.world.stage;
    st.hotspots.push(
      { id: 'doghouse', x: 239, y: 150, r: 16, label: '狗屋', use: async (S2) => { S2.sfx('metal_scrape', 0.3); await S2.say('josuke', '链子还拴着，狗不见了。碗是空的。'); } },
      { id: 'laundry', x: 252, y: 150, r: 12, label: '晾着的衣服', use: async (S2) => { F().laundry = true; await S2.say('josuke', '衣服晾了好几天了吧……都没人收。'); } },
      { id: 'milk', x: 204, y: 150, r: 12, label: '牛奶桶', use: async (S2) => { await S2.say(null, '牛奶桶是满的，已经馊了。'); } },
      { id: 'barn', x: 393, y: 150, r: 16, label: '谷仓', use: async (S2) => { S2.sfx('cow_moo', 0.4); await S2.say(null, '谷仓里只有牛在叫。'); } },
      { id: 'door', x: 103, y: 150, r: 16, label: '屋门', use: async () => { F().enterHouse = true; } },
    );
    T().goal(S, { x: 103, y: 150, label: '屋门', delay: 30, every: 15, done: () => !!F().enterHouse, text: '进屋看看：走到门口按 E' });
  }
  async function beatFarmIn(S) {
    const p = S.player, jt = S.actor('jotaro4');
    S.hint(null);
    if (jt) { jt.follow = null; await S.walk(jt, p.x + 30, p.y - 4, { speed: 60 }); S.face(jt, p); }
    await S.say('jotaro4', '一点人声都没有。这家的主人，大概已经……');
    await S.say('josuke', '……别说了。分头找吧。');
    await S.say('jotaro4', '我去谷仓。屋里交给你。');
    if (jt) { S.walk(jt, 520, 152, { speed: 60 }).catch(G.cancelIgnore); }
    S.mark('ch5_farm');
    S.sfx('creak', 0.7);
    S.party(['josuke'], { leader: 'josuke' });
    await S.setStage('farm_ch5', { x: 80, y: 160, facing: 1, music: 'tension' });
    await S.wait(0.4);
    S.sfx('doll_scurry', 0.6);
    await S.say('josuke', '……桌子底下有东西在动。', { expr: 'shock' });
    S.music('battle', 0.3);
    await S.vs({ key: 'ratt', hero: 'josuke', enemy: { cid: 'rat_a', anim: 'aim' } });
    G.uifx.vsTag('ratt');
    S.standCard('ratt', { y: NAME_TOP });
  }

  // ================================================================ 节拍 11 冰箱、手套、虫食、两发子弹
  async function beatFarmAfter(S) {
    const p = S.player;
    S.stopMusic(0.5);
    await S.wait(0.6);
    await S.say('josuke', '……打中了。');
    await S.walk(p, 258, 156, { speed: 50 });
    S.face(p, 1);
    await S.say('josuke', '冰箱门开着一条缝。');
    S.sfx('creak', 0.8);
    await S.fadeOut(0.12);
    S.sfx('fridge', 0.8);
    await S.wait(1.2);
    S.sfx('heartbeat', 0.4);
    await S.narrate('……', { pos: 'top' });
    S.sfx('thud', 0.8);
    S.mark('ch5_fridge');
    await S.fadeIn(0.4);
    S.face(p, -1);
    await S.say('josuke', '……原来主人早就……', { expr: 'shock' });
    // 承太郎进来：右手手套在冒烟
    const jt = S.spawn('jotaro4', 20, 152, { id: 'jotaro4_in', facing: 1, name: '空条承太郎' });
    await S.walk(jt, p.x - 34, p.y - 2, { speed: 50 });
    let smoking = true;
    const smoke = async () => { while (smoking) { S.fx('smoke', { x: jt.x + 8, y: jt.y - 18, n: 2, rise: 10, life: 0.5, colour: '#e0a0d0' }, { life: 0.6 }); await S.wait(0.35); } };
    smoke().catch(G.cancelIgnore);
    await S.say('jotaro4', '谷仓里还有一只。……被它的飞镖擦到了手。');
    S.face(p, jt);
    await S.say('josuke', '别动，我来。', {});
    await S.summon(p, { dur: 0.12, rise: 4 });
    S.standAct(p, 'reach', { dx: -18, z: 2, dur: 0.8 });
    smoking = false;
    P4().fixGlow(S, jt.x + 8, jt.y - 18);
    await S.wait(0.6);
    S.recall(p);
    S.mark('ch5_glove');
    await S.say('jotaro4', '……多谢。另一只跑了。');
    // SPW 来电
    for (let i = 0; i < 2; i++) { S.sfx('ding', 0.6); await S.wait(0.35); }
    await S.say('spw_phone', '承太郎先生，查清楚了：音石明射过的老鼠是两只。', { portrait: false, name: 'SPW 财团' });
    await S.say('jotaro4', '这一带的下水道已经全堵上了。它出不了这片山。');
    await S.narrate('牧场的摄像机里，一只耳朵缺了一块的老鼠，从镜头前跑了过去。', { pos: 'top' });
    await S.say('jotaro4', '耳朵上有缺口的那只……就叫它“虫食”。');
    S.mark('ch5_mushikui');
    S.sfx('clang', 0.4, 1.6);
    await S.say('jotaro4', '拿着。步枪子弹，你用疯狂钻石弹出去。');
    await S.say('jotaro4', '只有两发。');
    S.mark('ch5_bullets');
    await S.say('josuke', '……两发。', { expr: 'shock' });
  }

  // ================================================================ 节拍 12 池塘、捕鼠夹、时停
  async function beatPond(S) {
    const p = S.player;
    await S.setStage('hill_ch5', { x: 60, y: 160, facing: 1, music: 'tension' });
    const jt = S.spawn('jotaro4', 30, 154, { id: 'jotaro4', facing: 1, name: '空条承太郎' });
    S.walk(jt, 220, 154, { speed: 48 }).catch(G.cancelIgnore);
    await S.walk(p, 262, 160, { speed: 48 });
    await S.say('josuke', '脚印……到池塘边就没了。');
    S.sfx('splash', 0.7);
    S.fx('water_splash', { x: 250, y: 146, size: 0.8 });
    p.play('hurt');
    await S.wait(0.4);
    p.play('idle');
    S.mark('ch5_pond');
    await S.say('josuke', '哇！鞋……掉水里了！', { expr: 'shock' });
    S.face(jt, 1);
    await S.say('jotaro4', '……它是故意把脚印留到这里的。');
    await S.say('jotaro4', '它绕回来了。被盯上的是我们。');
    // 捕鼠夹 → 飞镖 → 时停
    await S.walk(p, 300, 162, { speed: 40 });
    S.sfx('clang', 0.9);
    S.shake(2, 0.2);
    await S.say('josuke', '捕鼠夹？！谁在草里放这种——', { expr: 'shock' });
    S.sfx('knife_hit', 0.9);
    p.play('hurt');
    S.fx('smoke', { x: p.x + 2, y: p.y - 30, n: 3, rise: 8, life: 0.5, colour: '#e0a0d0' }, { life: 0.6 });
    await S.wait(0.2);
    S.sfx('timestop', 0.9);
    S.filter('gray', 1);
    await S.wait(0.4, 'ui');
    jt.x = p.x - 24; jt.y = p.y - 2; S.face(jt, 1);
    await S.summon(jt, { dur: 0.08, rise: 4 });
    S.standAct(jt, 'punch', { dx: 18, z: 10, dur: 0.5 });
    S.sfx('whoosh', 0.7);
    S.fx('glint', { x: p.x + 2, y: p.y - 30, size: 6 }, { life: 0.3 });
    await S.wait(0.4, 'ui');
    S.filter('gray', null);
    S.sfx('time_resume', 0.8);
    S.recall(jt);
    p.play('idle');
    await S.say('josuke', '……飞镖呢？我脖子上刚才……', { expr: 'shock' });
    await S.say('jotaro4', '弹掉了。连同被它化掉的那一小块。');
    await S.say('jotaro4', '它在坡上。我往上走，它会对我开枪。');
    await S.say('jotaro4', '飞镖从哪儿来，你就往哪儿打。');
    S.spawn('mushikui', 778, 145, { id: 'mushikui', facing: -1, name: '虫食' });
  }
  async function beatEnd(S) {
    const p = S.player, jt = S.actor('jotaro4');
    S.stopMusic(0.5);
    await S.wait(0.8);
    if (jt) { await S.walk(jt, p.x + 30, p.y - 4, { speed: 44 }); S.face(jt, p); }
    S.face(p, 1);
    await S.wait(0.6);
    await S.say('jotaro4', '……干得好。');
    S.mark('ch5_praise');
    await S.wait(0.4);
    await S.say('josuke', '……诶？刚才那是在夸我？', { expr: 'shock' });
    S.music('victory', 0.8);
    await S.say('josuke', '喂，承太郎先生！再说一遍嘛！', { expr: 'smile' });
    if (jt) S.walk(jt, 40, 154, { speed: 40 }).catch(G.cancelIgnore);
    await S.wait(1.2);
    S.stopMusic(0.6);
    await S.tbc({ hold: 2.0 });
    S.mark('ch5_tbc');
  }

  // ================================================================ 第5章主流程
  G.STORY.ch5 = async function (S) {
    if (T().resetCounters) T().resetCounters();
    P4().clearOverlays();
    await S.chapterCard('ch5');
    // 节拍 1–2（康一的视角）
    S.party(['koichi'], { leader: 'koichi' });
    await S.run(async (S2) => {
      await beatCalendar(S2);
      await beatVisit(S2);
    }, { keepLocked: true });
    // 节拍 3 第二天：门外自由走动（找到没锁的窗）
    S.party(['josuke'], { leader: 'josuke' });
    await S.run(async (S2) => {
      await beatNextDay(S2);
      setupDoor(S2);
      S2.hint('门口转转：E 和人说话、调查', 6);
    });
    await S.until(() => !!F().window && !S.busy);
    // 节拍 4 → 第 7 战 → 节拍 6
    await S.run(async (S2) => {
      await beatWindow(S2);
      await C5().fightHeavensDoor(S2);
      await beatAfter(S2);
    }, { keepLocked: true });
    // 工作室自由走动：U 修墙 → 出门
    setupStudio(S);
    await S.run(async (S2) => { S2.hint('U：疯狂钻石的修复　E 调查', 6); });
    await S.until(() => !!F().leaveStudio && !S.busy);
    Object.assign(ST.rohan_in_ch5, { hotspots: [], triggers: [] });
    // 节拍 7 几天后 → 节拍 8 水渠自由走动（Q 换承太郎）
    S.party(['josuke', 'jotaro4'], { leader: 'josuke' });
    await S.run(async (S2) => {
      await beatJotaro(S2);
      setupDitch(S2);
      S2.hint('Q 换成承太郎：U 是白金之星的眼睛，看得清细节', 7);
    });
    await S.until(() => !!F().toFarm && !S.busy);
    Object.assign(ST.ditch_ch5, { hotspots: [], triggers: [] });
    // 节拍 9 牧场外：打空罐 → 自由走动
    await S.run(async (S2) => {
      if (G.world.player && G.world.player.cid !== 'josuke') G.party.setLeader('josuke', { force: true, silent: true });
      await beatCans(S2);
      setupFarmOut(S2);
    });
    await S.until(() => !!F().enterHouse && !S.busy);
    Object.assign(ST.farm_out_ch5, { hotspots: [], triggers: [] });
    // 第 8 战段 1 → 节拍 11 → 节拍 12 → 段 2 → 节拍 13
    await S.run(async (S2) => {
      await beatFarmIn(S2);
      await C5().fightRattA(S2);
      await beatFarmAfter(S2);
      await beatPond(S2);
      await C5().fightHill(S2);
      await beatEnd(S2);
    }, { keepLocked: true });
  };
  // 整章测试（tools/dev/p4_play.js）对照的剧情标记
  G.STORY.ch5.marks = ['ch5_calendar', 'ch5_visit', 'ch5_book', 'ch5_write', 'ch5_next_day', 'ch5_window', 'b07_start', 'b07_taunt', 'ch5_hair4',
    'b07_win', 'ch5_hair_story', 'ch5_hole_fix', 'ch5_jotaro', 'ch5_ditch', 'ch5_cans', 'ch5_farm', 'b08a_start', 'b08a_pan', 'b08a_duel',
    'b08a_rat_down', 'ch5_fridge', 'ch5_glove', 'ch5_mushikui', 'ch5_bullets', 'ch5_pond', 'b08b_start', 'b08b_shot1', 'b08b_reveal', 'b08b_kill',
    'ch5_praise', 'ch5_tbc'];
  void now;
})();
