// 地图几何集中登记，后续剧情只添加交互点，避免改变已约定的比例与背景键。
'use strict';
(function () {
  const G = window.G;
  G.NAMES = { giorno: '乔鲁诺', bucciarati: '布加拉提', koichi: '康一', jotaro4: '承太郎',
    luca: '卢卡', police: '警官', passer_m: '路人', passer_f: '路人', goldexp: '黄金体验', stickyfingers: '钢链手指', echoes3: '回音 ACT3' };
  const walls = (a, b, w) => [{ x0: -40, x1: a, y0: 0, y1: 240 }, { x0: b, x1: w + 40, y0: 0, y1: 240 }];
  const base = (id, bg, w, o = {}) => Object.assign({ id, bg, x0: 0, x1: w, camX: 0,
    music: 'daily', props: [], npcs: [], hotspots: [], triggers: [], obstacles: walls(8, w - 8, w),
    dlgPos: 'top', dlgPosFight: 'bottom' }, o);
  G.p5Stage = { base, walls };
  for (const [id, bg, w] of [
    ['map_pro', 'naples_map', 320], ['airin_pro', 'airport_hall', 480], ['airout_pro', 'airport_out', 640],
    ['street_ch1', 'naples_street', 480], ['cafe_ch1', 'naples_cafe', 480], ['station_ch1', 'funicular_station', 480],
    ['car_ch1', 'funicular_car', 320], ['square_ch1', 'station_square', 640], ['harbor_ch1', 'naples_harbor', 640],
  ]) G.STAGES[id] = base(id, bg, w, id === 'map_pro' ? { music: null } : {});
})();
