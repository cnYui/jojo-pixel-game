// 地图几何独立于章节流程，章节重试可以重建机关而保留同一个 Boss 对象。
'use strict';
(function(){
  const G=window.G,ST=G.STAGES;
  function stage(id,bg,w=320,y0=140,y1=176){ST[id]={id,bg,x0:0,x1:w,yMin:y0,yMax:y1,camX:0,music:'daily',props:[],npcs:[],hotspots:[],triggers:[],obstacles:[{x0:-40,x1:8,y0:0,y1:240},{x0:w-8,x1:w+40,y0:0,y1:240}],state:{}};}
  for(const n of [2,3,4,5])stage('map_ch'+n,'world_map',320,160,170);
  // 第2章 2026-10-10 晚按体验版重做：包船甲板、货轮甲板改成 640 宽（tools\bg_new\yacht_deck.py / freighter_deck.py），
  //   漂流那一夜换成雾海 sea_fog（tools\bg_new\sea_fog.py；pick ship / tint night），可走带照背景的 walk
  stage('boat_ch2','yacht_deck',640,146,172);stage('sea_ch2','sea_day');stage('underwater_ch2','underwater',640,158,178);
  stage('dinghy_ch2','sea_fog',320,150,170);stage('freighter_ch2','freighter_deck',640,146,172);stage('hold_ch2','freighter_corridor',640,148,176);
  // 对白默认放上面（engine\ui.js makeDlg 读 dlgPos）：这几张图人都站在画面下半，底部对话框会把人挡掉一半
  for(const id of ['boat_ch2','sea_ch2','dinghy_ch2','freighter_ch2','hold_ch2'])ST[id].dlgPos='top';
  stage('sg_street_ch3','singapore_street',960,150,176);stage('sg_hotel_ch3','singapore_hotel',320,148,176);
  stage('cable_ch3','cable_car',320,150,170);ST.cable_ch3.obstacles=[{x0:-40,x1:40,y0:0,y1:240},{x0:280,x1:360,y0:0,y1:240}];
  stage('sea_ch3','underwater',320,150,176);stage('train_ch3','train_interior',320,156,174);
  stage('calcutta_ch4','calcutta_street',1280,148,176);stage('alley_ch4','india_alley',320,146,176);
  stage('varanasi_ch4','ganges_ghat',640,148,176);stage('varanasi_st_ch4','calcutta_street',640,148,176);
  stage('road_ch5','desert_highway',320,152,168);stage('cliff_ch5','desert_highway',320,148,176);
  stage('fog_ch5','fog_town',320,146,176);stage('inn_ch5','enya_inn',320,148,176);
  stage('karachi_ch5','karachi_street',640,148,176);stage('brain_ch5','brain_inside',320,130,176);
  Object.assign(G.NAMES,{anne:'安妮',fake_tennille:'冒牌坦尼尔船长',darkbluemoon:'暗蓝之月',strength:'猩猩',devo:'被诅咒的迪波',devo_doll:'黑檀木恶魔',rubbersoul:'拉巴索',holhorse:'荷尔·荷斯',hangedman:'倒吊人',empress:'女帝',nena:'奈娜',wheel:'命运之轮',zz:'ZZ',enya:'恩雅婆婆',justice:'正义',steelydan:'斯蒂利·丹',lovers:'恋人',npc_sailor:'船员',npc_kid:'小孩',npc_townsfolk:'居民'});
})();
