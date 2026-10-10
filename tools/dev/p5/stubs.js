// 包 5 隔离验收仅替换声音和交互演出，时钟、输入、角色、替身、特效与战斗全部使用生产实现。
'use strict';
(function(){const G=window.G;G.dbg.hold=true;const log=[];
G.audio={unlocked:true,unlock(){},update(){},sfx(n){log.push(['sfx',n]);},music(n){log.push(['music',n]);},loop(n){log.push(['loop',n]);return{stop(){log.push(['stop',n]);},setRate(){}};},voice(){},cue(n){log.push(['cue',n]);return{hitIn:n==='time_resume'?1.02:0};},duck(){},timeStop(v){log.push(['timeStop',v]);}};
G.ui={hints:[],menuCalls:[],choices:[],hint(t){this.hints.push(t);},blocking(){return false;},notice(o){log.push(['notice',o.text]);return G.wait(o.minT||.1,'ui');},openMenu(t,opts){this.menuCalls.push(opts);return Promise.resolve(this.choices.length?this.choices.shift():1);}};
G.uifx={sfx(){},menacing(){},cutin(){return G.wait(.05,'ui');},title(n){log.push(['title',n]);return G.wait(.08,'ui');},vs(o){log.push(['vs',o]);return G.wait(.05,'ui');},vsTag(){}};
G.hud={on:false,reset(){this.steps=null;this.boss=null;this.timer=null;this.gauge=null;this.on=false;},flashEnergy(){},comboHit(){}};
G.S={busy:false,actor(id){return G.world.stage.actors.find(a=>a.id===id||a.cid===id);},zoom(){return G.wait(.03,'ui');}};G.__audioLog=log;
})();
