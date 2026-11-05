// 第11章　川尻家 / 败者食尘（开发脚本 第四部/docs/第11章_开发脚本.md；地图后缀 _ch11）。整章流程：
//   节拍 1 篇章卡 → 日历地图 → 2 插曲「我的爸爸不是爸爸」（早人潜行录证据，b11_spy）→ 吉良视角：天花板角落的红灯
//   → 3 露伴宅：照片、乙雅三、Cheap Trick 爬上露伴的背 → 第 17 战段 A 十字路口（b17a_street）→ 4 幽灵小路、铃美 → 段 B（b17b_alley）
//   → 5 铃美认出背影：两张川尻浩作的照片 → 6 那天夜里：吉良、箭、败者食尘
//   → 第 18 战：循环 1 露伴被炸 → 循环 2 躲开露伴（b18_avoid）、命运 → 循环 3 告诉他们 → 最后一次：偷猫草（b18_cat）、空气弹、拖时间到 8:13
//   → 11 仗助、亿泰听见吉良的名字，败者食尘被收回 → To Be Continued。
//   克制（第三部 D10 + 设计文档 4.6）：乙雅三死只给剪影倒下和滚走的图纸筒；被炸的人只是一片白光，然后时钟倒转；早人想寻死只用旁白；箭射中是一道闪光。
//   人物 cid 用 C11.cid(…)：别章正式图合进来以前用本章的 ph11_* 占位（story/p4_ch11_fights.js）。玩法在 p4_ch11_fights.js。
'use strict';
(function () {
  const G = window.G;
  const { base, walls } = G.p4Stage;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const C = () => G.C11;
  const F = () => G.flags;
  const clk = () => (G.clk ? G.clk.ui : 0);
  const NAME_TOP = 100;
  const UW = 640, UH = 360;
  const cid = (k) => C().cid(k);

  Object.assign(G.NAMES, {
    kinoto: '乙雅三', cheaptrick: 'Cheap Trick', ph11_hayato: '早人', ph11_kosaku: '爸爸', ph11_shinobu: '妈妈', ph11_rohan: '露伴',
    ph11_okuyasu: '亿泰', ph11_reimi: '铃美', ph11_killerq: '杀手皇后',
  });

  // ================================================================ 地图
  const ST = G.STAGES;
  ST.map_ch11 = base('map_ch11', 'morioh_map', 320, { yMin: 160, yMax: 170, music: null, obstacles: [] });
  ST.kawajiri_ch11 = base('kawajiri_ch11', 'kawajiri_house', 640, { music: 'tension', obstacles: walls(10, 630, 640) });
  ST.rohanhouse_ch11 = base('rohanhouse_ch11', 'rohan_house', 480, { music: 'daily' });
  ST.street_ch11 = base('street_ch11', 'street_crossing', 960, { music: 'battle' });
  ST.alley_ch11 = base('alley_ch11', 'ghost_alley', 640, { music: 'tension' });
  ST.corner_ch11 = base('corner_ch11', 'morning_corner', 640, { music: 'tension' });

  const focus = (o) => { G.world.focus = o; };
  const snapTo = (o) => { G.world.focus = o; G.world.snapCamera(); };
  const npc = (S, k, id, x, y, f) => C().spawnNpc(S, k.indexOf('_') > 0 || G.D.chars[k] ? k : cid(k), id, x, y, f);
  const setState = (S, o) => { const st = G.world.stage; st.state = Object.assign({}, o); };

  // ================================================================ 吉良视角（冷色罩 + 暗角）
  function kiraView(S, on) {
    if (on) { S.filter('tint', 0.28, { color: '#142a5a' }); S.filter('vignette', 0.6, { colour: '#000000', inner: 0.45 }); }
    else { S.filter('tint', null); S.filter('vignette', null); }
  }
  // 白光：被炸的人整个变白、发亮，然后消失（不画别的）
  async function whiteOut(S, a, o = {}) {
    if (!a) return;
    S.sfx('void_eat', 0.6); S.sfx('zoom', 0.5);
    a.tint = { color: '#ffffff', k: 1 };
    S.fx('glint', { x: a.x, y: a.y - 18, size: 14 }, { life: 0.5 });
    S.flash(0.35, o.peak || 0.85, '#ffffff');
    await S.animate(0.5, (k) => { a.alpha = 1 - k; });
    a.visible = false; a.tint = null; a.alpha = 1;
  }
  // 时钟倒转：白屏 → 大钟的指针倒着转回 7:00
  async function rewind(S, n) {
    S.hint(null);
    S.sfx('timestop', 0.6);
    const h = P4().overlay((g, t) => {
      const a = Math.min(1, t / 0.4);
      g.save();
      g.globalAlpha = a; g.fillStyle = '#ffffff'; g.fillRect(0, 0, UW, UH);
      if (t > 0.5) {
        const u = Math.min(1, (t - 0.5) / 1.8), cx = UW / 2, cy = UH / 2 - 10, r = 62;
        g.globalAlpha = Math.min(1, (t - 0.5) * 3);
        g.fillStyle = '#2a1a2a'; g.beginPath(); g.arc(cx, cy, r + 6, 0, Math.PI * 2); g.fill();
        g.fillStyle = '#f4efe2'; g.beginPath(); g.arc(cx, cy, r, 0, Math.PI * 2); g.fill();
        g.fillStyle = '#2a1a2a';
        for (let i = 0; i < 12; i++) { const an = i / 12 * Math.PI * 2; g.fillRect(Math.round(cx + Math.sin(an) * (r - 8)) - 2, Math.round(cy - Math.cos(an) * (r - 8)) - 2, 4, 4); }
        // 分针从 8:30 倒转 18 圈回到 12 点，时针跟着倒回 7
        const mins = 510 - (510 - 420) * (1 - Math.pow(1 - u, 2));
        const am = (mins % 60) / 60 * Math.PI * 2, ah = ((mins / 60) % 12) / 12 * Math.PI * 2;
        const hand = (ang, len, w, col) => { g.strokeStyle = col; g.lineWidth = w; g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx + Math.sin(ang) * len, cy - Math.cos(ang) * len); g.stroke(); };
        hand(ah, r * 0.5, 5, '#2a1a2a'); hand(am, r * 0.82, 3, '#2a1a2a');
        g.fillStyle = '#c02a2a'; g.beginPath(); g.arc(cx, cy, 4, 0, Math.PI * 2); g.fill();
        const hh = Math.floor(mins / 60), mm = Math.floor(mins % 60);
        P4().text(g, hh + ':' + String(mm).padStart(2, '0'), cx, cy + r + 18, '#2a1a2a', 16, 'center', '#ffffff');
      }
      g.restore();
    }, { z: 6 });
    for (let i = 0; i < 6; i++) G.defer(0.6 + i * 0.3, () => S.sfx('clock_tick', 0.7), 'ui');
    await S.wait(2.6, 'ui');
    S.mark('b18_rewind' + n);
    await S.fadeOut(0.3);
    h.close();
  }
  // 代替 VS 卡：一只停在 8:30 的钟（设计文档 4.1）
  async function stoppedClock(S) {
    const h = P4().overlay((g, t) => {
      const cx = UW / 2, cy = UH / 2, r = 70;
      g.save();
      g.globalAlpha = Math.min(1, t / 0.3);
      g.fillStyle = '#0a0408'; g.fillRect(0, 0, UW, UH);
      g.fillStyle = '#5e1a22'; g.beginPath(); g.arc(cx, cy, r + 8, 0, Math.PI * 2); g.fill();
      g.fillStyle = '#efe6d6'; g.beginPath(); g.arc(cx, cy, r, 0, Math.PI * 2); g.fill();
      g.strokeStyle = '#1a0a10'; g.lineWidth = 5; g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx + Math.sin(8.5 / 12 * Math.PI * 2) * r * 0.5, cy - Math.cos(8.5 / 12 * Math.PI * 2) * r * 0.5); g.stroke();
      g.lineWidth = 3; g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx, cy + r * 0.82); g.stroke();
      P4().text(g, '8:30', cx, cy + r + 22, '#f0c0c0', 16, 'center');
      P4().text(g, '第 18 战　败者食尘', cx, 40, '#ffe0e8', 16, 'center');
      g.restore();
    }, { z: 6 });
    S.sfx('clock_tick', 0.9);
    G.defer(1.0, () => S.sfx('clock_tick', 0.9), 'ui');
    await S.wait(2.2, 'ui');
    h.close();
  }
  // 早人记住的事（第 18 战，画面右上；循环之间不清空）
  let memo = [], memoH = null;
  function memoBoard() {
    if (memoH) memoH.close();
    memoH = P4().overlay((g) => {
      const W = G.world;
      if (!memo.length || !W || W.insert || (G.S && G.S.cardOn)) return;
      if (G.ui.dlg && G.ui.dlg.y0 < 100) return;
      const x0 = 418, y0 = 104, x1 = 632, y1 = y0 + 24 + memo.length * 16;
      G.ui.box(g, x0, y0, x1, y1, { fill: 'rgba(250,244,226,0.9)' });
      P4().text(g, '早人记住的事', x0 + 8, y0 + 6, '#5a3a20', 12, 'left', null);
      memo.forEach((s, i) => P4().text(g, '・' + s, x0 + 8, y0 + 22 + i * 16, '#3a2a1a', 12, 'left', null));
    }, { z: 1 });
  }
  function remember(S, s) {
    if (memo.indexOf(s) >= 0) return;
    memo.push(s);
    S.sfx('camera_shutter', 0.6);
  }
  // 照片特写（photo11 的第 n 帧放大到画面中间）
  async function showPhotos(S, frames, hold = 2) {
    const h = P4().overlay((g, t) => {
      g.save();
      g.globalAlpha = Math.min(1, t / 0.2) * 0.6; g.fillStyle = '#000'; g.fillRect(0, 0, UW, UH);
      g.globalAlpha = Math.min(1, t / 0.2);
      frames.forEach((f, i) => G.ui.sheet(g, 'prop:photo11', f, UW / 2 + (i - (frames.length - 1) / 2) * 110, UH / 2 + 10, 2.4));
      g.restore();
    }, { z: 4 });
    S.sfx('card_flip', 0.7);
    await S.wait(hold, 'ui');
    h.close();
  }
  // Cheap Trick 贴在某人背上（换图 / 删掉就停）
  function stickBack(S, ct, a) {
    T().tick(() => {
      if (!ct || ct.remove || !a || a.remove || ct.mem.free) return true;
      ct.x = a.x - (a.facing || 1) * 7; ct.y = a.y + 0.6; ct.z = 12; ct.facing = -(a.facing || 1);
      return false;
    });
  }

  // ================================================================ 节拍 1 篇章卡 → 日历地图
  async function beatCalendar(S) {
    S.player.visible = false;
    await S.setStage('map_ch11', { x: 160, y: 165, music: null });
    const an = G.D.bg.morioh_map.anchors;
    Object.assign(an, { c11_kawajiri: an.c11_kawajiri || [140, 100], c11_rohan: an.c11_rohan || [226, 92], c11_alley: an.c11_alley || [186, 80] });
    P4().CAL.ch11 = { pins: [{ at: 'c11_kawajiri', label: '川尻家' }, { at: 'c11_rohan', label: '露伴宅' }, { at: 'c11_alley', label: '幽灵小路' }], stamp: 'stamp_ch11' };
    // 红章换成「1999年7月」（P4.calendar 读 ui.map.stamp：借用一下再还回去）
    const m = G.D.ui.map, old = m.stamp;
    if (m.stamp_ch11) m.stamp = m.stamp_ch11;
    try {
      const cal = await P4().calendar(S, 'ch11', { hold: 1.8 });
      S.mark('ch11_calendar');
      await S.fadeOut(0.45);
      if (cal) cal.close();
    } finally { m.stamp = old; }
    S.player.visible = true;
  }

  // ================================================================ 节拍 2 插曲：我的爸爸不是爸爸
  async function beatSpyIntro(S) {
    const p = S.player;
    await S.setStage('kawajiri_ch11', { x: 596, y: 160, facing: -1, music: 'tension', fade: false });
    setState(S, { night: 1, cam: 1 });
    snapTo(p);
    await S.fadeIn(0.6);
    S.location('kawajiri', { y: NAME_TOP });
    await S.narrate('我叫川尻早人，小学五年级。我家住在杜王町。', { pos: 'top' });
    await S.narrate('爸爸从某一天起，变成了另一个人。……妈妈说他变温柔了。我不这么觉得。', { pos: 'top' });
    S.nameCard(cid('hayato'), { y: NAME_TOP });
    S.mark('ch11_hayato');
    await S.narrate('我在客厅的天花板角落装了摄像机。今晚，我要亲手拍到证据。', { pos: 'top' });
    focus(null);
  }
  async function beatSpyAfter(S) {
    const p = S.player, ko = S.actor('c11_kosaku'), sh = S.actor('c11_shinobu');
    S.hint(null);
    await S.walk(p, 556, 158, { speed: 50 });
    S.face(p, 1);
    S.sfx('door', 0.5);
    await S.narrate('指甲、签名、照片。……那个人不是爸爸。', { pos: 'top' });
    await S.fadeOut(0.4);
    // 吉良视角：客厅中间，抬头看天花板角落
    if (sh) sh.remove = true;
    p.visible = false;
    const k = ko || npc(S, 'kosaku', 'c11_kosaku', 330, 152, 1);
    Object.assign(k, { x: 330, y: 152, facing: 1, visible: true });
    k.play('idle');
    snapTo({ x: 330 });
    kiraView(S, true);
    S.music('tension', 0.5);
    await S.fadeIn(0.5);
    await S.wait(0.8);
    S.sfx('blip', 0.5);
    await S.zoom(2, 362, 40, 0.5);
    await S.wait(1.0);
    await S.zoom(1, null, null, 0.3);
    S.mark('ch11_kira_cam');
    await S.say(cid('kosaku'), '……原来如此。这个家里，还有一只眼睛。', { actor: k, expr: 'smile', name: '吉良' });
    await S.fadeOut(0.6);
    kiraView(S, false);
    k.remove = true;
    p.visible = true;
  }

  // ================================================================ 节拍 3 露伴宅：照片、乙雅三、Cheap Trick
  async function beatRohanHouse(S) {
    const ro = cid('rohan');
    S.party([ro, 'koichi'], { leader: ro });
    S.leadable('koichi', false, { msg: '康一：「露伴老师背上的东西……我替不了他。」' });
    await S.setStage('rohanhouse_ch11', { x: 190, y: 158, facing: 1, music: 'daily', fade: false });
    const p = S.player, ko = S.actor('koichi');
    if (ko) { ko.follow = null; Object.assign(ko, { x: 236, y: 162, facing: -1 }); }
    snapTo({ x: 220 });
    await S.fadeIn(0.5);
    S.location('rohanhouse', { y: NAME_TOP });
    await S.say('koichi', '露伴老师，你这几天一直在镇上拍照？');
    await S.say(ro, '换了一张脸的杀人魔，总得有个新身份。我在拍每一个从那家裁缝店附近走过的人。');
    await S.say(ro, '……这张有点意思。角落里有个小孩，举着摄像机在拍他爸爸。', { expr: 'smile' });
    await showPhotos(S, [2], 2.2);
    S.mark('ch11_rohan_photo');
    // 乙雅三夹着图纸筒走来，背一直靠着门柱
    const kn = npc(S, 'kinoto', 'c11_kinoto', 500, 156, -1);
    const roll = T().prop(S, 'roll11', kn.x - 6, kn.y + 0.5, { id: 'c11_roll', z: 14 });
    T().tick(() => { if (!roll || roll.remove || roll.mem.free || kn.remove) return true; roll.x = kn.x - 6 * kn.facing; roll.y = kn.y + 0.5; return false; });
    await S.walk(kn, 300, 150, { speed: 40 });
    S.face(p, kn); if (ko) S.face(ko, kn);
    await S.say('kinoto', '岸边先生，修房子的图纸带来了。', { actor: kn });
    S.nameCard('kinoto', { y: NAME_TOP });
    S.mark('ch11_kinoto');
    await S.say(ro, '上次烧坏的地方，这周能修完吗？');
    await S.say('kinoto', '能、能修完。……就是请别站到我后面去。', { actor: kn, expr: 'shock' });
    await S.say('koichi', '乙先生，你衣服后面好像沾了什么——');
    await S.say('kinoto', '别看！别看我的背！', { actor: kn, expr: 'rage' });
    await S.say(ro, '不让人看的东西……我就越想看。', { expr: 'smile' });
    await S.walk(p, 324, 152, { speed: 60 });
    S.face(p, -1);
    S.music(null);
    S.stopMusic(0.4);
    await S.say('kinoto', '……谢谢你。终于有人看了。', { actor: kn });
    // 剪影慢慢倒下，图纸筒滚到露伴脚边（不画过程）
    kn.tint = { color: '#06040c', k: 1 }; kn.shadow = false;
    const ct = S.spawn('cheaptrick', kn.x + 6, kn.y + 0.5, { id: 'c11_ct', facing: 1 });
    ct.z = 12;
    S.sfx('heartbeat', 0.5);
    await S.animate(0.8, (k) => { kn.rot = -(Math.PI / 2) * k * k; });
    S.sfx('thud', 0.5);
    roll.mem.free = true;
    S.arc(roll, p.x - 6, p.y + 2, 6, 0.5, { spin: 6 }).catch(G.cancelIgnore);
    await S.wait(0.8);
    // 小东西从剪影背上爬到露伴背上
    await S.arc(ct, p.x - 7, p.y + 0.6, 18, 0.45, { z1: 12 });
    stickBack(S, ct, p);
    S.mark('ch11_ct_jump');
    S.sfx('sting_shock', 0.7);
    S.music('tension', 0.4);
    await S.say('cheaptrick', '嘿嘿，新家。岸边露伴老师，以后请多关照～', { actor: ct });
    S.standCard('cheaptrick', { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.wait(1.2);
    await S.say('cheaptrick', '只要有人看到你的背，我就换个主人。你嘛……就跟他一样。', { actor: ct });
    await S.say(ro, '……这家伙从背上甩不掉。', { expr: 'rage' });
    await S.say('koichi', '露伴老师！', { expr: 'shock' });
    await S.animate(0.5, (k) => { kn.alpha = 1 - k; });
    kn.remove = true; roll.remove = true;
    S.music('battle', 0.3);
    await S.vs({ key: 'cheaptrick', hero: ro, enemy: { cid: 'kinoto', anim: 'idle' } });
    G.uifx.vsTag('cheaptrick');
  }
  async function streetIn(S) {
    await S.setStage('street_ch11', { x: 30, y: 144, facing: 1, music: 'battle' });
    const p = S.player, ko = S.actor('koichi');
    if (ko) { ko.follow = null; Object.assign(ko, { x: 10, y: 158, facing: 1, visible: true }); }
    const ct = S.spawn('cheaptrick', p.x, p.y, { id: 'c11_ct', facing: -1 });
    stickBack(S, ct, p);
  }

  // ================================================================ 节拍 4 幽灵小路、铃美
  async function beatAlleyIn(S) {
    const ro = cid('rohan');
    await S.setStage('alley_ch11', { x: 40, y: 156, facing: 1, music: 'tension' });
    setState(S, { dark: 0, hands: 0 });
    const p = S.player, ko = S.actor('koichi');
    if (ko) { ko.follow = null; Object.assign(ko, { x: 16, y: 166, facing: 1, visible: true }); }
    const ct = S.spawn('cheaptrick', p.x, p.y, { id: 'c11_ct', facing: -1 });
    stickBack(S, ct, p);
    S.location('alley11', { y: NAME_TOP });
    await S.say(ro, '街上到处都是眼睛。……康一君，这条小路。');
    await S.say('koichi', '幽灵小路？在这里绝对不能回头——', { expr: 'shock' });
    await S.say(ro, '我知道。所以才要来。');
    const re = npc(S, 'reimi', 'c11_reimi', 300, 152, -1);
    re.alpha = 0;
    await S.animate(0.6, (k) => { re.alpha = 0.85 * k; });
    await S.say(cid('reimi'), '又是你们。……背上那个东西，我看得见。', { actor: re });
    S.nameCard(cid('reimi'), { y: NAME_TOP });
    S.mark('ch11_reimi');
    await S.say(cid('reimi'), '这条路的规矩你们记得吧？走到出口之前，谁回头，谁就会被拖走。', { actor: re });
    await S.say('cheaptrick', '哈？想骗我回头？我可是贴在你背上，脸一直朝着后面哦～', { actor: ct });
    // 康一留在巷口，铃美退到出口那边
    if (ko) { ko.visible = false; }
    S.walk(re, 600, 150, { speed: 90 }).catch(G.cancelIgnore);
    await S.wait(0.4);
  }
  // 段 B 的收尾：按 U → 露伴一句话 → Cheap Trick 回头 → 手的影子把它拖走
  C().onAlleyU = async (S, c) => {
    const ro = cid('rohan'), p = S.player, ct = S.actor('c11_ct');
    S.hint(null);
    await S.say(ro, '喂，Cheap Trick。……后面有人在看你的背哦。');
    if (ct) { ct.play('look'); S.sfx('sting_shock', 0.8); }
    await S.say('cheaptrick', '诶？谁？哪里——', { actor: ct });
    S.state('hands', 1);
    S.sfx('wind', 0.8); S.shake(2, 0.6);
    if (ct) {
      ct.mem.free = true;
      S.mark('b17b_hands');
      await S.say('cheaptrick', '不——要——！放开我——！', { actor: ct });
      await S.animate(1.0, (k) => { ct.x = G.lerp(p.x - 7, p.x - 260, k * k); ct.z = 12 * (1 - k); ct.alpha = 1 - k * 0.8; });
      ct.remove = true;
    }
    S.state('hands', 0);
    S.state('dark', 0);
    c.data.won = true;
  };

  // ================================================================ 节拍 5 照片：铃美认出背影
  async function beatPhotos(S) {
    const ro = cid('rohan'), p = S.player;
    const re = S.actor('c11_reimi') || npc(S, 'reimi', 'c11_reimi', 600, 150, -1);
    Object.assign(re, { x: p.x + 40, y: 150, facing: -1, visible: true, alpha: 0.85 });
    S.face(p, 1);
    S.music('sad', 0.8);
    await S.say(ro, '……总算清净了。');
    await S.say('koichi', '露伴老师！你没事吧！乙先生他……', { expr: 'shock', name: '康一（巷口）' });
    await S.say(ro, '我会把他的事画下来。……一笔都不会画错。');
    await S.say(cid('reimi'), '那些照片，能给我看看吗？', { actor: re });
    await showPhotos(S, [0, 1], 2.6);
    S.mark('ch11_photos');
    await S.say(cid('reimi'), '这个背影。十五年前，那天晚上从我家走出去的，就是这个背影。', { actor: re });
    await S.say(ro, '川尻浩作。……住在这一带的上班族。');
    await S.say(ro, '还有那个举着摄像机的孩子。明天一早，我去见见他。');
    await S.fadeOut(0.6);
    re.remove = true;
  }

  // ================================================================ 节拍 6 那天夜里：吉良、箭、败者食尘
  async function beatNight(S) {
    const hay = cid('hayato');
    S.party([hay], { leader: hay });
    await S.setStage('kawajiri_ch11', { x: 580, y: 160, facing: 1, music: null, fade: false });
    setState(S, { night: 1 });
    const p = S.player;
    T().prop(S, 'tape11', 556, 150, { id: 'c11_tape', z: 6 });
    snapTo({ x: 520 });
    S.stopMusic(0.3);
    await S.fadeIn(0.6);
    await S.title('c11_night', { y: 110 });
    S.mark('ch11_night');
    S.sfx('door', 0.6);
    const ko = npc(S, 'kosaku', 'c11_kosaku', 500, 154, 1);
    kiraView(S, true);
    await S.walk(ko, 540, 156, { speed: 30 });
    S.face(p, -1);
    await S.say(cid('kosaku'), '早人。……你的录像带，拍得很好。', { actor: ko, expr: 'smile', name: '爸爸' });
    await S.say(hay, '爸、爸爸……', { expr: 'shock' });
    S.music('tension', 0.5);
    await S.say(cid('kosaku'), '我的名字是吉良吉影。只想过安静的生活。', { actor: ko, name: '吉良吉影' });
    const kq = npc(S, 'killerq', 'c11_kq', ko.x - 14, ko.y - 1, 1);
    kq.alpha = 0; kq.z = 4;
    S.sfx('menacing', 0.7);
    await S.animate(0.5, (k) => { kq.alpha = 0.9 * k; });
    S.standCard(cid('killerq'), { y: NAME_TOP });
    await S.wait(1.0);
    // 窗外浮着一张旧照片，里面伸出一支箭
    const ph = T().prop(S, 'yphoto11', 613, 150, { id: 'c11_yphoto', z: 70 });
    S.sfx('sting_shock', 0.7);
    await S.wait(0.6);
    const ar = T().prop(S, 'arrow11', 610, 150, { id: 'c11_arrow', z: 72 });
    if (ar) ar.facing = -1;
    S.sfx('whoosh', 0.9);
    if (ar) await S.arc(ar, ko.x + 4, ko.y + 0.5, 4, 0.28, { z1: 20 });
    S.flash(0.4, 1, '#ffffff');
    S.sfx('punch_heavy', 0.7);
    S.shake(4, 0.4);
    if (ar) ar.remove = true;
    S.mark('ch11_arrow');
    await S.wait(0.6);
    await S.say(cid('kosaku'), '……箭。是父亲吗？', { actor: ko, name: '吉良吉影', expr: 'shock' });
    if (ph) ph.remove = true;
    // 杀手皇后的身影变小，钻进早人的眼睛里
    S.sfx('sparkle', 0.8);
    const x0 = kq.x, y0 = kq.y;
    await S.animate(0.9, (k) => { kq.x = G.lerp(x0, p.x, k); kq.y = G.lerp(y0, p.y + 0.5, k); kq.z = 4 + 14 * k; kq.scale = 1 - 0.9 * k; });
    kq.remove = true;
    S.fx('glint', { x: p.x, y: p.y - 22, size: 6 }, { life: 0.4 });
    S.standCard('btd', { y: NAME_TOP });
    S.cue('sting_reveal');
    S.mark('ch11_btd');
    await S.wait(1.2);
    await S.say(cid('kosaku'), '从现在起，你就是一颗炸弹。谁从你这里知道我的事，谁就会被炸掉。', { actor: ko, name: '吉良吉影', expr: 'smile' });
    await S.say(cid('kosaku'), '然后时间会倒回去。……你什么都改变不了。晚安，早人。', { actor: ko, name: '吉良吉影', expr: 'smile' });
    await S.fadeOut(0.6);
    kiraView(S, false);
    ko.remove = true;
    await stoppedClock(S);
  }

  // ================================================================ 第 18 战：每一次早晨
  async function wakeUp(S, title, lines) {
    await S.setStage('kawajiri_ch11', { x: 612, y: 158, facing: -1, music: null, fade: false });
    setState(S, { morning: 1 });
    const p = S.player;
    snapTo(p);
    await S.fadeIn(0.5);
    await S.title(title, { y: 110 });
    S.sfx('clock_tick', 0.7);
    for (const l of lines) await S.narrate(l, { pos: 'top' });
    return p;
  }
  async function loop1(S) {
    const hay = cid('hayato');
    const p = await wakeUp(S, 'c11_loop1', ['……天亮了。昨晚的事，是做梦吗？']);
    S.mark('b18_loop1');
    const ko = npc(S, 'kosaku', 'c11_kosaku', 440, 152, 1);
    await S.walk(p, 470, 160, { speed: 50 });
    S.face(ko, p); S.face(p, ko);
    await S.say(cid('kosaku'), '早上好，早人。……昨晚的事，你都记得吧？', { actor: ko, expr: 'smile', name: '爸爸' });
    await S.say(cid('kosaku'), '去上学吧。路上别跟任何人说话。', { actor: ko, name: '爸爸' });
    await S.fadeOut(0.4);
    ko.remove = true;
    await S.setStage('corner_ch11', { x: 40, y: 160, facing: 1, music: 'daily', fade: false });
    setState(S, { clock: 480 });
    snapTo(p);
    await S.fadeIn(0.4);
    S.location('corner11', { y: NAME_TOP });
    await C().go(S, 400);
    // 8:20 露伴从右边走来
    S.state('clock', 500);
    const ro = npc(S, 'rohan', 'c11_rohan', 660, 152, -1);
    await S.walk(ro, p.x + 40, p.y - 4, { speed: 50 });
    S.face(p, ro);
    await S.say(cid('rohan'), '你就是照片上那个孩子？我是漫画家岸边露伴。有些事想问你。', { actor: ro });
    await S.say(hay, '不、不要过来……！我什么都不能说！', { expr: 'shock' });
    await S.say(cid('rohan'), '不用你说。……天堂之门。', { actor: ro, expr: 'smile' });
    S.sfx('card_flip', 0.9); S.sfxText('天堂之门', p, { dur: 1.0 });
    S.mark('b18_rohan1');
    await S.wait(0.6);
    await S.say(cid('rohan'), '“爸爸的名字是吉良吉影”……？', { actor: ro, expr: 'shock' });
    await whiteOut(S, ro);
    await S.wait(0.6);
    await S.narrate('露伴老师……变成了一片白光。', { pos: 'top' });
    remember(S, '谁从我这里知道，谁就会被炸');
    remember(S, '8:20 露伴老师会来街口');
    await rewind(S, 1);
  }
  async function loop2(S) {
    const hay = cid('hayato');
    await wakeUp(S, 'c11_loop2', ['……又躺在床上。钟是 7:00。', '露伴老师来街口之前，我得先躲起来。']);
    S.mark('b18_loop2');
    await S.fadeOut(0.3);
    await S.setStage('corner_ch11', { x: 240, y: 164, facing: 1, music: 'tension', fade: false });
    setState(S, { clock: 480 });
    const p = S.player;
    snapTo({ x: 320 });
    await S.fadeIn(0.4);
    // 8:13 仗助他们从小路口走出来去上学
    const hooks = {
      init: (S2, c) => { c.data.passed = false; },
      tick: (S2, c) => {
        if (c.t >= 13 && !c.data.passed) {
          c.data.passed = true;
          const g = [npc(S2, 'josuke', 'c11_josuke', 206, 142, -1), npc(S2, 'okuyasu', 'c11_okuyasu', 220, 140, -1), npc(S2, 'koichi', 'c11_koichi', 196, 144, -1)];
          g.forEach((a, i) => S2.walk(a, -40 - i * 20, 150 + i * 6, { speed: 40 }).then(() => { a.remove = true; }, G.cancelIgnore));
          S2.emote(g[0], '今天放学去哪？', 1.6);
          remember(S2, '8:13 仗助他们从小路口经过');
        }
      },
    };
    await C().avoid(S, hooks);
    for (const id of ['c11_josuke', 'c11_okuyasu', 'c11_koichi', 'c11_rohan_walk']) { const a = S.actor(id); if (a) a.remove = true; }
    S.mark('b18_avoid_ok');
    // 8:25 远处：爸爸和露伴擦肩而过 → 白光
    S.state('clock', 505);
    const ro = npc(S, 'rohan', 'c11_rohan', 600, 150, -1), ko = npc(S, 'kosaku', 'c11_kosaku', 660, 152, -1);
    focus({ x: 470 });
    S.walk(ko, 560, 152, { speed: 40 }).catch(G.cancelIgnore);
    await S.wait(1.4);
    await whiteOut(S, ro);
    S.mark('b18_fate');
    await S.narrate('……我明明躲开了。露伴老师还是在同一个时间，变成了白光。', { pos: 'top' });
    await S.walk(ko, p.x + 40, p.y - 4, { speed: 40 });
    S.face(p, ko);
    await S.say(cid('kosaku'), '已经发生过的事，会照样发生。上一次死掉的人，这一次也会在同一个时间死。', { actor: ko, expr: 'smile', name: '吉良吉影' });
    await S.say(cid('kosaku'), '这就是“命运”。好好上学去吧。', { actor: ko, name: '吉良吉影' });
    S.walk(ko, 700, 152, { speed: 46 }).then(() => { ko.remove = true; }, G.cancelIgnore);
    await S.wait(0.8);
    // 仗助他们折回来
    const js = npc(S, 'josuke', 'c11_josuke', 150, 150, 1), ok = npc(S, 'okuyasu', 'c11_okuyasu', 120, 156, 1), kc = npc(S, 'koichi', 'c11_koichi', 96, 162, 1);
    S.walk(ok, p.x - 50, p.y - 2, { speed: 60 }).catch(G.cancelIgnore);
    S.walk(kc, p.x - 70, p.y + 6, { speed: 60 }).catch(G.cancelIgnore);
    await S.walk(js, p.x - 28, p.y - 4, { speed: 60 });
    S.face(p, js);
    await S.say('josuke', '喂，小弟弟。刚才那边一道光……你看见什么了？');
    await S.say(cid('okuyasu'), '你脸色好差啊。出什么事了？', { actor: ok });
    await S.say(hay, '……不能说。说了，你们都会……', { expr: 'shock' });
    await S.say('josuke', '没事，大哥哥们是替身使者。有什么事都告诉我们。');
    await S.fadeOut(0.6);
    await S.narrate('我想到了一个最坏的办法。只要我自己不在了，就没人能从我这里知道——', { pos: 'top' });
    await S.narrate('可是，败者食尘连这个也不允许。', { pos: 'top' });
    for (let i = 0; i < 3; i++) { S.flash(0.25, 0.9, '#ffffff'); S.sfx('void_eat', 0.5); await S.wait(0.4, 'ui'); }
    for (const a of [js, ok, kc]) a.remove = true;
    remember(S, '我自己也逃不掉');
    await rewind(S, 2);
  }
  async function loop3(S) {
    const hay = cid('hayato');
    await wakeUp(S, 'c11_loop3', ['第三次的 7:00。……不说出口的话，总行了吧。']);
    S.mark('b18_loop3');
    await S.fadeOut(0.3);
    await S.setStage('corner_ch11', { x: 260, y: 162, facing: -1, music: 'tension', fade: false });
    setState(S, { clock: 492 });
    const p = S.player;
    const js = npc(S, 'josuke', 'c11_josuke', 206, 146, 1);
    snapTo({ x: 260 });
    await S.fadeIn(0.4);
    await S.say(hay, '仗助哥哥！……我有东西要给你看。');
    await S.say('josuke', '诶？你认识我？');
    F().c11pick = 0;
    const r = await S.choice(['把名字写在纸上给他', '给他看昨晚的录像带'], '怎么告诉他？');
    F().c11pick = null;
    await S.say('josuke', r === 0 ? '“吉良……吉影”？这是谁的名字？' : '录像里这个人……在剪指甲？他是谁？', { expr: 'shock' });
    await whiteOut(S, js);
    js.remove = true;
    await S.narrate('写出来也好，给他看也好。只要是从我这里知道的……都不行。', { pos: 'top' });
    remember(S, '写出来、给他看，也不行');
    await S.narrate('能让大家知道的，只有一个办法：让吉良自己说出他的名字。', { pos: 'top' });
    remember(S, '要让吉良自己说出名字');
    await rewind(S, 3);
  }
  // 拖时间：三轮选择，选让他接着得意的那句
  const STALL = [
    { kira: '想知道我是谁？……小鬼，你听得懂吗？', good: '你这种人，根本不敢说出自己的名字。', bad: '求求你……放过我。', to: 488 },
    { kira: '不敢？我只是喜欢安静的生活。', good: '安静？你只是个躲在爸爸脸后面的胆小鬼。', bad: '……我、我不说了。', to: 490 },
    { kira: '你在拖时间吧？就算拖，又能怎么样。', good: '我只是想知道，做了那么多坏事的人叫什么。', bad: '（哭出来）', to: 493 },
  ];
  async function loop4(S) {
    const hay = cid('hayato');
    await wakeUp(S, 'c11_loop4', ['最后一次的 7:00。……这一次，我不躲了。', '家里有爸爸藏起来的那株猫草。先把它拿出来。']);
    S.mark('b18_loop4');
    await C().cat(S);
    await S.fadeOut(0.4);
    for (const id of ['c11_kosaku', 'c11_shinobu']) { const a = S.actor(id); if (a) a.remove = true; }
    await S.setStage('corner_ch11', { x: 362, y: 160, facing: 1, music: 'tension', fade: false });
    setState(S, { clock: 484 });
    const p = S.player;
    const cat = T().prop(S, C().straycat(), p.x + 6, p.y + 0.5, { id: 'c11_cat', z: 12 });
    T().tick(() => { if (!cat || cat.remove) return true; cat.x = p.x + 6 * p.facing; cat.y = p.y + 0.5; return false; });
    snapTo({ x: 400 });
    await S.fadeIn(0.4);
    await S.narrate('8:04。爸爸每天这个时间从这里经过。', { pos: 'top' });
    const ko = npc(S, 'kosaku', 'c11_kosaku', 660, 152, -1);
    await S.walk(ko, p.x + 60, 154, { speed: 40 });
    // 空气弹：打中也好、没打中也好，都被怀表挡住
    await S.timing({ label: '看准时机按 J：猫草的空气弹！' });
    const b = T().prop(S, 'bubble11', p.x + 8, p.y + 0.5, { id: 'c11_bub', z: 14 });
    S.sfx('whoosh', 0.8);
    if (b) await S.arc(b, ko.x - 4, ko.y + 0.5, 4, 0.35, { z1: 18 });
    S.sfx('clang', 0.9); S.sfxText('叮', ko, { dur: 0.8 });
    if (b) b.remove = true;
    S.mark('b18_bubble');
    S.shake(2, 0.3);
    await S.say(cid('kosaku'), '……怀表。是口袋里的怀表替我挡住了。', { actor: ko, name: '爸爸', expr: 'shock' });
    await S.say(cid('kosaku'), '早人，你连猫草都偷出来了？小鬼的把戏。', { actor: ko, name: '爸爸', expr: 'smile' });
    // 拖到 8:13
    for (let tries = 0; ; tries++) {
      let ok = true;
      S.state('clock', 486);
      for (const q of STALL) {
        await S.say(cid('kosaku'), q.kira, { actor: ko, name: '爸爸', expr: 'smile' });
        const flip = Math.random() < 0.5, opts = flip ? [q.bad, q.good] : [q.good, q.bad];
        F().c11pick = flip ? 1 : 0;
        const r = await S.choice(opts, '让他接着说下去');
        F().c11pick = null;
        if (opts[r] === q.good) { await S.say(hay, q.good, { expr: 'rage' }); S.state('clock', q.to); S.sfx('clock_tick', 0.7); continue; }
        await S.say(hay, q.bad, { expr: 'shock' });
        if (tries >= 1) { S.state('clock', q.to - 1); continue; }      // 放水：选错只是少走一点
        await S.say(cid('kosaku'), '……无聊。', { actor: ko, name: '爸爸' });
        await S.notice({ text: '爸爸不想再说了……重来一次。', minT: 1.0 });
        ok = false;
        break;
      }
      if (ok) break;
    }
    S.state('clock', 493);
    S.mark('b18_stall_ok');
    await S.say(cid('kosaku'), '好啊。反正你什么都改变不了。我的名字是——', { actor: ko, name: '爸爸', expr: 'smile' });
    // 仗助、亿泰从小路口走出来
    const js = npc(S, 'josuke', 'c11_josuke', 206, 142, 1), ok2 = npc(S, 'okuyasu', 'c11_okuyasu', 196, 146, 1);
    S.walk(ok2, p.x - 50, 156, { speed: 56 }).catch(G.cancelIgnore);
    S.walk(js, p.x - 30, 150, { speed: 56 }).catch(G.cancelIgnore);
    await S.say(cid('kosaku'), '吉良吉影。', { actor: ko, name: '吉良吉影', expr: 'smile' });
    S.mark('ch11_name');
    S.music('battle', 0.3);
    await S.say('josuke', '……吉良吉影？', { expr: 'rage' });
    await S.say(cid('okuyasu'), '就是你这家伙！', { actor: ok2, expr: 'rage' });
    await S.say(cid('kosaku'), '什么——', { actor: ko, name: '吉良吉影', expr: 'shock' });
    const kq = npc(S, 'killerq', 'c11_kq', ko.x - 14, ko.y - 1, -1);
    kq.z = 4;
    S.sfx('stand_summon_star', 0.8); S.flash(0.2, 0.6, '#ffc0e0');
    S.fx('glint', { x: p.x, y: p.y - 22, size: 6 }, { life: 0.4 });
    await S.narrate('为了用杀手皇后对付他们，他自己把败者食尘收了回去。……时间不会再倒回去了。', { pos: 'top' });
    await S.say(hay, '他就是吉良吉影！露伴老师就是被他——！', { expr: 'rage' });
    S.state('clock', 505);
    await S.narrate('8:25。……露伴老师，没有出现在白光里。', { pos: 'top' });
    S.state('clock', 506);
    S.face(js, ko);
    await S.say('josuke', '早人，你退后。剩下的交给我们。');
    S.stopMusic(0.6);
    await S.tbc({ hold: 2.0 });
    S.mark('ch11_tbc');
  }

  // ================================================================ 第11章主流程
  G.STORY.ch11 = async function (S) {
    if (T().resetCounters) T().resetCounters();
    P4().clearOverlays();
    memo = []; memoH = null;
    await S.chapterCard('ch11');
    const hay = cid('hayato');
    S.party([hay], { leader: hay });
    await S.run(async (S2) => {
      await beatCalendar(S2);
      await beatSpyIntro(S2);
      await C().spy(S2);
      await beatSpyAfter(S2);
      await beatRohanHouse(S2);
      await streetIn(S2);
      await C().street(S2);
      await beatAlleyIn(S2);
      await C().alley(S2);
      await beatPhotos(S2);
      await beatNight(S2);
      memoBoard();
      await loop1(S2);
      await loop2(S2);
      await loop3(S2);
      await loop4(S2);
    }, { keepLocked: true });
    if (memoH) { memoH.close(); memoH = null; }
  };
  // 整章测试（tools/dev/p4_play.js --chapter ch11）对照的剧情标记
  G.STORY.ch11.marks = ['ch11_calendar', 'ch11_hayato', 'b11_start', 'b11_ev1', 'b11_ev2', 'b11_ev3', 'ch11_kira_cam', 'ch11_rohan_photo', 'ch11_kinoto',
    'ch11_ct_jump', 'b17a_start', 'b17a_clear', 'ch11_reimi', 'b17b_start', 'b17b_hands', 'ch11_photos', 'ch11_night', 'ch11_arrow',
    'ch11_btd', 'b18_loop1', 'b18_rohan1', 'b18_rewind1', 'b18_loop2', 'b18_avoid_ok', 'b18_fate', 'b18_rewind2', 'b18_loop3', 'b18_rewind3',
    'b18_loop4', 'b18_cat_ok', 'b18_bubble', 'b18_stall_ok', 'ch11_name', 'ch11_tbc'];
})();
