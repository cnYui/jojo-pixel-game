// 第六章让热、阴影和梦中规则决定胜负，梦一保留刻字与不可输的叙事边界。
'use strict';
(function () {
  const G = window.G, M = G.MID, T = G.TPL, W = G.world, I = G.input, px = G.px;
  async function camels(S) {
    S.mark('ch6_camel');
    await S.say('joseph', '阿拉伯沙漠！这回用骆驼，绝对不会坠机！');
    const camel = M.prop(S, 'camel', 92, 162);
    let x = 72, misses = 0;
    while (x < 580) {
      const ok = await S.timing({ label: '跟着骆驼保持平衡（J）', zone: [.36, .64], speed: .9, limit: 3 });
      if (ok) { x += 100; misses = 0; await S.walk('player', x, 162, { speed: 140 }); if (camel) camel.x = x + 16; }
      else if (++misses >= 3) { S.sfx('thud'); S.shake(2); await S.say('polnareff', '哇啊！……刚才那一小段，再来！'); misses = 0; }
    }
  }
  // 太阳：天上第二个太阳（替身）；地平线上的镜子穹顶（x 530）要走到看得见的地方才找得到反光；阴影 = 岩石 / 骆驼 / 车
  const DOME = 530, ROCKS = [100, 330, 570];
  function drawSun(P, d, t) {
    const cx = G.cam.x || 0, k = Math.floor(t * 12);
    // 第二个太阳（贴在天上不随镜头走），光芒 12 fps 步进
    const sx = 222, sy = 28;
    for (let i = 0; i < 12; i++) {
      const a = i * Math.PI / 6 + (k % 2) * .13, r0 = 14, r1 = 21 + ((i + k) % 3) * 2;
      px.line(P, sx + Math.cos(a) * r0, sy + Math.sin(a) * r0, sx + Math.cos(a) * r1, sy + Math.sin(a) * r1, '#fff1a0', .9);
    }
    px.disc(P, sx, sy, 12, '#ffcf3a'); px.disc(P, sx, sy, 8, '#fff6c8');
    // 镜子穹顶：一个银色的小圆顶（阿拉伯·法兹躲在里面）
    const dx = Math.round(DOME - cx);
    if (dx > -30 && dx < 350) {
      [24, 24, 22, 20, 18, 15, 11, 6].forEach((w, i) => px.rect(P, Math.round(dx - w / 2), 147 - i, w, 1, i < 2 ? '#8a96a8' : i > 5 ? '#eef6ff' : '#c9d6e6'));
      if (d.flash > 1.6) px.line(P, dx - 7, 142, dx - 2, 140, '#ffffff', 1, 2);
    }
    for (const xx of [30, ...ROCKS, ...d.camels]) px.ellipse(P, xx - cx - 22, 156, xx - cx + 22, 175, '#493434', null, 1, .55);
    for (const z of d.scorches) px.ellipse(P, z.x - cx - 12, 155, z.x - cx + 12, 176, '#5a2917', null, 1, .7);
    if (d.heat > 50 && G.FX.heat_haze) G.FX.heat_haze(P, t, 96, 150, { amp: (d.heat - 50) / 35 });
  }
  async function sun(S) {
    await M.scene(S, 'desert_ch6', null, 72, 'jotaro');
    await M.lines(S, [['kakyoin', '太阳没有落下……那是替身。'], ['jotaro', '附近一定有人在操纵。看反光。']]);
    S.mark('b12_sun');
    await M.objectFight(S, { id: 'b12_sun', lead: 'jotaro', swap: false,
      // 规划：乔瑟夫、波鲁纳雷夫躲在岩石后面喊热；花京院每 20 s 用触须撑一块阴影（下面的 cover）
      bench: { mode: 'stay', at: { joseph: [96, 170], polnareff: [334, 170], kakyoin: [150, 168] } },
      arena: [0, 640], music: 'battle', coverage: false, kitOverride: Object.fromEntries(M.crew.map(cid => [cid, {
        special: { need: 0, prompt: '反光！U 找准方向，J 投石', window: c => c.data.flash > 0 && c.data.domeSeen,
          async run(s, p, c) { await M.busy(c, async () => {
            const ok = await s.aim({ label: '方向键对准反光，J 投石', throw: true, time: 2, r: 12,
              start: [36, -20], drift: 0, jitter: 0 });
            if (ok) { s.fx('crack', { x: DOME, y: 142, size: 22 }); s.sfx('glass_break'); c.data.won = true; c.end(); }
            else { c.data.flash = 0; s.hint('投偏了！先躲进阴影，等下次反光。', 4); M.damage(c, 14); }
          }); } }
      }])),
      testHint: c => ({ heat: c.data.heat, flash: c.data.flash, mirrorX: DOME, shaded: c.data.shaded, domeSeen: c.data.domeSeen }),
      tick(c, dt) {
        const d = c.data, p = c.player; d.flash = Math.max(0, d.flash - dt);
        d.camels = [250 + Math.sin(c.t * .4) * 80, 450 + Math.cos(c.t * .45) * 80];
        d.camelActors.forEach((a, i) => { if (a) { const nx = d.camels[i]; a.facing = nx > a.x ? 1 : -1; a.x = nx; } });
        const cx = G.cam.x || 0;
        d.domeSeen = DOME >= cx + 10 && DOME <= cx + 310;
        d.shaded = [30, ...ROCKS, ...d.camels].some(x => Math.abs(p.x - x) < 21) || d.cover > c.t;
        d.heat = G.clamp(d.heat + (d.shaded ? -18 : 6) * dt, 0, 100);
        M.every(d, 'drain', dt, 1, () => { if (d.heat >= 100) M.drain(c, 3); });
        M.every(d, 'mirror', dt, 2, () => { d.flash = 2; S.fx('glint', { x: DOME, y: 141, size: 12 }); });
        M.every(d, 'coverT', dt, 20, () => { d.cover = c.t + 3; S.word('法皇撑影！', G.party.get('kakyoin')); });
        M.every(d, 'ray', dt, 3, () => { const x = p.x, y = p.y;
          c.hazard({ shape: 'rect', x0: x - 8, x1: x + 8, y0: 142, y1: 179, warn: 40 / 60, dur: .5,
            dmg: 14, once: true, guard: 'none', fxActive: 'sun_ray' });
          d.scorches.push({ x, y, born: c.t + 40 / 60 });
        });
        d.scorches = d.scorches.filter(z => c.t - z.born < 5);
        M.every(d, 'scorchDmg', dt, 1, () => { if (d.scorches.some(z => c.t >= z.born && Math.abs(p.x - z.x) < 14)) M.drain(c, 2); });
      }
    }, c => {
      Object.assign(c.data, { heat: 0, flash: 0, cover: 0, camels: [250, 450], scorches: [], domeSeen: false, won: false });
      for (const x of ROCKS) c.spawn({ cid: 'prop:rock', x, y: 166, team: 'object', hp: 9999, untargetable: true });
      c.spawn({ cid: 'prop:car', x: 30, y: 168, team: 'object', hp: 9999, untargetable: true });
      c.data.camelActors = [250, 450].map(x => c.spawn({ cid: 'prop:camel', x, y: 172, team: 'object', hp: 9999, untargetable: true }));
      M.pixel('sun_sky', P => drawSun(P, c.data, c.t));
      M.ui(S, g => M.hud(g, ['热量 ' + Math.round(c.data.heat) + '%　' + (c.data.shaded ? '在阴影里' : '快找阴影！'),
        c.data.domeSeen ? (c.data.flash > 0 ? '远处镜子穹顶在反光：U 瞄准！' : '盯住那个镜子穹顶……') : '往右走，找地平线上的反光']));
    });
    // 镜子穹顶碎开，阿拉伯·法兹蹲在里面（分镜 s10 现成）——全篇最短的 Boss 战，喜剧收尾
    S.camera(DOME - 160);
    const guy = S.exists('scene:s10_sunguy') ? S.spawn('scene:s10_sunguy', DOME, 152, { id: 'sunguy', team: 'npc' }) : null;
    S.sfx('glass_break'); S.shake(2, .3); await S.wait(.6);
    if (guy) S.word('！？', guy);
    await S.title('saiki');
    S.camera(null);
    await M.lines(S, [['polnareff', '就这？……一个躲在镜子后面的家伙？'], ['joseph', '哈哈哈哈！走！']]);
    if (guy) guy.remove = true;
  }
  async function dreamOne(S) {
    // 梦里只有花京院一个人（别的同伴在机舱里睡着）
    S.party(['kakyoin'], { leader: 'kakyoin' });
    await M.scene(S, 'dream_ch6', st => {
      st.hotspots = [90, 170, 250].map((x, i) => M.hot('toy' + i, x, '玩具箱', ['detail', 'peek'], '只有玩具。', async s => {
        if (i === 1) { s.flags.dreamKnife = true; s.sfx('metal_scrape'); await s.say('kakyoin', '一把小刀……趁醒来前，在手臂上留下记号！（再按 E）'); }
        else await s.say('kakyoin', '箱子里只有玩具。另找一只。');
      }));
    }, 72, 'kakyoin');
    await M.lines(S, [['kakyoin', '法皇……召不出来？'], ['death13', 'LALI-HO！这里是我的梦！']]);
    S.mark('b13a_death13');
    await M.objectFight(S, { id: 'b13a_death13', lead: 'kakyoin', swap: false, playerMinHp: 1, losable: false, coverage: false, bench: 'hide',
      kitOverride: { kakyoin: { combo: ['DREAM_FIST', 'DREAM_FIST', 'DREAM_FIST'], special: null, rush: null } },
      tick(c) {
        const p = c.player, h = W.stage.hotspots.find(z => Math.abs(z.x - p.x) < 25);
        // 找到小刀后在哪儿按 E 都能刻字；没找到时 E 查身边的玩具箱
        if (I.hit('ok') && !c.data.cine) {
          if (S.flags.dreamKnife) { I.consume('ok'); M.task(c, async () => { S.flags.engraved = true; S.sfx('slash'); await S.say(null, 'BABY STAND'); }); }
          else if (h) { I.consume('ok'); M.task(c, () => h.use(S, h, p)); }
        }
        if (S.flags.engraved) c.end();
        // 梦一按设计是目标段；超时刻字醒来，梦二才承担可失败的战斗。
        if (c.t >= 40 && !S.flags.engraved && !c.data.cine) M.task(c, async () => {
          S.flags.dreamKnife = true; S.flags.engraved = true; await S.say(null, 'BABY STAND'); c.end();
        });
      }, testHint: () => ({ knife: !!S.flags.dreamKnife, engraved: !!S.flags.engraved })
    }, c => { S.flags.dreamKnife = false; S.flags.engraved = false; c.player.stand.hide();
      for (const x of [90, 170, 250]) c.spawn({ cid: 'prop:toy_box', x, y: 162, team: 'object', hp: 9999, untargetable: true });
      c.spawn({ cid: 'death13', boss: true, hp: 9999, x: 240, y: 158, minHp: 9999 });
      M.ui(S, g => M.hud(g, [S.flags.dreamKnife ? '拿到小刀了：按 E 在手臂上刻字！' : 'E 查玩具箱，找出小刀', '四拍「LA」之后镰刀横扫：L 挡 / K 闪']));
    });
    // 先换回机舱再把同伴放回来（在梦里调 party 会把他们摆进梦里）
    await M.scene(S, 'cessna_ch6', null, 72, 'kakyoin');
    S.party(M.crew, { leader: 'kakyoin' }); M.prop(S, 'baby_cradle', 240);
    await M.lines(S, [['kakyoin', 'BABY STAND……是谁刻的？……是我自己！'], ['joseph', '小婴儿？你是不是太累了？']]);
    await S.crash(3, 4); S.shake(5, .6); S.sfx('crash'); await S.wait(.6);
  }
  async function death(S) {
    S.party(['kakyoin'], { leader: 'kakyoin' });
    await M.scene(S, 'dream_ch6', null, 72, 'kakyoin');
    await S.summon('kakyoin');
    S.mark('b13b_death13'); await S.say('kakyoin', '这次，我带着法皇进入了梦。');
    await M.objectFight(S, { id: 'b13b_death13', lead: 'kakyoin', swap: false, bench: 'hide',
      testHint: c => ({ phase: c.data.room, rooted: c.boss && c.boss.rootT }),
      tick(c, dt) { const d = c.data;
        M.every(d, 'roomT', dt, 10, () => { d.room = (d.room + 1) % 2; S.word(d.room ? '木马！' : '棋盘！', c.boss);
          if (!d.room) for (let i = 0; i < 8; i++) c.hazard({ shape: 'rect', x0: i * 40, x1: i * 40 + 20,
            y0: 145 + (i % 2) * 15, y1: 160 + (i % 2) * 15, warn: .6, dur: .25, dmg: 6, once: true, guard: 'none' });
          else c.hazard({ shape: 'rect', x0: 0, x1: 320, y0: c.player.y - 7, y1: c.player.y + 7,
            warn: .6, dur: .2, dmg: 14, once: true, guard: 'none', fxActive: 'dust' });
        });
        if (d.boss && (d.boss.dead || d.boss.hp <= 0)) c.end();
      }
    }, c => { c.data.room = 0; c.data.boss = c.spawn({ cid: 'death13', boss: true, hp: 1000, x: 230, y: 160 });
      M.ui(S, g => M.hud(g, ['J 三下第三下铺触须网，缠住它再打', '四拍「LA」之后镰刀横扫：L 挡 / K 闪']));
      c.on('hit', info => { if (info.t === c.boss && info.move && info.move.tag === 'net') c.boss.rootT = .5; });
    });
    await S.say('kakyoin', '梦结束了。把婴儿交给SPW，带去安全的地方。');
  }
  G.STORY.ch6 = async S => {
    await M.ensureBg('_ch6');
    S.party(M.crew, { leader: 'jotaro' }); await M.scene(S, 'desert_ch6');
    // 地图图标没有骆驼（map_camel），卡拉奇到沙漠边先坐车（规划：car → 骆驼）
    await S.chapterCard('ch6'); await S.route(['卡拉奇', '阿拉伯沙漠'], { vehicle: 'car', day: 17, left: 34 });
    await camels(S); await sun(S);
    await M.scene(S, 'village_ch6', st => {
      st.npcs = [M.npc('npc_townsfolk', 'merchant', 140, '商人', '下一班小飞机能送你们穿过沙漠。'),
        M.npc('npc_villager_f', 'woman', 280, '妇人', '这孩子的父母不在。能顺路把他送过去吗？'),
        M.npc('npc_kid', 'child', 410, '小孩', '那个婴儿……有时会自己笑。')];
      st.hotspots = [M.hot('baby', 306, '婴儿', ['detail', 'peek'], '一个婴儿在摇篮里睡觉。', null, async (s, h, p) => {
        if (p.cid === 'kakyoin') await s.say('kakyoin', '……婴儿的摇篮里，有一把小镰刀的玩具？');
        else if (p.cid === 'jotaro') await s.say('jotaro', '……这婴儿，刚才对我笑了一下。');
        else await s.say(p.cid, '睡得很香。');
      }), M.exit('plane', 590, '小飞机', 'ch6Plane')];
    });
    M.prop(S, 'baby_cradle', 306, 166); M.prop(S, 'cessna', 590, 156);
    await M.explore(S, 'ch6Plane', 'E 搭话；右侧小飞机 E 出发。');
    await M.scene(S, 'cessna_ch6', null, 72); M.prop(S, 'baby_cradle', 240);
    await S.say('polnareff', '婴儿也带上？……好吧，照顾小孩我很拿手！'); await dreamOne(S);
    await M.scene(S, 'camp_ch6', st => { st.hotspots = [M.hot('sleep', 500, '营火', ['life'], '带着替身入睡。', async s => {
      if ((s.flags.campTalk || 0) >= 3) s.flags.ch6Sleep = true; else await s.say('kakyoin', '先把事情告诉大家。');
    })]; }, 100, 'kakyoin');
    // 夜营的篝火（规划：desert(night) + fire）和一旁咯咯笑的婴儿
    M.pixel('campfire', P => { const x = 500 - (G.cam.x || 0); if (G.FX.fire) G.FX.fire(P, x, 166, G.clk.world, { w: 12, h: 16 }); });
    M.prop(S, 'baby_cradle', 540, 166);
    T.memberTalk(Object.fromEntries(['jotaro', 'joseph', 'polnareff'].map(cid => [cid, async s => {
      const key = 'camp_' + cid; if (!s.flags[key]) { s.flags[key] = true; s.flags.campTalk = (s.flags.campTalk || 0) + 1; }
      await s.say(cid, cid === 'jotaro' ? '你留下了记号……我相信你。' : cid === 'joseph' ? '别逞强。今晚大家轮流守夜。' : '你又要睡？花京院！别吓我啊！');
    }])));
    await M.explore(S, 'ch6Sleep', '与三位伙伴 E 搭话后，到营火 E；带法皇入梦。');
    await death(S); await M.end(S, 'ch6_complete');
  };
})();
