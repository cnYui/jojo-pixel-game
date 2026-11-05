// 第2章　葡萄丘高中 / 锁与表面：第 3 战「锁」（b03_thelock）和它的收尾、第 4 战「表面」段 A（b04a_surface）/ 段 B（b04b_surface）、
//   段 C 的「抗拒」小游戏。剧情节拍在 story/p4_ch2.js；数值和流程照 第四部/docs/第2章_开发脚本.md §3。
//   玉美、表面的招和 brain 只有这一章用，就写在这里（分章开发约定：各章不改 engine/p4_moves.js 里别人的东西）。
//   克制：玉美自伤嫁祸只给剪影 + 旁白；仗助“拿笔刺自己”只给黑屏 + 声音，马上交代那是回音贴的假声音；表面的手是木头。
//   战斗里要“停下来演一下”的地方（内疚的话、跑去开门、碎玻璃、酒瓶）用 cine() 自己暂停战斗：spec.events 每次尝试只触发一次，不够用。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const f = (n) => n / 60;
  const M = G.MOVES, K = G.KITS;
  const R = (G.P4CH2 = {});
  const DMG = 0.9;                       // 开发脚本 §0：这一章敌人伤害 ×0.9
  const player = () => G.world.player;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  // 在战斗里插一段演出：和 fight.js 的 paused() 一样把 W.cine 占住（玩家、敌人、战斗 tick 都停），演完还回去
  async function cine(ctx, fn) {
    const W = G.world, run = G.runId;
    if (W.fight !== ctx) return;
    const old = W.cine;
    W.cine = { by: 'p4-ch2' };
    try { await fn(); } catch (e) { if (!G.cancelled(e)) console.error(e); } finally { if (run === G.runId && W.fight === ctx) W.cine = old || null; }
  }
  R.cine = cine;

  // =====================================================================================================================
  // 锁（小林玉美的替身）：挂在人胸口的道具。lock_s / lock_m / lock_l 三档；帧 0 挂着，1–2 咔嚓扣上，3–6 碎掉。
  //   一个人身上只挂一把：锁变多就换大一档（越大越沉，坠得越低）
  // =====================================================================================================================
  const LOCK_KEYS = ['lock_s', 'lock_m', 'lock_l'];
  const LOCK_Z = { lock_s: 7, lock_m: 5, lock_l: 3 };
  const locks = new Map();               // 人 → 锁道具
  function hangLock(S, a, key, o = {}) {
    if (!a) return null;
    const old = locks.get(a);
    if (old) old.remove = true;
    const z0 = (LOCK_Z[key] || 6) + (o.dz || 0);
    const lk = T().prop(S, key, a.x, a.y + 0.5, { id: 'lock_' + (a.id || a.cid) + '_' + T().count('lock'), frame: 1, z: z0 });
    if (!lk) return null;
    locks.set(a, lk);
    if (o.sound !== false) {
      S.sfx('magnet_clack', 0.9); S.sfx('clang', 0.35, 1.3);
      S.sfxText('咔嚓', { wx: a.x, wy: a.y, wz: z0 + 26 }, { dur: 0.6 });
    }
    G.defer(f(5), () => { if (!lk.remove) T().setFrame(lk, 2); });
    G.defer(f(10), () => { if (!lk.remove) T().setFrame(lk, 0); });
    T().tick(() => {
      if (lk.remove || locks.get(a) !== lk) return true;
      if (a.remove) { lk.remove = true; return true; }
      lk.x = a.x + (o.dx || 0) * (a.facing || 1); lk.y = a.y + 0.5; lk.z = (a.z || 0) + z0; lk.visible = a.visible !== false;
      return false;
    });
    return lk;
  }
  async function breakLock(S, a) {
    const lk = locks.get(a);
    if (!lk) return;
    locks.delete(a);
    for (let i = 3; i <= 6; i++) { if (lk.remove) break; T().setFrame(lk, i); await S.wait(0.07); }
    lk.remove = true;
  }
  function dropLock(a) { const lk = locks.get(a); if (lk) lk.remove = true; locks.delete(a); }
  R.hangLock = hangLock;
  R.breakLock = breakLock;
  R.dropLock = dropLock;
  R.dropLocks = () => { for (const lk of locks.values()) lk.remove = true; locks.clear(); };

  // =====================================================================================================================
  // 第 3 战 锁（b03_thelock）：康一第一次能操作，不能换人。客厅（home_ch2，可走 x 52–312），不打本人：拟声字把玉美“吵”到崩溃
  // =====================================================================================================================
  const HM = { arena: [44, 320], doorX: 60, mid: 200, tam: [236, 158], ko: [124, 160] };
  const KO_SPEED = 68;
  // 内疚的话：玉美说一句，康一两个回答（认错的那句挂锁）。8 组，一次尝试里不重复
  const GUILT = [
    { q: '你妈妈辛辛苦苦把你养大，你就这么报答她？', admit: '……是我对不起妈妈', deny: '我没有骗过妈妈！' },
    { q: '捡了别人的钱包还嘴硬，你良心不会痛吗？', admit: '……也许是我不对', deny: '钱包本来就是我的！' },
    { q: '你把你姐姐也推出门了吧？她现在一定在外面哭。', admit: '……都是我害的', deny: '是你把她们扯进来的！' },
    { q: '压死小猫的人，晚上睡得着吗？', admit: '……我睡不着', deny: '那只是个布偶！' },
    { q: '你这种人，长大了也只会给家里丢脸。', admit: '……也许吧', deny: '我才不会！' },
    { q: '现在跪下来道歉，我还能原谅你哦～', admit: '……对不起', deny: '该道歉的是你！' },
    { q: '邻居们要是知道广濑家的儿子是小偷……', admit: '……别说出去', deny: '我不是小偷！' },
    { q: '你妈妈刚才哭了吧？是谁害的？', admit: '……是我', deny: '是你！' },
  ];
  const TAUNT = ['吵死了！', '别、别喊了！', '耳朵要聋了！', '呜哇——！'];
  const LOCK_HINT = ['胸口挂上了一把锁：走得慢了。挂满三把就会被压垮', '第二把锁……再挂一把就撑不住了！'];

  // 玉美：不攻击。在康一身边转悠，停下来时有时背过身去（耳边贴字的机会）；时不时往左边的门跑（战斗 tick 定时叫他跑）
  K.e_tamami = {
    hp: 999, speed: 46, moves: [], koStyle: 'none', idle: 'idle', armor: true,
    dmgMul: () => 0.02,                  // 本人不掉血（贴字只算“吵”），0.02 以上才会发 hit 事件
    brain(e, dt, ctx) {
      const m = e.mem, p = G.world.player, st = G.world.stage;
      if (!dt || !p || !st || m.hold) return true;
      if (e.state !== 'idle' && e.state !== 'walk') return true;
      const [lo, hi] = st.bounds();
      if (m.ears > 0) { m.ears -= dt; e.play('cover_ears'); return true; }
      if (m.run) {
        G.combat.walkTo(e, HM.doorX - 6, e.y, dt, 74 * (ctx && ctx.assist ? 0.85 : 1));
        e.play('run');
        if (e.x <= HM.doorX + 0.5) { m.run = false; if (ctx) ctx.data.doorReached = true; }
        return true;
      }
      if (m.pause > 0) { m.pause -= dt; e.play(m.wave ? 'wave' : 'idle'); return true; }
      if (!m.wp) {
        const side = Math.random() < 0.5 ? -1 : 1, dist = 34 + Math.random() * 40;
        let x = p.x + side * dist;
        if (x < lo + 6 || x > hi - 6) x = p.x - side * dist;
        m.wp = [clamp(x, lo + 6, hi - 6), clamp(p.y + Math.round(Math.random() * 16 - 8), st.yMin, st.yMax)];
      }
      if (Math.hypot(m.wp[0] - e.x, m.wp[1] - e.y) < 2) {
        // 站一会儿：45% 背过身去（挥着手说风凉话），不然面朝康一
        m.wp = null; m.pause = 0.7 + Math.random() * 0.8;
        const toward = Math.sign(p.x - e.x) || 1;
        m.wave = Math.random() < 0.45;
        e.facing = m.wave ? -toward : toward;
        e.play(m.wave ? 'wave' : 'idle');
        return true;
      }
      G.combat.walkTo(e, m.wp[0], m.wp[1], dt, e.speed);
      return true;
    },
  };

  // 内疚的回答：两个框左右随机，限时 2.5 s（放水 3.5 s）；← / → 或者点画面左右半边。机器人读 R.pick.good
  R.pick = null;
  function drawArrow(g, x, y, dir, col) {
    for (const [c, d] of [['#0c0a14', 1], [col, 0]]) {
      g.fillStyle = c;
      for (let r = 0; r < 7; r++) g.fillRect(Math.round(x + dir * (r - 3)) - d, Math.round(y - (6 - r)) - d, 1 + 2 * d, (6 - r) * 2 + 1 + 2 * d);
    }
  }
  function drawPick(g, st) {
    const t = G.clk.ui - st.t0, left = st.pick >= 0 ? 0 : Math.max(0, 1 - t / st.dur);
    P4().text(g, '康一要怎么回答？', 320, 132, '#ffe9a8', 16, 'center');
    for (let i = 0; i < 2; i++) {
      const kind = st.sides[i], x0 = i === 0 ? 56 : 334, x1 = x0 + 250, y0 = 156, y1 = 202;
      const on = st.pick === i, dim = st.pick >= 0 && !on;
      G.ui.box(g, x0, y0, x1, y1, { fill: on ? 'rgba(70,46,10,0.95)' : dim ? 'rgba(16,14,40,0.55)' : 'rgba(16,14,40,0.92)', border: on ? '#ffd34a' : '#fff' });
      drawArrow(g, x0 + 18, (y0 + y1) / 2, i === 0 ? -1 : 1, on ? '#ffd34a' : '#e8e0f0');
      P4().text(g, '「' + st.set[kind] + '」', x0 + 34, y0 + 15, dim ? '#8a84a0' : '#fff4d6', 16, 'left');
    }
    const bw = 528, bx = 56, by = 212;
    g.fillStyle = '#0c0a14'; g.fillRect(bx - 1, by - 1, bw + 2, 6);
    g.fillStyle = left < 0.35 ? '#e83040' : '#ffd34a'; g.fillRect(bx, by, Math.round(bw * left), 4);
  }
  async function guiltPick(S, c, set) {
    const I = G.input, run = G.runId;
    const sides = Math.random() < 0.5 ? ['admit', 'deny'] : ['deny', 'admit'];
    const st = { sides, set, t0: G.clk.ui, dur: c.assist ? 3.5 : 2.5, pick: -1, pickT: 0 };
    R.pick = { open: true, good: sides[0] === 'deny' ? 'left' : 'right' };
    I.consume('left'); I.consume('right');
    const h = P4().overlay((g) => drawPick(g, st), { z: 4 });
    S.sfx('heartbeat', 0.5);
    try {
      await G.until(() => {
        if (run !== G.runId || G.world.fight !== c) return true;
        if (st.pick < 0) {
          let k = -1;
          if (I.hit('left')) k = 0;
          else if (I.hit('right')) k = 1;
          else if (I.tap && I.tap.y > 120 && I.tap.y < 260) k = I.tap.x < 320 ? 0 : 1;
          if (k >= 0) { st.pick = k; st.pickT = G.clk.ui; S.sfx('menu_confirm', 0.6); }
        }
        return st.pick >= 0 ? G.clk.ui - st.pickT >= 0.35 : G.clk.ui - st.t0 >= st.dur;
      });
    } finally { h.close(); R.pick = null; }
    return st.pick < 0 ? 'timeout' : sides[st.pick];
  }
  function nextGuilt(d) {
    if (!d.order || d.gi >= d.order.length) {
      d.order = GUILT.map((_, i) => i);
      for (let i = d.order.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [d.order[i], d.order[j]] = [d.order[j], d.order[i]]; }
      d.gi = 0;
    }
    return GUILT[d.order[d.gi++]];
  }
  async function addLock(S, c) {
    const d = c.data, p = player();
    d.locks = (d.locks || 0) + 1;
    if (G.hud.steps) G.hud.steps.done = d.locks;
    hangLock(S, p, LOCK_KEYS[Math.min(2, d.locks - 1)]);
    p.speed = KO_SPEED * (1 - 0.15 * d.locks);
    S.shake(2, 0.2);
    S.pose(p, 'bow');
    await S.wait(0.5);
    S.unpose(p);
    if (d.locks >= 3) { S.sfx('heartbeat', 0.9); await S.wait(0.3); c.fail('康一被罪恶感压垮了……'); return; }
    S.hint(LOCK_HINT[d.locks - 1], 4);
  }
  async function guiltScene(S, c, e) {
    const d = c.data, p = player();
    const set = nextGuilt(d);
    S.face(e, p);
    e.play('wave');
    await S.say('tamami', set.q, { expr: 'smile' });
    const r = await guiltPick(S, c, set);
    d.picks = (d.picks || 0) + 1;
    if (r === 'deny') {
      d.denies = (d.denies || 0) + 1;
      await S.say('koichi', set.deny, { expr: 'rage' });
      S.emote(e, '啧……', 0.8);
    } else {
      await S.say('koichi', r === 'admit' ? set.admit : '……', { expr: 'shock' });
      await addLock(S, c);
    }
    if (!e.remove) e.play('idle');
  }
  // 玉美碰到门口：门开了，门外的妈妈哭了 → 康一挂一把锁；回音一句「啪！」把他弹回客厅中间，门关上
  async function doorScene(S, c, e) {
    const d = c.data, p = player();
    d.doors = (d.doors || 0) + 1;
    e.mem.run = false; e.mem.hold = true;
    S.state('door', 1);
    S.sfx('door', 0.8); S.sfx('creak', 0.5);
    S.face(e, -1);
    e.play('wave');
    await S.say('tamami', '伯母——！您儿子偷了人家五十万日元哦～', { expr: 'smile' });
    S.sfxText('呜呜……', { wx: 22, wy: 140, wz: 34 }, { dur: 1.4 });
    await S.narrate('门外传来妈妈的哭声。', { pos: 'top' });
    await addLock(S, c);
    if ((d.locks || 0) >= 3) return;
    S.face(p, e);
    S.standAct(p, 'shoot', { dx: 14, z: 12, dur: 0.5 });
    S.sfx('whoosh', 0.6, 1.4); S.sfx('punch', 0.7);
    S.sfxText('啪！', e, { dur: 0.7 });
    await S.arc(e, HM.mid, clamp(p.y, 150, 168), 12, 0.45, { anim: 'hurt' });
    S.state('door', 0); S.sfx('door', 0.6);
    e.mem.hold = false; e.mem.wp = null; e.mem.pause = 0.6; e.state = 'idle'; e.play('idle');
  }
  function tamamiHit(S, c, ev) {
    const d = c.data, e = S.actor('tamami'), p = player();
    if (!e || !p || ev.t !== e) return;
    const m = e.mem;
    // 捂着耳朵的时候听不太见：贴中只 +1，也不会再延长捂耳朵（光连按 J 压不垮他，要等他松手、绕到背后）
    const covered = m.ears > 0;
    let add;
    if (ev.slot === 'special') add = 12;
    else {
      // 背对康一、贴得很近：直接贴在耳边
      const ear = !covered && Math.sign(p.x - e.x) !== (e.facing || 1) && Math.abs(p.x - e.x) <= 16;
      const img = ev.move && ev.move.image;
      add = covered ? 1 : ear ? 10 : img && img === d.lastImg ? 2 : 4;
      d.lastImg = img;
      if (ear) { d.ears = (d.ears || 0) + 1; S.sfxText('！？', e, { dur: 0.6 }); }
      if (covered) {
        d.muffled = (d.muffled || 0) + 1;
        if (d.muffled === 4 && !d.muffleTold) { d.muffleTold = true; S.hint('玉美捂着耳朵的时候听不见：等他把手放下再贴', 5); }
      }
    }
    if (c.gauge) c.gauge.add(add);
    d.hits = (d.hits || 0) + 1;
    if (!covered || ev.slot === 'special') m.ears = 0.8;
    m.wp = null; m.pause = 0;
    G.world.move(e, (Math.sign(e.x - p.x) || 1) * 10, 0);       // 拟声字的击退：跑门的时候能把他拦住
    if (m.run) {
      d.runHits = (d.runHits || 0) + 1;
      if (d.runHits >= 3) { m.run = false; d.runHits = 0; d.blocked = (d.blocked || 0) + 1; S.emote(e, '呜……吵死了！', 1.0); }
    } else if (c.t - (d.tauntT == null ? -9 : d.tauntT) > 1.4) { d.tauntT = c.t; S.emote(e, TAUNT[(d.hits || 0) % TAUNT.length], 0.8); }
  }
  function tamamiSetup(S, c) {
    const d = c.data, p = player(), e = S.actor('tamami');
    dropLock(p);
    d.locks = 0; d.doorT = 0; d.guiltT = 0; d.runHits = 0;
    if (p) { p.speed = KO_SPEED; p.facing = 1; }
    S.state('door', 0);
    if (e) { Object.assign(e.mem, { wp: null, pause: 0.8, run: false, ears: 0, hold: false, wave: false }); e.facing = -1; e.play('idle'); }
    c.on('hit', (ev) => tamamiHit(S, c, ev));
    S.hint('J：回音贴字　K：闪避　L：格挡　把玉美吵到崩溃！绕到他背后贴最有效', 7);
  }
  function tamamiTick(S, c, dt) {
    const d = c.data, e = S.actor('tamami'), p = player();
    if (!e || !p) return;
    if (G.hud.steps && G.hud.steps.done !== (d.locks || 0)) G.hud.steps.done = d.locks || 0;
    if (d.doorReached) { d.doorReached = false; cine(c, () => doorScene(S, c, e)); return; }
    const run = !!e.mem.run;
    if (!run) {
      d.doorT += dt;
      const every = (c.gauge && c.gauge.value >= 50 ? 6 : 10) + (c.assist ? 3 : 0);
      if (d.doorT >= every && !(e.mem.ears > 0)) {
        d.doorT = 0; d.runHits = 0; d.runs = (d.runs || 0) + 1;
        e.mem.run = true; e.mem.wp = null; e.mem.pause = 0;
        S.emote(e, '伯母！你儿子他——', 1.6);
        if (!d.runTold) { d.runTold = true; S.hint('玉美要去门口找妈妈！贴字把他拦住（打中 3 下）', 4); }
      }
      d.guiltT += dt;
      if (d.guiltT >= (c.assist ? 12 : 8)) { d.guiltT = 0; cine(c, () => guiltScene(S, c, e)); return; }
    }
    if (!d.stuckTold && c.t > 60 && c.gauge && c.gauge.value < 20) {
      d.stuckTold = true;
      cine(c, async () => {
        await S.say('koichi', '（……他最怕的是吵。绕到他背后贴！）', { expr: 'normal' });
        S.hint('玉美背过身的时候，贴到他背后按 J：一下顶好几下', 6);
      });
    }
  }
  R.fightTamami = async function (S) {
    S.hint(null);
    const res = await S.fight({
      id: 'b03_thelock', arena: HM.arena, lead: 'koichi', swap: false, lockMsg: '这一战只能由康一应战',
      music: 'battle', after: null, dmgScale: DMG, playerMinHp: 1, losable: false, energy: { start: 0 },
      gauge: { max: 100, value: 0, label: '压力', color: '#9aa8ff' },
      steps: { n: 3, label: '锁（挂满三把就被压垮）' },
      waves: [[{ kit: 'e_tamami', actor: 'tamami', cid: 'tamami', id: 'tamami', name: '小林玉美', x: HM.tam[0], y: HM.tam[1], boss: true, hp: 999, minHp: 1 }]],
      testHint: (c) => ({ pressure: c.gauge ? Math.round(c.gauge.value) : 0, locks: c.data.locks || 0, hits: c.data.hits || 0, ears: c.data.ears || 0,
        runs: c.data.runs || 0, doors: c.data.doors || 0, blocked: c.data.blocked || 0, picks: c.data.picks || 0, denies: c.data.denies || 0,
        muffled: c.data.muffled || 0 }),
      onWave: async (S2, wi, spawned, attempt, c) => { tamamiSetup(S2, c); },
      tick: (c, dt) => tamamiTick(S, c, dt),
      endWhen: (c) => !!c.gauge && c.gauge.value >= 100,
    });
    S.hint(null);
    return res;
  };

  // 第 3 战收尾：画面暗下来，只剩玉美背过身的剪影（旁白交代，不出现过程）→ 妈妈和姐姐推门冲进来，妈妈的锁变得很大
  //   → 「U！」→ 金色圆圈，回音飞到妈妈耳边贴一句「相信我！」→ 三把锁一起碎掉
  R.tamamiFinale = async function (S) {
    const p = S.actor('koichi'), e = S.actor('tamami');
    S.hint(null);
    if (e) {
      e.team = 'npc'; e.brain = null; e.kit = G.KITS.tamami || null; e.moves = []; e.armor = false; e.dmgMul = null;
      e.atk = null; e.tele = null; e.state = 'idle'; e.mem.run = false; e.mem.hold = true; e.play('idle');
    }
    if (!locks.get(p)) hangLock(S, p, 'lock_s', { sound: false });       // 一把都没挂就赢了：收尾要三把锁一起碎，先给康一补上一把
    await S.say('tamami', '……好、好啊。这么吵，那我也不客气了。', { expr: 'rage' });
    S.walk(e, 270, 150, { speed: 50 }).catch(G.cancelIgnore);
    await S.wait(0.6);
    // 暗下来：玉美背过身，只剩剪影
    S.filter('tint', 0.6, { color: '#120a22' });
    S.sfx('heartbeat', 0.8);
    await S.until(() => !e.script);
    S.face(e, 1);
    e.tint = { color: '#04020a', k: 1 };
    S.mark('b03_silhouette');
    await S.narrate('他背过身去。……他想弄伤自己，让我妈以为是我干的。', { pos: 'top' });
    // 妈妈和姐姐推门冲进来
    S.state('door', 1); S.sfx('door', 0.9);
    const mom = S.spawn('hirose_mom', 30, 152, { id: 'hirose_mom', facing: 1 });
    const aya = S.spawn('ayana', 22, 162, { id: 'ayana', facing: 1 });
    hangLock(S, mom, 'lock_m', { sound: false, dz: 2 });
    hangLock(S, aya, 'lock_m', { sound: false });
    S.walk(aya, 72, 164, { speed: 70 }).catch(G.cancelIgnore);
    await S.walk(mom, 92, 154, { speed: 70 });
    S.filter('tint', null);
    await S.say('hirose_mom', '康一！你在对客人做什么？！', { expr: 'shock' });
    S.sfx('heartbeat', 0.9);
    hangLock(S, mom, 'lock_l', { dz: 2 });
    S.shake(2, 0.3);
    await S.say('koichi', '（妈妈的锁……变得这么大……！）', { expr: 'shock' });
    // U：金色圆圈，回音飞到妈妈耳边
    S.hint('按 U！', 4);
    for (let tries = 0; ; tries++) {
      const r = await S.press({ key: 'special', window: 3, at: 1.2, label: 'U！' });
      if (r !== 'miss' || tries >= 3) break;
      await S.say('koichi', '（……要让妈妈听见我的声音！）', { expr: 'rage' });
    }
    S.hint(null);
    S.face(p, mom);
    await S.summon(p, { dur: 0.14, rise: 6 });
    S.standAct(p, 'shoot', { dx: 14, z: 12, dur: 0.9 });
    S.sfx('super_start', 0.7);
    S.fx('shockwave', { x: p.x, y: p.y - 16, r_max: 120, dur: 0.6, colour: '#ffd84a' });
    S.flash(0.2, 0.5, '#ffe9a8');
    await S.wait(0.4);
    S.sfx('sparkle', 0.9);
    S.sfxText('相信我！', mom, { dur: 2.4 });
    await S.wait(0.5);
    S.mark('b03_trust');
    await S.say('hirose_mom', '……康一的声音……在耳朵里……', { expr: 'normal' });
    await S.say('hirose_mom', '……是啊。我的儿子，才不会做那种事。', { expr: 'smile' });
    S.sfx('glass_break', 0.8, 1.3); S.sfx('clang', 0.6);
    await Promise.all([breakLock(S, p), breakLock(S, mom), breakLock(S, aya)]);
    S.flash(0.15, 0.4);
    S.recall(p);
    if (e) e.tint = null;
    await S.wait(0.3);
  };

  // =====================================================================================================================
  // 第 4 战 表面（b04_surface）：段 A 学校走廊（仗助一个人）→ 段 B 商店街（仗助 ⇄ 康一）→ 段 C 抗拒（剧情里）。三段各是重来点
  // =====================================================================================================================
  const SF_COL = '#d8a868';
  const sfMove = (o) => Object.assign({ slot: 'enemy', body: 'cmd', melee: false, guard: 'normal', sfx: 'whoosh', sfxHit: 'punch', fxHit: 'light',
    accent: SF_COL, shake: [1, f(6)] }, o);
  // 模仿拳：照仗助的 J1–J3（8 / 8 / 14），预警 0.3 s，往前蹭一小步出拳
  M.SF_J1 = sfMove({ warn: { tier: 'W1', dur: 0.3 }, dur: 0.3 + f(20), active: [0.3, 0.3 + f(6)], dash: { dist: 30, time: f(6), w: 8 }, dmg: 8, push: 6 });
  M.SF_J2 = sfMove({ warn: { tier: 'W1', dur: 0.3 }, dur: 0.3 + f(20), active: [0.3, 0.3 + f(6)], dash: { dist: 30, time: f(6), w: 8 }, dmg: 8, push: 8, sfxRate: 1.08 });
  M.SF_J3 = sfMove({ warn: { tier: 'W1', dur: 0.3 }, dur: 0.3 + f(28), active: [0.3, 0.3 + f(8)], dash: { dist: 36, time: f(8), w: 8 }, dmg: 14, push: 24,
    sfxHit: 'punch_heavy', fxHit: 'heavy', shake: [2, f(10)], word: 'DORA!' });
  // 冲刺：0.5 s 预警（W4 地上一道线），沿线冲过去，地上留一道木屑；伤害 12
  M.SF_DASH = sfMove({ body: 'run', warn: { tier: 'W4', dur: 0.5 }, dur: 0.5 + f(30), active: [0.5, 0.8], dash: { dist: 110, time: 0.3, w: 8, line: true },
    dmg: 12, push: 14, sfx: 'skid' });
  // 踢（段 B 没了右手以后只剩冲刺和踢）：伤害 10
  M.SF_KICK = sfMove({ body: 'kick', warn: { tier: 'W1', dur: 0.35 }, dur: 0.35 + f(24), active: [0.35, 0.35 + f(8)], dash: { dist: 28, time: f(8), w: 8 },
    dmg: 10, push: 12 });
  const CHAIN = { SF_J1: 'SF_J2', SF_J2: 'SF_J3' };

  // 表面“准备好了”：没在出招、没在挨打、没在出完招的破绽里 → 正面的拳会被它侧身躲开，视线条会涨
  const sfReady = (e) => !!e && e.state === 'idle' && !e.atk && !e.tele && !(e.mem.open > 0) && !e.mem.ctrl && !e.mem.hold && !(e.stunT > 0);
  const evadeWord = (e) => { const t = G.clk.world; if (t - (e.mem.wordT || -9) < 0.6) return null; e.mem.wordT = t; return '哼～'; };
  K.e_surface = {
    hp: 600, speed: 60, moves: [], koStyle: 'none', idle: 'idle',
    onHitBy(t, att, m) {
      const c = G.world.fight, d = c ? c.data : {};
      if (!att) return null;
      // 段 A 演抛笔、段 B 没扎到手之前：什么都打不到它（碎玻璃那一招之前，它躲得太快）
      if (d.untouchable) { t.evadeWord = evadeWord(t); return 'evade'; }
      if (m.slot === 'shot' || m.slot === 'special' || d.noDodge) return null;
      // 正面的近身拳：侧身躲开（往上或往下让 5 px），接着照样回一拳
      if (sfReady(t) && Math.sign(att.x - t.x) === (t.facing || 1)) {
        G.world.move(t, 0, t.y > att.y ? 5 : -5);
        t.evadeWord = evadeWord(t);
        if (!(t.mem.counter > 0)) t.mem.counter = 0.18;
        return 'evade';
      }
      return null;
    },
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {}, m = e.mem, p = G.world.player, st = G.world.stage;
      if (!p || !st) return true;
      if (e.atk) {
        // 冲刺时地上留一道木屑
        if (e.atkId === 'SF_DASH' && e.atkT >= e.atk.active[0] && G.clk.world - (m.chipT || -9) > 0.06 && G.fx) {
          m.chipT = G.clk.world;
          G.fx.spawn('burst', { x: e.x - e.facing * 6, y: e.y - 2, n: 3, speed: 16, colours: ['#c89a5a', '#8a5a2a'], gravity: 120, life: 0.5 }, { life: 0.6, by: e });
        }
        m.lastAtk = e.atkId;
        return true;
      }
      if (m.lastAtk) {
        // 一招出完：模仿拳接着下一拳（J1 → J2 → J3），整套打完才露破绽 0.85 s
        const nx = CHAIN[m.lastAtk];
        m.lastAtk = null;
        if (nx && !d.cut && dt !== 0 && G.combat.tokens() < 2) { G.AI.tele(e, nx); return true; }
        m.open = 0.85;
      }
      if (!dt) return true;
      if (m.hold || m.ctrl || d.penMode) { if (!m.ctrl) e.play('idle'); return true; }
      if (e.state !== 'idle') return true;
      if (m.open > 0) { m.open -= dt; e.play(d.cut ? 'hurt' : 'shock'); return true; }
      const dx = p.x - e.x, adx = Math.abs(dx), dir = Math.sign(dx) || 1;
      e.facing = dir;                                 // 一直盯着对手（视线）
      if (m.counter > 0) {
        m.counter -= dt;
        if (m.counter <= 0 && !d.cut && adx < 60) { G.AI.tele(e, 'SF_J1'); return true; }
      }
      // 保持 46 px 左右，慢慢对齐到同一行
      const keep = 46;
      let mx = 0;
      if (adx > keep + 10) mx = dir; else if (adx < keep - 12) mx = -dir;
      const my = clamp(p.y - e.y, -18 * dt, 18 * dt);
      if (mx) { G.world.move(e, mx * e.speed * dt, my); e.play('walk'); } else { if (my) G.world.move(e, 0, my); e.play('idle'); }
      e.facing = dir;
      m.gap = (m.gap == null ? 1.4 : m.gap) - dt;
      if (m.gap > 0 || G.combat.tokens() >= 2 || Math.abs(p.y - e.y) > 12) return true;
      let id;
      if (d.cut) id = adx < 44 ? 'SF_KICK' : 'SF_DASH';
      else if (adx < 60) id = Math.random() < 0.7 ? 'SF_J1' : 'SF_KICK';
      else id = 'SF_DASH';
      if (id === 'SF_DASH' && adx > 130) { m.gap = 0.3; return true; }
      G.AI.tele(e, id);
      m.gap = (d.cut ? 1.3 : 1.6) + Math.random() * 0.8;
      return true;
    },
  };

  // ------------------------------------------------------------------------------------------------ 段 A：学校走廊
  const SA = { arena: [64, 470], ko: [112, 162], jo: [300, 158], sf: [384, 158] };
  let ovA = null;
  // 叠加层：表面头上的视线条、康一头上的血条、笔的红圈
  function drawA(g) {
    const c = G.world.fight;
    if (!c || c.id !== 'b04a_surface' || !G.cam || !G.cam.w2u) return;
    const d = c.data, S = G.S, sf = S.actor('surface'), ko = S.actor('koichi');
    if (sf && !d.penMode && ((d.gaze || 0) > 0.01 || d.ctrl)) {
      const u = G.cam.w2u(sf.x, sf.headY() - 8, 0), x = Math.round(u.x - 16), y = Math.round(u.y - 6);
      g.fillStyle = '#0c0a14'; g.fillRect(x - 1, y - 1, 34, 6);
      g.fillStyle = '#3a1020'; g.fillRect(x, y, 32, 4);
      g.fillStyle = d.ctrl ? (Math.floor(G.clk.ui * 8) % 2 ? '#ff5050' : '#ffd34a') : '#e83040';
      g.fillRect(x, y, Math.round(32 * (d.ctrl ? 1 : d.gaze || 0)), 4);
      P4().text(g, d.ctrl ? '操纵中' : '视线', x + 16, y - 15, '#ffd0d0', 12, 'center');
    }
    if (ko && !d.penMode && ko.vip) {
      const u = G.cam.w2u(ko.x, ko.y - 22, 0), x = Math.round(u.x - 14), y = Math.round(u.y - 4);
      const k = clamp(ko.hp / 90, 0, 1);
      g.fillStyle = '#0c0a14'; g.fillRect(x - 1, y - 1, 30, 5);
      g.fillStyle = '#1a3020'; g.fillRect(x, y, 28, 3);
      g.fillStyle = k < 0.35 ? '#e83040' : '#7ce07c'; g.fillRect(x, y, Math.round(28 * k), 3);
      P4().text(g, '康一', x + 14, y - 14, '#d0ffd0', 12, 'center');
    }
    const pen = S.actor('ch2_pen');
    if (pen && d.penMode && d.ring && !d.penHit) {
      const u = G.cam.w2u(pen.x, pen.y - pen.z - 1, 0), r = 9 + Math.round(Math.abs(Math.sin(G.clk.ui * 6)) * 3);
      g.fillStyle = '#ff3040';
      for (let i = 0; i < 24; i++) {
        const a = (i / 24) * Math.PI * 2;
        g.fillRect(Math.round(u.x + Math.cos(a) * r) - 1, Math.round(u.y + Math.sin(a) * r) - 1, 2, 2);
      }
    }
  }
  function stickPen(S, jo, pen) {
    T().tick(() => {
      if (!pen || pen.remove || !jo || jo.remove) return true;
      if (pen.mem.free) return false;
      pen.x = jo.x + jo.facing * 7; pen.y = jo.y + 0.5; pen.z = 21; pen.facing = -jo.facing;
      return false;
    });
  }
  function endControl(S, c) {
    const d = c.data, jo = S.actor('josuke'), sf = S.actor('surface');
    if (!d.ctrl) return;
    d.ctrl = null; d.gaze = 0; d.gazeCd = 2.2;
    if (jo) { jo.hold = false; jo.state = 'idle'; jo.play('idle'); }
    if (sf) { sf.mem.ctrl = false; sf.state = 'idle'; sf.play('idle'); }
  }
  function startControl(S, c, sf, jo) {
    const d = c.data, ko = S.actor('koichi');
    d.ctrl = { t: 0, dir: ko ? (Math.sign(ko.x - jo.x) || -1) : -1, punched: false };
    d.ctrlN = (d.ctrlN || 0) + 1;
    G.combat.stopRush(jo);
    jo.atk = null; jo.state = 'idle'; jo.hold = true;
    sf.atk = null; sf.tele = null; sf.mem.ctrl = true; sf.mem.counter = 0;
    S.sfx('sting_shock', 0.6);
    S.emote(sf, '照我的样子动吧～', 1.2);
    if (!d.ctrlTold) { d.ctrlTold = true; S.hint('被表面盯住、操纵了！背对它，或者上下换一行，视线就会断', 6); }
  }
  function controlTick(S, c, dt) {
    const d = c.data, q = d.ctrl;
    if (!q) return;
    const jo = S.actor('josuke'), sf = S.actor('surface'), ko = S.actor('koichi');
    if (!jo || !sf) { endControl(S, c); return; }
    q.t += dt;
    if (q.t < 1.3) {
      // 表面怎么走，仗助就怎么走：一起朝倒在地上的康一走过去
      G.world.move(jo, q.dir * 34 * dt, 0); jo.facing = q.dir; jo.play('walk');
      G.world.move(sf, q.dir * 34 * dt, 0); sf.facing = q.dir; sf.play('walk');
    } else if (!q.punched) {
      q.punched = true;
      sf.play('point'); jo.play('point');
      S.standAct(jo, 'punch', { dx: 20, z: 4, dur: 0.45 });
      if (ko && Math.abs(ko.x - jo.x) <= 42 && Math.abs(ko.y - jo.y) <= 14 && ko.hp > 0) {
        ko.hp = Math.max(0, ko.hp - 10); ko.flash = 1;
        d.koHits = (d.koHits || 0) + 1;
        S.sfx('punch', 0.8); S.sfxText('咚', ko, { dur: 0.6 });
      } else S.sfx('whoosh', 0.6);
    } else if (q.t >= 2.0) endControl(S, c);
  }
  function gazeTick(S, c, dt) {
    const d = c.data, jo = player(), sf = S.actor('surface');
    if (!sf || !jo || jo.cid !== 'josuke' || d.penMode || d.ctrl) return;
    d.gazeCd = Math.max(0, (d.gazeCd || 0) - dt);
    const sees = sf.facing === (Math.sign(jo.x - sf.x) || 1) && jo.facing === (Math.sign(sf.x - jo.x) || 1) && Math.abs(jo.y - sf.y) <= 8;
    if (sees && sfReady(sf) && d.gazeCd <= 0) d.gaze = Math.min(1, (d.gaze || 0) + dt * (c.assist ? 0.7 : 1));
    else d.gaze = Math.max(0, (d.gaze || 0) - dt * 1.5);
    if (d.gaze >= 1) startControl(S, c, sf, jo);
  }
  // 过半（HP ≤ 50%）：仗助被操纵着一肘打倒康一 → 背过身偷偷治好他 → 表面抛来一支笔，仗助握着笔对准自己的眼睛 → 换成康一
  async function penScene(S, sf, c) {
    const d = c.data, jo = S.actor('josuke'), ko = S.actor('koichi');
    R.hpA = Math.max(1, Math.round(sf.hp));
    d.penMode = true; d.untouchable = true; d.gaze = 0;
    endControl(S, c);
    S.hint(null);
    G.combat.stopRush(jo);
    jo.atk = null; jo.state = 'idle'; jo.hold = true; jo.play('idle');
    if (jo.stand) jo.stand.recall({ instant: true });
    sf.atk = null; sf.tele = null; sf.mem.hold = true; sf.state = 'idle'; sf.play('idle');
    await S.say('hazamada', '……玩够了。表面，让他去收拾那个小不点。', { expr: 'smile' });
    // 表面往康一那边走，仗助照着走过去
    S.walk(sf, clamp(ko.x + 96, SA.arena[0] + 12, SA.arena[1] - 12), sf.y, { speed: 56 }).catch(G.cancelIgnore);
    await S.walk(jo, ko.x + 24, ko.y - 3, { speed: 56 });
    jo.hold = true; S.face(jo, -1); S.face(sf, -1);
    sf.play('point'); jo.play('point');
    S.sfx('punch', 0.8); S.shake(2, 0.2);
    ko.flash = 1; S.sfxText('咚', ko, { dur: 0.6 });
    await S.wait(0.5);
    await S.say('hazamada', '哈哈！对朋友下手的感觉怎么样？', { expr: 'smile' });
    // 背对着表面和间田，偷偷用疯狂钻石治好康一
    await S.summon(jo, { dur: 0.1, rise: 4 });
    S.standAct(jo, 'reach', { dx: 14, z: 2, dur: 0.7 });
    P4().fixGlow(S, ko.x, ko.y - 6, { n: 5, vol: 0.4 });
    await S.wait(0.6);
    S.recall(jo);
    await S.say('koichi', '（小声）……我没事。', { expr: 'normal' });
    // 表面抛来一支笔：表面举起手，仗助也举起手
    S.face(sf, jo); S.face(jo, sf);
    const pen = T().prop(S, 'pen', sf.x, sf.y + 0.5, { id: 'ch2_pen', z: 20 });
    if (pen) {
      pen.mem.free = true;
      S.sfx('whoosh', 0.6);
      await S.arc(pen, jo.x + jo.facing * 7, jo.y + 0.5, 18, 0.45, { z1: 21, spin: 6 });
      pen.rot = 0; pen.mem.free = false;
      T().setFrame(pen, 0);
      stickPen(S, jo, pen);
    }
    sf.play('point'); jo.play('point');
    await S.say('surface', '这支笔……就戳进你自己的眼睛里吧～', { expr: 'smile' });
    S.sfx('heartbeat', 0.8);
    await S.say('josuke', '（手……停不下来……！）', { expr: 'shock' });
    // 换成康一
    S.unpose(ko);
    ko.untargetable = true;
    G.party.setLeader('koichi', { force: true });
    jo.team = 'npc'; jo.hold = true; jo.state = 'idle'; jo.play('point');
    S.face(ko, jo);
    await S.say('koichi', '（仗助君……！回音，拜托了！）', { expr: 'rage' });
    S.hint('J：给笔贴字！对准仗助手里的笔', 6);
    d.penT = 0; d.penTries = 1; d.ring = false;
  }
  // 康一的拟声字飞到笔那里（±9 px）→ 黑屏、「噗嗤」、仗助的惨叫 → 画面亮起来：笔停在眼前一寸，笔上贴着「噗嗤」两个字
  async function penHit(S, c) {
    const d = c.data, jo = S.actor('josuke'), pen = S.actor('ch2_pen');
    S.hint(null);
    await S.fadeOut(0.12);
    S.sfx('stab', 0.9);
    await S.narrate('噗嗤——', { onBlack: true, auto: 0.6 });
    S.sfx('grunt_jotaro', 0.9);
    await S.narrate('仗助：「呜啊啊啊——！」', { onBlack: true, auto: 0.7 });
    await S.wait(0.3);
    if (jo) { jo.play('shock'); }
    await S.fadeIn(0.3);
    if (pen) S.sfxText('噗嗤', { wx: pen.x, wy: pen.y, wz: pen.z + 2 }, { dur: 3.0 });
    S.sfx('sting_comedy', 0.6);
    S.mark('b04a_pen');
    await S.narrate('是回音的声音。他什么都没刺中。', { pos: 'top' });
    await S.say('hazamada', '刺、刺进去了！哈哈哈哈！', { expr: 'smile' });
    d.penDone = true;
  }
  function penTick(S, c, dt) {
    const d = c.data;
    if (!d.penMode || d.penHit || d.penDone) return;
    const pen = S.actor('ch2_pen');
    if (!pen) return;
    for (const s of G.world.shots) {
      if (s.dead || !s.owner || s.owner.cid !== 'koichi') continue;
      if (Math.abs(s.x - pen.x) <= 9 && Math.abs(s.y - pen.y) <= 10) { s.dead = true; d.penHit = true; cine(c, () => penHit(S, c)); return; }
    }
    d.penT += dt;
    if (d.penT >= 5) {
      // 5 s 没打中：再给一次（不会输），第二次起笔上出红圈
      d.penT = 0; d.penTries++; d.ring = true;
      S.sfx('heartbeat', 0.6);
      S.hint('笔还在往眼睛靠近……对准红圈里的笔按 J！', 5);
    }
  }
  function setupA(S, c) {
    const d = c.data, jo = player(), ko = S.actor('koichi'), sf = S.actor('surface');
    Object.assign(d, { gaze: 0, gazeCd: 1.5, ctrl: null, koHits: 0, evades: 0, untouchable: false, penMode: false, penHit: false, penDone: false, ring: false });
    const pen = S.actor('ch2_pen');
    if (pen) pen.remove = true;
    if (ko) { ko.untargetable = true; S.pose(ko, 'down'); ko.x = SA.ko[0]; ko.y = SA.ko[1]; ko.facing = 1; }
    if (jo) { jo.x = SA.jo[0]; jo.y = SA.jo[1]; jo.facing = 1; }
    if (sf) { sf.atlas = G.atlas('surface'); sf.facing = -1; Object.assign(sf.mem, { gap: 1.2, open: 0, ctrl: false, hold: false, counter: 0, lastAtk: null }); }
    c.on('evade', (ev) => {
      if (!sf || ev.who !== sf || d.untouchable) return;
      d.evades++;
      if (d.evades === 3 && !d.evadeTold) { d.evadeTold = true; S.hint('正面的拳全被它躲开了：等它出完一套招、露出破绽（愣住）再打，或者绕到侧面、背后！', 7); }
    });
    S.hint('表面面对你时会躲开正面的拳，视线条满了还会操纵你：上下换一行断开视线，等它出完招露出破绽再打！', 8);
  }
  function tickA(S, c, dt) {
    const d = c.data;
    if (d.penMode) { penTick(S, c, dt); return; }
    controlTick(S, c, dt);
    gazeTick(S, c, dt);
  }
  R.fightSurfaceA = async function (S) {
    S.hint(null);
    if (ovA) ovA.close();
    ovA = P4().overlay(drawA, { z: 2 });
    let res;
    try {
      res = await S.fight({
        id: 'b04a_surface', arena: SA.arena, lead: 'josuke', swap: false, lockMsg: '康一倒在地上……这一段只能由仗助应战',
        music: 'battle', after: null, dmgScale: DMG, energy: { start: 0 }, vip: 'koichi', vipHp: 90,
        waves: [[{ kit: 'e_surface', actor: 'surface', cid: 'surface', id: 'surface', name: '表面', x: SA.sf[0], y: SA.sf[1], boss: true, hp: 600, minHp: 240,
          phases: [{ at: 0.5, run: (S2, e, c) => penScene(S2, e, c) }] }]],
        testHint: (c) => {
          const sf = G.S.actor('surface'), ko = G.S.actor('koichi'), d = c.data;
          return { sfHp: sf ? Math.round(sf.hp) : null, koHp: ko ? ko.hp : null, gaze: Math.round((d.gaze || 0) * 100) / 100, ctrlN: d.ctrlN || 0,
            koHits: d.koHits || 0, evades: d.evades || 0, penMode: !!d.penMode, penTries: d.penTries || 0, penDone: !!d.penDone };
        },
        onWave: async (S2, wi, spawned, attempt, c) => { setupA(S2, c); },
        tick: (c, dt) => tickA(S, c, dt),
        endWhen: (c) => !!c.data.penDone,
      });
    } finally { if (ovA) { ovA.close(); ovA = null; } }
    const ko = S.actor('koichi');
    if (ko) { ko.vip = false; ko.untargetable = false; }
    S.hint(null);
    return res;
  };

  // ------------------------------------------------------------------------------------------------ 段 B：商店街（老酒铺门口）
  const SB = { arena: [240, 640], crates: [364, 150], sf: [470, 156] };
  function clearB(S) {
    for (const a of G.world.stage.actors) if (a.id && (a.id.indexOf('ch2_shard_') === 0 || a.id === 'ch2_bottle')) a.remove = true;
  }
  // J3 打碎啤酒箱：碎玻璃飞向表面，它伸手全接住
  async function shardsFly(S, c) {
    const d = c.data, jo = S.actor('josuke'), sf = S.actor('surface');
    S.hint(null);
    S.sfx('glass_break', 0.9); S.sfx('crash', 0.6); S.shake(2, 0.25);
    S.fx('burst', { x: SB.crates[0], y: 136, n: 14, speed: 40, colours: ['#d8f0e8', '#8ac8a0', '#f4f8f0'], gravity: 140, life: 0.8 });
    sf.atk = null; sf.tele = null; sf.state = 'idle'; sf.mem.hold = true;
    S.face(sf, -1);
    const hx = () => sf.x + sf.facing * 6;
    const shards = [];
    for (let i = 0; i < 5; i++) {
      const sh = T().prop(S, 'glass_shard', SB.crates[0] + (i - 2) * 3, SB.crates[1] + 0.5, { id: 'ch2_shard_' + i, frame: i % 2, z: 12 + i * 2 });
      if (sh) shards.push(sh);
    }
    S.sfx('whoosh', 0.7);
    await Promise.all(shards.map((sh, i) => S.arc(sh, hx() + (i - 2) * 2, sf.y + 0.5, 10 + i * 3, 0.32 + i * 0.05, { z1: 15 + (i % 3) * 2 })));
    sf.play('point');
    S.sfx('clang', 0.4, 1.6);
    // 碎玻璃跟着表面的手走
    shards.forEach((sh, i) => {
      T().setFrame(sh, i % 2);
      T().tick(() => {
        if (sh.remove || sf.remove || sh.mem.free) return true;
        sh.x = sf.x + sf.facing * 6 + (i - 2) * 2; sh.y = sf.y + 0.5; sh.z = (sf.z || 0) + 15 + (i % 3) * 2;
        return false;
      });
    });
    await S.say('surface', '想用碎玻璃扎我？太慢了，Great～', { expr: 'smile' });
    await S.say('josuke', '……全接住了啊。那正好。', { expr: 'smile' });
    d.shards = true;
    sf.mem.hold = false;
    S.hint('按住 L 按 J：修复！', 10);
  }
  // 按住 L 按 J：碎片在表面手里拼回酒瓶，把木头右手夹断
  async function trapHand(S, c) {
    const d = c.data, jo = S.actor('josuke'), sf = S.actor('surface');
    S.hint(null);
    sf.atk = null; sf.tele = null; sf.state = 'idle'; sf.mem.hold = true; sf.play('point');
    S.face(jo, sf);
    await S.summon(jo, { dur: 0.1, rise: 4 });
    S.standAct(jo, 'reach', { dx: 18, z: 4, dur: 0.8 });
    S.sfx('sparkle', 0.9);
    const hx = sf.x + sf.facing * 7, hy = sf.y + 0.5;
    const shards = [0, 1, 2, 3, 4].map((i) => S.actor('ch2_shard_' + i)).filter(Boolean);
    shards.forEach((sh) => { sh.mem.free = true; });
    await Promise.all(shards.map((sh) => { const x0 = sh.x, z0 = sh.z; return S.animate(0.3, (k) => { sh.x = G.lerp(x0, hx, k); sh.z = G.lerp(z0, 16, k); }); }));
    shards.forEach((sh) => { sh.remove = true; });
    P4().fixGlow(S, hx, hy - 18, { n: 8, r: 10 });
    const bottle = T().prop(S, 'bottle', hx, hy, { id: 'ch2_bottle', z: 12 });
    S.sfx('glass_break', 0.5, 1.4); S.sfx('axe_chop', 0.9);
    S.fx('burst', { x: hx, y: sf.y - 16, n: 10, speed: 34, colours: ['#c89a5a', '#8a5a2a', '#e8c890'], gravity: 160, life: 0.7 });
    sf.atlas = G.atlas('surface_cut'); sf.play('hurt'); sf.flash = 1;
    sf.hp = Math.max(1, sf.hp - 40);
    sf.dmgOut = 0.6; sf.speed = 48;
    S.shake(3, 0.3);
    S.sfxText('咔！', sf, { dur: 0.8 });
    if (bottle) await S.arc(bottle, hx + sf.facing * 12, hy + 4, 8, 0.4, { z1: 0, spin: 3 });
    S.recall(jo);
    S.mark('b04b_bottle');
    await S.say('surface', '我、我的手……！', { expr: 'shock' });
    await S.say('josuke', '本来就是块木头吧。修好的酒瓶，可不会把它还给你。', { expr: 'smile' });
    d.untouchable = false; d.noDodge = true; d.cut = true;
    sf.mem.hold = false; sf.mem.open = 0; sf.state = 'idle'; sf.play('idle');
    S.hint('表面没了右手，躲不开了：打它！（Q 换康一也行）', 5);
  }
  // HP ≤ 25%：间田喊「走了！」，带着表面往道口那边跑
  async function fleeScene(S, sf, c) {
    const d = c.data, hz = S.actor('hazamada');
    S.hint(null);
    sf.mem.hold = true; sf.atk = null; sf.tele = null; sf.state = 'idle';
    await S.say('hazamada', '走了！表面！', { expr: 'shock' });
    if (hz) S.walk(hz, 1010, 152, { speed: 110, anim: 'run' }).then(() => { hz.visible = false; }, G.cancelIgnore);
    S.face(sf, 1);
    await S.walk(sf, Math.min(sf.x + 150, 1000), 156, { speed: 110, anim: 'run' });
    sf.visible = false;
    d.fled = true;
  }
  function setupB(S, c) {
    const d = c.data, sf = S.actor('surface');
    Object.assign(d, { untouchable: true, shards: false, trap: false, noDodge: false, cut: false, fled: false, brkAtk: null });
    clearB(S);
    if (sf) {
      sf.atlas = G.atlas('surface'); sf.dmgOut = 1; sf.speed = 60; sf.visible = true;
      sf.hp = clamp(R.hpA || 300, 160, sf.maxHp);
      sf.facing = -1;
      Object.assign(sf.mem, { gap: 1.0, open: 0, ctrl: false, hold: false, counter: 0, lastAtk: null });
    }
    d.lastAtk = G.input.lastPress('attack');
    S.hint('表面躲得太快，现在一下都打不中。用 J3 打碎老酒铺门口的啤酒箱！', 8);
  }
  function tickB(S, c, dt) {
    const d = c.data, p = player();
    if (!p) return;
    if (!d.shards) {
      const a = p.atk, slot = a && a.slot;
      if (p.cid === 'josuke' && a && (slot === 'J3' || slot === 'fin') && a !== d.brkAtk && p.atkT >= a.active[0] && p.atkT <= a.active[1] + f(2)) {
        d.brkAtk = a;
        const dx = (SB.crates[0] - p.x) * p.facing;
        if (dx >= -6 && dx <= 48 && Math.abs(p.y - SB.crates[1]) <= 12) { cine(c, () => shardsFly(S, c)); return; }
      }
      if (!d.crateTold && c.t > 25) { d.crateTold = true; S.hint('仗助走到啤酒箱（老酒铺门口）旁边，面朝它打出 J3（J 连按三下）', 7); }
      d.lastAtk = G.input.lastPress('attack');
      return;
    }
    if (!d.trap) {
      const lp = G.input.lastPress('attack');
      if (lp !== d.lastAtk) {
        d.lastAtk = lp;
        if (p.cid === 'josuke' && p.state === 'guard') { d.trap = true; cine(c, () => trapHand(S, c)); return; }
      }
      if (p.cid !== 'josuke' && !d.swapTold) { d.swapTold = true; S.hint('修复要仗助来：按 Q 换回仗助', 4); }
    }
  }
  R.fightSurfaceB = async function (S) {
    S.hint(null);
    const res = await S.fight({
      id: 'b04b_surface', arena: SB.arena, lead: 'josuke', swap: true, allies: ['koichi'],
      music: 'battle', after: null, dmgScale: DMG, energy: { start: 0 },
      waves: [[{ kit: 'e_surface', actor: 'surface', cid: 'surface', id: 'surface', name: '表面', x: SB.sf[0], y: SB.sf[1], boss: true, hp: 600, minHp: 120,
        phases: [{ at: 0.25, run: (S2, e, c) => fleeScene(S2, e, c) }] }]],
      testHint: (c) => {
        const sf = G.S.actor('surface'), d = c.data;
        return { sfHp: sf ? Math.round(sf.hp) : null, shards: !!d.shards, trap: !!d.trap, cut: !!d.cut, fled: !!d.fled, lead: player() ? player().cid : null };
      },
      onRetry: async (S2) => { clearB(S2); },
      onWave: async (S2, wi, spawned, attempt, c) => { setupB(S2, c); },
      tick: (c, dt) => tickB(S, c, dt),
      endWhen: (c) => !!c.data.fled,
    });
    clearB(S);
    S.hint(null);
    return res;
  };

  // ------------------------------------------------------------------------------------------------ 段 C：抗拒（目标段，不会输）
  //   被隔着橱窗操纵的仗助一步步走向承太郎背后：每秒往前 8 px；连按 J 往回推（每下 1.6 px，一秒最多算 7 下，照第三部）。
  //   撑满 dur 秒（飙车族冲进来）或者走到 endX（承太郎按住手腕）就结束。机器人读 R.resist
  R.resist = null;
  R.resistRun = async function (S, o = {}) {
    const jo = S.actor('josuke'), I = G.input, run = G.runId;
    const st = { t: 0, x0: jo.x, dur: o.dur || 6, endX: o.endX || jo.x + 44, speed: o.speed || 8, push: 1.6, presses: [], open: true, n: 0 };
    R.resist = st;
    const lines = (o.lines || []).slice();
    const h = P4().overlay((g) => {
      if (!st.open) return;
      const k = clamp((jo.x - st.x0) / Math.max(1, st.endX - st.x0), 0, 1);
      const x0 = 160, w = 320, y = 62;          // 画面上方：人都站在下面那条可走带上，放下面会把仗助整个盖住
      G.ui.box(g, x0 - 10, y - 26, x0 + w + 10, y + 16);
      P4().text(g, '抗拒', x0, y - 20, '#ffe9a8', 12, 'left');
      P4().text(g, '连按 J！别让手靠近承太郎！', x0 + w, y - 20, '#fff4d6', 12, 'right');
      g.fillStyle = '#0c0a14'; g.fillRect(x0 - 1, y - 1, w + 2, 8);
      g.fillStyle = '#2a2030'; g.fillRect(x0, y, w, 6);
      g.fillStyle = k > 0.66 ? '#e83040' : '#ffd34a'; g.fillRect(x0, y, Math.round(w * k), 6);
      G.ui.keyCap(g, x0 + w + 16, y - 10, 'J', Math.floor(G.clk.ui * 8) % 2 === 0, 18);
    }, { z: 3 });
    let last = G.clk.world;
    try {
      await G.until(() => {
        if (run !== G.runId) return true;
        const t = G.clk.world, dt = Math.max(0, Math.min(0.05, t - last));
        last = t;
        st.t += dt;
        st.presses = st.presses.filter((q) => t - q < 1);
        let back = 0;
        if (I.hit('attack') && st.presses.length < 7) { st.presses.push(t); st.n++; back = st.push; }
        jo.x = Math.max(st.x0 - 12, jo.x + st.speed * dt - back);
        jo.facing = 1;
        jo.play(back ? 'guard' : 'walk');
        while (lines.length && st.t >= lines[0].at) { const l = lines.shift(); if (l.run) l.run(); }
        return st.t >= st.dur || jo.x >= st.endX;
      });
    } finally { st.open = false; h.close(); R.resist = null; }
    jo.play('idle');
    return { held: jo.x < st.endX, x: jo.x, presses: st.n };
  };
})();
