// 专属招式仍走统一命中规则，环境机关由战斗 tick 驱动，避免受伤或预警暂停机关计时。
'use strict';
(function(){
  const G=window.G,M=G.MOVES,K=G.KITS,f=n=>n/60;
  const basic=(id,tier,frames,dmg,reach=48,o={})=>M[id]=Object.assign({slot:'enemy',body:'cmd',warn:{tier,dur:f(frames)},dur:f(frames+22),active:[f(frames),f(frames+4)],reach:[0,reach],depth:12,dmg,push:8,sfx:'whoosh',sfxHit:'punch',cd:1.4},o);
  const data=c=>c&&c.data||{};
  const closeBrain=(e,dt,c)=>{if(!dt||e.rootT>0)return true;const p=c.player;e.facing=p.x>e.x?1:-1;G.AI.approach(e,p,34,dt);if(e.cool<=0&&G.combat.tokens()<2){const id=G.AI.pickMove(e,c);if(id){G.AI.tele(e,id);e.cool=.7;}}return true;};
  const kit=(id,hp,speed,moves,o={})=>K[id]=Object.assign({hp,speed,moves,brain:closeBrain},o);
  basic('DB_CLAW','W1',24,12,48,{sfxHit:'slash'});
  basic('DB_SCALE','W4',30,8,0,{melee:false,fireAt:[f(30)],shot:{kind:'gem',n:3,spread:18,speed:200,dmg:8,hitR:[4,6,20],reflect:true,colour:'#74afd8'},shotMod:(a,c)=>({n:a.hp<=a.maxHp*.5?5:3,onHit:(s,t,r)=>{if(t===c.player&&r.dmg&&!r.guard)data(c).barnacles=Math.min(5,(data(c).barnacles||0)+1);}})});
  basic('DB_AMBUSH','W4',30,14,0,{melee:false,dash:{dist:120,time:f(16),w:10,line:true},guard:'pierce'});
  basic('DB_VORTEX','W3',40,0,0,{melee:false,dur:f(40+240),onStart:(e,c)=>{data(c).vortex={t:0,x:e.x,y:e.y};},onEnd:(e,c)=>{const d=data(c);d.vortex=null;d.openUntil=c.t+f(45);d.damageOpenUntil=c.t+f(30);}});
  kit('e_darkmoon',700,90,['DB_CLAW','DB_SCALE','DB_AMBUSH'],{poiseMax:60,dmgMul:(t,a,m)=>{const c=G.world.fight;return c&&c.t<data(c).damageOpenUntil?1.5:1;},brain(e,dt,c){if(!dt)return true;const d=data(c);d.nextVortex=d.nextVortex==null?8:d.nextVortex;if(c.t>=d.nextVortex&&!e.atk&&!e.tele){d.nextVortex=c.t+(e.hp<=e.maxHp*.5?10:15);G.AI.tele(e,'DB_VORTEX');return true;}if(e.atk&&e.atkId==='DB_VORTEX')return true;return closeBrain(e,dt,c);}});
  // 力量的三样机关：猩猩本体多半在镜头外（货舱 640 宽），预警必须画在玩家脚下 / 身边，不能只靠本体头上的「！」和紫边。
  //   管道：预警一开始（hazardAt 0）就在玩家脚下圈出红圈 + 地缝冒蒸汽，0.5 s 后管道才伸出来——走开就躲得掉（原来 warn 0，管道直接从脚下冒出来，看不到预警）
  //   吊钩：预警 0.75 s 期间整条过道在玩家这一条纵深画红线、头顶晃着吊钩（J25.drawPixel 画）——上下让开或者 K 闪过去（原来红线只在出手那 4f 出现）
  //   管道缠住一次就收回（consume）：原来每 20f 判一次（once:false），挣脱 QTE 时世界停着、人还站在圈里，一出 QTE 又被同一根管道抓住
  //   ——一根管道连抓 2–3 次、连按 2–3 轮（ra_ch2_r1：三次尝试 56 次挣脱 QTE、第一只眼睛还没打碎就掉了一半血）。伤害按规划改成抓住时 8
  basic('ST_PIPE','W3',30,8,0,{melee:false,hazardAt:0,hazard:(e,c,mv)=>{const p=c.player,w=G.combat.warnDur(mv,c);G.combat.fxAt('smoke',{x:p.x,y:p.y+2,n:8,colour:'#d8dce8',life:.5,rise:18},e,w);G.audio.sfx('door',{rate:.7,vol:.5});return {shape:'ellipse',x:p.x,y:p.y,rx:16,ry:8,warn:w,dur:1,root:1,dmg:8,tag:'pipe',consume:true,onHit:(h,t,r)=>{if(t===p&&r.dmg&&!r.guard&&data(c).pipeCatch)data(c).pipeCatch(t);}};}});
  basic('ST_HOOK','W5',45,16,0,{melee:false,hazardAt:0,hazard:(e,c,mv)=>({shape:'rect',x0:c.spec.arena[0],x1:c.spec.arena[1],y0:c.player.y-6,y1:c.player.y+6,warn:G.combat.warnDur(mv,c),dur:f(6),dmg:16,guard:'none',tag:'hook',sfx:'whoosh',sfxRate:.6})});
  basic('ST_THROW','W4',30,10,0,{melee:false,fireAt:[f(30)],shot:{kind:'bullet',speed:180,dmg:10,reflect:true,hitR:[5,7,18],colour:'#c8a064'}});
  basic('ST_GRAB','W2',45,18,38,{guard:'none'});
  // 机关间隔 1.2 s → 1.6 s（每碎一只眼睛再 +0.6 s）：原来 1.2 s 一下，招本身就要 0.9–1.1 s，等于一招接一招，没空在眼睛底下打一套 J3 + 连打
  kit('e_strength',650,80,['ST_PIPE','ST_HOOK','ST_THROW','ST_GRAB'],{poiseMax:50,dmgMul:()=>{const c=G.world.fight;return c&&(data(c).eyes||0)>=3?1:0;},brain(e,dt,c){if(!dt)return true;const d=data(c);e.facing=c.player.x>e.x?1:-1;if((d.eyes||0)>=3)return closeBrain(e,dt,c);if(e.cool<=0){const i=e.patternI++%3,n=['ST_PIPE','ST_HOOK','ST_THROW'][i];G.AI.tele(e,n);e.cool=1.6+(d.eyes||0)*.6;}return true;}});
  basic('DE_RAZOR','W1',24,10,42,{sfxHit:'slash'});
  basic('DD_ANKLE','W1',20,12,34,{root:f(20)});basic('DD_JUMP','W1',16,10,48);
  kit('e_devo',300,55,['DE_RAZOR']);
  // 玩偶钻进家具底下时头顶冒「？」（登记过的拟声字；原来写的「看玻璃碎片里的倒影！」没有预渲染图，只能记缺图、用字库硬画）
  kit('e_doll',400,105,['DD_ANKLE','DD_JUMP'],{onHitBy:(t,a,m,i)=>{if(!t.mem.hidden)return null;if(i.slot==='J3'||i.slot==='special'){t.mem.hidden=false;t.mem.revealUntil=(G.world.fight?G.world.fight.t:0)+.5;t.alpha=1;return null;}return 'evade';},brain(e,dt,c){if(!dt)return true;if(c.t>=(e.mem.hideNext||0)){e.mem.hideNext=c.t+4;e.mem.hidden=true;G.uifx.sfx('？',c.player);}const striking=e.atk&&e.atkT>=(e.atk.active?e.atk.active[0]:0);if(striking&&!e.mem.wasStriking){e.mem.hidden=false;e.mem.revealUntil=c.t+.5;}e.mem.wasStriking=!!striking;if(c.t>=(e.mem.revealUntil||0))e.mem.hidden=true;e.alpha=e.mem.hidden?0:1;if(e.tele)G.combat.fxAt('dust',{x:e.x,y:e.y,n:3,life:.15},e,.15);return closeBrain(e,dt,c);}});
  basic('YT_WHIP','W1',24,10,60);
  basic('YT_ENGULF','W2',45,0,30,{onHit:(e,t,c,r)=>{if(t===c.player&&!r.guard&&data(c).engulf)data(c).engulf(t);},dmg:1,guard:'none'});
  // 甩黏液：预警一开始就在玩家脚下圈出要落黏液的地方（原来 warn 0，黏液直接落在脚下，W3 的 0.67 s 预警看不到画在哪）
  basic('YT_SPLASH','W3',40,0,0,{melee:false,hazardAt:0,hazard:(e,c,mv)=>{const p=c.player;return {shape:'rect',x0:p.x-22,x1:p.x+22,y0:p.y-10,y1:p.y+10,warn:G.combat.warnDur(mv,c),dur:3,dmg:3,tick:.6,once:false,tag:'slime',onHit:(h,t,r)=>{if(t===p&&!r.guard)data(c).slime=Math.min(5,(data(c).slime||0)+1);}};}});
  basic('YT_GRAB','W1',20,6,40);
  kit('e_yellow',600,70,['YT_WHIP','YT_ENGULF','YT_SPLASH'],{dmgMul:()=>{const c=G.world.fight;return data(c).water?1.5:.1;},brain:(e,dt,c)=>{e.moves=data(c).water?['YT_GRAB']:['YT_WHIP','YT_ENGULF','YT_SPLASH'];return closeBrain(e,dt,c);}});
  basic('JG_KICK','W1',20,10,40);basic('JG_DUST','W4',30,0,0,{melee:false,onStart:(e,c)=>{data(c).blindUntil=c.t+1;},hazard:(e,c)=>({shape:'rect',x0:e.x-90,x1:e.x+90,y0:140,y1:180,warn:0,dur:f(4),dmg:1})});
  basic('PO_SAND_KICK','W1',1,0,36,{slot:'J3',body:'cmd',dur:f(20),active:[0,f(4)],onStart:(p,c)=>{for(const r of data(c).reflections||[])if(r.kind==='eye'&&Math.abs(r.x-p.x)<56)r.closedUntil=c.t+10;G.combat.fxAt('dust',{x:p.x,y:p.y,n:12},p,.4);},melee:false});
  kit('e_jgeil',600,80,['JG_KICK','JG_DUST'],{poiseMax:40});
  basic('EMP_BITE','W1',12,4,0,{melee:false,hazard:(e,c)=>({shape:'ellipse',x:c.player.x,y:c.player.y,rx:14,ry:12,warn:0,dur:f(4),dmg:4})});
  basic('EMP_STRANGLE','W2',45,30,0,{melee:false,hazard:(e,c)=>({shape:'ellipse',x:c.player.x,y:c.player.y,rx:20,ry:15,warn:0,dur:f(4),dmg:30})});
  kit('e_empress',600,0,['EMP_BITE'],{dmgMul:(t,a,m)=>m.slot==='special'?.5:0,brain(e,dt,c){if(!dt)return true;e.x=c.player.x;e.y=c.player.y;if(e.cool<=0){G.AI.tele(e,data(c).growth>=3?'EMP_STRANGLE':'EMP_BITE');e.cool=2;}return true;}});
  basic('WF_RAM','W4',30,10,0,{melee:false,hazard:(e,c)=>({shape:'rect',x0:c.player.x-18,x1:c.player.x+18,y0:e.y-4,y1:e.y+4,warn:0,dur:f(4),dmg:10})});
  basic('WF_SIDE','W4',30,8,0,{melee:false,hazard:(e,c)=>({shape:'rect',x0:c.player.x-14,x1:c.player.x+14,y0:e.y-4,y1:e.y+4,warn:0,dur:f(4),dmg:8})});
  basic('WF_DIVE','W3',45,20,0,{melee:false,hazard:(e,c)=>({shape:'ellipse',x:c.player.x,y:c.player.y,rx:28,ry:10,warn:0,dur:f(6),dmg:20,push:30})});
  basic('WF_CHARGE','W4',30,16,0,{melee:false,dash:{dist:170,time:.55,w:10,line:true},guard:'pierce'});
  basic('WF_RAIN','W3',30,0,0,{melee:false,dur:2.5,onStart:(e,c)=>{data(c).oil=true;data(c).sparkAt=c.t+2;}});
  basic('WF_SPARK','W2',90,40,0,{melee:false,onStart:(e,c)=>{data(c).sparkUntil=0;if(!data(c).dug){G.combat.hit(e,c.player,{slot:'enemy',dmg:40,guard:'none',reach:[0,320],sfxHit:'explosion'});}data(c).dug=false;}});
  kit('e_wheelroad',900,90,['WF_RAM','WF_SIDE'],{dmgMul:()=>0,brain(e,dt,c){if(!dt)return true;e.x=135+Math.sin(c.t*.8)*38;if(e.cool<=0){e.y=[152,160,168][Math.floor(c.t*1.7)%3];G.AI.tele(e,e.patternI++%2?'WF_RAM':'WF_SIDE');e.cool=1.2;}return true;}});
  kit('e_wheel',900,95,['WF_DIVE','WF_CHARGE','WF_RAIN'],{armor:true,poiseMax:0,dmgMul:()=>{const c=G.world.fight;return c.t<data(c).flippedUntil?1.5:.5;},brain(e,dt,c){if(!dt)return true;const d=data(c);if(d.sparkAt&&c.t>=d.sparkAt&&!e.atk&&!e.tele){d.sparkAt=null;d.sparkUntil=c.t+1.5;G.AI.tele(e,'WF_SPARK');return true;}if(c.t<(d.flippedUntil||0)){e.rot=Math.PI;return true;}e.rot=0;return closeBrain(e,dt,c);}});
  basic('ZOMBIE_GRAB','W1',24,6,32,{root:.3});
  kit('e_zombie',30,40,['ZOMBIE_GRAB'],{koStyle:'fly'});
  kit('e_enya',800,0,[],{dmgMul:()=>{const c=G.world.fight;return c&&data(c).enyaOpen>c.t?1:0;},brain:()=>true});
  basic('LV_SPORE','W4',24,8,0,{melee:false,fireAt:[f(24)],shot:{kind:'gem',n:5,spread:35,speed:130,dmg:8,hitR:[3,6,18],colour:'#ffc0d8'}});
  basic('LV_DASH','W1',16,8,0,{melee:false,dash:{dist:90,time:.4,w:6,line:true}});
  kit('e_lovers',600,65,['LV_SPORE','LV_DASH']);
  G.BOSS25=G.BOSS25||{};
  const J=G.J25={f,hot:(id,x,y,label,tags,use,look,o={})=>Object.assign({id,x,y,label,tags,r:24,ry:120,use,look},o),lines:async(S,rows)=>{for(const row of rows)await S.say(row[0],row[1],row[2]?{expr:row[2]}:{});},
    count(id){const F=G.flags;F[id]=(F[id]||0)+1;return F[id];},
    unique(id,key){const F=G.flags,s=F[id]||(F[id]={});s[key]=true;return Object.keys(s).length;},
    valid(c){return G.world.fight===c;},
    harm(c,n){c.player.hp=Math.max(0,c.player.hp-n);if(!c.player.hp)c.fail();},
    async qte(c,fn){if(c.data.qteBusy)return false;c.data.qteBusy=true;const w=G.world,old=w.cine;w.cine={by:'mechanic-qte'};try{return await fn();}finally{if(this.valid(c)){w.cine=old;c.data.qteBusy=false;}}},
    anne(S){if(!G.flags.anneJoined||G.flags.anneLeft)return;const a=S.actor('anne')||S.spawn('anne',S.player.x-34,S.player.y,{id:'anne',team:'npc',label:'安妮'});S.follow(a,S.player);a.followSlot=6;a.leadable=false;},
    async end(S,mark){await S.tbc();S.mark(mark);},
    special(need,prompt,window,run,cd=8){return {need,prompt,window,run,cd};},
    resetActors(c){for(const a of c.enemies())a.remove=true;},
    base(id,lead,arena,extra={}){return Object.assign({id,lead,swap:false,arena,losable:true,playerMinHp:0,energy:{start:0},dmgScale:.9,warnTier:1},extra);},
    fire(p,range,dmg=60){return G.combat.createC(p).hitArea({x0:p.x+Math.min(0,p.facing*range),x1:p.x+Math.max(0,p.facing*range),y0:p.y-14,y1:p.y+14},{slot:'special',dmg,push:8,zr:160,poiseDmg:25,energy:0});},
    async transfer(c,id,px,ex){if(c.data.shifting)return;c.data.shifting=true;const old=G.world.cine,es=c.enemies().slice();G.world.cine={by:'battle-transition'};try{await G.S.setStage(id,{x:px,y:160,fade:false,music:null});if(!this.valid(c))return;for(const e of es){e.remove=false;e.x=ex==null?e.x:ex;G.world.stage.add(e);}G.world.stage.x0=c.spec.arena[0];G.world.stage.x1=c.spec.arena[1];this.rehide(c);}finally{if(this.valid(c)){G.world.cine=old;c.data.shifting=false;}}},
    // 换图会把整队带过去、重建跟随（party._applyVisible 还会把战前“同屏人数超了”藏起来的人重新显示）：
    //   这一战 bench:'hide' 的人再藏一次，只留操作角色和 AI 同伴（第3章黄色节制跳海时，板凳上的同伴原来会出现在海里）
    rehide(c){const b=c.spec.bench,mode=b&&typeof b==='object'?b.mode:b;if(mode!=='hide')return;const al=c.spec.allies||[];for(const a of G.party.members)if(a!==G.world.player&&!al.includes(a.cid)){a.visible=false;a.follow=null;if(a.stand)a.stand.hide();}},
    ui(c,text){G.ui.hint(text);},
    async inputTask(c,o){const run=G.runId,w=G.world,old=w.cine,start=G.clk.ui;let done=false,ok=false;w.cine={by:'mechanic-input'};const tick=()=>{if(run!==G.runId||w.fight!==c||c.data.joHp===0){done=true;return true;}const t=G.clk.ui-start;if(o.tick(c,t)){ok=true;done=true;return true;}if(t>=o.time||o.fail&&o.fail(c,t)){done=true;return true;}return false;};w.ticks.push(tick);try{await G.until(()=>done||run!==G.runId);return ok;}finally{const i=w.ticks.indexOf(tick);if(i>=0)w.ticks.splice(i,1);if(this.valid(c))w.cine=old;}},
  };
  J.drawPixel=function(P,layer){if(layer!=='mid'||!G.world.fight||G.world.insert)return;const c=G.world.fight,d=c.data,px=G.px,cx=G.cam.x||0;
    if(d.draw)d.draw(P,c);
    if(d.slime)for(let i=0;i<d.slime;i++)px.rect(P,c.player.x-cx-8+i*3,c.player.y-24,2,8,'#ffee38');
    if(d.barnacles)for(let i=0;i<d.barnacles;i++)px.rect(P,c.player.x-cx-9+i*4,c.player.y-36,3,4,'#b0a088');
    if(d.holes)for(let i=0;i<d.holes;i++)px.ellipse(P,c.player.x-cx-10+i*6,c.player.y-32,c.player.x-cx-6+i*6,c.player.y-28,'#100c20');
    if(d.reflections){for(const r of d.reflections)if(!r.dead&&!(r.closedUntil>c.t)){px.line(P,r.x-cx-6,r.y-7,r.x-cx+6,r.y-7,'#c0efff',.8);if(r===d.source)px.line(P,r.x-cx,r.y-7,c.player.x-cx,c.player.y-30,'#ff7050',.8);}if(d.lightUntil>c.t)px.line(P,d.lightFrom-cx,95,d.coinX-cx,75,'#ffe880',1,2);}
    if(d.bubbleUntil>c.t)for(let i=0;i<6;i++)px.ellipse(P,d.bubbleX-cx-2,(c.t*45+i*27)%160-3,d.bubbleX-cx+2,(c.t*45+i*27)%160+3,'#b4ffff',null,1,.7);
    if(d.eyesActors)for(const a of d.eyesActors)if(!a.dead){const x=a.x-cx,y=a.visualY;px.ellipse(P,x-9,y-5,x+9,y+5,'#b46488');px.ellipse(P,x-4,y-4,x+4,y+4,'#ffee68');px.rect(P,x-1,y-3,2,6,'#160c24');}
    // 力量的吊钩预警：玩家头顶垂下一根铁链、吊钩来回晃（红线由 combat 画在这条纵深上），晃得越来越快 = 快扫过来了
    for(const h of G.world.hazards)if(h.tag==='hook'&&h.phase==='warn'&&!h.dead){const u=Math.min(1,h.t/Math.max(.01,h.warn)),hx=Math.round(c.player.x-cx+Math.sin(G.clk.world*(5+9*u))*(10+14*u)),hy=Math.round(h.y0-42);
      for(let y=0;y<hy;y+=3)px.rect(P,hx,y,1,2,'#7a7a88');px.rect(P,hx-1,hy,3,7,'#c8c8d4');px.line(P,hx,hy+7,hx+5,hy+11,'#c8c8d4',1,2);px.line(P,hx+5,hy+11,hx+6,hy+6,'#c8c8d4',1,2);}
    if(d.radarUntil>c.t){const dx=d.barrels[d.tarIndex].x-c.player.x,x=c.player.x-cx;px.line(P,x,c.player.y-58,x+Math.sign(dx)*24,c.player.y-58,'#ffd640',1,2);px.line(P,x+Math.sign(dx)*24,c.player.y-58,x+Math.sign(dx)*18,c.player.y-63,'#ffd640',1,2);}
  };
})()
