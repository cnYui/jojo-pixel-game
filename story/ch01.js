// 第1章保留两种不同的解法：用隐藏触须保护乘客，用地火破解战车的正面架剑。
'use strict';
(function () {
  const G = window.G, T = G.TPL, F = () => G.flags;
  const crew = ['jotaro', 'joseph', 'avdol', 'kakyoin'];
  const seats = [64, 128, 192, 256, 352, 416, 480, 544];
  const passengerIds = seats.map((_, i) => 'passenger' + i);
  const counted = () => { F().planeTalk = (F().planeTalk || 0) + 1; };
  const lines = async (S, rows) => { for (const [who, text, expr] of rows) await S.say(who, text, expr ? { expr } : {}); };
  // 对话框放上面：人物 / 道具在画面下半（跪地、躺倒、桌面）时用，免得被底部对话框挡住
  const linesTop = async (S, rows) => { for (const [who, text, expr] of rows) await S.say(who, text, Object.assign({ pos: 'top' }, expr ? { expr } : {})); };
  const hot = (id, x, y, label, tags, use, look, o = {}) => Object.assign({ id, x, y, label, tags, r: 24, ry: 120, use, look }, o);
  const sayBy = (S, p, map) => S.say(p.cid, T.by(p, map));
  // 灰塔段 B 的触须网：平时那条半透明细线由 hazard 的 fxActive（fx_mid 的 tendrils_line，alpha .3）画；
  //   这里补两样：刚铺下的 0.4 s 亮一下（让玩家知道网铺在哪）、最后 1 s 闪烁（快消失了），缠住时几根丝收拢到灰塔身上
  const NET_GREEN = '#50e890', NET_LIGHT = '#c0ffd8';
  function thread(P, x0, y0, x1, y1, t, seed, a, colour) {
    const L = Math.max(1, Math.abs(x1 - x0)), n = Math.ceil(L / 1.5);
    for (let i = 0; i <= n; i++) {
      const s = i / n, sag = 3 * 4 * s * (1 - s), w = Math.sin(s * 9 + t * 3 + seed) * 0.8 * Math.sin(Math.PI * s);
      G.px.plot(P, Math.round(x0 + (x1 - x0) * s), Math.round(y0 + (y1 - y0) * s + sag + w), colour, a);
    }
  }
  function drawNets(P, ox, oy, t) {
    const W = G.world, fight = W.fight;
    if (!fight || fight.id !== 'b1b_towergray' || !G.px) return;
    for (const h of W.hazards) {
      if (h.tag !== 'net' || h.dead) continue;
      const age = h.t || 0, left = (h.warn || 0) + (h.dur || 0) - age;
      const fresh = Math.max(0, 1 - age / 0.4), blink = left < 1 && Math.floor(t * 8) % 2 === 0;
      if (fresh <= 0 && !blink) continue;
      const grow = Math.min(1, age / 0.12), x0 = h.x0 + ox, x1 = h.x1 + ox, xm = x0 + (x1 - x0) * grow, yc = (h.y0 + h.y1) / 2 + oy;
      const a = fresh > 0 ? 0.35 + 0.65 * fresh : 0.45, seed = (h.x0 | 0) % 17;
      for (let k = 0; k < 2; k++) thread(P, x0, yc - 4 + k * 8, xm, yc - 3 + k * 8, t, seed + k * 5, a, fresh > 0.5 ? NET_LIGHT : NET_GREEN);
    }
    const b = fight.boss;
    if (b && b.rootT > 0 && !b.remove) {
      const bx = b.x + ox, by = b.y - (b.z || 0) - 4 + oy;
      for (let k = 0; k < 6; k++) {
        const ang = k / 6 * Math.PI * 2 + t * 0.6, r = 16 + (k % 2) * 6;
        thread(P, bx + Math.cos(ang) * r, b.y + oy + Math.sin(ang) * 4, bx, by, t, k * 3, 0.9, k % 2 ? NET_LIGHT : NET_GREEN);
      }
    }
  }
  // 自由走动的去向提示：目标在画面里 → 头顶上下跳的金色箭头；在画面外 → 屏幕边上闪的箭头指过去
  //   target() 返回 { x, y } 或 null（不需要提示）；剧情忙、战斗、对话时不画
  function goalArrow(stageId, target) {
    const GOLD = '#ffd83c', INK = '#2a1a00';
    return { type: 'pixel', id: 'goal_arrow', x: 0, y: 0, draw(P, ox, oy, t) {
      const W = G.world, px = G.px;
      if (!px || !W.stage || W.stage.id !== stageId || !W.free || W.combat || G.S.busy || (G.ui && G.ui.blocking && G.ui.blocking())) return;
      const g = target(); if (!g) return;
      const p = W.player; if (p && Math.abs(p.x - g.x) < 28) return;   // 走到跟前就不挡画面
      const sx = Math.round(g.x + ox), bob = Math.round(Math.sin(t * 6) * 2);
      if (sx >= 10 && sx <= 310) {
        const y = Math.round((g.y - 58) + oy) + bob;
        px.poly(P, [[sx - 6, y - 1], [sx + 6, y - 1], [sx, y + 7]], INK);
        px.poly(P, [[sx - 4, y], [sx + 4, y], [sx, y + 5]], GOLD);
        return;
      }
      if (Math.floor(t * 3) % 3 === 2) return;   // 边上的箭头一闪一闪
      const right = sx > 310, x = right ? 306 + bob : 14 - bob, y = 112, d = right ? 1 : -1;
      for (let k = 0; k < 2; k++) {
        const cx = x - d * k * 7;
        px.poly(P, [[cx - d * 5, y - 7], [cx + d * 3, y], [cx - d * 5, y + 7]], INK);
        px.poly(P, [[cx - d * 4, y - 5], [cx + d * 2, y], [cx - d * 4, y + 5]], GOLD);
      }
    } };
  }
  // 法皇从行李架里取下的毛毯：自己画一条 16 px 的小毛毯（座位上的乘客只露头肩 16×18；原来借的 blanket 道具是 56×14 的床用被子，
  //   掉下来像一块淡绿色的玻璃板，比乘客还宽三倍）。下落时叠成小块左右晃，落地后披在妈妈肩上
  //   2026-10-10 客舱按人的比例重画：乘客坐在远侧座椅里（脚底 y 150、z 15，头肩下沿 y 135）。毛毯 y 141 = 落定时肩线在 y 132–136，
  //   depth 150.7 = 画在椅背（seats 道具 depth 150.5）前面：看起来是披在她肩上、搭在椅背顶上
  const BLK = ['#e6d6aa', '#b8a478', '#7c6a48', '#c85a4a'];
  // 坐姿和座椅（tools\bg_new\plane_cabin_side.py 的 SIT_Y / SIT_Z / SEATS_Y0）：头肩画在座椅后面，椅背 seats 图按 depth 盖住肩膀以下
  const SIT = { y: 150, z: 15 }, SEAT_DEPTH = 150.5;
  const seatsFront = { type: 'image', id: 'seats_front', image: 'bg/plane_cabin_side/seats', x: 0, y: 124, depth: SEAT_DEPTH };
  const blanketProp = { type: 'custom', id: 'blanket_small', x: 192, y: 141, depth: 150.7, z: 76, hidden: true,
    draw(g, x, y) {
      const z = Math.round(this.z || 0), top = y - z;
      if (z > 2) {   // 叠成一小块在空中晃
        const w = 10, x0 = x - 5 + Math.round(Math.sin(z * 0.35) * 2), y0 = top - 16;
        g.fillStyle = BLK[2]; g.fillRect(x0, y0, w, 5);
        g.fillStyle = BLK[0]; g.fillRect(x0 + 1, y0 + 1, w - 2, 3);
        g.fillStyle = BLK[3]; g.fillRect(x0 + 1, y0 + 2, w - 2, 1);
        return;
      }
      // 披在肩上：上窄下宽 5 行（[左缩进, 宽]），两端描深色边，下沿一行深一点，中间一道红条纹、两道褶子
      const rows = [[3, 10], [1, 14], [0, 16], [0, 16], [0, 16]];
      g.fillStyle = BLK[2]; g.fillRect(x - 5, top - 10, 10, 1);
      rows.forEach(([dx, w], i) => {
        const yy = top - 9 + i, x0 = x - 8 + dx;
        g.fillStyle = i === rows.length - 1 ? BLK[1] : BLK[0]; g.fillRect(x0, yy, w, 1);
        g.fillStyle = BLK[2]; g.fillRect(x0, yy, 1, 1); g.fillRect(x0 + w - 1, yy, 1, 1);
      });
      g.fillStyle = BLK[3]; g.fillRect(x - 7, top - 7, 14, 1);
      g.fillStyle = BLK[1]; g.fillRect(x - 3, top - 6, 1, 3); g.fillRect(x + 3, top - 6, 1, 3);
    } };
  function setupPlane() {
    const st = G.STAGES.plane_ch1;
    blanketProp.hidden = !F().blanket; blanketProp.z = F().blanket ? 0 : 76;
    st.props = [{ type: 'pixel', id: 'net_view', x: 0, y: 0, draw: drawNets },
      goalArrow('plane_ch1', () => ((F().planeTalk || 0) >= 3 ? null : { x: 572, y: 160 })), seatsFront, blanketProp];
    // 乘客都朝机头（右）坐着：座椅是朝右的（原来后四个翻成朝左，等于倒着坐）
    st.npcs = seats.map((x, i) => T.npc('npc_passenger_' + 'abcd'[i % 4], passengerIds[i], x, SIT.y,
      { anim: 'seated', facing: 1, z: SIT.z, shadow: false, talkRy: 48, vip: true, talk: async S => {
        counted();
        const n = T.count('seat' + i);
        const text = i === 1 ? (n === 1 ? '去中东出差，第一次坐这么久的飞机……' : '前面那位老爷爷，一直在自己笑。有点怪。')
          : i === 2 ? (F().blanket ? '毛毯……自己飘下来了？谢、谢谢……' : '孩子刚睡着，拜托小声一点哦。')
            : i === 4 ? (n === 1 ? 'Zzz……' : '……炸、炸鸡……Zzz') : '这次旅行，希望平安抵达。';
        await S.say('npc_passenger_' + 'abcd'[i % 4], text);
      } }));
    st.npcs.push(T.npc('grayfly', 'grayfly', 584, SIT.y, { anim: 'seated', facing: 1, z: SIT.z, shadow: false, talkRy: 48,
      talk: async S => { counted(); const n = T.count('grayfly'); await S.say('grayfly', ['嘿嘿……年轻人，旅途愉快啊。', '去开罗？真巧，真巧……嘿嘿嘿。', '这飞机啊，可得好好地飞……嘿嘿。'][(n - 1) % 3]); },
      onStand: async S => { counted(); await S.say('grayfly', '……嘿、嘿嘿。年轻人，手不要乱挥。'); } }));
    st.npcs.push(T.npc('npc_stewardess', 'stewardess', 420, 160, { talk: async S => {
      counted();
      if (T.count('stewardess') === 1) await lines(S, [['npc_stewardess', '本次航班飞往开罗，请系好安全带。……帽子在机舱里也不摘吗？'], ['jotaro', '不摘。']]);
      else await S.say('npc_stewardess', '需要毛毯的话请告诉我。');
    } }));
    const use = text => async (S, h, p) => { counted(); await S.say(p.cid, text); };
    st.hotspots = [
      // 调查点 y 放在过道（选中范围按脚底算），ly = 标签画在东西上面：紧急出口门的圆窗 (304,104)、行李架 (192,66)、两头的门
      hot('window', 304, 158, '舷窗', ['detail'], use('云海。'), async (S, h, p) => { counted(); await sayBy(S, p, { jotaro: '……窗户里面，好像有只虫子一闪而过。', _: '云海里看不出目的地。' }); }, { ly: 92 }),
      hot('bin', 192, 158, '行李架', ['reach'], use('最里面塞着一条毛毯，够不着。'), async (S, h, p) => {
        counted(); F().blanket = true;
        // 毛毯从行李架（y 50–84）飘下来，最后披在妈妈（座位 192）的肩上
        blanketProp.hidden = false; blanketProp.z = 76;
        S.sfx('whoosh', { vol: .4, rate: .7 });
        await S.animate(.8, k => { blanketProp.z = 76 * (1 - k) * (1 - k * .35); });
        blanketProp.z = 0;
        await S.say(p.cid, '法皇的手，比我自己的长一点。');
      }, { ly: 56 }),
      hot('toilet', 24, 158, '洗手间', ['life'], use('有人。'), async (S, h, p) => { counted(); await S.say(p.cid, '里面有一个人……在打瞌睡。'); }, { ly: 96 }),
      hot('cockpit_door', 618, 158, '驾驶舱门', ['life'], use('机组人员专用。'), async (S, h, p) => { counted(); await S.say(p.cid, '门后两个人，呼吸很平稳。'); }, { ly: 96 }),
    ];
    st.onLook = async (S, p) => {
      counted(); if (p.cid === 'avdol') F().sensed = true;
      await sayBy(S, p, { avdol: '……这架飞机上，有一个不属于人的气息。', joseph: '这里没有相机可砸……空姐的相机？不行不行。', jotaro: '……全是普通人。', kakyoin: '触须能伸到行李架上去。' });
    };
  }
  function planeTalks(S) {
    T.memberTalk({
      joseph: async S2 => { counted(); await S2.say('joseph', ['东京到开罗，最快的路线。五十天，绰绰有余！', '坐飞机？我可没什么不好的回忆。……好吧，两次。', 'Holly 那边有 SPW 的人守着。我们只管往前。'][(T.count('joPlane') - 1) % 3]); },
      avdol: async S2 => { counted(); await S2.say('avdol', T.count('avPlane') % 2 ? '乔斯达先生说“没问题”的时候，我反而有点担心。' : '刺客不会只派一个。大家都要小心。'); },
      kakyoin: async S2 => { counted(); if (T.count('kakPlane') % 2) await lines(S2, [['kakyoin', '替身是用塔罗牌起名字的吧？我的是『教皇』，你的呢？'], ['jotaro', '『星星』。……白金之星。']]); else await S2.say('kakyoin', '我从小就有替身，却从来没遇过能看见它的人。……感觉有点奇怪。'); },
      jotaro: async S2 => { counted(); await S2.say('jotaro', '……飞机上不能抽烟。'); },
    });
    S.hint('Q 换队长；E 搭话；U 替身调查。继续往驾驶舱走。', 7);
  }
  async function tower(S) {
    S.hint(null);
    S.music('tension');
    // 玩家可能在过道任何位置触发（搭话 3 次或走到 x ≥ 560）：灰塔登场、段 A 的场地都跟着队长的位置走，不在镜头外演
    const px0 = G.clamp(S.player.x, 140, 500), ax0 = G.clamp(px0 - 120, 16, 384);
    const bug = S.spawn('towergray', px0 + 150, 160, { id: 'gray_intro', z: 24, shadow: false, anim: 'fly', pivot: 'center' });
    // 跟随的三个人原来叠在队长身后一团（替身也亮着），对话时看不清谁在说话：散开站到队长身后一字排开（灰塔从右边来）
    crew.filter(cid => cid !== S.player.cid).forEach((cid, i) => {
      const a = S.actor(cid); if (!a) return;
      a.follow = null; if (a.stand && a.stand.visible) a.stand.recall();
      S.walk(a, G.clamp(px0 - 30 - i * 24, 20, 600), 157 + (i % 2) * 7, { speed: 110 }).then(() => { a.facing = 1; }, G.cancelIgnore);
    });
    const buzz = G.audio.loop('insect_buzz_loop', { vol: .35 });
    // 空姐听见怪声躲进前面的乘务间：两场战斗都不让她站在过道中间挡画面
    const sw = S.actor('stewardess');
    if (sw) { sw.talk = null; S.walk(sw, 636, 160, { speed: 110 }).then(() => { sw.visible = false; }, G.cancelIgnore); }
    try {
      await S.animate(.8, k => { bug.x = px0 + 150 - k * 110; bug.z = 24 + Math.sin(k * 28) * 8; });
      await lines(S, [[null, '然而，DIO的刺客早已潜伏在飞机上……'], ['jotaro', '……虫子？在飞机上？'], ['kakyoin', '承太郎，那不是普通的虫子。']]);
      bug.remove = true;
      S.hint('打它！（J）跟着灰塔挥空六次，或观察八秒。', 8);
      await S.fight({ id: 'b1a_towergray_jotaro', lead: 'jotaro', swap: false, arena: [ax0, ax0 + 240],
        playerMinHp: 40, losable: false, coverage: false, music: 'tension', finish: 'none', dmgScale: .8,
        steps: { n: 6, label: '跟着它挥空' },
        waves: [[{ kit: 'e_towergray_a', actor: 'towergray', id: 'towergray', x: ax0 + 170, y: 160, hp: 300, bodyW: 3, speed: 240, fly: { z: 24, bob: 6 }, pivot: 'center', koStyle: 'none' }]],
        onWave: async (s, wi, es, attempt, ctx) => { ctx.on('whiff', () => { ctx.data.whiffs = (ctx.data.whiffs || 0) + 1; ctx.step(ctx.data.whiffs); }); },
        endWhen: ctx => (ctx.data.whiffs || 0) >= 6 || ctx.t >= 8,
        testHint: ctx => ({ whiffs: ctx.data.whiffs || 0 }),
      });
      const ins = T.insert(S, { bg: 'menace', parts: [
        { cid: 'towergray', anim: 'needle', frame: 0, x: 220, y: 70, scale: 5 },
        { cid: 'starplat', anim: 'reach', frame: 0, x: 90, y: 172, scale: 3 },
      ] });
      S.sfx('stab'); S.fx('hit_spark', { x: 146, y: 94, size: 6 }, { space: 'canvas' });
      await S.wait(.4); ins.close();
      await T.closeup4(S, { cid: 'jotaro', expr: 'angry', dur: .7 });
      S.sfxText('ガキッ', { x: 320, y: 120 });
      S.standCard('towergray');
      await lines(S, [['avdol', '那是……『灰塔』！'], ['avdol', '专门把杀人伪装成事故的替身。去年那起空难，就是它干的。'], ['jotaro', '……连白金之星都抓不住。'], ['kakyoin', '承太郎，这里交给我。']]);
      // 花京院站到过道中间（规划 1-5 第 4 句）：段 B 第一次扑击的红线就在他身边
      const kak = S.actor('kakyoin');
      if (kak) { kak.follow = null; await S.walk(kak, 300, 162, { speed: Math.max(90, Math.abs(kak.x - 300) / 1.4) }); kak.facing = 1; }
      await lines(S, [['kakyoin', '它想让整架飞机的人陪葬。……我不会让它得逞。'], ['jotaro', '……随你。']]);
      await S.summon('kakyoin', { card: true });
      // 段 A 的灰塔是“打不中”招式组建的；段 B 换成新的灰塔角色，免得沿用段 A 的闪避钩子和 0 倍伤害
      const oldBug = S.actor('towergray'); if (oldBug) oldBug.remove = true;
      if (buzz && buzz.stop) buzz.stop(.15);   // 段 B 的嗡嗡声由灰塔自己放（升调提示红线）
      const tips = ['看到红线就走过去，面朝灰塔连按三下 J：第三下把触须网铺在面前。', '缠住时它掉在过道上：赶快对准它连按 J；能量满了趁缠住按 U。', '它刺你之前嘴里会闪光（！）：按 K 闪开，或者按 L 格挡。'];
      await S.fight({ id: 'b1b_towergray', lead: 'kakyoin', swap: false, arena: [16, 624], music: 'battle', dmgScale: .8,
        energy: { start: 0 }, vs: 'towergray', finish: 'none', losable: true,
        bench: { mode: 'stay', at: { jotaro: [596, 160], joseph: [606, 158], avdol: [616, 162] } },
        vips: passengerIds, vipHp: 20,
        kitOverride: { kakyoin: { combo: ['KAK_J1', 'KAK_J2', 'KAK_NET_HIDDEN'] } },
        waves: [[{ kit: 'e_towergray', cid: 'towergray', id: 'towergray', name: '灰塔', x: 340, y: 160, hp: 300, poiseMax: 0, speed: 240, bodyW: 3, fly: { z: 24, bob: 6 }, pivot: 'center', koStyle: 'none', boss: true }]],
        failWhen: ctx => {
          const all = passengerIds.every(id => { const a = S.actor(id); return !a || a.hp <= 0; });
          if (all) ctx.failText = '乘客都倒下了……';
          return all;
        },
        onRetry: async (s, attempt) => { passengerIds.forEach(id => { const a = S.actor(id); if (a) { a.hp = a.maxHp; a.state = 'idle'; a.play('seated'); } }); },
        onWave: async (s, wi, es, attempt, ctx) => {
          // 乘客只会被灰塔的“扑击”刺倒；针刺花京院、俯冲路过时不误伤座位上的人
          passengerIds.forEach(id => { const a = S.actor(id); if (a) { a.evadeWord = null; a.onHitBy = (t, att, m) => (m && m.diveAlongPath && att && att.mem && att.mem.diveTarget === t ? null : 'evade'); } });
          ctx.on('koBlocked', ({ e }) => { if (e === ctx.boss) ctx.data.defeated = true; });
          ctx.on('netCatch', ({ n }) => { if (n <= 2) S.hint(n === 1 ? '缠住了！它现在躲不开——对准它连按 J！' : '每缠住一次都会攒能量。能量满了，趁缠住按 U：绿宝石水花！', 5); });
          S.hint(attempt ? tips[(attempt - 1) % tips.length] : '它太快，平时打不中。它扑向乘客前会拉出红线：站到红线上连按三下 J，把触须网铺在面前，缠住它再打！', attempt ? 7 : 9);
        },
        tick: ctx => {
          const b = ctx.boss, p = ctx.player;
          if (b && b.tele && b.tele.move === 'TG_DIVE_FIRST' && !ctx.data.firstLine) { ctx.data.firstLine = true; S.hint('红线！走到红线上，面朝灰塔连按三下 J！', 3); }
          if (p && p.energy >= 100 && !ctx.data.fullTold) { ctx.data.fullTold = true; S.hint('能量满了！等灰塔被缠住再按 U，绿宝石水花才打得中。', 6); }
        },
        endWhen: ctx => !!ctx.data.defeated,
        testHint: ctx => ({ rooted: !!(ctx.boss && ctx.boss.rootT > 0), passengers: passengerIds.filter(id => S.actor(id) && S.actor(id).hp > 0).length, catches: (ctx.boss && ctx.boss.mem.catches) || 0 }),
      });
    } finally { if (buzz && buzz.stop) buzz.stop(.15); }
    G.hitStopAll(.3); S.impact(['invert', 'green']); S.shake(4, .3);
    // 花京院没有 pose 动作（原来回退成 idle）：用施法动作 cast，法皇在身后同样 cast
    await T.fullbody3(S, { cid: 'kakyoin', anim: 'cast', behind: { cid: 'hiero', anim: 'cast' }, bg: 'radial', colours: ['#126e3c', '#041c14'], dur: .7 });
    const b = S.actor('towergray');
    if (b) { S.fx('shatter', { x: b.x, y: b.y - b.z, pieces: 18, dur: .7, colours: ['#b0e070', '#fff8d0'] }); b.remove = true; }
    S.sfx('glass_break'); S.sfx('punch', { seed: 0 });
    // 格雷·弗莱从座位 584 站起来（规划 1-7：站起，摇晃，倒下）：从座椅后面挪到过道上，晃两下，倒在过道里
    const gray = S.actor('grayfly');
    if (gray) {
      gray.z = 0; gray.y = 159; gray.x = 590; gray.shadow = true; gray.facing = -1;
      S.pose(gray, 'hurt');
      S.shake(1, .2, { dir: 'x' });
    }
    await S.say('grayfly', 'DIO……大人……', { expr: 'scared' });
    if (gray) {
      S.pose(gray, 'idle');
      await S.animate(.5, k => { gray.x = 590 - Math.sin(k * Math.PI * 3) * 2; });
      S.pose(gray, 'down'); S.sfx('thud', .7);
    }
    await S.title('saiki');
    await S.say('avdol', '替身被打碎，本体也撑不住了。');
    passengerIds.forEach(id => { const a = S.actor(id); if (a) { a.state = 'idle'; a.play('seated'); a.hp = a.maxHp; } });
    await S.say('npc_passenger_a', '……我、我怎么睡着了？刚才好像做了个噩梦……');
    S.sfx('rumble'); S.sfx('thud'); S.shake(3, .6);
    // 氧气面罩从镜头里那几排座椅头顶的服务面板（y 84–89）掉出来（原来写死 x 100 / 280 / 450，队伍在机舱后半段时全在画面外）：
    //   面罩图的锚点在上沿；纵深 149 = 坐着的乘客后面；z 从 72 落到 61 → 挂在 y 88–97，正好吊在乘客头顶上方
    const cx0 = G.cam ? G.cam.x : 0;
    const rows = ((G.D && G.D.bg && G.D.bg.plane_cabin_side && G.D.bg.plane_cabin_side.anchors.rows) || [64, 96, 128, 160, 192, 224, 256, 352, 384, 416, 448, 480, 512, 544, 584])
      .filter(r => r + 8 > cx0 + 10 && r + 8 < cx0 + 310);
    rows.forEach((r, i) => { const mx = r + 8, m = T.prop(S, i % 3 === 2 ? 'scene:s06_mask_s' : 'scene:s06_mask', mx, 149, { z: 72 }); if (m) S.arc(m, mx, 149, -2, .3, { z1: 61 }).catch(G.cancelIgnore); });
    await S.say('joseph', '不对……飞机在往下掉！', { expr: 'shock' });
  }
  async function crash(S) {
    // 驾驶舱（2026-10-10 按人的比例重画，tools\bg_new\cockpit.py）：远侧副驾驶歪倒在座位上（画在背景里），
    //   近侧机长座空着——机长倒在座椅后面的地板上（s06_pilot_ko，头朝门口），帽子掉在旁边；警报灯一直闪（state.alarm）
    await S.setStage('cockpit_ch1', { x: 176, y: 172, music: 'tension', ambient: null });
    S.state('alarm', true); S.state('yoke', 0);
    T.prop(S, 'scene:s06_pilot_ko', 132, 174); T.prop(S, 'scene:s06_cap', 166, 175);
    // 底部对话框和 QTE 框会挡住地上的机长和抓着操纵杆的乔瑟夫——对白放上面、QTE 框放上面
    const crewAt = { jotaro: [52, 172], kakyoin: [72, 168], avdol: [92, 175] };
    for (const [cid, [x, y]] of Object.entries(crewAt)) { const a = S.actor(cid); if (a) { a.follow = null; a.x = x; a.y = y; a.facing = 1; } }
    const jo0 = S.actor('joseph'); if (jo0) { jo0.follow = null; jo0.x = 176; jo0.y = 172; jo0.facing = 1; }
    const top = async rows => { for (const [who, text, expr] of rows) await S.say(who, text, Object.assign({ pos: 'top' }, expr ? { expr } : {})); };
    await top([['joseph', '驾驶员……被灰塔下了手！', 'shock'], ['joseph', 'OH MY GOD!', 'shock']]);
    S.setLeader('joseph', { force: true });
    // 换队长会重建跟随：三个人原来跟着冲向操纵杆的乔瑟夫走，站到倒地的驾驶员身上。留在门口原位
    for (const [cid, [x, y]] of Object.entries(crewAt)) { const a = S.actor(cid); if (a) { a.follow = null; a.x = x; a.y = y; a.facing = 1; } }
    // 乔瑟夫冲到操纵杆前抓住（规划 1-8 CK_LUNGE / CK_GRAB）：站在空着的机长座前面、面朝挡风玻璃，双手攥住近侧的羊角盘，QTE 时一直抓着
    const jo = S.actor('joseph');
    if (jo) { jo.follow = null; await S.walk(jo, 228, 172, { speed: 130, anim: 'run' }); jo.facing = 1; S.pose(jo, 'guard'); }
    for (let n = 0; ; n++) {
      S.state('yoke', 0);
      if (!await S.clash({ id: 'ck_pull', label: '拉起来——！！（连按 J）', time: 4, y: 16 })) { await top([['joseph', 'OH NO！再来！']]); continue; }
      S.state('yoke', 1);       // 拉起来了：操纵杆拉到底
      if (await S.timing({ label: '机头对准海面！', speed: 1.1, zone: n ? [.396, .604] : [.42, .58], tries: 2, y: 16 })) break;
      await top([['joseph', 'OH NO！再来！']]);
    }
    if (jo) S.unpose(jo);
    await S.setStage('sky_ch1', { x: 120, y: 166, music: null, ambient: null });
    G.audio.stopMusic(.2);
    const plane = T.prop(S, 'plane_crash', 160, 160, { z: 90 });
    S.sfx('wind'); S.sfxText('呜哇啊啊啊——！！', { x: 320, y: 180 });
    if (plane) await S.animate(.9, k => { plane.x = 150 + k * 60; plane.z = 90 - k * 80; }); else await S.wait(.9);
    await S.setStage('sea_ch1', { x: 160, y: 156, music: null });
    S.impact(['invert', 'blue']); S.sfx('crash'); S.sfx('splash'); S.shake(5, .5);
    // water_splash 的 size 是倍数（1 = 34 px 水柱），原来写 30 = 一千多像素的水柱 + 九百像素的涟漪圈，天空整块被刷成平蓝（2026-10-11 发现）
    [100, 160, 220].forEach(x => S.fx('water_splash', { x, y: 140, size: 1.6 }));
    S.sfxText('扑通——！！', { x: 320, y: 180 });
    for (const [i, cid] of crew.entries()) { const a = S.actor(cid); a.x = 90 + i * 46; a.y = 156; a.follow = null; S.pose(a, 'float'); }
    // 海面只占画面下方，底部对话框会把漂在水上的四个人整个挡住：这一段对话框也放到上面
    await top([['joseph', '这是我人生第三次坠机了！']]);
    if (G.uifx.crashRecord) await G.uifx.crashRecord(2, 3);
    S.sfx('sting_comedy');
    await top([['jotaro', '……我再也不跟你坐同一架飞机了。'], ['kakyoin', '……第三次？'], ['avdol', '……我开始明白，您说的“没问题”是什么意思了。'], ['joseph', '有渔船！喂——！这边——！', 'shock']]);
    crew.forEach(cid => S.unpose(cid)); S.music('daily');
    await S.route(['东京', '香港'], { vehicle: 'plane', day: 1, left: 50 });
  }
  function setupHongkong(returning = false) {
    const st = G.STAGES[returning ? 'hk_street_ch1b' : 'hk_street_ch1'];
    // 桌子、电视、风筝要被剧情改帧 / 挪动，换图后由 placeHongkongProps 生成道具角色；这里只放去向箭头
    st.props = [goalArrow(st.id, () => (returning ? (F().ch1Exit ? null : { x: 944, y: 160 }) : F().garden ? null : F().dinnerDone ? { x: 944, y: 160 } : { x: 590, y: 158 }))];
    st.npcs = [
      T.npc('npc_hk_passer_a', 'passer', 150, 160, { talk: async S => {
        if (returning && S.player.cid === 'polnareff') await lines(S, [['polnareff', '是我。要再看一次吗？'], ['npc_hk_passer_a', '不、不用了！']]);
        else await S.say('npc_hk_passer_a', returning ? '那个变戏法的法国佬跟你们走了？' : T.count('passer') % 2 ? '刚才有个法国佬在街上用硬币变戏法，一剑串五个！厉害得很！' : '你们是游客？晚上别往码头那边乱走哦。');
      } }),
      T.npc('npc_hk_granny', 'granny', 300, 158, { talk: async S => {
        if (returning && S.player.cid === 'polnareff') await lines(S, [['polnareff', 'Madame，您年轻时一定是位大美人！'], ['npc_hk_granny', '死鬼佬，嘴巴真甜。……粥算你便宜点。']]);
        else await S.say('npc_hk_granny', returning ? '刚才那边又是火又是剑的，拍电影吗？' : T.count('granny') % 2 ? '后生仔，饮碗粥暖暖胃啦。' : '那个帽子仔，脸好臭。');
      } }),
      T.npc('npc_hk_owner', 'owner', 590, 158, { talk: async S => {
        if (!returning) { F().dinner = true; await dinner(S); }
        else await S.say('npc_hk_owner', S.player.cid === 'joseph' ? 'SPW 的人刚才来赔了一张新的，比原来的还好！' : '桌子……我的桌子……');
      } }),
      T.npc('npc_fortune', 'fortune', 760, 158, { talk: async S => {
        if (S.player.cid === 'avdol') await lines(S, [['avdol', returning ? '借你的牌看看。' : '同行啊。……你这副塔罗牌，少了一张『战车』。'], ['npc_fortune', returning ? '请便。……咦，“战车”那张又回来了？' : '咦？刚才被一个高个子法国人抽走了！']]);
        else await S.say('npc_fortune', returning ? '今晚的客人都好奇怪。' : '看相、算命、看风水～');
      } }),
      T.npc('npc_hk_passer_b', 'woman', 860, 158, { talk: async S => { await S.say('npc_hk_passer_b', F().kite ? '谢谢你们帮孩子取下风筝。' : '孩子的风筝挂到霓虹招牌上了……'); } }),
    ];
    st.hotspots = [
      hot('neon', 400, 60, '霓虹招牌', [], async (S, h, p) => sayBy(S, p, { jotaro: '……看不懂的字。原来是“当铺”。', _: '灯火通明的招牌。' }), async (S, h, p) => S.say(p.cid, '招牌在夜色里闪烁。')),
      hot('shopwindow', 230, 120, '橱窗倒影', ['detail'], async S => S.say(S.player.cid, '灯火映在玻璃上。'), async (S, h, p) => {
        F().polSeen = true;
        const view = T.show(S, { bg: 'hongkong_night', parts: [{ cid: 'polnareff', anim: 'idle', frame: 0, x: 180, y: 168, alpha: .45 }] });
        await S.say(p.cid, '……橱窗里，有个白头发的家伙一直跟着我们。'); view.close();
      }),
      hot('menu', 520, 120, '菜单板', [], async (S, h, p) => S.say(p.cid, '全是汉字。……我也只认得一半。'), async (S, h, p) => S.say(p.cid, '找老板点菜吧。')),
      hot('newsstand', 660, 150, '报摊电视', ['nensha'], async S => S.say(S.player.cid, '电视在放新闻：今日一架客机在香港外海迫降……'), async S => {
        await lines(S, [['joseph', '……剑？'], ['npc_hk_owner', '喂！我的电视！'], ['joseph', '……记在 SPW 财团的账上。']]);
      }, { cameraAt: { x: 660, y: 150 }, photo: { cid: 'chariot', anim: 'thrust', hold: 1.2 } }),
      hot('kite', 860, 70, '招牌上的风筝', ['reach'], async S => S.say(S.player.cid, '……够不着。这种事交给花京院。'), async S => {
        F().kite = true; const k = S.actor('kite_prop'); if (k) await S.arc(k, 860, 158, 8, .6);
        await S.say('npc_hk_passer_b', '咦，风筝自己掉下来了？谢谢！');
      }),
      hot('harbor', 940, 158, returning ? '往码头的路口' : '街道出口', [], async S => {
        if (returning) F().ch1Exit = true;
        else if (F().dinnerDone) F().garden = true;
        else await S.say(S.player.cid, '码头在那边。船要明天才开。先去大排档。');
      }, async S => S.say(S.player.cid, '沿着街道往右走。')),
    ];
    // 出口触发只在“会推进剧情”时生效：原来 once:false 且无条件，站在出口里每帧都重新触发，S.busy 一直为真，
    //   剧情的 until(flag && !busy) 永远等不到（真人停在右端就卡住，要走出去才继续）
    st.triggers = [
      { id: 'exit', x0: 936, x1: 960, y0: 140, y1: 180, once: false, cond: () => (returning ? !F().ch1Exit : !!F().dinnerDone && !F().garden),
        run: async () => { if (returning) F().ch1Exit = true; else F().garden = true; } },
      { id: 'exit_wait', x0: 930, x1: 960, y0: 140, y1: 180, once: true, cond: () => !returning && !F().dinnerDone,
        run: async S => { await S.say(S.player.cid, '码头在那边，船要明天才开。……先去大排档吃点东西。'); } },
    ];
    st.onLook = async (S, p) => sayBy(S, p, { jotaro: '……人太多，看不过来。', avdol: '这条街上的生命太多了……但有一个，冷冰冰地盯着我们。', joseph: '报摊那台电视看起来很好砸。', kakyoin: '上面好像挂着什么东西。', polnareff: '这里适合看剑的反光。' });
  }
  // 地图道具没有 type 时画不出来、也找不到角色：大排档两张桌（第二张会被烧成火焰时钟）、报摊电视、挂在招牌上的风筝
  function placeHongkongProps(S, returning) {
    T.prop(S, 'hk_table', 500, 164, { id: 'hk_table_a', frame: 0 });
    T.prop(S, 'hk_table', 548, 164, { id: 'hk_table_b', frame: 0 });
    T.prop(S, 'tv', 660, 152, { id: 'tv', frame: 0 });
    if (!F().kite) T.prop(S, 'kite', 860, 150, { id: 'kite_prop', z: 80, frame: 0 });
  }
  async function dinner(S) {
    if (F().dinnerDone) return;
    S.hint(null);
    // 众人围着两张大排档桌子（桌子 y 164 画在人前面，看起来像坐着）；波鲁纳雷夫从右边走到第二张桌旁。
    //   桌面、菜、烧成时钟的桌子都在画面下方，这一整段对话框放到上面，不然全被底部对话框挡住（名牌也在左下）
    const top = async rows => { for (const [who, text, expr] of rows) await S.say(who, text, Object.assign({ pos: 'top' }, expr ? { expr } : {})); };
    const seatsAt = { joseph: [492, 157, 1], kakyoin: [514, 155, 1], avdol: [538, 156, 1], jotaro: [470, 158, 1] };
    const owner = S.actor('owner');
    await Promise.all([
      ...Object.entries(seatsAt).map(([cid, [x, y]]) => { const a = S.actor(cid); if (!a) return null; a.follow = null; return S.walk(a, x, y, { speed: 120 }); }),
      owner ? S.walk(owner, 626, 158, { speed: 90 }) : null,
    ]);
    for (const [cid, [, , f]] of Object.entries(seatsAt)) { const a = S.actor(cid); if (a) a.facing = f; }
    if (owner) owner.facing = -1;
    await top([['npc_hk_owner', '几位？外面坐，凉快！今晚的叉烧刚出炉！'], ['joseph', '飞机是坐不了了。DIO 的刺客会连累一整架的乘客。'], ['avdol', '走海路？要多花好几天。'], ['joseph', '就像《八十天环游地球》！船和火车，一路往西！'], ['kakyoin', '五十天的期限，赶得上吗？'], ['joseph', '赶得上！……好，点菜就交给我！汉字嘛，看着长得差不多就行！']]);
    const choice = await S.choice(['指着第一行点', '挑最贵的点', '挑笔画最多的点', '全交给老板'], '乔瑟夫盯着菜单……');
    await top([['joseph', ['这行字看着很香！', '贵的一定好吃！', '笔画越多，菜越高级！', '老板，招牌菜全上！'][choice]]]);
    const pol = S.spawn('polnareff', 700, 158, { id: 'pol_intro' }); await S.walk(pol, 588, 158, { speed: 65 }); pol.facing = -1;
    await top([['polnareff', 'Excusez-moi～能帮我看看菜单吗？我一个字都看不懂。'], ['joseph', '哈哈！我也看不懂！一起点吧！']]);
    // 菜摆在第一张桌子的桌面上：纵深排在桌子前面（y 164.5），z 14 抬到桌面高度
    for (let i = 0; i < 3; i++) { T.prop(S, 'dish', 489 + i * 11, 164.5, { id: 'dish' + i, frame: i, z: 14 }); S.sfx('pop'); await S.wait(.15); }
    await top([['kakyoin', '……这是，青蛙？'], ['joseph', 'OH MY GOD!', 'shock'], ['polnareff', '哈哈哈！很有冒险精神嘛！作为谢礼——给各位看个小把戏。']]);
    const coins = [];
    for (let i = 0; i < 5; i++) { const a = T.prop(S, 'coin', 584, 158, { id: 'coin' + i, z: 30 }); coins.push(a); S.sfx('coin', { rate: 1 + i * .1 }); if (a) S.arc(a, 572 - i * 5, 158, 75, 1.4).catch(G.cancelIgnore); await S.wait(.227); }
    // 替身卡放到上方对话框下面（默认 y 40 正好被这一段放在上面的对话框盖住）
    await S.summon(pol, { card: { y: 100 } }); S.standAct(pol, 'thrust', { dx: -20, dur: .8 }); S.impact(['invert', 'blue']);
    coins.forEach((a, i) => { if (a) { a.x = 566 - i * 5; a.z = 38; a.script = null; } });
    await S.wait(.6); S.nameCard('polnareff');
    await top([['polnareff', '我的银色战车，剑术天下第一！'], ['avdol', '……你的剑尖，从刚才起就一直对着我。'], ['polnareff', '占卜师果然敏锐。DIO 大人说过，先收拾会喷火的那个。']]);
    coins.forEach(a => { if (a) a.remove = true; });
    // 火团画在两人中间（剑把火劈到桌上的位置）：原来 x 552 正好盖住阿布德尔的上半身
    await S.summon('avdol'); S.standAct('avdol', 'punch', { dur: .5 }); S.fx('fire_burst', { x: 566, y: 146, size: 20 });
    S.sfx('fire_burst'); S.sfx('slash', { seed: 0 }); S.sfxText('シュバッ', { x: 360, y: 210 });
    const table = S.actor('hk_table_b'); if (table) table.frozen = 1;
    await top([['polnareff', '瞧，火焰时钟。指针走到十二点之前——你会死在自己的火里。'], ['polnareff', '这里人太多了。去虎豹别墅吧，那里宽敞，适合决斗。']]);
    await S.walk(pol, 760, 158, { speed: 100 }); pol.remove = true;
    await top([['npc_hk_owner', '我、我的桌子！！'], ['joseph', '……记在 SPW 财团的账上。']]);
    if (G.party.rebuildFollow) G.party.rebuildFollow();
    F().dinnerDone = true; S.hint('往右走，去虎豹别墅。', 8);
  }
  // 虎像 → 红色魔术师石像：背景里画的是一只大虎像（x 17–68、y 84–116，底座到 y 132），道具 mr_statue 帧 0 的小老虎和它对不上，不用。
  //   雕刻时先在虎身上盖一块粗石（custom 道具，纵深 132：在所有走动的人后面），再把帧 1（24×40 的红色魔术师石像）立在底座上；碎了换帧 2。
  const garden = { carved: false };
  const STONE = ['#262634', '#58586a', '#6c6c82'];
  const tigerPatch = { type: 'custom', id: 'tiger_patch', x: 0, y: 0, depth: 132, cond: () => garden.carved, draw(g, ox, oy) {
    for (let y = 83; y <= 117; y++) {
      const j = ((y * 7) % 3) - 1;
      const l = 15 + Math.max(0, 89 - y) * 4 + (y > 110 ? j : 0), r = 70 - Math.max(0, 86 - y) * 2 + j;
      g.fillStyle = y <= 84 || y >= 117 ? STONE[0] : STONE[1]; g.fillRect(ox + l, oy + y, r - l + 1, 1);
      g.fillStyle = STONE[0]; g.fillRect(ox + l, oy + y, 1, 1); g.fillRect(ox + r, oy + y, 1, 1);
      if (y > 84 && y < 92) { g.fillStyle = STONE[2]; g.fillRect(ox + l + 2, oy + y, Math.max(0, (r - l) / 3) | 0, 1); }
    }
    g.fillStyle = STONE[0];   // 几道凿痕
    for (const [x, y, h] of [[24, 96, 6], [33, 101, 5], [61, 93, 7], [66, 104, 6]]) g.fillRect(ox + x, oy + y, 1, h);
  } };
  // 银色战车战的两样读招提示（地图像素层，只在 b02_chariot 里画）：
  //   ① 架剑光弧：他架剑时，替身身前一道银色竖弧、一点白光沿弧来回扫（剑在身前飞快地转）——“正面挡火”看得见；他出招 / 挨打时弧消失
  //   ② 石像诱饵（阶段 2、石像还没用过）：石像左边的站位处一个金色箭头 + 地上一排金点
  const SILVER = '#c8d8ff', GOLD = '#ffd83c', INK = '#2a1a00';
  function drawChariotView(P, ox, oy, t) {
    const W = G.world, fight = W.fight, px = G.px, K = G.KITS.e_polnareff;
    if (!fight || fight.id !== 'b02_chariot' || !px || !W.combat) return;
    const b = fight.boss;
    if (b && !b.remove && b.visible !== false && K && K.stanceUp && K.stanceUp(b)) {
      const s = b.stand, fc = b.facing || 1, sx = s && s.visible ? s.x : b.x;
      const cx = Math.round(sx + fc * 15 + ox), cy = Math.round(b.y - (s ? s.z : 0) - 28 + oy);
      const sweep = Math.sin(t * 9) * 1.15;
      for (let a = -1.3; a <= 1.3; a += 0.05) {
        const x = cx + Math.round(Math.cos(a) * 7 * fc), y = cy + Math.round(Math.sin(a) * 23), hot = Math.abs(a - sweep) < 0.24;
        px.plot(P, x, y, hot ? '#ffffff' : SILVER, hot ? 1 : 0.62);
        px.plot(P, x + fc, y, SILVER, hot ? 0.75 : 0.22);
      }
    }
    if (b && (b.phaseI || 0) === 1 && !b.mem.statueUsed && garden.carved) {
      const bob = Math.round(Math.sin(t * 6) * 2), ax = Math.round(34 + ox), ay = Math.round(100 + oy) + bob;
      px.poly(P, [[ax - 6, ay - 1], [ax + 6, ay - 1], [ax, ay + 7]], INK);
      px.poly(P, [[ax - 4, ay], [ax + 4, ay], [ax, ay + 5]], GOLD);
      const p = W.player, gy = Math.round((p ? p.y : 160) + 4 + oy);
      for (let x = 26; x <= 42; x += 2) px.plot(P, Math.round(x + ox), gy, GOLD, 0.35 + 0.3 * Math.max(0, Math.sin(t * 8 - x * 0.6)));
    }
  }
  function setupGarden() {
    const st = G.STAGES.hk_garden_ch1;
    garden.carved = false;
    st.props = [goalArrow('hk_garden_ch1', () => (F().duel ? null : { x: 200, y: 150 })), tigerPatch,
      { type: 'pixel', id: 'chariot_view', x: 0, y: 0, draw: drawChariotView }];
    st.npcs = [T.npc('polnareff', 'pol_garden', 200, 150, { standId: 'chariot', talk: async () => { F().duel = true; } })];
    st.hotspots = [['pagoda', 250, 104, '白塔', '七层塔。'], ['tiger', 44, 132, '虎像', '张着大嘴的老虎石像。'], ['lions', 90, 128, '金狮', '一对金狮子，镀金掉了一半。'], ['grotto', 160, 110, '彩绘假山洞', '洞里供着神像。']].map(([id, x, y, label, text]) => hot(id, x, y, label, [], async S => S.say(S.player.cid, text), async S => S.say(S.player.cid, text)));
    st.onLook = async (S, p) => S.say(p.cid, p.cid === 'avdol' ? '这里只有我们和他。……没有埋伏。' : '这里是一对一决斗的地方。');
  }
  async function chariot(S) {
    S.hint(null);
    // 对峙站位：波鲁纳雷夫留在原地（开战前一直看得见），阿布德尔走到他对面，其余三人退到右边石阶前观战（和战斗的 bench 位置一致）。
    //   观战的人站在场地（x ≤ 262）外面、前后错开：原来站在场地里（x 282–302），被逼到右边打的时候三个观众和三个波鲁纳雷夫挤成一团
    const intro = S.actor('pol_garden');
    if (intro) intro.facing = -1;
    const bench = { kakyoin: [276, 147], jotaro: [292, 142], joseph: [306, 151] };
    const spots = Object.assign({ avdol: [120, 152] }, bench);
    await Promise.all(Object.entries(spots).map(([cid, [x, y]]) => { const a = S.actor(cid); if (!a) return null; a.follow = null; return S.walk(a, x, y, { speed: 120 }); }));
    const av = S.actor('avdol'); if (av) av.facing = 1;
    ['jotaro', 'joseph', 'kakyoin'].forEach(cid => { const a = S.actor(cid); if (a) a.facing = -1; });
    await lines(S, [['polnareff', '来吧，占卜师。我们一对一。'], ['avdol', '乔斯达先生，请别插手。这是火与剑的较量。'], ['joseph', '……小心点。']]);
    await S.summon('avdol', { card: true });
    if (intro) intro.remove = true;   // 战斗里的波鲁纳雷夫在同一位置生成（VS 卡盖住替换）
    const tips = ['银边 + 剑竖在身前 = 架剑：正面的火会被劈开、拳会被弹开。按住 L 再按 J：地火从他脚下冒出来，架剑也挡不住。',
      '他头上冒「！」、往后拉剑的时候没在架剑：这时打他能打断。三连刺按 L 弹开任意一刺，他会僵住——连按 J 追击！',
      '突进刺会先拉红线：上下让开（K），他冲过头收不住剑，转身连按 J 打他。按住 L 挡三连刺只漏一点血。'];
    await S.fight({ id: 'b02_chariot', lead: 'avdol', swap: false, energy: { start: 0 }, arena: [14, 262], music: 'battle', vs: 'chariot', dmgScale: .8, finish: 'none', losable: true,   // 规划 .9：三连刺一套 21 伤太疼，.8
      onWave: async (s, wi, es, attempt, ctx) => {
        S.hint(attempt ? tips[(attempt - 1) % tips.length] : '他“架剑”（银边、剑竖在身前）时，正面的火会被劈开。按住 L 再按 J：从他脚下冒出地火！', 8);
        // 剑之结界以后他打不死，只剩攒能量放 Special：地火命中额外 +8 能量（规划“地火柱照样有效，用来攒能量”；原来一发只有 2，要 25 发）
        ctx.on('hit', ({ att, move }) => { if (att === ctx.player && move && move.fromGround && ctx.boss && ctx.boss.phaseI >= 3) G.combat.gainEnergy(att, 8, 'pillar'); });
        // 第一次弹开他的剑：告诉玩家这就是追击的时机（他会空 0.7 s 不举剑）
        ctx.on('parry', ({ who }) => { if (who === ctx.player && !ctx.data.punishTold && !(ctx.boss && ctx.boss.phaseI >= 3)) { ctx.data.punishTold = true; S.hint('弹开了！他僵住、剑也放下了——连按 J 打到第三下，继续按 J 接连打！', 5); } });
      },
      // 读招提示只各说一次：火第一次被劈开 / 拳第一次被弹开 / 血量第一次掉到 35% 以下
      tick: ctx => {
        const b = ctx.boss, p = ctx.player, d = ctx.data;
        if (!b || !p) return;
        const ph = b.phaseI || 0;
        if ((b.mem.cuts || 0) >= 1 && !d.cutTold && ph < 3) { d.cutTold = true; S.hint('火被劈开了！他架剑时别从正面放火：按住 L 再按 J 放地火，或者等他出招（头上冒「！」）时再打。', 8); }
        else if ((b.mem.parries || 0) >= 1 && !d.parryTold && ph < 3) { d.parryTold = true; S.hint('拳头被弹开了！架剑时正面打不进去。等他往后拉剑（「！」）时打断他，或者挡住三连刺再还手。', 8); }
        else if (p.hp <= p.maxHp * .35 && !d.lowTold) { d.lowTold = true; S.hint('撑住！三连刺按住 L 只漏一点血；看到红线就上下让开（K），他冲过头时转身打他。', 7); }
      },
      // 剑之结界（阶段 4）以后、能量满了才亮「按 U！」：之前按 U 放的是普通的十字火焰风暴（窗口外 combat 自动用本来的必杀）
      bench: { mode: 'stay', at: bench },
      // targetPick：地火、安卡认真身（原来按 x 找最近的敌人，脱甲后左右两个残像离得更近，地火总烧在残像脚下）
      kitOverride: { avdol: { targetPick: (a, c) => (c && c.boss) || null,
        special: { need: 100, prompt: '按 U！十字火焰风暴·Special', get title() { const f = G.world.fight; return f && f.boss && f.boss.phaseI >= 3 ? 'avdol_sp' : 'avdol'; },
        window: c => !!(c.boss && c.boss.phaseI >= 3 && c.player && c.player.energy >= 100),
        run: async (s, p, ctx, C) => {
          if (ctx.boss.phaseI >= 3) { await G.KITS.avdol.crossfireSp(p, C); ctx.end(); }
          else await G.KITS.avdol.special.run(p, C);
        } } } },
      // HP 规划写 900。旧版挨打马上又举剑、追击打不出来，按真人节奏要打 3 分钟以上，降到过 600；
      //   2026-10-09 晚改成“挨打 / 被弹开后空 0.7 s 再举剑”，追击一套能打 40–60，600 太快（测试打法 1 分钟），定 750（偏离规划 §5.2.3 的数值）
      waves: [[{ kit: 'e_polnareff', actor: 'polnareff', id: 'polnareff', x: 200, y: 150, hp: 750, poiseMax: 70, speed: 70, idle: 'fight', stand: 'chariot', boss: true, minHp: 1, koStyle: 'none', phases: [
        { at: .6, run: async (s, e, ctx) => {
          const statue = S.actor('mr_statue');
          // 不把石像角色交给 combat：它会按“击倒”把石像打飞淡出；碎掉只换成帧 2
          ctx.data.statue = { x: 44, y: 152, onBreak: () => { if (statue) statue.frozen = 2; s.sfx('glass_break'); s.fx('burst', { x: 44, y: 104, n: 14, speed: 90, gravity: 200, colours: ['#c8a070', '#8a6a48', '#e0c8a0'] }); } };
          s.fx('fire_burst', { x: 44, y: 100, size: 18 }); s.sfx('fire_burst');
          for (let i = 0; i < 6; i++) { s.fx('slash_arc', { x: 36 + (i % 3) * 8, y: 92 + (i % 2) * 12, size: 18 }); s.sfx('slash', { seed: i % 2 }); await s.wait(.18); }
          s.fx('dust', { x: 44, y: 116 }); s.sfxText('シュバババ', { x: 110, y: 170 });
          garden.carved = true; if (statue) { statue.frozen = 1; statue.visible = true; }
          await lines(s, [['polnareff', '瞧，你的替身像。'], ['avdol', '……雕得不错。']]); s.hint('站到石像左边（金色箭头处）：他的突进刺会先刺进石像，卡住的时候尽情打！', 8);
        } },
        { at: .4, run: async (s, e) => { s.sfx('armor_off'); s.fx('burst', { x: e.x, y: e.y - 30, n: 18, speed: 100, gravity: 160 }); await s.say('polnareff', '我的银色战车最快的样子，你还没见过！'); s.hint('他快了一倍，还多了两个残像：残像打不疼，脚下有影子的才是真身。', 7); } },
        { at: .2, set: { minHp: 1 }, run: async (s, e, ctx) => { s.fx('slash_arc', { x: e.x, y: e.y - 28, size: 28 }, { life: 2 }); await lines(s, [['polnareff', '你的火，一丝也进不来！'], ['avdol', '……那就不从正面进去。']]); s.hint('他再也不会倒下：用地火（按住 L 再按 J）攒满能量，按 U——十字火焰风暴·Special 从地底下烧他！', 10); } },
      ] }]],
      onRetry: async () => {
        garden.carved = false; const statue = S.actor('mr_statue'); if (statue) { statue.frozen = 0; statue.visible = false; statue.remove = false; }
        // 脱甲后的两个残影不归战斗管理，重来时不会被收走：上一次输在阶段 3 时，下一次一开场就是三个波鲁纳雷夫一起出招
        for (const a of G.world.stage.actors) if (a._cloneOf) a.remove = true;
      },
      testHint: ctx => {
        const b = ctx.boss, K = G.KITS.e_polnareff;
        return { phase: b ? b.phaseI + 1 : 1, stance: !!(b && K.stanceUp(b)), open: !!(b && G.clk.world - (b.mem.openAt == null ? -99 : b.mem.openAt) < K.openT),
          statueUsed: !!(b && b.mem.statueUsed), cuts: (b && b.mem.cuts) || 0, parries: (b && b.mem.parries) || 0 };
      },
    });
    S.impact(['invert', 'red']); S.flash(.16, .7); S.shake(6, .5);
    // 焦黑的波鲁纳雷夫出现在他被烧到的位置（原来写死 x 196，和爆炸的位置对不上）；之后跪地、站起来，全程都在画面里
    const pol = S.actor('polnareff');
    const px0 = pol ? G.clamp(pol.x, 40, 280) : 196, py0 = pol ? pol.y : 152, pf = pol ? pol.facing || -1 : -1;
    if (pol) { pol.visible = false; if (pol.stand && pol.stand.hide) pol.stand.hide(); }
    const char = T.prop(S, 'scene:s07_pol_char', px0, py0, { facing: pf });
    await S.wait(.5); if (char) S.pose(char, 'idle');
    // 战后这一段人都在画面下半（焦黑倒地、单膝跪地），对白一律放上面
    await linesTop(S, [['polnareff', '……从……地底下……？']]);
    // 僵住、晃两下、直挺挺倒下（分镜 s07 9.956–10.456 的喜剧停顿）
    if (char) {
      await S.animate(.5, k => { char.rot = Math.sin(k * Math.PI * 3) * .12 * k; });
      S.sfx('zoom'); await S.animate(.3, k => { char.rot = -pf * k * k * Math.PI / 2; });
      S.sfx('thud'); S.shake(3, .25); S.fx('dust', { x: px0 - pf * 20, y: py0 });
    }
    await linesTop(S, [['avdol', '十字火焰风暴·Special。你的剑再快，也切不到脚底下的火。'], ['polnareff', '你……一开始就算好了？']]);
    S.sfx('sting_comedy');
    await T.fullbody3(S, { cid: 'avdol', anim: 'yes', bg: 'radial', colours: ['#b85018', '#ffb044'], dur: 1.4 });
    S.sfxText('チッチッ', { x: 200, y: 140 });
    // 撑起上身：换成单膝跪地（scene:s07_pol_kneel），拔肉芽和雪莉的回忆都跪着说
    if (char) char.remove = true;
    const kneel = T.prop(S, 'scene:s07_pol_kneel', px0, py0, { facing: pf });
    if (!kneel && pol) { pol.visible = true; S.pose(pol, 'kneel'); }
    await linesTop(S, [['avdol', 'YES I AM!'], ['polnareff', '……我输了。输给这样的火，不丢人。'], ['avdol', '你的剑很干净。正因为这样，我才觉得奇怪。'], ['jotaro', '额头上。……又是那东西。']]);
    while (!await S.mash({ need: 6, time: 1.5, decay: 0, label: '这次简单多了——连按 J', y: 16 })) await linesTop(S, [['jotaro', '……稳住，再来。']]);
    S.impact('purple'); S.sfx('punch', { seed: 0 }); S.sfxText('ORA!', { x: 320, y: 150 }); await S.title('draw');
    S.music('sad'); S.sfx('heartbeat');
    // 回忆小窗放在左边、对话框下面（y 100），不和上方对话框重叠
    const memory = S.memory({ cid: 'jgeil', y: 100 });
    try { await linesTop(S, [['polnareff', '我妹妹雪莉，在下雨的回家路上……被一个男人害死了。'], ['polnareff', '唯一看见的人说，那个男人……两只手都是右手。'], ['polnareff', '我在找一个有两只右手的男人……他杀了我妹妹。'], ['polnareff', '后来我遇到了 DIO。他说他知道那个人在哪。……再后来，我就什么都不记得了。'], ['joseph', '跟我们走吧。DIO 身边，一定有那家伙的线索。'], ['jotaro', '……要来就来。']]); } finally { memory.close(); }
    // 站起来（战斗里架剑留下的银色描边一并去掉）
    if (kneel) kneel.remove = true;
    if (pol) { pol.visible = true; S.unpose(pol); pol.outline = null; pol.tint = null; pol.alpha = 1; pol.x = px0; pol.y = py0; pol.facing = pf; pol.play(pol.idleAnim || 'idle'); }
    await linesTop(S, [['polnareff', '……Merci。这把剑，借给你们。']]);
    if (pol) pol.remove = true;
    await S.join('polnareff', { notice: true }); S.music('travel');
  }
  G.STORY.ch1 = async S => {
    T.resetCounters(); S.party(crew, { leader: 'jotaro' });
    // 落海那场的 sea_day 背景登记在第2章的图包里；第1章开头先把它载进来，不然海面是一片空底
    await G.res.loadPack('bg_ch2');
    await S.chapterCard('ch1');
    await S.setStage('map_ch1', { x: 100, y: 160, music: 'travel' });
    await S.run(async s => { await s.route(['东京', '香港'], { vehicle: 'plane', day: 1, left: 50, cut: .6, view: { k: 1.9, x: 264, y: 66 } }); });
    setupPlane(); await S.setStage('plane_ch1', { x: 250, y: 160 }); planeTalks(S);
    await S.until(() => !S.busy && ((F().planeTalk || 0) >= 3 || S.player.x >= 560));
    await S.run(async s => { await tower(s); await crash(s); });
    setupHongkong(); await S.setStage('hk_street_ch1', { x: 80, y: 160 }); placeHongkongProps(S, false); S.location('hongkong');
    T.memberTalk({ joseph: s => s.say('joseph', '飞机是坐不得了。先吃饭，吃饱了再想办法！'), avdol: s => s.say('avdol', '香港的气很乱……人太多了。'), kakyoin: s => s.say('kakyoin', '要是来观光的就好了。') });
    S.hint('找大排档老板吃饭，然后沿街向右走。', 8);
    await S.until(() => F().garden && !S.busy);
    setupGarden(); await S.setStage('hk_garden_ch1', { x: 100, y: 160 });
    // 站在背景虎像的底座上（脚点 y 133 在所有走动的人后面，z 17 画到底座顶 y 116）；雕刻前不显示
    const statue = T.prop(S, 'mr_statue', 44, 133, { id: 'mr_statue', frame: 0, z: 17 }); if (statue) statue.visible = false;
    S.hint('与波鲁纳雷夫交谈，开始一对一决斗。', 8);
    await S.until(() => F().duel && !S.busy); await S.run(chariot);
    S.party(crew.concat('polnareff'), { leader: 'polnareff' });
    setupHongkong(true); await S.setStage('hk_street_ch1b', { x: 80, y: 160 }); placeHongkongProps(S, true);
    T.memberTalk({ polnareff: s => s.say('polnareff', '明天坐船？好啊，船上的女孩子……咳，我是说，船很好。') });
    S.hint('五名队长都可自由切换。向右走到码头。', 8);
    await S.until(() => F().ch1Exit && !S.busy);
    await S.run(async s => {
      // 五人并肩走进霓虹街：排成一行（间距 24 px）从画面中间往右走，边走边出旁白（原来五人挤在 x 870–918 的屏幕右缘叠成一团）
      const actors = crew.concat('polnareff').map(cid => s.actor(cid)).filter(Boolean);
      actors.forEach((a, i) => { a.follow = null; a.x = 700 + i * 24; a.y = 166 + (i % 2) * 6; a.facing = 1; });   // 走在前排（y ≥ 166），不被街边 NPC 挡住
      G.world.stage.camTarget = 660;
      const walking = Promise.all(actors.map(a => s.walk(a, a.x + 110, a.y, { speed: 30 })));
      await s.narrate('第二天，一行人登上了 SPW 财团安排的船，驶向新加坡。');
      await walking;
      await s.tbc(); s.mark('ch1_tbc');
    });
  };
  // 开发调参入口（只给 tools\dev\full\dev_chariot.py 用，正常游戏不调用、不在章节表里）：直接在虎豹别墅开打银色战车，
  //   战斗本身走和正式剧情同一个 chariot()；验收一律跑整章（test_ch1.py），这个入口的结果不当通关证据
  G.DEV = G.DEV || {};
  G.DEV.ch1Chariot = async S => {
    T.resetCounters(); S.party(crew, { leader: 'avdol' });
    setupGarden(); await S.setStage('hk_garden_ch1', { x: 100, y: 160, music: 'tension' });
    const statue = T.prop(S, 'mr_statue', 44, 133, { id: 'mr_statue', frame: 0, z: 17 }); if (statue) statue.visible = false;
    await S.run(chariot);
  };
})();
