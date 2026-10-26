// 成就清单（docs\ai\context\20261024-174008-成就系统_清单与页面.md §二）：62 条的定义和判定全在这里，
//   engine\achievements.js 只管存档、事件分发和解锁牌；改名字 / 条件 / 点数只动这个文件。
//   章节 13 条不手写：由 G.CHAPTERS 循环生成（等级分段在 achievements.js 的 chapterTier）。
//   试炼 16 条里的「本轮」统计（alive / downs / flawless / sptw / ranks）由 G.TRIAL.run 持有，事件里带过来，这里不自己存。
'use strict';
(function () {
  const G = window.G;
  const A = G.ach;
  if (!A) return;

  // 勋章中间的 14×14 点阵（1 = 亮色 0 = 空）：规划方之后补图案，换这张表不用动页面代码。
  //   未解锁的成就在页面上统一画 lock；其余按 def.icon 取。
  const GLYPH = {
    book: ['..............', '..###....###..', '.##..####..#..', '.#....##....#.', '#.....##......', '#.....##......',
      '#.....##......', '#.....##......', '#.....##......', '#.....##......', '#.....##......', '#.....##......', '#.....##......', '..............'],
    fist: ['..............', '...##.....##..', '..#..#...#..#.', '..#..#...#..#.', '..#..#...#..#.', '..#..######..#.',
      '..#.........#.', '..#.........#.', '...#.......#..', '...#########..', '..#.........#.', '..#.........#.', '...#########..', '.....####.....'],
    star: ['......##......', '......##......', '.....####.....', '.....####.....', '##############', '.############.',
      '..##########..', '...########...', '...########...', '..##########..', '..####..####..', '.###......###.', '.##........##.', '##..........##'],
    lens: ['....######....', '..##......##..', '.#..........#.', '#............#', '#............#', '#............#',
      '#............#', '.#..........#.', '..##..###..##.', '....#######...', '......######..', '.......######.', '........#####.', '.........####.'],
    clock: ['....######....', '..##......##..', '.#....##....#.', '#.....##.....#', '#.....##.....#', '#.....##.....#',
      '#.....####...#', '#............#', '#............#', '.#..........#.', '..##......##..', '....######....', '..............', '..............'],
    // 骷髅只用在 trial_down_first / trial_fail_10：克制，只画轮廓、不画血
    skull: ['....######....', '..##########..', '.###..##..###.', '.##....##....#', '.#.....##....#', '.#...........#',
      '.#....##.....#', '..#..####..#..', '...########...', '....######....', '....#.##.#....', '....######....', '.....####.....', '..............'],
    crown: ['..............', '..##......##..', '..##..##..##..', '..#..#..#..#..', '.##.#.##.#.##.', '.##.######.##.',
      '.###.####.###.', '.#.########.#.', '.#.########.#.', '..##########..', '..##########..', '..##########..', '..##########..', '..............'],
    // 占位：一个圆点（页面和解锁牌先跑通；规划方补图案）
    lock: ['..............', '....######....', '...########...', '..##########..', '.############.', '.############.',
      '.############.', '.############.', '.############.', '.############.', '..##########..', '...########...', '....######....', '..............'],
  };

  // ---------------------------------------------------------------- 小工具
  // 这些表都是边加载边登记（EXTRA 在 achievements.js 之后加载）：每次现取，不在加载时缓存
  const E = () => G.EXTRA || null;
  const wonCount = () => { const X = E(); return X ? +(X.state().won || 0) : 0; };
  const souvCount = () => { const X = E(); return X ? (X.state().souv || []).length : 0; };
  const playSec = () => (G.progress && G.progress.info ? G.progress.info().play || 0 : 0);
  const rankOf = id => (E() && E().rankOf(id)) || {};
  // 挑战列表（和标题「挑战」同一份登记表）
  const challenges = () => (E() ? E().CHALLENGES : []);
  // 当前包开放的章：体验版只到 G.DEMO.last；章节表还没来（成就先加载）时返回 null，调用方当作"全都算"
  const openChapters = () => {
    const cs = G.CHAPTERS;
    if (!Array.isArray(cs) || !cs.length) return null;
    const last = G.DEMO ? G.DEMO.last | 0 : cs.length - 1;
    return cs.filter((c, i) => i <= last);
  };
  const inOpen = chapter => { const list = openChapters(); return !list || list.some(c => c.key === chapter); };
  // 开放章的挑战：体验版里只算开到的章（未开放的章不进包，本来也打不到）
  const openChallenges = () => challenges().filter(d => inOpen(d.chapter));
  // 战斗事件里的 autowin 一律不算（成就文档 §一：G.dbg.autowin 判胜的战斗不算）
  const ok = e => !!(e && !e.autowin);
  // 默认值：剧情类 + 铜 + 拳头图案 + 不限章，后面每条只写自己要改的（等级写错会让总点数不对，所以显式写）
  const def = d => A.define(Object.assign({ cat: 'story', icon: 'fist', scope: null, tier: 'bronze' }, d));

  // ================================================================ 2.2 剧情旅程 · 战斗（10）
  def({ id: 'first_win', tier: 'bronze', name: '初次胜利', desc: '赢下第一场有血条的战斗。',
    on: { fight_won: (e, a) => { if (ok(e)) a.unlock('first_win'); } } });
  // 计数键 foes 存的是存档里"打赢过几场不同的战斗"（选章重温同一个 Boss 不会重复算）
  def({ id: 'foes_5', tier: 'bronze', name: '五个替身使者', desc: '打赢 5 个不同的战斗。', goal: 5,
    on: { fight_won: (e, a) => { if (!ok(e)) return; a.max('foes', wonCount()); if (a.count('foes') >= 5) a.unlock('foes_5'); } } });
  def({ id: 'foes_15', tier: 'silver', name: '十五个替身使者', desc: '打赢 15 个不同的战斗。', goal: 15,
    on: { fight_won: (e, a) => { if (!ok(e)) return; a.max('foes', wonCount()); if (a.count('foes') >= 15) a.unlock('foes_15'); } } });
  def({ id: 'foes_all', tier: 'gold', name: '全部击破', desc: '打赢「挑战」列表里的每一场。',
    on: { fight_won: (e, a) => {
      if (!ok(e)) return;
      const list = openChallenges(), X = E();
      if (X && list.length && list.every(d => X.wonOnce(d.id))) a.unlock('foes_all');
    } } });
  // 单场胜利：id 是成就 id，battle 是战斗 id（也是 scope：体验版按它所属章过滤）
  const winOn = (id, name, desc, tier, battle) => def({ id, tier, name, desc, scope: battle,
    on: { fight_won: (e, a) => { if (ok(e) && e.id === battle) a.unlock(id); } } });
  winOn('win_chariot', '战车之剑', '阿布德尔对银色战车，打赢。', 'bronze', 'b02_chariot');
  winOn('win_hanged', '镜中的敌人', '打赢皇帝与倒吊人。', 'bronze', 'b07_hangedman');
  winOn('win_sun', '正午的太阳', '打赢太阳。', 'silver', 'b12_sun');
  winOn('win_anubis', '无法被挡下的刀', '打赢阿努比斯神。', 'silver', 'b18a_anubis');
  winOn('win_cream', '看不见的虚空', '打赢瓦尼拉·艾斯的虚空冲刺。', 'silver', 'b26b_cream');
  winOn('win_dio', '时间开始流动', '打赢 DIO 最后一段。', 'gold', 'b28d3_dio');

  // ================================================================ 2.3 剧情旅程 · 技巧（14）
  def({ id: 'rank_s_1', tier: 'bronze', name: 'S 评价', desc: '拿到第一个 S 评价。',
    on: { fight_won: (e, a) => { if (ok(e) && e.rank === 'S') a.unlock('rank_s_1'); } } });
  def({ id: 'rank_s_10', tier: 'silver', name: '十个 S', desc: '累计 10 场战斗拿到 S（每场取最佳）。', goal: 10,
    on: { fight_won: (e, a) => {
      if (!ok(e)) return;
      const X = E(), ranks = X ? X.state().ranks : {};
      a.max('rank_s', Object.keys(ranks).filter(id => ranks[id] && ranks[id].rank === 'S').length);
      if (a.count('rank_s') >= 10) a.unlock('rank_s_10');
    } } });
  def({ id: 'rank_s_all', tier: 'platinum', name: '完美的旅途', desc: '「挑战」列表的每一场都拿到 S。', icon: 'crown',
    on: { fight_won: (e, a) => {
      if (!ok(e)) return;
      const list = openChallenges();
      if (list.length && list.every(d => rankOf(d.id).rank === 'S')) a.unlock('rank_s_all');
    } } });
  def({ id: 'no_hit', tier: 'silver', name: '毫发无伤', desc: '能输的战斗里，一下都没被打到就赢了。',
    on: { fight_won: (e, a) => { if (ok(e) && e.losable && e.hurt === 0) a.unlock('no_hit'); } } });
  def({ id: 'last_stand', tier: 'silver', name: '千钧一发', desc: '剩下不到一成血，打赢。',
    on: { fight_won: (e, a) => { if (ok(e) && e.hpLeft != null && e.hpLeft <= 0.1) a.unlock('last_stand'); } } });
  def({ id: 'parry_8', tier: 'silver', name: '精准的守护', desc: '一场战斗里精准格挡 8 次。',
    on: { fight_won: (e, a) => { if (ok(e) && e.parry >= 8) a.unlock('parry_8'); } } });
  def({ id: 'graze_8', tier: 'silver', name: '擦身而过', desc: '一场战斗里看穿（擦身闪避）8 次。',
    on: { fight_won: (e, a) => { if (ok(e) && e.graze >= 8) a.unlock('graze_8'); } } });
  def({ id: 'ora_100', tier: 'bronze', name: '欧拉欧拉欧拉', desc: '一场战斗里连打命中 100 次。',
    on: { fight_won: (e, a) => { if (ok(e) && e.rushHits >= 100) a.unlock('ora_100'); } } });
  def({ id: 'special_10', tier: 'bronze', name: '必杀', desc: '累计放出 10 次 U 必杀。', goal: 10,
    // 计数走 a.add（每次放就记一次）；够数的那一刻解锁，不等这场打完
    on: { special: (e, a) => { if (a.add('special', 1) >= 10) a.unlock('special_10'); } } });
  def({ id: 'comeback', tier: 'bronze', name: '不屈', desc: '输过 3 次以上，仍然赢了。',
    on: { fight_won: (e, a) => { if (ok(e) && e.attempts >= 4) a.unlock('comeback'); } } });
  // sptw_first / leaders_6 另外带 check：积够的证据会跟着存档走（计数 / 集合），
  //   读档或重新打开成就时再补判一次，就不用"这一次事件恰好把所有人凑齐"才解锁
  def({ id: 'sptw_first', tier: 'bronze', name: '白金之星·世界', desc: '第一次让时间停下。', icon: 'clock',
    on: { timestop: (e, a) => { if (e.by === 'jotaro') a.unlock('sptw_first'); } },
    check: a => { if (a.count('sptw') > 0) a.unlock('sptw_first'); } });
  def({ id: 'sptw_30', tier: 'silver', name: '时间是我的', desc: '累计停下 30 次时间。', icon: 'clock', goal: 30,
    on: { timestop: (e, a) => { if (e.by === 'jotaro' && a.add('sptw', 1) >= 30) a.unlock('sptw_30'); } } });
  // DIO 停止时间里能动的两幕：引擎里本来就有这两个 G.dbg.ev（dbgHook 转进来）
  def({ id: 'dio_growth', tier: 'gold', name: '半秒', desc: '在 DIO 停止的时间里，动了。', hidden: true, icon: 'clock',
    hint: '有人在停止的世界里动了。', on: { dio_growth: (e, a) => a.unlock('dio_growth') } });
  def({ id: 'dio_play_dead', tier: 'silver', name: '停止心跳', desc: '骗过了 DIO。', hidden: true, icon: 'clock',
    hint: '有时候，不动也是一种战斗。', on: { dio_play_dead: (e, a) => a.unlock('dio_play_dead') } });

  // ================================================================ 2.4 剧情旅程 · 探索与其他（8）
  def({ id: 'souv_10', tier: 'bronze', name: '拾荒旅人', desc: '收集 10 件旅途纪念品。', icon: 'lens', goal: 10,
    // 现场取存档里的件数：选章重走时 souv 会掉回原来的值，"取最大"才不会白白丢掉已经够 10 件的记录
    on: { souvenir: (e, a) => { a.max('souv', souvCount()); if (a.count('souv') >= 10) a.unlock('souv_10'); } } });
  def({ id: 'souv_all', tier: 'gold', name: '旅途纪念', desc: '收集全部旅途纪念品。', icon: 'lens',
    on: { souvenir: (e, a) => {
      const X = E(), list = openChapters();
      if (!X || !list) return;
      const all = X.SOUVENIRS.filter(d => list.some(c => c.key === d.chapter));
      if (all.length && all.every(d => X.has(d.id))) a.unlock('souv_all');
    } } });
  def({ id: 'look_30', tier: 'bronze', name: '好奇的承太郎', desc: '累计 30 次替身调查（U）。', icon: 'lens', goal: 30,
    on: { investigate: (e, a) => { if (a.add('investigate', 1) >= 30) a.unlock('look_30'); } } });
  def({ id: 'swap_50', tier: 'bronze', name: '换班', desc: '累计换 50 次队长。', icon: 'star', goal: 50,
    on: { swap: (e, a) => { a.mark('leaders', 'jotaro'); if (a.add('swap', 1) >= 50) a.unlock('swap_50'); } } });
  def({ id: 'leaders_6', tier: 'silver', name: '全员上场', desc: '六位角色都当过队长。', icon: 'star', goal: 6,
    // 开场队长总是承太郎（序章就是他），第一次换人时把他也算进去
    on: { swap: (e, a) => {
      a.mark('leaders', 'jotaro');
      // 集合大小用 mark 的返回值（count 查的是计数表，不查集合）；已经把 6 个人都记过了就不再解锁一次
      if (e.to && a.mark('leaders', e.to) >= 6) a.unlock('leaders_6');
    } },
    // 集合是攒在存档里的：读档后如果已经凑齐（上一次在解锁前就退出了），这里补上。
    //   判定要读当前存档里的集合（a.set），不能读上一个 G.ach 实例的闭包，所以包在函数里现取
    check: a => { if (a.set && a.set('leaders').length >= 6) a.unlock('leaders_6'); } });
  def({ id: 'challenge_first', tier: 'bronze', name: '再战', desc: '在「挑战」里赢下一场。',
    on: { fight_won: (e, a) => { if (ok(e) && e.mode === 'challenge') a.unlock('challenge_first'); } } });
  def({ id: 'play_3h', tier: 'bronze', name: '旅人', desc: '累计游玩 3 小时。', icon: 'clock',
    on: { play: (e, a) => { if (Math.max(+(e && e.sec) || 0, playSec()) >= 10800) a.unlock('play_3h'); } } });
  def({ id: 'play_10h', tier: 'silver', name: '长途旅行', desc: '累计游玩 10 小时。', icon: 'clock',
    on: { play: (e, a) => { if (Math.max(+(e && e.sec) || 0, playSec()) >= 36000) a.unlock('play_10h'); } } });

  // ================================================================ 2.5 星尘试炼（16，全部「仅试炼」）
  // 速战速决 / 光速的阈值就是玩法脚本里的 ⚙ TRIAL.FAST / FAST2：拿试炼自己的常量算，改一处两边一起变
  const fast = k => { const T = G.TRIAL; return T && T.CFG && T.CFG[k] ? T.CFG[k] : (k === 'FAST' ? 2700 : 1800); };
  const trial = d => def(Object.assign({ cat: 'trial', icon: 'star' }, d));
  trial({ id: 'trial_start', tier: 'bronze', name: '踏入试炼', desc: '开始一次星尘试炼。',
    on: { trial_start: (e, a) => a.unlock('trial_start') } });
  const streak = (id, tier, name, n) => trial({ id, tier, name, desc: '一轮里连续通过 ' + n + ' 关。', goal: n,
    // e.n = 本轮已通过的关数（trial_stage 的 payload）
    on: { trial_stage: (e, a) => { if (+e.n >= n) a.unlock(id); } } });
  streak('trial_5', 'bronze', '五连胜', 5);
  streak('trial_10', 'silver', '十连胜', 10);
  streak('trial_15', 'gold', '十五连胜', 15);
  trial({ id: 'trial_clear', tier: 'gold', name: '试炼完成', desc: '通过星尘试炼的最后一关。',
    on: { trial_clear: (e, a) => a.unlock('trial_clear') } });
  trial({ id: 'trial_no_loss', tier: 'platinum', name: '一个都不能少', desc: '通关，而且队伍里没有人倒下。',
    on: { trial_clear: (e, a) => { if (+e.downs === 0 && Array.isArray(e.squad) && e.squad.length >= 2) a.unlock('trial_no_loss'); } } });
  trial({ id: 'trial_solo', tier: 'platinum', name: '孤高的白金之星', desc: '只带承太郎一个人通关。',
    on: { trial_clear: (e, a) => { if (Array.isArray(e.squad) && e.squad.length === 1 && e.squad[0] === 'jotaro') a.unlock('trial_solo'); } } });
  trial({ id: 'trial_duo', tier: 'gold', name: '银色战车与白金之星', desc: '只带承太郎和波鲁纳雷夫通关。',
    on: { trial_clear: (e, a) => {
      const sq = Array.isArray(e.squad) ? e.squad.slice().sort().join(',') : '';
      if (sq === 'jotaro,polnareff') a.unlock('trial_duo');
    } } });
  trial({ id: 'trial_fast', tier: 'silver', name: '速战速决', desc: '45 分钟以内通关。',
    on: { trial_clear: (e, a) => { if (+e.time <= fast('FAST')) a.unlock('trial_fast'); } } });
  trial({ id: 'trial_fast2', tier: 'gold', name: '光速', desc: '30 分钟以内通关。',
    on: { trial_clear: (e, a) => { if (+e.time <= fast('FAST2')) a.unlock('trial_fast2'); } } });
  trial({ id: 'trial_s_all', tier: 'platinum', name: '全 S 试炼', desc: '一轮里每一关都拿 S。',
    on: { trial_clear: (e, a) => {
      const r = e.ranks;
      const keys = r && typeof r === 'object' ? Object.keys(r) : [];
      const n = e.n != null ? +e.n : keys.length;      // e.n = 本轮通过的关数
      if (n > 0 && keys.length >= n && keys.every(k => (r[k] && r[k].rank ? r[k].rank : r[k]) === 'S')) a.unlock('trial_s_all');
    } } });
  trial({ id: 'trial_flawless_5', tier: 'silver', name: '无伤五次', desc: '一轮里有 5 关一下都没被打到。', goal: 5,
    on: { trial_stage: (e, a) => { if (+e.flawless >= 5) a.unlock('trial_flawless_5'); } } });
  trial({ id: 'trial_time_30', tier: 'silver', name: '时间统治者', desc: '一轮里停下 30 次时间。', goal: 30,
    on: { trial_stage: (e, a) => { if (+e.sptw >= 30) a.unlock('trial_time_30'); } } });
  trial({ id: 'trial_last_one', tier: 'gold', name: '最后一人', desc: '队伍只剩承太郎一个人时，赢下一关。',
    // 承太郎必选，所以"最后一人"必然是他
    on: { trial_stage: (e, a) => { if (+e.alive === 1 && Array.isArray(e.squad) && e.squad.length >= 2) a.unlock('trial_last_one'); } } });
  trial({ id: 'trial_down_first', tier: 'bronze', name: '再会，伙伴', desc: '第一次失去同伴。', hidden: true, icon: 'skull',
    hint: '有人没能走到最后。', on: { trial_down: (e, a) => a.unlock('trial_down_first') } });
  trial({ id: 'trial_fail_10', tier: 'bronze', name: '不屈的试炼者', desc: '累计失败 10 次。', icon: 'skull', goal: 10,
    on: { trial_over: (e, a) => { if (a.add('trial_over', 1) >= 10) a.unlock('trial_fail_10'); } } });

  // 白金（1 条）在 achievements.js 里注册过了（最后一条），列表里永远排最后。
  // 页面和解锁牌按 def.icon 取图案；未解锁统一画 lock
  A.GLYPH = GLYPH;
  G.ACH_GLYPH = GLYPH;
})();
