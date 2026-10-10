// 对话框上的名字 G.NAMES + 各章共用的地图几何（背景 key、可走范围、墙、障碍）。NPC / 调查点 / 触发区在各章文件里往上加。
//   地图 id 一律带章节后缀（_pro / _chN[a-z] / _fin，技术约定 §2.8）；G.STAGES 由 world.js 建好，这里只往里加。
//   背景 key、宽度、脚底线 / 可走范围照规划 §5.1 / §5.2 的地图表；背景元数据（G.D.bg[key].walk）有的话 Stage 自己会读，这里写的是兜底。
'use strict';
(function () {
  const G = window.G;

  // 对话框名字（图集里的名字太正式，或者同一个人在剧情里另有称呼）
  G.NAMES = {
    jotaro: '承太郎', joseph: '乔瑟夫', avdol: '阿布德尔', kakyoin: '花京院', polnareff: '波鲁纳雷夫', iggy: '伊奇',
    holly: '荷莉', dio: 'DIO', jgeil: 'J·凯尔', grayfly: '格雷·弗莱', towergray: '灰塔',
    npc_police: '狱警', npc_nurse: '校医', npc_student_f_a: '女生', npc_student_f_b: '女生', npc_student_m: '男生',
    npc_stewardess: '空姐', npc_passenger_a: '乘客', npc_passenger_b: '乘客', npc_passenger_c: '乘客', npc_passenger_d: '乘客',
    npc_hk_owner: '大排档老板', npc_hk_granny: '卖粥阿婆', npc_hk_passer_a: '路人', npc_hk_passer_b: '妇人', npc_fortune: '算命先生',
  };

  const ST = G.STAGES;
  // 左右两堵“墙”（单屏地图：只让人在可走的那一段里走）
  const walls = (xa, xb, w = 320) => [{ x0: -40, x1: xa, y0: 0, y1: 240 }, { x0: xb, x1: w + 40, y0: 0, y1: 240 }];

  // ---------------------------------------------------------------- 序章
  // 拘留所：牢内可走 x 96–236、y 122–138；走廊 ground 166（狱警、荷莉、乔瑟夫、阿布德尔站这里）。铁栏前景按 state.bend 选图（0..1）
  //   fgDepth 144 = 铁栏底横杠的脚底线：牢里的人画在铁栏后面，走廊上的人画在铁栏前面（承太郎掰开铁栏走出来以后也是）
  ST.jail_pro = {
    id: 'jail_pro', bg: 'jail_cell', x0: 0, x1: 320, yMin: 122, yMax: 138, camX: 0, music: 'daily', fgDepth: 144,
    props: [], npcs: [], hotspots: [], triggers: [], obstacles: walls(96, 236), state: { bend: 0 },
  };
  // 空条家（白天 / 夜 / 早上是同一张地图换背景：S.setStage('kujo_pro', { bg: 'kujo_house_night' })）。左前矮桌 x 14–82 挡路
  ST.kujo_pro = {
    id: 'kujo_pro', bg: 'kujo_house_day', x0: 0, x1: 320, yMin: 148, yMax: 176, camX: 0, music: 'daily',
    props: [], npcs: [], hotspots: [], triggers: [], obstacles: walls(90, 300),
  };
  // 上学路的长石阶（2026-10-10 新画 school_stairs，640 宽不循环；用户：“在动漫里确实是在一个下楼梯的场景触发的”）：
  //   纵深带固定 y 150–160，人站在台阶上的高度用 z（剧情每帧按 x 算：坡顶 80，20 级每级低 4 px，人行道 0；背景 anchors.stairs 同一组数）
  ST.stairs_pro = {
    id: 'stairs_pro', bg: 'school_stairs', x0: 0, x1: 640, yMin: 150, yMax: 160, camX: 0, music: 'daily',
    props: [], npcs: [], hotspots: [], triggers: [], obstacles: walls(12, 628, 640),
  };
  // 校门：480 宽不循环，可走 x 16–464、y 140–176；樱花在背景的 petals 层
  ST.school_pro = {
    id: 'school_pro', bg: 'school_gate', x0: 0, x1: 480, yMin: 140, yMax: 176, camX: 0, music: 'daily',
    props: [], npcs: [], hotspots: [], triggers: [], obstacles: walls(16, 464, 480),
  };
  // 保健室（新画）：可走 x 40–290、y 148–176；锚点 bed1 (100,152)、bed2 (180,152)、desk (236,156)、door (300,156)
  ST.infirmary_pro = {
    id: 'infirmary_pro', bg: 'school_infirmary', x0: 0, x1: 320, yMin: 148, yMax: 176, camX: 0, music: 'tension',
    props: [], npcs: [], hotspots: [], triggers: [], obstacles: walls(40, 290),
  };
  // 承太郎家卧室（黄昏）：可走 x 40–290、y 150–176；中间被褥 (150,166) 挡住，绕着走
  ST.bedroom_pro = {
    id: 'bedroom_pro', bg: 'kujo_bedroom_dusk', x0: 0, x1: 320, yMin: 150, yMax: 176, camX: 0, music: 'sad',
    props: [], npcs: [], hotspots: [], triggers: [],
    obstacles: walls(40, 290).concat([{ x0: 122, x1: 178, y0: 160, y1: 174 }]),
  };
  // 黄昏门口（s05 自绘，460 宽，只演过场）
  ST.gate_pro = {
    id: 'gate_pro', bg: 'dusk_gate', x0: 0, x1: 460, yMin: 146, yMax: 160, camX: 0, music: 'travel',
    props: [], npcs: [], hotspots: [], triggers: [], obstacles: [],
  };

  // ---------------------------------------------------------------- 第1章
  // 世界地图（S.route 用插入画面画路线；这张图只是让世界场景有个地方站）
  ST.map_ch1 = {
    id: 'map_ch1', bg: 'world_map', x0: 0, x1: 320, yMin: 160, yMax: 170, camX: 0, music: 'travel',
    props: [], npcs: [], hotspots: [], triggers: [], obstacles: [],
  };
  // 客机侧剖客舱（新画，640 宽、两头是墙、不循环）：过道 y 156–166、x 16–624；乘客座位槽 x 64…544、格雷·弗莱 584
  //   新背景还没导出时退回原片的透视客舱（固定竞技场，过道 x 112–208；技术约定 §8.2 第 9 条）
  ST.plane_ch1 = {
    id: 'plane_ch1', bg: 'plane_cabin_side', x0: 0, x1: 640, yMin: 156, yMax: 166, camX: 0, music: 'travel',
    ambient: { name: 'plane_engine_loop', vol: 0.25 },
    props: [], npcs: [], hotspots: [], triggers: [], obstacles: walls(16, 624, 640),
  };
  // 驾驶舱（2026-10-10 按人的比例重画）：地板 y 172，可走 x 44–240（门口 → 机长座前面），再往右是操纵台和仪表板
  ST.cockpit_ch1 = {
    id: 'cockpit_ch1', bg: 'cockpit', x0: 0, x1: 320, yMin: 164, yMax: 176, camX: 0, music: null,
    props: [], npcs: [], hotspots: [], triggers: [], obstacles: walls(44, 240), state: { alarm: true, yoke: 0 },
  };
  // 机外俯冲（天空）→ 海面
  ST.sky_ch1 = {
    id: 'sky_ch1', bg: 'sky_day', x0: 0, x1: 320, yMin: 150, yMax: 170, camX: 0, music: null,
    props: [], npcs: [], hotspots: [], triggers: [], obstacles: [],
  };
  ST.sea_ch1 = {
    id: 'sea_ch1', bg: 'sea_day', x0: 0, x1: 320, yMin: 150, yMax: 176, camX: 0, music: null,
    props: [], npcs: [], hotspots: [], triggers: [], obstacles: [],
  };
  // 香港夜街：地图宽 960（近景层 640 循环），ground 154，可走 y 150–176
  ST.hk_street_ch1 = {
    id: 'hk_street_ch1', bg: 'hongkong_night', x0: 0, x1: 960, yMin: 150, yMax: 176, camX: 0, music: 'daily',
    ambient: { name: 'crowd_loop', vol: 0.3 },
    props: [], npcs: [], hotspots: [], triggers: [], obstacles: walls(8, 952, 960),
  };
  ST.hk_street_ch1b = Object.assign({}, ST.hk_street_ch1, { id: 'hk_street_ch1b', music: 'travel', npcs: [], hotspots: [], triggers: [], props: [] });
  // 虎豹别墅（夜）：ground 150，可走 y 140–176；虎像在 (44,132)（第 2 战会被雕成红色魔术师）
  ST.hk_garden_ch1 = {
    id: 'hk_garden_ch1', bg: 'hk_garden_night', x0: 0, x1: 320, yMin: 140, yMax: 176, camX: 0, music: 'tension',
    props: [], npcs: [], hotspots: [], triggers: [], obstacles: walls(12, 308),
  };
})();
