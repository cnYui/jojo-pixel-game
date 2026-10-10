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
  const saved = G.store.get('progress', null);
  const valid = saved && saved.v === 1 && Number.isInteger(saved.max) && saved.max >= 0 && saved.max < names.length;
  const progress = valid ? { v: 1, max: saved.max, last: Number.isInteger(saved.last) ? G.clamp(saved.last, 0, 12) : 0, clear: !!saved.clear } : { v: 1, max: 0, last: 0, clear: false };
  G.progress = {
    get max() { return Math.min(progress.max, LAST); }, get clear() { return progress.clear; },
    reach(i) { progress.max = Math.max(progress.max, G.clamp(i, 0, 12)); G.store.set('progress', progress); },
    start(i) { progress.last = i; this.reach(i); },
    finish() { progress.clear = true; G.store.set('progress', progress); },
  };
  let titleBg, menuTask = 0, transitioning = false;
  const text = (g, s, x, y, col = '#fff4d6', size = 16, align = 'left') => G['f' + size].draw(g, s, x, y, col, { align, outline: '#130b20' });
  async function controls() {
    await G.ui.notice({ title: '操作说明', text: '方向键 / WASD 移动；Q 换队长。\n自由：E 调查，U 替身调查，J 亮替身。\n战斗：J 三连与连打；K 闪避；L 格挡，\n看准命中前按 L 弹反；U 必杀。\nEnter / 空格 / 点击确认；Esc 暂停。' });
  }
  async function settings() {
    let idx = 0;
    for (;;) {
      const s = G.settings, opts = ['减少闪烁：' + (s.reduceFlash ? '开' : '关'), '喊声：' + (s.grunts ? '开' : '关'),
        '连打改成按住 J：' + (s.mashHold ? '开' : '关'), '音乐音量：' + Math.round(s.musicVol * 100) + '%', '音效音量：' + Math.round(s.sfxVol * 100) + '%'];
      if (G.touch && G.touch.on) opts.push('按键大小：' + Math.round(s.touchSize * 100) + '%');
      opts.push('返回');
      const change = (i, dir) => {
        if (i < 3) { const k = ['reduceFlash', 'grunts', 'mashHold'][i]; s[k] = !s[k]; }
        else if (i < 5) { const k = i === 3 ? 'musicVol' : 'sfxVol'; s[k] = G.clamp(Math.round((s[k] + dir * .1) * 10) / 10, 0, 1); }
        else if (i === 5 && opts.length === 7) s.touchSize = G.clamp(Math.round((s.touchSize + dir * .1) * 10) / 10, .7, 1.5);
        else return false;
        s.save(); return true;
      };
      idx = await G.ui.openMenu('设置', opts, { idx, escIndex: opts.length - 1, note: '左右调节，确认切换', onKey(i, dir, m) {
        if (!change(i, dir)) return false;
        if (i === 3 || i === 4) m.options[i] = (i === 3 ? '音乐音量：' : '音效音量：') + Math.round(s[i === 3 ? 'musicVol' : 'sfxVol'] * 100) + '%';
        else if (i < 3) m.options[i] = ['减少闪烁：', '喊声：', '连打改成按住 J：'][i] + (s[['reduceFlash', 'grunts', 'mashHold'][i]] ? '开' : '关');
        else m.options[i] = '按键大小：' + Math.round(s.touchSize * 100) + '%';
        return true;
      } });
      if (idx === opts.length - 1) break;
      change(idx, 1);
    }
  }
  async function chapterMenu() {
    if (DEMO) {   // 体验版：只列开放的几章，一页
      const cs = G.CHAPTERS.slice(0, LAST + 1), opts = cs.map(c => c.title), back = opts.length; opts.push('返回');
      for (;;) {
        const i = await G.ui.openMenu('选择章节', opts, { escIndex: back, note: '体验版只开放到' + cs[LAST].title.split('　')[0] });
        if (i === back) return null;
        if (cs[i].run) return i;
      }
    }
    let page = 0;
    for (;;) {
      const start = page * 5, cs = G.CHAPTERS.slice(start, start + 5);
      const opts = cs.map(c => c.title + (c.run ? '' : '（制作中）'));
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
    while (token === menuTask && G.scene === titleScene) {
      const opts = [], actions = [];
      const add = (s, f) => { opts.push(s); actions.push(f); };
      if (G.progress.max > 0) add('继续', () => G.playFrom(G.progress.max));
      add('从序章开始', () => G.playFrom(0)); add('选择章节', async () => { const idx = await chapterMenu(); if (idx != null) await G.playFrom(idx); }); add('操作说明', controls); add('设置', settings);
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
      if (advancing) G.world.update(wdt);
    },
    drawWorld: g => G.world.draw(g), drawUI: g => G.ui.draw(g), drawTop: g => G.ui.drawTop(g),
    hasPixel: () => G.world.hasPixel(), drawPixel: (P, layer) => G.world.drawPixel(P, layer),
    hasOver: () => G.world.hasOver(), drawOver: g => G.world.drawOver(g),
  };
  async function pause() {
    gameScene.frozen = true;
    for (;;) {
      const i = await G.ui.openMenu('暂停', ['继续', '操作说明', '设置', '返回标题'], { escIndex: 0 });
      if (i === 0) break;
      if (i === 1) await controls();
      if (i === 2) await settings();
      if (i === 3) { await G.goTitle(); break; }
    }
    gameScene.frozen = false;
  }
  function reset() {
    G.cancelRun(); G.S.busy = false; G.S.cardOn = false; G.S.ambient(null); G.S._filters.clear(); G.ui.reset(); G.party.reset(); G.post.clear(); G.fx.clear();
    if (G.time && G.time.clear) G.time.clear();
    G.world.insert = null; G.world.cine = null; G.world.stage = null; G.world.player = null; G.world.fight = null;
    G.world.combat = false; G.world.free = false; G.world.ticks = []; G.world.anims = []; G.world.shots = []; G.world.hazards = [];
    G.world.focus = null; G.world.slow = 1; G.lateGame = null; G.midGame = null;
    G.world.zoom = null; G.cam.zoom = null; G.cam.x = 0; G.cam.y = 0; G.cam.shakeDur = 0;
    G.slowAllK = 1; G.slowAllT = 0; G.hitStopAll_t = 0; G.fadeA = 0; G.flags = {}; G.input.clear();
    gameScene.frozen = false;
  }
  G.goTitle = async route => {
    reset(); G.curChapter = null; G.setScene(titleScene); G.audio.music(DEMO ? 'title' : 'title_song', { fade: 1.5 });
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
      if (idx === 12) G.progress.finish(); else G.progress.reach(idx + 1);
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
  function showError(e) {
    if (G.cancelled(e)) return;
    console.error(e); G.dbg.ev('startup_error', { msg: String(e.message || e) });
    const el = document.getElementById('loading') || document.body.appendChild(document.createElement('div'));
    el.id = 'loading'; el.textContent = '运行遇到错误：' + String(e.message || e) + '\n请查看浏览器控制台。';
  }
  async function boot() {
    const el = document.getElementById('loading');
    if (!G.D) { el.textContent = '缺少 data/data_meta.js：先运行 tools\\build_assets.py'; return; }
    await G.res.preloadPack('core', (n, total) => { el.textContent = '载入角色与字库：' + n + ' / ' + total; });
    G.initFonts(); G.audio.init(); await G.audio.loadSfx();
    await G.res.loadPack('bg_title'); titleBg = new G.Background(G.D.bg.title_pyramids);
    G.start(); await G.goTitle(); el.remove(); G.booted = true;
  }
  boot().catch(showError);
})();
