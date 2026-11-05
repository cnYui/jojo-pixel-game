// 第3章　海边别墅 / 由花子与意大利菜（G.STORY.ch3，地图后缀 _ch3；开发脚本 第四部/docs/第3章_开发脚本.md）。整章流程：
//   节拍 1 篇章卡 → 日历地图（两枚新图钉 + 红章 1999年5月）→ 2 放学后的教室（告白、亿泰被头发吊起来、爱的豪华）
//   → 3 第二天自由走动（教室 → 走廊尽头的由花子）→ 4 康一不见了 → 5 海边别墅（电椅）→ 第5战段 1 逃脱
//   → 6 门把电由花子、回音 ACT2 → 段 2 别墅 → 7 别墅区（仗助 / 亿泰找「呜呜」）→ 段 3 海岬 → 8 啪嘤岬
//   → 9 英语笔记 → 10 意大利餐厅 → 11 小游戏 东尼欧的晚餐（四道菜）→ 12 电视雪花 → To Be Continued
//   克制：电椅只是绕着电线的椅子，由花子被电只是头发炸起来；悬崖只给剪影；亿泰的毛病全是卡通式（眼泪喷泉、搓泥、蛀牙飞出去、脚气冒烟）。
//   战斗和小游戏在 story/p4_ch3_fights.js（G.P4CH3）。
'use strict';
(function () {
  const G = window.G;
  const T = () => G.TPL;
  const P4 = () => G.P4;
  const C3 = () => G.P4CH3;
  const F = () => G.P4CH3.F;
  const now = () => (G.clk ? G.clk.world : 0);
  const NAME_TOP = 100;
  const { base, walls } = G.p4Stage;
  const ST = G.STAGES;

  Object.assign(G.NAMES, { yukako: '由花子', tonio: '东尼欧', echoes2: '回音', pearljam: '珍珠果酱', okuyasu: '亿泰', echoes1: '回音' });

  // ================================================================ 地图
  ST.map_ch3 = base('map_ch3', 'morioh_map', 320, { yMin: 160, yMax: 170, music: null, obstacles: [] });
  ST.class_ch3 = base('class_ch3', 'budogaoka_classroom', 320, { obstacles: walls(8, 312, 320) });
  ST.hall_ch3 = base('hall_ch3', 'budogaoka_hall', 640);
  ST.villa_ch3 = base('villa_ch3', 'seaside_villa', 640, {
    music: 'tension', state: { shoebox: 0, chair: 0, hair_walls: 0, hair_door: 0, hair_stairs: 0, hair_window: 0 },
  });
  ST.villa_out_ch3 = base('villa_out_ch3', 'seaside_villa_out', 640, { music: 'tension' });
  ST.cape_ch3 = base('cape_ch3', 'cape_cliff', 320, { music: 'tension', obstacles: walls(8, 234, 320) });
  ST.trattoria_ch3 = base('trattoria_ch3', 'trattoria', 480);
  ST.kitchen_ch3 = base('kitchen_ch3', 'trattoria_kitchen', 480);
  ST.living_ch3 = base('living_ch3', 'higashikata_living', 480, { music: null, state: { fog: 0 }, obstacles: walls(10, 470, 480) });

  // ================================================================ 小工具（写法同序章）
  const pool = (cid) => G.party._actor(cid);
  function place(S, cid, x, y, facing, o = {}) {
    const a = pool(cid), W = G.world;
    Object.assign(a, { x, y, z: 0, facing: facing || 1, follow: null, hold: false, script: null, state: 'idle', remove: false, rot: 0, alpha: 1, tint: null });
    a.visible = o.visible !== false;
    if (W.player !== a) a.team = 'npc';
    a.play(a.idleAnim || 'idle');
    W.stage.add(a);
    return a;
  }
  const focus = (o) => { G.world.focus = o; };
  const snapTo = (o) => { G.world.focus = o; G.world.snapCamera(); };
  const koichi = () => C3().koichiGear(pool('koichi'), 1);

  // ================================================================ 节拍 1 日历地图（第3章自己的红章「1999年5月」，序章的两枚图钉变灰）
  const PINS_OLD = [[170, 70], [118, 126]];
  const PINS_NEW = [{ xy: [266, 136], label: '海边别墅' }, { xy: [146, 98], label: '意大利餐厅' }];
  async function calendar(S) {
    const ui = (G.D && G.D.ui) || {}, m = ui.map || {}, m3 = ui.map_ch3 || {};
    const img = (k) => { const im = k ? G.image(k) : null; return im && G.ready(im) ? im : null; };
    const ease = (u) => 1 - Math.pow(1 - Math.max(0, Math.min(1, u)), 3);
    const pins = PINS_NEW.map((p, i) => Object.assign({ t0: 0.5 + i * 0.45 }, p));
    const stampAt = 0.5 + pins.length * 0.45 + 0.25;
    const pin = (g, xy, im, dy) => {
      if (!im) return;
      const meta = m.pin || { ax: 5, ay: 15 };
      g.drawImage(im, Math.round(xy[0] * 2 - meta.ax * 2), Math.round(xy[1] * 2 - meta.ay * 2 + (dy || 0)), im.width * 2, im.height * 2);
    };
    const h = P4().overlay((g, t) => {
      for (const xy of PINS_OLD) pin(g, xy, img(m.pin_gray && m.pin_gray.image));
      for (const q of pins) {
        const u = (t - q.t0) / 0.3;
        if (u < 0) continue;
        const dy = u < 1 ? -60 * (1 - ease(u)) : u < 1.4 ? -Math.round(Math.sin((u - 1) / 0.4 * Math.PI) * 6) : 0;
        pin(g, q.xy, img(m.pin && m.pin.image), dy);
        if (u >= 1) P4().text(g, q.label, Math.round(q.xy[0] * 2 + 12), Math.round(q.xy[1] * 2 - 34), '#fff4d6', 12, 'left', '#2a0a1a');
      }
      if (t >= stampAt) {
        const sm = m3.stamp, sim = sm && img(sm.image);
        if (sim) {
          const u = Math.min(1, (t - stampAt) / 0.14), sc = 1.9 - 0.9 * ease(u);
          const w = Math.round(sm.w * sc), hh = Math.round(sm.h * sc);
          g.save(); g.globalAlpha = Math.min(1, u * 2); g.drawImage(sim, Math.round(534 - w / 2), Math.round(262 - hh / 2), w, hh); g.restore();
        }
      }
      const pl = m.place, plim = pl && img(pl.image);
      if (plim) g.drawImage(plim, 640 - pl.w - 14, 12);
    }, { z: 1 });
    for (const q of pins) G.defer(q.t0 + 0.3, () => { S.sfx('pop', 0.7); S.sfx('thud', 0.4); }, 'ui');
    G.defer(stampAt, () => { S.sfx('thud', 1); S.sfx('card_flip', 0.6); S.shake(2, 0.2); }, 'ui');
    await S.wait(stampAt + 1.8, 'ui');
    return h;
  }
  async function beatCalendar(S) {
    S.player.visible = false;
    await S.setStage('map_ch3', { x: 160, y: 165, music: null });
    const h = await calendar(S);
    S.mark('ch3_calendar');
    await S.fadeOut(0.45);
    h.close();
  }

  // ================================================================ 节拍 2 放学后的教室：告白、亿泰被头发吊起来
  async function beatConfess(S) {
    S.party(['koichi'], { leader: 'koichi' });
    const p = koichi();
    await S.setStage('class_ch3', { x: 200, y: 158, facing: -1, music: 'daily', fade: false });
    p.visible = true;
    snapTo({ x: 160 });
    await S.fadeIn(0.6);
    await S.narrate('五月。我在学校里，第一次被女生叫住。', { pos: 'top' });
    const yk = S.spawn('yukako', -10, 158, { id: 'yukako', facing: 1, name: '山岸由花子' });
    await S.walk(yk, 120, 158, { speed: 46 });
    S.face(p, -1);
    await S.say('yukako', '广濑康一君。……可以占用你一点时间吗？');
    S.nameCard('yukako', { y: NAME_TOP });
    await S.say('koichi', '诶？我、我吗？', { expr: 'shock' });
    await S.say('yukako', '我注意你很久了。你在走廊上说话的声音，我一句都没漏过。', { expr: 'smile' });
    yk.play('blush');
    await S.say('koichi', '（这、这是……告白？！）', { expr: 'smile' });
    await S.say('yukako', '我想和你在一起。从今天起，我会把你照顾好的。', { expr: 'smile' });
    await S.say('koichi', '那个……能先从朋友做起吗？');
    yk.play('idle');
    await S.say('yukako', '朋友？……也好。那明天的便当我来做。你喜欢吃什么，我都知道。');
    S.mark('ch3_confess');
    await S.say('koichi', '（……都、都知道？）', { expr: 'shock' });
    await S.walk(yk, -20, 158, { speed: 50 });
    yk.visible = false;
    // 仗助、亿泰从窗边探头
    const js = place(S, 'josuke', 300, 150, -1), ok = place(S, 'okuyasu', 318, 160, -1);
    await Promise.all([S.walk(js, 238, 150, { speed: 60 }), S.walk(ok, 258, 162, { speed: 60 })]);
    S.face(p, 1);
    await S.say('okuyasu', '哟～康一，艳福不浅啊！', { expr: 'smile' });
    await S.say('josuke', '可那个女生……眼神有点不对劲。');
    await S.say('okuyasu', '交给我。她要是觉得康一不怎么样，自己就会走了吧？');
    // 两人故意走到门口大声说
    await Promise.all([S.walk(js, 70, 152, { speed: 70 }), S.walk(ok, 46, 160, { speed: 70 })]);
    S.face(js, -1); S.face(ok, -1);
    await S.say('okuyasu', '康一那家伙，矮、没胆、还尿过床！', { expr: 'smile' });
    await S.say('josuke', '对对，考试全靠蒙！', { expr: 'smile' });
    // 门“咣”地打开：由花子站在门口，长发像活的一样竖起来，一缕勾住亿泰的领子吊到半空
    yk.visible = true; yk.x = 14; yk.y = 158; yk.facing = 1;
    S.sfx('door', 0.9); S.sfx('sting_shock', 0.8);
    S.sfxText('咣', { wx: 14, wy: 120, wz: 0 }, { dur: 0.7 });
    yk.play('cmd');
    S.fx('wrap', { x: ok.x, y: ok.y, h: 30, w: 12, n: 4, kind: 'tendril', colour: '#1a1024' }, { life: 1.6, follow: ok });
    S.pose(ok, 'hurt');
    await S.animate(0.5, (k) => { ok.z = Math.round(26 * k); });
    S.mark('ch3_hair_lift');
    await S.say('yukako', '谁准你们说康一君的坏话？', { expr: 'rage' });
    S.standCard('lovedeluxe', { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.wait(1.0);
    await S.say('okuyasu', '头、头发？！', { expr: 'shock' });
    // 发丝一松，摔在地上
    await S.animate(0.18, (k) => { ok.z = Math.round(26 * (1 - k)); });
    S.pose(ok, 'down');
    S.sfx('thud', 0.9); S.shake(2, 0.2);
    yk.play('idle');
    await S.wait(0.4);
    await S.say('yukako', '康一君，明天见。', { expr: 'smile' });
    await S.walk(yk, -24, 158, { speed: 50 });
    yk.remove = true;
    S.unpose(ok);
    await S.say('josuke', '……这下麻烦了。');
    await S.fadeOut(0.6);
  }

  // ================================================================ 节拍 3 第二天：自由走动（教室 → 走廊尽头的由花子）
  const KO_TOLD = '（康一的回音能听见墙后的声音：Q 换成康一按 U）';
  async function useBento(S) {
    F().bento = true;
    S.mark('ch3_bento');
    await S.say(null, '便当盒上贴着纸条：『给康一君。全部吃完哦。』');
    await S.say('koichi', '……什么时候放的？', { expr: 'shock' });
  }
  function setupSchoolFree(S) {
    const st = G.world.stage;
    T().prop(S, 'bento', 189, 149, { id: 'bento', frame: 0, z: 32 });
    st.hotspots.push(
      { id: 'desk', x: 189, y: 152, r: 20, label: '康一的课桌', tags: ['erase'], use: useBento,
        look: async (S2, h, p) => {
          if (p.cid !== 'okuyasu') return;
          await S2.say('okuyasu', '这便当……要不我削掉它？');
          await S2.say('koichi', '不行！会被杀掉的！', { expr: 'shock' });
        } },
      { id: 'blackboard', x: 64, y: 150, r: 22, label: '黑板', use: async (S2) => { await S2.say(null, '值日表上，康一的名字旁边被人画了一颗小小的心。'); } },
      { id: 'lockers', x: 220, y: 150, r: 18, label: '储物柜', tags: ['fix'],
        use: async (S2) => { await S2.say(null, '康一的柜门关不严，像是被人撬过。'); },
        look: async (S2, h, p) => {
          if (p.cid !== 'josuke') return;
          F().locker = true;
          await S2.say('josuke', '……锁被弄坏了。谁撬了康一的柜子？');
        } },
      { id: 'window2', x: 270, y: 150, r: 18, label: '窗户', tags: ['listen', 'sound'],
        use: async (S2) => { await S2.say(null, '窗外的树叶在晃。'); },
        look: async (S2, h, p) => {
          if (p.cid !== 'koichi') return;
          F().wind = true;
          S2.sfx('wind', 0.4);
          await S2.say(null, '……沙沙。沙沙。');
          await S2.say(null, '窗外的树上，有头发一样的东西缠着。');
          await S2.say('koichi', '……我什么都没看见。', { expr: 'shock' });
        } },
    );
    st.triggers.push({ x0: -20, x1: 18, run: async () => { F().toHall = true; } });
    T().memberTalk({
      josuke: async (S2) => { await S2.say('josuke', '那个女生……在走廊那头吧。去问问清楚？'); },
      okuyasu: async (S2) => { await S2.say('okuyasu', '便当诶，我还没吃过女生做的便当……', { expr: 'smile' }); },
    });
    T().goal(S, { x: 14, y: 158, label: '走廊', delay: 40, every: 15, done: () => !!F().toHall, text: '去走廊（教室左边的门）' });
  }
  async function talkYukako(S, me) {
    const n = F().yTalk = (F().yTalk || 0) + 1;
    if (n === 1) await T().say(S, me, '康一君，便当好吃吗？', { expr: 'smile' });
    else if (n === 2) await T().say(S, me, '下午的数学，你有两道题空着呢。');
    else {
      await T().say(S, me, '我说了，我会把你照顾好的。', { expr: 'rage' });
      S.mark('ch3_stare');
      await S.say('koichi', '（……她一直盯着我。）', { expr: 'shock' });
      F().stare = true;
    }
  }
  function setupHallFree(S) {
    const st = G.world.stage;
    const yk = S.spawn('yukako', 60, 154, { id: 'yukako', facing: 1, name: '山岸由花子' });
    yk.talk = talkYukako; yk.label = '山岸由花子';
    st.hotspots.push({ id: 'yk_listen', x: 60, y: 154, r: 30, label: '由花子', tags: ['listen', 'sound'],
      look: async (S2, h, p) => {
        if (p.cid !== 'koichi') return;
        S2.sfx('heartbeat', 0.4);
        await S2.say(null, '……康一君、康一君、康一君……');
        await S2.say('koichi', '她一直在小声念我的名字……', { expr: 'shock' });
      } });
    T().goal(S, { x: 60, y: 154, label: '由花子', delay: 60, every: 15, done: () => !!F().stare, text: '走廊尽头站着由花子：走过去按 E' });
  }

  // ================================================================ 节拍 4 康一不见了
  async function beatMissing(S) {
    T().memberTalk({});
    await S.fadeOut(0.5);
    await S.narrate('那天放学，她说要请我去一个安静的地方补课。', { pos: 'top' });
    await S.narrate('然后，我什么都不记得了。', { pos: 'top' });
    S.party(['josuke', 'okuyasu'], { leader: 'josuke' });
    await S.setStage('class_ch3', { x: 160, y: 156, facing: -1, music: 'tension', fade: false });
    const ok = S.actor('okuyasu');
    if (ok) Object.assign(ok, { x: 210, y: 162, follow: null, facing: -1 });
    snapTo({ x: 160 });
    await S.fadeIn(0.5);
    await S.say('josuke', '康一没来？');
    await S.say('okuyasu', '他妈妈打电话问，是不是住在你家……', { expr: 'shock' });
    await S.say('josuke', '那个长发的女生也没来。');
    S.face(S.player, 1);
    if (ok) S.face(ok, -1);
    S.mark('ch3_missing');
    await S.wait(0.8);
    await S.fadeOut(0.6);
    focus(null);
  }

  // ================================================================ 节拍 5 海边别墅（电椅）
  async function beatVilla(S) {
    S.party(['koichi'], { leader: 'koichi' });
    const p = koichi();
    await S.setStage('villa_ch3', { x: 548, y: 156, facing: -1, music: 'tension', fade: false });
    T().prop(S, 'echair', 535, 141, { id: 'vl_chair0' });
    S.pose(p, 'down');
    snapTo({ x: 500 });
    await S.fadeIn(0.8);
    S.location('villa', { y: NAME_TOP });
    await S.wait(0.6);
    S.unpose(p);
    S.face(p, -1);
    S.mark('ch3_villa');
    const yk = S.spawn('yukako', 400, 156, { id: 'yukako', facing: 1, name: '山岸由花子' });
    await S.walk(yk, 500, 156, { speed: 40 });
    await S.say('yukako', '醒了？饭做好了。吃完就开始学习吧。', { expr: 'smile' });
    await S.say('yukako', '这把椅子是给你学习用的。答错一题，就会麻一下。');
    S.fx('lightning', { x0: 528, y0: 104, x1: 542, y1: 136, colour: '#fff4a0' }, { life: 0.3 });
    S.sfx('crossfire', 0.5);
    await S.say('koichi', '这、这是绑架吧！', { expr: 'shock' });
    await S.say('yukako', '我是在帮你。你会变成配得上我的人。', { expr: 'smile' });
    await S.say('yukako', '我去订橄榄油，一会儿就回来。你乖乖把这一页写完。');
    await S.walk(yk, 40, 156, { speed: 70 });
    S.sfx('door', 0.8);
    yk.remove = true;
    S.sfx('clang', 0.6);
    S.sfxText('咔嚓', { wx: 57, wy: 110, wz: 0 }, { dur: 0.7 });
    const c0 = S.actor('vl_chair0');
    if (c0) c0.remove = true;
    focus(null);
  }

  // ================================================================ 节拍 6 门把电由花子 → 回音 ACT2
  async function beatKnob(S) {
    const p = S.player;
    S.hint(null);
    focus({ x: 200 });
    S.sfx('footstep0', 0.6);
    await S.wait(0.4); S.sfx('footstep1', 0.7); await S.wait(0.4); S.sfx('footstep2', 0.8);
    await S.say('koichi', '（脚步声……她回来了！）', { expr: 'shock' });
    // 握住门把：电线连着门把，「滋啦」一声，头发全炸起来
    S.sfx('crossfire', 0.9);
    S.fx('lightning', { x0: 57, y0: 70, x1: 57, y1: 112, colour: '#fff4a0' }, { life: 0.5 });
    S.flash(0.12, 0.6, '#fff4a0');
    S.sfxText('滋啦！', { wx: 57, wy: 96, wz: 0 }, { dur: 1.0 });
    S.shake(3, 0.4);
    S.mark('ch3_knob');
    await S.wait(0.6);
    await S.say('yukako', '……康一君。你居然想逃？', { expr: 'rage' });
    // 头发从门缝钻进来，缠住康一的头，把他拖到门口
    S.state('hair_walls', 1);
    S.sfx('slime', 0.9);
    S.fx('wrap', { x: p.x, y: p.y, h: 30, w: 12, n: 4, kind: 'tendril', colour: '#1a1024' }, { life: 1.6, follow: p });
    S.pose(p, 'hurt');
    await S.animate(0.8, (k) => { p.x = G.lerp(p.x, 170, k * 0.35); });
    p.x = 170;
    for (const id of ['vl_shoe', 'vl_chair']) { const a = S.actor(id); if (a) { S.sfx('crash', 0.7); await S.arc(a, a.x + 60, 168, 12, 0.35, { spin: 1 }); } }
    S.state('hair_door', 1);
    const yk = S.spawn('yukako', 60, 156, { id: 'yukako', facing: 1, name: '山岸由花子' });
    yk.play('cmd');
    S.sfx('sting_shock', 0.7);
    await S.wait(0.5);
    S.unpose(p);
    S.face(p, -1);
    // 回音 ACT1 缩成一团、壳裂开
    const e1 = S.spawn(C3().ECH1(), p.x - 16, 158, { id: 'e1_shell', facing: -1 });
    e1.z = 6;
    e1.play('hatch');
    S.sfx('glass_break', 0.6);
    S.fx('crack', { x: e1.x, y: e1.y - 14, size: 10 }, { life: 1.2 });
    await S.say('koichi', '回音……你别死！', { expr: 'shock' });
    S.flash(0.2, 0.8, '#f4ffd0');
    S.sfx('power_up', 0.9);
    await S.animate(0.4, (k) => { e1.alpha = 1 - k; });
    e1.remove = true;
    C3().koichiGear(p, 2);
    await S.summon(p, { dur: 0.3, rise: 8, card: { y: NAME_TOP } });
    S.mark('ch3_act2');
    await S.say('koichi', '……不是死了。是长大了！');
    yk.play('idle');
    S.music('battle', 0.3);
    await S.vs({ key: 'lovedeluxe', hero: 'koichi', enemy: { cid: 'yukako', anim: 'cmd' } });
    G.uifx.vsTag('lovedeluxe');
    focus(null);
  }
  async function afterLoveDeluxe(S) {
    const p = S.player, yk = S.actor('yukako');
    S.hint(null);
    if (yk) { yk.team = 'npc'; yk.brain = null; yk.atk = null; yk.tele = null; S.pose(yk, 'hurt'); }
    await S.say('yukako', '康一君……为什么不明白我的心意！', { expr: 'rage' });
    await S.say('koichi', '……趁现在！', { expr: 'shock' });
    S.sfx('crash', 0.9); S.sfx('glass_break', 0.8); S.shake(4, 0.4);
    S.fx('burst', { x: 607, y: 100, n: 16, speed: 40, colours: ['#d8f0ff', '#a0c8e0'], gravity: 140, life: 0.8 }, { life: 1 });
    await S.walk(p, 620, 156, { speed: 120, anim: 'walk' });
    await S.fadeOut(0.5);
    focus(null);
  }

  // ================================================================ 节拍 7 别墅区（仗助 / 亿泰）：电话亭、邮箱、「呜呜」
  function setupVillaOut(S) {
    const st = G.world.stage;
    st.hotspots.push(
      { id: 'booth', x: 513, y: 150, r: 20, label: '电话亭', use: async (S2) => {
        F().booth = true;
        await S2.say(null, '听筒还挂在外面晃。');
        await S2.say('okuyasu', '这么远……他是怎么拨的号？', { expr: 'shock' });
      } },
      { id: 'mailbox', x: 135, y: 152, r: 16, label: '邮箱', use: async (S2) => { F().mailbox = true; await S2.say(null, '门牌：山岸。'); } },
      { id: 'gate', x: 170, y: 152, r: 18, label: '铁门', tags: ['fix'],
        use: async (S2) => { await S2.say(null, '铁门的栏杆往外弯着。'); },
        look: async (S2, h, p) => { if (p.cid !== 'josuke') return; await S2.say('josuke', '……是从里面撑开的。'); } },
      { id: 'villa', x: 230, y: 150, r: 24, label: '别墅', tags: ['erase', 'pull'],
        look: async (S2, h, p) => { if (p.cid !== 'okuyasu') return; await S2.say('okuyasu', '我把门口这段空间削掉，一步就过去了！', { expr: 'smile' }); await S2.say('josuke', '……先找到康一在哪间屋再说。'); } },
      { id: 'villa_window', x: 103, y: 152, r: 20, label: '别墅的窗', use: findWuwu },
    );
    T().memberTalk({ okuyasu: async (S2) => { await S2.say('okuyasu', '康一那小子，可别出什么事啊……'); } });
    T().goal(S, { x: 103, y: 152, label: '窗', delay: 40, every: 15, done: () => !!F().wuwu, text: '别墅的窗上贴着什么……走过去按 E' });
  }
  async function findWuwu(S2) {
    if (F().wuwu) return;
    F().wuwu = true;
    S2.sfx('blip', 0.8, 0.7);
    S2.sfxText('呜呜……', { wx: 103, wy: 72, wz: 0 }, { dur: 1.6 });
    await S2.say(null, '墙上贴着一个哭脸一样的字「呜呜……」，一碰就响。');
    S2.mark('ch3_wuwu');
    await S2.say('josuke', '是康一的字！他就在这栋！', { expr: 'shock' });
  }
  async function villaOutIn(S) {
    S.party(['josuke', 'okuyasu'], { leader: 'josuke' });
    await S.setStage('villa_out_ch3', { x: 24, y: 160, facing: 1, music: 'tension', fade: false });
    S.player.visible = true;
    await S.fadeIn(0.5);
    S.mark('ch3_out');
    await S.say('josuke', '康一的电话是从这一带打来的。');
    await S.say('okuyasu', '电话亭就在前面！');
    S.hint('E 调查　U 替身调查　Q 换队长', 6);
  }
  async function windowBurst(S) {
    const p = S.player;
    T().memberTalk({});
    S.sfx('crash', 1); S.sfx('glass_break', 0.9); S.shake(4, 0.4);
    S.fx('burst', { x: 103, y: 70, n: 18, speed: 46, colours: ['#d8f0ff', '#a0c8e0'], gravity: 140, life: 0.8 }, { life: 1 });
    const ko = place(S, 'koichi', 100, 156, 1), yk = S.spawn('yukako', 70, 156, { id: 'yk_run', facing: 1, skin: 'grey', name: '山岸由花子' });
    yk.skin = 'grey';
    S.walk(ko, 700, 156, { speed: 130 }).catch(G.cancelIgnore);
    await S.wait(0.3);
    S.walk(yk, 700, 158, { speed: 120 }).catch(G.cancelIgnore);
    await S.say('josuke', '康一！……往海岬那边跑了！', { expr: 'shock' });
    await S.say('okuyasu', '后面那个……头发怎么变色了？！', { expr: 'shock' });
    await S.fadeOut(0.5);
    ko.remove = false;
  }

  // ================================================================ 节拍 8 海岬（段 3 在 fights）→ 啪嘤岬
  async function capeIn(S) {
    S.party(['koichi'], { leader: 'koichi' });
    const p = C3().koichiGear(pool('koichi'), 2);
    await S.setStage('cape_ch3', { x: 120, y: 160, facing: 1, music: 'tension', fade: false });
    p.visible = true;
    const yk = S.spawn('yukako', 196, 158, { id: 'yukako', facing: -1, name: '山岸由花子' });
    yk.skin = 'white';
    G.world.snapCamera();
    await S.fadeIn(0.5);
    await S.say('yukako', '……跑不掉的。康一君。', { expr: 'wnormal' });
  }
  async function afterCape(S) {
    const p = S.player, yk = S.actor('yukako');
    if (yk) { S.unpose(yk); yk.skin = 'white'; S.face(yk, p); }
    S.recall(p);
    await S.say('yukako', '……为什么救我？', { expr: 'wshock' });
    S.face(p, yk);
    await S.say('koichi', '你一次也没有听我说过话。');
    S.face(p, -1);
    S.walk(p, 30, 162, { speed: 40 }).catch(G.cancelIgnore);
    S.mark('ch3_walkaway');
    const js = place(S, 'josuke', -20, 156, 1), ok = place(S, 'okuyasu', -40, 164, 1);
    await Promise.all([S.walk(js, 70, 156, { speed: 90 }), S.walk(ok, 52, 164, { speed: 90 })]);
    await S.say('okuyasu', '她的头发怎么白了？！', { expr: 'shock' });
    S.music('daily', 1.0);
    await S.narrate('后来，渔民们说看见一个女孩从崖下弹了回来。', { pos: 'top' });
    await S.narrate('那里从此被叫作“啪嘤岬”。', { pos: 'top' });
    await S.fadeOut(0.8);
  }

  // ================================================================ 节拍 9 几天后：英语笔记
  async function beatNotes(S) {
    S.party(['koichi', 'josuke'], { leader: 'koichi' });
    const p = C3().koichiGear(pool('koichi'), 2);
    await S.setStage('class_ch3', { x: 200, y: 158, facing: -1, music: 'daily', fade: false });
    p.visible = true;
    const js = S.actor('josuke');
    if (js) Object.assign(js, { x: 236, y: 152, follow: null, facing: -1 });
    T().prop(S, 'notebook', 189, 149, { id: 'notebook', z: 32 });
    snapTo({ x: 170 });
    await S.fadeIn(0.5);
    await S.say(null, '康一的桌上放着一本笔记，封面写「英语·满分笔记 由花子」。');
    S.mark('ch3_notes');
    await S.say('koichi', '……这是什么意思啊。', { expr: 'shock' });
    await S.say('josuke', '意思是，她还没放弃。', { expr: 'smile' });
    await S.fadeOut(0.6);
    focus(null);
  }

  // ================================================================ 节拍 10 意大利餐厅 → 节拍 11 小游戏
  const TR = { table: 228, seat: 198, seat2: 268 };
  async function trattoriaIn(S) {
    S.party(['josuke', 'okuyasu'], { leader: 'josuke' });
    await S.setStage('trattoria_ch3', { x: 40, y: 158, facing: 1, music: 'daily', fade: false });
    const p = S.player, ok = S.actor('okuyasu');
    p.visible = true;
    if (ok) Object.assign(ok, { x: 20, y: 164, follow: null, facing: 1 });
    G.world.snapCamera();
    await S.fadeIn(0.5);
    S.location('trattoria', { y: NAME_TOP });
    if (ok) await S.walk(ok, 120, 162, { speed: 60 });
    await S.say('okuyasu', '镇上新开的意大利馆子！据说吃了会变健康！', { expr: 'smile' });
    await S.walk(p, 160, 156, { speed: 60 });
    const tn = S.spawn('tonio', 443, 152, { id: 'tonio', facing: -1, name: '东尼欧' });
    await S.walk(tn, 250, 154, { speed: 50 });
    await S.say('tonio', '欢迎光临。我是东尼欧·特拉萨迪。', { expr: 'smile' });
    S.nameCard('tonio', { y: NAME_TOP });
    S.mark('ch3_tonio');
    await S.say('tonio', '请伸出手。……您睡眠不足，肩膀很僵，还有蛀牙。');
    await S.say('okuyasu', '诶？！你是医生吗？', { expr: 'shock' });
    await S.say('tonio', '我是厨师。今天的菜单，由您的身体来决定。', { expr: 'smile' });
    await S.say('josuke', '（……摸一下手就知道？不对劲。）');
    // 亿泰入座，东尼欧回后厨
    if (ok) { await S.walk(ok, TR.seat, 156, { speed: 60 }); S.face(ok, 1); S.pose(ok, 'sit'); }
    await S.walk(tn, 460, 152, { speed: 60 });
    tn.remove = true;
    await S.say('josuke', '亿泰，你先吃着。我去后面看看。');
    await S.say('josuke', '（先在水槽洗手，趁他背对着溜过去。）');
  }
  async function kitchenIn(S, round) {
    S.party(['josuke'], { leader: 'josuke' });
    await S.setStage('kitchen_ch3', { x: 34, y: 158, facing: 1, music: 'daily' });
    S.player.visible = true;
    const tn = S.spawn('tonio', 240, 150, { id: 'tonio_k', facing: 1, name: '东尼欧' });
    tn.team = 'npc';
    G.world.snapCamera();
  }
  // 每轮之后切到前厅：亿泰吃一道菜，演一种毛病好了
  const DISH = [
    { name: '矿泉水', fx: 'tears', lines: [['okuyasu', '眼睛……停不下来啊！', 'shock'], ['okuyasu', '像睡了十个小时一样清醒！', 'smile']] },
    { name: '番茄马苏里拉沙拉', fx: 'dirt', lines: [['okuyasu', '肩膀上……搓下来好多泥！', 'shock'], ['okuyasu', '肩膀好了！胳膊转起来像风车！', 'smile']] },
    { name: '番茄面', fx: 'teeth', lines: [['okuyasu', '噗！牙、牙飞出去了！', 'shock'], ['okuyasu', '……新牙当场长出来了？！', 'smile']] },
  ];
  async function dishScene(S, i) {
    S.party(['josuke', 'okuyasu'], { leader: 'josuke' });
    await S.setStage('trattoria_ch3', { x: 300, y: 158, facing: -1, music: 'daily' });
    const ok = S.actor('okuyasu'), p = S.player;
    p.visible = true;
    if (ok) { Object.assign(ok, { x: TR.seat, y: 156, follow: null, facing: 1 }); S.pose(ok, 'sit'); }
    const d = DISH[i];
    const dish = T().prop(S, 'dish', TR.table, 151, { id: 'dish', frame: i, z: 22 });
    snapTo({ x: 240 });
    await S.say(null, '第' + (i + 1) + '道：' + d.name + '。');
    if (ok) {
      S.unpose(ok);
      if (d.fx === 'tears') {
        S.sfx('water_gush', 0.8);
        for (const dir of [-1, 1]) S.fx('burst', { x: ok.x + dir * 3, y: ok.y - 26, n: 18, speed: 50, colours: ['#a0d8f8', '#e0f4ff'], gravity: 140, angle: 90 - dir * 40, spread: 30, life: 0.9 }, { life: 1.2 });
      } else if (d.fx === 'dirt') {
        S.sfx('sand', 0.7);
        S.fx('burst', { x: ok.x, y: ok.y - 22, n: 16, speed: 30, colours: ['#7a5a3a', '#a07a4a'], gravity: 160, life: 0.8 }, { life: 1 });
        ok.play('dodge'); S.shake(1, 0.4);
      } else {
        S.sfx('pop', 1); S.sfxText('噗！', ok, { dur: 0.7 });
        S.fx('burst', { x: ok.x + 4, y: ok.y - 24, n: 2, speed: 70, colours: ['#fafafa'], gravity: 160, life: 0.8, size: 2 }, { life: 1 });
      }
      await S.wait(0.6);
      for (const l of d.lines) await S.say(l[0], l[1], { expr: l[2] });
      S.pose(ok, 'sit');
    }
    if (dish) dish.remove = true;
  }
  async function caughtScene(S) {
    const p = S.player;
    S.hint(null);
    const tn = S.actor('tonio_k') || S.spawn('tonio', p.x - 22, p.y - 2, { id: 'tonio_k', facing: 1 });
    Object.assign(tn, { x: p.x - 22, y: p.y - 2, facing: 1 });
    tn.play('rage');
    S.sfx('sting_shock', 0.9);
    S.face(p, -1);
    S.mark('mg_caught');
    await S.say('tonio', '……客人。您在我的冰箱前面做什么？', { expr: 'rage' });
    await S.say('josuke', '（什么时候站到我背后的……！）', { expr: 'shock' });
    tn.play('idle');
    await S.say('tonio', '我只是想让客人吃上真正健康的饭。……请回座位吧。', { expr: 'smile' });
    await S.fadeOut(0.4);
    // 前厅：最后一道布丁，菜里的小家伙们；也给仗助端一盘
    S.party(['josuke', 'okuyasu'], { leader: 'josuke' });
    await S.setStage('trattoria_ch3', { x: TR.seat2 + 14, y: 158, facing: -1, music: 'daily' });
    const ok = S.actor('okuyasu');
    S.player.visible = true;
    if (ok) { Object.assign(ok, { x: TR.seat, y: 156, follow: null, facing: 1 }); S.pose(ok, 'sit'); }
    const t2 = S.spawn('tonio', 300, 152, { id: 'tonio', facing: -1, name: '东尼欧' });
    const dish = T().prop(S, 'dish', TR.table, 151, { id: 'dish', frame: 3, z: 22 });
    snapTo({ x: 250 });
    await S.fadeIn(0.4);
    await S.say(null, '第4道：布丁。');
    if (ok) { S.unpose(ok); S.sfx('fire', 0.5); S.fx('smoke', { x: ok.x, y: ok.y, n: 8, rise: 18, colour: '#c8c0a8', life: 1.2 }, { life: 1.4 }); }
    await S.say('okuyasu', '脚底冒烟了……袜子不臭了！', { expr: 'shock' });
    const pj = S.spawn('pearljam', TR.table + 4, 152, { id: 'pj', facing: -1 });
    pj.z = 24;
    S.sfx('pop', 0.6);
    S.standCard('pearljam', { y: NAME_TOP });
    S.cue('sting_reveal');
    await S.say('tonio', '它们叫“珍珠果酱”。会顺着菜，去治客人身上坏掉的地方。', { expr: 'smile' });
    await S.say('tonio', '这一盘，是给您的。', { expr: 'smile' });
    S.face(S.player, -1);
    await S.wait(0.4);
    S.sfx('sparkle', 0.8);
    S.fx('sparkles', { x: S.player.x, y: S.player.y - 30, n: 7, radius: 12, colour: '#ffe9a8', period: 0.5 }, { life: 0.9 });
    await S.say('josuke', 'Great！', { expr: 'smile' });
    S.mark('ch3_great');
    await S.say('okuyasu', '肩膀也好了！我再也不要回家吃泡面了！', { expr: 'smile' });
    pj.remove = true; if (dish) dish.remove = true; t2.remove = true;
    await S.fadeOut(0.6);
  }

  // ================================================================ 节拍 12 那天夜里：电视雪花
  async function beatTv(S) {
    S.party(['josuke'], { leader: 'josuke' });
    await S.setStage('living_ch3', { x: 231, y: 152, facing: -1, music: null, fade: false });
    S.player.visible = true;
    snapTo({ x: 231 });
    await S.fadeIn(0.6);
    await S.say('josuke', '哈啊……都这么晚了。电视怎么只剩雪花了。');
    let flick = -1;
    S.sfx('tv_game', 0.15);
    S.insert({
      draw: (wg, t) => {
        wg.fillStyle = '#16121c'; wg.fillRect(0, 0, 320, 180);
        wg.fillStyle = '#2a2430'; wg.fillRect(40, 18, 240, 144);
        const x0 = 52, y0 = 28, w = 216, h = 120;
        for (let y = 0; y < h; y += 3) for (let x = 0; x < w; x += 3) {
          const v = 90 + ((Math.sin((x * 12.9898 + y * 78.233 + Math.floor(t * 24) * 37.719)) * 43758.5453) % 1 + 1) % 1 * 150;
          wg.fillStyle = 'rgb(' + (v | 0) + ',' + (v | 0) + ',' + ((v + 10) | 0) + ')'; wg.fillRect(x0 + x, y0 + y, 3, 3);
        }
        // 雪花里闪过一个发光的影子（两下），最后钻进右边的电线
        const on = (t > 1.4 && t < 1.55) || (t > 1.9 && t < 2.1) || (t > 2.6 && t < 3.1);
        if (on) {
          const k = t > 2.6 ? (t - 2.6) / 0.5 : 0, cx = 160 + k * 130, cy = 88;
          wg.fillStyle = '#ffec78';
          wg.fillRect(cx - 3, cy - 14, 6, 6); wg.fillRect(cx - 5, cy - 8, 10, 12); wg.fillRect(cx - 6, cy + 4, 4, 8); wg.fillRect(cx + 2, cy + 4, 4, 8);
          if (flick < 0) flick = t;
        }
        wg.fillStyle = '#0a080e'; wg.fillRect(284, 120, 36, 3);
      },
    });
    await S.wait(3.4);
    S.mark('ch3_tv');
    S.insert(null);
    await S.say('josuke', '……刚才电视里，是不是有什么东西？', { expr: 'shock' });
    S.stopMusic(0.6);
    await S.tbc({ hold: 2.0 });
    S.mark('ch3_tbc');
  }

  // ================================================================ 第3章主流程
  G.STORY.ch3 = async function (S) {
    if (T().resetCounters) T().resetCounters();
    P4().clearOverlays();
    G.P4CH3.F = {};
    await S.chapterCard('ch3');
    S.party(['koichi'], { leader: 'koichi' });
    koichi();
    await S.run(async (S2) => {
      await beatCalendar(S2);
      await beatConfess(S2);
    }, { keepLocked: true });
    // 节拍 3 第二天：教室自由走动 → 走廊
    S.party(['koichi', 'josuke', 'okuyasu'], { leader: 'koichi' });
    koichi();
    await S.run(async (S2) => {
      await S2.setStage('class_ch3', { x: 200, y: 158, facing: -1, music: 'daily', fade: false });
      S2.player.visible = true;
      G.world.snapCamera();
      await S2.fadeIn(0.5);
      S2.mark('ch3_school');
      setupSchoolFree(S2);
      S2.hint('E 调查　Q 换队长：康一按 U 能听到墙后的声音', 8);
    });
    await S.until(() => !!F().toHall && !S.busy);
    await S.run(async (S2) => {
      await S2.setStage('hall_ch3', { x: 600, y: 158, facing: -1, music: 'daily' });
      setupHallFree(S2);
    });
    await S.until(() => !!F().stare && !S.busy);
    // 节拍 4 → 5 → 段 1 → 6 → 段 2
    await S.run(async (S2) => {
      await beatMissing(S2);
      await beatVilla(S2);
      await C3().escape(S2);
      await beatKnob(S2);
      await C3().loveDeluxe(S2);
      await afterLoveDeluxe(S2);
      await villaOutIn(S2);
      setupVillaOut(S2);
    }, { keepLocked: false });
    await S.until(() => !!F().wuwu && !S.busy);
    // 「呜呜」→ 窗户炸开 → 段 3 海岬 → 啪嘤岬 → 笔记 → 餐厅 → 小游戏 → 电视雪花
    await S.run(async (S2) => {
      await windowBurst(S2);
      await capeIn(S2);
      await C3().cape(S2);
      await afterCape(S2);
      await beatNotes(S2);
      await trattoriaIn(S2);
      for (let i = 0; i < 4; i++) {
        await S2.fadeOut(0.4);
        await kitchenIn(S2, i);
        await S2.fadeIn(0.4);
        await C3().tonio(S2, i);
        if (i < 3) await dishScene(S2, i);
      }
      await caughtScene(S2);
      await beatTv(S2);
    }, { keepLocked: true });
  };
  G.STORY.ch3.marks = ['ch3_calendar', 'ch3_confess', 'ch3_hair_lift', 'ch3_school', 'ch3_bento', 'ch3_stare', 'ch3_missing', 'ch3_villa',
    'b05a_start', 'b05a_listen', 'b05a_dial', 'b05a_barricade', 'ch3_knob', 'ch3_act2', 'b05b_start', 'b05b_scalp', 'b05b_trap', 'b05b_white',
    'ch3_out', 'ch3_wuwu', 'b05c_tail', 'b05c_pop', 'b05c_saved', 'ch3_walkaway', 'ch3_notes', 'ch3_tonio', 'mg_round1', 'mg_round2', 'mg_round3',
    'mg_caught', 'ch3_great', 'ch3_tv', 'ch3_tbc'];
})();
