// 包 3 自测脚本：把 §4.10 的每个组件摆出来，test_ui.py 一步步驱动、截图、断言（也可以手动开 ui_demo.html?step=名字 看）
'use strict';
(function () {
  const G = window.G;
  const ui = () => G.ui, fx = () => G.uifx, hud = () => G.hud, W = () => G.world;
  const A = (cid, x, y, o) => new G.DemoActor(cid, x, y, o);
  const LONG = '这一路要走五十天，从东京到开罗。DIO 在等着我们，可荷莉的时间不多了——所以别磨蹭。' +
    '你下一句要说的是「真是够了」吧？……呀嘞呀嘞daze。行李收拾好，明天一早的飞机。' +
    '还有，路上不管遇到什么替身使者，都别一个人冲上去。这是命令，也是老头子的请求。';

  const D = (window.DEMO = {
    log: [], done: {}, ret: {},
    boot() {
      const go = () => {
        if (G.initFonts) G.initFonts();
        if (G.audio && G.audio.init) { try { G.audio.init(); } catch (e) { D.log.push('audio.init: ' + e.message); } }
        G.setScene ? G.setScene(G.demoScene) : (G.scene = G.demoScene);
        D.reset('school_gate');
        G.start();
        window.__ready = true;
        const q = new URLSearchParams(location.search).get('step');
        if (q && D[q]) D[q]();
        const el = document.getElementById('loading'); if (el) el.remove();
      };
      if (G.res && G.res.preloadPack) G.res.preloadPack('core').then(() => G.res.preloadPack('bg_fixture')).then(go, go);
      else go();
    },
    // 清场：换背景、复位 UI / HUD / 世界
    reset(bg = 'school_gate') {
      ui().reset();
      const w = W();
      w.insert = null; w.cine = null; w.combat = false; w.fight = null; w.fightT = 0; w.near = null; w._look = null; w.free = true;
      if (G.post && G.post.clear) G.post.clear();
      w.setStage(bg);
      G.cam.x = 0; G.cam.y = 0; G.cam.zoom = null;
      G.party.members = []; G.party._lookReady = false; G.party.locked = false;
      G.S.busy = false;
      w.player = null;
      return w.stage;
    },
    // ============================================================ 对话（3 页长句 + 三种表情写法 + 32×46 头像 + 顶部 + 无头像描述）
    async dialog() {
      D.reset('kujo_house_day');
      const w = W();
      w.player = w.add(A('jotaro', 120, 160, { team: 'player' }));
      w.add(A('joseph', 170, 160, { facing: -1 }));
      D.done.dialog = false;
      await ui().say('joseph', LONG, { expr: 'grave' });                          // emotion 名
      await ui().say('jotaro', '……吵死了。我自己会处理。', { expr: 'portrait_angry' });   // 图集 expressions 的 id
      await ui().say('joseph', '承太郎！你下一句要说的是「我去」，对吧？', { expr: 's19_jp_open' });   // 场景专用头像名（32×46）
      await ui().say('kakyoin', '（顶部对话框）……让我来带路吧。', { expr: 'evil', pos: 'top' });
      await ui().say(null, '桌上放着一本漫画书。翻开的那一页画着一个戴帽子的男人。');
      D.done.dialog = true;
    },
    // ============================================================ 旁白（三种位置 + 黑场）
    async narr() {
      D.reset('jail_cell');
      D.done.narr = false;
      await ui().narrate('1987 年，日本·东京。警察局的拘留室里，关着一个自己不肯出去的高中生。', { pos: 'top' });
      await ui().narrate('（居中旁白）他说牢房里有“恶灵”。', { pos: 'center' });
      await ui().narrate('（底部旁白）……第二天早上，铁栏被掰弯了。', { pos: 'bottom' });
      G.fadeA = 1;
      await ui().narrate('——五十天后。', { onBlack: true });
      G.fadeA = 0;
      D.done.narr = true;
    },
    // ============================================================ 选项（带 title；有对话框 / 没对话框两种位置）
    async choice() {
      D.reset('kujo_house_day');
      D.done.choice = false;
      ui().say('joseph', '承太郎，你要跟我们一起去埃及吗？', {});
      D.ret.c1 = await ui().choice(['去。', '……（压低帽檐）', '让我再想想'], '承太郎的回答');
      D.ret.c2 = await ui().choice(['调查书桌', '调查窗外', '离开']);
      D.done.choice = true;
    },
    async notice() {
      D.reset('school_gate');
      D.done.notice = false;
      await ui().notice({ who: 'kakyoin', title: '花京院典明', text: '加入了队伍！', sub: '绿色法皇：远程 · 宝石弹幕 · 触须网' });
      D.done.notice = true;
    },
    async menu() {
      D.reset('title_pyramids');
      D.done.menu = false;
      const vol = { v: 8 };
      const opts = ['继续', '操作说明', '设置', '音乐音量  < ' + vol.v + ' >', '回到标题'];
      D.ret.menu = await ui().openMenu('暂停', opts, {
        escIndex: 0, note: 'Esc 返回游戏　←→ 调音量',
        onKey(i, dir, m) { if (i !== 3) return false; vol.v = Math.max(0, Math.min(10, vol.v + dir)); m.options[3] = '音乐音量  < ' + vol.v + ' >'; return true; },
      });
      D.done.menu = true;
    },
    // ============================================================ 7 种 QTE（test_ui.py 自动输入）
    async qte(type) {
      D.reset(type === 'pluck' ? 'school_gate' : 'hongkong_night');
      D.done['qte_' + type] = false;
      const o = {
        mash: { type: 'mash', label: '这次简单多了——连按 J', need: 6, time: 1.5 },
        timing: { type: 'timing', label: '扯回来！（J）', speed: 1.0, zone: [0.36, 0.64], tries: 2 },
        rhythm: { type: 'rhythm', label: '跟着心跳吸气（J）', notes: [0.8, 1.3, 1.8, 2.3, 2.8, 3.3], window: 0.16, pass: 0.5 },
        clash: { type: 'clash', id: 'demo_clash', label: '拉起来——！！（连按 J）', time: 4, colours: ['#b090ff', '#ffd040'] },
        press: { type: 'press', key: 'guard', window: 0.4, perfect: 0.1, label: 'L——挡住她！', failOk: true },
        pluck: { type: 'pluck', onReset: async () => { await ui().say('joseph', '别慌！再来一次！', { expr: 'grave' }); } },
        aim: { type: 'aim', label: '按住方向键稳住！', time: 6, need: 2 },
      }[type];
      D.ret['qte_' + type] = await ui().startQte(o);
      await ui().say('jotaro', '（QTE 结束后的第一句——狂点也不该被跳过）', {});
      D.done['qte_' + type] = true;
    },
    // ============================================================ 卡片：名牌 / 替身卡 / 地点卡 / 大字 / 拟声字 / ゴゴゴ / 换队长
    cards() {
      const st = D.reset('school_gate');
      const w = W();
      const jo = w.add(A('jotaro', 110, 162, { team: 'player' }));
      const ka = w.add(A('kakyoin', 210, 162, { facing: -1 }));
      w.player = jo;
      void st;
      fx().location('school');
      fx().nameCard('kakyoin');
      fx().standCard('hiero', { side: 'right' });
      D.men = fx().menacing({ actor: ka, n: 4 });
      fx().sfx('ドドド', { x: 120, y: 120 }, { dur: 3, rot: -6 });
      fx().sfx('ORA!', jo, { dur: 3, rot: 8 });
      fx().sfx('キィン！', { wx: 160, wy: 130, wz: 0 }, { dur: 3 });
      fx().sfx('看穿！', { x: 520, y: 300 }, { dur: 3 });
      fx().leaderCard(jo);
      setTimeout(() => {}, 0);
    },
    titleStand() { D.reset('jail_cell'); fx().title('stand', { dur: 2.0 }); },
    titleSaiki() { D.reset('hk_garden_night'); fx().title('saiki', { y: 230, pop: 0.12, dur: 1.2 }); },
    chapter() { D.reset('kujo_house_day'); D.done.chapter = false; fx().chapterCard('prologue').then(() => { D.done.chapter = true; }); },
    // ============================================================ VS（序2 法皇）
    vs() {
      D.reset('school_gate');
      const w = W();
      w.player = w.add(A('jotaro', 100, 162, { team: 'player' }));
      w.add(A('kakyoin', 220, 162, { facing: -1, anim: 'possessed' }));
      D.done.vs = false;
      fx().vs({ hero: 'jotaro', enemy: { cid: 'hiero', anim: 'idle', scale: 2 }, key: 'hiero' }).then(() => { D.done.vs = true; });
    },
    vsTower() {
      D.reset('plane_cabin_side');
      const w = W();
      w.player = w.add(A('kakyoin', 100, 162, { team: 'player' }));
      D.done.vs = false;
      fx().vs({ hero: 'kakyoin', enemy: { cid: 'towergray', anim: 'fly', scale: 4 }, key: 'towergray' }).then(() => { D.done.vs = true; });
    },
    // ============================================================ 必杀切入（玩家）/ W6 敌人切入
    cutin(cid = 'jotaro') {
      D.reset('hongkong_night');
      const w = W();
      w.player = w.add(A(cid, 120, 164, { team: 'player' }));
      w.add(A('polnareff', 200, 164, { facing: -1, team: 'enemy', boss: true }));
      D.done.cutin = false;
      fx().cutin({ cid, title: cid }).then(() => { D.done.cutin = true; });
    },
    ecut() {
      D.combat();
      D.done.ecut = false;
      fx().cutin({ enemy: true, portrait: 'kakyoin', expr: 'evil', stand: 'hiero', title: 'w6_hg_splash' }).then(() => { D.done.ecut = true; });
    },
    // ============================================================ 面板 / 坠毁章 / 眼部条带 / 念写照片 / 回忆小窗 / TBC
    panel() { D.reset('school_infirmary'); D.pnl = fx().panel('tissue_note'); },
    crash() { D.reset('sea_day'); D.done.crash = false; fx().crashRecord(2, 3).then(() => { D.done.crash = true; }); },
    eye() {
      D.reset('kujo_bedroom_dusk');
      W().player = W().add(A('jotaro', 140, 162, { team: 'player' }));
      D.done.eye = false;
      fx().eyeStrip('jotaro', { dur: 0.6 }).then(() => { D.done.eye = true; });
    },
    photo() { D.reset('kujo_house_night'); D.done.photo = false; fx().photo({ arrow: { x: 11, y: 7, angle: 225 } }).then(() => { D.done.photo = true; }); },
    memory() { D.reset('hk_garden_night'); D.mem = fx().memoryPanel({ cid: 'jgeil' }); },
    tbc() {
      D.reset('hongkong_night');
      const w = W();
      w.add(A('jotaro', 100, 164)); w.add(A('avdol', 140, 164)); w.add(A('kakyoin', 180, 164)); w.add(A('joseph', 220, 164));
      D.done.tbc = false;
      fx().tbc().then(() => { D.done.tbc = true; });
    },
    // ============================================================ 战斗 HUD（4 人 + Boss 条带阶段刻度 + 计时 + 环境槽 + 连击 + vsTag）
    combat() {
      D.reset('hk_garden_night');
      const w = W();
      const p = w.add(A('avdol', 100, 164, { team: 'player', hp: 120, maxHp: 120, energy: 100 }));
      p.hp = 26;
      w.player = p;
      w.add(A('jotaro', 60, 168, { team: 'ally', hp: 130, maxHp: 130 }));
      w.add(A('kakyoin', 40, 160, { team: 'ally', hp: 100, maxHp: 100, state: 'down' }));
      const jo = w.stage.actors[1]; jo.hp = 80; jo.energy = 100;
      w.add(A('joseph', 20, 166, { team: 'ally', hp: 110, maxHp: 110 }));
      const boss = w.add(A('polnareff', 230, 164, { team: 'enemy', boss: true, hp: 900, maxHp: 900, facing: -1, phases: [{ at: 0.6 }, { at: 0.4 }, { at: 0.2 }], poiseMax: 70, poise: 40 }));
      boss.hp = 610; boss.name = '让·皮埃尔·波鲁纳雷夫';
      w.add(A('jgeil', 280, 160, { team: 'enemy', hp: 60, maxHp: 60, facing: -1 })).hp = 25;
      w.combat = true; w.free = false;
      w.fight = { swap: true, storyU: true, spec: { kitOverride: { avdol: { special: { prompt: '按 U！' } } } }, emit() {} };
      hud().on = true; hud().boss = boss;
      hud().timer = { label: '撑到天亮还有', until: 32 };
      hud().gauge = { label: '热量', value: 64, max: 100, color: '#ff8040' };
      fx().vsTag('chariot');
      return boss;
    },
    combo(n, word) { for (let i = 0; i < n; i++) hud().comboHit(word); },
    steps() {
      D.reset('jail_cell');
      const w = W();
      w.player = w.add(A('jotaro', 160, 132, { team: 'player', hp: 130, maxHp: 130 }));
      w.combat = true; w.free = false;
      hud().on = true; hud().steps = { n: 6, done: 2, label: '阿布德尔的试探' };
    },
    // ============================================================ 探索：头像条（灰 / 问号）+ 互动提示 + U + 表情 + 可破坏物小血条
    explore() {
      D.reset('hongkong_night');
      const w = W();
      const jo = w.add(A('jotaro', 120, 164, { team: 'player' }));
      const jos = w.add(A('joseph', 96, 166));
      const av = w.add(A('avdol', 76, 162, { look: 'unknown', leadable: false }));
      const ka = w.add(A('kakyoin', 56, 168, { look: 'gray', leadable: false }));
      const owner = w.add(A('jgeil', 200, 162, { facing: -1, label: '大排档老板' }));
      const pipe = w.add(A('dio', 280, 164, { team: 'object', hp: 30, maxHp: 30 })); pipe.visible = false;
      w.player = jo;
      G.party.members = [jo, jos, av, ka];
      w.near = { actor: owner, label: '大排档老板', x: owner.x, top: owner.headY() };
      jos.emote = { text: '!?', t: 99, color: '#ffe14a' };
      G.party._lookReady = true;
      w._look = { x: 250, y: 150, ly: 120, tags: ['detail'], label: '橱窗' };
      D.pipe = pipe;
      pipe.visible = true; pipe.cid = 'dio';
      setTimeout(() => {}, 0);
    },
    hitPipe() { D.pipe.hp -= 8; },
    letterbox() { D.reset('dusk_gate'); ui().letterboxTarget = 32; ui().insertUI = { draw(g, t) { g.fillStyle = 'rgba(40,0,60,0.35)'; g.fillRect(0, 0, 640, 360); G.f16.draw(g, '（插入层 insertUI 测试 t=' + t.toFixed(1) + '）', 320, 170, '#fff', { align: 'center', outline: '#000' }); } }; },
    hint() { D.reset('school_gate'); ui().hint('按 U 进行替身调查——每个队长看到的东西不一样（Q 换队长）', 6); },
    // 小工具：给测试读
    st() { return Object.assign(ui().state(), { qteObj: !!ui().qte, cine: W().cine, insert: !!W().insert, missingGlyph: [...G.dbg.missingGlyph], missingImg: [...G.dbg.missingImg], missingHead: [...G.dbg.missingHead] }); },
  });
})();
