// 全局玩法加量（2026-10-18 用户：“玩法也需要多做一些”）——三样东西共用一个存档键 jojo-extras，不碰 progress / settings：
//   ① 战斗评价：能输的 Boss 战打赢时，按用时、受伤、精准格挡 / 擦身闪避、连打、大招给 S / A / B / C，记每场最佳；
//   ② 挑战：标题菜单「挑战」单独重打打赢过的 Boss 战（各章用 G.EXTRA.challenge 登记入口，战斗配置和正式剧情是同一份）；
//   ③ 旅途纪念品：每章自由走动的地图里藏几件小东西，有的 E 调查就能捡、有的要某位队长的 U 替身调查才看得见
//      （鼓励换队长、四处看），标题菜单「收藏」看图鉴。
// 评价只是锦上添花：不挡剧情、不影响通关；画面上只在右侧亮 4 秒，不用按键关掉（自动测试和真人都不会被卡住）。
'use strict';
(function () {
  const G = window.G;
  const KEY = 'extras';
  const blank = () => ({ v: 1, ranks: {}, won: {}, souv: {} });
  function load() {
    const s = G.store.get(KEY, null);
    if (!s || s.v !== 1 || typeof s !== 'object') return blank();
    return { v: 1, ranks: s.ranks && typeof s.ranks === 'object' ? s.ranks : {}, won: s.won && typeof s.won === 'object' ? s.won : {},
      souv: s.souv && typeof s.souv === 'object' ? s.souv : {} };
  }
  let save = load();
  const persist = () => G.store.set(KEY, save);
  // 存档被换掉（小红书容器回读到更新的存档、标题里清除存档）后重新读
  G.store.onLoad(() => { save = load(); });
  const clamp01 = v => Math.max(0, Math.min(1, v));
  const RANKS = ['C', 'B', 'A', 'S'];
  const RANK_COL = { S: '#ffe040', A: '#ff7a52', B: '#74c0ff', C: '#c8c4d8' };
  const chapterIndex = key => (G.CHAPTERS || []).findIndex(c => c.key === key);
  const mmss = t => { t = Math.max(0, Math.round(t)); return Math.floor(t / 60) + ':' + String(t % 60).padStart(2, '0'); };

  const E = G.EXTRA = {
    CHALLENGES: [],     // { id（战斗 id）, chapter（章 key）, title（列表里显示的名字）, run(S) }
    SOUVENIRS: [],      // { id, chapter, name, desc, hint（没找到时图鉴里给的提示）}
    mode: null,         // 挑战模式中 = { def, result }
    stamp: null,        // 右侧的评价牌（ui 时钟）

    // ================================================================ ① 战斗评价
    // fight.js 每次开打（含重试）调一次：统计只算打赢的那一次尝试
    track(c) {
      const spec = c.spec || {};
      c.stats = { hurt: 0, parry: 0, graze: 0, rushHits: 0, special: 0, guard: 0 };
      if (spec.rank === false) return;
      const st = c.stats, W = G.world;
      c.on('hurt', e => { const p = W.player; st.hurt += (e && e.dmg ? e.dmg : 0) / Math.max(1, (p && p.maxHp) || 100); });
      c.on('parry', e => { if (e && e.who === W.player) st.parry++; });
      c.on('graze', e => { if (e && e.who === W.player) st.graze++; });
      c.on('guard', e => { if (e && e.who === W.player) st.guard++; });
      c.on('rushHit', e => { if (e && e.who === W.player) st.rushHits++; });
      c.on('special', e => { if (e && e.who === W.player) { st.special++; if (G.ach && G.ach.add) G.ach.add('special', 1); } });
    },
    // 分数：用时 40 + 受伤 40 + 技巧 20。par = 这一战“打得利落”的参考秒数（各章在 spec.par 里写，没写按 90 s）。
    //   用时 ≤ 0.6 par 满分、≥ 1.6 par 0 分；受伤按“掉了几条血”算（掉满一条血 0 分）；
    //   技巧：精准格挡 4、看穿 3、连打每 15 下 1、用过大招 3，封顶 20。选了「放水再来」最高 B。
    grade(stats, spec, time, assist) {
      const par = spec.par || 90;
      const tScore = 40 * clamp01((par * 1.6 - time) / par);
      const dScore = 40 * clamp01(1 - stats.hurt);
      const sScore = Math.min(20, stats.parry * 4 + stats.graze * 3 + Math.floor(stats.rushHits / 15) + (stats.special ? 3 : 0));
      const score = Math.round(tScore + dScore + sScore);
      let r = score >= 85 ? 3 : score >= 68 ? 2 : score >= 50 ? 1 : 0;
      if (assist) r = Math.min(r, 1);
      return { rank: RANKS[r], score, time, hurt: Math.round(stats.hurt * 100), parry: stats.parry, graze: stats.graze,
        rushHits: stats.rushHits, special: stats.special, assist: !!assist };
    },
    // fight.js 打赢时（spec.after 之前）调：记最佳、亮评价牌；挑战模式把结果交给结算画面
    won(c, attempt, assist) {
      // 星尘试炼的评价 / 纪录只进试炼自己的存档（键 trial），不能盖掉「挑战」里的最佳
      if (G.TRIAL && G.TRIAL.active && G.TRIAL.onWon) return G.TRIAL.onWon(c, attempt, assist);
      const spec = c.spec || {};
      save.won[c.id] = true;
      const rankable = spec.rank !== false && (spec.rank === true || spec.losable);
      let rec = null;
      if (rankable && c.stats) {
        // 参考用时：战斗配置里的 spec.par 优先，其次是挑战登记时写的 par（第1–4章的战斗配置里没有 par）
        const reg = this.CHALLENGES.find(d => d.id === c.id);
        rec = this.grade(c.stats, Object.assign({}, spec, { par: spec.par || (reg && reg.par) || 90 }), c.t, assist);
        rec.attempts = attempt + 1;
        const old = save.ranks[c.id];
        rec.best = !old || RANKS.indexOf(rec.rank) > RANKS.indexOf(old.rank) || (old.rank === rec.rank && rec.score > (old.score || 0));
        if (rec.best) save.ranks[c.id] = { rank: rec.rank, score: rec.score, time: Math.round(rec.time) };
        this.stamp = { rec, t0: G.clk.ui, dur: 4 };
        if (G.audio && G.audio.sfx) G.audio.sfx(rec.rank === 'S' || rec.rank === 'A' ? 'ding' : 'pop', { vol: .6 });
        if (G.dbg && G.dbg.ev) G.dbg.ev('fight_rank', { id: c.id, rank: rec.rank, score: rec.score, t: Math.round(c.t) });
      }
      persist();
      // 成就（engine\achievements.js）：章节取同 id 的挑战登记，没登记就取当前章；调试判胜（c.autowin）不算
      if (!c.autowin && G.ach && G.ach.emit) {
        const reg = this.CHALLENGES.find(d => d.id === c.id);
        const chapter = reg ? reg.chapter : (G.CHAPTERS && G.CHAPTERS[G.curChapter] ? G.CHAPTERS[G.curChapter].key : null);
        const lead = G.world.player, st = c.stats || {};
        G.ach.emit('fight_won', { id: c.id, chapter, mode: this.mode ? 'challenge' : 'story', rank: rec ? rec.rank : null,
          score: rec ? rec.score : 0, time: c.t, hurt: rec ? rec.hurt : Math.round(st.hurt * 100),
          hpLeft: lead ? lead.hp / Math.max(1, lead.maxHp) : 0,     // 队长打赢那一刻的血量比
          parry: st.parry || 0, graze: st.graze || 0, rushHits: st.rushHits || 0, special: st.special || 0,
          attempts: attempt + 1, assist: !!assist, losable: !!c.spec.losable, lead: lead && lead.cid });
      }
      if (this.mode && this.mode.def && this.mode.def.id === c.id) this.mode.result = rec || { rank: null, time: c.t, attempts: attempt + 1 };
      return rec;
    },
    rankOf(id) { return save.ranks[id] || null; },
    wonOnce(id) { return !!save.won[id]; },

    // ================================================================ ② 挑战
    challenge(def) {
      if (!def || !def.id || !def.run) return;
      this.CHALLENGES = this.CHALLENGES.filter(d => d.id !== def.id);
      this.CHALLENGES.push(def);
    },
    // 打赢过这一战，或者这一章已经打通过（这个功能加进来之前就通关的存档也能玩）
    unlocked(def) {
      const ci = chapterIndex(def.chapter), P = G.progress;
      if (G.DEMO && ci > G.DEMO.last) return false;
      return !!save.won[def.id] || (P && (P.clear || (ci >= 0 && ci < P.max)));
    },
    challengesOpen() { return this.CHALLENGES.filter(d => this.unlocked(d)); },
    // 标题菜单「挑战」：先选章、再选战斗；返回要打的 def（null = 返回）
    async challengeMenu() {
      const open = this.challengesOpen();
      if (!open.length) { await G.ui.notice({ title: '挑战', text: '打赢一场替身战以后，就能在这里单独再打。' }); return null; }
      const chapters = (G.CHAPTERS || []).filter(c => open.some(d => d.chapter === c.key));
      for (;;) {
        const opts = chapters.map(c => {
          const ds = this.CHALLENGES.filter(d => d.chapter === c.key), s = ds.filter(d => (this.rankOf(d.id) || {}).rank === 'S').length;
          return c.title + '　' + ds.filter(d => this.unlocked(d)).length + ' 战' + (s ? '　S×' + s : '');
        });
        opts.push('返回');
        const i = await G.ui.openMenu('挑战　选择章节', opts, { escIndex: opts.length - 1, note: '评价：用时 · 受伤 · 精准格挡 / 看穿 · 连打' });
        if (i >= chapters.length) return null;
        const ds = this.CHALLENGES.filter(d => d.chapter === chapters[i].key && this.unlocked(d));
        const o2 = ds.map(d => { const r = this.rankOf(d.id); return d.title + '　' + (r ? '最佳 ' + r.rank + '（' + mmss(r.time) + '）' : '未评价'); });
        o2.push('返回');
        const j = await G.ui.openMenu(chapters[i].title, o2, { escIndex: o2.length - 1 });
        if (j < ds.length) return ds[j];
      }
    },
    // 挑战打完的结算（main.js 的 playChallenge 调）：返回 0 = 再打一次、1 = 回挑战列表、2 = 回标题
    async challengeResult(def) {
      const r = this.mode && this.mode.result, best = this.rankOf(def.id);
      const lines = r && r.rank
        ? ['评价　' + r.rank + (r.best ? '　（新纪录！）' : ''), '用时 ' + mmss(r.time) + '　受伤 ' + r.hurt + '%',
          '精准格挡 ' + r.parry + '　看穿 ' + r.graze + '　连打 ' + r.rushHits + (r.assist ? '\n（放水再来：最高 B）' : ''),
          best ? '这一战的最佳：' + best.rank + '（' + mmss(best.time) + '）' : '']
        : ['打赢了！', '用时 ' + mmss(r ? r.time : 0)];
      await G.ui.notice({ title: def.title, text: lines.filter(Boolean).join('\n') });
      return G.ui.openMenu(def.title, ['再挑战一次', '回到挑战列表', '回到标题'], { escIndex: 1 });
    },

    // ================================================================ ③ 旅途纪念品
    souvenir(def) {
      if (!def || !def.id) return;
      this.SOUVENIRS = this.SOUVENIRS.filter(d => d.id !== def.id);
      this.SOUVENIRS.push(def);
    },
    has(id) { return !!save.souv[id]; },
    chapterSouvenirs(key) { return this.SOUVENIRS.filter(d => d.chapter === key); },
    // 直接给一件（小游戏赢了、剧情里别人送的）：at = 闪光的世界坐标 { x, y }（可省）
    async give(S, id, at) {
      const def = this.SOUVENIRS.find(d => d.id === id);
      if (this.has(id) || !def) return false;
      save.souv[id] = true; persist();
      S.sfx('sparkle', .8);
      if (at) S.fx('glint', { x: at.x, y: at.y - 14, size: 9 });
      const list = this.chapterSouvenirs(def.chapter), n = list.filter(d => this.has(d.id)).length;
      if (G.dbg && G.dbg.ev) G.dbg.ev('souvenir', { id, n });
      await S.notice({ title: '旅途纪念品', text: def.name, sub: def.desc + '　（本章 ' + n + ' / ' + list.length + '）' });
      return true;
    },
    // 地图上的纪念品调查点（放进 stage.hotspots）。o.look = 能看见它的替身调查标签（例：['nensha']）——有它就只能 U 找到；
    //   没有就是 E 调查（label 默认“有什么在闪”）。捡过的不再出现。o.found(S, h, p) 捡到以前的额外台词（可省）。
    hot(id, x, y, o = {}) {
      const take = async (S, h, p) => {
        if (this.has(id)) return;
        if (o.found) await o.found(S, h, p);
        await this.give(S, id, { x: h.x, y: h.y });
      };
      const cond = () => !this.has(id) && (!o.cond || o.cond());
      const h = { id: 'souv_' + id, x, y, r: o.r || 16, ry: o.ry || 60, cond, souvenir: id };
      if (o.look) { h.tags = o.look; h.look = take; }
      else { h.label = o.label || '有什么在闪'; h.use = take; }
      return h;
    },
    // 标题菜单「收藏」：选章看本章的纪念品（没找到的给提示）
    async collectionMenu() {
      const chapters = (G.CHAPTERS || []).filter((c, i) => this.chapterSouvenirs(c.key).length && (!G.DEMO || i <= G.DEMO.last));
      if (!chapters.length) { await G.ui.notice({ title: '收藏', text: '还没有可以收集的纪念品。' }); return; }
      for (;;) {
        const all = this.SOUVENIRS.filter(d => chapters.some(c => c.key === d.chapter)), got = all.filter(d => this.has(d.id)).length;
        const opts = chapters.map(c => { const ds = this.chapterSouvenirs(c.key), n = ds.filter(d => this.has(d.id)).length;
          return c.title + '　' + n + ' / ' + ds.length + (n === ds.length ? '　★' : ''); });
        opts.push('返回');
        const i = await G.ui.openMenu('收藏　旅途纪念品 ' + got + ' / ' + all.length, opts, { escIndex: opts.length - 1,
          note: '有的 E 就能捡，有的要换队长用 U 替身调查' });
        if (i >= chapters.length) return;
        const ds = this.chapterSouvenirs(chapters[i].key);
        const text = ds.map(d => this.has(d.id) ? '★ ' + d.name + '：' + d.desc : '？ ？？？　提示：' + (d.hint || '仔细找找')).join('\n');
        await G.ui.notice({ title: chapters[i].title, text });
      }
    },

    // ================================================================ 画（G.ui.draw 里，uifx 之后）：右侧的评价牌
    drawUI(g) {
      const s = this.stamp;
      if (!s) return;
      const t = G.clk.ui - s.t0;
      if (t > s.dur) { this.stamp = null; return; }
      const r = s.rec, F16 = G.f16, F12 = G.f12;
      if (!F16 || !F12) return;
      const slide = Math.round((1 - clamp01(t / .25)) * 160), fade = clamp01((s.dur - t) / .4);
      const x0 = 476 + slide, y0 = 98, x1 = x0 + 154, y1 = y0 + 78;
      g.save();
      g.globalAlpha = fade;
      G.ui.box(g, x0, y0, x1, y1, { fill: 'rgba(18,14,34,0.9)', border: RANK_COL[r.rank] });
      F12.draw(g, '战斗评价', x0 + 10, y0 + 8, '#fff4d6', { outline: '#140c18' });
      // 大字母：f16 画在 3 倍缩放的坐标里（像素字放大不糊）
      const pop = t < .35 ? 1 + (.35 - t) * 1.6 : 1;
      g.save(); g.translate(x0 + 30, y0 + 46); g.scale(3 * pop, 3 * pop);
      F16.draw(g, r.rank, 0, -8, RANK_COL[r.rank], { align: 'center', outline: '#140c18' });
      g.restore();
      F12.draw(g, '用时 ' + mmss(r.time), x0 + 62, y0 + 24, '#ffe3a0', { outline: '#140c18' });
      F12.draw(g, '受伤 ' + r.hurt + '%', x0 + 62, y0 + 38, '#ffe3a0', { outline: '#140c18' });
      F12.draw(g, '格挡 ' + r.parry + ' 看穿 ' + r.graze, x0 + 62, y0 + 52, '#ffe3a0', { outline: '#140c18' });
      if (r.best && t % .6 < .4) F12.draw(g, '新纪录！', x1 - 8, y0 + 8, '#ff9a6a', { align: 'right', outline: '#140c18' });
      g.restore();
    },
    clearStamp() { this.stamp = null; },
    // 调试快照 / 自动测试读
    state() {
      return { ranks: Object.assign({}, save.ranks), won: Object.keys(save.won).length, souv: Object.keys(save.souv),
        challenges: this.CHALLENGES.map(d => d.id), souvenirs: this.SOUVENIRS.map(d => d.id), mode: this.mode ? this.mode.def.id : null,
        stamp: this.stamp ? this.stamp.rec.rank : null };
    },
    // 测试 / 调试：清空本存档
    reset() { save = blank(); persist(); },
  };

  // 第1–4章已经写好的单战入口（G.DEV，章节文件里定义；这里用到时才取，所以可以先登记）。第5章起各章在自己的文件里登记。
  //   par = 评价的参考用时：照 2026-10 整章自动测试的打法用时放宽（真人第一次打会慢，S 要打得很利落）。
  [['b02_chariot', 'ch1', 'VS 银色战车（阿布德尔）', 'ch1Chariot', 100], ['b03_darkbluemoon', 'ch2', 'VS 暗蓝之月（承太郎）', 'ch2Darkmoon', 110],
    ['b04_strength', 'ch2', 'VS 力量（承太郎）', 'ch2Strength', 100], ['b05_devo', 'ch3', 'VS 黑檀木恶魔（波鲁纳雷夫）', 'ch3Devo', 90],
    ['b06_yellowtemperance', 'ch3', 'VS 黄色节制（承太郎）', 'ch3Yellow', 100], ['b07_hangedman', 'ch4', 'VS 皇帝 & 倒吊人（波鲁纳雷夫）', 'ch4Hanged', 120],
    ['b08_empress', 'ch4', 'VS 女帝（乔瑟夫）', 'ch4Empress', 110]]
    .forEach(([id, chapter, title, dev, par]) => E.challenge({ id, chapter, title, par, run: S => G.DEV[dev](S) }));
})();
