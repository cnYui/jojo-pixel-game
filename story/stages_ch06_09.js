// 中段地图按规划保留自由探索和战斗宽度，循环沙漠由距离计数独立表示。
'use strict';
(function () {
  const ST = window.G.STAGES;
  const add = (id, bg, width, yMin = 148, yMax = 176, music = 'daily') => {
    ST[id] = { id, bg, x0: 0, x1: width, yMin, yMax, music, props: [], npcs: [], hotspots: [], triggers: [], obstacles: [] };
  };
  add('desert_ch6', 'desert_noon', 640); add('village_ch6', 'yaprin_village', 640);
  add('cessna_ch6', 'cessna_cabin', 320, 154, 172, 'tension'); add('dream_ch6', 'dream_carnival', 320, 140, 176, 'battle');
  add('camp_ch6', 'desert_night', 640, 148, 176, 'ominous');
  add('island_ch7', 'redsea_island', 480); add('sub_ch7', 'submarine', 640, 150, 176, 'tension');
  add('seabed_ch7', 'seabed_mouth', 320, 150, 174, 'battle'); add('coast_ch7', 'egypt_coast', 320);
  add('coast_ch8', 'egypt_coast', 320); add('desert_ch8', 'desert_day', 640, 148, 178, 'battle');
  add('glide_ch8', 'desert_day', 640, 48, 150, 'battle'); add('aswan_ch8', 'aswan_town', 960);
  add('temple_ch9', 'egypt_temple', 640); add('nile_ch9', 'nile_bank', 640);
  add('luxor_ch9', 'luxor_town', 960); add('rail_ch9', 'egypt_rail', 640, 148, 178, 'battle');
  add('house_ch9', 'luxor_house', 640, 146, 176, 'tension');
})();
