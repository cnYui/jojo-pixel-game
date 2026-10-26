// 成就系统（用户 2026-10-24：剧情和星尘试炼都要有成就，成就页从主页进）：这里只管存档、事件分发、解锁排队；
//   每条成就的判定写在 story\achievements_def.js，页面和解锁牌的画法在 engine\ui_ach.js。
// 存档键 ach（不碰 progress / extras / settings 的结构）。?autotest=1 时默认关闭，自动测试不会把存档刷满。
'use strict';
(function () {
  const G = window.G;
  const KEY = 'ach';
  const VALID_CAT = { story: 1, trial: 1, meta: 1 };
  const VALID_TIER = { bronze: 1, silver: 1, gold: 1, platinum: 1 };
  const EPOCH = Date.UTC(2026, 9, 24);      // 成就系统上线那天：日期按"第几天"倒推，不受浏览器时区和本机时间回拨影响
  // 徽章等级对应的点数（成就文档 §一）。页面和档案里的总分都由这里算，不手写总数
  const TIER_PTS = { bronze: 5, silver: 10, gold: 20, platinum: 40 };
  // 章节成就的等级分段（成就文档 §2.1）：章序号 ≤4 铜（序章 + 第 1–4 章，共 5 条）、5–8 银、其余（第 9 章起含终章）金。
  //   分段按成就文档的条目走（章节 145 点 = 5×5 + 4×10 + 4×20），不封顶，以后加章就按这条往下算
  const chapterTier = i => (i <= 4 ? 'bronze' : i <= 8 ? 'silver' : 'gold');
  const CHAPTER_ICON = i => (i >= 7 ? 'crown' : 'book');     // 王冠留给后半程和通关感
  const PLAT_ID = 'platinum';
  // 白金的条件是"其余全解锁"（见 unlock），但清单文件仍会注册一条只有名字 / 等级的 meta 定义；
  //   这里注册的占位没有 scope，故意让清单那份盖掉它（define 里对白金放行覆盖），页面就拿到 hidden / hint
  const PLAT_DEF = { id: PLAT_ID, cat: 'meta', tier: 'platinum', name: '白金之星', desc: '解锁其他所有成就。', icon: 'star', on: {} };
  // 计数类合并写：每 5 次变化或 10 s 写一次盘（每次命中都写太重）
  const FLUSH_EVERY = 5;
  const FLUSH_SEC = 10;

  const blank = () => ({ v: 1, got: {}, cnt: {}, sets: {} });
  const isObj = o => !!o && typeof o === 'object' && !Array.isArray(o);
  // 读档容错：不是对象 / 版本不对 / 字段类型不对，一律当空（坏存档不能把成就页弄崩）
  function load() {
    const s = G.store.get(KEY, null);
    if (!isObj(s) || s.v !== 1) return blank();
    const out = blank();
    if (isObj(s.got)) for (const id in s.got) { const t = +s.got[id]; if (t > 0) out.got[id] = t; }
    if (isObj(s.cnt)) for (const k in s.cnt) { const n = +s.cnt[k]; if (n > 0) out.cnt[k] = n; }
    if (isObj(s.sets)) for (const k in s.sets) if (Array.isArray(s.sets[k])) out.sets[k] = s.sets[k].filter(v => typeof v === 'string');
    return out;
  }

  let save = load();
  let needInit = true;        // 章节成就要等 main.js 读 G.CHAPTERS，第一次用到时再生成
  let cntDirty = 0, lastFlush = 0, cacheAll = null, cacheKey = '';
  const toasts = [];          // 排队中的解锁牌（ui_ach 定时取）

  const A = (G.ach = {
    enabled: !(G.dbg && G.dbg.autotest),
    DEFS: [],

    define(def) {
      if (!isObj(def) || !def.id) return;
      // 同名重复注册（脚本被插两次）只留第一份；白金的定义在下面常驻占位（没有 on），
      //   清单文件注册的那份带 hint / scope，要把占位的那份换掉，否则页面丢了提示
      const at = A.DEFS.findIndex(d => d.id === def.id);
      if (at >= 0 && def.id === PLAT_ID) A.DEFS[at] = def;
      else if (at >= 0) return;
      else {
        if (!VALID_CAT[def.cat] || !VALID_TIER[def.tier]) return;
        A.DEFS.push(def);
      }
      cacheAll = null;                                   // 定义变了：列表缓存作废
    },
    // 打开时补一次条件检查：enable 之前 unlock 都是空转，autotest 里先喂事件再开也能认
    enable(on) {
      A.enabled = !!on;
      if (A.enabled) A.recheck();
      else if (toasts.length) toasts.length = 0;     // 关掉时把没出的解锁牌丢掉，别留到下次打开才冒出来
    },

    // ------------------------------------------------------------ 章节成就（懒生成）
    // 13 条由 G.CHAPTERS 循环生成；main.js 在成就之后加载，所以不能在脚本加载时读
    initChapters() {
      const list = G.CHAPTERS;
      if (!Array.isArray(list) || !list.length) return false;
      list.forEach((c, i) => {
        // 成就文档的 id 是 ch_prologue / ch_1 … ch_final：章 key 里的 "ch" 前缀去掉（ch1 → 1）
        const id = 'ch_' + String(c.key).replace(/^ch(?=\d)/, '');
        A.define({
          id, cat: 'story', tier: chapterTier(i), name: c.sub || c.title,
          desc: '打完《' + c.title + '》。', icon: CHAPTER_ICON(i), scope: i,
          on: { chapter_done: (e, X) => { if (e && e.idx === i) X.unlock(id); } },
        });
      });
      needInit = false;
      cacheAll = null;
      return true;
    },

    // 当前包开放的成就：体验版里 trial 类整类不出现，章节成就只到 G.DEMO.last，战斗成就按它所属章
    list(cat) {
      if (needInit) A.initChapters();
      if (cacheAll && cacheKey === A.cacheKeyOf()) return cat && cat !== 'all' ? cacheAll.filter(d => d.cat === cat) : cacheAll.slice();
      const demo = G.DEMO || null;
      const out = A.DEFS.filter(d => !demo || A.openIn(demo, d));
      out.sort((a, b) => (a.id === PLAT_ID) - (b.id === PLAT_ID));      // 白金永远排最后
      cacheAll = out;
      cacheKey = A.cacheKeyOf();
      return cat && cat !== 'all' ? out.filter(d => d.cat === cat) : out.slice();
    },
    // 过滤条件的签名：DEMO 和章节表变了才重建缓存（章节战斗成就反查章节表，表变了过滤结果也会变）
    cacheKeyOf() { return (G.DEMO ? 'd' + G.DEMO.last : '-') + '|' + A.DEFS.length + '|' + ((G.CHAPTERS && G.CHAPTERS.length) | 0); },
    openIn(demo, d) {
      if (d.cat === 'trial') return false;
      if (d.cat === 'meta') return true;             // 白金由 unlock 时单独判「当前列表里其余全解锁」
      // 章节成就的 scope = 章序号；战斗成就的 scope = 战斗 id（到章节表 / 挑战登记表里反查所属章）
      const last = demo.last | 0;
      if (typeof d.scope === 'number') return d.scope <= last;
      const key = A.chapterOf(d.scope);
      const ci = (G.CHAPTERS || []).findIndex(c => c.key === key);
      return ci < 0 || ci <= last;
    },
    // 到章节表里按战斗 id 反查所属章（战斗成就的 scope 写的是战斗 id 或章 key）
    chapterOf(scope) {
      const cs = G.CHAPTERS || [];
      const own = cs.find(c => c.key === scope);
      if (own) return own.key;
      const chal = G.EXTRA && G.EXTRA.CHALLENGES;
      if (Array.isArray(chal)) { const d = chal.find(x => x.id === scope); if (d) return d.chapter; }
      return null;
    },

    // ------------------------------------------------------------ 查
    // 解锁时间戳（ms）：存档只记「第几天」（见 write），这里还原成日期用于显示
    dateOf(id) { const d = save.got[id]; return d > 0 ? EPOCH + (d - 1) * 864e5 : 0; },
    has(id) { if (needInit) A.initChapters(); return save.got[id] > 0; },
    at(id) { if (needInit) A.initChapters(); return save.got[id] || 0; },
    count(key) { return save.cnt[key] || 0; },
    max(key, v) {
      if (!A.enabled) return save.cnt[key] || 0;
      const n = +v || 0;
      if (n <= (save.cnt[key] || 0)) return save.cnt[key] || 0;
      save.cnt[key] = n; cntDirty++;
      A.schedule();
      A.recheck();
      return save.cnt[key];
    },
    add(key, n = 1) {
      if (!A.enabled) return save.cnt[key] || 0;
      save.cnt[key] = (save.cnt[key] || 0) + n;
      cntDirty++;
      A.schedule();
      A.recheck();
      return save.cnt[key];
    },
    // 往集合里记一个值（leaders_6 用）：返回集合大小
    mark(key, val) {
      if (!A.enabled) return (save.sets[key] || []).length;
      const arr = save.sets[key] || (save.sets[key] = []);
      if (val != null && arr.indexOf(val) < 0) { arr.push(val); cntDirty++; A.schedule(); A.recheck(); }
      return arr.length;
    },
    set(key) { return (save.sets[key] || []).slice(); },

    // ------------------------------------------------------------ 解锁
    unlock(id, o) {
      if (!A.enabled || !id) return false;
      if (needInit) A.initChapters();
      if (save.got[id] > 0) return false;
      if (id === PLAT_ID) {                    // 白金自己不算「其余」；体验版里只数当前开放的
        const others = A.list().filter(d => d.id !== PLAT_ID);
        if (!others.length || !others.every(d => save.got[d.id] > 0)) return false;
      }
      // 各条的条件都在自己的 on 里判（unlock 只负责落盘和排队）；白金例外，就是上面那句"其余全解锁"
      // 存的是「从成就系统上线那天起的第几天」而不是 ms：页面只显示月-日，存 ms 会让存档每解锁一条就涨几十字节
      save.got[id] = Math.max(1, Math.floor((((o && o.at) || Date.now()) - EPOCH) / 864e5) + 1);
      A.write();                               // 解锁立即写盘：手机随时被杀进程
      const def = A.DEFS.find(d => d.id === id) || (id === PLAT_ID ? PLAT_DEF : null);
      if (def) A.toast(def);
      if (G.dbg && G.dbg.ev) G.dbg.ev('ach_unlock', { id: def ? def.id : id });
      if (id !== PLAT_ID) A.unlock(PLAT_ID);   // 每解锁一条都给白金一次机会，条件不满足时它自己 return
      return true;
    },
    // 条件检查：计数 / 集合变化、新定义注册、读档之后都调一遍——各条的判定偏"事件式"，
    //   可有些条件不靠事件也会自己满足（读档、容器回读后集合已齐），这里按需再问一次各条定义
    recheck() {
      if (!A.enabled) return;
      if (needInit) A.initChapters();
      for (const d of A.DEFS.slice()) {             // 遍历副本：判定里可能注册新定义
        if (d.check) { try { d.check(A); } catch (e) { if (G.dbg && G.dbg.ev) G.dbg.ev('ach_error', { id: d.id, msg: String(e && e.message) }); } }
      }
      A.unlock(PLAT_ID);
    },

    // ------------------------------------------------------------ 事件
    emit(type, data) {
      if (!A.enabled || !type) return;
      if (needInit && !A.initChapters()) return;    // 章节表还没来：这条事件谁都不该认
      const d = data || {};
      for (const def of A.DEFS.slice()) {           // 判定里可能注册新定义，遍历副本
        const fn = def.on && def.on[type];
        if (!fn) continue;
        try { fn(d, A); } catch (e) { console.error(e); if (G.dbg && G.dbg.ev) G.dbg.ev('ach_error', { id: def.id, type, msg: String(e && e.message) }); }
      }
      A.unlock(PLAT_ID);
    },
    // engine\core.js 的 G.dbg.ev 统一转一手：只认这 5 种（其余判断事件太多，接了没用还费时）
    HOOK: { swap: 1, investigate: 1, souvenir: 1, dio_growth: 1, dio_play_dead: 1 },
    dbgHook(type, e) {
      if (!A.enabled || !A.HOOK[type]) return;
      A.emit(type, e);
    },

    // ------------------------------------------------------------ 汇总
    summary() {
      const list = A.list();
      let got = 0, pts = 0, ptsTotal = 0;
      for (const d of list) {
        const p = TIER_PTS[d.tier] || 0;
        ptsTotal += p;
        if (save.got[d.id] > 0) { got++; pts += p; }
      }
      return { got, total: list.length, pts, ptsTotal };
    },
    state() {
      return { got: Object.keys(save.got), cnt: Object.assign({}, save.cnt), sets: JSON.parse(JSON.stringify(save.sets)) };
    },

    // ------------------------------------------------------------ 解锁牌
    toast(def) {
      if (!def) return;
      if (toasts.some(t => t.def.id === def.id)) return;      // 同一帧解锁两次不叠两条
      toasts.push({ def, t: 0 });
    },
    toastQueue() { return toasts; },

    // ------------------------------------------------------------ 写档
    write() {
      cntDirty = 0; lastFlush = G.clk.ui;
      G.store.set(KEY, save);
    },
    // 计数类合并写：攒够 5 次变化或过了 10 s 才落盘；解锁走 write() 立即写
    schedule() {
      if (cntDirty >= FLUSH_EVERY || G.clk.ui - lastFlush >= FLUSH_SEC) A.write();
    },
    // 计数类的合并写很懒（每 5 次变化或 10 s），切后台 / 关页面前要落盘；没变化就不动
    flush() { if (cntDirty > 0) A.write(); },
    // 清除存档 / 容器回读后重读（G.progress.erase 会调 G.store.reload）
    reload() {
      save = load(); cntDirty = 0; lastFlush = G.clk.ui;
      cacheAll = null;                       // 章节表可能换了（换包 / 调试），列表缓存一起作废
      toasts.length = 0;                     // 旧存档的解锁牌不能盖到新存档的画面上
      A.recheck();
    },

    // ------------------------------------------------------------ 页面
    // G.ui.draw 调的是这个名字；画法在 ui_ach.js（G.uiAch），这里只转一手
    drawToast(g) { if (G.uiAch && G.uiAch.drawToast) G.uiAch.drawToast(g); },
    openPage() {
      if (!G.uiAch || !G.uiAch.openPage) return Promise.resolve();
      return G.uiAch.openPage();
    },
  });

  // 存档被换掉（小红书容器回读到更新的那份、标题里清除存档）后重读，成就页刷新
  G.store.onLoad(() => A.reload());
  // 先给白金占个位（最后一条），其余定义由 story\achievements_def.js 注册
  A.define(PLAT_DEF);
})();
