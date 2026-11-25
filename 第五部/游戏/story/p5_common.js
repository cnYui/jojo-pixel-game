// 这里只提供可走动的角色参数；第五部招式和替身调查由后续剧情、战斗任务实现。
'use strict';
(function () {
  const G = window.G;
  G.P5 = { clearOverlays() {} };
  for (const [cid, hp, standId] of [['giorno', 120, 'goldexp'], ['bucciarati', 140, 'stickyfingers'], ['koichi', 100, 'echoes3']]) {
    G.KITS[cid] = { hp, speed: 66, standId };
  }
  G.P5.openShell = async (S, chapter, stage, leader) => {
    await S.chapterCard(chapter);
    S.party([leader], { leader });
    await S.setStage(stage, { x: 80, y: 160, facing: 1 });
    S.free(true);
    S.hint('方向键 / WASD 移动　Esc 暂停', 8);
    // 空壳停在自由走动，不触发假通关；回标题由既有暂停菜单取消本次流程。
    await S.until(() => false);
  };
})();
