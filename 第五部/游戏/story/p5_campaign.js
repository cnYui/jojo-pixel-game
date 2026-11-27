// 第2章到终章共用过场、探索、预警和战斗重试，篇章数据各自维护。
'use strict';
(function () {
  const G = window.G, episodes = G.P5_EPISODES;
  if (!episodes) throw new Error('缺少黄金之风后续章节');
  const attackNames = {
    shadow: '替身会从另一侧突袭。预警出现时用 K 拉开距离。',
    rush: '直线冲刺有预警，向上或下闪开。',
    zone: '地面亮起后离开危险区，再靠近反击。',
    projectile: '避开远程射击的车道，贴近后用 J 连打。',
  };
  const addMove = (key, extra) => G.MOVES['P5_C_' + key] = Object.assign({
    slot: 'enemy', body: 'attack', stand: 'rush', standDx: 10, dur: .85,
    active: [.36, .52], dmg: 10, push: 3, reach: [0, 40], depth: 9,
    guard: 'normal', sfx: 'whoosh', sfxHit: 'punch', warn: { tier: 'W1', dur: .48 },
  }, extra);
  addMove('jab', { dmg: 6 });
  addMove('shadow', { active: [.52, .64], reach: [0, 54], dmg: 15, warn: { tier: 'W2', dur: .7 } });
  addMove('rush', { melee: false, dash: { dist: 82, time: .42, w: 8, line: true }, warn: { tier: 'W4', dur: .65 } });
  addMove('projectile', { melee: false, fireAt: [.36], shot: {
    kind: 'bullet', speed: 170, dmg: 10, hitR: [4, 6, 18], reflect: true, colour: '#e6c69d',
  }, warn: { tier: 'W4', dur: .62 } });

  function heroKit(id, stand) {
    if (G.KITS[id]?.combo) return;
    // 布加拉提在第1章仅有过场配置，后续可操作时也必须装入出拳链。
    G.KITS[id] = Object.assign({}, G.KITS.giorno, { hp: 132 },
      G.KITS[id], { standId: stand || G.KITS[id]?.standId });
  }
  const heroSpecial = {
    giorno: ['赋予生命', '#f3d87d'], bucciarati: ['拉链连击', '#b9c8ff'], abbacchio: ['忧郁蓝调', '#ab9df6'],
    mista: ['性感手枪', '#ffda81'], narancia: ['航空史密斯', '#f3a780'], fugo: ['紫烟', '#c299ee'],
    trish: ['辣妹', '#f6a6d2'], doppio: ['预见', '#f58cad'],
  };
  function setHeroSpecial(lead, heroStand) {
    const [word, colour] = heroStand === 'requiem' ? ['镇魂曲', '#f3da98'] : heroSpecial[lead] || ['觉醒', '#e7c5ff'];
    return { need: 100, prompt: '能量满时按 U：' + word,
      run: async (S, p, c, C) => {
        const e = c.boss;
        if (!e || e.dead) return;
        p.facing = e.x >= p.x ? 1 : -1;
        C.stand('rush', { dx: 14 });
        S.fx('sparkles', { x: e.x, y: e.y - 18, n: 14, radius: 16, colour, period: .32 }, { life: .6 });
        G.combat.hit(p, e, { slot: 'special', dmg: heroStand === 'requiem' ? 35 : 25, push: 4, guard: 'none', sfxHit: 'punch_heavy' });
        S.mark('p5_campaign_special');
        await C.wait(.24);
      } };
  }
  function makeBoss(config, id) {
    const { enemy, stand, attack, name, hp } = config;
    return { id, cid: enemy, name, hp: hp || 94, x: 224, y: 160, boss: true, kit: {
      hp: hp || 94, speed: 50, standId: enemy === stand ? null : stand, moves: [], koStyle: 'fade',
      brain(e, dt, c) {
        if (!dt || e.atk || e.tele) return true;
        const p = c.player, d = c.data;
        const dx = Math.abs(p.x - e.x), dy = Math.abs(p.y - e.y);
        e.facing = p.x >= e.x ? 1 : -1;
        const special = (d.next || 0) <= c.t;
        if (special) {
          d.next = c.t + (config.heroStand === 'requiem' ? 2.65 : 3.5);
          if (attack === 'zone') {
            const half = config.enemy === 'cioccolata' ? 34 : 24;
            c.hazard({ owner: e, side: 'enemy', shape: 'rect', x0: p.x - half, x1: p.x + half,
              y0: p.y - 6, y1: p.y + 6, warn: .72, dur: .65, dmg: 13,
              guard: 'none', push: 0, once: true, sfx: 'whoosh' });
            G.S.standAct(e, 'punch', { dx: 10, dur: .85 });
          } else {
            if (attack === 'shadow') {
              const opposite = Math.sign(p.x - e.x) || 1;
              e.x = G.clamp(p.x + opposite * 45, 24, 296);
              e.y = p.y;
            }
            G.AI.tele(e, 'P5_C_' + attack);
          }
          d.attacks = (d.attacks || 0) + 1;
          return true;
        }
        if (dy > 3) G.AI.kite(e, p, 20, dt);
        else G.AI.approach(e, p, 20, dt);
        if (e.cool <= 0 && dx < 33 && dy < 8) { G.AI.tele(e, 'P5_C_jab'); e.cool = 1.6; }
        return true;
      },
    } };
  }
  async function battle(S, config, id) {
    const lead = config.lead || 'giorno';
    if (config.heroStand) S.player.setStand(config.heroStand);
    try {
      await S.fight({ id, arena: [12, 308], lead, music: 'battle', after: 'tension',
        losable: true, coverage: false, energy: { start: config.heroStand === 'requiem' ? 100 : 38 },
        waves: [[makeBoss(config, id + '_boss')]],
        kitOverride: { [lead]: { special: setHeroSpecial(lead, config.heroStand) } },
        async onWave(S2, _, actors, attempt, c) {
          Object.assign(c.player, { x: 96, y: 160, facing: 1 });
          c.data.next = c.t + .8;
          S2.hint(attackNames[config.attack] + '　J 连打 / L 格挡', 8);
          S2.mark(id + '_start');
        },
        testHint: c => ({ bossHp: c.boss?.hp, bossX: c.boss?.x, bossY: c.boss?.y,
          attack: config.attack, attacks: c.data.attacks || 0,
          hazards: G.world.hazards.filter(h => !h.dead).map(h => ({
            x0: h.x0, x1: h.x1, y0: h.y0, y1: h.y1, phase: h.phase, left: h.warn - h.t,
          })) }),
      });
      G.combat.stopRush(S.player); S.recall(S.player);
      S.mark(id + '_win');
      await S.wait(.45);
    } finally {
      if (config.heroStand && S.player?.cid === lead) S.player.setStand(G.KITS[lead].standId);
    }
  }
  async function dialogue(S, cues) {
    for (const [speaker, text, expr] of cues || []) {
      if (speaker) await S.say(speaker, text, { pos: 'top', expr: expr || 'normal' });
      else await S.narrate(text, { pos: 'top' });
    }
  }
  async function explore(S, label, width, id) {
    let inspected = false;
    G.world.stage.hotspots.push({ id: 'campaign_evidence', label, x: 134, y: 160, r: 26,
      use: async S2 => { await S2.narrate(label, { pos: 'top' }); G.ach.investigate(id); inspected = true; } });
    const goal = G.TPL.goal(S, { x: width - 30, y: 160, delay: 4, label: '继续', text: '向右继续',
      done: () => S.player.x >= width - 31 });
    S.mark('p5_campaign_explore'); S.hint('E：' + label + '　向右继续', 7); S.free(true);
    await S.until(() => !S.busy && (S.player.x >= width - 31 || inspected));
    S.free(false); goal.stop(); S.hint(null);
  }
  for (const [key, ep] of Object.entries(episodes)) {
    ep.scenes.forEach((scene, i) => {
      const bg = scene.bg || ep.bg;
      if (!G.D.bg[bg]) throw new Error('缺少第五部场景背景：' + bg);
      const id = 'p5_s' + i + '_' + (key === 'final' ? 'fin' : key);
      G.STAGES[id] = G.p5Stage.base(id, bg, G.D.bg[bg].w, { music: 'tension' });
      if (scene.fight) {
        const lead = scene.fight.lead || 'giorno';
        heroKit(lead, lead === 'doppio' ? 'kingcrimson' : G.D.heroes[lead]?.stand);
      }
    });
    G.STORY[key] = async S => {
      await S.chapterCard(key);
      for (const [i, scene] of ep.scenes.entries()) {
        const lead = scene.fight?.lead || scene.lead || 'giorno';
        const bg = scene.bg || ep.bg, width = G.D.bg[bg].w;
        S.party([lead], { leader: lead });
        await S.setStage('p5_s' + i + '_' + (key === 'final' ? 'fin' : key), {
          x: scene.explore ? 72 : 96, y: 160, facing: 1, music: i ? 'tension' : 'daily',
        });
        S.player.visible = true;
        if (scene.apparition) {
          S.spawn('prop:' + scene.apparition, 228, 157, { id: 'campaign_apparition' });
          S.mark('p5_campaign_apparition');
        }
        // 对话角色没有战斗实体时仍使用正式头像，避免额外演员挡住走道。
        await dialogue(S, scene.say);
        const sceneId = key + '_' + (i + 1);
        if (scene.explore) await explore(S, scene.explore, width, sceneId);
        if (scene.fight) await battle(S, scene.fight, 'b_p5_' + sceneId);
        await dialogue(S, scene.after);
      }
      S.mark('p5_' + key + '_clear');
      if (key !== 'final') await S.tbc();
      else await G.ui.notice({ title: '黄金之风　终', text: '感谢游玩。\n从那不勒斯到罗马，黄金之风的旅程到此落幕。' });
    };
  }
})();
