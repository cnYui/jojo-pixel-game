// 第四部：对话框上的名字 G.NAMES + 序章的地图几何。NPC / 调查点 / 触发区在 story/p4_prologue.js 里往上加。
//   背景元数据（第四部/assets/_meta/bg.json）里有 w、ground、walk、anchors：Stage 自己会读 walk 当可走带、读 w 当地图宽，
//   这里只写左右两堵“墙”和换背景要用的东西。地图 id 一律带 _pro 后缀（和第三部同一个约定）。
'use strict';
(function () {
  const G = window.G;

  // 对话框名字：图集里的全名太长，剧情里都叫短名
  G.NAMES = {
    josuke: '仗助', jotaro4: '承太郎', koichi: '康一', tomoko: '朋子', ryohei: '良平', angelo: '安杰罗', aqua: '水中项链',
    crazyd: '疯狂钻石', thug_a: '学长A', thug_b: '学长B', robber: '劫匪', clerk: '店员', fan_a: '女生', fan_b: '女生',
    flirt: '搭讪的男人', kid: '小学生', granny: '老奶奶', milkman: '送奶工',
  };

  const ST = G.STAGES;
  const walls = (xa, xb, w) => [{ x0: -40, x1: xa, y0: 0, y1: 240 }, { x0: xb, x1: w + 40, y0: 0, y1: 240 }];
  // dlgPos 'top'：第四部的图人都站在画面最下面一条（可走带 y 142–176），底部对话框正好把说话的人整个盖住，
  //   所以对白放上面（engine/ui.js makeDlg 读它；第三部第2–4章的船上、街上也是这么做的）。
  //   战斗里上面是血条和进度 HUD，对白又都是在战斗暂停时说的，所以打架时放回下面（dlgPosFight）
  const base = (id, bg, w, o = {}) => Object.assign({
    id, bg, x0: 0, x1: w, camX: 0, music: 'daily', props: [], npcs: [], hotspots: [], triggers: [], obstacles: walls(8, w - 8, w),
    dlgPos: 'top', dlgPosFight: 'bottom',
  }, o);

  // 节拍 1：杜王町俯视地图（篇章卡之后的日历地图画在插入画面上，这张图只是让世界有个地方站）
  ST.map_pro = base('map_pro', 'morioh_map', 320, { yMin: 160, yMax: 170, music: null, obstacles: [] });
  // 节拍 2–4、8：上学路（960 宽）。早上 / 下午是同一张图：下午打开 tint 层 state.pm
  ST.road_pro = base('road_pro', 'morioh_road', 960, { state: { pm: 0 } });
  // 节拍 5–7、序1：葡萄丘高中校门（640 宽）
  ST.gate_pro = base('gate_pro', 'budou_gate', 640);
  // 节拍 9：超市（640 宽）
  ST.market_pro = base('market_pro', 'supermarket', 640, { obstacles: walls(12, 628, 640) });
  // 节拍 10–12：东方家门口（傍晚 / 夜 / 雨是三张图：S.setStage('house_pro', { bg: 'higashikata_night' })）
  ST.house_pro = base('house_pro', 'higashikata_eve', 640);
  // 序2 段 1：东方家客厅（480 宽）。tint 层 state.fog = 水汽浓度 / 100
  ST.living_pro = base('living_pro', 'higashikata_living', 480, { music: 'tension', state: { fog: 0 }, obstacles: walls(10, 470, 480) });
  // 序2 段 2、节拍 14–15：下雨的海边路（1280 宽），路边有块大岩石；雨停后换 angelo_after
  ST.rain_pro = base('rain_pro', 'angelo_rain', 1280, { music: 'tension', state: { rain: 1 } });
})();
