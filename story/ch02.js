// 第2章　南海 / 南海漂流（规划 §6.1；原著 127–132 话，第 2–5 天）
//   2026-10-10 晚按序章 / 第1章体验版的精度重做（用户：“重新开第二章，开始做他第二章的剧情”）：剧情、自由走动、过场全部重写，
//   两场战斗的机关沿用原来的（招式在 engine\moves_ch02_05.js），补演出和手感。
//
//   流程：世界地图 → 包船甲板（自由：找偷渡者）→ 偷渡少女跳海、鲨鱼 QTE → 甲板（自由：查船长——烟头 + 舱盖，再去和他对质，
//   选那句谎话）→ 劫持 QTE → 第 3 战 暗蓝之月（水下）→ 舱底的炸弹、救生艇、船爆炸 → 雾里漂流一夜，货轮出现 → 货轮甲板
//   （自由：空无一人的船，三处调查；吊车自己转、船员不见了；笼子里的猩猩看得见替身）→ 管道抓人、承太郎掉进货舱 → 第 4 战 力量
//   → 货轮缩回一条生锈的小破船 → 船员都找到了 → SPW 的船 → 地图：新加坡（第 5 天）→ TBC
//
//   台词都是新写的（规划 §1.4 第 1 条：不冒充原句）；分镜原句只有阿布德尔那句「这艘船……就是替身！」（分镜 s08 4.94 s）。
//   安妮的名字是游戏里起的（原著没给名字）。“抽烟的人一说谎，鼻子上的血管就会浮起来”是原著里承太郎编的那句谎。
//   克制处理（规划 §6.1）：原著里被力量害死的水手，这里是“不见了”，战后从小破船的船舱里出来、都没事；
//   真正的坦尼尔船长只说“在香港的仓库里睡大觉”；冒牌船长打晕后绑起来交给 SPW。
//   背景：tools\bg_new\yacht_deck.py / sea_fog.py / freighter_deck.py / freighter_corridor.py / underwater.py（2026-10-10 晚重画），
//   坐标都从背景导出的 anchors 取（bgA），背景挪了位置剧情跟着走。
//   注意：进图时 Stage 会把定义里的 props / hotspots 各复制一份（world.js Stage 构造），进图以后再改 G.STAGES 的定义不影响现场——
//   所以地图的定义都在 setStage 之前写好，显示与否、说什么都读 G.flags，不靠改道具对象。
'use strict';
(function () {
  const G = window.G, T = G.TPL, J = G.J25, F = () => G.flags;
  const crew = ['jotaro', 'joseph', 'avdol', 'kakyoin', 'polnareff'];
  const lines = async (S, rows) => { for (const [who, text, expr] of rows) await S.say(who, text, expr ? { expr } : {}); };
  // 对话框放上面：人在画面下半（水里、救生艇里、躺着）时用，免得被底部对话框挡住
  const linesTop = async (S, rows) => { for (const [who, text, expr] of rows) await S.say(who, text, Object.assign({ pos: 'top' }, expr ? { expr } : {})); };
  const hot = (id, x, y, label, tags, use, look, o = {}) => Object.assign({ id, x, y, label, tags, r: 24, ry: 120, use, look }, o);
  const sayBy = (S, p, map) => S.say(p.cid, T.by(p, map));
  const pick = (key, arr) => arr[(T.count(key) - 1) % arr.length];
  const follow = () => { if (G.party && G.party.rebuildFollow) G.party.rebuildFollow(); };
  // 第2章专用音效（tools\game_sfx.py 2026-10-10 晚新合成：ape_screech / ship_horn / whirlpool / sea_loop / gulls / creak / lighter）：
  //   还没进数据包时用现成的顶上（直接播不存在的名字会记 missingSfx）
  const hasSnd = n => !!(G.audio && G.audio.has && G.audio.has(n));
  const snd = (name, alt, o = {}, ao = o) => { if (hasSnd(name)) G.audio.sfx(name, o); else if (alt) G.audio.sfx(alt, ao); };
  const ape = (vol = .6) => snd('ape_screech', 'bird_screech', { vol }, { rate: .45, vol: vol * .85 });
  const seaAmbient = (S, vol = .3) => { if (hasSnd('sea_loop')) S.ambient('sea_loop', vol); else S.ambient('wind_loop', vol * .5); };
  // 甲板上隔一阵远处的海鸥叫；货轮上隔一阵船体吱嘎（T.every 换图自己停）
  const gullsOn = () => T.every(10, () => { if (Math.random() < .6) snd('gulls', null, { vol: .35 }); });
  const creaksOn = () => T.every(8.5, () => snd('creak', null, { vol: .3, rate: .9 + Math.random() * .3 }), () => !!F().pipesMoved);
  // 过场开始前把亮着的替身都收回去：自由走动时按 U / J 亮出来的替身，剧情一跑起来就不会自己收（auto-recall 只在 free 时计时），
  //   会一直浮在每个人身后（2026-10-10 整章自动测试的截图：发现偷渡者那段四个替身全亮着）
  const calmStands = () => { for (const a of (G.party && G.party.members) || []) if (a.stand && a.stand.visible && a.stand.mode !== 'recall') a.stand.recall({ sfx: false }); };
  const place = (S, cid, x, y, facing = 1) => { const a = S.actor(cid); if (a) { a.visible = true; a.follow = null; a.x = x; a.y = y; a.facing = facing; S.unpose(a); } return a; };

  // ---------------------------------------------------------------- 背景锚点（没有就用默认值）
  const bgA = (bg, k, d) => { const b = G.D && G.D.bg && G.D.bg[bg]; const v = b && b.anchors ? b.anchors[k] : null; return v != null ? v : d; };
  const YD = { rods: [96, 150], lifeboat: [160, 148], cabin_door: [300, 150], radio: [350, 150], captain: [420, 152], cigarette: [440, 160],
    hatch: [470, 152], bow: [590, 152], overboard: [250, 146] };
  const FD = { gangway: [30, 152], galley: [110, 150], cage: [230, 152], cage_inside: [232, 146], crane: [370, 150], hold_door: [470, 150],
    bridge: [560, 150], log: [610, 150] };
  const SD = { boat: [110, 162], ladder: [250, 150] };
  const Y = k => bgA('yacht_deck', k, YD[k]);
  const Fr = k => bgA('freighter_deck', k, FD[k]);
  const Sf = k => bgA('sea_fog', k, SD[k]);

  // ---------------------------------------------------------------- 说话的人
  const capName = () => (F().captainCaught ? '冒牌坦尼尔船长' : '坦尼尔船长');
  const anneName = () => (F().anneNamed ? '安妮' : '偷渡者');
  const sayCap = (S, text, o = {}) => S.say('fake_tennille', text, Object.assign({ name: capName(), actor: S.actor('captain') || S.actor('captain_down') }, o));
  const sayAnne = (S, text, o = {}) => S.say('anne', text, Object.assign({ name: anneName(), actor: S.actor('anne') }, o));
  const saySailor = (S, id, text, o = {}) => S.say('npc_sailor', text, Object.assign({ name: '船员', actor: S.actor(id) }, o));

  // ---------------------------------------------------------------- 安妮（不是队员：换图不会被带过去，每张图自己放）
  function anneAt(S, x, y, o = {}) {
    let a = S.actor('anne');
    if (!a) a = S.spawn('anne', x, y, { id: 'anne', team: 'npc', label: anneName(), name: anneName() });
    a.visible = true; a.alpha = 1; a.follow = null; a.x = x; a.y = y; a.facing = o.facing || 1;
    a.name = anneName(); a.label = anneName();
    S.unpose(a);
    return a;
  }
  // 跟队：排在最后（跟随槽 6），不能当队长；搭话按队长不同
  function anneFollow(S) {
    if (!F().anneJoined || F().anneLeft) return null;
    const a = anneAt(S, S.player.x - 34, S.player.y, { facing: S.player.facing });
    S.follow(a, S.player); a.followSlot = 6; a.leadable = false;
    a.talk = async (S2, me, p) => {
      const L = p && p.cid;
      const t = L === 'jotaro' ? pick('c2anJo', ['……干嘛？我又没说要跟着你。', '你的帽子……睡觉的时候也戴着吗？'])
        : L === 'polnareff' ? pick('c2anPol', ['别靠近我，色狼。', '你的头发是用胶水立起来的吗？'])
          : L === 'joseph' ? pick('c2anJos', ['老爷爷，你的手是假的吗？……好酷。', '到了新加坡，我自己去找爸爸。不用你们管。'])
            : L === 'avdol' ? pick('c2anAv', ['你是算命的？那你算算，我爸爸在不在新加坡？', '……火能变成那种形状，好厉害。'])
              : L === 'kakyoin' ? pick('c2anKak', ['你说话好客气。……跟那个戴帽子的完全不一样。', '刚才接住我的，是你吧？……谢谢。'])
                : '……';
      await S2.say('anne', t, { name: '安妮', actor: a });
      // 第一次搭话时她想起来一件事：船长半夜在舱盖那边鼓捣（指向线索 2）
      if (!F().captainCaught && T.count('c2anneHint') === 1)
        await S2.say('anne', '对了。我躲在帆布下面的时候，看见船长半夜一个人蹲在舱盖那边，鼓捣了好久。', { name: '安妮', actor: a });
    };
    return a;
  }

  // ---------------------------------------------------------------- 水里的人 / 鲨鱼：水线以上照常画，水线以下只画一层淡淡的影子 + 一圈白沫
  //   （安妮、鲨鱼没有 float 动作；五个主角落水用自己的 float 帧，水线画在帧里，不走这里）。直接放进现场的 stage.props（不经复制）
  function swimmer(id, cid, o) {
    return Object.assign({ type: 'custom', id, x: 0, y: 0, depth: 150, anim: 'idle', frame: 0, flip: false, wl: 20, under: 0.28, alpha: 1, hidden: false, foam: 9,
      draw(g, sx, sy, t) {
        if (this.hidden || !G.atlas) return;
        const A = G.atlas(cid);
        if (!A || !A.draw) return;
        const bob = Math.round(Math.sin((t || 0) * 3 + this.x * 0.05));
        const x = sx, y = sy + bob, wly = y - Math.round(this.wl);
        const ga = g.globalAlpha;
        g.save(); g.beginPath(); g.rect(x - 70, wly, 140, 80); g.clip();
        g.globalAlpha = ga * this.alpha * this.under;
        A.draw(g, this.anim, this.frame, x, y, { flip: this.flip });
        g.restore();
        g.save(); g.beginPath(); g.rect(x - 70, wly - 90, 140, 90); g.clip();
        g.globalAlpha = ga * this.alpha;
        A.draw(g, this.anim, this.frame, x, y, { flip: this.flip });
        g.restore();
        g.globalAlpha = ga * this.alpha * 0.9;
        g.fillStyle = '#e6f4ff';
        const half = this.foam, ft = Math.floor((t || 0) * 6);
        for (let i = -half; i <= half; i++) if ((i + ft) % 3) g.fillRect(x + i, wly + (Math.abs(i) > half - 3 ? 1 : 0), 1, 1);
        g.globalAlpha = ga;
      } }, o);
  }
  // 坐在船里：人画在船身道具后面（船道具的 y 最大），前排脚底 = 船 y − 3、后排 = 船 y − back（lifeboat 9、rusty_boat 8）；
  //   安妮矮，再往上 6（tools\art\art_props.py 的 lifeboat / rusty_boat 说明：人放在 pivot ±40 以内、16 px 一个）
  const LIFEBOAT_SEATS = [['anne', -40, 'b'], ['joseph', -24, 'f'], ['polnareff', -8, 'b'], ['jotaro', 8, 'f'], ['avdol', 24, 'b'], ['kakyoin', 40, 'f']];
  const RUSTY_SEATS = [['anne', -26, 'b'], ['joseph', -12, 'f'], ['polnareff', 2, 'b'], ['jotaro', 16, 'f'], ['avdol', 30, 'b'], ['kakyoin', 44, 'f']];
  function seat(S, bx, by, rows, back = 9) {
    for (const [cid, dx, r] of rows) {
      const y = by - (r === 'b' ? back : 3) - (cid === 'anne' ? 6 : 0);
      if (cid === 'anne') anneAt(S, bx + dx, y, { facing: 1 }); else place(S, cid, bx + dx, y, 1);
    }
  }
  const addLive = (...ps) => { const st = G.world.stage; const ids = new Set(ps.map(p => p.id)); st.props = st.props.filter(p => !ids.has(p.id)).concat(ps); };
  const dropLive = (...ids) => { const st = G.world.stage; st.props = st.props.filter(p => !ids.includes(p.id)); };

  // ================================================================ 第 3 战：暗蓝之月（水下）
  //   机关沿用：氧气槽、气泡柱、藤壶（L 按住刮掉）、漩涡、星之指（情境招 U）。补：半血时的一句、第一次星之指的说明。
  G.BOSS25.darkmoon = () => J.base('b03_darkbluemoon', 'jotaro', [0, 640], {
    vs: 'darkbluemoon', music: 'battle', gauge: { label: '氧气', max: 100, value: 100 }, bench: 'hide',
    kitOverride: { jotaro: { dodge: { dist: 40 }, special: J.special(0, '星之指：U', c => c.data.barnacles >= 3 || c.t < c.data.openUntil, async (s, p, c, C) => {
      c.data.barnacles = 0; c.data.fingers = (c.data.fingers || 0) + 1;
      C.stand('finger', { dur: .45 }); G.audio.sfx('stab'); G.uifx.sfx('ズガッ', p);
      C.fx('glint', { x: p.x + p.facing * 80, y: p.y - 24, size: 12 }); J.fire(p, 80, 60); await C.wait(.3);
      if (c.data.fingers === 1) G.ui.hint('星之指：手指一下子伸长，连身上的藤壶一起弹掉了！', 4);
    }) } },
    waves: [[{ actor: 'darkbluemoon', kit: 'e_darkmoon', boss: true, hp: 700, poiseMax: 60, speed: 90, x: 430, y: 165, pivot: 'center', fly: { z: 10, bob: 2 },
      phases: [{ at: .5, run: async (S, e, c) => {
        if (c.attempt > 0) { await S.say('fake_tennille', '藤壶会一直长下去！', { name: '冒牌坦尼尔船长', pos: 'top' }); return; }
        await S.say('fake_tennille', '藤壶会一直长，一直长……直到你在海底动弹不得！', { name: '冒牌坦尼尔船长', pos: 'top' });
        await S.say('jotaro', '……那就在长满之前，把你打上岸。', { pos: 'top' });
      } }] }]],
    onWave: async (s, i, es, a, c) => {
      Object.assign(c.data, { barnacles: 0, bubbleX: 0, bubbleUntil: 0, nextBubble: 6, scrape: 0, damageCarry: 0, baseSpeed: c.player.speed, fingers: 0 });
      s.hint(a > 0 ? '氧气见底会掉血：进气泡柱补气。漩涡结束它停在中间时按 U。'
        : '水下：氧气一直在掉，走进冒出来的气泡柱补气；按住 L 两秒刮掉身上的藤壶；漩涡结束它停在中间——按 U 星之指！', 12);
    },
    // 2026-10-10 晚：氧气每秒 −4 → −3、气泡柱每 10 s → 8 s 冒一次、持续 4 → 5 s、见底每秒 −5 → −4（整章自动测试在这场输了 4 次，都是憋死的；规划 §6.1 同步改）
    // 气泡柱冒在承太郎左右 30–90 px（水下走速只有 38 px/s：原来随机冒在 640 宽场地的任何地方，4 s 内根本走不到）；
    //   站在里面每秒净补 6（原来 +6 减掉每秒 −4 只剩 +2，补不回来）
    tick(c, dt) {
      const d = c.data, p = c.player, b = c.boss;
      d.nextBubble -= dt;
      if (d.nextBubble <= 0) { d.nextBubble += 8; d.bubbleX = G.clamp(p.x + (Math.random() < .5 ? -1 : 1) * G.rand(30, 90), 40, 600); d.bubbleUntil = c.t + 5; G.combat.fxAt('bubbles', { x0: d.bubbleX - 8, y0: 16, x1: d.bubbleX + 8, y1: 178 }, p, 5); }
      const inBubble = c.t < d.bubbleUntil && Math.abs(p.x - d.bubbleX) <= 8;
      c.gauge.add((-3 + (inBubble ? 10 : 0)) * dt);
      p.speed = d.baseSpeed * .6 * Math.max(.5, 1 - d.barnacles * .1);
      if (G.input.isDown('guard')) { d.scrape += dt; if (d.scrape >= 2 && d.barnacles) { d.scrape -= 2; d.barnacles--; G.audio.sfx('glass_break', { rate: 1.8, vol: .6 }); } } else d.scrape = 0;
      d.damageCarry += (d.barnacles + (c.gauge.value <= 0 ? 4 : 0)) * dt;
      while (d.damageCarry >= 1) { d.damageCarry--; J.harm(c, 1); }
      if (d.vortex && b) {
        const v = d.vortex; v.t += dt;
        if (!v.snd) { v.snd = true; snd('whirlpool', 'water_gush', { vol: .8 }, { vol: .6, rate: .7 }); }
        if (v.t < 2) { b.x = 320 + Math.cos(v.t * Math.PI) * 260; b.y = 166 + Math.sin(v.t * Math.PI) * 7; }
        else {
          b.x = 320; b.y = 166;
          const dx = 320 - p.x; p.x += Math.sign(dx) * Math.min(Math.abs(dx), 60 * dt);
          v.hitT = (v.hitT || 0) + dt;
          if (Math.abs(dx) <= 16 && v.hitT >= J.f(20)) { v.hitT = 0; G.combat.hit(b, p, { dmg: 6, slot: 'enemy', push: 0, guard: 'none' }); }
        }
      }
    },
    testHint: c => ({ oxygen: c.gauge.value, barnacles: c.data.barnacles, vortex: !!c.data.vortex, bubbleX: c.data.bubbleX, bubbleActive: c.t < c.data.bubbleUntil, starWindow: c.t < c.data.openUntil }),
  });

  // ================================================================ 第 4 战：力量（货舱）
  //   机关沿用：三只“眼睛”（打碎前船壁护着猩猩）、管道 / 吊钩 / 扔东西、60% 起墙往里挤。
  //   补：墙面变肉按血量分四档（背景 pick flesh 0 / .33 / .66 / 1）、挤过来的隔舱壁画出来、60% / 30% 的两句。
  let shipEyes = [];
  // 船的“眼睛”是剧情自己生成的可破坏物，不归战斗管：每次开打（含重来）先收掉上一次的。原来重来一次就多一套眼睛，
  //   旧眼睛还挂着上一次的计数器——打碎了也不算数，眼睛计数永远到不了 3，猩猩一直无敌（2026-10-09 实测连输三次后卡死）
  const clearEyes = () => { shipEyes.forEach(a => { a.remove = true; }); shipEyes = []; };
  const HOLD_EYES = [['a', 'eye_porthole', [120, 70]], ['b', 'eye_searchlight', [360, 40]], ['c', 'eye_radar', [560, 60]]];
  // 挤过来的隔舱壁（左右各一道）：x / y 都是 0，draw 拿到的就是镜头偏移；画在人前面（depth 179）
  const bulkheads = { type: 'custom', id: 'squeeze_walls', x: 0, y: 0, depth: 179, draw(g, ox) {
    const W = G.world, c = W.fight;
    if (!c || c.id !== 'b04_strength' || !W.stage) return;
    const s = Math.round(c.data.squeezeShown || 0);
    if (s <= 0) return;
    const fl = W.stage.state ? W.stage.state.flesh || 0 : 0;
    const col = fl > .5 ? ['#8a3a62', '#c06888', '#4a1a3a'] : ['#56646a', '#8a9a98', '#2c3436'];   // 和 freighter_corridor 的青灰钢板 / 肉色一套
    for (const side of [-1, 1]) {
      const edge = side < 0 ? s : 640 - s, x0 = side < 0 ? 0 : edge, w = s;
      const ex = Math.round(edge + ox);
      g.fillStyle = col[0]; g.fillRect(Math.round(x0 + ox), 18, w, 162);
      g.fillStyle = col[1]; g.fillRect(side < 0 ? ex - 4 : ex, 18, 4, 162);
      g.fillStyle = col[2];
      for (let y = 28; y < 180; y += 18) g.fillRect(side < 0 ? ex - 10 : ex + 7, y, 3, 3);
    }
  } };
  G.BOSS25.strength = () => J.base('b04_strength', 'jotaro', [0, 640], {
    vs: 'strength', music: 'battle', bench: 'hide',
    // HP 650 → 560、眼睛 120 → 54（2026-10-10 晚：自动测试 36 次只有 1 次打碎三只眼睛；规划 §6.1 同步改）
    waves: [[{ actor: 'strength', kit: 'e_strength', boss: true, hp: 560, poiseMax: 50, speed: 80, x: 430, y: 160,
      phases: [{ at: .6, run: async (S, e, c) => {
        if (c.attempt > 0) return;
        S.sfx('metal_crunch', { rate: .6 }); S.shake(3, .4);
        await S.say('jotaro', '……整艘船，都在发抖。', { pos: 'top' });
      } }, { at: .3, run: async (S, e, c) => {
        if (c.attempt > 0) return;
        S.sfx('heartbeat');
        await S.say('jotaro', '墙壁……在跳。这艘船，是活的。', { pos: 'top' });
      } }] }]],
    onWave: async (s, i, es, a, c) => {
      const d = c.data;
      clearEyes();
      Object.assign(d, { eyes: 0, eyesActors: shipEyes, wallClock: 0, squeeze: 0, squeezeShown: 0 });
      // 重来时墙也要退回原位、墙面变回铁皮（挤墙改的是地图边界，战斗的重来不会自动还原）
      G.world.stage.x0 = c.spec.arena[0]; G.world.stage.x1 = c.spec.arena[1]; G.world.stage.state.flesh = 0;
      d.pipeCatch = () => { if (d.qteBusy) return; J.qte(c, async () => { const ok = await s.mash({ need: 10, time: 2, decay: 0, label: '管道缠住了！连按 J 挣脱' }); if (J.valid(c)) { c.player.rootT = 0; if (!ok) J.harm(c, 4); } return ok; }).catch(G.cancelIgnore); };
      for (const [k, an, def] of HOLD_EYES) {
        const [x, y] = bgA('freighter_corridor', an, def), idx = shipEyes.length;
        const e = s.spawn('prop:ship_eye_' + k, x, 160, { id: 'ship_eye_' + idx, team: 'object', hp: 54, z: 160 - y, shadow: false });
        e.visualY = y;
        const SL = ['J3', 'rush', 'fin', 'special'];
        e.breakable = { upward: true, slots: SL, filter: m => SL.includes(m.slot), onBreak: () => {
          d.eyes++; e.frozen = 1; G.audio.sfx('glass_break'); G.audio.sfx('punch_heavy', { vol: .6 }); ape(.7);
          G.shake(3, .3); G.combat.fxAt('hit_spark', { x, y: y + 2, size: 16 }, e, .3); G.combat.fxAt('burst', { x, y, n: 14, speed: 70, colours: ['#ffee68', '#b46488', '#ffffff'] }, e, .5);
          G.ui.hint('船的眼睛 ' + d.eyes + ' / 3' + (d.eyes >= 3 ? '——船壁护不住它了！猩猩露出来了！' : ''), 3);
        } };
        shipEyes.push(e);
      }
      s.hint(a > 0 ? '先打碎三只眼睛：站在正下方，J3、连打或 U 往上打。'
        : '船壁在保护猩猩！墙上有三只“眼睛”——站在正下方，用 J3、连打或 U 往上打碎它们。', 12);
    },
    tick(c, dt) {
      const d = c.data, b = c.boss, st = G.world.stage;
      if (!b) return;
      // 挤墙：三只眼睛全碎（猩猩露出来）以后开始，每 12 s 两边各往里推 60 px（最窄 640 − 2×160 = 320）。
      //   原来是血量 60% 后每 20 s 一次——眼睛碎了以后本体十几秒就打完，墙一次都来不及挤（2026-10-10 自动测试）
      if ((d.eyes || 0) >= 3) {
        d.wallClock += dt;
        if (d.wallClock >= 12) { d.wallClock -= 12; if (!d.squeeze) G.ui.hint('两边的墙在往里挤！别被夹在墙边。', 3); d.squeeze = Math.min(160, d.squeeze + 60); st.x0 = d.squeeze; st.x1 = 640 - d.squeeze; snd('creak', 'door', { vol: .9 }, { rate: .6 }); G.shake(2, .3); }
      }
      // 隔舱壁的画面慢慢推到新的边界（判定在上面一下子改）
      d.squeezeShown += Math.sign(d.squeeze - d.squeezeShown) * Math.min(Math.abs(d.squeeze - d.squeezeShown), 60 * dt);
      // 墙面变肉：按血量分四档，切档时心跳一下
      const r = b.hp / b.maxHp, want = r > .6 ? 0 : r > .45 ? .33 : r > .3 ? .66 : 1;
      if ((st.state.flesh || 0) !== want) { st.state.flesh = want; if (want > 0) { G.audio.sfx('heartbeat', { vol: .7 }); G.flash(.08, .25, '#ff6080'); } }
    },
    after: async (s, es, a, c) => { clearEyes(); },
    testHint: c => ({ eyes: c.data.eyes, squeeze: c.data.squeeze }),
  });

  // ================================================================ 包船甲板（boat_ch2，yacht_deck，640 宽）
  const clueN = () => Object.keys(F().captainClues || {}).length;
  const hasClue = k => !!(F().captainClues || {})[k];
  function memberTalkYacht() {
    T.memberTalk({
      joseph: async S => S.say('joseph', pick('c2joBoat', ['坐船慢是慢了点，可不会连累别的乘客。', '飞机？……我跟飞机八字不合。到新加坡之前，谁也别跟我提飞机。', 'Holly 那边有 SPW 的医生守着。我们只管往前走。'])),
      avdol: async S => S.say('avdol', pick('c2avBoat', ['今天早上抽到的塔罗牌是『月亮』。……月亮代表藏起来的敌人，还有谎言。', '“船上很安全”——这句话，我不太敢说出口。'])),
      kakyoin: async S => S.say('kakyoin', pick('c2kakBoat', ['南海的颜色真好看。……能这样坐船看海，还是第一次。', '法皇的触须能钻进很窄的缝。要查什么地方，可以换我来。'])),
      polnareff: async S => S.say('polnareff', pick('c2polBoat', ['阳光、大海、游艇……就差一位美女了。', '这船上一个女孩子都没有！这趟旅行太残酷了。'])),
      jotaro: async S => S.say('jotaro', pick('c2joTalk', ['……', '……吵死了。'])),
    });
  }
  function memberTalkClues() {
    T.memberTalk({
      joseph: async S => S.say('joseph', pick('c2joClue', ['那个船长是 SPW 审核过的……应该没问题吧？', '安妮那孩子，跟 Holly 小时候一样倔。'])),
      avdol: async S => S.say('avdol', pick('c2avClue', ['『月亮』……谎言。我总觉得说的就是这艘船。', '船长身上的气息很乱，像是在拼命压着什么。'])),
      kakyoin: async S => S.say('kakyoin', pick('c2kakClue', ['那个舱盖，船长一直不让人碰。……让法皇看看？', '承太郎从刚才起就一直盯着船长。'])),
      polnareff: async S => S.say('polnareff', pick('c2polClue', ['那小丫头居然叫我色狼……我只是看了一眼而已！', '船长那张脸，越看越像坏人。……我说真的。'])),
      jotaro: async S => S.say('jotaro', pick('c2joClue2', ['……那个船长，在说谎。', '……'])),
    });
  }
  // 甲板上的烟头：船长掐灭的（anneJoins 里他点了一根），显示读 flags（道具对象进图会被复制，不能靠改它的字段）
  function cigProp() {
    const [x, y] = Y('cigarette');
    return { type: 'custom', id: 'cigarette', x, y, depth: y - 4, draw(g, sx, sy) {
      if (!F().cigDropped) return;
      const pm = G.D && G.D.props && G.D.props.cigarette, im = pm && G.image ? G.image(pm.image) : null;
      if (im && G.ready && G.ready(im)) { const w = pm.size ? pm.size[0] : im.width, h = pm.size ? pm.size[1] : im.height; g.drawImage(im, 0, 0, w, h, sx - (w >> 1), sy - h, w, h); return; }
      g.fillStyle = '#f4efe6'; g.fillRect(sx - 3, sy - 2, 4, 2); g.fillStyle = '#6a5a50'; g.fillRect(sx + 1, sy - 2, 2, 2);
    } };
  }
  function setupYacht() {
    const st = G.STAGES.boat_ch2;
    st.props = [cigProp()];
    st.triggers = [];
    const [cx, cy] = Y('captain'), [rx, ry] = Y('rods'), [hx, hy] = Y('hatch'), [dx, dy] = Y('cabin_door');
    st.npcs = [
      T.npc('fake_tennille', 'captain', cx, cy, { facing: -1, label: '船长', name: '坦尼尔船长', talk: captainTalk, cond: () => !F().captainCaught,
        // 他看得见替身：亮替身时眼睛跟着转了一下（只有承太郎当队长时说破）
        onStand: async (S, a, p) => { S.emote(a, '！', .6); await sayCap(S, '……今天的海风真大啊。'); if (p && p.cid === 'jotaro') await S.say('jotaro', '（……他的眼睛，跟着白金之星转了一下。）'); } }),
      T.npc('npc_sailor', 'sailor_a', rx + 26, ry + 6, { facing: -1, label: '船员', name: '船员', talk: async S => saySailor(S, 'sailor_a', pick('c2sa', F().anneJoined
        ? ['那个小丫头运气真好，鲨鱼都给你们打跑了。', '钓竿还在，鱼一条没上。今天的海……怪安静的。']
        : ['这片海鲨鱼多，掉下去可就上不来了。', '钓了一上午，一条都没上钩。今天的海……怪安静的。'])) }),
      T.npc('npc_sailor', 'sailor_b', dx + 22, dy + 6, { facing: 1, label: '船员', name: '船员', talk: async S => saySailor(S, 'sailor_b', pick('c2sb', F().anneJoined
        ? ['原来啃面包的不是老鼠，是那个丫头。……咬我那一口真疼。', '船长一大早就在甲板上转来转去，像在等什么。']
        : ['厨房的面包少了一个，边上一圈小小的牙印。', '有老鼠？船上的老鼠可没这么挑食。'])) }),
      T.npc('npc_sailor', 'sailor_c', hx + 36, hy + 6, { facing: -1, label: '船员', name: '船员', talk: async S => saySailor(S, 'sailor_c', pick('c2sc',
        ['船长不让碰那个舱盖，说下面是机器零件。', '船长昨晚半夜一个人在甲板上抽烟……他不是说自己从来不抽烟吗？'])) }),
    ];
    const say = (S, p, text) => S.say(p.cid, text);
    st.hotspots = [
      hot('lifeboat', Y('lifeboat')[0], Y('lifeboat')[1], '救生艇', ['life', 'detail'],
        async (S, h, p) => {
          if (F().anneFound) { await say(S, p, '救生艇。帆布掀开了，里面空了。'); return; }
          const n = T.count('c2tarpUse');
          if (n === 1) await say(S, p, '救生艇。帆布绑得很随便……下面鼓鼓的。');
          else if (n === 2) await say(S, p, T.by(p, { avdol: '……帆布好像动了一下。用火焰探一探（U）？', jotaro: '……帆布在动。看仔细点（U）。',
            _: '……帆布好像动了一下。（阿布德尔的火焰、承太郎的眼睛看得出来：Q 换队长，U 替身调查）' }));
          else { await say(S, p, '……不管了，掀开看看！'); F().anneFound = true; }
        },
        async (S, h, p) => {
          if (F().anneFound) { await say(S, p, '帆布下面已经没人了。'); return; }
          await say(S, p, T.by(p, { avdol: '帆布下面……有一个很小的生命，在发抖。', jotaro: '……帆布在动。下面有人。', _: '帆布下面有人。' }));
          F().anneFound = true;
        }, { ly: 108 }),
      hot('rods', rx, ry, '钓竿', ['cut'],
        async (S, h, p) => sayBy(S, p, { polnareff: '钓鱼？交给我！……（一拉）什么都没有。', joseph: '年轻的时候，我在纽约的码头钓过一条这么大的——……好吧，这么大。', _: '钓竿。线一下子绷紧，又松开了。' }),
        async (S, h, p) => S.say(p.cid, '……鱼线被我切断了。Pardon。'), { ly: 118 }),
      hot('radio', Y('radio')[0], Y('radio')[1], '无线电', [],
        async (S, h, p) => sayBy(S, p, { joseph: '这里是乔瑟夫·乔斯达，SPW 听到请回答——……全是杂音。', kakyoin: '频道被拧到了一个奇怪的频率上。……谁动过？', _: '无线电。全是杂音。' }), null, { ly: 108 }),
      hot('cabin_door', dx, dy, '船舱', [],
        async (S, h, p) => S.say(p.cid, F().anneJoined ? '船舱。安妮的湿衣服晾在门口。' : '船舱。堆着罐头、淡水和救生衣。'), null, { ly: 110 }),
      hot('hatch', hx, hy, '舱盖', ['peek', 'reach'],
        async (S, h, p) => {
          if (hasClue('hatch')) { await say(S, p, '舱盖下面……滴答，滴答。'); return; }
          if (!F().anneJoined) { await say(S, p, '舱盖锁着。船员说下面是机器零件。'); return; }
          await say(S, p, T.by(p, { kakyoin: '锁死了。……不过触须能从缝里钻进去（U）。', _: '舱盖锁死了。……下面好像有滴答声？（花京院的触须能从缝里钻进去：Q 换队长，U 替身调查）' }));
        },
        async (S, h, p) => {
          J.unique('captainClues', 'hatch');
          await lines(S, [['kakyoin', '舱底堆着几个箱子……有一个绑着电线，在滴答响。'], ['kakyoin', '……是计时器。']]);
          if (clueN() >= 2) S.hint('线索够了。去找船长对质。', 6);
        }, { ly: 140 }),
      hot('cigarette', Y('cigarette')[0], Y('cigarette')[1], '烟头', ['detail', 'grab'],
        async (S, h, p) => {
          if (hasClue('cigarette')) { await say(S, p, '刚掐灭的烟头。滤嘴上有很深的牙印。'); return; }
          await say(S, p, T.by(p, { jotaro: '……烟头。看仔细点（U）。', _: '一截刚掐灭的烟头。……船长不是说甲板上禁止吸烟吗？' }));
          if (p.cid !== 'jotaro') { J.unique('captainClues', 'cigarette'); if (clueN() >= 2) S.hint('线索够了。去找船长对质。', 6); }
        },
        async (S, h, p) => {
          J.unique('captainClues', 'cigarette');
          await lines(S, [['jotaro', '滤嘴上有很深的牙印。……抽这根烟的人，紧张得要命。'], ['jotaro', '刚才站在这里的，只有船长。']]);
          if (clueN() >= 2) S.hint('线索够了。去找船长对质。', 6);
        }, { cond: () => !!F().cigDropped, ly: 150 }),
      hot('bow', Y('bow')[0], Y('bow')[1], '船头', [],
        async (S, h, p) => sayBy(S, p, { polnareff: '船头！张开双臂……这种事一个人做好寂寞。', avdol: '风很大。……风里有一股不像海的味道。', _: '风很大。远处有一群海鸥。' }), null, { ly: 120 }),
    ];
    st.onLook = async (S, p) => sayBy(S, p, {
      avdol: F().anneFound ? '船上的生命……和名单上的人数对上了。' : '这艘船上的生命……比名单上多一个。',
      jotaro: '……', joseph: '这里没有相机可以砸。……船长的相机？算了。', kakyoin: '触须能伸到舱盖下面去。', polnareff: 'Voilà～',
    });
  }
  async function captainTalk(S) {
    if (!F().anneJoined) {
      await sayCap(S, pick('c2capA', ['SPW 的人审核过我，放心吧。到新加坡三天，你们只管休息。', '小鬼头别在甲板上乱跑。', '我还有事，别跟着我。']));
      return;
    }
    if (!F().captainLied && hasClue('cigarette')) {
      F().captainLied = true;
      await lines(S, [['jotaro', '……甲板上禁止吸烟。你自己说的。']]);
      await sayCap(S, '当然。我在海上跑了二十年，从来不抽烟。');
      await lines(S, [['jotaro', '……是吗。']]);
      if (clueN() < 2) return;
    }
    if (clueN() < 2) {
      await sayCap(S, pick('c2capB', ['别在船上乱查。小鬼们，回船舱休息去。', '那个偷渡的丫头，看好了。……别让她再给我添麻烦。']));
      return;
    }
    await confront(S);
  }

  // ---------------------------------------------------------------- 开场（甲板上）
  async function boatIntro(S) {
    calmStands();
    const [cx, cy] = Y('captain');
    const cap = S.actor('captain');
    crew.forEach((cid, i) => place(S, cid, 120 + i * 26, 152 + (i % 2) * 8, 1));
    await lines(S, [['polnareff', '海风！阳光！这才叫旅行嘛～'],
      ['joseph', '飞机太危险，会连累别的乘客。坐船就安心多了——这艘船是 SPW 安排的，船长也是他们审核过的。']]);
    if (cap) { cap.facing = -1; await S.walk(cap, 268, 156, { speed: 70 }); cap.facing = -1; }
    await sayCap(S, '我是船长坦尼尔。到新加坡大约三天。船上的规矩只有一条——');
    const jo = S.actor('jotaro');
    if (jo) S.emote(jo, '…', .8);
    await sayCap(S, '甲板上禁止吸烟。……把烟掐了，小鬼。');
    S.sfx('whoosh', { vol: .4, rate: 1.4 });
    await lines(S, [['jotaro', '……呀嘞呀嘞。'], ['polnareff', '哇哦，这船长真凶。']]);
    if (cap) { await S.walk(cap, cx, cy, { speed: 60 }); cap.facing = -1; }
    follow();
  }

  // ---------------------------------------------------------------- 发现偷渡者 → 跳海 → 鲨鱼
  async function anneReveal(S) {
    calmStands();
    S.hint(null);
    const [lx, ly] = Y('lifeboat'), [ox, oy] = Y('overboard');
    const p = S.player;
    for (const cid of crew) { const a = S.actor(cid); if (a) a.follow = null; }
    S.state('tarp', 1); S.sfx('whoosh', { vol: .7, rate: .8 });
    const anne = S.spawn('anne', lx + 4, ly - 2, { id: 'anne', team: 'npc', label: '偷渡者', name: '偷渡者', shadow: false, z: 18 });
    anne.facing = p.x > lx ? 1 : -1;
    await S.arc(anne, lx + 16, ly + 6, 12, .35);
    anne.z = 0; anne.shadow = true;
    S.emote(anne, '！', .8);
    const sb = S.actor('sailor_b');
    if (sb) { sb.talk = null; await S.walk(sb, lx + 40, ly + 6, { speed: 130 }); sb.facing = -1; }
    await sayAnne(S, '别碰我！');
    if (sb) { S.sfx('punch', { vol: .4, rate: 1.6 }); S.shake(1, .15); S.act(sb, 'hurt'); }
    await saySailor(S, 'sailor_b', '痛——！这小子咬人！');
    await lines(S, [['polnareff', '哈哈哈，好凶的小鬼。']]);
    await sayAnne(S, '我有钱！……到了新加坡，我会付船票的！');
    await lines(S, [['joseph', '小家伙，你一个人跑到海上来做什么？']]);
    await sayAnne(S, '关你什么事！谁要被你们关起来！');
    anne.facing = ox > anne.x ? 1 : -1;
    await S.walk(anne, ox, oy + 4, { speed: 130, anim: 'run' });
    S.sfx('whoosh');
    await S.arc(anne, ox + 6, oy - 6, 26, .32);
    anne.visible = false;
    S.sfx('splash'); S.fx('water_splash', { x: ox + 8, y: oy - 14, size: .9 });
    S.sfxText('扑通——！！', { x: 320, y: 120 });
    await lines(S, [['joseph', 'OH MY GOD! 跳下去了！', 'shock']]);
    await saySailor(S, 'sailor_a', '这片海有鲨鱼——！');
    const jo = S.actor('jotaro');
    await lines(S, [['jotaro', '……呀嘞呀嘞daze。']]);
    S.sfxText('呀嘞呀嘞daze', jo || 'player');
    if (jo) { await S.walk(jo, ox, oy + 4, { speed: 140, anim: 'run' }); S.sfx('whoosh'); await S.arc(jo, ox + 6, oy - 6, 26, .32); jo.visible = false; S.sfx('splash'); S.fx('water_splash', { x: ox + 8, y: oy - 14, size: 1 }); }
    await S.wait(.3);
    await sharkScene(S);
  }
  async function sharkScene(S) {
    // sea_ch2（sea_day，320 单屏，海平线 y 100）：安妮在左边扑腾，承太郎从右边游过来，鲨鱼从右后方冲过来
    await S.setStage('sea_ch2', { x: 236, y: 170, fade: true, music: 'tension' });
    seaAmbient(S, .35);
    for (const cid of crew) { const a = S.actor(cid); if (a) { a.follow = null; a.visible = cid === 'jotaro'; } }
    const jo = S.actor('jotaro');
    if (jo) { jo.visible = true; jo.x = 236; jo.y = 170; jo.facing = -1; S.pose(jo, 'float'); }
    const anneSw = swimmer('anne_swim', 'anne', { x: 112, y: 158, wl: 26, anim: 'shock', depth: 158 });
    const shark = swimmer('shark_swim', 'prop:shark', { x: 330, y: 160, wl: 6, depth: 160, under: .45, foam: 12, flip: false });
    addLive(anneSw, shark);
    await linesTop(S, [['anne', '咕噜……救、救命——！']]);
    S.sfx('water_gush', { vol: .5 });
    await S.animate(1.2, k => { shark.x = 330 - k * 120; shark.y = 160 + Math.sin(k * 9) * 1.5; });
    await linesTop(S, [['jotaro', '……']]);
    const r = await S.press({ key: 'attack', window: .67, failOk: true, label: '鲨鱼冲过来了！按 J', y: 16 });
    if (jo) S.summon(jo, { dur: .12, rise: 4 });
    if (r === 'miss') {
      S.sfx('punch', { vol: .6 }); S.shake(3, .3); if (jo) jo.hp = Math.max(1, jo.hp - 8);
      S.fx('water_splash', { x: shark.x - 20, y: 156, size: .8 });
      await linesTop(S, [['jotaro', '……啧。']]);
    }
    if (jo) S.standAct(jo, 'punch', { dx: -22, z: 0, dur: .3 });
    S.impact('blue'); S.sfx('punch', { seed: 2 }); S.shake(4, .35);
    S.fx('hit_spark', { x: shark.x + 6, y: 150, size: 18 }); S.fx('water_splash', { x: shark.x, y: 154, size: 1.1 });
    S.sfxText('ドゴォ', { x: Math.round(shark.x * 2), y: 250 });
    await S.animate(.6, k => { shark.x += 4; shark.y = 160 - Math.sin(k * Math.PI) * 60; shark.under = .45 + .55 * Math.sin(k * Math.PI); shark.wl = 6 + Math.sin(k * Math.PI) * 30; });
    shark.hidden = true;
    S.sfx('splash'); S.fx('water_splash', { x: 300, y: 150, size: .7 });
    if (jo) S.recall(jo);
    await linesTop(S, [['jotaro', '……抓紧。']]);
    await S.fadeOut(.4);
    dropLive('anne_swim', 'shark_swim');
    if (jo) S.unpose(jo);
  }
  async function anneJoins(S) {
    // 回到甲板：安妮湿淋淋地站在承太郎旁边
    setupYacht();
    const [ox] = Y('overboard');
    await S.setStage('boat_ch2', { x: ox + 10, y: 160, fade: false, music: 'daily' });
    calmStands();
    seaAmbient(S, .3); gullsOn();
    S.state('tarp', 1);
    crew.forEach((cid, i) => { if (cid !== 'jotaro') place(S, cid, ox - 90 + i * 22, 152 + (i % 2) * 8, 1); });
    place(S, 'jotaro', ox + 10, 160, 1);
    const anne = anneAt(S, ox + 36, 158, { facing: -1 });
    await S.fadeIn(.4);
    await lines(S, [['polnareff', '这小子……喂，等等。你该不会是——女孩子？！', 'shock']]);
    S.pose(anne, 'angry');
    await sayAnne(S, '看什么看！色狼！', { expr: 'angry' });
    await lines(S, [['polnareff', '色、色狼？！', 'shock']]);
    S.unpose(anne);
    await sayAnne(S, '……谁要你们救。我要去新加坡，找我爸爸。');
    await lines(S, [['joseph', '一个人偷渡去找爸爸？……好吧。到新加坡之前，你跟着我们。'],
      ['avdol', '到了新加坡，SPW 的人会帮她联系家人。']]);
    F().anneNamed = true;
    anne.name = '安妮'; anne.label = '安妮';
    await sayAnne(S, '……安妮。我叫安妮。');
    await sayAnne(S, '喂，戴帽子的。……谢、谢谢你。');
    await lines(S, [['jotaro', '……吵死了。']]);
    // 船长过来看了一眼，点了根烟，抽两口又掐灭在甲板上（烟头 = 线索 1）
    const cap = S.actor('captain');
    const [cx, cy] = Y('captain');
    if (cap) {
      await S.walk(cap, ox + 70, 156, { speed: 80 }); cap.facing = -1;
      await sayCap(S, '又出什么事了？……偷渡的？关进船舱！');
      await lines(S, [['joseph', '这孩子我们来照顾。船长，不用你操心。']]);
      await sayCap(S, '……哼。随便你们。');
      await S.walk(cap, cx, cy, { speed: 70 }); cap.facing = -1;
      S.emote(cap, '…', 1.2); snd('lighter', 'fire', { vol: .6 }, { vol: .12, rate: 2.2 });
      await S.wait(1.0);
      F().cigDropped = true;
      S.sfx('footstep0', { vol: .5 });
    }
    F().anneJoined = true;
    await lines(S, [['kakyoin', '承太郎，你也觉得那个船长有点怪？'], ['jotaro', '……他说甲板上禁止吸烟。']]);
    follow();
    anneFollow(S);
  }

  // ---------------------------------------------------------------- 对质：选那句谎话
  async function confront(S) {
    calmStands();
    const cap = S.actor('captain');
    if (S.player.cid !== 'jotaro') await S.say(S.player.cid, '承太郎，交给你了。');
    await lines(S, [['jotaro', '你真的是坦尼尔船长？']]);
    await sayCap(S, '当然。SPW 审核过的，你们的乔斯达先生也看过我的证件。');
    for (;;) {
      const n = await S.choice(['抽烟的人一说谎，鼻子上的血管就会浮起来。', '你身上有一股海水的腥味。', '你的帽子戴反了。'], '承太郎要说哪一句？');
      if (n === 0) break;
      if (n === 1) { await sayCap(S, '我在海上跑了二十年，身上当然有海水味。小鬼，别乱说。'); continue; }
      if (cap) S.emote(cap, '？', .8);
      await sayCap(S, '……（摸了摸帽檐）没有反。别耍我，小鬼。');
      await lines(S, [['polnareff', '噗。']]);
    }
    await lines(S, [['jotaro', '抽烟的人一说谎，鼻子上的血管就会浮起来。']]);
    S.sfx('heartbeat');
    // 〔特写·头像×4〕大家下意识去摸鼻子——船长也摸了
    await T.closeup4(S, { heads: [{ cid: 'polnareff', expr: 'shock' }, { cid: 'joseph', expr: 'shock' }], dur: 1.0 });
    await lines(S, [['polnareff', '（摸鼻子）我、我又不抽烟！'], ['joseph', '……我也不抽。']]);
    await T.closeup4(S, { heads: [{ cid: 'fake_tennille', expr: 'normal' }], dur: 1.3, sfx: 'sting_reveal' });
    await lines(S, [['jotaro', '……骗你的。不过——你摸了鼻子。'], ['jotaro', '“我是坦尼尔船长”。刚才那句，是谎话。']]);
    F().captainCaught = true;
    if (cap) { cap.name = '冒牌坦尼尔船长'; S.pose(cap, 'reveal'); }
    await sayCap(S, '……哼。哈哈哈！小鬼，眼睛倒是挺尖。', { expr: 'reveal' });
    await lines(S, [['avdol', '真正的坦尼尔船长在哪里？']]);
    await sayCap(S, '谁知道呢？也许正绑在香港的哪个仓库里睡大觉吧。', { expr: 'reveal' });
    await sayCap(S, 'DIO 大人早就算到你们会坐船——这片海，就是你们的坟墓！', { expr: 'reveal' });
    await hostage(S);
  }
  async function hostage(S) {
    const cap = S.actor('captain'), anne = S.actor('anne');
    S.music('tension');
    if (cap && anne) {
      // 船长扑到安妮身边抓住她：安妮跟队时可能在地图边上（船长原来只往她右边 18 px 走，碰到地图边界就停在半路，
      //   人质那段两人隔着六十多像素——2026-10-10 整章自动测试的截图）。先让安妮站进来一点，船长从他那一侧扑过去
      anne.follow = null; S.unpose(cap);
      const ax = G.clamp(anne.x, 90, 540);
      if (Math.abs(ax - anne.x) > 1) await S.walk(anne, ax, anne.y, { speed: 100 });
      const side = cap.x >= anne.x ? 1 : -1;
      await S.walk(cap, anne.x + side * 18, anne.y + 1, { speed: 170 });
      cap.x = anne.x + side * 18; cap.y = anne.y + 1;
      cap.facing = -side; anne.facing = side;
      S.pose(cap, 'grab'); S.pose(anne, 'shock');
      S.sfx('whoosh'); S.shake(1, .2);
      // 抓住以后拖着她退到人群外面一块空甲板上（原来就地抓：安妮跟在队尾，船长被前排的波鲁纳雷夫整个挡住），大家转过来面对他
      const xs = crew.map(cid => S.actor(cid)).filter(Boolean).map(a => a.x);
      const lo = Math.min(...xs), hi = Math.max(...xs);
      const spot = lo - 70 >= 70 ? lo - 56 : Math.min(570, hi + 56), dir = spot < lo ? -1 : 1;
      S.camera(anne);
      await S.wait(.3);
      S.unpose(cap); S.unpose(anne);
      await Promise.all([S.walk(cap, spot + dir * 12, anne.y, { speed: 110 }), S.walk(anne, spot - dir * 4, anne.y, { speed: 110, anim: 'shock' })]);
      cap.facing = -dir; anne.facing = -dir;
      S.pose(cap, 'grab'); S.pose(anne, 'shock');
      for (const cid of crew) { const a = S.actor(cid); if (a) { a.follow = null; a.facing = dir; } }
    }
    await sayAnne(S, '放开我——！');
    await sayCap(S, '别过来！再往前一步，这丫头就去喂鲨鱼！', { expr: 'reveal' });
    for (;;) {
      if (await S.mash({ need: 8, time: 1.6, decay: 0, label: '白金之星！夺回安妮——连按 J', y: 16 })) break;
      await lines(S, [['jotaro', '……放开她。']]);
    }
    const jo = S.actor('jotaro');
    if (jo) { S.summon(jo, { dur: .12, rise: 4 }); S.standAct(jo, 'punch', { dx: 20, dur: .3 }); }
    S.sfx('punch'); S.impact('purple'); S.sfxText('ORA!', cap || 'player');
    if (cap) { S.unpose(cap); S.act(cap, 'hurt'); }
    if (anne) {
      S.unpose(anne);
      const ka = S.actor('kakyoin');
      const tx = ka ? ka.x + 16 : anne.x - 60;
      S.fx('tendrils', { pts: [[ka ? ka.x : tx, (ka ? ka.y : 156) - 20], [(tx + anne.x) / 2, anne.y - 40], [anne.x, anne.y - 24]], colour: '#50e890', grow: .25, wiggle: 1 }, { life: .9 });
      S.sfx('hiero_tentacle');
      await S.arc(anne, tx, 158, 26, .5);
    }
    await lines(S, [['kakyoin', '我接住她了！']]);
    if (jo) S.recall(jo);
    // 冒牌船长翻过栏杆跳进海里；海里伸出一只蓝色的手，抓住承太郎的脚踝
    const [ox, oy] = Y('overboard');
    if (cap) {
      cap.talk = null;
      await sayCap(S, '……在水里，没有人赢得了我的『暗蓝之月』！', { expr: 'reveal' });
      S.unpose(cap); S.camera(cap);
      await S.walk(cap, ox, oy + 4, { speed: 150 });
      await S.arc(cap, ox + 6, oy - 6, 24, .3); cap.visible = false;
      S.sfx('splash'); S.fx('water_splash', { x: ox + 8, y: oy - 14, size: .8 });
    }
    if (jo) {
      jo.follow = null; S.camera(jo);
      await S.walk(jo, ox - 6, oy + 6, { speed: 110 });
      jo.facing = 1;
      S.sfx('water_gush'); S.shake(3, .3);
      S.fx('water_splash', { x: ox + 6, y: oy - 10, size: .6 });
      await lines(S, [['jotaro', '……！？']]);
      S.sfxText('ガシッ', jo);
      await S.arc(jo, ox + 6, oy - 6, 16, .35); jo.visible = false;
      S.sfx('splash'); S.fx('water_splash', { x: ox + 8, y: oy - 14, size: 1 });
    }
    await lines(S, [['joseph', '承太郎被拖下去了！', 'shock'], ['avdol', '水里是对方的地盘……我们的替身够不着！']]);
    S.camera(null);
  }

  // ---------------------------------------------------------------- 打完暗蓝之月：炸弹、救生艇、爆炸
  async function afterDarkMoon(S) {
    calmStands();
    setupYacht();
    const [ox] = Y('overboard');
    await S.setStage('boat_ch2', { x: ox - 10, y: 158, fade: true, music: null });
    seaAmbient(S, .3);
    S.state('tarp', 1);
    crew.forEach((cid, i) => place(S, cid, ox - 130 + i * 24, 152 + (i % 2) * 8, 1));
    const jo = place(S, 'jotaro', ox - 14, 160, 1);
    anneAt(S, ox - 160, 160, { facing: 1 });
    const cap = S.spawn('fake_tennille', ox + 24, 160, { id: 'captain_down', team: 'npc', name: '冒牌坦尼尔船长' });
    S.pose(cap, 'down');
    await lines(S, [['kakyoin', '承太郎！……法皇把你们俩一起捞上来了。'], ['polnareff', '这家伙还在喘气。']]);
    S.unpose(cap); cap.facing = -1;
    await sayCap(S, '可、可恶……我的暗蓝之月……', { expr: 'reveal' });
    if (jo) { S.summon(jo, { dur: .12, rise: 4 }); S.standAct(jo, 'punch', { dx: 20, dur: .3 }); }
    S.impact('purple'); S.sfx('punch', { seed: 1 }); S.shake(3, .3); S.sfxText('ORA!', cap);
    await S.arc(cap, cap.x + 26, 160, 10, .35); S.pose(cap, 'down');
    if (jo) S.recall(jo);
    S.nameCard('fake_tennille');
    await S.wait(1.6);
    await S.title('saiki');
    // 舱底的滴答声越来越快
    for (let i = 0; i < 6; i++) { S.sfx('clock_tick', { rate: 1 + i * .25, vol: .8 }); await S.wait(.32 - i * .04); }
    await lines(S, [['kakyoin', '舱底的箱子……滴答声越来越快了！'], ['joseph', '是炸弹！所有人，上救生艇！', 'shock']]);
    S.sfx('blip'); await S.wait(.15); S.sfx('blip', { rate: 1.3 }); await S.wait(.12); S.sfx('blip', { rate: 1.6 });
    await S.fadeOut(.5);
    // 远景：救生艇划开一段距离，回头看见那艘船炸开（sea_day + 远处小船道具）
    await S.setStage('sea_ch2', { x: 160, y: 168, fade: false, music: null });
    seaAmbient(S, .35);
    for (const cid of crew) { const a = S.actor(cid); if (a) a.visible = false; }
    const yacht = T.prop(S, 'boat', 236, 118, { id: 'far_yacht' });
    seat(S, 116, 178, LIFEBOAT_SEATS);
    T.prop(S, 'lifeboat', 116, 178, { id: 'lifeboat_near' });
    await S.fadeIn(.4);
    await S.wait(.4);
    S.impact(['invert', 'red']); S.sfx('explosion'); S.shake(5, .6);
    S.fx('explosion', { x: 236, y: 110, size: 64 }); S.fx('smoke', { x: 236, y: 106, n: 18, colour: '#605860', life: 2.5, rise: 30 });
    S.sfxText('ドドド', { x: 470, y: 200 });
    if (yacht) yacht.remove = true;
    await S.wait(.8);
    await linesTop(S, [['joseph', 'OH MY GOD……船，没了。', 'shock'], ['polnareff', '乔斯达先生，你坐什么，什么就出事啊。'],
      ['joseph', '这次可不算我的！是那个冒牌船长装的炸弹！'], ['avdol', '冒牌船长绑在船员那条救生艇上了。……到了陆地，交给 SPW。']]);
  }

  // ---------------------------------------------------------------- 雾里漂流一夜 → 货轮出现
  async function drift(S) {
    calmStands();
    await S.setStage('dinghy_ch2', { x: 120, y: 166, fade: true, music: 'sad' });
    seaAmbient(S, .22);
    S.state('ship', 0); S.state('night', 1);
    const [bx, by] = Sf('boat');
    seat(S, bx, by + 16, LIFEBOAT_SEATS);
    T.prop(S, 'lifeboat', bx, by + 16, { id: 'drift_boat' });
    await linesTop(S, [['joseph', 'SPW 已经收到求救信号了。最晚明天，就会有船来接我们。'],
      ['polnareff', '饿死了……有没有人带吃的？']]);
    await S.say('anne', '……我有饼干。（从口袋里掏出一包压扁的饼干）……从厨房拿的。', { name: '安妮', pos: 'top' });
    await linesTop(S, [['polnareff', '原来啃面包的老鼠是你！'], ['polnareff', '你这小鬼，差点害大家喂鲨鱼。']]);
    await S.say('anne', '要你管！你才像只猩猩！', { name: '安妮', pos: 'top' });
    await linesTop(S, [['polnareff', '猩、猩猩？！'], ['kakyoin', '……雾越来越大了。']]);
    await S.say('anne', '喂。……戴帽子的，你叫什么名字？', { name: '安妮', pos: 'top' });
    await linesTop(S, [['jotaro', '……空条承太郎。']]);
    await S.say('anne', '承太郎……我爸爸在新加坡。我已经三年没见过他了。', { name: '安妮', pos: 'top' });
    await linesTop(S, [['jotaro', '……睡吧。']]);
    await S.fadeOut(.8);
    await S.narrate('漫长的一夜过去了。', { pos: 'center', onBlack: true, auto: 1.4 });
    S.state('night', .35);
    S.music('tension');
    await S.fadeIn(.8);
    snd('ship_horn', 'train_horn', { vol: .7 }, { rate: .45, vol: .7 });
    await S.animate(1.2, k => S.state('ship', k < .5 ? 0 : .5));
    await linesTop(S, [['avdol', '……汽笛声？'], ['polnareff', '船！是船！我们得救了！']]);
    S.state('ship', 1); snd('ship_horn', 'train_horn', { vol: 1 }, { rate: .4, vol: .9 }); S.shake(1, .4);
    await linesTop(S, [['joseph', 'SPW 的船？……不对，没听说会派这么大的货轮来。'],
      ['avdol', '舷梯是放下来的。……像是在等我们。'], ['jotaro', '……上去看看。']]);
    await S.fadeOut(.5);
  }

  // ================================================================ 无人货轮（freighter_ch2，freighter_deck，640 宽）
  const FSEARCH = ['galley', 'bridge', 'crane', 'cage', 'log'];
  const searched = () => Object.keys(F().shipInvestigations || {}).filter(k => FSEARCH.includes(k)).length;
  function memberTalkFreighter() {
    T.memberTalk({
      joseph: async S => S.say('joseph', pick('c2joFr', ['这么大的船，一个人都没有？……OH MY GOD，我最讨厌鬼故事了。', 'SPW 的人呢？不对……这艘船，到底是谁的？'])),
      avdol: async S => S.say('avdol', pick('c2avFr', ['这艘船上的生命……很奇怪。到处都有，又到处都没有。', '大家别走散。'])),
      kakyoin: async S => S.say('kakyoin', pick('c2kakFr', ['机器都开着，船却没有人开。……它是怎么动的？', '安妮，跟紧我们。'])),
      polnareff: async S => S.say('polnareff', pick('c2polFr', ['有吃的吗？……厨房！厨房在哪？', '喂喂，这船是不是有点太安静了？'])),
      jotaro: async S => S.say('jotaro', pick('c2joFr2', ['……', '……别乱碰东西。'])),
    });
  }
  // 铁笼的正面铁栏（freighter_deck 导出的 anchors.cage_front：两张图 + depth 144.5）：背景里已经画着整只笼子，
  //   这里再按纵深叠一层铁栏——笼子里的猩猩（脚底 y 140）在铁栏后面，可走带上的人（≥ 146）在铁栏前面。按 state.cage_open 选图
  function cageFront() {
    const cf = bgA('freighter_deck', 'cage_front', null);
    if (!cf || !cf.images) return null;
    return { type: 'custom', id: 'cage_front', x: 0, y: 0, depth: cf.depth || 144.5, draw(g, sx, sy) {
      const st = G.world.stage, im = G.image ? G.image(cf.images[st && st.state && st.state.cage_open ? 1 : 0]) : null;
      if (im && G.ready && G.ready(im)) g.drawImage(im, Math.round((cf.x || 0) + sx), Math.round((cf.y || 0) + sy));
    } };
  }
  function setupFreighter() {
    const st = G.STAGES.freighter_ch2;
    st.props = [cageFront()].filter(Boolean); st.triggers = [];
    const [gx, gy] = Fr('gangway'), [ix, iy] = Fr('cage_inside'), [crx, cry] = Fr('crane');
    st.npcs = [
      T.npc('npc_sailor', 'fsailor_a', gx + 40, gy + 2, { facing: 1, label: '船员', name: '船员', cond: () => !F().pipesMoved,
        talk: async S => saySailor(S, 'fsailor_a', pick('c2fsa', ['有人吗——？……喂，有人吗？', '这船的漆是新的，锈却是旧的。怪了。'])) }),
      T.npc('npc_sailor', 'fsailor_b', gx + 70, gy + 10, { facing: 1, label: '船员', name: '船员', cond: () => !F().pipesMoved,
        talk: async S => saySailor(S, 'fsailor_b', pick('c2fsb', F().sailorGone
          ? ['老张不见了……就在吊车底下，一眨眼的工夫。', '我、我想回救生艇上去……']
          : ['我跟船跑了十五年，从没见过开着引擎、一个人都没有的船。', '吊车那边是老张。他说要去找船员名单。'])) }),
      T.npc('npc_sailor', 'fsailor_c', crx + 6, cry + 8, { facing: -1, label: '船员', name: '船员', cond: () => !F().sailorGone,
        talk: async S => saySailor(S, 'fsailor_c', pick('c2fsc', ['我去吊车的操纵室看看，说不定能找到船员名单。', '这吊车……刚才是不是自己动了一下？'])) }),
      // 笼子里的猩猩：翻着一张报纸。普通人看不见替身——它看得见（亮替身时它的眼睛跟着转）
      T.npc('strength', 'ape', ix, iy, { facing: -1, label: '猩猩', name: '猩猩', anim: 'idle', shadow: false, cond: () => !F().pipesMoved,
        talk: async (S, a, p) => { S.emote(a, '…', 1.0); ape(.5); await S.say(null, T.by(p, { polnareff: '（猩猩咧开嘴，冲波鲁纳雷夫笑了一下。）', _: '（猩猩把报纸翻了一页。）' })); },
        onStand: async (S, a, p) => {
          S.emote(a, '！', .8); ape(.6);
          await S.say(null, '（猩猩的眼睛……跟着替身转了一圈。）');
          F().apeSaw = true;
          await S.say(p.cid, T.by(p, { polnareff: '喂……这只猩猩，看得见替身？！', avdol: '……普通的动物，是看不见替身的。', kakyoin: '它看见法皇了。……这只猩猩，不简单。', joseph: 'OH MY GOD，猩猩看得见我的藤蔓？', _: '……它看得见。' }));
        } }),
    ];
    const say = (S, p, text) => S.say(p.cid, text);
    const mark = async (S, id) => { J.unique('shipInvestigations', id); await freighterEvents(S); };
    const photoImg = G.D && G.D.props && G.D.props.photo_ape_helm ? G.D.props.photo_ape_helm.image : null;
    st.hotspots = [
      hot('galley', Fr('galley')[0], Fr('galley')[1], '厨房', ['detail'],
        async (S, h, p) => { await sayBy(S, p, { polnareff: '吃的！……锅里的汤还是热的。可是一个人都没有。', _: '厨房。锅里的汤还是热的。' }); await mark(S, 'galley'); },
        async (S, h, p) => { await say(S, p, '饭菜还冒着热气。……人刚走不久。可是甲板上没有一个脚印。'); await mark(S, 'galley'); }, { ly: 110 }),
      hot('bridge', Fr('bridge')[0], Fr('bridge')[1], '舰桥', ['life'],
        async (S, h, p) => { await sayBy(S, p, { joseph: '舰桥。仪表都亮着，舵……自己在转！', _: '舰桥。仪表都亮着，舵自己在转。' }); await mark(S, 'bridge'); },
        async (S, h, p) => { await lines(S, [['avdol', '舰桥里一个人也没有……可是……'], ['avdol', '……整艘船，都在呼吸。']]); await mark(S, 'bridge'); }, { ly: 96 }),
      hot('crane', crx, cry, '吊车', ['detail', 'reach'],
        async (S, h, p) => { await say(S, p, '吊车。操纵室里没人，钥匙还插着。'); await mark(S, 'crane'); },
        async (S, h, p) => { await say(S, p, T.by(p, { kakyoin: '触须够得着操纵室……操纵杆是温的。', _: '……吊臂上的钢缆，刚刚还在晃。' })); await mark(S, 'crane'); }, { ly: 70 }),
      hot('cage', Fr('cage')[0], Fr('cage')[1], '笼子', ['detail', 'life'],
        async (S, h, p) => { await sayBy(S, p, { polnareff: '一只猩猩？你好啊，大个子～', joseph: '货船上运猩猩？……看起来倒挺老实。', _: '笼子里关着一只猩猩。在看报纸。' }); await mark(S, 'cage'); },
        async (S, h, p) => { await say(S, p, T.by(p, { jotaro: '……它在看报纸。还会翻页。', avdol: '这只猩猩的气息……和这艘船连在一起。', _: '……这只猩猩不对劲。' })); await mark(S, 'cage'); }, { ly: 110 }),
      hot('log', Fr('log')[0], Fr('log')[1], '航海日志', ['nensha'],
        async (S, h, p) => { await sayBy(S, p, { joseph: '航海日志……最后一页是空的。墨水还没干。', _: '航海日志。最后一页是空的，墨水还没干。' }); await mark(S, 'log'); },
        async (S, h, p) => { await lines(S, [['joseph', '照片上……是一只猩猩在掌舵？！', 'shock'], ['joseph', 'OH MY GOD！开这艘船的，是那只猩猩！']]); F().apeSaw = true; await mark(S, 'log'); },
        Object.assign({ ly: 110 }, photoImg ? { photo: { image: photoImg } } : {})),
      hot('hold_door', Fr('hold_door')[0], Fr('hold_door')[1], '货舱口', [],
        async (S, h, p) => say(S, p, searched() >= 2 ? '下面黑漆漆的。……有什么东西在下面动。' : '通往货舱的楼梯。下面黑漆漆的。'), null, { ly: 110 }),
    ];
    st.onLook = async (S, p) => sayBy(S, p, {
      avdol: '……到处都是生命的气息。墙里、地板下面、管子里。', jotaro: '……太安静了。', kakyoin: '触须探不到船员。', joseph: '这里没有相机……', polnareff: 'Voilà～……没人鼓掌。',
    });
  }
  // 调查到第 2 处：吊车自己转了一下，吊车下面的船员不见了（只剩一顶帽子）；第 3 处：管道动了 → 掉进货舱
  async function freighterEvents(S) {
    const n = searched();
    if (n >= 2 && !F().sailorGone) {
      F().sailorGone = true;
      calmStands();
      const sc = S.actor('fsailor_c');
      S.sfx('metal_scrape', { rate: .7 }); S.state('crane', 1);
      await S.wait(.5);
      snd('creak', 'door', { vol: .8 }, { rate: .5, vol: .7 });
      await saySailor(S, 'fsailor_c', '哇——！', { pos: 'top' });
      S.flash(.1, .5, '#ffffff');
      if (sc) { T.prop(S, 'hat', sc.x, sc.y + 1, { id: 'sailor_hat' }); sc.remove = true; }
      await S.wait(.4);
      await saySailor(S, 'fsailor_b', '老、老张呢？刚才还在吊车下面！');
      await lines(S, [['avdol', '……他还活着。气息……在这艘船的下面。'], ['jotaro', '……大家别离开彼此的视线。']]);
    }
    if (n >= 3 && !F().pipesMoved) await pipesGrab(S);
  }
  async function pipesGrab(S) {
    calmStands();
    S.music('ominous');
    S.sfx('metal_crunch', { rate: .7 }); S.shake(2, .6);
    await lines(S, [['kakyoin', '……墙上的管子，自己在动！'], ['avdol', '这艘船……就是替身！']]);
    S.sfxText('メキメキッ', { x: 320, y: 160 });
    S.sfx('metal_crunch'); S.shake(4, .5); S.flash(.12, .6, '#ffffff');
    // 管道把大家缠住：承太郎脚下的甲板裂开，掉进货舱
    for (const cid of crew) { const a = S.actor(cid); if (a) { a.follow = null; S.pose(a, 'hurt'); } }
    const an = S.actor('anne'); if (an) { an.follow = null; S.pose(an, 'shock'); }
    for (const id of ['fsailor_a', 'fsailor_b']) { const a = S.actor(id); if (a) { S.emote(a, '！', .6); a.remove = true; } }
    await lines(S, [['joseph', '我的藤蔓都扯不断……！', 'shock'], ['polnareff', '承太郎——！脚下！']]);
    const jo = S.actor('jotaro');
    if (jo) { S.sfx('crash'); S.fx('crack', { x: jo.x, y: jo.y - 2, size: 18 }, { life: 1 }); await S.wait(.25); S.sfx('whoosh'); await S.animate(.35, k => { jo.z = -k * 40; jo.alpha = 1 - k; }); jo.visible = false; jo.alpha = 1; jo.z = 0; }
    F().pipesMoved = true;
    await S.fadeOut(.4);
    S.sfx('thud');
  }

  // ---------------------------------------------------------------- 货舱：猩猩现身 → 第 4 战
  async function holdIntro(S) {
    calmStands();
    await S.setStage('hold_ch2', { x: 120, y: 162, fade: false, music: null });
    for (const cid of crew) { const a = S.actor(cid); if (a) { S.unpose(a); a.visible = cid === 'jotaro'; a.follow = null; } }
    const jo = place(S, 'jotaro', 120, 162, 1);
    if (jo) S.pose(jo, 'down');
    await S.fadeIn(.5);
    await S.wait(.4);
    if (jo) S.unpose(jo);
    await lines(S, [['jotaro', '……货舱。']]);
    const apeA = S.spawn('strength', 520, 160, { id: 'ape_intro', team: 'npc', name: '猩猩' });
    apeA.facing = -1; apeA.alpha = 0;
    ape(.8);
    await S.animate(.6, k => { apeA.alpha = k; });
    S.camera(apeA); await S.wait(.6);
    const men = S.menacing({ x: 470, y: 130, dur: 1.6 });
    await lines(S, [['jotaro', '……猩猩。'], ['jotaro', '替身使者是你吗。']]);
    ape(1); S.shake(2, .3); S.emote(apeA, '！', .8);
    await S.say(null, '（猩猩咧开嘴，露出一整排牙齿。整个货舱的墙壁，跟着它一起“笑”了。）', { pos: 'top' });
    if (men && men.stop) men.stop();
    S.camera(null);
    apeA.remove = true;
  }

  // ---------------------------------------------------------------- 结尾：货轮缩回生锈的小破船
  async function ending(S) {
    calmStands();
    // 欧拉连打把猩猩打出舱外 → 一阵剧烈的摇晃 → 甲板、墙壁、管道一起缩小
    S.impact(['invert', 'purple']); S.shake(6, .8); S.sfx('metal_crunch', { rate: .5 });
    await S.title('saiki');
    await S.fadeOut(.5);
    await S.setStage('sea_ch2', { x: 160, y: 170, fade: false, music: null });
    seaAmbient(S, .3);
    for (const cid of crew) { const a = S.actor(cid); if (a) { a.visible = false; a.follow = null; S.unpose(a); } }
    const big = T.prop(S, 'rusty_freighter', 168, 150, { id: 'freighter_far', alt: 'prop:ship' });
    await S.fadeIn(.4);
    S.sfx('metal_crunch', { rate: .4 }); S.shake(3, 1);
    if (big) await S.animate(1.4, k => { big.scale = 1 - k * .8; big.alpha = 1 - k * .9; big.y = 150 + k * 18; });
    if (big) big.remove = true;
    seat(S, 162, 179, RUSTY_SEATS, 8);
    T.prop(S, 'rusty_boat', 162, 179, { id: 'rusty_boat' });
    S.sfx('splash');
    await linesTop(S, [['polnareff', '船……变小了？', 'shock'], ['joseph', 'OH MY GOD! 我们刚才站在一只猩猩的替身上？！', 'shock'],
      ['avdol', '本体被打倒，替身就撑不住那么大的样子了。']]);
    // 船员从小破船的船舱里钻出来——都没事
    //   小破船船尾的驾驶室占 x 105–132（rusty_boat pivot −57…−30）：两个船员从驾驶室顶上的舱口一个个钻出来，站在顶上（z 26 = 顶棚高）
    for (const [id, x] of [['esailor_a', 112], ['esailor_c', 126]]) {
      const s = S.spawn('npc_sailor', x, 171, { id, team: 'npc', name: '船员', shadow: false });
      s.facing = 1; s.z = 0; S.sfx('door', { vol: .4, rate: 1.4 });
      await S.animate(.35, k => { s.z = 26 * k; });
    }
    await S.say('npc_sailor', '我们被关在一个很黑的地方……醒过来就在这儿了。幸好都没事。', { name: '船员', pos: 'top', actor: S.actor('esailor_a') });
    await S.say('npc_sailor', '……我的帽子呢？我的帽子掉哪儿去了？', { name: '船员（老张）', pos: 'top', actor: S.actor('esailor_c') });
    await linesTop(S, [['kakyoin', '被替身吞进去的人，都放出来了。'], ['jotaro', '……那只猩猩呢。'], ['polnareff', '晕在船尾。……让 SPW 送它去动物园吧。']]);
    const ship = T.prop(S, 'ship', 330, 128, { id: 'spw_ship' });
    snd('ship_horn', 'train_horn', { vol: .5, rate: 1.3 }, { rate: .7, vol: .6 });
    if (ship) await S.animate(1.2, k => { ship.x = 330 - k * 70; });
    await linesTop(S, [['joseph', 'SPW 的船来了！……这回总该能到新加坡了。']]);
    await S.say('anne', '……新加坡。爸爸，我来了。', { name: '安妮', pos: 'top' });
    await linesTop(S, [['jotaro', '……呀嘞呀嘞daze。']]);
    S.sfxText('呀嘞呀嘞daze', S.actor('jotaro') || 'player');
    await S.fadeOut(.5);
    await S.setStage('map_ch2', { x: 100, y: 160, fade: false, music: 'travel' });
    await S.fadeIn(.3);
    await S.route(['香港', '新加坡'], { vehicle: 'ship', day: 5, left: 46, history: ['东京', '香港'] });
    await S.narrate('第五天，一行人终于踏上了新加坡的土地。', { pos: 'center' });
    await S.tbc(); S.mark('ch2_tbc');
  }

  // ================================================================ 章节流程
  G.STORY.ch2 = async S => {
    T.resetCounters();
    S.party(crew, { leader: 'jotaro' });
    for (const k of ['anneFound', 'anneJoined', 'anneNamed', 'anneLeft', 'captainClues', 'captainLied', 'captainCaught', 'cigDropped',
      'shipInvestigations', 'sailorGone', 'pipesMoved', 'apeSaw']) delete F()[k];
    F().anneLeft = false;
    await S.chapterCard('ch2');
    await S.setStage('map_ch2', { x: 100, y: 160, music: 'travel' });
    await S.run(async s => {
      await s.route(['香港', '新加坡'], { vehicle: 'ship', day: 2, left: 49, cut: .6, history: ['东京', '香港'] });
      await s.narrate('为了不连累别的乘客，一行人改走海路。SPW 财团包下一艘船，驶向新加坡。', { pos: 'center' });
    });
    // 甲板：开场 → 自由（找偷渡者）
    setupYacht();
    await S.setStage('boat_ch2', { x: 140, y: 156, music: 'daily' });
    seaAmbient(S, .3); gullsOn();
    S.state('tarp', 0);
    S.location('south_sea');
    await S.run(boatIntro);
    memberTalkYacht();
    S.hint('在甲板上逛逛：E 搭话 / 调查，U 替身调查，Q 换队长。', 8);
    const [lx, ly] = Y('lifeboat');
    T.goal(S, { x: lx, y: ly, h: 52, label: '救生艇', delay: 40, every: 20, done: () => !!F().anneFound, text: '救生艇的帆布……好像在动。去看看。' });
    const t0 = G.clk.world;
    await S.until(() => (F().anneFound && !S.busy) || (!S.busy && G.world.free && G.clk.world - t0 > 90));
    // 卡住太久（90 s）：替玩家做完——换成阿布德尔、走到救生艇前、探一下（规划 §1.3 第 2 条）
    if (!F().anneFound) await S.run(async s => {
      s.setLeader('avdol', { force: true });
      await s.walk(s.player, lx + 10, ly + 4, { speed: 90 });
      await G.LOOK.avdol.run(s, s.player, { x: lx, y: ly - 30 });
      await s.say('avdol', '帆布下面……有一个很小的生命，在发抖。');
      F().anneFound = true;
    });
    await S.run(anneReveal);
    await S.run(anneJoins);
    memberTalkClues();
    S.hint('那个船长有点不对劲。查一查甲板上的东西（烟头、舱盖），再去找他谈谈。', 10);
    const [cx, cy] = Y('captain');
    T.goal(S, { x: cx, y: cy, h: 54, label: '船长', delay: 20, every: 20, when: () => clueN() >= 2, done: () => !!F().captainCaught, text: '线索够了。去找船长对质。' });
    T.goal(S, { x: Y('hatch')[0], y: Y('hatch')[1], h: 30, label: '舱盖', delay: 45, every: 25, done: () => hasClue('hatch'), text: '舱盖下面好像有声音。花京院的触须能钻进去（Q 换队长，U）。' });
    const t1 = G.clk.world;
    let helped = false;
    await S.until(() => {
      if (F().captainCaught && !S.busy) return true;
      // 卡住太久（80 s）：替玩家查完剩下的线索
      if (!helped && !S.busy && G.world.free && G.clk.world - t1 > 80 && clueN() < 2) {
        helped = true;
        S.run(async s => {
          if (!hasClue('hatch')) {
            s.setLeader('kakyoin', { force: true });
            await s.walk(s.player, Y('hatch')[0], Y('hatch')[1] + 4, { speed: 90 });
            await G.LOOK.kakyoin.run(s, s.player, { x: Y('hatch')[0], y: Y('hatch')[1] });
            J.unique('captainClues', 'hatch'); await s.say('kakyoin', '舱底有个绑着电线的箱子……在滴答响。');
          }
          if (!hasClue('cigarette')) {
            s.setLeader('jotaro', { force: true });
            await s.walk(s.player, Y('cigarette')[0] - 8, 156, { speed: 90 });
            J.unique('captainClues', 'cigarette'); await s.say('jotaro', '烟头的滤嘴上有很深的牙印。……船长。');
          }
          s.hint('线索够了。去找船长对质。', 6);
        }).catch(G.cancelIgnore);
      }
      return false;
    });
    // 第 3 战 → 炸船 → 漂流
    await S.run(async s => {
      s.standCard('darkbluemoon');
      await s.wait(1.0);
      await s.setStage('underwater_ch2', { x: 150, y: 168, fade: true, music: 'battle' });
      await s.fight(G.BOSS25.darkmoon());
      await afterDarkMoon(s);
      await drift(s);
    });
    // 货轮：自由（三处调查）
    setupFreighter();
    await S.setStage('freighter_ch2', { x: Fr('gangway')[0] + 20, y: 156, music: 'tension' });
    seaAmbient(S, .12); creaksOn();
    S.state('crane', 0);
    anneFollow(S);
    memberTalkFreighter();
    S.hint('空无一人的货轮。调查船上的东西（至少三处）。', 10);
    T.goal(S, { x: Fr('galley')[0], y: Fr('galley')[1], h: 50, label: '厨房', delay: 35, every: 25, done: () => searched() >= 1, text: '先看看厨房。' });
    T.goal(S, { x: Fr('cage')[0], y: Fr('cage')[1], h: 56, label: '笼子', delay: 40, every: 25, when: () => searched() >= 1, done: () => searched() >= 2, text: '甲板中间有个铁笼子。' });
    T.goal(S, { x: Fr('bridge')[0], y: Fr('bridge')[1], h: 60, label: '舰桥', delay: 40, every: 25, when: () => searched() >= 2, done: () => searched() >= 3, text: '去舰桥看看。' });
    await S.until(() => F().pipesMoved && !S.busy);
    // 第 4 战 → 结尾
    await S.run(async s => {
      await holdIntro(s);
      s.standCard('strength');
      await s.wait(1.0);
      await s.fight(G.BOSS25.strength());
      await ending(s);
    });
  };

  // 开发调参入口（只给 tools\dev\full\dev_fight.py 用，正常游戏不调用）：直接开打这一章的某一战，战斗配置和正式剧情是同一份。
  //   验收一律跑整章（test_mid_early.py），这个入口的结果不当通关证据
  G.DEV = G.DEV || {};
  G.DEV.ch2Darkmoon = async S => { S.party(crew, { leader: 'jotaro' }); await S.setStage('underwater_ch2', { x: 150, y: 168, music: 'battle' }); await S.run(async s => { await s.fight(G.BOSS25.darkmoon()); }); };
  G.DEV.ch2Strength = async S => { S.party(crew, { leader: 'jotaro' }); await S.setStage('hold_ch2', { x: 100, y: 160, music: 'tension' }); await S.run(async s => { await s.fight(G.BOSS25.strength()); }); };
  // 第 4 战的隔舱壁画在货舱地图上（地图定义在 stages_ch02_05.js；进图时复制，draw 只读 W.fight）
  if (G.STAGES.hold_ch2) G.STAGES.hold_ch2.props = [bulkheads];
})();
