// 用固定步长核验听觉节拍和冻结边界，避免浏览器帧抖动掩盖计时错误。
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const events = [], words = [], player = { cid: 'jotaro' }, boss = { cid: 'dio' };
const G = { runId: 1, world: { player }, input: { isDown: () => false },
  audio: { cue: name => { events.push({ name, phase: G.time?.phase, t: G.time?.t }); return { hitIn: .85 }; },
    sfx: name => events.push({ name, phase: G.time.phase, t: G.time.t }), timeStop: () => {} },
  uifx: { title: () => {}, sfx: text => words.push(text) }, dbg: { ev: () => {} },
  cam: { w2s: (x,y) => ({x,y}) }, combat: { hit: () => {} } };
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../../engine/timestop.js'), 'utf8'), { window: { G } });
const T = G.time;
T.stop(boss, { prewarn: false, burst: .6, dur: 3.2, resume: .36, ticks: true, words: true, grant: { actor: player, sec: .5 } });
let sawGrant = false, sawFrozen = false;
for (let i = 0; i < 400 && T.active; i++) {
  T.update(1/60);
  if (T.phase === 'stopped' && T.t > .01 && T.t < .49) { assert.equal(T.isFrozen(player), false); sawGrant = true; }
  if (T.phase === 'stopped' && T.t > .52) { assert.equal(T.isFrozen(player), true); sawFrozen = true; }
}
const ticks = events.filter(e => e.name === 'clock_tick');
assert.equal(ticks.length, 8);
ticks.forEach((e,i) => { assert.equal(e.phase, 'stopped'); assert.ok(Math.abs(e.t-(i+1)*.4)<1e-8); });
assert.deepEqual(words, ['チク…','タク…','チク…','タク…','チク…','タク…','チク…','タク…']);
assert.ok(sawGrant && sawFrozen);
assert.equal(events.filter(e => e.name === 'time_resume').length, 1);
assert.equal(T.active, false);
assert.equal(T.isFrozen(player), false);
events.length=0; words.length=0;
let holding=true, holdChecks=0;
T.stop(boss,{prewarn:false,burst:.4,dur:1.2,resume:.36,holdWhile:()=>{holdChecks++;return holding;}});
for(let i=0;i<24;i++)T.update(1/60);
assert.equal(T.phase,'stopped');
assert.equal(T.t,0);
for(let i=0;i<120;i++)T.update(1/60);
assert.equal(T.t,0);
assert.equal(T.phase,'stopped');
assert.equal(events.filter(e=>e.name==='time_resume').length,0);
assert.equal(T.isFrozen(player),true);
holding=false;
T.o.grant={actor:player,sec:.5};T.immune.add(player);
for(let i=0;i<29;i++){T.update(1/60);assert.equal(T.isFrozen(player),false);}
T.update(1/60);T.update(1/60);
assert.equal(T.isFrozen(player),true);
for(let i=0;i<150&&T.active;i++)T.update(1/60);
assert.equal(T.active,false);
assert.equal(events.filter(e=>e.name==='time_resume').length,1);
assert.ok(holdChecks>=120);
let cancelHold=true;
T.stop(boss,{prewarn:false,burst:0,dur:1.2,holdWhile:()=>cancelHold});T.update(1/60);
assert.equal(T.phase,'stopped');G.runId++;T.update(1/60);
assert.equal(T.active,false);assert.equal(T.isFrozen(player),false);
console.log(JSON.stringify({ok:true,ticks:ticks.map(e=>Number(e.t.toFixed(3))),grant:true,resumeCue:1,holdWhile:{holdSec:2,stoppedSec:1.2,grantSec:.5,cancel:true}}));
