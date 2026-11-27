// 第五部入口沿用现成引擎；序章和第1章仍可直接试玩，后续按通关记录解锁。
'use strict';
(function () {
  const G = window.G;
  const names = [
    [
        "prologue",
        "序章　那不勒斯",
        "黄金之风"
    ],
    [
        "ch1",
        "第1章　街头干部",
        "布加拉提登场"
    ],
    [
        "ch2",
        "第2章　监狱面试",
        "黑色安息日"
    ],
    [
        "ch3",
        "第3章　卡普里岛",
        "宝藏"
    ],
    [
        "ch4",
        "第4章　庞贝",
        "镜中人"
    ],
    [
        "ch5",
        "第5章　特快列车",
        "壮烈成仁与沙滩男孩"
    ],
    [
        "ch6",
        "第6章　娃娃脸与白色相簿",
        "公路追击"
    ],
    [
        "ch7",
        "第7章　威尼斯",
        "老板"
    ],
    [
        "ch8",
        "第8章　撒丁岛",
        "过去"
    ],
    [
        "final",
        "终章　罗马",
        "镇魂曲"
    ]
];
  const LAST = names.length - 1;
  G.CHAPTERS = names.map(([key, title, sub], i) => ({ key, title, sub, run: G.STORY[key] || null,
    music: ['daily', 'tension', 'battle', 'sad', 'victory'], next: i + 1 }));
  G.DEMO = null;
  G.curChapter = null;
  const KEY = 'p5-progress';
  const saved = G.store.get(KEY, null);
  const valid = saved && saved.v === 1 && Number.isInteger(saved.max) && saved.max >= 0 && saved.max <= LAST;
  const progress = valid ? { v: 1, max: saved.max, last: Number.isInteger(saved.last) ? G.clamp(saved.last, 0, LAST) : 0, clear: !!saved.clear } : { v: 1, max: 0, last: 0, clear: false };
  G.ach.init(G.CHAPTERS, valid ? progress : null);
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
    await G.ui.notice({ title: '操作说明', text: '方向键 / WASD 移动；Q 换队长。\n自由：E 调查、说话；U 黄金体验赋予生命。\n战斗：J 三连与连打；K 闪避；L 格挡，\n看准命中前按 L 弹反；能量满了按 U 必杀。\nEnter / 空格 / 点击确认；Esc 暂停。' });
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
      const allowed = Math.max(1, G.progress.max);
      const disabled = cs.map((c, i) => !c.run || start + i > allowed ? i : -1).filter(i => i >= 0);
      const opts = cs.map((c, i) => c.title + (!c.run ? '（制作中）' : disabled.includes(i) ? '（未解锁）' : ''));
      const prev = opts.length; opts.push('上一页'); const next = opts.length; opts.push('下一页'); const back = opts.length; opts.push('返回');
      const i = await G.ui.openMenu('选择章节　' + (page + 1) + ' / ' + pages, opts, { escIndex: back, disabled });
      if (i === back) return null;
      if (i === prev) { page = (page + pages - 1) % pages; continue; }
      if (i === next) { page = (page + 1) % pages; continue; }
      if (disabled.includes(i) && cs[i].run) continue;
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
      add('操作说明', controls); add('设置', settings);
      add('成就 ' + G.ach.count() + ' / ' + G.ach.list().length, () => G.uiAch.open());
      const i = await G.ui.openMenu('', opts, { y: 214, dim: 0, note: '同人游戏，免费体验。角色版权归原作者。' });
      if (token !== menuTask) return;
      await actions[i]();
    }
  }
  // 标题菜单不压暗背景人物，保证第五部角色和标题同时可辨。
  const TITLE_CAST = [['giorno', 48, 1], ['bucciarati', 272, -1]];
  const titleScene = {
    name: 'title', frozen: false,
    update(dt) { G.ui.update(dt); },
    drawWorld(g) {
      if (titleBg) titleBg.draw(g, 0, G.clk.world, { state: {} });
      for (const [cid, x, facing] of TITLE_CAST) {
        G.atlas(cid).draw(g, 'idle', G.clk.ui, x, 170, { flip: facing < 0 });
      }
    },
    drawUI(g) {
      const meta = G.D.ui && G.D.ui.logo && G.D.ui.logo.main;
      const im = G.image(typeof meta === 'string' ? meta : meta && meta.image || 'ui/logo_main');
      if (G.ready(im)) {
        // 整数倍放大：像素字的笔画才不会一粗一细
        const k = Math.max(1, Math.floor(Math.min(520 / im.width, 150 / im.height)));
        const x = Math.round(320 - im.width * k / 2);
        // 海湾的亮部会吞掉浅色笔画，用暗底衬保证菜单出现时标题仍清楚。
        g.fillStyle = '#20142bd9'; g.fillRect(x - 10, 16, im.width * k + 20, im.height * k + 12);
        g.drawImage(im, x, 22, Math.round(im.width * k), Math.round(im.height * k));
      } else text(g, 'JoJo的奇妙冒险　黄金之风', 320, 55, '#ffe070', 16, 'center');
      text(g, '同人像素游戏', 320, 116, '#ffd9a0', 12, 'center');   // 菜单框会盖到下半屏，副标题放在标志下面
      if (progress.clear) text(g, '★', 610, 14, '#ffe040');
      G.ui.draw(g);
      G.uiAch.drawToast(g);
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
    drawWorld: g => G.world.draw(g),
    drawUI(g) { G.ui.draw(g); G.uiAch.drawToast(g); },
    drawTop: g => G.ui.drawTop(g),
    hasPixel: () => G.world.hasPixel(), drawPixel: (P, layer) => G.world.drawPixel(P, layer),
    hasOver: () => G.world.hasOver(), drawOver: g => G.world.drawOver(g),
  };
  async function pause() {
    // 暂停后世界不再更新，连打停在半空、拳声循环却照响（暂停菜单里一直是连打声）：先把主控的连打收掉
    if (G.world.player && G.combat && G.combat.stopRush) G.combat.stopRush(G.world.player);
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
    // 回标题 / 换章会把整个世界丢掉：谁身上还挂着连打，拳声循环的句柄跟着丢，就在标题画面里一直响。先记下场景，世界清空后再收
    const oldStage = G.world.stage;
    G.cancelRun(); G.S.busy = false; G.S.cardOn = false; G.S.ambient(null); G.S._filters.clear(); G.ui.reset(); G.party.reset(); G.post.clear(); G.fx.clear();
    if (G.time && G.time.clear) G.time.clear();
    if (G.P5 && G.P5.clearOverlays) G.P5.clearOverlays();
    G.world.insert = null; G.world.cine = null; G.world.stage = null; G.world.player = null; G.world.fight = null;
    G.world.combat = false; G.world.free = false; G.world.ticks = []; G.world.anims = []; G.world.shots = []; G.world.hazards = [];
    G.world.focus = null; G.world.slow = 1; G.lateGame = null; G.midGame = null;
    G.world.zoom = null; G.cam.zoom = null; G.cam.x = 0; G.cam.y = 0; G.cam.shakeDur = 0;
    G.slowAllK = 1; G.slowAllT = 0; G.hitStopAll_t = 0; G.fadeA = 0; G.flags = {}; G.input.clear();
    // 战斗已经清空（W.fight = null），收连打时发的 rushEnd 不会再进到剧情的监听里
    if (oldStage && G.combat && G.combat.stopRush) for (const a of oldStage.actors) G.combat.stopRush(a);
    gameScene.frozen = false;
  }
  G.goTitle = async route => {
    reset(); G.curChapter = null; G.setScene(titleScene);
    G.audio.music(G.D.audio.music.title_song ? 'title_song' : 'title', { fade: 1.5 });
    const token = ++menuTask; titleMenu(token, route).catch(showError);
  };
  // 一章的地图常借别章的背景（学校走廊、商店街、杜王大酒店……），背景图按章分包，只载 bg_<本章> 会缺图。
  //   按地图 id 的后缀（_pro / _chN / _fin）找出这一章的地图，看它们的背景在哪个包里，一起载入；
  //   剧情里中途换的背景（地图 id 对不上的）在 G.STORY.chN.packs 里补，比如 ['bg_ch2']
  const SUFFIX = { prologue: '_pro', final: '_fin' };
  function chapterPacks(c) {
    const suf = SUFFIX[c.key] || '_' + c.key, want = new Set((c.run && c.run.packs) || []);
    const packs = (G.D && G.D.packs) || {};
    for (const st of Object.values(G.STAGES || {})) {
      if (!st || !st.id || !st.id.endsWith(suf) || typeof st.bg !== 'string') continue;
      for (const [name, p] of Object.entries(packs)) if (p.bg && p.bg.indexOf(st.bg) >= 0) want.add(name);
    }
    want.delete('bg_common'); want.delete('bg_' + c.key);
    return [...want];
  }
  G.playFrom = async idx => {
    const c = G.CHAPTERS[idx];
    if (transitioning || !c || !c.run) return;
    transitioning = true; menuTask++; reset(); G.curChapter = idx; G.progress.start(idx);
    G.setScene(gameScene); G.fadeA = 1;
    const id = G.runId;
    try {
      G.audio.stopMusic(.8); await G.res.loadPack('bg_common'); await G.res.loadPack('bg_' + c.key);
      for (const p of chapterPacks(c)) await G.res.loadPack(p);
      G.audio.releaseExcept(c.music); G.audio.prefetch(c.music.slice(0, 2)); transitioning = false;
      await c.run(G.S);
      if (id !== G.runId) return;
      G.ach.chapterDone(c.key);
      if (idx === LAST) G.progress.finish(); else G.progress.reach(idx + 1);
      G.ui.hints = []; G.post.clear(); G.cam.zoom = null; G.world.zoom = null;
      const next = G.CHAPTERS[idx + 1];
      if (next && !next.run) {
        G.fadeA = 0;   // 黑幕画在 UI 层上面，会把提示框整个盖住
        await G.ui.notice({ title: c.title + '　完', text: '感谢游玩！\n' + next.title + '「' + next.sub + '」还在制作中，敬请期待。' });
      }
      const i = await G.ui.openMenu(c.title + '　完', next && next.run ? ['继续下一章', '选择章节', '返回标题'] : ['返回标题', '选择章节'], { escIndex: 0 });
      if (i === 1) await G.goTitle('chapters');
      else if (i === 0 && next && next.run) await G.playFrom(idx + 1); else await G.goTitle();
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
    if (!G.D) { el.textContent = '缺少 data/data_meta.js：先运行 python3 第五部/tools/build_p5.py'; return; }
    await G.res.preloadPack('core', (n, total) => { el.textContent = '载入角色与字库：' + n + ' / ' + total; });
    G.initFonts(); G.audio.init(); await G.audio.loadSfx();
    await G.res.loadPack('bg_title'); titleBg = new G.Background(G.D.bg.p5_title);
    G.start(); await G.goTitle(); el.remove(); G.booted = true;
  }
  boot().catch(showError);
})();
