// 第四部入口：启动、标题、章节、设置与存档。章节脚本只管自己的剧情（story/p4_*.js）。
//   骨架照第三部 main.js；不同的地方：章节表换成第四部；存档键单独用 p4-progress（两部放在同一个网站上时不串档）；
//   标题曲只用仓库里自己写的芯片音乐 title（商业歌曲不随包分发）；暂停菜单多一页「发型记录」。
'use strict';
(function () {
  const G = window.G;
  const names = [
    ['prologue', '序章　杜王町', '仗助登场'], ['ch1', '第1章　虹村家', '弓与箭'],
    ['ch2', '第2章　葡萄丘高中', '锁与表面'], ['ch3', '第3章　海边别墅', '由花子与意大利菜'],
    ['ch4', '第4章　杜王港', '辣妹与透明宝宝'], ['ch5', '第5章　露伴宅', '漫画家与猎鼠'],
    ['ch6', '第6章　幽灵小路', '丰收与纽扣'], ['ch7', '第7章　商店街', '灰姑娘与枯萎穿心攻击'],
    ['ch8', '第8章　吉良家旧宅', '原子心之父'], ['ch9', '第9章　国道隧道', '宇宙人、公路之星与猫草'],
    ['ch10', '第10章　送电铁塔', '铁塔与谜'], ['ch11', '第11章　川尻家', '败者食尘'],
    ['final', '终章　杜王町', '钻石是不会碎的'],
  ];
  const LAST = names.length - 1;
  G.CHAPTERS = names.map(([key, title, sub], i) => ({ key, title, sub, run: G.STORY[key] || null,
    music: ['daily', 'tension', 'battle', 'sad', 'victory'], next: i + 1 }));
  G.DEMO = null;
  G.curChapter = null;
  const KEY = 'p4-progress';
  const saved = G.store.get(KEY, null);
  const valid = saved && saved.v === 1 && Number.isInteger(saved.max) && saved.max >= 0 && saved.max <= LAST;
  const progress = valid ? { v: 1, max: saved.max, last: Number.isInteger(saved.last) ? G.clamp(saved.last, 0, LAST) : 0, clear: !!saved.clear } : { v: 1, max: 0, last: 0, clear: false };
  G.progress = {
    // 只把“能玩的章节”算进继续：第1章还没做时，打完序章也不该出现一个点了没反应的「继续」
    get max() { let m = Math.min(progress.max, LAST); while (m > 0 && !G.CHAPTERS[m].run) m--; return m; },
    get clear() { return progress.clear; },
    reach(i) { progress.max = Math.max(progress.max, G.clamp(i, 0, LAST)); G.store.set(KEY, progress); },
    start(i) { progress.last = i; this.reach(i); },
    finish() { progress.clear = true; G.store.set(KEY, progress); },
  };
  let titleBg, menuTask = 0, transitioning = false;
  const text = (g, s, x, y, col = '#fff4d6', size = 16, align = 'left') => G['f' + size].draw(g, s, x, y, col, { align, outline: '#130b20' });
  async function controls() {
    await G.ui.notice({ title: '操作说明', text: '方向键 / WASD 移动；Q 换队长。\n自由：E 调查、说话；U 疯狂钻石修复（对着坏掉的东西）。\n战斗：J 三连与连打；K 闪避；L 格挡，\n看准命中前按 L 弹反；能量满了按 U 必杀。\nEnter / 空格 / 点击确认；Esc 暂停。' });
  }
  async function hairBook() {
    await G.ui.notice({ title: '东方仗助 发型记录', text: G.P4.hair.pageText() });
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
    let page = 0;
    const pages = Math.ceil(G.CHAPTERS.length / 5);
    for (;;) {
      const start = page * 5, cs = G.CHAPTERS.slice(start, start + 5);
      const opts = cs.map(c => c.title + (c.run ? '' : '（制作中）'));
      const prev = opts.length; opts.push('上一页'); const next = opts.length; opts.push('下一页'); const back = opts.length; opts.push('返回');
      const i = await G.ui.openMenu('选择章节　' + (page + 1) + ' / ' + pages, opts, { escIndex: back });
      if (i === back) return null;
      if (i === prev) { page = (page + pages - 1) % pages; continue; }
      if (i === next) { page = (page + 1) % pages; continue; }
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
      add('从序章开始', () => G.playFrom(0)); add('选择章节', async () => { const idx = await chapterMenu(); if (idx != null) await G.playFrom(idx); });
      add('操作说明', controls); add('发型记录', hairBook); add('设置', settings);
      const i = await G.ui.openMenu('', opts, { y: 214, note: '同人游戏，免费体验。角色版权归原作者。' });
      if (token !== menuTask) return;
      await actions[i]();
    }
  }
  // 标题：夕阳下的杜王町屋顶，三个人逆光站在左右两侧的樱花树下，中间留给菜单
  const TITLE_CAST = [['koichi', 34, 1], ['josuke', 66, 1], ['jotaro4', 268, -1]];
  const titleScene = {
    name: 'title', frozen: false,
    update(dt) { G.ui.update(dt); },
    drawWorld(g) {
      if (titleBg) titleBg.draw(g, 0, G.clk.world, { state: {} });
      for (const [cid, x, facing] of TITLE_CAST) {
        G.atlas(cid).draw(g, 'idle', 0, x, 170, { flip: facing < 0, backlit: { dark: '#140a18', k: .88, rim: '#ffb070' } });
      }
    },
    drawUI(g) {
      const meta = G.D.ui && G.D.ui.logo && G.D.ui.logo.main;
      const im = G.image(typeof meta === 'string' ? meta : meta && meta.image || 'ui/logo_main');
      if (G.ready(im)) {
        // 整数倍放大：像素字的笔画才不会一粗一细
        const k = Math.max(1, Math.floor(Math.min(520 / im.width, 150 / im.height)));
        g.drawImage(im, Math.round(320 - im.width * k / 2), 22, Math.round(im.width * k), Math.round(im.height * k));
      } else text(g, 'JoJo的奇妙冒险　不灭钻石', 320, 55, '#ffe070', 16, 'center');
      text(g, '同人像素游戏', 320, 116, '#ffd9a0', 12, 'center');   // 菜单框会盖到下半屏，副标题放在标志下面
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
      const i = await G.ui.openMenu('暂停', ['继续', '发型记录', '操作说明', '设置', '返回标题'], { escIndex: 0 });
      if (i === 0) break;
      if (i === 1) await hairBook();
      if (i === 2) await controls();
      if (i === 3) await settings();
      if (i === 4) { await G.goTitle(); break; }
    }
    gameScene.frozen = false;
  }
  function reset() {
    G.cancelRun(); G.S.busy = false; G.S.cardOn = false; G.S.ambient(null); G.S._filters.clear(); G.ui.reset(); G.party.reset(); G.post.clear(); G.fx.clear();
    if (G.time && G.time.clear) G.time.clear();
    if (G.P4 && G.P4.clearOverlays) G.P4.clearOverlays();
    G.world.insert = null; G.world.cine = null; G.world.stage = null; G.world.player = null; G.world.fight = null;
    G.world.combat = false; G.world.free = false; G.world.ticks = []; G.world.anims = []; G.world.shots = []; G.world.hazards = [];
    G.world.focus = null; G.world.slow = 1; G.lateGame = null; G.midGame = null;
    G.world.zoom = null; G.cam.zoom = null; G.cam.x = 0; G.cam.y = 0; G.cam.shakeDur = 0;
    G.slowAllK = 1; G.slowAllT = 0; G.hitStopAll_t = 0; G.fadeA = 0; G.flags = {}; G.input.clear();
    gameScene.frozen = false;
  }
  G.goTitle = async route => {
    reset(); G.curChapter = null; G.setScene(titleScene);
    G.audio.music('title', { fade: 1.5 });
    const token = ++menuTask; titleMenu(token, route).catch(showError);
  };
  G.playFrom = async idx => {
    const c = G.CHAPTERS[idx];
    if (transitioning || !c || !c.run) return;
    transitioning = true; menuTask++; reset(); G.curChapter = idx; G.progress.start(idx);
    G.setScene(gameScene); G.fadeA = 1;
    const id = G.runId;
    try {
      G.audio.stopMusic(.8); await G.res.loadPack('bg_common'); await G.res.loadPack('bg_' + c.key);
      G.audio.releaseExcept(c.music); G.audio.prefetch(c.music.slice(0, 2)); transitioning = false;
      await c.run(G.S);
      if (id !== G.runId) return;
      if (idx === LAST) G.progress.finish(); else G.progress.reach(idx + 1);
      G.ui.hints = []; G.post.clear(); G.cam.zoom = null; G.world.zoom = null;
      const next = G.CHAPTERS[idx + 1];
      if (next && !next.run) {
        G.fadeA = 0;   // 黑幕画在 UI 层上面，会把提示框整个盖住
        await G.ui.notice({ title: c.title + '　完', text: '感谢游玩！\n' + next.title + '「' + next.sub + '」还在制作中，敬请期待。' });
      }
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
    if (!G.D) { el.textContent = '缺少 data/data_meta.js：先运行 python3 第四部/tools/build_p4.py'; return; }
    await G.res.preloadPack('core', (n, total) => { el.textContent = '载入角色与字库：' + n + ' / ' + total; });
    G.initFonts(); G.audio.init(); await G.audio.loadSfx();
    await G.res.loadPack('bg_title'); titleBg = new G.Background(G.D.bg.title_morioh);
    G.start(); await G.goTitle(); el.remove(); G.booted = true;
  }
  boot().catch(showError);
})();
