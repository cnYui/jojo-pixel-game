// 启动、标题、章节、设置与存档集中在入口，章节只负责自己的剧情与玩法。
'use strict';
(function () {
  const G = window.G;
  const names = [
    ['prologue', '序章　东京', '替身之名'], ['ch1', '第1章　香港', '灰塔与银色战车'],
    ['ch2', '第2章　南海', '南海漂流'], ['ch3', '第3章　新加坡', '新加坡的恶意'],
    ['ch4', '第4章　印度', '两只右手的男人'], ['ch5', '第5章　巴基斯坦', '公路、浓雾与卡拉奇'],
    ['ch6', '第6章　阿拉伯', '沙漠的太阳与梦'], ['ch7', '第7章　红海', '许愿与大嘴'],
    ['ch8', '第8章　埃及沙漠', '九荣神：沙与预言'], ['ch9', '第9章　尼罗河', '刀、磁铁与影子'],
    ['ch10', '第10章　开罗', '赌局与看门鸟'], ['ch11', '第11章　DIO的馆', '日落之前'],
    ['final', '终章　DIO的世界', '直到黎明'],
  ];
  G.CHAPTERS = names.map(([key, title, sub], i) => ({ key, title, sub, run: G.STORY[key] || null,
    music: ['daily', 'travel', 'battle', 'tension', 'sad', 'ominous', 'boss', 'ending', 'victory'], next: i + 1 }));
  // 体验版：发布包的 index.html 在 main.js 前写 window.JOJO_DEMO = { last: 1 }（tools\dev\make_demo.py）；开发时网址加 ?demo=1 也能看。
  //   只开放到第 last 章（0 = 序章），打完那一章出「体验版到此结束」；标题曲换成原工程的 title（STAND PROUD 是商业歌曲，不随发布包分发）
  const DEMO = window.JOJO_DEMO || (/[?&]demo=1(&|$)/.test(location.search) ? { last: 1 } : null);
  const LAST = DEMO ? G.clamp(DEMO.last | 0, 0, names.length - 1) : names.length - 1;
  G.DEMO = DEMO ? { last: LAST } : null;
  G.curChapter = null;
  // 存档（键 progress）。版本号仍是 v:1，只加了可选字段：旧版本读到新存档照样认得（多出来的字段它忽略），回退到旧包也不会丢「继续」。
  //   max = 玩到的最远一章；last = 最近开始的一章；clear = 打穿终章；
  //   done = 打完过的章序号；play = 累计游玩秒数（只算世界在走的时候，暂停不算）；at = 最后一次写档的时间（ms）。
  //   旧存档没有 done / play / at：读出来补空，不去猜哪些章打完过（选章直接跳进去也会抬高 max）。
  const blankProgress = () => ({ v: 1, max: 0, last: 0, clear: false, done: [], play: 0, at: 0 });
  function readProgress() {
    const s = G.store.get('progress', null);
    if (!s || typeof s !== 'object' || s.v !== 1 || !Number.isInteger(s.max) || s.max < 0 || s.max >= names.length) return blankProgress();
    const p = blankProgress();
    p.max = s.max; p.last = Number.isInteger(s.last) ? G.clamp(s.last, 0, 12) : 0; p.clear = !!s.clear;
    if (Array.isArray(s.done)) s.done.forEach(i => { if (Number.isInteger(i) && i >= 0 && i < names.length && p.done.indexOf(i) < 0) p.done.push(i); });
    p.done.sort((a, b) => a - b);
    p.play = +s.play > 0 ? +s.play : 0; p.at = +s.at > 0 ? +s.at : 0;
    return p;
  }
  let progress = readProgress(), playDirty = 0;
  // play 在内存里是小数秒，写档时取整；每 60 秒游玩顺手写一次，防止手机直接杀进程（pagehide 不一定触发）丢掉一大段时长
  // achievements.js 自己的存档是懒合并写的，切后台 / 关页面时顺手让它落盘（没有 G.ach 时什么也不做）
  const persist = () => { progress.at = Date.now(); playDirty = 0; G.store.set('progress', Object.assign({}, progress, { play: Math.round(progress.play) }));
    if (G.ach && G.ach.emit) G.ach.emit('play', { sec: progress.play }); if (G.ach && G.ach.flush) G.ach.flush(); };
  G.progress = {
    get max() { return Math.min(progress.max, LAST); }, get clear() { return progress.clear; },
    reach(i) { progress.max = Math.max(progress.max, G.clamp(i, 0, 12)); persist(); },
    start(i) { progress.last = i; this.reach(i); },
    finish() { progress.clear = true; persist(); },
    // 打完第 i 章：记下通关、把“继续”推到下一章（终章 = 通关）
    complete(i) {
      if (progress.done.indexOf(i) < 0) { progress.done.push(i); progress.done.sort((a, b) => a - b); }
      if (i === 12) this.finish(); else this.reach(i + 1);
      if (G.ach && G.ach.emit) G.ach.emit('chapter_done', { idx: i, key: names[i][0] });
    },
    isDone(i) { return progress.done.indexOf(i) >= 0; },
    tick(dt) { progress.play += dt; playDirty += dt; if (playDirty >= 60) persist(); },
    // 切后台 / 关页面：只有这一段真玩过（playDirty > 0）才补写，光开着标题页不会刷新“上次存档”的时间，也不会凭空造出一份存档
    flush() { if (playDirty > 0) persist(); G.store.flush(); },
    info() {
      const done = progress.done.filter(i => i <= LAST);
      return { max: Math.min(progress.max, LAST), last: Math.min(progress.last, LAST), clear: progress.clear, done, total: LAST + 1,
        play: Math.round(progress.play), at: progress.at };
    },
    // 清除存档：进度、收藏（战斗评价、纪念品）和成就 / 试炼纪录；设置和操作提示保留
    erase() { G.store.remove('progress'); G.store.remove('extras'); G.store.remove('ach'); G.store.remove('trial'); G.store.reload(); },
  };
  G.store.onLoad(() => { progress = readProgress(); });
  addEventListener('pagehide', () => G.progress.flush());
  document.addEventListener('visibilitychange', () => { if (document.hidden) G.progress.flush(); });
  let titleBg, menuTask = 0, transitioning = false;
  const text = (g, s, x, y, col = '#fff4d6', size = 16, align = 'left') => G['f' + size].draw(g, s, x, y, col, { align, outline: '#130b20' });
  async function controls() {
    await G.ui.notice({ title: '操作说明', text: '方向键 / WASD 移动；Q 换队长。\n自由：E 调查，U 替身调查，J 亮替身。\n战斗：J 三连与连打；K 闪避；L 格挡，\n看准命中前按 L 弹反；U 必杀。\nEnter / 空格 / 点击确认；Esc 暂停。' });
  }
  async function settings() {
    let idx = 0;
    for (;;) {
      const s = G.settings, opts = ['操作说明', '减少闪烁：' + (s.reduceFlash ? '开' : '关'), '喊声：' + (s.grunts ? '开' : '关'),
        '连打改成按住 J：' + (s.mashHold ? '开' : '关'), '音乐音量：' + Math.round(s.musicVol * 100) + '%', '音效音量：' + Math.round(s.sfxVol * 100) + '%'];
      const touchIdx = (G.touch && G.touch.on) ? opts.length : -1;
      if (touchIdx >= 0) opts.push('按键大小：' + Math.round(s.touchSize * 100) + '%');
      opts.push('返回');
      const change = (i, dir) => {
        if (i === 0) return false;    // 操作说明是提示框，不进左右调节
        if (i < 4) { const k = ['reduceFlash', 'grunts', 'mashHold'][i - 1]; s[k] = !s[k]; }
        else if (i < 6) { const k = i === 4 ? 'musicVol' : 'sfxVol'; s[k] = G.clamp(Math.round((s[k] + dir * .1) * 10) / 10, 0, 1); }
        else if (i === touchIdx) s.touchSize = G.clamp(Math.round((s.touchSize + dir * .1) * 10) / 10, .7, 1.5);
        else return false;
        s.save(); return true;
      };
      idx = await G.ui.openMenu('设置', opts, { idx, escIndex: opts.length - 1, note: '左右调节，确认切换', onKey(i, dir, m) {
        if (!change(i, dir)) return false;
        if (i === 4 || i === 5) m.options[i] = (i === 4 ? '音乐音量：' : '音效音量：') + Math.round(s[i === 4 ? 'musicVol' : 'sfxVol'] * 100) + '%';
        else if (i < 4) m.options[i] = ['减少闪烁：', '喊声：', '连打改成按住 J：'][i - 1] + (s[['reduceFlash', 'grunts', 'mashHold'][i - 1]] ? '开' : '关');
        else m.options[i] = '按键大小：' + Math.round(s.touchSize * 100) + '%';
        return true;
      } });
      if (idx === opts.length - 1) break;
      if (idx === 0) { await controls(); continue; }    // 「操作说明」并进设置，标题菜单才少一项、不盖住 logo
      change(idx, 1);
    }
  }
  // ---------------------------------------------------------------- 存档界面
  const mark = i => (G.progress.isDone(i) ? '　★' : '');    // 选章菜单里打完过的章后面标 ★
  const fmtPlay = s => { const m = Math.floor(s / 60); return m < 1 ? '不到1分钟' : m < 60 ? m + '分钟' : Math.floor(m / 60) + '小时' + (m % 60) + '分'; };
  const fmtAt = ms => { if (!ms) return '还没有'; const d = new Date(ms), p = n => (n < 10 ? '0' : '') + n; return (d.getMonth() + 1) + '月' + d.getDate() + '日 ' + p(d.getHours()) + ':' + p(d.getMinutes()); };
  // 战斗评价 / 纪念品的数量：只数当前包开放的章（体验版只到第 LAST 章）
  function extrasCount() {
    const E = G.EXTRA;
    if (!E) return { fights: 0, souv: 0, souvTotal: 0 };
    const st = E.state(), open = d => { const ci = G.CHAPTERS.findIndex(c => c.key === d.chapter); return ci >= 0 && ci <= LAST; };
    return { fights: Object.keys(st.ranks).length, souv: E.SOUVENIRS.filter(d => open(d) && E.has(d.id)).length, souvTotal: E.SOUVENIRS.filter(open).length };
  }
  // 标题菜单「成就 x / X」上的两个数；成就模块没来就显示 0 / 0
  const achGot = () => { const a = G.ach && G.ach.summary ? G.ach.summary() : null; return a ? a.got : 0; };
  const achTotal = () => { const a = G.ach && G.ach.summary ? G.ach.summary() : null; return a ? a.total : 0; };
  const hasSave = () => { const P = G.progress.info(); return P.max > 0 || P.at > 0 || P.done.length > 0 || extrasCount().fights + extrasCount().souv > 0; };
  function saveRows() {
    const P = G.progress.info(), X = extrasCount(), S = G.store.status(), where = [];
    // 存放位置：哪条通道最近一次写成功（或还没试过）就算数；两条都失败才告诉玩家“这次玩的不会留下”
    if (S.hasXhs && S.xhs !== false) where.push('小红书小工具存储');
    if (S.local !== false) where.push('本机浏览器');
    const rows = ['最远：' + G.CHAPTERS[P.max].title, '通关：' + P.done.length + ' / ' + P.total + ' 章' + (P.clear ? '　★全部通关' : ''),
      '游玩：' + fmtPlay(P.play), '存档：' + fmtAt(P.at)];
    if (X.fights || X.souvTotal) rows.push('战斗评价 ' + X.fights + ' 场　纪念品 ' + X.souv + ' / ' + X.souvTotal);
    if (G.ach && G.ach.summary) {
      const a = G.ach.summary();
      rows.push('成就：' + a.got + ' / ' + a.total + '　成就点 ' + a.pts);
    }
    rows.push(where.length ? '存放：' + where.join(' + ') : '存放：失败！关掉后这次的进度不会留下');
    if (where.length) rows.push('清理应用数据或卸载后，存档会丢失');
    return rows;
  }
  // 清除只在标题里给（游戏中途清掉当前这章的进度没有意义）；默认选“取消”，Esc 也是取消
  async function saveMenu() {
    let idx = 0;
    for (;;) {
      idx = await G.ui.openMenu('存档', ['查看存档', '清除存档', '返回'], { idx, escIndex: 2, note: '每章开头和结尾自动保存，不用手动存' });
      if (idx === 2) return;
      if (idx === 0) { await G.ui.notice({ title: '存档', text: saveRows().join('\n') }); continue; }
      const j = await G.ui.openMenu('清除存档？', ['取消', '清除进度、收藏和成就'], { idx: 0, escIndex: 0, note: '设置会保留，清除后无法恢复' });
      if (j !== 1) continue;
      G.progress.erase();
      await G.ui.notice({ title: '存档', text: '存档已清除。' });
      return;
    }
  }
  async function chapterMenu() {
    if (DEMO) {   // 体验版：只列开放的几章，一页
      const cs = G.CHAPTERS.slice(0, LAST + 1), opts = cs.map((c, i) => c.title + mark(i)), back = opts.length; opts.push('返回');
      for (;;) {
        const i = await G.ui.openMenu('选择章节', opts, { escIndex: back, note: '体验版只开放到' + cs[LAST].title.split('　')[0] });
        if (i === back) return null;
        if (cs[i].run) return i;
      }
    }
    let page = 0;
    for (;;) {
      const start = page * 5, cs = G.CHAPTERS.slice(start, start + 5);
      const opts = cs.map((c, k) => c.title + (c.run ? '' : '（制作中）') + mark(start + k));
      const prev = opts.length; opts.push('上一页'); const next = opts.length; opts.push('下一页'); const back = opts.length; opts.push('返回');
      const i = await G.ui.openMenu('选择章节　' + (page + 1) + ' / 3', opts, { escIndex: back });
      if (i === back) return null;
      if (i === prev) { page = (page + 2) % 3; continue; }
      if (i === next) { page = (page + 1) % 3; continue; }
      if (!cs[i].run) { await G.ui.notice({ title: cs[i].title, text: '这一章还在制作中。' }); continue; }
      return start + i;
    }
  }
  async function titleMenu(token, route) {
    if (route === 'chapters') { const idx = await chapterMenu(); if (idx != null) { await G.playFrom(idx); return; } }
    if (route === 'challenge' && G.EXTRA) { const def = await G.EXTRA.challengeMenu(); if (def) { await G.playChallenge(def); return; } }
    // 试炼失败后选「重新编队」回来：直接摊开编队页（流程同标题菜单里的「星尘试炼」）
    if (route === 'trial' && G.TRIAL) {
      if (G.TRIAL.unlocked()) { const sq = await G.TRIAL.menu(); if (sq) { await G.playTrial(sq); return; } }
      else await G.ui.notice({ title: '星尘试炼', text: '打穿终章以后开放。' });
    }
    while (token === menuTask && G.scene === titleScene) {
      const opts = [], actions = [];
      const add = (s, f) => { opts.push(s); actions.push(f); };
      // 继续 = 玩到的最远一章；最远那章已经打完（体验版打完最后一章、或打穿终章）就改叫“重温”，免得以为后面还有
      if (G.progress.max > 0) { const m = G.progress.max; add((G.progress.isDone(m) ? '重温：' : '继续：') + G.CHAPTERS[m].title, () => G.playFrom(m)); }
      add('从序章开始', () => G.playFrom(0)); add('选择章节', async () => { const idx = await chapterMenu(); if (idx != null) await G.playFrom(idx); });
      // 2026-10-18 玩法加量（story\extras.js）：打赢过替身战才出现「挑战」，有纪念品登记了才出现「收藏」
      if (G.EXTRA && G.EXTRA.challengesOpen().length) add('挑战', async () => { const def = await G.EXTRA.challengeMenu(); if (def) await G.playChallenge(def); });
      // 星尘试炼（story\trial.js）：体验版 Boss 不全，整项不显示；没打穿终章也显示，点开给一句提示让人知道有这回事
      if (G.TRIAL && !DEMO) add('星尘试炼', async () => {
        if (!G.TRIAL.unlocked()) { await G.ui.notice({ title: '星尘试炼', text: '打穿终章以后开放。' }); return; }
        const sq = await G.TRIAL.menu(); if (sq) await G.playTrial(sq);
      });
      if (G.EXTRA && G.EXTRA.SOUVENIRS.length) add('收藏', () => G.EXTRA.collectionMenu());
      if (G.ach && G.ach.openPage) add('成就　' + achGot() + ' / ' + achTotal(), () => G.ach.openPage());
      if (hasSave()) add('存档', saveMenu);
      add('设置', settings);    // 「操作说明」并进设置第一项，标题菜单才放得下
      const i = await G.ui.openMenu('', opts, { y: 205, note: '同人游戏，免费体验。角色版权归原作者。' });
      if (token !== menuTask) return;
      await actions[i]();
    }
  }
  const titleScene = {
    name: 'title', frozen: false,
    update(dt) { G.ui.update(dt); },
    drawWorld(g) {
      if (titleBg) titleBg.draw(g, 0, G.clk.world, { state: {} });
      ['jotaro', 'joseph', 'avdol', 'kakyoin', 'polnareff', 'iggy'].forEach((cid, i) => {
        G.atlas(cid).draw(g, 'idle', 0, 48 + i * 45, 145, { backlit: { dark: '#0a0610', k: .9, rim: '#ffb060' } });
      });
    },
    drawUI(g) {
      const meta = G.D.ui && G.D.ui.logo && G.D.ui.logo.main;
      const im = G.image(typeof meta === 'string' ? meta : meta && meta.image || 'ui/logo_main');
      if (G.ready(im)) { const k = Math.min(560 / im.width, 160 / im.height); g.drawImage(im, Math.round(320 - im.width * k / 2), 26, Math.round(im.width * k), Math.round(im.height * k)); }
      else text(g, 'JoJo的奇妙冒险　星尘斗士', 320, 55, '#ffe070', 16, 'center');
      text(g, DEMO ? '同人像素游戏 · 体验版' : '同人像素游戏', 320, 182, '#ffd9a0', 12, 'center');
      if (progress.clear) text(g, '★', 610, 14, '#ffe040');
      G.ui.draw(g);
    },
    drawTop(g) { G.ui.drawTop(g); },
  };
  const gameScene = {
    name: 'world', frozen: false,
    update(dt, advancing, wdt) {
      G.ui.update(dt);
      if (G.input.hit('pause') && !G.ui.menu && !G.ui.qte) { G.input.consume('pause'); pause().catch(showError); }
      if (advancing) { G.progress.tick(dt); G.world.update(wdt); }    // 暂停 / 顿帧时不算游玩时长
    },
    drawWorld: g => G.world.draw(g), drawUI: g => G.ui.draw(g), drawTop: g => G.ui.drawTop(g),
    hasPixel: () => G.world.hasPixel(), drawPixel: (P, layer) => G.world.drawPixel(P, layer),
    hasOver: () => G.world.hasOver(), drawOver: g => G.world.drawOver(g),
  };
  async function pause() {
    gameScene.frozen = true;
    for (;;) {
      const trial = !!(G.TRIAL && G.TRIAL.active);
      // 试炼没有存档点，手滑点了就等于本轮作废：先确认一次（默认「取消」）
      const i = await G.ui.openMenu('暂停', ['继续', '操作说明', '设置', trial ? '放弃试炼（本轮作废）' : '返回标题'], { escIndex: 0 });
      if (i === 0) break;
      if (i === 1) await controls();
      if (i === 2) await settings();
      if (i === 3) {
        if (trial) {
          const j = await G.ui.openMenu('放弃试炼？', ['取消', '放弃'], { idx: 0, escIndex: 0, note: '本轮作废，要从第 1 关重新开始' });
          if (j !== 1) continue;
        }
        await G.goTitle(); break;
      }
    }
    gameScene.frozen = false;
  }
  function reset() {
    G.cancelRun(); G.S.busy = false; G.S.cardOn = false; G.S.ambient(null); G.audio.stopLoops(.1); G.S._filters.clear(); G.ui.reset(); G.party.reset(); G.post.clear(); G.fx.clear();
    if (G.time && G.time.clear) G.time.clear();
    G.world.insert = null; G.world.cine = null; G.world.stage = null; G.world.player = null; G.world.fight = null;
    G.world.combat = false; G.world.free = false; G.world.ticks = []; G.world.anims = []; G.world.shots = []; G.world.hazards = [];
    G.world.focus = null; G.world.slow = 1; G.lateGame = null; G.midGame = null;
    G.world.zoom = null; G.cam.zoom = null; G.cam.x = 0; G.cam.y = 0; G.cam.shakeDur = 0;
    G.slowAllK = 1; G.slowAllT = 0; G.hitStopAll_t = 0; G.fadeA = 0; G.flags = {}; G.input.clear();
    if (G.EXTRA) { G.EXTRA.clearStamp(); G.EXTRA.mode = null; }
    if (G.TRIAL && G.TRIAL.reset) G.TRIAL.reset();    // 回标题 / 换场景时把试炼的 active 和本轮记录清掉
    gameScene.frozen = false;
  }
  G.goTitle = async route => {
    reset(); G.curChapter = null; G.setScene(titleScene);
    // 公开包没有用户标题曲，沿用仓库内的芯片音乐。
    G.audio.music(!DEMO && G.D.audio.music.title_song ? 'title_song' : 'title', { fade: 1.5 });
    const token = ++menuTask; titleMenu(token, route).catch(showError);
  };
  G.playFrom = async idx => {
    const c = G.CHAPTERS[idx];
    if (transitioning || !c || !c.run || idx > LAST) return;
    transitioning = true; menuTask++; reset(); G.curChapter = idx; G.progress.start(idx);
    G.setScene(gameScene); G.fadeA = 1;
    const id = G.runId;
    try {
      G.audio.stopMusic(.8); await G.res.loadPack('bg_common'); await G.res.loadPack('bg_' + c.key);
      G.audio.releaseExcept(c.music); G.audio.prefetch(c.music.slice(0, 2)); transitioning = false;
      await c.run(G.S);
      if (id !== G.runId) return;
      G.progress.complete(idx);
      G.ui.hints = []; G.post.clear(); G.cam.zoom = null; G.world.zoom = null;
      if (DEMO && idx >= LAST) {
        const span = LAST === 0 ? '序章' : LAST === 1 ? '序章 + 第1章' : '序章到' + c.title.split('　')[0];
        G.fadeA = 0;   // 黑幕画在 UI 层上面，会把提示框整个盖住

        await G.ui.notice({ title: '体验版到此结束', text: '感谢游玩！\n体验版（' + span + '）到这里就结束了。\n后面的旅程还在制作中，敬请期待。' });
        await G.goTitle(); return;
      }
      const next = G.CHAPTERS[idx + 1];
      const i = await G.ui.openMenu(c.title + '　完', [next && next.run ? '继续下一章' : '返回标题', '选择章节'], { escIndex: 0 });
      if (i === 1) await G.goTitle('chapters');
      else if (next && next.run) await G.playFrom(idx + 1); else await G.goTitle();
    } catch (e) { if (id === G.runId) showError(e); } finally { transitioning = false; }
  };
  // 挑战：单独打一场替身战（入口是各章登记的 def.run，和 G.DEV 同一份战斗配置）；打完给结算，不推进章节进度。
  //   战斗里选「回到标题」时 S.fight 自己回标题并抛 RunCancelled，这里只要不把它当错误显示。
  G.playChallenge = async def => {
    const idx = G.CHAPTERS.findIndex(c => c.key === def.chapter), c = G.CHAPTERS[idx];
    if (transitioning || !c) return;
    for (;;) {
      transitioning = true; menuTask++; reset(); G.curChapter = idx;
      G.EXTRA.mode = { def, result: null };
      G.setScene(gameScene); G.fadeA = 1;
      const id = G.runId;
      try {
        G.audio.stopMusic(.8); await G.res.loadPack('bg_common'); await G.res.loadPack('bg_' + c.key);
        G.audio.releaseExcept(c.music); transitioning = false;
        await def.run(G.S);
        if (id !== G.runId) return;
        G.ui.hints = []; G.post.clear(); G.cam.zoom = null; G.world.zoom = null; G.fadeA = 0;
        const pick = await G.EXTRA.challengeResult(def);
        if (pick === 0) continue;
        await G.goTitle(pick === 1 ? 'challenge' : undefined); return;
      } catch (e) { if (id === G.runId) showError(e); return; } finally { transitioning = false; }
    }
  };
  // 星尘试炼：照 playChallenge 的写法；一轮里的各关由 trial.js 自己换场景、开打、结算。
  //   这里每轮先 reset 一次，再按 trial.js 的返回值决定重来（重新开始用同一套编队）、重新编队还是回标题；不推进章节进度。
  G.playTrial = async squad => {
    if (transitioning || !squad) return;
    for (;;) {
      transitioning = true; menuTask++; reset(); G.curChapter = null;
      G.setScene(gameScene); G.fadeA = 1;
      const id = G.runId;
      try {
        G.audio.stopMusic(.8); await G.res.loadPack('bg_common'); transitioning = false;
        G.TRIAL.begin(squad);
        const r = await G.TRIAL.play(G.S);
        if (id !== G.runId) return;
        if (r === 'restart') continue;
        if (r === 'squad') { await G.goTitle('trial'); return; }
        await G.goTitle(); return;    // 'cleared' / 'title'
      } catch (e) { if (id === G.runId) showError(e); return; } finally { transitioning = false; }
    }
  };
  function showError(e) {
    if (G.cancelled(e)) return;
    console.error(e); G.dbg.ev('startup_error', { msg: String(e.message || e) });
    const el = document.getElementById('loading') || document.body.appendChild(document.createElement('div'));
    el.id = 'loading'; el.textContent = '运行遇到错误：' + String(e.message || e) + '\n请查看浏览器控制台。';
  }
  async function boot() {
    const el = document.getElementById('loading');
    if (!G.D) { el.textContent = '缺少 data/data_meta.js：先运行 tools\\build_assets.py'; return; }
    // 小红书容器的存档接口只有异步版：和载入资源同时回读，标题出来之前最多再等 1.5 s（超时照常进游戏，用本机浏览器里的那份）
    const storeReady = G.store.hydrate();
    await G.res.preloadPack('core', (n, total) => { el.textContent = '载入角色与字库：' + n + ' / ' + total; });
    G.initFonts(); G.audio.init(); await G.audio.loadSfx();
    await G.res.loadPack('bg_title'); titleBg = new G.Background(G.D.bg.title_pyramids);
    await storeReady;
    G.start(); await G.goTitle(); el.remove(); G.booted = true;
  }
  boot().catch(showError);
})();
