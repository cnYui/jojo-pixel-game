// 第10章　送电铁塔 / 铁塔与谜（开发脚本 第四部/docs/第10章_开发脚本.md；地图后缀 _ch10）。整章流程：
//   1 篇章卡 → 日历地图（「送电铁塔」「宫本的屋子」、红章 7 月）→ 2 塔脚（未起隆、丰大打招呼）→ 3 塔脚自由走动（未起隆 U 变喇叭、爬脚钉）
//   → 4 塔上（照片里的人、Superfly、VS）→ 第 15 战 → 5 丰大认输、留在塔上 → 6 放学路（康一变成纸）→ 7 东方家（朋子的纸、裕也来了）
//   → 8 夜路自由走动（裕也 U 闻气味）→ 9 宫本的屋子（枪声的纸、康一的纸、VS）→ 第 16 战前半 → 纸里的世界 → 第 16 战后半 → 11 图书馆、To Be Continued
//   克制（第三部 D10）：人变成纸只给纸片和「唰」；丰大钉未起隆只有一声「锵」；陷阱纸的火、蝎子、电都是纸上冒出来的，没有伤口。
//   两场战斗在 story/p4_ch10_fights.js（G.P4CH10）。铁塔是竖向地图：镜头竖向不跟人，这里自己设 stage.camY（docs/第10章_背景.md）。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const C10 = () => G.P4CH10;
  const F = () => G.flags;
  const now = () => (G.clk ? G.clk.world : 0);
  const NAME_TOP = 100;
  const { base, walls } = G.p4Stage;
  const MK = () => C10().cid.mikitaka();
  const YU = () => C10().cid.yuya();

  // 对话框短名（未起隆、裕也的正式 cid 第9章也会加，一样的字）
  Object.assign(G.NAMES, { toyohiro: '丰大', terunosuke: '辉之辅', mikitaka: '未起隆', mikitaka_tmp: '未起隆', yuya: '裕也', yuya_tmp: '裕也' });

  // ================================================================ 地图
  const ST = G.STAGES;
  ST.map_ch10 = base('map_ch10', 'morioh_map', 320, { yMin: 160, yMax: 170, music: null, obstacles: [] });
  ST.tower_ch10 = base('tower_ch10', 'transmission_tower', 320, { music: 'daily', state: { pm: 1 }, obstacles: walls(8, 312, 320) });
  ST.road_ch10 = base('road_ch10', 'morioh_road', 960, { state: { pm: 1 } });
  ST.home_ch10 = base('home_ch10', 'higashikata_living', 480, { music: 'tension', state: { fog: 0 }, obstacles: walls(10, 470, 480) });
  ST.miyamoto_ch10 = base('miyamoto_ch10', 'miyamoto_house', 480, { music: 'tension', state: { shred: 0 }, obstacles: walls(8, 380, 480) });
  ST.paper_ch10 = base('paper_ch10', 'paper_world', 480, { music: null, obstacles: walls(8, 472, 480) });
  ST.library_ch10 = base('library_ch10', 'library', 320, { music: 'sad', state: { book: 0 } });

  // 队伍池里的那个人（入队还是同一个 Actor）
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
  const camY = (y) => { const st = G.world.stage; if (st) st.camY = y; };
  // 镜头竖向卷动（铁塔）
  const scrollTo = (S, y, dur) => { const st = G.world.stage, y0 = st.camY || 0; return S.animate(dur, (k) => { st.camY = Math.round(G.lerp(y0, y, k * k * (3 - 2 * k))); }); };

  // ================================================================ 节拍 1 篇章卡 → 日历地图（本章的红章 7 月在 ui.map_ch10，序章那枚 4 月不动）
  const PINS = [{ xy: [46, 44], label: '送电铁塔' }, { xy: [140, 100], label: '宫本的屋子' }];
  async function calendar(S) {
    const m = (G.D.ui && G.D.ui.map) || {}, mine = (G.D.ui && G.D.ui.map_ch10) || {};
    const an = (G.D.bg.morioh_map && G.D.bg.morioh_map.anchors) || {};
    const gray = [an.school, an.home].filter(Boolean);
    const img = (meta) => { const im = meta && G.image(meta.image); return im && G.ready(im) ? im : null; };
    const ease = (u) => 1 - Math.pow(1 - Math.max(0, Math.min(1, u)), 3);
    const pins = PINS.map((p, i) => ({ p, t0: 0.5 + i * 0.45 }));
    const stampAt = 0.5 + pins.length * 0.45 + 0.25;
    const h = P4().overlay((g, t) => {
      const pin = (xy, im, dy = 0) => {
        if (!im) return;
        const pm = m.pin || { ax: 5, ay: 15 };
        g.drawImage(im, Math.round(xy[0] * 2 - pm.ax * 2), Math.round(xy[1] * 2 - pm.ay * 2 + dy), im.width * 2, im.height * 2);
      };
      for (const xy of gray) pin(xy, img(m.pin_gray));
      for (const q of pins) {
        const u = (t - q.t0) / 0.3;
        if (u < 0) continue;
        const dy = u < 1 ? -60 * (1 - ease(u)) : u < 1.4 ? -Math.round(Math.sin((u - 1) / 0.4 * Math.PI) * 6) : 0;
        pin(q.p.xy, img(m.pin), dy);
        if (u >= 1) P4().text(g, q.p.label, Math.round(q.p.xy[0] * 2 + 12), Math.round(q.p.xy[1] * 2 - 34), '#fff4d6', 12, 'left', '#2a0a1a');
      }
      if (t >= stampAt) {
        const sm = mine.stamp, sim = img(sm);
        if (sim) {
          const u = Math.min(1, (t - stampAt) / 0.14), sc = 1.9 - 0.9 * ease(u);
          const w = Math.round(sm.w * sc), hh = Math.round(sm.h * sc);
          g.save(); g.globalAlpha = Math.min(1, u * 2);
          g.drawImage(sim, Math.round(534 - w / 2), Math.round(262 - hh / 2), w, hh);
          g.restore();
        }
      }
      const pl = mine.place, plim = img(pl);
      if (plim) g.drawImage(plim, 640 - pl.w - 14, 12);
    }, { z: 1 });
    for (const q of pins) G.defer(q.t0 + 0.3, () => { S.sfx('pop', 0.7); S.sfx('thud', 0.4); }, 'ui');
    G.defer(stampAt, () => { S.sfx('thud', 1); S.sfx('card_flip', 0.6); S.shake(2, 0.2); }, 'ui');
    await S.wait(stampAt + 1.8, 'ui');
    return h;
  }
  async function beatCalendar(S) {
    S.player.visible = false;
    await S.setStage('map_ch10', { x: 160, y: 165, music: null });
    const cal = await calendar(S);
    S.mark('ch10_calendar');
    await S.fadeOut(0.45);
    if (cal) cal.close();
  }

  // ================================================================ 节拍 2 塔脚（傍晚）：未起隆、丰大打招呼
  async function beatTowerFoot(S) {
    const p = S.player;
    await S.setStage('tower_ch10', { x: 200, y: 162, facing: -1, music: 'daily', fade: false });
    C10().ground();
    p.visible = true;
    const mk = pool(MK());
    Object.assign(mk, { x: 232, y: 166, facing: -1, visible: true });
    const ty = S.spawn('toyohiro', 140, 42, { id: 'toyohiro', facing: 1, name: '钢田一丰大' });
    snapTo({ x: 160 });
    await S.fadeIn(0.6);
    S.location('tower', { y: NAME_TOP });
    S.mark('ch10_tower_foot');
    await S.say(MK(), '仗助先生，那座塔好像我们星球的天线。', { expr: 'smile' });
    S.nameCard(C10().nameKey('mikitaka'), { y: NAME_TOP });
    await S.say('josuke', '那是送电铁塔，早就不用了。……喂，上面晾着衣服？');
    // 塔上有人：镜头往上看一眼
    await scrollTo(S, -60, 0.8);
    S.walk(ty, 170, 42, { speed: 40 }).catch(G.cancelIgnore);
    await S.say('toyohiro', '哟！下面的，要不要上来坐坐？', { expr: 'smile' });
    S.nameCard('toyohiro', { y: NAME_TOP });
    await S.say('toyohiro', '我就住在这儿。不用交房租，夏天有风，还能看海。', { expr: 'smile' });
    await scrollTo(S, 0, 0.6);
    await S.say('josuke', '……真的有人住在铁塔上啊。', { expr: 'shock' });
    S.standCard(C10().standKey('earthwind'), { y: NAME_TOP });
    await S.say(MK(), '我也想住住看。地球人的房子，都很有意思。', { expr: 'smile' });
    focus(null);
  }

  // ================================================================ 节拍 3 塔脚自由走动
  async function useLeg(S) {
    if (F().climb) return;
    F().climb = true;
  }
  function setupTowerFree(S) {
    const st = G.world.stage;
    T().prop(S, 'horn', -50, 150, { id: 'mk_horn_hidden' }).visible = false;
    st.hotspots.push(
      { id: 'sign', x: 48, y: 150, r: 18, label: '告示牌', use: async (S2) => { await S2.say(null, '「私人住宅　请勿靠近」——字是手写的。'); F().sign = true; } },
      { id: 'bucket', x: 85, y: 150, r: 16, label: '水桶', use: async (S2) => { await S2.say(null, '从上面垂下来的水桶，装着刚接的雨水。'); await S2.say('josuke', '真的在过日子……'); } },
      { id: 'path', x: 60, y: 168, r: 18, ry: 10, label: '土路', use: async (S2) => { await S2.say(null, '只有一行脚印通到塔下，没有出来的。'); } },
      { id: 'leg', x: 72, y: 152, r: 14, label: '脚钉', use: useLeg },
    );
    T().goal(S, { x: 72, y: 152, label: '脚钉', delay: 20, every: 15, done: () => !!F().climb, text: '左边塔腿上有脚钉：走过去按 E 爬上去' });
  }
  // 未起隆在自由走动里按 U：变成一只小喇叭（示范，一次性；之后只冒一句）
  const LOOK_MK = {
    tags: ['morph'], cd: 1, miss: null,
    run: async (S, p) => {
      if (F().horn) { S.emote(p, '变身要歇一会儿……', 1); return; }
      F().horn = true;
      p.visible = false;
      const h = T().prop(S, 'horn', p.x, p.y + 0.5, { id: 'mk_horn', z: 12 });
      S.sfx('blip', 0.8);
      S.sfxText('嘀嘀——', h, { dur: 0.9 });
      await S.wait(0.9);
      h.remove = true; p.visible = true;
      await S.say(MK(), '像这样，我什么都能变。只是不能变得比我自己大太多。', { expr: 'smile' });
    },
  };
  G.LOOK.mikitaka_tmp = LOOK_MK;
  if (!G.LOOK.mikitaka) G.LOOK.mikitaka = LOOK_MK;

  // ================================================================ 节拍 4 爬上去：照片里的人、Superfly、VS
  async function beatTowerTop(S) {
    const p = S.player, mk = pool(MK()), ty = S.actor('toyohiro');
    T().memberTalk({});
    if (p.cid !== 'josuke') S.setLeader('josuke', { force: true, silent: true });
    const pl = S.player;
    // 顺着脚钉往上爬：人留在原处，镜头一路卷上去，最后两个人站到中层的梁上
    S.sfx('footstep1', 0.6);
    await S.animate(0.5, (k) => { pl.z = Math.round(30 * k); });
    pl.visible = false; mk.visible = false;
    await scrollTo(S, -88, 1.2);
    S.mark('ch10_climb');
    C10().level(C10().TW.mid);
    G.world.stage.x0 = 84; G.world.stage.x1 = 236;
    Object.assign(pl, { x: 98, y: 42, z: 0, facing: 1, visible: true });
    Object.assign(mk, { x: 90, y: 44, facing: 1, visible: true, follow: null });
    if (ty) Object.assign(ty, { x: 182, y: 42, facing: -1 });
    G.world.snapCamera();
    S.music('tension', 0.8);
    await S.say('toyohiro', '请坐。茶是凉的，将就一下。', { expr: 'smile' });
    await S.say('toyohiro', '有个人寄了一张照片来，照片里的人跟我说话。');
    await S.say('toyohiro', '他说只要把一个替身使者关进这座塔，我就能下去过好日子。');
    await S.say('josuke', '……照片里的人？吉良的老爸！', { expr: 'shock' });
    await S.say('toyohiro', '这座塔就是我的替身——Superfly。进来的人，最后总得留下一个。', { expr: 'smile' });
    S.standCard('superfly', { y: NAME_TOP });
    S.cue('sting_reveal');
    S.mark('ch10_superfly_card');
    await S.wait(0.8);
    await S.say('toyohiro', '我被关在这里好几年了。今天，该换你了。', { expr: 'rage' });
    await S.say(MK(), '仗助先生，我也来帮忙。……不过我不会打架。');
    S.music('battle', 0.3);
    await S.vs({ key: 'superfly', hero: 'josuke', enemy: { cid: 'toyohiro', anim: 'idle' } });
    G.uifx.vsTag('superfly');
  }

  // ================================================================ 节拍 5 丰大认输
  async function beatTowerEnd(S) {
    const p = S.player, ty = S.actor('toyohiro');
    S.music('daily', 1);
    if (ty) { S.face(p, ty); }
    await S.say('toyohiro', '被自己的力气打回来了……我认输。', { expr: 'shock' });
    await S.say('toyohiro', '出去的办法很简单：别让塔里一个人都不剩。只要我还在，你们就能下去。');
    if (ty) { S.unpose(ty); ty.play('idle'); }
    // 未起隆从铁架上松开（变回人）
    const mk = pool(MK());
    Object.assign(mk, { x: Math.min(230, (ty ? ty.x : 200) + 26), y: 44, visible: true, team: 'npc', tint: null });
    P4().fixGlow(S, mk.x, mk.y - 14, { n: 5 });
    await S.say('toyohiro', '其实我也没那么想下去。这里风景好，镇上的人迟早会把它当成名胜吧。', { expr: 'smile' });
    await S.say('josuke', '……那你就好好当你的名胜吧。');
    await S.say(MK(), '仗助先生，我刚才变成电线的时候，听到很远的地方有人在打电话。');
    await S.say('josuke', '吉良的老爸……还在找人对付我们。', { expr: 'rage' });
    S.mark('ch10_tower_end');
    await S.fadeOut(0.8);
    S.leave(MK(), { drop: true });
    C10().ground();
  }

  // ================================================================ 节拍 6 放学路：康一变成纸
  async function beatKoichiPaper(S) {
    const p = S.player;
    await S.setStage('road_ch10', { x: 40, y: 160, facing: 1, music: 'tension', fade: false });
    S.state('pm', 1);
    p.visible = false;
    const ko = S.spawn('koichi', 300, 160, { id: 'koichi_road', facing: 1 });
    const te = S.spawn('terunosuke', 520, 152, { id: 'terunosuke_road', facing: -1, visible: false });
    te.visible = false;
    snapTo({ x: 420 });
    await S.fadeIn(0.6);
    S.walk(ko, 430, 160, { speed: 34 }).catch(G.cancelIgnore);
    await S.narrate('那天放学，我一个人走在回家的路上。', { pos: 'top' });
    await S.until(() => !ko.script);
    // 电线杆后面跳出一个白头发的少年
    te.visible = true;
    S.sfx('whoosh', 0.9);
    await S.arc(te, 468, 158, 12, 0.3);
    S.face(ko, 1);
    await S.say('terunosuke', '你好。能借我看一眼你害怕的样子吗？', { expr: 'smile' });
    await S.say('koichi', '诶？！', { expr: 'shock' });
    S.sfxText('（抓住书包带）', ko, { dur: 1 });
    await S.wait(0.6);
    await S.say('terunosuke', '找到了。你害怕的时候，会抓书包带。', { expr: 'smile' });
    // 白光，「唰」：康一的位置只剩一张对折的纸，书包掉在地上
    S.flash(0.25, 0.9);
    S.sfx('whoosh', 1); S.sfx('card_flip', 0.9);
    S.sfxText('唰', ko, { dur: 0.8 });
    ko.visible = false;
    const pp = T().prop(S, 'paper', ko.x, ko.y + 0.5, { id: 'ko_paper', frame: 0, z: 18 });
    T().prop(S, 'koichi_bag', ko.x - 8, ko.y + 1, { id: 'ko_bag0', frame: 0 });
    await S.animate(0.5, (k) => { pp.z = Math.round(18 * (1 - k)); });
    S.mark('ch10_koichi_paper');
    await S.walk(te, pp.x + 10, pp.y, { speed: 50 });
    pp.remove = true;
    await S.say('terunosuke', '第一张。下一张……是东方仗助。', { expr: 'smile' });
    await S.walk(te, 980, 152, { speed: 60 });
    te.remove = true; ko.remove = true;
    await S.fadeOut(0.6);
    focus(null);
  }

  // ================================================================ 节拍 7 东方家：朋子的纸、裕也来了
  async function beatHome(S) {
    const p = S.player;
    await S.setStage('home_ch10', { x: 40, y: 160, facing: 1, music: 'tension', fade: false });
    p.visible = true;
    T().prop(S, 'paper', 231, 150, { id: 'tomoko_paper', frame: 3, z: 12 });
    G.world.snapCamera();
    await S.fadeIn(0.5);
    S.location('higashikata', { y: NAME_TOP });
    await S.say('josuke', '我回来了。……妈？');
    await S.walk(p, 214, 158, { speed: 60 });
    S.face(p, 1);
    await S.say('josuke', '沙发上……一张纸？上面画着妈的脸？', { expr: 'shock' });
    S.mark('ch10_tomoko_paper');
    S.sfx('ding', 0.6);
    await S.say('hirose_mom_voice', '仗助君吗？康一到现在还没回家……', { name: '康一的妈妈（电话）' });
    await S.say('josuke', '……阿姨，我去找他。', { expr: 'rage' });
    // 门铃：裕也
    S.sfx('ding', 0.8);
    const yu = place(S, YU(), 30, 158, 1);
    await S.walk(yu, 150, 158, { speed: 60 });
    S.face(p, -1);
    await S.say(YU(), '东方仗助，我出院了。来道个谢。');
    S.nameCard(C10().nameKey('yuya'), { y: NAME_TOP });
    await S.say(YU(), '……你家里有股味道。人吓到发抖时的汗味，还很新鲜。', { expr: 'shock' });
    await S.say('josuke', '……带我去找。', { expr: 'rage' });
    S.standCard(C10().standKey('highway'), { y: NAME_TOP });
    S.party(['josuke', YU()], { leader: 'josuke' });
    S.mark('ch10_yuya_join');
    await S.wait(0.6);
    await S.fadeOut(0.5);
  }

  // ================================================================ 节拍 8 夜路：裕也 U 闻气味
  const SCENTS = [{ x: 300, y: 162, line: '这边。' }, { x: 560, y: 156, line: '往右，他走得很快。' }, { x: 820, y: 160, line: '到了——前面那间屋子。' }];
  async function smell(S, h, p) {
    const i = h.si;
    if (F()['scent' + i]) { await S.say(YU(), '这里闻过了。'); return; }
    if (i > 0 && !F()['scent' + (i - 1)]) { await S.say(YU(), '……这里味道太淡了。先找前面的。'); return; }
    F()['scent' + i] = true;
    S.sfx('sparkle', 0.6);
    S.sfxText('嗅', p, { dur: 0.7 });
    // 地上亮一串粉色脚印，指向下一处
    const nx = SCENTS[i + 1] ? SCENTS[i + 1].x : 940;
    for (let k = 1; k <= 4; k++) {
      const x = G.lerp(h.x, nx, k / 5);
      const fp = T().prop(S, 'scent', x, h.y + (k % 2 ? 2 : -2), { id: 'scent_fp' + i + '_' + k, frame: 0 });
      G.defer(6, () => { fp.remove = true; });
    }
    await S.say(YU(), SCENTS[i].line);
    if (i === 2) { S.mark('ch10_scent3'); F().scentDone = true; }
  }
  function setupRoadFree(S) {
    const st = G.world.stage;
    T().prop(S, 'koichi_bag', 200, 162, { id: 'ko_bag', frame: 0 });
    st.hotspots.push({ id: 'bag', x: 200, y: 162, r: 16, label: '书包', use: async (S2) => {
      await S2.say(null, '康一的书包。……他不会把它丢在这里的。');
      F().bag = true;
      await S2.say(YU(), '书包上就是那股味道。按 Q 换我，我用鼻子带路。');
    } });
    SCENTS.forEach((s, i) => st.hotspots.push({ id: 'scent' + i, si: i, x: s.x, y: s.y, r: 20, ry: 12, label: '气味', tags: ['smell'], fx: s.x, fy: s.y - 4,
      use: async (S2) => { await S2.say('josuke', '……我又没有那么灵的鼻子。'); }, look: smell }));
    st.triggers.push({ x0: 930, x1: 1000, run: async () => { F().toMiyamoto = true; } });
  }
  const LOOK_YU = {
    tags: ['smell'], cd: 0.8, miss: '……这里没有那股味道。',
    run: async (S, p, h) => { if (h) S.face(p, h.x > p.x ? 1 : -1); S.sfx('blip', 0.4); await S.wait(0.2); },
  };
  G.LOOK.yuya_tmp = LOOK_YU;
  if (!G.LOOK.yuya) G.LOOK.yuya = LOOK_YU;
  async function roadIn(S) {
    await S.setStage('road_ch10', { x: 40, y: 160, facing: 1, music: 'tension', fade: false });
    S.state('pm', 1);
    G.world.snapCamera();
    await S.fadeIn(0.5);
    S.hint('Q 换成裕也：按 U 闻气味，跟着粉色脚印走', 8);
  }

  // ================================================================ 节拍 9 宫本的屋子
  async function beatMiyamoto(S) {
    const p = S.player;
    T().memberTalk({});
    if (p.cid !== 'josuke') S.setLeader('josuke', { force: true, silent: true });
    await S.setStage('miyamoto_ch10', { x: 40, y: 160, facing: 1, music: 'tension', fade: false });
    S.state('shred', 0);
    const pl = S.player, yu = S.actor(YU());
    if (yu) Object.assign(yu, { x: 20, y: 164, facing: 1 });
    const papers = T().prop(S, 'paper', 94, 150, { id: 'table_papers', frame: 0, z: 12 });
    G.world.snapCamera();
    await S.fadeIn(0.5);
    S.location('miyamoto', { y: NAME_TOP });
    await S.walk(pl, 140, 158, { speed: 50 });
    await S.say('josuke', '有人吗？');
    // 他从矮桌上的一张纸里展开出来
    S.sfx('card_flip', 0.9);
    const te = S.spawn('terunosuke', 200, 154, { id: 'terunosuke', facing: -1, alpha: 0 });
    await S.animate(0.5, (k) => { te.alpha = k; });
    void papers;
    S.mark('ch10_miyamoto');
    await S.say('terunosuke', '欢迎。我叫宫本辉之辅。', { expr: 'smile' });
    S.nameCard('terunosuke', { y: NAME_TOP });
    S.standCard('enigma', { y: NAME_TOP });
    S.cue('sting_reveal');
    S.mark('ch10_enigma_card');
    await S.wait(0.6);
    await S.say('terunosuke', '你妈妈我已经放回家了。我要的不是她，是你害怕的样子。');
    // 「砰」：纸上画的枪
    const gun = T().prop(S, 'paper', te.x - 14, te.y + 0.5, { id: 'gun_paper', frame: 1, z: 18 });
    S.sfx('gunshot', 0.9); S.flash(0.1, 0.6);
    S.sfxText('砰！', gun, { dur: 0.8 });
    await S.wait(0.5);
    gun.remove = true;
    await S.say('josuke', '……这种东西吓不到我。');
    await S.say('terunosuke', '是吗？那这张呢？', { expr: 'smile' });
    const kp = T().prop(S, 'paper', te.x - 12, te.y + 0.5, { id: 'ko_paper_show', frame: 2, z: 20 });
    await S.say('terunosuke', '我把它扔到马路上去，会怎么样？', { expr: 'smile' });
    await S.say(YU(), '东方仗助……别慌。他就等着你慌。', { expr: 'shock' });
    kp.remove = true;
    S.music('battle', 0.3);
    await S.vs({ key: 'enigma', hero: 'josuke', enemy: { cid: 'terunosuke', anim: 'idle' } });
    G.uifx.vsTag('enigma');
  }

  // ================================================================ 第 16 战前半之后：仗助变成纸 → 纸里的世界
  async function josukePaper(S) {
    const p = S.player, te = S.actor('terunosuke'), yu = S.actor(YU());
    if (p.cid !== 'josuke') S.setLeader('josuke', { force: true, silent: true });
    const js = S.player;
    S.state('shred', 1);
    S.sfx('metal_crunch', 0.6);
    await S.say('terunosuke', '碎纸机开了哦。康一君会被切成两千片。', { expr: 'smile' });
    const kp = T().prop(S, 'paper', te.x + 20, te.y + 0.5, { id: 'ko_paper_throw', frame: 2, z: 20 });
    S.sfx('whoosh', 0.8);
    await S.arc(kp, 378, 150, 30, 0.5);
    await S.say('josuke', '康一！', { expr: 'shock' });
    S.sfxText('（咬住嘴唇）', js, { dur: 1 });
    await S.wait(0.5);
    await S.say('terunosuke', '咬嘴唇。……这就是你害怕的样子。', { expr: 'smile' });
    S.flash(0.3, 0.9);
    S.sfx('whoosh', 1); S.sfx('card_flip', 0.9);
    S.sfxText('唰', js, { dur: 0.8 });
    js.visible = false;
    T().prop(S, 'paper', js.x, js.y + 0.5, { id: 'js_paper', frame: 4, z: 4 });
    S.mark('ch10_josuke_paper');
    kp.remove = true;
    if (yu) S.face(yu, te);
    await S.say(YU(), '……东方仗助！', { expr: 'shock' });
    await S.say('terunosuke', '你没帮他，我也没接到对付你的命令。回去吧，喷上君。', { expr: 'smile' });
    await S.fadeOut(0.5);
    // 纸里的世界：仗助的声音
    await S.setStage('paper_ch10', { x: 160, y: 158, facing: 1, music: null, fade: false });
    S.party(['josuke', YU()], { leader: 'josuke' });
    const pj = S.player;
    pj.visible = true; pj.tint = { color: '#c8c0b0', k: 0.35 };
    const yu2 = S.actor(YU());
    if (yu2) yu2.visible = false;
    const ko = S.spawn('koichi', 320, 160, { id: 'koichi_paper', facing: -1 });
    ko.tint = { color: '#c8c0b0', k: 0.35 };
    G.world.snapCamera();
    await S.fadeIn(0.6);
    await S.say('josuke', '……可恶，动不了。这里是纸的里面？', { expr: 'shock' });
    await S.say('koichi', '仗、仗助君？你也被折进来了？', { expr: 'shock' });
    await S.say('josuke', '外面只剩裕也了。……裕也，靠你了。', { expr: 'rage' });
    await S.fadeOut(0.5);
    ko.remove = true;
    pj.tint = null;
    await S.setStage('miyamoto_ch10', { x: 60, y: 156, facing: 1, music: 'battle', fade: false });
    S.state('shred', 1);
    S.party(['josuke', YU()], { leader: YU() });
    const js2 = pool('josuke');
    js2.visible = false;
    const te2 = S.spawn('terunosuke', 300, 156, { id: 'terunosuke', facing: -1 });
    void te2;
    G.world.snapCamera();
    await S.fadeIn(0.4);
    const yu3 = S.player;
    await S.say(yu3.cid, '……我不走。我欠东方仗助一条命。', { expr: 'rage' });
    await S.say('terunosuke', '是吗。那你也会害怕的。', { expr: 'smile' });
  }

  // ================================================================ 节拍 11 图书馆：章末
  async function beatLibrary(S) {
    S.party(['josuke'], { leader: 'josuke' });
    await S.setStage('library_ch10', { x: 120, y: 160, facing: 1, music: 'sad', fade: false });
    S.state('book', 0);
    const p = S.player;
    Object.assign(p, { x: 150, y: 160, facing: 1, visible: true, tint: null });
    const ko = S.spawn('koichi', 120, 158, { id: 'koichi_lib', facing: 1 });
    const tm = S.spawn('tomoko', 96, 162, { id: 'tomoko_lib', facing: 1 });
    G.world.snapCamera();
    await S.fadeIn(0.8);
    S.location('library', { y: NAME_TOP });
    S.mark('ch10_library');
    await S.say('koichi', '从纸里出来的时候，我还以为自己睡了一觉。', { expr: 'smile' });
    await S.say('tomoko', '仗助，你这几天怎么老盯着我看？');
    S.face(p, -1);
    await S.say('josuke', '……没什么。');
    await S.walk(p, 262, 158, { speed: 40 });
    S.face(p, 1);
    S.state('book', 1);
    S.sfx('sparkle', 0.6);
    await S.narrate('几天后，杜王町图书馆多了一本没有作者的书，书名叫《谜》。', { pos: 'top' });
    await S.narrate('听说把耳朵贴在书上，能听到里面有人在小声求救。', { pos: 'top' });
    const yu = place(S, YU(), 20, 162, 1);
    await S.walk(yu, 200, 162, { speed: 60 });
    S.face(p, -1);
    await S.say(YU(), '东方仗助。你害怕的时候会咬嘴唇……这个我会替你保密。', { expr: 'smile' });
    await S.say('josuke', '……谢了。');
    void ko; void tm;
    S.music('victory', 1.0);
    await S.narrate('吉良吉影的父亲还在找替身使者。下一个，会是谁呢？', { pos: 'top' });
    S.stopMusic(0.6);
    await S.tbc({ hold: 2.0 });
    S.mark('ch10_tbc');
  }

  // ================================================================ 第10章主流程
  G.STORY.ch10 = async function (S) {
    if (T().resetCounters) T().resetCounters();
    P4().clearOverlays();
    await S.chapterCard('ch10');
    S.party(['josuke', MK()], { leader: 'josuke' });
    await S.run(async (S2) => {
      await beatCalendar(S2);
      await beatTowerFoot(S2);
    }, { keepLocked: true });
    // 节拍 3 塔脚自由走动（20 s 后箭头指脚钉）
    setupTowerFree(S);
    await S.run(async (S2) => { S2.hint('E 调查；Q 换成未起隆，按 U 看看他会变什么', 8); });
    await S.until(() => !!F().climb && !S.busy);
    Object.assign(G.STAGES.tower_ch10, { hotspots: [], npcs: [], triggers: [] });
    // 节拍 4 → 第 15 战 → 节拍 5 → 6 → 7
    await S.run(async (S2) => {
      await beatTowerTop(S2);
      await C10().fightSuperfly(S2);
      await beatTowerEnd(S2);
      await beatKoichiPaper(S2);
      await beatHome(S2);
    }, { keepLocked: true });
    // 节拍 8 夜路：三处气味都闻到（或者 60 s）→ 走到右端
    await S.run(roadIn);
    setupRoadFree(S);
    const t8 = now();
    T().goal(S, { x: 940, y: 158, label: '那间屋子', delay: 0, every: 15, done: () => !!F().toMiyamoto,
      text: '往右走（跟着气味）' });
    void t8;
    await S.until(() => !!F().toMiyamoto && !S.busy);
    Object.assign(G.STAGES.road_ch10, { hotspots: [], npcs: [], triggers: [] });
    // 节拍 9 → 第 16 战 → 节拍 11
    await S.run(async (S2) => {
      await beatMiyamoto(S2);
      await C10().fightEnigmaA(S2);
      await josukePaper(S2);
      await C10().fightEnigmaB(S2);
      await S2.say('josuke', '……修好了。只是修成了一本书。', { expr: 'normal' });
      await S2.say('koichi', '仗助君，裕也君的纸！', { expr: 'shock' });
      const yp = S2.actor('mh_yuya'), js = S2.player;
      if (yp) {
        await S2.walk(js, yp.x - 16, yp.y, { speed: 60 });
        await S2.summon(js, { dur: 0.1, rise: 4 });
        S2.standAct(js, 'reach', { dx: 16, z: 2, dur: 0.8 });
        P4().fixGlow(S2, yp.x, yp.y - 6);
        yp.remove = true;
        const yu = place(S2, YU(), yp.x, yp.y, -1);
        S2.recall(js);
        await S2.say(yu.cid, '……我刚才是不是很丢脸？', { expr: 'shock' });
        await S2.say('josuke', '不。是你把我们救出来的。', { expr: 'smile' });
      }
      await S2.fadeOut(0.8);
      await beatLibrary(S2);
    }, { keepLocked: true });
  };
  // 整章测试（tools/dev/p4_play.js --chapter ch10）对照的剧情标记
  G.STORY.ch10.marks = ['ch10_calendar', 'ch10_tower_foot', 'ch10_climb', 'ch10_superfly_card', 'ch10_rivet_fix', 'ch10_josuke_stuck',
    'ch10_cable_swing', 'ch10_superfly_win', 'ch10_tower_end', 'ch10_koichi_paper', 'ch10_tomoko_paper', 'ch10_yuya_join', 'ch10_scent3',
    'ch10_miyamoto', 'ch10_enigma_card', 'ch10_wink_hit', 'ch10_josuke_paper', 'ch10_papers_held', 'ch10_yuya_paper', 'ch10_papers_open',
    'ch10_book', 'ch10_library', 'ch10_tbc'];
})();
