// 序章按开发脚本第三节推进，主流程等自由走动结束，调查支线仍走 S.run 的互斥入口。
'use strict';
(function () {
  const G = window.G, T = () => G.TPL;
  const prop = (S, id, x, y, o = {}) => S.spawn('prop:' + id, x, y, { id, ...o });
  async function hall(S) {
    await S.setStage('airin_pro', { x: 64, y: 160, facing: 1, music: 'daily' });
    S.player.visible = true;
    S.location('airport_hall', { y: 100 });
    await S.narrate('2001 年，意大利。我是广濑康一，这次一个人坐飞机来到了那不勒斯。', { pos: 'top' });
    await S.say('jotaro4', '康一君，我要你确认一个少年。名字叫汐华初流乃，十五岁。', { name: '承太郎（电话）' });
    await S.say('koichi', '承太郎先生，他是什么人？');
    await S.say('jotaro4', '……也许和 DIO 有血缘。取到一点他的皮肤细胞就行，不要打草惊蛇。', { name: '承太郎（电话）' });
    await S.say('koichi', 'DIO……！好、好的，我试试看。', { expr: 'shock' });
    const st = G.world.stage;
    for (const [id, label, x, text] of [
      ['info', '问讯台', 104, '问讯台。进城的出租车在大厅右侧出口外。'],
      ['flight', '航班屏', 180, '航班屏上的到达时间一行行滚动。我的飞机已经抵达了。'],
      ['belt', '行李转盘', 378, '行李转盘还在缓缓转动。护照和行李都带齐了。'],
    ]) st.hotspots.push({ id, label, x, y: 154, use: async S2 => {
      G.flags['p5Inspect_' + id] = true; S2.mark('p5_inspect_' + id); await S2.say(null, text);
    } });
    for (const [cid, x, text] of [['passer_m', 255, '第一次来那不勒斯？出口在右边，行李可要自己看好。'],
      ['passer_f', 318, '这里的车开得快。过出租车道时，记得看看左右。']]) {
      S.spawn(cid, x, 150, { id: cid, facing: -1, label: '路人', talk: async S2 => {
        G.flags['p5Inspect_' + cid] = true; S2.mark('p5_inspect_' + cid); await S2.say(cid, text);
      } });
    }
    prop(S, 'suitcase', 70, 163);
    S.hint('E 调查、搭话；方向键移动，向右走出机场', 7);
    const goal = T().goal(S, { x: 456, y: 160, delay: 45, label: '出口',
      text: '出租车在右边：走到大厅尽头出机场', done: () => !!G.flags.p5HallExit });
    S.free(true); S.mark('p5_hall_free');
    await S.until(() => S.player.x >= 452 && !S.busy);
    G.flags.p5HallExit = true; goal.stop(); S.free(false); S.hint(null); S.mark('p5_hall_exit');
  }
  async function exit(S) {
    await S.setStage('airout_pro', { x: 300, y: 160, facing: 1, music: 'daily', fade: false });
    const gi = S.spawn('giorno', 352, 156, { id: 'giorno', facing: -1 });
    const taxi = prop(S, 'taxi', 380, 160);
    const bag = prop(S, 'suitcase', 308, 164);
    G.world.focus = { x: 350 }; G.world.snapCamera();
    await S.fadeIn(.5); S.location('airport_out', { y: 100 });
    S.mark('p5_taxi_offer');
    await S.say('giorno', '这位客人，进城吗？行李我帮你放后备箱。', { expr: 'smile' });
    await S.say('koichi', '啊，谢谢你，你的意大利语……不对，你会说日语？', { expr: 'smile' });
    await S.say('giorno', '一点点。');
    await S.animate(.6, k => { bag.x = G.lerp(308, 352, k); bag.z = Math.sin(k * Math.PI) * 12; });
    bag.visible = false; gi.visible = false;
    S.sfx('whoosh');
    await S.animate(.7, k => { taxi.x = G.lerp(380, 485, k); });
    S.mark('p5_luggage_stolen');
    await S.say('koichi', '等一下！我的行李！我的护照还在里面！', { expr: 'shock' });
    await S.summon(S.player, { dur: .2, rise: 4 });
    S.nameCard('koichi', { y: 100 }); S.standCard('echoes3', { y: 100 });
    S.mark('p5_echoes_card'); await S.wait(2.6);
    await S.animate(.45, k => { taxi.x = G.lerp(485, 420, k); });
    G.world.focus = null;
    await S.title('b_pro1_taxi', { dur: 1.6 });
    await G.P5PRO.fightTaxi(S);
    S.music('daily', .6); S.recall(S.player);
    gi.visible = true; gi.x = 392; gi.y = 155; gi.facing = -1;
    const police = S.spawn('police', 510, 151, { id: 'police', facing: -1 });
    G.world.focus = { x: 390 }; G.world.snapCamera();
    await S.walk(police, 452, 153, { speed: 50 });
    S.mark('p5_police'); await S.say('police', '喂，这里不让停车！');
    await S.walk(gi, 430, 155, { speed: 40 });
    // 纸币只在这一幕出现，用小型插入层画，避免修改现成道具和引擎。
    const bill = { x: 439, z: 17 };
    const paper = G.P5.overlay(g => {
      const at = G.cam.w2u(bill.x, 155 - bill.z, 0);
      g.fillStyle = '#1b332b'; g.fillRect(at.x - 7, at.y - 4, 15, 9);
      g.fillStyle = '#add59b'; g.fillRect(at.x - 6, at.y - 3, 13, 7);
      g.fillStyle = '#4e865b'; g.fillRect(at.x - 1, at.y - 2, 3, 5);
    });
    S.mark('p5_banknote');
    await S.animate(.8, k => { bill.x = G.lerp(434, 451, k); bill.z = 17 + Math.sin(k * Math.PI) * 2; });
    await S.wait(.6); paper.close();
    S.face(police, 1); await S.walk(police, 570, 151, { speed: 54 }); police.remove = true;
    await S.walk(gi, 378, 156, { speed: 44 }); S.face(gi, -1);
    S.emote(S.player, '……！', 1.2);
    await S.say('giorno', '对不起，行李我只能收下了。');
    if (!gi.stand) gi.setStand('goldexp');
    await S.summon(gi, { dur: .2, rise: 4 });
    S.nameCard('giorno', { y: 100 }); S.standCard('goldexp', { y: 100 });
    S.mark('p5_goldexp_card'); await S.wait(2.7);
    bag.x = 354; bag.y = 163; bag.visible = true;
    S.standAct(gi, 'reach', { dx: -12, z: 4, dur: 1 });
    S.sfx('sparkle'); S.fx('sparkles', { x: bag.x, y: bag.y - 8, n: 8, radius: 12, colour: '#ffe29c', period: .5 }, { life: 1.3 });
    S.mark('p5_suitcase'); await S.wait(.55);
    bag.remove = true;
    const frog = prop(S, 'frog', 354, 163);
    S.sfx('pop'); S.mark('p5_frog'); await S.wait(.7);
    await S.say('koichi', '行李……变成青蛙了？！他也是替身使者！', { expr: 'shock' });
    frog.atlas = G.atlas('prop:frog_hop'); S.mark('p5_frog_hop');
    for (let i = 0; i < 4; i++) {
      const x = frog.x;
      await S.animate(.4, k => { frog.x = x + 23 * k; frog.z = Math.sin(k * Math.PI) * 13; });
      await S.wait(.12);
    }
    frog.remove = true; S.recall(gi);
    await S.walk(gi, 610, 154, { speed: 55 }); gi.remove = true;
    await S.narrate('那个侧脸，和照片上的汐华初流乃一模一样。', { pos: 'top' });
    S.mark('p5_prologue_end');
    await S.tbc();
  }
  G.STORY.prologue = async S => {
    await S.chapterCard('prologue');
    S.party(['koichi'], { leader: 'koichi' }); S.player.visible = false;
    await S.setStage('map_pro', { x: 160, y: 165, music: null, fade: false });
    await G.P5.calendar(S);
    await hall(S); await exit(S);
  };
})();
