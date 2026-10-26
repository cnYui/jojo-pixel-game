// 第7章　红海 / 许愿与大嘴（规划 §6.6；原著 174–182 话，第 22–29 天）
//   2026-10-18 按体验版精度重写（用户：“继续把整个 jojo 游戏做完……场景画面精细一些，玩法也多做一些”）。节拍表：docs\章节素材调研\ch7_红海_节拍表.md
//   机关沿用初版：审判（许愿泥偶 + 动摇槽撑 45 s → 阿布德尔归来、打碎神灯）、女教皇（潜艇里 12 件金属找“眨眼”的伪装 + 漏水倒计时 →
//   海底巨嘴：上排牙咬下来时精准格挡顶住再打碎、下排牙 J3 / 连打）；这一版补自由走动（小岛、潜艇）、阿布德尔归来的过场、
//   老人的钓鱼小游戏、三件纪念品，金属物件 / 牙位都读重画后背景的 anchors（obj_* / upper / lower）。
//
//   流程：世界地图 → 红海小岛（自由走动：岛民老人、钓鱼、螃蟹、小屋；波鲁纳雷夫擦神灯）→ 许三个愿望之一 → 第 14 战阶段 1（撑 45 s）
//   → 小屋里喷出火焰：阿布德尔归来（特写）→ 阶段 2（打碎神灯、打本体）→ 卡梅欧「再起不能」→ 假死的解释（喜剧）→ 阿布德尔归队
//   → 潜艇（第 25 天，自由走动：先看熟 12 件金属）→ 乔瑟夫的咖啡杯咬掉义手 → 第 15 战段 1 → 漏水沉没（坠毁章 4 → 5）→ 潜水服
//   → 段 2 海底巨嘴 → 被吐到埃及海岸，米朵拉的背影 → 地图（潜艇开到 42% 沉没，第 29 天）→ 埃及 → TBC
//
//   台词都是新写的（规划 §1.4）。克制处理：乔瑟夫被咬掉的是义手（冒火花，不是真手）；米朵拉只画背影。
'use strict';
(function () {
  const G = window.G, M = G.MID, T = G.TPL, W = G.world, I = G.input, px = G.px, F = () => G.flags, X = G.EXTRA;
  G.TRIAL_SRC = G.TRIAL_SRC || {};
  const pick = (key, arr) => arr[(T.count(key) - 1) % arr.length];
  const sayBy = (S, p, map) => S.say(p.cid, T.by(p, map));
  const lines = async (S, rows) => { for (const [who, text, expr] of rows) await S.say(who, text, expr ? { expr } : {}); };
  const hasSnd = n => !!(G.audio && G.audio.has && G.audio.has(n));
  const snd = (name, alt, o = {}) => { if (hasSnd(name)) G.audio.sfx(name, o); else if (alt) G.audio.sfx(alt, o); };
  const amb = (S, name, alt, vol) => { if (hasSnd(name)) S.ambient(name, vol); else if (alt) S.ambient(alt, vol * .6); };
  const calmStands = () => { for (const a of (G.party && G.party.members) || []) if (a.stand && a.stand.visible && a.stand.mode !== 'recall') a.stand.recall({ sfx: false }); };
  const follow = () => { if (G.party && G.party.rebuildFollow) G.party.rebuildFollow(); };
  function place(S, cid, x, y = 164, facing = 1) {
    const a = S.actor(cid); if (!a) return null;
    a.visible = true; a.follow = null; a.x = x; a.y = y; a.facing = facing; a.alpha = 1; a.scale = 1; a.z = 0; S.unpose(a);
    return a;
  }
  const CREW5 = ['jotaro', 'joseph', 'avdol', 'kakyoin', 'polnareff'];
  // 阿布德尔在第 14 战之前还是“？”（第4章假死）；归来以后正式归队
  function party(S, leader = 'jotaro') {
    if (F().ch7AvdolBack) S.party(CREW5, { leader });
    else { S.party(CREW5, { leader }); G.party.remove('avdol', { look: 'unknown' }); }
    for (const a of G.party.members) a.scale = 1;
  }

  // ---------------------------------------------------------------- 背景锚点（没有就用背景规格里的默认值）
  const bgA = (bg, k, d) => { const b = G.D && G.D.bg && G.D.bg[bg]; const v = b && b.anchors ? b.anchors[k] : null; return v != null ? v : d; };
  const ISd = { arrive: [56, 164], pier: [20, 160], boat: [24, 170], oldman: [140, 160], umbrella: [140, 130], crabs: [[200, 172], [300, 174]], lamp: [244, 166],
    rocks: [320, 158], hut: [400, 150], hut_door: [398, 160], exit: [470, 162] };
  const SBd = { arrive: [40, 164], helm: [70, 160], periscope: [190, 152], chart: [280, 154], galley: [360, 152], bunks: [450, 150], gear: [530, 150], hatch: [610, 156] };
  const MTd = { throat: [24, 152], upper: [[60, 64], [100, 62], [140, 60], [180, 60], [220, 62], [260, 64]],
    lower: [[60, 148], [100, 150], [140, 150], [180, 150], [220, 150], [260, 148]], arrive: [250, 162] };
  const ECd = { arrive: [60, 164], shore: [30, 170], helipad: [200, 162], sign: [124, 150], road: [290, 162], midler: [100, 170] };
  const IS = k => bgA('redsea_island', k, ISd[k]);
  const SB = k => bgA('submarine', k, SBd[k]);
  const MT = k => bgA('seabed_mouth', k, MTd[k]);
  const EC = k => bgA('egypt_coast', k, ECd[k]);
  const footY = (id, y) => { const st = G.STAGES[id]; return G.clamp(y, st.yMin + 2, st.yMax - 2); };

  // 潜艇的 12 件金属（女教皇会伪装成其中一件）：背景导出 obj_<名字>（物件中心，在墙上 / 架子上）；旧背景没有就摆在地上
  const METAL = ['pressure_gauge', 'valve', 'wrench', 'metal_cup', 'razor', 'binoculars', 'pipe_elbow', 'radio', 'diving_boot', 'oxygen_tank', 'compass', 'hatch_handle'];
  const LABELS = ['压力表', '阀门', '扳手', '金属杯', '剃刀', '望远镜', '弯管', '收音机', '潜水靴', '氧气瓶', '罗盘', '舱门把手'];
  const NOTES = ['指针稳稳地指着正常范围。', '拧得很紧的阀门。', '一把大号扳手，挂在工具板上。', '乔瑟夫的咖啡杯。……杯沿有点烫。', '刮胡子用的剃刀，刀刃很亮。',
    '黄铜的望远镜，镜片擦得很干净。', '管道的弯头，接缝上一点锈都没有。', '收音机里只有沙沙的杂音。', '一只潜水靴，鞋底是铅做的。', '氧气瓶，压力表显示满瓶。',
    '罗盘的针……一直指着北边。', '舱门的转盘把手。'];
  const metalSpots = () => {
    const b = G.D && G.D.bg && G.D.bg.submarine, a = b && b.anchors;
    if (a && METAL.every(id => a['obj_' + id])) return { wall: true, pts: METAL.map(id => a['obj_' + id]) };
    return { wall: false, pts: METAL.map((id, i) => [36 + i * 50, 164]) };
  };
  // 12 件金属都看过（E 或 U 都算）时（7-08）：花京院在队里就由他说，不在（没这可能）就由队长说；
  //   ch7AllSeen 给第 15 战段 1 的小地图条用——记住了就全亮，不用再靠记忆找
  const metalsAllSeen = s => { for (let i = 0; i < METAL.length; i++) if (!s.flags['metal_seen_' + i]) return false; return true; };
  async function markMetalSeen(s, i) {
    s.flags['metal_seen_' + i] = true;
    if (F().ch7AllSeen || !metalsAllSeen(s)) return;
    F().ch7AllSeen = true;
    const who = G.party.members.some(a => a.cid === 'kakyoin') ? 'kakyoin' : s.player.cid;
    await s.say(who, '……都记住了。哪一件挂在哪里，闭上眼睛也想得起来。');
  }

  // ---------------------------------------------------------------- 纪念品
  X.souvenir({ id: 'ch7_conch', chapter: 'ch7', name: '红海的海螺', desc: '小岛沙滩上捡的。贴着耳朵，能听见海浪……还有一点像灯神的笑声。', hint: '红海小岛的礁石缝里（要伸得进去的替身）' });
  X.souvenir({ id: 'ch7_logbook', chapter: 'ch7', name: '潜艇的航海日志', desc: 'SPW 准备的潜艇上的日志。最后一行是乔瑟夫的字：“咖啡太烫”。', hint: '潜艇的海图桌（开战以前）' });
  X.souvenir({ id: 'ch7_metal_tooth', chapter: 'ch7', name: '金属的牙', desc: '从巨嘴里打下来的一颗牙，敲起来是铁的声音。', hint: '埃及海岸，被吐出来的地方' });

  // ================================================================ 小岛（island_ch7，redsea_island 480 宽）
  //   自由走动：戴斗笠的老人（钓鱼小游戏；乔瑟夫在场时他话说一半就被乔瑟夫打断——伏笔）、螃蟹、礁石、小屋（乔瑟夫 E「这里没什么好看的」；
  //   花京院 U「小屋里有一双眼睛」）；波鲁纳雷夫 E 擦沙滩上的神灯 → 推进（别人 E：「一盏旧油灯。」）
  async function fishing(S) {
    const say = t => S.say('npc_islander', t, { name: '老人', actor: S.actor('islander') });
    if (F().ch7Fished) { await say(pick('c7fish2', ['今天的鱼不爱咬钩。', '钓鱼嘛，钓的是时间。'])); return; }
    await say('……要试试我的鱼竿吗？浮标沉下去的那一下，往上提。');
    const c = await S.choice(['试试', '不用了'], '老人的鱼竿');
    if (c !== 0) { await say('……那就看看海吧。'); return; }
    const catches = [['一只破凉鞋……', 'sting_comedy'], ['一条小丑鱼！……放回去吧。', 'splash'], ['一条大石斑鱼！', 'water_splash']];
    let got = 0;
    for (let r = 0; r < 3; r++) {
      S.sfx('splash', .25);
      const ok = await S.timing({ label: '浮标沉下去了！提竿（J）', zone: [.44, .58 - r * .02], speed: 1.15 + r * .2 });
      if (ok) { got++; S.sfx(catches[Math.min(got, 3) - 1][1], .5); await S.say(null, '钓上来了：' + catches[Math.min(got, 3) - 1][0]); }
      else await S.say(null, '……鱼跑了。');
    }
    F().ch7Fished = true;
    await sayBy(S, S.player, got >= 3
      ? { joseph: '哈哈哈！今晚加餐！', polnareff: 'Magnifique！石斑鱼要清蒸！', kakyoin: '……没想到我还挺擅长这个。', _: '……还行。' }
      : { joseph: '鱼啊，你就不能给我一点面子吗！', _: '……下次。' });
  }
  function setupIsland(st) {
    st.state = Object.assign({}, st.state, { burnt: 0, dusk: 0 });
    const [ox, oy] = IS('oldman'), [hx, hy] = IS('hut_door'), [lx, ly] = IS('lamp'), [rx, ry] = IS('rocks');
    st.npcs = [T.npc('npc_islander', 'islander', ox, footY('island_ch7', oy), { facing: 1, label: '戴斗笠的老人', name: '老人', talk: async S => {
      const p = S.player;
      if (p.cid === 'joseph' || T.count('c7old') > 1) {
        await S.say('npc_islander', '这座岛上只住着我一个……还有一个客人——', { name: '老人', actor: S.actor('islander') });
        if (p.cid === 'joseph') await S.say('joseph', '啊哈哈哈！老人家，天气真好啊！我们是来钓鱼的！');
        else await S.say('joseph', '（远处）老人家！要不要来点饮料！');
      }
      await fishing(S);
    } })];
    st.hotspots = [
      M.hot('crab', IS('crabs')[0][0], '螃蟹', ['detail', 'cut'], '螃蟹横着爬远了。', async (S, h, p) => sayBy(S, p, { polnareff: '螃蟹！……别夹我的手指！', joseph: '红海的螃蟹，肯定好吃。', _: '一只螃蟹横着爬远了。' }), null, footY('island_ch7', IS('crabs')[0][1])),
      M.hot('rocks', rx, '礁石', [], '', async (S, h, p) => sayBy(S, p, { kakyoin: '海水清得能看见底下的珊瑚。', _: '被浪冲得光溜溜的礁石。' }), null, footY('island_ch7', ry + 6)),
      // 海螺改成替身调查（7-02）：礁石缝太窄，只有法皇的触须伸得进去——鼓励换队长用 U 找纪念品
      X.hot('ch7_conch', rx + 22, footY('island_ch7', ry + 10), { look: ['peek'], label: '礁石缝',
        found: s => s.say('kakyoin', '触须伸进礁石缝……摸到一只海螺。') }),
      M.hot('hut', hx, '小屋', ['peek', 'life'], '',
        async (S, h, p) => sayBy(S, p, { joseph: '……这里没什么好看的，走吧走吧！', polnareff: '门半开着……有人吗？', _: '一间晾着渔网的小木屋，窗口黑漆漆的。' }),
        async (S, h, p) => S.say(p.cid, p.cid === 'kakyoin' ? '小屋里……有一双眼睛在看我们。是我看错了吗？' : '……屋里有人的气息。'), footY('island_ch7', hy)),
      M.hot('lamp', lx, '旧油灯', ['cut'], '', async (S, h, p) => {
        if (p.cid !== 'polnareff') { await S.say(p.cid, '一盏旧油灯，半埋在沙里。'); return; }
        S.sfx('metal_scrape'); F().ch7Lamp = true;
      }, async S => { await S.say('polnareff', '剑尖一挑——这盏灯，看起来值点钱！'); F().ch7Lamp = true; }, footY('island_ch7', ly)),
    ];
    st.onLook = async (S, p) => S.say(p.cid, T.by(p, { kakyoin: '……岛上除了老人，好像还有别人。', _: '海风很舒服。' }));
  }
  async function island(S) {
    // 自由走动段前面的过场要先关掉 free：S.run 交还操作时会把 free 打开，而这几个自由走动段是直接调用的
    //   （M.explore 要等 !S.busy，不能包进 S.run）。留着 free = true，过场台词播放期间界面也算“可走动”，
    //   自动测试会在这个窗口里抢按 Q 换队长，按键被台词框吃掉，最后报 swap_failed。
    S.free(false);
    party(S, 'polnareff');
    await M.scene(S, 'island_ch7', setupIsland, IS('arrive')[0], 'polnareff');
    M.prop(S, 'genie_lamp', IS('lamp')[0], footY('island_ch7', IS('lamp')[1]), { id: 'beach_lamp' });
    M.prop(S, 'boat', IS('boat')[0] + 8, footY('island_ch7', IS('boat')[1]), { id: 'spw_boat' });
    amb(S, 'sea_loop', 'wind_loop', .2);
    S.location('redsea');
    await lines(S, [['joseph', '红海上的无名小岛。SPW 的人会在这里接我们。'], ['polnareff', '天好蓝！……说起来，这里有没有什么宝藏？']]);
    T.memberTalk({
      joseph: async s => s.say('joseph', pick('c7isJo', ['小屋？别管它，那里什么都没有！……真的没有！', 'SPW 的人说，下一程要坐潜艇。'])),
      kakyoin: async s => s.say('kakyoin', pick('c7isKa', ['乔斯达先生从刚才起就有点心神不宁。', '这么清的海水，在日本很少见。'])),
      polnareff: async s => s.say('polnareff', pick('c7isPo', ['阿布德尔要是在，一定会说这里像开罗的海。……啊，不说了。', '那边沙滩上有个东西在发光！'])),
      jotaro: async s => s.say('jotaro', pick('c7isJt', ['……', '……老头子在藏什么。'])),
    });
    follow();
    T.goal(S, { x: IS('lamp')[0], y: footY('island_ch7', IS('lamp')[1]), h: 44, label: '发光的东西', delay: 45, every: 25, done: () => !!F().ch7Lamp, text: '沙滩上有个东西在发光（波鲁纳雷夫 E）。' });
    await M.explore(S, 'ch7Lamp', '红海小岛：E 搭话、调查；让波鲁纳雷夫去擦沙滩上的旧灯。');
  }

  // ================================================================ 第 14 战：审判（island_ch7）
  //   阶段 1（波鲁纳雷夫，撑 45 s）：泥偶 HP 9999（打不死），打泥偶 → 动摇 +10，满 100 跪地 3 s（受伤 ×1.5）；审判本体在场上游走。
  //   阶段 2（阿布德尔）：泥偶被火烧过变脆（受伤 ×2、HP 200）；本体藏进神灯，3 下重击（J3 / 连打 / U）打破灯才出来；HP 1000。
  //   同伴退到沙滩左边当观众（面朝右边的战斗）：原地留着会和泥偶、审判挤在灯旁边，玩家前后被夹、没有地方周旋。
  const SPECTATORS = () => { const x = IS('pier')[0] + 12; return { jotaro: [x + 10, 152], joseph: [x + 34, 149], kakyoin: [x + 58, 153], polnareff: [x + 82, 150] }; };
  const faceFight = c => { const sp = SPECTATORS(); for (const a of G.party.members) if (a !== c.player && sp[a.cid]) a.facing = 1; };
  // 泥偶按愿望塑形：0 雪莉 / 1 金山 / 2 另一个自己
  const DOLLS = ['clay_sherry', 'clay_gold', 'clay_pol'];
  // 泥偶低语（7-04 新增）：每 8 s 一句，三句一组 ⟳ 轮换；说的时候人就在旁边 → 动摇 +15（不只是干撑 45 s）
  const WHISPERS = [
    ['哥哥……你为什么不早点来……', '这次，别再丢下我了。', '哥哥的手……好暖和。'],
    ['全部都是你的……只要你站着别动。', '金子不会背叛你。', '伸手就能拿到哦。'],
    ['你保护不了任何人。', '雪莉的仇，你报了吗？', '银色战车……只会刺空气。'],
  ];
  // 输掉的台词：玩家 HP 归零时引擎自己调 c.fail()（不带文本），会把章节先设好的台词冲掉；
  //   所以开打时给 c.fail 包一层，没带文本就用脚本里的这一句（b14a 按愿望三种，其余各一句）
  function lossText(c, text) {
    if (!c._lossPatched) {
      const f0 = c.fail.bind(c);
      c.fail = t => f0(t || c._lossText);
      c._lossPatched = true;
    }
    c._lossText = text;
  }
  // 放水：脚本一律写“受伤 ×0.6”，引擎在 assist 时已经另外乘了 CFG.assistMul（0.7），
  //   这里按本段原有的 dmgScale（base）补上差额，避免放水后反而比正常更难（b14b/b15b 本来就有基准缩放）。
  const assistScale = (c, base = 1) => { if (c && c.assist) c.spec.dmgScale = base * .6 / G.combat.CFG.assistMul; };
  // 阶段 2 的战斗配置与开场（剧情 / 试炼共用一份）：愿望从 F().ch7Wish 读，试炼的 setup 会补一个默认值。
  //   两只泥偶会同时从前后扑击，玩家还要靠火焰打灯；把本段敌方伤害压到 65%，
  //   给真实走位留下容错，避免未被夹击时也被连续扑击耗死。
  function judgementSpec() {
    const lx = IS('lamp')[0];
    return { id: 'b14b_judgement', lead: 'avdol', swap: false, arena: [0, G.STAGES.island_ch7.x1], par: 70, dmgScale: .65,
      bench: { mode: 'stay', at: SPECTATORS() },
      tick(c) {
        const d = c.data;
        assistScale(c, .65);
        // J3 在灯 60 px 以内出手也算一次重击（火球本身不一定打得到道具，见 10-10 旧测试）。
        //   招式表里的招式对象是复用的，不能靠对象身份判断“新的一次”：用 atkT 归零判断重新出手。
        const atk = c.player.atk, j3 = !!(atk && atk.slot === 'J3');
        if (j3 && (!d.j3Was || c.player.atkT < d.j3T)) {
          if (Math.abs(c.player.x - d.lampX) <= 60) d.countLamp();
        }
        d.j3Was = j3; d.j3T = c.player.atkT;
        if (d.body && (d.body.dead || d.body.hp <= 0)) c.end();
      },
      testHint: c => ({ lampHits: c.data.lampHits, body: !!c.data.body,
        dolls: (c.data.dolls || []).filter(a => a && !a.remove && !a.dead && a.hp > 0).length }),
    };
  }
  function judgementInit(S, c) {
    const lx = IS('lamp')[0], wish = F().ch7Wish == null ? 0 : F().ch7Wish;
    // 第一阶段的泥偶和审判仍挂在舞台对象列表里；先移除它们，避免第二阶段的目标选择和攻击判定误认旧对象。
    for (const a of G.world.stage.actors) if (a.team === 'enemy') a.remove = true;
    Object.assign(c.data, { lampHits: 0, body: null, dolls: [], lampAt: null, j3Was: false, j3T: -1 });
    lossText(c, '……这次……不能再倒下……');
    c.player.x = lx - 74; c.player.y = 160; c.player.facing = 1; faceFight(c);
    // 阶段 2 是「许愿的那个 + 另一个」都成了泥偶（7-06）：许的是金山，另一个就是雪莉；否则另一个是金山
    const pair = [DOLLS[wish], wish === 1 ? 'clay_sherry' : 'clay_gold'];
    c.data.dolls = pair.map((cid, i) => c.spawn({ cid, kit: 'clay', x: lx + 6 + i * 80,
      y: 160, hp: 200, dmgMul: (a, p, m) => m.fire || p && p.cid === 'avdol' ? 2 : 1 }));
    const lamp = c.spawn({ cid: 'prop:genie_lamp', id: 'judgement_lamp', x: lx + 146, y: 164, hp: 9999, team: 'object' });
    c.data.lampX = lamp.x;
    // 神灯计数（7-06）：打中灯算一次；「在灯 60 px 以内出手的 J3」同样算一次。同一次 J3 两条路都满足时
    //   0.8 s 内只算一次（火球射程 125 px / 速度 200 px/s，命中不会晚于出手后 0.7 s）。
    const countLamp = () => {
      const d = c.data;
      if (d.body) return;
      if (c.t - (d.lampAt == null ? -9 : d.lampAt) < .8) return;
      d.lampAt = c.t;
      S.sfx('clang', .6);
      d.lampHits++;
      if (d.lampHits < (c.assist ? 2 : 3)) return;
      lamp.remove = true; S.fx('shatter', { src: 'prop:genie_lamp', logical: 'idle', x: lamp.x, y: lamp.y });
      // 神灯碎裂后本体暴露，阿布德尔的火焰是这一段的主解法；提高暴露本体的受火伤倍率，
      // 让玩家在泥偶持续扑击前有明确的收尾窗口。
      d.body = c.spawn({ cid: 'judgement', x: lamp.x - 40, y: 160, hp: 600, boss: true, dmgIn: 1.7 });
      S.word('本体！', d.body);
    };
    c.data.countLamp = countLamp;
    lamp.breakable = { filter: () => false, onHit(s, b, info) {
      if (!info || !['J3', 'rush', 'special'].includes(info.slot)) return;
      // 近战（连打 / U）要在灯旁边；J3 的火球可以远距离打中
      if (info.slot !== 'J3' && Math.abs(c.player.x - lamp.x) > 60) return;
      countLamp();
    } };
    M.ui(S, g => M.hud(g, c.data.body ? ['审判本体出现了！']
      : ['神灯 ' + c.data.lampHits + '/' + (c.assist ? 2 : 3), '对灯用 J 三连第三下（火球）/ 连打 / U']));
  }
  async function judgement(S) {
    calmStands();
    const lampProp = S.actor('beach_lamp'), [lx, ly] = IS('lamp');
    S.sfx('metal_scrape'); await S.wait(.4);
    snd('genie_appear', 'sparkle', { vol: .8 }); S.flash(.2, .6, '#fff6c0'); S.fx('burst', { x: lx, y: ly - 20, n: 24, colours: ['#ffe873', '#9fe8ff'] });
    const genie = S.spawn('judgement', lx + 10, footY('island_ch7', ly - 4), { id: 'genie_intro', team: 'npc', name: '灯神' }); genie.standReact = false; genie.talk = null; genie.facing = -1;
    await S.say('judgement', 'HAIL 2 U！我是神灯里的灯神！擦亮我的人，可以许三个愿望～', { actor: genie });
    S.mark('ch7_wishes');
    const wish = await S.choice(['让雪莉回来', '要一座金山', '让自己再强一点'], '三个愿望……先说哪一个？');
    F().ch7Wish = wish;
    const rows = wish === 0 ? [['polnareff', '雪莉……如果能再见你一面……'], [null, '沙子聚拢，塑成了一张熟悉的面孔。']]
      : wish === 1 ? [['polnareff', '一座金山！……这、这也太夸张了！'], [null, '金色的泥沙堆起来，又站起了一个人形。']]
        : [['polnareff', '另一个我？……这不是我的愿望！'], [null, '泥偶朝波鲁纳雷夫伸出了手。']];
    await lines(S, rows);
    await S.say('judgement', '愿望已经实现了！……那么，代价是你的命！', { actor: genie });
    genie.remove = true;
    // 灯神已经从灯里出来：探索时擦的那盏旧灯不再留在沙滩上（第二段另有一盏要打碎的灯，两盏同时在场分不清）
    if (lampProp) lampProp.remove = true;
    S.mark('b14a_judgement');
    await M.objectFight(S, { id: 'b14a_judgement', lead: 'polnareff', swap: false, coverage: false, vs: 'judgement', par: 60, timer: { until: 45, label: '坚持' },
      bench: { mode: 'stay', at: SPECTATORS() },
      tick(c, dt) {
        const d = c.data;
        assistScale(c);
        d.kneel = Math.max(0, d.kneel - dt);
        if (d.kneel > 0) { c.player.speed = 0; c.player.dmgIn = 1.5; c.player.play('kneel'); }
        else { c.player.speed = d.speed; c.player.dmgIn = 1; }
        // 泥偶低语：每 8 s 一句（S.bark 不停下战斗）；说话那一刻人就在旁边 → 动摇 +15、拟声字「下不了手……」
        M.every(d, 'whisper', dt, 8, () => {
          const doll = d.doll;
          if (!doll || doll.remove || doll.dead) return;
          S.bark(doll.cid, WHISPERS[wish][d.whisperN++ % 3], { dur: 1.6, name: '泥偶' });
          if (!d.whisperMark) { d.whisperMark = true; S.mark('c7_whisper'); }
          if (d.kneel > 0) return;
          const near = Math.abs(doll.x - c.player.x) <= (c.assist ? 30 : 50) && Math.abs(doll.y - c.player.y) <= 24;
          if (!near) return;
          d.shaken = Math.min(100, d.shaken + 15);
          S.word('下不了手……', c.player);
          if (d.shaken >= 100) { d.shaken = 0; d.kneel = 3; S.word('动摇！', c.player); }
        });
        if (c.t >= 45) c.end();
      }, testHint: c => ({ shaken: c.data.shaken, kneel: c.data.kneel,
        whisperIn: Math.max(0, 8 - (c.data.whisper || 0)), left: Math.max(0, 45 - c.t) }),
    }, c => {
      Object.assign(c.data, { shaken: 0, kneel: 0, speed: c.player.speed, whisper: 0, whisperN: 0, whisperMark: false });
      lossText(c, ['……雪莉……', '……金子……', '……我……'][wish]);
      S.hint('泥偶是假的：别打它，也别听它说话。', 6);
      // 玩家站在中间偏左、泥偶和审判都在右边：开场两边都有空地可以走位
      c.player.x = lx - 44; c.player.y = 162; c.player.facing = 1; faceFight(c);
      const mud = c.spawn({ cid: DOLLS[wish], kit: 'clay', x: lx + 76, y: 162, hp: 9999, boss: true });
      c.data.doll = mud;
      c.spawn({ cid: 'judgement', x: lx + 156, y: 156, hp: 9999, minHp: 9999 });
      c.on('hit', h => {
        if (h.t === mud && h.att === c.player) {
          c.data.shaken += 10;
          if (c.data.shaken >= 100) { c.data.shaken = 0; c.data.kneel = 3; S.word('动摇！', c.player); }
          else if (c.data.shaken % 30 === 0) S.word('下不了手……', c.player);
        }
      });
      M.ui(S, g => M.hud(g, ['动摇 ' + c.data.shaken + '%', '撑住 45 秒；泥偶是假的，离它远一点'], 40));
    });
    S.player.dmgIn = 1;
    await avdolReturns(S);
    S.mark('b14b_judgement');
    await M.objectFight(S, judgementSpec(), c => judgementInit(S, c));
    S.player.dmgIn = 1;
    await afterJudgement(S);
  }
  // 阶段 1 撑满：一道火焰从小屋里喷出来，把泥偶烧成焦壳——阿布德尔走出来（特写）→ 自动换他上场
  async function avdolReturns(S) {
    calmStands();
    const [hx, hy] = IS('hut_door');
    S.state('burnt', 1);
    S.sfx('fire_burst'); S.flash(.15, .7, '#ffb060'); S.shake(3, .4);
    S.fx('fire', { x: hx - 30, y: footY('island_ch7', hy), w: 40, h: 50 }, { life: 1.2 });
    // 火舌扫过泥偶（7-05）：0.4 s 烧成焦黑（tint 到 #2a2028）→ 裂成 16 块 → 移除。
    //   泥偶是砂土捏的，被火一烧就变脆——这也是阶段 2 里它受火伤 ×2 的来由。
    const doll = G.world.stage.actors.find(a => !a.remove && a.team === 'enemy' && String(a.cid).indexOf('clay_') === 0);
    if (doll) {
      doll.frozen = 1;
      for (let k = 1; k <= 4; k++) { doll.tint = { color: '#2a2028', k: k / 4 }; await S.wait(.1); }
      S.fx('shatter', { src: doll.cid, logical: 'idle', x: doll.x, y: doll.y, pieces: 16, dur: .9, tint_to: '#2a2028' });
      snd('clay_crumble', 'thud', { vol: .8 });
      S.mark('c7_burn');
      doll.remove = true;
    }
    await S.wait(.6);
    F().ch7AvdolBack = true;
    const av = await S.join('avdol', { notice: false }); av.hp = av.maxHp;
    S.leadable('avdol', true);
    place(S, 'avdol', hx, footY('island_ch7', hy + 2), -1);
    await T.fullbody3(S, { cid: 'avdol', behind: { cid: 'magred' }, aura: '#ff953f' });
    await S.say('avdol', '……好久不见了。');
    await T.closeup4(S, { heads: [{ cid: 'polnareff', expr: 'shock' }, { cid: 'kakyoin' }, { cid: 'jotaro' }, { cid: 'joseph' }], dur: 1.0, scale: 3 });
    await lines(S, [['polnareff', '阿布德尔！你、你还活着啊！！'], ['avdol', '后面再解释。先打碎那盏灯——审判的本体，就躲在里面！']]);
    S.setLeader('avdol', { force: true });
  }
  async function afterJudgement(S) {
    calmStands(); party(S, 'avdol');
    const [lx] = IS('lamp');
    const cameo = S.spawn('cameo', lx + 90, footY('island_ch7', 162), { id: 'cameo_down', team: 'npc', name: '卡梅欧' }); cameo.standReact = false; cameo.talk = null;
    S.pose(cameo, 'down');
    S.nameCard('cameo');
    await S.say(null, '审判的替身使者卡梅欧，被埋进了沙子里，只露出一个头。');
    await S.title('saiki');
    cameo.remove = true;
    for (const [cid, dx] of [['avdol', 0], ['polnareff', -30], ['joseph', 34], ['kakyoin', 60], ['jotaro', -60]]) place(S, cid, lx + dx, 162, dx > 0 ? -1 : 1);
    await lines(S, [['polnareff', '……阿布德尔。你明明被荷尔·荷斯打中了额头！'], ['avdol', '子弹只擦破了额头。乔斯达先生让我先躲起来，好骗过 DIO 的刺客。'],
      ['joseph', '对不起啦～敌人越以为他死了，他就越安全嘛！'], ['polnareff', '你们两个！！我、我还以为……我还为你哭了！！'], ['avdol', '……谢谢你，波鲁纳雷夫。'], ['jotaro', '……呀嘞呀嘞。']]);
    await S.notice({ text: '—— 阿布德尔 回到了队伍！——' });
  }

  // ================================================================ 潜艇（sub_ch7，submarine 640 宽）
  //   自由走动（第 25 天）：先看熟 12 件金属（E 都有正常的说明，战斗里要找“眨眼”的那件）；海图桌（纪念品航海日志）、潜望镜、铺位、潜水装备；
  //   到操舵台找乔瑟夫 → 他的咖啡杯咬掉了义手 → 第 15 战段 1。
  function setupSub(st) {
    st.state = Object.assign({}, st.state, { alarm: 0, leak: 0, dark: 0 });
    const ms = metalSpots();
    st.hotspots = ms.pts.map(([x, y], i) => Object.assign(M.hot('metal_' + i, x, LABELS[i], ['detail', 'peek', 'life'], '',
      async s => { await s.say(null, LABELS[i] + '：' + NOTES[i]); await markMetalSeen(s, i); },
      async (s, h, p) => { await s.say(p.cid, LABELS[i] + '……' + (p.cid === 'avdol' ? '没有生命的反应。' : '看上去没有异常。')); await markMetalSeen(s, i); },
      footY('sub_ch7', ms.wall ? 158 : y)), { ly: ms.wall ? y - 6 : y - 30 }));
    const H = (id, k, label, use) => { const v = SB(k); return Object.assign(M.hot(id, v[0], label, [], '', use, null, footY('sub_ch7', v[1] + 6)), { ly: v[1] - 30 }); };
    st.hotspots.push(
      H('periscope', 'periscope', '潜望镜', async (S, h, p) => sayBy(S, p, { kakyoin: '海面上什么都没有。……这片海，安静得让人不安。', _: '从天花板垂下来的潜望镜。' })),
      H('bunks', 'bunks', '铺位', async (S, h, p) => sayBy(S, p, { polnareff: '床好窄……我的发型会压扁的。', _: '双层铺位，帘子拉了一半。' })),
      H('gear', 'gear', '潜水装备', async (S, h, p) => sayBy(S, p, { joseph: '潜水服五套，氧气也够。……但愿用不上。', _: '潜水头盔和潜水服挂在墙上。' })),
      X.hot('ch7_logbook', SB('chart')[0] + 12, footY('sub_ch7', SB('chart')[1] + 8), { label: '海图桌上的日志' }),
      Object.assign(M.exit('helm', SB('helm')[0], '操舵台（乔瑟夫）', 'ch7Helm'), { y: footY('sub_ch7', SB('helm')[1] + 4) }),
    );
    st.onLook = async (S, p) => S.say(p.cid, T.by(p, { avdol: '……潜艇里除了我们，还有一个“生命”。说不清在哪里。', kakyoin: '金属太多了，看得我眼花。', _: '……到处都是金属。' }));
  }
  async function submarine(S) {
    S.free(false);   // 同 island：进自由走动段之前先锁住操作，过场台词放完再由 M.explore 打开
    party(S, 'jotaro');
    await M.scene(S, 'sub_ch7', setupSub, SB('arrive')[0] + 20, 'jotaro');
    amb(S, 'fan_loop', 'wind_loop', .12);
    const ms = metalSpots();
    // 旧背景没画金属物件：摆出 12 件道具当摆设；新背景画在墙上，不再叠一层
    const deco = ms.wall ? [] : METAL.map((id, i) => M.prop(S, 'disguise_' + id, ms.pts[i][0], 162));
    await S.say(null, '第二十五天。SPW 财团准备的潜艇，正潜在红海的深处。');
    await lines(S, [['joseph', '这次是潜艇！总不会坠毁了吧？'], ['avdol', '……乔斯达先生，请不要立这种旗。'], ['kakyoin', '艇里全是金属仪器。……能伪装的东西太多了。']]);
    T.memberTalk({
      joseph: async s => s.say('joseph', pick('c7suJo', ['我来掌舵！……潜艇也算车吧？', '咖啡要不要？我自己煮的。'])),
      avdol: async s => s.say('avdol', pick('c7suAv', ['能回到大家身边，真好。', '金属的味道……太浓了。'])),
      kakyoin: async s => s.say('kakyoin', pick('c7suKa', ['记住每件东西挂在哪里。……总觉得会用得上。', '舷窗外面有一群鱼游过去。'])),
      polnareff: async s => s.say('polnareff', pick('c7suPo', ['阿布德尔！我们来比比谁先找到厕所！', '潜艇里的厕所……我想起了那家旅馆。'])),
      jotaro: async s => s.say('jotaro', pick('c7suJt', ['……', '……这里太挤了。'])),
    });
    follow();
    T.goal(S, { x: SB('helm')[0], y: footY('sub_ch7', SB('helm')[1] + 4), h: 50, label: '操舵台', delay: 50, every: 25, done: () => !!F().ch7Helm, text: '去操舵台找乔瑟夫。' });
    await M.explore(S, 'ch7Helm', '潜艇：E 先看熟每件金属物件，再去操舵台找乔瑟夫。');
    for (const a of deco) if (a) a.remove = true;
    W.stage.props = [];
  }
  // 乔瑟夫的咖啡杯突然变形，咬掉了他的义手（〔局部 insert〕义手掉在地上冒火花，不是真手）
  async function handCut(S) {
    calmStands();
    const jo = S.actor('joseph');
    if (jo) place(S, 'joseph', SB('helm')[0] + 10, footY('sub_ch7', SB('helm')[1] + 4), 1);
    await S.say('joseph', '来，咖啡——咦？这杯子……刚刚眨了一下眼？');
    S.sfx('metal_crunch'); S.shake(3, .3); S.flash(.1, .6, '#ffffff');
    const ins = T.show(S, { bg: 'black', parts: [{ cid: 'prop:joseph_hand', x: 160, y: 120, scale: 3 }], draw: (g, t) => {
      // T.show 的 draw 回调拿到的是 CanvasRenderingContext2D，不是像素工具的图层对象。
      if (Math.floor(t * 14) % 2 === 0) { g.fillStyle = '#ffe070'; g.fillRect(168, 112, 3, 2); g.fillStyle = '#fff6b0'; g.fillRect(172, 108, 2, 2); }
    } });
    await S.wait(1); ins.close();
    await lines(S, [['joseph', 'OH MY GOD！我的手——！……还好，是义手。'], ['avdol', '是替身！它伪装成了艇里的东西！'], ['jotaro', '……出来。我要一件一件找。']]);
    S.state('alarm', 1); S.sfx('sub_alarm', .6);
    S.mark('b15a_highpriestess');
  }
  // 第 15 战段 1：漏水倒计时 90 s；12 件金属里有一件是女教皇，每 5 s 换一件，会“眨眼”（闪一帧）；面朝它 J 打中 → 现形，打中 3 下缩回去换位置；
  //   打错 → 艇体破损 −10 s；识破 3 次（或倒计时到 0，带着 −20 HP）进段 2。阿布德尔每 20 s 用生命探测报方向。
  // 第 15 战段 1 的小地图条（7-10）：HUD 下方居中一条 200×6；12 个点按 obj_* 的 x 映射到条上，
  //   看过的白、没看过的灰（12 件都看过 ch7AllSeen 时全白）、打错过的红；承太郎的位置用黄色小三角。
  //   潜艇里来回找一件“会眨眼的金属”纯靠记忆太苦，这条让人一眼看出还有哪几件没看过。
  function drawMetalMap(g, c, ms) {
    const x0 = 220, y0 = 84, w = 200, h = 6;
    g.fillStyle = '#0c0a14'; g.fillRect(x0 - 1, y0 - 1, w + 2, h + 2);
    g.fillStyle = '#2a2030'; g.fillRect(x0, y0, w, h);
    const xs = ms.pts.map(p => p[0]), lo = Math.min.apply(null, xs), hi = Math.max.apply(null, xs);
    const mapX = x => Math.round(x0 + 4 + (w - 8) * (hi === lo ? .5 : (x - lo) / (hi - lo)));
    const all = !!F().ch7AllSeen, wrong = c.data.wrong || {};
    for (let i = 0; i < ms.pts.length; i++) {
      const seen = all || !!F()['metal_seen_' + i];
      g.fillStyle = wrong[i] ? '#e04050' : seen ? '#f0f0f0' : '#706878';
      g.fillRect(mapX(ms.pts[i][0]) - 1, y0 + 1, 2, h - 2);
    }
    const px2 = mapX(c.player.x);
    g.fillStyle = '#ffd83c';
    g.beginPath(); g.moveTo(px2, y0 - 6); g.lineTo(px2 - 3, y0 - 1); g.lineTo(px2 + 3, y0 - 1); g.closePath(); g.fill();
  }
  async function disguiseFight(S) {
    let penalty = false;
    const ms = metalSpots();
    // 同伴不做 AI 战友：他们会去打 12 个物件（可攻击的道具），把“打错扣 10 秒”和现形判定搅乱；留在原地当观众
    await M.objectFight(S, { id: 'b15a_highpriestess', lead: 'jotaro', swap: false, bench: 'stay', vs: 'highpriestess', par: 80,
      arena: [0, 640], coverage: false,
      tick(c, dt) {
        const d = c.data;
        assistScale(c);
        if (!d.body) M.every(d, 'shift', dt, 5, () => { d.target = (d.target + 5) % 12; S.sfx('metal_scrape'); });
        M.every(d, 'hint', dt, 20, () => S.hint('阿布德尔：生命探测——它在' + (ms.pts[d.target][0] > c.player.x ? '右边！' : '左边！'), 4));
        // 眨眼周期：放水 1 s 一次（默认 1.5 s）
        const per = c.assist ? 1 : 1.5;
        for (let i = 0; i < d.props.length; i++) {
          const blink = !d.body && i === d.target && c.t % per < .22;
          d.props[i].frozen = blink ? 1 : 0;
          // 新背景墙上画着“正常版”的物件：道具平时透明，只在眨眼那一帧露出来（旧背景就一直显示道具）
          if (ms.wall) d.props[i].alpha = blink ? 1 : 0;
        }
        if (!d.mapMark && c.t > 1.5) { d.mapMark = true; S.mark('c7_minimap'); }
        if (I.okHit()) {
          I.consumeOk();
          const pick2 = ms.pts.findIndex(([x]) => Math.abs(c.player.x - x) < 20);
          if (pick2 >= 0) S.hint(LABELS[pick2] + (pick2 === d.target && !d.body ? '……刚才眨了眼！站到它下面按 J！' : '：暂时看不出破绽。'), 3);
        }
        M.every(d, 'alarm', dt, 12, () => S.sfx('sub_alarm'));
        if (c.t + d.penalty > 45) G.S.state('leak', 1);
        if (d.found >= 3 || c.t + d.penalty >= 90) { penalty = d.found < 3; c.end(); }
      },
      testHint: c => ({ target: c.data.target, found: c.data.found, exposed: !!c.data.body, hits: c.data.hits, penalty: c.data.penalty, left: Math.max(0, 90 - c.t - c.data.penalty),
        targetX: ms.pts[c.data.target][0], wall: ms.wall }),
    }, c => {
      Object.assign(c.data, { target: 3, found: 0, penalty: 0, props: [], body: null, hits: 0, strike: null, wrong: {}, mapMark: false });
      lossText(c, '……被它……钻了空子……');
      for (const [i, id] of METAL.entries()) {
        const [x, y] = ms.pts[i];
        // 墙上的物件：人站在可走带后沿（y 152）打它，物件画在墙上（z = 离地高度）；upward = 往上打得到（|dx| ≤ 24）
        const a = c.spawn({ cid: 'prop:disguise_' + id, x, y: ms.wall ? 152 : 164, z: ms.wall ? Math.max(0, 152 - y - 5) : 0, team: 'object', hp: 9999 });
        c.data.props.push(a);
        a.breakable = { upward: ms.wall, slots: ['J1', 'J2', 'J3', 'rush', 'special'], filter: () => false, onHit() {
          const d = c.data, p = c.player, strike = p.atk || p.rush;
          if (d.body || !strike || d.strike === strike) return;
          // 一招只算离拳头最近的那一件（相邻物件间距比拳头范围小）
          const aim = ms.wall ? p.x : p.x + p.facing * 30;
          const near = d.props.filter(o => ms.wall || (o.x - p.x) * p.facing >= -8).sort((u, v) => Math.abs(u.x - aim) - Math.abs(v.x - aim))[0];
          if (near !== a) return;
          d.strike = strike;
          if (i !== d.target) { d.penalty += 10; d.wrong[i] = true; S.sfx('metal_crunch'); S.hint('打错了！艇体受损，少了十秒。', 3); return; }
          a.visible = false; d.hits = 0;
          d.body = c.spawn({ cid: 'highpriestess', kit: 'highpriestess', x: a.x, y: 164, hp: 9999 });
          S.fx('burst', { x: a.x, y: (ms.wall ? y : 150), n: 14, colours: ['#c8d0e0', '#8a96a8'] });
          S.word('现形！', d.body); S.hint('女教皇现形了！K / L 躲扑击，J 打中三下。', 4);
        } };
      }
      c.on('hit', h => {
        const d = c.data;
        if (h.t !== d.body || h.att !== c.player || h.dmg <= 0) return;
        if (++d.hits < 3) return;
        d.body.remove = true; d.body = null; d.found++; d.shift = 0; d.target = (d.target + 7) % 12;
        for (const a of d.props) a.visible = true;
        S.sfx('metal_scrape'); S.word('缩回去了！', c.player);
      });
      M.ui(S, g => {
        M.hud(g, ['识破 ' + c.data.found + '/3　漏水 ' + Math.ceil(Math.max(0, 90 - c.t - c.data.penalty)) + ' 秒',
          c.data.body ? '现形了！再打中 ' + (3 - c.data.hits) + ' 下' : '盯住会眨眼的金属，站到它下面按 J；E 只观察']);
        drawMetalMap(g, c, ms);
      });
    });
    return penalty;
  }
  async function sinking(S) {
    S.state('leak', 1); S.state('alarm', 1); S.shake(4, 1);
    S.sfx('water_gush', .6);
    await lines(S, [['avdol', '它钻进管道逃出去了！艇体被它咬穿了！'], ['joseph', '进水了！大家穿好潜水服——快！']]);
    // 坠毁记录牌和后面两句都在 UI 层，而黑幕画在 UI 层之上：先 fadeOut 再放牌 = 几秒纯黑、牌子和台词全看不见。
    //   所以这里不淡出，牌子直接盖在进水的艇体上（下一段 setStage 自己会淡入）。
    //   牌子只挂约 2.7 s 就自己收掉，而 STORY_SHOTS 只按台词触发（后面那两句已经在牌子收掉之后），
    //   所以这里补一个 S.mark 单独拍一张牌——不然“牌子到底有没有被黑幕盖住”永远没有截图证据。
    const rec = S.crash(4, 5);
    await S.wait(.6);        // 牌 0.2 s 滑入、hold 2 s：等它停稳再拍。总时长仍由 rec 决定，不会变长
    S.mark('c7_crash');
    await rec;
    await S.say('joseph', '……这个也算我的吗？！');
    await S.say('polnareff', '算。');
  }

  // ================================================================ 第 15 战段 2：海底巨嘴（seabed_ch7，seabed_mouth）
  //   舌头往喉咙卷（往左 40 px/s，放水 28）：卷到喉咙口会被咽下去一次（扣血、退回中间）；
  //   上颚每 2.5 s 压下来（预警 45f，伤 10；key bite）：咬下来那一刻精准格挡 = 白金之星顶住牙 → 看准时机 J 打碎上排一颗；
  //   下排牙 J3 / 连打 / U 打碎；12 颗全碎就被吐出来。氧气 120 s（放水 160 s）。
  // 巨嘴的布景（剧情 / 试炼共用）：lead 只给剧情路径；试炼的队长由试炼统一决定，这里不设。
  async function mouthSetup(S, lead) {
    await M.ensureBg('_ch7');
    await M.scene(S, 'seabed_ch7', st => { st.state = Object.assign({}, st.state, { bite: 0, spit: 0 }); }, MT('arrive')[0], lead);
  }
  // 段 2 的战斗配置（剧情 / 试炼共用）：氧气、牙数、咬合都在这一份里改。
  function mouthSpec(S) {
    const ax = MT('arrive')[0], throatX = MT('throat')[0];
    // 上排咬合和舌头推移同时生效，环境战没有可站到屏外的安全区；保留 20 点基础伤害，
    // 只在本段统一缩放敌方伤害，避免一次漏挡直接把氧气战变成反复读档。
    return { id: 'b15b_highpriestess', lead: 'jotaro', swap: false, coverage: false, par: 90, dmgScale: .75,
      // 同伴在 @arrive 右边一字排开（原来 +80 = 330 出了 320 宽的图），朝左看承太郎打牙
      bench: { mode: 'stay', at: { joseph: [ax + 12, 160], avdol: [ax + 26, 158], kakyoin: [ax + 40, 162], polnareff: [ax + 54, 160] } },
      tick(c, dt) {
        const d = c.data;
        assistScale(c, .75);
        d.oxygen = Math.max(0, d.oxygen - dt);
        // 舌头持续把人往喉咙卷：40 px/s（放水 28），卷到喉咙口就被咽下去一次（7-12）
        c.player.x = Math.max(8, c.player.x - (c.assist ? 28 : 40) * dt);
        if (c.player.x <= throatX + 10) {
          // 放水可叠加：手工减免统一走 G.combat.assistK，第 1 档与原系数一致
          // 放水时 M.damage 传的攻击者是 null，引擎的放水倍率不会作用，所以这里手工乘
          M.damage(c, Math.round(8 * G.combat.assistK(c, .6)));
          S.hint('被卷进喉咙！', 1.5);
          c.player.x = 120;
          S.fx('bubbles', { x0: throatX - 4, y0: 108, x1: throatX + 18, y1: 168, n: 14 });
          if (!d.throatMark) { d.throatMark = true; S.mark('c7_throat'); }
        }
        M.every(d, 'bite', dt, 2.5, () => {
          const warn = 45 / 60;
          // 放水时这类剧情危险区没有 owner，引擎的放水倍率不会作用，所以这里手工乘
          c.hazard({ shape: 'rect', x0: 0, x1: 320, y0: 145, y1: 176, warn, dur: .12, dmg: Math.round(10 * G.combat.assistK(c, .6)), once: true, guard: 'normal', parry: true, tag: 'upper_bite', sfx: 'teeth_crunch',
            onActive: () => { G.S.state('bite', 1); G.S.shake(3, .2); } });
          d.biteAt = c.t + warn; d.biteOff = d.biteAt + .4;
        });
        // 咬合时背景整个上颚往下压 12 px，牙是道具不会跟着动（看着像被压进牙龈）：
        //   bite 开着的 0.4 s 里活着的上排牙 z −= 12，回 0 时加回来（重试时牙是新生成的，天然复原）
        const biting = !!d.biteAt && c.t >= d.biteAt && c.t < d.biteOff;
        if (biting !== !!d.biting) {
          d.biting = biting;
          for (let i = 0; i < 6; i++) { const a = d.teeth[i]; if (a && !a.dead && a.hp > 0) a.z += biting ? -12 : 12; }
        }
        if (d.biteOff && c.t >= d.biteOff) { d.biteOff = 0; d.biteAt = 0; G.S.state('bite', 0); }
        d.broken = d.teeth.filter(a => a.dead || a.hp <= 0).length;
        if (d.broken === 12) c.end();
        else if (d.oxygen <= 0) c.fail('氧气耗尽了……再来一次。');
      }, testHint: c => ({ broken: c.data.broken, oxygen: c.data.oxygen, throatIn: Math.round(c.player.x - throatX) }),
    };
  }
  // penalty = 段 1 没识破，带着 −20 HP 进水：只有剧情路径会传 true。
  function mouthInit(S, c, penalty) {
    const up = MT('upper'), lo = MT('lower');
    Object.assign(c.data, { oxygen: c.assist ? 160 : 120, broken: 0, teeth: [], biteOff: 0, biteAt: 0, biting: false, throatMark: false });
    lossText(c, '……还……没完……');
    // 放水时剧情直接扣血绕过 hit()，引擎的放水倍率不会作用，所以这里手工乘；保底 1 点，别让重试惩罚直接扣成 0 血
    if (penalty) c.player.hp = Math.max(1, c.player.hp - Math.round(20 * G.combat.assistK(c, .6)));
    for (const a of G.party.members) if (a !== c.player) a.facing = -1;
    for (let i = 0; i < 12; i++) {
      const upper = i < 6, [x, gy] = upper ? up[i] : lo[i - 6];
      // 上排：牙根在上颚（gy），牙尖朝下 27 px；人站在可走带后沿（152）打它 → z = 152 − 牙尖 y。下排：牙根在下颚牙床上，立在可走带后沿
      const a = c.spawn({ cid: upper ? 'prop:upper_tooth' : 'prop:lower_tooth', id: 'tooth_' + i, x, y: upper ? 152 : Math.max(152, gy + 4),
        hp: 80, team: 'object', z: upper ? Math.max(30, 152 - (gy + 27)) : 0 });
      // 下排牙允许连段中的任意一拳登记命中；J3、连打和 U 仍是推荐解法，
      // 但 J1/J2 也能稳定推进，避免玩家在舌头推移下因连段断开而原地耗血。
      a.breakable = { anim: 'idle', frames: [0, 1], upward: upper, filter: m => !upper && ['J1', 'J2', 'J3', 'rush', 'special'].includes(m.slot) };
      c.data.teeth.push(a);
    }
    c.on('parry', h => {
      if (h.move && h.move.tag === 'upper_bite' && !c.data.cine) M.task(c, async () => {
        const t = c.data.teeth.slice(0, 6).filter(a => a.hp > 0).sort((a, b) => Math.abs(a.x - c.player.x) - Math.abs(b.x - c.player.x))[0];
        const ok = await S.timing({ label: '顶住上颚，J 击碎牙齿！', zone: [.38, .62], limit: 3 });
        // 失败的精准格挡仍扣血，但只留一小段惩罚；上排每 2.5 秒出招，连续失误不应瞬间清空整条生命。
        if (ok && t) M.toothHit(c, t); else M.drain(c, 4);
      });
    });
    M.ui(S, g => M.hud(g, ['牙齿 ' + c.data.broken + '/12　氧气 ' + Math.ceil(c.data.oxygen) + ' 秒',
      '上排：咬下来那一刻按 L 顶住，再按 J', '下排：J 三连第三下 / 连打 / U']));
    // 旧背景没画上颚：补一条牙床；新背景（有 upper 锚点）画好了
    const hasJaw = !!(G.D && G.D.bg && G.D.bg.seabed_mouth && G.D.bg.seabed_mouth.anchors && G.D.bg.seabed_mouth.anchors.upper);
    if (!hasJaw) M.pixel('mouth_ceiling', P => { px.rect(P, 0, 64, 320, 10, '#795353'); });
    M.pixel('dive_helmets', P => {
      for (const a of W.stage.actors) if (CREW5.includes(a.cid) && !a.remove && a.visible !== false)
        px.blitFrame(P, 'prop:dive_helmet', 'idle', 0, a.x - G.cam.x, a.headY() + 14 - G.cam.y);
    });
  }
  async function mouth(S, penalty) {
    party(S, 'jotaro');
    await mouthSetup(S, 'jotaro');
    S.mark('b15b_highpriestess');
    await lines(S, [['kakyoin', '这里是……海底的岩洞？不对，地面在动！'], ['avdol', '是嘴！我们被吞进了一张巨大的嘴里！'], ['jotaro', '……坚硬如钻石？那就一颗一颗打碎。']]);
    await M.objectFight(S, mouthSpec(S), c => mouthInit(S, c, penalty));
    S.state('bite', 0); S.state('spit', 1);
    S.sfx('water_splash'); S.shake(4, .5);
    await S.say(null, '最后一颗牙碎了。巨嘴猛地张开，把五个人吐了出去——');
  }
  // 被吐到埃及海岸：米朵拉满嘴碎牙趴在沙滩上（只画背影）→ 纪念品金属的牙 → 地图（潜艇 42% 沉没，第 29 天）→ 埃及
  async function coast(S) {
    S.free(false);   // 同 island：进自由走动段之前先锁住操作，过场台词放完再由 M.explore 打开
    party(S, 'jotaro');
    await M.scene(S, 'coast_ch7', st => {
      st.state = Object.assign({}, st.state, { dusk: 0 });
      const [sx, sy] = EC('shore'), [nx, ny] = EC('sign');
      st.hotspots = [
        X.hot('ch7_metal_tooth', sx + 30, footY('coast_ch7', sy), { label: '沙滩上闪着金属光' }),
        Object.assign(M.hot('sign', nx, '路牌', [], '', async (S, h, p) => sayBy(S, p, { avdol: '……EGYPT。终于回来了。', joseph: 'EGYPT！我们到了！', _: '双语的路牌：EGYPT。' })), { y: footY('coast_ch7', ny + 10) }),
        M.exit('road', EC('road')[0], '去小镇的路', 'ch7Road'),
      ];
    }, EC('arrive')[0], 'jotaro');
    amb(S, 'sea_loop', 'wind_loop', .2);
    const [mx, my] = EC('midler');
    const mid = S.spawn('midler_back', mx, footY('coast_ch7', my), { id: 'midler', team: 'npc', name: '米朵拉' }); mid.facing = -1; mid.standReact = false; mid.talk = null;
    S.nameCard('midler');
    await S.say(null, '女教皇的替身使者米朵拉，满嘴碎牙趴在沙滩上，再起不能。');
    await lines(S, [['polnareff', '……从背影看，好像是个美人？'], ['jotaro', '……走了。']]);
    mid.remove = true;
    S.location('egypt_coast');
    await lines(S, [['avdol', '这里就是埃及。……DIO 就在这片土地的某个地方。'], ['joseph', '第二十九天。荷莉，再等等我们。']]);
    // 海岸的同伴搭话（7-13）：全员刚被吐出来，聊的都是这一路报废的交通工具和之后的打算
    T.memberTalk({
      joseph: async s => s.say('joseph', pick('c7coJo', ['埃及！……飞机、汽车、潜艇，全都报废了。', '接下来走路也行！'])),
      avdol: async s => s.say('avdol', pick('c7coAv', ['这里的空气，我很熟悉。', '先去找 SPW 的人。'])),
      kakyoin: async s => s.say('kakyoin', pick('c7coKa', ['海水把一切都冲干净了。', '……还剩二十二天。'])),
      polnareff: async s => s.say('polnareff', pick('c7coPo', ['头盔里全是水，我的发型……', '阿布德尔，晚上请我吃饭，这是罚你的！'])),
      jotaro: async s => s.say('jotaro', pick('c7coJt', ['……', '……走吧。'])),
    });
    follow();
    await M.explore(S, 'ch7Road', '埃及的海岸：E 调查；沿着土路往右走。');
  }

  // ================================================================ 本章入口
  G.STORY.ch7 = async S => {
    T.resetCounters();
    S.free(false);   // 篇章卡 / 航线 / 进岛过场期间不给操作（理由见 island 顶部）
    for (const key of ['ch7Lamp', 'ch7Wish', 'ch7AvdolBack', 'ch7Helm', 'ch7Fished', 'ch7Road', 'ch7AllSeen']) delete F()[key];
    for (let i = 0; i < 12; i++) delete F()['metal_seen_' + i];
    await M.ensureBg('_ch7');
    party(S, 'polnareff');
    await S.chapterCard('ch7');
    await S.setStage('map_ch7', { x: 100, y: 160, music: 'travel' });
    await S.route(['阿拉伯沙漠', '红海'], { vehicle: 'ship', day: 22, left: 28, history: ['东京', '香港', '新加坡', '加尔各答', '瓦拉纳西', '卡拉奇', '阿拉伯沙漠'] });
    // 自由走动段不能包在 S.run 里：M.explore 等的条件是 !S.busy，S.run 期间 busy 一直是 true，会卡死。
    //   直接调用时 S.busy 为 false，M.explore 自己开 free、等旗标、再关掉（同第6章的 village / camp）。
    await island(S);
    await S.run(async s => { await judgement(s); });
    await submarine(S);
    await S.run(async s => {
      await handCut(s);
      const penalty = await disguiseFight(s);
      await sinking(s);
      await mouth(s, penalty);
    });
    await coast(S);
    await S.run(async s => {
      await s.setStage('map_ch7', { x: 100, y: 160, music: 'travel' });
      // 潜艇图标开到 42% 沉没（规划照分镜 s11）；地图图标名是 map_sub
      await s.route(['红海', '阿斯旺'], { vehicle: 'sub', cut: .42, day: 29, left: 22, history: ['东京', '香港', '新加坡', '加尔各答', '瓦拉纳西', '卡拉奇', '阿拉伯沙漠', '红海'] });
    });
    await M.end(S, 'ch7_complete');
  };

  // ================================================================ 单战入口（开发调参 G.DEV / 标题「挑战」）
  G.DEV = G.DEV || {};
  G.DEV.ch7Judgement = async S => {
    await M.ensureBg('_ch7'); F().ch7AvdolBack = false; party(S, 'polnareff');
    await M.scene(S, 'island_ch7', setupIsland, IS('arrive')[0], 'polnareff');
    M.prop(S, 'genie_lamp', IS('lamp')[0], footY('island_ch7', IS('lamp')[1]), { id: 'beach_lamp' });
    await S.run(async s => judgement(s));
  };
  G.DEV.ch7Priestess = async S => {
    await M.ensureBg('_ch7'); F().ch7AvdolBack = true; party(S, 'jotaro');
    await M.scene(S, 'sub_ch7', setupSub, SB('arrive')[0] + 20, 'jotaro'); W.stage.props = [];
    await S.run(async s => { const pen = await disguiseFight(s); await mouth(s, pen); });
  };
  X.challenge({ id: 'b14b_judgement', chapter: 'ch7', title: 'VS 审判（波鲁纳雷夫 → 阿布德尔）', run: S => G.DEV.ch7Judgement(S) });
  X.challenge({ id: 'b15b_highpriestess', chapter: 'ch7', title: 'VS 女教皇（承太郎）', run: S => G.DEV.ch7Priestess(S) });

  // ================================================================ 星尘试炼关卡工厂
  //   两关都靠 M.objectFight 开打：它负责 waves / energy / data.ready / init 包装和 midGame 清理，
  //   而试炼的 setup + spec 分支会把 spec 直接交给 S.fight、漏掉这些包装，所以用 run 包一层、仍经它开打。
  G.TRIAL_SRC['b14b_judgement'] = {
    chapter: 'ch7', pack: '_ch7',
    run: async (S, o) => {
      await M.ensureBg('_ch7');
      // 试炼不经过许愿选择：固定第一个愿望（雪莉），阶段 2 的泥偶组合才和剧情里的 pair 逻辑一致。
      //   阿布德尔归队是阶段 2 的前置（剧情里由 avdolReturns 设）
      F().ch7AvdolBack = true; F().ch7Wish = 0;
      // burnt = 1 是阿布德尔那把火烧过之后的背景；setupIsland 每次进关都会把 state 复位，所以摆完景再设
      await M.scene(S, 'island_ch7', st => { setupIsland(st); st.state.burnt = 1; }, IS('arrive')[0]);
      // 阶段 1 的泥偶 / 审判不能带进阶段 2（新场景本来就没有，这里是重复进入时的保险）
      for (const a of G.world.stage.actors) if (a.team === 'enemy') a.remove = true;
      await M.objectFight(S, o.wrap(judgementSpec()), c => judgementInit(S, c));
    },
  };
  G.TRIAL_SRC['b15b_highpriestess'] = {
    chapter: 'ch7', pack: '_ch7',
    run: async (S, o) => {
      await mouthSetup(S);
      // 试炼没有段 1，penalty 恒为 false（不扣那 20 点血）
      await M.objectFight(S, o.wrap(mouthSpec(S)), c => mouthInit(S, c, false));
    },
  };
})();
