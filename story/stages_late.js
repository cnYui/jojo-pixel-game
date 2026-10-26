// 后段地图独立登记，保证切章不会复用上一章的机关或演员。
'use strict';
(function () {
  const G = window.G, ST = G.STAGES;
  const map = (id, bg, width, ymin, ymax, music = 'tension') => ({ id, bg, x0: 8, x1: width - 8,
    yMin: ymin, yMax: ymax, music, camX: 0, props: [], npcs: [], hotspots: [], triggers: [], obstacles: [] });
  ST.cafe_ch10 = map('cafe_ch10', 'cafe_interior', 320, 150, 172, 'daily');
  // 咖啡馆的前景牌桌按 148 这条线参与纵深排序：走在可走带（150–172）里的人画在牌桌前面，
  // 站在桌后的发牌小哥、吧台后的老板被牌桌挡住；不设的话从桌前走过的人会被牌桌整个盖住。
  ST.cafe_ch10.fgDepth = 148;
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
  // 2026-10-18：世界地图过场用的空地图 + 对白放上面（背景重画后人都站在画面下半，同第2–9章）
  ST.map_ch10 = map('map_ch10', 'world_map', 320, 160, 170, 'travel'); ST.map_ch11 = map('map_ch11', 'world_map', 320, 160, 170, 'travel');
  ST.map_fin = map('map_fin', 'world_map', 320, 160, 170, 'travel');
  for (const id of Object.keys(ST)) if (/_(ch1[01]|fin)$/.test(id)) ST[id].dlgPos = 'top';
  Object.assign(G.NAMES, { darby: '丹尼尔·J·达比', telence: '泰伦斯·T·达比', holhorse: '荷尔·荷斯',
    boingo: '波因哥', petshop: '佩特夏普', kennyg: '肯尼·G', vanilla: '瓦尼拉·艾斯',
    nukesaku: '努凯萨克', dio: 'DIO', wilson: '威尔逊·菲利普斯' });
})();
