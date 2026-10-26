// 战斗上下文持有尝试和检查点，Boss 保留对象身份，让剧情机关与重试引用一致。
'use strict';
(function () {
  const G=window.G, W=G.world, S=G.S;
  const alive=a=>a&&!a.remove&&!a.dead&&a.hp>0;
  function actor(id){return typeof id==='object'?id:S.actor(id);}
  const names=a=>(G.D.heroes&&G.D.heroes[a.cid]&&G.D.heroes[a.cid].name)||a.name||a.cid;
  S.fight=async function fight(raw){
    const spec=Object.assign({arena:[W.stage.x0,W.stage.x1],waves:[],energy:{start:0},playerMinHp:0,warnTier:1,dmgScale:1,coverage:true},raw);
    if(!spec.id)throw new Error('战斗必须有 id');
    spec.losable=spec.losable==null?spec.playerMinHp===0:spec.losable;
    spec.kitOverride=Object.assign({},spec.kitOverride);
    if(spec.onSpecial)spec.kitOverride[spec.lead]=Object.assign({},spec.kitOverride[spec.lead],{special:{need:100,run:spec.onSpecial}});
    const run=G.runId, active=()=>run===G.runId&&W.fight===c;
    const guard=async p=>{try{await Promise.race([Promise.resolve(p),G.until(()=>!active())]);return active();}catch(e){if(G.cancelled(e))return false;throw e;}};
    const members=(G.party.members||[]).slice();
    const stateKeys=['team','visible','follow','followSlot','minHp','speed','dmgOut','dmgIn','scale','alpha','z','frozen','hold','untargetable','hidden','controlReverseUntil','x','y'];
    const capture=a=>({a,values:Object.fromEntries(stateKeys.map(k=>[k,a[k]]))});
    const saved=members.map(capture);
    const previous={combat:W.combat,free:W.free,x0:W.stage.x0,x1:W.stage.x1,locked:G.party.locked};
    const managed=[],listeners=new Map(),defaults=new Map();let attempt=0,assist=false,assistLevel=0,outcome=null,checkpoint=null,phaseBusy=false,storyWas=false;
    let eventDone=new Set(),hazardTicks=[],reinforceT=0,reinforceN=0;
    const c={spec,id:spec.id,attempt,assist,assistLevel:0,wave:0,swap:!!spec.swap,lockMsg:spec.lockMsg,storyU:false,data:{},
      get t(){return W.fightT;},get player(){return W.player;},get boss(){return this.enemies().find(a=>a.boss)||null;},
      enemies(){return W.stage.actors.filter(a=>a.team==='enemy'&&!a.remove&&(managed.includes(a)||managed.includes(a._cloneOf)));},allies(){return W.stage.actors.filter(a=>a===W.player||a.team==='ally'||a.vip);},objects(){return W.stage.actors.filter(a=>a.team==='object'&&!a.remove);},
      gauge:null,hazard:o=>G.combat.hazard(o),shoot:(owner,shot,o)=>G.combat.shoot(owner,shot,o),
      spawn(e){
        const cid=e.cid||e.actor||e.id, k=typeof e.kit==='string'?G.KITS[e.kit]:e.kit;
        const x=e.x==null?(e.side==='left'?spec.arena[0]+20:spec.arena[1]-24):e.x,y=e.y==null?W.player.y:e.y;
        let a=e._obj;if(!a){a=e._obj=(e.actor&&actor(e.actor))||new G.Actor(cid,x,y,Object.assign({},e,{kit:k,team:e.team||'enemy'}));
          if(k){a.kit=k;a.moves=k.moves||[];a.brain=k.brain||null;}for(const key of ['boss','name','poiseMax','speed','bodyW','fly','pivotMode','onHitBy','dmgMul','armor','koStyle','brain'])if(e[key]!=null)a[key]=e[key];if(e.pivot)a.pivotMode=e.pivot;
          a.team=e.team||'enemy';if(e.hp!=null)a.maxHp=e.hp;defaults.set(a,{speed:a.speed,minHp:a.minHp,skin:a.skin,koStyle:a.koStyle,dmgIn:a.dmgIn,dmgOut:a.dmgOut,hold:a.hold,frozen:a.frozen,alpha:a.alpha});}
        if(!W.stage.actors.includes(a))W.stage.actors.push(a);if(!managed.includes(a))managed.push(a);
        const def=defaults.get(a);G.combat.resetActor(a);if(def)Object.assign(a,def);a.x=x;a.y=y;a.z=e.z||0;a.hold=e.hold==null?a.hold:!!e.hold;a.visible=true;a.untargetable=!!e.untargetable;a.phaseI=0;a.patternI=0;a.moveCd={};a.cool=.6;a._koDone=false;a._finishing=null;a._phaseDone=new Set();a._enemySpec=e;a.phases=e.phases||[];
        if(spec.finish)a.koStyle=spec.finish;if(e.minHp!=null)a.minHp=e.minHp;if(a.stand)a.stand.summon({instant:true});return a;
      },
      setLead(cid){return G.party.setLeader(cid,{force:true,silent:true});},fillEnergy(a){G.combat.gainEnergy(actor(a||W.player),100,'story');},
      step(i){if(G.hud.steps)G.hud.steps.done=Math.max(G.hud.steps.done||0,i);this.emit('step',{i});},
      on(type,fn){if(!listeners.has(type))listeners.set(type,new Set());listeners.get(type).add(fn);return ()=>listeners.get(type)&&listeners.get(type).delete(fn);},
      emit(type,data){for(const fn of listeners.get(type)||[])fn(data,this);},
      end(){outcome='win';},fail(text){this.failText=text;outcome='lose';}
    };
    W.fight=c;W.combat=false;W.free=false;W.stage.x0=spec.arena[0];W.stage.x1=spec.arena[1];G.party.locked=!spec.swap;
    if(spec.lead)c.setLead(spec.lead);
    if(!saved.some(s=>s.a===W.player))saved.push(capture(W.player));
    const initialPlayer=W.player;
    if(spec.music!==null)G.audio.music(spec.music||'battle',.5);
    G.dbg.resetCounts();
    function prepareParty(){
      // 重试从同一位置和属性开始，机关设置的停步、缩小和磁化不能跨尝试遗留。
      for(const s of saved)Object.assign(s.a,s.values);
      if(spec.lead)c.setLead(spec.lead);
      if(!members.includes(initialPlayer)){W.player=initialPlayer;G.combat.resetActor(initialPlayer);Object.assign(initialPlayer,saved.find(s=>s.a===initialPlayer).values);initialPlayer.energy=spec.energy.start||0;initialPlayer.minHp=spec.playerMinHp;}
      const allied=new Set(spec.allies||[]),bench=typeof spec.bench==='object'?spec.bench:{mode:spec.bench||'stay'};
      for(const a of members){a.follow=null;a.team=a===W.player?'player':allied.has(a.cid)?'ally':'npc';a.visible=a.team!=='npc'||bench.mode!=='hide';const at=bench.at&&bench.at[a.cid];if(at){a.x=at[0];a.y=at[1];}if(a.team!=='npc'){G.combat.resetActor(a);a.energy=spec.energy.start||0;a.minHp=a===W.player?spec.playerMinHp:0;if(a.stand)a.stand.summon({instant:true});}}
      for(const id of [spec.vip,...(spec.vips||[])].filter(Boolean)){const v=actor(id);if(v){v.vip=true;v.team='npc';v.hp=spec.vipHp||v.maxHp;v.dead=false;v.remove=false;v.state='idle';}}
    }
    function setupHud(){G.hud.reset();G.hud.on=true;if(spec.steps)G.hud.steps=Object.assign({done:0},spec.steps);if(spec.timer||spec.survive){const timer=spec.timer||{};G.hud.timer={label:timer.label||'坚持',until:timer.until||spec.survive,t:0,left:timer.until||spec.survive};}if(spec.gauge){const q=Object.assign({max:100},spec.gauge);q.value=q.value==null?q.max:q.value;q.add=n=>{q.value=G.clamp(q.value+n,0,q.max);};c.gauge=q;G.hud.gauge=q;}}
    function resetAttempt(){
      listeners.clear();outcome=null;c.attempt=attempt;c.assist=assist;c.assistLevel=assistLevel;c.storyU=false;storyWas=false;eventDone=new Set();hazardTicks=(spec.hazards||[]).map(()=>0);reinforceT=0;reinforceN=0;phaseBusy=false;c.data={};
      W.fightT=0;W.shots=[];W.hazards=[];W.slow=1;W.cine=null;G.time.clear();G.fx.killTag('fight');for(const a of managed){a.remove=true;if(a.stand)a.stand.hide();}prepareParty();setupHud();
      if(checkpoint){W.player.x=checkpoint.px;W.player.y=checkpoint.py;W.player.energy=checkpoint.energy;}
      // 战斗评价（story\extras.js）：每次尝试重新统计受伤 / 精准格挡 / 看穿 / 连打，只算打赢的那一次
      if(G.EXTRA&&G.EXTRA.track)G.EXTRA.track(c);
    }
    async function paused(fn,by){
      if(!active())return;const old=W.cine;W.cine={by:by||'fight-event'};
      try{await guard(fn());}finally{if(active())W.cine=old||null;}
    }
    async function phase(e,i,q){
      if(phaseBusy||!active())return;phaseBusy=true;e._phaseDone.add(i);e.atk=null;e.tele=null;e.mem.dash=null;e.state='idle';e.stateT=0;e.iframe=999;
      try{await paused(async()=>{G.post.impact('invert',2/60,{force:true});if(q.run)await guard(q.run(S,e,c));if(!active())return;Object.assign(e,q.set||{});e.phaseI=i+1;c.emit('phase',{e,index:e.phaseI,boss:e,i:e.phaseI});if(spec.onPhase)await guard(spec.onPhase(S,e,e.phaseI,attempt,c));},'phase');
        if(active()&&spec.checkpoint&&q.checkpoint)checkpoint={wave:c.wave,boss:e,i,hp:q.at==null?e.hp:e.maxHp*q.at,energy:W.player.energy,px:W.player.x,py:W.player.y};
      }finally{if(active())e.iframe=0;phaseBusy=false;}
    }
    const tick=dt=>{
      if(!active())return true;if(!W.combat||W.cine||phaseBusy||outcome)return false;
      if(spec.tick)spec.tick(c,dt);
      if(W.player.hp<=0&&spec.losable||spec.vip&&actor(spec.vip)&&actor(spec.vip).hp<=0||spec.failWhen&&spec.failWhen(c)){c.fail();return false;}
      if(spec.endWhen&&spec.endWhen(c)||spec.survive&&c.t>=spec.survive){c.end();return false;}
      if(G.hud.timer){G.hud.timer.t=c.t;G.hud.timer.left=Math.max(0,G.hud.timer.until-c.t);}
      if(c.gauge){const q=c.gauge,old=q.value;q.add((q.rate?q.rate(c):0)*dt);if(q.value<=0&&old>0){if(q.onEmpty==='lose')c.fail();else if(typeof q.onEmpty==='function')q.onEmpty(c);}if(q.value>=q.max&&old<q.max&&q.onFull)q.onFull(c);}
      const special=G.combat.kitOf(W.player).special,story=spec.kitOverride[W.player.cid]&&spec.kitOverride[W.player.cid].special;
      c.storyU=!!(story&&(!special.window||special.window(c)));if(c.storyU&&!storyWas){G.ui.hint(story.prompt||'按 U！');G.uifx.sfx('U!',W.player);}storyWas=c.storyU;
      for(let i=0;i<(spec.events||[]).length;i++){const e=spec.events[i];if(!eventDone.has(i)&&e.when(c.t,c)){eventDone.add(i);paused(()=>e.run(S,c.enemies(),attempt,c)).catch(G.cancelIgnore);break;}}
      for(const e of c.enemies())if(alive(e))for(let i=0;i<(e.phases||[]).length;i++){const q=e.phases[i];if(!e._phaseDone.has(i)&&(q.when?q.when(e,c):e.hp/e.maxHp<=q.at)){phase(e,i,q).catch(G.cancelIgnore);return false;}}
      (spec.hazards||[]).forEach((q,i)=>{hazardTicks[i]+=dt;if(hazardTicks[i]>=q.every){hazardTicks[i]-=q.every;const h=q.make(c,Math.floor(c.t/q.every));if(h)c.hazard(h);}});
      if(spec.reinforce){const r=spec.reinforce;reinforceT+=dt;if(reinforceT>=r.every&&c.enemies().filter(alive).length<(r.max||5)){reinforceT=0;const e=r.make(reinforceN++,c);if(e)c.spawn(e);}}
      G.hud.boss=c.boss;return false;
    };
    W.ticks.push(tick);
    async function failed(){
      // 星尘试炼（story\trial.js）失败有自己的结算（重新开始 / 重新编队 / 回标题），不弹这里的再来一次菜单
      if(G.TRIAL&&G.TRIAL.active)return false;
      W.combat=false;W.cine={by:'failure'};G.slowAll(.3,.5);await guard(G.wait(.5,'ui'));if(!active())return false;
      W.player.state='down';W.player.play('down');G.post.filter('sepia',1,{dur:.6});G.audio.cue('game_over_jingle');
      if(G.ui.notice)await guard(G.ui.notice({text:c.failText||names(W.player)+'倒下了……',minT:1.2,auto:true}));else await guard(G.wait(1.2,'ui'));if(!active())return false;
      // 放水项是否需要广告只在开菜单前问一次：supported 最长 3 秒且可能抛异常，出错一律按“没有广告”免费放水，
      // 本地包 / 公开包 / 不在 233 乐园时不能被这一步卡住。
      let ad=false;
      if(attempt+1>=G.combat.CFG.assistAfter&&G.ads&&typeof G.ads.supported==='function'){
        try{ad=await G.ads.supported();}catch(e){ad=false;}
        if(!active())return false;
      }
      // 玩家关掉广告后要回到同一张菜单重选，所以“开菜单 → 处理选择”放进循环；广告播放期间只等 watch，不做别的事。
      for(;;){
        const opts=['再来一次','回到标题'];if(attempt+1>=G.combat.CFG.assistAfter)opts.push(ad?'看广告·放水再来':'放水再来');
        let choice=1;try{choice=await Promise.race([G.ui.openMenu(null,opts),G.until(()=>!active()).then(()=>1)]);}catch(e){if(!G.cancelled(e))throw e;}
        if(!active()||choice===1)return false;
        if(choice===2){
          if(ad){
            let r;try{r=await G.ads.watch('assist');}catch(e){r={success:false,reason:'exception',technical:true};}
            if(!active())return false;
            if(r&&r.success){assist=true;assistLevel++;}
            else if(r&&r.technical){
              // 技术原因播不出来不能让玩家吃亏：照样放水，并明确告诉他这次是免费的。
              assist=true;assistLevel++;
              if(G.ui.notice)await guard(G.ui.notice({text:'广告暂时无法播放，本次免费放水',minT:1.2,auto:true}));
              if(!active())return false;
            }else{
              // 玩家自己关掉 / 跳过：不放水，回到循环重新选；重开菜单前先把提示放完，免得菜单把 notice 盖住。
              if(G.ui.notice)await guard(G.ui.notice({text:'广告没有看完，没有放水',minT:1.2,auto:true}));
              if(!active())return false;
              continue;
            }
          }else{assist=true;assistLevel++;}
        }
        attempt++;G.post.filter('sepia',null);W.cine=null;return true;
      }
    }
    let result='ended';
    try{
      while(active()){
        resetAttempt();if(attempt&&spec.onRetry)await paused(()=>spec.onRetry(S,attempt,c));if(!active())break;
        if(!attempt&&spec.vs)await paused(()=>G.uifx.vs({key:spec.vs,hero:W.player.cid,enemy:spec.waves[0]&&spec.waves[0][0]&&(spec.waves[0][0].cid||spec.waves[0][0].actor),attempt:0}));if(!active())break;if(spec.vs)G.uifx.vsTag(spec.vs);
        let lost=false,autowinArmed=false;
        for(let wi=checkpoint?checkpoint.wave:0;wi<spec.waves.length&&active();wi++){
          c.wave=wi;W.combat=false;const spawned=spec.waves[wi].map(e=>c.spawn(e));
          if(checkpoint&&wi===checkpoint.wave){const e=checkpoint.boss;e.hp=checkpoint.hp;e.phaseI=checkpoint.i+1;for(let i=0;i<=checkpoint.i;i++){e._phaseDone.add(i);Object.assign(e,e.phases[i].set||{});} }
          if(spec.onWave)await paused(()=>spec.onWave(S,wi,spawned,attempt,c));if(!active())break;W.combat=true;G.hud.boss=c.boss;
          // 仅 ?autotest=1 的调试开关，不是通关证据：指定战斗开场 1 秒后判胜，让测试跳过战斗直达后面的剧情。
          // 放在第一波生成并开打之后，c.end() 会走本场战斗真正的 after 收尾；每次尝试只挂一次，多波战斗不会重复排计时。
          if(!autowinArmed && G.dbg && G.dbg.autowin && G.dbg.autowin.has(spec.id)){
            autowinArmed=true;
            // 记一笔：E.won 据此不发 fight_won，免得测试判胜也刷成就
            c.autowin=true;
            G.defer(1.0, () => { if (active() && outcome == null) c.end(); });
          }
          await guard(G.until(()=>outcome||(!phaseBusy&&!W.cine&&!c.enemies().some(alive))));if(!active())break;
          if(outcome==='lose'){lost=true;break;}if(outcome==='win')break;
        }
        if(!active())break;
        if(!spec.waves.length){W.combat=true;await guard(G.until(()=>outcome));if(!active())break;lost=outcome==='lose';}
        if(lost){if(await failed())continue;break;}
        const finishes=c.enemies().map(e=>e._finishing).filter(Boolean);if(finishes.length)await guard(Promise.all(finishes));if(!active())break;
        result='win';if(G.EXTRA&&G.EXTRA.won)G.EXTRA.won(c,attempt,assist);if(typeof spec.after==='function')await guard(spec.after(S,c.enemies(),attempt,c));else if(spec.after)G.audio.music(spec.after,.5);break;
      }
    }finally{
      if(active()){
        W.combat=false;W.free=previous.free;W.cine=null;W.stage.x0=previous.x0;W.stage.x1=previous.x1;W.shots=[];W.hazards=[];W.slow=1;G.time.clear();
        for(const a of managed){if(a.stand)a.stand.recall({instant:true});if(a.mem&&a.mem.buzz&&a.mem.buzz.stop)a.mem.buzz.stop(.05);}
        for(const a of managed)if(a.team==='object'||a.team==='npc')a.remove=true;
        for(const s of saved){for(const k of stateKeys)if(k!=='x'&&k!=='y')s.a[k]=s.values[k];s.a.team=s.a===W.player?'player':s.values.team;if(s.a.stand)s.a.stand.recall();}
        G.party.locked=previous.locked;if(G.party.rebuildFollow)G.party.rebuildFollow();G.uifx.vsTag(null);G.input.lockOk(.8);G.hud.reset();G.ui.hints=[];W.fight=null;G.post.filter('sepia',null);
      }
      listeners.clear();const i=W.ticks.indexOf(tick);if(i>=0)W.ticks.splice(i,1);
    }
    // 试炼里失败不换场景（TRIAL.play 接住 TrialFailed 自己弹结算），普通战斗照旧回标题
    if(result!=='win'){
      if(G.TRIAL&&G.TRIAL.active){const e=new Error('试炼失败');e.name='TrialFailed';throw e;}
      if(run===G.runId&&G.goTitle)await G.goTitle();const e=new Error('战斗已经取消，剧情不能继续');e.name='RunCancelled';throw e;
    }
    return {result,attempts:attempt+1};
  };
})();
