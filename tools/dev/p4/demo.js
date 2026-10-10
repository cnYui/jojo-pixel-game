// 包 4 自测场景（test_world.py 逐个调用 window.P4.xxx()，结果是 JSON；截图拼成联系表返回 dataURL）
'use strict';
(function () {
  const G = window.G;
  const W = () => G.world;
  const step = (n) => G.__step(n);
  const sec = (s) => step(Math.round(s * 60));
  const tap = (a) => G.input.inject ? G.input.inject(a) : G.input.press(a);
  const hold = (a, on) => G.input.hold ? G.input.hold(a, on) : on ? G.input.press(a, 'p4') : G.input.release(a, 'p4');
  const shots = [];
  function cap(label, src) {
    const c = G.mkCanvas(640, 360, true);
    const s = src || G.wv;
    c.width = s === G.wv ? 640 : 640; c.height = s === G.wv ? 360 : 360;
    const g = c.getContext('2d');
    g.imageSmoothingEnabled = false;
    g.drawImage(s, 0, 0, s.width, s.height, 0, 0, 640, 360);
    shots.push({ label, c });
  }
  function sheet(cols = 3) {
    const n = shots.length, rows = Math.ceil(n / cols), cw = 640, ch = 360, pad = 22;
    const c = G.mkCanvas(cols * (cw + 8) + 8, rows * (ch + pad + 8) + 8, true);
    const g = c.getContext('2d');
    g.fillStyle = '#202028'; g.fillRect(0, 0, c.width, c.height);
    g.font = '16px sans-serif'; g.fillStyle = '#ffe9a8'; g.imageSmoothingEnabled = false;
    shots.forEach((s, i) => {
      const x = 8 + (i % cols) * (cw + 8), y = 8 + Math.floor(i / cols) * (ch + pad + 8);
      g.fillText(s.label, x, y + 16);
      g.drawImage(s.c, x, y + pad);
    });
    shots.length = 0;
    return c.toDataURL('image/png');
  }
  const free = (on) => { W().free = on; };
  function resetWorld() {
    G.time.__set(null);
    G.party.reset();
    W().player = null; W().combat = false; W().fight = null; W().insert = null; W().zoom = null; W().focus = null;
    G.cam.shakeAmp = 0; G.cam.shakeDur = 0; G.S.log.length = 0; G.ui.hints.length = 0; G.uifx.cards.length = 0;
    G.input.clear();
  }
  function stage(id, bg, o = {}) {
    G.STAGES[id] = Object.assign({ id, bg }, o);
    return G.STAGES[id];
  }

  const P4 = (window.P4 = {
    async init() {
      await G.res.preloadPack('core');
      await G.res.preloadPack('bg_fixture');
      G.setScene(G.worldScene);
      G.start();
      return { chars: Object.keys(G.D.chars).length, bg: Object.keys(G.D.bg) };
    },

    // ① 逻辑名 → resolve 结果表
    resolveTable() {
      const cids = ['jotaro', 'starplat', 'kakyoin', 'hiero', 'avdol', 'magred', 'polnareff', 'chariot', 'joseph', 'iggy', 'fool',
        'towergray', 'theworld', 'dio', 'holly'];
      const names = ['idle', 'walk', 'run', 'talk', 'cmd', 'cmd2', 'cmd_hold', 'guard', 'dodge', 'hurt', 'down', 'getup', 'special', 'pose',
        'shock', 'win', 'punch', 'punch2', 'punch_heavy', 'rush', 'block', 'fist', 'windup', 'attack', 'attack2', 'shoot', 'fly'];
      const out = {};
      const fmt = (r) => r.name + (r.f != null ? '#' + r.f : '') + (r.rot ? '@' + r.rot : '') + (r.flip ? '~flip' : '') + (r.dy ? 'dy' + r.dy : '') + (r.fell ? '*' : '');
      for (const c of cids) { const A = G.atlas(c); out[c] = {}; for (const n of names) out[c][n] = fmt(A.resolve(n)); }
      const A = G.atlas('chariot');
      out['chariot(skin bare)'] = {};
      for (const n of ['idle', 'punch', 'punch2', 'punch_heavy', 'rush', 'attack', 'block', 'hurt']) out['chariot(skin bare)'][n] = fmt(A.resolve(n, 'bare'));
      out['prop:jail_pipe'] = { idle: fmt(G.atlas('prop:jail_pipe').resolve('idle')), 1: fmt(G.atlas('prop:jail_pipe').resolve(1)) };
      const heads = {
        'jotaro:normal': (G.head('jotaro', 'normal') || []).length, 'jotaro:portrait_angry': (G.head('jotaro', 'portrait_angry') || []).length,
        'jotaro:s05_jotaro_talk': (G.head('jotaro', 's05_jotaro_talk') || []).length, 'joseph:s19_jp_evil': (G.head('joseph', 's19_jp_evil') || []).length,
        'joseph:s19_jp_evil size': G.headSize('joseph', 's19_jp_evil'), 'polnareff:shock_big size': G.headSize('polnareff', 'shock_big'),
      };
      G.head('kakyoin', 'no_such_face');
      return { table: out, heads, missingHead: [...G.dbg.missingHead], fallbacks: [...G.dbg.animFallbacks].length, missingImg: [...G.dbg.missingImg] };
    },

    // ② 四人组队在香港夜街走 30 s：跟随者两两最近距离、不卡墙、单屏只显示 4 人
    walk30() {
      resetWorld();
      const def = stage('hk_street_p4', 'hongkong_night', { x0: 0, x1: 960 });
      G.party.set(['jotaro', 'joseph', 'avdol', 'kakyoin'], { leader: 'jotaro' });
      const p = G.party.leader();
      p.x = 120; p.y = 162;
      W().setStage(def, { player: p, x: 120, y: 162 });
      free(true);
      const I = G.input;
      let minPair = 1e9, minPairT = 0, samples = 0, maxLag = 0;
      const plan = [['right', 6], ['left', 3], ['up', 0.5], ['right', 3], ['down', 0.6], ['left', 5], ['up', 0.4], ['down', 0.4],
        ['up', 0.4], ['down', 0.4], ['right', 7], ['none', 3.3]];
      let t = 0;
      for (const [k, d] of plan) {
        if (k !== 'none') hold(k, true);
        for (let i = 0; i < Math.round(d * 60); i++) {
          G.__stepOne(1 / 60); t += 1 / 60;
          if (i % 5 === 0) {
            const fol = G.party.members.filter((m) => m !== W().player && m.visible);
            for (let a = 0; a < fol.length; a++) for (let b = a + 1; b < fol.length; b++) {
              const dd = Math.hypot(fol[a].x - fol[b].x, fol[a].y - fol[b].y);
              if (dd < minPair) { minPair = dd; minPairT = t; }
            }
            for (const f of fol) maxLag = Math.max(maxLag, Math.abs(f.x - W().player.x));
            samples++;
          }
        }
        if (k !== 'none') hold(k, false);
        if (k === 'right' && t > 25) cap('走完 30 s（停下后）');
      }
      G.__render();
      cap('香港夜街 · 四人轨迹跟随（停下）');
      const st = W().stage;
      const pos = G.party.members.map((m) => [m.cid, Math.round(m.x), Math.round(m.y), m.visible, m.followSlot]);
      const inBounds = G.party.members.every((m) => m.x >= st.x0 && m.x <= st.x1 && m.y >= st.yMin && m.y <= st.yMax);
      // 单屏地图：五人只显示队长 + 3
      const kdef = stage('kujo_p4_pro', 'kujo_house_day');
      G.party.set(['jotaro', 'joseph', 'avdol', 'kakyoin', 'polnareff'], { leader: 'jotaro' });
      W().setStage(kdef, { player: G.party.leader(), x: 160, y: 160 });
      sec(1.5);
      const visibleSmall = G.party.members.filter((m) => m.visible).map((m) => m.cid);
      cap('空条家（单屏 320）· 五人只显示队长 + 3');
      const max = G.party.maxFollowers();
      W().setStage(def, { player: G.party.leader(), x: 300, y: 160 });
      sec(1);
      const visibleWide = G.party.members.filter((m) => m.visible).map((m) => m.cid);
      return { minPair: +minPair.toFixed(2), minPairT: +minPairT.toFixed(2), samples, maxLag: Math.round(maxLag), pos, inBounds, visibleSmall, maxSmall: max, visibleWide, sheet: sheet(3) };
    },

    // 换队长 5 次：HP / 能量 / 替身对象不变、镜头缓动、跳过不能当队长的人
    swap5() {
      resetWorld();
      const def = stage('hk_swap_p4', 'hongkong_night', { x0: 0, x1: 960 });
      G.party.set(['jotaro', 'joseph', 'avdol', 'kakyoin'], { leader: 'jotaro' });
      W().setStage(def, { player: G.party.leader(), x: 200, y: 162 });
      free(true);
      const snap = () => G.party.members.map((m) => ({ cid: m.cid, uid: m.uid, hp: m.hp, en: m.energy, stand: m.stand ? m.stand.id + '#' + m.stand.owner.uid : null }));
      G.party.members.forEach((m, i) => { m.hp = 50 + i * 7; m.energy = 10 + i * 13; });
      // 把队员拉开，镜头才看得出缓动
      sec(0.5);
      hold('right', true); sec(2.5); hold('right', false); sec(0.2);
      const before = snap();
      const leaders = [], camTrace = [];
      for (let i = 0; i < 5; i++) {
        tap('swap');
        for (let k = 0; k < 24; k++) { G.__stepOne(1 / 60); if (i === 0) camTrace.push(G.cam.x); }
        leaders.push(W().player.cid);
        if (i === 1) { G.__render(); cap('换队长后（阿布德尔）· 替身亮出来 + 换人卡'); }
      }
      const after = snap();
      const same = JSON.stringify(before) === JSON.stringify(after);
      const camJumps = camTrace.slice(1).map((v, i) => Math.abs(v - camTrace[i]));
      // 不能当队长：花京院灰掉，Q 跳过并只提示一次
      G.party.setLeader('jotaro', { force: true, silent: true });
      G.party.setLeadable('kakyoin', false, { look: 'gray', msg: '……让我先看看你妈妈的情况。' });
      const seq = [];
      for (let i = 0; i < 6; i++) { tap('swap'); sec(0.4); seq.push(W().player.cid); }
      const hints = G.ui.hints.slice();
      tap('lead4'); sec(0.4);
      const afterLead4 = W().player.cid;
      G.party.setLeadable('kakyoin', true);
      tap('lead4'); sec(0.4);
      const afterLead4b = W().player.cid;
      G.__render(); cap('数字键 4 选花京院');
      return { leaders, same, maxCamStep: Math.max(...camJumps), camFirst: camTrace[0], camLast: camTrace[camTrace.length - 1], cards: G.uifx.cards.slice(),
        skipSeq: seq, hints, afterLead4, afterLead4b, evSwap: G.dbg.counts.swap || 0, sheet: sheet(2) };
    },

    // ③ 替身：召唤 → idle → act（punch / rush / block）→ 收回；绿色法皇偏上站位 + 触须连线；乔瑟夫的藤蔓；伊奇的沙
    standFrames() {
      resetWorld();
      const def = stage('types_p4', 'p4_types', { x0: 0, x1: 640 });
      G.party.set(['jotaro', 'kakyoin', 'joseph', 'iggy'], { leader: 'jotaro' });
      W().setStage(def, { player: G.party.leader(), x: 110, y: 164 });
      const [jo, ka, js, ig] = G.party.members;
      for (const m of G.party.members) { m.follow = null; }
      jo.x = 70; jo.y = 166; ka.x = 150; ka.y = 166; js.x = 220; js.y = 166; ig.x = 280; ig.y = 166;
      free(false);
      for (const m of [jo, ka, js, ig]) m.stand.summon();
      step(6); cap('召唤 0.1 s（白化 + 抖动渐显 + 上升线）');
      step(6); cap('召唤 0.2 s');
      sec(0.4); cap('idle：承太郎身后 dx −6 z 6；法皇 dx −4 z 10 + 触须');
      jo.stand.act('punch', { seq: [[0, 0.05], [1, 0.083], [2, 99]], dur: 0.33 }); ka.stand.act('punch', { dx: 60, z: 8, dur: 0.6 }); js.stand.act('punch'); ig.stand.act('punch');
      step(4); cap('act punch 0.07 s（法皇伸到 dx 60）');
      step(8); cap('act punch 0.2 s');
      jo.stand.act('rush'); ka.stand.act('rush', { dx: 30 }); js.stand.act('rush');
      step(10); cap('act rush（±1 抖）');
      jo.stand.act('block', { hold: true }); ka.stand.act('block', { hold: true });
      step(10); cap('act block');
      for (const m of [jo, ka, js, ig]) m.stand.recall();
      step(7); cap('收回 0.12 s（白化溶解）');
      step(20); cap('收回完');
      const modes = [jo, ka, js, ig].map((m) => m.stand.mode);
      // 冻住：本体时停被冻住时替身不动（浮动用本体 ownT）
      jo.stand.summon({ dur: 0.01 }); step(3);
      G.time.__set('stopped', [ka]);
      const z0 = jo.stand.z, x0 = jo.stand.x; const ow0 = jo.ownT;
      sec(1);
      const frozenOk = jo.stand.z === z0 && jo.stand.x === x0 && jo.ownT === ow0;
      G.time.__set(null);
      // 站位覆盖（序2 敌方法皇 dx 20 身前）
      ka.standPos = { dx: 20, z: 10, link: 'tendril' }; ka.stand.summon({ dur: 0.01 }); sec(0.3);
      const kaFront = Math.round((ka.stand.x - ka.x) * ka.facing);
      cap('standPos 覆盖：法皇浮在花京院身前 dx 20');
      ka.standPos = null;
      // 自由走动 2.5 s 不动作自动收回
      free(true); jo.stand.summon({ dur: 0.01 }); sec(1.0); const m1 = jo.stand.mode; sec(1.8); const m2 = jo.stand.mode; sec(0.4);
      return { modes, frozenOk, kaFront, autoRecall: [m1, m2, jo.stand.mode], sheet: sheet(3) };
    },

    // ④ 光环 / 抖动透明（缓存命中率）/ 描边 / 逆光剪影 / rot −90 倒地 / 朝左
    effects() {
      resetWorld();
      const def = stage('fx_p4', 'p4_types', { x0: 0, x1: 640 });
      W().setStage(def, {});
      free(false);
      const g = G.wg;
      const drawAll = (fn) => { G.__render(); fn(g); };
      G.__render();
      const heroes = ['jotaro', 'joseph', 'avdol', 'kakyoin', 'polnareff', 'iggy'];
      drawAll((g) => heroes.forEach((c, i) => G.atlas(c).draw(g, 'idle', 0, 30 + i * 52, 150, { backlit: { dark: '#0a0610', k: 0.9, rim: '#ffb060' } })));
      cap('逆光剪影 backlit（标题画面那套）');
      drawAll((g) => {
        G.atlas('starplat').draw(g, 'idle', 0, 50, 140, { alpha: 0.92, aura: { color: '#b090ff', alpha: 0.55, grow: 1, jitter: true, t: 0.3 } });
        G.atlas('hiero').draw(g, 'idle', 0, 130, 140, { alpha: 0.92, aura: { color: '#70ffb0', alpha: 0.55, grow: 1, t: 1.1 } });
        G.atlas('magred').draw(g, 'idle', 0, 210, 140, { alpha: 0.92, aura: { color: '#ff7a30', alpha: 0.55, grow: 2, t: 2 } });
        G.atlas('jotaro').draw(g, 'idle', 0, 280, 160, { outline: '#f0e8c0' });
      });
      cap('光环 grow 1/1/2 + 描边 #f0e8c0');
      drawAll((g) => {
        G.atlas('jotaro').draw(g, 'idle', 0, 40, 160, { rim: '#ffd488' });
        G.atlas('jotaro').draw(g, 'idle', 0, 90, 160, { sil: '#201030' });
        G.atlas('jotaro').draw(g, 'idle', 0, 140, 160, { tint: { color: '#ff3048', k: 0.6 } });
        G.atlas('jotaro').draw(g, 'idle', 0, 190, 160, { flash: 0.8 });
        G.atlas('jotaro').draw(g, 'idle', 0, 240, 160, { dither: 0.5 });
        G.atlas('jotaro').draw(g, 'walk', 1, 290, 160, { flip: true, scale: 1 });
      });
      cap('rim / sil / tint / flash / dither 0.5 / 朝左');
      drawAll((g) => {
        G.atlas('dio').draw(g, 'down', 0, 60, 160, {});
        G.atlas('dio').draw(g, 'down', 0, 140, 160, { flip: true });
        G.atlas('joseph').draw(g, 'down', 0, 210, 160, {});
        G.atlas('joseph').draw(g, 'down', 0, 280, 160, { flip: true });
        G.atlas('jotaro').draw(g, 'idle', 0, 40, 110, { scale: 2 });
      });
      cap('down 回退：dio rot −90（朝左取反）、joseph lie~flip；×2');
      // 抖动透明缓存命中率：同一个人站着连续淡出 3 轮（每轮 2 s）
      G.Atlas.clearCache();
      const A = G.atlas('kakyoin');
      for (let r = 0; r < 3; r++) for (let i = 0; i < 120; i++) { G.__render(); A.draw(g, 'idle', 0, 160, 150, { dither: 1 - i / 120 }); }
      const s = G.Atlas.stats;
      const hitRate = s.ditherHit / Math.max(1, s.ditherHit + s.ditherMiss);
      // 残影
      const jo = new G.Actor('jotaro', 100, 160);
      W().stage.add(jo);
      jo.ghostOn = true; jo.state = 'dodge';
      for (let i = 0; i < 12; i++) { jo.x += 4; step(1); }
      cap('残影：承太郎闪避（4 个快照，dither 0.2→0.55）');
      return { ditherHitRate: +hitRate.toFixed(3), ditherHit: s.ditherHit, ditherMiss: s.ditherMiss, cacheSize: G.Atlas.cacheSize(), ghosts: jo.ghosts.length, sheet: sheet(3) };
    },

    // ⑤ 推近 2 倍 + 震屏；W6 自动推镜
    zoomShake() {
      resetWorld();
      const def = stage('hk_zoom_p4', 'hongkong_night', { x0: 0, x1: 960 });
      G.party.set(['jotaro', 'kakyoin'], { leader: 'jotaro' });
      W().setStage(def, { player: G.party.leader(), x: 240, y: 162 });
      free(true); sec(0.5);
      cap('原始（320×180）', G.screen);
      W().zoom = { k: 2, x: 240, y: 130 };
      sec(0.1); cap('推近 2 倍（中心 = 承太郎胸口）', G.screen);
      G.shake(4, 2, {}); step(3); cap('推近 2 倍 + 震屏 4（不露黑边）', G.screen);
      W().zoom = null; G.cam.shakeDur = 0;
      // W6：敌人预警时镜头 0.2 s 推到 1.3，收招完 0.2 s 拉回
      const e = new G.Actor('dio', 320, 162, { team: 'enemy', facing: -1 });
      W().stage.add(e); W().combat = true; free(false);
      e.tele = { move: 'X', t: 0, dur: 1, tier: 'W6' };
      const ks = [];
      for (let i = 0; i < 20; i++) { step(1); ks.push(G.cam.zoom ? +G.cam.zoom.k.toFixed(3) : 1); }
      cap('W6 预警：镜头推到 1.3', G.screen);
      e.tele = null; e.atk = { warn: { tier: 'W6' } }; sec(0.3);
      const during = G.cam.zoom ? G.cam.zoom.k : 1;
      e.atk = null;
      const back = [];
      for (let i = 0; i < 20; i++) { step(1); back.push(G.cam.zoom ? +G.cam.zoom.k.toFixed(3) : 1); }
      // 战斗镜头：操作角色留在中间 60%
      e.x = 900; sec(2);
      const px = W().player.x - G.cam.x;
      W().combat = false; e.remove = true;
      return { ks, during, back, playerScreenX: Math.round(px), sheet: sheet(2) };
    },

    // ⑥ 调查点（E 和带标签的 U）+ NPC onStand + 触发区 + 可破坏物
    async interact() {
      resetWorld();
      const used = [], looked = [], trig = [], breaks = [], hits = [], stood = [];
      const def = stage('jail_p4_pro', 'p4_types', {
        x0: 0, x1: 640,
        props: [{ type: 'breakable', id: 'pipe', sprite: 'jail_pipe', frames: [0, 1], x: 330, y: 160, w: 16, h: 48, hp: 30, free: true,
          onHit: async (S, h, info) => { hits.push(info.slot); }, onBreak: async (S, h) => { breaks.push(h.id); } }],
        npcs: [{ cid: 'holly', id: 'holly', x: 200, y: 162, label: '荷莉', talk: async (S, me) => { used.push('talk:' + me.id); },
          onStand: async (S, me, leader) => { stood.push(me.id + '<' + leader.cid); } },
          { cid: 'enya', id: 'stranger', x: 470, y: 162, talk: async () => {} }],
        hotspots: [
          { id: 'mag', x: 100, y: 160, label: '杂志', use: async (S, h, leader) => { used.push('use:' + h.id + ':' + leader.cid); } },
          { id: 'fly', x: 130, y: 160, label: '苍蝇', tags: ['detail'], look: async (S, h, leader) => { looked.push(h.id + ':' + leader.cid); } },
          { id: 'vent', x: 560, y: 160, label: '通风口', tags: ['reach'], look: async (S, h, leader) => { looked.push(h.id + ':' + leader.cid); } },
        ],
        triggers: [{ id: 'tz', x0: 400, x1: 420, run: async () => { trig.push('tz'); } }],
      });
      G.party.set(['jotaro', 'kakyoin'], { leader: 'jotaro' });
      W().setStage(def, { player: G.party.leader(), x: 100, y: 162 });
      free(true);
      const advance = async (s) => { for (let i = 0; i < Math.round(s * 60); i++) { step(1); await Promise.resolve(); } };
      await advance(0.3);
      const near1 = W().near && W().near.label;
      tap('ok'); await advance(0.3);
      // U：承太郎在苍蝇旁（detail 对得上）
      W().player.x = 110; await advance(0.1);
      const ready1 = G.party.lookReady();
      const look1 = W().findLook() && W().findLook().id;
      tap('special'); await advance(0.4);
      const cd1 = G.party.lookCd.jotaro;
      tap('special'); await advance(0.1);   // 冷却中：没反应
      const ev1 = G.dbg.counts.investigate || 0;
      // 走远一点按 U：对不上 → 口头禅
      const p = W().player;
      p.x = 260; await advance(1.2);
      tap('special'); await advance(0.4);
      const missLine = G.S.log.filter((l) => l[0] === 'say').map((l) => l[2]);
      // 亮替身：NPC 荷莉 onStand
      p.x = 180; await advance(0.2);
      tap('attack'); await advance(0.6);
      cap('亮替身：荷莉 onStand');
      // 普通 NPC（没写 onStand）走 G.LOOK.onStandDefault
      p.x = 450; await advance(0.1);
      tap('attack'); await advance(0.6);
      // 触发区
      p.x = 405; await advance(0.3);
      // 可破坏物：J 三下打碎
      p.x = 310; p.facing = 1; await advance(0.3);
      for (let i = 0; i < 4; i++) { tap('attack'); await advance(0.45); }
      cap('自由走动 J 打碎水管（碎帧）');
      const pipe = W().stage.find('pipe');
      // 换花京院去通风口（reach）
      p.x = 540; await advance(0.2);
      G.party.setLeader('kakyoin', { force: true });
      W().player.x = 545; await advance(0.5);
      tap('special'); await advance(0.4);
      return { near1, used, ready1, look1, looked, cd1: +cd1.toFixed(2), ev1, missLine, stood, defaultReact: G.S.log.filter((l) => l[0] === 'onStandDefault'),
        trig, hits, breaks, pipe: pipe ? { hp: pipe.hp, frozen: pipe.frozen, state: pipe.state, team: pipe.team } : null,
        objects: W().objects().length, events: G.dbg.events.filter((e) => e.type === 'investigate' || e.type === 'look_missing'), sheet: sheet(2) };
    },

    // ⑦ 背景类型：pano / petals / pick / strip / image flicker / glow / stars / clouds / tint(key) / neon / reflect
    bgTypes() {
      resetWorld();
      free(false);
      const out = {};
      W().setStage(stage('types2_p4', 'p4_types', { x0: 0, x1: 640 }), {});
      sec(0.5); cap('p4_types：stars / clouds / wrap(h) / strip / image flicker / glow / pick');
      W().stage.state.night = 0.6; W().stage.state.p = 0.4; sec(0.2); cap('tint key=night 0.6，pick values → 0.3 那张');
      W().stage.camX = 200; W().player = null; W().stage.camTarget = 200; sec(0.5); cap('camX 200');
      W().setStage(stage('school_p4_pro', 'school_gate', { x0: 0, x1: 480 }), {});
      W().stage.camTarget = 0; sec(1.2); cap('校门 camX 0 + 花瓣');
      W().stage.camTarget = 160; sec(1.2); cap('校门 camX 160');
      W().setStage(stage('jail2_p4_pro', 'jail_cell', {}), {});
      const picks = [];
      for (const b of [0, 0.14, 0.5, 1]) { W().stage.state.bend = b; sec(0.05); picks.push(b); cap('拘留所 bend ' + b); }
      W().setStage(stage('hk2_p4', 'hongkong_night', { x0: 0, x1: 960 }), {});
      W().stage.camTarget = 0; sec(0.3); cap('香港 camX 0：霓虹 + 倒影');
      W().stage.camTarget = 330; sec(0.6); cap('香港 camX 330');
      W().stage.camTarget = 640; sec(0.6); cap('香港 camX 640（一周期）');
      out.badTypes = G.dbg.events.filter((e) => e.type === 'bg_type_missing');
      out.sheet = sheet(3);
      return out;
    },

    // ⑧ 时停 over pass：被冻住的人加描边、能动的人全彩画在变色的世界上
    overPass() {
      resetWorld();
      W().setStage(stage('hk3_p4', 'hongkong_night', { x0: 0, x1: 960 }), {});
      G.party.set(['jotaro', 'kakyoin'], { leader: 'jotaro' });
      W().setStage(stage('hk3_p4', 'hongkong_night', { x0: 0, x1: 960 }), { player: G.party.leader(), x: 150, y: 164 });
      const e = new G.Actor('dio', 220, 164, { team: 'enemy', facing: -1, stand: 'theworld' });
      W().stage.add(e);
      free(false);
      const jo = W().player;
      jo.stand.summon({ dur: 0.01 }); e.stand.summon({ dur: 0.01 }); sec(0.3);
      G.time.__set('stopped', [jo]);
      jo.stand.act('rush');
      sec(0.3);
      cap('时停中：承太郎 + 白金之星全彩（over pass），DIO 冻住描边');
      G.time.__set(null);
      return { sheet: sheet(1) };
    },

    // ⑨ 30 个角色同屏 canvas pass 耗时
    perf() {
      resetWorld();
      W().setStage(stage('hk4_p4', 'hongkong_night', { x0: 0, x1: 960 }), {});
      const cids = ['jotaro', 'joseph', 'avdol', 'kakyoin', 'polnareff', 'iggy', 'dio', 'holly', 'enya', 'mariah'];
      for (let i = 0; i < 30; i++) {
        const a = new G.Actor(cids[i % cids.length], 20 + i * 10, 152 + (i % 6) * 4, { facing: i % 2 ? 1 : -1 });
        if (a.stand && i % 3 === 0) a.stand.summon({ dur: 0.01 });
        if (i % 5 === 0) a.ghostOn = true;
        W().stage.add(a);
      }
      W().stage.camTarget = 0;
      free(false);
      step(30);
      G.__perf.canvasMs.length = 0; G.__perf.renderMs.length = 0;
      for (let i = 0; i < 240; i++) { for (const a of W().stage.actors) if (a.ghostOn) a.x += (i % 40 < 20 ? 1 : -1); step(1); }
      const avg = (arr) => arr.reduce((s, v) => s + v, 0) / arr.length;
      cap('30 人同屏');
      return { canvasAvgMs: +avg(G.__perf.canvasMs).toFixed(3), canvasMaxMs: +Math.max(...G.__perf.canvasMs).toFixed(3), renderAvgMs: +avg(G.__perf.renderMs).toFixed(3), sheet: sheet(1) };
    },

    invariants() {
      resetWorld();
      G.party.set(['jotaro', 'joseph', 'avdol', 'kakyoin', 'polnareff'], { leader: 'jotaro' });
      W().setStage(stage('bounds_p4_pro', 'p4_types', { x0: 0, x1: 320 }), { player: G.party.leader(), x: 8, y: 160 });
      const st = W().stage, p = W().player;
      const bound = () => G.party.members.every((a) => a.x >= st.x0 + 8 && a.x <= st.x1 - 8 && a.y >= st.yMin && a.y <= st.yMax);
      const entryBound = bound();
      for (const a of G.party.members) W().move(a, -1000, 1000, true);
      const freeBound = bound();
      st.lock = { x0: 100, x1: 220 };
      p.x = 160; W().move(p, -1000, 0); const battleLeft = p.x;
      W().move(p, 1000, 0); const battleRight = p.x;
      W().move(p, -1000, 0, true); const freeLeft = p.x;
      st.lock = null;
      free(false);
      p.stand.summon({ dur: 0.01 }); step(3);
      p.stopT = 1 / 120;
      const before = [p.ownT, p.animT, p.stand.poseT, p.stand.x];
      p.invuln = p.iframe = p.rootT = p.stunT = p.dodgeCd = 1;
      step(1);
      const stopStep = JSON.stringify(before) === JSON.stringify([p.ownT, p.animT, p.stand.poseT, p.stand.x]) && p.stopT === 0;
      const stopTimers = [p.invuln, p.iframe, p.rootT, p.stunT, p.dodgeCd].every((v) => v === 1);
      step(1);
      const resumed = p.ownT > before[0] && p.stand.poseT > before[2];
      const a = new G.Actor('dio', 170, 164, { team: 'enemy' });
      const b = new G.Actor('dio', 172, 164, { team: 'enemy' });
      st.add(a); st.add(b);
      G.time.__set('stopped', [p]);
      const frozenPositions = [a.x, a.y, b.x, b.y];
      a.invuln = a.rootT = 1;
      step(30);
      const frozenSeparation = JSON.stringify(frozenPositions) === JSON.stringify([a.x, a.y, b.x, b.y]);
      const frozenTimers = a.invuln === 1 && a.rootT === 1 && a.ownT === 0;
      G.time.__set('stopped', [p, b]); step(1);
      const movableSeparation = a.x === frozenPositions[0] && b.x > frozenPositions[2];
      G.time.__set(null);
      const dmgMul = () => 0.5, targetPick = () => p, onHitBy = () => 'evade', onShotNear = () => true;
      G.KITS.p4_kit = { hp: 99, speed: 81, dmgMul, targetPick, onHitBy, onShotNear, fly: { z: 12 }, armor: 'attack', koStyle: 'faint', standPos: { dx: 20, z: 10 } };
      const kitActor = new G.Actor('kakyoin', 200, 164, { kit: 'p4_kit' });
      const kitInherited = kitActor.hp === 99 && kitActor.speed === 81 && kitActor.dmgMul === dmgMul && kitActor.targetPick === targetPick &&
        kitActor.onHitBy === onHitBy && kitActor.onShotNear === onShotNear && kitActor.fly.z === 12 && kitActor.armor === 'attack' && kitActor.koStyle === 'faint' && kitActor.standPos.dx === 20;
      const explicit = new G.Actor('kakyoin', 200, 164, { kit: 'p4_kit', dmgMul: null, targetPick: null, fly: null, armor: false, standPos: null });
      const override = explicit.dmgMul === null && explicit.targetPick === null && explicit.fly === null && explicit.armor === false && explicit.standPos === null;
      const objectKit = new G.Actor('kakyoin', 220, 164, { kit: G.KITS.p4_kit });
      const objectKitInherited = objectKit.kit === G.KITS.p4_kit && objectKit.hp === 99 && objectKit.speed === 81 && objectKit.targetPick === targetPick;
      delete G.KITS.p4_kit;
      const object = new G.Actor('prop:jail_pipe', 240, 164, { team: 'object' });
      const ally = new G.Actor('kakyoin', 250, 164, { team: 'ally' });
      const npc = new G.Actor('holly', 260, 164, { team: 'npc' });
      st.add(object); st.add(ally); st.add(npc);
      a.rootT = 0; W().slow = 0.25;
      const clocks = [p, a, ally, npc, object].map((x) => x.ownT);
      let tickDt = 0; W().ticks.push((dt) => { tickDt = dt; return true; });
      step(1);
      const clockDelta = [p, a, ally, npc, object].map((x, i) => +(x.ownT - clocks[i]).toFixed(6));
      W().slow = 1;
      return { entryBound, freeBound, battleLeft, battleRight, freeLeft, stopStep, stopTimers, resumed, frozenSeparation, frozenTimers,
        movableSeparation, kitInherited, objectKitInherited, override, clockDelta, tickDt };
    },

    dbg() { return { missingImg: [...G.dbg.missingImg], missingHead: [...G.dbg.missingHead], fallbacks: [...G.dbg.animFallbacks], log: G.S.log.slice(-20) }; },
  });
})();
