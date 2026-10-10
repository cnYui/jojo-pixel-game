// 新加坡把可疑行为变成玩家收集的证据；玩偶和黏液保留各自的原著破解方法。
'use strict';
(function(){
  const G=window.G,J=G.J25,T=G.TPL,F=()=>G.flags,crew=['jotaro','joseph','avdol','kakyoin','polnareff'];
  G.BOSS25.devo=()=>J.base('b05_devo','polnareff',[30,290],{
    vs:'devo',music:'battle',gauge:{label:'恨意',max:100,value:0},bench:'hide',
    waves:[[{actor:'devo',kit:'e_devo',boss:true,hp:300,minHp:1,x:248,y:164}],[{actor:'devo_doll',kit:'e_doll',boss:true,hp:400,x:105,y:162}]],
    onWave:async(S,i,es,a,c)=>{const d=c.data,b=es[0];if(i===0){d.devo=b;d.strength=1;c.on('hit',e=>{if(e.t===d.devo){c.gauge.add(20);d.strength=Math.min(1.5,1+(300-e.t.hp)/600);}});S.hint('他在故意挨打……恨得越深，玩偶就越强。',12);}else{
        await S.say('devo','嘿嘿嘿……恨够了……');b.dmgOut=d.strength;d.shards=[[100,170],[175,120],[295,80]];c.gauge.label='玩偶强度';c.gauge.max=1.5;c.gauge.value=d.strength;
        d.draw=(P,ctx)=>{const px=G.px,enemy=ctx.boss;for(const [x,y] of d.shards){px.poly(P,[[x-8,y],[x+5,y-12],[x+8,y-2]],'#5578a6',.9);px.line(P,x-5,y-2,x+3,y-9,'#d0f8ff');if(enemy&&enemy.mem.hidden){const rx=x+G.clamp((enemy.x-x)*.04,-4,4);px.blitFrame(P,'devo_doll','idle',0,rx,y-1,{scale:.18,alpha:.95});}}};
        S.hint('看镜子碎片里的倒影，靠近藏身处；J 连按三次的贯穿突刺或 U 能逼出玩偶。',12);}
    },tick(c,dt){if(c.wave===0){c.gauge.add(2*dt);if(c.gauge.value>=100&&c.boss){c.boss.remove=true;G.audio.sfx('sting_reveal');}}},
    after:async(S,es,a,c)=>{const b=es[0];S.fx('burst',{x:b?b.x:160,y:145,n:40,colours:['#ffffff','#e0dcff'],speed:100});S.sfx('slash');await S.title('saiki');await S.say(null,'迪波再也没醒来。');},
    testHint:c=>({phase:c.wave,hate:c.gauge.value,strength:c.data.strength,hidden:!!(c.boss&&c.boss.mem.hidden),shards:c.data.shards})
  });
  const windowOpen=c=>{const b=c.boss;return b&&!c.data.water&&Math.min(Math.abs(b.x-60),Math.abs(b.x-260))<=24;};
  async function intoWater(c){if(c.data.water||c.data.shifting)return;c.data.water=true;c.data.slime=0;c.data.waterUntil=c.t+20;c.spec.arena=[30,290];G.world.hazards=[];G.audio.sfx('glass_break');G.combat.fxAt('water_splash',{x:c.boss.x,y:150,size:24},c.player,.6);await J.transfer(c,'sea_ch3',120,205);}
  G.BOSS25.yellow=()=>J.base('b06_yellowtemperance','jotaro',[40,280],{
    vs:'yellowtemperance',bench:'hide',music:'battle',gauge:{label:'黏液',max:5,value:0},
    waves:[[{actor:'rubbersoul',kit:'e_yellow',boss:true,hp:600,x:220,y:160,poiseMax:0}]],
    kitOverride:{jotaro:{special:J.special(0,'抱住他跳窗：U',c=>windowOpen(c)&&Math.abs(c.player.x-c.boss.x)<=32,async(S,p,c)=>{await intoWater(c);})}},
    onWave:async(S,i,es,a,c)=>{if(G.world.stage.id!=='cable_ch3')await J.transfer(c,'cable_ch3',120,220);c.spec.arena=[40,280];G.world.stage.x0=40;G.world.stage.x1=280;
      const d=c.data;Object.assign(d,{slime:0,water:false,carry:0,contactAt:0,puddles:[],baseSpeed:c.player.speed});es[0].idleAnim='slime';es[0].play('slime');
      d.engulf=()=>{if(d.qteBusy)return;d.slime=Math.min(5,d.slime+3);J.qte(c,async()=>{const ok=await S.mash({need:12,time:2.4,decay:0,label:'黏液包住身体！连按 J 挣脱'});if(!ok&&J.valid(c))J.harm(c,10);return ok;}).catch(G.cancelIgnore);};
      c.on('hit',e=>{if(e.att===c.boss&&e.t===c.player&&!e.guard&&!d.water)d.slime=Math.min(5,d.slime+1);if(e.t===c.boss&&!d.water){if(e.slot==='J3'&&windowOpen(c))intoWater(c).catch(G.cancelIgnore);else if(c.t>=d.contactAt){d.contactAt=c.t+.4;d.slime=Math.min(5,d.slime+1);}}});
      const anne=S.spawn('anne',270,166,{id:'anne_battle',team:'npc'});S.pose(anne,'idle');S.hint('黏液会吸收伤害！K 甩掉一层；逼他到窗边，用 J3 或 U 跳入海里。',12);
    },tick(c,dt){const d=c.data,p=c.player,b=c.boss;if(!b)return;if(d.water){c.gauge.label='海里剩余';c.gauge.max=20;c.gauge.value=Math.max(0,d.waterUntil-c.t);p.speed=d.baseSpeed;b.idleAnim='idle';if(c.t>=d.waterUntil&&!d.shifting){d.water=false;d.slime=0;c.spec.arena=[40,280];b.idleAnim='slime';J.transfer(c,'cable_ch3',120,220).catch(G.cancelIgnore);G.ui.hint('他爬回车厢了，再逼他跳窗！');}return;}
      if(G.input.hit('dodge'))d.slime=Math.max(0,d.slime-1);c.gauge.label='黏液';c.gauge.max=5;c.gauge.value=d.slime;
      if(Math.abs(p.x-b.x)<15&&Math.abs(p.y-b.y)<9&&c.t>=d.contactAt){d.contactAt=c.t+.65;d.slime=Math.min(5,d.slime+1);}d.carry+=d.slime*dt;while(d.carry>=1){d.carry--;J.harm(c,1);}
      const slow=G.world.hazards.some(h=>!h.dead&&h.phase==='active'&&h.tag==='slime'&&p.x>=h.x0&&p.x<=h.x1&&p.y>=h.y0&&p.y<=h.y1);p.speed=d.baseSpeed*(slow?.6:1);
    },testHint:c=>({water:c.data.water,slime:c.data.slime,waterLeft:c.data.waterUntil-c.t,window:windowOpen(c),bossX:c.boss&&c.boss.x})
  });
  function arrival(){const st=G.STAGES.sg_street_ch3;st.npcs=[T.npc('npc_police','police_sg',140,164,{talk:S=>S.say('npc_police','偷渡者？……没看见没看见。')}),T.npc('npc_townsfolk','vendor_sg',400,164,{talk:S=>S.say('npc_townsfolk','欢迎来到新加坡。前面就是酒店。')})];st.hotspots=[J.hot('merlion',280,80,'鱼尾狮海报',[],S=>S.say('polnareff','Magnifique！给我拍照！')),J.hot('hotel_door',740,120,'酒店入口',[],async S=>{F().sgHotel=true;await S.say('polnareff','我要单人间！');})];}
  function hotel(){const st=G.STAGES.sg_hotel_ch3;st.npcs=[];st.hotspots=[['fridge',260,122,'冰箱',[],'冰箱……嗯？好像比刚才重？'],['bed',95,151,'床底',['cut'],'剑尖挑起床单……什么都没有。'],['mirror',176,90,'梳妆镜',[],'我真帅。'],['window',294,82,'窗户',[],'新加坡的夜景，Magnifique！']].map(([id,x,y,label,tags,line])=>{const run=async S=>{J.unique('hotelClues',id);await S.say('polnareff',line);};return J.hot(id,x,y,label,tags,run,run);});}
  function suspicious(){const st=G.STAGES.sg_street_ch3,clue=(key,text,cid)=>async S=>{J.unique('yellowClues',key);await S.say(cid||S.player.cid,text);};
    st.npcs=[T.npc('anne','anne_sg',250,162,{talk:clue('cat','那个红头发的哥哥，刚才踢了一只猫！','anne')})];
    const flame=clue('life','他的生命之火……是两层的。','avdol'),shadow=clue('shadow','他的影子边缘在蠕动。','jotaro');
    st.hotspots=[J.hot('cherry',110,150,'樱桃摊',[],clue('cherry','“花京院”把樱桃整个嚼碎咽下了。……平时他不是这样吃的。','joseph')),
      J.hot('false_kakyoin',360,150,'观察花京院',['life','detail'],S=>S.say('kakyoin','……早。那个小鬼，烦死了。'),S=>S.player.cid==='avdol'?flame(S):shadow(S)),
      J.hot('cable_station',770,118,'缆车站',[],async S=>{if(Object.keys(F().yellowClues||{}).length<2){await S.say('jotaro','……先弄清楚他有什么不对劲。');return;}await S.choice(['指认他'],'至少两处破绽都指向同一个人');F().yellowCaught=true;})];}
  G.STORY.ch3=async S=>{for(const k of ['sgHotel','hotelClues','yellowClues','yellowCaught'])delete F()[k];S.party(crew,{leader:'jotaro'});await S.chapterCard('ch3');await S.setStage('map_ch3',{x:100,y:160,music:'travel'});await S.run(s=>s.route(['香港','新加坡'],{vehicle:'ship',day:6,left:45,cut:.6}));arrival();await S.setStage('sg_street_ch3',{x:70,y:164});S.location('singapore');J.anne(S);S.hint('沿街走到酒店门口，E 进入。',10);await S.until(()=>F().sgHotel&&!S.busy);
    hotel();S.party(['polnareff'],{leader:'polnareff'});await S.setStage('sg_hotel_ch3',{x:145,y:164,music:'tension'});S.hint('波鲁纳雷夫独自检查房间；调查两个不同的地方。',10);await S.until(()=>Object.keys(F().hotelClues||{}).length>=2&&!S.busy);
    await S.run(async s=>{s.sfx('door');await s.say('devo','想不到我会在冰箱里吧……越恨你，我的恶魔越强！');s.nameCard('devo');s.standCard('ebonydevil');await s.fight(G.BOSS25.devo());S.party(crew,{leader:'jotaro'});await J.lines(s,[['avdol','刚才到底发生了什么？'],['polnareff','我一个人就够了！'],[null,'第二天清晨，“花京院”主动带大家去缆车站。']]);});
    G.party.setLeadable('kakyoin',false,{look:'gray',msg:'……我今天不想走在前面。'});suspicious();await S.setStage('sg_street_ch3',{x:80,y:164});J.anne(S);S.hint('樱桃、安妮的话、阿布德尔的生命之火、承太郎的观察：收集至少两处破绽。',12);await S.until(()=>F().yellowCaught&&!S.busy);
    await S.run(async s=>{await s.setStage('cable_ch3',{x:125,y:160,music:'tension'});await s.say('jotaro','……你不是花京院。');s.fx('tendrils',{pts:[[[202,144],[240,92]],[[212,145],[264,118]],[[225,145],[258,160]]],colour:'#ffee40',wiggle:2});s.sfx('drain');await s.say('rubbersoul','黄色节制可以变成任何人！你的拳头只会被我吃掉！');s.nameCard('rubbersoul');s.standCard('yellowtemperance');await s.fight(G.BOSS25.yellow());s.pose(s.actor('rubbersoul'),'beg');await s.choice(['饶他','不饶'],'拉巴索在水里求饶');s.sfx('punch');s.fx('hit_spark',{x:205,y:135});await J.lines(s,[['jotaro','先把你知道的说出来。'],['rubbersoul','下、下一批是荷尔·荷斯和 J·凯尔！J·凯尔……两只手都是右手！']]);await T.closeup4(s,{cid:'polnareff',expr:'shock',dur:1.2});await s.say('polnareff','……两只右手？');G.party.setLeadable('kakyoin',true);await s.setStage('train_ch3',{x:180,y:164,music:'travel'});await s.say('kakyoin','被打晕关在储物间……幸亏你们认出了他。');s.pose('kakyoin','cherry');s.sfx('rero');await J.lines(s,[['kakyoin','rerorero……'],['polnareff','……你能不能别这样吃樱桃。'],['kakyoin','这是我的自由。']]);s.unpose('kakyoin');await J.end(s,'ch3_tbc');});
  };
  // 开发调参入口（只给 tools\dev\full\dev_fight.py 用，正常游戏不调用）：直接开打这一章的某一战，战斗配置和正式剧情是同一份。
  //   验收一律跑整章（test_mid_early.py），这个入口的结果不当通关证据
  G.DEV=G.DEV||{};
  G.DEV.ch3Devo=async S=>{hotel();S.party(['polnareff'],{leader:'polnareff'});await S.setStage('sg_hotel_ch3',{x:145,y:164,music:'tension'});await S.run(async s=>{await s.fight(G.BOSS25.devo());});};
  G.DEV.ch3Yellow=async S=>{S.party(crew,{leader:'jotaro'});await S.setStage('cable_ch3',{x:125,y:160,music:'tension'});await S.run(async s=>{await s.fight(G.BOSS25.yellow());});};
})();
