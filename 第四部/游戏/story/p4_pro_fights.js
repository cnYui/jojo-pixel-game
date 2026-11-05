// 序章的三场战斗（开发脚本 §3）：序1「承太郎的试探」（六步教学）、序2 段 1「水中项链」（客厅水汽战）、段 2「雨中追本体」。
//   剧情节拍在 story/p4_prologue.js；这里只管开打到打完。招式和对手的 brain 在 engine/p4_moves.js。
//   战斗里要“停下来演一下”的地方（钻嘴、吐出来、抓住安杰罗）不走 spec.events（每次尝试只触发一次），用 cine() 自己暂停战斗。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const f = (n) => n / 60;
  const R = (G.P4PRO = {});

  // 在战斗里插一段演出：和 fight.js 的 paused() 一样把 W.cine 占住（玩家、敌人、战斗 tick 都停），演完还回去。
  //   战斗已经结束 / 回了标题就什么都不做
  async function cine(ctx, fn) {
    const W = G.world, run = G.runId;
    if (W.fight !== ctx) return;
    const old = W.cine;
    W.cine = { by: 'p4-fight' };
    try { await fn(); } catch (e) { if (!G.cancelled(e)) console.error(e); } finally { if (run === G.runId && W.fight === ctx) W.cine = old || null; }
  }
  const player = () => G.world.player;
  const member = (cid) => ((G.party && G.party.members) || []).find((a) => a.cid === cid) || null;

  // =====================================================================================================================
  // 序1 承太郎的试探（b_pro1_jotaro）：仗助单挑，目标段，HP 最低到 1
  // =====================================================================================================================
  const P1 = { arena: [150, 470], jt: [300, 158] };
  const T1_HINT = {
    1: '发型暴走中！对着承太郎按 J 三下（J1→J2→J3）',
    2: 'J3 打出去以后接着连按 J：DORARARA！',
    3: '承太郎出拳了：拳头亮起来就按 K 闪开（2 次）',
    4: '按住 L 格挡：疯狂钻石会替你挡下（2 次）',
    5: '拳头碰到你的前一瞬间按一下 L：精准格挡',
    6: '能量满了：按 U！',
  };
  // 发型暴走：攻击 ×1.5、不会硬直（armor）、不能格挡（noGuard，第四部在 combat.js 加的），屏幕边缘泛紫
  function hairRage(S, on) {
    const p = member('josuke') || player();
    if (!p) return;
    if (on) {
      p.dmgOut = 1.5; p.armor = true; p.noGuard = true;
      S.filter('vignette', 0.45, { colour: '#a040c0', inner: 0.55 });
    } else {
      p.dmgOut = 1; p.armor = false; p.noGuard = false;
      S.filter('vignette', null);
    }
  }
  R.hairRage = hairRage;
  function t1Next(S, ctx, k) {
    const d = ctx.data;
    d.step = k; d.ok = 0; d.relax = false; d.stepT0 = ctx.t; d.demoed = false; d.forced = false;
    d.evades = 0; d.guards = 0; d.parryFails = 0;
    S.hint(T1_HINT[k], 60);
    if (k === 6) { ctx.fillEnergy(); S.sfx('meter_full', 0.8); }
  }
  let demoH = null;            // 自动示范的按键帽（叠加层）：打完要关掉
  function t1Setup(S, ctx) {
    const d = ctx.data;
    hairRage(S, true);
    if (demoH) demoH.h.close();
    demoH = d.demo = P4().keyDemo(() => player());
    t1Next(S, ctx, 1);
    // 第 ③ 步：闪开 2 次。一次出拳只算一次（闪避判定 evade / 擦身 graze / 拳头到跟前时按了 K，三样都可能同时来）
    const evadeOnce = () => {
      if (d.step !== 3 || ctx.t - (d.lastEv == null ? -9 : d.lastEv) < 0.6) return;
      d.lastEv = ctx.t;
      if (++d.evades >= 2) d.ok = 3; else S.sfx('blip', 0.5);
    };
    ctx.on('evade', (e) => { if (e.who === player()) evadeOnce(); });
    ctx.on('graze', (e) => { if (e.who === player()) evadeOnce(); });
    ctx.on('dodge', (e) => {
      const p = player(), jt = S.actor('jotaro4');
      if (d.step !== 3 || !p || !jt || (e && e.who !== p)) return;
      const busy = jt.tele || (jt.atk && jt.atkT < jt.atk.active[1]);
      if (busy && Math.abs(jt.x - p.x) <= 80) evadeOnce();
    });
    // 第 ④ 步：挡住 2 次（慢速欧拉一串算两次：0.5 s 去重）；精准格挡也算
    const guardOnce = () => {
      if (d.step !== 4 || ctx.t - (d.lastGd == null ? -9 : d.lastGd) < 0.5) return;
      d.lastGd = ctx.t;
      if (++d.guards >= 2) d.ok = 4; else S.sfx('blip', 0.5);
    };
    ctx.on('guard', (e) => { if (e.who === player()) guardOnce(); });
    ctx.on('parry', (e) => {
      if (e.who !== player()) return;
      if (d.step === 4) guardOnce();
      if (d.step === 5) d.ok = 5;
    });
    // 第 ⑤ 步：两次没弹到（挨打或者只是普通格挡）就放宽判定窗口
    ctx.on('hit', (e) => {
      if (d.step !== 5 || e.t !== player() || ctx.t - (d.lastFail == null ? -9 : d.lastFail) < 0.8) return;
      d.lastFail = ctx.t;
      if (++d.parryFails >= 2 && !d.relax) {
        d.relax = true;
        ctx.spec.kitOverride.josuke.parryWin = f(16);
        S.hint('承太郎的拳头一亮白光就按一下 L（判定放宽了）', 60);
      }
    });
    ctx.on('special', () => { if (d.step === 6) S.hint(null); });
    T().tick(() => {
      if (G.world.fight !== ctx) return true;
      const p = player();
      if (!p || G.world.cine) return false;
      const slot = p.atk && p.atk.slot;
      if (d.step === 1 && slot === 'J3') d.ok = 1;
      if (d.step === 2 && (slot === 'fin' || p.state === 'rushEnd')) d.ok = 2;
      if (d.step === 6 && ctx.storyU && !d.u6) { d.u6 = true; S.hint(T1_HINT[6], 60); }
      // 发型暴走中按 L：不让格挡，头上冒一句
      if (d.step <= 2 && G.input.isDown('guard') && ctx.t - (d.calmT == null ? -9 : d.calmT) > 2.5) { d.calmT = ctx.t; S.emote(p, '冷静不下来！', 1.2); }
      const el = ctx.t - (d.stepT0 || 0);
      // 卡住 30 s：自动示范一次（头顶亮按键）；示范完 15 s 还没过，就当这一步过了（教学不能卡死人）
      if (!d.demoed && el > 30) { d.demoed = true; d.demoT = ctx.t; demoStep(S, ctx, d.step).catch(G.cancelIgnore); }
      if (d.demoed && !d.forced && d.ok !== d.step && ctx.t - d.demoT > 15) { d.forced = true; d.ok = d.step; }
      return false;
    });
  }
  // 自动示范：真的往输入里塞按键（G.input.inject / press），和玩家自己按一模一样
  async function demoStep(S, ctx, k) {
    const d = ctx.data, I = G.input, demo = d.demo, run = G.runId;
    const live = () => run === G.runId && G.world.fight === ctx && d.step === k && d.ok !== k;
    const tap = async (a, label, gap) => { if (!live()) return; demo.press(label, 0.16); I.inject(a); await G.wait(gap, 'world'); };
    const jt = () => S.actor('jotaro4');
    // 等承太郎这一拳快到了：返回离命中还有多少秒
    const waitPunch = async (lead) => {
      await G.until(() => !live() || (jt() && jt().tele && jt().tele.dur - jt().tele.t <= lead));
    };
    S.sfx('ding', 0.4);
    if (k === 1) { for (let i = 0; i < 3; i++) await tap('attack', 'J', 0.22); }
    else if (k === 2) {
      for (let i = 0; i < 3; i++) await tap('attack', 'J', 0.22);
      for (let i = 0; i < 14; i++) await tap('attack', 'J', 0.07);
    } else if (k === 3) {
      for (let i = 0; i < 2 && live(); i++) { await waitPunch(0.12); await tap('dodge', 'K', 0.8); }
    } else if (k === 4) {
      for (let i = 0; i < 2 && live(); i++) {
        await waitPunch(0.5);
        if (!live()) break;
        demo.press('L', 1.6); I.press('guard', 'demo');
        await G.wait(1.6, 'world');
        I.release('guard', 'demo');
      }
    } else if (k === 5) {
      for (let i = 0; i < 2 && live(); i++) { await waitPunch(0.08); await tap('guard', 'L', 0.9); }
    } else if (k === 6) await tap('special', 'U', 0.3);
    demo.label = null;
  }
  const t1Event = (k, line) => ({
    when: (t, ctx) => ctx.data.step === k && ctx.data.ok === k,
    run: async (S, es, attempt, ctx) => {
      ctx.step(k);
      S.sfx('ding', 0.6);
      if (ctx.data.demo) ctx.data.demo.label = null;
      if (k === 2) {
        hairRage(S, false);
        S.flash(0.15, 0.4, '#e0b0ff');
      }
      if (line) await S.say(line[0], line[1], line[2] || {});
      if (k === 2) await S.say('josuke', '……呼。头脑总算冷下来了。', { expr: 'normal' });
      t1Next(S, ctx, k + 1);
    },
  });
  // 第 ⑥ 步的剧情 U：多拉拉拉冲上去，命中前一帧全屏灰阶 0.6 s（时停），承太郎已经站在仗助背后，拳头落空
  async function finaleTs(S, p, ctx, C) {
    const jt = S.actor('jotaro4');
    ctx.data.uUsed = true;          // 窗口关上：「按 U！」提示和金色 U 钮不再亮着
    S.hint(null);
    if (ctx.data.demo) ctx.data.demo.label = null;
    const st = G.world.stage;
    const [lo, hi] = st.bounds ? st.bounds() : [st.x0 + 10, st.x1 - 10];
    if (jt) {
      // 冲到承太郎面前；时停后他要站到仗助“背后” 26 px 处。背后那一侧没地方了（贴着场地边）就从另一侧冲过去，
      //   不然夹紧以后承太郎会和仗助叠在同一个位置，把仗助整个挡住
      p.facing = jt.x < p.x ? -1 : 1;
      if (jt.x - p.facing * 34 - p.facing * 26 < lo || jt.x - p.facing * 34 - p.facing * 26 > hi) p.facing = -p.facing;
      await C.dash(G.clamp(jt.x - p.facing * 34, lo, hi), jt.y, f(8));
    }
    C.stand('rush', { dx: 16, jitter: 1 });
    await C.rush(0.5, { dmg: false, tick: f(12), word: 'DORA', visual: { reach: 26, spread: 30, rate: 45, scale: 1.2, big: 0.25 } });
    S.sfx('timestop', 0.9);
    S.filter('gray', 1);
    G.hitStopAll(0.5);
    await S.wait(0.6, 'ui');
    if (jt) {
      jt.atk = null; jt.tele = null; jt.state = 'idle'; jt.play('idle');
      jt.x = G.clamp(p.x - p.facing * 26, lo, hi); jt.y = p.y + 2; jt.facing = p.facing;
      if (jt.stand) jt.stand.recall({ instant: true });
    }
    S.filter('gray', null);
    S.sfx('time_resume', 0.8);
    C.stand('punch', { dx: 24, seq: [[2, 99]] });
    S.sfx('whoosh', 0.9);
    await C.wait(0.25);
    S.sfxText('！？', p, { dur: 0.9 });
    S.mark('pro_ts_dodge');
    await C.wait(0.55);
    ctx.data.finaleU = true;
    ctx.end();
  }
  R.fightJotaro = async function (S) {
    S.hint(null);
    const jt = S.actor('jotaro4');
    if (jt && !jt.stand && jt.setStand) jt.setStand('starplat');
    const res = await S.fight({
      id: 'b_pro1_jotaro', arena: P1.arena, lead: 'josuke', swap: false, lockMsg: '这一战只能由仗助应战',
      music: 'battle', after: null, dmgScale: 0.8, playerMinHp: 1, losable: false, coverage: false,
      energy: { start: 0 },
      steps: { n: 6, label: '承太郎的试探' },
      kitOverride: { josuke: { parryWin: f(10), special: { need: 100, title: 'josuke', bg: 'radial', colours: ['#6a1a4a', '#3a0a28', '#a8306e'],
        window: (c) => c.data.step === 6 && !c.data.uUsed, prompt: '按 U！', run: finaleTs } } },
      // boss: true 只为不画头顶小血条（HUD 这一战显示教学进度格）；9999 血 + 最低 1 血：怎么打也打不倒
      waves: [[{ kit: 'e_jotaro4_test', actor: 'jotaro4', cid: 'jotaro4', id: 'jotaro4', name: '空条承太郎', x: P1.jt[0], y: P1.jt[1],
        boss: true, hp: 9999, minHp: 1, idle: 'idle' }]],
      testHint: (ctx) => ({ step: ctx.data.step || 0, ok: ctx.data.ok || 0, relax: !!ctx.data.relax, demoed: !!ctx.data.demoed }),
      onWave: async (S2, wi, spawned, attempt, ctx) => { t1Setup(S2, ctx); },
      events: [
        t1Event(1, ['jotaro4', '……冷静点。']),
        t1Event(2, ['jotaro4', '你也有替身啊。']),
        t1Event(3, null),
        t1Event(4, ['jotaro4', '力气不小。']),
        t1Event(5, null),
      ],
      endWhen: (ctx) => !!ctx.data.finaleU,
    });
    // 打完：发型暴走的残留清掉；承太郎变回普通 NPC（他是剧情里现成的那个人，战斗只是借他当对手）
    hairRage(S, false);
    if (demoH) { demoH.h.close(); demoH = null; }
    if (jt) {
      jt.team = 'npc'; jt.kit = G.KITS.jotaro4; jt.brain = null; jt.moves = []; jt.armor = false; jt.dmgMul = null; jt.onHitBy = null;
      jt.atk = null; jt.tele = null; jt.state = 'idle'; jt.play('idle');
      if (jt.stand) jt.stand.recall({ instant: true });
    }
    return res;
  };

  // =====================================================================================================================
  // 序2 段 1 水中项链（b_pro2_aqua）：客厅，仗助 + 承太郎（AI，Q 换人）
  // =====================================================================================================================
  const LR = { arena: [18, 462], hum: [26, 150], wall: [159, 146], hole: [159, 104], glove: [380, 147], box: [374, 98], sink: [400, 146] };
  const LOW = 0.3;              // 项链 HP 低于 30%：可以引它钻进含着手套的嘴里
  let gloveH = null;
  const prop = (S, id) => S.actor(id);
  // 仗助张着嘴：连打、连打终结、挨打喊痛
  const mouthOpen = (p) => !!p && (p.state === 'rush' || p.state === 'rushEnd' || p.state === 'hurt' || !!p.rush);
  function aquaProps(S) {
    const hum = prop(S, 'lr_hum') || T().prop(S, 'humidifier', LR.hum[0], LR.hum[1], { id: 'lr_hum', frame: 0 });
    T().setFrame(hum, 0);
    const box = prop(S, 'lr_box') || T().prop(S, 'glovebox', LR.box[0], 142, { id: 'lr_box', frame: 0, z: 44 });
    T().setFrame(box, 0);
    const hole = prop(S, 'lr_hole');
    if (hole) hole.remove = true;
  }
  function humPulse(S, c) {
    const hum = prop(S, 'lr_hum');
    if (!hum) return;
    S.sfx('blip', 0.7);
    S.sfxText('嘀', { wx: LR.hum[0], wy: LR.hum[1], wz: 26 }, { dur: 0.6 });
    T().setFrame(hum, 1);
    G.defer(1.2, () => { if (!c.data.humBroken) T().setFrame(hum, 0); });
    S.fx('smoke', { x: LR.hum[0] + 2, y: LR.hum[1] - 14, colour: '#f0f4f8', loop: true, rise: 34, t1: 1.2, life: 1.2 }, { life: 1.8 });
    if (c.gauge) c.gauge.add(40);
    S.hint('加湿器自己开了：水汽 +40（J3 打碎它就不会再开）', 5);
  }
  function breakHum(S, c) {
    const d = c.data;
    d.humBroken = true;
    T().setFrame(prop(S, 'lr_hum'), 2);
    S.sfx('glass_break', 0.8); S.sfx('crash', 0.5);
    S.fx('burst', { x: LR.hum[0], y: LR.hum[1] - 8, n: 10, speed: 30, colours: ['#e8e8e0', '#a0a8b0'], gravity: 120, life: 0.7 });
    S.shake(2, 0.2);
    S.hint('加湿器打坏了，不会再自己开了', 4);
  }
  function openWall(S, c) {
    const d = c.data;
    d.wallOpen = true; d.hole = [LR.wall[0], LR.wall[1]];
    T().prop(S, 'wallhole', LR.hole[0], 142, { id: 'lr_hole', frame: 0, z: 26 });
    if (c.gauge) c.gauge.add(-50);
    S.sfx('crash', 0.9); S.sfx('rain_loop', 0.5);
    S.fx('burst', { x: LR.wall[0], y: 120, n: 14, speed: 34, colours: ['#d8c8a8', '#a08060'], gravity: 120, life: 0.8 });
    S.fx('smoke', { x: LR.wall[0], y: 112, colour: '#f4f8fc', loop: true, rise: 30, t1: 1.6, life: 1.4 }, { life: 2.2 });
    S.shake(3, 0.3);
    S.hint('墙上开了洞，水汽散出去了（−50）。可雨会飘进来：它能顺着雨丝从洞口钻进来！按住 L 按 J 修好墙', 7);
  }
  function fixThing(S, c, what) {
    const d = c.data, p = player();
    S.standAct(p, 'reach', { dx: 16, z: 6, dur: 0.6 });
    if (what === 'wall') {
      d.wallOpen = false; d.hole = null;
      const hole = prop(S, 'lr_hole');
      if (hole) hole.remove = true;
      P4().fixGlow(S, LR.hole[0], LR.hole[1] + 4);
      S.hint('墙修好了：雨进不来，它也钻不进来了', 4);
    } else {
      d.humBroken = false; d.humT = 0;
      T().setFrame(prop(S, 'lr_hum'), 0);
      P4().fixGlow(S, LR.hum[0], LR.hum[1] - 8);
      S.hint('……加湿器也修好了。（修它对你可没好处）', 4);
    }
  }
  // 打散（重击打中）：0.6 s 看不见、打不到，然后在别处重组
  function scatter(S, aq, c) {
    if (!aq || aq.mem.scatter > 0 || c.data.inMouth) return;
    aq.mem.scatter = 0.6;
    aq.atk = null; aq.tele = null; aq.state = 'idle';
    G.AI.hide(aq, true, { alpha: 0 });
    S.fx('water_splash', { x: aq.x, y: aq.y - 10, size: 1.2 }, { life: 0.6 });
    S.sfx('splash', 0.7);
  }
  function reform(S, aq, c) {
    const st = G.world.stage, p = player();
    // 一半时候重组到仗助附近（引它钻嘴的机会），一半到客厅另一头
    let x = p.x + (Math.random() < 0.5 ? -1 : 1) * (40 + Math.random() * 60);
    if (Math.random() < 0.5) x = p.x < 240 ? 330 + Math.random() * 100 : 60 + Math.random() * 100;
    aq.x = G.clamp(x, st.x0 + 14, st.x1 - 14); aq.y = G.clamp(p.y + (Math.random() * 16 - 8), st.yMin, st.yMax);
    G.AI.hide(aq, false);
    aq.alpha = Math.max(0.15, 1 - (c.data.vapor || 0) / 120);
    S.fx('water_splash', { x: aq.x, y: aq.y - 12, size: 0.9 }, { life: 0.5 });
    S.sfx('bubbles', 0.5);
  }
  // 钻嘴：先在仗助头顶亮 0.35 s 红圈；红圈亮完嘴还张着、它还在 48 px 内 → 钻进去
  async function mouthEntry(S, c, aq) {
    const d = c.data, p = player();
    d.inMouth = true;
    d.entries = (d.entries || 0) + 1;
    const trap = d.glove && p.cid === 'josuke' && aq.hp <= aq.maxHp * LOW;
    aq.atk = null; aq.tele = null;
    aq.mem.hold = true;
    S.sfx('slime', 0.8);
    const x0 = aq.x, y0 = aq.y, z0 = aq.z || 0;
    await S.animate(0.22, (k) => { aq.x = G.lerp(x0, p.x + p.facing * 4, k); aq.y = G.lerp(y0, p.y + 0.5, k); aq.z = G.lerp(z0, 22, k); aq.scale = 1 - 0.6 * k; });
    aq.visible = false;
    if (trap) {
      // 含着的乳胶手套：项链钻进来正好被兜住。拉出来打个结 = 段 1 结束
      S.sfx('pop', 0.9);
      S.sfxText('咕！', p, { dur: 0.8 });
      S.shake(2, 0.3);
      d.trapped = true;
      S.mark('pro_aqua_trapped');
      return;
    }
    const dmg = Math.round(20 * 0.8);
    p.hp = Math.max(1, p.hp - dmg); p.flash = 1;
    p.state = 'hurt'; p.play('hurt'); p.atk = null;
    if (p.rush) { if (p.rush.loop && p.rush.loop.stop) p.rush.loop.stop(0.05); p.rush = null; }
    S.sfx('bubbles', 0.9); S.shake(3, 0.4);
    S.sfxText('咕噜咕噜', p, { dur: 1.0 });
    if (!d.mouthTold) { d.mouthTold = true; S.hint('它钻进嘴里了！连按 J 把它吐出来！', 4); }
    const ok = await S.mash({ need: 12, time: 2.4, label: '连按 J！吐出来！' });
    if (!ok) { p.hp = Math.max(1, p.hp - Math.round(10 * 0.8)); p.flash = 1; S.sfx('punch', 0.6); }
    // 吐出来：落在 40 px 外，打散一下再重组
    const st = G.world.stage;
    aq.x = G.clamp(p.x + p.facing * 40, st.x0 + 14, st.x1 - 14); aq.y = p.y; aq.z = 14; aq.scale = 1; aq.visible = true;
    S.sfx('splash', 0.9);
    S.fx('water_splash', { x: p.x + p.facing * 14, y: p.y - 24, size: 1.0 }, { life: 0.6 });
    aq.mem.hold = false;
    p.state = 'idle'; p.play('idle'); p.iframe = 0.6;
    d.inMouth = false;
    d.entryCd = 5;
    scatter(S, aq, c);
    if (!d.glove && aq.hp <= aq.maxHp * LOW && !d.lowTold) {
      d.lowTold = true;
      await S.say('josuke', '这家伙……光吐出来没完没了！得有什么东西把它兜住。', { expr: 'rage' });
    }
  }
  function aquaSetup(S, ctx) {
    const d = ctx.data;
    aquaProps(S);
    if (gloveH) { gloveH.close(); gloveH = null; }
    d.vapor = ctx.gauge ? ctx.gauge.value : 30;
    d.humT = 6; d.entryCd = 3; d.lastAtkPress = G.input.lastPress('attack');
    S.state('fog', d.vapor / 100);
    const jt = member('jotaro4');
    if (jt) { jt.dmgOut = 0.8; jt.energy = 0; }
    // 重击打中就打散（J3 / 连打终结 / 必杀；承太郎 AI 的拳也算）
    ctx.on('hit', (e) => {
      const aq = S.actor('aqua');
      if (!aq || e.t !== aq || d.inMouth) return;
      if (['J3', 'fin', 'special'].indexOf(e.slot) >= 0 || (e.att && e.att.cid === 'jotaro4' && e.slot === 'J3')) scatter(S, aq, ctx);
    });
    S.hint('水汽越浓，水中项链越快、越难看清。J3 能打碎加湿器、打墙放汽', 7);
  }
  function aquaTick(S, c, dt) {
    const d = c.data, p = player(), aq = S.actor('aqua');
    if (!p || !aq) return;
    d.vapor = c.gauge ? c.gauge.value : 0;
    S.state('fog', d.vapor / 100);
    const jt = member('jotaro4');
    // 承太郎当 AI 时别让他自己放时停（能量卡在 99）
    if (jt && jt !== p && jt.energy > 99) jt.energy = 99;
    // 项链：被打散 → 0.6 s 后重组；平时透明度跟着水汽走
    if (aq.mem.scatter > 0) { aq.mem.scatter -= dt; if (aq.mem.scatter <= 0) reform(S, aq, c); }
    else if (!d.inMouth) aq.alpha = Math.max(0.15, 1 - d.vapor / 120);
    // 加湿器每 20 s 自己开一次
    if (!d.humBroken) { d.humT = (d.humT || 0) + dt; if (d.humT >= 20) { d.humT = 0; humPulse(S, c); } }
    // J3 / 终结打加湿器、打墙（一招只算一次）
    const a = p.atk, slot = a && a.slot;
    if (a && (slot === 'J3' || slot === 'fin') && a !== d.brkAtk && p.atkT >= a.active[0] && p.atkT <= a.active[1] + f(2)) {
      d.brkAtk = a;
      if (!d.humBroken && Math.abs(p.x - LR.hum[0]) <= 46 && Math.abs(p.y - LR.hum[1]) <= 14 && p.facing < 0) breakHum(S, c);
      else if (!d.wallOpen && Math.abs(p.x - LR.wall[0]) <= 30 && p.y <= 152) openWall(S, c);
    }
    // 按住 L 按 J：修墙 / 修加湿器（只有仗助会修）
    const lp = G.input.lastPress('attack');
    if (lp !== d.lastAtkPress) {
      d.lastAtkPress = lp;
      if (p.cid === 'josuke' && p.state === 'guard') {
        if (d.wallOpen && Math.abs(p.x - LR.wall[0]) <= 36 && p.y <= 156) fixThing(S, c, 'wall');
        else if (d.humBroken && Math.abs(p.x - LR.hum[0]) <= 46 && Math.abs(p.y - LR.hum[1]) <= 16) fixThing(S, c, 'hum');
      }
    }
    // 乳胶手套：走到水槽边按 E
    if (!d.glove && !d.gloveReq) {
      const near = Math.abs(p.x - LR.glove[0]) <= 24 && Math.abs(p.y - LR.glove[1]) <= 14;
      if (near && !d.gloveHint) { d.gloveHint = true; S.hint('水槽边有一盒乳胶手套：按 E 拿一只', 4); }
      if (!near) d.gloveHint = false;
      if (near && G.input.hit('ok')) { G.input.consume('ok'); d.gloveReq = true; }
    }
    // 承太郎（AI）喊位置：项链开始扑的时候
    if (jt && jt !== p && aq.tele && aq.tele !== d.calledTele) {
      d.calledTele = aq.tele;
      const fromHole = d.wallOpen && d.hole && Math.abs(aq.x - d.hole[0]) < 12;
      S.emote(jt, fromHole ? '上面！' : aq.x < p.x ? '左边！' : '右边！', 0.9, '#bfe8ff');
    }
    // 钻嘴：张嘴时它会凑过来；在 48 px 内亮红圈 0.35 s，圈亮完还张着嘴 → 钻进去
    d.entryCd = Math.max(0, (d.entryCd || 0) - dt);
    const open = mouthOpen(p) && p.cid === 'josuke';
    const dist = Math.hypot(aq.x - p.x, (aq.y - p.y) * 1.6);
    const ready = !d.inMouth && d.entryCd <= 0 && !(aq.mem.scatter > 0) && !aq.hidden && !aq.atk && !aq.tele;
    aq.mem.bait = open && ready && dist < 110;
    if (aq.mem.bait && dist >= 30) G.combat.walkTo(aq, p.x + p.facing * 20, p.y, dt, 110);
    if (open && ready && dist < 48) {
      d.ring = (d.ring || 0) + dt;
      if (!d.ringFx) { d.ringFx = true; S.sfx('sting_shock', 0.4); }
      if (d.ring >= 0.35) { d.ring = 0; d.ringFx = false; cine(c, () => mouthEntry(S, c, aq)); }
    } else { d.ring = 0; d.ringFx = false; }
    // 没拿手套、它已经弱了还卡 60 s：承太郎提示「……厨房。」
    if (!d.glove && aq.hp <= aq.maxHp * LOW) {
      d.lowT = (d.lowT || 0) + dt;
      if (d.lowT > 60 && !d.helpKitchen) {
        d.helpKitchen = true;
        cine(c, async () => {
          await S.say('jotaro4', '……厨房。');
          S.hint('厨房水槽边有一盒乳胶手套：拿一只含在嘴里，再引它钻嘴', 8);
        });
      }
    }
    if (aq.hp <= aq.maxHp * LOW && !d.lowHint) {
      d.lowHint = true;
      S.hint(d.glove ? '它弱了！含着手套，在它旁边连打（张嘴）引它钻进来！' : '它弱了……可光打散它、吐出来，是抓不住水的', 7);
    }
  }
  R.fightAqua = async function (S) {
    S.hint(null);
    const res = await S.fight({
      id: 'b_pro2_aqua', arena: LR.arena, lead: 'josuke', swap: true, allies: ['jotaro4'],
      music: 'battle', after: null, dmgScale: 0.8, losable: true, energy: { start: 0 },
      gauge: { max: 100, value: 30, label: '水汽', color: '#c8e8ff', rate: (c) => (c.data.wallOpen ? 0.5 : 2) },
      waves: [[{ kit: 'e_aqua', actor: 'aqua', cid: 'aqua', id: 'aqua', name: '水中项链', x: 300, y: 154, boss: true, hp: 400, minHp: 1 }]],
      testHint: (ctx) => {
        const aq = G.S.actor('aqua'), d = ctx.data;
        return { vapor: Math.round(d.vapor || 0), glove: !!d.glove, wallOpen: !!d.wallOpen, humBroken: !!d.humBroken, inMouth: !!d.inMouth,
          entries: d.entries || 0, trapped: !!d.trapped, helpKitchen: !!d.helpKitchen, aquaHp: aq ? aq.hp : null, aquaMax: aq ? aq.maxHp : null };
      },
      onWave: async (S2, wi, spawned, attempt, ctx) => { aquaSetup(S2, ctx); },
      events: [{
        when: (t, ctx) => !!ctx.data.gloveReq && !ctx.data.glove,
        run: async (S2, es, attempt, ctx) => {
          const p = player();
          ctx.data.glove = true;
          T().setFrame(S2.actor('lr_box'), 1);
          S2.sfx('pop', 0.8);
          if (gloveH) gloveH.close();
          gloveH = P4().gloveIcon();
          await S2.say(p.cid === 'josuke' ? 'josuke' : 'jotaro4', p.cid === 'josuke' ? '……这个能用。' : '……拿着，仗助。');
          S2.mark('pro_glove');
          S2.hint('拿到乳胶手套（含在嘴里）。等它弱了，故意在它旁边连打，引它钻嘴！', 7);
        },
      }],
      tick: (c, dt) => aquaTick(S, c, dt),
      endWhen: (c) => !!c.data.trapped,
    });
    S.state('fog', 0.2);
    return res;
  };
  R.closeGlove = () => { if (gloveH) { gloveH.close(); gloveH = null; } };
  R.showGlove = () => { if (!gloveH) gloveH = P4().gloveIcon(); };

  // =====================================================================================================================
  // 序2 段 2 雨中追本体（b_pro2_chase）：60 s 追上安杰罗，第二次失败起放宽到 80 s
  // =====================================================================================================================
  const CH = { arena: [12, 1100], start: [70, 160], angelo: [250, 160], endX: 1040 };
  // 路边的东西：安杰罗跑过时踢翻（垃圾桶滚向仗助，自行车横倒挡路）
  const OBS = [
    { kind: 'trash', x: 380, y: 152 }, { kind: 'bike', x: 470, y: 166 }, { kind: 'trash', x: 590, y: 168 },
    { kind: 'bike', x: 700, y: 150 }, { kind: 'trash', x: 830, y: 158 }, { kind: 'bike', x: 940, y: 164 },
  ];
  let trailH = null;
  function chaseSetup(S, ctx) {
    const d = ctx.data;
    d.limit = ctx.attempt >= 2 || ctx.assist ? 80 : 60;
    if (G.hud.timer) { G.hud.timer.until = d.limit; G.hud.timer.left = d.limit; }
    d.endX = CH.endX; d.angeloSpeed = 58; d.catches = 0;
    for (const a of G.world.stage.actors) if (a.id && a.id.indexOf('ob_') === 0) a.remove = true;
    d.obs = OBS.map((o, i) => {
      const a = T().prop(S, o.kind, o.x, o.y, { id: 'ob_' + i, frame: 0 });
      return { a, kind: o.kind, x: o.x, y: o.y, w: o.kind === 'bike' ? 26 : 16, down: false, done: false, vx: 0 };
    });
    if (trailH) trailH.close();
    trailH = P4().waterTrail(() => S.actor('angelo'));
    R.showGlove();
    S.hint('追上安杰罗！挡路的东西：K 闪过，或者 J 打开', 6);
  }
  function chaseTick(S, c, dt) {
    const d = c.data, p = player(), an = S.actor('angelo');
    if (!p || !an) return;
    if (G.hud.timer && G.hud.timer.until !== d.limit) G.hud.timer.until = d.limit;
    if (c.t >= d.limit) { c.fail('安杰罗逃进了雨里……'); return; }
    for (const o of d.obs) {
      if (o.done) continue;
      // 安杰罗跑过：踢翻
      if (!o.down && an.x >= o.x - 6) {
        o.down = true;
        T().setFrame(o.a, 1);
        S.sfx(o.kind === 'bike' ? 'metal_crunch' : 'thud', 0.7);
        S.sfxText(o.kind === 'bike' ? '哐！' : '咣！', { wx: o.x, wy: o.y, wz: 20 }, { dur: 0.6 });
        if (o.kind === 'trash') { o.vx = -70; o.y = G.clamp(p.y, 148, 172); o.a.y = o.y; }
        if (Math.random() < 0.5) S.emote(an, '别过来！', 0.8);
      }
      if (!o.down) continue;
      if (o.vx) { o.x += o.vx * dt; o.a.x = o.x; o.a.rot = (o.a.rot || 0) - dt * 6; if (o.x < CH.arena[0] + 10) { o.done = true; o.a.remove = true; continue; } }
      // J 打开
      const at = p.atk;
      if (at && at.slot !== 'enemy' && p.atkT >= at.active[0] && p.atkT <= at.active[1] + f(2)) {
        const dx = (o.x - p.x) * p.facing;
        if (dx >= -4 && dx <= 46 && Math.abs(o.y - p.y) <= 12) {
          o.done = true;
          S.sfx('crash', 0.7);
          S.fx('burst', { x: o.x, y: o.y - 8, n: 8, speed: 30, colours: ['#6a8ab0', '#c0c8d0'], gravity: 120, life: 0.6 });
          S.arc(o.a, o.x + p.facing * 40, G.clamp(o.y + 10, 148, 176), 18, 0.4, { spin: p.facing * 6 }).then(() => { o.a.remove = true; }, G.cancelIgnore);
          continue;
        }
      }
      // 撞上：绊一跤（K 的无敌帧能穿过去）
      if (p.iframe <= 0 && p.invuln <= 0 && Math.abs(o.x - p.x) < o.w / 2 + 5 && Math.abs(o.y - p.y) < 7) {
        o.done = true; o.vx = 0;
        G.combat.hit(null, p, { slot: 'enemy', dmg: 4, push: 18, guard: 'normal', sfxHit: 'thud', fxHit: 'light' });
        S.sfxText('咚', p, { dur: 0.5 });
      }
    }
    // 追上：连按 J 抓住
    if (!d.grab && Math.abs(an.x - p.x) < 22 && Math.abs(an.y - p.y) < 10) {
      d.grab = true;
      cine(c, async () => {
        an.mem.hold = true; an.atk = null; an.state = 'idle'; an.play('hurt');
        S.face(p, an); S.face(an, p);
        S.sfx('whoosh', 0.7);
        const ok = await S.mash({ need: 8, time: 1.5, label: '连按 J！抓住他！' });
        d.catches++;
        if (ok) { d.caught = true; S.mark('pro_angelo_caught'); return; }
        // 没抓牢：被他推开，他加速跑一段
        S.sfx('punch', 0.7);
        p.x -= p.facing * 20; p.state = 'hurt'; p.play('hurt'); p.flash = 1;
        S.emote(an, '放手！', 0.9);
        an.mem.hold = false; an.mem.boost = 2;
        await S.wait(0.3);
        p.state = 'idle'; p.play('idle');
        d.grab = false;
      });
    }
  }
  R.chaseAngelo = async function (S) {
    S.hint(null);
    const res = await S.fight({
      id: 'b_pro2_chase', arena: CH.arena, lead: 'josuke', swap: false, lockMsg: '仗助追上去！',
      music: 'battle', after: null, dmgScale: 0.8, losable: true, energy: { start: 0 }, bench: { mode: 'hide' },
      timer: { label: '追上本体：', until: 60 },
      steps: { n: 1, label: '追上安杰罗' },
      waves: [[{ kit: 'e_angelo_run', actor: 'angelo', cid: 'angelo', id: 'angelo', name: '安杰罗', x: CH.angelo[0], y: CH.angelo[1],
        boss: true, hp: 999, minHp: 1, untargetable: true }]],
      testHint: (ctx) => {
        const an = G.S.actor('angelo'), p = player(), d = ctx.data;
        return { limit: d.limit, angeloX: an ? Math.round(an.x) : null, gap: an && p ? Math.round(an.x - p.x) : null, caught: !!d.caught, catches: d.catches || 0 };
      },
      onWave: async (S2, wi, spawned, attempt, ctx) => {
        const p = player();
        p.x = CH.start[0]; p.y = CH.start[1]; p.facing = 1;
        chaseSetup(S2, ctx);
      },
      tick: (c, dt) => chaseTick(S, c, dt),
      endWhen: (c) => !!c.data.caught,
    });
    if (trailH) { trailH.close(); trailH = null; }
    for (const a of G.world.stage.actors) if (a.id && a.id.indexOf('ob_') === 0) a.remove = true;
    return res;
  };
})();
