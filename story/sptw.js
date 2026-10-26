// 承太郎 · 白金之星·世界（终章阶段 3 与星尘试炼共用）
//   终章原来把这段写在 final.js 的 kitOverride 里；抽出来以后，试炼给承太郎换的 kit 也用同一份时停参数，
//   两边不会再各写一遍（改一个常量就能同时影响剧情和试炼）。
//   加载顺序：本文件要排在 story/final.js 之前；final.js 只在运行时读 G.SPTW，脚本加载时不读。
'use strict';
(function () {
  const G = window.G;

  // 蓝色时停：参数照终章阶段 3 的 kitOverride（tint / sfx / burst / dur / resume / 两句大字）
  const STOP = { tint: 'blue', sfx: 'timestop_sp', burst: .4, dur: 2, resume: .36,
    lines: { start: 'jotaro_ts', end: 'jotaro_resume' } };

  // 剧情型 special：combat.special 认作“这一个 kitOverride 的 special”时，run 收到 (S, p, c, C)。
  //   终章阶段 3 原样使用；不 await 时停（和原来一样，run 返回后 special 的 finally 才能放开操作）。
  const storyU = {
    name: '白金之星·世界', need: 100, title: 'jotaro_ts',
    // 能量满才是“窗口开着”：HUD 的「按 U！」和触屏金圈只在真能放的时候出现。
    window: c => c.player.energy >= (c.player.energyMax || 100),
    prompt: '能量满了！按 U：白金之星·世界',
    run(s, p) { G.time.stop(p, STOP); },
  };

  // kit 级 special：K.jotaro.special 的结构（name / title / bg / colours / run / pose），
  //   run 签名 (p, C)。承太郎当 AI 队友时 combat.updateAlly 也会走这里，所以不能依赖 C。
  const kitSpecial = {
    name: '白金之星·世界', need: 100, title: 'jotaro_ts', bg: 'radial', pose: 'cmd',
    colours: ['#1e3f8a', '#0a1a3c', '#3a6ac8'],
    async run(p) {
      const done = G.time.stop(p, STOP);
      // 等整段时停结束时，combat.special 还挂着 special-run 的 cine 和 special 状态，
      //   updatePlayer 会被这两项挡住；先放开，承太郎才能在停止的时间里行动，结束再由 finally 收尾。
      const w = G.world;
      if (w && w.cine && w.cine.by === 'special-run') w.cine = null;
      if (p.state === 'special') { p.state = 'idle'; p.hold = false; if (p.play) p.play('idle'); }
      await done;
    },
  };
  // 试炼的 HUD 倒数用：和 STOP 的时长同源，改 STOP.dur 不用再改 HUD。
  kitSpecial.timeStopSec = STOP.dur;

  G.SPTW = { STOP, storyU, kitSpecial };
})();
