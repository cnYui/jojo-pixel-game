// 战斗规则集中在这里，剧情仅订阅事件，避免教学、Boss 与玩家各自维护一套伤害判定。
'use strict';
(function () {
  const G = window.G, f = n => n / 60;
  const CFG = {
    comboBufFrom:f(2), comboBuf:f(12), rushEntryWin:f(15), rushEntryPresses:1,
    rushSustain:f(12), rushMax:f(90), rushCd:f(30), rushStopPerHit:f(1), rushHurtStun:f(4),
    fin:{dmg:16,push:40,stopAll:f(8),recover:f(24),energy:4},
    dodge:{dist:48,dur:f(14),iframe:f(10),cd:f(30),yMul:.6},
    graze:{win:f(6),energy:10,nextMul:1.3,nextT:f(30),word:'看穿！',bullet:{k:.3,dur:f(24),cd:3,bossOnly:true,tintAmount:.35}},
    guard:{mul:.2,pushLight:8,pushHeavy:16,energy:1,releaseLock:f(4)},
    parry:{win:f(6),lockout:.35,energy:15,stun:f(30),poiseDmg:25,stopAll:f(6),word:'キィン！'},pierceLeak:.3,
    hurt:{light:f(12),heavy:f(24),heavyPush:24,down:f(30),getupIframe:f(30)},invuln:{heavy:f(33),light:f(10)},
    ally:{downT:2.2,getupHp:.6,getupIframe:1,energyMul:.5,specialChance:.3},
    energy:{max:100,j:2,rushHit:1,shotHit:1,fin:4,hurt:4,hurtEvery:f(20),guard:1,graze:10,parry:15},lowHp:.25,
    stop:{light:f(3),heavyAll:f(6),rush:f(1),finAll:f(8),specialAll:f(12),specialHold:.2,bossKoAll:f(18),parryAll:f(6)},
    shake:{light:[1,f(6)],mid:[3,f(15)],heavy:[5,.5]},
    poise:{j12:10,j3:25,rush:3,shot:2,parry:25,breakStun:f(90),breakMul:1.2,regen:f(120)},
    armorTiers:['W2','W5','W6'],rushCap:{after:f(45),mul:.6,counter:'BOSS_BURST'},
    wallSlam:{minPush:40,bounce:8,sfx:'wall_slam',crack:12},
    warnTier:{1:{W1:f(24),W2:f(45),W3:1,W4:f(36),W5:f(45),W6:1},2:{W1:f(20),W2:f(40),W3:f(50),W4:f(30),W5:f(40),W6:1},3:{W1:f(18),W2:f(36),W3:f(45),W4:f(28),W5:f(36),W6:1},4:{W1:f(16),W2:f(30),W3:f(40),W4:f(24),W5:f(30),W6:1}},
    enemyDmg:{light:8,mid:12,heavy:20,super:30},maxTokens:2,cutin:.92,
    failSlow:{k:.3,dur:.5},failSepia:.6,assistMul:.7,assistAfter:2
  };
  const W = () => G.world, now = () => G.clk.world, ctx = () => W().fight;
  const clamp = (n,a,b) => Math.max(a,Math.min(b,n));
  const cancelled = e => G.cancelled && G.cancelled(e);
  const guardedWait = p => Promise.resolve(p).catch(e=>{if(cancelled(e))return false;throw e;});
  const background = p => Promise.resolve(p).catch(G.cancelIgnore);
  const actors = () => W().stage ? W().stage.actors : [];
  const enemySide = a => a && a.team === 'enemy';
  const alive = a => a && !a.remove && !a.dead && a.hp > 0 && !a.untargetable && a.visible !== false;
  const targets = a => actors().filter(t => t !== a && alive(t) && (enemySide(a) ? t === W().player || t.team === 'ally' || t.vip : t.team === 'enemy' || t.team === 'object'));
  const emit = (type,data) => { if (G.dbg && G.dbg.ev) G.dbg.ev(type,data); const c=ctx(); if(c && c.emit)c.emit(type,data); };
  const snd = (name,o) => name && G.audio && G.audio.sfx && G.audio.sfx(name,o);
  const word = (text,a,o) => text && G.uifx && G.uifx.sfx && G.uifx.sfx(text,a,o);
  const fxAt = (name,kw,a,life,o={}) => G.fx && G.fx.spawn ? G.fx.spawn(name,kw,Object.assign({by:a,life},o)) : null;
  const play = (a,name,o) => a.play && a.play(name,o);
  const state = (a,s) => {a.state=s; a.stateT=0;};
  const idle = a => { a.atk=null; a.tele=null; a._preHazard=false; a.outline=null; a.auraFlame=null; a.ghostOn=false; state(a,'idle'); play(a,a.idleAnim || 'idle'); if(a.stand)a.stand.idle(); };
  const getMove = m => typeof m === 'string' ? G.MOVES[m] : m;
  const kitOf = a => Object.assign({},a.kit || G.KITS[a.cid] || {},ctx() && ctx().spec.kitOverride && ctx().spec.kitOverride[a.cid] || {});
  function normMove(m) {return Object.assign({slot:'enemy',dur:.5,active:[0,.1],reach:[0,40],depth:8,zr:26,from:'body',dmg:0,push:0,guard:'normal',hits:1,every:0,parryBreak:true,sfxHit:'punch',fxHit:'light'},getMove(m) || {});}
  function gainEnergy(a,n,reason) {
    if(!a || !n || enemySide(a))return;
    const old=a.energy || 0; a.energy=clamp(old+n*(a===W().player ? 1 : CFG.ally.energyMul),0,CFG.energy.max);
    if(old<100 && a.energy>=100){if(a===W().player && G.hud)G.hud.flashEnergy(); else snd('meter_full');}
  }
  function resetActor(a) {
    if(a.rush && a.rush.loop && a.rush.loop.stop)a.rush.loop.stop(.05);
    if(a.mem && a.mem.buzz && a.mem.buzz.stop)a.mem.buzz.stop(.05);
    Object.assign(a,{hp:a.maxHp,energy:0,stopT:0,iframe:0,invuln:0,rootT:0,rootImmuneT:0,rootBy:null,stunT:0,burn:null,breakT:0,poise:a.poiseMax || 0,poiseIdleT:0,chainT:0,chainGapT:0,nextMul:1,nextMulT:0,dead:false,remove:false,atk:null,atkT:0,tele:null,rush:null,rushCdT:0,dodgeCd:0,combo:-1,ghostOn:false,ghosts:[],state:'idle',stateT:0,vx:0,vy:0,vz:0,rot:0,alpha:1,outline:null,firstParryDone:false,parryUntil:-Infinity,lastGuardPressT:-Infinity,parryLockUntil:-Infinity,tsGuard:false,mem:{}});
    play(a,a.idleAnim || 'idle'); if(a.stand){a.stand.skin=null;a.stand.idle();}
  }
  function origin(a,m) {return m.from==='stand' && a.stand ? a.stand.origin() : a;}
  function hitCheck(a,m,t) {
    m=normMove(m); const o=origin(a,m),sc=a.scale || 1;
    const test=t=>{
      if(t.breakable&&t.breakable.upward){return alive(t)&&Math.abs(t.x-o.x)<=24&&Math.abs(t.y-o.y)<=18&&['J3','rush','special'].includes(m.slot);}
      if(!alive(t) || Math.abs((t.z||0)-(o.z||0))>m.zr)return false;
      if(m.shape && m.shape.kind==='circle')return Math.hypot(t.x-o.x,t.y-o.y)<=m.shape.r*sc+(t.bodyW||6)*(t.scale||1);
      const dx=(t.x-o.x)*(a.facing||1),bw=(t.bodyW||6)*(t.scale||1);
      return dx>=m.reach[0]*sc-bw && dx<=m.reach[1]*sc+bw && Math.abs(t.y-o.y)<=m.depth*Math.max(sc,t.scale||1);
    };
    return t ? test(t) : targets(a).filter(test);
  }
  function shove(t,att,push) {
    if(!push)return; const dir=att ? Math.sign(t.x-att.x)||att.facing||1 : 1;
    t._push={left:.18,v:push*dir/.18,mag:Math.abs(push)};
  }
  function poiseHit(t,n) {
    if(!t.poiseMax || t.breakT>0)return;
    t.poise=Math.max(0,t.poise-n);t.poiseIdleT=0;
    if(t.poise<=0){t.breakT=CFG.poise.breakStun;t.atk=null;t.tele=null;state(t,'broken');play(t,'hurt');word('破绽！',t);fxAt('sparkles',{x:t.x,y:t.y-48,n:4,radius:8,colour:'#ffd83c',period:.5},t,t.breakT);}
  }
  function evade(t,att,m,o) {
    emit('evade',{who:t,src:o.src || m});
    // source 保存首个重叠，而不是每次 K 重新认领持续危险区。
    if(o.first !== false && !t.grazed && now()-t.dodgeT0<=CFG.graze.win+1e-8 && now()>=t.dodgeT0){
      t.grazed=true;t.nextMul=CFG.graze.nextMul;t.nextMulT=CFG.graze.nextT;gainEnergy(t,10,'graze');
      fxAt('glint',{x:t.x,y:t.y-40,size:8,dur:.25},t,.25);word(CFG.graze.word,t);snd('dodge_perfect');emit('graze',{who:t,src:o.src || m,boss:!!(att&&att.boss)});
      if(att && att.boss && now()>=(t._bulletNext || 0)){t._bulletNext=now()+3; W().slow=.3;W()._combatSlowT=f(24); if(G.post)G.post.filter('ts_'+t.cid,.35,{dur:f(24)});}
    }
    return {evade:true,dmg:0};
  }
  function parry(t,att,m,o) {
    gainEnergy(t,15,'parry');emit('parry',{who:t,att,move:o.src || m});snd('parry');word(CFG.parry.word,t);G.hitStopAll(CFG.parry.stopAll);
    if(G.fx)G.fx.hit(t.x,t.y-24,'parry',{by:t,colour:t.stand&&t.stand.color});
    if(!t.firstParryDone){t.firstParryDone=true;if(G.post)G.post.impact('bw3',f(2));}
    if(att && att.atk && m.parryBreak!==false){att.atk=null;att.tele=null;}
    if(m.onParried && m.onParried(att,t,ctx())===true){if(o.shot)o.shot.dead=true;return {parry:true,dmg:0,handled:true};}
    const k=kitOf(t).parry || {},s=o.shot;
    if(s){
      if(k.effect==='reflect' && s.reflect!==false){s.owner=t;s.side='player';s.vx=-s.vx;s.vy=-s.vy;s.ang=Math.atan2(s.vy,s.vx);s.hitSet.clear();s.firstT.clear();s.life=Math.max(s.life,.8);}
      else s.dead=true;
    }
    if(att){att.stunT=CFG.parry.stun;att._hurtDur=CFG.parry.stun;att.atk=null;att.tele=null;state(att,'hurt');play(att,'hurt');poiseHit(att,25);att.flash=f(2)*7;
      if(['root','sink'].includes(k.effect)){att.rootT=Math.max(att.rootT,k.dur || .5);att.rootBy=t;fxAt('vines',{x:att.x,y:att.y,n:5,h:35,colour:k.fx==='firerope'?'#ff6030':'#70ffb0'},t,att.rootT);}
    }
    return {parry:true,dmg:0};
  }
  function hit(att,t,move,o={}) {
    const m=normMove(move),slot=m.slot,info={slot,shot:o.shot||null,rushHits:att && att.rush ? att.rush.n+1 : 0};
    if(!t || t.dead || t.remove)return {dmg:0};
    if(!o.queued && G.time && G.time.isFrozen(t)){G.time.queueHit(t,att,m);return {queued:true,dmg:0};}
    if(!o.queued && t.iframe>0)return evade(t,att,m,o);
    if(!o.queued && t.invuln>0)return {invuln:true,dmg:0};
    // 隐藏网的捕捉先于飞虫闪避钩子，否则“未定身就闪避”会使网永远无法命中。
    if(m.tag==='net' && m.root && t.rootImmuneT<=0){t.rootT=t.boss && m.rootBoss!=null?m.rootBoss:m.root;t.rootImmuneT=t.rootT+(m.rootImmune||1);t.rootBy=att;}
    const hook=t.onHitBy || kitOf(t).onHitBy,mode=!o.queued && hook ? hook(t,att,m,info) : null;
    if(mode==='evade'){word(t.evadeWord,t);emit('evade',{who:t,src:o.src||m});return {evade:true,dmg:0};}
    if(mode==='parry'){if(att){att.stunT=f(20);att._hurtDur=f(20);att.atk=null;att.tele=null;state(att,'hurt');play(att,'hurt');}word('キィン！',t);snd('parry');return {parry:true,dmg:0};}
    const sourceX=m.guardSourceX==null?att&&att.x:m.guardSourceX;
    const front=o.hazard&&!m.guardFromOwner&&m.guardSourceX==null || sourceX==null || (sourceX-t.x)*(t.facing||1)>=-1;
    const queuedGuard=o.queued && t.tsGuard && m.guard!=='none';
    if(!o.queued && front && m.guard!=='none' && now()<=t.parryUntil+1e-8 && (!o.hazard || o.parryAllowed))return parry(t,att,m,o);
    const guarded=!o.queued && front && (mode==='block' || t.state==='guard') && !['none','parryOnly'].includes(m.guard);
    let mul=typeof t.dmgMul==='function'?t.dmgMul(t,att,m,info):t.dmgMul==null?1:t.dmgMul;
    if(slot==='rush' && att && att.rush){att.rush.n++;emit('rushHit',{who:att,n:att.rush.n});}
    if(t.team==='object' && t.breakable){
      const b=t.breakable;b.onHit&&b.onHit(G.S,b,info);
      if((b.filter ? !b.filter(m,info) : b.only && !(Array.isArray(b.only)?b.only:[b.only]).includes(slot)) || b.minRushHits && info.rushHits<b.minRushHits)mul=0;
    }
    if(mul<=.01){snd('clang');fxAt('clash_sparks',{x:t.x,y:t.y-22,colour:'#c080ff'},att,.2);return {immune:true,dmg:0};}
    const c=ctx(),side=enemySide(att)?(c?c.spec.dmgScale==null?1:c.spec.dmgScale:1)*(c&&c.assist?CFG.assistMul:1):1;
    let dmg=Math.max(1,Math.round((m.dmg||0)*mul*(att&&att.dmgOut || 1)*(t.dmgIn || 1)*side*(att&&att.nextMul || 1)*(t.breakT>0 ? t.mem.breakMul || CFG.poise.breakMul:1)*(slot==='rush' && t.boss && t.chainT>=CFG.rushCap.after?CFG.rushCap.mul:1)*(guarded ? m.guard==='pierce' ? CFG.pierceLeak : CFG.guard.mul:queuedGuard?.3:1)));
    if(!m.dmg)dmg=0;
    const min=Math.max(t.minHp || 0,t===W().player && c ? c.spec.playerMinHp || 0 : 0);
    t.hp=Math.max(min,t.hp-dmg);t.flash=Math.max(t.flash || 0,m.flashTarget ? m.flashTarget*7 : .9);
    if(att){att.nextMul=1;att.nextMulT=0;gainEnergy(att,(m.energy==null ? slot==='rush'?1:slot==='shot'?1:slot==='fin'?4:2:m.energy)*(t.team==='object'?.5:1),'hit');}
    if(guarded){gainEnergy(t,1,'guard');snd('guard');emit('guard',{who:t,att,move:m});shove(t,att,m.push>=24?16:8);if(G.fx)G.fx.hit(t.x,t.y-24,'guard',{by:t});}
    if(t===W().player || t.team==='ally'){
      if(!o.queued)t.invuln=m.push>=24?CFG.invuln.heavy:CFG.invuln.light;
      if(dmg>0 && !guarded && now()>=(t.hurtEnergyT || 0)){gainEnergy(t,4,'hurt');t.hurtEnergyT=now()+f(20);}
    }
    if(m.stop){if(att)att.stopT=Math.max(att.stopT || 0,m.stop);t.stopT=Math.max(t.stopT || 0,m.stop);}
    if(m.stopAll){G.hitStopAll(m.stopAll);if(m.stopAll>=.1 && G.audio.duck)G.audio.duck(.65,.15);}
    if(G.fx)G.fx.hit(t.x,t.y-24,guarded?'guard':m.fxHit,{by:att,colour:m.accent});
    snd(m.sfxHit,{rate: m.sfxRate || 1,vol:m.sfxVol==null?1:m.sfxVol,x:t.x});
    if(m.hitSfx2)snd(m.hitSfx2.name,m.hitSfx2);
    if(m.hitFx)for(const e of m.hitFx)fxAt(e.name,Object.assign({x:t.x,y:t.y-22},e.kw),att,e.life);
    if(m.shake)G.shake(...m.shake);if(m.bump && G.cam.bump)G.cam.bump(m.bump);word(m.word,t);
    if(att && !enemySide(att) && G.hud)G.hud.comboHit(att.rush ? kitOf(att).rush.word : m.word);
    if(!guarded && t.team!=='object'){poiseHit(t,m.poiseDmg==null ? slot==='special'?999:slot==='rush'?3:slot==='shot'?2:slot==='J3'||slot==='fin'?25:10 : m.poiseDmg);}
    const armor=t.armor || t.tele && CFG.armorTiers.includes(t.tele.tier) || t.atk && t.atkT<t.atk.active[1] && (t.atk.armor || t.atk.warn && CFG.armorTiers.includes(t.atk.warn.tier));
    const gap=now()-(t._lastHit==null?-Infinity:t._lastHit);t.chainT=gap<.3?(t.chainT || 0)+gap:0;t._lastHit=now();
    if(t.boss && t.chainT>=CFG.rushCap.after)t._counter=true;
    if(!guarded && !queuedGuard && !armor && t.team!=='object' && t.breakT<=0 && t.hp>0){
      t.atk=null;t.tele=null;t._preHazard=false;cancelRush(t);t.facing=att?Math.sign(att.x-t.x)||t.facing:t.facing;
      state(t,m.launch?'launched':'hurt');play(t,'hurt');t._hurtDur=slot==='rush'?f(4):m.push>=24?f(24):m.stun || f(12);
      if(m.launch){const d=m.launch.t || .4;t._launch={t:0,dur:d,h:m.launch.z || 16};}
      else if(m.push>=24)t._heavyDown=true;
      shove(t,att,m.push);
    }
    if(m.root && t.rootImmuneT<=0){t.rootT=t.boss && m.rootBoss!=null?m.rootBoss:m.root;t.rootImmuneT=t.rootT+(m.rootImmune || 1);t.rootBy=att;}
    if(m.burn){const b=m.burn,tick=b.tick||.5;t.burn=Object.assign({},b,{owner:att,tick,dps:b.dps==null?(b.dmg||4)/tick:b.dps,until:now()+(b.dur||tick*(b.n||2))+1e-6,_next:now()+tick});}
    emit('hit',{att,t,move:m,dmg,guard:guarded,slot,rushHits:info.rushHits});if(t===W().player && dmg)emit('hurt',{att,move:m,dmg});
    if(min>0 && t.hp===min && (t.koStyle==='none' || c && c.spec.finish==='none'))emit('koBlocked',{e:t});
    if(t.hp<=0)ko(t,att);
    else if(t.team==='object' && t.breakable && t.hp<=0)ko(t,att);
    return {dmg,guard:guarded,t};
  }
  function startMove(a,id,o={}) {
    const m=normMove(id);if(m.warn && m.warn.tier==='W5'&&m.guard!=='parryOnly')m.guard='none';a.atk=m;a.atkId=typeof id==='string'?id:null;a.atkT=o.elapsed || 0;a._hitSet=new Set();a._window=-1;a._fired=new Set();a._lastEvery=0;
    a.tele=null;state(a,m.slot==='fin'?'rushEnd':'attack');play(a,m.body || 'cmd',{restart:true});
    if(a.stand && m.stand)a.stand.act(m.stand,{dx:m.standDx,seq:m.standSeq,dur:m.dur});
    if(m.step)W().move(a,m.step*a.facing,0);snd(m.sfx,{vol:m.sfxVol,rate:m.sfxRate});
    if(m.onStart)m.onStart(a,ctx());
    if(m.hazard && m.hazardAt===0 && !a._preHazard)makeMoveHazards(a,m);a._preHazard=false;
    return m;
  }
  function makeMoveHazards(a,m){const hs=m.hazard(a,ctx(),m);for(const h of Array.isArray(hs)?hs:[hs])if(h)hazard(Object.assign({owner:a,side:enemySide(a)?'enemy':'player'},h));}
  function moveTick(a,dt) {
    const m=a.atk;if(!m)return;const prev=a.atkT;a.atkT+=dt;
    if(m.preSfx && prev<=m.preSfx.at && a.atkT>=m.preSfx.at)snd(m.preSfx.name,m.preSfx);
    if(m.standSeqs)for(let i=0;i<m.standSeqs.length;i++)if(prev<=m.standSeqs[i][0] && a.atkT>=m.standSeqs[i][0] && a.stand)a.stand.act(m.stand,{dx:m.standDx,seq:m.standSeqs[i][1].map(q=>[q[0],q[1]-m.standSeqs[i][0]])});
    for(const t of m.fireAt || [])if(a.atkT>=t && !a._fired.has(t)){a._fired.add(t);
      // 先复制弹体，避免教学放宽改到共享招式，也兼容返回覆写的修饰器。
      const shot=Object.assign({},m.shot);if(m.shotMod)Object.assign(shot,m.shotMod(a,ctx(),shot)||{});
      const org=m.shotFrom?m.shotFrom(a,ctx()):origin(a,m);shoot(a,shot,org);if(m.fireSfx)snd(m.fireSfx.name,m.fireSfx);}
    const active=a.atkT>=m.active[0] && a.atkT<m.active[1],wi=m.windows?m.windows.findIndex(q=>a.atkT>=q[0] && a.atkT<q[1]):active?0:-1;
    if(wi>=0 && wi!==a._window){a._hitSet.clear();a._window=wi;if(m.sfxEach)snd(m.sfxEach[wi]);if(m.slashArc)fxAt('slash_arc',{x:a.x+a.facing*22,y:a.y-26,size:m.slashArc},a,.2);}
    if(active && !a._fired.has('active')){
      a._fired.add('active');
      if(m.net){const n=m.net,xx=a.x+a.facing*n.x0,x1=a.x+a.facing*n.x1;const old=W().hazards.filter(h=>h.owner===a && h.tag==='net' && !h.dead);if(n.max && old.length>=n.max)old[0].dead=true;hazard({owner:a,side:'player',shape:'rect',x0:Math.min(xx,x1),x1:Math.max(xx,x1),y0:a.y-n.h,y1:a.y+n.h,tag:'net',warn:0,dur:n.dur,dmg:n.dmg,root:n.root,rootBoss:n.rootBoss,rootImmune:n.rootImmune,alpha:n.alpha,hidden:n.hidden,zr:80,fxActive:'tendrils_line',consume:true});}
      if(m.pillar){const p=targetOf(a),h=m.pillar;hazard({owner:a,side:'player',shape:'ellipse',x:p?p.x:a.x+a.facing*h.front,y:p?p.y:a.y,rx:h.r,ry:8,warn:h.warn,dur:h.dur,dmg:h.dmg,energy:h.energy,stopAll:h.stopAll,fromGround:true,fxActive:'fire',zr:60});}
      if(m.hazard && m.hazardAt!==0)makeMoveHazards(a,m);
      if(m.dash || m.diveAlongPath){const d=m.dash,pts=m.diveAlongPath?a._telePath:d.line && a._telePath || [[a.x,a.y],[a.x+a.facing*d.dist,a.y]];beginDash(a,pts,m.diveAlongPath || d.dist/d.time,m);}
    }
    if(a.mem.dash)dashTick(a,dt);
    if(wi>=0 && m.melee!==false){if(m.every && a.atkT-a._lastEvery>=m.every){a._lastEvery=a.atkT;a._hitSet.clear();}for(const t of hitCheck(a,m))if(!a._hitSet.has(t.uid)){a._hitSet.add(t.uid);const r=hit(a,t,m,{first:prev<=m.active[0],src:m});if(r.dmg && m.onHit)m.onHit(a,t,ctx(),r);if(a.atk!==m)break;}}
    if(a.atk===m && a.atkT>=m.dur){if(a===W().player && m.melee!==false && !m.shot && !m.net && !a._hitSet.size)emit('whiff',{who:a,move:m});if(m.onEnd)m.onEnd(a,ctx());idle(a);}
  }
  function startRush(a) {
    const k=kitOf(a),r=k.rush;if(!r)return false;
    a.atk=null;state(a,'rush');play(a,'cmd');a.rush={t:0,tick:0,n:0,end:CFG.rushSustain,wordT:0,loop:r.loop && G.audio.loop?G.audio.loop(r.loop):null};if(a.stand)a.stand.act('rush',{dx:16,hold:true,jitter:1});
    emit('rushStart',{who:a,n:0});if(G.dbg&&G.dbg.ev)G.dbg.ev('rush',{who:a});fxAt('rush',{x:a.x+a.facing*24,y:a.y-22,fist:r.fist || a.standId,flip:a.facing<0},a,CFG.rushMax,{follow:a});return true;
  }
  function cancelRush(a){const r=a.rush;if(!r)return;if(r.loop&&r.loop.stop)r.loop.stop(.05);emit('rushEnd',{who:a,n:r.n});a.rush=null;a.rushCdT=CFG.rushCd;}
  function endRush(a) {if(!a.rush)return;cancelRush(a);startMove(a,kitOf(a).rush.finisher);}
  function rushTick(a,dt,auto) {
    const r=a.rush,k=kitOf(a).rush;if(!r || !k)return;r.t+=dt;r.tick-=dt;r.wordT-=dt;
    if(!auto && G.input.take('attack',CFG.comboBuf))r.end=r.t+CFG.rushSustain;
    if(r.tick<=0){r.tick+=k.tick || f(4);const m=Object.assign({slot:'rush',from:'body',energy:1,stop:f(1),sfxHit:k.hitSfx || 'punch',fxHit:'light',poiseDmg:3},k);
      if(k.shot)shoot(a,Object.assign({slot:'rush'},k.shot));else for(const t of hitCheck(a,m))hit(a,t,m,{first:true});
      if(k.tickSfx)snd(k.tickSfx,{rate:k.tickSfxRate,vol:k.tickSfxVol});
      if(k.voice && (G.settings==null || G.settings.voices!==false) && r.n%2===0 && G.audio.voice)G.audio.voice(k.voice);
      fxAt('clash_sparks',{x:a.x+a.facing*36,y:a.y-24,n:3},a,.16);G.shake(1,.05);
    }
    if(r.wordT<=0){r.wordT=k.wordEvery || f(12);word(k.word,a,{size:42,jitter:2.5});}
    if(!auto && (r.t>=r.end-1e-9 || r.t>=CFG.rushMax-1e-9))endRush(a);
  }
  function dodge(a) {
    const d=Object.assign({},CFG.dodge,kitOf(a).dodge),i=G.input;let x=(i.isDown('right')?1:0)-(i.isDown('left')?1:0),y=(i.isDown('down')?1:0)-(i.isDown('up')?1:0);if(!x&&!y)x=-a.facing;
    if(a.controlReverseUntil>now())x=-x;
    const len=Math.hypot(x,y)||1;a._dodge={x:x/len*d.dist,y:y/len*d.dist*d.yMul,dur:d.dur,t:0,u:0};a.atk=null;cancelRush(a);a.iframe=d.iframe;a.dodgeCd=d.cd;a.dodgeT0=now();a.grazed=false;a.ghostOn=true;state(a,'dodge');play(a,'dodge');snd('dodge');if(G.fx)G.fx.dustAt(a.x,a.y,-x,4);emit('dodge',{who:a});
  }
  function motionTick(a,dt) {
    if(a._push){const p=a._push,before=a.x;W().move(a,p.v*Math.min(dt,p.left),0);p.left-=dt;if(Math.abs(a.x-before)<Math.abs(p.v*dt)*.5 && p.mag>=40 && now()>=(a._wallNext || 0)){a._wallNext=now()+1;W().move(a,-Math.sign(p.v)*8,0);snd('wall_slam');fxAt('crack',{x:a.x,y:a.y-20,size:12},a,.4);G.shake(3,.2);a.stunT=Math.max(a.stunT,f(12));p.left=0;}if(p.left<=0)a._push=null;}
    a.rushCdT=Math.max(0,(a.rushCdT || 0)-dt);a.guardRelT=Math.max(0,(a.guardRelT || 0)-dt);a._specialCd=Math.max(0,(a._specialCd || 0)-dt);a.cool=Math.max(0,(a.cool || 0)-dt);
    for(const id in a.moveCd)a.moveCd[id]=Math.max(0,a.moveCd[id]-dt);
    if(a.poiseMax){if(a.breakT<=1e-9)a.breakT=0;a.poiseIdleT+=dt;if(a.breakT<=0 && (a.state==='broken'||a.poiseIdleT>=2)){a.poise=a.poiseMax;a.mem.breakMul=null;if(a.state==='broken')idle(a);}}
    if(a.state==='dodge'){const d=a._dodge;d.t+=dt;const u=1-Math.pow(1-clamp(d.t/d.dur,0,1),3);W().move(a,d.x*(u-d.u),d.y*(u-d.u));d.u=u;if(d.t>=d.dur)idle(a);return true;}
    if(a.state==='launched'){const l=a._launch;if(l){l.t+=dt;a.z=l.h*Math.sin(Math.PI*clamp(l.t/l.dur,0,1));if(l.t>=l.dur){a.z=0;a._launch=null;state(a,'down');a.downT=f(30);play(a,'down');}}return true;}
    if(a.state==='hurt'){if(a.stateT>=a._hurtDur && a.stunT<=0){if(a._heavyDown){a._heavyDown=false;state(a,'down');a.downT=f(30);a.iframe=Math.max(a.iframe,f(30));play(a,'down');}else idle(a);}return true;}
    if(a.state==='broken')return true;
    if(a.state==='down'){
      if(a.hp<=0 && a!==W().player && a.team==='ally' && a.stateT>=2.2){a.hp=Math.round(a.maxHp*.6);a.iframe=1;idle(a);}
      else if(a.hp>0 && a.stateT>=(a.downT || .5)){a.iframe=Math.max(a.iframe,.5);idle(a);}return true;
    }
    if(a.stunT>0)return true;return false;
  }
  function guardPress(a) {const lp=G.input.lastPress('guard');if(lp===a.lastGuardPressT)return;a.lastGuardPressT=lp;if(lp>=a.parryLockUntil){a.parryUntil=lp+(kitOf(a).parryWin || CFG.parry.win);}else a.parryUntil=-Infinity;a.parryLockUntil=lp+CFG.parry.lockout;}
  function updatePlayer(a,dt) {
    const w=W(),i=G.input,k=kitOf(a);guardPress(a);
    if(motionTick(a,dt) || a.hold || a.state==='special')return;
    if(w.cine)return;
    if(!w.combat && (!w.free || G.ui && G.ui.blocking && G.ui.blocking()))return;
    const m=a.atk,can=!m || a.atkT>=(m.cancel==null?m.active[1]:m.cancel);
    if(w.combat && can && chords(a,k,dt))return;
    const deferKey=key=>Object.keys(k.chords||{}).some(name=>name.split('+').includes(key))&&i.fresh(key);
    if(w.combat && can && !deferKey('dodge') && i.take('dodge',.12) && a.dodgeCd<=0){dodge(a);return;}
    if(w.combat && can && i.take('special',.12)){background(special(a));if(a.state==='special')return;}
    if(w.combat && can && !deferKey('guard') && i.isDown('guard')){
      if(a.state!=='guard'){a.atk=null;state(a,'guard');play(a,'guard');if(a.stand)a.stand.act('block',{hold:true});}
      a.guardT+=dt;if(i.isDown('left'))a.facing=-1;if(i.isDown('right'))a.facing=1;
      if(k.guardAttack && i.take('attack',.12) && now()>=(a._guardAttackNext || 0)){const gm=getMove(k.guardAttack);a._guardAttackNext=now()+(gm.cd || 0);startMove(a,k.guardAttack);}return;
    }
    if(a.state==='guard'){idle(a);a.guardRelT=CFG.guard.releaseLock;return;}
    if(a.state==='rush'){rushTick(a,dt,false);return;}
    if(a.atk){
      const atk=a.atk;moveTick(a,dt);const t=a.atkT;
      if(atk.slot==='J3'){
        if(i.lastPress('attack')>=a._attackStart+atk.active[0] && i.lastPress('attack')<=a._attackStart+atk.active[1]+CFG.rushEntryWin && i.buffered('attack',.3))a._rushRequest=true;
        if(t>=atk.dur && a._rushRequest && a.rushCdT<=0){i.take('attack',.3);a._rushRequest=false;startRush(a);}
      }else if((atk.slot==='J1'||atk.slot==='J2') && t>=atk.link && i.lastPress('attack')>=a._attackStart+atk.active[0]+CFG.comboBufFrom && i.take('attack',CFG.comboBuf)){a.combo=(a.combo+1)%3;startPlayerMove(a,k.combo[a.combo]);}
      return;
    }
    if(a.guardRelT>0)return;
    if(!deferKey('attack') && i.take('attack',.12)){a.combo=0;startPlayerMove(a,k.combo && k.combo[0]);return;}
    let x=(i.isDown('right')?1:0)-(i.isDown('left')?1:0),y=(i.isDown('down')?1:0)-(i.isDown('up')?1:0);if(a.controlReverseUntil>now())x=-x;if(x || y){const d=Math.hypot(x,y);W().move(a,x/d*a.speed*dt,y/d*a.speed*.6*dt);if(x)a.facing=Math.sign(x);if(a.state!=='walk')state(a,'walk');play(a,'walk');}else if(a.state==='walk')idle(a);
    if(G.post && G.post.pulse)G.post.pulse('lowhp',w.combat && a.hp/a.maxHp<=CFG.lowHp);
  }
  function chords(a,k,dt){
    const i=G.input; a._chordHold=a._chordHold||{};
    for(const [name,action] of Object.entries(k.chords||{})){const keys=name.split('+');if(keys.length!==2)continue;
      if(typeof action==='object'&&action.hold){const held=keys.every(key=>i.isDown(key));const v=a._chordHold[name]||{t:0,done:false};a._chordHold[name]=v;if(!held){v.t=0;v.done=false;continue;}v.t+=dt;if(v.t>=action.hold&&!v.done){v.done=true;background(action.run(G.S,a,ctx(),createC(a)));}return true;}
      if(i.chord(...keys)){if(typeof action==='string')startPlayerMove(a,action);else if(action.run)background(action.run(G.S,a,ctx(),createC(a)));return true;}
    }return false;
  }
  function startPlayerMove(a,id){if(!id)return;a._attackStart=now();a._rushRequest=false;startMove(a,id);}
  function targetOf(a){const c=ctx(),fn=a.targetPick || kitOf(a).targetPick;let t=fn?fn(a,c):null;if(Array.isArray(t))t=t.reduce((b,x)=>!b || Math.hypot(x.x-a.x,x.y-a.y)<Math.hypot(b.x-a.x,b.y-a.y)?x:b,null);return alive(t)?t:enemySide(a)?W().player:targets(a).sort((x,y)=>Math.abs(x.x-a.x)-Math.abs(y.x-a.x))[0];}
  function updateEnemy(a,dt){
    const w=W(),c=ctx();if(a.dead || w.cine || !w.combat || !w.player || w.player.hp<=0)return;
    // brain 的缠住状态需要收到每帧，其他动作仍由同一个状态机结算。
    const blocked=motionTick(a,dt),brain=a.brain || kitOf(a).brain;
    if(a.rootT>0 && brain){brain(a,dt,c);return;}if(blocked)return;
    if(a.tele){a.tele.t+=dt;const k=kitOf(a);if(k.onWarnTick)k.onWarnTick(a,a.tele.t/a.tele.dur);if(a.tele.t>=a.tele.dur){const q=a.tele;startMove(a,q.move,{elapsed:q.elapsed});}return;}
    if(a.atk){moveTick(a,dt);if(brain)brain(a,0,c);return;}
    if(a._counter){a._counter=false;a.chainT=0;G.AI.tele(a,CFG.rushCap.counter);return;}
    if(brain && brain(a,dt,c))return;
    const t=targetOf(a);if(!alive(t))return;a.facing=t.x>a.x?1:-1;G.AI.approach(a,t,a.range || 30,dt);
    if(a.cool<=0 && tokens()<CFG.maxTokens){const id=G.AI.pickMove(a,c);if(id){G.AI.tele(a,id);a.cool=.7;}}
  }
  function updateAlly(a,dt){if(W().cine || !W().combat)return;if(motionTick(a,dt))return;if(a.atk){moveTick(a,dt);return;}const t=targetOf(a);if(!t)return;a.facing=t.x>a.x?1:-1;walkTo(a,t.x-a.facing*28,t.y,dt,a.speed);if(a.cool<=0 && Math.abs(t.x-a.x)<65){a.cool=.4;a.combo=(a.combo+1)%3;startMove(a,kitOf(a).combo[a.combo]);}if(a.energy>=100 && Math.random()<CFG.ally.specialChance*dt)background(special(a));}
  function walkTo(a,x,y,dt,speed){const dx=x-a.x,dy=y-a.y,d=Math.hypot(dx,dy);if(d<1){play(a,a.idleAnim || 'idle');return;}const step=Math.min(d,(speed || a.speed)*dt);W().move(a,dx/d*step,dy/d*step*.6);a.facing=dx<0?-1:1;play(a,'walk');}
  function tweenTo(a,x,y,dur){const x0=a.x,y0=a.y,run=G.runId;return guardedWait(Promise.race([new Promise(res=>W().anims.push({t:0,dur,fn:u=>{if(run!==G.runId)return;a.x=x0+(x-x0)*u;a.y=y0+(y-y0)*u;},res})),G.until(()=>run!==G.runId)]));}
  function ghostBurst(a,n){a.ghostOn=true;for(let i=0;i<n;i++)a.ghosts.push({x:a.x,y:a.y,z:a.z,t:a.ownT,anim:a.anim,frame:a.frameIndex?a.frameIndex():0,facing:a.facing,skin:a.skin,scale:a.scale});}
  function tokens(){return actors().filter(a=>enemySide(a)&&(a.tele || a.atk)).length;}
  function warnDur(m,c){m=getMove(m);return m.warn && m.warn.dur!=null?m.warn.dur:CFG.warnTier[c && c.spec.warnTier || 1][m.warn && m.warn.tier || 'W1'];}
  function shoot(owner,spec,o={}) {
    spec=Object.assign({},spec);const n=spec.n || 1,group={stopped:false};let first;
    for(let i=0;i<n;i++){
      const z=o.z==null ? owner && owner.stand?owner.stand.z+14:18 : o.z,base=spec.ang==null?(owner && owner.facing<0?Math.PI:0):spec.ang,ang=base+(n>1?(i/(n-1)*2-1)*(spec.spread||0)*Math.PI/180:0);
      const s=Object.assign({kind:'bullet',life:2.4,dmg:8,push:8,slot:'shot',reflect:true,hitR:[8,7,18],x:owner?owner.x:0,y:owner?owner.y:160,z,owner,side:enemySide(owner)?'enemy':'player',t:0,dead:false},spec,o,{ang,hitSet:new Set(),firstT:new Map(),nearSet:new Set(),cine:W().cine,_group:group});
      s.vx=spec.vx==null?Math.cos(ang)*(spec.speed || 160):spec.vx;s.vy=spec.vy==null?Math.sin(ang)*(spec.speed || 160):spec.vy;s._travel=0;W().shots.push(s);if(!first)first=s;
    }return first;
  }
  function updateShots(dt){
    const w=W(),tm=G.time;if(w.cine && w.cine.by!=='special-run')return;
    for(const s of w.shots){if(s.dead || w.cine && s.cine!==w.cine)continue;let d=dt*(s.side==='enemy'?w.slow:1);if(tm && tm.flowScale()===0){if(!tm.immune.has(s.owner) || s._travel>=8)continue;d=Math.min(d,Math.max(0,8-s._travel)/Math.max(1,Math.hypot(s.vx,s.vy)));s.tsHold=true;}
      const t=targetOf(s.owner || {x:s.x,y:s.y,team:s.side==='enemy'?'enemy':'player'});
      if(s.homing && t){let delta=Math.atan2(t.y-s.y,t.x-s.x)-s.ang;delta=Math.atan2(Math.sin(delta),Math.cos(delta));s.ang+=clamp(delta,-s.homing*d,s.homing*d);s.vx=Math.cos(s.ang)*(s.speed || 160);s.vy=Math.sin(s.ang)*(s.speed || 160);}
      const x0=s.x,y0=s.y;s.t+=d;
      if(s.curve){const xy=point(s.curve,clamp(s.t/(s.curveDur||1),0,1));s.x=xy[0];s.y=xy[1];s.ang=Math.atan2(s.y-y0,s.x-x0);}else{s.x+=s.vx*d;s.y+=s.vy*d;}
      s.z+=(s.vz || 0)*d;s._travel+=Math.hypot(s.x-x0,s.y-y0);s.life-=d;
      const ts=targets(s.owner || {team:s.side==='enemy'?'enemy':'player'});
      for(const t of ts){if(s.dead)break;
        if(t.team==='enemy' && s.side==='player' && !s.nearSet.has(t.uid) && (s.x-t.x)*(t.facing||1)>=0 && Math.abs(t.x-s.x)<=80 && Math.abs(t.y-s.y)<=16){s.nearSet.add(t.uid);const fn=t.onShotNear || kitOf(t).onShotNear;fn&&fn(t,s,ctx());if(s.dead)break;}
        const r=s.hitR,rx=r[0]+(t.bodyW || 6)*(t.scale || 1),ry=r[1],rz=r[2];
        // 连续弹道相交防止高速宝石一步越过较窄的本体。
        const dx=s.x-x0,dy=s.y-y0,u=clamp(((t.x-x0)*dx+(t.y-y0)*dy)/(dx*dx+dy*dy || 1),0,1),cross=Math.abs(x0+dx*u-t.x)<=rx && Math.abs(y0+dy*u-t.y)<=ry && Math.abs(s.z-(t.z || 0)-20)<=rz;
        if(!cross || (s.ground||s.fromGround) && t.z>=4 || s.hitSet.has(t.uid))continue;
        const first=!s.firstT.has(t.uid);if(first)s.firstT.set(t.uid,now());const rr=hit(s.owner,t,s,{src:s,shot:s,first});
        if(rr.parry)continue;if(rr.evade || rr.invuln)continue;s.hitSet.add(t.uid);if(rr.dmg&&s.stopAllFirst&&!s._group.stopped){s._group.stopped=true;G.hitStopAll(s.stopAllFirst);}if(rr.dmg&&s.explodeFx)fxAt('explosion',{x:s.x,y:s.y-s.z,size:s.explodeFx},s.owner,.35);s.onHit&&s.onHit(s,t,rr);if(s.splash)for(const tt of ts)if(tt!==t && Math.hypot(tt.x-t.x,(tt.y-t.y)*2)<=s.splash.r)hit(s.owner,tt,Object.assign({},s,{dmg:s.splash.dmg}));if(!s.pierce || s.hitSet.size>s.pierce)s.dead=true;
      }
      const ar=ctx()?ctx().spec.arena:[w.stage.x0,w.stage.x1];if(s.life<=0 || s.travel&&s._travel>=s.travel || s.x<ar[0]-80 || s.x>ar[1]+80)s.dead=true;
    }w.shots=w.shots.filter(s=>!s.dead);
    if(w._combatSlowT>0){w._combatSlowT-=dt;if(w._combatSlowT<=0)w.slow=1;}
  }
  function hazard(o) {const h=Object.assign({shape:'rect',warn:.5,dur:.3,delay:0,dmg:10,push:8,side:'enemy',once:true,tick:0,guard:'normal',alpha:1,t:0,phase:'warn',dead:false},o,{hitSet:new Set(),firstT:new Map(),nextHit:new Map()});if(h.follow){h.x=h.follow.x;h.y=h.follow.y;}W().hazards.push(h);return h;}
  function inHazard(h,t){if(h.shape==='ellipse')return Math.pow((t.x-h.x)/(h.rx || 10),2)+Math.pow((t.y-h.y)/(h.ry || 8),2)<=1;return t.x>=h.x0 && t.x<=h.x1 && t.y>=h.y0 && t.y<=h.y1;}
  function updateHazards(dt){const w=W();if(w.cine)return;for(const h of w.hazards){if(h.dead)continue;if(G.time && G.time.flowScale()===0 && !G.time.immune.has(h.owner))continue;h.t+=dt*(h.side==='enemy'?w.slow:1);if(h.t<h.delay)continue;const tt=h.t-h.delay;if(tt<h.warn){h.phase='warn';continue;}if(tt>=h.warn+h.dur){h.phase='done';h.dead=true;continue;}const just=h.phase!=='active';h.phase='active';if(just){snd(h.sfx,{rate:h.sfxRate});if(h.fxActive)fxAt(h.fxActive,{x:h.x==null?(h.x0+h.x1)/2:h.x,y:h.y==null?(h.y0+h.y1)/2:h.y,w:h.x1-h.x0 || h.rx*2,h:36,dur:h.dur,colour:h.colour,alpha:h.alpha!==1?h.alpha:undefined,hz:h},h.owner,h.dur);}
      for(const t of targets(h.owner || {team:h.side==='enemy'?'enemy':'player'})){if(!inHazard(h,t) || h.once && h.hitSet.has(t.uid) || now()<(h.nextHit.get(t.uid) || 0))continue;const first=!h.firstT.has(t.uid);if(first)h.firstT.set(t.uid,now());const rr=hit(h.owner,t,Object.assign({slot:'enemy'},h),{src:h,hazard:true,first,parryAllowed:just && (h.parry || h.guard==='parryOnly')});if(rr.evade || rr.invuln)continue;h.hitSet.add(t.uid);h.nextHit.set(t.uid,now()+(h.tick || .2));if(rr.dmg || rr.parry){h.onHit&&h.onHit(h,t,rr);if(h.consume)h.dead=true;}}
    }w.hazards=w.hazards.filter(h=>!h.dead);}
  function point(pts,u){if(!pts || pts.length<2)return [0,0];if(pts.length===2)return [pts[0][0]+(pts[1][0]-pts[0][0])*u,pts[0][1]+(pts[1][1]-pts[0][1])*u];const v=1-u;return [v*v*pts[0][0]+2*v*u*pts[1][0]+u*u*pts[2][0],v*v*pts[0][1]+2*v*u*pts[1][1]+u*u*pts[2][1]];}
  function beginDash(e,pts,speed,move,res){if(!pts)return;e.mem.dash={pts,t:0,dur:Math.max(f(1),Math.hypot(pts[pts.length-1][0]-pts[0][0],pts[pts.length-1][1]-pts[0][1])/speed),move,hit:new Set(),res};e.ghostOn=true;}
  function dashTick(e,dt){const d=e.mem.dash;if(!d)return;const x0=e.x,y0=e.y;d.t+=dt;const xy=point(d.pts,clamp(d.t/d.dur,0,1));e.x=xy[0];e.y=xy[1];const m=d.move;
    if(e.mem.statueLunge && Math.min(x0,e.x)<=e.mem.statueLunge.x && Math.max(x0,e.x)>=e.mem.statueLunge.x){const st=e.mem.statueLunge;e.x=st.x+e.facing*-6;e.atk=null;e.tele=null;e.mem.dash=null;e.mem.statueUsed=true;e.mem.statueLunge=null;state(e,'x_stuck');snd('clang');st.onBreak&&st.onBreak();if(st.actor){st.actor.hp=0;ko(st.actor,e);}d.res&&d.res();return;}
    for(const t of targets(e)){const dx=e.x-x0,dy=e.y-y0,u=clamp(((t.x-x0)*dx+(t.y-y0)*dy)/(dx*dx+dy*dy || 1),0,1);if(Math.hypot(t.x-(x0+dx*u),(t.y-(y0+dy*u))*1.5)>(m.dash?m.dash.w:8)+(t.bodyW || 6) || d.hit.has(t.uid))continue;d.hit.add(t.uid);hit(e,t,m,{first:true});if(!e.mem.dash)break;}
    if(d.t>=d.dur && e.mem.dash){e.mem.dash=null;e.ghostOn=false;if(m.diveAlongPath)idle(e);d.res&&d.res();}
  }
  function createC(p){
    const run=G.runId,c=ctx(),valid=()=>run===G.runId&&(!c||ctx()===c);
    return {p,ctx:c,valid,
      wait(sec){const end=now()+sec;return guardedWait(G.until(()=>!valid()||now()>=end));},
      until(fn,timeout=5){const start=now();return guardedWait(G.until(()=>!valid()||fn()||now()>=start+timeout));},
      target:range=>valid()?targets(p).filter(a=>Math.abs(a.x-p.x)<=range).sort((a,b)=>Math.abs(a.x-p.x)-Math.abs(b.x-p.x))[0]:null,
      dash:(x,y,d)=>valid()?tweenTo(p,x,y,d):Promise.resolve(),
      front:(x0,x1,depth)=>({x0:Math.min(p.x+p.facing*x0,p.x+p.facing*x1),x1:Math.max(p.x+p.facing*x0,p.x+p.facing*x1),y0:p.y-depth,y1:p.y+depth}),
      hitArea:(b,m,o)=>valid()?targets(p).filter(t=>t.x>=b.x0&&t.x<=b.x1&&t.y>=b.y0&&t.y<=b.y1).filter(t=>hit(p,t,m,o).dmg>0):[],
      shoot:(s,o)=>valid()?shoot(p,s,o):null,fx:(n,k,o)=>valid()?fxAt(n,k,p,undefined,o):null,zoom:(...a)=>valid()?G.S.zoom(...a):Promise.resolve(),
      impact:(a,s,h)=>{if(valid())Array.isArray(a)?G.post.impactSeq(a,s,h,{force:true}):G.post.impact(a,s,{force:true});},
      stopAll:s=>valid()&&G.hitStopAll(s),shake:(a,d)=>valid()&&G.shake(a,d),word:(s,a)=>valid()&&word(s,a||p),stand:(s,o)=>valid()&&p.stand&&p.stand.act(s,o),sfx:(...a)=>valid()&&snd(...a),flash:(...a)=>valid()&&G.flash(...a),
      async rush(dur,o={}){if(!valid())return;const r=Object.assign({},kitOf(p).rush,o);if(p.stand)p.stand.act('rush',{hold:true});for(let t=0;t<dur-1e-8&&valid();t+=r.tick||f(4)){if(r.dmg!==false){if(r.shot)shoot(p,Object.assign({},r.shot,{slot:'special',energy:0}));else for(const a of hitCheck(p,Object.assign({from:'body',slot:'special'},r)))hit(p,a,Object.assign({},r,{slot:'special',energy:0,stop:f(1)}));}word(r.word,p);await this.wait(r.tick||f(4));}}
    };
  }
  async function special(p){
    const c=ctx(),base=p.kit || G.KITS[p.cid] || {},k=kitOf(p),s=k.special,run=G.runId;if(!s || p._specialCd>0)return false;
    const story=s!==base.special,open=!s.window || s.window(c),use=story && open ? s : base.special;if(!use)return false;const need=use.need==null?100:use.need;
    if(p.energy<need)return false;
    if(need)p.energy=0;p._specialCd=use.cd || 1;state(p,'special');p.iframe=999;const old=W().cine;W().cine={by:p};emit('special',{who:p});
    try{if(G.uifx && G.uifx.cutin)await Promise.race([G.uifx.cutin({cid:p.cid,portrait:p.cid,title:use.title || use.name,colours:use.colours,bg:use.bg,dur:CFG.cutin}),G.until(()=>run!==G.runId)]);if(run!==G.runId)return false;W().cine={by:'special-run',owner:p};const C=createC(p);if(story && use===s)await Promise.race([use.run(G.S,p,c,C),G.until(()=>run!==G.runId||ctx()!==c)]);else await Promise.race([use.run(p,C),G.until(()=>run!==G.runId||ctx()!==c)]);return true;}
    catch(e){if(cancelled(e))return false;throw e;}
    finally {if(run===G.runId&&ctx()===c){p.iframe=Math.max(CFG.hurt.getupIframe,p.invuln || 0);if(!p.dead)idle(p);W().cine=old || null;}}
  }
  function ko(t,att){const c=ctx(),style=c&&c.spec.finish || t.koStyle;if(style==='none' && enemySide(t)){t.hp=1;emit('koBlocked',{e:t});return;}
    cancelRush(t);
    if(t.team==='object'){t.dead=true;state(t,'broken');const b=t.breakable;play(t,b&&b.anim || 'broken');if(b&&b.frames)t.frozen=b.frames[1];b&&b.onBreak&&b.onBreak(G.S,b);emit('break',{obj:t});return;}
    if(t===W().player || t.team==='ally' || t.vip){state(t,'down');play(t,'down');t.atk=null;t.tele=null;t.downT=2.2;return;}
    if(t.boss && ['ko','draw','shatter'].includes(style)){t._finishing=bossFinish(t,att,{style});background(t._finishing);return;}
    t.dead=true;t.atk=null;t.tele=null;state(t,'dead');play(t,'down');const run=G.runId,x=t.x,dir=att?Math.sign(t.x-att.x)||att.facing:1;
    W().anims.push({t:0,dur:1,fn:u=>{if(run!==G.runId)return;t.x=x+dir*35*Math.min(1,u/.6);t.z=u<.6?26*Math.sin(Math.PI*u/.6):u<.8?5*Math.sin(Math.PI*(u-.6)/.2):0;t.alpha=u>.8?1-(u-.8)/.2:1;},res:()=>{if(run!==G.runId)return;t.remove=true;t.onKo&&t.onKo(t);}});
  }
  async function bossFinish(e,att,o={style:'ko'}){
    if(e._koDone)return;e._koDone=true;e.dead=true;e.atk=null;e.tele=null;cancelRush(e);const w=W(),old=w.cine,run=G.runId,c=ctx(),valid=()=>run===G.runId&&ctx()===c,guard=async p=>{try{await Promise.race([Promise.resolve(p),G.until(()=>!valid())]);return valid();}catch(e){if(cancelled(e))return false;throw e;}};w.cine={by:'finish'};
    G.hitStopAll(f(18));G.post.impactSeq(o.style==='draw'?['invert']:['invert',att&&att.stand?({starplat:'purple',hiero:'green',magred:'red',chariot:'blue'}[att.stand.id] || 'purple'):'purple'],f(2),0,{force:true});
    if(G.S && G.S.zoom && !await guard(G.S.zoom(1.35,e,-28,.2)))return;if(!valid())return;G.flash(f(8),.5);G.slowAll(.25,.6);e.ghostOn=true;ghostBurst(e,3);play(e,'hurt');
    const x=e.x,dir=att?att.facing:1;const flight=new Promise(res=>w.anims.push({t:0,dur:.6,fn:u=>{if(valid()){e.x=x+dir*35*u;e.z=24*Math.sin(Math.PI*u);}},res}));
    if(!await guard(Promise.all([flight,att?createC(att).rush(.6,{dmg:false}):Promise.resolve()])))return;e.ghostOn=false;
    if(e.stand && e.stand.visible){fxAt(o.style==='draw'?'stand_out':'shatter',{cid:e.stand.id,x:e.stand.x,y:e.stand.y-e.stand.z,pieces:30,dur:o.style==='draw'?.25:.9},e,.9);e.stand.hide();}else if(o.style==='shatter')fxAt('shatter',{cid:e.cid,x:e.x,y:e.y-e.z,pieces:18,dur:.7},e,.7);
    e.z=0;play(e,'down');if(G.fx)G.fx.dustAt(e.x,e.y,0,8);snd('thud');snd('ko_hit');if(!await guard(G.uifx && G.uifx.title?G.uifx.title(o.style==='draw'?'draw':'saiki',{x:320,y:230,pop:.12,dur:1.2}):G.wait(1.2,'ui')))return;snd('jingle_victory');if(G.S && G.S.zoom && !await guard(G.S.zoom(1,null,null,.2)))return;if(!valid())return;w.zoom=null;w.cine=old || null;e.onKo&&e.onKo(e);
  }
  function drawPixel(P,layer){if(layer!=='mid' || W().insert)return;const w=W(),cx=G.cam.x || 0,cy=G.cam.y || 0,px=G.px;
    for(const h of w.hazards)if(!h.hidden && h.phase==='warn'){const a=Math.floor(now()*16)%2?.7:.35;if(h.shape==='ellipse'){for(let i=0;i<24;i++){const t=i*Math.PI/12,t2=(i+1)*Math.PI/12;px.line(P,h.x-cx+Math.cos(t)*h.rx,h.y-cy+Math.sin(t)*h.ry,h.x-cx+Math.cos(t2)*h.rx,h.y-cy+Math.sin(t2)*h.ry,'#ff3030',a);}}else {px.line(P,h.x0-cx,h.y0-cy,h.x1-cx,h.y0-cy,'#ff3030',a);px.line(P,h.x0-cx,h.y1-cy,h.x1-cx,h.y1-cy,'#ff3030',a);}}
    for(const a of actors())if(a.tele && a.tele.tier==='W4' && a.tele.path){const p=a.tele.path;let last=point(p,0);for(let i=1;i<=24;i++){const next=point(p,i/24);if(i%2)px.line(P,last[0]-cx,last[1]-cy,next[0]-cx,next[1]-cy,'#ff4040',.8);last=next;}}
    for(const s of w.shots){if(s.kind==='img')continue;const x=s.x-cx,y=s.y-s.z-cy;if(s.draw){s.draw(P,x,y,s);continue;}if(s.kind==='gem')px.poly(P,[[x,y-4],[x+3,y],[x,y+4],[x-3,y]],s.colour || '#50ff9a');else {px.rect(P,x-(s.r || 3),y-(s.r || 3),(s.r || 3)*2,(s.r || 3)*2,s.kind==='ankh'?'#ffb020':s.colour || '#ff6030',1);px.line(P,x,y,x-s.vx*.018,y-s.vy*.018,'#ffe080',.5,2);}}
    if(G.J25 && G.J25.drawPixel)G.J25.drawPixel(P,layer);
  }
  function drawShot(g,s,cx,cy){if(s.image && typeof s.image==='object'){const a=G.atlas(s.image.cid);a.draw(g,s.image.logical || s.anim || 'idle',Math.floor(s.t*12),s.x-cx,s.y-s.z-cy,{flip:s.vx<0});}else {const im=G.image(s.image);if(im)g.drawImage(im,s.x-cx-im.width/2,s.y-s.z-cy-im.height/2);}}
  G.combat={CFG,updatePlayer,updateAlly,updateEnemy,updateShots,updateHazards,drawPixel,drawShot,startMove,hitCheck,hit,ko,shoot,hazard,gainEnergy,special,bossFinish,kitOf,resetActor,warnDur,fxAt,tweenTo,tokens,walkTo,ghostBurst,createC};
  G.AI={dist:(e,t)=>Math.hypot(e.x-t.x,e.y-t.y),aligned:(e,t,dy=6)=>Math.abs(e.y-t.y)<=dy,approach:(e,t,keep,dt)=>{if(Math.abs(t.x-e.x)>keep)walkTo(e,t.x-Math.sign(t.x-e.x)*keep,t.y,dt,e.speed);},kite:(e,t,keep,dt)=>walkTo(e,t.x-Math.sign(t.x-e.x)*keep,t.y,dt,e.speed),
    pickMove(e,c){const t=targetOf(e);if(!t)return null;if(e.pattern)return this.next(e);const ids=(e.moves || []).filter(id=>{const m=getMove(id);return m && !(e.moveCd[id]>0) && (!m.range || Math.abs(e.x-t.x)>=m.range[0] && Math.abs(e.x-t.x)<=m.range[1]) && (!m.cond || m.cond(e,t,c));});let n=ids.reduce((s,id)=>s+(getMove(id).weight==null?1:getMove(id).weight),0)*Math.random();return ids.find(id=>(n-=getMove(id).weight==null?1:getMove(id).weight)<=0) || null;},
    next(e){if(!e.pattern || !e.pattern.length)return null;return e.pattern[e.patternI++%e.pattern.length];},
    tele(e,id,o={}){if(!getMove(id))return null;const m=normMove(id),t=o.target || targetOf(e),d=Math.max(f(1),warnDur(m,ctx())-(e.mem.startupMinus || 0));if(t)e.facing=t.x>e.x?1:-1;let path=m.warn&&m.warn.path?m.warn.path(e,ctx()):null;if(!path && m.warn && m.warn.tier==='W4')path=[[e.x,e.y],[e.x+e.facing*(m.dash?m.dash.dist:160),t?t.y:e.y]];e._telePath=path;e.tele={move:id,t:0,dur:d,tier:m.warn&&m.warn.tier || 'W1',target:t,path,elapsed:Math.min(m.active[0],m.warn&&m.warn.dur!=null?m.warn.dur:m.active[0])};state(e,'windup');play(e,m.body || 'cmd');e.moveCd[id]=m.cd || 0;
      const tier=e.tele.tier;if(tier==='W1'||tier==='W2')e.emote={text:tier==='W1'?'!':'!!',t:d};if(tier==='W5'){e.outline='#c040ff';if(m.guard!=='parryOnly')m.guard='none';snd('menacing');}if(tier==='W6' && G.uifx)background(G.uifx.cutin({enemy:true,portrait:m.warn.portrait || e.cid,title:m.warn.title,dur:.6}));if(m.hazard && m.hazardAt===0){makeMoveHazards(e,m);e._preHazard=true;}return e.tele;},
    use:(e,id,o)=>o && o.skipWarn===false?G.AI.tele(e,id):startMove(e,id),threat:(e,p)=>p.atk && hitCheck(p,p.atk,e)?Math.max(0,p.atk.active[0]-p.atkT):-1,
    dash:(e,pts,speed,o={})=>new Promise(res=>beginDash(e,pts,speed,normMove(o.move || {dmg:0}),res)),blink(e,x,y,o={}){ghostBurst(e,3);e.x=x;e.y=y;fxAt('glint',{x,y:y-20,size:10},e,.2);word(o.word,e);},hide:(e,on,o={})=>{e.untargetable=on;e.hidden=on;e.alpha=on?o.alpha || 0:1;},summon:(spec,o)=>ctx() && ctx().spawn(Object.assign({},spec,o)),hazard,shoot,
    cut(e,s){if(!s.cuttable || s.fromGround || s.dead)return false;s.dead=true;fxAt('slash_arc',{x:s.x,y:s.y-s.z,size:16},e,.3);fxAt('fire_chunks',{x:s.x,y:s.y-s.z,n:12},e,.3);word('被劈开了！',e);snd('slash');return true;},
    clones(e,n,o={}){const cs=[];for(let i=0;i<n;i++){const a=new G.Actor(e.cid,e.x+(i?1:-1)*16,e.y+(i?1:-1)*5,{team:'enemy',kit:e.kit,boss:false,hp:e.maxHp,speed:e.speed,stand:e.standId,dmgOut:o.dmgMul || .5,shadow:false,alpha:.5});a.moves=e.moves;a.brain=()=>false;a.dmgMul=()=>0;a.onHitBy=()=>{word(o.word || '残像！',a);return 'evade';};a._cloneOf=e;W().stage.actors.push(a);cs.push(a);}return cs;}
  };
})();
