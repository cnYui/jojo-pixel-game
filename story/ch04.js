// 倒吊人的光路和女帝的柏油机关由玩家解开，普通人保持零伤害。
'use strict';
(function(){
  const G=window.G,J=G.J25,T=G.TPL,F=()=>G.flags,crew=['jotaro','joseph','avdol','kakyoin','polnareff'];
  const canReflect=(r,c)=>!r.dead&&(!r.expires||r.expires>c.t)&&!(r.closedUntil>c.t)&&Math.abs(r.x-c.player.x)<r.reach;
  // 镜子 / 橱窗的玻璃框：和 india_alley 背景里画好的镜子（_IA_MIRROR 26,44,70,112）、橱窗（_IA_WINDOW 206,62,290,116）对齐
  const GLASS={mirror:[28,46,68,110],window:[208,64,288,114]};
  const bez=(pts,u)=>{const v=1-u;return [v*v*pts[0][0]+2*v*u*pts[1][0]+u*u*pts[2][0],v*v*pts[0][1]+2*v*u*pts[1][1]+u*u*pts[2][1]];};
  // 倒吊人的画面：反光扫过还在的玻璃、碎掉的玻璃留裂纹、藏身的那面里看得见它举刀；硬币、光路、荷尔·荷斯的红色弯曲虚线（W4 36f）
  function drawHanged(P,d,ctx){
    const px=G.px,cx=G.cam.x||0,t=ctx.t;
    if(d.phase){if(d.blindUntil>t){const x=ctx.player.x-cx;for(const r of [[0,0,320,95],[0,95,Math.max(0,x-48),85],[x+48,95,320,85]])px.rect(P,...r,'#050310',.9);}return;}
    for(const r of d.reflections){
      const b=GLASS[r.kind];if(!b)continue;const x0=b[0]-cx,y0=b[1],x1=b[2]-cx,y1=b[3],w=x1-x0,h=y1-y0;
      if(r.dead){const ix=x0+w*.45,iy=y0+h*.42,len=Math.max(w,h)*.5;
        for(let k=0;k<9;k++){const a=k*.7+.3;px.line(P,ix,iy,ix+Math.cos(a)*len,iy+Math.sin(a)*len,'#1c2230',.95);}
        px.poly(P,[[ix-6,iy-2],[ix+4,iy-8],[ix+8,iy+5],[ix-2,iy+9]],'#121620',.9);continue;}
      const k=((t*.7+(r.kind==='window'?.8:0))%1.6)/1.6;
      if(k<1){const sx=x0+(w-h*.35)*k;px.line(P,sx,y1-2,sx+h*.35,y0+2,'#e8fbff',.55);px.line(P,sx+3,y1-2,sx+3+h*.35,y0+2,'#ffffff',.3);}
      if(r===d.source){px.rect(P,x0+1,y0+1,w-2,h-2,'#401018',.25);px.blitFrame(P,'hangedman',d.knifeWarn>t?'attack':'idle',0,Math.round((x0+x1)/2),y1-4,{alpha:.85});}
    }
    for(const r of d.reflections)if(r.kind==='puddle'){const x=r.x-cx;px.ellipse(P,x-12,r.y-2,x+12,r.y+2,r===d.source?'#ff8a80':'#88bcda',null,1,.65);}
    if(d.coinUntil>t){const x=d.coinX-cx,yy=Math.round(58+Math.abs(Math.sin((t-d.coinAt)*6))*8);px.ellipse(P,x-3,yy-4,x+3,yy+4,'#ffe273');px.plot(P,x-1,yy-2,'#ffffff');}
    if(d.lightUntil>t)px.ring(P,d.coinX-cx,64,6+Math.round(Math.sin(t*30)*2),1,'#fff6c0');
    if(d.gun){const pts=d.gun.curve,a=Math.floor(t*16)%2?.9:.55;let last=bez(pts,0);for(let i=1;i<=20;i++){const nx=bez(pts,i/20);if(i%2)px.line(P,last[0]-cx,last[1]-22,nx[0]-cx,nx[1]-22,'#ff3040',a);last=nx;}}
  }
  // 换地图后队伍会被 setStage 带过去：按这一战的 bench:'hide' 再藏一次（只留操作角色和 AI 同伴）
  const rehide=c=>{const al=c.spec.allies||[];for(const a of G.party.members)if(a!==c.player&&!al.includes(a.cid)){a.visible=false;if(a.stand)a.stand.hide();}};
  async function exposeJgeil(c){if(c.data.phase||c.data.shifting)return;c.data.phase=1;const ghost=c.boss;ghost.remove=true;G.world.shots=[];G.world.hazards=[];for(const a of c.data.reflectActors||[])a.remove=true;c.spec.arena=[400,720];await J.transfer(c,'calcutta_ch4',460,600);if(!J.valid(c))return;rehide(c);
    const e=c.spawn({actor:'jgeil',kit:'e_jgeil',boss:true,hp:600,poiseMax:40,x:635,y:163});
    c.data.civilians=[G.S.spawn('npc_townsfolk',548,164,{id:'jgeil_civilian0',team:'npc'}),G.S.spawn('npc_townsfolk',655,164,{id:'jgeil_civilian1',team:'npc'})];
    e.onHitBy=(target,att)=>{const n=c.data.civilians.find(a=>Math.abs(a.x-target.x)<=18&&att&&(a.x-att.x)*(target.x-a.x)>=0);if(!n)return null;att.stunT=.5;G.uifx.sfx('住手！他是无辜的！',att);return 'evade';};
    // 名牌（左下）先放完再给提示：提示框在底部，同时出会压住名牌的副标题
    G.S.nameCard('jgeil');G.defer(2.7,()=>{if(J.valid(c))G.ui.hint('J·凯尔躲在路人身后：绕到另一边再打！',8);},'world');
  }
  G.BOSS25.hanged=()=>J.base('b07_hangedman','polnareff',[24,296],{
    vs:'emperor_hangedman',music:'battle',allies:['kakyoin'],bench:'hide',gauge:{label:'光路截击',max:3,value:0},
    kitOverride:{polnareff:{chords:{'dodge+attack':'PO_SAND_KICK'}}},
    waves:[[{actor:'hangedman',kit:{hp:3,speed:0,moves:[],brain:()=>true,dmgMul:()=>0},boss:true,hp:3,untargetable:true,x:48,y:160,alpha:0}]],
    onWave:async(S,i,es,a,c)=>{if(G.world.stage.id!=='alley_ch4'){c.spec.arena=[24,296];await J.transfer(c,'alley_ch4',150,48);rehide(c);}
      // 重试：上一次的镜窗可破坏物、路人眼睛是 S.spawn 生成的（不归战斗管），不清掉会一层层叠起来（旧的打碎了还挡着新的）
      for(const o of G.world.stage.actors)if(o.id&&/^(reflection_|eye_|jgeil_civilian)/.test(o.id))o.remove=true;
      const d=c.data;Object.assign(d,{phase:0,reflectActors:[],reflections:[],stabs:0,nextKnife:2,nextGun:2.5,nextCoin:12,lightUntil:0,coinUntil:0,coinAt:0,coinCheck:0,blindUntil:0,gun:null,knifeWarn:0});
      const kak=S.actor('kakyoin');if(kak){kak.minHp=1;kak.hp=kak.maxHp=100;kak.brain=()=>true;kak.moves=[];kak.team='npc';S.follow(kak,c.player);kak.visible=true;}
      for(const [id,x,y] of [['mirror',48,116],['window',248,116]]){const r={kind:id,x,y,reach:95,dead:false};d.reflections.push(r);const o=S.spawn('prop:mirror_shard',x,162,{id:'reflection_'+id,team:'object',hp:20,alpha:0,shadow:false});o.breakable={onBreak:()=>{r.dead=true;S.sfx('glass_break');for(let k=0;k<3;k++)d.reflections.push({kind:'shard',x:x+(k-1)*12,y:165,reach:18,expires:c.t+3});}};d.reflectActors.push(o);}
      for(const x of [92,173,276])d.reflections.push({kind:'puddle',x,y:172,reach:20});
      for(const [i,x] of [120,211].entries()){d.reflections.push({kind:'eye',x,y:145,reach:70,closedUntil:0});d.reflectActors.push(S.spawn('npc_townsfolk',x,163,{id:'eye_'+i,team:'npc'}));}
      d.draw=(P,ctx)=>drawHanged(P,d,ctx);
      S.hint('J3 打碎镜窗，K+J 扬沙让路人闭眼',10);
    },tick(c,dt){const d=c.data,p=c.player;if(d.phase){if(c.boss&&Math.floor(c.t)%7<2){const n=d.civilians&&d.civilians[Math.floor(c.t/7)%2];if(n&&c.boss.state==='idle')G.combat.walkTo(c.boss,n.x+(p.x<n.x?14:-14),n.y,dt,100);}return;}
      const rs=d.reflections.filter(r=>canReflect(r,c));if(rs.length)d.source=rs[Math.floor(c.t/3)%rs.length];else d.source=null;
      if(c.t>=d.nextKnife){d.nextKnife=c.t+2.6;if(d.source){const r=d.source;c.boss.x=r.x;d.knifeWarn=c.t+.5;G.audio.sfx('slash');c.hazard({owner:c.boss,shape:'rect',x0:p.x-14,x1:p.x+14,y0:p.y-8,y1:p.y+8,warn:.5,dur:J.f(4),tier:'W1',dmg:14,guardSourceX:r.x,guardFromOwner:true,consume:true});}}
      // 荷尔·荷斯：先亮 0.6 s 红色弯曲虚线（规划 W4 36f），子弹照这条线飞；走出线外、面朝枪口按住 L，或精准弹反（キィン！）
      if(c.t>=d.nextGun&&!d.gun){d.nextGun=c.t+2.5;const x=p.x<160?300:20,y=164;d.gun={x,y,at:c.t+J.f(36),curve:[[x,y],[160,115],[p.x,p.y]]};G.combat.fxAt('glint',{x,y:y-22,size:8},c.boss,.6);G.audio.sfx('glint',{vol:.6});}
      if(d.gun&&c.t>=d.gun.at){const g=d.gun;d.gun=null;G.audio.sfx('gunshot',{vol:.7});c.shoot(c.boss,{kind:'bullet',dmg:12,curve:g.curve,curveDur:.45,life:1,reflect:true,guardSourceX:g.x},{x:g.x,y:g.y,z:22});}
      // 硬币：弹起后在半空停 40f；0.4 s 后（硬币到顶）没有别的倒影照到人，倒吊人只能跳进硬币——光路亮 30f，这期间按 J
      if(c.t>=d.nextCoin){d.nextCoin=c.t+12;d.coinX=p.x;d.coinAt=c.t;d.coinUntil=c.t+J.f(40);d.coinCheck=c.t+.4;G.audio.sfx('coin');G.ui.hint('花京院弹起了硬币——别让别的倒影照到你！',2.5);}
      if(d.coinCheck&&c.t>=d.coinCheck){d.coinCheck=0;if(!rs.length){d.lightFrom=d.lastSourceX||48;d.lightUntil=c.t+J.f(30);d.interceptUntil=c.t+J.f(30);G.audio.sfx('glint');G.ui.hint('光路出现！现在按 J！',1.5);}else G.ui.hint('还有倒影照到你！打碎镜窗、扬沙，走离水洼。');}
      if(d.source)d.lastSourceX=d.source.x;if(d.interceptUntil>c.t&&G.input.hit('attack')&&Math.abs(p.x-d.coinX)<=48){d.interceptUntil=0;d.lightUntil=0;d.stabs++;c.gauge.value=d.stabs;G.input.consume('attack');G.combat.fxAt('shatter',{src:'prop:mirror_shard',logical:'idle',x:d.coinX,y:78,pieces:44,dur:.9},p,.9);G.audio.sfx('slash');if(d.stabs>=3)exposeJgeil(c).catch(G.cancelIgnore);}
    },after:async(S,es,a,c)=>{for(const n of [...(c.data.reflectActors||[]),...(c.data.civilians||[])])n.remove=true;await S.say('polnareff','……为了雪莉。');S.fx('speedlines',{cx:180,cy:20,colour:'#fff0bf',n:16},{space:'canvas',life:.6});T.prop(S,'hat',650,170);await S.title('saiki');},
    testHint:c=>({phase:c.data.phase,stabs:c.data.stabs,coinIn:c.data.nextCoin-c.t,intercept:c.data.interceptUntil>c.t,activeReflections:(c.data.reflections||[]).filter(r=>canReflect(r,c)).map(r=>({kind:r.kind,x:r.x})),reflections:c.data.reflections})
  });
  G.BOSS25.empress=()=>J.base('b08_empress','joseph',[20,620],{
    vs:'empress',music:'battle',bench:'hide',gauge:{label:'女帝成长',max:3,value:0},
    waves:[[{actor:'empress',kit:'e_empress',boss:true,hp:600,minHp:1,x:150,y:160}]],
    kitOverride:{joseph:{special:J.special(0,'念写：U → 柏油方向',c=>c.data.growth>=1,async(S,p,c,C)=>{c.data.radarUntil=c.t+3;C.fx('vines',{x0:p.x,y0:p.y-15,x1:p.x+32,y1:p.y-40,t1:.5});S.sfx('camera_shutter');await C.wait(.35);},8)}},
    onWave:async(S,i,es,a,c)=>{const d=c.data;Object.assign(d,{growth:F().empressFruit?.3:0,reverseAt:6,radarUntil:0,tarIndex:1,barrels:[],police:[],policeAt:5,baseOut:c.player.dmgOut||1});c.player.dmgOut=d.baseOut*.7;
      for(const [i,x] of [100,325,555].entries())d.barrels.push(S.spawn('prop:tar_barrel',x,166,{id:'tar_barrel_'+i,team:'npc',shadow:false}));for(const [i,x] of [50,600].entries())d.police.push(S.spawn('npc_police',x,164,{id:'empress_police_'+i,team:'npc'}));
      // 女帝长在乔瑟夫的手臂上：Boss 本体只留判定和血条（透明），画面上是贴在前臂的小头，张嘴时换 bite 帧
      es[0].alpha=0;es[0].shadow=false;
      d.draw=(P,ctx)=>{const px=G.px,p=ctx.player,b=ctx.boss,level=Math.min(3,Math.floor(d.growth)),f=p.facing||1,bite=!!(b&&(b.tele||b.atk));px.blitFrame(P,'empress','l'+level+(bite?'_bite':'_idle'),0,Math.round(p.x-(G.cam.x||0)-f*7),Math.round(p.y-(p.z||0)-14),{scale:.34+level*.06,flip:f<0});if(d.radarUntil>ctx.t){const x=d.barrels[d.tarIndex].x-(G.cam.x||0);px.ring(P,x,155,16,1,'#ffd84a');}};
      S.hint('成长到一级后按 U 念写，找到柏油桶按 E',10);
    },events:[{when:t=>t>=4,run:async S=>{await J.lines(S,[['joseph','你下一句要说的是——“杀人犯！”'],['empress','杀人犯！……咦？']]);S.sfx('sting_shock');}}],
    tick(c,dt){const d=c.data,p=c.player,b=c.boss;d.growth=Math.min(3,d.growth+dt/20);c.gauge.value=d.growth;b.idleAnim='l'+Math.floor(d.growth)+'_idle';b.x=p.x-8;b.y=p.y;b.z=20;
      if(c.t>=d.reverseAt){d.reverseAt=c.t+6;p.controlReverseUntil=G.clk.world+1;G.ui.hint('手臂在乱抓！左右颠倒一秒。');}
      for(const n of d.police){G.combat.walkTo(n,p.x+(n.x<p.x?-18:18),p.y,dt,38);if(Math.abs(n.x-p.x)<22&&c.t>=d.policeAt){p.rootT=.5;d.policeAt=c.t+3;G.audio.sfx('sting_shock');}if(G.input.hit('attack')&&Math.abs(n.x-p.x)<55){n.x+=Math.sign(n.x-p.x||1)*35;G.uifx.sfx('退开！',p);}}
      if(G.input.okHit()&&!d.qteBusy){const near=d.barrels.findIndex(a=>Math.abs(a.x-p.x)<26);if(near<0)return;G.input.consumeOk();if(near!==d.tarIndex){G.ui.hint('这桶不是柏油。用 U 念写找方向。');return;}J.qte(c,async()=>{G.audio.sfx('drain');await G.S.say('empress','动不了……这是什么！');const ok=await G.S.clash({label:'隐者之紫！波纹——！（连按 J）',time:4});if(!J.valid(c))return;if(ok){G.S.fx('vines',{x0:p.x-28,y0:p.y,x1:p.x+20,y1:p.y-25,t1:.6});c.end();}else{d.growth=Math.min(3,d.growth+1);d.tarIndex=(d.tarIndex+1)%3;G.ui.hint('女帝挣脱了！柏油桶换了位置。');}}).catch(G.cancelIgnore);}
    },after:async(S,es,a,c)=>{for(const n of [...c.data.barrels,...c.data.police])n.remove=true;await S.title('saiki');},testHint:c=>({growth:c.data.growth,tarIndex:c.data.tarIndex,barrels:c.data.barrels.map(a=>a.x),radar:c.data.radarUntil>c.t,reversed:c.player.controlReverseUntil>G.clk.world})
  });
  function calcutta(){const st=G.STAGES.calcutta_ch4;st.npcs=[T.npc('npc_townsfolk','spice_vendor',170,164,{talk:S=>S.say('avdol','这里的气味让我想起开罗。')}),T.npc('npc_kid','beggar',270,164,{talk:async S=>{await S.say('npc_kid','先生，给一点零钱好吗？');await S.say('joseph','怎么一下子来了这么多人！快走！');}})];st.hotspots=[J.hot('cow',350,160,'圣牛',[],S=>S.say('polnareff','牛舔了我一脸……Mon dieu！')),J.hot('taxi',610,145,'黄色出租车',[],S=>S.say('joseph','印度的车都这么开吗？')),J.hot('roof',810,70,'楼顶',['detail'],S=>S.say('jotaro','那边楼顶上，有个戴牛仔帽的家伙在看我们。'),S=>S.say('jotaro','那边楼顶上，有个戴牛仔帽的家伙在看我们。')),J.hot('alley',1050,125,'巷口',[],async S=>{F().ch4Alley=true;await S.say('polnareff','那个有两只右手的家伙……在里面！');})];}
  function varanasi(){const st=G.STAGES.varanasi_st_ch4;st.npcs=[T.npc('npc_police','varanasi_police',160,164,{talk:S=>S.say('npc_police','手臂上有怪物的外国老头！站住！')})];st.hotspots=[J.hot('fruit',80,144,'水果摊',[],async S=>{F().empressFruit=true;await S.say('empress','Baby～肚子饿了～');}),J.hot('newspaper',280,145,'报纸',[],S=>S.say('joseph','“通缉：手臂上有怪物的外国老头”……OH MY GOD！')),J.hot('river',550,130,'河坛石阶',[],async S=>{F().empressArena=true;await S.say('joseph','先摆脱警察，再想办法对付她！');})];}
  G.STORY.ch4=async S=>{for(const k of ['ch4Alley','empressArena','empressFruit'])delete F()[k];await G.MID.ensureBg('_ch4');S.party(crew,{leader:'jotaro'});await S.chapterCard('ch4');await S.setStage('map_ch4',{x:100,y:160,music:'travel'});await S.run(s=>s.route(['新加坡','加尔各答'],{vehicle:'train',day:9,left:42,cut:.6}));calcutta();await S.setStage('calcutta_ch4',{x:65,y:164});S.location('calcutta');J.anne(S);S.hint('探索印度街头，向右前往巷口。',10);await S.until(()=>F().ch4Alley&&!S.busy);
    await S.run(async s=>{s.nameCard('holhorse');await J.lines(s,[['holhorse','比起当老大，我更适合当老二。'],['polnareff','这是我妹妹的仇！谁都别插手！'],['avdol','波鲁纳雷夫，后面——！']]);const h=T.show(s,{bg:'black',parts:[{kind:'sprite',cid:'avdol',anim:'hurt',x:160,y:175,scale:3,alpha:.45},{kind:'sprite',cid:'polnareff',anim:'hurt',x:250,y:175,scale:2,alpha:.3}]});s.fx('glint',{x:165,y:95,size:22},{space:'canvas'});s.sfx('gunshot');await s.wait(.8);h.close();await T.closeup4(s,{cid:'polnareff',expr:'shock',dur:1.2});await s.say('polnareff','阿布德尔——！');G.party.remove('avdol',{look:'unknown'});await s.say('kakyoin','冷静！……我们一起去。');await s.setStage('alley_ch4',{x:150,y:164,music:'battle'});s.standCard('hangedman');await s.fight(G.BOSS25.hanged());await J.lines(s,[['holhorse','奈娜，挡住他们！'],['nena','荷尔·荷斯！'],['joseph','……走吧。阿布德尔不会希望我们停下来。']]);s.sfx('car_engine');await s.say(null,'乔瑟夫偷偷看了一眼怀表，什么也没说。');await s.setStage('map_ch4',{x:100,y:160,music:'travel'});await s.route(['加尔各答','瓦拉纳西'],{vehicle:'car',day:10,left:41,cut:.6});await J.lines(s,[[null,'第二天，乔瑟夫左臂上的一点血变成了肉瘤。'],['empress','Baby～']]);});
    S.party(['joseph'],{leader:'joseph'});varanasi();await S.setStage('varanasi_st_ch4',{x:70,y:164,music:'tension'});S.hint('乔瑟夫独自找办法；沿街走到河坛石阶。',10);await S.until(()=>F().empressArena&&!S.busy);
    await S.run(async s=>{await s.setStage('varanasi_ch4',{x:180,y:160});s.standCard('empress');await s.fight(G.BOSS25.empress());const h=T.show(s,{bg:'black',parts:[{kind:'sprite',cid:'nena',anim:'true_form',x:160,y:170,scale:2,o:{sil:'#24162e'}}]});await s.say('joseph','……原来她一直戴着别人的样子。');h.close();S.party(crew,{leader:'jotaro'});G.party.remove('avdol',{look:'unknown'});await J.end(s,'ch4_tbc');});
  };
})();
