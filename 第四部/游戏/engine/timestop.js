// 三个阶段共享同一条时停时间轴，避免恢复音效、画面和排队伤害各自漂移。
'use strict';
(function () {
  const G=window.G, resumeLead=1.02;
  let resolveStop=null, generation=0, phaseLength=0, resumeAt=Infinity, cuePlayed=false, forceResume=false, tickAt=1, queued=[], queueT=0;
  function cue(name,o){const a=G.audio;return a&&a.cue?a.cue(name,o):{hitIn:0};}
  // 台词大字是 G.runPromise：这里不等它，回标题 / 换章取消时要有人接住拒绝，否则是 Uncaught (in promise) RunCancelled。
  function title(key){const p=G.uifx&&G.uifx.title?G.uifx.title(key):null;if(p&&p.catch)p.catch(G.cancelIgnore);}
  function change(phase,dur){T.phase=phase;T.t=0;phaseLength=dur;
    if(phase==='burst'){
      const p=G.world.player;if(p)p.tsGuard=G.input.isDown('guard');
      G.audio.timeStop(true,T.o);if(T.o.lines&&T.o.lines.start)title(T.o.lines.start);
    }
    if(phase==='stopped'){tickAt=.4;if(forceResume){phaseLength=resumeLead;forceResume=false;}if(phaseLength<=resumeLead)resumeCue();}
    if(phase==='resume'&&T.o.lines&&T.o.lines.end)title(T.o.lines.end);
  }
  function resumeCue(){if(cuePlayed)return;cuePlayed=true;cue('time_resume');resumeAt=T.t+resumeLead;}
  function flush(){
    for(const [target,list] of T.queue){const push=list.reduce((sum,q)=>sum+(q.move.push||0),0);list.forEach((q,i)=>queued.push({target,att:q.att,move:Object.assign({},q.move,{push:i===list.length-1?push:0})}));}
    T.queue.clear();queueT=0;T.active=false;T.phase=null;G.audio.timeStop(false);G.dbg.ev('timestop',{by:T.by&&T.by.cid,queued:queued.length});
    if(!queued.length)finish();
  }
  function finish(){T.immune.clear();T.by=null;T.o=null;if(G.world.player)G.world.player.tsGuard=false;const r=resolveStop;resolveStop=null;if(r)r();}
  const T=G.time={active:false,phase:null,by:null,t:0,o:null,immune:new Set(),queue:new Map(),
    stop(by,o={}){
      this.clear();generation=G.runId;this.active=true;this.by=by;this.o=Object.assign({dur:2,burst:.6,resume:.36,tint:'yellow',prewarn:true,sfx:'timestop',music:'tape',ticks:true,words:true},o);
      this.o.dur=Math.max(resumeLead,this.o.dur);this.immune=new Set(o.immune||[by]);cuePlayed=false;forceResume=false;resumeAt=Infinity;
      const promise=new Promise(r=>{resolveStop=r;});
      if(this.o.prewarn){const h=cue(this.o.sfx);change('warn',h.hitIn|| (this.o.sfx==='timestop_sp'?.924:.85));}else change('burst',this.o.burst);
      return promise;
    },
    resume(){if(!this.active)return;if(this.phase==='warn')change('burst',this.o.burst);if(this.phase==='burst'){forceResume=true;}else if(this.phase==='stopped'){resumeCue();phaseLength=resumeAt;}},
    isFrozen(a){return this.active&&(this.phase==='burst'||this.phase==='stopped')&&!this.immune.has(a);},
    flowScale(){return this.active&&(this.phase==='burst'||this.phase==='stopped')?0:1;},
    overActive(){return this.active&&this.phase!=='warn'&&this.immune.size>0;},
    visual(){if(!this.active||this.phase==='warn')return null;const o=this.o,by=this.by||{x:160,y:100,z:0},p=G.cam.w2s(o.cx==null?by.x:o.cx,o.cy==null?by.y-(by.z||0)-24:o.cy);return {phase:this.phase,u:Math.min(1,this.t/Math.max(.001,phaseLength)),cx:p.x,cy:p.y,tint:o.tint,dur:o.burst,resumeDur:o.resume};},
    queueHit(t,att,move){if(!this.queue.has(t))this.queue.set(t,[]);this.queue.get(t).push({att,move:Object.assign({},move)});},
    update(dt){
      if((this.active||queued.length)&&G.runId!==generation){this.clear();return;}
      if(queued.length){queueT-=dt;while(queueT<=0&&queued.length){const q=queued.shift();if(!q.target.remove)G.combat.hit(q.att,q.target,q.move,{queued:true});queueT+=.03;}if(!queued.length)finish();}
      if(!this.active)return;
      // 首次觉醒让玩家在静止画面完成输入，释放后才计算真正能行动的时停秒数。
      if(this.phase==='stopped'&&this.o.holdWhile&&this.o.holdWhile())return;
      this.t+=dt;
      if(this.o.grant&&this.phase==='stopped'&&this.t>this.o.grant.sec)this.immune.delete(this.o.grant.actor);
      if(this.phase==='stopped'){
        if(!cuePlayed&&this.t>=phaseLength-resumeLead)resumeCue();
        if(this.o.ticks&&this.t+1e-9>=tickAt){const tick=Math.round(tickAt/.4);tickAt+=.4;G.audio.sfx('clock_tick');if(this.o.words)G.uifx.sfx(tick%2?'チク…':'タク…',this.by);}
      }
      if(this.t+1e-9<phaseLength)return;
      if(this.phase==='warn')change('burst',this.o.burst);
      else if(this.phase==='burst'){if(this.o.grant)this.immune.add(this.o.grant.actor);change('stopped',this.o.dur);}
      else if(this.phase==='stopped')change('resume',this.o.resume);
      else flush();
    },
    clear(){this.active=false;this.phase=null;this.t=0;this.queue.clear();queued=[];this.immune.clear();G.audio&&G.audio.timeStop&&G.audio.timeStop(false);finish();}
  };
})();
