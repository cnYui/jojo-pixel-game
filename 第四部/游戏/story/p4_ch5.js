// 第5章　露伴宅 / 漫画家与猎鼠（G.STORY.ch5，地图 id 后缀 _ch5）：剧情节拍、地图、自由走动。还没做：空壳先占住 index.html 里的位置，
//   各章只改自己的这两份文件（p4_ch5.js、p4_ch5_fights.js），不用碰 index.html 和 main.js。
//   做这一章时：在这里注册 G.STORY.ch5 = async function (S) { … }（有了它章节菜单就能进），地图用 G.p4Stage.base；
//   开发脚本写在 第四部/docs/第5章_开发脚本.md。规矩见 第四部/docs/分章开发约定.md
'use strict';
(function () {
  const G = window.G;
  // 露伴当队长时按 U：天堂之门把对方“翻开成书”读一读（tags 'read'）。读的内容由调查点自己的 look 演
  G.LOOK.rohan = {
    tags: ['read'], cd: 1, miss: '……这个没什么好读的。',
    run: async (S, p, h) => {
      if (h) S.face(p, h.x > p.x ? 1 : h.x < p.x ? -1 : p.facing);
      await S.summon(p, { dur: 0.14, rise: 4 });
      S.standAct(p, 'write', { dx: 16, z: 4, dur: 0.7 });
      S.sfx('card_flip', 0.8);
      if (h) S.fx('glint', { x: h.x, y: h.y - 14, size: 7 }, { life: 0.4 });
      await S.wait(0.5);
    },
  };
})();
