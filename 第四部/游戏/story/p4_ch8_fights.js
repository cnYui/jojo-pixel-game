// 第8章　吉良家旧宅 / 原子心之父：战斗和小游戏（开发脚本 第四部/docs/第8章_开发脚本.md §3、§4）。
//   第 12 战「原子心之父」（b12_atomheart，仗助 ⇄ 承太郎）：吉广在三个相框之间钻来钻去，探身出手后才打得到；
//     打出相框倒地时，换承太郎用拍立得拍一张“只有他一个人”的照片就赢。
//   第 13 战「Boy II Man」（b13_boyiiman，露伴）：猜拳，先赢 3 局；输 3 局替身被拿光就失败重来。不扣血，靠读习惯。
//   剧情节拍在 story/p4_ch8.js；这里只管开打到打完。招式、brain 也写在这里（第四部的公共招式表 engine/p4_moves.js 不动）。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const f = (n) => n / 60;
  const M = G.MOVES, K = G.KITS;
  const R = (G.P4CH8 = {});
  const player = () => G.world.player;
  const members = () => ((G.party && G.party.members) || []);

  // 在战斗里插一段演出（照 p4_pro_fights.js 的 cine）：占住 W.cine，玩家、敌人、战斗 tick 都停，演完还回去
  async function cine(ctx, fn) {
    const W = G.world, run = G.runId;
    if (W.fight !== ctx) return;
    const old = W.cine;
    W.cine = { by: 'p4-ch8' };
    try { await fn(); } catch (e) { if (!G.cancelled(e)) console.error(e); } finally { if (run === G.runId && W.fight === ctx) W.cine = old || null; }
  }

  // =====================================================================================================================
  // 第 12 战 原子心之父（b12_atomheart）
  // =====================================================================================================================
  //   相框的位置照 docs/第8章_背景.md 的锚点（x 是地图坐标，y 是相框在背景图上的高度）
  const FRAMES = [{ id: 'portrait', x: 239, y: 59 }, { id: 'table_frame', x: 307, y: 114 }, { id: 'tv_screen', x: 390, y: 109 }];
  const ARENA = [150, 510];
  const BACK_Y = 144;                 // 在相框里时站在可走带最靠里的一条（画在家具后面）
  const VIEW_HALF = 36;               // 取景框半宽：他倒地时，框里只能有他一个人
  const DOWN_T = 4.2;                 // 摔出相框以后躺多久
  const SEPIA = { color: '#a08050', k: 0.35 };

  // 探身挥一道白光：近身 8 伤（伤害系数 ×1.1 另外乘）。往前扑 36 px
  M.YH_SLASH = {
    slot: 'enemy', body: 'throw', stand: null, warn: { tier: 'W1', dur: 0.6 }, dur: 0.6 + f(24), active: [0.6, 0.6 + f(8)],
    melee: false, dash: { dist: 36, time: f(8), w: 10 }, dmg: 8, push: 10, guard: 'normal',
    sfx: 'whoosh', sfxHit: 'punch', fxHit: 'light', accent: '#f4ecd8', shake: [1, f(6)],
  };
  // 远了就扔茶杯：横着飞，L 挡得住，精准格挡打回去
  M.YH_CUP = {
    slot: 'enemy', body: 'throw', stand: null, warn: { tier: 'W1', dur: 0.55 }, dur: 0.55 + f(20), active: [0.55, 0.56], melee: false,
    fireAt: [0.55], sfx: 'whoosh', sfxVol: 0.5,
    shot: { kind: 'img', image: 'props/teacup', speed: 170, life: 2.4, r: 4, hitR: [6, 6, 18], dmg: 6, push: 6, guard: 'normal', reflect: true },
    shotFrom(e) { const p = G.world.player; return { x: e.x + e.facing * 8, y: p ? p.y : e.y, z: 16 }; },
  };

  function inFrame(e, fr, S) {
    const m = e.mem;
    m.mode = 'frame'; m.frame = fr; m.t = 0; m.gap = 1.2 + Math.random() * 0.8;
    e.atk = null; e.tele = null; e.state = 'idle'; e.untargetable = true;
    e.x = fr.x; e.y = BACK_Y; e.z = Math.max(0, 146 - fr.y - 16);
    e.alpha = 0.8; e.scale = 0.8; e.play('idle');
    if (S) { S.fx('glint', { x: fr.x, y: fr.y, size: 8 }, { life: 0.3 }); S.sfx('card_flip', 0.4); }
  }
  // 从相框里探出来：落到地面那一条（站在队长同一排），这时开始打得到
  function leanOut(e) {
    const p = player(), m = e.mem;
    m.mode = 'lean'; m.t = 0;
    e.z = 0; e.scale = 1; e.alpha = 1; e.untargetable = false;
    e.y = G.clamp(p ? p.y : 156, 146, 172);
    e.facing = p && p.x > e.x ? 1 : -1;
    if (G.fx) G.fx.spawn('smoke', { x: e.x, y: e.y - 14, n: 5, colour: '#e8dcc0', rise: 10, life: 0.5 }, { by: e });
    const near = p && Math.abs(p.x - e.x) < 70;
    G.AI.tele(e, near ? 'YH_SLASH' : 'YH_CUP');
  }
  K.e_yoshihiro = {
    hp: 9999, speed: 40, moves: ['YH_SLASH', 'YH_CUP'], koStyle: 'none', idle: 'idle', armor: true,
    dmgMul: () => 0.02,
    // 在相框里：拳头穿过去。探出来以后被打中：摔出相框（倒地，可以拍照了）
    onHitBy(t, att) {
      const m = t.mem;
      if (m.mode === 'frame' || m.mode === 'down') { t.evadeWord = m.mode === 'frame' ? '打不到照片！' : null; return 'evade'; }
      knockDown(t, att);
      return null;
    },
    brain(e, dt, ctx) {
      const m = e.mem, d = ctx ? ctx.data : {}, S = G.S;
      e.tint = SEPIA;
      if (!m.mode) inFrame(e, FRAMES[0], null);
      m.t = (m.t || 0) + dt;
      if (m.mode === 'down') {
        if (e.state === 'idle') e.play('down');
        if (m.t >= DOWN_T) { d.downT = 0; inFrame(e, FRAMES[(FRAMES.indexOf(m.frame) + 1) % FRAMES.length], S); }
        else d.downT = DOWN_T - m.t;
        return true;
      }
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      if (m.mode === 'frame') {
        e.play('idle');
        const p = player();
        if (p) e.facing = p.x > e.x ? 1 : -1;
        m.gap -= dt;
        // 换相框：多半挑离队长最近的那个，偶尔钻到最远的（画中画）
        if (m.gap <= 0) {
          const near = FRAMES.slice().sort((a, b) => Math.abs(a.x - (p ? p.x : 300)) - Math.abs(b.x - (p ? p.x : 300)));
          const fr = Math.random() < 0.7 ? near[0] : near[near.length - 1];
          if (fr !== m.frame && Math.random() < 0.5) { inFrame(e, fr, S); m.gap = 0.5; return true; }
          leanOut(e);
        }
        return true;
      }
      if (m.mode === 'lean') { m.mode = 'out'; m.t = 0; e.play('idle'); return true; }
      if (m.mode === 'out') {
        // 出手以后露在外面 1.2 s：这就是打他的机会
        e.play('idle');
        if (m.t >= 1.2) inFrame(e, m.frame, S);
        return true;
      }
      return true;
    },
  };
  function knockDown(e, att) {
    const m = e.mem, ctx = G.world.fight, d = ctx ? ctx.data : {};
    m.mode = 'down'; m.t = 0;
    e.atk = null; e.tele = null; e.untargetable = false;
    const dir = att && att.x < e.x ? 1 : -1;
    e.x = G.clamp(e.x + dir * 40, ARENA[0] + 20, ARENA[1] - 20);
    e.play('down');
    d.knocks = (d.knocks || 0) + 1; d.downT = DOWN_T;
    G.S.sfx('thud', 0.8); G.S.shake(2, 0.2);
    G.S.sfxText('砰', e, { dur: 0.6 });
  }
  // 取景框里除了他还有谁（队长和队友都算；拍照的人自己也不能在框里）
  const crowd = (e) => members().filter((a) => a.visible !== false && !a.remove && Math.abs(a.x - e.x) < VIEW_HALF && Math.abs(a.y - e.y) < 22);
  // 取景框：他倒地时画在他身上（白框，框里有人就变红）
  let viewH = null;
  function viewfinder() {
    return P4().overlay((g) => {
      const W = G.world, c = W.fight, e = G.S.actor('yoshihiro');
      if (!c || c.id !== 'b12_atomheart' || !e || !(c.data.downT > 0) || W.cine || !G.cam || !G.cam.w2u) return;
      const a = G.cam.w2u(e.x - VIEW_HALF, e.y - 40, 0), b = G.cam.w2u(e.x + VIEW_HALF, e.y + 6, 0);
      const bad = crowd(e).length > 0;
      const col = bad ? '#ff5a5a' : '#fff8e0';
      const x0 = Math.round(a.x), y0 = Math.round(a.y), x1 = Math.round(b.x), y1 = Math.round(b.y), L = 10;
      g.fillStyle = col;
      for (const [x, y, sx, sy] of [[x0, y0, 1, 1], [x1, y0, -1, 1], [x0, y1, 1, -1], [x1, y1, -1, -1]]) {
        g.fillRect(sx > 0 ? x : x - L, y - (sy > 0 ? 0 : 1), L, 2);
        g.fillRect(x - (sx > 0 ? 0 : 1), sy > 0 ? y : y - L, 2, L);
      }
      P4().text(g, bad ? '框里不止他一个人' : '取景框', Math.round((x0 + x1) / 2), y0 - 16, col, 12, 'center');
    }, { z: 2 });
  }
  // 承太郎按 U：咔嚓。框里只有他 → 赢；还有别人 → 他笑着钻回相框
  async function takePhoto(S, p, ctx, C) {
    const e = S.actor('yoshihiro'), d = ctx.data;
    S.sfx('camera_shutter', 0.9); S.sfx('blip', 0.5);
    S.flash(0.15, 0.9, '#ffffff');
    await C.wait(0.3);
    if (!e) return;
    const extra = crowd(e);
    if (extra.length) {
      d.badShots = (d.badShots || 0) + 1;
      await cine(ctx, async () => {
        await S.say('yoshihiro', '哈哈！拍到两个人了，这可不算！', { expr: 'smile' });
        S.hint('取景框里只能有吉广一个人：让开以后再拍', 5);
      });
      d.downT = 0;
      inFrame(e, e.mem.frame || FRAMES[0], S);
      return;
    }
    d.solo = true;
    S.mark('ch8_photo_solo');
  }
  R.fightAtomHeart = async function (S) {
    S.hint(null);
    if (viewH) viewH.close();
    viewH = viewfinder();
    const res = await S.fight({
      id: 'b12_atomheart', arena: ARENA, lead: 'josuke', swap: true, allies: ['josuke', 'jotaro4'], music: 'battle', after: null,
      dmgScale: 1.1, energy: { start: 0 },
      steps: { n: 2, label: '原子心之父' },
      kitOverride: { jotaro4: { special: { need: 0, title: 'photo8', name: '拍照', colours: ['#3a2a1a', '#140c06', '#8a6a40'],
        window: (c) => c.data.downT > 0 && !c.data.solo, prompt: '按 U：用拍立得拍下他！', run: takePhoto } } },
      waves: [[{ kit: 'e_yoshihiro', cid: 'yoshihiro', id: 'yoshihiro', name: '吉良吉广', x: FRAMES[0].x, y: BACK_Y, boss: true, hp: 9999, minHp: 1, idle: 'idle' }]],
      testHint: (c) => ({ knocks: c.data.knocks || 0, downT: c.data.downT || 0, bad: c.data.badShots || 0 }),
      onWave: async (S2, wi, spawned) => {
        const e = spawned[0];
        e.mem.mode = null;
        inFrame(e, FRAMES[0], null);
        S2.hint('吉广在相框里时打不到：等他探出身子出手以后再打（Q 换人）', 7);
      },
      tick: (c) => {
        const d = c.data, p = player(), e = S.actor('yoshihiro');
        // 他倒地时，不在操作的那个人站着别动（AI 冲上去打会挤进取景框）：临时当成 npc
        for (const a of members()) if (a !== p && (a.team === 'ally' || a.team === 'npc')) a.team = d.downT > 0 ? 'npc' : 'ally';
        if (d.downT > 0 && !d.solo && e) {
          if (p && p.cid !== 'jotaro4' && !d.toldSwap) { d.toldSwap = true; S.hint('按 Q 换承太郎：拍立得在他手里（按 U 拍照）', 4); }
        } else d.toldSwap = false;
      },
      events: [{
        when: (t, c) => (c.data.knocks || 0) >= 1,
        run: async (S2, es, attempt, c) => {
          c.step(1);
          await S2.say('jotaro4', '他摔出来了……照片里的人，只能待在照片里。');
          await S2.say('jotaro4', '那就再拍他一张。框里只有他自己，他就哪儿也去不了。');
          S2.hint('他倒地时：换承太郎按 U 拍照。取景框里不能有别人（拍照的人也站到框外）', 7);
        },
      }],
      endWhen: (c) => !!c.data.solo,
    });
    if (viewH) { viewH.close(); viewH = null; }
    for (const a of members()) if (a.team === 'npc' || a.team === 'ally') a.team = 'npc';
    return res;
  };

  // =====================================================================================================================
  // 第 13 战 Boy II Man（b13_boyiiman）：猜拳
  // =====================================================================================================================
  const HANDS = ['石头', '剪刀', '布'];
  const KEYS = ['left', 'up', 'right'];             // ← 石头  ↑ 剪刀  → 布
  const beats = (a, b) => (a - b + 3) % 3 === 2;   // a 赢 b：石头(0) 赢 剪刀(1)、剪刀 赢 布(2)、布 赢 石头
  const BEAT = 0.75;                                // 「石头——」「剪刀——」「布！」每拍 0.75 s
  const THROW = BEAT * 2;                           // 第三拍：出手的时刻
  const WIN = 0.35;                                 // 前后 0.35 s 内出手才算
  const TELL = [BEAT * 1.25, BEAT * 1.25 + 0.4];    // 第二拍中间大柳的手先“动一下”（习惯）
  let jkH = null;
  function rohanCid() { return (G.D.chars && G.D.chars.rohan) ? 'rohan' : 'ph8_rohan'; }
  function josephCid() { return (G.D.chars && G.D.chars.joseph_old) ? 'joseph_old' : 'ph8_joseph'; }
  function newRound(d) {
    const r = d.round = { n: d.played || 0, t0: null, pick: null, at: null, oy: Math.floor(Math.random() * 3), said: null, done: false };
    // 心理战：前两局说真话；之后一半是假的（小动作永远是真的）
    const lie = r.n >= 2 && Math.random() < 0.5;
    r.said = lie ? (r.oy + 1 + Math.floor(Math.random() * 2)) % 3 : r.oy;
    return r;
  }
  function jkOverlay() {
    const props = () => (G.D && G.D.props) || {};
    return P4().overlay((g, t) => {
      const W = G.world, c = W.fight;
      if (!c || c.id !== 'b13_boyiiman') return;
      const d = c.data, r = d.round;
      const pm = props().jk_big, im = pm && G.image(pm.image);
      const fw = pm ? pm.size[0] : 34, fh = pm ? pm.size[1] : 30;
      const hand = (fr, x, y, flip, alpha) => {
        if (!im || !G.ready(im)) return;
        g.save(); g.globalAlpha = alpha == null ? 1 : alpha;
        g.translate(x, y); if (flip) g.scale(-1, 1);
        g.drawImage(im, fr * fw, 0, fw, fh, -fw, -fh, fw * 2, fh * 2);
        g.restore();
      };
      // 比分
      G.ui.box(g, 200, 8, 440, 52, { fill: 'rgba(14,10,30,0.88)' });
      P4().text(g, '露伴 ' + (d.win || 0) + ' : ' + (d.lose || 0) + ' 大柳', 320, 14, '#ffe9a8', 16, 'center');
      const left = 3 - (d.lose || 0);
      P4().text(g, '天堂之门　剩下 ' + left + ' / 3', 320, 34, left <= 1 ? '#ff8a8a' : '#c8f0d0', 12, 'center');
      // 键位
      P4().text(g, '← 石头　↑ 剪刀　→ 布', 320, 330, '#fff4d6', 12, 'center');
      // 出手以后的结果（双方的手、谁赢）在结算演出里也要看得见：只在还没出手时被演出挡住
      if (!r || r.t0 == null || (W.cine && !r.show)) return;
      const el = c.t - r.t0;
      const shake = el < THROW && !r.show ? Math.round(Math.sin(el * 18) * 3) : 0;
      // 露伴的手（左，朝右）、大柳的手（右，朝左）：没出手前都攥着拳头晃
      const rf = r.show ? r.pick : 0;
      let of = r.show ? r.oy : 0, oa = 1;
      if (!r.show && el >= TELL[0] && el < TELL[1]) of = r.oy;          // 习惯：先动一下
      if (d.invisible) oa = 1;
      hand(rf, 250, 240 + shake, false, d.invisible && !r.show ? 0.15 : 1);
      hand(of, 390, 240 + shake, true, oa);
      const word = el < BEAT ? '石头——' : el < THROW ? '剪刀——' : '布！';
      if (!r.show) P4().text(g, word, 320, 120, '#ffffff', 16, 'center');
      if (r.show && r.msg) P4().text(g, r.msg, 320, 120, r.msgCol || '#ffffff', 16, 'center');
      void t;
    }, { z: 2 });
  }
  async function roundTalk(S, c) {
    const d = c.data, r = d.round, rc = rohanCid();
    d.played = (d.played || 0);
    if (r.n === 0 && !d.introDone) {
      d.introDone = true;
      await S.say('oyanagi', '第一局！我先告诉你，我出' + HANDS[r.said] + '哦。', { expr: 'smile' });
      return;
    }
    // 静的插曲：第 3 局开始前，露伴的手突然看不见了（这一局不算，重来）
    if (r.n === 2 && !d.shizukaDone) {
      d.shizukaDone = true;
      S.sfx('pop', 0.5);
      await S.say(null, '（长椅那边，乔瑟夫怀里传来一声小小的喷嚏）');
      d.invisible = true;
      await S.say('oyanagi', '诶？！你的手不见了！看不见的手不算！', { expr: 'shock' });
      await S.say(rc, '……是静。', { expr: 'shock' });
      await S.say(josephCid(), '哈？静，你在帮露伴？', { expr: 'shock' });
      await S.say(rc, '我拒绝。……我岸边露伴，不需要婴儿帮忙赢一个小鬼。', { expr: 'rage' });
      d.invisible = false;
      S.mark('ch8_shizuka_jk');
    }
    const lines = ['这一把我出' + HANDS[r.said] + '。信不信由你～', '我还是出' + HANDS[r.said] + '。真的哦。', '下一把……' + HANDS[r.said] + '。'];
    await S.say('oyanagi', lines[r.n % lines.length], { expr: 'smile' });
  }
  async function roundResult(S, c) {
    const d = c.data, r = d.round, rc = rohanCid();
    r.show = true;
    if (r.foul) {
      r.msg = r.foul === 'early' ? '先出了！' : '后出了！'; r.msgCol = '#ff8a8a';
      d.lose = (d.lose || 0) + 1;
      S.sfx('menu_error', 0.7);
      await S.wait(0.6);
      await S.say('oyanagi', r.foul === 'early' ? '你先出了！先出就是输哦～' : '后出是犯规哦～这局算我赢！', { expr: 'smile' });
    } else if (r.pick === r.oy) {
      r.msg = '平局'; r.msgCol = '#ffe9a8';
      S.sfx('blip', 0.6);
      await S.wait(0.7);
      await S.say('oyanagi', '平局！再来！');
      return 'tie';
    } else if (beats(r.pick, r.oy)) {
      r.msg = '露伴赢！'; r.msgCol = '#a8f0b8';
      d.win = (d.win || 0) + 1;
      S.sfx('ding', 0.8);
      await S.wait(0.7);
      await S.say(rc, d.win >= 3 ? '……这是最后一局。' : '读到了。', { expr: 'smile' });
    } else {
      r.msg = '大柳赢！'; r.msgCol = '#ff8a8a';
      d.lose = (d.lose || 0) + 1;
      S.sfx('sting_shock', 0.6);
      await S.wait(0.7);
      await S.say('oyanagi', '我赢啦！你的替身，归我三分之一！', { expr: 'smile' });
    }
    if (r.foul || !beats(r.pick, r.oy)) {
      // 被拿走三分之一：替身的影子从露伴身上飞向大柳
      const p = player(), oy = S.actor('oyanagi');
      if (p && oy) S.fx('sparkles', { x: (p.x + oy.x) / 2, y: p.y - 24, n: 8, radius: 14, colour: '#f0d070', period: 0.4, size: 3 }, { life: 0.8 });
      S.sfx('whoosh', 0.7);
      if ((d.lose || 0) === 1 && !d.taughtTell) {
        d.taughtTell = true;
        await S.say(rc, '……等等。他出手之前，手先动了一下。', { expr: 'shock' });
        S.hint('看大柳的手：“剪刀——”那一拍他会先动一下，那就是他要出的。他嘴上说的不一定是真的', 8);
      }
    }
    return 'done';
  }
  R.fightBoyIIMan = async function (S) {
    S.hint(null);
    if (jkH) jkH.close();
    jkH = jkOverlay();
    const res = await S.fight({
      id: 'b13_boyiiman', lead: rohanCid(), swap: false, lockMsg: '这一战只能由露伴应战', music: 'battle', after: null,
      waves: [], losable: false, playerMinHp: 1, coverage: false, energy: { start: 0 },
      testHint: (c) => ({ win: c.data.win || 0, lose: c.data.lose || 0, round: c.data.round ? c.data.round.n : -1 }),
      tick: (c, dt) => {
        const d = c.data, p = player();
        if (p) { p.hold = true; p.state = 'idle'; }
        if (d.busy) return;
        if ((d.win || 0) >= 3) return;
        // 输满 3 局：c.fail 带上失败的字（failWhen 那条路会把字清掉）
        if ((d.lose || 0) >= 3) { c.fail('天堂之门被 Boy II Man 拿光了……'); return; }
        if (!d.round || d.round.done) {
          const r = newRound(d);
          d.busy = true;
          cine(c, async () => { await roundTalk(S, c); r.t0 = c.t; S.sfx('blip', 0.5); }).finally(() => { d.busy = false; });
          return;
        }
        const r = d.round, el = c.t - r.t0;
        if (r.t0 == null) return;
        // 拍子声
        r.beat = r.beat || 0;
        if (r.beat < 1 && el >= BEAT) { r.beat = 1; S.sfx('blip', 0.5); }
        if (r.beat < 2 && el >= THROW) { r.beat = 2; S.sfx('pop', 0.7); }
        if (r.pick == null) {
          for (let k = 0; k < 3; k++) {
            if (G.input.take(KEYS[k], 0.05)) {
              r.pick = k; r.at = el;
              if (el < THROW - WIN) r.foul = 'early';
              break;
            }
          }
          if (r.pick == null && el > THROW + WIN) { r.pick = 0; r.foul = 'late'; }
          if (r.pick != null && !r.foul && el > THROW + WIN) r.foul = 'late';
        }
        if (r.pick != null && el >= THROW - 0.05 || r.foul) {
          r.done = true; d.played = (d.played || 0) + 1;
          d.busy = true;
          cine(c, async () => {
            const out = await roundResult(S, c);
            if (out === 'tie') d.played -= 1;   // 平局不算一局（心理战的说真话 / 假话照局数算）
            await S.wait(0.4);
          }).finally(() => { d.busy = false; });
        }
      },
      endWhen: (c) => (c.data.win || 0) >= 3 && !c.data.busy,
    });
    if (jkH) { jkH.close(); jkH = null; }
    const p = player();
    if (p) p.hold = false;
    return res;
  };
  R.cine = cine;
})();
