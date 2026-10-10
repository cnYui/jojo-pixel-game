// 第2章先让玩家亲自发现偷渡者与船长破绽，战斗机关复用统一伤害和失败重试。
'use strict';
(function(){
  const G=window.G,J=G.J25,T=G.TPL,F=()=>G.flags,crew=['jotaro','joseph','avdol','kakyoin','polnareff'];
  // 水下只有被拖下去的承太郎：其他人这一战藏起来（原来留在原地，和承太郎叠在一起）
  G.BOSS25.darkmoon=()=>J.base('b03_darkbluemoon','jotaro',[0,640],{
    vs:'darkbluemoon',music:'battle',gauge:{label:'氧气',max:100,value:100},bench:'hide',
    kitOverride:{jotaro:{dodge:{dist:40},special:J.special(0,'星之指：U',c=>c.data.barnacles>=3||c.t<c.data.openUntil,async(s,p,c,C)=>{c.data.barnacles=0;C.stand('finger',{dur:.45});C.fx('glint',{x:p.x+p.facing*80,y:p.y-24,size:12});J.fire(p,80,60);await C.wait(.3);})}},
    waves:[[{actor:'darkbluemoon',kit:'e_darkmoon',boss:true,hp:700,poiseMax:60,speed:90,x:430,y:165,pivot:'center',fly:{z:10,bob:2}}]],
    onWave:async(s,i,es,a,c)=>{Object.assign(c.data,{barnacles:0,bubbleX:0,bubbleUntil:0,nextBubble:10,scrape:0,damageCarry:0,baseSpeed:c.player.speed});s.hint('氧气会消耗；走进气泡柱补气。L 按住两秒刮藤壶；漩涡后按 U 星之指。',12);},
    // 气泡柱冒在承太郎左右 30–90 px（水下走速只有 38 px/s：原来随机冒在 640 宽场地的任何地方，4 s 内根本走不到）；
    //   站在里面每秒净补 6（原来 +6 减掉每秒 −4 只剩 +2，补不回来）
    tick(c,dt){const d=c.data,p=c.player,b=c.boss;d.nextBubble-=dt;if(d.nextBubble<=0){d.nextBubble+=10;d.bubbleX=G.clamp(p.x+(Math.random()<.5?-1:1)*G.rand(30,90),40,600);d.bubbleUntil=c.t+4;G.combat.fxAt('bubbles',{x0:d.bubbleX-8,y0:16,x1:d.bubbleX+8,y1:178},p,4);}
      const inBubble=c.t<d.bubbleUntil&&Math.abs(p.x-d.bubbleX)<=8;c.gauge.add((-4+(inBubble?10:0))*dt);
      p.speed=d.baseSpeed*.6*Math.max(.5,1-d.barnacles*.1);if(G.input.isDown('guard')){d.scrape+=dt;if(d.scrape>=2&&d.barnacles){d.scrape-=2;d.barnacles--;sfx('glass_break');}}else d.scrape=0;
      d.damageCarry+=(d.barnacles+(c.gauge.value<=0?5:0))*dt;while(d.damageCarry>=1){d.damageCarry--;J.harm(c,1);}
      if(d.vortex&&b){const v=d.vortex;v.t+=dt;if(v.t<2){b.x=320+Math.cos(v.t*Math.PI)*260;b.y=166+Math.sin(v.t*Math.PI)*7;}else{b.x=320;b.y=166;const dx=320-p.x;p.x+=Math.sign(dx)*Math.min(Math.abs(dx),60*dt);v.hitT=(v.hitT||0)+dt;if(Math.abs(dx)<=16&&v.hitT>=J.f(20)){v.hitT=0;G.combat.hit(b,p,{dmg:6,slot:'enemy',push:0,guard:'none'});}}}
    },testHint:c=>({oxygen:c.gauge.value,barnacles:c.data.barnacles,vortex:!!c.data.vortex,bubbleX:c.data.bubbleX,bubbleActive:c.t<c.data.bubbleUntil,starWindow:c.t<c.data.openUntil})
  });
  function sfx(n){G.audio.sfx(n);}
  // 船的“眼睛”是剧情自己生成的可破坏物，不归战斗管：每次开打（含重来）先收掉上一次的。原来重来一次就多一套眼睛，
  //   旧眼睛还挂着上一次的计数器——打碎了也不算数，眼睛计数永远到不了 3，猩猩一直无敌（2026-10-09 实测连输三次后卡死）
  let shipEyes = [];
  const clearEyes = () => { shipEyes.forEach(a => { a.remove = true; }); shipEyes = []; };
  G.BOSS25.strength=()=>J.base('b04_strength','jotaro',[0,640],{
    vs:'strength',music:'battle',bench:'hide',waves:[[{actor:'strength',kit:'e_strength',boss:true,hp:650,poiseMax:50,speed:80,x:430,y:160}]],
    onWave:async(s,i,es,a,c)=>{const d=c.data;clearEyes();Object.assign(d,{eyes:0,eyesActors:shipEyes,wallClock:0,squeeze:0});
      // 重来时墙也要退回原位、墙面变回铁皮（挤墙改的是地图边界，战斗的重来不会自动还原）
      G.world.stage.x0=c.spec.arena[0];G.world.stage.x1=c.spec.arena[1];G.world.stage.state.flesh=0;
      d.pipeCatch=()=>{if(d.qteBusy)return;J.qte(c,async()=>{const ok=await s.mash({need:10,time:2,decay:0,label:'管道缠住了！连按 J 挣脱'});if(J.valid(c)){c.player.rootT=0;if(!ok)J.harm(c,6);}return ok;}).catch(G.cancelIgnore);};
      for(const [i,x,y] of [[0,120,70],[1,360,40],[2,560,60]]){const e=s.spawn('prop:ship_eye_'+['a','b','c'][i],x,160,{id:'ship_eye_'+i,team:'object',hp:120,z:160-y,shadow:false});e.visualY=y;e.breakable={upward:true,filter:m=>['J3','rush','special'].includes(m.slot),onBreak:()=>{d.eyes++;e.frozen=1;sfx('glass_break');G.ui.hint('船体眼睛 '+d.eyes+'/3');}};d.eyesActors.push(e);}
      s.hint('船壁保护本体。站在三个眼睛正下方，用 J3、连打或 U 向上击碎。',12);
    },
    tick(c,dt){const d=c.data,b=c.boss;if(!b)return;if(b.hp<=b.maxHp*.6){d.wallClock+=dt;if(d.wallClock>=20){d.wallClock-=20;d.squeeze=Math.min(160,d.squeeze+80);G.world.stage.x0=d.squeeze;G.world.stage.x1=640-d.squeeze;sfx('door');}}if(b.hp<=b.maxHp*.3){G.world.stage.state.flesh=Math.min(1,(G.world.stage.state.flesh||0)+dt*.3);}},
    after:async(s,es,a,c)=>{clearEyes();},testHint:c=>({eyes:c.data.eyes,squeeze:c.data.squeeze})
  });
  function setupBoat(){const st=G.STAGES.boat_ch2;st.props=[];
    st.npcs=[T.npc('fake_tennille','captain',272,154,{talk:async S=>{if(!F().anneJoined){await S.say('fake_tennille','SPW的人审核过我，放心吧。小鬼头别在甲板上乱跑。');return;}if(Object.keys(F().captainClues||{}).length<2){await S.say('fake_tennille','别在船上乱查，去休息。');return;}const n=await S.choice(['抽烟的人一说谎，鼻子上的血管就会浮出来','你身上有海水的腥味','你的帽子戴反了'],'用哪一句话试探船长？');if(n===0){await J.lines(S,[['fake_tennille','血管？……'],['jotaro','……你摸了。']]);F().captainCaught=true;}else await S.say('fake_tennille','小鬼，别乱说。');}}),...[[30,'饭少了一份……有老鼠？'],[148,'船长今天好像心情不好。'],[210,'我们一直没看见船长下舱。']].map(([x,t],i)=>T.npc('npc_sailor','sailor'+i,x,162,{talk:S=>S.say('npc_sailor',t)}))];
    const txt=t=>async S=>S.say(S.player.cid,t);
    st.hotspots=[J.hot('lifeboat',60,120,'救生艇',['life','detail'],txt('帆布下面鼓鼓的。'),async S=>{F().anneFound=true;await S.say(S.player.cid,'帆布下面……有个人在发抖。');}),J.hot('radio',120,118,'无线电',[],txt('信号很差。')),J.hot('rod',160,146,'鱼竿',[],txt('钓鱼？我来！')),
      J.hot('cigarette',240,160,'烟头',['detail'],txt('一截刚掐灭的烟。'),async S=>{J.unique('captainClues','cigarette');await S.say('jotaro','滤嘴上有牙印。……这人很紧张。');}),J.hot('deckhatch',192,148,'舱盖',['peek'],txt('舱盖锁着。'),async S=>{J.unique('captainClues','hatch');await S.say('kakyoin','有一个箱子在滴答响。');})];
  }
  function setupFreighter(){const st=G.STAGES.freighter_ch2;st.npcs=[];st.props=[];st.hotspots=[['galley',60,126,'餐厅',['detail'],'饭菜还冒着热气。'],['bridge',270,86,'舰桥',['life'],'……整艘船都在呼吸。'],['crane',190,55,'吊车',[],'吊车……自己转了一下。'],['cage',125,140,'笼子',[],'一只猩猩，居然在翻报纸。'],['log',225,135,'航海日志',[],'最后一页是空的，墨水还没干。']].map(([id,x,y,label,tags,text])=>{const use=async S=>{J.unique('shipInvestigations',id);await S.say(S.player.cid,text);};return J.hot(id,x,y,label,tags,use,use);});}
  G.STORY.ch2=async S=>{S.party(crew,{leader:'jotaro'});for(const k of ['anneFound','anneJoined','captainCaught','captainClues','shipInvestigations'])delete F()[k];F().anneLeft=false;
    await S.chapterCard('ch2');await S.setStage('map_ch2',{x:100,y:160,music:'travel'});await S.run(async s=>s.route(['香港','新加坡'],{vehicle:'ship',day:2,left:49,cut:.6}));
    setupBoat();await S.setStage('boat_ch2',{x:100,y:160});S.location('south_sea');S.hint('Q 换队长；阿布德尔或承太郎调查救生艇帆布。',10);await S.until(()=>F().anneFound&&!S.busy);
    await S.run(async s=>{await J.lines(s,[['anne','放开！谁要你们管！'],['joseph','她跳下去了！有鲨鱼！']]);await s.setStage('sea_ch2',{x:130,y:160,fade:false});T.prop(s,'shark',220,165);const r=await s.press({key:'attack',window:.67,failOk:true,label:'鲨鱼冲来了！J'});if(r==='miss')s.player.hp=Math.max(1,s.player.hp-8);s.sfx('punch');s.fx('water_splash',{x:180,y:160,size:24});await s.say('anne','……谁要你救！我要去新加坡找爸爸！');F().anneJoined=true;});
    setupBoat();await S.setStage('boat_ch2',{x:100,y:160});J.anne(S);S.hint('调查烟头与舱盖，再找船长搭话。',10);await S.until(()=>F().captainCaught&&!S.busy);
    await S.run(async s=>{await s.say('fake_tennille','居然敢揭穿我！先拿这个小鬼开刀！');while(!await s.mash({need:8,time:1.6,decay:0,label:'夺回安妮！连按 J'}))await s.say('jotaro','……放开她。');await s.say('kakyoin','我接住她了！');s.standCard('darkbluemoon');await s.setStage('underwater_ch2',{x:150,y:165,fade:false,music:'battle'});await s.fight(G.BOSS25.darkmoon());
      await s.setStage('boat_ch2',{x:220,y:160,fade:false});s.nameCard('fake_tennille');await s.say('jotaro','你这船长，到此为止。');await s.title('saiki');for(let i=0;i<5;i++){s.sfx('blip',{rate:1+i*.2});await s.wait(.2-i*.025);}await s.say('kakyoin','舱底有炸弹！上救生艇！');s.fx('explosion',{x:160,y:80,size:64});s.sfx('explosion');await s.setStage('dinghy_ch2',{x:120,y:160,fade:false,music:'travel'});await J.lines(s,[['joseph','这次可不算我的！'],['polnareff','你这个小鬼，差点害我们全掉海里。'],['anne','笨蛋！你才像猩猩。'],[null,'夜里，雾中出现一艘无人货轮。舷梯已经放下。']]);});
    setupFreighter();await S.setStage('freighter_ch2',{x:70,y:160,music:'tension'});J.anne(S);S.hint('这艘船空无一人。调查三个不同的地方。',10);await S.until(()=>Object.keys(F().shipInvestigations||{}).length>=3&&!S.busy);
    await S.run(async s=>{await J.lines(s,[['avdol','这不是一艘普通的船……整艘船都是替身！'],['jotaro','……船里的眼睛。先打碎它们。']]);s.standCard('strength');await s.setStage('hold_ch2',{x:100,y:160,fade:false});await s.fight(G.BOSS25.strength());s.fx('burst',{x:430,y:130,n:24,speed:90});await s.title('saiki');await s.setStage('dinghy_ch2',{x:120,y:160,fade:false,music:'travel'});await J.lines(s,[[null,'庞大的货轮变成一艘生锈的小破船。'],['npc_sailor','我们被关在货舱里！幸好都没事。'],['joseph','SPW的船来了。……这回总该能到新加坡了。']]);await J.end(s,'ch2_tbc');});
  };
  // 开发调参入口（只给 tools\dev\full\dev_fight.py 用，正常游戏不调用）：直接开打这一章的某一战，战斗配置和正式剧情是同一份。
  //   验收一律跑整章（test_mid_early.py），这个入口的结果不当通关证据
  G.DEV=G.DEV||{};
  G.DEV.ch2Darkmoon=async S=>{S.party(crew,{leader:'jotaro'});await S.setStage('underwater_ch2',{x:150,y:165,music:'battle'});await S.run(async s=>{await s.fight(G.BOSS25.darkmoon());});};
  G.DEV.ch2Strength=async S=>{S.party(crew,{leader:'jotaro'});await S.setStage('hold_ch2',{x:100,y:160,music:'tension'});await S.run(async s=>{await s.fight(G.BOSS25.strength());});};
})();
