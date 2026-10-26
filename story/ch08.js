// 第8章　埃及沙漠 / 九荣神：沙与预言（规划 §6.7；原著 183–192 话，游戏内第 29–31 天）
//   2026-10-20 照游玩脚本 ch8 整章重写（用户要求：用已交付素材把第5章到终章全部做完）。
//   初版（10 月初，14 KB）的机关写法沿用：盖布神的声圈 / 水爪、滑翔的水柱、托特预言的 30 秒计时；
//   这一版补自由走动（埃及海岸、阿斯旺街市）、投口香糖小游戏、掰手腕、九荣神过场、墓与花京院离队，
//   台词逐字照脚本，坐标全部从背景导出的 anchors 取（bgA 带默认值）。
//
//   流程：篇章卡 → 埃及海岸（SPW 直升机送来伊奇、投口香糖收买它）→ 自由走动 → 埃及九荣神 →
//   沙漠：直升机被击落、花京院 / 波鲁纳雷夫 / 阿布德尔接连倒下 → 第 16 战段 1 盖布 · 沙地（听声辨位 + 石子诱饵）
//   → 段 2 盖布 · 滑翔（↑↓ 躲水柱 + 愚者体力）→ 扔出伊奇、恩多尔自尽、沙丘下的墓 → 花京院住院离队
//   → 阿斯旺（只有伊奇 / 波鲁纳雷夫能当队长；假承太郎、茶馆掰手腕）→ 第 17 战三个托特预言 → 奥因哥现形、TBC
//
//   克制处理（规划 §4.6）：直升机驾驶员只有远景剪影 + 无线电一句；花京院眼伤只捂眼、不画血，之后缠绷带；
//   恩多尔之死只用背对 + 黑屏 + 很轻的水声 + 留白；埋葬只有沙堆和拐杖剪影。
'use strict';
(function () {
  const G = window.G, J = G.J25, M = G.MID, T = G.TPL, F = () => G.flags, X = G.EXTRA;
  const I = G.input;   // 战斗机关里直接读按键（E / J / K / ↑↓）
  const CREW5 = ['jotaro', 'joseph', 'avdol', 'kakyoin', 'polnareff'];   // 伊奇 8-03 入队；花京院 8-10 离队
  const lines = async (S, rows) => { for (const row of rows) await S.say(row[0], row[1], row[2] ? { expr: row[2] } : {}); };
  const pick = (key, arr) => arr[(T.count(key) - 1) % arr.length];
  const sayBy = (S, p, map) => S.say(p.cid, T.by(p, map));
  // 音效：新合成的还没进数据包时用现成的顶上（直接播不存在的名字会记 missingSfx）
  const hasSnd = n => !!(G.audio && G.audio.has && G.audio.has(n));
  const snd = (name, alt, o = {}) => { if (hasSnd(name)) G.audio.sfx(name, o); else if (alt) G.audio.sfx(alt, o); };
  const amb = (S, name, alt, vol) => { if (hasSnd(name)) S.ambient(name, vol); else if (alt) S.ambient(alt, vol * .6); };
  const calmStands = () => { for (const a of (G.party && G.party.members) || []) if (a.stand && a.stand.visible && a.stand.mode !== 'recall') a.stand.recall({ sfx: false }); };
  const follow = () => { if (G.party && G.party.rebuildFollow) G.party.rebuildFollow(); };

  // ---------------------------------------------------------------- 背景锚点（没有就用背景规格里的默认值）
  const bgA = (bg, k, d) => { const b = G.D && G.D.bg && G.D.bg[bg]; const v = b && b.anchors ? b.anchors[k] : null; return v != null ? v : d; };
  const COd = { arrive: [60, 164], shore: [30, 170], helipad: [200, 162], sign: [124, 150], road: [290, 162], beach: [150, 168] };
  const DDd = { arrive: [40, 164], jeep: [28, 166], crash: [520, 108], rocks: [[120, 160], [300, 158], [470, 162]],
    pebbles: [[136, 166], [214, 171], [318, 163], [402, 170], [490, 166]], dune_ndoul: [600, 150], grave: [560, 164] };
  const ASd = { arrive: [40, 164], orange: [150, 152], orange_vendor: [168, 160], tea_table: [300, 158], tea: [300, 152],
    teahouse_owner: [330, 156], cloth: [420, 150], carriage: [560, 162], boingo: [690, 156], alley: [700, 150], crate: [716, 158],
    fountain: [810, 156], exit: [940, 162], tea_seats: [[286, 158], [314, 158]] };
  const CO = k => bgA('egypt_coast', k, COd[k]);
  const DD = k => bgA('desert_day', k, DDd[k]);
  const AS = k => bgA('aswan_town', k, ASd[k]);
  // 站人的锚点 y 夹进可走带（背景的物件锚点有时给的是物件底，人要站在它前面）
  const footY = (id, y) => { const st = G.STAGES[id]; return G.clamp(y, st.yMin + 2, st.yMax - 2); };
  const at = (id, k, getter) => { const v = getter(k); return [v[0], footY(id, v[1])]; };

  // 世界地图上本章要用的“埃及东部沙漠”（第 30 天在路上；CITIES 里只有大城市，这里补一个坐标给航线用）
  if (!T.CITIES['埃及东部沙漠']) T.CITIES['埃及东部沙漠'] = [54, 77];

  function place(S, cid, x, y = 164, facing = 1) {
    const a = S.actor(cid); if (!a) return null;
    a.visible = true; a.follow = null; a.x = x; a.y = y; a.facing = facing; a.alpha = 1; a.scale = 1; S.unpose(a);
    return a;
  }
  function sit(S, cid, x, y, facing = 1) {
    const a = place(S, cid, x, y, facing);
    if (a) S.pose(a, 'sit', { freeze: 0 });
    return a;
  }
  // 角色原地播一段动作（不挡剧情）
  function act(a, anim, ms) {
    if (!a) return;
    a.hold = true; a.frozen = null; a.play(anim, { restart: true });
    G.defer((ms || 600) / 1000, () => { if (a && !a.remove) { a.hold = false; a.play(a.idleAnim || 'idle'); } }, 'world');
  }
  // 插入画面里的一张漫画格（prop:comic_panel 的帧：0–5 第 8 章三组，12 大问号）
  const comicCell = (g, frame, x, y) => {
    const A = G.propAtlas('comic_panel');
    if (A && A.ready && A.ready()) A.draw(g, 'idle', frame, x + 34, y + 56);
  };

  // ---------------------------------------------------------------- 纪念品（story\extras.js）
  X.souvenir({ id: 'ch8_gum_wrapper', chapter: 'ch8', name: '咖啡味口香糖的包装纸', desc: '银色的包装纸，还有一点咖啡味。伊奇入队的“契约书”。', hint: '海岸，伊奇入队的沙滩上' });
  X.souvenir({ id: 'ch8_comic_page', chapter: 'ch8', name: '托特神漫画的一页', desc: '画着一个被马车撞飞的人。……画得还挺好。', hint: '阿斯旺窄巷的木箱后面（要钻得进去的鼻子）' });
  X.souvenir({ id: 'ch8_teahouse_sign', chapter: 'ch8', name: '阿斯旺茶馆的木牌', desc: '掰手腕赢来的招牌。背面刻着“薄荷茶 两杯起”。', hint: '阿斯旺的茶馆，跟老板比比力气' });

  // ================================================================ 8-02 SPW 的直升机
  async function heliArrive(S) {
    calmStands(); S.party(CREW5, { leader: 'jotaro' });
    const ar = CO('arrive'), hp = CO('helipad');
    await S.setStage('coast_ch8', { x: ar[0], y: footY('coast_ch8', ar[1]), music: 'daily' });
    amb(S, 'sea_loop', 'wind_loop', .18);
    for (const [cid, dx] of [['jotaro', 0], ['joseph', 24], ['avdol', 44], ['kakyoin', -20], ['polnareff', 66]]) place(S, cid, ar[0] + dx, footY('coast_ch8', ar[1]), 1);
    S.location('egypt_coast');
    // 直升机从画面右上飞进来：旋翼两帧交替（不是“会自己播”的 loop 道具，这里按 12 fps 手动换帧）
    const heli = T.prop(S, 'heli', 372, 24, { id: 'spw_heli' });
    await S.wait(.5);
    snd('heli', 'plane_engine', { vol: .5 });
    await S.animate(1.1, k => {
      if (!heli) return;
      heli.x = G.lerp(372, hp[0], k); heli.y = G.lerp(24, hp[1] - 26, k) - Math.sin(k * Math.PI) * 4;
      heli.frozen = Math.floor(G.clk.world * 12) % 2;
    });
    S.sfx('crash', .35); S.shake(1, .25);
    for (let i = 0; i < 3; i++) S.fx('dust', { x: hp[0] - 12 + i * 12, y: footY('coast_ch8', hp[1]), size: 10 }, { life: .6 });
    const pilot = S.spawn('npc_spw', hp[0] - 34, footY('coast_ch8', hp[1]), { id: 'spw_pilot', team: 'npc', label: 'SPW 驾驶员' });
    const dog = S.spawn('iggy', hp[0] - 16, footY('coast_ch8', hp[1]), { id: 'iggy_beach', team: 'npc', label: '伊奇' });
    dog.talk = null;
    await S.walk(pilot, hp[0] - 66, footY('coast_ch8', hp[1]), { speed: 52 });
    await S.say('npc_spw', '乔斯达先生，您要的“援军”送到了。', { name: 'SPW 驾驶员', actor: pilot });
    await S.say('joseph', '来了来了！大家看，这就是我说的替身使者——伊奇！');
    await S.say('polnareff', '……狗？');
    // 伊奇扑到波鲁纳雷夫头上（不画伤口，只演扯头发）
    S.sfx('dog_bark');
    const pol = S.actor('polnareff');
    if (pol) pol.facing = dog.x > pol.x ? 1 : -1;
    await S.arc(dog, pol ? pol.x + 6 : dog.x, pol ? pol.y : dog.y, 26, .32, { anim: 'dodge' });
    dog.y = pol ? pol.y - 40 : dog.y; dog.z = 0;
    act(dog, 'bite', 700); act(pol, 'shock', 800);
    await S.say('polnareff', '哇！别扯我的头发！这是我精心梳了一早上的——！', { expr: 'shock' });
    await S.arc(dog, CO('helipad')[0] - 8, footY('coast_ch8', hp[1]), 18, .28);
    S.word('ふん', dog);
    await S.say('npc_spw', '这只狗……很难搞，祝你们好运。', { name: 'SPW 驾驶员', actor: pilot });
    await S.say('avdol', '它叫伊奇。在纽约的街头，连警察都抓不到它。');
    await S.say('joseph', '放心，我有秘密武器——咖啡味的口香糖！');
    G.flags.ch8HeliSeen = true;
  }

  // ================================================================ 8-03 投口香糖（小游戏，不会失败）
  async function gumToss(S) {
    S.flags.ch8GumTries = 0;
    const dog = S.actor('iggy_beach');
    const beach = CO('beach'), gy = footY('coast_ch8', beach[1]);
    if (dog) { dog.x = beach[0] - 40; dog.y = gy; dog.facing = 1; dog.play('run'); }
    // 伊奇在沙滩上来回跑（3 s 一个来回，到头停 0.3 s 回头看）
    let t = 0, dir = 1, rest = 0;
    T.tick(dt => {
      if (!dog || dog.remove) return true;
      t += dt;
      if (rest > 0) { rest -= dt; return false; }
      dog.x += dir * 26 * dt; dog.facing = dir;
      if (Math.abs(dog.x - (beach[0] + dir * 50)) < 2) { dir = -dir; rest = .3; dog.x = beach[0] - dir * -50; }
      if (t > 90) return true;
      return false;
    });
    const gum = T.prop(S, 'gum', CO('arrive')[0] + 92, footY('coast_ch8', 166), { id: 'gum_box' });
    await S.say('joseph', '咖啡味的！你闻闻——接住！');
    const MISS = {
      1: async () => { await S.say('joseph', '喂！那是付了钱的！……再来一块！'); S.sfx('pop', .5); },
      2: async () => {
        const pol = S.actor('polnareff');
        if (dog && pol) { S.sfx('dog_bark'); await S.arc(dog, pol.x, pol.y - 40, 24, .3, { anim: 'dodge' }); act(pol, 'shock', 700); }
        await S.say('polnareff', '为什么又是我——！', { expr: 'shock' });
        if (dog && pol) { dog.x = beach[0]; dog.y = gy; }
      },
      3: async () => { S.sfx('pop', .5); S.word('ポン', S.actor('avdol')); await S.say('avdol', '……乔斯达先生，再低一点。'); },
      4: async () => { act(dog, 'dodge', 600); await S.say('joseph', '这只狗，在看不起我……！'); },
    };
    let tries = 0, hit = false;
    while (!hit && tries < 5) {
      tries++;
      S.flags.ch8GumTries = tries;
      if (tries >= 5) {   // 第 5 次自动扔中
        hit = true;
        break;
      }
      const ok = await S.aim({ label: '方向键对准伊奇，J 扔口香糖', throw: true, time: 3, r: 16, start: [40, -10], drift: 14 + 4 * tries, jitter: .5 });
      if (ok) { hit = true; break; }
      await MISS[tries]();
    }
    if (gum) gum.remove = true;
    S.sfx('pop', .5);
    if (dog) { act(dog, 'dodge', 500); }
    await S.wait(.4);
    // 伊奇嚼着口香糖，慢吞吞走到乔瑟夫脚边坐下
    if (dog) {
      const jo = S.actor('joseph');
      await S.walk(dog, (jo ? jo.x : CO('arrive')[0]) + 26, gy, { speed: 34, anim: 'walk' });
      S.pose(dog, 'sit', { freeze: 0 });
    }
    await S.say('joseph', '哈哈哈！看见没有？这就是交涉的艺术！');
    await S.say('kakyoin', '……靠口香糖收买的援军。');
    const dogAt = dog ? { x: dog.x, y: dog.y } : { x: beach[0], y: gy };
    if (dog) dog.remove = true;
    // 入队的是队伍里的伊奇（另一个 Actor）：先撤掉海滩上那只 NPC，在它的位置入队，不然会有两只伊奇
    await S.join('iggy', { notice: true, x: dogAt.x, y: dogAt.y });
    S.nameCard('iggy');
    // 测试器用这个旗标判断“口香糖小游戏已经演完”，之后才在海岸自由走动
    F().ch8Gum = true;
  }

  // ================================================================ 8-04 埃及海岸（自由走动）
  function setupCoast(S) {
    const st = G.STAGES.coast_ch8;
    st.props = []; st.triggers = [];
    const pilotAt = [CO('helipad')[0] - 26, footY('coast_ch8', CO('helipad')[1])];
    st.npcs = [
      T.npc('npc_spw', 'spw_pilot', pilotAt[0], pilotAt[1], { facing: -1, label: 'SPW 驾驶员', name: 'SPW 驾驶员', talk: async (S, a) => {
        const p = S.player;
        if (p && p.cid === 'iggy') { S.sfx('dog_bark'); await S.say('iggy', '汪。'); await S.say('npc_spw', '……你别瞪我。口香糖不是我买的。', { name: 'SPW 驾驶员', actor: a }); return; }
        await S.say('npc_spw', pick('c8pilot', ['这只狗……很难搞。', '车给你们备在土路上了。直升机我开回去。', '祝你们好运。']), { name: 'SPW 驾驶员', actor: a });
      } }),
    ];
    const H = (id, k, label, tags, use, look, o = {}) => {
      const v = CO(k);
      return J.hot(id, v[0], footY('coast_ch8', v[1] + (o.dy || 0)), label, tags, use, look, Object.assign({ ry: 90, r: 22 }, o));
    };
    st.hotspots = [
      H('heli', 'helipad', '直升机', [], async (S, h, p) => sayBy(S, p, {
        joseph: '这次的飞机不是我开的！所以绝对不会掉下来！', _: 'SPW 财团的直升机，旋翼还在慢慢转。' }),
      async S => { S.sfx('metal_scrape', .4); await S.say('jotaro', '……旋翼上有沙子。'); }),
      H('sign', 'sign', '路牌', [], async (S, h, p) => sayBy(S, p, {
        avdol: 'EGYPT。……这一次，是真的回来了。', _: '双语的路牌：EGYPT。' }), null, { dy: 10 }),
      H('shore', 'shore', '海浪', [], async (S, h, p) => sayBy(S, p, {
        polnareff: '海水好清……我的头发被那只狗弄得全是沙子。', _: '海浪一下一下拍着沙滩。' })),
      X.hot('ch8_gum_wrapper', CO('beach')[0] + 10, footY('coast_ch8', CO('beach')[1]), { label: '沙上一张银色的包装纸', look: null }),
      M.exit('road', CO('road')[0], '土路（出发）', 'ch8Road'),
    ];
    st.onLook = async (S, p) => S.say(p.cid, T.by(p, {
      iggy: '（伊奇对着大海打了个喷嚏。）', _: '……海风有点咸。' }));
  }
  async function coastExplore(S) {
    calmStands(); S.party(CREW5.concat('iggy'), { leader: 'jotaro' });
    setupCoast(S);
    await S.setStage('coast_ch8', { x: 55, y: footY('coast_ch8', CO('arrive')[1]), music: 'daily' });
    amb(S, 'sea_loop', 'wind_loop', .16);
    T.prop(S, 'spw_jeep', CO('road')[0], footY('coast_ch8', CO('road')[1] + 2), { id: 'coast_jeep', facing: -1, frame: 0 });
    follow();
    T.memberTalk({
      joseph: async s => s.say('joseph', pick('c8talkj', ['伊奇可是我从纽约请来的！', '它喜欢咖啡味……我口袋里还有一整盒。'])),
      avdol: async s => s.say('avdol', pick('c8talka', ['伊奇的替身叫“愚者”，能用沙子变出任何形状。', '别小看它。'])),
      kakyoin: async s => s.say('kakyoin', pick('c8talkk', ['……它刚才对我龇牙了。', '狗也会讨厌人吗？'])),
      polnareff: async s => s.say('polnareff', pick('c8talkp', ['那只狗绝对是故意的！', '我的头发……'])),
      jotaro: async s => s.say('jotaro', pick('c8talkt', ['……', '……狗。'])),
      iggy: s => { s.sfx('dog_bark'); return s.say('iggy', '汪。'); },
    });
    S.free(true);
    S.hint('海岸：E 调查；沿着土路往右走。', 8);
    T.goal(S, { x: CO('road')[0], y: footY('coast_ch8', CO('road')[1]) - 44, label: '出发', delay: 40, every: 25,
      done: () => !!F().ch8Road, text: 'SPW 的车在土路上等着。' });
    await S.until(() => F().ch8Road && !S.busy);
    S.free(false);
  }

  // ================================================================ 8-05 埃及九荣神
  async function nineGods(S) {
    // 先把上一段淡到全黑，再淡回来：神名卡和对白要看得见。
    //   （setStage 的 fade:false 会连淡入一起跳过；黑幕是画在 UI 层之上的，卡片也一起被罩住）
    await S.fadeOut(.5);
    await S.fadeIn(.3);
    await S.title('nine_gods');
    await S.say(null, 'DIO 手下最后的刺客——以埃及九位神明为名的替身使者，正在前方等着。');
    await S.setStage('map_ch8', { x: 100, y: 160, music: 'travel' });
    await S.route(['红海', '埃及东部沙漠'], { vehicle: 'car', day: 30, left: 21,
      history: ['东京', '香港', '新加坡', '加尔各答', '瓦拉纳西', '卡拉奇', '阿拉伯沙漠', '红海'] });
  }

  // ================================================================ 8-06 沙漠里的水声
  async function desertAmbush(S) {
    const ar = DD('arrive');
    await S.setStage('desert_ch8', { x: ar[0], y: footY('desert_ch8', ar[1]), music: null });
    S.state('smoke', 0); S.state('sunset', 0);
    amb(S, 'wind_loop', 'wind', .1);
    S.party(CREW5.concat('iggy'), { leader: 'jotaro' });
    for (const [cid, dx] of [['jotaro', 40], ['joseph', 16], ['avdol', 62], ['kakyoin', 84], ['polnareff', 104], ['iggy', 22]])
      place(S, cid, ar[0] + dx, footY('desert_ch8', ar[1]), 1);
    T.prop(S, 'spw_jeep', DD('jeep')[0], footY('desert_ch8', DD('jeep')[1]), { id: 'desert_jeep', frame: 0 });
    S.location('egypt_desert');
    await S.until(() => !G.uifx.cards.some(k => k.kind === 'loc'));
    await S.say('joseph', '休息一下。SPW 的直升机应该已经飞回去了。');
    snd('water_jet', 'water_splash', { vol: .3 });
    await S.wait(.6);
    // 远处天上：直升机剪影一歪、冒黑烟、落到沙丘后面（只有远景剪影 + 无线电一句）
    const crash = DD('crash');
    const sil = T.prop(S, 'heli', crash[0], crash[1], { id: 'crash_heli', scale: .5, alpha: .7 });
    S.state('smoke', 1);
    snd('crash', 'explosion', { vol: .4 });
    if (sil) await S.animate(.6, k => { sil.x = crash[0] + k * 26; sil.y = crash[1] + k * k * 26; sil.rot = k * .6; sil.frozen = Math.floor(G.clk.world * 10) % 2; });
    else await S.wait(.6);
    if (sil) { sil.remove = true; }
    await S.say('npc_spw', '……来不及了。', { name: '无线电', portrait: false });
    S.sfx('radio_static', .6);
    await S.wait(1);
    await S.say('avdol', '直升机……被打下来了！从那么远的地方？！');
    await S.say('kakyoin', '大家别动！有东西在沙子底下——');
    const kak = S.actor('kakyoin');
    if (kak) {
      S.fx('water_gush', { x: kak.x, y: footY('desert_ch8', kak.y), size: 14 }, { life: .6 });
      S.sfx('water_jet', .7);
      S.pose(kak, 'cover_eyes', { freeze: 0 });
    }
    await S.say('kakyoin', '……看不见了。', { expr: 'hurt' });
    const pol = S.actor('polnareff');
    if (pol) { pol.facing = 1; await S.walk(pol, pol.x + 14, footY('desert_ch8', pol.y), { speed: 90 }); }
    await S.say('polnareff', '花京院！', { expr: 'shock' });
    S.sfx('water_jet', .7);
    if (pol) { S.pose(pol, 'hurt', { freeze: 0 }); pol.y = footY('desert_ch8', pol.y + 2); }
    await S.say('avdol', '它是靠声音找人的！……我来引开它！');
    // 阿布德尔把手镯往右扔出 80 px（落沙的声圈 48 px），0.6 s 什么都没发生
    if (kak) { S.unpose(kak); S.pose(kak, 'cover_eyes', { freeze: 0 }); }
    const av = S.actor('avdol');
    if (av) {
      S.sfx('metal_drop', .8);
      const bx = av.x + 80, by = footY('desert_ch8', av.y);
      S.fx('shockwave', { x: bx, y: by, squash: .3, r_max: 48, dur: .5, colour: '#e8d8a8' });
      await S.wait(.6);
      await S.say('avdol', '……不上当？！');
      S.sfx('water_jet', .7);
      S.pose(av, 'down', { freeze: 0 });
    }
    await S.say('joseph', '阿布德尔！……可恶，谁都不能动了！', { expr: 'shock' });
    await S.say('jotaro', '……老头子，你别出声。');
    // 远处的沙丘上：拄拐杖的人跪坐着、耳朵贴着拐杖
    const ws = T.show(S, { bg: 'desert_day', letterbox: 20, parts: [
      { kind: 'sprite', cid: 'ndoul', anim: 'idle', x: 210, y: 152, scale: 2 }] });
    S.sfx('cane_tap', .8);
    await S.wait(.35);
    S.sfx('cane_tap', .8);
    S.nameCard('ndoul');
    await S.wait(.5);
    await S.say('ndoul', '……五个人、一条狗。声音，已经告诉了我一切。', { name: '恩多尔' });
    ws.close();
    S.letterbox(false);
    await S.vs({ key: 'geb', hero: 'jotaro', enemy: { cid: 'geb' } });
    G.uifx.vsTag(null);
    await S.title('god_geb');
    await S.say('joseph', '承太郎……只有你和伊奇了。我们这些人一动，就会被它听见。');
    // 承太郎拿出口香糖晃了晃
    const gum = T.prop(S, 'gum', S.player.x + 12, footY('desert_ch8', S.player.y) - 26, { id: 'jotaro_gum' });
    await S.say('jotaro', '……跟上。');
    if (gum) gum.remove = true;
    const ig = S.actor('iggy');
    if (ig) { await S.walk(ig, S.player.x - 18, footY('desert_ch8', S.player.y + 2), { speed: 60 }); S.pose(ig, 'sit', { freeze: 0 }); await S.say('iggy', '……汪。'); S.unpose(ig); }
    S.flags.ch8AmbushSeen = true;
  }

  // ================================================================ 8-07 第 16 战段 1：盖布神 · 沙地（b16a_geb）
  async function gebSand(S) {
    const pebbles = DD('pebbles');
    await M.scene(S, 'desert_ch8', st => { st.props = []; st.triggers = []; }, 48, 'jotaro');
    S.mark('b16a_geb');
    S.state('smoke', 1); S.state('sunset', 0);
    await M.objectFight(S, {
      id: 'b16a_geb', lead: 'jotaro', swap: false, coverage: false, arena: [0, 640], bench: 'hide', music: 'battle_egypt', par: 90,
      testHint: c => ({ distance: c.data.distance, pebble: c.data.pebble, ignore: c.data.ignore, stones: c.data.stones, loops: c.data.loops }),
      tick(c, dt) {
        const d = c.data, p = c.player;
        if (d.done !== false) return;
        const dx = p.x - d.lastX;
        if (dx > 0 && dx < 30) d.distance = Math.max(2000, d.distance - dx * 2);
        d.lastX = p.x;
        d.quiet = Math.abs(dx) > .05 ? 0 : d.quiet + dt;
        // 伊奇跟在身后 24 px（不打、不会被打）
        if (d.dog) { d.dog.x = G.clamp(p.x - 24, 4, 636); d.dog.y = footY('desert_ch8', p.y + 2); }
        // 地图循环：走到右边淡出淡入回到左边，距离不断，石子重新摆好
        if (p.x >= 600 && !d.looping) {
          d.looping = true;
          M.task(c, async () => {
            p.hold = true;
            await S.fadeOut(.15);
            p.x = 80; d.lastX = 80; if (d.dog) d.dog.x = 56;
            d.stones = pebbles.slice(); d.pebble = false; respawnStones(c, d);
            d.loops++;
            d.sounds = []; d.marks = [];
            S.hint('……还有 ' + Math.ceil(d.distance) + ' 米', 2);
            await S.fadeIn(.18);
            if (!p.remove) p.hold = false;
            d.looping = false;
          });
        }
        // 声圈 → 水爪（提前量 = 往移动方向 速度 × 20f × 0.5）
        const noise = (x, y, r, delay = 20 / 60) => {
          S.fx('shockwave', { x, y, squash: .25, r_max: r, dur: .5, colour: '#b8eaff' });
          if (c.t < d.ignore) return;
          const lead = dx / Math.max(dt, .001) * delay * .5;
          d.sounds.push({ x: G.clamp(x + lead, 8, 632), y, at: c.t + delay });
        };
        M.every(d, 'step', dt, .32, () => { if (Math.abs(dx) > .05) { noise(p.x, p.y, 24); } });
        if (I.hit('attack')) noise(p.x, p.y, 64);
        if (d.quiet >= 3) { d.quiet = 0; noise(p.x, p.y, 24); }
        // E：石子旁捡石子 / 手上有石子就往前扔（扔出去 48 px 声圈，之后 2 s 不理你的声音）
        if (I.okHit()) {
          I.consumeOk();
          if (d.pebble) {
            d.pebble = false;
            const x = G.clamp(p.x + p.facing * 64, 8, 632), y = footY('desert_ch8', p.y);
            S.fx('shockwave', { x, y, squash: .3, r_max: 48, dur: .5, colour: '#fff0b0' });
            S.sfx('pop');
            d.ignore = c.t + 2; d.sounds = [{ x, y, at: c.t + 20 / 60 }];
          } else if (d.stones.some(x => Math.abs(x - p.x) < 26)) {
            const sx = d.stones.find(x => Math.abs(x - p.x) < 26);
            d.stones = d.stones.filter(x => x !== sx);
            d.pebble = true;
            S.word('石子', p);
            if (d.stoneActors) { const a = d.stoneActors.find(q => q.x === sx); if (a) a.remove = true; }
          }
        }
        // 放水可叠加：手工减免统一走 G.combat.assistK，第 1 档与原系数一致
        const warn = c.assist ? 30 / 60 : 20 / 60;
        for (const n of d.sounds.filter(n => n.at <= c.t)) {
          d.marks.push({ x: n.x, y: n.y, at: c.t, warn });
          c.hazard({ shape: 'ellipse', x: n.x, y: n.y, rx: 18, ry: 10, warn, dur: .18,
            dmg: Math.round(20 * G.combat.assistK(c, 12 / 20)), once: true, guard: 'none', fxActive: 'geb_claw', sfx: 'water_jet' });
        }
        d.sounds = d.sounds.filter(n => n.at > c.t);
        d.marks = d.marks.filter(m => c.t - m.at < m.warn + .4);
        // 同伴：第一段画面里看得到四个人在左边原地不动（循环一次后就不画了）
        if (d.loops >= 1 && !d.partyGone) {
          d.partyGone = true;
          for (const cid of ['joseph', 'avdol', 'kakyoin', 'polnareff']) { const a = G.party.get(cid); if (a) { a.visible = false; a.follow = null; } }
        }
        if (d.distance <= 2000) { d.done = true; c.end(); }
      }
    }, c => {
      const p = c.player;
      p.x = 48; p.y = footY('desert_ch8', 163); p.visible = true; p.hold = false;
      Object.assign(c.data, { distance: 4000, lastX: 48, quiet: 0, ignore: 0, pebble: false, sounds: [], marks: [], loops: 0,
        stones: pebbles.slice(), done: false, stoneActors: [], partyGone: false });
      for (const cid of ['joseph', 'avdol', 'kakyoin', 'polnareff']) {
        const a = G.party.get(cid);
        if (a) { a.visible = true; a.follow = null; a.x = 34 + G.rand(0, 40); a.y = footY('desert_ch8', 166); a.facing = 1; a.play('idle'); }
      }
      c.data.dog = c.spawn({ cid: 'iggy', x: 24, y: footY('desert_ch8', 166), team: 'npc', hold: true, untargetable: true });
      respawnStones(c, c.data);
      M.ui(S, g => {
        const d = c.data;
        M.hud(g, ['恩多尔距离 ' + Math.ceil(d.distance) + ' 米',
          d.pebble ? 'E 扔出石子，水爪会去打它' : '向右走；脚步声会引来水爪，K 闪；石子旁 E 捡']);
      });
      M.pixel('geb8_marks', P => {
        const d = c.data, cx = G.cam.x || 0;
        for (const m of d.marks) {   // 湿痕：沙色深一档的椭圆 + 两三个浅蓝水泡（出爪前 20f）
          const x = Math.round(m.x - cx), y = Math.round(m.y), k = G.clamp((c.t - m.at) / m.warn, 0, 1);
          G.px.ellipse(P, x - 12, y - 3, x + 12, y + 3, '#a88a55', null, 1, .5 + k * .3);
          for (let i = 0; i < 3; i++) G.px.rect(P, x - 6 + i * 5, y - 1 - (i % 2), 2, 2, '#bff0ff', .5 + k * .4);
        }
      });
      S.hint('慢慢走、别乱出拳：恩多尔是听着声音打的。', 6);
    });
    S.insertUI(null);
  }
  // 石子重新摆（也用在上面的循环里）
  function respawnStones(c, d) {
    for (const a of d.stoneActors || []) a.remove = true;
    d.stoneActors = [];
    for (const x of d.stones) d.stoneActors.push(c.spawn({ cid: 'prop:pebble', x, y: footY('desert_ch8', 167), team: 'object', untargetable: true }));
  }

  // ================================================================ 8-08 第 16 战段 2：盖布神 · 滑翔（b16b_geb）
  async function gebGlide(S) {
    S.party(CREW5.concat('iggy'), { leader: 'jotaro' });
    await M.scene(S, 'glide_ch8', st => { st.props = []; st.triggers = []; }, 110, 'jotaro');
    S.state('glide', 1); S.state('smoke', 1); S.state('sunset', 0);
    await S.say('jotaro', '伊奇。……变。');
    const fool = S.spawn('fool', 110, 100, { id: 'fool_glide', team: 'npc', untargetable: true, hold: true });
    if (fool) fool.play('glide');
    S.sfx('stand_summon_fool');
    await S.say('iggy', '汪！');
    S.mark('b16b_geb');
    const oldHold = S.player.hold;
    try {
      await M.objectFight(S, {
        id: 'b16b_geb', lead: 'jotaro', swap: false, coverage: false, arena: [0, 640], bench: 'hide', music: 'battle_egypt', par: 60,
        // 测试器直接遍历 columns 读 x / top / hit，所以这里给整张表（以前只给第一根，测试器会当成对象遍历失败）
        testHint: c => ({ distance: Math.round(c.data.distance), height: Math.round(c.data.height), stamina: Math.round(c.data.stamina),
          columns: c.data.columns.map(z => ({ x: Math.round(z.x), top: Math.round(z.top), hit: !!z.hit, fired: !!z.fired })) }),
        tick(c, dt) {
          const d = c.data, p = c.player;
          if (d.done !== false) return;
          const down = I.isDown('down') || (I.isDown('up') && d.collapse > 0) ? 1 : 0;
          const up = I.isDown('up') && d.collapse <= 0 ? 1 : 0;
          d.height = G.clamp(d.height + (down - up) * 74 * dt, 50, 144);
          p.hold = true; p.x = 110; p.y = d.height + 18; p.z = 0; p.play('idle');
          if (d.wing) { d.wing.x = 110 - G.cam.x * 0; d.wing.y = d.height; d.wing.play('glide'); }
          // 愚者体力：飞太高伊奇撑不住，压低一点回体力；撑不住时翼下坠 30 px、1.5 s 内抬不起来
          d.stamina = G.clamp(d.stamina + (d.height < 90 ? -12 : d.height >= 110 ? 10 : 0) * dt, 0, 100);
          if (d.collapse > 0) { d.collapse -= dt; d.height = Math.min(144, d.height - 30 * dt); }
          if (d.stamina <= 0 && d.collapse <= 0) {
            d.collapse = 1.5;
            S.hint('伊奇撑不住了！', 2);
          }
          if (d.collapse > 0 && d.stamina >= 30) d.collapse = Math.max(d.collapse, .4);
          d.distance = Math.max(0, d.distance - 80 * dt); d.scroll += 80 * dt;
          // 沙粒打在翼面上（地面上一个 14 px 声圈）→ 0.67 s 后水柱从下往上冲，柱顶 = 那一刻翼的高度 − 8
          const gap = d.distance < 500 ? (c.assist ? 1.6 : 1.2) : (c.assist ? 2.5 : 2);
          M.every(d, 'wingT', dt, gap, () => {
            S.fx('shockwave', { x: p.x - 20, y: 168, squash: .2, r_max: 14, dur: .4, colour: '#e6d6a8' });
            snd('sand_storm', 'sand_wind', { vol: .4 });
            d.columns.push({ x: 290, at: c.t, top: d.height - 8, fired: false, hit: false });
          });
          for (const col of d.columns) {
            col.x -= 180 * dt;
            if (c.t - col.at > .67 && !col.fired) { col.fired = true; snd('water_jet', 'water_splash', { vol: .7 }); }
            if (col.fired && !col.hit && Math.abs(col.x - 110) < 13 && d.height > col.top - 10) {
              col.hit = true;
              M.damage(c, Math.round(16 * G.combat.assistK(c, 10 / 16)));
            }
          }
          d.columns = d.columns.filter(col => col.x > -40);
          if (d.distance <= 0) { d.done = true; c.end(); }
        }
      }, c => {
        const p = c.player;
        Object.assign(c.data, { distance: 2000, height: 90, stamina: 100, scroll: 0, columns: [], done: false, collapse: 0 });
        p.hold = true; p.y = 108;
        c.data.wing = c.spawn({ cid: 'fool', x: 110, y: 90, team: 'npc', hold: true, untargetable: true, idleAnim: 'glide' });
        if (c.data.wing) c.data.wing.z = 0;
        M.pixel('glide8', P => {
          const d = c.data, cx = G.cam.x || 0;
          // 地面速度线
          for (let i = 0; i < 12; i++) {
            const x = ((i * 31 - d.scroll % 31) + 320) % 320;
            G.px.line(P, x, 168, x + 14, 167, '#d9b474', 1);
          }
          for (const col of d.columns) {
            const x = col.x - cx;
            if (!col.fired) G.px.ellipse(P, x - 12, 160, x + 12, 167, '#a4efff', null, 1, .8);
            else G.FX.geb_column(P, x, 170, G.clk.world, G.clk.world - .12, { top: col.top });
          }
        });
        M.ui(S, g => {
          const d = c.data;
          M.hud(g, ['距离 ' + Math.ceil(d.distance) + ' 米', '愚者体力 ' + Math.max(0, Math.round(d.stamina)) + '%',
            '↑↓ 改变高度：沙粒响了就往上飞']);
        });
      });
    } finally {
      S.player.hold = oldHold;
      S.state('glide', 0);
      const f = S.actor('fool_glide'); if (f) f.remove = true;
    }
    await S.press({ key: 'special', window: 1, label: 'U——把伊奇扔出去！', failOk: true });
    S.state('glide', 0);
  }

  // ================================================================ 8-09 扔出伊奇 → 恩多尔
  async function ndoulEnd(S) {
    const ar = DD('arrive');
    await S.setStage('desert_ch8', { x: 180, y: footY('desert_ch8', ar[1]), music: null });
    S.state('smoke', 1); S.state('sunset', 0);
    const ig = S.actor('iggy');
    const jt = S.player;
    if (ig) { ig.visible = true; ig.x = jt.x - 16; ig.y = footY('desert_ch8', jt.y); ig.facing = 1; }
    await S.say('jotaro', '伊奇——去！');
    if (ig) {
      const dune = DD('dune_ndoul');
      await S.arc(ig, dune[0] - 10, footY('desert_ch8', dune[1]), 34, .6, { anim: 'dodge', spin: 0 });
      ig.x = dune[0] - 10; ig.y = footY('desert_ch8', dune[1]);
    }
    const nd = S.spawn('ndoul', DD('dune_ndoul')[0], footY('desert_ch8', DD('dune_ndoul')[1]), { id: 'ndoul_dune', team: 'npc' });
    if (nd) { nd.facing = -1; nd.play('idle'); }
    S.sfx('cane_tap', .6);
    await S.wait(.5);
    // 承太郎冲到恩多尔面前（260 px/s）
    const target = DD('dune_ndoul')[0] - 26;
    await S.walk(jt, target, footY('desert_ch8', DD('dune_ndoul')[1]), { speed: 260, anim: 'run' });
    S.sfx('punch_heavy'); S.sfx('thud'); S.fx('hit_spark', { x: target + 16, y: 132, size: 18 }); S.shake(3, .2); S.impact('invert', 2 / 24);
    if (nd) { S.pose(nd, 'down', { freeze: 0 }); }
    await S.title('saiki');
    await S.say('ndoul', '……你的脚步声……我记住了。', { name: '恩多尔' });
    await S.say('jotaro', '……DIO 的替身是什么。');
    await S.say('ndoul', '九荣神……还有八个……你们，到不了 DIO 大人身边。', { name: '恩多尔' });
    await S.say('jotaro', '老头子的替身能读出你脑子里的东西。你藏不住的。');
    await S.say('ndoul', '……那就……让它什么都读不到。', { name: '恩多尔' });
    // 承太郎回头看向来路（背对恩多尔）→ 黑屏 1.2 s + 很轻的一声水响（不画）
    if (jt) jt.facing = -1;
    S.fx('shockwave', { x: 90, y: 150, squash: .3, r_max: 30, dur: .5, colour: '#d8eaff' });
    await S.fadeOut(.3);
    S.sfx('water_jet', .25);
    await S.wait(1.2);
    const cane = T.prop(S, 'cane', DD('dune_ndoul')[0] - 18, footY('desert_ch8', DD('dune_ndoul')[1]), { id: 'ndoul_cane', rot: .5 });
    await S.fadeIn(.4);
    if (cane) { cane.rot = 1.35; }
    await S.say('jotaro', '……他自己选了结局。');
    if (ig) { await S.walk(ig, jt.x + 22, footY('desert_ch8', jt.y + 2), { speed: 70, anim: 'walk' }); S.pose(ig, 'sit', { freeze: 0 }); }
    // 淡出 → 夕阳、黑烟灭了 → 淡入：沙丘下的墓
    await S.fadeOut(.8);
    S.state('sunset', 1); S.state('smoke', 0);
    const grave = DD('grave');
    if (nd) nd.remove = true;
    if (cane) { cane.x = grave[0]; cane.y = footY('desert_ch8', grave[1]); cane.rot = 0; }
    if (jt) place(S, 'jotaro', grave[0] - 34, footY('desert_ch8', grave[1]), 1);
    if (ig) place(S, 'iggy', grave[0] - 48, footY('desert_ch8', grave[1] + 2), 1), S.pose(S.actor('iggy'), 'sit', { freeze: 0 });
    M.pixel('ndoul_mound', P => {   // 沙堆：沙色深一档 + 阴影
      const x = grave[0] - (G.cam.x || 0), y = Math.round(footY('desert_ch8', grave[1]));
      G.px.ellipse(P, x - 16, y - 5, x + 16, y + 2, '#c9a86a');
      G.px.ellipse(P, x - 12, y - 7, x + 12, y - 1, '#dcbd80');
      G.px.ellipse(P, x - 18, y + 1, x + 18, y + 4, '#8f7448', null, 1, .6);
    });
    await S.fadeIn(.6);
    await S.say(null, '承太郎把恩多尔埋在沙丘下，插上了他的拐杖。');
    S.flags.ch8GraveSeen = true;
  }

  // ================================================================ 8-10 花京院离队
  async function kakyoinLeave(S) {
    const grave = DD('grave'), y = footY('desert_ch8', grave[1]);
    // 花京院的眼睛缠上绷带（住院中），由 SPW 工作人员扶着站在墓旁
    const kak = G.party.get('kakyoin');
    if (kak) { kak.mem.bandage = true; }
    place(S, 'kakyoin', grave[0] - 140, y, 1);
    if (kak) S.pose(kak, 'hurt', { freeze: 0 });
    const nurse = S.spawn('npc_spw', grave[0] - 154, y, { id: 'spw_nurse', team: 'npc', label: 'SPW 工作人员' });
    if (nurse) nurse.facing = 1;
    place(S, 'joseph', grave[0] - 90, y, 1);
    const av = S.actor('avdol');
    if (av) { place(S, 'avdol', grave[0] - 76, y, 1); S.pose(av, 'hurt', { freeze: 0 }); }
    place(S, 'polnareff', grave[0] - 200, y, 1);
    const pol = S.actor('polnareff');
    if (pol) { S.pose(pol, 'hurt', { freeze: 0 }); S.walk(pol, grave[0] - 112, y, { speed: 60, anim: 'limp_walk' }).catch(G.cancelIgnore); }
    T.prop(S, 'spw_jeep', grave[0] - 180, y, { id: 'leave_jeep', frame: 0 });
    await S.wait(.8);
    await S.say('avdol', '……他到最后，都没有出卖 DIO。', { expr: 'grave' });
    await S.say('joseph', '是个可怕的对手。……也是个忠心的人。', { expr: 'grave' });
    await S.say('npc_spw', '花京院先生的眼睛要马上治疗。我们送他去开罗的医院。', { name: 'SPW 工作人员', actor: nurse });
    await S.say('kakyoin', '……对不起，我先走一步。', { expr: 'hurt' });
    await S.say('polnareff', '说什么傻话！你只是去睡几天觉！', { expr: 'shock' });
    await S.say('kakyoin', '我会回来的。……在 DIO 的馆门口等我。', { expr: 'hurt' });
    await S.say('jotaro', '……嗯。');
    // 花京院上车，吉普开出画面左边
    if (kak) await S.walk(kak, grave[0] - 178, y, { speed: 44, anim: 'walk' });
    if (nurse) { nurse.remove = true; }
    const jeep = S.actor('leave_jeep');
    S.sfx('car_engine', .5);
    if (kak) { kak.remove = true; }
    if (jeep) S.walk(jeep, -60, y, { speed: 150, anim: 'idle' }).catch(G.cancelIgnore);
    await S.wait(.9);
    if (jeep) jeep.remove = true;
    // 花京院离队：灰 + 小绷带
    S.leave('kakyoin', { look: 'gray' });
    await S.notice({ who: 'kakyoin', title: '', text: '花京院 暂时离开了队伍' });
    if (av) S.unpose(av);
    if (pol) S.unpose(pol);
    S.flags.ch8KakyoinLeft = true;
  }

  // ================================================================ 8-11 阿斯旺（自由走动）
  function setupAswan(S) {
    const st = G.STAGES.aswan_ch8;
    st.props = []; st.triggers = [];
    const seat = AS('tea_seats'), fy = footY('aswan_ch8', AS('fountain')[1]);
    const fake = T.npc('fake_jotaro', 'fake_jotaro', AS('fountain')[0], fy, { facing: -1, label: '承太郎？', name: '承太郎？', z: 6,
      talk: async (S, a) => {
        const p = S.player;
        const n = T.count('c8fake');
        if (p && p.cid === 'iggy') {
          S.sfx('dog_bark'); S.sfx('dog_bark');
          await S.say('iggy', '汪！汪！');
          await S.say('fake_jotaro', n > 1 ? '……呀、呀嘞呀嘞～' : '……这、这只狗怎么回事。呀嘞呀嘞。', { name: '承太郎？', actor: a });
          return;
        }
        F().ch8FakeSeen = true;
        await S.say('polnareff', pick('c8fakep', ['承太郎？你站在那上面干什么？']));
        await S.say('fake_jotaro', n > 1 ? '……呀、呀嘞呀嘞～' : '……我、我在看风景。呀嘞呀嘞～', { name: '承太郎？', actor: a });
      } });
    st.npcs = [
      T.npc('npc_merchant', 'orange_vendor', AS('orange_vendor')[0], footY('aswan_ch8', AS('orange_vendor')[1]), { facing: -1, label: '橘子摊老板', name: '橘子摊老板', talk: async (S, a) => {
        const p = S.player;
        if (p && p.cid === 'iggy') { S.sfx('dog_bark'); await S.say('iggy', '汪。'); await S.say('npc_merchant', '哪来的小狗？别偷我的橘子！', { name: '橘子摊老板', actor: a }); return; }
        await S.say('npc_merchant', '橘子！又甜又便宜！', { name: '橘子摊老板', actor: a });
        S.sfx('coin', .5);
        await S.say('polnareff', '来两个！……一个给伊奇？它吃橘子吗？');
      } }),
      T.npc('npc_townsfolk', 'teahouse_owner', AS('teahouse_owner')[0], footY('aswan_ch8', AS('teahouse_owner')[1]), { facing: -1, label: '茶馆老板', name: '茶馆老板',
        talk: (S, a) => armWrestle(S, a) }),
      T.npc('npc_townsfolk', 'carriage_driver', AS('carriage')[0] + 20, footY('aswan_ch8', AS('carriage')[1]), { facing: -1, label: '马车夫', name: '马车夫', talk: async (S, a) => {
        const p = S.player;
        if (p && p.cid === 'iggy') await S.say('npc_townsfolk', '狗不能上车！……好吧，你别咬我。', { name: '马车夫', actor: a });
        else await S.say('npc_townsfolk', '去车站吗？……这匹马脾气不好，坐稳了。', { name: '马车夫', actor: a });
      } }),
      T.npc('boingo', 'boingo', AS('boingo')[0], footY('aswan_ch8', AS('boingo')[1]), { facing: -1, label: '看漫画的男孩', name: '看漫画的男孩', talk: async (S, a) => {
        const p = S.player;
        if (p && p.cid === 'iggy') { S.sfx('dog_bark'); await S.say('boingo', '狗、狗……走开……', { name: '看漫画的男孩', actor: a }); return; }
        await S.say('boingo', pick('c8boingo', ['……预、预言是绝对的。', '别、别看我的漫画！', '哥哥会……会让它应验的……']), { name: '看漫画的男孩', actor: a });
      } }),
      fake,
    ];
    const H = (id, k, label, tags, use, look, o = {}) => {
      const v = AS(k);
      return J.hot(id, v[0], footY('aswan_ch8', v[1]), label, tags, use, look, Object.assign({ r: 22, ry: 90 }, o));
    };
    st.hotspots = [
      H('orange_heap', 'orange', '橘子', ['scent'], async (S, h, p) => sayBy(S, p, { _: '堆成小山的橘子，个个金黄。' }),
        async S => { F().ch8OrangeSniff = true; S.sfx('dog_bark', .4); await S.say(null, '（伊奇嗅了嗅橘子堆，打了个喷嚏。）'); await S.say(null, '……有一颗的味道，像火药。'); }),
      M.exit('tea_table', AS('tea_table')[0] - 10, '茶桌（歇脚）', 'ch8Tea'),
      H('cloth', 'cloth', '布店', [], async (S, h, p) => {
        if (p && p.cid === 'iggy') { await S.say(null, '（伊奇钻到挂布底下，又钻了出来。）'); return; }
        await sayBy(S, p, { polnareff: '这块红布……做成头巾一定很衬我。', _: '挂布被风吹得鼓起来。' });
      }),
      H('carriage', 'carriage', '马车', ['cut'], async (S, h, p) => S.say(p.cid, '一辆两轮的马车，马在甩尾巴。'),
        async S => { F().ch8Reins = true; await S.say('polnareff', '缰绳有点旧……一剑就能割断。'); }),
      H('crate', 'crate', '巷口木箱', ['scent', 'hole'], async (S, h, p) => S.say(p.cid, '巷口堆着几只木箱。'),
        async (S, h) => { await S.say(null, '（伊奇钻进木箱后面，叼出一张纸）'); await X.give(S, 'ch8_comic_page', { x: h.x, y: h.y }); }),
      H('fountain', 'fountain', '喷泉', [], async (S, h, p) => { S.sfx('bat_flap', .6); await S.say(p.cid, '鸽子从喷泉边飞起来。'); }),
      H('fake_scent', 'fountain', '奇怪的气味', ['scent', 'cut'], null, async (S, h, p) => {
        F().ch8FakeSeen = true;
        if (p && p.cid === 'iggy') { snd('dog_bark', 'dog_bark', {}); S.sfx('dog_bark'); S.sfx('dog_bark'); await S.say(null, '（气味线从伊奇连到“承太郎”身上；伊奇狂叫三声。）'); await S.say(null, '……这个人的味道，不对。'); }
        else await S.say('polnareff', '……承太郎的帽子，什么时候变成这个形状了？');
      }),
    ];
    st.onLook = async (S, p) => S.say(p.cid, T.by(p, { iggy: '（伊奇抬头嗅了嗅风。到处都是香料的味道。）', polnareff: '……热闹得很。', _: '……香料、干果、马粪。阿斯旺的午后。' }));
  }
  async function armWrestle(S, a) {
    const p = S.player;
    if (p && p.cid === 'iggy') {
      S.sfx('dog_bark'); await S.say('iggy', '汪。');
      await S.say('npc_townsfolk', '你是想喝茶吗？狗可不能喝茶。', { name: '茶馆老板', actor: a });
      return;
    }
    if (F().ch8ArmWin) {
      await S.say('npc_townsfolk', pick('c8armw', ['你的手腕……是练剑的吧？', '茶管够！']), { name: '茶馆老板', actor: a });
      return;
    }
    await S.say('npc_townsfolk', '外国人，敢不敢跟我掰手腕？赢了我，这块招牌送你！', { name: '茶馆老板', actor: a });
    const sel = await S.choice(['来！', '下次吧'], '茶馆老板');
    if (sel === 1) { await S.say('npc_townsfolk', '哈哈，怕了吧？', { name: '茶馆老板', actor: a }); return; }
    await S.say('polnareff', '银色战车的主人，会输给你？');
    const ok = await S.clash({ label: '连按 J！掰倒他！', time: 4, push: .07, rate: .2, start: .5 });
    if (ok) {
      snd('wall_slam', 'thud', { vol: .5 });
      await S.say('npc_townsfolk', '……哎哟！好、好家伙！', { name: '茶馆老板', actor: a });
      await X.give(S, 'ch8_teahouse_sign', { x: a ? a.x : AS('teahouse_owner')[0], y: footY('aswan_ch8', AS('teahouse_owner')[1]) });
      await S.say('npc_townsfolk', '招牌拿去！再请你喝一杯！', { name: '茶馆老板', actor: a });
      await S.say('polnareff', 'Magnifique！');
      F().ch8ArmWin = true;
    } else {
      await S.say('npc_townsfolk', '哈哈哈哈！再练练吧，小伙子！', { name: '茶馆老板', actor: a });
      await S.say('polnareff', '刚、刚才是我的头发挡住了视线！再来！');
    }
  }
  async function aswanExplore(S) {
    calmStands();
    S.party(['jotaro', 'joseph', 'avdol', 'polnareff', 'iggy'], { leader: 'polnareff' });
    const kak = G.party.get('kakyoin');
    if (kak) { kak.mem.bandage = true; }
    S.leadable('jotaro', false, { look: 'gray', msg: '承太郎去买东西了。' });
    for (const cid of ['joseph', 'avdol']) S.leadable(cid, false, { msg: '这次由伊奇和波鲁纳雷夫行动。' });
    setupAswan(S);
    const ar = AS('arrive');
    await S.setStage('aswan_ch8', { x: ar[0], y: footY('aswan_ch8', ar[1]), music: 'daily' });
    amb(S, 'bazaar_loop', 'crowd_loop', .16);
    S.setLeader('polnareff', { force: true, silent: true });
    for (const [cid, dx] of [['polnareff', 40], ['iggy', 18], ['joseph', 0], ['avdol', -20]]) place(S, cid, ar[0] + dx, footY('aswan_ch8', ar[1]), 1);
    S.location('aswan');
    await S.until(() => !G.uifx.cards.some(k => k.kind === 'loc'));
    await S.say('joseph', '阿斯旺。坐火车去卢克索之前，在这里补点东西。');
    await S.say('polnareff', '承太郎说他去买东西了……那家伙，一句话就走。');
    await S.say('joseph', '我的腰……阿布德尔也伤着。这一段，就交给你和伊奇了。');
    follow();
    T.memberTalk({
      joseph: async s => s.say('joseph', pick('c8aswj', ['腰……年纪大了，坐车坐得腰疼。', '茶馆的薄荷茶，我请客！'])),
      avdol: async s => s.say('avdol', pick('c8aswa', ['阿斯旺的市场，我小时候来过。', '……承太郎去哪儿买东西了？'])),
      polnareff: async s => s.say('polnareff', pick('c8aswp', ['伊奇，你别乱跑！', '你闻什么呢？'])),
      iggy: s => { s.sfx('dog_bark'); return s.say('iggy', '……汪。'); },
    });
    S.free(true);
    S.hint('阿斯旺：E 搭话、调查；累了就去茶馆的茶桌歇脚。', 10);
    T.goal(S, { x: AS('tea_table')[0], y: footY('aswan_ch8', AS('tea_table')[1]) - 44, label: '茶桌', delay: 60, every: 25,
      done: () => !!F().ch8Tea, text: '乔瑟夫想喝杯茶。' });
    await S.until(() => F().ch8Tea && !S.busy);
    S.free(false);
    S.flags.ch8Aswan = true;
  }

  // ================================================================ 8-12 / 8-13 托特漫画与三个预言
  const PHASE_TEXT = { 1: '乔瑟夫喝下了下毒的茶！', 2: '一辆马车撞飞了波鲁纳雷夫！', 3: '橘子在承太郎的脸上爆炸！' };
  async function comicPanel(S, phase) {
    const base = (phase - 1) * 2;
    const v = T.show(S, { bg: 'black', letterbox: 18, draw(g, t) {
      // 三个格子（68×56，间隔 4）＋标题＋预言大字 ＋ 小字 ＋ 右下的漫画本
      const ys = 46;
      for (let i = 0; i < 3; i++) {
        const x = 44 + i * 72;
        g.fillStyle = '#fff4ce'; g.fillRect(x, ys, 68, 56);
        g.strokeStyle = '#20152b'; g.lineWidth = 2; g.strokeRect(x + 1, ys + 1, 66, 54);
        comicCell(g, i < 2 ? base + i : 12, x, ys);
      }
      const F = G.f12;
      if (!F) return;
      ['危险靠近', '预言兑现', '命运拐弯'].forEach((s, i) => F.draw(g, s, 78 + i * 72, 108, '#e8dcc0', { align: 'center', outline: '#100c18' }));
      F.draw(g, PHASE_TEXT[phase], 160, 128, '#ffe9a8', { align: 'center', outline: '#100c18' });
      F.draw(g, '托特神：三个画格，三十秒改变结局。', 160, 142, '#bdb0c8', { align: 'center', outline: '#100c18' });
      const A = G.propAtlas('manga');
      if (A && A.ready && A.ready()) { A.draw(g, 'idle', 0, 272, 150, { scale: 2 }); A.draw(g, 'idle', 1, 292, 158, { scale: 2 }); }
    } });
    try { await S.wait(2.5); } finally { v.close(); S.letterbox(false); }
    await S.say('boingo', PHASE_TEXT[phase], { name: '波因哥' });
  }
  async function prophecyFight(S, phase) {
    const seat = AS('tea_seats').map(v => [v[0], footY('aswan_ch8', v[1])]);
    const tea = AS('tea'), table = AS('tea_table');
    const targetX = phase === 1 ? table[0] : phase === 2 ? AS('carriage')[0] : null;
    S.mark('b17_prophecy' + phase);
    await M.objectFight(S, {
      id: 'b17_prophecy' + phase, lead: phase === 1 ? 'iggy' : 'polnareff', swap: true,
      allies: ['iggy', 'polnareff'], bench: { mode: 'stay', at: { joseph: seat[0], avdol: seat[1] } },
      arena: [0, 960], music: 'comedy', par: 25, timer: { until: 30, label: '预言' },
      // targetX / cartX / orangeX / dropX 都给出去：测试器按锚点走位，不再依赖写死的 x
      testHint: c => ({ phase, targetX: c.data.targetX, cartX: c.data.cart ? Math.round(c.data.cart.x) : c.data.targetX,
        orangeX: Math.round(AS('orange')[0]), dropX: Math.round(AS('tea_table')[0] + 60),
        orange: c.data.orange, left: Math.max(0, 30 - c.t), solved: c.data.solved }),
      tick(c, dt) {
        const d = c.data, p = c.player;
        if (d.solved) { if (!d.ended) { d.ended = true; c.end(); } return; }
        // 预言 2：第 10 秒起马车慢慢往左挪（10 px/s，冲着波鲁纳雷夫的方向）
        if (phase === 2 && c.t > 10 && d.cart && !d.cut) d.cart.x = Math.max(200, d.cart.x - 10 * dt);
        if (phase === 2 && d.horse && !d.cut) d.horse.x = (d.cart ? d.cart.x : AS('carriage')[0]) + 40;
        if (I.okHit()) {
          I.consumeOk();
          const near = (x, pad = 34) => Math.abs(p.x - x) < pad;
          if (phase === 1) {
            if (p.cid === 'iggy' && near(tea[0] - 5)) {
              // 伊奇跳上桌撞翻茶杯：乔瑟夫、阿布德尔起身追
              S.sfx('splash');
              S.word('搅局成功！', p);
              d.solved = true;
              if (d.cup) { d.cup.rot = Math.PI; d.cup.y = footY('aswan_ch8', tea[1]); }
              M.pixel('c8_bubble', P => { const x = tea[0] - (G.cam.x || 0), y = footY('aswan_ch8', tea[1]); for (let i = 0; i < 3; i++) G.px.disc(P, x - 3 + i * 4, y - 2 - i, 2, '#f2f2e2', .7); });
              M.task(c, async () => { await S.say('joseph', '伊奇！你这只臭狗！……嗯？桌布怎么在冒泡？'); });
            } else if (p.cid === 'iggy' && near(tea[0] + 6)) {
              S.sfx('pop', .6);
              S.word('搅局成功！', p);
              d.solved = true;
              if (d.cake) d.cake.remove = true;
              M.task(c, async () => {
                await S.say('joseph', '伊奇！那是我的蛋糕！');
                await S.say('avdol', '乔斯达先生……茶杯，没人碰过。');
              });
            } else if (near(tea[0] - 5) || near(tea[0] + 6)) {
              M.task(c, async () => { await S.say('polnareff', '这杯是乔斯达先生的……我替他尝一口？'); S.hint('让伊奇去搅局吧（Q 换人）。', 3); });
            }
          } else if (phase === 2) {
            if (p.cid === 'polnareff' && near(d.cart ? d.cart.x : targetX, 40)) {
              S.sfx('slash');
              S.word('割断缰绳！', p);
              d.cut = true; d.solved = true;
              if (d.horse) { d.horse.frozen = 2; M.task(c, () => S.walk(d.horse, -60, footY('aswan_ch8', AS('carriage')[1]), { speed: 150, anim: 'idle' })); }
              if (d.cart) { d.cart.frozen = 1; }
              const fake = d.fake;
              M.task(c, async () => {
                if (fake) await S.arc(fake, 820, footY('aswan_ch8', 160), 26, .55, { anim: 'hurt', spin: 0 });
                S.sfx('thud'); S.fx('stars', { x: 820, y: 130, size: 14 });
                await S.say('fake_jotaro', '呜哇——！为、为什么是我？！', { name: '承太郎？', actor: fake });
              });
            } else if (near(d.cart ? d.cart.x : targetX, 40)) {
              M.task(c, async () => { S.sfx('dog_bark'); await S.say(null, '（伊奇冲马叫了一声，马更躁了。）'); S.hint('让波鲁纳雷夫用剑割断缰绳（Q 换人）。', 3); });
            }
          } else if (phase === 3) {
            if (!d.orange && near(AS('orange')[0], 36)) {
              d.orange = true; S.word('拿起橘子', p); S.sfx('pop', .5);
              if (d.orangeProp) { d.orangeProp.x = p.x + p.facing * 7; d.orangeProp.y = footY('aswan_ch8', p.y) - (p.cid === 'iggy' ? 8 : 24); }
            } else if (d.orange && near(table[0] + 60, 36)) {
              d.solved = true;
              S.sfx('explosion');
              S.fx('explosion', { x: table[0] + 60, y: footY('aswan_ch8', 148), size: 22 });
              S.shake(3, .3);
              M.task(c, async () => { await S.say('fake_jotaro', '……谢、谢谢？', { name: '承太郎？' }); await S.wait(.3); await S.say(null, '（橘子在“承太郎”的脸上炸开了。）'); });
            }
          }
        }
        // 橘子跟着操作的人
        if (phase === 3 && d.orange && d.orangeProp) { d.orangeProp.x = p.x + p.facing * 7; d.orangeProp.y = footY('aswan_ch8', p.y) - (p.cid === 'iggy' ? 8 : 24); }
        if (c.t >= 30 && !d.solved) {
          const msg = phase === 1 ? '毒茶喷了一脸……从这一格漫画重来。' : phase === 2 ? '马车撞飞了你……从这一格漫画重来。' : '橘子爆了！……从这一格漫画重来。';
          if (phase === 1) { S.sfx('splash'); if (M.dashTo) {} }
          c.fail(msg);
        }
      }
    }, c => {
      const p = c.player;
      // 开始站位照脚本：预言 1 队长在茶桌左侧；预言 2 在马车左侧；预言 3 在茶桌
      const sx = phase === 1 ? table[0] - 100 : phase === 2 ? AS('carriage')[0] - 120 : table[0];
      p.x = sx; p.y = footY('aswan_ch8', 162);
      Object.assign(c.data, { phase, targetX: targetX, orange: false, solved: false, ended: false, cut: false,
        cart: null, horse: null, cup: null, cake: null, orangeProp: null, fake: null });
      // 坐着的两个人（重试时也复原）
      for (const [cid, i, face] of [['joseph', 0, 1], ['avdol', 1, -1]]) {
        const a = G.party.get(cid);
        if (a) { a.x = seat[i][0]; a.y = seat[i][1]; a.facing = face; S.pose(a, 'sit', { freeze: 0 }); }
      }
      // 假承太郎（NPC，不打人也不会被打）
      const fakeAt = phase === 1 ? [table[0] + 40, 160] : phase === 2 ? [AS('carriage')[0] + 70, 160] : [table[0] + 60, 160];
      c.data.fake = c.spawn({ cid: 'fake_jotaro', x: fakeAt[0], y: footY('aswan_ch8', fakeAt[1]), team: 'npc', hold: true, untargetable: true, facing: -1 });
      // 道具（预言 1 茶杯/蛋糕在桌面 @tea；预言 2 马车+马；预言 3 橘子）
      if (phase === 1) {
        c.data.cup = c.spawn({ cid: 'prop:tea_cup', x: tea[0] - 5, y: footY('aswan_ch8', tea[1]), team: 'object', untargetable: true });
        c.data.cake = c.spawn({ cid: 'prop:cake', x: tea[0] + 6, y: footY('aswan_ch8', tea[1]), team: 'object', untargetable: true });
      } else if (phase === 2) {
        c.data.cart = c.spawn({ cid: 'prop:carriage', x: AS('carriage')[0], y: footY('aswan_ch8', AS('carriage')[1]), team: 'object', untargetable: true });
        c.data.horse = c.spawn({ cid: 'prop:horse', x: AS('carriage')[0] + 40, y: footY('aswan_ch8', AS('carriage')[1]), team: 'object', untargetable: true });
      } else {
        c.data.orangeProp = c.spawn({ cid: 'prop:orange', x: AS('orange')[0], y: footY('aswan_ch8', AS('orange')[1]), team: 'object', untargetable: true });
      }
      M.ui(S, g => {
        const d = c.data;
        const tip = phase === 1 ? '伊奇：到茶杯 / 蛋糕旁按 E 搅局（Q 换人）'
          : phase === 2 ? (d.cut ? '马跑了！' : '波鲁纳雷夫：到马车旁按 E 割断缰绳')
          : d.orange ? '把橘子递给“承太郎”：E' : '左边拿起橘子（E），递给“承太郎”';
        M.hud(g, ['托特预言：' + PHASE_TEXT[phase] + '　' + Math.ceil(Math.max(0, 30 - c.t)) + ' 秒', tip]);
        const A = G.propAtlas('manga');
        if (A && A.ready && A.ready()) A.draw(g, 'idle', 0, 600, 120, { scale: 2 });
      });
    });
    S.insertUI(null);
    F().ch8Solved = (F().ch8Solved || 0) + 1;
    S.flags['ch8Solved' + phase] = true;
  }
  async function teaHouse(S) {
    const seat = AS('tea_seats').map(v => [v[0], footY('aswan_ch8', v[1])]);
    const table = AS('tea_table');
    sit(S, 'joseph', seat[0][0], seat[0][1], 1);
    sit(S, 'avdol', seat[1][0], seat[1][1], -1);
    const lead = S.player;
    place(S, lead.cid, table[0] - 100, footY('aswan_ch8', 162), 1);
    const other = lead.cid === 'iggy' ? 'polnareff' : 'iggy';
    place(S, other, table[0] - 120, footY('aswan_ch8', 164), 1);
    const fake = S.actor('fake_jotaro');
    if (fake) { fake.hold = true; await S.walk(fake, table[0] + 40, footY('aswan_ch8', 158), { speed: 52, anim: 'walk' }); fake.facing = -1; }
    await S.say('joseph', '啊——总算能坐下了。老板，四杯薄荷茶！……伊奇，你也要？');
    await S.say('fake_jotaro', '……我、我也坐。呀嘞呀嘞～', { name: '承太郎？', actor: fake });
    await S.say(null, '（窄巷那边：波因哥翻开漫画。）');
    S.flags.ch8Tea = true;
  }
  async function prophecies(S) {
    for (let phase = 1; phase <= 3; phase++) {
      await comicPanel(S, phase);
      await prophecyFight(S, phase);
    }
  }

  // ================================================================ 8-14 预言应验
  async function ending(S) {
    const table = AS('tea_table');   // 茶桌锚点：真承太郎从左边走进来，停在茶桌左边
    // 假承太郎的脸被炸黑，烟散开：变回奥因哥
    const fake = S.actor('fake_jotaro');
    const fakeAt = fake ? [fake.x, fake.y] : [table[0] + 60, footY('aswan_ch8', 158)];
    if (fake) fake.remove = true;
    const oi = S.spawn('oingo', fakeAt[0], fakeAt[1], { id: 'oingo_boom', team: 'npc' });
    if (oi) { oi.facing = -1; oi.play('boom'); }
    S.sfx('explosion', .5); S.fx('smoke', { x: fakeAt[0], y: fakeAt[1] - 26, size: 16 });
    S.nameCard('oingo');
    await S.say('polnareff', '……你不是承太郎？！', { expr: 'shock' });
    await S.say('oingo', '预言……为什么总是落到我头上？！');
    const bo = S.spawn('boingo', AS('boingo')[0] - 10, footY('aswan_ch8', AS('boingo')[1]), { id: 'boingo_run', team: 'npc' });
    if (bo) { bo.facing = 1; bo.play('scared'); }
    S.nameCard('boingo');
    await S.say('boingo', '哥、哥哥！漫画上画的是……“承太郎的脸”……就是你现在的脸……', { name: '波因哥' });
    await S.say('oingo', '你怎么不早说！！');
    await S.title('god_khnum');
    await S.wait(.8);
    await S.title('god_thoth');
    // 三个客人追出来
    for (let i = 0; i < 3; i++) {
      const cu = S.spawn('npc_townsfolk', AS('tea_table')[0] + 10 + i * 16, footY('aswan_ch8', 166), { id: 'c8_customer' + i, team: 'npc' });
      if (cu) cu.facing = 1;
    }
    await S.say(null, '（茶馆里被泼了一桌子茶的三个客人站起来。）');
    await S.say('npc_townsfolk', '是你们两个！把我们的茶都打翻了！', { name: '客人', actor: S.actor('c8_customer0') });
    await S.say('oingo', '快、快跑！');
    S.sfx('whoosh');
    if (oi) S.walk(oi, 980, footY('aswan_ch8', 166), { speed: 180, anim: 'run' }).catch(G.cancelIgnore);
    if (bo) S.walk(bo, 1000, footY('aswan_ch8', 166), { speed: 180, anim: 'run' }).catch(G.cancelIgnore);
    for (let i = 0; i < 3; i++) { const cu = S.actor('c8_customer' + i); if (cu) S.walk(cu, 1010 + i * 6, footY('aswan_ch8', 166), { speed: 180, anim: 'run' }).catch(G.cancelIgnore); }
    await S.wait(1.2);
    if (oi) oi.remove = true;
    if (bo) bo.remove = true;
    for (let i = 0; i < 3; i++) { const cu = S.actor('c8_customer' + i); if (cu) cu.remove = true; }
    await S.say('boingo', '绝、绝对会应验的……！', { name: '波因哥' });
    // 真承太郎拎着纸袋从左边走进来
    S.leadable('jotaro', true);
    const jt = G.party.get('jotaro');
    if (jt) { jt.visible = true; jt.x = -20; jt.y = footY('aswan_ch8', 162); jt.facing = 1; }
    const bag = T.prop(S, 'suitcase', -26, footY('aswan_ch8', 162) - 18, { id: 'c8_bag' });
    if (jt) { S.walk(jt, table[0] - 40, footY('aswan_ch8', 162), { speed: 60, anim: 'walk' }).catch(G.cancelIgnore); }
    if (bag) S.walk(bag, table[0] - 46, footY('aswan_ch8', 162) - 18, { speed: 60, anim: 'idle' }).catch(G.cancelIgnore);
    await S.wait(1.6);
    if (bag) bag.remove = true;
    await S.say('jotaro', '……你们在干什么。');
    await S.say('polnareff', '承太郎！你、你是真的吧？给我看看你的帽子！', { expr: 'shock' });
    await S.say('jotaro', '……？');
    await S.say('iggy', '汪。');
    S.flags.ch8Ending = true;
    await M.end(S, 'ch8_complete');
  }

  // ================================================================ 本章入口
  G.STORY.ch8 = async S => {
    T.resetCounters();
    for (const key of ['ch8Gum', 'ch8Road', 'ch8Tea', 'ch8GumTries', 'ch8OrangeSniff', 'ch8Reins', 'ch8FakeSeen', 'ch8ArmWin',
      'ch8Solved1', 'ch8Solved2', 'ch8Solved3', 'ch8Solved', 'ch8HeliSeen', 'ch8AmbushSeen', 'ch8GraveSeen', 'ch8KakyoinLeft',
      'ch8Aswan', 'ch8Ending']) delete F()[key];
    await M.ensureBg('_ch8');
    S.party(CREW5, { leader: 'jotaro' });
    await S.chapterCard('ch8');
    await S.run(async s => { await heliArrive(s); });
    await S.run(async s => { await gumToss(s); });
    await coastExplore(S);
    await S.run(async s => { await nineGods(s); await desertAmbush(s); });
    await S.run(async s => { await gebSand(s); await gebGlide(s); await ndoulEnd(s); await kakyoinLeave(s); });
    await aswanExplore(S);
    await S.run(async s => { await teaHouse(s); await prophecies(s); await ending(s); });
  };

  // ================================================================ 单战入口（开发调参 G.DEV / 标题「挑战」）
  G.DEV = G.DEV || {};
  G.DEV.ch8Geb = async S => {
    await M.ensureBg('_ch8'); S.party(CREW5.concat('iggy'), { leader: 'jotaro' });
    S.state('smoke', 1); S.state('sunset', 0);
    await S.run(async s => { await gebSand(s); await gebGlide(s); await ndoulEnd(s); });
  };
  G.DEV.ch8Prophecy = async S => {
    await M.ensureBg('_ch8');
    S.party(['jotaro', 'joseph', 'avdol', 'polnareff', 'iggy'], { leader: 'polnareff' });
    S.leadable('jotaro', false, { look: 'gray', msg: '承太郎去买东西了。' });
    for (const cid of ['joseph', 'avdol']) S.leadable(cid, false, { msg: '这次由伊奇和波鲁纳雷夫行动。' });
    setupAswan(S);
    await S.setStage('aswan_ch8', { x: AS('tea_table')[0] - 100, y: footY('aswan_ch8', 162), music: 'comedy' });
    await S.run(async s => { await teaHouse(s); await prophecies(s); });
  };
  X.challenge({ id: 'b16a_geb', chapter: 'ch8', title: 'VS 盖布神（承太郎）', par: 150, run: S => G.DEV.ch8Geb(S) });
  X.challenge({ id: 'b17_prophecy1', chapter: 'ch8', title: '托特神的三个预言（伊奇 / 波鲁纳雷夫）', par: 75, run: S => G.DEV.ch8Prophecy(S) });
})();
