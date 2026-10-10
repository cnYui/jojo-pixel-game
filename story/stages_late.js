// 后段地图独立登记，保证切章不会复用上一章的机关或演员。
'use strict';
(function () {
  const G = window.G, ST = G.STAGES;
  const map = (id, bg, width, ymin, ymax, music = 'tension') => ({ id, bg, x0: 8, x1: width - 8,
    yMin: ymin, yMax: ymax, music, camX: 0, props: [], npcs: [], hotspots: [], triggers: [], obstacles: [] });
  ST.cafe_ch10 = map('cafe_ch10', 'cafe_interior', 320, 150, 172, 'daily');
  ST.cairo_day_ch10 = map('cairo_day_ch10', 'cairo_day', 960, 150, 176, 'daily');
  ST.sewer_ch10 = map('sewer_ch10', 'cairo_sewer', 640, 148, 172);
  ST.flashback_ch10 = map('flashback_ch10', 'mansion_hall', 320, 148, 172, 'ominous');
  ST.mansion_ext_ch11 = map('mansion_ext_ch11', 'mansion_exterior', 320, 150, 172, 'ominous');
  ST.corridor_ch11 = map('corridor_ch11', 'mansion_corridor', 640, 150, 174, 'ominous');
  ST.game_ch11 = map('game_ch11', 'game_room', 320, 150, 172);
  ST.illusion_ch11 = map('illusion_ch11', 'illusion_corridor', 640, 150, 174);
  ST.hall_ch11 = map('hall_ch11', 'mansion_hall', 320, 148, 174);
  ST.tower_ch11 = map('tower_ch11', 'mansion_tower', 320, 150, 172, 'ominous');
  ST.stairs_fin = map('stairs_fin', 'mansion_stairs', 320, 146, 174, 'ominous');
  ST.chase_fin = map('chase_fin', 'cairo_street_night', 960, 150, 176, 'boss');
  ST.roof_fin = map('roof_fin', 'cairo_rooftops', 640, 145, 176, 'boss');
  ST.street_fin = map('street_fin', 'cairo_street_night', 960, 148, 176, 'boss');
  ST.dawn_fin = map('dawn_fin', 'cairo_street_dawn', 960, 148, 176, 'sad');
  ST.bedroom_fin = map('bedroom_fin', 'kujo_bedroom_morning', 320, 150, 176, 'ending');
  ST.airport_fin = map('airport_fin', 'airport', 320, 150, 176, 'ending');
  Object.assign(G.NAMES, { darby: '丹尼尔·J·达比', telence: '泰伦斯·T·达比', holhorse: '荷尔·荷斯',
    boingo: '波因哥', petshop: '佩特夏普', kennyg: '肯尼·G', vanilla: '瓦尼拉·艾斯',
    nukesaku: '努凯萨克', dio: 'DIO', wilson: '威尔逊·菲利普斯' });
})();
