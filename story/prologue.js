// 序章　东京 / 替身之名（规划 §5.1；地图后缀 _pro）。整章流程：
//   序-0 篇章卡 → 序-1 牢房（过场）→ 序-2 牢房（自由：调查、J 亮替身、U 星之眼）→ 序-3 荷莉来接、乔瑟夫、阿布德尔
//   → 序-3b 掰铁栏、走出牢房 → 序-4 序1「阿布德尔的试探」（教学战 b00_avdol_test，6 步，在铁栏外的走廊打）→ 序-5「替身」大标题、压帽
//   → 序-6 空条家白天（自由：Q 换队长、每人的 U）→ 序-7 念写（DIO 的照片）→ 夜里的眼睛 → 第二天早上
//   → 序-8 上学路（自由，只有承太郎：坡顶小路 → 走下长石阶 stairs_pro）→ 序-8b 下石阶时被绊倒滚下去、花京院递纸巾
//   → 走到校门（school_pro）走进去 → 序-9 保健室（推门进去；纸巾字条、校医被操纵、两次按 L 的 QTE）
//   → 序-10 序2「被操纵的花京院」（b01_kakyoin，VS 卡）→ 序-11 欧拉终结、「胜负已分」、扛回家
//   → 序-12 空条家·肉芽 → 序-13 拔肉芽（QTE pluck）+ 乔瑟夫的波纹 → 序-14 荷莉病倒 → 序-15 卧室「50 天」
//   → 序-16 找 DIO 在哪（自由 / 解谜：承太郎 U 找到苍蝇；卡住保护 40 s 提示 / 70 s 替玩家做完）→ 序-17 决心、花京院入队
//   → 序-18 黄昏出发「目标——埃及！」→ To Be Continued
//   台词照规划 §5.1.1 的台词表（新写的大意，标了“分镜原句”的照用）；死亡、伤口按 D10 克制处理。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const F = () => G.flags;
  const now = () => (G.clk ? G.clk.world : 0);
  const cnt = (k) => (G.flags[k] = (G.flags[k] || 0) + 1);
  const by = (leader, map) => G.TPL.by(leader, map);
  const NAME_TOP = 24;          // 名牌放左上（UI y）：后面紧跟底部对话框时用
  const CARD_BELOW_HUD = 100;   // 开战前一刻放的左侧替身卡：放在战斗 HUD 队长面板（UI y 8–94）下面
  const LOC_BELOW_STRIP = 50;   // 多人自由走动的地图：地点卡放在左上队伍头像条（UI y 8–40）下面
  // 序1 在铁栏外的走廊打（用户 2026-10-09：开打时承太郎要从铁栏里出来）：场地、走廊纵深、阿布德尔 / 水管的位置
  const CORRIDOR = { arena: [88, 256], y: [150, 176] };
  const AVDOL_AT = [278, 164];
  const PIPE = [112, 151];

  // ================================================================ 序-1 / 序-2 牢房
  function jailNotes(S) {
    // 收音机按 daily 的拍子（0.4535 s）吐音符，一直到牢房这一段结束
    let k = 0;
    T().every(0.4535, () => { k++; T().floater(S, 'scene:s02_note', 224, 104.5, { z: 4, rise: 16, dur: 1.4, frame: k % 2, wave: 2 }); }, () => F().jailOut);
  }
  async function jailIntro(S) {
    const p = S.player;
    p.facing = 1;
    T().prop(S, 'scene:s02_stool', 137, 123.5, { id: 'stool' });
    S.pose(p, 'sit');
    jailNotes(S);
    S.zoom(1.14, 160, 100, 2.6);
    S.location('tokyo');
    S.sfx('footstep', { vol: 0.25, seed: 1 });
    G.defer(0.6, () => S.sfx('footstep', { vol: 0.2, seed: 2 }));
    await S.narrate('不良少年空条承太郎，赖在牢里不肯出来。', { pos: 'top' });
    await S.narrate('他说，自己被“恶灵”附身了。', { pos: 'top' });
    S.nameCard('jotaro');
    await S.zoom(1, null, null, 0.5);
    S.unpose(p);
    // 人物名牌（左下，2.6 s）和地点卡（左上）还在的时候先不出提示条：电脑上提示条在下面会压住名牌，手机上提示条在上面会压住地点卡
    G.defer(2.3, () => {
      const st = G.world.stage;
      if (st && st.id === 'jail_pro' && !F().jailReady && !Object.keys(jailSeen()).length)
        S.hint(`随便看看牢房（0 / ${JAIL_KEYS.length}）　E 调查　U 恶灵的眼睛　J 恶灵伸手`, 12);
    }, 'ui');
  }
  // ---------------------------------------------------------------- 序-2 牢房探索（用户 2026-10-09：别那么快进荷莉来接的剧情，让玩家在牢房里好好探索）
  //   能调查的 10 样东西，每样都有 E 调查 / U 用“恶灵”的眼睛看 / J 让“恶灵”伸手 的反应（灯泡只有 U / J）；
  //   调查满 JAIL_BED 样以后，去床上躺下（E）= 等人来；调查满 JAIL_AUTO 样会自己听见脚步声。
  //   不再有“2 样或 25 秒就进剧情”的倒计时；40 s 没有新发现给提示，满 JAIL_BED 样后给床的目标箭头。
  const JAIL_NAMES = { police: '狱警', pipe: '水管', tally: '「正」字', magazines: '杂志堆', bulb: '灯泡', poster: '海报',
    bars: '铁栏', window: '高窗', radio: '收音机', cans: '空罐子' };
  const JAIL_KEYS = Object.keys(JAIL_NAMES);
  const JAIL_BED = 4, JAIL_AUTO = 8;
  const BUNK = [150, 124];
  const jailSeen = () => F().jailSeen || (F().jailSeen = {});
  const jailN = () => Object.keys(jailSeen()).length;
  function discover(S, key) {
    const seen = jailSeen();
    if (!JAIL_NAMES[key] || seen[key]) return;
    seen[key] = 1;
    cnt('jailN');
    const n = jailN(), all = JAIL_KEYS.length;
    if (n >= JAIL_AUTO) { F().jailReady = true; F().jailAuto = true; return; }
    S.hint(`牢房 ${n} / ${all}` + (n >= JAIL_BED ? '　想等人来，就去床上躺下（E）' : '　E 调查　U 恶灵的眼睛　J 恶灵伸手'), 5);
  }
  // “恶灵”伸手去碰画面上 (x, sy) 处的东西（世界坐标；sy = 东西在画面上的高度，不是脚底线）。
  //   白金之星 reach 帧的手在锚点前方约 40 px、上方约 37 px：倒推替身站哪儿（dx 可以是负数 = 浮在承太郎身后，越过头顶去够）
  async function reachTo(S, x, sy) {
    const p = S.player, dir = x < p.x ? -1 : 1;
    S.face(p, dir);
    const dx = G.clamp(Math.abs(x - p.x) - 40, -46, 58), z = Math.round(G.clamp(p.y - 37 - sy, -42, 72));
    S.standAct(p, 'reach', { dx, z, hold: true });
    S.sfx('whoosh', { vol: 0.6, rate: 1.1 });
    await S.wait(0.32);
  }
  async function standBack(S) { await S.recall(S.player); }
  // 床：调查够了才躺得下（= 等人来）
  async function useBunk(S) {
    const n = jailN(), all = JAIL_KEYS.length;
    if (n < JAIL_BED) {
      await S.say('jotaro', '……还不困。');
      const left = JAIL_KEYS.filter((k) => !jailSeen()[k]).slice(0, 3).map((k) => JAIL_NAMES[k]);
      S.hint(`牢里还有东西可以看看（${n} / ${all}）：${left.join('、')}`, 6);
      return;
    }
    const p = S.player;
    await S.walk(p, BUNK[0], BUNK[1], { speed: 60 });
    S.face(p, 1);
    S.pose(p, 'sit');
    await S.say('jotaro', '……睡一会儿。');
    F().jailReady = true;
  }
  // 40 s 没有新发现：点两三样还没看过的；调查够了以后给床的目标箭头
  function jailHelp(S) {
    let lastN = jailN(), lastT = now(), goal = null;
    T().tick(() => {
      if (F().jailReady) { if (goal) goal.stop(); return true; }
      const n = jailN(), W = G.world;
      if (n !== lastN) { lastN = n; lastT = now(); }
      if (n >= JAIL_BED && !goal) {
        goal = T().goal(S, { x: BUNK[0], y: BUNK[1] - 26, h: 0, label: '床', delay: 15, every: 25, done: () => !!F().jailReady,
          text: '看够了的话，去床上躺一会儿（E）——外面好像有人要来' });
      }
      if (W.free && !S.busy && now() - lastT > 40) {
        lastT = now();
        const left = JAIL_KEYS.filter((k) => !jailSeen()[k]).slice(0, 3).map((k) => JAIL_NAMES[k]);
        if (left.length) S.hint('还能看看：' + left.join('、') + '　（E / U / J 都试试）', 7);
      }
      return false;
    });
  }
  // ---- 各样东西的“恶灵伸手”（J）反应
  const standTouch = {
    pipe: async (S) => {
      await reachTo(S, PIPE[0], PIPE[1] - 30);
      S.sfx('thud', 0.7); S.sfxText('咚', { wx: PIPE[0] + 4, wy: PIPE[1], wz: 30 });
      await S.say('jotaro', '……水管在抖。再用力一点，就要喷水了。');
      await standBack(S);
    },
    tally: async (S) => {
      await reachTo(S, 88, 48);
      S.sfx('slash', { vol: 0.35, rate: 1.6 });
      await S.say('jotaro', '……“它”又在墙上划了一道。');
      await standBack(S);
    },
    magazines: async (S) => {
      await reachTo(S, 88, 108);
      S.sfx('whoosh', { vol: 0.3, rate: 2 });
      await S.say('jotaro', '“它”一页一页地翻。……比我看得还快。');
      await standBack(S);
    },
    bulb: async (S) => {
      await reachTo(S, 160, 42);
      S.sfx('glass_break', { vol: 0.25, rate: 2.2 });
      S.flash(0.08, 0.35, '#000000');
      G.defer(0.16, () => S.flash(0.06, 0.25, '#000000'));
      S.shake(0.6, 0.15);
      await S.say('jotaro', '……灯泡晃了一下。再碰就碎了。');
      await standBack(S);
    },
    poster: async (S) => {
      await reachTo(S, 182, 54);
      await S.say('jotaro', '……算了。别人的东西，别碰。');
      await standBack(S);
    },
    bars: async (S) => {
      const p = S.player;
      S.face(p, 1);
      S.standAct(p, 'block', { dx: 14, z: 6, hold: true });
      S.sfx('rumble', 0.45);
      S.shake(1, 0.3, { dir: 'x' });
      S.sfxText('ギギ…', { wx: p.x + 12, wy: 138, wz: 30 }, { dur: 0.6, jitter: 1 });
      await S.wait(0.5);
      await S.say('jotaro', '……栏杆在响。——不行。出去的话，“它”会伤到人。');
      await standBack(S);
    },
    window: async (S) => {
      await reachTo(S, 222, 48);
      S.fx('burst', { x: 222, y: 48, n: 8, speed: 30, colours: ['#a08060', '#d8c0a0'], gravity: -10, life: 0.8 }, { space: 'world' });
      S.sfx('whoosh', { vol: 0.4, rate: 1.8 });
      await S.say('jotaro', '……麻雀飞走了。');
      await standBack(S);
    },
    radio: async (S) => {
      await reachTo(S, 224, 104);
      S.sfx('pop', 0.5);
      if (G.audio && G.audio.duck) G.audio.duck(1.7, 2.6);
      const guard = S.actor('police');
      if (guard) { S.emote(guard, '！', 0.8); await T().say(S, 'police', '喂、喂！收音机小声点！……咦，你根本没碰它啊？'); }
      await S.say('jotaro', '……');
      await standBack(S);
    },
    cans: async (S) => {
      await reachTo(S, 248, 126);
      const guard = S.actor('police');
      const can = T().prop(S, 'disguise_metal_cup', 236, 132, { id: 'can_fly', z: 6 });
      S.sfx('clang', { vol: 0.5, rate: 1.4 });
      if (can) { await S.arc(can, 64, 170, 18, 0.7); S.sfx('clang', { vol: 0.4, rate: 1.1 }); }
      if (guard) { S.pose(guard, 'shock'); S.emote(guard, '！？', 1.0); await T().say(S, 'police', '罐、罐子自己滚出来了……！'); S.pose(guard, 'read'); }
      if (can) can.remove = true;
      await standBack(S);
    },
  };
  // 白金之星把手臂伸出铁栏，把狱警手里的漫画拿回牢房（狱警 onStand、铁栏的 U 共用；只演一次）
  async function grabMagazine(S) {
    if (F().grabbed) return;
    F().grabbed = true;
    discover(S, 'police');
    const p = S.player, guard = S.actor('police');
    // 走到铁栏左前（牢里纵深最靠前），替身压低、手从栏杆缝里伸到狱警手上的漫画（reach 帧的手在锚点前 40、上 37 px）
    if (Math.abs(p.x - 110) > 3 || Math.abs(p.y - 138) > 3) await S.walk(p, 110, 138, { speed: 70 });
    S.face(p, -1);
    await S.summon(p, { dur: 0.2, rise: 0 });
    const mx = guard ? guard.x + 8 : 48, my = (guard ? guard.y : 168) - 20;
    S.standAct(p, 'reach', { dx: G.clamp(p.x - mx - 40, -40, 58), z: Math.round(G.clamp(p.y - 37 - my, -42, 40)), hold: true });
    S.sfx('whoosh', { vol: 0.8, rate: 0.9 });
    await S.wait(0.3);
    const mag = T().prop(S, 'magazine', guard ? guard.x + 8 : 48, guard ? guard.y - 1 : 166, { id: 'mag_fly', z: 18, alt: 'prop:manga' });
    if (guard) S.pose(guard, 'idle');
    if (mag) await S.arc(mag, 124, 136, 30, 0.4);
    S.sfx('pop', 0.7);
    if (guard) { S.pose(guard, 'shock'); S.emote(guard, '！？', 1.0); }
    if (S.player.stand) S.player.stand.idle();
    await T().say(S, 'police', '又、又来了！漫画自己飞起来了！');
    await S.say('jotaro', '……我说过，别管我。');
    await S.recall(p);
    if (guard) S.pose(guard, 'idle');
  }
  async function talkPolice(S) {
    discover(S, 'police');
    const n = cnt('policeN');
    if (n === 1) {
      await T().say(S, 'police', '空条，你妈妈打电话来了，今天就来接你。拜托你，赶紧出去吧。');
      await S.say('jotaro', '不出去。');
    } else if (n === 2) {
      await T().say(S, 'police', '被你打的那四个混混，到现在还在发抖……你到底对他们做了什么？');
      await S.say('jotaro', '……没做什么。是“它”做的。');
    } else if (F().grabbed && !F().policeBeg) {
      F().policeBeg = true;
      await T().say(S, 'police', '求你了，别再让它拿我的东西了！');
    } else {
      await T().say(S, 'police', '……我什么都没看见。什么都没看见。');
    }
  }
  // 调查点：E = use（e 句）、U = look（u 句）、J = standTouch[key]；三种都记一次“已调查”（key = JAIL_NAMES 的键）
  function jailHot(id, key, x, y, ly, label, e, u, o = {}) {
    const h = {
      id, x, y, ly, r: 12, ry: 7, label, tags: ['detail'],
      use: e == null ? null : async (S) => { discover(S, key); await S.say('jotaro', e); },
      look: async (S) => { discover(S, key); await S.say('jotaro', u); },
      onStand: standTouch[key] ? async (S) => { discover(S, key); await standTouch[key](S); } : null,
    };
    return Object.assign(h, o);
  }
  function setupJail(S) {
    const st = G.STAGES.jail_pro;
    st.state = { bend: 0 };
    st.props = [
      // 走廊左边铁栏前的水管：序-2 隔着铁栏是调查点，序1（教学战在走廊打）第 5 步是可破坏物（连打第 8 击起才掉血，J 三连只“咚咚”响）
      {
        type: 'breakable', id: 'pipe', sprite: 'jail_pipe', frames: [0, 1], anim: 'idle', x: PIPE[0], y: PIPE[1], z: 0, w: 16, h: 48, hp: 30,
        only: ['rush'], minRushHits: 8, free: false,
        onHit: async (S2, h, info) => {
          if (info && (info.slot === 'J1' || info.slot === 'J2' || info.slot === 'J3')) {
            G.S.sfx('thud', 0.8); G.S.sfxText('咚', { wx: PIPE[0] + 4, wy: PIPE[1], wz: 30 });
            const ctx = G.world.fight; if (ctx) ctx.data.pipeTaps = (ctx.data.pipeTaps || 0) + 1;
          }
        },
        onBreak: async () => pipeBurst(G.S),
      },
    ];
    st.npcs = [
      {
        cid: S.cid('npc_police', 'scene:s09_man'), id: 'police', name: '狱警', x: 40, y: 168, facing: 1, anim: 'read',
        standReact: true, onStand: async (S2) => { if (!F().grabbed && S2.player.x <= 116) await grabMagazine(S2); },
      },
    ];
    // 牢里可走 x 96–236、y 122–138：调查点按 x 和纵深错开，相邻两样走两步就能分开选（E 选中范围 r 12 × ry 7）
    st.hotspots = [
      // 狱警隔着铁栏搭话（他坐在走廊左边，人走不到跟前：调查点放在牢里左边的栏杆前）；J = 伸手抢他的漫画
      {
        id: 'police_talk', x: 100, y: 136, r: 12, ry: 7, ly: 150, label: '狱警', tags: ['detail'], use: talkPolice,
        look: async (S) => {
          discover(S, 'police');
          await S.say('jotaro', F().grabbed ? '……他在发抖。漫画被拿走了，现在假装在看天花板。' : '他在看这周的漫画周刊。……看得正起劲。');
          if (!F().grabbed) S.hint('站在铁栏左边、面朝他按 J：让“恶灵”伸手', 5);
        },
        onStand: async (S) => {
          if (!F().grabbed) { await grabMagazine(S); return; }
          discover(S, 'police');
          const guard = S.actor('police');
          await reachTo(S, 48, 140);
          if (guard) { S.pose(guard, 'shock'); S.emote(guard, '！！', 1.0); await T().say(S, 'police', '别、别过来！漫画已经给你了！'); S.pose(guard, 'idle'); }
          await standBack(S);
        },
      },
      jailHot('pipe_look', 'pipe', 114, 137, 112, '栏杆外的水管', '栏杆外头的水管。……滴答滴答，吵死了。', '阀门锈住了。用力打一下就会喷水。'),
      jailHot('tally', 'tally', 104, 123, 52, '墙上的「正」字', '前面住过的人划的。……我懒得数。', '三个半『正』字。那人住了十七天。', { lx: 90 }),
      jailHot('magazines', 'magazines', 122, 128, 100, '杂志堆', '……“它”拿进来的。我自己可没出过这道门。', '最上面那本是这周刚出的。……值班室少了一本，就在这儿。', { lx: 96 }),
      { id: 'bunk', x: BUNK[0], y: BUNK[1], r: 12, ry: 7, ly: 96, label: '床（躺下等人来）', use: useBunk },
      jailHot('bulb', 'bulb', 164, 126, 38, '灯泡', null, '钨丝快断了。……“它”的眼睛连这个都看得清清楚楚。'),
      jailHot('poster', 'poster', 184, 123, 52, '摇滚海报', '……不是我贴的。', '海报角上有一个拳印。……这个是我。'),
      jailHot('bars', 'bars', 182, 137, 120, '铁栏', '我不出去。……我身上有东西，会伤到人。', '栏杆很结实。……对“它”来说不算什么。', {
        tags: ['detail', 'grab'],
        look: async (S) => {
          discover(S, 'bars');
          await S.say('jotaro', '栏杆很结实。……对“它”来说不算什么。');
          if (!F().grabbed) {
            await S.say(null, '铁栏外，狱警手里拿着一本漫画周刊。');
            await grabMagazine(S);
          }
        },
      }),
      jailHot('window', 'window', 212, 123, 47, '高窗', '天气不错。……跟我没关系。', '窗外有只麻雀。……它也在看我。'),
      jailHot('radio', 'radio', 226, 129, 104, '收音机', '……这首还行。', '电池快没电了。指示灯一秒闪一次。', {
        use: async (S) => { discover(S, 'radio'); if (G.audio && G.audio.duck) G.audio.duck(1.3, 2.0); await S.say('jotaro', '……这首还行。'); },
      }),
      jailHot('cans', 'cans', 234, 136, 124, '空罐子', '狱警的。“它”顺手拿的。……我没碰。', '罐子底下压着一张纸条：『求你别再拿了』。'),
    ];
    st.onLook = async (S2, leader) => { await S2.say('jotaro', '……没什么特别的。'); };
    st.triggers = [];
  }
  // 自由走动时 J 亮替身、面朝狱警（x ≤ 112、朝左）：不靠 onStand 的范围也能触发
  function watchGrab(S) {
    let last = G.input && G.input.lastPress ? G.input.lastPress('attack') : 0;
    T().tick(() => {
      if (F().grabbed || F().jailReady) return true;
      const lp = G.input && G.input.lastPress ? G.input.lastPress('attack') : 0;
      if (lp !== last) {
        last = lp;
        const p = S.player, W = G.world;
        if (W.free && !S.busy && p && p.x <= 116 && p.facing < 0) S.run(grabMagazine).catch(G.cancelIgnore);
      }
      return false;
    });
  }

  // 〔特写·局部 insert〕乔瑟夫把左手（义手）伸到铁栏前；半透明的白金之星从牢里伸手穿过栏杆，一捏——小指“啪”地掉下来
  //   （原著：恶灵扯掉义手的小指）。用户 2026-10-09 嫌旧版奇怪（3 倍精灵被画面切掉、名牌压在上面、看不出捏了什么）：
  //   改成 2 倍、人都在画面里；画的顺序 = 替身（牢里）→ 铁栏 → 乔瑟夫（铁栏外）→ 小指；两只手在两根栏杆的空当里碰上
  async function pinkyInsert(S) {
    if (G.uifx && G.uifx.cards) G.uifx.cards = G.uifx.cards.filter((c) => c.kind !== 'name');
    const BAR_X = [44, 72, 100, 128, 156, 184, 212, 240, 268, 296];
    const HAND = [204, 122];           // 乔瑟夫 point 帧（翻转）的指尖 ≈ 白金之星 reach 帧的手（2 倍；插入画面不吃推镜，见 G.cam.box）
    const sp = { kind: 'sprite', cid: 'starplat', anim: 'reach', frame: 0, x: 58, y: 196, scale: 2, alpha: 0 };
    const jo = { kind: 'sprite', cid: 'joseph', anim: 'point', frame: 0, x: 234, y: 178, scale: 2, flip: true };
    const pk = { kind: 'sprite', cid: 'prop:pinky', anim: 'idle', frame: 0, x: HAND[0], y: HAND[1] + 4, scale: 3, hidden: true, o: { rot: 0 } };
    const ins = T().insert(S, {
      bg: 'menace', colours: ['#2a2048', '#0e0820'], lines: true, inner: 56,
      parts: [sp],
      draw: (wg, t) => {
        wg.fillStyle = '#4a505e'; for (const x of BAR_X) wg.fillRect(x - 3, 0, 7, 180);
        wg.fillStyle = '#9aa0b0'; for (const x of BAR_X) wg.fillRect(x - 2, 0, 2, 180);
        wg.fillStyle = '#4a505e'; wg.fillRect(0, 152, 320, 7);
        wg.fillStyle = '#9aa0b0'; wg.fillRect(0, 152, 320, 2);
        T().part(wg, jo, t);
        T().part(wg, pk, t);
      },
    });
    if (G.world.insert) G.world.insert.tag = 'pinky';      // 自动测试认这个插入画面
    S.mark('pro_pinky');
    S.sfx('whoosh', { vol: 0.7, rate: 0.8 });
    await S.animate(0.42, (k) => { const e = 1 - Math.pow(1 - k, 3); sp.x = 58 + 60 * e; sp.alpha = 0.62 * Math.min(1, k * 1.6); });
    await S.wait(0.12);
    // 捏：火花 + 小指脱落，乔瑟夫吓一跳
    S.sfx('pop', 0.9);
    S.shake(2, 0.2);
    S.fx('hit_spark', { x: HAND[0], y: HAND[1], size: 9, accent: '#c8a8ff' }, { space: 'canvas', tag: 'insert' });
    S.sfxText('ポロッ', { x: HAND[0] * 2 - 44, y: HAND[1] * 2 + 26 }, { dur: 0.9 });     // UI 坐标 = 画布 ×2
    jo.anim = 'shock';
    pk.hidden = false;
    await S.animate(0.6, (k) => {
      pk.x = HAND[0] - 30 * k;
      pk.y = HAND[1] + 4 + 54 * k * k - 16 * Math.sin(Math.PI * k);
      pk.o.rot = k * Math.PI * 3;
      sp.alpha = 0.62 - 0.25 * k;
    });
    S.sfx('pop', { vol: 0.45, rate: 1.5 });
    await S.wait(0.45);
    ins.close();
  }

  // ================================================================ 序-3 荷莉、乔瑟夫、阿布德尔（照分镜 s02 2.60–10.55）
  async function jailVisitors(S) {
    const p = S.player;
    S.hint(null);
    // 自己调查满了 = 听见脚步声；躺下以后 = 被吵醒
    S.sfx('footstep', { vol: 0.35, seed: 3 });
    G.defer(0.45, () => S.sfx('footstep', { vol: 0.4, seed: 4 }));
    G.defer(0.9, () => S.sfx('footstep', { vol: 0.45, seed: 5 }));
    await S.say('jotaro', F().jailAuto ? '……外面有脚步声。' : '……啧。睡不成了。');
    if (Math.abs(p.x - 148) > 2 || Math.abs(p.y - 124) > 2) await S.walk(p, 148, 124, { speed: 70 });
    S.face(p, -1);
    S.pose(p, 'sit');
    const holly = S.spawn('holly', -16, 166, { id: 'holly', facing: 1 });
    const jo = S.spawn('joseph', -40, 166, { id: 'joseph', facing: 1 });
    const av = S.spawn('avdol', 344, 166, { id: 'avdol', facing: -1, standPos: { dx: -26, z: 22 } });
    S.zoom(1.6, 128, 134, 0.3);
    await S.walk(holly, 104, 166, { speed: 70 });
    S.pose(holly, 'wave');
    T().floater(S, 'scene:s02_heart', 106, 166.5, { z: 44, rise: 18, dur: 1.4, wave: 3 });
    // 名牌默认在左下（UI y 265），会被底部对话框（y 272–352）整个盖住；接底部对话的名牌放左上
    S.nameCard('holly', { y: NAME_TOP });
    await S.say('holly', '承太郎～妈妈来接你啦！');
    // 4.55 承太郎回头吼：怒筋跳动、抖 1 px
    S.face(p, -1);
    T().stick(S, 'scene:s02_vein', p, { dur: 1.4, shake: true, dz: -2 });
    S.shake(1, 0.28, { dir: 'x' });
    await S.say('jotaro', '我被恶灵附身了，别管我！', { expr: 'angry' });
    // 5.75 爱心炸开，承太郎冒汗
    S.sfx('pop', 0.8); S.sfx('sparkle', 0.6);
    S.fx('burst', { x: 106, y: 120, n: 10, speed: 50, colours: ['#ff8ab0', '#ffd0e0'], life: 0.5 }, { space: 'world' });
    T().stick(S, 'scene:s02_sweat', p, { dur: 1.6, dx: 8, dz: -6 });
    await S.say('holly', '呀，承太郎回我话了～');
    S.unpose(holly);
    await S.say('holly', '妈妈今天把你爱吃的都做好了哦！外公也来了！');
    await S.say('jotaro', '……外公？');
    // 6.45 乔瑟夫大步进场，7.20 踏定：顶镜、放射速度线、shake 2、ドドド
    S.zoom(1.25, 120, 130, 0.3);
    await S.walk(jo, 150, 166, { speed: 90 });
    S.bump(0.2, 0.12);
    S.fx('speedlines', { style: 'radial', n: 36, inner: 40, alpha: 0.5, colour: '#ffffff' }, { space: 'canvas', life: 0.33 });
    S.shake(2, 0.3);
    S.sfx('dododo', 0.8);
    S.sfxText('ドドド', jo, { dur: 1.2, jitter: 2 });
    S.nameCard('joseph');
    await S.say('joseph', '我是你外公……乔瑟夫·乔斯达！', { pos: 'top' });
    await S.say('joseph', '从纽约飞了十几个小时，就为了把你从这里拎出来。出来吧，承太郎！', { pos: 'top' });
    S.unpose(p);
    S.face(p, -1);
    await S.say('jotaro', '别过来。……我身上的东西，会伤到你。');
    await pinkyInsert(S);
    const pinky = T().prop(S, 'pinky', 158, 166, { id: 'pinky', z: 26 });
    if (pinky) await S.arc(pinky, 164, 167, 6, 0.3);
    S.sfx('pop', 0.6);
    S.emote(jo, '？', 1.0);
    S.sfxText('？', jo, { dur: 0.8 });
    await S.say('joseph', '……哦？', { expr: 'shock' });
    await S.say('joseph', '别紧张，这是义手。真的那根，五十年前就没了。');
    if (pinky) pinky.remove = true;
    S.sfx('pop', 0.4);
    await S.say('joseph', '……果然是“那个”。阿布德尔，拜托你了。', { expr: 'grave' });
    // 8.60 阿布德尔中景，9.65 加速推镜 + 火焰光环
    await S.walk(av, 262, 166, { speed: 70 });
    S.face(av, -1);
    S.nameCard('avdol', { y: NAME_TOP });
    await S.say('avdol', '交给我吧，乔斯达先生。');
    S.zoom(2.4, av, -26, 0.3);
    await S.say('avdol', '空条承太郎。你不想伤到别人——这份心意，我收下了。');
    av.auraFlame = { colour: '#ff6a28', intensity: 0.4, grow: 3, height: 8, seed: 1 };
    S.fx('sparkles', { x: av.x, y: av.y - 24, n: 6, radius: 14, colour: '#ffb060' }, { follow: av, dy: -24, life: 1.2 });
    S.sfx('charge', 0.8);
    const push = S.zoom(2.95, av, -26, 0.9);
    const aura = S.animate(0.9, (k) => { av.auraFlame = { colour: '#ff6a28', intensity: 0.4 + 0.8 * k, grow: 3, height: 8 + 10 * k, seed: 1 }; });
    await S.say('avdol', '那就由我把你拖出来吧！');
    // 推镜和火焰光环演完再拉回（翻得快时也不会被半截的推镜盖掉）
    await Promise.all([push, aura]);
    // 10.55 音乐切 battle；红色魔术师在走廊升起；替身卡左侧（开战后左上是承太郎的血条面板：卡片放在面板下面）
    S.music('battle', 0.3);
    await S.zoom(1, null, null, 0.3);
    av.auraFlame = null;
    S.sfx('power_up', 0.8);
    await S.summon(av, { rise: 14, dur: 0.35, card: { side: 'left', y: CARD_BELOW_HUD } });
    S.flash(0.12, 0.35, '#ffc060');
    S.unpose(p);
    await S.wait(0.4);
  }

  // ================================================================ 序-4 序1 阿布德尔的试探（教学战，规划 §5.1.2）
  const STEP_HINT = {
    1: '←→↑↓ 在走廊里走动',
    2: '火球来了——按 K 闪避（闪开的一瞬间无敌）',
    3: '火柱躲不开——按住 L，让替身挡住',
    4: '火绳收紧的一瞬间按 L——精准格挡（别乱按：连着乱按不算）',
    5: '左边铁栏前有根水管——对着它按 J 三连，接着连按 J（欧拉连打）',
    6: '能量满了——按 U，替身必杀！',
  };
  function teachNext(S, ctx, k) {
    ctx.data.step = k;
    ctx.data.relax = false;
    ctx.data.stepT0 = ctx.t;
    ctx.data.ok = 0;
    ctx.data.hinted = false;
    // 这一步的提示一直挂着，直到做到（6 s 就消失的话，第一次玩的人还没看懂提示就没了）
    S.hint(STEP_HINT[k], 60);
    if (k === 6) { ctx.fillEnergy(); S.sfx('meter_full', 0.8); }
    if (k === 5 && ctx.data.pipeBroken) ctx.data.ok = 5;   // 早就打爆了：直接算过
  }
  function teachSetup(S, ctx) {
    const p = () => G.world.player;
    ctx.data.evades = 0; ctx.data.guards = 0; ctx.data.guardHold = 0; ctx.data.jetFails = 0; ctx.data.bindFails = 0; ctx.data.rushed = false;
    // 火球从阿布德尔身前飞出；火柱铺满整条走廊（场地 x + 走廊纵深各放宽 4 px，躲不开、只能挡）
    ctx.data.fireX = AVDOL_AT[0] - 20;
    ctx.data.jetBox = [CORRIDOR.arena[0], CORRIDOR.arena[1], CORRIDOR.y[0] - 4, CORRIDOR.y[1] + 4];
    teachNext(S, ctx, 1);
    let lx = p().x, ly = p().y, dist = 0, lastHurt = -9;
    ctx.on('evade', () => { if (ctx.data.step === 2 && ++ctx.data.evades >= 2) ctx.data.ok = 2; });
    ctx.on('graze', () => { if (ctx.data.step === 2 && ++ctx.data.evades >= 2) ctx.data.ok = 2; });
    // 火球飞到跟前（70 px 内、正朝人飞）时按了 K 也算闪开（每个火球只算一次）：教学要的是“看见火球按 K”，
    //   按早了几帧、无敌帧没盖住碰撞也算会了（放宽后火球变慢，早按更常见，以前会一直卡在这一步）
    ctx.on('dodge', (e) => {
      const pl = p();
      if (ctx.data.step !== 2 || !pl || (e && e.who && e.who !== pl)) return;
      const s = (G.world.shots || []).find((q) => !q.dead && !q._taught && q.side === 'enemy' && Math.abs(q.y - pl.y) < 14 &&
        Math.abs(q.x - pl.x) < 70 && (q.x - pl.x) * (q.vx || 0) < 0);
      if (!s) return;
      s._taught = true;
      if (++ctx.data.evades >= 2) ctx.data.ok = 2;
    });
    // 第 3 步：火柱每 10f 烧一下，挡住 3 下（约 0.5 s）或者在火里按住 L 满 1 s（下面的 tick）就算过
    ctx.on('guard', () => { if (ctx.data.step === 3 && ++ctx.data.guards >= 3) ctx.data.ok = 3; });
    ctx.on('parry', () => {
      if (ctx.data.step === 3 && ++ctx.data.guards >= 3) ctx.data.ok = 3;
      if (ctx.data.step === 4) ctx.data.ok = 4;
    });
    // 格挡仍有少量漏伤；只有没挡住的命中才算教学失败，否则连续格挡永远被清零。
    ctx.on('hit', (e) => {
      if (e.t !== p() || e.guard || !e.dmg) return;
      if (ctx.data.step === 3) { ctx.data.guards = 0; ctx.data.guardHold = 0; }
      const t = ctx.t;
      if (t - lastHurt < 1.6) return;      // 同一次火柱 / 束缚只算一次失败
      lastHurt = t;
      if (ctx.data.step === 3) {
        if (++ctx.data.jetFails >= 2 && !ctx.data.relax) { ctx.data.relax = true; S.hint('火柱一亮就按住 L，别松手', 60); }
      } else if (ctx.data.step === 4) {
        if (++ctx.data.bindFails >= 3 && !ctx.data.relax) {
          ctx.data.relax = true; ctx.data.parryWin = 12 / 60;
          S.hint('红圈最亮的时候按一下 L', 60);
        }
      }
    });
    ctx.on('rushStart', () => { if (ctx.data.step === 5) ctx.data.rushed = true; });
    ctx.on('special', () => { if (ctx.data.step === 6) S.hint(null); });     // 必杀切入时收起提示框，别压在招式名上
    ctx.on('break', () => { ctx.data.pipeBroken = true; if (ctx.data.step === 5) ctx.data.ok = 5; });
    T().tick((dt) => {
      if (G.world.fight !== ctx) return true;
      const pl = p();
      const d = ctx.data, el = ctx.t - (d.stepT0 || 0);
      // 第 3 步（规划 §5.1.2 表）：火柱烧着的时候按住 L 满 1 s 就算过，不用等它烧满几下
      if (d.step === 3 && pl && !G.world.cine && pl.state === 'guard' &&
          G.world.hazards.some((h) => h.tag === 'flame_jet' && h.phase === 'active' && !h.dead)) {
        d.guardHold = (d.guardHold || 0) + dt;
        if (d.guardHold >= 1) d.ok = 3;
      }
      if (d.step === 1 && pl) {
        dist += Math.abs(pl.x - lx) + Math.abs(pl.y - ly);
        if (el >= 4 && !d.relax && dist < 40) { d.relax = true; S.hint('按任一方向键，走一小段即可', 60); }
        if (dist >= (d.relax ? 20 : 40)) d.ok = 1;
      }
      if (pl) { lx = pl.x; ly = pl.y; }
      if (d.step === 2 && !d.relax && el > 7.0 && d.evades < 2) { d.relax = true; S.hint('阿布德尔手上的火光一亮就按 K（闪开 2 发）', 60); }
      if (d.step === 5 && !d.relax && el > 20) {
        d.relax = true;
        const pipe = S.actor('pipe');
        if (pipe && pipe.breakable) pipe.breakable.minRushHits = 4;
        S.hint('靠近左边水管，J 三连后继续连按 J；现在四下连打即可破管', 60);
      }
      // 第 6 步开窗那一帧，战斗流程会把提示换成短短的「按 U！」：换回这一步的完整提示（HUD 能量条旁边仍显示「按 U！」）
      if (d.step === 6 && ctx.storyU && !d.u6) { d.u6 = true; S.hint(STEP_HINT[6], 60); }
      if (d.step === 6 && !d.relax && el > 8) { d.relax = true; S.hint('只需按一下 U，白金之星会替你完成这一击', 60); }
      return false;
    });
  }
  const teachEvent = (k, line) => ({
    when: (t, ctx) => ctx.data.step === k && ctx.data.ok === k,
    run: async (S, es, attempt, ctx) => {
      ctx.step(k);
      S.sfx('ding', 0.6);
      if (line) await S.say(line[0], line[1], line[2] || {});
      teachNext(S, ctx, k + 1);
    },
  });
  // 第 5 步水管爆开：喷水、蒸汽、走廊里的火熄掉（「ジュウウ」）
  async function pipeBurst(S) {
    const ctx = G.world.fight;
    if (ctx) ctx.data.pipeBroken = true;
    S.fx('water_gush', { x: PIPE[0] + 2, y: PIPE[1] - 34, direction: 1, strength: 1.0, t1: 2.0 }, { life: 2.4 });
    S.fx('smoke', { x: 150, y: 158, colour: '#e8e8f0', loop: true, rise: 40, t1: 2.0, life: 1.4 }, { life: 3.4 });
    S.sfx('splash', 0.9); S.sfx('water_gush', 0.8);
    S.sfx('fire_burst', { vol: 0.5, rate: 0.6 });
    S.sfxText('ジュウウ', { wx: 170, wy: 160, wz: 30 }, { dur: 1.0 });
    S.shake(2, 0.3);
  }
  async function fightAvdolTest(S) {
    S.hint(null);
    await S.fight({
      id: 'b00_avdol_test', arena: CORRIDOR.arena, lead: 'jotaro', swap: false, lockMsg: '这一战只能由承太郎应战',
      music: null, after: null, warnTier: 1, dmgScale: 0.8,
      playerMinHp: 1, losable: false, coverage: false,
      energy: { start: 0 },
      steps: { n: 6, label: '阿布德尔的试探' },
      // 第 6 步的剧情必杀（必杀替换）：欧拉连打冲到红色魔术师面前，最后一拳停在阿布德尔鼻尖前（finaleOra）→ 序-5「替身」
      //   只在第 6 步开窗：否则开战第一帧就弹「按 U！」把第 1 步的移动提示顶掉，前面攒满能量按 U 还会跳过教学
      kitOverride: { jotaro: { special: { need: 100, title: 'jotaro', bg: 'radial', colours: ['#5a2aa0', '#34146a', '#46208a'],
        window: (c) => c.data.step === 6, prompt: '按 U！', run: finaleOra } } },
      //   阿布德尔站在走廊右边（不写 x / y 时 c.spawn 会把他挪到承太郎身边）；
      //   boss: true 只为不画头顶小血条（他不能被打，HUD 这一战显示的是教学进度格）
      waves: [[{
        kit: 'e_avdol_test', actor: 'avdol', cid: 'avdol', id: 'avdol', stand: 'magred', name: '阿布德尔', x: AVDOL_AT[0], y: AVDOL_AT[1], boss: true,
        untargetable: true, standPos: { dx: -26, z: 22 }, idle: 'idle',
      }]],
      testHint: (ctx) => ({ step: ctx.data.step || 0, relax: !!ctx.data.relax }),
      onWave: async (S2, wi, spawned, attempt, ctx) => { teachSetup(S2, ctx); },
      events: [
        teachEvent(1, null),
        teachEvent(2, ['joseph', '躲得好！……喂，阿布德尔，下手轻点！']),
        teachEvent(3, ['jotaro', '……它，在帮我挡。']),
        teachEvent(4, ['avdol', '挣断了红色束缚？……有意思。']),
        teachEvent(5, ['avdol', '用水灭火？……冷静的家伙。']),
      ],
      endWhen: (ctx) => !!ctx.data.finaleU,
    });
  }
  // 第 6 步 U：白金之星冲到红色魔术师面前欧拉连打（红色魔术师架住），最后一拳停在阿布德尔鼻尖前。阿布德尔不能被打：只演、不判伤
  async function finaleOra(S, p, ctx, C) {
    const av = S.actor('avdol'), f = (n) => n / 60;
    S.hint(null);
    // 朝向直接设：C.aim 对不能被打的人（untargetable）不转身，第 5 步打完水管还朝左，会背对阿布德尔连打
    if (av) { p.facing = av.x < p.x ? -1 : 1; S.standAct(av, 'block', { hold: true }); }
    await C.dash(av ? av.x - 62 : p.x + 40, av ? av.y : p.y, f(8));
    C.stand('rush', { dx: 16, jitter: 1 });
    // 拳影墙只伸到红色魔术师架住的位置（再长会盖住站在阿布德尔身后的乔瑟夫）
    await C.rush(1.1, { dmg: false, tick: f(12), word: 'ORA', visual: { reach: 20, spread: 28, rate: 45, scale: 1.1, big: 0.25 } });
    C.stand('punch', { dx: 28, seq: [[2, 99]] });
    C.sfx('punch_heavy');
    C.impact(['invert', 'purple'], f(2), f(10));
    C.shake(5, f(24));
    if (av) C.fx('shockwave', { x: av.x - 22, y: av.y - 38, r_max: 56, dur: 0.4, colour: '#d8c8ff' });
    C.stopAll(f(12));
    await C.wait(0.7);
    ctx.data.finaleU = true;
    ctx.end();
  }

  // ================================================================ 序-3b 掰铁栏、走出牢房（照分镜 s02 12.86–13.95）
  //   用户 2026-10-09：开打的时候承太郎要从铁栏里出来——掰铁栏挪到开战前，教学战在铁栏外的走廊打（铁栏不再挡住打斗）
  async function breakout(S) {
    const p = S.player, av = S.actor('avdol'), jo = S.actor('joseph'), holly = S.actor('holly');
    S.hint(null);
    // 红色魔术师的火舌舔上铁栏：再不出来就烧进去
    S.face(p, 1);
    S.sfx('fire_burst', { vol: 0.7, rate: 0.9 });
    S.fx('fire_burst', { x: 214, y: 128, size: 24, dur: 0.6 });
    S.shake(1.5, 0.25);
    await S.wait(0.35);
    await S.say('jotaro', '……别小看我。', { expr: 'angry' });
    await S.cutin({ cid: 'jotaro', portrait: 'jotaro', title: 'jail_bars', bg: 'radial', colours: ['#5a2aa0', '#34146a', '#46208a'], dur: 0.92 });
    if (Math.abs(p.x - 160) > 2 || Math.abs(p.y - 128) > 2) await S.walk(p, 160, 128, { speed: 80 });
    S.face(p, 1);
    // 12.86 白金之星带残影扑到铁栏
    p.ghostOn = true;
    S.summon(p, { dur: 0.12, rise: 4 });
    S.standAct(p, 'block', { dx: 186 - p.x, z: 6, hold: true });
    S.sfx('whoosh', { vol: 0.9, rate: 0.85 });
    await S.wait(0.14);
    p.ghostOn = false;
    // 13.00 撑住发抖
    S.state('bend', 0.14);
    S.shake(1.4, 0.4, { dir: 'x' });
    S.sfxText('ギギギ…', { wx: 186, wy: 138, wz: 34 }, { dur: 0.6, jitter: 1.5 });
    S.sfx('rumble', 0.8);
    await S.wait(0.39);
    // 13.39 掰断
    S.impact('invert');
    S.state('bend', 1);
    S.sfxText('メキメキッ', { wx: 186, wy: 138, wz: 40 }, { dur: 0.9, jitter: 2 });
    for (let i = 0; i < 3; i++) G.defer(i * 0.04, () => S.fx('hit_spark', { x: 180 + i * 6, y: 104 + i * 7, size: 14, accent: '#c8a8ff', seed: i }));
    S.fx('shockwave', { x: 186, y: 120, r_max: 60, width: 3 });
    S.fx('smoke', { x: 186, y: 136, n: 10, rise: 26, life: 1.4 });
    S.fx('burst', { x: 186, y: 60, n: 18, speed: 20, colours: ['#a8a090', '#d8d0c0'], gravity: 90, life: 1.0 });
    S.shake(4, 0.5);
    S.sfx('crash', 0.9);
    await S.wait(0.56);
    // 13.95 替身白化收回；承太郎从缺口走出来，站到走廊上（走廊在铁栏的纵深线前面：画在铁栏上面）
    S.recall(p);
    S.zoom(1.25, 182, 140, 0.3);
    await S.walk(p, 182, 130, { speed: 50 });
    await S.walk(p, 182, 160, { speed: 40 });
    S.face(p, 1);
    if (av) S.face(av, -1);
    await S.say('avdol', '……他自己走出来了。');
    // 围观的人让出走廊：荷莉退到狱警旁边，乔瑟夫从前排绕到阿布德尔身后；阿布德尔站到走廊右边
    //   （第 5 步对着左边水管连打时，拳影墙往左伸 50 px 左右，左边别站太多人）
    const moves = [];
    if (holly) moves.push(S.walk(holly, 28, 154, { speed: 90, face: 1 }));
    if (jo) moves.push(S.walk(jo, 150, 175, { speed: 90 }).then(() => S.walk(jo, 306, 174, { speed: 90, face: -1 })));
    if (av) moves.push(S.walk(av, AVDOL_AT[0], AVDOL_AT[1], { speed: 60, face: -1 }));
    await Promise.all(moves);
    S.face(p, 1);
    await S.zoom(1, null, null, 0.3);
    await S.say('avdol', '很好。那就让我看看，你身上的“恶灵”有几分本事！');
    // 场地换成走廊：牢里 y 122–138 → 走廊 y 150–176；左右交给战斗场地夹（牢房的左右墙不要了）
    const st = G.world.stage;
    st.yMin = CORRIDOR.y[0]; st.yMax = CORRIDOR.y[1]; st.obstacles = [];
  }

  // ================================================================ 序-5 「替身」（照分镜 s02 13.95–17.90）
  async function standName(S) {
    const p = S.player, av = S.actor('avdol'), jo = S.actor('joseph');
    S.hint(null);
    S.recall(p);
    if (av) { S.recall(av); S.face(av, -1); }
    S.face(p, 1);
    S.zoom(1.25, av ? (p.x + av.x) / 2 : p.x, 136, 0.3);
    await S.say('avdol', '……够了。拳头停在了我面前——它听你的。');
    S.title('stand', { sfx: 'freeze', y: 76 });      // 放在头顶上方：默认画面正中会盖住人
    S.sfx('freeze', 0.8);
    S.mark('pro_stand_title');
    await S.say('avdol', '乔斯达先生，接下来交给您。');
    await S.zoom(1, null, null, 0.3);
    if (jo) { S.face(jo, jo.x < p.x ? 1 : -1); S.face(p, jo.x < p.x ? -1 : 1); }
    await S.say('joseph', '那不是恶灵，是『替身』！');
    await S.say('joseph', '站在你身边、替你战斗的东西——你自己的精神，变成了看得见的样子。');
    await S.say('jotaro', '……替身。');
    // 15.90 〔特写·全身×3〕压帽 + 身后半透明的白金之星 + ゴゴゴ两组
    const fb = await T().fullbody3(S, {
      cid: 'jotaro', anim: 'pose', frame: 1, bg: 'menace', colours: ['#3a1a6a', '#14062a'], scale: 3, x: 150, y: 176,
      cap: true, capAt: 0.45, glint: [150, 64], glintAt: 0.5, behind: { cid: 'starplat', anim: 'pose', dx: 50, alpha: 0.62 }, hold: true,
    });
    const m1 = S.menacing({ x: 470, y: 120, n: 4, seed: 1 });
    const m2 = S.menacing({ x: 130, y: 210, n: 3, seed: 2 });
    S.sfx('menacing', 0.8);
    S.mark('pro_cap_shadow');
    await S.wait(0.6);
    S.sfxText('呀嘞呀嘞daze', { x: 470, y: 290 }, { dur: 1.6 });
    await S.say('jotaro', '呀嘞呀嘞daze。');
    m1.stop(); m2.stop();
    fb.close();
    F().jailOut = true;
  }

  // ================================================================ 序-6 空条家（白天，自由）
  async function talkHolly6(S) {
    const n = cnt('holly6');
    if (n % 3 === 1) {
      await S.say('holly', '爸爸难得来日本，晚饭我要做一大桌！阿布德尔先生，您吃不吃纳豆？');
      await S.say('avdol', '……我试试。');
    } else if (n % 3 === 2) {
      await S.say('holly', '承太郎小时候可乖了，每天都说“妈妈最好了”……');
      await S.say('jotaro', '……别说了。');
    } else {
      await S.say('holly', '大家怎么都这么严肃？是在聊什么好玩的事吗？');
    }
  }
  const memberTalk6 = {
    joseph: async (S) => {
      const n = cnt('jo6');
      if (n === 1) await S.say('joseph', '你外公我也有替身，叫『隐者之紫』。先别问，待会儿让你看样东西。');
      else F().p7 = true;
    },
    avdol: async (S) => {
      const n = cnt('av6');
      if (n % 3 === 1) await S.say('avdol', '我的力量是天生的。但你和乔斯达先生不一样——你们的替身，是最近才醒过来的。');
      else if (n % 3 === 2) { await S.say('avdol', '替身用塔罗牌起名字。你那一个，我想叫它『星星』。'); await S.say('jotaro', '……随你。'); }
      else await S.say('avdol', '乔斯达家的人这个时候一起醒过来……我有不好的预感。');
    },
    jotaro: async (S) => {
      const n = cnt('jt6');
      if (n % 2 === 1) await S.say('jotaro', '……那个藤蔓老头真是我外公？');
      else await S.say('jotaro', '……吵死了。');
    },
  };
  function setupKujo6(S) {
    const st = G.STAGES.kujo_pro;
    st.props = [];
    st.npcs = [T().npc('holly', 'holly', 170, 160, { name: '荷莉', label: '荷莉', talk: talkHolly6 })];
    st.hotspots = [
      {
        id: 'tokonoma', x: 90, y: 150, ly: 100, r: 18, ry: 7, label: '壁龛挂轴',
        use: async (S, h, L) => S.say(L.cid, by(L, { jotaro: '……老妈挑的。', joseph: '富士山。Holly 的品味随她妈妈。', avdol: '好画。山的气很稳。' })),
      },
      {
        id: 'furin', x: 214, y: 152, ly: 40, r: 16, label: '风铃', tags: ['life'],
        use: async (S, h, L) => S.say(L.cid, by(L, { jotaro: '叮叮响。', joseph: '日本的夏天声音。', _: '……风铃。' })),
        look: async (S, h, L) => S.say('avdol', '风铃后面……躲着一只壁虎。生命探测不会说谎。'),
      },
      {
        id: 'garden', x: 270, y: 152, ly: 120, r: 18, label: '庭院池塘', tags: ['detail'],
        use: async (S, h, L) => S.say(L.cid, by(L, { joseph: '锦鲤！真想钓一条。', avdol: '水很静。', _: '……池塘。' })),
        look: async (S) => S.say('jotaro', '池子里第三条锦鲤，尾巴缺了一块。……没事干的时候我会数。'),
      },
      {
        id: 'teatable', x: 90, y: 174, ly: 156, r: 18, ry: 7, label: '矮桌茶具',
        use: async (S, h, L) => S.say(L.cid, by(L, { jotaro: '凉了。', joseph: '日本茶……苦，但我喜欢。', avdol: '乔斯达先生喝了三杯。' })),
      },
      {
        id: 'camera', x: 90, y: 162, ly: 146, r: 18, ry: 6, label: '拍立得相机', tags: ['nensha'], lookOnly: true,
        cameraAt: { x: 64, y: 150, z: 8 },
        use: async (S, h, L) => {
          if (L.cid === 'joseph') { F().p7 = true; return; }
          if (L.cid === 'avdol') { await S.say('avdol', '乔斯达先生的相机。……不，那是用来砸的。'); return; }
          await S.say('jotaro', '外公带来的拍立得。');
          S.hint('换成乔瑟夫试试（Q）', 4);
        },
        look: async () => { F().p7 = true; },
      },
    ];
    st.onLook = async (S, L) => {
      if (L.cid === 'joseph') { await S.say('joseph', '念写？好啊——'); F().p7 = true; return; }
      if (L.cid === 'avdol') { await S.say('avdol', '这座房子里有四个……不，五个生命。还有一只壁虎。'); return; }
      await S.say(L.cid, by(L, { jotaro: '……这家里只有老妈的东西。', _: '……' }));
    };
    st.triggers = [];
  }

  // ================================================================ 序-7 念写（照分镜 s03 0–10.33）
  async function nensha(S) {
    const jo = S.actor('joseph'), jt = S.actor('jotaro'), av = S.actor('avdol');
    S.hint(null);
    S.setLeader('jotaro', { force: true, silent: true });
    S.music('ominous', 0.6);
    // 站位：乔瑟夫在矮桌旁，承太郎、阿布德尔在右边
    await Promise.all([
      S.walk(jo, 104, 160, { speed: 80 }),
      S.walk(jt, 190, 164, { speed: 80 }),
      av ? S.walk(av, 244, 158, { speed: 80 }) : Promise.resolve(),
    ]);
    S.face(jo, -1); S.face(jt, jo); if (av) S.face(av, jo);
    S.pose(jo, 'camera');
    S.emote(jt, '？', 1.2);
    S.sfx('pop', 0.6);
    await S.say('joseph', '看好了！');
    // 1.71–1.77 六根紫色藤蔓从手臂爆出；隐者之紫替身卡；手刀劈相机
    S.face(jo, -1);
    for (let i = 0; i < 6; i++) {
      G.defer(i * 0.012, () => S.fx('vines', { x0: jo.x - 6, y0: jo.y - 28, x1: jo.x - 14 - i * 5, y1: jo.y - 46 - (i % 3) * 8, t1: 0.3, colour: 'purple', strands: 1, seed: i }, { life: 1.2 }));
    }
    S.sfx('vine', 0.9);
    S.standCard('hermit', { side: 'right' });
    S.cue('sting_reveal');
    await S.wait(0.5);
    S.fx('crack', { x: 64, y: 140, size: 18 });
    S.fx('hit_spark', { x: 64, y: 140, size: 14, accent: '#d0a0ff' });
    S.fx('shockwave', { x: 64, y: 142, r_max: 30, width: 2 });
    S.impact('invert');
    S.sfxText('バキッ!!', { wx: 64, wy: 150, wz: 30 }, { dur: 0.9, jitter: 2 });
    S.sfx('crash', 0.8); S.sfx('punch', { seed: 0, vol: 0.8 });
    const cam = (G.world.stage.actors || []).find((a) => a.cid === 'prop:camera');
    if (cam) cam.remove = true;
    S.mark('pro_camera_chop');
    await S.wait(0.35);
    S.sfx('camera_shutter');
    // 空白相片飞向镜头
    T().floater(S, 'scene:s03_photo_blank', 64, 150, { z: 12, rise: 40, dur: 0.6, dx: 60 });
    S.sfx('zoom', 0.8);
    await S.wait(0.6);
    S.unpose(jo);
    // 3.58–6.42 menace 底上相片显影：DIO 背影、回头的红眼、颈后星形胎记
    //   照片 16×20、中心锚点：×5 放在 y 68，整张都在底部对话框（世界 y 136 起）上面
    const ph = T().insert(S, {
      bg: 'menace', colours: ['#3a1040', '#12061a'],
      parts: [{ kind: 'sprite', cid: 'prop:photo', anim: 'idle', frame: 0, x: 160, y: 68, scale: 5 }],
    });
    S.mark('pro_photo');
    await S.say('joseph', '我的替身能把远处的景象“写”进照片里。这叫念写。');
    S.sfx('heartbeat', 0.8);
    ph.parts[0].frame = 1;
    await S.wait(0.8);
    S.sfx('heartbeat', 0.9);
    ph.parts[0].frame = 2;
    S.cue('sting_shock');
    S.fx('glint', { x: 167, y: 54, size: 10 }, { space: 'canvas', tag: 'insert' });
    await S.wait(0.6);
    await S.say('jotaro', '……这家伙是谁。');
    await S.say('joseph', 'DIO夺走了我祖父乔纳森的身体！', { expr: 'grave' });
    await S.say('joseph', '将近一百年前，他和我祖父一起沉进了大海。四年前，他的棺材被人从大西洋里捞了上来。', { expr: 'grave' });
    ph.close();
    await S.say('avdol', '他的头，接在乔纳森的身体上。所以乔斯达家的人，都被他牵着醒了过来。', { expr: 'grave' });
    await S.say('joseph', '承太郎，你脖子后面，是不是有一颗星形的胎记？');
    // 6.42–10.33 承太郎脸部特写转愤怒 → 背影回头，颈后胎记闪光，ゴゴゴ ×4
    const cu = await T().closeup4(S, { cid: 'jotaro', expr: 'normal', bg: 'menace', colours: ['#2a1a50', '#0a0418'], hold: true, impact: false });
    await S.wait(0.5);
    cu.parts[0].expr = 'angry';
    S.shake(1, 0.2);
    await S.wait(0.6);
    cu.close();
    const back = T().insert(S, { bg: 'menace', colours: ['#2a1a50', '#0a0418'], parts: [{ kind: 'sprite', cid: 'scene:s03_jotaro_back', anim: 'idle', frame: 0, x: 160, y: 178, scale: 3 }] });
    const mm = S.menacing({ x: 520, y: 140, n: 4, seed: 4 });
    S.sfx('menacing4', 0.8);
    G.defer(0.4, () => { back.parts[0].frame = 1; S.fx('glint', { x: 150, y: 62, size: 9 }, { space: 'canvas', tag: 'insert' }); });
    G.defer(0.9, () => { back.parts[0].frame = 2; S.fx('glint', { x: 150, y: 62, size: 9 }, { space: 'canvas', tag: 'insert' }); });
    S.mark('pro_birthmark');
    await S.say('jotaro', '……乔斯达家的宿命吗。');
    mm.stop();
    back.close();
    await S.say('jotaro', '……相机碎了。');
    await S.say('joseph', '念写一次就得砸一台，相机钱可不便宜……回头记在 SPW 财团的账上！');
    // 夜：同一张地图换夜景 2 s → 黑场中央一双发光的眼睛 → 第二天早上
    await S.setStage('kujo_pro', { bg: 'kujo_house_night', x: 190, y: 164, music: null });
    S.stopMusic(1.0);
    await S.wait(2.0);
    await S.fadeOut(0.6);
    const eyes = T().show(S, { bg: 'black', parts: [{ kind: 'sprite', cid: 'scene:s11_eyes', anim: 'idle', frame: 0, x: 160, y: 92, scale: 2 }] });
    G.fadeA = 0;
    G.defer(1.2, () => { eyes.parts[0].frame = 1; G.defer(0.12, () => { eyes.parts[0].frame = 0; }); });
    S.sfx('heartbeat', 0.5);
    await S.narrate('那天夜里，远在某处，有一双眼睛睁开了。', { pos: 'bottom' });
    eyes.close();
    G.fadeA = 1;
    await S.narrate('第二天早上', { pos: 'center', onBlack: true, auto: 1.5 });
  }

  // ================================================================ 序-8 上学路（自由，只有承太郎）：坡顶小路 → 长石阶 → 序-8b → 校门
  //   用户 2026-10-09 晚：“对话里说是有楼梯，但这里并没有真正做一个下楼梯的场景……在动漫里确实是在一个下楼梯的场景触发的”。
  //   新地图 stairs_pro（背景 school_stairs，640 宽）：坡顶小路 x < 184，20 级石阶往右下走到 x 404 的人行道。
  //   纵深带固定 y 150–160，人站在台阶上的高度 = z（坡顶 80，每级低 4 px，人行道 0），背景 anchors.stairs 是同一组数。
  //   走到第 8 级（anchors.trip_x）→ 序-8b 绊倒、滚下去；之后往右走到头（x ≥ 600）去学校 → school_pro（校门）→ 走进校门 → 序-9
  const STAIRS = { x0: 184, run: 11, rise: 4, n: 20, top: 80 };
  const stairsGeo = () => {
    const st = G.world.stage, a = st && st.id === 'stairs_pro' && st.anchors && st.anchors.stairs;
    return a || (G.D && G.D.bg && G.D.bg.school_stairs && G.D.bg.school_stairs.anchors.stairs) || STAIRS;
  };
  const stairsAnchor = (k, dflt) => (G.D && G.D.bg && G.D.bg.school_stairs && G.D.bg.school_stairs.anchors[k]) || dflt;
  // 台阶面离人行道多高（= 人的 z）：和 tools\bg_new\school_stairs.py 的 height() 一个算法
  function stairZ(x) {
    const s = stairsGeo();
    if (x < s.x0) return s.top;
    const i = Math.floor((x - s.x0) / s.run);
    return i >= s.n ? 0 : s.top - s.rise * (i + 1);
  }
  const isWalker = (a) => typeof a.cid === 'string' && !/^(prop|scene):/.test(a.cid);
  // 每帧按 x 给台阶上的人（承太郎、两个女生、花京院）设高度；影子不用引擎的（引擎把影子画在纵深线上，人在坡顶时会落到石垣上），
  //   改由下面的 stairShadows 画在脚下那一级台阶上。剧情自己摆高度时（滚下台阶）给人设 mem.stairManual
  function stairsTick() {
    T().tick(() => {
      const st = G.world.stage;
      if (!st || st.id !== 'stairs_pro') return true;
      for (const a of st.actors) {
        if (a.remove || !isWalker(a) || a.mem.stairManual) continue;
        a.z = stairZ(a.x);
        a.shadow = false;
      }
      return false;
    });
  }
  const stairShadows = {
    type: 'custom', id: 'stair_shadows', x: 0, y: 0, depth: -1,
    draw(g, ox, oy) {
      const st = G.world.stage;
      if (!st || st.id !== 'stairs_pro') return;
      g.fillStyle = 'rgba(28,22,40,0.30)';
      for (const a of st.actors) {
        if (a.remove || !a.visible || a.alpha <= 0.3 || !isWalker(a)) continue;
        const x = Math.round(a.x + ox), y = Math.round(a.y - stairZ(a.x) + oy);
        g.fillRect(x - 6, y - 1, 13, 2); g.fillRect(x - 4, y - 2, 9, 1); g.fillRect(x - 4, y + 1, 9, 1);
      }
    },
  };
  function setupStairs(S) {
    const st = G.STAGES.stairs_pro;
    st.props = [stairShadows];
    st.npcs = [
      T().npc(S.cid('npc_student_f_a', 'scene:s09_woman'), 'girlA', 34, 154, { facing: 1, name: '女生A', label: '女生A', talk: talkGirlA }),
      T().npc(S.cid('npc_student_f_b', 'scene:s09_woman'), 'girlB', 22, 158, { facing: 1, name: '女生B', label: '女生B', talk: talkGirlB }),
    ];
    // 调查点的 y 在纵深带里（选中范围按脚底算），ly = 标签画在东西上面（坡顶的东西要减掉台阶高度 80）
    st.hotspots = [
      { id: 'sakura', x: 92, y: 155, ly: 22, r: 16, label: '樱花树', use: async (S2) => S2.say('jotaro', '……春天了。') },
      {
        id: 'view', x: 166, y: 155, ly: 44, r: 16, label: '远处的学校', tags: ['detail'],
        use: async (S2) => S2.say('jotaro', '学校就在下面。……这段石阶，一天走两趟。'),
        look: async (S2) => S2.say('jotaro', '……石阶下面，有个人一直站着往这边看。'),
      },
      { id: 'mirror', x: 432, y: 155, ly: 92, r: 14, label: '转角镜', use: async (S2) => S2.say('jotaro', '镜子里映着整条石阶。') },
    ];
    st.onLook = async (S2) => S2.say('jotaro', '……樱花。全是普通人。');
    st.triggers = [
      { id: 'trip', x0: stairsAnchor('trip_x', 265), x1: 404, run: async (S2) => { await stairsFall(S2); } },
      { id: 'to_school', x0: 600, x1: 999, cond: () => !!F().p8b, run: async () => { F().p8c = true; } },
    ];
  }
  // 校门（序-8 后半）：从石阶那边走过来，走进校门（门口那一段往上走）= 去保健室
  function setupSchool(S) {
    const st = G.STAGES.school_pro;
    st.props = [];
    const boyCid = S.cid('npc_student_m', 'npc_student_f_b', 'scene:s09_man');
    st.npcs = [
      T().npc(boyCid, 'boy', 300, 152, { facing: -1, name: '男生', label: '男生', talk: talkBoy }),
    ];
    st.hotspots = [
      { id: 'gate_plaque', x: 200, y: 146, ly: 120, r: 16, label: '校名牌', use: async (S) => S.say('jotaro', '门牌被樱花挡住了。……无所谓。') },
      { id: 'sakura', x: 150, y: 146, ly: 100, r: 16, label: '樱花树', use: async (S) => S.say('jotaro', '……春天了。') },
      { id: 'gate', x: 282, y: 146, ly: 128, r: 12, label: '铁门', use: async (S) => S.say('jotaro', '迟到也无所谓。') },
    ];
    st.onLook = async (S) => S.say('jotaro', '……樱花。全是普通人。');
    // 校门开着的那一段（门柱 x 206–262，右边半扇铁门关着）：走到门口再往上走（y ≤ 145）就进去了
    st.triggers = [
      { id: 'to_infirmary', x0: 212, x1: 258, y0: 0, y1: 145, cond: () => !!F().p8b, run: async () => { F().p9go = true; } },
    ];
  }
  async function talkGirlA(S, me) {
    const n = cnt('girlA');
    if (n % 2 === 1) {
      await T().say(S, me, 'JoJo！今天也好帅！');
      await S.say('jotaro', '……吵死了。');
      T().floater(S, 'scene:s02_heart', me.x, me.y + 0.5, { z: 44, rise: 14, dur: 1.2 });
      await T().say(S, me, '被他骂了～');
    } else {
      await T().say(S, me, 'JoJo，书包我帮你拿吧？');
      await S.say('jotaro', '不用。');
    }
  }
  async function talkGirlB(S, me) {
    const n = cnt('girlB');
    if (n % 2 === 1) await T().say(S, me, '听说昨天转来一个新同学，好像叫……花京院？');
    else await T().say(S, me, '他一直站在石阶下面往这边看，有点吓人呢。');
  }
  async function talkBoy(S, me) {
    const n = cnt('boy');
    if (n % 2 === 1) {
      if (me.atlas && me.atlas.has && me.atlas.has('bow')) S.act(me, 'bow');
      await T().say(S, me, '空、空条同学早！');
      await S.say('jotaro', '……嗯。');
    } else await T().say(S, me, '今天第一节是体育……啊，你肯定不上。');
  }
  // 序-8b 石阶上的“意外”（用户 2026-10-09：动漫里是在下楼梯时出的事）：再往下迈一级，脚边一根细细的绿线闪一下（法皇的触须，
  //   只亮 4 帧）→ 一脚踩空，顺着石阶一路磕下去（空中“受击”、落在台阶上趴一下，每下“咚”一声扬灰）→ 摔在人行道上
  //   → 镜头推近：左膝的裤子划开一道口子（不画血）→ 花京院从学校那边走过来递纸巾。两个女生留在台阶上面尖叫
  //   原著（Wiki 核过）：下楼梯时被绊倒、左膝划破、花京院递纸巾
  async function stairsFall(S) {
    const p = S.player, s = stairsGeo();
    S.hint(null);
    const girls = ['girlA', 'girlB'].map((id) => S.actor(id)).filter(Boolean);
    for (const g of girls) { g.follow = null; g.paused = false; g.state = 'idle'; g.play(g.idleAnim || 'idle'); }
    // 再往下迈一级（站到那一级踏面的中间）
    const i0 = G.clamp(Math.floor((p.x - s.x0) / s.run), 0, s.n - 1);
    const xStep = s.x0 + Math.min(s.n - 1, i0 + 1) * s.run + Math.floor(s.run / 2);
    if (Math.abs(p.x - xStep) > 1) await S.walk(p, xStep, p.y, { speed: 40 });
    S.face(p, 1);
    const zy = p.y - stairZ(p.x);
    S.fx('tendrils', { pts: [[p.x - 12, zy - 1], [p.x + 2, zy - 2], [p.x + 14, zy - 1]], colour: '#50e890', wiggle: 0.5 }, { life: 4 / 60 + 0.02 });
    await S.wait(0.07);
    // 踩空：往前栽，一路磕到人行道（每下滚过 3 级左右）
    p.mem.stairManual = true;
    S.sfx('whoosh', { vol: 0.5, rate: 1.5 });
    const land = stairsAnchor('bottom', [418, 156]);
    const xs = [xStep + 30, xStep + 64, xStep + 100, land[0]].map((x) => Math.min(x, land[0]));
    let x0 = p.x;
    for (let k = 0; k < xs.length; k++) {
      const x1 = xs[k], last = k === xs.length - 1;
      if (x1 <= x0) continue;
      p.rot = 0.35;
      S.pose(p, 'hurt');
      if (k === 1) S.mark('pro_stairs_tumble');
      await S.arc(p, x1, p.y, last ? 7 : 10, last ? 0.24 : 0.22, { z1: stairZ(x1), spin: 0.5, anim: 'hurt' });
      p.rot = 0;
      S.pose(p, 'down');
      p.z = stairZ(x1);
      S.sfx('thud', last ? 0.95 : 0.7);
      S.fx('dust', { x: x1, y: p.y - p.z, n: last ? 10 : 6, speed: last ? 60 : 40 });
      S.shake(last ? 2.5 : 1.2, last ? 0.25 : 0.12);
      if (!last) await S.wait(0.06);
      x0 = x1;
    }
    p.mem.stairManual = false;
    S.mark('pro_stairs_landed');
    // 台阶上面的两个女生（在镜头外）尖叫
    for (const g of girls) S.emote(g, '！', 1.0);
    if (girls[0]) await T().say(S, girls[0], 'JoJo——！');
    await S.wait(0.3);
    S.unpose(p);
    S.face(p, 1);
    // 镜头推近：左膝的裤子划开一道口子（不画血）——膝盖上画一道浅色的口子，只在这一段
    const st = G.world.stage;
    const slit = { type: 'custom', id: 'knee_slit', x: 0, y: 0, depth: p.y + 0.6, draw(g, ox, oy) {
      const pl = G.world.player; if (!pl) return;
      const f = pl.facing < 0 ? -1 : 1, x = Math.round(pl.x + 4 * f + ox), y = Math.round(pl.y - pl.z - 9 + oy);
      g.fillStyle = '#141830'; g.fillRect(x - 2, y - 1, 5, 1); g.fillRect(x - 2, y + 1, 5, 1);
      g.fillStyle = '#f0c4a0'; g.fillRect(x - 1, y, 3, 1);
    } };
    if (st) st.props.push(slit);
    await S.zoom(2.4, p.x + 3, p.y - 14, 0.3);
    S.mark('pro_knee_slit');
    await S.say(null, '左膝的裤子被划开了一道口子。');
    await S.zoom(1, null, null, 0.3);
    if (st) st.props = st.props.filter((q) => q !== slit);
    // 花京院从学校那边（右边）走过来
    const kak = S.spawn('kakyoin', 620, 155, { id: 'kakyoin_s', facing: -1 });
    await S.walk(kak, land[0] + 28, 155, { speed: 55 });
    S.nameCard('kakyoin', { y: NAME_TOP });
    await S.say('kakyoin', '你没事吧？膝盖划破了。……用这个擦一下吧。', { actor: kak });
    const tissue = T().prop(S, 'tissue', kak.x - 6, 155.5, { id: 'tissue_hand', z: 26 });
    if (tissue) { S.mark('pro_stairs_tissue'); await S.arc(tissue, p.x + 4, 155.5, 6, 0.35, { z1: 26 }); tissue.remove = true; }
    S.sfx('pop', 0.5);
    await S.say('jotaro', '……你是谁。');
    await S.say('kakyoin', '花京院典明。昨天刚转来。', { actor: kak });
    await S.walk(kak, 640, 155, { speed: 45 });
    kak.remove = true;
    await S.say('jotaro', '……刚才那一下，不是我自己绊倒的。');
    F().p8b = true;
    T().goal(S, { x: 612, y: 155, label: '学校', every: 15, done: () => !!F().p8c, text: '去保健室包扎一下（往右走，去学校）' });
  }
  // 跟着承太郎走的 NPC：承太郎转身朝她们走过去（56 px 内）就站住，好让人搭话；走开 80 px 以上再跟上
  function followersPause(S, list, stop) {
    T().tick(() => {
      if (stop()) return true;
      const p = S.player;
      if (!p) return false;
      for (const [id, slot] of list) {
        const g = S.actor(id);
        if (!g || g.remove) continue;
        const dx = g.x - p.x, d = Math.abs(dx) + Math.abs(g.y - p.y) * 0.5;
        if (g.follow && d < 56 && Math.sign(dx) === p.facing) {
          g.follow = null; g.paused = true; g.state = 'idle'; g.play(g.idleAnim || 'idle'); g.facing = dx > 0 ? -1 : 1;
        } else if (!g.follow && g.paused && d > 80 && !S.busy) {
          g.paused = false; S.follow(g, 'player'); g.followSlot = slot;
        }
      }
      return false;
    });
  }

  // ================================================================ 序-9 保健室（自由 → 纸巾字条 → 校医被操纵 → QTE）
  function setupInfirmary(S) {
    const st = G.STAGES.infirmary_pro;
    st.props = [];
    st.npcs = [
      T().npc(S.cid('npc_nurse', 'npc_student_f_b', 'scene:s09_woman'), 'nurse', 230, 156, { facing: -1, name: '校医', label: '校医', talk: talkNurse,
        onStand: async (S2, me) => { S2.emote(me, '……', 1.4); await T().say(S2, me, '……'); } }),
      T().npc(S.cid('npc_student_f_a', 'scene:s09_woman'), 'girlC', 90, 150, { facing: 1, name: '女生C', label: '女生C', talk: talkGirlC }),
    ];
    st.hotspots = [
      { id: 'cabinet', x: 263, y: 152, ly: 90, r: 16, label: '药柜', use: async (S) => S.say('jotaro', '消毒水、绷带……一切正常。') },
      { id: 'door', x: 299, y: 154, ly: 92, r: 12, label: '门', use: async (S) => S.say('jotaro', '……包扎完再走。') },
      {
        id: 'window', x: 180, y: 152, ly: 64, r: 16, label: '窗', tags: ['detail'],
        use: async (S) => S.say('jotaro', '窗外是樱花。'),
        look: async (S) => S.say('jotaro', '窗外的树上……有一根绿色的线，一直连到楼上。'),
      },
      { id: 'curtain', x: 48, y: 152, ly: 110, r: 14, label: '布帘', use: async (S) => S.say('jotaro', '白色的布帘。') },
      {
        // 纸巾是承太郎身上的调查点：坐到床边以后才出现（E / U 都行）
        id: 'tissue', x: 130, y: 156, r: 22, ry: 14, label: '纸巾', tags: ['detail'], cond: () => !!F().sat && !F().noteRead,
        use: async (S) => { F().noteRead = true; },
        look: async (S) => { F().noteRead = true; },
      },
    ];
    st.onLook = async (S) => S.say('jotaro', '……老师的影子，有一点绿。');
    st.triggers = [];
  }
  async function talkGirlC(S, me) {
    const n = cnt('girlC');
    if (n % 2 === 1) await T().say(S, me, 'JoJo 也来保健室？……今天运气真好～');
    else await T().say(S, me, '老师今天好像怪怪的，一直不说话。');
  }
  async function talkNurse(S, me) {
    if (F().sat) { await T().say(S, me, '……'); return; }
    await T().say(S, me, '哎呀，空条同学也会受伤？坐到床边来，我给你消毒。');
    const p = S.player;
    await S.walk(p, 130, 156, { speed: 60 });
    S.face(p, 1);
    S.pose(p, 'sit');
    F().sat = true;
    S.hint('看看花京院给的那张纸巾（按 E）', 30);
  }
  async function infirmaryQte(S) {
    const p = S.player, nurse = S.actor('nurse'), girl = S.actor('girlC');
    S.hint(null);
    // 〔特写〕纸巾上用墨水写着字
    const pn = S.panel('tissue_note', { pop: 0.2 });
    S.mark('pro_tissue_note');
    await S.wait(0.4, 'ui');
    S.cue('sting_shock');
    await S.wait(2.2, 'ui');
    pn.close(0.2);
    await S.wait(0.25, 'ui');
    S.unpose(p);
    // 校医的眼睛变绿，拿起钢笔转向女生 C
    if (nurse) {
      S.pose(nurse, 'possessed');
      S.emote(nurse, '！', 0.6, '#70ffb0');
      const pen = T().prop(S, 'pen', nurse.x - 6, nurse.y + 0.5, { id: 'pen', z: 24 });
      await S.walk(nurse, 112, 152, { speed: 60, anim: 'possessed' });
      S.face(nurse, -1);
      if (pen) { pen.x = nurse.x - 8; pen.y = nurse.y + 0.5; }
      S.pose(nurse, 'stab');
      // QTE 1：0.5 s 内按 L → 白金之星截住钢笔（没按到也会截住，只是承太郎吃 10 伤）
      //   QTE 框放到画面上方（y 44，上面留出“成功！”的位置）：默认在正中，会把钢笔、校医和承太郎整个挡住
      const q1 = await S.press({ key: 'guard', window: 0.5, label: 'L！', failOk: true, y: 44 });
      S.face(p, -1);
      S.summon(p, { dur: 0.12, rise: 4 });
      S.standAct(p, 'block', { dx: 26, hold: true });
      S.fx('hit_spark', { x: 100, y: 128, size: 8, accent: '#b090ff' });
      S.sfxText('ガシッ', { wx: 100, wy: 140, wz: 20 });
      S.sfx('parry', 0.8);
      if (q1 === 'miss') { p.hp = Math.max(1, (p.hp || 130) - 10); p.flash = 1; S.shake(2, 0.2); S.sfx('punch', { vol: 0.6 }); }
      if (girl) { S.emote(girl, '！', 0.5); await S.wait(0.3); S.pose(girl, 'down'); S.sfx('thud', 0.5); }
      await S.wait(0.4);
      if (S.player.stand) S.player.stand.idle();
      // QTE 2：校医转身扎向承太郎（精准格挡教过了；按不准也照样过）
      S.face(nurse, 1);
      await S.walk(nurse, 116, 156, { speed: 80, anim: 'possessed' });
      S.pose(nurse, 'stab');
      const q2 = await S.press({ key: 'guard', window: 0.4, perfect: 0.1, label: 'L——挡住她！', failOk: true, y: 44 });
      S.standAct(p, 'block', { dx: 14, hold: true });
      S.sfxText('ガシッ', nurse);
      S.sfx(q2 === 'perfect' ? 'parry' : 'guard', 0.9);
      if (q2 === 'perfect') S.fx('glint', { x: 120, y: 126, size: 8 });
      if (q2 === 'miss') { p.hp = Math.max(1, (p.hp || 130) - 10); p.flash = 1; S.shake(2, 0.2); }
      if (q2 === 'perfect') await S.say('jotaro', '……慢了。');
      // 从她嘴里扯出一团绿色的触须（原著：从嘴里把法皇扯出来）
      const tn = S.fx('tendrils', { pts: [[nurse.x, nurse.y - 36], [nurse.x + 8, nurse.y - 40], [p.x - 10, p.y - 30]], colour: '#50e890', grow: 0.4 }, { life: 0.6 });
      S.sfx('hiero_tentacle', 0.9);
      await S.wait(0.5);
      S.killFx(tn);
      if (pen) pen.remove = true;
      S.pose(nurse, 'faint');
      S.sfx('thud', 0.6);
      await S.recall(p);
    }
    await S.say('jotaro', '……出来。躲在后面操纵别人的家伙。', { expr: 'angry' });
    // 花京院推开保健室的门走进来（门在右边 x 283–315）
    S.state('door', 1); S.sfx('door', 0.7);
    await S.wait(0.25);
    const kak = S.spawn('kakyoin', 299, 152, { id: 'kakyoin_i', facing: -1 });
    await S.walk(kak, 282, 156, { speed: 40, anim: 'possessed' });   // 别贴着右边缘：最后的推镜要把他的额头放在画面里
    S.pose(kak, 'possessed');
    const mg = S.menacing({ actor: kak, n: 3 });
    S.sfx('menacing', 0.7);
    await S.say('kakyoin', '空条承太郎……DIO大人要你的命。', { expr: 'evil', actor: kak });
    await S.say('kakyoin', '我的『绿色法皇』能钻进任何人的身体。那位老师，只是借来用一下。', { expr: 'evil', actor: kak });
    await S.say('jotaro', '把女人和无关的人扯进来……我饶不了你。', { expr: 'angry' });
    // 〔推镜冲上去〕推到花京院额头：肉芽在扭（承太郎没看见，玩家看见）
    const sayLast = S.say('kakyoin', '那就到外面来吧。在这里打，倒下的可不止你一个。', { expr: 'evil', actor: kak, pos: 'top' });
    await S.punchIn(kak, { k: 3, dur: 0.14, dy: -40 });
    const bud = T().prop(S, 'fleshbud', kak.x + 1, kak.y + 0.6, { id: 'bud_i', z: 40, scale: 0.5 });
    S.mark('pro_fleshbud_peek');
    G.defer(0.5, () => { if (bud) bud.remove = true; });
    await sayLast;
    mg.stop();
    await S.zoom(1, null, null, 0.2);
    await S.walk(kak, 340, 156, { speed: 50 });
    kak.remove = true;
  }

  // ================================================================ 序-10 序2 被操纵的花京院（规划 §5.1.3）
  async function kakyoinPhase2(S, e, ctx) {
    const mg = S.menacing({ actor: e, n: 2, dur: 0.5 });
    await S.say('kakyoin', '别以为抓得住我。', { expr: 'evil', actor: e });
    mg.stop();
  }
  // 阶段 3：花京院站定，W6 切入「绿宝石水花——！」→ 26 颗全力水花；宝石飞到时按着 L（格挡 / 精准格挡）就演完（成功后 ctx.end()）
  function holdBrain(e, dt, ctx) {
    const p = G.world.player;
    if (p) e.facing = p.x > e.x ? 1 : -1;
    if (e.state !== 'hurt' && e.state !== 'broken') { e.state = 'idle'; if (e.anim !== (e.idleAnim || 'idle')) e.play(e.idleAnim || 'idle'); }
    return true;
  }
  async function kakyoinPhase3(S, e, ctx) {
    ctx.data.final = 1;
    const mg = S.menacing({ actor: e, n: 3 });
    await S.say('kakyoin', '这一击……你躲不开！', { expr: 'evil', actor: e });
    mg.stop();
    S.hint('全力的绿宝石水花——宝石飞来时按住 L，用替身正面挡下来！', 8);
    finalSplashDirector(S, e, ctx);
  }
  function finalSplashDirector(S, e, ctx) {
    const d = ctx.data;
    d.cyc = 0; d.phase3 = 'warn'; d.cycT = ctx.t; d.blocked = false; d.hurt = false; d.dodged = false;
    ctx.on('guard', () => { if (d.phase3 === 'fly') d.blocked = true; });
    ctx.on('parry', () => { if (d.phase3 === 'fly') d.blocked = true; });
    ctx.on('hurt', () => { if (d.phase3 === 'fly') d.hurt = true; });
    ctx.on('evade', () => { if (d.phase3 === 'fly') d.dodged = true; });
    ctx.on('graze', () => { if (d.phase3 === 'fly') d.dodged = true; });
    // 玩家贴脸或绕到他身后时，水花往反方向飞、永远挡不到（自动测试在这里转了 15 分钟）：
    //   预警开始先往空的那一边退开、转向玩家；发射那一刻再转一次
    const ARENA = [40, 440];
    const face = () => { const p = G.world.player; if (p) e.facing = p.x >= e.x ? 1 : -1; };
    const startWarn = () => {
      d.phase3 = 'warn'; d.cycT = ctx.t; d.blocked = false; d.hurt = false; d.dodged = false;
      const p = G.world.player;
      if (p && Math.abs(p.x - e.x) < 70) {
        const tx = (ARENA[1] - p.x) > (p.x - ARENA[0]) ? Math.min(ARENA[1] - 12, p.x + 90) : Math.max(ARENA[0] + 12, p.x - 90);
        Promise.resolve(G.combat.tweenTo(e, tx, p.y, 0.3)).catch(() => {});
        S.sfx('dodge', 0.5);
      }
      face();
      G.TPL.bossCutin({ portrait: 'kakyoin', expr: 'evil', title: 'w6_hg_splash', colours: ['#1c6a40', '#0a3a20'] });
      S.sfx('sting_shock', 0.8);
      S.fx('glow', { x: e.x + e.facing * 20, y: e.y - 30, r: 10, colour: '#70ffb0' }, { life: 1.0, follow: e, dx: 20, dy: -30 });
      S.sfxText('绿宝石水花！', e, { dur: 0.9 });
      if (d.cyc === 0) S.mark('pro_hg_final');
    };
    const fire = () => {
      d.phase3 = 'fly'; d.cycT = ctx.t;
      face();
      S.sfx('emerald', 0.9);
      for (let i = 0; i < 26; i++) {
        const a = (-24 + 48 * (i / 25)) * Math.PI / 180;
        G.defer((i % 6) * 0.05, () => {
          if (!G.world.fight) return;
          ctx.shoot(e, { kind: 'gem', speed: 320, vx: 320 * Math.cos(a) * e.facing, vy: 120 * Math.sin(a), dmg: 4, push: 2, hitR: [3, 3, 18], life: 1.4,
            reflect: false, guard: 'normal', x: e.x + e.facing * 20, y: e.y + Math.sin(a) * 4, z: 20 }, {});
        });
      }
    };
    startWarn();
    T().tick(() => {
      if (G.world.fight !== ctx || d.win) return true;
      const el = ctx.t - d.cycT;
      if (d.phase3 === 'warn' && el >= 1.0) fire();
      else if (d.phase3 === 'fly') {
        if (d.blocked) { d.win = true; return true; }
        // 宝石飞过去了没打中，但玩家一直面朝他按着 L：也算正面挡下（教学步骤，别让人卡住）
        const pl = G.world.player;
        if (el >= 1.3 && !d.hurt && pl && pl.state === 'guard' && (e.x - pl.x) * (pl.facing || 1) > 0) { d.win = true; return true; }
        if (el >= 1.3) {
          d.phase3 = 'rest'; d.cycT = ctx.t; d.cyc++;
          if (!d.hurt) S.hint('这一次，用替身正面挡住它（按住 L）', 4);
        }
      } else if (d.phase3 === 'rest' && el >= 2.0) startWarn();
      return false;
    });
  }
  async function fightKakyoin(S) {
    const p = S.player;
    const kak = S.spawn('kakyoin', 330, 150, { id: 'kakyoin_e', facing: -1, standPos: { dx: 20, z: 10, link: 'tendril' } });
    p.x = 150; p.y = 150; p.facing = 1;
    G.world.snapCamera && G.world.snapCamera();
    S.pose(kak, 'possessed');
    await S.summon(kak, { rise: 16, dur: 0.35, card: { side: 'right', y: 52 } });   // y 52：开战后不压右上 Boss 血条的尾巴
    await S.fight({
      id: 'b01_kakyoin', arena: [40, 440], lead: 'jotaro', swap: false, lockMsg: '这一战只能由承太郎应战',
      music: 'battle', after: null, vs: 'hiero', warnTier: 1, dmgScale: 0.8, energy: { start: 0 },
      losable: true, coverage: true, finish: 'none',
      waves: [[{
        kit: 'e_kakyoin', actor: 'kakyoin_e', cid: 'kakyoin', id: 'kakyoin_e', stand: 'hiero', name: '花京院典明', boss: true,
        hp: 600, poiseMax: 50, speed: 66, idle: 'possessed', koStyle: 'none', standPos: { dx: 20, z: 10, link: 'tendril' },
        phases: [
          { at: 0.5, run: kakyoinPhase2 },
          { at: 0.2, run: kakyoinPhase3, set: { brain: holdBrain, moves: [], pattern: null } },
        ],
      }]],
      onWave: async (S2, wi, spawned, attempt, ctx) => {
        S2.unpose(spawned[0]);
        if (attempt === 0) S2.hint('他躲在远处。靠近他的替身，触须甩过来的一瞬间按 L（精准格挡）就能抓住它！', 5);
        else await S2.say('kakyoin', '……再来几次都一样。', { expr: 'evil', actor: spawned[0] });
      },
      testHint: (ctx) => ({ phase: ctx.data.final ? 3 : ((ctx.boss && ctx.boss.phaseI) || 0) + 1, final: ctx.data.phase3 || null }),
      endWhen: (ctx) => !!ctx.data.win,
    });
  }

  // ================================================================ 序-11 欧拉（照分镜 s04 5.69–8.05）→「胜负已分」→ 扛回家
  async function oraFinish(S) {
    const p = S.player, kak = S.actor('kakyoin_e');
    S.hint(null);
    // 白金之星挡下水花、触须缠拳「ガシッ」、扯回
    if (kak) {
      S.standAct(p, 'block', { dx: 14, hold: true });
      S.sfxText('ガシッ', { wx: p.x + p.facing * 20, wy: p.y, wz: 30 });
      S.sfx('hiero_tentacle', 0.8);
      await S.wait(0.3);
      S.shake(2, 0.2);
      await S.walk(kak, p.x + p.facing * 30, p.y, { speed: 260, anim: 'hurt' });
    }
    // 漫画格 _ora_bg + starplat.rush + 拳影 + 每 0.085 s 一个火花 + ORA ×3
    S.letterbox(34);
    const ora = T().show(S, {
      bg: (P, t) => { const f = G.FX && G.FX.ora_bg; if (f) f(P, t, 160, 100); },
      parts: [{ kind: 'sprite', cid: 'starplat', anim: 'rush', x: 110, y: 168, scale: 2, aura: '#b090ff' },
        { kind: 'sprite', cid: 'kakyoin', anim: 'hurt', x: 238, y: 168, scale: 2, flip: true, jitter: 1.5 }],
    });
    S.fx('rush', { x: 150, y: 106, t1: 1.4, direction: 1, fist: 'starplat', spread: 30, rate: 34, reach: 16 }, { space: 'canvas', tag: 'insert' });
    const L = G.audio && G.audio.loop ? G.audio.loop('ora_loop', { vol: 0.9 }) : null;
    let k = 0;
    T().every(0.085, () => { k++; S.fx('hit_spark', { x: 200 + (k % 3) * 8, y: 96 + (k % 4) * 6, size: 12, accent: '#c080ff', seed: k }, { space: 'canvas', tag: 'insert' }); S.sfx('punch', { vol: 0.5, seed: k, rate: k % 2 ? 1.12 : 1.0 }); }, () => k >= 16);
    for (const [i, x] of [[0, 360], [1, 440], [2, 520]]) G.defer(0.06 + i * 0.3, () => S.sfxText('ORA', { x, y: 120 + i * 30 }, { dur: 0.6, jitter: 2.5 }));
    S.mark('pro_ora_rush');
    await S.wait(1.42);
    if (L && L.stop) L.stop(0.05);
    // 7.111 终结：帧 2、hit_spark 22、shockwave 70、invert → purple、ORA!! 64 号
    ora.parts[0].anim = 'punch'; ora.parts[0].frame = 2;
    S.impact(['invert', 'purple'], 1 / 24, 0.19);
    S.fx('hit_spark', { x: 214, y: 100, size: 22, accent: '#c080ff', dur: 0.3 }, { space: 'canvas', tag: 'insert' });
    S.fx('shockwave', { x: 214, y: 100, r_max: 70, width: 3 }, { space: 'canvas', tag: 'insert' });
    S.sfxText('ORA!!', { x: 430, y: 150 }, { dur: 1.0, jitter: 3 });
    S.sfx('ko_hit', 0.9); S.sfx('crit', 0.8);
    S.shake(4, 0.4);
    S.mark('pro_ora_finish');
    await S.wait(0.2);
    ora.close();
    // 7.30 花京院被打飞（抛物线 + 旋转 0 → −80°）落地、法皇白化消散
    if (kak) {
      if (kak.stand) kak.stand.recall({ dur: 0.25 });
      S.fx('speedlines', { style: 'horizontal', n: 30, inner: 8, alpha: 0.8 }, { space: 'canvas', life: 0.4 });
      await S.arc(kak, G.clamp(kak.x + p.facing * 90, 60, 420), 152, 26, 0.55, { spin: -80 * Math.PI / 180 });
      S.pose(kak, 'down');
      kak.rot = 0;
      S.fx('shockwave', { x: kak.x, y: kak.y, r_max: 30, squash: 0.25, width: 2 });
      S.fx('dust', { x: kak.x, y: kak.y, n: 10 });
      S.shake(3, 0.3);
      S.sfx('thud', 1.0);
    }
    S.letterbox(false);
    await S.title('draw', { y: 230, pop: 0.12, dur: 1.2, sfx: 'ko_hit' });
    S.sfx('jingle_victory', 0.7);
    if (G.input && G.input.lockOk) G.input.lockOk(0.8);
    await S.wait(0.8);
    // 承太郎走近，低头看昏迷的花京院
    if (kak) {
      await S.walk(p, kak.x - p.facing * 18, kak.y, { speed: 50 });
      S.face(p, kak);
    }
    await S.say('jotaro', '……');
    const face = await T().closeup4(S, { cid: 'kakyoin', expr: 'faint', bg: '#1a2a20', lines: false, impact: false, hold: true });
    await S.say('jotaro', '额头上……这是什么。');
    face.close();
    await S.say('jotaro', '带回去，问那个老头。');
    // 扛上肩：花京院倒下的帧旋转 90° 叠在肩上
    if (kak) {
      kak.hold = true;
      T().tick(() => { if (kak.remove) return true; kak.x = p.x - 2 * p.facing; kak.y = p.y + 0.4; kak.z = 34; kak.rot = Math.PI / 2 * -p.facing; return false; });
      await S.walk(p, 20, p.y, { speed: 40 });
    }
    await S.fadeOut(0.8);
  }

  // ================================================================ 序-12 空条家·肉芽（下午）→ 序-13 拔肉芽
  async function budScene(S) {
    const p = S.player;
    S.music('tension', 0.6);
    const holly = S.spawn('holly', 260, 158, { id: 'holly', facing: -1 });
    const kak = S.spawn('kakyoin', 40, 164, { id: 'kakyoin_lie', facing: 1 });
    kak.hold = true; kak.z = 34;
    T().tick(() => { if (kak.remove || F().kakDown) return true; kak.x = p.x - 2 * p.facing; kak.y = p.y + 0.4; kak.z = 34; kak.rot = -Math.PI / 2 * p.facing; return false; });
    const jo = S.actor('joseph'), av = S.actor('avdol');
    if (jo) { jo.x = 230; jo.y = 162; jo.facing = -1; }
    if (av) { av.x = 280; av.y = 154; av.facing = -1; }
    p.x = 20; p.y = 164; p.facing = 1;
    await S.fadeIn(0.6);
    await S.walk(p, 120, 164, { speed: 45 });
    S.emote(holly, '！', 0.6);
    S.sfx('pop', 0.5);
    await S.say('holly', '呀！承太郎带朋友回家了～是同学吗？要不要留下来吃饭？');
    await S.say('jotaro', '……他昏过去了。');
    // 花京院躺在榻榻米上
    F().kakDown = true;
    kak.x = 160; kak.y = 164; kak.z = 0; kak.rot = 0;
    S.pose(kak, 'down');
    S.zoom(1.6, 160, 150, 0.4);
    await S.say('avdol', '额头上……是DIO的肉芽。', { expr: 'grave' });
    await S.say('joseph', 'DIO用自己的细胞做成“芽”，种进人的脑子，人就会对他死心塌地。', { expr: 'grave' });
    await S.say('avdol', '已经扎得很深了。硬拔，触手会钻进拔它的人身体里。不拔……这个少年几天内就会死。', { expr: 'grave' });
    await S.zoom(1, null, null, 0.3);
    await S.say('jotaro', '那就拔。');
    await S.say('joseph', '你没听懂吗！它会钻进你的——', { expr: 'shock' });
    await S.summon(p, { dur: 0.3, rise: 10 });
    S.flash(0.07, 0.35, '#d8c0ff');
    await S.say('jotaro', '我的替身，手很稳。');
    // 序-13 小游戏（操作说明用乔瑟夫的台词讲：提示框在底部会和小游戏自己的“拔出 / 钻入”进度条叠在一起）
    S.hint(null);
    await S.say('joseph', '……好。方向键把替身的手指对准肉芽，按住 J 慢慢拔！手一偏开，触手就会往里钻！', { expr: 'grave' });
    S.mark('pro_pluck');
    await T().pluck(S);
    S.insert(null);
    // 8.77「ズルッ」、粉色碎屑、触手断开钻向承太郎手背
    S.sfxText('ズルッ', { x: 320, y: 140 }, { dur: 0.9, jitter: 2 });
    S.sfx('stab', { vol: 0.8, rate: 0.7 });
    const arm = T().insert(S, {
      bg: 'tatami_top',
      parts: [
        { kind: 'sprite', cid: 'scene:s04_jotarm', anim: 'idle', frame: 0, x: 220, y: 120, scale: 3 },
        { kind: 'sprite', cid: 'prop:fleshbud', anim: 'idle', x: 150, y: 110, scale: 3 },
      ],
    });
    S.fx('burst', { x: 150, y: 96, n: 16, speed: 70, colours: ['#e070b0', '#ffb0d8'], life: 0.5 }, { space: 'canvas', tag: 'insert' });
    await S.wait(0.7);
    arm.close();
    // 〔特写·全身×3〕乔瑟夫：就是现在——波纹！
    const jf = await T().fullbody3(S, { cid: 'joseph', anim: 'point', frame: 0, bg: 'radial', colours: ['#1a3a8a', '#0a1a4a'], aura: '#ffd83c', hold: true, x: 150, y: 176 });
    S.sfx('hamon', 0.6);
    await S.say('joseph', '就是现在——波纹！');
    jf.close();
    // 〔局部 insert〕乔瑟夫的前臂滑入，波纹 3 股 → 肉芽黄闪 → 炸成灰
    const ham = T().insert(S, {
      bg: 'tatami_top',
      parts: [
        { kind: 'sprite', cid: 'scene:s04_josarm', anim: 'idle', frame: 0, x: 340, y: 110, scale: 3 },
        { kind: 'sprite', cid: 'prop:fleshbud', anim: 'idle', x: 150, y: 110, scale: 3 },
      ],
      draw: (wg, t) => {
        if (t > 0.17) T().px(wg, (P) => { const h = G.FX && G.FX.hamon; if (h) h(P, 230, 96, 156, 92, t, { strands: 3, colour: '#ffd83c' }); });
      },
    });
    await S.animate(0.17, (k) => { ham.parts[0].x = 340 - 100 * k; });
    S.sfx('hamon', 0.9);
    await S.wait(0.48);
    ham.parts[1].hidden = true;
    S.fx('shatter', { src: 'prop:fleshbud', anim: 'idle', x: 150, y: 110, pieces: 30, scale: 3, tint_to: '#3a2c30', dur: 0.9 }, { space: 'canvas', tag: 'insert' });
    S.flash(0.1, 0.6, '#fff0a0');
    S.sfxText('バチバチッ', { x: 300, y: 150 }, { dur: 0.9, jitter: 2 });
    S.sfx('fire_burst', { vol: 0.45, rate: 1.6 });
    S.mark('pro_hamon');
    await S.wait(0.8);
    ham.close();
    // 花京院坐起
    kak.remove = true;
    const sit = T().prop(S, 'scene:s04_kaksit', 160, 164, { id: 'kak_sit', facing: 1 });
    await S.say('kakyoin', '……我……怎么在这里……', { actor: sit || undefined });
    await S.say('kakyoin', '为什么……要救我？', { actor: sit || undefined });
    S.pose(p, 'pose');
    await S.say('jotaro', '……谁知道呢。');
    S.unpose(p);
    await S.fadeOut(0.8);
    await S.narrate('那天夜里，什么都没有发生。——直到第二天早上。', { pos: 'center', onBlack: true });
    if (sit) sit.remove = true;
    holly.remove = true;
  }

  // ================================================================ 序-14 荷莉病倒（照分镜 s05 0–2.35）
  async function hollyFaints(S) {
    const p = S.player;
    S.music('daily', 0.3);
    const holly = S.spawn('holly', 170, 160, { id: 'holly', facing: -1 });
    for (const id of ['joseph', 'avdol', 'kakyoin']) { const a = S.actor(id); if (a) a.visible = false; }
    p.x = 330; p.y = 164; p.visible = true;
    await S.fadeIn(0.6);
    S.pose(holly, 'wave');
    // 哼着歌挥手，音符跟着 daily 的拍子飘出、ding ×6
    for (let i = 0; i < 6; i++) {
      G.defer(i * 0.1667, () => {
        if (F().hollyDown) return;
        T().floater(S, 'scene:s05_note0' + (i % 3), holly.x + 8, holly.y + 0.5, { z: 44, rise: 16, dur: 1.0, wave: 2 });
        S.sfx('ding', { vol: 0.35, rate: 1 + i * 0.05 });
      });
    }
    await S.wait(1.0);
    // 1.00「ドクン」停住 → 1.40 音乐抽空 → 1.55「ドサッ」倒地
    F().hollyDown = true;
    S.unpose(holly);
    S.sfxText('ドクン', holly, { dur: 0.6 });
    S.sfx('heartbeat', 0.9);
    S.pose(holly, 'faint');
    await S.wait(0.4);
    S.stopMusic(0.1);
    await S.wait(0.15);
    holly.visible = false;
    const down = T().prop(S, 'scene:s05_holly_down', holly.x, holly.y, { id: 'holly_down' });
    S.sfxText('ドサッ', { wx: holly.x, wy: holly.y, wz: 16 }, { dur: 0.7 });
    S.sfx('thud', 0.9);
    S.cue('sting_shock');
    S.impact('invert');
    S.music('sad', 0.5);
    S.fx('vines', { x0: holly.x - 4, y0: holly.y - 10, x1: holly.x + 16, y1: holly.y - 30, t1: 0.8, colour: ['#1a1030', '#3aa860', '#a8f090', '#8a44d8'], thorns: true, strands: 3 }, { life: 3.0 });
    S.mark('pro_holly_down');
    await S.wait(0.6);
    await S.walk(p, holly.x + 30, holly.y + 2, { anim: 'run', speed: 110 });
    S.face(p, -1);
    S.pose(p, 'shock');
    await S.say('jotaro', '……老妈！？');
    S.unpose(p);
    await S.fadeOut(0.6);
    if (down) down.remove = true;
    holly.remove = true;
  }

  // ================================================================ 序-15 卧室（照分镜 s05 2.35–6.65）→ 序-16 找 DIO（自由 / 解谜）
  function setupBedroom(S) {
    const st = G.STAGES.bedroom_pro;
    const medicCid = S.cid('scene:s19_medic');
    st.props = [];
    st.npcs = [
      T().npc('holly', 'holly', 150, 166, { name: '荷莉', label: '荷莉', anim: 'bed', facing: 1, noTurn: true, talk: talkHollyBed }),
      T().npc(medicCid, 'medic', 60, 158, { name: 'SPW 财团的医生', label: 'SPW 医生', facing: 1, talk: talkMedic }),
    ];
    st.hotspots = [
      {
        id: 'photo', x: 250, y: 170, r: 16, ry: 10, label: '念写的照片', tags: ['detail', 'nensha'],
        photo: { frames: [2, 2, 2] },
        use: async (S, h, L) => {
          if (L.cid === 'jotaro') { await S.say('jotaro', 'DIO 的背影。……背景太暗。'); return; }
          if (L.cid === 'joseph') { await S.say('joseph', '再念写一次？……相机的钱算我的。'); return; }
          if (L.cid === 'avdol') {
            if (F().flyFound) { F().p17 = true; return; }
            await S.say('avdol', '我总觉得照片里有什么……承太郎，你的眼睛比较尖。');
            return;
          }
          await S.say(L.cid, '……照片。');
        },
        look: async (S, h, L) => {
          if (L.cid === 'jotaro') { await findFly(S); return; }
          if (L.cid === 'joseph') { await S.say('joseph', '拍出来一样。线索一定就在这张照片里。'); return; }
          await S.say(L.cid, '……');
        },
      },
      {
        id: 'window', x: 210, y: 152, ly: 74, r: 16, label: '障子窗', tags: ['life'],
        use: async (S, h, L) => S.say(L.cid, by(L, { jotaro: '天黑了。', joseph: '东京的黄昏。……很久没看了。', _: '……' })),
        look: async (S) => S.say('avdol', '窗外没有敌人的气息。至少今晚没有。'),
      },
    ];
    st.onLook = async (S, L) => S.say(L.cid, by(L, {
      jotaro: '……老妈的呼吸很浅。', joseph: '这里没有相机……照片就在桌上。', avdol: '这间屋子里，Holly 女士的生命之火……在一点点变小。', _: '……',
    }));
    st.triggers = [];
  }
  async function talkHollyBed(S, me, L) {
    const lead = S.player;
    if (lead.cid === 'joseph') { await S.say('holly', '爸爸，对不起，让你担心了……', { expr: 'sick', actor: me }); return; }
    if (lead.cid === 'avdol') { await S.say('holly', '阿布德尔先生……纳豆，下次一定请您吃……', { expr: 'sick', actor: me }); return; }
    await S.say('holly', '大家……怎么都这个表情。妈妈没事的哦……', { expr: 'sick', actor: me });
    await S.say('jotaro', '……睡吧。');
  }
  async function talkMedic(S, me) { await T().say(S, me, '退烧药没有用。这不是普通的病。'); }
  async function talkKakyoin16(S) {
    const n = cnt('kak16');
    if (n % 2 === 1) await S.say('kakyoin', '被肉芽控制的那段时间，脑子里只有 DIO 的声音。');
    else await S.say('kakyoin', '你妈妈……是个好人。');
  }
  // 星之眼：〔POV〕照片放大 z 3，右下角的小黑点放大成一只苍蝇
  async function findFly(S, automatic = false) {
    S.hint(null);
    const ph = T().insert(S, { bg: '#1a1410', parts: [{ kind: 'sprite', cid: 'prop:photo', anim: 'idle', frame: 2, x: 160, y: 158, scale: 7 }] });
    await S.wait(0.4);
    S.fx('glint', { x: 196, y: 140, size: 8 }, { space: 'canvas', tag: 'insert' });
    S.sfx('glint', 0.8);
    await S.zoom(3, 196 + (G.cam ? G.cam.x : 0), 140 + (G.cam ? G.cam.y : 0), 0.3);
    S.mark('pro_fly');
    if (automatic) await S.narrate('承太郎：照片角落……有一只苍蝇。', { auto: 2 });
    else await S.say('jotaro', '照片角落……有一只苍蝇。');
    await S.zoom(1, null, null, 0.2);
    ph.close();
    F().flyFound = true;
    F().flyT = G.clk.world;
  }
  async function bedroomScene(S) {
    const p = S.player;
    await S.join('kakyoin');
    S.leadable('kakyoin', false, { msg: '……让我先看看你妈妈的情况。', look: 'gray' });
    const jo = S.actor('joseph'), av = S.actor('avdol'), kak = S.actor('kakyoin');
    for (const a of [jo, av]) if (a) a.visible = false;
    const jk = T().prop(S, 'scene:s05_joseph_kneel', 120, 158, { id: 'jo_kneel', facing: 1 });
    const ak = T().prop(S, 'scene:s05_avdol_kneel', 200, 158, { id: 'av_kneel', facing: -1 });
    p.x = 240; p.y = 170; p.facing = -1;   // y 170：站在榻榻米上托盘的前面（原来 158 正好踩在托盘上）
    if (kak) { kak.x = 270; kak.y = 158; kak.facing = -1; kak.visible = true; kak.follow = null; }
    S.music('sad', 0.5);
    await S.fadeIn(0.6);
    await S.say('avdol', '她的替身正在反噬她的身体……', { expr: 'grave', actor: ak || undefined });
    if (jk) { jk.visible = false; }
    const reach = T().prop(S, 'scene:s05_joseph_reach', 120, 158, { id: 'jo_reach', facing: 1 });
    await S.say('joseph', 'Holly 的身体撑不住替身。她一直忍着，什么都没跟我们说……', { expr: 'grave' });
    await S.say('joseph', '这样下去，她撑不过五十天！', { expr: 'grave' });
    // 〔特写〕荷莉病容 ×4 + 红色大字「50」「天」随心跳砸出
    const cu = await T().closeup4(S, { cid: 'holly', expr: 'sick', bg: 'menace', colours: ['#4a0a18', '#140006'], hold: true, impact: true });
    S.sfx('heartbeat', 0.9);
    S.sfx('punch_heavy', { vol: 0.8, rate: 0.6 });
    S.title('day50', { x: 290, y: 180, pop: 0.18, dur: 1.4 });
    await S.wait(0.8);
    S.sfx('heartbeat', 0.9);
    S.sfx('punch_heavy', { vol: 0.8, rate: 0.6 });
    S.mark('pro_50days');
    await S.title('day_unit', { x: 380, y: 196, pop: 0.18, dur: 1.0 });
    cu.close();
    await T().say(S, 'medic', 'SPW 财团会派医疗团队二十四小时守着她。……各位，请去做该做的事。');
    await S.say('joseph', '打倒 DIO，Holly 的替身就会停下来。可那家伙……到底在哪？');
    // 回到自由走动：跪着的两人站起来（换回队员本体）
    if (reach) reach.remove = true;
    if (jk) jk.remove = true;
    if (ak) ak.remove = true;
    if (jo) { jo.visible = true; jo.x = 120; jo.y = 160; }
    if (av) { av.visible = true; av.x = 200; av.y = 160; }
    T().prop(S, 'photo', 250, 170, { id: 'photo_prop', frame: 2, z: 2 });
    T().memberTalk({ kakyoin: talkKakyoin16 });
    S.hint('念写的照片放在矮桌上。换着人，按 U 看看。', 7);
    T().goal(S, { x: 250, y: 170, h: 24, label: '照片', delay: 7.5, every: 16, done: () => !!F().flyFound,
      text: '走到矮桌的照片前，换着人（Q）按 U 看看——谁的眼睛最尖？' });
    T().goal(S, { x: 250, y: 170, h: 24, label: '照片', every: 12, done: () => !!F().p17, when: () => !!F().flyFound && !S.busy,
      text: '照片角落有一只苍蝇——换成阿布德尔（Q），让他看看照片（按 E）' });
  }
  // 卡住保护（规划 §1.3 第 2 条）：40 s 提示 → 70 s 替玩家做完；找到苍蝇 20 s 后还没换阿布德尔 → 自动换人走过去
  async function autoFly(S) {
    S.setLeader('jotaro', { force: true });
    await S.walk(S.player, 236, 170, { speed: 70 });
    S.face(S.player, 1);
    const h = G.world.stage.hotspots.find((x) => x.id === 'photo');
    if (G.LOOK && G.LOOK.jotaro) await G.LOOK.jotaro.run(S, S.player, h);
    await findFly(S, true);
  }
  async function autoAvdol(S) {
    S.setLeader('avdol', { force: true });
    await S.walk(S.player, 236, 170, { speed: 70 });
    S.face(S.player, 1);
    F().p17 = true;
  }
  async function bedroomFree(S) {
    const t0 = now();
    let hinted = false, auto1 = false, auto2 = false;
    await S.until(() => {
      if (F().p17) return true;
      if (S.busy) return false;
      const el = now() - t0;
      if (!F().flyFound) {
        if (el > 40 && !hinted) { hinted = true; S.hint('阿布德尔：用替身的眼睛看看照片。（按 U）', 8); }
        else if (el > 60 && !auto1) {
          auto1 = true;
          S.run(async S2 => { await autoFly(S2); await autoAvdol(S2); }).catch(G.cancelIgnore);
        }
      } else if (now() - (F().flyT || 0) > 20 && !auto2) { auto2 = true; S.run(autoAvdol).catch(G.cancelIgnore); }
      return false;
    });
  }

  // ================================================================ 序-17 决心（照分镜 s05 6.65–10.55）
  async function resolveScene(S) {
    const kak = S.actor('kakyoin');
    S.setLeader('jotaro', { force: true, silent: true });
    const p = S.player;
    if (p.x > 230) await S.walk(p, 220, 166, { speed: 60 });
    await S.say('avdol', '这种苍蝇，只在埃及阿斯旺一带的尼罗河边才有。');
    await S.say('avdol', 'DIO……在埃及。');
    await S.say('joseph', '明天一早就有飞往开罗的飞机。');
    // 〔局部 insert〕承太郎的手：张开、发抖 → 攥紧「ギュッ」；身后白金之星升起、ゴゴゴ
    const fist = T().insert(S, {
      bg: 'menace', colours: ['#2a1a50', '#0a0418'],
      parts: [
        { kind: 'sprite', cid: 'starplat', anim: 'portrait', frame: 0, x: 220, y: 230, scale: 3, alpha: 0.7 },
        { kind: 'sprite', cid: 'scene:s05_fist', anim: 'idle', frame: 0, x: 140, y: 150, scale: 4, jitter: 1 },
      ],
    });
    S.animate(1.4, (k) => { fist.parts[0].y = 230 - 70 * k; });
    await S.wait(0.6);
    fist.parts[1].frame = 1; fist.parts[1].jitter = 0;
    S.sfxText('ギュッ', { x: 280, y: 200 }, { dur: 0.7 });
    S.fx('shockwave', { x: 140, y: 120, r_max: 40, width: 2 }, { space: 'canvas', tag: 'insert' });
    S.sfx('punch_heavy', { vol: 0.5 });
    const mm = S.menacing({ x: 470, y: 120, n: 4 });
    S.sfx('menacing', 0.6);
    await S.wait(0.8);
    await S.say('jotaro', '……我去把DIO揍扁。', { expr: 'glare' });
    mm.stop();
    fist.close();
    if (kak) { kak.visible = true; kak.x = 300; kak.y = 166; await S.walk(kak, 262, 164, { speed: 50 }); S.face(kak, p); }
    await S.say('kakyoin', '我也一起去。');
    await S.say('jotaro', '……为什么。');
    await S.say('kakyoin', '……谁知道呢。');
    await S.say('kakyoin', '开玩笑的。你救了我的命——这就够了。');
    S.leadable('kakyoin', true);
    S.sfx('power_up');
    await S.notice({ who: 'kakyoin', title: '', text: '—— 花京院典明 加入了队伍！——' });
  }

  // ================================================================ 序-18 出发（照分镜 s05 10.55–12.90）
  async function departure(S) {
    S.party(['jotaro', 'joseph', 'avdol', 'kakyoin'], { leader: 'jotaro' });
    await S.setStage('gate_pro', { x: 120, y: 152, facing: 1, music: null });
    S.camera(0);
    const ids = ['jotaro', 'joseph', 'avdol', 'kakyoin'];
    const acts = ids.map((id) => S.actor(id)).filter(Boolean);
    acts.forEach((a, i) => { a.follow = null; a.x = 120 - i * 18; a.y = 150 + (i % 2) * 4; a.facing = 1; a.tint = { color: '#0a0610', k: 0.9 }; a.outline = '#ffb060'; });
    S.sfx('wind', 0.6);
    S.camera(60);
    const walks = acts.map((a, i) => G.wait(i * 0.35).then(() => S.walk(a, 330 - i * 20, a.y, { speed: 34 })));
    let k = 0;
    T().every(0.33, () => { k++; S.sfx('footstep', { vol: 0.3, seed: k % 4 }); }, () => k >= 14);
    await S.wait(1.0);
    S.music('travel', 0.8);
    S.cue('sting_reveal');
    S.sfx('dododo', 0.7);
    S.sfxText('ドドド', { x: 120, y: 260 }, { dur: 1.4, jitter: 2 });
    S.sfxText('ドドド', { x: 520, y: 260 }, { dur: 1.4, jitter: 2 });
    S.mark('pro_egypt');
    await S.title('egypt', { y: 150, dur: 1.8 });
    await Promise.all(walks);
    acts.forEach((a) => { a.tint = null; a.outline = null; });
    await S.tbc({ hold: 2.0 });
    S.mark('pro_tbc');
  }

  // ================================================================ 序章主流程
  G.STORY.prologue = async function (S) {
    // 序章开头：片头 op → 序幕 coffin → 黑场 0.3 s → 篇章卡
    await S.video('op');
    await S.video('coffin');
    G.fadeA = 1;
    await S.wait(0.3, 'ui');
    G.fadeA = 0;
    await S.chapterCard('prologue');
    // 序-1 / 序-2 牢房（只有承太郎；不教 Q）
    S.party(['jotaro'], { leader: 'jotaro' });
    setupJail(S);
    G.fadeA = 1;
    await S.setStage('jail_pro', { x: 148, y: 124, facing: 1, music: 'daily' });
    await S.run(jailIntro);
    // 自由探索：调查够了去床上躺下 / 调查满 JAIL_AUTO 样听见脚步声，才进荷莉来接的剧情（没有倒计时）
    watchGrab(S);
    jailHelp(S);
    await S.until(() => !!F().jailReady && !S.busy);
    // 序-3 → 序-3b（掰铁栏出来）→ 序-4（走廊教学战）→ 序-5
    await S.run(async (S2) => {
      await jailVisitors(S2);
      await breakout(S2);
      await fightAvdolTest(S2);
      await standName(S2);
    }, { keepLocked: true });
    // 序-6 空条家（白天）
    S.party(['jotaro', 'joseph', 'avdol'], { leader: 'jotaro' });
    setupKujo6(S);
    await S.setStage('kujo_pro', { bg: 'kujo_house_day', x: 200, y: 164, facing: -1, music: 'daily' });
    T().prop(S, 'camera', 64, 150, { id: 'camera_prop', z: 8 });
    T().memberTalk(memberTalk6);
    await S.run(async (S2) => {
      S2.location('kujo', { y: LOC_BELOW_STRIP });
      S2.hint('Q 换队长。每个人按 U 调查的方式都不一样。', 7);
    });
    // 先让人自己逛一会儿；12 s 后指一下相机（乔瑟夫当队长在相机前按 U = 念写）
    T().goal(S, { x: 64, y: 150, h: 18, label: '拍立得', delay: 12, every: 16, done: () => !!F().p7,
      text: '外公的拍立得在左边矮桌上——按 Q 换成乔瑟夫，走到相机前按 U' });
    const t6 = now();
    await S.until(() => F().p7 || now() - t6 > 60);
    // 序-7 念写 → 夜 → 第二天早上
    await S.run(nensha, { keepLocked: true });
    // 序-8 上学路（外公和阿布德尔留在家里）：坡顶小路 → 走下长石阶（序-8b 在半路出事）→ 往右走到校门 → 走进校门
    S.leave('joseph'); S.leave('avdol');
    T().memberTalk({});     // 空条家给队员挂的搭话清掉（不然承太郎自己也算一个能搭话的“NPC”）
    setupStairs(S);
    await S.setStage('stairs_pro', { x: 56, y: 155, facing: 1, music: 'daily' });
    stairsTick();
    await S.run(async (S2) => {
      S2.location('school', { y: LOC_BELOW_STRIP });
      for (const [id, slot] of [['girlA', 2], ['girlB', 3]]) { const g = S2.actor(id); if (g) { S2.follow(g, 'player'); g.followSlot = slot; } }
      followersPause(S2, [['girlA', 2], ['girlB', 3]], () => F().p8b);
      S2.hint('外公和阿布德尔留在家里。', 4);
      // 爱心从女生头顶冒出来：她们站在台阶上时头顶也跟着高（z 加上脚下那一级的高度）
      T().every(3.1, () => { const g = S2.actor(Math.random() < 0.5 ? 'girlA' : 'girlB'); if (g && g.follow) T().floater(S2, 'scene:s02_heart', g.x, g.y + 0.5, { z: 44 + stairZ(g.x), rise: 12, dur: 1.0 }); }, () => F().p8b);
    });
    T().goal(S, { x: STAIRS.x0 + 8, y: 155, h: 44 + STAIRS.top, label: '石阶', delay: 4.5, every: 15, done: () => !!F().p8b,
      text: '上学去——往右走，走下石阶' });
    await S.until(() => F().p8c);
    // 离开石阶：人的高度、影子交还给引擎
    for (const a of (G.party && G.party.members) || []) { a.z = 0; a.shadow = true; a.mem.stairManual = false; }
    setupSchool(S);
    await S.setStage('school_pro', { x: 24, y: 160, facing: 1, music: 'daily' });
    T().goal(S, { x: 236, y: 146, label: '校门', delay: 0.5, every: 15, done: () => !!F().p9go,
      text: '去保健室包扎一下（走到校门口，往上走进去）' });
    await S.until(() => F().p9go);
    // 序-9 保健室
    setupInfirmary(S);
    await S.run(async (S2) => {
      // 从门口进来（门开着），走进屋里再把门拉上
      await S2.setStage('infirmary_pro', { x: 299, y: 152, facing: -1, music: 'tension' });
      if (G.audio && G.audio.duck) G.audio.duck(0.6, 30);
      await S2.walk(S2.player, 280, 160, { speed: 55 });
      S2.state('door', 0); S2.sfx('door', 0.6);
    });
    T().goal(S, { x: 230, y: 156, label: '校医', every: 15, done: () => !!F().sat, text: '找校医包扎一下（走到她跟前按 E）' });
    await S.until(() => F().noteRead);
    // 9b → QTE → 序-10 序2 → 序-11（校门上上午的人都散了：清掉 NPC 和触发区）
    Object.assign(G.STAGES.school_pro, { npcs: [], hotspots: [], triggers: [], onLook: null });
    await S.run(async (S2) => {
      await infirmaryQte(S2);
      await S2.setStage('school_pro', { x: 150, y: 150, facing: 1, music: 'battle' });
      await fightKakyoin(S2);
      await oraFinish(S2);
    }, { keepLocked: true });
    // 序-12 / 序-13 空条家·肉芽（下午）
    await S.join('joseph'); await S.join('avdol');
    G.STAGES.kujo_pro.npcs = []; G.STAGES.kujo_pro.hotspots = []; G.STAGES.kujo_pro.onLook = null;
    await S.run(async (S2) => {
      await S2.setStage('kujo_pro', { bg: 'kujo_house_day', x: 20, y: 164, facing: 1, music: 'tension', fade: false });
      await budScene(S2);
      // 序-14 荷莉病倒（早上）
      await S2.setStage('kujo_pro', { bg: 'kujo_house_morning', x: 330, y: 164, facing: -1, music: null, fade: false });
      await hollyFaints(S2);
    }, { keepLocked: true });
    // 序-15 卧室 → 序-16 找 DIO
    setupBedroom(S);
    await S.run(async (S2) => {
      await S2.setStage('bedroom_pro', { x: 240, y: 170, facing: -1, music: 'sad', fade: false });
      await bedroomScene(S2);
    });
    await bedroomFree(S);
    // 序-17 决心 → 序-18 出发 → TBC
    await S.run(async (S2) => {
      await resolveScene(S2);
      await departure(S2);
    }, { keepLocked: true });
  };
})();
