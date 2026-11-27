// 第1章沿用序章的串行节拍；自由探索的U调查走既有互斥脚本入口。
'use strict';
(function () {
  const G = window.G, P = G.P5;
  const prop = (S, id, x, y) => S.spawn('prop:' + id, x, y, { id });
  // 特效跟随世界坐标，不把相机坐标烘进图片；换图立即失效。
  P.worldInk = fn => {
    const stage = G.world.stage;
    return P.overlay((g, t) => {
      if (G.world.stage !== stage) return;
      fn((x, y, draw) => {
        const at = G.cam.w2u(x, y, 0);
        g.save(); g.translate(Math.round(at.x), Math.round(at.y)); g.scale(2, 2);
        draw(g); g.restore();
      }, t, g);
    });
  };
  G.LOOK = G.LOOK || {};
  G.LOOK.giorno = { tags: ['p5_life'], cd: .5, miss: '这个不需要生命。',
    run: async (S, p, h) => {
      if (!h) { S.mark('p5_life_unneeded'); return; }
      await S.summon(p, { dur: .2, rise: 4 });
      S.standAct(p, 'reach', { dx: 12, dur: .6 }); S.sfx('sparkle');
      await S.wait(.3);
    } };
  async function street(S) {
    await S.setStage('street_ch1', { x: 48, y: 162, facing: 1, music: 'daily' });
    S.player.visible = true; S.location('naples_street', { y: 100 });
    await S.narrate('我想成为黑帮里的明星。不是为了钱，也不是为了让人害怕。', { pos: 'top' });
    await S.narrate('我要改变这个让孩子也沾上毒品的帮派。这座城市，不该把未来交给他们。', { pos: 'top' });
    const st = G.world.stage, life = {}, born = {};
    const gravel = prop(S, 'gravel', 220, 162);
    // 长椅和钥匙共用脚底纵深，让站在椅前的人自然遮住它们；z只负责把钥匙抬到座位。
    prop(S, 'bench', 340, 160);
    const key = prop(S, 'key', 344, 160); key.z = 11;
    const ink = P.worldInk((at, t) => {
      at(100, 159, g => {
        if (life.vine) {
          const h = Math.min(30, (t - born.vine) * 35);
          g.scale(1, (9 + h) / 40);
          G.ui.sheet(g, 'vine', 0, 0, 0);
        } else {
          // 源图已带花盆；未赋予生命时只露底部，避免额外画一套盆。
          g.beginPath(); g.rect(-12, -9, 24, 9); g.clip();
          G.ui.sheet(g, 'vine', 0, 0, 0);
        }
      });
      if (life.butterfly) {
        const k = Math.min(1, (t - born.butterfly) / 2.2);
        at(G.lerp(340, 404, k), 143 - Math.sin(k * Math.PI) * 20, g => {
          g.scale((2 + Math.abs(Math.sin(t * 16)) * 4) / 6, 1);
          G.ui.sheet(g, 'butterfly', 0, 0, 4);
        });
      }
    });
    for (const [id, label, x, text] of [
      ['vine', '花盆', 100, '花盆里长出了藤蔓。黄金体验，把生命交给了它。'],
      ['frog', '碎石', 220, '碎石变成了青蛙。去吧，离车轮远一点。'],
      ['butterfly', '长椅上的钥匙', 340, '钥匙变成蝴蝶，朝失主飞去了。'],
    ]) st.hotspots.push({ id, label, x, y: 160, r: 14, tags: ['p5_life'],
      use: S2 => S2.say('giorno', life[id] ? text : '试着用黄金体验赋予它生命吧。按 U。'),
      look: async S2 => {
        if (life[id]) { await S2.say('giorno', '它已经得到生命了。'); return; }
        life[id] = true; born[id] = G.clk.ui - ink.t0;
        if (id === 'frog') { gravel.visible = false; prop(S2, 'frog', 220, 162); }
        if (id === 'butterfly') key.visible = false;
        S2.fx('sparkles', { x, y: 148, n: 8, radius: 12, colour: '#ffe29c', period: .5 }, { life: 1 });
        await S2.wait(id === 'butterfly' ? 2.3 : .9);
        S2.mark('p5_life_' + id); G.ach.life(id); await S2.say('giorno', text);
        if (id === 'butterfly') await S2.say('passer_f', '是我的钥匙！刚才还找不到呢。谢谢你！', { expr: 'smile' });
      } });
    for (const [cid, x, text] of [['passer_m', 168, '街头干部布加拉提在找一个金发少年。听说和机场的事有关。'],
      ['passer_f', 404, '布加拉提正在查卢卡受伤的事。他对这条街的孩子倒很照顾。']])
      S.spawn(cid, x, 152, { id: cid, facing: -1, label: '路人', talk: async S2 => {
        S2.mark('p5_ch1_talk_' + cid); await S2.say(cid, text);
      } });
    const goal = G.TPL.goal(S, { x: 456, y: 162, delay: 35, label: '咖啡座', text: '向右前往街角咖啡座', done: () => S.player.x >= 455 });
    S.hint('U 黄金体验赋予生命：花盆、碎石、钥匙；E 搭话。向右前进', 10);
    S.free(true); S.mark('p5_ch1_street_free');
    await S.until(() => S.player.x >= 455 && !S.busy);
    S.free(false); goal.stop(); ink.close(); S.hint(null); S.recall(S.player);
  }
  async function luca(S) {
    await S.setStage('cafe_ch1', { x: 190, y: 162, facing: 1, music: 'tension' });
    S.location('naples_cafe', { y: 100 });
    const l = S.spawn('luca', 252, 159, { id: 'luca', facing: -1 });
    const frog = prop(S, 'frog', 226, 163), shovel = prop(S, 'shovel', 245, 159);
    S.pose(l, 'cry'); S.mark('p5_luca_cry');
    await S.say('luca', '小鬼，机场那一带是我的地盘。你拉客不交钱？呜……我看着都心酸。', { expr: 'rage' });
    await S.say('giorno', '我拒绝。');
    S.unpose(l); S.pose(l, 'attack'); S.mark('p5_luca_attack');
    await S.animate(.5, k => { shovel.rot = -70 * Math.sin(k * Math.PI); shovel.x = 245 - 17 * k; shovel.z = 14 * Math.sin(k * Math.PI); });
    S.sfx('thud'); S.shake(2, .2); S.fx('sparkles', { x: frog.x, y: 158, n: 7, radius: 14, colour: '#ffe8ab', period: .35 }, { life: .8 });
    await S.summon(S.player, { dur: .2 }); S.standAct(S.player, 'reach', { dur: .8 });
    S.pose(l, 'hurt'); S.emote(l, '……！', .9); S.mark('p5_luca_reflect');
    await S.wait(.6); S.pose(l, 'down'); shovel.z = 0; shovel.rot = 70;
    await S.say('giorno', '打它的那一下，会原样回到打的人身上。');
    S.mark('p5_luca_down'); await S.wait(.8); S.recall(S.player);
  }
  async function encounter(S) {
    await S.setStage('station_ch1', { x: 90, y: 161, music: 'daily' });
    S.location('funicular_station', { y: 100 }); S.mark('p5_funicular_station');
    await S.walk(S.player, 284, 160, { speed: 58 });
    await S.setStage('car_ch1', { x: 120, y: 163, facing: 1, music: 'tension' });
    S.location('funicular_car', { y: 100 });
    const b = S.spawn('bucciarati', 252, 160, { id: 'bucciarati', facing: -1 });
    await S.walk(b, 177, 160, { speed: 42 }); S.mark('p5_bucciarati_enter');
    await S.say('bucciarati', '卢卡住院了。有人看见他和一个金发少年说话。你认识他吗？');
    await S.say('giorno', '不认识。');
    await S.say('bucciarati', '是吗。我只要尝一下汗的味道，就知道人有没有撒谎。', { expr: 'smile' });
    // 仅此瞬间用剪影表现靠近，离开这一拍立即恢复彩色。
    S.player.tint = { color: '#190e24', k: 1 }; b.tint = { color: '#190e24', k: 1 };
    await S.walk(b, 139, 161, { speed: 35 }); S.emote(S.player, '……！', 1); S.mark('p5_sweat_silhouette');
    await S.wait(.8); S.player.tint = null; b.tint = null; await S.walk(b, 198, 161, { speed: 50 });
    await S.say('bucciarati', '——这是撒谎的味道。', { expr: 'rage' });
    S.nameCard('bucciarati', { y: 100 }); S.standCard('stickyfingers', { y: 100 });
    await S.summon(b, { dur: .3 }); await S.summon(S.player, { dur: .3 });
    S.mark('p5_bucciarati_cards'); await S.wait(2.7);
    await G.P5CH1.fight(S, 1);
  }
  async function square(S) {
    await S.setStage('square_ch1', { x: 230, y: 162, facing: 1, music: 'tension' });
    S.location('station_square', { y: 100 });
    const b = S.spawn('bucciarati', 380, 160, { id: 'bucciarati', facing: -1 });
    await S.say('giorno', '外面也有拉链……但你留下的小东西，还能替我带路。');
    await S.summon(S.player, { dur: .2 }); S.standAct(S.player, 'reach', { dur: .7 }); S.sfx('sparkle');
    const dot = { x: 252, y: 151 };
    const fly = P.worldInk((at, t) => at(dot.x, dot.y, g => {
      G.ui.sheet(g, 'insect_light', 0, 0, 2, 1, { alpha: Math.sin(t * 16) > 0 ? 1 : .7 });
    }));
    await S.animate(1.5, k => { dot.x = G.lerp(252, b.x, k); dot.y = 147 - Math.sin(k * Math.PI * 3) * 7; });
    S.mark('p5_tracking_fly'); await S.wait(.8);
    await S.say('giorno', '黄金体验赋予它生命。现在，你躲到哪里都没有用了。');
    fly.close(); await G.P5CH1.fight(S, 2);
  }
  async function harbor(S) {
    await S.setStage('harbor_ch1', { x: 272, y: 162, facing: 1, music: 'sad' });
    S.location('naples_harbor', { y: 100 });
    S.spawn('bucciarati', 330, 160, { id: 'bucciarati', facing: -1 }); S.mark('p5_harbor_alliance');
    await S.say('bucciarati', '为什么手下留情？');
    await S.say('giorno', '因为你刚才为了一个孩子手里的毒品生气。你不是那种人。');
    await S.say('giorno', '我，乔鲁诺·乔巴拿，有一个梦想。', { expr: 'rage' });
    await S.say('giorno', '我要成为黑帮里的明星。', { expr: 'smile' });
    await S.wait(2.2); S.music('daily', .8);
    await S.say('bucciarati', '……想进组织，先过干部波尔波那一关。跟我来。', { expr: 'smile' });
    S.mark('p5_ch1_end'); await S.tbc();
  }
  G.STORY.ch1 = async S => {
    await S.chapterCard('ch1'); S.party(['giorno'], { leader: 'giorno' });
    await street(S); await luca(S); await encounter(S); await square(S); await harbor(S);
  };
})();
