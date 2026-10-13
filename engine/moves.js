// 招式表 G.MOVES、角色招式组 G.KITS（6 主角 + M1 敌人 + 敌人 brain）。数值照规划 §3.2–§3.6、§5.1.2 / §5.1.3 / §5.2.2 / §5.2.3（包 5）
//   时间一律写秒（f = 1/60 s，注释里写帧数）；判定 reach 是规划里写的“相对本体脚点”的值（from 'body'），
//   规划明写“从法皇算”的才用 from 'stand'（技术约定 §4.14.2 的例子写 from 'stand'，取规划表头的说法，见交付说明）。
//   招式的缺省字段由 combat.js 的 normMove 补（§4.14.2 的默认值）。
'use strict';
(function () {
  const G = window.G;
  const f = (n) => n / 60;
  const M = (G.MOVES = {});
  const K = (G.KITS = {});

  // ======================================================================= 承太郎 · 白金之星（规划 §3.3）
  // J1 刺拳：前摇 6 / 判定 4 / 收招 10，判定 6–40 ±8，伤害 10，击退 6，能量 +2，顿帧 3f 局部
  M.SP_J1 = {
    slot: 'J1', body: 'cmd', stand: 'punch', standSeq: [[0, f(6)], [1, f(12)], [2, 99]], standDx: 14,
    dur: f(20), active: [f(6), f(10)], from: 'body', reach: [6, 40], depth: 8,
    dmg: 10, push: 6, energy: 2, poiseDmg: 10, stop: f(3), link: f(10), cancel: f(10), step: 2,
    sfx: 'whoosh', sfxHit: 'punch', sfxSeed: 0, fxHit: 'light', accent: '#ffd83c', shake: [1, f(6)],
  };
  // J2 直拳：同上，替身多冲 4 px，判定 6–42
  M.SP_J2 = Object.assign({}, M.SP_J1, {
    slot: 'J2', standDx: 18, reach: [6, 42], sfxSeed: 1, sfxRate: 1.08,
  });
  // J3 上勾拳：9 / 4 / 16，判定 6–46，伤害 18，击退 24 + 小浮空（z 10，24f），顿帧 6f 全局，ORA!
  //   替身前冲 24 px（upper 帧的拳头在替身身前 20 px：拳头 ≈ 本体前 44 px，和判定 46 对齐；以前 16，拳头只到 36）
  //   2026-10-10：upper 补成 3 帧（art_stands）：0 下蹲蓄力（0–8f）→ 1 上冲（8–17f，盖住判定 9–13f）→ 2 收势拳过头顶（17f 起）；
  //   以前 upper 只有 1 帧，前 7f 拿 punch 帧 0 垫蓄力（standPre），现在不用了
  M.SP_J3 = {
    slot: 'J3', body: 'cmd', stand: 'punch_heavy', standSeq: [[0, f(8)], [1, f(17)], [2, 99]], standDx: 24, dur: f(29), active: [f(9), f(13)], from: 'body',
    reach: [6, 46], depth: 8, dmg: 18, push: 24, launch: { z: 10, t: f(24) }, energy: 2, poiseDmg: 25,
    stopAll: f(6), link: f(13), cancel: f(13), step: 3, sfx: 'whoosh', sfxRate: 0.85, sfxHit: 'punch_heavy', sfxVol: 0.8,
    fxHit: 'heavy', accent: '#ffd83c', shake: [3, f(15)], bump: 0.06, word: 'ORA!', flashTarget: f(2),
  };
  // 连打终结：6 / 4 / 24，判定 6–54 ±10，16 / 40 / 8f 全局（CFG.fin），受击者紫色闪 2f
  //   替身前冲 24 px（punch 帧 2 的拳头在替身身前 31 px → 本体前 55 px，对齐判定 54）
  M.SP_FIN = {
    slot: 'fin', body: 'cmd', stand: 'punch', standSeq: [[2, 99]], standDx: 24, dur: f(34), active: [f(6), f(10)],
    from: 'body', reach: [6, 54], depth: 10, dmg: 16, push: 40, launch: { z: 22, t: f(36) }, energy: 4, poiseDmg: 25,
    stopAll: f(8), link: 99, cancel: f(10), step: 4, sfx: 'whoosh', sfxHit: 'crit', fxHit: 'finisher', accent: '#c080ff',
    shake: [3, f(15)], bump: 0.08, word: 'ORA!!', flashTarget: f(2),
  };
  // U 终结一拳（必杀里用）：伤害 30、击退 60、浮空 16、12f 全局 + 0.2 s 定格、invert → purple
  M.SP_U_FIN = {
    slot: 'special', body: 'cmd', stand: 'punch', dur: f(30), active: [0, f(4)], from: 'body', reach: [0, 64], depth: 14,
    dmg: 30, push: 60, launch: { z: 16, t: f(40) }, energy: 0, poiseDmg: 999, stopAll: 0, guard: 'none',
    sfxHit: 'ko_hit', fxHit: 'finisher', accent: '#c080ff', shake: [6, f(30)], bump: 0.2, word: 'ORA!!!', flashTarget: f(2),
  };
  K.jotaro = {
    hp: 130, speed: 64, standId: 'starplat',
    combo: ['SP_J1', 'SP_J2', 'SP_J3'],
    rush: {
      tick: f(4), dmg: 4, push: 1, reach: [6, 52], depth: 10, loop: 'ora_loop', voice: 'ora_voice', word: 'ORA',
      fx: 'fists', fist: 'starplat', accent: '#d8c8ff', hitSfx: 'punch', finisher: 'SP_FIN',
    },
    guard: { pose: 'block' }, guardAttack: null, chords: {}, parry: { effect: 'reflect' }, dodge: {},
    special: { name: '欧拉欧拉', title: 'jotaro', bg: 'radial', colours: ['#5a2aa0', '#34146a', '#46208a'], run: spJotaro, pose: 'cmd' },
    explore: { pose: 'punch' }, grunt: 'grunt_jotaro',
  };
  // 欧拉欧拉：切入 0.92 s（combat 放）→ 冲刺 8f → 连打 60f（15 × 5）→ 终结 30（共 105）
  async function spJotaro(p, C) {
    const t = C.target(180);
    C.aim(t);
    if (t) await C.dash(t.x - p.facing * 30, t.y, f(8));
    C.stand('rush', { dx: 16, jitter: 1 });
    await C.rush(f(60), { dmg: 15, tick: f(12), reach: [6, 56], depth: 12, word: 'ORA', wordEvery: f(14),
      visual: { reach: 42, spread: 34, rate: 45, scale: 1.35, big: 0.3 } });
    C.stand('punch', { dx: 20, seq: [[2, 99]] });
    const hit = C.hitArea(C.front(0, 64, 14), 'SP_U_FIN');
    if (hit.length) {
      C.fx('shockwave', { x: hit[0].x, y: hit[0].y - 24, r_max: 64, dur: 0.4, colour: '#d8c8ff' });
      C.impact(['invert', 'purple'], f(2), f(12));
      C.stopAll(f(12) + 0.2);
      C.shake(6, f(30));
    }
    await C.wait(0.45);
  }

  // ======================================================================= 花京院 · 绿色法皇（规划 §3.3）
  // J1 / J2 绿宝石·点射：6 / — / 10，3 颗 × 4，速度 320，扇形 ±6°，射程 160，半径 4，击退 2，每颗命中 +1
  //   宝石从法皇手上出（cast 帧捧着宝石的手在替身身前 12 px、离替身脚底约 30 px；以前出手点是替身脚底 z 4，贴地飞），
  //   射程 160 px 飞满碎成绿光点；宝石纵深判定 ±8（和近战一样；±4 时 ±6° 扇形两边的宝石 40 px 外就全从身边擦过）；法皇浮着出招（z 10，和待机同高），站在花京院身后偏前（dx 4、画在本体后面），不再把花京院整个挡住
  M.KAK_J1 = {
    slot: 'J1', body: 'cmd', stand: 'cast', standDx: 4, standZ: 10, standDepth: 'back', dur: f(16), active: [f(6), f(8)], melee: false, from: 'stand',
    fireAt: [f(6)], link: f(8), cancel: f(8), shotAhead: 12, shotZ: 30,
    shot: { kind: 'gem', n: 3, spread: 6, speed: 320, life: 0.7, range: 160, fizzle: 'gem', hitR: [4, 8, 22], dmg: 4, push: 2, energy: 1,
      stop: f(1), colour: '#50ff9a', slot: 'shot', reflect: true, accent: '#70ffb0' },
    sfx: 'emerald_shot', energy: 0, accent: '#70ffb0',
  };
  M.KAK_J2 = Object.assign({}, M.KAK_J1, { slot: 'J2' });
  // J3 触须网：9 / — / 16，前方 16–80 px 铺 8 根丝，存在 90f；碰到 → 缠住 30f（Boss 20f，之后 60f 免疫），抓到 6 伤
  M.KAK_NET = {
    slot: 'J3', body: 'cmd', stand: 'punch_heavy', standDx: 6, standZ: 10, standDepth: 'back', dur: f(25), active: [f(9), f(13)], melee: false, from: 'body',
    link: f(13), cancel: f(13), energy: 2, sfx: 'hiero_tentacle', accent: '#50e890',
    net: { x0: 16, x1: 80, h: 10, dur: f(90), dmg: 6, root: f(30), rootBoss: f(20), rootImmune: f(60), max: 0, alpha: 1, hidden: false },
  };
  // 灰塔段 B 的“藏起来的触须网”：存在 360f、同时最多 3 张、半透明 .3、hidden（规划 §5.2.2 kitOverride）
  M.KAK_NET_HIDDEN = Object.assign({}, M.KAK_NET, {
    net: { x0: 16, x1: 80, h: 12, dur: f(360), dmg: 6, root: f(45), rootBoss: f(45), rootImmune: f(60), max: 3, alpha: 0.3, hidden: true },
  });
  // 连打终结：12 颗 × 2，扇形 ±20°，8f 全局，能量 +4
  M.KAK_FIN = {
    slot: 'fin', body: 'cmd', stand: 'cast', standDx: 4, standZ: 10, standDepth: 'back', dur: f(30), active: [f(6), f(8)], melee: false, from: 'stand',
    fireAt: [f(6)], link: 99, cancel: f(10), energy: 0, sfx: 'emerald', shotAhead: 12, shotZ: 30,
    shot: { kind: 'gem', n: 12, spread: 20, speed: 380, life: 0.7, range: 190, fizzle: 'gem', hitR: [4, 4, 22], dmg: 2, push: 2, energy: 0.34,
      stop: f(1), stopAllFirst: f(8), colour: '#50ff9a', slot: 'fin', reflect: true, accent: '#70ffb0' },
  };
  K.kakyoin = {
    hp: 100, speed: 66, standId: 'hiero',
    combo: ['KAK_J1', 'KAK_J2', 'KAK_NET'],
    rush: {
      tick: f(6), dmg: 2, push: 1, reach: [0, 180], depth: 10, loop: null, voice: null, word: null, fx: 'gems',
      accent: '#70ffb0', finisher: 'KAK_FIN', pose: 'cast', standDx: 4, standZ: 10, standDepth: 'back', jitter: 0, shotAhead: 12, shotZ: 30,
      shot: { kind: 'gem', n: 4, spread: 10, speed: 380, life: 0.7, range: 180, fizzle: 'gem', hitR: [4, 4, 22], dmg: 2, push: 1, energy: 0.5,
        stop: f(1), colour: '#50ff9a', slot: 'rush', reflect: true, accent: '#70ffb0' },
      tickSfx: 'emerald', tickSfxEvery: f(18), tickSfxRate: 1.2,
    },
    guard: { pose: 'block' }, guardAttack: null, chords: {}, parry: { effect: 'root', dur: f(30) }, dodge: {},
    special: { name: '绿宝石水花', title: 'kakyoin', bg: 'radial', colours: ['#1c6a40', '#0a3a20', '#2a8a50'], run: spKakyoin },
    explore: { pose: 'cast' }, grunt: 'grunt_kakyoin',
  };
  // 绿宝石水花：发射 24f，24 颗 × 4 = 96，全屏追踪 1.5 rad/s，每颗 1f 局部，最后一颗 10f 全局
  //   宝石从法皇双手（C.hand：替身身前 12 px、离替身脚底 30 px）迸出，不再从花京院身上出；
  //   追踪 1.5 rad/s 时扇形 ±34° 的宝石大半从目标身边擦过、绕着飞 1.6 s，改 3.2 rad/s 收束到目标，飞满 420 px 碎成光点
  async function spKakyoin(p, C) {
    const target = C.target();
    const aim = C.aim(target);
    C.stand('cast', { dx: 4, z: 10, depth: 'back', hold: true });
    const h0 = C.hand(12, 30);
    C.fx('glow', { x: h0.x, y: h0.y - h0.z, r: 32, colour: '#50ff9a', alpha: 0.35 }, { life: 0.5 });
    C.sfx('emerald'); C.sfx('sparkle', { vol: 0.6 });
    let first = true;
    for (let i = 0; i < 24; i++) {
      const last = i === 23;
      // 扇形围绕敌人方向展开，追踪负责收束而非把反向弹体掉头。
      const ang = aim + (G.hrange(-34, 34, 77, i) * Math.PI) / 180;
      C.shoot({
        kind: 'gem', speed: 380, ang, life: 1.2, range: 420, fizzle: 'gem', homing: 3.2, homingTarget: target, hitR: [5, 7, 22], dmg: 4, push: 2, energy: 0, stop: f(1),
        stopAll: last ? f(10) : 0, slot: 'special', colour: '#50ff9a', big: true, reflect: false, accent: '#70ffb0',
        onHit: () => { if (first) { first = false; C.impact(['invert', 'green'], f(2), f(6)); } },
      }, C.hand(12, 30));
      if (i % 3 === 0) await C.wait(f(3)); // 24 颗在 24f 内射完
    }
    await C.wait(0.7);
  }

  // ======================================================================= 阿布德尔 · 红色魔术师（规划 §3.3）
  M.AV_J1 = {
    slot: 'J1', body: 'cmd', stand: 'punch', standDx: 14, dur: f(20), active: [f(6), f(10)], from: 'body',
    reach: [6, 42], depth: 8, dmg: 10, push: 6, energy: 2, poiseDmg: 10, stop: f(3), link: f(10), cancel: f(10), step: 2,
    sfx: 'whoosh', sfxHit: 'punch', fxHit: 'light', accent: '#ff9040', shake: [1, f(6)], fire: true, cuttable: true,
    hitFx: [{ name: 'fire', kw: { w: 8, h: 10 }, life: 0.2 }], hitSfx2: { name: 'fire_burst', vol: 0.35 },
  };
  M.AV_J2 = Object.assign({}, M.AV_J1, { slot: 'J2', sfxSeed: 1 });
  // J3 火球：9 / — / 16，速度 200、半径 6，18 + 燃烧 2 × 4，击退 24，6f 全局，ゴオッ
  //   2026-10-09 晚（用户截图：火从替身拳头出来，火球却从地上冒出来）：火球从红色魔术师 cast 帧的手上出
  //   （替身身前 22 px = 本体前约 34 px、离替身脚底 34 px），朝面向飞 130 px 后化成一团烟和火星熄灭 = 射程约 165 px（从阿布德尔身前算，
  //   规划 §3.3 阿布德尔）；射程内照常碰撞、爆炸、顿帧。以前出手点是阿布德尔脚底（z 0）：火球贴地飞，|z − 20| > 18 永远打不到站着的人，
  //   燃烧也被角色自己的 burn 字段盖掉（combat.shotOrigin）
  //   2026-10-10：替身改摆自己的重拳帧 magred.heavy（0 蓄火 0–9f → 1 直拳，火球在第 9f 从拳头上飞出）；重拳的拳头在替身身前 27 px、
  //   离替身脚底 34 px，出手点跟着拳头挪到 27，射程 130 → 125，从阿布德尔身前算仍是约 165 px（12 + 27 + 125 = 164）
  M.AV_J3 = {
    slot: 'J3', body: 'cmd', stand: 'punch_heavy', standSeq: [[0, f(9)], [1, 99]], standDx: 12, dur: f(29), active: [f(9), f(13)], melee: false, from: 'stand',
    fireAt: [f(9)], link: f(13), cancel: f(13), energy: 0, sfx: 'fire_burst', shotAhead: 27, shotZ: 34,
    shot: { kind: 'fireball', speed: 200, life: 1.2, range: 125, fizzle: 'fire', r: 6, hitR: [7, 6, 22], dmg: 18, push: 24, energy: 2, stopAll: f(6),
      burn: { dmg: 4, n: 2, tick: 0.5 }, cuttable: true, slot: 'J3', word: 'ゴオッ', explodeFx: 18, poiseDmg: 25,
      sfxHit: 'fire_burst', fxHit: 'heavy', accent: '#ff9040', shake: [3, f(15)] },
  };
  // 地火柱（guardAttack，按住 L 再按 J）：施法 12f；目标脚下冒火星 40f → 火柱 30f，伤 20，6f 全局，冷却 90f，fromGround
  //   替身照旧摆 cast（双手前推放火；punch_heavy 2026-10-10 起指向重拳帧，这里写明 cast，画面和以前一样）
  M.AV_PILLAR = {
    slot: 'guardAttack', body: 'cmd', stand: 'cast', standDx: 8, dur: f(12), active: [f(2), f(4)], melee: false,
    link: 99, cancel: f(12), energy: 0, sfx: 'fire_burst', sfxRate: 0.8, cd: f(90),
    pillar: { r: 10, warn: f(40), dur: f(30), dmg: 20, energy: 2, stopAll: f(6), front: 64, launch: { z: 14, t: f(30) }, word: 'ゴオッ' },
  };
  // 连打 火焰洪流：每 6f 一击 4，判定 8–96 ±10，每击可被斩火
  //   爆炎：替身重拳（0 蓄火 0–6f → 1 直拳出火球，盖住判定 6–10f）
  M.AV_FIN = {
    slot: 'fin', body: 'cmd', stand: 'punch_heavy', standSeq: [[0, f(6)], [1, 99]], standDx: 12, dur: f(34), active: [f(6), f(10)], from: 'body',
    reach: [8, 96], depth: 12, dmg: 16, push: 40, energy: 4, poiseDmg: 25, stopAll: f(8), link: 99, cancel: f(10),
    sfx: null, sfxHit: 'explosion', sfxVol: 0.6, fxHit: 'finisher', accent: '#ff7a30', shake: [3, f(15)], bump: 0.08,
    flashTarget: f(2), fire: true, cuttable: true, hitFx: [{ name: 'explosion', kw: { size: 28 } }],
  };
  // U 十字火焰风暴：追踪安卡 ≤ 40f，60 + 燃烧 4 × 4 + 周围 48 px 溅射 20，击退 50，12f 全局，invert → red
  M.AV_U_ANKH = {
    kind: 'ankh', size: 34, speed: 240, life: 40 / 60 + 0.4, homing: 3.0, hitR: [12, 10, 26], dmg: 60, push: 50,
    burn: { dmg: 4, n: 4, tick: 0.5 }, splash: { r: 48, dmg: 20 }, cuttable: true, slot: 'special', energy: 0,
    stopAll: f(12) + 0.2, poiseDmg: 999, reflect: false,
  };
  K.avdol = {
    hp: 120, speed: 60, standId: 'magred',
    combo: ['AV_J1', 'AV_J2', 'AV_J3'],
    rush: {
      tick: f(6), dmg: 4, push: 1, reach: [8, 96], depth: 10, loop: 'fire_loop', voice: null, word: 'ゴオオッ', wordEvery: f(24),
      fx: 'fire', accent: '#ffb070', finisher: 'AV_FIN', cuttable: true, fire: true,
      tickSfx: 'fire_burst', tickSfxEvery: f(18), tickSfxRate: 1.3, tickSfxVol: 0.5,
    },
    // L 火墙（规划 §3.3）：按住格挡时身前一道 fire(w 10, h 30, intensity .7)，松手 / 被打 / 出招就收（combat.state）
    guard: { pose: 'block', fx: { name: 'fire', kw: { w: 10, h: 30, intensity: 0.7 }, dx: 16 } }, guardAttack: 'AV_PILLAR', chords: {},
    parry: { effect: 'root', dur: f(40), fx: 'firerope' }, dodge: {},
    special: { name: '十字火焰风暴', title: 'avdol', bg: 'menace', colours: ['#5a1010', '#2a0608', '#a0301a'], run: spAvdol },
    explore: { pose: 'punch' }, grunt: 'grunt_avdol',
  };
  async function spAvdol(p, C) {
    const target = C.target();
    C.aim(target);                                  // 只用来把人转向最近的敌人；火焰不再朝敌人斜着飞 / 追着拐弯，沿转好后的朝向水平直飞（2026-10-11 用户要求）
    const ang = p.facing < 0 ? Math.PI : 0;
    C.stand('cast', { dx: 12, hold: true });   // 双手前推（punch_heavy 2026-10-10 起是重拳帧；大招照旧 cast）
    C.sfx('crossfire');
    // 安卡在红色魔术师伸出的手上聚起来，再从手上飞出去（以前从阿布德尔身上、离地 24 px 飞出，大安卡整个压在他身上）
    const h0 = C.hand(24, 32);
    C.fx('fire_ankh', { x: h0.x, y: h0.y - h0.z, size: 54, grow: 0.18 }, { life: 0.2 });
    await C.wait(0.18);
    const s = C.shoot(Object.assign({}, M.AV_U_ANKH, {
      ang, homing: 0, hitR: [12, 14, 26], visualSize: 76,       // 不追踪；直飞靠纵深判定吃敌人，从 10 放宽到 14（和重拳的纵深一样）
      onHit: (sh, t) => {
        C.impact(['invert', 'red'], f(2), f(8));
        C.flash(f(9), 0.7, '#ffffff');
        C.shake(6, f(21));
        C.fx('explosion', { x: sh.x, y: sh.y - sh.z, size: 100 });
        C.fx('fire_burst', { x: sh.x, y: sh.y - sh.z, size: 52, dur: 0.65 });
        C.fx('shockwave', { x: sh.x, y: sh.y - sh.z, r_max: 78, dur: 0.45, colour: '#ffb020' });
      },
    }), C.hand(24, 32));
    await C.until(() => !s || s.dead, 1.4);
    await C.wait(0.35);
  }
  // 十字火焰风暴·Special（第 2 战阶段 4，剧情专用 U 的 run 里调用：G.KITS.avdol.crossfireSp(p, C)）：
  //   4 个安卡从左右两侧绕弧线飞去（会被架剑切开）+ 第 5 个从目标脚下地面冒出（fromGround，切不到）→ 命中返回 true
  K.avdol.crossfireSp = async function (p, C) {
    C.stand('cast', { dx: 12, hold: true });
    C.sfx('crossfire');
    const t = C.target(400);
    for (let i = 0; i < 4; i++) {
      const side = i % 2 === 0 ? -1 : 1;
      C.shoot(Object.assign({}, M.AV_U_ANKH, {
        size: 26, dmg: 30, homing: 4.5, life: 1.2, ang: side < 0 ? -0.9 : Math.PI + 0.9, splash: null, burn: null, stopAll: 0,
      }), { x: (t ? t.x : p.x) + side * 150, y: (t ? t.y : p.y) + (i < 2 ? -8 : 8), z: 34 });
      await C.wait(0.18);
    }
    await C.wait(0.35);
    if (!t) return false;
    // 第 5 道：W3 式地裂光 → 火柱 + 安卡从下往上
    C.fx('crack', { x: t.x, y: t.y, size: 22, dur: 0.3 }, { life: 0.5 });
    C.sfx('rumble', { vol: 0.8 });
    await C.wait(0.35);
    let landed = false;
    C.fx('fire', { x: t.x, y: t.y, w: 18, h: 44, intensity: 1.3 }, { life: 0.7 });
    C.shoot(Object.assign({}, M.AV_U_ANKH, {
      fromGround: true, cuttable: false, vz: 220, speed: 0, homing: 0, life: 0.5, dmg: 60,
      onHit: (sh) => {
        landed = true;
        C.impact(['invert', 'red'], f(2), f(10));
        C.flash(f(9), 0.7, '#ffffff'); C.shake(6, f(21));
        C.fx('explosion', { x: sh.x, y: sh.y - sh.z, size: 64 });
      },
    }), { x: t.x, y: t.y, z: 0 });
    await C.wait(0.7);
    return landed;
  };

  // ======================================================================= 波鲁纳雷夫 · 银色战车（规划 §3.3；M1 不在他身上打仗，给能用的组）
  //   判定 8–60（规划写 8–56）：thrust 帧 1 / 2 的剑尖在替身身前 51 px，替身前冲 14 → 剑尖到本体前 65 px，
  //   原来的 56（+ 体宽 62）比画面上的剑短一截，剑尖碰到人却不掉血；命中时剑尖 glint（规划 §3.3）
  M.PN_J1 = {
    slot: 'J1', body: 'cmd', stand: 'punch', standSeq: [[0, f(4)], [2, f(7)], [1, 99]], standDx: 14, dur: f(19),
    active: [f(6), f(9)], from: 'body', reach: [8, 60], depth: 6, dmg: 10, push: 6, energy: 2, poiseDmg: 10, stop: f(3),
    link: f(9), cancel: f(9), step: 2, sfx: null, sfxHit: 'slash0', fxHit: 'light', accent: '#9cc8ff', shake: [1, f(6)],
    preSfx: { name: 'slash0', at: f(2) }, tipGlint: true, hitFx: [{ name: 'glint', kw: { size: 7, dur: 0.18 }, life: 0.18 }],
  };
  M.PN_J2 = Object.assign({}, M.PN_J1, { slot: 'J2', sfxHit: 'slash1', preSfx: { name: 'slash1', at: f(2) } });
  M.PN_J3 = {
    slot: 'J3', body: 'cmd', stand: 'punch_heavy', standDx: 20, dur: f(29), active: [f(9), f(13)], from: 'body',
    reach: [8, 70], depth: 6, dmg: 18, push: 24, energy: 2, poiseDmg: 25, stopAll: f(6), link: f(13), cancel: f(13), step: 16,
    sfx: 'stab', sfxHit: 'slash0', fxHit: 'heavy', accent: '#9cc8ff', shake: [3, f(15)], bump: 0.06, word: 'シュッ',
    flashTarget: f(2), ghostDash: true, lines: true,
  };
  M.PN_FIN = {
    slot: 'fin', body: 'cmd', stand: 'punch', standDx: 18, dur: f(33), active: [f(6), f(9)], from: 'body',
    reach: [8, 64], depth: 8, dmg: 16, push: 40, energy: 4, poiseDmg: 25, stopAll: f(8), link: 99, cancel: f(9),
    sfxHit: 'crit', fxHit: 'finisher', accent: '#9cc8ff', shake: [3, f(15)], bump: 0.08, flashTarget: f(2),
    preSfx: { name: 'slash1', at: f(2) },
  };
  M.PN_U_HIT = {
    slot: 'special', from: 'body', reach: [-40, 40], depth: 14, dmg: 12, push: 0, energy: 0, poiseDmg: 0, stop: f(2),
    sfxHit: 'slash0', fxHit: 'light', accent: '#c8d8ff', guard: 'none',
  };
  M.PN_U_FIN = {
    slot: 'special', from: 'body', reach: [0, 70], depth: 14, dmg: 24, push: 50, launch: { z: 14, t: f(36) }, energy: 0,
    poiseDmg: 999, sfxHit: 'ko_hit', fxHit: 'finisher', accent: '#c8d8ff', guard: 'none', shake: [5, f(24)], bump: 0.15,
  };
  K.polnareff = {
    hp: 110, speed: 70, standId: 'chariot',
    combo: ['PN_J1', 'PN_J2', 'PN_J3'],
    rush: {
      tick: f(4), dmg: 4, push: 1, reach: [8, 60], depth: 12, loop: 'rapier_loop', voice: 'hora_voice', word: 'HORA',
      fx: 'thrust', accent: '#c8d8ff', hitSfx: 'slash', finisher: 'PN_FIN',
    },
    guard: { pose: 'block' }, guardAttack: null, chords: {}, parry: { effect: 'reflect' }, dodge: {},
    special: { name: '银色战车——卸甲', title: 'polnareff', bg: 'radial', colours: ['#28305a', '#141830', '#3a4a8a'], run: spPolnareff },
    explore: { pose: 'punch' }, grunt: 'grunt_polnareff',
  };
  // 卸甲·残像连刺：围刺 36f（12 × 6）+ 正面一刺 24（M1 普通版）
  //   “卸甲”真的卸：替身换成脱甲皮（skin 'bare'），盔甲碎片从替身身上炸开；残影用脱甲的突刺帧；放完换回带甲（规划 §3.3）
  async function spPolnareff(p, C) {
    const t = C.target(200);
    C.aim(t);
    C.sfx('armor_off');
    const st = p.stand, oldSkin = st ? st.skin : null;
    const sx = st && st.visible ? st.x : p.x;
    C.fx('burst', { x: sx, y: p.y - 30, n: 16, speed: 90, life: 0.6, colours: ['#c8d8ff', '#ffffff', '#8890b0'], gravity: 160 });
    if (st) st.skin = 'bare';
    try {
      if (t) await C.dash(t.x - p.facing * 34, t.y, f(6));
      C.sfx('rapier_loop', { vol: 0.7 });
      for (let i = 0; i < 6; i++) {
        const tt = C.target(200);
        if (tt) {
          const a = (i / 6) * Math.PI * 2;
          C.fx('stand_summon', { cid: 'chariot', logical: 'bare_thrust', frame: 1, x: tt.x + Math.cos(a) * 32,
            y: tt.y + Math.sin(a) * 8, dur: 0.03, alpha: 0.45, flip: Math.cos(a) > 0, aura_colour: '#9cc8ff' }, { life: 0.16 });
          C.fx('slash_arc', { x: tt.x + Math.cos(a) * 22, y: tt.y - 26 + Math.sin(a) * 14, size: 38, dur: 0.18, flip: i % 2 === 0 });
          C.hitArea({ x0: tt.x - 40, x1: tt.x + 40, y0: tt.y - 14, y1: tt.y + 14 }, 'PN_U_HIT');
        }
        await C.wait(f(6));
      }
      C.stand('punch', { dx: 22 });
      C.fx('slash_arc', { x: p.x + p.facing * 42, y: p.y - 26, size: 52, dur: 0.25, flip: p.facing < 0 });
      const hit = C.hitArea(C.front(0, 70, 14), 'PN_U_FIN');
      if (hit.length) { C.impact(['invert', 'blue'], f(2), f(8)); C.stopAll(f(10)); }
      await C.wait(0.4);
    } finally { if (st) st.skin = oldSkin; }
  }

  // ======================================================================= 乔瑟夫 · 隐者之紫（vine；M1 给能用的组）
  //   2026-10-09 晚：J1 / J2 / J3 / 终结以前写 stand: null，隐者之紫一根藤都不出（只看见乔瑟夫指一下、对面掉血）。
  //   现在每招都让藤蔓从伸出去的手上（身前 12 px、离脚底 30 px，stand.js）长出去：0.1 s 长到 vineLen（藤尖 ≈ 判定远端），
  //   判定一结束 vineHold 后 0.1 s 缩回；J3 带刺三股、抓住时在对手身上缠一圈（缠住多久缠多久）
  M.JS_J1 = {
    slot: 'J1', body: 'cmd', stand: 'punch', dur: f(20), active: [f(6), f(10)], from: 'body', reach: [8, 60], depth: 6,
    dmg: 9, push: 6, energy: 2, poiseDmg: 10, stop: f(3), link: f(10), cancel: f(10), step: 1,
    sfx: 'vine', sfxVol: 0.6, sfxHit: 'punch', fxHit: 'light', accent: '#d0a0ff', vineLen: 52, vineHold: f(5),
  };
  M.JS_J2 = Object.assign({}, M.JS_J1, { slot: 'J2', sfxSeed: 2 });
  M.JS_J3 = {
    slot: 'J3', body: 'cmd2', stand: 'punch_heavy', dur: f(31), active: [f(9), f(15)], from: 'body', reach: [8, 68], depth: 6,
    dmg: 12, push: -16, root: f(40), rootBoss: f(24), energy: 2, poiseDmg: 25, stopAll: f(6), link: f(15), cancel: f(15),
    sfx: 'vine', sfxHit: 'hamon', fxHit: 'heavy', accent: '#d0a0ff', word: 'ギュルッ', vineLen: 58, vineHold: f(10), flashTarget: f(2),
    onHit(a, t) { G.combat.fxAt('wrap', { h: Math.round(t.topPx() * (t.scale || 1) * 0.9), w: 14, n: 4, kind: 'vine' }, a, Math.max(0.3, t.rootT || 0), { follow: t }); },
  };
  M.JS_FIN = {
    slot: 'fin', body: 'cmd', stand: 'punch_heavy', dur: f(34), active: [f(6), f(10)], from: 'body', reach: [8, 64], depth: 10,
    dmg: 16, push: 40, energy: 4, poiseDmg: 25, stopAll: f(8), link: 99, cancel: f(10), sfx: 'vine', sfxHit: 'punch_heavy',
    fxHit: 'finisher', accent: '#ffd83c', vineLen: 54, vineHold: f(6), flashTarget: f(2), hitFx: [{ name: 'sparkles', kw: { colour: '#ffd83c', n: 8, radius: 14 }, life: 0.5 }],
    // 波纹爆（规划 §3.3）：金黄闪 + 波纹顺着藤打进对手身体
    onHit(a, t) { G.combat.fxAt('hamon', { x0: a.x + a.facing * 12, y0: a.y - (a.z || 0) - 30, x1: t.x, y1: G.combat.midY(t), strands: 3, colour: '#ffd83c' }, a, 0.25); if (G.flash) G.flash(f(6), 0.35, '#fff0a0'); },
  };
  M.JS_U_HIT = {
    slot: 'special', from: 'body', reach: [-20, 20], depth: 12, dmg: 14, push: 0, root: f(60), energy: 0, stop: f(2),
    sfxHit: 'hamon', fxHit: 'light', accent: '#ffb020', guard: 'none',
  };
  K.joseph = {
    hp: 110, speed: 64, standId: 'hermit',
    combo: ['JS_J1', 'JS_J2', 'JS_J3'],
    // 连打 波纹藤鞭（规划 §3.3）：每 6f 重新抽一鞭，上下交替（relash），打中时波纹沿藤闪一下（hamon）
    //   本体摆 cmd_hold（joseph.vine_hold：手臂伸直握拳拽住藤蔓、轻微抖动的 2 帧循环）；以前写死 cmd，甩藤放完定在“收势”帧
    rush: { tick: f(6), dmg: 4, push: 1, reach: [8, 64], depth: 10, loop: null, voice: null, word: null, fx: 'vines',
      accent: '#d0a0ff', hitSfx: 'vine', finisher: 'JS_FIN', relash: true, vineLen: 54, hamon: true, body: 'cmd_hold' },
    guard: { pose: 'block' }, guardAttack: null, chords: {}, parry: { effect: 'root', dur: f(30) }, dodge: {},
    special: { name: '波纹疾走', title: 'joseph', bg: 'radial', colours: ['#20305a', '#101830', '#3050a0'], run: spJoseph },
    explore: { pose: 'punch' }, grunt: 'grunt_joseph',
  };
  async function spJoseph(p, C) {
    const t = C.target(220);
    if (!t) { await C.wait(0.3); return; }
    C.aim(t);
    C.sfx('hamon');
    // 藤蔓从乔瑟夫伸出去的手上（point 帧：身前 12 px、离脚底 30 px）射向对手
    C.fx('vines', { t1: 0.12, colour: 'purple', strands: 3, bend: -14 },
      { follow: p, dx: 12, dy: -30, follow1: t, dy1: -28, life: 0.85 });
    C.fx('hamon', { strands: 3, colour: '#ffd83c' },
      { follow: p, dx: 12, dy: -30, follow1: t, dy1: -28, life: 0.85 });
    C.fx('wrap', { h: 48, w: 16, n: 5, kind: 'vine' }, { follow: t, life: 0.85 });
    for (let i = 0; i < 5; i++) {
      C.fx('vines', { x0: t.x + (i - 2) * 6, y0: t.y, x1: t.x + (i - 2) * 3, y1: t.y - 40, t1: 0.6, colour: 'purple', strands: 1 }, { life: 0.7 });
      C.hitArea({ x0: t.x - 20, x1: t.x + 20, y0: t.y - 12, y1: t.y + 12 }, 'JS_U_HIT');
      C.fx('hit_spark', { x: t.x + (i - 2) * 5, y: t.y - 30 - i * 3, size: 20, colour: '#fff8c0', accent: '#ffb020' });
      await C.wait(0.05);
    }
    C.flash(0.2, 0.6, '#fff0a0');
    await C.wait(0.5);
  }

  // ======================================================================= 伊奇 · 愚者（M1 不在队里，最小组）
  M.IG_J1 = {
    slot: 'J1', body: 'bite', stand: null, dur: f(20), active: [f(6), f(10)], from: 'body', reach: [4, 22], depth: 6,
    dmg: 8, push: 4, energy: 2, poiseDmg: 10, stop: f(3), link: f(10), cancel: f(10), step: 3,
    sfx: 'dog_bark', sfxRate: 1.2, sfxVol: 0.5, sfxHit: 'punch', fxHit: 'light', accent: '#e8c070',
  };
  //   2026-10-09 晚：愚者的图集只有 idle / claw / slam / wall / glide，以前写的 punch / punch_heavy 全部回退成 idle，
  //   沙爪、沙拳根本不出手。现在直接用 claw：帧 0 举爪（前摇）→ 帧 1 爪子砸到地上（判定开始那一帧）；
  //   替身前冲 18 px，爪尖落在本体前约 41 px（判定 44–48）；落爪处扬沙（activeFx），J3 / 终结加地面冲击环
  //   2026-10-10：愚者的 claw / slam 按原工程 _fool_frame 重画（art_stands）：claw 1 的爪尖落在替身身前约 26 px，
  //   slam 有了真正的砸地帧（0 人立举沙拳 → 1 砸进身前约 29 px），J3 沙拳 / 连打终结改用 slam；扬沙落点跟着改
  const SAND = ['#f0c878', '#d8a050', '#fbe0a0'];
  M.IG_J2 = {
    slot: 'J2', body: 'cmd', stand: 'claw', standSeq: [[0, f(6)], [1, 99]], standDx: 18, dur: f(20), active: [f(6), f(10)], from: 'body', reach: [6, 44],
    depth: 8, dmg: 10, push: 6, energy: 2, poiseDmg: 10, stop: f(3), link: f(10), cancel: f(10), sfx: 'sand', sfxHit: 'punch',
    fxHit: 'light', accent: '#e8c070', sand: 10,
    activeFx: [{ name: 'burst', dx: 26, kw: { n: 10, speed: 70, life: 0.45, colours: SAND, gravity: 220, angle: 90, spread: 120, size: 1 }, life: 0.45 }],
  };
  M.IG_J3 = {
    slot: 'J3', body: 'cmd', stand: 'slam', standSeq: [[0, f(9)], [1, 99]], standDx: 18, dur: f(29), active: [f(9), f(13)], from: 'body', reach: [6, 48],
    depth: 10, dmg: 18, push: 24, energy: 2, poiseDmg: 25, stopAll: f(6), link: f(13), cancel: f(13), sfx: 'sand',
    sfxHit: 'thud', fxHit: 'heavy', accent: '#e8c070', word: 'ズガッ', sand: 30, shake: [3, f(15)], flashTarget: f(2),
    activeFx: [
      { name: 'burst', dx: 29, kw: { n: 30, speed: 110, life: 0.6, colours: SAND, gravity: 300, angle: 90, spread: 140, size: 2 }, life: 0.6 },
      { name: 'shockwave', dx: 29, kw: { r_max: 30, squash: 0.3, colour: '#e8c070', dur: 0.35, width: 2 }, life: 0.35 },
      { name: 'dust', dx: 29, kw: { n: 6, speed: 60 }, life: 0.6 },
    ],
  };
  M.IG_FIN = {
    slot: 'fin', body: 'cmd', stand: 'slam', standSeq: [[0, f(6)], [1, 99]], standDx: 20, dur: f(34), active: [f(6), f(10)], from: 'body', reach: [6, 56],
    depth: 12, dmg: 16, push: 40, energy: 4, poiseDmg: 25, stopAll: f(8), link: 99, cancel: f(10), sfxHit: 'crit',
    fxHit: 'finisher', accent: '#e8c070', sand: 40, flashTarget: f(2), word: 'ズガッ',
    activeFx: [
      { name: 'burst', dx: 29, kw: { n: 40, speed: 150, life: 0.7, colours: SAND, gravity: 300, angle: 90, spread: 60, size: 2 }, life: 0.7 },
      { name: 'shockwave', dx: 29, kw: { r_max: 40, squash: 0.3, colour: '#e8c070', dur: 0.4, width: 3 }, life: 0.4 },
    ],
  };
  M.IG_U = {
    slot: 'special', from: 'body', shape: { kind: 'circle', r: 96 }, depth: 30, dmg: 70, push: 50, energy: 0, poiseDmg: 999,
    sfxHit: 'thud', fxHit: 'finisher', accent: '#e8c070', guard: 'none', shake: [5, f(24)],
  };
  K.iggy = {
    hp: 80, speed: 84, standId: 'fool',
    combo: ['IG_J1', 'IG_J2', 'IG_J3'],
    // 连打 沙暴连抓：愚者每一跳重新抓一下（claw 帧 0 → 1，relash），每抓一下扬沙；L 沙盾 = 愚者的 wall 帧（规划 §3.3）
    rush: { tick: f(4), dmg: 4, push: 1, reach: [6, 52], depth: 12, loop: null, voice: null, word: null, fx: 'sand',
      accent: '#e8c070', hitSfx: 'punch', finisher: 'IG_FIN', tickSfx: 'sand', tickSfxEvery: f(12),
      pose: 'claw', standDx: 18, relash: true, lashSeq: [[0, f(2)], [1, 99]] },
    guard: { pose: 'wall', dx: 22 }, guardAttack: null, chords: {}, parry: { effect: 'sink', dur: f(30) }, dodge: { dist: 52 },
    special: { name: '愚者·沙之巨像', title: 'iggy', bg: 'radial', colours: ['#9a5420', '#6e3614', '#c08040'], run: spIggy },
    explore: { pose: 'idle' }, grunt: null,
  };
  async function spIggy(p, C) {
    // 沙之巨像（2026-10-10）：先人立、举起大沙拳从沙里升起（slam 帧 0，0.2 s），再一拳砸地（帧 1）——扬沙、冲击环、判定都在砸下那一刻；
    //   以前 slam 只有一张和 claw 帧 0 一样的举爪图，一出来就判定
    C.fx('stand_summon', { cid: 'fool', logical: 'slam', frame: 0, scale: 3, rise: 46, dur: 0.2,
      aura_colour: '#e8c070', flip: p.facing < 0 }, { follow: p, dx: 12, life: 0.24 });
    await C.wait(0.22);
    C.fx('stand_summon', { cid: 'fool', logical: 'slam', frame: 1, scale: 3, rise: 0, dur: 0.01,
      aura_colour: '#e8c070', flip: p.facing < 0 }, { follow: p, dx: 12, life: 0.63 });
    C.fx('burst', { x: p.x, y: p.y, n: 60, speed: 220, life: 0.9, colours: ['#e8c070', '#c89a50', '#fbe0a0'], gravity: 300, size: 2 });
    C.fx('shockwave', { x: p.x, y: p.y, r_max: 96, squash: 0.3, colour: '#e8c070', dur: 0.5 });
    C.word('ドドド', { wx: p.x, wy: p.y, wz: 50 });
    const hit = C.hitMove('IG_U');
    if (hit.length) { C.impact(['invert', 'purple'], f(2), f(2)); C.stopAll(f(12)); }
    await C.wait(0.6);
  }

  // ======================================================================= 敌人通用
  // 连打上限的反冲（规划 §3.6）：W1 12f，全身冲击环 r 40，伤 12，不可挡（能闪不能挡）
  M.BOSS_BURST = {
    slot: 'enemy', body: 'cmd', stand: 'punch', warn: { tier: 'W1', dur: f(12) }, dur: f(12 + 4 + 20), active: [f(12), f(16)],
    shape: { kind: 'circle', r: 40 }, depth: 40, dmg: 12, push: 30, guard: 'none', armor: true, sfxHit: 'punch_heavy',
    fxHit: 'heavy', accent: '#ffffff', sfx: 'whoosh', shake: [3, f(12)],
    onStart(e) { G.combat.fxAt('shockwave', { x: e.x, y: e.y - e.z - 18, r_max: 40, width: 3, dur: 0.35, colour: '#ffffff' }, e, f(12)); },
  };

  // ======================================================================= 序1 阿布德尔的试探（规划 §5.1.2）
  // 火球：W1 30f（红色魔术师 cast 帧 0 + 手上 glow + charge），30 / 弹道 / 20，从牢房右缘 (240, 承太郎的 y) 横飞，
  //   r 6、速度 160（放宽 −30%），伤 8；精准格挡 = 火球在白金之星手里捏灭（onParried 返回 true，不打回去）
  M.MR_FIREBALL = {
    slot: 'enemy', body: 'cmd', stand: 'cast', standDx: 0, warn: { tier: 'W1', dur: f(30), glow: '#ff8a30' },
    dur: f(50), active: [f(30), f(31)], melee: false, fireAt: [f(30)], sfx: 'charge', sfxVol: 0.5,
    shot: { kind: 'fireball', speed: 160, life: 3.0, r: 6, hitR: [7, 6, 18], dmg: 8, push: 8, guard: 'normal', reflect: false },
    shotFrom(e, ctx, t) { const W = G.world; const p = W.player; return { x: (ctx && ctx.data.fireX) || 240, y: p ? p.y : e.y, z: 18, dir: -1 }; },
    shotMod(e, ctx, s) { if (ctx && ctx.data.relax) s.speed *= 0.7; },
    fireSfx: { name: 'fire_burst', rate: 1.3, vol: 0.7 },
    onParried(att, def, ctx, info) {
      const s = info && info.shot;
      if (s) G.combat.fxAt('smoke', { x: s.x, y: s.y - s.z, n: 6, colour: '#8a8a98', life: 0.9, rise: 20 }, def);
      G.audio.sfx('fire_burst', { rate: 0.6, vol: 0.4 });
      return true;
    },
  };
  // 火柱：W2 45f（阿布德尔 aura_flame + ゴオオッ），45 / 90 / 30；覆盖整个场地（ctx.data.jetBox；序1 是铁栏外的走廊），每 10f 4（挡住 ×0.2）
  //   once: false 才会每 10f 判一次（hazard 默认 once，一道火柱只打一下，教学“挡住火柱”要挡满 5 道才过）；
  //   火焰画面在 onActive 里画：地面两排错开的火舌铺满场地 + 一道从红色魔术师手上喷出的胸口高火焰洪流
  //   （原来的 fxActive: 'fire_jet' 只拿到 x / y、没有 x0 / x1，一直画不出来）
  M.MR_FLAME_JET = {
    slot: 'enemy', body: 'cmd', stand: 'cast', warn: { tier: 'W2', dur: f(45), word: 'ゴオオッ' }, dur: f(45 + 90 + 30),
    active: [f(45), f(135)], melee: false, sfx: null,
    hazardAt: f(45),
    hazard(e, ctx, mv) {
      const d = (ctx && ctx.data) || {};
      const box = d.jetBox || [96, 240, 116, 142];
      const dur = d.relax || (d.jetCount || 0) >= 2 ? f(60) : f(90);
      return {
        shape: 'rect', x0: box[0], x1: box[1], y0: box[2], y1: box[3], warn: 0, dur, tick: f(10), once: false, dmg: 4, push: 4,
        guard: 'normal', fxWarn: null, sfx: 'fire', tag: 'flame_jet',
        onActive(h) {
          if (G.flash) G.flash(f(5), 0.5, '#ffc060');
          const fx = (n, kw) => G.combat.fxAt(n, kw, e, h.dur);
          for (let r = 0; r < 2; r++) {
            const y = r ? h.y1 - 7 : h.y0 + 9;
            for (let x = h.x0 + 12 + r * 11, i = 0; x <= h.x1 - 10; x += 22, i++) fx('fire', { x, y, w: 18, h: 16, seed: r * 13 + i });
          }
          fx('fire_jet', { x0: h.x1 + 8, x1: h.x0 + 4, y: (h.y0 + h.y1) / 2 - 22, thick: 0.9, seed: 3 });
        },
      };
    },
  };
  // 红色束缚：W3 40f（脚下红圈每 10f 脉冲），40 / 8 / 20；以承太郎为中心 r 20，6 + 缠住 60f，只能精准格挡
  M.MR_RED_BIND = {
    slot: 'enemy', body: 'cmd', stand: 'cast', warn: { tier: 'W3', dur: f(40) }, dur: f(40 + 8 + 20), active: [f(40), f(48)],
    melee: false, sfx: null, hazardAt: 0,
    hazard(e, ctx, mv) {
      const p = G.world.player;
      return {
        shape: 'ellipse', x: p ? p.x : e.x, y: p ? p.y : e.y, rx: 20, ry: 9, follow: p, followWarn: true,
        warn: G.combat.warnDur(mv, ctx), dur: f(8), dmg: 6, root: f(60), rootFx: 'firerope', guard: 'parryOnly', parry: true,
        fxWarn: 'zone_warn', warnColour: '#ff6020', sfx: 'fire', sfx2: 'vine', tag: 'red_bind', once: true,
      };
    },
  };
  K.e_avdol_test = {
    hp: 999, speed: 0, standId: 'magred', moves: ['MR_FIREBALL', 'MR_FLAME_JET', 'MR_RED_BIND'], untargetable: true,
    koStyle: 'none', idle: 'idle',
    // brain avdol_test：按 ctx.data.step 出招（1 不出、2 每 70f 火球、3 一次火柱（失败重来）、4 红色束缚、5 每 120f 火球、6 停手）
    brain(e, dt, ctx) {
      const d = ctx ? ctx.data : {};
      const m = e.mem;
      e.facing = -1;
      if (e.state !== 'idle' && e.state !== 'walk') return true;   // 出招中交给默认的招式更新
      const step = d.step || 1;
      if (m.lastStep !== step) { m.lastStep = step; m.gap = step === 2 ? 0.8 : step === 5 ? 1.2 : 0.6; }
      m.gap = (m.gap || 0) - dt;
      const p = G.world.player;
      if (!p || p.state === 'down' || m.gap > 0) return true;
      if (step === 2) { G.AI.tele(e, 'MR_FIREBALL'); m.gap = f(70); }
      else if (step === 3) {
        if (!d.jetActive) { G.AI.tele(e, 'MR_FLAME_JET'); m.gap = 1.6; }
      } else if (step === 4) { G.AI.tele(e, 'MR_RED_BIND'); m.gap = 1.6; }
      else if (step === 5) { G.AI.tele(e, 'MR_FIREBALL'); m.gap = f(120); }
      return true;
    },
  };

  // ======================================================================= 序2 被操纵的花京院（规划 §5.1.3）
  // 绿宝石水花：冷却 150f、权重 3；W2 45f；45 / 弹道 / 30；12 颗扇形 ±25°，速度 300，半径 3，每颗 4；精准格挡 = 宝石碎掉
  M.HG_SPLASH = {
    slot: 'enemy', body: 'cmd', stand: 'cast', standDx: 4, warn: { tier: 'W2', dur: f(45), glow: '#70ffb0', word: '绿宝石水花！' },
    dur: f(45 + 30), active: [f(45), f(46)], melee: false, from: 'stand', fireAt: [f(45)], cd: f(150), weight: 3, sfx: null,
    shot: { kind: 'gem', n: 12, spread: 25, speed: 300, life: 1.6, hitR: [3, 4, 18], dmg: 4, push: 4, guard: 'normal',
      reflect: false, colour: '#50ff9a', guardPush: 16 },
    fireSfx: { name: 'emerald' },
  };
  // 全力水花（阶段 3，剧情 phases[2].run 里用 G.AI.tele(e, 'HG_SPLASH_W6') 放）：W6 60f + 26 颗 ±24° 速度 320
  M.HG_SPLASH_W6 = Object.assign({}, M.HG_SPLASH, {
    warn: { tier: 'W6', dur: f(60), title: 'w6_hg_splash', portrait: 's04_kak_evil', colours: ['#1c6a40', '#0a3a20'] },
    dur: f(60 + 40), active: [f(60), f(61)], fireAt: [f(60)], cd: 0, weight: 0,
    shot: Object.assign({}, M.HG_SPLASH.shot, { n: 26, spread: 24, speed: 320, dmg: 4 }),
  });
  // 触须鞭：离法皇 ≤ 64、冷却 60f、权重 4；W1 24f；24 / 6 / 18；从法皇算 8–56 ±8；10 伤、击退 16；精准格挡 → 抓触须 QTE
  M.HG_WHIP = {
    slot: 'enemy', body: 'cmd', stand: 'punch', standDx: 6, warn: { tier: 'W1', dur: f(24) }, dur: f(48), active: [f(24), f(30)],
    from: 'stand', reach: [8, 56], depth: 8, dmg: 10, push: 16, cd: f(60), weight: 4, guard: 'normal',
    sfx: 'hiero_tentacle', sfxHit: 'punch', fxHit: 'light', accent: '#70ffb0', whip: true,
    cond(e, t) { const o = e.stand ? e.stand.origin() : e; return Math.abs(t.x - o.x) <= 64 && Math.abs(t.y - o.y) <= 14; },
    onParried(att, def, ctx) { grabTentacle(att, def, ctx); return true; },
  };
  // 触须陷阱：冷却 300f、权重 2、场上最多 1 组（阶段 2 起 2 组）；W3 60f；3 段 40 px 地面线，4 + 缠住 40f，不可挡
  M.HG_TRAP = {
    slot: 'enemy', body: 'cmd', stand: 'cast', warn: { tier: 'W3', dur: f(60) }, dur: f(60 + 10), active: [f(60), f(61)],
    melee: false, cd: f(300), weight: 2, sfx: null, hazardAt: 0,
    cond(e, t, ctx) {
      const n = G.world.hazards.filter((h) => h.tag === 'hg_trap' && h.owner === e && h.phase !== 'done').length / 3;
      return n < ((e.phaseI || 0) >= 1 ? 2 : 1);
    },
    hazard(e, ctx, mv) {
      const p = G.world.player;
      const x = p ? p.x : e.x, y = p ? p.y : e.y;
      const warn = G.combat.warnDur(mv, ctx);
      const segs = [[x - 20, y], [x - 56, y - 7], [x + 16, y + 7]];
      return segs.map(([sx, sy], i) => ({
        shape: 'rect', x0: sx, x1: sx + 40, y0: sy - 2, y1: sy + 2, warn, dur: f(240), dmg: 4, root: f(40), guard: 'none',
        once: true, consume: true, tag: 'hg_trap', fxWarn: 'tendrils_faint', fxActive: 'tendrils_line', sfx: i === 0 ? 'vine' : null,
        sfxRate: 1.2, colour: '#50e890',
      }));
    },
  };
  M.HG_BACKSTEP = { slot: 'enemy', body: 'walk', dur: f(40), active: [99, 99], melee: false, sfx: 'whoosh' };
  // 抓触须 QTE：成功 = 法皇和花京院 0.13 s 被拽到承太郎身前 30 px、晕 120f、韧性清零、受伤 ×1.5；失败 = 挣脱、换位
  async function grabTentacle(e, p, ctx) {
    const S = G.S;
    if (!S || !p) return;
    G.uifx.sfx('ガシッ', p, { jitter: 2 });
    G.audio.sfx('hiero_tentacle', { vol: 0.9 });
    e.state = 'x_grabbed'; e.stateT = 0; e.atk = null; e.tele = null;
    let ok = false;
    try {
      const q = S.timing ? S.timing({ label: '扯回来！（J）', speed: 1.0, zone: [0.36, 0.64], tries: 2 })
        : G.ui.startQte({ type: 'timing', label: '扯回来！（J）', speed: 1.0, zone: [0.36, 0.64], tries: 2 });
      ok = !!(await q);
    } catch (err) { ok = false; }
    if (ctx && ctx.emit) ctx.emit('qte', { type: 'timing', result: ok });
    G.dbg.ev('qte', { type: 'timing', result: ok });
    if (!G.world.fight || e.dead) return;
    if (ok) {
      const tx = p.x + p.facing * 30;
      G.audio.sfx('whoosh', { rate: 0.8 });
      G.shake(2, 0.2);
      G.combat.fxAt('speedlines', { cx: 160, cy: 90, style: 'horizontal', n: 30, inner: 8, alpha: 0.7 }, p, 0.15, { space: 'canvas' });
      await G.combat.tweenTo(e, tx, p.y, 0.13);
      e.facing = -p.facing;
      e.poise = 0;
      e.state = 'broken'; e.stateT = 0; e.breakT = f(120); e.mem.breakMul = 1.5;
      G.uifx.sfx('破绽！', e, { jitter: 2 });
    } else {
      e.state = 'idle';
      G.AI.blink(e, G.clamp(p.x + (p.x < 200 ? 120 : -120), (ctx && ctx.spec.arena[0] + 20) || 20, (ctx && ctx.spec.arena[1] - 20) || 300), e.y, { word: null });
    }
  }
  K.e_kakyoin = {
    hp: 600, poiseMax: 50, speed: 66, standId: 'hiero', idle: 'possessed', standPos: { dx: 20, z: 10, link: 'tendril' },
    moves: ['HG_SPLASH', 'HG_WHIP', 'HG_TRAP'], koStyle: 'none',
    // brain kakyoin_kite：保持 90–140 px；56 px 内以 70 px/s 后撤 40f；每 180f（阶段 2：120f）换站位；同时只出一招；阶段 3 交给剧情
    brain(e, dt, ctx) {
      const m = e.mem, p = G.world.player;
      if (!p) return true;
      const ph = e.phaseI || 0;
      if (ph >= 2 && !(ctx && ctx.data.kakFight)) {           // 阶段 3：站定，等剧情放 W6
        if (e.state === 'idle' || e.state === 'walk') { e.play(e.idleAnim); e.facing = p.x > e.x ? 1 : -1; }
        return e.state === 'idle' || e.state === 'walk';
      }
      if (e.state === 'x_back') {
        G.world.move(e, m.backDir * 70 * dt, 0);
        e.play('walk');
        if (e.stateT >= f(40)) { e.state = 'idle'; m.repos = Math.max(m.repos || 0, 0.6); }
        return true;
      }
      if (e.state === 'x_grabbed') return true;
      if (e.state !== 'idle' && e.state !== 'walk') return false;
      m.reposT = (m.reposT == null ? f(180) : m.reposT) - dt;
      m.splash2 = m.splash2 || 0;
      if (m.splash2 > 0) { m.splash2 -= dt; if (m.splash2 <= 0 && G.combat.tokens() < 2) { G.AI.use(e, 'HG_SPLASH', { skipWarn: false }); return true; } }
      const dx = p.x - e.x, adx = Math.abs(dx);
      e.facing = dx > 0 ? 1 : -1;
      if (adx < 56 && Math.abs(p.y - e.y) < 20 && (m.backCd || 0) <= 0) {   // HG_BACKSTEP
        e.state = 'x_back'; e.stateT = 0; m.backDir = dx > 0 ? -1 : 1; m.backCd = 1.2;
        G.audio.sfx('whoosh', { vol: 0.6 });
        G.combat.ghostBurst(e, 3);
        return true;
      }
      m.backCd = (m.backCd || 0) - dt;
      if (m.reposT <= 0) {                                      // 换站位：走到场地另一侧的随机点
        m.reposT = ph >= 1 ? f(120) : f(180);
        const ar = ctx ? ctx.spec.arena : [0, 320];
        const left = p.x > (ar[0] + ar[1]) / 2;
        m.goal = [left ? G.rand(ar[0] + 20, ar[0] + 100) : G.rand(ar[1] - 100, ar[1] - 20), G.rand(G.world.stage.yMin + 2, G.world.stage.yMax - 2)];
      }
      let gx, gy;
      if (m.goal) { gx = m.goal[0]; gy = m.goal[1]; if (Math.hypot(gx - e.x, gy - e.y) < 4) m.goal = null; }
      else {
        const want = adx < 90 ? e.x - Math.sign(dx || 1) * 30 : adx > 140 ? e.x + Math.sign(dx) * 30 : e.x;
        gx = want; gy = p.y;
      }
      G.combat.walkTo(e, gx, gy, dt, e.speed);
      if (G.combat.tokens() < 1 && e.cool <= 0) {
        const id = G.AI.pickMove(e, ctx);
        if (id) {
          G.AI.tele(e, id);
          e.cool = G.rand(0.5, 0.9);
          if (id === 'HG_SPLASH' && ph >= 1) m.splash2 = M.HG_SPLASH.dur + f(20);   // 阶段 2：连放两次（间隔 20f）
        }
      }
      return true;
    },
  };

  // ======================================================================= 第 1 战 灰塔（规划 §5.2.2）
  // 针刺：W1 20f（嘴里 glint）→ 冲刺 64 px（10f）；伤 8（段 A）/ 10（段 B）
  M.TG_NEEDLE = {
    slot: 'enemy', body: 'idle', stand: null, warn: { tier: 'W1', dur: f(20) }, dur: f(20 + 10 + 14), active: [f(20), f(30)],
    melee: false, dash: { dist: 64, time: f(10), w: 7 }, dmg: 8, push: 8, guard: 'normal', sfxHit: 'stab', fxHit: 'light',
    accent: '#e0e8f8', sfx: 'whoosh', sfxRate: 1.6, cd: f(90),
    cond(e, t) { return Math.abs(t.x - e.x) <= 64 && Math.abs(t.y - e.y) < 16; },
  };
  // 段 B 的针只刺花京院（规划 §5.2.2 表）：目标由 brain 显式给玩家，乘客另有保护，避免冲刺误伤座位上的人
  M.TG_NEEDLE_B = Object.assign({}, M.TG_NEEDLE, { dmg: 10, cond(e) { const p = G.world.player; return !!p && Math.hypot(p.x - e.x, p.y - e.y) <= 48; } });
  // 扑向乘客：W4 66f（贝塞尔红线到乘客头部 + insect_buzz 升调），沿线 300 px/s 俯冲；乘客倒下；被精准格挡 → 晕 30f（不算缠住）
  //   规划写 36f；真人从看到红线到走上去连按三下 J 要 1 s 左右，36f 来不及，放宽到 66f（偏离规划 §5.2.2 的数值）
  M.TG_DIVE = {
    slot: 'enemy', body: 'idle', stand: null, warn: { tier: 'W4', dur: f(66), path: (e, ctx) => e.mem.divePath }, dur: f(66) + 3,
    active: [f(66), f(66) + 3], melee: false, diveAlongPath: 300, dmg: 30, push: 0, guard: 'normal', sfxHit: 'stab',
    fxHit: 'light', accent: '#e0e8f8', sfx: 'whoosh', sfxRate: 1.4,
    onParried(att, def, ctx) {
      att.state = 'hurt'; att.stateT = 0; att.stunT = f(30); att.atk = null; att.tele = null;
      att.mem.dash = null; att.mem.stunnedFly = true;
      G.uifx.sfx('キィン！', def, { jitter: 2 });
      return true;
    },
  };
  // 开场第一次扑击：红线 2 s，给玩家一次从容的“走上红线铺网”（规划 §5.2.2 时间线建议）
  M.TG_DIVE_FIRST = Object.assign({}, M.TG_DIVE, { warn: Object.assign({}, M.TG_DIVE.warn, { dur: f(120) }), dur: f(120) + 3, active: [f(120), f(120) + 3] });
  function towerFlit(e, dt, ctx, m) {
    m.flitT = (m.flitT || 0) - dt;
    const p = G.world.player;
    const st = G.world.stage;
    if (m.flitT <= 0 || !m.goal) {
      m.flitT = f(30);
      const cx = p ? p.x : e.x;
      const ar = ctx ? ctx.spec.arena : [st.x0, st.x1];
      m.goal = [G.clamp(cx + G.rand(-80, 80), ar[0] + 8, ar[1] - 8), G.rand(st.yMin + 1, st.yMax - 1)];
    }
    const dx = m.goal[0] - e.x, dy = m.goal[1] - e.y, d = Math.hypot(dx, dy);
    if (d > 1) {
      const sp = Math.min(e.speed, d * 6) * dt;
      e.x += (dx / d) * sp; e.y = G.clamp(e.y + (dy / d) * sp * 0.6, st.yMin, st.yMax);
      e.facing = dx > 0 ? 1 : -1;
    }
  }
  K.e_towergray_a = {
    hp: 300, speed: 240, moves: ['TG_NEEDLE'], koStyle: 'none', bodyW: 3, fly: { z: 24, bob: 6 }, pivot: 'center', idle: 'idle',
    evadeWord: '它躲开了！',
    dmgMul: () => 0,
    onHitBy(e) { return 'evade'; },
    brain(e, dt, ctx) {
      const m = e.mem, p = G.world.player;
      if (!p) return true;
      const th = G.AI.threat(e, p);
      if (th >= 0 && th <= f(6) && (m.blinkCd || 0) <= 0) {   // 判定碰到它之前 6f：瞬移 12 px +「它躲开了！」
        const dir = Math.random() < 0.5 ? -1 : 1;
        G.AI.blink(e, e.x + dir * 12 + (p.facing * 10), e.y + G.rand(-4, 4), { word: e.evadeWord });
        m.blinkCd = f(8);
        return true;
      }
      m.blinkCd = (m.blinkCd || 0) - dt;
      if (e.state !== 'idle' && e.state !== 'walk') return false;
      towerFlit(e, dt, ctx, m);
      if (e.cool <= 0 && G.combat.tokens() < 2) {
        const id = G.AI.pickMove(e, ctx);
        if (id) { G.AI.tele(e, id); e.cool = G.rand(0.8, 1.4); }
      }
      return true;
    },
  };
  // 段 B 的规则（真人试玩后定的数值，规划 §5.2.2 的意思不变）：
  //   · 平时在过道上空高飞（z 24），触须网藏在座椅下面够不着它；只有扑向乘客（红线预警 → 俯冲）和刺花京院时飞低，才会撞进网里
  //   · 缠住 2 s（规划 45f 太短，真人看到“缠住了！”再出手已经挣脱）：掉到过道地面挣扎，这时攻击全部命中；
  //     每缠住一次给花京院 +20 能量，攒满后趁缠住放绿宝石水花（原著：触须网里的近距离水花）
  //   · 挣脱后 1 s 内不再被网缠住
  K.e_towergray = {
    hp: 300, poiseMax: 0, speed: 240, moves: ['TG_NEEDLE_B'], koStyle: 'none', bodyW: 3, fly: { z: 24, bob: 6 }, pivot: 'center',
    idle: 'idle', evadeWord: '它躲开了！',
    rootTime: f(120), rootBonus: 20,
    // 没被缠住时所有攻击都躲开；「它躲开了！」0.8 s 最多冒一次（一把宝石 3 颗，每颗都冒字会叠成一团看不清）
    onHitBy(e, att, move, info) {
      if (e.rootT > 0) return null;
      const now = G.clk.world, show = now - (e.mem.evadeShown == null ? -9 : e.mem.evadeShown) > 0.8;
      if (show) e.mem.evadeShown = now;
      e.evadeWord = show ? '它躲开了！' : null;
      return 'evade';
    },
    targetPick(e, ctx) {
      const vs = G.world.allies().filter((a) => a.vip && a.state !== 'down');
      return vs.length ? vs : null;
    },
    brain(e, dt, ctx) {
      const m = e.mem, K0 = K.e_towergray;
      const W = G.world, p = W.player;
      if (!m.buzz && G.audio.loop) { m.buzz = G.audio.loop('insect_buzz_loop', { vol: 0.35 }); }
      // 刚被缠住：缠住 2 s、掉到过道地面（x, 160）挣扎；挣脱后 60f 内网不再缠
      if (e.rootT > 0) {
        if (!m.rooted) {
          m.rooted = true; e.rootT = Math.max(e.rootT, K0.rootTime); e.rootImmuneT = e.rootT + f(60);
          e.atk = null; e.tele = null; m.dash = null; e.ghostOn = false;
          e.state = 'x_tangled'; e.stateT = 0; m.flyZ = 24;
          if (e.fly) e.fly = Object.assign({}, e.fly, { z: 0, bob: 0 });
          e.y = G.clamp(160, W.stage.yMin, W.stage.yMax);
          e.frozen = 0;
          if (m.buzz) m.buzz.setRate(0.8);
          if (p) G.combat.gainEnergy(p, K0.rootBonus, 'net');
          // 缠绕的丝线由剧情在地图像素层画（ch01 drawNets）；拟声字用现成的法皇绿「ギュルッ」
          G.uifx.sfx('ギュルッ', e, { jitter: 1.5 });
          G.audio.sfx('hiero_tentacle', { vol: 0.8 });
          m.catches = (m.catches || 0) + 1;
          if (ctx) ctx.emit('netCatch', { e, n: m.catches });
        }
        e.x += Math.floor(e.stateT * 10) % 2 ? 1 : -1;   // 每 6f 抖 1 px
        return true;
      }
      if (m.rooted) {
        m.rooted = false; e.frozen = null; e.state = 'idle'; e.play(e.idleAnim || 'idle');
        if (m.buzz) m.buzz.setRate(1.0);
      }
      // 平时高飞：网够不着（rootImmuneT 每帧续一点；预警和俯冲时 brain 不在这条路上，免疫两帧内自然消掉）
      const flying = e.state === 'idle' || e.state === 'walk' || (e.state === 'hurt' && m.stunnedFly);
      if (flying) {
        e.rootImmuneT = Math.max(e.rootImmuneT || 0, f(3));
        if (e.fly && e.fly.z !== 24) e.fly = Object.assign({}, e.fly, { z: 24, bob: 6 });
      }
      if (e.state === 'hurt' && m.stunnedFly) { if (e.stunT <= 0) { m.stunnedFly = false; e.state = 'idle'; } return true; }
      if (e.state !== 'idle' && e.state !== 'walk') return false;
      towerFlit(e, dt, ctx, m);
      m.diveT = (m.diveT == null ? (ctx && ctx.data.firstDiveAt != null ? ctx.data.firstDiveAt : 2.5) : m.diveT) - dt;
      const tokens = G.combat.tokens();
      if (m.diveT <= 0 && tokens < 2) {
        const vs = W.allies().filter((a) => a.vip && a.state !== 'down');
        if (vs.length) {
          let tg, id = 'TG_DIVE';
          if (!m.firstDone) {   // 开场第一次：红线固定穿过过道 x 220–300（挑离 260 最近的乘客，从过道前侧飞过去）
            m.firstDone = true; id = 'TG_DIVE_FIRST';
            tg = vs.reduce((b, v) => (Math.abs(v.x - 260) < Math.abs(b.x - 260) ? v : b));
            e.x = G.clamp(tg.x + 70, W.stage.x0 + 10, W.stage.x1 - 10); e.y = W.stage.yMax - 1;
          } else {
            // 之后扑离它最近的三个乘客之一：红线总在花京院附近，走得过去
            const near = vs.slice().sort((a, b) => Math.abs(a.x - e.x) - Math.abs(b.x - e.x)).slice(0, 3);
            tg = G.pick(near);
          }
          const yh = tg.y, x1 = tg.x;
          const cx = (e.x + x1) / 2 + G.rand(-20, 20), cy = Math.max(e.y, W.stage.yMax) + 6;
          m.divePath = [[e.x, e.y], [cx, cy], [x1, yh]];
          m.diveTarget = tg;
          G.AI.tele(e, id, { target: tg });
          if (e.fly) e.fly = Object.assign({}, e.fly, { z: 10, bob: 2 });   // 飞低：撞得进网
          if (m.buzz) { m.buzz.setRate(1.0); m.rateUp = 0; }
          m.diveT = f(270);
          return true;
        }
      }
      // 针：只刺 48 px 内的花京院
      if (p && e.cool <= 0 && tokens < 2 && !(e.moveCd.TG_NEEDLE_B > 0) && M.TG_NEEDLE_B.cond(e)) {
        G.AI.tele(e, 'TG_NEEDLE_B', { target: p });
        if (e.fly) e.fly = Object.assign({}, e.fly, { z: 14, bob: 2 });
        e.cool = G.rand(0.8, 1.4);
      }
      return true;
    },
    onWarnTick(e, u) { if (e.mem.buzz && e.tele && /^TG_DIVE/.test(e.tele.move)) e.mem.buzz.setRate(1.0 + 0.5 * u); },
  };

  // ======================================================================= 第 2 战 银色战车（规划 §5.2.3）
  // 三连刺：距离 ≤ 64、冷却 70f、权重 4；W1 24f；每刺 6 / 3 / 4 共 3 刺；从本体 8–56 ±6；每刺 8；刺穿；每刺单独判弹反
  //   真人试玩调整（偏离规划 §5.2.3 的数值）：触发距离 ≤ 64 → ≤ 56（判定 8–56 加身宽本来就够到 62，站在中距离一直被戳）、
  //   第三刺后多收招 18f → 30f（收招就是打他的空档：规划“收招时不架剑”，18f 真人看到第三刺结束再按 J 已经来不及）、冷却 70f → 90f、
  //   预警 24f → 30f（看到剑尖闪光到第一刺 0.6 s，真人来得及闪 / 挡）、权重 4 → 3（原来十招里六招是三连刺）
  //   被弹反（任意一刺）：他硬直 30f，之后再空 0.7 s 不举剑（openAt），给弹反的人一套 J1–J3 + 连打的追击
  const chariotParried = (att) => { if (att && att.mem) att.mem.openAt = G.clk.world + f(30); };
  M.SC_TRIPLE = {
    slot: 'enemy', body: 'cmd', stand: 'punch', standDx: 14, warn: { tier: 'W1', dur: f(30), glintTip: true },
    dur: f(30 + 39 + 30), active: [f(36), f(65)], windows: [[f(36), f(39)], [f(49), f(52)], [f(62), f(65)]],
    standSeqs: [[f(30), [[0, f(34)], [2, f(36)], [1, f(43)]]], [f(43), [[0, f(47)], [2, f(49)], [1, f(56)]]], [f(56), [[0, f(60)], [2, f(62)], [1, 99]]]],
    from: 'body', reach: [8, 56], depth: 6, dmg: 8, push: 8, guard: 'pierce', parryBreak: true, range: [0, 56], cd: f(90), weight: 3,
    sfx: null, sfxEach: ['slash0', 'slash1', 'slash0'], sfxHit: 'punch', fxHit: 'light', accent: '#9cc8ff',
    onParried: chariotParried,
  };
  // 突进刺：距离 64–160、冷却 150f、权重 2；W4 36f 直线；36 / 10（冲 96 px）/ 20；冲刺路径 ±6；16、击退 30；刺穿
  //   收招 20f → 40f（冲过头收不住剑：横向让开红线以后，转身就能打他一套；原来 20f 真人反应不过来）
  M.SC_LUNGE = {
    slot: 'enemy', body: 'cmd', stand: 'punch', standDx: 20, warn: { tier: 'W4', dur: f(36) }, dur: f(36 + 10 + 40),
    // 距离下限 64 → 56：三连刺改成 ≤ 56 触发后，56–64 之间两招都够不上，站在那里他会一直发呆
    active: [f(36), f(46)], melee: false, dash: { dist: 96, time: f(10), w: 6, line: true }, dmg: 16, push: 30, guard: 'pierce',
    range: [56, 160], cd: f(150), weight: 2, sfx: 'stab', sfxHit: 'slash0', fxHit: 'heavy', accent: '#9cc8ff', ghostDash: true,
    onParried: chariotParried,
  };
  // 横斩：距离 ≤ 48、冷却 90f、权重 2；W1 24f；24 / 4 / 14 → 24（同三连刺：收招留出还手的空档）；6–48 ±10；12
  M.SC_SLASH = {
    slot: 'enemy', body: 'cmd', stand: 'slash', standDx: 12, warn: { tier: 'W1', dur: f(24), glintTip: true }, dur: f(24 + 4 + 24),
    active: [f(24), f(28)], from: 'body', reach: [6, 48], depth: 10, dmg: 12, push: 12, guard: 'normal', range: [0, 48],
    cd: f(90), weight: 2, sfx: 'slash1', sfxHit: 'punch', fxHit: 'light', accent: '#9cc8ff', slashArc: 15,
    onParried: chariotParried,
  };
  // 架剑（规划 §5.2.3）只在他站着（idle / walk）时算数：出招预警、出招、收招、受击、破绽、卡住石像时一律不架。
  //   旧写法只看 mem.stance：受击 / 预警时 brain 不跑，标志一直留着——地火刚烧中他、他正后拉蓄势时，紧跟的拳头照样被弹开、
  //   火照样被劈开，真人觉得判定不讲理；而且挨打一结束马上又举剑，J3 火球、连打总被劈开，追击打不出来
  const STANCE_OUTLINE = '#c8d8ff';
  const CHARIOT_OPEN_T = 0.7;   // 挨打（或被弹反硬直结束）以后多久不举剑：追击的空档
  const stanceUp = (e) => !!(e.mem.stance && (e.state === 'idle' || e.state === 'walk'));
  // 正面的火被劈开：剑光 + 「被劈开了！」（0.4 s 最多冒一次，连打每 6f 一击不会叠成一团）
  function chariotCutFx(e, x, y) {
    const now = G.clk.world;
    if (now - (e.mem.cutT == null ? -9 : e.mem.cutT) <= 0.4) return;
    e.mem.cutT = now;
    G.combat.fxAt('slash_arc', { x: x == null ? e.x + e.facing * 14 : x, y: y == null ? e.y - 28 : y, size: 15, flip: Math.random() < 0.5 }, e, 0.15);
    G.uifx.sfx('被劈开了！', e, { jitter: 1.5 });
    G.audio.sfx('slash', { vol: 0.6 });
  }
  K.e_polnareff = {
    hp: 900, poiseMax: 70, speed: 70, standId: 'chariot', idle: 'fight', moves: ['SC_TRIPLE', 'SC_LUNGE', 'SC_SLASH'],
    koStyle: 'none',
    onShotNear(e, s, ctx) {
      if (!stanceUp(e) || s.fromGround || !s.cuttable) return;
      if ((s.x - e.x) * e.facing < 0) return;   // 不是正面来的
      if (G.AI.cut(e, s)) e.mem.cuts = (e.mem.cuts || 0) + 1;   // 剧情据此提示一次“火被劈开了”
    },
    onHitBy(e, att, move, info) {
      if (!att || !move) return null;
      const front = (att.x - e.x) * e.facing >= 0;
      const fire = move.cuttable && !move.fromGround;
      // 剑之结界（阶段 4）：左右来的安卡都被劈开（规划“4 个安卡全被切开”），只有地底下来的火切不到
      if ((e.phaseI || 0) >= 3 && fire && info && info.shot) {
        chariotCutFx(e, info.shot.x, info.shot.y - (info.shot.z || 0));
        info.shot.dead = true;
        return 'evade';
      }
      if (stanceUp(e) && front) {
        // 架剑中正面的拳头（J1 / J2）100% 弹开；连打火焰 / 终结爆炎 100% 劈开（规划：架剑期间正面的火 100% 切开）
        if (info && (info.slot === 'J1' || info.slot === 'J2')) { e.mem.parries = (e.mem.parries || 0) + 1; return 'parry'; }
        if (fire) { e.mem.cuts = (e.mem.cuts || 0) + 1; chariotCutFx(e); return 'evade'; }
      }
      // 真的挨打了：之后 0.7 s 不举剑。重击（击退 ≥ 24 / 浮空）会把他打倒：倒地 24f + 30f 期间有无敌，从爬起来再算 0.7 s，
      //   不然 J3 火球把他打倒、连打火焰穿过倒地的他，他一爬起来就举剑，后面的连打全被劈开
      e.mem.openAt = G.clk.world + ((move.push || 0) >= 24 || move.launch ? f(24 + 30) : 0);
      return null;
    },
    // 出招预警的第一帧：放下架剑（描边、举剑、剑尖闪光撤掉），替身后拉蓄势 + 剑尖一闪（规划“剑尖 glint”；原来 glintTip 没人读）
    onWarnTick(e) {
      const m = e.mem;
      if (!e.tele || m.teleSeen === e.tele) return;
      m.teleSeen = e.tele; m.stance = false; m.stanceT = 0;
      if (e.outline === STANCE_OUTLINE) e.outline = null;
      if (e.stand) { e.stand.act('punch', { dx: 4, seq: [[0, 99]], hold: true }); m.pulledBack = true; }
      const sx = e.stand ? e.stand.x : e.x, sz = (e.z || 0) + (e.stand ? e.stand.z : 0);
      G.combat.fxAt('glint', { x: sx + e.facing * 22, y: e.y - sz - 34, size: 10, dur: 0.3 }, e, 0.3);
    },
    brain(e, dt, ctx) { return chariotBrain(e, dt, ctx); },
  };
  function chariotBrain(e, dt, ctx) {
    const m = e.mem, W = G.world, p = W.player;
    if (!p) return true;
    const ph = e.phaseI || 0, ck = (G.D && G.D.ck) || 1;   // 0 = 阶段 1；1 = 阶段 2（石像）；2 = 阶段 3（脱甲）；3 = 阶段 4（剑之结界后）
    // 阶段切换时一次性的变化（台词 / 过场在剧情 phases[].run）
    if (m.ph !== ph) {
      const prev = m.ph == null ? 0 : m.ph;
      m.ph = ph;
      if (ph >= 2 && prev < 2) {   // 脱甲：stand.skin 'bare'、速度 ×1.8、前摇 −2f、2 个残影
        if (!m.baseSpeed) m.baseSpeed = e.speed;
        e.speed = m.baseSpeed * 1.8;
        e.skin = null;
        if (e.stand) e.stand.skin = 'bare';
        m.startupMinus = f(2);
        G.audio.sfx('armor_off');
        G.combat.fxAt('burst', { x: e.x, y: e.y - 30, n: 18, speed: 110, life: 0.7, colours: ['#c8d8ff', '#ffffff', '#8890b0'], gravity: 180 }, e);
        if (G.D.props && G.D.props.chariot_armor) {
          for (let i = 0; i < 4; i++) G.combat.fxAt('burst', { x: e.x + e.facing * 6, y: e.y - 34, n: 2, speed: 120, life: 0.8, colours: ['#d8e0ff'], gravity: 300, angle: 90 + (i - 1.5) * 30, spread: 20 }, e);
        }
        m.clones = G.AI.clones(e, 2, { dmgMul: 0.5, word: '残像！' });
        // 残像被打：「残像！」0.6 s 冒一次，不再同时冒默认的「它躲开了！」（地火站在残像身上时每帧都判一次，字会叠成一团）
        m.clones.forEach((c, i) => {
          c.evadeWord = null;
          c.onHitBy = (t) => { const now = G.clk.world; if (now - (t.mem.wordAt == null ? -9 : t.mem.wordAt) > 0.6) { t.mem.wordAt = now; G.uifx.sfx('残像！', t); } return 'evade'; };
          c.brain = chariotClone(e, i);
          c.idleAnim = e.idleAnim; c.alpha = 0.7;
          // 残像的替身也是脱了甲的样子（原来新建的替身没有 skin，三个人里只有真身是细长的银色骨架）
          if (c.stand) { c.stand.skin = 'bare'; c.stand.alpha = 0.6; c.stand.summon({ sfx: false }); }
        });
      }
      if (ph >= 3 && prev < 3) {   // 剑之结界：站到中央不动、给阿布德尔能量 +50；之后一直架剑
        (m.clones || []).forEach((c) => { c.remove = true; });
        m.clones = null;
        const ar = ctx ? ctx.spec.arena : [16, 304];
        m.center = (ar[0] + ar[1]) / 2;
        if (!m.barrierGiven) { m.barrierGiven = true; G.combat.gainEnergy(p, 50, 'barrier'); }
        e.minHp = Math.max(e.minHp || 0, 1);
        G.combat.fxAt('slash_arc', { x: e.x, y: e.y - 28, size: 22 }, e, 0.3);
      }
    }
    // 刺进石像：卡住 = 破绽 1.2 s（规划“卡住 60f、受伤 ×1.5、韧性清零”）。用 combat 的 broken 状态：
    //   原来的 x_stuck 一挨打就切成普通受击，第一拳之后卡住就结束了；broken 期间挨打不打断、伤害按 breakMul 算
    if (e.state === 'x_stuck') {
      m.stance = false; m.wasAtk = false; m.statueStuck = (m.statueStuck || 0) + 1;
      e.atk = null; e.tele = null; e.poise = 0; e.breakT = 1.2; m.breakMul = 1.5;
      e.state = 'broken'; e.stateT = 0; e.play('hurt');
      if (e.outline === STANCE_OUTLINE) e.outline = null;
      if (e.stand && e.stand.mode !== 'hidden') e.stand.act('hurt', { dx: -6, hold: true });
      m.openAt = G.clk.world + 1.2;   // 卡住结束后照样再空 0.7 s
      G.uifx.sfx('破绽！', e, { jitter: 2 });
      G.combat.fxAt('sparkles', { x: e.x, y: e.y - 48, n: 4, radius: 8, colour: '#ffd83c', period: 0.5 }, e, 1.2);
      return true;
    }
    const busy = e.state !== 'idle' && e.state !== 'walk';
    const now = G.clk.world, open = now - (m.openAt == null ? -99 : m.openAt) < CHARIOT_OPEN_T;
    const stanceDur = ph >= 3 ? 99 : ph >= 2 ? 1.3 : 1.0;
    // 架剑的节奏：出招 → 收招 → 举剑（阶段 1 1.0 s / 阶段 3 1.3 s / 阶段 4 一直举）→ 举完才出下一招。
    //   挨打 / 被弹反后先空 0.7 s（追击的空档），再举剑。brain 在预警、受击时不跑，所以“出过招”记在 attack 状态里
    if (busy) { m.stance = false; if (e.state === 'attack') m.wasAtk = true; }
    else {
      if (m.wasAtk) { m.wasAtk = false; m.stanceT = stanceDur; e.cool = Math.max(e.cool, Math.min(stanceDur, 1.6) + G.rand(0.15, 0.4)); }
      if (open) { m.stance = false; m.reraise = true; }
      else {
        if (m.reraise) { m.reraise = false; m.stanceT = stanceDur; e.cool = Math.max(e.cool, Math.min(stanceDur, 1.6) * 0.8 + G.rand(0.1, 0.3)); }
        if (ph >= 3) m.stanceT = 99;
        m.stanceT = (m.stanceT || 0) - dt;
        m.stance = m.stanceT > 0;
      }
    }
    if (m.stance) {
      if (e.stand) { if (e.stand.pose !== 'block' || e.stand.mode !== 'act') e.stand.act('block', { dx: 12, hold: true }); }
      m.pulledBack = false;
      e.outline = STANCE_OUTLINE;
      m.glintT = (m.glintT || 0) - dt;
      if (m.glintT <= 0) {   // 剑尖每 0.25 s 一闪：举剑帧的剑尖在替身 x + 朝向 12、离地 54 px
        m.glintT = 0.25;
        const sx = e.stand ? e.stand.x : e.x, sz = (e.z || 0) + (e.stand ? e.stand.z : 0);
        G.combat.fxAt('glint', { x: sx + e.facing * 12, y: e.y - sz - 54, size: 5, dur: 0.2 }, e, 0.22);
      }
    } else {
      if (e.outline === STANCE_OUTLINE) e.outline = null;
      if (!busy && e.stand && e.stand.mode === 'act' && (e.stand.pose === 'block' || e.stand.pose === 'hurt' || m.pulledBack)) { e.stand.idle(); m.pulledBack = false; }
    }
    if (busy) return false;
    const dx = p.x - e.x, adx = Math.abs(dx);
    e.facing = dx > 0 ? 1 : -1;
    // 阶段 2：石像诱饵（阿布德尔站在石像左侧 20 px 内、石像挡在两人中间）→ SC_LUNGE 先刺石像
    if (ph === 1 && !m.statueUsed) {
      const stt = statueOf(ctx);
      if (stt && p.x <= stt.x && p.x >= stt.x - 20 && e.x > stt.x) {
        // 突进刺只冲 96 px：离石像太远时先走近（原来在远处出招，冲不到石像，诱饵白站）
        if (e.x - stt.x > 90) { G.combat.walkTo(e, stt.x + 72, p.y, dt, e.speed); return true; }
        if (!open && e.cool <= 0 && G.combat.tokens() < 2) {
          m.statueLunge = stt;
          G.AI.tele(e, 'SC_LUNGE');
          e.cool = G.rand(0.6, 1.0);
          return true;
        }
      }
    }
    if (ph >= 3) {   // 阶段 4：站在场地中央举剑不动；64 px 内三连刺，否则站定 2.5 s 一次突进刺（冲出去以后走回中央）
      const home = m.center == null || Math.abs(e.x - m.center) <= 2;
      if (!home) G.combat.walkTo(e, m.center, e.y, dt, e.speed);
      else { e.play(e.idleAnim); m.lungeT = (m.lungeT == null ? 1.2 : m.lungeT) - dt; }
      if (!open && G.combat.tokens() < 2) {
        if (adx <= 64 * ck && Math.abs(p.y - e.y) < 12 && (e.moveCd.SC_TRIPLE || 0) <= 0) { G.AI.tele(e, 'SC_TRIPLE'); e.moveCd.SC_TRIPLE = f(50); }
        else if (home && m.lungeT <= 0) { m.lungeT = 2.5; G.AI.tele(e, 'SC_LUNGE'); }
      }
      return true;
    }
    // 平时：不架剑时保持 40–110 px；架剑时站定（举剑不走动，地火打得中）
    if (!m.stance) {
      const keep = adx > 110 ? 1 : adx < 36 * ck ? -1 : 0;
      const gx = e.x + keep * Math.sign(dx || 1) * 20, gy = p.y;
      if (keep !== 0 || Math.abs(gy - e.y) > 3) G.combat.walkTo(e, gx, gy, dt, e.speed);
      else e.play(e.idleAnim);
    } else e.play(e.idleAnim);
    if (!open && e.cool <= 0 && G.combat.tokens() < 2) {
      const id = G.AI.pickMove(e, ctx);
      // 出招间隔：真人试玩时 0.6–1.1 s 太密（刚格挡完下一招已经来了，地火都来不及放），阶段 1–2 放宽到 0.8–1.3 s，脱甲后 0.5–0.9 s
      //   （收招后还会被“举剑时长”顶到更晚，见上）
      if (id) { G.AI.tele(e, id); e.cool = ph >= 2 ? G.rand(0.5, 0.9) : G.rand(0.8, 1.3); }
      // 近战缩小而突进范围不缩时会出现空档；继续走到缩小后的近战距离，避免对静止玩家挥空。
      else if (!m.stance && adx > 50 * ck && adx < 64) G.combat.walkTo(e, p.x - Math.sign(dx || 1) * 44 * ck, p.y, dt, e.speed);
    }
    return true;
  }
  // 残像（阶段 3）：跟在真身左右 24 px、纵深错开 6 px（看着像一个人分成三个），一直面朝玩家；
  //   真身没在出招、离玩家够近时才偶尔出招（冷却 1.6–2.4 s）。原来残像走默认 AI，三个人轮流贴脸出招，被逼进角落就是一套连死
  function chariotClone(real, i) {
    return (c, dt, ctx) => {
      if (!dt) return true;
      const p = G.world.player, st = G.world.stage;
      if (!p || !st || real.remove || real.dead) return true;
      if (c.state !== 'idle' && c.state !== 'walk') return true;
      const side = i ? 1 : -1;
      const gx = G.clamp(real.x + side * 24, st.x0 + 4, st.x1 - 4), gy = G.clamp(real.y + side * 6, st.yMin, st.yMax);
      if (Math.hypot(gx - c.x, gy - c.y) > 3) G.combat.walkTo(c, gx, gy, dt, Math.max(c.speed, real.speed) * 1.1);
      else c.play(c.idleAnim || 'idle');
      c.facing = p.x > c.x ? 1 : -1;
      if (c.cool <= 0 && !real.tele && !real.atk && G.combat.tokens() < 2 && Math.abs(p.y - c.y) < 10) {
        const id = G.AI.pickMove(c, ctx);
        if (id) { G.AI.tele(c, id); c.cool = G.rand(1.6, 2.4); }
      }
      return true;
    };
  }
  // 石像的位置：剧情在 ctx.data.statue = { x, y, actor?, onBreak? } 里给；没给就找地图上 id 为 mr_statue 的角色 / 道具
  function statueOf(ctx) {
    if (ctx && ctx.data && ctx.data.statue) return ctx.data.statue;
    const st = G.world.stage;
    if (!st) return null;
    const a = st.find && st.find('mr_statue');
    if (a) return { x: a.x, y: a.y, actor: a };
    const pr = (st.props || []).find((q) => q && (q.id === 'mr_statue' || q.sprite === 'mr_statue'));
    return pr ? { x: pr.x, y: pr.y, prop: pr } : null;
  }
  K.e_polnareff.statueOf = statueOf;
  K.e_polnareff.stanceUp = stanceUp;          // 剧情的架剑光弧、testHint 用（和斩火 / 弹剑同一个判断）
  K.e_polnareff.openT = CHARIOT_OPEN_T;
})();
