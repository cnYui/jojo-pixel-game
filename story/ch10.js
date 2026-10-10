// 第十章的赌局、预言和反咬分别持有重试点，原著必败段不会伪装成玩家失败。
'use strict';
(function () {
  const G = window.G, W = G.world, L = G.LATE, T = G.TPL;
  const crew = ['jotaro', 'joseph', 'avdol', 'polnareff', 'iggy'];
  async function soul(S, cid, doll = false) {
    S.sfx('drain');
    const v = T.show(S, { bg: '#17242c', draw(g, t) {
      const k = Math.min(1, t / 1.4), sc = Math.max(1, Math.round(4 - k * 3));
      T.sprite(g, cid, 'idle', 0, 160, 115 + k * 20, { scale: sc, alpha: 1 - k * .65 });
      g.fillStyle = '#d8b36e'; if (doll) T.sprite(g, 'prop:atum_doll_b', 'idle', 0, 160, 140);
      else { g.fillRect(148, 142, 24, 8); g.fillStyle = '#fff5b4'; g.fillRect(151, 143, 18, 2); }
    } }); try { await S.wait(1.6); } finally { v.close(); }
  }
  G.LATE.soul = soul;
  async function catchCheat(S, sweat, round) {
    const q = { type: 'dealer', caught: false, tooEarly: false, sweat, round,
      touch: { buttons: ['j'], captions: { j: '抓出千' } } };
    await L.game(S, q, s => {
      s.extra = s.t >= 1.05 && s.t <= 1.26;
      if (L.hit('attack')) { if (s.extra && !s.tooEarly) { s.caught = true; S.sfx('card_flip'); } else s.tooEarly = true; }
      if (s.t >= 2) { s.done = true; s.win = s.caught; }
    }, (g, s) => {
      g.fillStyle = '#154538'; g.fillRect(0, 0, 320, 180);
      T.sprite(g, 'darby', 'sit', 0, 259, 170, { scale: 2 });
      for (let n = 0; n < 4; n++) { g.fillStyle = '#eadbb6'; g.fillRect(48 + n * 27, 100, 20, 29); }
      g.fillStyle = '#dba57e'; g.fillRect(112 + Math.sin(s.t * 5) * 15, 81, 34, 13);
      if (s.extra) { g.fillStyle = '#ffdc63'; g.fillRect(146, 92, 20, 28); }
    }, (g, s) => {
      L.label(g, '盯住发牌的手', '多抽一张牌的瞬间按 J；提前动手会打草惊蛇');
      const drops = Math.min(3, Math.floor(s.sweat / 25)); L.text(g, '汗滴 ' + '●'.repeat(drops), 450, 278, '#8ccaff');
      if (s.caught) L.text(g, '抓到了！', 320, 315, '#ffe174', 'center');
    }); return q.caught;
  }
  async function poker(S) {
    for (let attempt = 0; ; attempt++) {
      let sweat = 0, looks = 0, bluff = false, round = 0, failed = false;
      S.mark('ch10_poker_round3');
      while (sweat < 100) {
        const opts = ['看牌', '不看牌，直接加注', '押同伴的灵魂', '押母亲的灵魂'];
        if (!bluff) opts.push('「我已经换过牌了。你要看吗？」');
        const i = await S.choice(opts, '承太郎的下注');
        if (i === 0) { looks++; sweat = Math.max(0, sweat - 10); } else { looks = 0; sweat += [0, 20, 25, 40, 50][i]; }
        if (i === 4) bluff = true;
        if (looks >= 2) { failed = true; break; }
        if (sweat < 100 && await catchCheat(S, sweat, round++)) sweat += 15;
        await S.say('darby', sweat < 70 ? '你连牌都不看……到底有什么把握？' : '这……这不可能。他到底换了什么牌？！');
      }
      if (!failed) { G.flags.darbySweat = Math.min(100, sweat); G.dbg.ev('poker_win', { attempt, round }); return; }
      await S.say('jotaro', '看牌反而暴露了想法。重来这一手。');
    }
  }
  // 三个预言在同一张地图上连着打：荷尔·荷斯打不死、每场用 c.end() 收尾，敌人不会被移走。每场新建一份敌人写法会留下上一场的
  // 荷尔·荷斯（第3个预言时场上三个人一起开枪，伊奇几秒就倒）。同一章里三场共用一份写法 → fight.spawn 按 e._obj 复用同一个角色。
  const holhorseSpec = () => ({ cid: 'holhorse', kit: 'e_holhorse_late', boss: true, hp: 99999, x: 620, y: 160 });
  async function prophecy(S, index, hh = holhorseSpec()) {
    const xMirror = 410, xDrum = 520, target = 638;
    S.mark('ch10_prophecy_' + (index + 1));
    await S.say('boingo', ['十五秒后，镜子前的子弹会击中头部！', '十五秒后，油桶旁有人会滑倒，被子弹击中！', '十五秒后，路口正中有人会被击中！'][index]);
    await S.fight({ id: 'b22_prophecy' + (index + 1), lead: 'iggy', swap: true, arena: [300, 700], vs: index === 0 ? 'emperor_thoth' : null,
      allies: ['polnareff'], bench: 'hide', finish: 'none', waves: [[hh]],
      steps: { label: '让预言落到荷尔·荷斯身上', total: 3, done: index },
      timer: { label: '预言', until: 15 },
      onWave(s, n, es, attempt, c) {
        W.stage.props = W.stage.props.filter(p => !String(p.id || '').startsWith('late_'));
        W.stage.actors = W.stage.actors.filter(a => !a.lateProp);
        c.player.x = 360; c.player.y = 160; c.data.rotated = false; c.data.drumX = xDrum; c.data.oil = false;
        const mirror = T.prop(s, 'mirror_stand', xMirror, 165), drum = T.prop(s, 'oil_drum', xDrum, 167);
        c.data.mirror = mirror; c.data.drum = drum;
        mirror.lateProp = drum.lateProp = true;
        s.insertUI(g => L.hud(g, ['托特神 · 第' + (index + 1) + '个预言',
          ['靠近镜子按 E 转向，反射他的子弹', '靠近油桶按 E，把它推到路中央', '把荷尔·荷斯引到发光的路口'][index]]));
        L.pixel(P => G.px.rect(P, target - 15 - G.cam.x, 148, 30, 25, '#eecf68', .33));
      },
      tick(c) {
        if (L.hit('ok')) {
          if (index === 0 && Math.abs(c.player.x - xMirror) < 30) { c.data.rotated = true; c.data.mirror.facing = -1; G.S.sfx('clang'); }
          if (index === 1 && Math.abs(c.player.x - c.data.drumX) < 35) { c.data.drumX += 30; c.data.drum.x = c.data.drumX; c.data.oil = c.data.drumX >= 600; G.S.sfx('thud'); }
        }
        if (c.t >= 15) {
          const win = index === 0 ? c.data.rotated : index === 1 ? c.data.oil : Math.abs(c.boss.x - target) <= 35;
          if (win) { c.boss.play('hurt'); G.S.sfx('gunshot'); G.S.impact('invert', 2 / 60); c.step(index + 1); c.end(); }
          else { L.damage(c, 40); c.fail('预言落到了自己身上……只重来当前预言。'); }
        }
      }, after(s) { s.insertUI(null); }, onRetry(s) { s.hint('这个预言重新开始；前面的兑现结果保留。', 4); }
    });
  }
  async function birdFight(S, stage, hp, first) {
    await S.setStage(stage, { x: first ? 380 : 100, y: 160 });
    let remaining = 0;
    await S.fight({ id: first ? 'b23a_petshop' : 'b23b_petshop', lead: 'iggy', swap: false, vs: first ? 'horus' : null,
      arena: first ? [300, 700] : [20, 610], bench: 'hide', finish: 'none',
      kitOverride: { iggy: { parryWin: 8 / 60 } },
      waves: [[{ cid: 'petshop', kit: 'e_petshop', hp, boss: true, x: first ? 590 : 430, y: 160 }]],
      onWave(s, n, es, attempt, c) {
        W.stage.props = W.stage.props.filter(p => !String(p.id || '').startsWith('late_'));
        W.stage.obstacles = W.stage.obstacles.filter(o => !o.lateIce);
        s.mark(first ? 'ch10_bird_street' : 'ch10_bird_sewer');
        c.data.bites = 0; c.data.walls = []; c.data.frozen = []; c.data.freezeT = 0;
        s.insertUI(g => L.hud(g, [first ? '荷鲁斯神 · 街道' : '荷鲁斯神 · 下水道', '俯冲咬来的瞬间按 L，再连按 J 反咬；高处打不到',
          first ? null : '白霜出现一秒后平台冻结；水面会冻住脚步']));
        c.on('birdBite', ({ e }) => L.task(c, async () => {
          e.mem.locked = true;
          const win = await L.clash(s, { label: '咬住不放！（连按 J）', time: 4, a: 'fool', b: 'horus' });
          if (win) { e.hp = Math.max(1, e.hp - 300); c.data.bites++; s.sfx('punch_heavy'); G.dbg.ev('petshop_bite', { hp: e.hp }); }
          else L.damage(c, 18);
          e.mem.locked = false; e.cool = .8; e.mem.perch = false;
          if (e.hp <= 1 || first && e.hp <= 750) { remaining = e.hp <= 1 ? 0 : e.hp; c.end(); }
        }));
        c.on('iceWall', () => {
          if (c.data.walls.filter(a => !a.dead && !a.remove).length >= 2) return;
          const x = G.clamp(c.player.x + 45, c.spec.arena[0] + 25, c.spec.arena[1] - 25);
          const wall = c.spawn({ cid: 'prop:ice_wall', id: 'ice_' + c.t, team: 'object', x, y: 160, hp: 2, bodyW: 12,
            dmgMul: (t, a, m) => m.dmg ? 1 / m.dmg : 0, onHitBy(t, a, m, info) { return ['J1', 'J2', 'J3', 'rush'].includes(info.slot) ? null : 'evade'; } });
          wall.breakable = { anim: 'broken', onBreak() { s.sfx('ice'); const i = W.stage.obstacles.indexOf(wall.mem.ob); if (i >= 0) W.stage.obstacles.splice(i, 1); } };
          wall.mem.ob = { x0: x - 10, x1: x + 10, y0: 147, y1: 174, lateIce: true }; W.stage.obstacles.push(wall.mem.ob); c.data.walls.push(wall);
        });
        if (!first) L.pixel(P => {
          for (const x of c.data.frozen) G.px.rect(P, x - G.cam.x, 151, 45, 3, '#c9f1ff');
          if (c.data.warningX != null) G.px.rect(P, c.data.warningX - G.cam.x, 151, 45, 3, Math.floor(G.clk.ui * 12) % 2 ? '#8bcbdf' : '#edf9ff');
        });
      },
      tick(c, dt) {
        if (first) return;
        c.data.freezeT += dt;
        if (c.data.freezeT >= 9 && c.data.warningX == null) c.data.warningX = 70 + (c.data.frozen.length * 95) % 470;
        if (c.data.freezeT >= 10) { c.data.freezeT %= 10; c.data.frozen.push(c.data.warningX); c.data.warningX = null; G.S.sfx('ice'); }
        const water = c.player.y > 168 || c.data.frozen.some(x => c.player.x >= x && c.player.x <= x + 45);
        if (water && c.t >= (c.data.rootNext || 0)) { c.player.rootT = 1; c.data.rootNext = c.t + 2.2; }
      }, after(s) { s.insertUI(null); }
    }); return remaining;
  }
  L.ch10 = { catchCheat, poker, prophecy, birdFight };
  G.STORY.ch10 = async function (S) {
    S.party(crew, { leader: 'polnareff' }); await S.chapterCard('ch10'); await S.setStage('cafe_ch10', { x: 85, y: 164 });
    S.location('cairo_outskirts');
    S.mark('ch10_arrival'); await S.narrate('第36天，开罗郊外。一个赌徒说，他知道那栋馆的位置。');
    const darby = S.spawn('darby', 237, 164, { id: 'darby', name: '丹尼尔·J·达比' }); darby.play('sit');
    const cat = S.spawn('npc_cat', 160, 161, { id: 'bet_cat', name: '猫' });
    const dealer = S.spawn('npc_dealer', 286, 164, { id: 'dealer', name: '发牌小哥' });
    L.pixel(P => { for (let n = 0; n < 3; n++) G.px.rect(P, 130 + n * 20, 167, 7, 4, '#bd795b'); });
    // 名牌放左上（后面紧跟底部对话框，默认 y 264 会被对话框盖住）；先等地点卡收走，两张卡不叠在同一个角
    await S.until(() => !G.uifx.cards.some(k => k.kind === 'loc')); S.nameCard('darby', { y: 24 });
    await L.lines(S, [['darby', '我是丹尼尔·J·达比。你们愿意赌上灵魂吗？'], ['polnareff', '就赌那只猫，先吃哪块肉！']]);
    S.mark('ch10_cat_bet'); await S.choice(['左边的肉', '中间的肉', '右边的肉'], '猫会先吃哪块？');
    cat.play('eat'); await S.wait(.8); cat.remove = true;
    await S.say('darby', '你的选择，我早就知道。'); await soul(S, 'polnareff'); S.leave('polnareff');
    S.setLeader('joseph', { force: true }); S.mark('ch10_joseph_cheat');
    const suspicious = await S.choice(['袖口藏牌', '洗牌手法', '发牌小哥'], '揭穿一次出千');
    G.flags.darbyCheatFound = suspicious === 2;
    await S.say('joseph', suspicious === 2 ? '原来发牌的也是你的人！' : '这动作……一定藏着什么。');
    await S.say('darby', '就算你发现这一处，也看不到下一处。'); await soul(S, 'joseph'); S.leave('joseph');
    S.setLeader('jotaro', { force: true });
    // 直接放的 VS 卡退场时会自动挂左上角小标签（S.fight 结束时才摘）；赌局有自己的顶栏，放完就摘掉
    await S.vs({ key: 'osiris', hero: 'jotaro', enemy: { cid: 'darby', anim: 'sit', scale: 2 } }); G.uifx.vsTag(null);
    await poker(S);
    await S.say('jotaro', '开牌啊。你不是赌上了一切吗？'); await S.say('darby', '啊……啊……');
    S.party(crew, { leader: 'jotaro' }); await S.narrate('筹码碎开，灵魂回到伙伴们身上。赌徒抱着筹码，不再回答。');
    S.mark('ch10_cairo_search');
    await L.explore(S, 'cairo_day_ch10', { exitX: 905, location: 'cairo', hint: '换队长调查：照片、鸟的气息与北面的气味。继续向右找馆。', hotspots: [
      L.hot('photo', 170, '宅邸照片', ['nensha', 'detail'], async s => s.say('joseph', '没人认得这栋房子……念写只拍到一角屋顶。'), async s => { G.flags.mansionPhoto = true; await s.say('joseph', '屋顶的一角。这条线索还不够。'); }),
      L.hot('bird', 380, '树梢', ['life'], async s => s.say('avdol', '一只鸟始终盯着这条街。'), async s => { G.flags.mansionBird = true; await s.say('avdol', '不是普通的鸟……它在监视我们。'); }),
      L.hot('scent', 600, '城北的气味', ['scent'], async s => s.say(null, '伊奇对着城北低吼。'), async s => { G.flags.mansionScent = true; await s.say(null, '气味一直延伸到城北。'); })
    ], npcs: [T.npc('npc_dealer', 'bread_seller', 275, 160, { label: '卖烤饼的', talk: async s => s.say(null, '这个屋顶？没见过。来块烤饼吗？') })] });
    await S.setStage('flashback_ch10'); S.filter('sepia', 1); S.mark('ch10_holhorse_memory');
    await L.lines(S, [['holhorse', '只要在背后开枪……'], ['dio', '你的呼吸很平稳，荷尔·荷斯。']]);
    await L.view(S, { bg: 'black', parts: [{ cid: 'dio', x: 190, y: 172, scale: 3 }, { cid: 'holhorse', x: 74, y: 173, scale: 2 }] }, .7);
    await S.say('holhorse', '子弹……消失了？我发誓，永远效忠您！'); S.filter('sepia', null);
    S.party(['iggy', 'polnareff'], { leader: 'iggy' }); await S.setStage('cairo_day_ch10', { x: 360, y: 160 });
    const hh = holhorseSpec();
    for (let n = 0; n < 3; n++) await prophecy(S, n, hh);
    if (hh._obj) hh._obj.play('down');
    await L.lines(S, [['holhorse', '再低一厘米……当 No.2 果然最好。'], ['boingo', '预言怎么全落到我们身上了？！']]);
    S.sfx('dog_bark'); await S.narrate('波因哥抱着漫画跑了。荷尔·荷斯躺平，之后再没有出现。');
    S.party(['iggy'], { leader: 'iggy' }); await S.narrate('第47天。伊奇独自溜出去，闯进了那只鸟的领地。');
    const remain = await birdFight(S, 'cairo_day_ch10', 1500, true);
    await S.narrate('它追进了下水道。水和平台都开始冻结。');
    if (remain > 0) await birdFight(S, 'sewer_ch10', remain, false);
    await S.narrate('那只鸟再也没有飞起来。尼罗河边，一个孩子捡起了拖着腿的伊奇。');
    await L.view(S, { bg: 'cairo_day', parts: [{ cid: 'iggy', anim: 'walk', x: 120, y: 166, scale: 2 }], draw(g) {
      g.fillStyle = '#eee0b5'; g.fillRect(117, 151, 5, 8);
    } }, 1.7);
    // 馆外背景在第11章的背景包里（packs.json），从选章直接进第10章时还没插进页面：先加载再换图（同第1章结尾预载第2章）。
    S.party(crew, { leader: 'iggy' }); await G.res.loadPack('bg_ch11'); await S.setStage('mansion_ext_ch11');
    await S.narrate('第48天。伊奇带着众人，找到了 DIO 的馆。'); S.music('ominous'); S.mark('ch10_end'); await S.tbc();
  };
})();
