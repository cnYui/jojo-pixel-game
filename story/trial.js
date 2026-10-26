// 星尘试炼：子菜单 / 编队 / 逐关流程 / 永久倒下 / 休息与结算。
//   这一层只负责“试炼自己的规则和界面”，每一关的布景与战斗配置由各章登记的 G.TRIAL_SRC[id] 提供，
//   流程只按 story/trial_stages.js 的关卡表去取，不复制任何一章的战斗数值。
'use strict';
(function () {
  const G = window.G;
  const T = G.TRIAL = G.TRIAL || {};
  const KEY = 'trial';
  const RANKS = ['C', 'B', 'A', 'S'];

  // 六张角色卡：承太郎必选（锁），其余选 0–2 人；顺序也是编队顺序（承太郎永远第一）。
  const ROSTER = [
    { cid: 'jotaro', name: '承太郎', stand: '白金之星·世界' },
    { cid: 'polnareff', name: '波鲁纳雷夫', stand: '银色战车' },
    { cid: 'joseph', name: '乔瑟夫', stand: '隐者之紫' },
    { cid: 'kakyoin', name: '花京院', stand: '绿色法皇' },
    { cid: 'avdol', name: '阿布德尔', stand: '红色魔术师' },
    { cid: 'iggy', name: '伊奇', stand: '愚者' },
  ];
  const rosterOf = cid => ROSTER.find(r => r.cid === cid) || { cid, name: cid, stand: '' };
  const nameOf = cid => (G.NAMES && G.NAMES[cid]) || (G.D && G.D.heroes && G.D.heroes[cid] && G.D.heroes[cid].short) || rosterOf(cid).name || cid;
  const mmss = t => { t = Math.max(0, Math.round(t)); return Math.floor(t / 60) + ':' + String(t % 60).padStart(2, '0'); };
  const snd = (name, o) => { if (G.audio && G.audio.sfx) G.audio.sfx(name, o); };
  const rankVal = r => Math.max(0, RANKS.indexOf(r));

  // 存档（键 trial）：读的时候逐字段校验，旧包 / 手改坏的字段只丢那一项，不整个存档作废。
  const blankSave = () => ({ v: 1, runs: 0, fails: 0, clears: 0,
    best: { stage: 0, time: 0, squad: [] }, ranks: {} });
  function readSave() {
    const s = G.store.get(KEY, null), b = blankSave();
    if (!s || typeof s !== 'object' || s.v !== 1) return b;
    const num = (v, d) => (Number.isFinite(v) && v >= 0 ? Math.round(v) : d);
    b.runs = num(s.runs, 0); b.fails = num(s.fails, 0); b.clears = num(s.clears, 0);
    if (s.best && typeof s.best === 'object') {
      b.best.stage = num(s.best.stage, 0);
      b.best.time = num(s.best.time, 0);
      if (Array.isArray(s.best.squad)) b.best.squad = s.best.squad.filter(x => typeof x === 'string').slice(0, 3);
    }
    if (s.ranks && typeof s.ranks === 'object') {
      for (const id in s.ranks) {
        const r = s.ranks[id];
        if (r && typeof r === 'object' && RANKS.indexOf(r.rank) >= 0) b.ranks[id] = { rank: r.rank, score: num(r.score, 0), time: num(r.time, 0) };
      }
    }
    return b;
  }
  let save = readSave();

  let rulesSeen = false;          // 本次打开页面后只在第一次进「星尘试炼」时弹规则卡
  let curDef = null, curN = 0;    // 当前这一关（onWon 里把真实战斗 id 映射回关卡 id）
  let falling = [];               // 正在播“倒下 0.5 s → 淡出 0.6 s”的我方，tick 每帧推进
  let hudObj = null;              // 没有别的插入画面时，时停倒数自己占一层
  let hudTarget = null, hudOrig = null, hudPatched = null;   // 有别的插入画面时，在它的 draw 末尾追加，保住 === 身份
  let flawlessStage = -1, flawlessAdded = false, stageDirty = false;
  let stopSeen = false;           // 一次时停只累加一次 run.sptw

  // 评价比较：先等级、再分数、最后用时；存档和本轮都按同一口径保留最好的一次。
  function better(a, b) {
    if (!b) return true;
    const d = rankVal(a.rank) - rankVal(b.rank);
    if (d) return d > 0;
    if ((a.score || 0) !== (b.score || 0)) return (a.score || 0) > (b.score || 0);
    return (a.time || 0) < (b.time || 0);
  }

  Object.assign(T, {
    active: false,
    CFG: { PERMADEATH: true, SQUAD_MAX: 3, SCALE_PER_STAGE: 0.02, SCALE_MAX: 1.6, CHECKPOINT: 0, FAST: 2700, FAST2: 1800 },
    stages: T.stages || [],
    run: null,
    save,
    stamp: null,

    unlocked() { return !!(G.progress && G.progress.clear) && !G.DEMO; },

    // 每关敌人伤害系数：原战斗的 dmgScale × 1 + 0.02×(N−1) × tune，封顶 SCALE_MAX。
    stageScale(n) {
      const c = this.CFG;
      return Math.min(c.SCALE_MAX, 1 + c.SCALE_PER_STAGE * ((n || 1) - 1));
    },

    // ================================================================ 标题子菜单
    async menu() {
      if (!this.unlocked()) { await G.ui.notice({ title: '星尘试炼', text: '打穿终章以后开放。' }); return null; }
      if (!rulesSeen) { rulesSeen = true; await this.rules(); }
      for (;;) {
        const i = await G.ui.openMenu('星尘试炼', ['开始试炼', '规则', '最高纪录', '返回'], { escIndex: 3,
          note: '固定关卡顺序　·　倒下的伙伴不会回来' });
        if (i === 3) return null;
        if (i === 1) { await this.rules(); continue; }
        if (i === 2) { await this.record(); continue; }
        const squad = await this.squadPage();
        if (squad) return squad;      // 取消编队 = 回子菜单，不直接退回标题
      }
    },
    async rules() {
      const pages = [
        'SPW 财团收录了五十天旅途里的每一场战斗。这里，旅途里的强敌会一个接一个重现。',
        '每一关打赢，活着的伙伴恢复全部体力。倒下的伙伴不会回来。',
        '承太郎倒下，试炼就从头开始。',
      ];
      for (let i = 0; i < pages.length; i++) await G.ui.notice({ title: '星尘试炼　规则 ' + (i + 1) + ' / ' + pages.length, text: pages[i] });
    },
    async record() {
      const s = this.save || save;
      const far = Math.min(s.best.stage || 0, this.stages.length);
      const rows = [far > 0 ? '最远　第 ' + far + ' 关　' + this.stages[far - 1].title.replace(/^VS /, '') : '最远　—',
        '通关　' + (s.clears || 0) + ' 次',
        s.best.time > 0 ? '最快　' + mmss(s.best.time) + '（队伍：' + (s.best.squad || []).map(nameOf).join(' · ') + '）' : '最快　—'];
      if (G.ach && G.ach.list) {
        const list = G.ach.list('trial') || [];
        if (list.length) rows.push('试炼成就　' + list.filter(d => G.ach.has && G.ach.has(d.id)).length + ' / ' + list.length);
      }
      await G.ui.notice({ title: '星尘试炼　最高纪录', text: rows.join('\n') });
    },

    // ================================================================ 编队小页
    // 用独立 scene 而不是 openMenu：要画 6 张卡、支持勾选和触屏点选；返回前把标题场景还原，
    // 标题菜单协程还在 await 这一页，不能让它以为已经离开标题。
    squadPage() {
      return new Promise(resolve => {
        const prevScene = G.scene;
        const sel = { jotaro: true, polnareff: true };
        const total = ROSTER.length;
        let idx = 0, lastCol = 0, done = false;

        const finish = val => {
          if (done) return;
          done = true;
          // 取消键自己吃掉，别让刚还原的标题菜单又收到同一次 Esc / 返回。
          if (G.input) { G.input.consume('attack'); G.input.consumeOk(); G.input.consume('pause'); G.input.consume('back'); G.input.lockOk(.25); }
          G.setScene(prevScene);
          resolve(val);
        };
        const toggle = i => {
          const cid = ROSTER[i].cid;
          if (cid === 'jotaro') { G.ui.hint('承太郎必须出战。', 1.5); snd('menu_cancel', { vol: .5 }); return; }
          if (sel[cid]) { delete sel[cid]; snd('menu_cancel', { vol: .5 }); return; }
          if (Object.keys(sel).length >= T.CFG.SQUAD_MAX) { G.ui.hint('最多三人出战。', 1.5); snd('menu_cancel', { vol: .5 }); return; }
          sel[cid] = true; snd('menu_confirm', { vol: .5 });
        };
        const begin = () => finish(['jotaro'].concat(ROSTER.filter(r => r.cid !== 'jotaro' && sel[r.cid]).map(r => r.cid)));
        const move = dir => {
          if (dir === 'left' || dir === 'right') {
            if (idx >= total) return;
            const row = Math.floor(idx / 3), col = idx % 3;
            idx = row * 3 + (col + (dir === 'left' ? 2 : 1)) % 3;
            lastCol = idx % 3;
          } else if (dir === 'up') {
            if (idx >= total) idx = 3 + lastCol;
            else if (idx >= 3) idx -= 3;
            if (idx < total) lastCol = idx % 3;
          } else {
            if (idx < 3) idx += 3;
            else if (idx < total) idx = total;
            if (idx < total) lastCol = idx % 3;
          }
          snd('menu_move', { vol: .5 });
        };
        const startRect = () => ({ x: 240, y: 292, w: 160, h: 28 });
        const cardRect = i => ({ x: 14 + (i % 3) * 204, y: 58 + Math.floor(i / 3) * 116, w: 194, h: 106 });

        const scene = {
          name: 'title',        // 触屏沿用标题菜单那一套（tap / 暂停键 = 返回）
          mode: 'squad',
          frozen: false,
          update(dt) {
            G.ui.update(dt);
            const I = G.input;
            if (!I) return;
            if (I.hit('pause') || I.hit('back')) { finish(null); return; }
            if (I.tap) {
              const t = I.tap;
              for (let i = 0; i < total; i++) {
                const r = cardRect(i);
                if (t.x >= r.x && t.x <= r.x + r.w && t.y >= r.y && t.y <= r.y + r.h) { idx = i; lastCol = i % 3; toggle(i); return; }
              }
              const b = startRect();
              if (t.x >= b.x && t.x <= b.x + b.w && t.y >= b.y && t.y <= b.y + b.h) { idx = total; begin(); }
              return;
            }
            if (I.hit('left')) move('left');
            else if (I.hit('right')) move('right');
            else if (I.hit('up')) move('up');
            else if (I.hit('down')) move('down');
            if (I.hit('attack') || (I.hit('ok') && !I.okLocked())) {
              I.consume('attack'); I.consumeOk();
              if (idx >= total) begin(); else toggle(idx);
            }
          },
          drawWorld(g) { g.fillStyle = '#08060f'; g.fillRect(0, 0, 320, 180); },
          drawUI(g) {
            const F16 = G.f16, F12 = G.f12;
            g.fillStyle = '#08060f'; g.fillRect(0, 0, 640, 360);
            g.fillStyle = 'rgba(90,70,160,0.07)';
            for (let x = -160; x < 720; x += 48) g.fillRect(x, 0, 10, 360);
            if (!F16) return;
            F16.draw(g, '星尘试炼　编队', 320, 8, '#ffe9a8', { align: 'center', outline: '#140c18' });
            if (F12) F12.draw(g, '承太郎必须出战　·　再选 0-2 人（最多 3 人）', 320, 30, '#cfc8dc', { align: 'center', outline: '#140c18' });

            ROSTER.forEach((r, i) => {
              const R = cardRect(i), on = !!sel[r.cid], cur = idx === i;
              // 卡片底：选中偏暖色，和未选中的冷色一眼分开
              g.fillStyle = on ? 'rgba(48,36,22,0.95)' : 'rgba(18,14,34,0.92)';
              g.fillRect(R.x, R.y, R.w, R.h);
              const frame = (x, y, w, h, col) => {
                g.fillStyle = col;
                g.fillRect(x, y, w, 2); g.fillRect(x, y + h - 2, w, 2);
                g.fillRect(x, y, 2, h); g.fillRect(x + w - 2, y, 2, h);
              };
              frame(R.x, R.y, R.w, R.h, on ? '#ffd040' : '#4a4060');
              if (cur) frame(R.x - 3, R.y - 3, R.w + 6, R.h + 6, '#ffffff');
              if (G.atlas) {
                const A = G.atlas(r.cid);
                if (A && A.draw) A.draw(g, 'idle', 0, R.x + 52, R.y + R.h - 10, { scale: .85 });
              }
              F16.draw(g, r.name, R.x + 96, R.y + 18, on ? '#fff4d6' : '#bdb6c8', { outline: '#140c18' });
              if (F12) F12.draw(g, r.stand, R.x + 96, R.y + 44, on ? '#ffd9a0' : '#8f89a4', { outline: '#140c18' });
              if (F12) F12.draw(g, r.cid === 'jotaro' ? '队长　必选' : on ? '出战' : '待选', R.x + 96, R.y + 72,
                r.cid === 'jotaro' ? '#ffe040' : on ? '#9fffb0' : '#77708c', { outline: '#140c18' });
              if (r.cid === 'jotaro') {       // 锁：承太郎不允许取消，给玩家一个明确的“别按了”的记号
                const lx = R.x + R.w - 20, ly = R.y + 10;
                g.fillStyle = '#cfc8dc';
                g.fillRect(lx + 2, ly, 7, 2); g.fillRect(lx, ly + 2, 2, 4); g.fillRect(lx + 9, ly + 2, 2, 4);
                g.fillRect(lx - 1, ly + 5, 13, 9);
                g.fillStyle = '#0c0a14'; g.fillRect(lx + 2, ly + 8, 2, 3); g.fillRect(lx + 6, ly + 8, 2, 3);
              }
            });

            const b = startRect(), curB = idx >= total;
            g.fillStyle = curB ? 'rgba(60,44,18,0.96)' : 'rgba(18,14,34,0.92)';
            g.fillRect(b.x, b.y, b.w, b.h);
            G.ui.box(g, b.x, b.y, b.x + b.w, b.y + b.h, { fill: curB ? 'rgba(60,44,18,0.96)' : 'rgba(18,14,34,0.92)', border: curB ? '#ffffff' : '#ffd040' });
            F16.draw(g, '开始', b.x + b.w / 2, b.y + 5, curB ? '#fff' : '#ffe9a8', { align: 'center', outline: '#140c18' });
            if (F12) F12.draw(g, '←→↑↓ 选择　J / Enter 勾选　Esc 返回　·　触屏点卡片 / 开始', 320, 332, '#8f89a4', { align: 'center', outline: '#140c18' });
            G.ui.draw(g);     // 提示（“承太郎必须出战。”“最多三人出战。”）
          },
          drawTop(g) { G.ui.drawTop(g); },
        };
        if (G.input) G.input.lockOk(.2);
        G.setScene(scene);
      });
    },

    // ================================================================ 一轮
    begin(squad) {
      const arr = (Array.isArray(squad) ? squad : []).filter(x => typeof x === 'string');
      if (arr[0] !== 'jotaro') throw new Error('试炼编队必须把承太郎放在第一位');
      const clean = [];
      arr.forEach(cid => { if (ROSTER.some(r => r.cid === cid) && clean.indexOf(cid) < 0) clean.push(cid); });
      if (clean[0] !== 'jotaro') throw new Error('试炼编队缺少承太郎');
      clean.length = Math.min(clean.length, this.CFG.SQUAD_MAX);
      this.run = { squad: clean.slice(), alive: clean.slice(), lead: 'jotaro', stage: 0, stages: 0, t0: G.clk.ui,
        downs: 0, flawless: 0, sptw: 0, ranks: [], time: 0 };
      this.active = true;
      this.stamp = null;
      curDef = null; curN = 0; stopSeen = false; falling = [];
      this._dropHud();
      save.runs = (save.runs || 0) + 1;
      persist();
      if (G.SPTW) this.SPTW = G.SPTW;   // 实施文档 §五 的 G.TRIAL.SPTW 别名，最终关等共用一处
      // 只建一次：承太郎的 kit 副本把 U 换成白金之星·世界；退出试炼后 party.reset 会清空 pool，剧情仍用原 kit。
      if (G.KITS && G.KITS.jotaro && G.SPTW && G.SPTW.kitSpecial && !G.KITS.jotaro_sptw) {
        G.KITS.jotaro_sptw = Object.assign({}, G.KITS.jotaro, { special: G.SPTW.kitSpecial });
      }
      if (G.ach && G.ach.emit) G.ach.emit('trial_start', { squad: clean.slice() });
      return this.run;
    },

    async play(S) {
      const run = this.run;
      if (!run) throw new Error('星尘试炼还没有开始');
      if (!this.stages.length) throw new Error('星尘试炼没有关卡');
      this.active = true;
      const M = this.stages.length;

      for (let i = 0; i < M; i++) {
        const n = i + 1, def = this.stages[i];
        const src = G.TRIAL_SRC && G.TRIAL_SRC[def.id];
        if (!src) throw new Error('星尘试炼缺少战斗配置：' + def.id);
        curDef = def; curN = n;
        run.stage = n; run.stages = n;
        flawlessStage = n; flawlessAdded = false; stageDirty = false;
        stopSeen = false;
        if ((save.best.stage || 0) < n) { save.best.stage = n; persist(); }

        // 每关重置：试炼不继承上一关的剧情 flag / 机关状态；背景包按关卡表的 pack 补载。
        G.flags = {};
        G.midGame = null; G.lateGame = null;
        if (G.world) G.world.free = false;      // 名牌 / 休息期间不接受自由走动，流程全自动
        await G.res.loadPack('bg_common');
        if (G.MID && G.MID.ensureBg && src.pack) await G.MID.ensureBg(src.pack);
        // 休息的黑场会一直盖到下一关：先淡回来，名牌才看得见（不 await，和名牌一起出现）。
        if (G.fadeA > 0 && G.fade && G.cancelIgnore) G.fade(0, .25).catch(G.cancelIgnore);
        await this.banner(def, n);

        const lead = def.solo ? 'jotaro' : (run.alive.indexOf(run.lead) >= 0 ? run.lead : run.alive[0]);
        if (!lead) throw new Error('星尘试炼的队伍已经空了');
        run.lead = lead;
        S.party(run.alive, { leader: lead });
        for (const cid of run.alive) {     // 重开一轮时复用的 Actor 不能带着上一轮的倒下标记 / 隐身 / 停步
          const a = G.party.get(cid);
          if (a) {
            delete a._trialDown;
            a.alpha = 1; a.remove = false; a.dead = false; a.hp = a.maxHp;
            a.state = 'idle'; a.hold = false; a.atk = null; a.iframe = 0;
            if (a.play) a.play(a.idleAnim || 'idle');
          }
        }
        const jot = G.party.get('jotaro');
        if (jot && !def.noStop && G.KITS && G.KITS.jotaro_sptw) jot.kit = G.KITS.jotaro_sptw;

        const wrap = this._wrap(run, def, n);
        let failed = false;
        try {
          if (typeof src.run === 'function') await src.run(S, { trial: true, wrap });
          else {
            if (typeof src.setup === 'function') await src.setup(S, { trial: true });
            const spec = typeof src.spec === 'function' ? await src.spec({ trial: true }) : {};
            await S.fight(wrap(spec));
          }
        } catch (e) {
          if (e && e.name === 'TrialFailed') failed = true;
          else throw e;
        }
        run.lead = this._liveLead(S, run);
        this._dropHud();
        if (failed) {
          const r = await this._fail(def, n);     // 倒下的人先留在画面上，失败演出播完再清
          if (r !== 'revive') return r;
          // 复活：整队（含已永久倒下的队友）回到名单，仍从这一关重打；倒下数是真实记录，不能洗白。
          run.alive = run.squad.slice();
          run.lead = 'jotaro';
          run.revives = (run.revives || 0) + 1;
          this.active = true;                     // fight.js 的 failed() 会看它，下一场仍按试炼失败处理
          this._flushFalling();                   // 先收掉淡出标记，下面的每关重置才能把队友重新显示出来
          if (G.ach && G.ach.emit) G.ach.emit('trial_revive', { n, squad: run.squad.slice(), revives: run.revives });
          i--;                                    // 回退一格让 for 的 i++ 回到同一关，关卡号 / 评价等每关状态照常重新初始化
          continue;
        }
        this._flushFalling();

        const rec = this._lastRank(def.id);
        if (G.ach && G.ach.emit) {
          G.ach.emit('trial_stage', { n: run.stage, id: def.id, rank: rec ? rec.rank : null, hurt: rec ? rec.hurt : 0,
            alive: run.alive.length, squad: run.squad.slice(), stages: run.stages, flawless: run.flawless,
            sptw: run.sptw, ranks: run.ranks.slice() });
        }
        if (n === M) {
          await G.wait(.8, 'ui');
          this._clearStamp();
          return this._clear(def);
        }
        await G.wait(.8, 'ui');     // 先让右侧评价牌亮 0.8 s，再进休息
        this._clearStamp();
        await this._rest(S, def, n, rec);
      }
      return 'cleared';
    },

    // S.fight 的胜利回调：只写试炼自己的存档 / 本轮统计，不碰 G.EXTRA 的 won / ranks。
    onWon(c, attempt) {
      const def = curDef || this.stages.find(d => d.id === c.id) || null;
      const n = curN || (def ? this.stages.indexOf(def) + 1 : 0);
      const par = (def && def.par) || (c.spec && c.spec.par) || 90;
      let rec = null;
      if (c.stats && G.EXTRA && G.EXTRA.grade) {
        rec = G.EXTRA.grade(c.stats, Object.assign({}, c.spec || {}, { par }), c.t, false);
        rec.attempts = (attempt || 0) + 1;
      }
      const id = def ? def.id : c.id;
      if (rec) {
        const entry = { id, n, rank: rec.rank, score: rec.score, time: Math.round(rec.time), hurt: rec.hurt };
        if (this.run) {
          const at = this.run.ranks.findIndex(r => r.id === id);
          if (at < 0) this.run.ranks.push(entry);
          else if (better(rec, this.run.ranks[at])) this.run.ranks[at] = entry;
        }
        const bestSave = better(rec, save.ranks[id]);
        if (bestSave) {
          save.ranks[id] = { rank: rec.rank, score: rec.score, time: Math.round(rec.time) };
        }
        rec.best = bestSave;      // G.EXTRA.drawUI 的“新纪录！”小字
        persist();
        // 一轮里“无伤”按关算：最终关有三段，任一段挨打就不算这一关无伤；
        // 前一段已经记过无伤、后一段挨打时要把这一关的计数退回来。
        if (flawlessStage !== n) { flawlessStage = n; flawlessAdded = false; stageDirty = false; }
        if (rec.hurt > 0 && !stageDirty) {
          stageDirty = true;
          if (flawlessAdded) { flawlessAdded = false; if (this.run) this.run.flawless = Math.max(0, this.run.flawless - 1); }
        }
        if (!stageDirty && !flawlessAdded) { flawlessAdded = true; if (this.run) this.run.flawless++; }
        this.stamp = { rec, t0: G.clk.ui, dur: 4 };
        // 评价牌挂在 G.EXTRA 的右上角小牌上（G.ui.draw 只调 E.drawUI）：试炼不另造一套画法。
        if (G.EXTRA) G.EXTRA.stamp = this.stamp;
        snd(rec.rank === 'S' || rec.rank === 'A' ? 'ding' : 'pop', { vol: .6 });
      }
      if (!c.autowin && G.ach && G.ach.emit && this.run) {
        const p = c.player || {};
        G.ach.emit('fight_won', {
          id: c.id, chapter: def ? def.chapter : '', mode: 'trial',
          rank: rec ? rec.rank : null, score: rec ? rec.score : 0, time: rec ? rec.time : c.t,
          hurt: rec ? rec.hurt : 0, hpLeft: p.maxHp ? Math.max(0, Math.min(1, (p.hp || 0) / p.maxHp)) : 0,
          parry: rec ? rec.parry : 0, graze: rec ? rec.graze : 0, rushHits: rec ? rec.rushHits : 0,
          special: rec ? rec.special : 0, attempts: rec ? rec.attempts : 1, assist: false, losable: true,
          lead: p.cid || this.run.lead, trial: true,
        });
      }
      return rec;
    },

    // 每帧：倒下判定 + 白金之星·世界的倒数与“本轮停了几次”。
    tick(c, dt) {
      const run = this.run;
      if (!run) return;
      if (this.active && G.ui) this._ensureHud();
      const tm = G.time;
      const isStop = !!(tm && tm.active && tm.by && tm.by.cid === 'jotaro');
      if (isStop && !stopSeen) { stopSeen = true; run.sptw++; }
      else if (!isStop) stopSeen = false;
      // 换队长后下一关的 lead 跟着走；队里已经没有当前队长时，用活着的第一人。
      const p = G.world && G.world.player;
      if (p && run.alive.indexOf(p.cid) >= 0) run.lead = p.cid;
      if (!this.CFG.PERMADEATH) return;
      for (const cid of run.alive.slice()) {
        const a = G.party && G.party.get ? G.party.get(cid) : null;
        if (a && !a._trialDown && a.hp <= 0) {
          if (this._fall(c, a)) return;      // 承太郎倒下 = 本轮结束，剩下的不用再判
        }
      }
      this._tickFalling(dt);
    },

    // 时停 ✘ 的关把承太郎的 U 换回欧拉欧拉；其余时候返回 null，让 actor 自己的 kit 生效。
    kitOverride(run, def) {
      if (!def || !def.noStop) return null;
      if (!G.KITS || !G.KITS.jotaro || !G.KITS.jotaro.special) return null;
      return { jotaro: { special: G.KITS.jotaro.special } };
    },

    reset() {
      this.active = false;
      this.run = null;
      this.stamp = null;
      curDef = null; curN = 0;
      falling = [];
      stopSeen = false;
      flawlessStage = -1; flawlessAdded = false; stageDirty = false;
      this._dropHud();
    },

    // 1.5 s 的 Boss 名牌：不按键、不阻塞输入之外的东西；开场锁 .5 s 确认键，免得上一关的连打吃进来。
    async banner(def, n) {
      const M = this.stages.length || 1;
      if (G.input && G.input.lockOk) G.input.lockOk(.5);
      await this._overlay(1.5, (g, t) => {
        const F16 = G.f16, F12 = G.f12;
        if (!F16) return;
        const a = Math.min(1, t / .15);
        g.save();
        g.globalAlpha = a;
        const x0 = 120, y0 = 18, x1 = 520, y1 = 86;
        G.ui.box(g, x0, y0, x1, y1, { fill: 'rgba(18,14,34,0.9)', border: '#ffd040' });
        F12 && F12.draw(g, '第 ' + n + ' 关 / ' + M, 320, y0 + 8, '#ffe9a8', { align: 'center', outline: '#140c18' });
        F16.draw(g, def.title, 320, y0 + 28, '#fff', { align: 'center', outline: '#140c18' });
        F12 && F12.draw(g, def.sub || '', 320, y0 + 54, '#96dcff', { align: 'center', outline: '#140c18' });
        g.restore();
      });
    },

    // ---------------------------------------------------------------- 内部：关卡包装 / 倒下 / 休息 / 结算
    _wrap(run, def, n) {
      return spec => {
        spec = spec || {};
        const ki = Object.assign({}, spec.kitOverride || {});
        const extra = def.solo ? null : T.kitOverride(run, def);
        if (extra) for (const cid in extra) ki[cid] = Object.assign({}, ki[cid] || {}, extra[cid]);
        const scale = T.stageScale(n) * (def.tune == null ? 1 : def.tune);
        return Object.assign({}, spec, {
          lead: run.lead,
          swap: !def.solo && run.alive.length > 1,
          allies: def.solo ? [] : run.alive.filter(cid => cid !== run.lead),
          bench: 'hide', vs: null, finish: spec.finish || 'ko', playerMinHp: 0, losable: true,
          dmgScale: (spec.dmgScale == null ? 1 : spec.dmgScale) * scale,
          kitOverride: ki,
          tick(c, dt) { if (typeof spec.tick === 'function') spec.tick(c, dt); T.tick(c, dt); },
        });
      };
    },
    _liveLead(S, run) {
      const p = S.player;
      if (p && run.alive.indexOf(p.cid) >= 0) return p.cid;
      return run.alive[0] || 'jotaro';
    },
    // 永久倒下：先摘出名单（Q 换人 / 下一关都不再出现），再播 0.5 s 倒下 + 0.6 s 淡出；
    //   party.remove 默认会立刻 a.remove，这里用 stay 让它留在画面上播完，赶在 2.2 s 自动复活前拿走。
    _fall(c, a) {
      const run = this.run;
      if (!run) return false;
      const cid = a.cid, at = run.alive.indexOf(cid);
      if (at < 0) return false;
      a._trialDown = true;
      const wasLead = !!(G.world && G.world.player === a);
      run.alive.splice(at, 1);
      run.downs++;
      if (G.party) G.party.remove(cid, { drop: true, stay: true });
      a.state = 'down'; a.hold = true; a.iframe = 999;
      if (a.play) a.play('down');
      falling.push({ a, t: 0 });
      if (run.lead === cid) run.lead = run.alive[0] || 'jotaro';
      if (G.ui && G.ui.hint) G.ui.hint(nameOf(cid) + '　倒下了。', 2);
      if (G.ach && G.ach.emit) G.ach.emit('trial_down', { cid, n: run.stage });
      if (cid === 'jotaro') {
        if (c && c.fail) c.fail('承太郎倒下了……');
        return true;
      }
      if (wasLead && run.alive.indexOf('jotaro') >= 0) {
        if (G.party) G.party.setLeader('jotaro', { force: true, silent: false });
        const j = G.party.get('jotaro');
        if (j) j.invuln = Math.max(j.invuln || 0, 1);
        run.lead = 'jotaro';
      }
      return false;
    },
    _tickFalling(dt) {
      for (let i = falling.length - 1; i >= 0; i--) {
        const f = falling[i];
        f.t += dt;
        if (f.t >= .5 && !f.hid) { f.hid = true; if (f.a.stand && f.a.stand.hide) f.a.stand.hide(); }
        if (f.t >= .5) f.a.alpha = Math.max(0, 1 - (f.t - .5) / .6);
        if (f.t >= 1.1) { f.a.alpha = 0; f.a.remove = true; falling.splice(i, 1); }
      }
    },
    _flushFalling() { falling.forEach(f => { f.a.alpha = 0; f.a.remove = true; }); falling = []; },

    _lastRank(id) {
      if (!this.run) return null;
      const r = this.run.ranks.find(x => x.id === id);
      return r ? { rank: r.rank, score: r.score, time: r.time, hurt: r.hurt, parry: 0, graze: 0, rushHits: 0, special: 0 } : null;
    },

    async _rest(S, def, n, rec) {
      const run = this.run;
      const cum = Math.max(0, Math.round(G.clk.ui - run.t0));
      await this._overlay(1.5, g => {
        const F16 = G.f16, F12 = G.f12;
        if (!F16) return;
        G.ui.box(g, 140, 110, 500, 230, { fill: 'rgba(18,14,34,0.9)', border: '#ffd040' });
        F16.draw(g, '第 ' + n + ' 关　通过！', 320, 124, '#ffe9a8', { align: 'center', outline: '#140c18' });
        if (rec) {
          g.save(); g.translate(196, 178); g.scale(2.4, 2.4);
          F16.draw(g, rec.rank, 0, 0, rec.rank === 'S' ? '#ffe040' : '#fff', { align: 'center', outline: '#140c18' });
          g.restore();
          F12 && F12.draw(g, '评价 ' + rec.rank, 236, 162, '#fff4d6', { outline: '#140c18' });
          F12 && F12.draw(g, '用时 ' + mmss(rec.time), 236, 180, '#ffe3a0', { outline: '#140c18' });
        } else if (F12) F12.draw(g, '评价 —', 236, 162, '#fff4d6', { outline: '#140c18' });
        F12 && F12.draw(g, '本轮 ' + mmss(cum), 488, 208, '#96dcff', { align: 'right', outline: '#140c18' });
      });
      // 回血 / 回能量：只对还活着的人；倒下的已经摘出 alive，不会回来。
      let any = false;
      for (const cid of run.alive) {
        const a = G.party.get(cid);
        if (!a) continue;
        a.hp = a.maxHp; a.energy = 0; a.state = 'idle'; a.atk = null; a.hold = false;
        if (a.play) a.play(a.idleAnim || 'idle');
        any = true;
      }
      if (any) {
        snd('sparkle', { vol: .7 });
        for (let k = 0; k < 4; k++) {
          for (const cid of run.alive) {
            const a = G.party.get(cid);
            if (a && S && S.fx) S.fx('glint', { x: a.x + (k % 2 ? 7 : -7), y: a.y - 24 - k * 3, size: 5 });
          }
          await G.wait(.2, 'ui');
        }
      } else await G.wait(.8, 'ui');
      await G.fade(1, .25);
      await G.wait(.25, 'ui');
    },

    async _fail(def, n) {
      const run = this.run;
      run.time = Math.max(0, Math.round(G.clk.ui - run.t0));
      // 先不记失败：玩家可能看广告复活，复活的这一轮不应该在存档里多一次 fails。
      this.active = false;
      if (G.world) { G.world.combat = false; G.world.free = false; }
      // fight.js 的 failed() 在试炼里直接返回 false，慢动作 / 褐色滤镜 / 失败音效由这里补上。
      if (G.slowAll) G.slowAll(.3, .5);
      await G.wait(.5, 'ui');
      const p = G.world && G.world.player;
      if (p) {
        p.state = 'down'; p.hold = true; p.iframe = 999;
        if (p.play) p.play('down');
        if (p.stand && p.stand.hide) p.stand.hide();
      }
      if (G.post && G.post.filter) G.post.filter('sepia', 1, { dur: .6 });
      if (G.audio && G.audio.cue) G.audio.cue('game_over_jingle');
      // 广告可用性只决定菜单长什么样；supported 自己保证不抛，这里再兜一层，异常按不可用处理。
      let adOK = false, revived = false, choice = 2;
      try {
        await G.ui.notice({ title: '试炼失败', minT: 1.2,
          text: '止步　第 ' + n + ' 关　' + def.title + '\n用时 ' + mmss(run.time) + '　　倒下 ' + run.downs + ' 人' });
        if (G.ads) {
          try { adOK = typeof G.ads.supported === 'function' && !!(await G.ads.supported()); }
          catch (e) { adOK = false; }
        }
        if (adOK) {
          // 复活放在第二项，但光标仍从「重新开始」开始；玩家连按确认键时不会直接看广告。
          for (;;) {
            choice = await G.ui.openMenu(null, ['重新开始', '看广告·全员复活', '重新编队', '回到标题'], { idx: 0, escIndex: 2 });
            if (choice !== 1) break;
            let res = null;
            try { res = await G.ads.watch('trial_revive'); }   // 广告最长可能 120 s，按约定不自己加超时
            catch (e) { res = { success: false, technical: true, reason: 'exception' }; }
            if (res && res.success) { revived = true; break; }
            if (res && res.technical) {      // 技术原因播不出来：不让玩家吃亏，免费复活
              await G.ui.notice({ text: '广告暂时无法播放，本次免费复活' });
              revived = true; break;
            }
            // 玩家关掉 / 跳过，或正在播另一个广告：回菜单重选，不复活也不记失败。
            await G.ui.notice({ text: '广告没有看完，没有复活' });
          }
        } else {
          choice = await G.ui.openMenu(null, ['重新开始', '重新编队', '回到标题'], { idx: 0, escIndex: 1 });
        }
      } finally {
        if (G.post && G.post.filter) G.post.filter('sepia', null);
        this._flushFalling();
      }
      if (revived) return 'revive';
      // 只有玩家最终放弃这一轮才落失败档 / 发 trial_over；复活分支在上面已经返回。
      save.fails = (save.fails || 0) + 1;
      persist();
      if (G.ach && G.ach.emit) G.ach.emit('trial_over', { n, id: def.id, downs: run.downs });
      if (adOK) return choice === 0 ? 'restart' : choice === 2 ? 'squad' : 'title';
      return choice === 0 ? 'restart' : choice === 1 ? 'squad' : 'title';
    },

    async _clear(def) {
      const run = this.run;
      run.time = Math.max(0, Math.round(G.clk.ui - run.t0));
      const prevBest = save.best.time || 0;
      const newBest = !prevBest || run.time < prevBest;
      save.clears = (save.clears || 0) + 1;
      save.best.stage = Math.max(save.best.stage || 0, this.stages.length);
      if (newBest) { save.best.time = run.time; save.best.squad = run.squad.slice(); }
      persist();
      if (G.ach && G.ach.emit) {
        G.ach.emit('trial_clear', { time: run.time, downs: run.downs, squad: run.squad.slice(),
          ranks: run.ranks.slice(), flawless: run.flawless, sptw: run.sptw, revives: run.revives || 0 });
      }
      this.active = false;
      const count = { S: 0, A: 0, B: 0, C: 0 };
      run.ranks.forEach(r => { if (r && count[r.rank] != null) count[r.rank]++; });
      const lines = ['用时 ' + mmss(run.time) + '　　倒下 ' + run.downs + ' 人',
        '各关评价：S×' + count.S + '　A×' + count.A + '　B×' + count.B + '　C×' + count.C,
        '编队：' + run.squad.map(nameOf).join(' · ')];
      if (newBest) lines.push('（新纪录！）');
      if (G.fadeA) G.fadeA = 0;       // 黑场由下面这层自己画，别让上一关的淡出把它一起盖住
      const ui = G.ui, prev = ui.insertUI || null;
      const obj = { draw(g) {
        g.fillStyle = '#05040a'; g.fillRect(0, 0, 640, 360);
        const F16 = G.f16;
        if (!F16) return;
        g.save(); g.translate(320, 62); g.scale(3, 3);
        F16.draw(g, '试炼通关', 0, 0, '#ffe040', { align: 'center', outline: '#3a1400' });
        g.restore();
        if (G.f12) G.f12.draw(g, '星尘试炼', 320, 24, '#96dcff', { align: 'center', outline: '#140c18' });
      } };
      ui.insertUI = obj;
      try { await G.ui.notice({ title: '星尘试炼　通关！', text: lines.join('\n') }); }
      finally { if (ui.insertUI === obj) ui.insertUI = prev; }
      return 'cleared';
    },

    // 时停倒数要叠在关卡自己的插入画面之上，但 common.js 用 `ui.insertUI === mine` 来收画面，
    // 所以不能换掉那个对象：在它的 draw 末尾追加，身份仍然相等，关卡自己收得掉。
    _ensureHud() {
      const ui = G.ui;
      if (!ui) return;
      const cur = ui.insertUI;
      if (hudTarget) {
        if (cur === hudTarget && hudTarget.draw === hudPatched) return;
        if (hudTarget.draw === hudPatched) hudTarget.draw = hudOrig;
        hudTarget = null; hudOrig = null; hudPatched = null;
      }
      if (hudObj) {
        if (cur === hudObj) return;
        if (ui.insertUI === hudObj) ui.insertUI = null;
        hudObj = null;
      }
      if (cur && typeof cur.draw === 'function') {
        hudTarget = cur; hudOrig = cur.draw;
        hudPatched = function (g, t) { hudOrig.call(this, g, t); T._drawStopHud(g); };
        cur.draw = hudPatched;
      } else {
        hudObj = { draw(g) { T._drawStopHud(g); } };
        ui.insertUI = hudObj;
      }
    },
    _dropHud() {
      if (hudTarget) {
        if (hudTarget.draw === hudPatched) hudTarget.draw = hudOrig;
        if (G.ui && G.ui.insertUI === hudTarget) G.ui.insertUI = null;
        hudTarget = null; hudOrig = null; hudPatched = null;
      }
      if (hudObj) {
        if (G.ui && G.ui.insertUI === hudObj) G.ui.insertUI = null;
        hudObj = null;
      }
    },
    _clearStamp() {
      this.stamp = null;
      if (G.EXTRA && G.EXTRA.clearStamp) G.EXTRA.clearStamp();
    },
    _drawStopHud(g) {
      const tm = G.time;
      if (!tm || !tm.active || !tm.by || tm.by.cid !== 'jotaro') return;
      if (tm.phase !== 'stopped') return;     // burst 阶段 t 会重置，画出来会从 1.6 跳回 2.0
      const rem = Math.max(0, ((tm.o && tm.o.dur) || 2) - (tm.t || 0));
      const col = rem <= .5 ? '#ff5a4a' : '#c8e4ff';
      const text = '白金之星·世界 ' + rem.toFixed(1) + ' s';
      const F12 = G.f12;
      const w = (F12 ? F12.width(text) : 190) + 16;
      const x = Math.round(320 - w / 2), y = 52;
      G.ui.box(g, x, y, x + w, y + 20, { fill: 'rgba(10,14,34,0.85)', border: col });
      if (F12) F12.draw(g, text, 320, y + 4, col, { align: 'center', outline: '#0a0610' });
    },
    async _overlay(dur, draw) {
      const ui = G.ui, prev = ui.insertUI || null;
      const obj = { draw };
      ui.insertUI = obj;
      try { await G.wait(dur, 'ui'); }
      finally { if (ui.insertUI === obj) ui.insertUI = prev; }
    },
  });

  const persist = () => { G.store.set(KEY, save); T.save = save; };

  // 实施文档 §五把共用的白金之星·世界挂在 G.TRIAL.SPTW 上；加载顺序上 G.SPTW 由别的文件先提供。
  if (G.SPTW) T.SPTW = G.SPTW;

  // 白金之星·世界可能在 special 的 cine 期间开始，那一帧 tick 还不会跑；在外面包一层记数，
  // 免得“本轮停下 30 次”漏算。不改 timestop.js；离开试炼后 T.active 为假，不影响剧情。
  (function hookStop() {
    const tm = G.time;
    if (!tm || typeof tm.stop !== 'function' || tm._trialStopHook) return;
    const orig = tm.stop;
    tm.stop = function (by, o) {
      const t = G.TRIAL;
      const r = orig.apply(this, arguments);
      if (t && t.active && t.run && by && by.cid === 'jotaro') {
        t.run.sptw++; stopSeen = true;
        if (G.ui) t._ensureHud();      // 时停从 cine 里开始时 tick 还没跑，这一帧就要有倒数
      }
      return r;
    };
    tm._trialStopHook = true;
  })();

  // 存档被容器回读 / 清除后重新读；T.save 始终指向最新的那份，外部读存档不会拿到旧对象。
  G.store.onLoad(() => { save = readSave(); T.save = save; });
})();
