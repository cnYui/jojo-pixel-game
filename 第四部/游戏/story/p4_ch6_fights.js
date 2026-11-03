// 第6章　幽灵小路 / 丰收与纽扣：探索、小游戏和战斗（G.P4CH6）。剧情节拍在 story/p4_ch6.js；规矩见 第四部/docs/分章开发约定.md
//   exAlley      探索「不能回头」（露伴 ⇄ 康一，自由走动：转身 = 被影子手拖回去）
//   coins        小游戏「捡硬币」mg_coins（俯视 3×3 街区，派 5 队丰收）
//   harvestWall  第 9 战段 1 b09a_wall（外墙四层：抛上去、拉上来）
//   harvestRoof  第 9 战段 2 b09b_roof（水管：断一段修一段 → 醉酒 → 道歉 → 削 → 撕）
//   killerQueen  第 10 战 b10_kq（重清爬回学校，目标段不会输）+ b10c_button（最后一只丰收带着纽扣跑）
//   clueCard     线索小卡（第 12 节拍：纽扣）
//   克制：硬币炸弹只有白光；重清只给白光、剪影和一只只消失的丰收。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const f = (n) => n / 60;
  const K = G.KITS;
  const R = (G.P4CH6 = {});
  const F = () => G.flags;
  const W = () => G.world;
  const player = () => G.world.player;
  const clk = () => (G.clk ? G.clk : { ui: 0, world: 0 });
  const text = (g, s, x, y, col, size, align, outline) => P4().text(g, s, x, y, col, size, align, outline);
  const OKU = () => (G.P4CH6CID ? G.P4CH6CID.OKU() : 'okuyasu');
  const ROHAN = 'rohan';

  // 本章新上场的两个“队长”：重清（第 10 战只能爬）和一只丰收（纽扣段）。没有招式：J / U 由战斗自己接管
  K.shigechi = K.shigechi || { hp: 80, speed: 20, combo: [], guard: null, chords: {}, dodge: {}, special: null, explore: null, grunt: null };
  K.harvest = K.harvest || { hp: 10, speed: 52, combo: [], guard: null, chords: {}, dodge: {}, special: null, explore: null, grunt: null };

  // 在战斗里插一段演出（同序章 p4_pro_fights.js 的 cine）
  async function cine(ctx, fn) {
    const w = G.world, run = G.runId;
    if (w.fight !== ctx) return;
    const old = w.cine;
    w.cine = { by: 'p4-fight' };
    try { await fn(); } catch (e) { if (!G.cancelled(e)) console.error(e); } finally { if (run === G.runId && w.fight === ctx) w.cine = old || null; }
  }
  const members = () => (G.party && G.party.members) || [];
  const partnerOf = (p) => members().find((a) => a !== p && a.visible !== false) || null;
  // 这一帧拳头在不在判定里（普通三连、连打都算）
  const swinging = (p) => !!p && (!!p.rush || p.state === 'rush' || (!!p.atk && p.atkT >= p.atk.active[0] && p.atkT <= p.atk.active[1] + f(2)));
  const u = (x, y, z) => (G.cam && G.cam.w2u ? G.cam.w2u(x, y, z || 0) : { x: x * 2, y: (y - (z || 0)) * 2 });

  // =====================================================================================================================
  // 探索「不能回头」（ex_alley）：从铃美身边（330）走到出口（600）。按 ← 转身 = 回头：影子手把人拖回 330，暗度退一档
  // =====================================================================================================================
  const AX = { start: 330, exit: 600 };
  const TEMPT = [
    { x: 380, sfx: 'footstep1', who: '背后的声音', line: '「露伴老师——！等等我！」……是康一的声音。' },
    { x: 430, sfx: 'coin', who: null, line: '背后“叮”的一声，像是硬币掉在了地上。……是自己的钱包吗？' },
    { x: 480, sfx: 'drip', who: '背后的声音', line: '「康一君……好疼……救救我……」有个女孩子在哭。' },
    { x: 530, sfx: 'dog_bark', who: null, line: '背后，阿诺德一声接一声地叫。叫得很急。' },
    { x: 570, sfx: 'card_flip', who: '背后的声音', line: '「露伴，你的原稿掉了。」……是自己的声音。' },
  ];
  R.exAlley = async function (S) {
    const w = W(), d = { tempt: 0, dark: 0, idle: 0, lastX: 0, busy: false, done: false, lastFacing: 1, lastCid: null, drags: 0 };
    const p0 = S.player;
    Object.assign(p0, { x: AX.start, y: 154, facing: 1 });
    for (const m of members()) if (m !== p0) Object.assign(m, { x: AX.start - 22, y: 162, facing: 1 });
    S.state('dark', 0); S.state('hands', 0);
    S.mark('ex_alley_start');
    S.hint('往右走到出口（→）。千万别回头：别按 ←', 7);
    const other = (p) => (p.cid === ROHAN ? 'koichi' : ROHAN);
    async function dragBack(S2) {
      const p = S2.player;
      d.drags++;
      S2.state('hands', 1);
      S2.sfx('heartbeat', 0.8); S2.sfx('whoosh', 0.7);
      S2.shake(2, 0.5);
      S2.sfxText('！', p, { dur: 0.6 });
      p.play('hurt');
      const x0 = p.x, ms = members().filter((m) => m !== p).map((m) => [m, m.x]);
      await S2.animate(0.9, (k) => {
        p.x = G.lerp(x0, AX.start, k * k);
        for (const [m, mx] of ms) m.x = G.lerp(mx, AX.start - 22, k * k);
      });
      p.play('idle'); p.facing = 1;
      d.dark = Math.max(0, d.dark - 0.25);
      S2.state('dark', d.dark);
      await S2.wait(0.3);
      S2.state('hands', 0);
      if (!F().ch6Dragged) {
        F().ch6Dragged = true;
        S2.mark('ch6_dragged');
        await S2.say(other(p), other(p) === 'koichi' ? '露伴老师！刚才……有好多只手！' : '……康一君，看来那姑娘没骗人。', { expr: 'shock' });
        S2.hint('一回头就会被拖回去。忍住，一直往右走', 5);
      }
      d.lastFacing = 1;
    }
    async function tempt(S2, q) {
      const p = S2.player;
      S2.sfx(q.sfx, 0.7);
      d.dark = Math.min(1, d.dark + 0.2);
      S2.state('dark', d.dark);
      const pt = partnerOf(p);
      if (pt) S2.emote(pt, '别回头！', 1.4);
      await S2.say(null, q.line, q.who ? { name: q.who } : {});
      if (q.x === 570) await S2.say(ROHAN === p.cid ? ROHAN : 'koichi', ROHAN === p.cid ? '……我的原稿从来不会掉。' : '露、露伴老师的声音？……不对，老师在我旁边。', { expr: 'rage' });
    }
    T().tick((dt) => {
      if (d.done) return true;
      const p = S.player;
      if (!p || !w.free || S.busy || d.busy) { if (p) { d.lastFacing = p.facing; d.lastCid = p.cid; } return false; }
      if (p.cid !== d.lastCid) { d.lastCid = p.cid; d.lastFacing = p.facing; }
      if (p.x >= AX.exit) { d.done = true; return true; }
      const run = (fn) => { d.busy = true; S.run(fn).then(() => { d.busy = false; }, (e) => { d.busy = false; G.cancelIgnore(e); }); };
      // 回头：这一帧刚从朝右转成朝左
      if (p.facing === -1 && d.lastFacing === 1 && p.x > AX.start + 4) { d.lastFacing = -1; run(dragBack); return false; }
      d.lastFacing = p.facing;
      if (d.tempt < TEMPT.length && p.x >= TEMPT[d.tempt].x) { const q = TEMPT[d.tempt++]; run((S2) => tempt(S2, q)); return false; }
      // 原地站 8 s：背后再喊一次（不加暗）
      if (Math.abs(p.x - d.lastX) < 0.5) d.idle += dt; else d.idle = 0;
      d.lastX = p.x;
      if (d.idle > 8) {
        d.idle = 0;
        run(async (S2) => { S2.sfx('heartbeat', 0.5); await S2.say(null, '「……回头看看嘛。就一眼。」', { name: '背后的声音' }); });
      }
      return false;
    });
    await S.run(async () => {});
    await S.until(() => d.done && !S.busy && !d.busy);
    if (!F().ch6Dragged) { F().ch6Dragged = true; S.mark('ch6_dragged'); }
    F().ch6AlleyOut = true;
    S.hint(null);
    S.mark('ch6_alley_out');
    await S.run(async () => {}, { keepLocked: true });
  };

  // =====================================================================================================================
  // 小游戏「捡硬币」（mg_coins）：方向键选街区，J 派一队丰收（5 队），一队来回 4–6 s。90 s 捡 10000 日元（放水：75 s 里 7000）
  // =====================================================================================================================
  //   底数：商店街、车站前、便利店多；住宅区、公园、银行中等；派出所 / 河边 / 工地底数高但 40% 回不来（12 s 后才补位）
  const BASE = [450, 650, 380, 600, 900, 820, 1000, 560, 420];
  const LOST = ['被巡警追了！', '被狗追了！', '掉进下水道口了！'];
  function blocksMeta() {
    const m = (G.D && G.D.bg && G.D.bg.morioh_blocks) || {};
    const an = m.anchors || {};
    let bl = m.blocks || (m.meta && m.meta.blocks) || null;
    if (!bl) {
      const names = ['住宅区', '商店街', '公园', '车站前', '派出所', '河边', '工地', '便利店', '银行'];
      const cs = [[61, 51], [160, 51], [259, 51], [61, 105], [160, 105], [259, 105], [61, 154], [160, 154], [259, 154]];
      bl = cs.map((c, i) => [c[0] - 46, c[1] - 24, c[0] + 46, c[1] + 24, names[i], i === 4 || i === 5 || i === 6]);
    }
    return bl.map((b, i) => {
      const c = an['b' + i] || [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2];
      return { i, x0: b[0], y0: b[1], x1: b[2], y1: b[3], name: b[4], danger: !!b[5], cx: c[0], cy: c[1], base: BASE[i], visits: 0 };
    });
  }
  const HOME = [160, 178];
  function coinsInit(S, c) {
    const d = c.data;
    d.init = true;
    d.limit = c.assist ? 75 : 90; d.need = c.assist ? 7000 : 10000;
    d.blocks = blocksMeta();
    d.cur = 1; d.money = 0; d.found = false; d.forceLot = false;
    const safe = [0, 1, 2, 3, 7, 8];
    d.lot = safe[Math.floor(Math.random() * safe.length)];
    d.squads = [0, 1, 2, 3, 4].map((i) => ({ i, st: 'home', t: 0, dur: 0, b: null, lose: false }));
    d.pops = [];
    const p = player();
    p.hold = true; p.visible = false;
    G.hud.on = false;
    if (d.h) d.h.close();
    d.h = P4().overlay((g, t) => coinsDraw(g, t, c), { z: 2 });
    S.hint('方向键选街区，按 J 派一队丰收去捡。红框的街区底数高，可是容易回不来', 8);
  }
  function squadPos(q) {
    if (q.st !== 'out') return null;
    const b = q.b, k = q.t / q.dur, s = k < 0.5 ? k * 2 : (1 - k) * 2;
    return [G.lerp(HOME[0], b.cx, s), G.lerp(HOME[1], b.cy, s)];
  }
  function coinsTick(S, c, dt) {
    const d = c.data, I = G.input;
    if (!d.init) coinsInit(S, c);
    const p = player();
    p.hold = true;
    if (c.t >= d.limit) { c.fail('时间到了……只捡到 ¥' + d.money + '。'); return; }
    // 选街区
    const col = d.cur % 3, row = Math.floor(d.cur / 3);
    if (I.hit('left') && col > 0) { d.cur--; S.sfx('blip', 0.4); }
    if (I.hit('right') && col < 2) { d.cur++; S.sfx('blip', 0.4); }
    if (I.hit('up') && row > 0) { d.cur -= 3; S.sfx('blip', 0.4); }
    if (I.hit('down') && row < 2) { d.cur += 3; S.sfx('blip', 0.4); }
    if (I.hit('attack')) {
      I.consume('attack');
      const q = d.squads.find((s) => s.st === 'home');
      if (q) {
        const b = d.blocks[d.cur];
        Object.assign(q, { st: 'out', b, t: 0, dur: 4 + Math.random() * 2, lose: b.danger && Math.random() < 0.4 });
        S.sfx('doll_scurry', 0.5);
      } else S.sfx('guard', 0.3);
    }
    for (const q of d.squads) {
      if (q.st === 'lost') { q.t += dt; if (q.t >= 12) { q.st = 'home'; S.sfx('pop', 0.4); } continue; }
      if (q.st !== 'out') continue;
      q.t += dt;
      const b = q.b;
      if (q.lose && q.t >= q.dur * 0.5) {
        q.st = 'lost'; q.t = 0;
        d.pops.push({ x: b.cx, y: b.cy, s: LOST[[4, 5, 6].indexOf(b.i)] || '回不来了！', col: '#ff8a8a', t0: clk().ui });
        S.sfx('sting_comedy', 0.4);
        continue;
      }
      if (q.t >= q.dur) {
        q.st = 'home';
        const gain = Math.max(10, Math.round(b.base * Math.pow(0.8, b.visits) / 10) * 10);
        b.visits++;
        d.money += gain;
        d.pops.push({ x: HOME[0], y: HOME[1] - 18, s: '+¥' + gain, col: '#ffe070', t0: clk().ui });
        S.sfx('coin', 0.5);
        if (!d.found && (b.i === d.lot || d.forceLot)) {
          d.found = true;
          d.pops.push({ x: HOME[0], y: HOME[1] - 34, s: '……还有一张彩票？', col: '#ffffff', t0: clk().ui });
          S.sfx('ding', 0.6);
        }
      }
    }
    if (d.money >= d.need && !d.found) d.forceLot = true;
  }
  function coinsDraw(g, t, c) {
    const w = W(), d = c.data;
    if (w.fight !== c || !d.blocks) return;
    const blink = Math.floor(clk().ui * 4) % 2 === 0;
    for (const b of d.blocks) {
      const a = u(b.x0, b.y0), z = u(b.x1, b.y1);
      const sel = b.i === d.cur;
      g.save();
      if (sel) {
        g.strokeStyle = blink ? '#fff4a0' : '#ffd83c'; g.lineWidth = 4;
        g.strokeRect(Math.round(a.x) + 2, Math.round(a.y) + 2, Math.round(z.x - a.x) - 4, Math.round(z.y - a.y) - 4);
      }
      const est = Math.max(10, Math.round(b.base * Math.pow(0.8, b.visits) / 10) * 10);
      text(g, '约 ¥' + est, Math.round((a.x + z.x) / 2), Math.round(z.y) - 22, b.danger ? '#ffb0b0' : '#fff4d6', 12, 'center', '#1a1008');
      g.restore();
    }
    // 在外面的队：一串小黄点
    for (const q of d.squads) {
      const pp = squadPos(q);
      if (!pp) continue;
      const s = u(pp[0], pp[1]);
      g.fillStyle = '#2a1e06';
      for (let k = 0; k < 4; k++) g.fillRect(Math.round(s.x) - 7 + k * 4, Math.round(s.y) - 3 + (k % 2) * 3, 5, 5);
      g.fillStyle = '#ffd83c';
      for (let k = 0; k < 4; k++) g.fillRect(Math.round(s.x) - 6 + k * 4, Math.round(s.y) - 2 + (k % 2) * 3, 3, 3);
    }
    // 右上角：时间、金额、彩票、待命
    const left = Math.max(0, Math.ceil(d.limit - c.t));
    g.fillStyle = 'rgba(16,10,4,0.72)'; g.fillRect(452, 8, 180, 76);
    text(g, '剩余 ' + left + ' 秒', 620, 14, left <= 10 ? '#ff8a8a' : '#ffffff', 12, 'right', '#000000');
    text(g, '¥' + d.money + ' / ' + d.need, 620, 32, d.money >= d.need ? '#a0ff9a' : '#ffe070', 16, 'right', '#000000');
    const home = d.squads.filter((q) => q.st === 'home').length;
    text(g, '待命 ' + home + ' / 5 队', 620, 54, '#fff4d6', 12, 'right', '#000000');
    text(g, d.found ? '彩票 ✓' : '彩票 ？', 466, 54, d.found ? '#ffffff' : '#a89a80', 12, 'left', '#000000');
    // 浮字
    d.pops = d.pops.filter((q) => clk().ui - q.t0 < 1.4);
    for (const q of d.pops) {
      const k = (clk().ui - q.t0) / 1.4, s = u(q.x, q.y);
      g.save(); g.globalAlpha = 1 - k;
      text(g, q.s, Math.round(s.x), Math.round(s.y - 20 - k * 24), q.col, 16, 'center', '#000000');
      g.restore();
    }
    text(g, '方向键 选街区　J 派丰收', 320, 334, '#fff4d6', 12, 'center', '#000000');
  }
  R.coins = async function (S) {
    S.party(['josuke', OKU()], { leader: 'josuke' });
    await S.setStage('town_ch6', { x: 160, y: 165, music: 'daily', fade: false });
    for (const m of members()) m.visible = false;
    await S.fadeIn(0.5);
    S.mark('mg_coins_start');
    await S.say('josuke', '重清，丰收能分成几队吧？我们看地图出主意，你来派。', { expr: 'smile' });
    await S.say('shigechi', '五队！一队一百只！');
    await S.say(OKU(), '派出所、河边、工地那几块听说有巡警、有狗、有下水道口。小心点。');
    let hc = null;
    await S.fight({
      id: 'mg_coins', arena: [0, 320], lead: 'josuke', swap: false, music: 'battle', after: null, playerMinHp: 1, losable: false,
      bench: { mode: 'hide' }, energy: { start: 0 }, coverage: false,
      testHint: (ctx) => ({ money: ctx.data.money || 0, need: ctx.data.need, found: !!ctx.data.found, cur: ctx.data.cur, lot: ctx.data.lot }),
      tick: (c, dt) => { coinsTick(S, c, dt); hc = c.data.h; },
      endWhen: (c) => !!c.data.init && c.data.money >= c.data.need && c.data.found,
      onRetry: async () => { if (hc) hc.close(); },
    });
    if (hc) hc.close();
    S.hint(null);
    await S.say('shigechi', '一万多日元！……还有这个，一张彩票。', { expr: 'smile' });
    await S.say('josuke', '彩票？兑奖的号码，晚报上就有。', { expr: 'smile' });
    await S.fadeOut(0.5);
    for (const m of members()) m.visible = true;
  };

  // =====================================================================================================================
  // 丰收（两段共用）：一小群一小群扑过来叮人，每只 1 血，挥拳就散，叮一下 2 伤
  // =====================================================================================================================
  const ZL = [0, 38, 76, 116];
  function setLvl(a, L) { a.lvl = L; a.fly = { z: ZL[L], bob: 0 }; a.z = ZL[L]; a.shadow = L === 0; }
  function clearLvl(a) { a.lvl = null; a.fly = null; a.z = 0; a.shadow = true; }
  function bugSpawn(S, d, x, L, dir) {
    d.bugN = (d.bugN || 0) + 1;
    const a = S.spawn('harvest', x, 150, { id: 'hb' + d.bugN, facing: dir, shadow: false });
    a.hold = true;
    setLvl(a, L);
    a.shadow = false;
    a.play('walk');
    const b = { a, L, cd: 0.6, sp: 22 + Math.random() * 10 };
    d.bugs.push(b);
    return b;
  }
  function bugsTick(S, c, dt, o) {
    const d = c.data, p = player();
    d.bugs = d.bugs.filter((b) => !b.a.remove);
    d.bugT = (d.bugT || 0) + dt;
    const pl = p.lvl || 0;
    if (d.bugT >= (o.every || 2.2) && d.bugs.length < (o.max || 6) && (!o.can || o.can(p))) {
      d.bugT = 0;
      const side = Math.random() < 0.5 ? -1 : 1, n = Math.random() < 0.5 ? 2 : 1;
      for (let k = 0; k < n && d.bugs.length < (o.max || 6); k++) {
        const x = side < 0 ? o.x0 + 4 + k * 8 : o.x1 - 4 - k * 8;
        bugSpawn(S, d, x, pl, -side);
      }
      S.sfx('doll_scurry', 0.35);
    }
    const hit = swinging(p);
    for (const b of d.bugs) {
      const a = b.a;
      b.cd = Math.max(0, b.cd - dt);
      if (b.L !== pl) { a.x += a.facing * b.sp * 0.5 * dt; if (a.x < o.x0 || a.x > o.x1) a.facing = -a.facing; continue; }
      const dx = p.x - a.x;
      a.facing = dx > 0 ? 1 : -1;
      // 挥拳就散
      const fx = (a.x - p.x) * p.facing;
      if (hit && fx >= -6 && fx <= 40) {
        a.remove = true;
        S.fx('burst', { x: a.x, y: a.y - 8 - ZL[b.L], n: 5, speed: 26, colours: ['#ffd83c', '#6c4aa0'], gravity: 80, life: 0.4 });
        S.sfx('pop', 0.4);
        d.kills = (d.kills || 0) + 1;
        continue;
      }
      if (Math.abs(dx) > 9) a.x += Math.sign(dx) * b.sp * dt;
      else if (b.cd <= 0 && p.state !== 'hurt' && p.iframe <= 0) {
        b.cd = 1.1;
        G.combat.hit(null, p, { slot: 'enemy', dmg: 2, push: 6, guard: 'normal', sfxHit: 'punch', fxHit: 'light' });
        S.sfxText('叮', p, { dur: 0.4 });
        a.x -= Math.sign(dx) * 10;
      }
    }
  }
  function bugsClear(d) { for (const b of d.bugs || []) b.a.remove = true; d.bugs = []; }

  // =====================================================================================================================
  // 第 9 战段 1 外墙（b09a_wall）：四层。同一层 28 px 内按 J 把队友抛上一层；队长在上层、队友在正下面一层，按住 L 按 J 拉上来
  // =====================================================================================================================
  const WL = { arena: [16, 292], josuke: 120, oku: 152, sg: 250 };
  function wallInit(S, c) {
    const d = c.data;
    d.init = true; d.bugs = []; d.bugT = 0;
    for (const a of W().stage.actors) if (a.id && /^hb\d/.test(a.id)) a.remove = true;
    const jo = members().find((a) => a.cid === 'josuke'), ok = members().find((a) => a.cid === OKU());
    if (jo) { jo.x = WL.josuke; jo.y = 150; jo.facing = 1; setLvl(jo, 0); }
    if (ok) { ok.x = WL.oku; ok.y = 150; ok.facing = -1; setLvl(ok, 0); ok.visible = true; }
    const sg = S.actor('shigechi_wall');
    if (sg) { sg.x = WL.sg; setLvl(sg, 3); sg.facing = -1; }
    d.lastJ = G.input.lastPress('attack');
    S.hint('靠近亿泰按 J：把他抛上一层。抛上去以后 Q 换成上面的人', 8);
  }
  async function lift(S, c, who, from, to, how) {
    const z0 = ZL[from], z1 = ZL[to];
    S.sfx('whoosh', 0.8);
    who.play('hurt');
    await S.animate(0.45, (k) => { who.fly.z = Math.round(z0 + (z1 - z0) * k + Math.sin(k * Math.PI) * (how === 'throw' ? 18 : 6)); });
    setLvl(who, to);
    who.play('idle');
    S.sfx('thud', 0.5);
    S.shake(1, 0.15);
  }
  function wallTick(S, c, dt) {
    const d = c.data, p = player();
    if (!d.init) wallInit(S, c);
    if (p.lvl == null) setLvl(p, 0);
    const pt = partnerOf(p);
    if (pt && pt.lvl == null) setLvl(pt, 0);
    bugsTick(S, c, dt, { x0: WL.arena[0], x1: WL.arena[1], every: 2.4, max: 6 });
    const lp = G.input.lastPress('attack');
    const pressed = lp !== d.lastJ;
    d.lastJ = lp;
    if (!pt || !pressed) return;
    const dx = Math.abs(pt.x - p.x);
    if (p.state === 'guard' && pt.lvl === p.lvl - 1 && dx <= 28) {
      cine(c, async () => {
        S.emote(p, '抓紧！', 0.9);
        await lift(S, c, pt, pt.lvl, p.lvl, 'pull');
        if (!d.pullTold) { d.pullTold = true; S.hint('拉上来了。再把对方往上抛', 5); }
      });
      return;
    }
    if (p.state !== 'guard' && pt.lvl === p.lvl && pt.lvl < 3 && dx <= 28) {
      cine(c, async () => {
        S.emote(p, '上去！', 0.9);
        p.atk = null; p.state = 'idle'; p.play('idle');
        await lift(S, c, pt, pt.lvl, pt.lvl + 1, 'throw');
        S.hint('Q 换成上面的人；站到下面那人头顶，按住 L 再按 J 拉他上来', 6);
      });
    }
  }
  R.harvestWall = async function (S) {
    S.party(['josuke', OKU()], { leader: 'josuke' });
    await S.setStage('wall_ch6', { x: WL.josuke, y: 150, facing: 1, music: 'battle', fade: false });
    const sg = S.spawn('shigechi', WL.sg, 150, { id: 'shigechi_wall', facing: -1, name: '重清', shadow: false });
    sg.hold = true;
    setLvl(sg, 3); sg.shadow = false;
    const jo = S.player, ok = S.actor(OKU());
    if (ok) Object.assign(ok, { x: WL.oku, y: 150, facing: -1, follow: null });
    await S.fadeIn(0.4);
    S.mark('b09a_start');
    await S.say('shigechi', '嘿嘿！丰收能把我扛上楼顶，你们上得来吗？', { actor: sg, expr: 'smile' });
    await S.say(OKU(), '仗助，把我扔上去！我够得着二楼的檐！', { expr: 'rage' });
    await S.fight({
      id: 'b09a_wall', arena: WL.arena, lead: 'josuke', swap: true, allies: [OKU()], music: 'battle', after: null, dmgScale: 1, energy: { start: 0 },
      steps: { n: 1, label: '两个人都爬上楼顶' },
      testHint: (ctx) => ({ lv: members().map((a) => a.cid + ':' + a.lvl).join(','), bugs: (ctx.data.bugs || []).length, kills: ctx.data.kills || 0 }),
      tick: (c, dt) => wallTick(S, c, dt),
      endWhen: (c) => !!c.data.init && members().every((a) => a.lvl === 3),
      onRetry: async (S2, at, c) => { bugsClear(c.data); },
    });
    for (const a of W().stage.actors) if (a.id && /^hb\d/.test(a.id)) a.remove = true;
    await S.say('shigechi', '真、真上来了？！……可汇票在我这儿！', { actor: sg, expr: 'shock' });
    S.walk(sg, 340, 150, { speed: 70 }).catch(G.cancelIgnore);
    await S.say('josuke', '别跑！', { expr: 'rage' });
    await S.fadeOut(0.4);
    for (const m of members()) clearLvl(m);
    sg.remove = true;
  };

  // =====================================================================================================================
  // 第 9 战段 2 楼顶（b09b_roof）：两栋楼之间只剩水管（446–536，人锁在 y 148），前面一段断了就修（仗助按住 L 按 J）
  // =====================================================================================================================
  const RF = { arena: [330, 632], pipe: [446, 536], pipeY: 148, segs: [[454, 472], [472, 490], [490, 508], [508, 526]], goal: 586, sg: [600, 150] };
  function roofInit(S, c) {
    const d = c.data;
    d.init = true; d.bugs = []; d.bugT = 0; d.cut = [false, false, false, false]; d.fixed = [false, false, false, false];
    for (let i = 1; i <= 4; i++) S.state('brk' + i, 0);
    for (const a of W().stage.actors) if (a.id && /^hb\d/.test(a.id)) a.remove = true;
    const jo = members().find((a) => a.cid === 'josuke'), ok = members().find((a) => a.cid === OKU());
    if (jo) Object.assign(jo, { x: 350, y: 156, facing: 1 });
    if (ok) Object.assign(ok, { x: 372, y: 164, facing: 1, visible: true });
    d.lastJ = G.input.lastPress('attack');
    S.hint('走水管过去（→）。断了的那段：仗助按住 L 再按 J 修好', 7);
  }
  function roofTick(S, c, dt) {
    const d = c.data, p = player();
    if (!d.init) roofInit(S, c);
    if (d.drunk) { roofDrunk(S, c, dt); return; }
    bugsTick(S, c, dt, { x0: 336, x1: 440, every: 3.0, max: 4, can: (pl) => pl.x < 446 });
    // 水管上：人锁在 y 148
    if (p.x > RF.pipe[0] - 16 && p.x < RF.pipe[1] + 4) p.y = p.x > RF.pipe[0] ? RF.pipeY : G.lerp(p.y, RF.pipeY, Math.min(1, dt * 10));
    for (let i = 0; i < 4; i++) {
      const s = RF.segs[i];
      if (!d.cut[i] && p.x > s[0] - 26 && (i === 0 || d.fixed[i - 1])) {
        d.cut[i] = true;
        S.state('brk' + (i + 1), 1);
        S.sfx('metal_crunch', 0.7);
        S.sfxText('咔嚓', { wx: (s[0] + s[1]) / 2, wy: RF.pipeY, wz: 6 }, { dur: 0.6 });
        if (i === 0) S.hint('丰收把前面那段水管咬断了！仗助：按住 L 再按 J 修好', 6);
      }
      if (d.cut[i] && !d.fixed[i] && p.x > s[0] - 3) p.x = s[0] - 3;
    }
    const lp = G.input.lastPress('attack'), pressed = lp !== d.lastJ;
    d.lastJ = lp;
    const i = d.cut.findIndex((v, k) => v && !d.fixed[k]);
    if (i >= 0 && Math.abs(p.x - (RF.segs[i][0] - 3)) <= 22) {
      if (p.cid !== 'josuke') {
        if (d.okuTold !== i) { d.okuTold = i; S.emote(p, '……我修不了，换仗助！', 1.6); S.hint('亿泰只会削，不会修：Q 换成仗助', 5); }
      } else if (pressed && p.state === 'guard') {
        d.fixed[i] = true;
        S.state('brk' + (i + 1), 0);
        S.standAct(p, 'reach', { dx: 16, z: 4, dur: 0.5 });
        P4().fixGlow(S, (RF.segs[i][0] + RF.segs[i][1]) / 2, RF.pipeY - 6);
        if (!F().ch6PipeFixed) { F().ch6PipeFixed = true; S.mark('b09_pipe_fixed'); }
      }
    }
    if (p.x >= RF.goal && !d.drunk) {
      d.drunk = true;
      cine(c, async () => {
        const sg = S.actor('shigechi_roof'), pt = partnerOf(p);
        if (pt) Object.assign(pt, { x: p.x - 22, y: p.y + 6, facing: 1 });
        const hs = [];
        for (let k = 0; k < 8; k++) {
          const h = S.spawn('harvest', p.x + 40 + k * 4, p.y - 6 + (k % 3) * 6, { id: 'hvd' + k, facing: -1, shadow: false });
          h.hold = true; h.play('walk'); hs.push(h);
          S.walk(h, p.x - 10 + (k % 4) * 8, p.y - 4 + (k % 3) * 5, { speed: 90 }).catch(G.cancelIgnore);
        }
        S.sfx('doll_scurry', 0.9);
        await S.say('shigechi', '丰收！把酒精“送”进他们身体里！', { actor: sg, expr: 'rage' });
        S.sfx('drip', 0.7);
        await S.wait(0.4);
        for (const h of hs) h.remove = true;
        S.mark('b09_drunk');
        await S.say('josuke', '……呜、头……好晕……', { expr: 'shock' });
        d.drunkT = 0;
        p.controlReverseUntil = clk().world + 6;
        S.filter('vignette', 0.5, { colour: '#7a3a10', inner: 0.45 });
        S.hint('醉了！方向键反过来了……撑住', 6);
      });
    }
  }
  function roofDrunk(S, c, dt) {
    const d = c.data, p = player();
    if (d.drunkT == null) return;
    d.drunkT += dt;
    d.swayT = (d.swayT || 0) + dt;
    if (d.swayT > 0.5) { d.swayT = 0; S.shake(1, 0.35); }
    if (p.x < RF.goal - 40) p.x = RF.goal - 40;
    if (d.drunkT >= 6 && !d.drunkDone) {
      d.drunkDone = 'pending';
      cine(c, async () => {
        const pt = partnerOf(p);
        for (const a of [p, pt]) if (a) { a.state = 'down'; a.play('down'); }
        S.sfx('thud', 0.7);
        S.shake(2, 0.3);
        await S.wait(0.6);
        d.drunkDone = true;
      });
    }
  }
  R.harvestRoof = async function (S) {
    S.party(['josuke', OKU()], { leader: 'josuke' });
    await S.setStage('roof_ch6', { x: 350, y: 156, facing: 1, music: 'battle', fade: false });
    for (let i = 1; i <= 4; i++) S.state('brk' + i, 0);
    const sg = S.spawn('shigechi', RF.sg[0], RF.sg[1], { id: 'shigechi_roof', facing: -1, name: '重清' });
    sg.hold = true;
    const ok = S.actor(OKU());
    if (ok) Object.assign(ok, { x: 372, y: 164, facing: 1, follow: null });
    await S.fadeIn(0.4);
    S.mark('b09b_start');
    await S.say('shigechi', '这边只有水管能走哦。丰收会一段一段把它咬断！', { actor: sg, expr: 'smile' });
    await S.fight({
      id: 'b09b_roof', arena: RF.arena, lead: 'josuke', swap: true, allies: [OKU()], music: 'battle', after: null, dmgScale: 1, energy: { start: 0 },
      steps: { n: 1, label: '走水管追上重清' },
      testHint: (ctx) => ({ x: Math.round(player().x), cut: (ctx.data.cut || []).join(','), fixed: (ctx.data.fixed || []).join(','), drunk: !!ctx.data.drunk }),
      tick: (c, dt) => roofTick(S, c, dt),
      endWhen: (c) => c.data.drunkDone === true,
      onRetry: async (S2, at, c) => { bugsClear(c.data); S2.filter('vignette', null); },
    });
    for (const a of W().stage.actors) if (a.id && /^h(b|vd)\d/.test(a.id)) a.remove = true;
    const p = S.player;
    p.controlReverseUntil = 0;
    S.filter('vignette', 0.35, { colour: '#7a3a10', inner: 0.5 });
    const pt = partnerOf(p);
    for (const a of [p, pt]) if (a) { a.state = 'down'; a.play('down'); a.hold = true; }
    // 丰收围上来
    const ring = [];
    for (let k = 0; k < 10; k++) {
      const h = S.spawn('harvest', p.x - 30 + k * 7, p.y + ((k % 2) ? 10 : -6), { id: 'hvr' + k, facing: k < 5 ? 1 : -1, shadow: false });
      h.hold = true; h.play('idle'); ring.push(h);
    }
    await S.walk(sg, p.x + 34, p.y, { speed: 40 });
    S.face(sg, -1);
    await S.say('shigechi', '嘿嘿，动不了了吧？……道歉的话，我就考虑放过你们。', { actor: sg, expr: 'smile' });
    const pick = await S.choice(['假装道歉，说钱都给他', '真心道歉'], '要怎么说？');
    S.mark('b09_apology');
    if (pick === 0) {
      await S.say('josuke', '……对不起。钱全都给你，行了吧？', { expr: 'shock' });
      await S.say(OKU(), '（仗助这家伙，说谎眼睛都不眨……）', { expr: 'shock' });
      await S.say('shigechi', '真的？全都给我？嘿嘿嘿……', { actor: sg, expr: 'smile' });
    } else {
      await S.say('josuke', '……说好三个人分，是我们先吵起来的。对不起。', { expr: 'normal' });
      await S.say('shigechi', '……诶？你、你真的道歉了？', { actor: sg, expr: 'shock' });
    }
    const ck = T().prop(S, 'check', sg.x - 6, sg.y + 0.5, { id: 'check_roof', frame: 0, z: 20 });
    await S.say('shigechi', '那、那我就把汇票收好——', { actor: sg, expr: 'smile' });
    // 放松的那一刻：亿泰削空间，汇票自己飞过来
    for (let tries = 0; tries < 3; tries++) {
      const r = await S.press({ key: 'attack', window: 0.8, label: 'J：轰炸空间——削！' });
      if (r === 'perfect' || r === 'ok') break;
      if (tries < 2) await S.say(OKU(), '……手软了。再来！', { expr: 'rage' });
    }
    const okA = S.actor(OKU());
    if (okA) { okA.state = 'idle'; okA.play('idle'); }
    await S.summon(okA, { dur: 0.12, rise: 4 });
    S.standAct(okA, 'erase', { dx: 18, z: 4, dur: 0.6 });
    S.sfx('whoosh', 0.9);
    S.sfxText('削！', okA, { dur: 0.8 });
    if (ck) await S.arc(ck, okA.x + 10, okA.y + 0.5, 14, 0.35);
    S.recall(okA);
    await S.say(OKU(), '空间削掉一块，东西就自己过来了。……我脑子不好使，这招倒是好使。', { expr: 'smile' });
    await S.say('shigechi', '还、还给我！', { actor: sg, expr: 'shock' });
    if (ck) ck.remove = true;
    for (const a of [p, pt]) if (a) { a.hold = false; a.state = 'idle'; a.play('idle'); }
    S.filter('vignette', null);
    await S.say('josuke', '……重清。看好了。', { expr: 'rage' });
    for (let tries = 0; tries < 3; tries++) {
      const r = await S.press({ key: 'ok', window: 0.8, label: 'E：撕碎！' });
      if (r === 'perfect' || r === 'ok') break;
    }
    for (const h of ring) h.remove = true;
    G.world.focus = null;
  };

  // =====================================================================================================================
  // 第 10 战 杀手皇后（b10_kq）：重清只能爬（×0.3），从操场爬到走廊窗边（520）。吉良在后面 14 px/s 地走。
  //   J：派丰收扑上去抱住吉良的腿（拖住 1.5 s，冷却 3 s）。吉良追上：杀手皇后一挥把重清推开（不扣血），吉良退 50 px。目标段，不会输
  // =====================================================================================================================
  const KQ = { arena: [10, 630], sg: 150, kira: 70, window: 520, kiraSpeed: 14 };
  function crawlPlay(a, map) {
    if (a._p6play) return;
    const orig = a.play;
    a._p6play = orig;
    a.play = function (n, o) { return orig.call(this, map[n] || n, o); };
  }
  function crawlRestore(a) { if (a && a._p6play) { a.play = a._p6play; delete a._p6play; } }
  function kqInit(S, c) {
    const d = c.data, p = player(), kr = S.actor('kira');
    d.init = true; d.cd = 0; d.holdT = 0; d.lastJ = G.input.lastPress('attack');
    p.x = KQ.sg; p.y = 160; p.facing = 1; p.speed = 20; p.noGuard = true; p.dodgeCd = 999;
    if (kr) { kr.x = KQ.kira; kr.y = 158; kr.facing = 1; kr.hold = true; kr.play('walk'); kr.team = 'npc'; }
    if (d.h) d.h.close();
    d.h = P4().overlay((g) => {
      const w = W(), pl = player();
      if (w.fight !== c || !pl) return;
      const s = u(pl.x, pl.y, 0);
      const k = d.cd > 0 ? 1 - d.cd / 3 : 1;
      g.fillStyle = 'rgba(0,0,0,0.6)'; g.fillRect(Math.round(s.x) - 17, Math.round(s.y) - 68, 34, 6);
      g.fillStyle = k >= 1 ? '#ffd83c' : '#a89a60'; g.fillRect(Math.round(s.x) - 16, Math.round(s.y) - 67, Math.round(32 * k), 4);
      text(g, '到窗边 ' + Math.max(0, Math.round(KQ.window - pl.x)) + ' px', 620, 14, '#fff4d6', 12, 'right', '#000000');
    }, { z: 2 });
    S.hint('往右爬到走廊窗边（→）。J：派丰收抱住吉良的腿', 7);
  }
  function kqTick(S, c, dt) {
    const d = c.data, p = player(), kr = S.actor('kira');
    if (!d.init) kqInit(S, c);
    if (!kr) return;
    p.dodgeCd = 999;
    d.cd = Math.max(0, d.cd - dt);
    const lp = G.input.lastPress('attack'), pressed = lp !== d.lastJ;
    d.lastJ = lp;
    if (pressed && d.cd <= 0) {
      d.cd = 3;
      const h = S.spawn('harvest', p.x - 4, p.y - 2, { id: 'hvk' + Math.floor(c.t * 10), facing: -1, shadow: false });
      h.hold = true; h.play('walk');
      S.sfx('doll_scurry', 0.6);
      S.arc(h, kr.x + 6, kr.y + 1, 16, 0.35).then(() => {
        d.holdT = 1.5; S.emote(kr, '……！', 0.8); S.sfx('thud', 0.5);
        G.defer(1.5, () => { h.remove = true; });
      }, G.cancelIgnore);
    }
    if (d.holdT > 0) { d.holdT -= dt; kr.play('hurt'); }
    else if (!d.swat) {
      kr.play('walk');
      kr.facing = p.x > kr.x ? 1 : -1;
      kr.x += kr.facing * KQ.kiraSpeed * dt;
    }
    if (!d.swat && Math.abs(kr.x - p.x) < 14) {
      d.swat = true;
      cine(c, async () => {
        S.summon(kr, { dur: 0.1, rise: 4 });
        S.standAct(kr, 'punch', { dx: 18, z: 6, dur: 0.5 });
        S.sfx('punch_heavy', 0.8); S.shake(3, 0.3);
        S.sfxText('啪', p, { dur: 0.5 });
        await S.animate(0.35, (k) => { p.x += 1.2; });
        p.x = Math.min(p.x, KQ.window - 4);
        kr.x = Math.max(KQ.arena[0] + 4, kr.x - 50);
        S.recall(kr);
        if (!d.swatTold) { d.swatTold = true; S.hint('被追上了也别停！J 让丰收拖住他', 5); }
        d.swat = false;
      });
    }
  }
  // 纽扣段（b10c_button）：最后一只丰收拖着纽扣从走廊（520）往左跑到操场的仗助（70）。
  //   学生的脚、扫帚碰到就从这一小段开头重来（检查点 520 / 390 / 228）。同一段重来 3 次以后，学生们就让开了
  const BT = { arena: [40, 630], start: 520, cps: [520, 390, 228], goal: 120 };
  const WALKERS = [
    { cid: 'kid', x0: 420, x1: 510, y: 160, sp: 34 }, { cid: 'fan_a', x0: 400, x1: 500, y: 170, sp: 26 },
    { cid: 'fan_b', x0: 250, x1: 370, y: 152, sp: 30 }, { cid: 'kid', x0: 130, x1: 220, y: 166, sp: 36 },
  ];
  const BROOM = { x0: 280, x1: 340, every: 3.2, on: 1.0 };
  function btInit(S, c) {
    const d = c.data, p = player();
    d.init = true; d.cp = 0; d.fails = [0, 0, 0]; d.broomT = 0;
    p.x = BT.start; p.y = 162; p.facing = -1; p.speed = 52; p.noGuard = true; p.dodgeCd = 999;
    for (const a of W().stage.actors) if (a.id && /^st6_/.test(a.id)) a.remove = true;
    d.walkers = WALKERS.map((q, i) => {
      const a = S.spawn(q.cid, G.lerp(q.x0, q.x1, Math.random()), q.y, { id: 'st6_' + i, facing: 1 });
      a.hold = true; a.play('walk');
      return Object.assign({ a, dir: Math.random() < 0.5 ? -1 : 1, off: false }, q);
    });
    d.btn = S.actor('btn6') || T().prop(S, 'button', p.x, p.y + 0.5, { id: 'btn6', z: 12 });
    if (d.h) d.h.close();
    d.h = P4().overlay((g) => {
      const w = W();
      if (w.fight !== c) return;
      const on = d.broomT % BROOM.every < BROOM.on;
      const warn = !on && BROOM.every - (d.broomT % BROOM.every) < 0.8;
      if (on || warn) {
        const a = u(BROOM.x0, 172), b = u(BROOM.x1, 142);
        g.save(); g.globalAlpha = on ? 0.5 : 0.25 + 0.2 * Math.sin(clk().ui * 20);
        g.fillStyle = on ? '#c89a62' : '#ffe070';
        g.fillRect(Math.round(a.x), Math.round(b.y), Math.round(b.x - a.x), Math.round(a.y - b.y));
        g.restore();
        if (on) text(g, '扫帚！', Math.round((a.x + b.x) / 2), Math.round(b.y) - 18, '#fff4d6', 12, 'center', '#000000');
      }
      const pl = player();
      if (pl) text(g, '到仗助那里 ' + Math.max(0, Math.round(pl.x - BT.goal)) + ' px', 620, 14, '#fff4d6', 12, 'right', '#000000');
    }, { z: 2 });
    S.hint('把纽扣交给仗助！往左跑（←），躲开学生的脚和扫帚（上下走能绕开）', 8);
  }
  function btTick(S, c, dt) {
    const d = c.data, p = player();
    if (!d.init) btInit(S, c);
    p.dodgeCd = 999;
    d.broomT += dt;
    if (d.btn) { d.btn.x = p.x + p.facing * 2; d.btn.y = p.y + 0.5; d.btn.z = 12; }
    // 检查点
    for (let i = BT.cps.length - 1; i > d.cp; i--) if (p.x <= BT.cps[i]) { d.cp = i; S.sfx('blip', 0.4); break; }
    const easy = d.fails[d.cp] >= 3;
    let hitBy = null;
    for (const q of d.walkers) {
      const a = q.a;
      a.x += q.dir * q.sp * dt;
      if (a.x < q.x0) { a.x = q.x0; q.dir = 1; }
      if (a.x > q.x1) { a.x = q.x1; q.dir = -1; }
      a.facing = q.dir;
      if (easy) { a.y = G.lerp(a.y, 145, Math.min(1, dt * 3)); continue; }
      if (Math.abs(a.x - p.x) < 9 && Math.abs(a.y - p.y) < 6) hitBy = 'foot';
    }
    const broomOn = d.broomT % BROOM.every < BROOM.on;
    if (!easy && broomOn && p.x > BROOM.x0 && p.x < BROOM.x1) hitBy = 'broom';
    if (hitBy && !d.reset) {
      d.reset = true;
      d.fails[d.cp]++;
      cine(c, async () => {
        S.sfx(hitBy === 'broom' ? 'whoosh' : 'thud', 0.6);
        S.sfxText(hitBy === 'broom' ? '唰' : '咚', p, { dur: 0.5 });
        p.flash = 1;
        await S.animate(0.3, (k) => { p.alpha = 1 - 0.7 * k; });
        p.x = BT.cps[d.cp]; p.y = 162; p.facing = -1; p.alpha = 1;
        if (d.fails[d.cp] === 3) S.hint('学生们好像察觉到了什么，让开了路', 5);
        d.reset = false;
      });
    }
  }
  R.killerQueen = async function (S) {
    // ---- 1 放学路上（过场）：吉良、杀手皇后、硬币炸弹
    S.party(['shigechi'], { leader: 'shigechi' });
    await S.setStage('jhs_ch6', { x: 200, y: 160, facing: -1, music: null, fade: false });
    S.state('pm', 0.9);
    const sg = S.player;
    const kr = S.spawn('kira', -20, 158, { id: 'kira', facing: 1, name: '西装男人' });
    if (kr.setStand && !kr.stand) kr.setStand('killerqueen');
    G.world.focus = { x: 140 }; G.world.snapCamera();
    await S.fadeIn(0.6);
    S.mark('b10_start');
    await S.say('shigechi', '得赶快告诉仗助……那个纸袋里的东西……', { expr: 'shock' });
    await S.walk(kr, 110, 158, { speed: 40 });
    await S.say('kira', '……同学。你拿错了我的纸袋。', { actor: kr, name: '西装男人' });
    await S.say('shigechi', '……！你、你就是那个纸袋的主人？', { expr: 'shock' });
    S.sfx('menacing', 0.7);
    S.nameCard('kira', { y: 100 });
    await S.say('kira', '看见了，就没办法了。我只想安安静静地生活。', { actor: kr, name: '吉良', expr: 'rage' });
    await S.summon(kr, { dur: 0.3, rise: 6, card: true });
    await S.say('shigechi', '替、替身！丰收——！', { expr: 'rage' });
    // 丰收扑上去，从他口袋里扯出一枚 100 日元
    const hs = [];
    for (let k = 0; k < 6; k++) {
      const h = S.spawn('harvest', sg.x - 6, sg.y - 2 + (k % 3) * 4, { id: 'hvs' + k, facing: -1, shadow: false });
      h.hold = true; h.play('walk'); hs.push(h);
      S.walk(h, kr.x + 8 + (k % 3) * 4, kr.y + (k % 2) * 4, { speed: 120 }).catch(G.cancelIgnore);
    }
    S.sfx('doll_scurry', 0.9);
    await S.wait(0.6);
    const coin = T().prop(S, 'coin100', kr.x + 8, kr.y + 0.5, { id: 'kq_coin', z: 14 });
    await S.say('shigechi', '嘿嘿，一百日元！钱我最喜欢了！', { expr: 'smile' });
    if (coin) await S.arc(coin, sg.x - 8, sg.y + 0.5, 18, 0.5);
    await S.say('kira', '……那枚硬币，杀手皇后已经碰过了。', { actor: kr, name: '吉良', expr: 'smile' });
    // 硬币炸开：只有白光。丰收挡在重清前面
    for (const [k, h] of hs.entries()) { h.x = sg.x - 12 + k * 2; h.y = sg.y + 1; }
    S.sfx('explosion', 0.9);
    S.flash(0.5, 1, '#ffffff');
    S.shake(4, 0.5);
    S.mark('b10_coin_bomb');
    if (coin) coin.remove = true;
    for (const h of hs) h.remove = true;
    sg.state = 'down'; sg.play('down');
    await S.wait(0.8);
    await S.say('shigechi', '……丰、丰收挡住了……', { expr: 'shock' });
    await S.say('kira', '你的朋友……叫什么名字？', { actor: kr, name: '吉良' });
    await S.say('shigechi', '仗……仗助和亿泰……你这个杀人犯，他们会揍扁你的！', { expr: 'rage' });
    S.recall(kr);
    await S.vs({ key: 'killerqueen', hero: 'shigechi', enemy: { cid: 'kira', anim: 'idle' } });
    G.uifx.vsTag('killerqueen');
    // ---- 2 爬回学校
    crawlPlay(sg, { walk: 'crawl', idle: 'crawl', guard: 'crawl', dodge: 'crawl' });
    sg.state = 'idle';
    G.world.focus = null;
    S.mark('b10_crawl');
    let h2 = null;
    await S.fight({
      id: 'b10_kq', arena: KQ.arena, lead: 'shigechi', swap: false, music: 'battle', after: null, playerMinHp: 1, losable: false,
      energy: { start: 0 }, steps: { n: 1, label: '爬到走廊窗边' },
      testHint: (ctx) => { const k = S.actor('kira'); return { x: Math.round(player().x), kira: k ? Math.round(k.x) : null, cd: ctx.data.cd }; },
      tick: (c, dt) => { kqTick(S, c, dt); h2 = c.data.h; },
      endWhen: (c) => !!c.data.init && player().x >= KQ.window,
      onRetry: async () => { if (h2) h2.close(); },
    });
    if (h2) h2.close();
    for (const a of W().stage.actors) if (a.id && /^hvk/.test(a.id)) a.remove = true;
    // 窗边：喊不出来的“仗助”。白光、剪影，丰收一只只消失；最后一只扯下了吉良袖口的纽扣
    crawlRestore(sg);
    sg.state = 'idle'; sg.play('cry');
    kr.hold = true; kr.play('walk');
    S.mark('b10_window');
    await S.say('shigechi', '仗助——！亿泰——！我、我在这儿……', { expr: 'shock' });
    await S.walk(kr, sg.x - 18, kr.y, { speed: 30 });
    S.face(kr, 1);
    const last = S.spawn('harvest', kr.x + 4, kr.y, { id: 'hv_btn', facing: 1, shadow: false });
    last.hold = true; last.play('idle');
    await S.say('kira', '安静点。窗户那边，听不见的。', { actor: kr, name: '吉良' });
    await S.summon(kr, { dur: 0.2, rise: 4 });
    S.standAct(kr, 'punch', { dx: 14, z: 6, dur: 0.6 });
    S.sfx('heartbeat', 0.8);
    S.flash(0.6, 1, '#ffffff');
    sg.tint = { color: '#000000', k: 1 };
    await S.wait(0.8);
    await S.animate(1.2, (k) => { sg.alpha = 1 - k; });
    sg.visible = false; sg.alpha = 1; sg.tint = null;
    S.recall(kr);
    await S.narrate('重清的声音，没能传到窗户那边。', { pos: 'top' });
    S.music('sad', 1.5);
    await S.say('kira', '……袖口的纽扣，掉了一颗？', { actor: kr, name: '吉良', expr: 'shock' });
    await S.walk(kr, 700, kr.y, { speed: 40 });
    kr.visible = false;
    last.remove = true;
    // ---- 3 纽扣：最后一只丰收
    S.party(['harvest'], { leader: 'harvest' });
    await S.setStage('jhs_ch6', { x: BT.start, y: 162, facing: -1, music: 'tension', fade: false });
    S.state('pm', 1);
    const hv = S.player;
    crawlPlay(hv, { walk: 'carry', idle: 'carry' });
    S.mark('b10c_start');
    await S.say(null, '一只丰收，拖着一颗纽扣，往操场跑去。');
    let h3 = null;
    await S.fight({
      id: 'b10c_button', arena: BT.arena, lead: 'harvest', swap: false, music: 'tension', after: null, playerMinHp: 1, losable: false,
      energy: { start: 0 }, steps: { n: 1, label: '把纽扣交给仗助' },
      testHint: (ctx) => ({ x: Math.round(player().x), y: Math.round(player().y), cp: ctx.data.cp, fails: (ctx.data.fails || []).join(',') }),
      tick: (c, dt) => { btTick(S, c, dt); h3 = c.data.h; },
      endWhen: (c) => !!c.data.init && player().x <= BT.goal,
      onRetry: async () => { if (h3) h3.close(); },
    });
    if (h3) h3.close();
    crawlRestore(hv);
    for (const a of W().stage.actors) if (a.id && (/^st6_/.test(a.id) || a.id === 'btn6')) a.remove = true;
    await S.fadeOut(0.6);
    kr.remove = true;
  };

  // =====================================================================================================================
  // 线索小卡：画面中间一张牛皮纸卡片 + 快门声
  // =====================================================================================================================
  R.clueCard = async function (S, what) {
    S.sfx('camera_shutter', 0.8);
    const h = P4().overlay((g, t) => {
      const k = Math.min(1, t / 0.25), x = 320, y = 150;
      g.save();
      g.globalAlpha = k;
      g.fillStyle = 'rgba(0,0,0,0.45)'; g.fillRect(0, 0, 640, 360);
      g.fillStyle = '#3a2a18'; g.fillRect(x - 112, y - 54, 224, 108);
      g.fillStyle = '#e8d4a8'; g.fillRect(x - 108, y - 50, 216, 100);
      g.fillStyle = '#c8b080'; g.fillRect(x - 108, y + 16, 216, 2);
      text(g, '线索', x - 94, y - 42, '#8a3a2a', 12, 'left', null);
      text(g, what, x, y - 18, '#2a1a0a', 16, 'center', null);
      text(g, '西装外套的纽扣', x, y + 24, '#5a4028', 12, 'center', null);
      // 纽扣
      g.fillStyle = '#4c3a74'; g.fillRect(x - 10, y - 2, 20, 14);
      g.fillStyle = '#7a64a6'; g.fillRect(x - 8, y, 16, 10);
      g.fillStyle = '#f4ecd8'; g.fillRect(x - 4, y + 3, 3, 3); g.fillRect(x + 2, y + 3, 3, 3);
      g.restore();
    }, { z: 6 });
    await S.wait(2.2);
    h.close();
  };
})();
