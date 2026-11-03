// 第7章　商店街 / 灰姑娘与枯萎穿心攻击（开发脚本 第四部/docs/第7章_开发脚本.md；地图后缀 _ch7）。整章流程：
//   节拍 1 篇章卡 → 日历地图（两枚图钉 + 1999年7月）→ 2 灰姑娘美容院（由花子换脸）→ 3 约会自由走动（康一记下“她的脸”四条线索）
//   → 4 口红、拥抱、三十分钟到了 → 5 戴口罩的由花子、美容院 → 6 六张脸解谜（康一押上自己的眼睛）
//   → 7 几天后，裁缝店的纽扣和登记簿 → 白光 → 8 枯萎穿心攻击 → 第 11 战段 A → 10 承太郎倒下、回音 ACT3 → 段 B
//   → 12 本体被拖出小巷、「我拒绝」→ 段 C → 14 他看得见替身、黑屏 → 15 修复光自由走动（追到美容院门口断掉）
//   → 16 吉良视角（辻彩之死只在旁白里）→ 17 走出美容院的上班族、第二天、To Be Continued
//   克制：由花子“脸变丑”只给背影和口罩；爆炸只给白光和焦黑；吉良切手只给黑屏 + 闷响；修复光只画一道金线；辻彩之死只有旁白；
//   川尻浩作本人只给剪影。第 11 战三段在 story/p4_ch7_fights.js（G.P4CH7）。
'use strict';
(function () {
  const G = window.G, { base, walls } = G.p4Stage;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const R = () => G.P4CH7;
  const F = () => G.flags;
  const now = () => (G.clk ? G.clk.world : 0);
  const NAME_TOP = 100;
  // 别章画的人（由花子 / 亿泰 / 吉良 / 杀手皇后）：正式图合进来以前用 ph7_* 占位，R().cid 自动挑
  const cid = (c) => (R() ? R().cid(c) : c);
  const YK = () => cid('yukako');

  Object.assign(G.NAMES, {
    aya: '辻彩', cinderella: '灰姑娘', echoes3: '回音 ACT3', sha: '枯萎穿心攻击', kawajiri: '穿西装的男人', tailor: '裁缝店老板',
    ph7_yukako: '由花子', ph7_okuyasu: '亿泰', ph7_kira: '吉良', ph7_killerqueen: '杀手皇后',
  });
  if (!G.NAMES.yukako) G.NAMES.yukako = '由花子';
  if (!G.NAMES.okuyasu) G.NAMES.okuyasu = '亿泰';
  if (!G.NAMES.kira) G.NAMES.kira = '吉良';

  // ================================================================ 地图（docs/第7章_背景.md）
  const ST = G.STAGES;
  ST.map_ch7 = base('map_ch7', 'morioh_map', 320, { yMin: 160, yMax: 170, music: null, obstacles: [] });
  ST.salon_ch7 = base('salon_ch7', 'cinderella_salon', 480, { obstacles: walls(12, 468, 480), state: { night: 0 } });
  ST.date_ch7 = base('date_ch7', 'morioh_grand_hotel', 480, { state: { pm: 0 } });
  ST.tailor_ch7 = base('tailor_ch7', 'tailor_shop', 480, { music: 'tension', obstacles: walls(12, 440, 480), state: { after: 0 } });
  ST.street_ch7 = base('street_ch7', 'morioh_avenue', 960, { music: 'tension', state: { after: 0, closed: 0, pm: 0 } });
  const clearStage = (id) => Object.assign(ST[id], { npcs: [], hotspots: [], triggers: [] });
  const anc = (bg, k, d) => { const b = G.D && G.D.bg && G.D.bg[bg]; return (b && b.anchors && b.anchors[k]) || d; };

  // 日历地图：两枚新图钉（杜王町地图上本来没有这两处的锚点，开章时补上），红章换成「1999年7月」
  P4().CAL.ch7 = { pins: [{ at: 'ch7_salon', label: '灰姑娘美容院' }, { at: 'ch7_tailor', label: '裁缝店' }], stamp: 'stamp_199907' };

  const pool = (c) => G.party._actor(c);
  function place(S, c, x, y, facing, o = {}) {
    const a = pool(c), W = G.world;
    Object.assign(a, { x, y, z: 0, facing: facing || 1, follow: null, hold: false, script: null, state: 'idle', remove: false, rot: 0, alpha: 1, tint: null });
    a.visible = o.visible !== false;
    if (W.player !== a) a.team = 'npc';
    a.play(a.idleAnim || 'idle');
    W.stage.add(a);
    return a;
  }
  const focus = (o) => { G.world.focus = o; };
  const snapTo = (o) => { G.world.focus = o; G.world.snapCamera(); };
  // 倒在地上：有 down 动作就用，没有就整个人横过来（康一、由花子占位都没画 down）
  function lieDown(S, a) {
    if (!a) return;
    if (a.atlas && a.atlas.has && a.atlas.has('down')) { S.pose(a, 'down'); return; }
    S.pose(a, 'hurt');
    a.rot = -Math.PI / 2;
  }
  function getUp(S, a) { if (!a) return; a.rot = 0; S.unpose(a); }

  // ================================================================ 节拍 1 篇章卡 → 日历地图
  async function beatCalendar(S) {
    S.player.visible = false;
    await S.setStage('map_ch7', { x: 160, y: 165, music: null });
    const mapA = G.D.bg.morioh_map.anchors, ui = G.D.ui.map || {};
    mapA.ch7_salon = mapA.ch7_salon || [214, 86];
    mapA.ch7_tailor = mapA.ch7_tailor || [188, 100];
    const old = ui.stamp;
    if (ui.stamp_199907) ui.stamp = ui.stamp_199907;
    let cal = null;
    try { cal = await P4().calendar(S, 'ch7', { hold: 1.8 }); } finally { ui.stamp = old; }
    S.mark('ch7_calendar');
    await S.fadeOut(0.45);
    if (cal) cal.close();
  }

  // ================================================================ 节拍 2 灰姑娘美容院：由花子换脸
  async function beatSalon(S) {
    const door = anc('cinderella_salon', 'door', [31, 148]), chair = anc('cinderella_salon', 'chair1', [176, 148]);
    await S.setStage('salon_ch7', { x: 60, y: 160, music: 'daily', fade: false });
    S.player.visible = false;
    const yk = S.spawn(YK(), door[0], door[1] + 10, { id: 'yukako', facing: 1, name: '山岸由花子' });
    const aya = S.spawn('aya', 120, 150, { id: 'aya', facing: -1 });
    snapTo({ x: 160 });
    await S.fadeIn(0.6);
    S.location('salon', { y: NAME_TOP });
    S.sfx('ding', 0.6);
    await S.walk(yk, 76, 158, { speed: 34 });
    S.mark('ch7_salon');
    await S.narrate('康一君说过，他喜欢的是“真正的我”。……可真正的我，到底是什么样子？', { pos: 'top' });
    S.face(aya, yk);
    await S.say('aya', '欢迎光临。你是来找“恋爱运”的吧？', { expr: 'smile' });
    S.nameCard('aya', { y: NAME_TOP });
    await S.say(YK(), '你、你怎么知道……', { expr: 'shock', actor: yk });
    await S.say('aya', '人的脸决定了别人怎么看你。眉毛、眼角、嘴角，差一毫米，运气就完全不一样。');
    await S.say('aya', '先试三十分钟吧。请坐，闭上眼睛。');
    await S.walk(yk, chair[0], chair[1] + 6, { speed: 40 });
    S.face(yk, -1);
    await S.walk(aya, chair[0] - 26, chair[1] + 6, { speed: 40 });
    S.face(aya, 1);
    // 灰姑娘从辻彩身后浮出来：指尖一挑，五官像贴纸一样揭下、换上（只给光，不画脸的变化）
    const cin = S.spawn('cinderella', aya.x - 4, aya.y - 1, { id: 'cinderella', facing: 1, alpha: 0, shadow: false });
    cin.z = 10;
    S.sfx('stand_summon_hiero', 0.6);
    await S.animate(0.5, (k) => { cin.alpha = 0.85 * k; cin.x = aya.x - 4 + 14 * k; });
    S.standCard('cinderella', { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.wait(0.9);
    for (let i = 0; i < 3; i++) {
      S.sfx('sparkle', 0.6);
      S.fx('sparkle', { x: yk.x, y: yk.y - 30, n: 6 }, { life: 0.5 });
      await S.wait(0.35);
    }
    S.flash(0.2, 0.6, '#ffe0f0');
    S.mark('ch7_makeover');
    await S.animate(0.4, (k) => { cin.alpha = 0.85 * (1 - k); });
    cin.remove = true;
    await S.say('aya', '好了，请看镜子。……三十分钟以内，你的魅力谁也挡不住。', { expr: 'smile' });
    S.face(yk, 1);
    await S.say(YK(), '这、这是我……？', { expr: 'smile', actor: yk });
    await S.fadeOut(0.5);
  }

  // ================================================================ 节拍 3 约会自由走动：康一记下“她的脸”
  //   四条线索的顺序 = 解谜里对照的顺序；FACES[n] = 第 n 号脸每条对得上（1）还是对不上（0）（docs/第7章_背景.md 的六张脸表）
  const CLUES = ['齐刘海，两边长发垂下', '眉毛细长，尾巴上挑', '眼角上挑', '不笑时嘴角是平的'];
  const FACES = { 1: [0, 0, 0, 0], 2: [0, 0, 0, 0], 3: [0, 0, 0, 0], 4: [1, 1, 1, 1], 5: [0, 0, 1, 0], 6: [0, 1, 0, 1] };
  const RIGHT = 4;
  let mem = null;
  const gotN = () => (mem ? mem.got.filter(Boolean).length : 0);
  function tick(g, x, y, ok) {
    if (ok) { g.fillStyle = '#2a8a3a'; for (let k = 0; k < 4; k++) g.fillRect(x + 1 + k, y + 4 + k, 2, 2); for (let k = 0; k < 6; k++) g.fillRect(x + 4 + k, y + 6 - k, 2, 2); }
    else { g.fillStyle = '#c03030'; for (let k = 0; k < 8; k++) { g.fillRect(x + 1 + k, y + 1 + k, 2, 2); g.fillRect(x + 8 - k, y + 1 + k, 2, 2); } }
  }
  // 画面右上「康一的记忆」：照序章超市清单的样子；face = 解谜时正在看的那张脸（每条打勾 / 打叉）
  function memoBox(g, face) {
    const x0 = 438, y0 = face ? 110 : 10, x1 = 630, rows = CLUES.length;
    const y1 = y0 + 28 + rows * 18;
    G.ui.box(g, x0, y0, x1, y1, { fill: 'rgba(250,244,226,0.95)' });
    P4().text(g, face ? face + ' 号 vs 康一的记忆' : '康一的记忆：她的脸', x0 + 10, y0 + 7, '#5a3a20', 12, 'left', null);
    CLUES.forEach((s, i) => {
      const y = y0 + 26 + i * 18, got = mem && mem.got[i];
      g.fillStyle = '#5a3a20'; g.fillRect(x0 + 10, y + 1, 12, 12);
      g.fillStyle = '#faf4e2'; g.fillRect(x0 + 11, y + 2, 10, 10);
      if (face && got) tick(g, x0 + 11, y + 2, FACES[face][i] === 1);
      else if (!face && got) tick(g, x0 + 11, y + 2, true);
      P4().text(g, got ? s : '？？？', x0 + 28, y, got ? '#3a2a1a' : '#9a8a70', 12, 'left', null);
    });
  }
  function memoOpen() {
    mem = { got: [false, false, false, false] };
    mem.h = P4().overlay((g) => {
      const W = G.world;
      if (!W || W.insert || (G.S && G.S.cardOn) || mem.hide) return;
      if (G.ui.dlg && G.ui.dlg.y0 < 100) return;
      memoBox(g, null);
    });
  }
  async function gotClue(S, i, line) {
    if (!mem || mem.got[i]) return;
    mem.got[i] = true;
    F()['ch7c' + i] = true;
    S.sfx('pop', 0.7); S.sfx('sparkle', 0.4);
    await S.say('koichi', line);
    S.hint('记下了：' + CLUES[i] + '（' + gotN() + ' / 4）', 3);
    if (gotN() === 4) S.mark('ch7_clues');
  }
  async function talkYukako(S, me) {
    if (!mem.got[0]) {
      await T().say(S, me, '……别一直盯着我看嘛。', { expr: 'smile' });
      await gotClue(S, 0, '（刘海剪得整整齐齐，两边的长发一直垂到腰。）');
      return;
    }
    if (gotN() >= 3 && !mem.got[3]) {
      await T().say(S, me, '我只是……不习惯被人这么夸。');
      await gotClue(S, 3, '（她不笑的时候，嘴抿成一条直线。）');
      return;
    }
    await T().say(S, me, F().ch7c3 ? '康一君，今天谢谢你陪我。' : '那边的露天座，要不要坐一下？', { expr: 'smile' });
  }
  function setupDate() {
    const t1 = anc('morioh_grand_hotel', 'table1', [344, 150]), t2 = anc('morioh_grand_hotel', 'table2', [398, 150]);
    const door = anc('morioh_grand_hotel', 'hotel_door', [151, 146]), sign = anc('morioh_grand_hotel', 'sign', [461, 82]);
    Object.assign(ST.date_ch7, {
      npcs: [
        T().npc(YK(), 'yukako', 300, 156, { facing: -1, label: '由花子', talk: talkYukako }),
        T().npc('clerk', 'doorman', door[0] + 18, 152, { facing: 1, label: '门童', name: '门童',
          talk: async (S, me) => { await T().say(S, me, '杜王大酒店，欢迎光临。……那位白衣服的先生，今天出门了。'); } }),
      ],
      hotspots: [
        { id: 'table1', x: t1[0], y: 152, r: 14, ry: 10, label: '露天座', use: async (S) => {
          if (mem.got[1]) { await S.say(null, '空着的露天座。'); return; }
          await S.say(null, '两个人坐下。由花子低着头搅咖啡。');
          await gotClue(S, 1, '（她的眉毛又细又长，尾巴往上挑。）');
        } },
        { id: 'table2', x: t2[0], y: 152, r: 14, ry: 10, label: '露天座', use: async (S) => {
          if (mem.got[2]) { await S.say(null, '桌上还留着两个咖啡杯。'); return; }
          await S.say(YK(), '……你在看什么？', { name: '由花子', expr: 'rage' });
          await gotClue(S, 2, '（就算现在变温柔了，眼角还是往上吊着，有点凶。）');
        } },
        { id: 'menu', x: sign[0], y: 152, r: 12, label: '菜单板', use: async (S) => {
          await S.say(null, '今日推荐：草莓芭菲。');
          await S.say('koichi', '（一份要一千二……）', { expr: 'shock' });
        } },
      ],
      triggers: [],
    });
  }
  async function dateIn(S) {
    const p = S.player;
    setupDate();
    await S.setStage('date_ch7', { x: 120, y: 160, facing: 1, music: 'daily', fade: false });
    S.state('pm', 0);
    p.visible = true;
    await S.fadeIn(0.5);
    S.location('ch7_cafe', { y: NAME_TOP });
    await S.narrate('那天下午，我在酒店门口碰见了山岸同学。……她好像哪里不一样了。', { pos: 'top' });
    const yk = S.actor('yukako');
    await S.walk(yk, 170, 156, { speed: 44 });
    S.face(yk, -1);
    S.mark('ch7_date');
    await S.say(YK(), '康一君……之前的事，对不起。我们能重新开始吗？', { expr: 'smile', actor: yk });
    await S.say('koichi', '诶？啊，好、好的……（怎么回事，心跳得好快）', { expr: 'shock' });
    await S.walk(yk, 300, 156, { speed: 44 });
    S.face(yk, -1);
    memoOpen();
    S.hint('陪由花子走走：和她说话、去露天座坐坐（E）。记住她的脸', 7);
  }

  // ================================================================ 节拍 4 口红、拥抱、三十分钟到了
  async function beatLipstick(S) {
    const p = S.player, yk = S.actor('yukako');
    if (mem) mem.hide = true;
    S.hint(null);
    if (yk) { S.face(p, yk); await S.walk(p, yk.x - 20, yk.y, { speed: 40 }); S.face(p, 1); S.face(yk, -1); }
    S.sfx('heartbeat', 0.6);
    await S.say('koichi', '对、对不起，我肚子突然……！', { expr: 'shock' });
    S.walk(p, -30, 160, { speed: 110 }).catch(G.cancelIgnore);
    await S.say(YK(), '康一君？！……不好，三十分钟快到了！', { expr: 'shock', actor: yk });
    await S.fadeOut(0.4);
    // 转场：美容院
    await S.setStage('salon_ch7', { x: 60, y: 160, music: 'tension', fade: false });
    p.visible = false;
    const lp = anc('cinderella_salon', 'lipstick', [293, 102]);
    const aya = S.spawn('aya', lp[0] - 10, 152, { id: 'aya', facing: -1 });
    const y2 = S.spawn(YK(), lp[0] - 50, 156, { id: 'yukako', facing: 1 });
    snapTo({ x: lp[0] - 30 });
    await S.fadeIn(0.4);
    await S.say('aya', '想要更久？那就全身都换。不过有一个条件。');
    S.face(aya, y2);
    const lip = T().prop(S, 'lipstick', aya.x - 8, aya.y + 1, { id: 'lip', z: 18 });
    await S.say('aya', '这支口红，从现在开始，每三十分钟涂一次。一次都不能忘。');
    await T().closeup4(S, { heads: [{ cid: 'aya', expr: 'smile' }], dur: 0.7, bg: 'radial', sfx: 'glint', impact: false });
    S.mark('ch7_lipstick');
    await S.say(YK(), '……我答应。', { actor: y2 });
    if (lip) lip.remove = true;
    await S.fadeOut(0.5);
    aya.remove = true; y2.remove = true;
    // 转场回咖啡馆，傍晚：康一把她落下的包还给她，两人抱在一起，头顶一颗爱心
    clearStage('date_ch7');
    await S.setStage('date_ch7', { x: 260, y: 160, facing: 1, music: 'daily', fade: false });
    S.state('pm', 1);
    const yk3 = S.spawn(YK(), 330, 158, { id: 'yukako', facing: -1 });
    Object.assign(p, { x: 200, y: 158, facing: 1, visible: true });
    snapTo({ x: 290 });
    await S.fadeIn(0.5);
    await S.walk(p, 300, 158, { speed: 60, anim: 'run' });
    await S.say('koichi', '山岸同学！你的包落在露天座上了！');
    await S.say(YK(), '康一君……', { expr: 'smile', actor: yk3 });
    await S.walk(yk3, 314, 158, { speed: 30 });
    S.sfx('heartbeat', 0.6);
    const heart = T().prop(S, 'heart', 307, 158, { id: 'heart', z: 56 });
    S.animate(1.4, (k) => { if (heart) heart.z = 56 + 10 * k; }).catch(G.cancelIgnore);
    S.mark('ch7_hug');
    await S.animate(1.4, (k) => S.filter('tint', 0.7 * k, { color: '#ffffff' }));
    await S.narrate('……三十分钟，到了。', { pos: 'top' });
    S.sfx('blip', 0.8);
    S.sfxText('嘀', yk3, { dur: 0.8 });
    await S.wait(0.6);
    S.filter('tint', null);
    if (heart) heart.remove = true;
    await S.fadeOut(0.6);
    yk3.remove = true;
    if (mem) mem.hide = true;
  }

  // ================================================================ 节拍 5 戴口罩的她 → 美容院
  async function beatMasked(S) {
    const p = S.player;
    await S.setStage('street_ch7', { x: 600, y: 160, facing: 1, music: 'tension', fade: false });
    S.state('pm', 0);
    p.visible = true;
    // 戴帽子和口罩的女生：只给背影（整个人压暗一点，头像不给脸）
    const yk = S.spawn(YK(), 700, 152, { id: 'yk_mask', facing: 1, name: '戴口罩的女生' });
    yk.tint = { color: '#20203a', k: 0.45 };
    snapTo({ x: 650 });
    await S.fadeIn(0.5);
    await S.narrate('那以后，山岸同学好几天没来学校。', { pos: 'top' });
    await S.walk(p, 660, 158, { speed: 50 });
    S.face(p, 1);
    await S.say('koichi', '……山岸同学？');
    S.mark('ch7_masked');
    await S.say(YK(), '……认错人了。', { name: '戴口罩的女生', portrait: false });
    S.walk(yk, 940, 148, { speed: 96, anim: 'run' }).then(() => { yk.remove = true; }, G.cancelIgnore);
    await S.wait(0.6);
    await S.say('koichi', '帽檐下面那绺长黑发……绝对是她！', { expr: 'shock' });
    await S.walk(p, 900, 150, { speed: 90, anim: 'run' });
    await S.fadeOut(0.4);
    // 美容院里：由花子背对着、捂着脸
    await S.setStage('salon_ch7', { x: 60, y: 160, facing: 1, music: 'tension', fade: false });
    const aya = S.spawn('aya', 300, 152, { id: 'aya', facing: -1 });
    const y2 = S.spawn(YK(), 250, 156, { id: 'yukako', facing: 1 });
    y2.tint = { color: '#20203a', k: 0.45 };
    snapTo({ x: 220 });
    await S.fadeIn(0.4);
    await S.say(YK(), '把我的脸还给我！你说过只要涂口红——', { expr: 'shock', actor: y2, portrait: false, name: '由花子' });
    await S.say('aya', '可你没涂。命运被改过一次，就会一直往坏的那边滑下去。');
    await S.say('aya', '你原来的脸……已经不在你身上了。');
    await S.walk(p, 210, 158, { speed: 70 });
    S.face(p, 1);
    await S.say('koichi', '请等一下！她是山岸由花子，不管脸变成什么样，我都认得出来！', { expr: 'rage' });
    S.face(aya, p);
    await S.say('aya', '……那就让你来选。', { expr: 'smile' });
  }

  // ================================================================ 节拍 6 六张脸解谜
  const FACE_DESC = {
    1: '（1 号：斜刘海，眉毛弯弯的，眼角往下垂，嘴角带笑。）',
    2: '（2 号：卷卷的刘海，粗粗的平眉，圆眼睛，大嘴巴。）',
    3: '（3 号：中分，八字眉，眼角和嘴角都往下耷拉。）',
    4: '（4 号：齐刘海，两边长发垂下。细眉上挑，眼角上挑，嘴抿成一条线。）',
    5: '（5 号：中分，淡淡的细眉，眼角上挑，嘴角带笑。）',
    6: '（6 号：碎短刘海，细眉上挑，圆眼睛，嘴角是平的。）',
  };
  const MISS = ['……你再看一眼她的刘海。', '……眉毛呢？', '……眼角呢？你记得她瞪人的样子吗？', '……她不笑的时候，嘴是什么样子？'];
  let puzzle = null;
  async function lookFace(S, n) {
    puzzle.seen[n] = true;
    puzzle.last = n;
    S.sfx('card_flip', 0.6);
    // 大特写：左边放大 4 倍的脸，右边「康一的记忆」逐条对照
    const h = T().show(S, { bg: '#2a0c1c', vignette: 0.5, parts: [{ kind: 'sprite', cid: 'prop:face_big', frame: n - 1, x: 96, y: 148, scale: 1 }] });
    const ov = P4().overlay(() => {}, { z: 3 });
    ov.fn = (g) => memoBox(g, n);
    if (!puzzle.markedLook) { puzzle.markedLook = true; S.mark('ch7_faces'); }
    try {
      await S.say('koichi', FACE_DESC[n]);
    } finally { ov.close(); h.close(); }
  }
  async function chooseFace(S) {
    if (!Object.keys(puzzle.seen).length) { await S.say('aya', '先好好看看那几张脸吧。慢慢看，不着急。', { expr: 'smile' }); return; }
    const opts = ['1 号', '2 号', '3 号', '4 号', '5 号', '6 号', '再看看'];
    const i = await S.choice(opts, '她原来的脸是——', { idx: Math.max(0, (puzzle.last || 1) - 1) });
    if (i == null || i >= 6) return;
    const n = i + 1;
    S.mark('ch7_choose');
    if (n !== RIGHT) {
      puzzle.wrong++;
      const bad = FACES[n].findIndex((v, k) => !v && mem && mem.got[k]);
      const k = bad >= 0 ? bad : FACES[n].findIndex((v) => !v);
      await S.say('aya', '确定？' + MISS[k < 0 ? 0 : k]);
      if (puzzle.wrong >= 2) { puzzle.last = RIGHT; S.hint('辻彩的视线停在第 4 张脸上', 4); }
      return;
    }
    puzzle.done = true;
  }
  function setupSalonPuzzle() {
    const hs = [];
    for (let n = 1; n <= 6; n++) {
      const fx = anc('cinderella_salon', 'face' + n, [320 + n * 23, 70]);
      hs.push({ id: 'face' + n, x: fx[0], y: 146, r: 10, ry: 5, label: n + ' 号脸', use: (S) => lookFace(S, n) });
    }
    // 地图已经换好了：调查点直接挂在当前的 Stage 上（和序章 setupRoadFree 一样）
    G.world.stage.hotspots.push(...hs);
  }
  async function puzzleIn(S) {
    const p = S.player, aya = S.actor('aya'), y2 = S.actor('yukako');
    S.sfx('door', 0.5);
    await S.say('aya', '她原来的脸就在这六张里面。选对了，我还给她；选错了，她这辈子就是那张脸。');
    await S.say(YK(), '我、我选不出来……康一君，你帮我选。你选哪张，我都认。', { expr: 'shock', actor: y2, portrait: false, name: '由花子' });
    // 换成解谜用的地图件：辻彩站到工作台边上（和她说话 = 选）
    if (aya) aya.remove = true;
    if (y2) { y2.x = 200; y2.y = 162; S.face(y2, 1); }
    setupSalonPuzzle();
    const a2 = S.spawn('aya', 300, 160, { id: 'aya', facing: 1, label: '辻彩：就是这张', name: '辻彩' });
    a2.talk = (S2) => chooseFace(S2);
    puzzle = { seen: {}, last: 0, wrong: 0, done: false };
    if (mem) mem.hide = false;
    S.face(p, 1);
    S.hint('走到每张脸下面按 E 看清楚，再去跟辻彩说“就是这张”', 8);
  }
  async function faceBack(S) {
    const p = S.player, aya = S.actor('aya'), y2 = S.actor('yukako');
    if (mem) { mem.h.close(); mem = null; }
    S.hint(null);
    T().memberTalk({});
    await S.say('koichi', '是 4 号。……要是我选错了，就把我的眼睛拿走吧。', { expr: 'rage' });
    await S.say(YK(), '康一君！', { expr: 'shock', actor: y2, portrait: false, name: '由花子' });
    if (aya) S.face(aya, p);
    await S.say('aya', '……肯为她押上自己眼睛的人，我还是第一次见。', { expr: 'smile' });
    const cin = S.spawn('cinderella', aya.x + 10, aya.y - 1, { id: 'cinderella', facing: -1, alpha: 0, shadow: false });
    cin.z = 10;
    await S.animate(0.4, (k) => { cin.alpha = 0.85 * k; });
    const f4 = anc('cinderella_salon', 'face4', [412, 70]);
    const lt = T().prop(S, 'gold_trail', f4[0], 150, { id: 'facefly', z: 80 });
    if (lt) await S.arc(lt, y2.x, y2.y + 0.5, 30, 0.7, { z1: 36 });
    if (lt) lt.remove = true;
    S.flash(0.3, 0.8, '#fff4c0');
    S.sfx('sparkle', 1);
    P4().fixGlow(S, y2.x, y2.y - 20, { n: 7 });
    y2.tint = null;
    S.mark('ch7_face_back');
    await S.wait(0.5);
    S.face(y2, p);
    await S.say(YK(), '康一君……！', { expr: 'smile', actor: y2 });
    await S.say('aya', '恋爱不是靠脸的运气撑着的。我要看的，是你们肯不肯为对方豁出去。');
    await S.say('aya', '……这次的魔法，免费。', { expr: 'smile' });
    await S.animate(0.4, (k) => { cin.alpha = 0.85 * (1 - k); });
    cin.remove = true;
    await S.fadeOut(0.6);
    clearStage('salon_ch7');
  }

  // ================================================================ 节拍 7–8 几天后，裁缝店：纽扣、登记簿、白光、枯萎穿心攻击
  async function beatTailor(S) {
    const p = S.player;
    S.party(['jotaro4', 'koichi'], { leader: 'jotaro4' });
    S.leadable('koichi', false, { msg: '康一：「承太郎先生，拜托了……」' });
    const cf = anc('tailor_shop', 'counter_front', [272, 160]), led = anc('tailor_shop', 'ledger', [240, 98]);
    const doorIn = anc('tailor_shop', 'door_in', [25, 140]), blast = anc('tailor_shop', 'blast', [250, 154]);
    await S.setStage('tailor_ch7', { x: cf[0] - 40, y: 160, facing: 1, music: 'tension', fade: false });
    S.state('after', 0);
    const ko = S.actor('koichi');
    if (ko) { ko.follow = null; Object.assign(ko, { x: cf[0] - 70, y: 164, facing: 1 }); }
    const tl = S.spawn('tailor', anc('tailor_shop', 'counter', [272, 146])[0] + 10, 148, { id: 'tailor', facing: -1 });
    snapTo({ x: cf[0] - 30 });
    await S.title('days_later', { y: 110 });
    await S.fadeIn(0.5);
    S.location('tailor', { y: NAME_TOP });
    const btn = T().prop(S, 'button', p.x + 8, p.y + 0.5, { id: 'button', z: 28 });
    await S.say('jotaro4', '重清最后抓在手里的，就是这颗纽扣。……是从西装袖口上扯下来的。');
    S.mark('ch7_tailor');
    await S.say('koichi', '这种纽扣很少见吧？做西装的店……杜王町就这一家。');
    await S.say('tailor', '这个牌子的纽扣啊……前几天还有位客人拿来让我缝。我这就翻登记簿。');
    S.nameCard('tailor', { y: NAME_TOP });
    if (btn) btn.remove = true;
    await S.narrate('只要看到那个名字，杀死重清的人……就有名字了。', { pos: 'top' });
    // 门口滚进来一个带履带的小东西
    const sha = S.spawn('sha', doorIn[0], doorIn[1] + 18, { id: 'sha_in', facing: 1 });
    S.sfx('skid', 0.5);
    await S.walk(sha, led[0] - 20, 160, { speed: 46 });
    S.sfxText('看这边！', sha, { dur: 0.9 });
    await S.say('sha', '看这边！', { name: '尖细的声音', portrait: false });
    S.face(p, -1);
    await S.say('jotaro4', '……康一，趴下！', { expr: 'rage' });
    sha.play('boom');
    S.sfx('explosion', 1);
    S.flash(0.8, 1, '#ffffff');
    S.shake(6, 0.6);
    S.mark('ch7_blast');
    await S.wait(0.3);
    S.state('after', 1);
    sha.remove = true;
    tl.x = blast[0] + 40; lieDown(S, tl);
    S.fx('smoke', { x: blast[0], y: blast[1], n: 10, rise: 20, life: 1.2 }, { life: 1.6 });
    await S.wait(1.0);
    await S.say('koichi', '店、店老板……登记簿被炸没了！', { expr: 'shock' });
    await S.say('jotaro4', '他只是昏过去了。……那东西还在外面。是个自己会动的炸弹。');
    await S.fadeOut(0.4);
    // 马路上：蓝色的小坦克慢慢转过来
    await S.setStage('street_ch7', { x: 300, y: 160, facing: -1, music: 'tension', fade: false });
    S.state('after', 1); S.state('closed', 0);
    const ko2 = S.actor('koichi');
    if (ko2) { ko2.follow = null; Object.assign(ko2, { x: 250, y: 152, facing: 1 }); }
    Object.assign(S.player, { x: 300, y: 160, facing: 1 });
    const s2 = S.spawn('sha', 470, 158, { id: 'sha_card', facing: -1 });
    snapTo({ x: 380 });
    await S.fadeIn(0.4);
    S.standCard('sha', { y: NAME_TOP });
    S.cue('sting_reveal');
    S.mark('ch7_sha_card');
    await S.wait(1.0);
    await S.say('jotaro4', '本体不在附近。……这东西是冲着“热”来的。');
    await S.say('koichi', '它、它朝我过来了！', { expr: 'shock' });
    S.music('battle', 0.3);
    await S.vs({ key: 'sha', hero: 'jotaro4', enemy: { cid: 'sha', anim: 'idle' } });
    G.uifx.vsTag('sha');
    s2.remove = true;
  }

  // ================================================================ 段 A 之后：坦克绕到康一背后，承太郎扑过去挡住
  async function beatShield(S) {
    const p = S.player, ko = S.actor('koichi');
    const sha = S.spawn('sha', ko.x + 60, ko.y, { id: 'sha_cut', facing: -1 });
    snapTo({ x: ko.x + 40 });
    await S.walk(sha, ko.x - 16, ko.y + 4, { speed: 70 });
    S.face(sha, 1);
    await S.say('sha', '看这边！', { name: '枯萎穿心攻击', portrait: false });
    S.walk(p, ko.x - 6, ko.y + 6, { speed: 160, anim: 'run' }).catch(G.cancelIgnore);
    await S.wait(0.25);
    sha.play('boom');
    S.sfx('explosion', 1);
    S.flash(0.8, 1, '#ffffff');
    S.shake(6, 0.6);
    S.mark('b11a_shield');
    await S.wait(0.4);
    sha.remove = true;
  }

  // ================================================================ 节拍 10 康一一个人：回音 ACT3
  async function beatAct3(S) {
    const jd = anc('morioh_avenue', 'jotaro_down', [620, 168]);
    const jt = S.actor('jotaro4'), ko = S.actor('koichi');
    // 镜头切到马路中间：承太郎倒在地上，大衣烧破了
    S.setLeader('koichi', { force: true, silent: true });
    const p = S.player;
    if (jt) { jt.follow = null; jt.x = jd[0]; jt.y = jd[1]; jt.facing = -1; lieDown(S, jt); }
    Object.assign(p, { x: jd[0] + 90, y: 160, facing: -1 });
    const sha = S.spawn('sha', jd[0] - 100, 156, { id: 'sha_cut', facing: 1 });
    S.fx('smoke', { x: jd[0], y: jd[1], n: 8, rise: 18, life: 1.2 }, { life: 1.6 });
    snapTo({ x: jd[0] });
    await S.wait(0.8);
    await S.say('koichi', '承太郎先生！！', { expr: 'shock' });
    await S.say('sha', '看这边！', { name: '枯萎穿心攻击', portrait: false });
    await S.narrate('我好怕。腿在抖。……可是承太郎先生，是为了护住我才倒下的。', { pos: 'top' });
    await S.say('koichi', '我……不逃了！', { expr: 'rage' });
    // 一个小小的人形站起来：灰白的身体、绿色的头冠
    const e3 = S.spawn('echoes3', p.x - 14, p.y - 1, { id: 'echoes3_cut', facing: -1, alpha: 0, shadow: false });
    e3.z = 6;
    S.sfx('stand_summon_star', 0.7);
    S.fx('sparkle', { x: e3.x, y: e3.y - 24, n: 8 }, { life: 0.6 });
    await S.animate(0.6, (k) => { e3.alpha = k; e3.z = 6 + 8 * k; });
    S.standCard('echoes3', { y: NAME_TOP });
    S.cue('sting_reveal');
    S.mark('ch7_act3');
    await S.wait(1.0);
    await S.say('echoes3', 'Let\'s ki……不对。主人，请下命令。', { actor: e3 });
    await S.say('koichi', '它、它说话了？！', { expr: 'shock' });
    await S.say('koichi', '……把那个坦克，按在地上！', { expr: 'rage' });
    await S.animate(0.3, (k) => { e3.alpha = 1 - k; });
    e3.remove = true; sha.remove = true;
    S.hint('回音 ACT3：J 近身拳（第三下最重）　重量满了按 U：3 FREEZE', 6);
  }

  // ================================================================ 节拍 12 本体被拖出小巷、「我拒绝」
  async function beatKiraPulled(S) {
    const p = S.player, alley = anc('morioh_avenue', 'alley', [307, 146]), jd = anc('morioh_avenue', 'jotaro_down', [620, 168]);
    const jt = S.actor('jotaro4');
    const stuck = S.spawn('sha', 560, 150, { id: 'sha_stuck', facing: -1 });
    S.pose(stuck, 'stuck');
    const e3 = S.spawn('echoes3', 548, 150, { id: 'echoes3_hold', facing: 1, shadow: false });
    e3.z = 4;
    Object.assign(p, { x: 520, y: 162, facing: -1 });
    focus({ x: 440 });
    await S.narrate('3 FREEZE 压住的是那个坦克……可是，有人“跟着”变重了。', { pos: 'top' });
    // 小巷里一个穿西装的男人，被一股看不见的重量拖着，一步一步走出来
    const kira = S.spawn(cid('kira'), alley[0], alley[1], { id: 'kira_cut', facing: 1, name: '吉良吉影' });
    S.sfx('metal_scrape', 0.5);
    await S.walk(kira, 470, 158, { speed: 14 });
    S.mark('ch7_kira_pulled');
    await S.say(cid('kira'), '……真是个让人不愉快的小鬼。', { expr: 'rage', actor: kira, name: '吉良' });
    S.nameCard(cid('kira'), { y: NAME_TOP });
    S.standCard(cid('killerqueen'), { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.wait(1.0);
    await S.say(cid('kira'), '我只想安安静静地生活。……为什么你们非要来打扰？', { actor: kira, name: '吉良' });
    await S.walk(kira, p.x - 18, p.y, { speed: 30 });
    kira.play('punch');
    S.sfx('punch_heavy', 0.8);
    S.shake(3, 0.25);
    await S.arc(p, p.x + 26, p.y + 4, 10, 0.35, { anim: 'hurt' });
    lieDown(S, p);
    await S.wait(0.4);
    await S.say('koichi', '你、你就是……杀了重清的人……', { expr: 'shock' });
    await S.say(cid('kira'), '把这个替身解除。我数到三。', { actor: kira, name: '吉良' });
    await S.say('koichi', '……我拒绝。', { expr: 'smile' });
    S.mark('ch7_refuse');
    await S.say(cid('kira'), '那就——', { expr: 'rage', actor: kira, name: '吉良' });
    // 他身后，承太郎慢慢站起来
    if (jt) { getUp(S, jt); jt.x = jd[0] - 40; jt.y = 160; S.face(jt, -1); }
    focus({ x: (kira.x + jd[0]) / 2 });
    S.sfx('footstep0', 0.6);
    await S.wait(0.5);
    await S.say('jotaro4', '……你的对手，是我。', { expr: 'rage' });
    S.face(kira, 1);
    await S.say(cid('kira'), '……！', { expr: 'shock', actor: kira, name: '吉良' });
    e3.remove = true;
    kira.remove = true;
    S.music('battle', 0.3);
    await S.vs({ key: 'kira', hero: 'jotaro4', enemy: { cid: cid('kira'), anim: 'pose' } });
    G.uifx.vsTag('kira');
    getUp(S, p);
    focus(null);
  }

  // ================================================================ 节拍 14 段 C 之后：他看得见替身 → 黑屏
  async function beatSeesStand(S) {
    const p = S.player, kira = S.actor('kira'), ko = S.actor('koichi');
    const vend = anc('morioh_avenue', 'vending', [407, 146]);
    // 收尾的一记欧拉：吉良飞出去撞上售货机
    S.face(p, kira);
    await S.summon(p, { dur: 0.08, rise: 4 });
    S.standAct(p, 'punch', { dx: 22, z: 4, dur: 0.5 });
    S.sfx('punch_heavy', 1);
    S.sfxText('ORA!!', kira, { dur: 0.9 });
    S.impact('invert', 1 / 30);
    S.shake(5, 0.35);
    S.mark('b11c_ora');
    if (kira) { await S.arc(kira, vend[0] + 10, 150, 18, 0.45, { anim: 'hurt' }); S.pose(kira, 'hurt'); }
    S.sfx('metal_crunch', 0.8);
    S.recall(p);
    await S.wait(0.5);
    await S.say('jotaro4', '……呀嘞呀嘞。');
    lieDown(S, p);
    await S.wait(0.6);
    // 仗助和亿泰从右边跑过来
    const js = S.spawn('josuke', 980, 158, { id: 'josuke_run', facing: -1 });
    const ok = S.spawn(cid('okuyasu'), 1000, 166, { id: 'okuyasu', facing: -1, name: '虹村亿泰' });
    focus({ x: (p.x + 600) / 2 });
    S.walk(ok, p.x + 60, 166, { speed: 120, anim: 'run' }).catch(G.cancelIgnore);
    await S.walk(js, p.x + 30, 158, { speed: 120, anim: 'run' });
    await S.say('josuke', '承太郎先生！康一！', { expr: 'shock', actor: js });
    // 两道金光：承太郎、康一坐起来
    await S.summon(js, { dur: 0.1, rise: 4 });
    S.standAct(js, 'reach', { dx: 18, z: 2, dur: 0.8 });
    P4().fixGlow(S, p.x, p.y - 10);
    if (ko) P4().fixGlow(S, ko.x, ko.y - 10);
    await S.wait(0.6);
    S.recall(js);
    getUp(S, p); if (ko) getUp(S, ko);
    await S.say(cid('okuyasu'), '这个穿西装的就是杀人魔？看着挺普通的嘛。', { actor: ok, name: '亿泰' });
    if (kira) { S.unpose(kira); S.face(kira, js); }
    await S.say(cid('kira'), '救、救命……我只是路过……你能把我也治好吗？', { expr: 'shock', actor: kira, name: '吉良' });
    await S.say('josuke', '……行吧，伤成这样也没法跑。', { actor: js });
    await S.walk(js, kira.x + 34, kira.y, { speed: 50 });
    S.face(js, kira);
    await S.summon(js, { dur: 0.1, rise: 4 });
    S.standAct(js, 'reach', { dx: 14, z: 2, dur: 1.2 });
    await S.wait(0.5);
    // 吉良的视线跟着疯狂钻石的手移了一下
    S.emote(kira, '……', 1.2);
    await S.wait(0.6);
    S.recall(js);
    await S.say(cid('okuyasu'), '喂。……你刚才在看什么？', { actor: ok, name: '亿泰', expr: 'rage' });
    await S.say(cid('kira'), '……！', { expr: 'shock', actor: kira, name: '吉良' });
    await S.say('koichi', '他看得见替身！他就是本体！', { expr: 'shock' });
    S.mark('ch7_sees_stand');
    await S.say(cid('kira'), '……啧。', { expr: 'rage', actor: kira, name: '吉良' });
    // 黑屏。一声闷响，压着嗓子喘一口气。坦克从柏油里猛地跳出来
    await S.fadeOut(0.15);
    S.stopMusic(0.1);
    await S.wait(0.5);
    S.sfx('thud', 0.9);
    S.shake(2, 0.2);
    await S.wait(0.6);
    S.sfx('grunt_enemy', 0.4);
    await S.wait(0.8);
    S.mark('ch7_hand');
    if (kira) kira.remove = true;
    const stuck = S.actor('sha_stuck');
    if (stuck) { S.unpose(stuck); stuck.x = 560; stuck.y = 158; }
    await S.fadeIn(0.3);
    S.sfx('skid', 0.7);
    await S.say('koichi', '3 FREEZE 的重量……断掉了！他把连着替身的那只手——', { expr: 'shock' });
    await S.say('jotaro4', '……别看。追！', { expr: 'rage' });
    js.remove = true; ok.remove = true;
  }

  // ================================================================ 节拍 15 修复光自由走动：金线追到美容院门口
  async function trailIn(S) {
    const door = anc('morioh_avenue', 'salon_door', [919, 146]);
    S.party(['josuke', 'koichi'], { leader: 'josuke' });
    S.leadable('koichi', false, { msg: '康一：「仗助君，跟着光走！」' });
    const p = S.player;
    Object.assign(p, { x: 360, y: 160, facing: 1, visible: true });
    const ko = S.actor('koichi');
    if (ko) Object.assign(ko, { x: 330, y: 164 });
    const ok = S.spawn(cid('okuyasu'), 336, 156, { id: 'okuyasu', facing: 1, name: '虹村亿泰' });
    S.follow(ok, 'player');
    const st = S.actor('sha_stuck');
    if (st) { st.x = 520; st.y = 150; S.pose(st, 'stuck'); }
    // 亿泰削掉了它脚下的地面，坦克卡在坑里（只在台词里交代）
    snapTo({ x: 420 });
    await S.say('josuke', '跑不掉的。……他掉在地上的东西，我来“修”。', { expr: 'rage' });
    await S.summon(p, { dur: 0.1, rise: 4 });
    S.standAct(p, 'reach', { dx: 18, z: 0, dur: 0.8 });
    P4().fixGlow(S, p.x + 20, p.y);
    const tr = T().prop(S, 'gold_trail', p.x + 24, p.y, { id: 'trail', z: 20 });
    if (tr) { tr.frozen = null; tr.hold = false; tr.play('idle'); }
    S.recall(p);
    S.mark('ch7_trail');
    await S.say('josuke', '修好的东西，会自己回到原来的地方！跟着那道光！');
    await S.say(cid('okuyasu'), '坦克我来——削！……好，它卡在坑里出不来了！', { actor: ok, name: '亿泰', expr: 'smile' });
    // 金线：始终在仗助前面 60–90 px，到美容院门口停住
    const trail = { tr, x: p.x + 24, done: false };
    T().tick((dt) => {
      if (!tr || tr.remove) return true;
      const pl = G.world.player;
      const want = Math.min(door[0], Math.max(trail.x, pl.x + 70));
      trail.x += Math.sign(want - trail.x) * Math.min(Math.abs(want - trail.x), 90 * dt);
      tr.x = trail.x; tr.y = 158; tr.z = 18 + Math.round(Math.sin(now() * 6) * 3);
      if (Math.random() < 0.2) S.fx('sparkle', { x: tr.x, y: tr.y - tr.z, n: 1 }, { life: 0.3 });
      return false;
    });
    G.world.stage.triggers.push({ x0: door[0] - 40, x1: 980, run: async () => { F().trailEnd = true; } });
    T().goal(S, { x: door[0], y: 158, label: '金线', delay: 25, every: 15, done: () => !!F().trailEnd, text: '跟着金线往右走' });
    S.hint('跟着金线往右走（方向键）', 6);
  }
  async function trailEnd(S) {
    const p = S.player, door = anc('morioh_avenue', 'salon_door', [919, 146]);
    const tr = S.actor('trail');
    S.hint(null);
    G.world.stage.triggers.length = 0;
    if (tr) { S.fx('sparkle', { x: tr.x, y: tr.y - 18, n: 8 }, { life: 0.5 }); S.sfx('glass_break', 0.4); tr.remove = true; }
    S.mark('ch7_trail_end');
    S.face(p, 1);
    await S.say('josuke', '光……断了？！', { expr: 'shock' });
    await S.say(cid('okuyasu'), '怎么回事？这家是美容院吧？', { actor: 'okuyasu', name: '亿泰' });
    await S.narrate('美容院里，一点声音也没有。', { pos: 'top' });
    await S.fadeOut(0.6);
    void door;
  }

  // ================================================================ 节拍 16 吉良视角：辻彩（只在旁白里交代）
  async function beatKiraPov(S) {
    const p = S.player;
    await S.setStage('salon_ch7', { x: 60, y: 160, music: null, fade: false });
    p.visible = false;
    for (const a of (G.party && G.party.members) || []) a.visible = false;
    S.state('night', 1);
    S.filter('tint', 0.25, { color: '#1a2a5a' });
    S.filter('vignette', 0.6, { colour: '#000000', inner: 0.5 });
    const aya = S.spawn('aya', 300, 154, { id: 'aya', facing: 1 });
    const kira = S.spawn(cid('kira'), 40, 158, { id: 'kira_pov', facing: 1, name: '吉良吉影' });
    snapTo({ x: 200 });
    await S.title('kira_pov', { y: 110 });
    await S.fadeIn(0.6);
    S.music('tension', 0.6);
    S.sfx('ding', 0.5);
    await S.walk(kira, 230, 158, { speed: 34 });
    S.face(aya, -1);
    await S.say(cid('kira'), '我需要一张新的脸。……还有指纹。', { actor: kira, name: '吉良' });
    await S.say('aya', '你……你是谁？我不给不认识的人——', { expr: 'shock' });
    const kq = S.spawn(cid('killerqueen'), kira.x - 10, kira.y - 1, { id: 'kq_pov', facing: 1, alpha: 0, shadow: false });
    kq.z = 8;
    S.sfx('menacing', 0.6);
    await S.animate(0.5, (k) => { kq.alpha = 0.8 * k; });
    await S.say(cid('kira'), '你没得选。', { expr: 'rage', actor: kira, name: '吉良' });
    await S.say('aya', '……要换成谁的脸？', { expr: 'shock' });
    // 橱窗外，一个下班的上班族正好路过（只给剪影）
    const ks = S.spawn('kawajiri', -20, 146, { id: 'kosaku_sil', facing: 1, shadow: false });
    ks.tint = { color: '#04020a', k: 1 };
    S.face(kira, -1);
    await S.walk(ks, 70, 146, { speed: 30 });
    await S.say(cid('kira'), '……那个人就行。', { actor: kira, name: '吉良' });
    S.mark('ch7_new_face');
    S.sfx('sparkle', 0.8);
    S.flash(1.0, 1, '#ffffff');
    await S.wait(0.5);
    ks.remove = true; kq.remove = true;
    await S.narrate('那天夜里，灰姑娘美容院的辻彩，再也没有醒来。', { pos: 'top' });
    await S.fadeOut(0.8);
    aya.remove = true; kira.remove = true;
    S.filter(null);
  }

  // ================================================================ 节拍 17 走出美容院的人 → 第二天 → To Be Continued
  async function beatWalkout(S) {
    const p = S.player, door = anc('morioh_avenue', 'salon_door', [919, 146]);
    await S.setStage('street_ch7', { x: 860, y: 162, facing: 1, music: null, fade: false });
    S.state('after', 1); S.state('pm', 1);
    for (const a of (G.party && G.party.members) || []) a.visible = true;
    p.visible = true;
    const ko = S.actor('koichi');
    if (ko) { ko.follow = null; Object.assign(ko, { x: 830, y: 166, facing: 1 }); }
    const ok = S.spawn(cid('okuyasu'), 846, 154, { id: 'okuyasu', facing: 1, name: '虹村亿泰' });
    snapTo({ x: 840 });
    await S.fadeIn(0.6);
    // 美容院门开了：黑色刺头短发、穿西装的男人，礼貌地点一下头，往左走远
    S.sfx('ding', 0.5);
    const kw = S.spawn('kawajiri', door[0], door[1], { id: 'kawajiri', facing: -1, name: '穿西装的男人' });
    await S.walk(kw, 890, 150, { speed: 30 });
    kw.play('pose');
    await S.wait(0.5);
    S.mark('ch7_walkout');
    S.walk(kw, 560, 148, { speed: 30 }).catch(G.cancelIgnore);
    await S.wait(0.8);
    S.face(ok, -1);
    await S.say(cid('okuyasu'), '……刚才出来的是谁？', { actor: ok, name: '亿泰' });
    await S.say('josuke', '普通的上班族吧。……光断在这儿，那家伙肯定还在里面！', { expr: 'rage' });
    S.face(p, 1);
    S.walk(p, door[0], door[1], { speed: 80, anim: 'run' }).then(() => { p.visible = false; }, G.cancelIgnore);
    if (ko) S.walk(ko, door[0], door[1], { speed: 80, anim: 'run' }).then(() => { ko.visible = false; }, G.cancelIgnore);
    S.walk(ok, door[0], door[1], { speed: 80, anim: 'run' }).then(() => { ok.remove = true; }, G.cancelIgnore);
    // 镜头留在那个人的背影上
    focus(kw);
    await S.wait(1.8);
    await S.fadeOut(0.8);
    kw.remove = true;
    // 第二天：美容院拉下了百叶
    focus(null);
    S.state('pm', 0); S.state('closed', 1);
    p.visible = false; if (ko) ko.visible = false;
    snapTo({ x: 840 });
    await S.title('next_day', { y: 110 });
    await S.fadeIn(0.6);
    S.music('sad', 1.0);
    await S.narrate('第二天，美容院没有再开门。辻彩小姐不见了。', { pos: 'top' });
    await S.narrate('我们知道了他的名字——吉良吉影。可是那张脸，已经没有人认得出来了。', { pos: 'top' });
    S.stopMusic(0.8);
    await S.tbc({ hold: 2.0 });
    S.mark('ch7_tbc');
  }

  // ================================================================ 第7章主流程
  G.STORY.ch7 = async function (S) {
    if (T().resetCounters) T().resetCounters();
    P4().clearOverlays();
    mem = null; puzzle = null;
    for (const id of ['salon_ch7', 'date_ch7', 'tailor_ch7', 'street_ch7']) clearStage(id);
    await S.chapterCard('ch7');
    S.party(['koichi'], { leader: 'koichi' });
    await S.run(async (S2) => {
      await beatCalendar(S2);
      await beatSalon(S2);
      await dateIn(S2);
    }, { keepLocked: true });
    // 节拍 3 自由走动：四条线索全齐，或者 70 s
    await S.run(async () => {});
    const t3 = now();
    const nextClue = () => {
      const t1 = anc('morioh_grand_hotel', 'table1', [344, 150]), t2 = anc('morioh_grand_hotel', 'table2', [398, 150]);
      if (!mem || !mem.got[0]) return [300, '由花子'];
      if (!mem.got[1]) return [t1[0], '露天座'];
      if (!mem.got[2]) return [t2[0], '露天座'];
      return [300, '由花子'];
    };
    let g3 = null, g3k = null;
    T().tick(() => {
      const [x, lb] = nextClue();
      if (g3k !== x + lb) { if (g3) g3.stop(); g3k = x + lb; g3 = T().goal(S, { x, y: 156, label: lb, delay: 25, every: 15, done: () => gotN() >= 4, text: '去' + lb + '那边看看' }); }
      return gotN() >= 4;
    });
    await S.until(() => (gotN() >= 4 || now() - t3 > 70) && !S.busy);
    if (g3) g3.stop();
    clearStage('date_ch7');
    // 节拍 4–5 → 节拍 6 解谜
    await S.run(async (S2) => {
      await beatLipstick(S2);
      await beatMasked(S2);
      await puzzleIn(S2);
    }, { keepLocked: true });
    await S.run(async () => {});
    const f4 = anc('cinderella_salon', 'face4', [412, 70]);
    T().goal(S, { x: f4[0], y: 146, label: '……刘海。', delay: 90, every: 20, done: () => !!(puzzle && puzzle.done),
      text: '辻彩指了指第 4 张脸：「……刘海。」' });
    const t6 = now();
    T().tick(() => { if (puzzle && !puzzle.done && now() - t6 > 90) { puzzle.last = RIGHT; return true; } return !!(puzzle && puzzle.done); });
    await S.until(() => !!(puzzle && puzzle.done) && !S.busy);
    // 节拍 6 收尾 → 7–8 裁缝店 → 第 11 战
    await S.run(async (S2) => {
      await faceBack(S2);
      await beatTailor(S2);
      S2.mark('b11a_start');
      await R().fightA(S2);
      await beatShield(S2);
      await beatAct3(S2);
      S2.mark('b11b_start');
      await R().fightB(S2);
      S2.setLeader('jotaro4', { force: true, silent: true });
      await beatKiraPulled(S2);
      S2.mark('b11c_start');
      await R().fightC(S2);
      await beatSeesStand(S2);
      await trailIn(S2);
    }, { keepLocked: true });
    // 节拍 15 修复光自由走动
    await S.run(async () => {});
    await S.until(() => !!F().trailEnd && !S.busy);
    await S.run(async (S2) => {
      await trailEnd(S2);
      S2.leave('jotaro4', { drop: true });
      await beatKiraPov(S2);
      await beatWalkout(S2);
    }, { keepLocked: true });
  };
  G.STORY.ch7.marks = ['ch7_calendar', 'ch7_salon', 'ch7_makeover', 'ch7_date', 'ch7_clues', 'ch7_lipstick', 'ch7_hug', 'ch7_masked',
    'ch7_faces', 'ch7_choose', 'ch7_face_back', 'ch7_tailor', 'ch7_blast', 'ch7_sha_card', 'b11a_start', 'b11a_cig', 'b11a_shield', 'ch7_act3',
    'b11b_start', 'b11b_freeze', 'ch7_kira_pulled', 'ch7_refuse', 'b11c_start', 'b11c_ora', 'ch7_sees_stand', 'ch7_hand', 'ch7_trail',
    'ch7_trail_end', 'ch7_new_face', 'ch7_walkout', 'ch7_tbc'];
})();
