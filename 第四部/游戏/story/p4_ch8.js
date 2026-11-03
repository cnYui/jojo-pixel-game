// 第8章　吉良家旧宅 / 原子心之父（G.STORY.ch8，地图 id 后缀 _ch8；开发脚本 第四部/docs/第8章_开发脚本.md）。整章流程：
//   节拍 1 篇章卡 → 日历（吉良家旧宅、杜王站、1999年7月）→ 2 旧宅门口 → 3 旧宅自由走动（本子、奖状、相册、遗照）
//   → 4 咔嚓：照片空间 → 第 12 战 原子心之父（仗助 ⇄ 承太郎，拍到他一个人就赢）→ 5 封进相片、“他换了一张脸”、
//   修锁开箱 → 弓与箭被吉广卷走 → 6 吉良视角：吉良吉影的新生活（川尻家傍晚，不能操作）
//   → 7 杜王站前自由走动（康一 / 乔瑟夫 / 露伴，找透明的静）→ 8 猜拳小子大柳贤 → 第 13 战 Boy II Man（露伴，先赢 3 局）
//   → 9 “照片里的老爷爷拿箭射了我” → 10 那天夜里：川尻家天花板角落的摄像机 → To Be Continued。
//   露伴（第5章）、乔瑟夫（第4章）、换脸后的吉良（第7章）由别章画：cast() 先找正式 cid，没有就用本章的临时占位 ph8_*。
//   两场战斗在 story/p4_ch8_fights.js（G.P4CH8）。
'use strict';
(function () {
  const G = window.G, { base, walls } = G.p4Stage;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const C8 = () => G.P4CH8;
  const F = () => G.flags;
  const now = () => (G.clk ? G.clk.world : 0);
  const NAME_TOP = 100;
  const PH = { rohan: 'ph8_rohan', joseph_old: 'ph8_joseph', kawajiri: 'ph8_kosaku' };
  const cast = (cid) => (G.D && G.D.chars && G.D.chars[cid] ? cid : PH[cid] || cid);
  const ui = () => (G.D && G.D.ui) || {};
  // 名牌 / 替身卡 / 地点卡：别章的人（露伴、乔瑟夫）的卡由别章画，没合进来时不放（放了会记成缺图）
  const nameCard = (S, cid) => { if ((ui().namecards || {})[cid]) S.nameCard(cid, { y: NAME_TOP }); };
  const standCard = (S, id) => { if ((ui().standcards || {})[id]) S.standCard(id, { y: NAME_TOP }); };
  const focus = (o) => { G.world.focus = o; };
  const snapTo = (o) => { G.world.focus = o; G.world.snapCamera(); };
  const pool = (cid) => G.party._actor(cid);
  function place(S, cid, x, y, facing) {
    const a = pool(cid), W = G.world;
    Object.assign(a, { x, y, z: 0, facing: facing || 1, follow: null, hold: false, script: null, state: 'idle', remove: false, rot: 0, alpha: 1, visible: true });
    if (W.player !== a) a.team = 'npc';
    a.play(a.idleAnim || 'idle');
    W.stage.add(a);
    return a;
  }

  Object.assign(G.NAMES, { yoshihiro: '吉广', oyanagi: '大柳', shinobu: '忍', ph8_rohan: '露伴', ph8_joseph: '乔瑟夫', ph8_kosaku: '吉良', kawajiri: '吉良' });

  // ================================================================ 地图（docs/第8章_背景.md）
  const ST = G.STAGES;
  ST.map_ch8 = base('map_ch8', 'morioh_map', 320, { yMin: 160, yMax: 170, music: null, obstacles: [] });
  ST.kiraout_ch8 = base('kiraout_ch8', 'kira_house_out', 480, { music: 'tension', state: { pm: 1 }, obstacles: walls(8, 472, 480) });
  ST.kirahouse_ch8 = base('kirahouse_ch8', 'kira_house', 640, { music: 'tension', state: {}, obstacles: walls(8, 632, 640) });
  ST.kawajiri_ch8 = base('kawajiri_ch8', 'kawajiri_house', 640, { music: null, state: { dusk: 1 }, obstacles: walls(8, 632, 640) });
  ST.station_ch8 = base('station_ch8', 'morioh_station', 960, { music: 'daily', state: {}, obstacles: walls(96, 792, 960) });

  // ================================================================ 替身调查的兜底（正式的由别章注册：康一第2章、露伴第5章、乔瑟夫第4章）
  const LOOK = G.LOOK;
  if (!LOOK.koichi) LOOK.koichi = { tags: ['listen'], cd: 1.5, miss: '……什么都没听到。', run: async (S) => { S.sfx('blip', 0.5); await S.wait(0.4); } };
  for (const cid of ['joseph_old', 'ph8_joseph']) {
    if (!LOOK[cid]) LOOK[cid] = { tags: ['nensha'], cd: 2, miss: '……人老了，手也抖了。', run: async (S, p) => {
      S.sfx('camera_shutter', 0.8); S.flash(0.12, 0.6, '#d8b0ff');
      S.fx('sparkles', { x: p.x, y: p.y - 26, n: 8, radius: 12, colour: '#c080ff', period: 0.5, size: 3 }, { life: 0.8 });
      await S.wait(0.6);
    } };
  }
  for (const cid of ['rohan', 'ph8_rohan']) {
    if (!LOOK[cid]) LOOK[cid] = { tags: ['read'], cd: 2, miss: '没有值得读的东西。', run: async (S) => { S.sfx('card_flip', 0.6); await S.wait(0.5); } };
  }

  // ================================================================ 节拍 1 篇章卡 → 日历（1999年7月）
  //   P4.calendar 只会盖 4 月的章：照它的画法在这里画一份本章的（图钉 + 7 月红章 + 前面各章的灰图钉）
  const PINS = [{ xy: [130, 104], label: '吉良家旧宅' }, { xy: [203, 62], label: '杜王站' }];
  const GRAY = [[170, 70], [118, 126], [96, 112], [236, 120]];
  async function calendar(S) {
    const m = ui().map || {}, m8 = ui().map8 || {};
    const img = (k) => { const im = k ? G.image(k) : null; return im && G.ready(im) ? im : null; };
    const ease = (u) => 1 - Math.pow(1 - Math.max(0, Math.min(1, u)), 3);
    const pins = PINS.map((p, i) => ({ p, t0: 0.5 + i * 0.45 }));
    const stampAt = 0.5 + pins.length * 0.45 + 0.25;
    const h = P4().overlay((g, t) => {
      const pin = (xy, im, dy = 0) => {
        if (!im) return;
        const meta = m.pin || { ax: 5, ay: 15 };
        g.drawImage(im, Math.round(xy[0] * 2 - meta.ax * 2), Math.round(xy[1] * 2 - meta.ay * 2 + dy), im.width * 2, im.height * 2);
      };
      for (const xy of GRAY) pin(xy, img(m.pin_gray && m.pin_gray.image));
      for (const q of pins) {
        const u = (t - q.t0) / 0.3;
        if (u < 0) continue;
        const dy = u < 1 ? -60 * (1 - ease(u)) : u < 1.4 ? -Math.round(Math.sin((u - 1) / 0.4 * Math.PI) * 6) : 0;
        pin(q.p.xy, img(m.pin && m.pin.image), dy);
        if (u >= 1) P4().text(g, q.p.label, Math.round(q.p.xy[0] * 2 + 12), Math.round(q.p.xy[1] * 2 - 34), '#fff4d6', 12, 'left', '#2a0a1a');
      }
      if (t >= stampAt) {
        const sm = m8.stamp, sim = sm && img(sm.image);
        if (sim) {
          const u = Math.min(1, (t - stampAt) / 0.14), sc = 1.9 - 0.9 * ease(u);
          const w = Math.round(sm.w * sc), hh = Math.round(sm.h * sc);
          g.save(); g.globalAlpha = Math.min(1, u * 2);
          g.drawImage(sim, Math.round(534 - w / 2), Math.round(262 - hh / 2), w, hh);
          g.restore();
        }
      }
      const pl = m.place, plim = pl && img(pl.image);
      if (plim) g.drawImage(plim, 640 - pl.w - 14, 12);
    }, { z: 1 });
    for (const q of pins) G.defer(q.t0 + 0.3, () => { S.sfx('pop', 0.7); S.sfx('thud', 0.4); }, 'ui');
    G.defer(stampAt, () => { S.sfx('thud', 1); S.sfx('card_flip', 0.6); S.shake(2, 0.2); }, 'ui');
    await S.wait(stampAt + 1.8, 'ui');
    return h;
  }
  async function beatCalendar(S) {
    S.player.visible = false;
    await S.setStage('map_ch8', { x: 160, y: 165, music: null });
    const h = await calendar(S);
    S.mark('ch8_calendar');
    await S.fadeOut(0.45);
    h.close();
  }

  // ================================================================ 节拍 2 旧宅门口（傍晚）
  async function beatGate(S) {
    const p = S.player;
    p.visible = true;
    await S.setStage('kiraout_ch8', { x: 120, y: 158, facing: 1, music: 'tension', fade: false });
    S.state('pm', 1); S.state('gate', 0);
    const jt = S.actor('jotaro4');
    if (jt) Object.assign(jt, { x: 92, y: 152, facing: 1, follow: null });
    snapTo({ x: 200 });
    await S.fadeIn(0.6);
    if (jt) S.walk(jt, 196, 150, { speed: 50 }).catch(G.cancelIgnore);
    await S.walk(p, 220, 160, { speed: 50 });
    S.location('kira_house', { y: NAME_TOP });
    await S.say('jotaro4', '裁缝店的登记簿上写着这个地址。吉良吉影，三十三岁。');
    await S.say('josuke', '住宅区正中间的独栋……看着就是个普通人家啊。');
    await S.say('jotaro4', '普通人家，才最适合藏东西。');
    S.sfx('door', 0.7);
    S.state('gate', 1);
    S.mark('ch8_gate');
    await S.wait(0.4);
    await T().closeup4(S, { heads: [{ cid: 'josuke', expr: 'shock' }], dur: 0.4, bg: 'menace', sfx: 'menacing' });
    await S.say('josuke', '……二楼的窗帘，刚才动了一下？', { expr: 'shock' });
    await S.say('jotaro4', '进去。别碰任何照片。');
    if (jt) S.walk(jt, 226, 146, { speed: 50 }).catch(G.cancelIgnore);
    await S.walk(p, 232, 146, { speed: 50 });
    await S.fadeOut(0.5);
    focus(null);
  }

  // ================================================================ 节拍 3 旧宅自由走动
  async function lookNotebook(S, h, p) {
    if (p.cid !== 'jotaro4') return;
    await S.say('jotaro4', '……是指甲的长度。他每天都在量自己的指甲。');
    await S.say('jotaro4', '指甲长得越快的时候……就是他“想做事”的时候。');
    if (!F().notebook) { F().notebook = true; S.mark('ch8_notebook'); S.hint('线索：吉良吉影的档案', 3); }
  }
  async function useNotebook(S) {
    await S.say(null, '书桌上摊着一本本子。密密麻麻的日期和数字，字太小，看不清。');
    if (!F().notebook && S.player.cid !== 'jotaro4') S.hint('按 Q 换承太郎，按 U 看清小字', 5);
  }
  async function useAlbum(S) {
    await S.say(null, '一本相册。毕业照、运动会、修学旅行……');
    await S.say(null, '每一张照片上，同一个人的脸都被剪掉了。');
    await S.say('josuke', '……他连一张自己的脸都不想留下吗。', { expr: 'shock' });
    if (!F().album) { F().album = true; S.mark('ch8_album'); }
  }
  async function usePortrait(S) {
    await S.say(null, '长押上挂着一位老人的遗照。……照片里的眼睛，好像跟着人转。');
    F().portrait = true;
  }
  async function useAwards(S) {
    await S.say(null, '三张奖状、四座奖杯。……全是第三名。');
    await S.say('josuke', '一次第一都没拿过？这家伙是故意的吧。');
    await S.say('jotaro4', '不出风头，也不垫底。……他一直都是这样活的。');
  }
  async function useBox(S) {
    if (F().boxOpen) { await S.say(null, '箱子空了。'); return; }
    await S.say(null, '储物间里有一只长木箱，挂着一把生锈的锁。锁芯坏了，打不开。');
    if (F().afterFight && S.player.cid !== 'josuke') S.hint('换成仗助按 U：疯狂钻石能把坏锁修好', 5);
  }
  function setupHouse(after) {
    const st = G.world.stage;
    st.hotspots = [
      { id: 'notebook', x: 40, y: 150, r: 18, label: '书桌上的本子', tags: ['detail'], fx: 32, fy: 101, use: useNotebook, look: lookNotebook },
      { id: 'awards', x: 156, y: 150, r: 18, label: '奖状和奖杯', use: useAwards },
      { id: 'bookshelf', x: 94, y: 150, r: 14, label: '书架', use: async (S) => { await S.say(null, '一排排整整齐齐的书，书脊都朝着同一个方向。'); } },
      { id: 'portrait', x: 239, y: 150, r: 18, label: '佛坛的遗照', use: usePortrait },
      { id: 'album', x: 331, y: 152, r: 18, label: '桌上的相册', use: useAlbum },
      { id: 'tv', x: 393, y: 150, r: 16, label: '电视', use: async (S) => { await S.say(null, '电视没插电。屏幕上落了一层灰。'); } },
      { id: 'phone', x: 469, y: 150, r: 14, label: '电话台', use: async (S) => { await S.say(null, '电话线被拔掉了。'); } },
      { id: 'box', x: 588, y: 152, r: 20, label: '长木箱', tags: ['fix'], fx: 588, fy: 118, use: useBox, look: after ? fixBox : async (S) => { await S.say('josuke', '……先别动它。这屋子里有东西在看着我们。'); } },
    ];
    st.npcs = []; st.triggers = [];
  }
  async function houseIn(S) {
    const p = S.player;
    await S.setStage('kirahouse_ch8', { x: 470, y: 158, facing: -1, music: 'tension' });
    S.state('photo', 0);
    const jt = S.actor('jotaro4');
    if (jt) Object.assign(jt, { x: 494, y: 152, facing: -1 });
    G.world.snapCamera();
    S.hint('E 调查；按 Q 换承太郎，他的 U 能看清小字', 7);
    void p;
  }
  async function talkJotaro3(S) { await S.say('jotaro4', '……小心照片。'); }
  async function talkJosuke3(S) { await S.say('josuke', '这屋子安静得让人发毛。'); }

  // ================================================================ 节拍 4 咔嚓 → 第 12 战
  async function beatSnap(S) {
    const p = S.player;
    T().memberTalk({});
    if (p.cid !== 'josuke') S.setLeader('josuke', { force: true, silent: true });
    const pl = S.player, jt = S.actor('jotaro4');
    S.hint(null);
    // 两个人站到和室中间（照片空间 photo_x 150–510 里）
    if (pl.x < 200 || pl.x > 470) { pl.x = 330; pl.y = 160; }
    if (jt) { jt.follow = null; jt.x = G.clamp(pl.x - 40, 180, 480); jt.y = 156; }
    G.world.snapCamera();
    focus({ x: 330 });
    S.sfx('camera_shutter', 1);
    S.flash(0.25, 1, '#ffffff');
    S.state('photo', 1);
    S.mark('ch8_snap');
    await S.wait(0.6);
    S.face(pl, -1);
    await S.say('josuke', '刚才……是快门的声音？', { expr: 'shock' });
    // 一张相片从柜子底下滑出来，飘到半空；相片里的老人探出半个身子
    const ph = T().prop(S, 'ghost_photo', 280, 160, { id: 'gphoto', frame: 0, z: 2 });
    S.sfx('card_flip', 0.7);
    if (ph) await S.animate(0.8, (k) => { ph.z = 2 + 40 * k; ph.x = 280 + 20 * k; });
    const yh = S.spawn('yoshihiro', 300, 150, { id: 'yoshihiro_pre', facing: 1, alpha: 0 });
    yh.tint = { color: '#a08050', k: 0.35 }; yh.z = 26; yh.scale = 0.8;
    await S.animate(0.5, (k) => { yh.alpha = 0.85 * k; });
    nameCard(S, 'yoshihiro');
    standCard(S, 'atomheart');
    S.cue('sting_reveal');
    await S.wait(0.6);
    await S.say('yoshihiro', '你们已经在我的照片里了。', { expr: 'smile', actor: yh });
    await S.say('yoshihiro', '这个房间被拍下来的那一瞬间，就是你们的牢笼。哪儿也去不了。', { actor: yh });
    await S.say('jotaro4', '……他是照片里的人。拳头打不到照片。');
    await S.say('yoshihiro', '我儿子只想安静地生活。谁来打扰，我就让谁永远留在这张相片里！', { expr: 'rage', actor: yh });
    yh.remove = true; if (ph) ph.remove = true;
    S.music('battle', 0.3);
    await S.vs({ key: 'atomheart', hero: 'josuke', enemy: { cid: 'yoshihiro', anim: 'idle' } });
    G.uifx.vsTag('atomheart');
  }

  // ================================================================ 节拍 5 封进相片 → 修锁开箱 → 弓与箭被卷走
  async function beatSealed(S) {
    const p = S.player, jt = S.actor('jotaro4'), jo = S.actor('josuke');
    S.state('photo', 0);
    S.flash(0.2, 0.6, '#ffffff');
    // 吉广被拍进相片：地上那个人消失，变成一张相片
    const yhe = S.actor('yoshihiro');
    if (yhe) yhe.remove = true;
    const ph = T().prop(S, 'ghost_photo', (jt ? jt.x : p.x) + 12, 156, { id: 'gphoto', frame: 0, z: 22 });
    await S.wait(0.4);
    await S.say('jotaro4', '他只能待在自己的照片里。那就让他待在一张只有他自己的照片里。');
    await S.say('yoshihiro', '放、放我出去！', { expr: 'shock' });
    if (jo && ph) { await S.walk(jo, ph.x - 16, 156, { speed: 60 }).catch(G.cancelIgnore); S.face(jo, 1); }
    S.sfx('card_flip', 0.8); S.sfx('pop', 0.5);
    T().setFrame(ph, 1);
    await S.say('josuke', 'Great～对折，再贴上胶带。这下他哪儿都去不了了。', { expr: 'smile' });
    // 承太郎把相片钉到墙上（背景层 pinned）
    if (ph) await S.arc(ph, 359, 150, 30, 0.45, { z1: 70 }).catch(G.cancelIgnore);
    if (ph) ph.remove = true;
    S.state('pinned', 1);
    S.sfx('thud', 0.5);
    S.mark('ch8_pinned');
    await S.wait(0.4);
    await S.say('yoshihiro', '……没用的。吉影已经换了一张脸。你们找不到他的。', { name: '吉广（相片里闷闷的声音）' });
    await S.say('josuke', '换了一张脸……？！', { expr: 'shock' });
    S.mark('ch8_face');
    S.hint('线索：“他换了一张脸”', 3);
    await S.say('jotaro4', '……再找找。他爹拼了命也要守着的，一定不止一个秘密。');
    S.music('tension', 0.8);
  }
  async function fixBox(S) {
    if (F().boxOpen) { await S.say('josuke', '……已经修好了。'); return; }
    F().boxOpen = true;
    P4().fixGlow(S, 588, 118);
    await S.wait(0.4);
    S.sfx('door', 0.6);
    S.state('box', 1);
    const ar = T().prop(S, 'arrow2', 588, 150, { id: 'arrow2', z: 6 });
    S.sfx('sting_shock', 0.7);
    await S.say('josuke', '锁修好了……！这是……弓和箭？！', { expr: 'shock' });
    S.mark('ch8_arrow');
    await S.say('jotaro4', '形兆那支箭交给了 SPW 财团。……这是第二套。');
    // 走廊的窗被风吹开；墙上的胶带一松，相片哗啦展开，卷起弓与箭从窗口飞走
    S.sfx('wind', 0.8);
    S.state('window', 1);
    S.state('pinned', 0);
    const ph = T().prop(S, 'ghost_photo', 359, 150, { id: 'gphoto2', frame: 0, z: 70 });
    await S.say('yoshihiro', '……那是我儿子的东西！', { expr: 'rage', name: '吉广（相片里）' });
    focus({ x: 520 });
    if (ph) await S.arc(ph, ar ? ar.x : 588, 150, 20, 0.5, { z1: 10 }).catch(G.cancelIgnore);
    const fly = (o, x, z) => S.arc(o, x, 146, 40, 0.8, { z1: z }).catch(G.cancelIgnore);
    if (ar) fly(ar, 468, 70);
    if (ph) await fly(ph, 468, 76);
    S.sfx('whoosh', 0.9);
    if (ar) ar.remove = true;
    if (ph) ph.remove = true;
    S.mark('ch8_flyaway');
    await S.say('josuke', '啊！从窗户……！', { expr: 'shock' });
    await S.say('jotaro4', '……让他跑了。');
    await S.say('jotaro4', '有那支箭，他会去镇上找新的替身使者。');
    F().houseDone = true;
  }

  // ================================================================ 节拍 6 吉良视角：吉良吉影的新生活（川尻家，傍晚）
  async function beatKiraLife(S) {
    const p = S.player;
    S.party([cast('kawajiri')], { leader: cast('kawajiri') });
    await S.setStage('kawajiri_ch8', { x: 426, y: 150, facing: 1, music: null, fade: false });
    S.state('dusk', 1); S.state('night', 0); S.state('cam', 0);
    const kira = S.player;
    kira.hold = true;
    snapTo({ x: 430 });
    S.stopMusic(0.3);
    await S.fadeIn(0.8);
    await S.title('kira_life', { y: 110 });
    S.location('kawajiri', { y: NAME_TOP });
    S.music('tension', 1.2);
    await S.narrate('川尻浩作。三十三岁，公司职员。……从今天起，这就是我。', { pos: 'top' });
    S.sfx('blip', 0.4);
    S.sfxText('沙沙', { wx: 440, wy: 120, wz: 0 }, { dur: 0.8 });
    await S.narrate('签名的笔迹不对。……他的字，比我想的还要难看。', { pos: 'top' });
    S.mark('ch8_kira_sign');
    const sh = S.spawn('shinobu', 380, 156, { id: 'shinobu', facing: 1 });
    await S.walk(sh, 412, 154, { speed: 40 });
    nameCard(S, 'shinobu');
    S.sfx('pop', 0.4);
    await S.say('shinobu', '你今天……怎么这么早回家？');
    S.face(kira, -1);
    await S.say(cast('kawajiri'), '嗯。想早点回来。', { expr: 'smile' });
    await S.say('shinobu', '……你以前从来不会这么说。', { expr: 'shock' });
    S.mark('ch8_shinobu');
    await S.narrate('这个女人，对她的丈夫早就没有兴趣了。很好。……没兴趣的人，不会多问。', { pos: 'top' });
    S.sfx('door', 0.5);
    await S.say(null, '（走廊那头，早人的房门“咔哒”一声关上了）');
    await S.narrate('儿子叫早人，几乎不说话。……也好。', { pos: 'top' });
    S.walk(sh, 360, 158, { speed: 36 }).catch(G.cancelIgnore);
    await S.say('shinobu', '（……怎么觉得，他今天有点不一样。）');
    await S.fadeOut(0.8);
    sh.remove = true;
    kira.hold = false;
    void p;
  }

  // ================================================================ 节拍 7 杜王站前自由走动：找静
  async function useBench1(S) {
    await S.say(null, '长椅上有一个小小的手印……还是湿的。');
    if (!F().bench1) { F().bench1 = true; S.hint('按 Q 换乔瑟夫，按 U 念写：看看静往哪去了', 6); }
  }
  async function lookBench(S, h, p) {
    if (p.cid !== cast('joseph_old')) return;
    await S.say(cast('joseph_old'), '照片出来了……另一张长椅？她往东边爬过去了！', { expr: 'shock' });
    F().bench1 = true; F().nensha = true;
  }
  async function useBench2(S) {
    if (F().shizuka) { await S.say(null, '静安安稳稳地待在乔瑟夫怀里（虽然看不见）。'); return; }
    if (!F().nensha && !F().bench1) { await S.say(null, '一张空长椅。'); return; }
    F().shizuka = true;
    S.sfx('pop', 0.6);
    S.fx('sparkles', { x: 615, y: 140, n: 7, radius: 10, colour: '#e0f0ff', period: 0.5, size: 2 }, { life: 0.8 });
    S.sfxText('诶嘿', { wx: 615, wy: 136, wz: 0 }, { dur: 0.9 });
    await S.say(null, '长椅上什么都没有……可是有东西在笑。');
    await S.say(cast('joseph_old'), '静！找到你了！……OH MY GOD，别抓我的胡子！', { expr: 'shock' });
    S.mark('ch8_shizuka');
  }
  async function listenBench(S, h, p) {
    if (p.cid !== 'koichi') return;
    await S.say('koichi', '……右边那张长椅，有婴儿在笑！');
    F().bench1 = true; F().nensha = true;
  }
  function setupStation() {
    const st = G.world.stage;
    st.hotspots = [
      { id: 'bench1', x: 485, y: 158, r: 18, label: '长椅', tags: ['nensha', 'listen'], fx: 485, fy: 140, use: useBench1,
        look: async (S, h, p) => { if (p.cid === 'koichi') await listenBench(S, h, p); else await lookBench(S, h, p); } },
      { id: 'bench2', x: 615, y: 158, r: 18, label: '另一张长椅', tags: ['listen'], fx: 615, fy: 140, use: useBench2, look: listenBench },
      { id: 'tickets', x: 126, y: 150, r: 18, label: '售票机', use: async (S) => { await S.say(null, '去 S 市的电车，二十分钟一班。'); } },
      { id: 'phone', x: 688, y: 150, r: 14, label: '公用电话', use: async (S) => { await S.say(null, '电话亭里贴着一张寻人启事……不对，是寻猫启事。'); } },
      { id: 'cafe', x: 730, y: 150, r: 16, label: '咖啡馆', use: async (S) => { await S.say(null, '咖啡馆的玻璃窗上映着广场的钟。'); } },
    ];
    st.npcs = [];
    const oy = S8().spawn('oyanagi', 380, 160, { id: 'oyanagi', facing: -1, label: '小学生',
      talk: async (S) => { await T().say(S, 'oyanagi', '大哥哥，要不要猜拳？', { expr: 'smile' }); if (F().shizuka) F().toJanken = true; } });
    void oy;
  }
  const S8 = () => G.S;
  async function stationIn(S) {
    const rc = cast('rohan'), jc = cast('joseph_old');
    S.party(['koichi', jc, rc], { leader: 'koichi' });
    await S.setStage('station_ch8', { x: 230, y: 160, facing: 1, music: 'daily', fade: false });
    S.state('pm', 0);
    const jo = S.actor(jc), ro = S.actor(rc);
    if (jo) Object.assign(jo, { x: 200, y: 156, facing: 1 });
    if (ro) Object.assign(ro, { x: 176, y: 162, facing: 1 });
    G.world.snapCamera();
    await S.fadeIn(0.6);
    S.location('station', { y: NAME_TOP });
    await S.say('koichi', '乔斯达先生，静呢？刚才不是还抱在怀里吗？', { expr: 'shock' });
    await S.say(jc, '哈？静？……OH MY GOD，手里是空的！', { expr: 'shock' });
    await S.say(rc, '看不见的婴儿，在车站前面走丢了。……这素材倒是不坏。', { expr: 'smile' });
    nameCard(S, rc);
    await S.say('koichi', '露伴老师！快帮忙找啦！', { expr: 'shock' });
    S.hint('找透明的静：E 调查，Q 换人。乔瑟夫 U 念写、康一 U 听声音', 8);
  }
  async function talkJoseph7(S) { await S.say(cast('joseph_old'), '静啊，别爬太远……哈？你说什么？'); }
  async function talkRohan7(S) { await S.say(cast('rohan'), '我在找取材的角度，不是在找婴儿。……好吧，也在找。'); }
  async function talkKoichi7(S) { await S.say('koichi', '静会不会爬到马路上去了……'); }

  // ================================================================ 节拍 8 猜拳小子 → 第 13 战
  async function beatJanken(S) {
    T().memberTalk({});
    const rc = cast('rohan'), jc = cast('joseph_old');
    S.setLeader(rc, { force: true, silent: true });
    const ro = S.player, oy = S.actor('oyanagi'), ko = S.actor('koichi'), jo = S.actor(jc);
    S.hint(null);
    oy.talk = null;
    // 站位：露伴和大柳在广场中间面对面，康一和乔瑟夫退到长椅那边看
    Object.assign(ro, { x: 340, y: 160, facing: 1 });
    Object.assign(oy, { x: 390, y: 160, facing: -1 });
    if (ko) Object.assign(ko, { x: 470, y: 166, facing: -1, follow: null });
    if (jo) Object.assign(jo, { x: 498, y: 160, facing: -1, follow: null });
    G.world.snapCamera();
    focus({ x: 380 });
    await S.title('janken', { y: 110 });
    await S.say('oyanagi', '大哥哥，跟我猜拳吧。', { expr: 'smile' });
    nameCard(S, 'oyanagi');
    await S.say(rc, '我拒绝。……我很忙。');
    await S.say('oyanagi', '不比的话，我就一直跟着你。跟到你家，跟到你画画的桌子旁边。', { expr: 'smile' });
    await S.say(rc, '……啰嗦的小鬼。来吧，先赢三局的算赢。', { expr: 'rage' });
    await S.say('oyanagi', '输一局，你的替身就归我三分之一哦。', { expr: 'smile' });
    standCard(S, 'boyiiman');
    S.cue('sting_reveal');
    S.mark('ch8_janken');
    await S.wait(0.8);
    await S.say('koichi', '替、替身使者？！露伴老师！', { expr: 'shock' });
    S.music('battle', 0.3);
    await S.vs({ key: 'boyiiman', hero: rc, enemy: { cid: 'oyanagi', anim: 'idle' } });
    G.uifx.vsTag('boyiiman');
  }
  async function beatAfterJanken(S) {
    const rc = cast('rohan'), jc = cast('joseph_old'), oy = S.actor('oyanagi');
    S.music('victory', 0.8);
    S.mark('ch8_jk_win');
    await S.say('oyanagi', '我……输了？', { expr: 'shock' });
    S.fx('sparkles', { x: S.player.x, y: S.player.y - 24, n: 10, radius: 16, colour: '#f0d070', period: 0.5, size: 3 }, { life: 1.0 });
    S.sfx('power_up', 0.6);
    await S.say(rc, '猜拳不是靠运气。读懂对手的习惯，就跟读一本书一样。', { expr: 'smile' });
    await S.say('koichi', '露伴老师……你这孩子的替身是哪来的？');
    await S.say('oyanagi', '……一个从照片里探出头的老爷爷，拿箭射了我。', { actor: oy });
    S.mark('ch8_arrow_kid');
    await S.say(jc, '哈？照片？', { expr: 'shock' });
    S.sfx('pop', 0.4);
    await S.say(null, '（乔瑟夫怀里打了一个小小的喷嚏，他的胡子湿了一块）');
    await S.narrate('那支箭还在镇上。……它会找上下一个人。', { pos: 'top' });
    await S.fadeOut(0.8);
    if (oy) oy.remove = true;
  }

  // ================================================================ 节拍 10 那天夜里：摄像机 → To Be Continued
  async function beatCamera(S) {
    S.party([cast('kawajiri')], { leader: cast('kawajiri') });
    await S.setStage('kawajiri_ch8', { x: 250, y: 152, facing: 1, music: null, fade: false });
    G.world.stage.state = { night: 1 };
    const kira = S.player;
    kira.hold = true;
    snapTo({ x: 280 });
    S.stopMusic(0.3);
    await S.fadeIn(0.8);
    await S.title('that_night', { y: 110 });
    await S.narrate('平静的生活。……只要没有人来打扰。', { pos: 'top' });
    // 镜头慢慢摇到客厅天花板右上角：一台小摄像机，红灯一闪一闪（对白框先收起来：摄像机在 y 9–16）
    S.state('cam', 1);
    await S.animate(2.4, (k) => { focus({ x: 280 + 90 * k }); }).catch(G.cancelIgnore);
    await S.zoom(2.2, 364, 30, 1.2);
    S.sfx('blip', 0.4);
    await S.wait(1.6);
    S.mark('ch8_camera');
    await S.zoom(1, null, null, 0.3);
    G.world.zoom = null;
    S.music('tension', 0.5);
    await S.tbc({ hold: 2.0 });
    S.mark('ch8_tbc');
    kira.hold = false;
  }

  // ================================================================ 第8章主流程
  G.STORY.ch8 = async function (S) {
    if (T().resetCounters) T().resetCounters();
    P4().clearOverlays();
    await S.chapterCard('ch8');
    S.party(['josuke', 'jotaro4'], { leader: 'josuke' });
    await S.run(async (S2) => {
      await beatCalendar(S2);
      await beatGate(S2);
      await houseIn(S2);
    }, { keepLocked: true });
    // 节拍 3 旧宅自由走动：相册 + 遗照（或 50 s）→ 咔嚓
    setupHouse(false);
    T().memberTalk({ jotaro4: talkJotaro3, josuke: talkJosuke3 });
    await S.run(async () => {});   // 放开操作（上一段 keepLocked）
    const t3 = now();
    T().goal(S, { x: 331, y: 156, label: '相册', delay: 30, every: 15, done: () => !!F().album, text: '和室的矮桌上有一本相册' });
    await S.until(() => ((F().album && F().portrait) || now() - t3 > 50) && !S.busy);
    // 节拍 4 → 第 12 战 → 节拍 5
    await S.run(async (S2) => {
      await beatSnap(S2);
      await C8().fightAtomHeart(S2);
      await beatSealed(S2);
    }, { keepLocked: true });
    // 节拍 5 自由走动：修锁开箱
    F().afterFight = true;
    setupHouse(true);
    T().memberTalk({ jotaro4: talkJotaro3, josuke: talkJosuke3 });
    await S.run(async (S2) => { S2.hint('储物间的长木箱：仗助按 U 修好坏锁', 7); });
    T().goal(S, { x: 588, y: 156, label: '长木箱', delay: 10, every: 15, done: () => !!F().houseDone, text: '储物间的长木箱：仗助按 U 修好坏锁' });
    await S.until(() => !!F().houseDone && !S.busy);
    // 节拍 6 吉良视角
    await S.run(async (S2) => {
      await S2.fadeOut(0.6);
      await beatKiraLife(S2);
      await stationIn(S2);
    }, { keepLocked: true });
    // 节拍 7 车站自由走动：找静（找到后再跟大柳说话，或 70 s 后直接开始）
    setupStation();
    T().memberTalk({ [cast('joseph_old')]: talkJoseph7, [cast('rohan')]: talkRohan7, koichi: talkKoichi7 });
    await S.run(async () => {});
    const t7 = now();
    T().goal(S, { x: 485, y: 160, label: '长椅', delay: 20, every: 15, done: () => !!F().shizuka, text: '长椅那边好像有什么：E 调查' });
    T().goal(S, { x: 380, y: 160, label: '小学生', delay: 2, every: 15, when: () => !!F().shizuka, done: () => !!F().toJanken, text: '找到静了。广场中间那个小学生在看露伴……' });
    await S.until(() => ((F().shizuka && F().toJanken) || now() - t7 > 70) && !S.busy);
    // 节拍 8 → 第 13 战 → 节拍 9 → 节拍 10
    await S.run(async (S2) => {
      await beatJanken(S2);
      await C8().fightBoyIIMan(S2);
      await beatAfterJanken(S2);
      await beatCamera(S2);
    }, { keepLocked: true });
  };
  // 整章测试（tools/dev/p4_play.js --chapter ch8）对照的剧情标记
  G.STORY.ch8.marks = ['ch8_calendar', 'ch8_gate', 'ch8_notebook', 'ch8_album', 'ch8_snap', 'ch8_photo_solo', 'ch8_pinned', 'ch8_face',
    'ch8_arrow', 'ch8_flyaway', 'ch8_kira_sign', 'ch8_shinobu', 'ch8_shizuka', 'ch8_janken', 'ch8_jk_win', 'ch8_arrow_kid', 'ch8_camera', 'ch8_tbc'];
})();
