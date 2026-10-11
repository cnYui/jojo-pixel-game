// 第4章　印度 / 两只右手的男人（规划 §6.3；原著 140–149 话，第 9–11 天）
//   2026-10-11 按序章 / 第1章体验版、第2、3章重做版的精度重做（用户：“接着做第四章”）：剧情、自由走动、过场全部重写，
//   两场战斗的机关沿用原来的（倒吊人的倒影 + 硬币光路、女帝的柏油桶 + 念写；招式在 engine\moves_ch02_05.js），补演出和手感。
//
//   流程：世界地图 → 加尔各答街（到站：一群小孩围住乔瑟夫、圣牛舔了波鲁纳雷夫；自由走动，楼顶有个戴牛仔帽的人影）→ 巷口：荷尔·荷斯
//   → 波鲁纳雷夫冲进雨里的后巷，阿布德尔追进去——镜子里的倒吊人、荷尔·荷斯的枪（剪影，阿布德尔倒下）→ 花京院：一起去
//   → 第 7 战 皇帝 & 倒吊人（后巷：倒影 + 硬币光路 → 加尔各答街：J·凯尔躲在路人身后）→「为了雪莉」，雨停 → 荷尔·荷斯拿奈娜挡剑逃走，
//   奈娜抓着乔瑟夫的手臂哭（一滴血）→ 街角：“阿布德尔不会希望我们停下来”→ 地图：贝拿勒斯（第 10 天）→ 乔瑟夫手臂上长出女帝
//   → 贝拿勒斯老城（只有乔瑟夫：水果摊、报纸、警察、神庙）→ 女帝喊“杀人犯”、警察吹哨追 → 河坛：第 8 战 女帝 → 奈娜的剪影 → 会合 → TBC
//
//   台词都是新写的（规划 §1.4 第 1 条：不冒充原句）；分镜原句只有荷尔·荷斯那句「比起当老大，我更适合当老二」（s09）。
//   克制处理（规划 §6.3）：阿布德尔中枪用剪影 + 枪声 + 留白，不画伤口；J·凯尔倒下以后只看到帽子落地；奈娜的真面目只用剪影；
//   警察是普通人，乔瑟夫只推开不打伤。阿布德尔是假死：乔瑟夫偷偷看了一眼怀表（伏笔）。
//   背景：tools\bg_new\calcutta_street.py / india_alley.py / varanasi_street.py / ganges_ghat.py（2026-10-11 重画），
//   坐标都从背景导出的 anchors 取（bgA），背景挪了位置剧情跟着走。
//   注意：进图时 Stage 会把定义里的 props / hotspots 各复制一份，进图以后再改 G.STAGES 的定义不影响现场——地图的定义都在 setStage 之前写好。
'use strict';
(function () {
  const G = window.G, J = G.J25, T = G.TPL, F = () => G.flags;
  const crew = ['jotaro', 'joseph', 'avdol', 'kakyoin', 'polnareff'];
  const lines = async (S, rows) => { for (const [who, text, expr] of rows) await S.say(who, text, expr ? { expr } : {}); };
  const hot = (id, x, y, label, tags, use, look, o = {}) => Object.assign({ id, x, y, label, tags, r: 22, ry: 120, use, look }, o);
  const sayBy = (S, p, map) => S.say(p.cid, T.by(p, map));
  const pick = (key, arr) => arr[(T.count(key) - 1) % arr.length];
  const follow = () => { if (G.party && G.party.rebuildFollow) G.party.rebuildFollow(); };
  // 第4章专用音效（tools\game_sfx.py 2026-10-11 新合成）：还没进数据包时用现成的顶上（直接播不存在的名字会记 missingSfx）
  const hasSnd = n => !!(G.audio && G.audio.has && G.audio.has(n));
  const snd = (name, alt, o = {}, ao = o) => { if (hasSnd(name)) G.audio.sfx(name, o); else if (alt) G.audio.sfx(alt, ao); };
  const amb = (S, name, alt, vol) => { if (hasSnd(name)) S.ambient(name, vol); else if (alt) S.ambient(alt, vol * .6); };
  const calmStands = () => { for (const a of (G.party && G.party.members) || []) if (a.stand && a.stand.visible && a.stand.mode !== 'recall') a.stand.recall({ sfx: false }); };
  const place = (S, cid, x, y, facing = 1) => { const a = S.actor(cid); if (a) { a.visible = true; a.follow = null; a.x = x; a.y = y; a.facing = facing; a.alpha = 1; S.unpose(a); } return a; };
  // 图集里有没有这个动作（先看 G.D.chars：直接 G.atlas 不存在的角色会记 missingImg）
  const hasChar = cid => !!(G.D && G.D.chars && G.D.chars[cid]);
  const hasAnim = (cid, name) => { if (!hasChar(cid)) return false; const A = G.atlas && G.atlas(cid); return !!(A && !A.missing && A._try && A._try(name)); };
  const hasProp = id => !!(G.D && G.D.props && G.D.props[id]);
  // 背景有没有某个 key 的图层（新背景画了碎玻璃 pick，旧背景没有就由剧情自己画裂纹）
  const bgHas = (bg, key) => { const b = G.D && G.D.bg && G.D.bg[bg]; return !!(b && (b.layers || []).concat(b.fg || []).some(l => l && l.key === key)); };
  function drawProp(g, id, sx, sy, frame = 0, alpha = 1) {
    const pm = G.D && G.D.props && G.D.props[id], im = pm && G.image ? G.image(pm.image) : null;
    if (!im || !(G.ready && G.ready(im))) return false;
    const w = pm.size ? pm.size[0] : im.width, h = pm.size ? pm.size[1] : im.height, n = pm.frames || 1, f = Math.max(0, Math.min(n - 1, frame | 0));
    const ga = g.globalAlpha; g.globalAlpha = ga * alpha;
    g.drawImage(im, f * w, 0, w, h, Math.round(sx - w / 2), Math.round(sy - h), w, h);
    g.globalAlpha = ga;
    return true;
  }

  // ---------------------------------------------------------------- 背景锚点（没有就用默认值）
  const bgA = (bg, k, d) => { const b = G.D && G.D.bg && G.D.bg[bg]; const v = b && b.anchors ? b.anchors[k] : null; return v != null ? v : d; };
  const CAd = { arrive: [70, 164], spice: [250, 160], spice_vendor: [270, 154], chai: [370, 160], cow: [500, 166], taxi: [640, 152], rickshaw: [760, 152],
    shrine: [900, 150], roof: [1010, 46], alley_mouth: [1210, 152] };
  const ALd = { mirror_box: [28, 46, 68, 110], window_box: [208, 64, 288, 114], puddles: [[92, 172], [173, 172], [276, 172]], mirror: [48, 160], window: [248, 160],
    eye_a: [120, 163], eye_b: [211, 163], entrance: [300, 160] };
  const VSd = { arrive: [40, 164], fruit: [90, 152], police: [170, 164], newspaper: [285, 152], sweets: [400, 152], temple: [495, 150], ghat_stairs: [600, 152] };
  const GHd = { arrive: [60, 160], shrine: [169, 134], barrels: [[100, 166], [325, 166], [555, 166]] };
  const CA = k => bgA('calcutta_street', k, CAd[k]);
  const AL = k => bgA('india_alley', k, ALd[k]);
  const VS = k => bgA('varanasi_street', k, VSd[k]);
  const GH = k => bgA('ganges_ghat', k, GHd[k]);

  // ---------------------------------------------------------------- 说话的人
  const sayHH = (S, text, o = {}) => S.say('holhorse', text, Object.assign({ name: '荷尔·荷斯', actor: S.actor('holhorse_cut') }, o));
  const sayEmp = (S, text, o = {}) => { snd('empress_voice', null, { vol: .7, rate: .9 + Math.random() * .2 }); return S.say('empress', text, Object.assign({ name: '女帝' }, o)); };
  const sayNena = (S, text, o = {}) => S.say('nena', text, Object.assign({ name: '奈娜', actor: S.actor('nena_cut') }, o));

  // ---------------------------------------------------------------- 安妮（跟队 NPC，不能当队长；第2、3章同一套）
  function anneFollow(S) {
    if (!F().anneJoined || F().anneLeft) return null;
    let a = S.actor('anne');
    if (!a) a = S.spawn('anne', S.player.x - 34, S.player.y, { id: 'anne', team: 'npc', label: '安妮', name: '安妮' });
    a.visible = true; a.alpha = 1; S.unpose(a);
    S.follow(a, S.player); a.followSlot = 6; a.leadable = false;
    a.talk = async (S2) => {
      const L = S2.player && S2.player.cid;
      const t = F().c4AvdolDown
        ? pick('c4anSad', ['……那个算命的叔叔，真的不会回来了吗？', '我不哭。……你们也别哭。'])
        : L === 'jotaro' ? pick('c4anJo', ['好多人……别把我弄丢了。', '你都不觉得热吗？'])
          : L === 'polnareff' ? pick('c4anPol', ['牛舔你的时候，你叫得比我还大声。', '你一直在看那条巷子。……你在找谁？'])
            : L === 'joseph' ? pick('c4anJos', ['老爷爷，钱别再随便给了。', '到了印度，你说要送我上飞机的。'])
              : L === 'avdol' ? pick('c4anAv', ['你说这里像开罗？开罗也这么挤吗？', '算命的，你今天的脸色不太好。'])
                : pick('c4anKak', ['那边有卖芒果的！……樱桃就别想了。', '你说话还是那么客气。']);
      await S2.say('anne', t, { name: '安妮', actor: a });
    };
    return a;
  }

  // ================================================================ 第 7 战：皇帝 & 倒吊人（后巷 → 加尔各答街）
  //   机关沿用：倒吊人只在照得到波鲁纳雷夫的倒影里（镜子、橱窗、3 个水洼、两个路人的眼睛）；打碎镜窗、踢沙让路人闭眼、
  //   花京院每 12 s 弹一枚硬币——别的倒影都照不到人时它只能跳进硬币，光路上按 J 刺中它，三次后段 2：J·凯尔躲在路人身后。
  //   荷尔·荷斯（打不死）：开枪前 0.6 s 红色弯曲虚线，子弹照这条线拐弯飞；补：开枪时他在画面边上露个头（皇帝），跳弹音。
  //   2026-10-11 补：雨（背景 key rain）、镜子 / 橱窗碎了切背景 pick、倒吊人换倒影时一声 mirror_flash、打完雨停一道光。
  const canReflect = (r, c) => !r.dead && (!r.expires || r.expires > c.t) && !(r.closedUntil > c.t) && Math.abs(r.x - c.player.x) < r.reach;
  const bez = (pts, u) => { const v = 1 - u; return [v * v * pts[0][0] + 2 * v * u * pts[1][0] + u * u * pts[2][0], v * v * pts[0][1] + 2 * v * u * pts[1][1] + u * u * pts[2][1]]; };
  // 倒吊人的画面：反光扫过还在的玻璃、碎掉的玻璃（背景没有碎玻璃 pick 时自己画裂纹）、藏身的那面里看得见它举刀；硬币、光路、荷尔·荷斯的红色弯曲虚线（W4 36f）
  function drawHanged(P, d, c) {
    const px = G.px, cx = G.cam.x || 0, t = c.t;
    if (d.phase) { if (d.blindUntil > t) { const x = c.player.x - cx; for (const r of [[0, 0, 320, 95], [0, 95, Math.max(0, x - 48), 85], [x + 48, 95, 320, 85]]) px.rect(P, ...r, '#050310', .9); } return; }
    for (const r of d.reflections) {
      const b = r.box; if (!b) continue;
      const x0 = b[0] - cx, y0 = b[1], x1 = b[2] - cx, y1 = b[3], w = x1 - x0, h = y1 - y0;
      if (r.dead) {
        if (d.bgGlass) continue;
        const ix = x0 + w * .45, iy = y0 + h * .42, len = Math.max(w, h) * .5;
        for (let k = 0; k < 9; k++) { const a = k * .7 + .3; px.line(P, ix, iy, ix + Math.cos(a) * len, iy + Math.sin(a) * len, '#1c2230', .95); }
        continue;
      }
      const k = ((t * .7 + (r.kind === 'window' ? .8 : 0)) % 1.6) / 1.6;
      if (k < 1) { const sx = x0 + (w - h * .35) * k; px.line(P, sx, y1 - 2, sx + h * .35, y0 + 2, '#e8fbff', .55); px.line(P, sx + 3, y1 - 2, sx + 3 + h * .35, y0 + 2, '#ffffff', .3); }
      if (r === d.source) { px.rect(P, x0 + 1, y0 + 1, w - 2, h - 2, '#401018', .25); px.blitFrame(P, 'hangedman', d.knifeWarn > t ? 'attack' : 'idle', 0, Math.round((x0 + x1) / 2), y1 - 4, { alpha: .85 }); }
    }
    for (const r of d.reflections) if (r.kind === 'puddle') { const x = r.x - cx; px.ellipse(P, x - 12, r.y - 2, x + 12, r.y + 2, r === d.source ? '#ff8a80' : '#88bcda', null, 1, .65); }
    if (d.coinUntil > t) { const x = d.coinX - cx, yy = Math.round(58 + Math.abs(Math.sin((t - d.coinAt) * 6)) * 8); px.ellipse(P, x - 3, yy - 4, x + 3, yy + 4, '#ffe273'); px.plot(P, x - 1, yy - 2, '#ffffff'); }
    if (d.lightUntil > t) px.ring(P, d.coinX - cx, 64, 6 + Math.round(Math.sin(t * 30) * 2), 1, '#fff6c0');
    if (d.gun) { const pts = d.gun.curve, a = Math.floor(t * 16) % 2 ? .9 : .55; let last = bez(pts, 0); for (let i = 1; i <= 20; i++) { const nx = bez(pts, i / 20); if (i % 2) px.line(P, last[0] - cx, last[1] - 22, nx[0] - cx, nx[1] - 22, '#ff3040', a); last = nx; } }
  }
  const rehide = c => { const al = c.spec.allies || []; for (const a of G.party.members) if (a !== c.player && !al.includes(a.cid)) { a.visible = false; if (a.stand) a.stand.hide(); } };
  // 开枪时荷尔·荷斯在画面边上露个头（皇帝），开完枪缩回去
  function hhPeek(c, x, on) {
    let a = G.S.actor('hh_peek');
    if (!a && on) { a = G.S.spawn('holhorse', x, 158, { id: 'hh_peek', team: 'npc', name: '荷尔·荷斯' }); a.standReact = false; a.talk = null; }
    if (!a) return;
    a.visible = !!on; a.x = x; a.facing = x > c.player.x ? -1 : 1;
    if (on) G.S.pose(a, hasAnim('holhorse', 'shoot') ? 'shoot' : 'idle');
  }
  async function exposeJgeil(c) {
    if (c.data.phase || c.data.shifting) return;
    c.data.phase = 1;
    const ghost = c.boss; ghost.remove = true;
    G.world.shots = []; G.world.hazards = []; c.data.gun = null; hhPeek(c, 0, false);
    for (const a of c.data.reflectActors || []) a.remove = true;
    c.spec.arena = [400, 720];
    if (G.STAGES.calcutta_ch4) G.STAGES.calcutta_ch4.state.rain = 1;
    snd('mirror_flash', 'glint', { vol: .8 });
    await J.transfer(c, 'calcutta_ch4', 460, 600);
    if (!J.valid(c)) return;
    G.world.stage.state.rain = 1;
    rehide(c);
    const e = c.spawn({ actor: 'jgeil', kit: 'e_jgeil', boss: true, hp: 600, poiseMax: 40, x: 635, y: 163 });
    c.data.civilians = [G.S.spawn('npc_townsfolk', 548, 164, { id: 'jgeil_civilian0', team: 'npc' }), G.S.spawn('npc_villager_f', 655, 164, { id: 'jgeil_civilian1', team: 'npc' })];
    e.onHitBy = (target, att) => { const n = c.data.civilians.find(a => Math.abs(a.x - target.x) <= 18 && att && (a.x - att.x) * (target.x - a.x) >= 0); if (!n) return null; att.stunT = .5; G.uifx.sfx('住手！他是无辜的！', att); return 'evade'; };
    // 名牌（左下）先放完再给提示：提示框在底部，同时出会压住名牌的副标题
    G.S.nameCard('jgeil');
    G.defer(2.7, () => { if (J.valid(c)) G.ui.hint('J·凯尔躲在路人身后：绕到另一边再打！', 6); }, 'world');
  }
  G.BOSS25.hanged = () => J.base('b07_hangedman', 'polnareff', [24, 296], {
    vs: 'emperor_hangedman', music: 'battle', allies: ['kakyoin'], bench: 'hide', gauge: { label: '光路截击', max: 3, value: 0 },
    kitOverride: { polnareff: { chords: { 'dodge+attack': 'PO_SAND_KICK' } } },
    waves: [[{ actor: 'hangedman', kit: { hp: 3, speed: 0, moves: [], brain: () => true, dmgMul: () => 0 }, boss: true, hp: 3, untargetable: true, x: 48, y: 160, alpha: 0 }]],
    onWave: async (S, i, es, a, c) => {
      if (G.world.stage.id !== 'alley_ch4') { c.spec.arena = [24, 296]; await J.transfer(c, 'alley_ch4', 150, 48); rehide(c); }
      // 重试：上一次的镜窗可破坏物、路人眼睛、荷尔·荷斯的头是 S.spawn 生成的（不归战斗管），不清掉会一层层叠起来
      for (const o of G.world.stage.actors) if (o.id && /^(reflection_|eye_|jgeil_civilian|hh_peek)/.test(o.id)) o.remove = true;
      const st = G.world.stage; st.state.rain = 1; st.state.mirror = 0; st.state.window = 0; st.state.sunbeam = 0;
      amb(S, 'rain_loop', 'wind_loop', .35);
      const d = c.data;
      Object.assign(d, { phase: 0, reflectActors: [], reflections: [], stabs: 0, nextKnife: 2, nextGun: 2.5, nextCoin: 12, lightUntil: 0, coinUntil: 0, coinAt: 0, coinCheck: 0,
        blindUntil: 0, gun: null, knifeWarn: 0, lastSource: null, bgGlass: bgHas('india_alley', 'mirror') });
      const kak = S.actor('kakyoin');
      if (kak) { kak.minHp = 1; kak.hp = kak.maxHp = 100; kak.brain = () => true; kak.moves = []; kak.team = 'npc'; S.follow(kak, c.player); kak.visible = true; }
      for (const kind of ['mirror', 'window']) {
        const box = AL(kind + '_box'), x = AL(kind)[0];
        const r = { kind, x, y: box[3], box, reach: 95, dead: false };
        d.reflections.push(r);
        const o = S.spawn('prop:mirror_shard', x, 162, { id: 'reflection_' + kind, team: 'object', hp: 20, alpha: 0, shadow: false });
        o.breakable = { onBreak: () => {
          r.dead = true; G.world.stage.state[kind] = 1; S.sfx('glass_break'); snd('mirror_flash', null, { vol: .6, rate: .8 });
          for (let k = 0; k < 3; k++) d.reflections.push({ kind: 'shard', x: x + (k - 1) * 12, y: 165, reach: 18, expires: c.t + 3 });
        } };
        d.reflectActors.push(o);
      }
      for (const [x, y] of AL('puddles')) d.reflections.push({ kind: 'puddle', x, y, reach: 20 });
      for (const [i, k] of ['eye_a', 'eye_b'].entries()) {
        const [x, y] = AL(k);
        d.reflections.push({ kind: 'eye', x, y: y - 18, reach: 70, closedUntil: 0 });
        const n = S.spawn(i ? 'npc_villager_f' : 'npc_townsfolk', x, y, { id: 'eye_' + i, team: 'npc' }); n.standReact = false; n.talk = null;
        d.reflectActors.push(n);
      }
      d.draw = (P, ctx) => drawHanged(P, d, ctx);
      S.hint(a > 0 ? '碎镜窗、K+J 踢沙、离开水洼；光路出现按 J。'
        : '倒吊人藏在倒影里！J3 碎镜窗、K+J 踢沙、离开水洼，等光路按 J。', 12);
    },
    tick(c, dt) {
      const d = c.data, p = c.player;
      if (d.phase) {
        if (c.boss && Math.floor(c.t) % 7 < 2) { const n = d.civilians && d.civilians[Math.floor(c.t / 7) % 2]; if (n && c.boss.state === 'idle') G.combat.walkTo(c.boss, n.x + (p.x < n.x ? 14 : -14), n.y, dt, 100); }
        return;
      }
      const rs = d.reflections.filter(r => canReflect(r, c));
      d.source = rs.length ? rs[Math.floor(c.t / 3) % rs.length] : null;
      if (d.source && d.source !== d.lastSource) snd('mirror_flash', null, { vol: .45 });
      if (d.source) { d.lastSource = d.source; d.lastSourceX = d.source.x; }
      if (c.t >= d.nextKnife) {
        d.nextKnife = c.t + 2.6;
        if (d.source) { const r = d.source; c.boss.x = r.x; d.knifeWarn = c.t + .5; G.audio.sfx('slash'); c.hazard({ owner: c.boss, shape: 'rect', x0: p.x - 14, x1: p.x + 14, y0: p.y - 8, y1: p.y + 8, warn: .5, dur: J.f(4), tier: 'W1', dmg: 14, guardSourceX: r.x, guardFromOwner: true, consume: true }); }
      }
      // 荷尔·荷斯：先亮 0.6 s 红色弯曲虚线（规划 W4 36f），子弹照这条线飞；走出线外、面朝枪口按住 L，或精准弹反（キィン！）
      if (c.t >= d.nextGun && !d.gun) {
        d.nextGun = c.t + 2.5;
        const x = p.x < 160 ? 306 : 14, y = 164;
        d.gun = { x, y, at: c.t + J.f(36), curve: [[x, y], [160, 115], [p.x, p.y]] };
        hhPeek(c, x, true);
        G.combat.fxAt('glint', { x, y: y - 22, size: 8 }, c.boss, .6); G.audio.sfx('glint', { vol: .6 });
      }
      if (d.gun && c.t >= d.gun.at) {
        const g = d.gun; d.gun = null;
        G.audio.sfx('gunshot', { vol: .7 }); snd('ricochet', null, { vol: .55 });
        c.shoot(c.boss, { kind: 'bullet', dmg: 12, curve: g.curve, curveDur: .45, life: 1, reflect: true, guardSourceX: g.x }, { x: g.x, y: g.y, z: 22 });
        G.defer(.5, () => { if (J.valid(c) && !c.data.gun) hhPeek(c, g.x, false); }, 'world');
      }
      // 硬币：弹起后在半空停 40f；0.4 s 后（硬币到顶）没有别的倒影照到人，倒吊人只能跳进硬币——光路亮 30f，这期间按 J
      if (c.t >= d.nextCoin) { d.nextCoin = c.t + 12; d.coinX = p.x; d.coinAt = c.t; d.coinUntil = c.t + J.f(40); d.coinCheck = c.t + .4; G.audio.sfx('coin'); G.ui.hint('花京院弹起了硬币——别让别的倒影照到你！', 2.5); }
      if (d.coinCheck && c.t >= d.coinCheck) {
        d.coinCheck = 0;
        if (!rs.length) { d.lightFrom = d.lastSourceX || 48; d.lightUntil = c.t + J.f(30); d.interceptUntil = c.t + J.f(30); G.audio.sfx('glint'); snd('mirror_flash', null, { vol: .8, rate: 1.2 }); G.ui.hint('光路出现！现在按 J！', 1.5); }
        else G.ui.hint('还有倒影照到你！打碎镜窗、扬沙，走离水洼。');
      }
      if (d.interceptUntil > c.t && G.input.hit('attack') && Math.abs(p.x - d.coinX) <= 48) {
        d.interceptUntil = 0; d.lightUntil = 0; d.stabs++; c.gauge.value = d.stabs; G.input.consume('attack');
        G.combat.fxAt('shatter', { src: 'prop:mirror_shard', logical: 'idle', x: d.coinX, y: 78, pieces: 44, dur: .9 }, p, .9); G.audio.sfx('slash'); G.shake(3, .25);
        if (d.stabs >= 3) exposeJgeil(c).catch(G.cancelIgnore);
      }
    },
    after: async (S, es, a, c) => {
      for (const n of [...(c.data.reflectActors || []), ...(c.data.civilians || [])]) n.remove = true;
      hhPeek(c, 0, false);
      c.data.jgeilX = es[0] ? es[0].x : 640;
    },
    testHint: c => ({ phase: c.data.phase, stabs: c.data.stabs, coinIn: c.data.nextCoin - c.t, intercept: c.data.interceptUntil > c.t,
      activeReflections: (c.data.reflections || []).filter(r => canReflect(r, c)).map(r => ({ kind: r.kind, x: r.x })), reflections: c.data.reflections }),
  });

  // ================================================================ 第 8 战：女帝（河坛）
  //   机关沿用：女帝长在乔瑟夫左臂上（成长 0→3 级，吃到东西 +0.3）、J 伤害 ×0.7、每 6 s 抢一次操作（左右颠倒 1 s）、两个警察追来缠人
  //   （J 只推开不伤人）；成长到 1 级后 U 念写 → 3 s 指向柏油桶；走到柏油桶按 E，手臂按进去 → 连打波纹 → 胜。
  //   2026-10-11 补：3 级的帧（l3）、印度警察的皮肤、木桶 / 柏油桶分开画（念写指到时柏油桶冒出黑亮的柏油）、警哨、女帝的声音、河坛环境音。
  const barrelProp = tar => (hasProp('tar_drum') ? 'tar_drum' : 'tar_barrel');
  // 贴在乔瑟夫前臂上的女帝：l0–l2 原大、l3 ×0.8，横向偏移按级 7 / 8 / 10 / 12（美术代理的对照图 tools\art\_preview\ch4_女帝缩放对照.png；
  //   原来的 .34 + 级 × .06 让 l0 / l1 只剩 2–5 px，根本看不见）
  const EMP_SCALE = [1, 1, 1, .8], EMP_DX = [7, 8, 10, 12];
  G.BOSS25.empress = () => J.base('b08_empress', 'joseph', [20, 620], {
    vs: 'empress', music: 'battle', bench: 'hide', gauge: { label: '女帝成长', max: 3, value: 0 },
    waves: [[{ actor: 'empress', kit: 'e_empress', boss: true, hp: 600, minHp: 1, x: 150, y: 160 }]],
    kitOverride: { joseph: { special: J.special(0, '念写：U → 柏油方向', c => c.data.growth >= 1, async (S, p, c, C) => {
      c.data.radarUntil = c.t + 3; C.fx('vines', { x0: p.x, y0: p.y - 15, x1: p.x + 32, y1: p.y - 40, t1: .5 }, { life: 1.2 }); S.sfx('camera_shutter'); await C.wait(.35);
    }, 8) } },
    onWave: async (S, i, es, a, c) => {
      const d = c.data;
      for (const o of G.world.stage.actors) if (o.id && /^(tar_barrel_|empress_police_)/.test(o.id)) o.remove = true;
      Object.assign(d, { growth: F().empressFruit ? .3 : 0, reverseAt: 6, radarUntil: 0, tarIndex: 1, barrels: [], police: [], policeAt: 5, whistled: false, baseOut: c.player.dmgOut || 1 });
      c.player.dmgOut = d.baseOut * .7;
      const id = barrelProp();
      // 三只桶：背景导出的第一只（x 100）正好在左边角楼脚下、和角楼抢，挪到台阶前的 x 180（画背景的代理建议）
      const BAR = GH('barrels').map(([x, y], k) => [k === 0 && x < 150 ? 180 : x, y]);
      for (const [i2, [x, y]] of BAR.entries()) { const b = S.spawn('prop:' + id, x, y, { id: 'tar_barrel_' + i2, team: 'npc', shadow: false }); b.frozen = 0; b.standReact = false; d.barrels.push(b); }
      const india = hasAnim('npc_police', 'india_idle');
      for (const [i2, x] of [50, 600].entries()) { const n = S.spawn('npc_police', x, 164, { id: 'empress_police_' + i2, team: 'npc' }); if (india) n.skin = 'india'; n.standReact = false; n.talk = null; d.police.push(n); }
      // 女帝长在乔瑟夫的手臂上：Boss 本体只留判定和血条（透明），画面上是贴在前臂的小头，张嘴时换 bite 帧
      es[0].alpha = 0; es[0].shadow = false;
      const maxLv = hasAnim('empress', 'l3_idle') ? 3 : 2;
      d.draw = (P, ctx) => {
        const px = G.px, p = ctx.player, b = ctx.boss, level = Math.min(maxLv, Math.floor(d.growth)), f = p.facing || 1, bite = !!(b && (b.tele || b.atk));
        px.blitFrame(P, 'empress', 'l' + level + (bite ? '_bite' : '_idle'), 0, Math.round(p.x - (G.cam.x || 0) - f * EMP_DX[level]), Math.round(p.y - (p.z || 0) - 14), { scale: EMP_SCALE[level], flip: f < 0 });
        if (d.radarUntil > ctx.t) { const x = d.barrels[d.tarIndex].x - (G.cam.x || 0); px.ring(P, x, 155, 16, 1, '#ffd84a'); }
      };
      S.hint(a > 0 ? '一级后按 U 念写，找到柏油桶按 E。' : '女帝打不得！一级后按 U 念写找柏油桶，走过去按 E。', 10);
    },
    events: [{ when: t => t >= 4, run: async S => {
      await lines(S, [['joseph', '你下一句要说的是——“杀人犯！”']]);
      await sayEmp(S, '杀人犯！……咦？');
      S.sfx('sting_shock');
    } }],
    tick(c, dt) {
      const d = c.data, p = c.player, b = c.boss;
      d.growth = Math.min(3, d.growth + dt / 20); c.gauge.value = d.growth;
      b.idleAnim = 'l' + Math.min(hasAnim('empress', 'l3_idle') ? 3 : 2, Math.floor(d.growth)) + '_idle'; b.x = p.x - 8; b.y = p.y; b.z = 20;
      // 念写指到的那只桶冒出柏油（tar_drum 第 1 帧）；其他时候三只一样
      d.barrels.forEach((a, i) => { a.frozen = (i === d.tarIndex && d.radarUntil > c.t) ? 1 : 0; });
      if (c.t >= d.reverseAt) { d.reverseAt = c.t + 6; p.controlReverseUntil = G.clk.world + 1; G.ui.hint('手臂在乱抓！左右颠倒一秒。'); snd('empress_voice', null, { vol: .5, rate: .9 + Math.random() * .2 }); }
      for (const n of d.police) {
        G.combat.walkTo(n, p.x + (n.x < p.x ? -18 : 18), p.y, dt, 38);
        if (n.anim === 'walk' && hasAnim('npc_police', 'india_run')) G.S.pose(n, 'run');
        if (!d.whistled && c.t >= 4.5) { d.whistled = true; snd('police_whistle', 'sting_shock', { vol: .7 }); }
        if (Math.abs(n.x - p.x) < 22 && c.t >= d.policeAt) { p.rootT = .5; d.policeAt = c.t + 3; G.audio.sfx('sting_shock'); }
        if (G.input.hit('attack') && Math.abs(n.x - p.x) < 55) { n.x += Math.sign(n.x - p.x || 1) * 35; G.uifx.sfx('退开！', p); }
      }
      if (G.input.okHit() && !d.qteBusy) {
        const near = d.barrels.findIndex(a => Math.abs(a.x - p.x) < 26);
        if (near < 0) return;
        G.input.consumeOk();
        if (near !== d.tarIndex) { G.ui.hint('这桶不是柏油。用 U 念写找方向。'); return; }
        J.qte(c, async () => {
          G.audio.sfx('drain'); snd('slime', null, { vol: .6, rate: .7 });
          await sayEmp(G.S, '动不了……这是什么！');
          const ok = await G.S.clash({ label: '隐者之紫！波纹——！（连按 J）', time: 4 });
          if (!J.valid(c)) return;
          if (ok) { G.S.fx('vines', { x0: p.x - 28, y0: p.y, x1: p.x + 20, y1: p.y - 25, t1: .6 }, { life: 1.4 }); G.audio.sfx('hamon'); c.end(); }
          else { d.growth = Math.min(3, d.growth + 1); d.tarIndex = (d.tarIndex + 1) % 3; G.ui.hint('女帝挣脱了！柏油桶换了位置。'); }
        }).catch(G.cancelIgnore);
      }
    },
    after: async (S, es, a, c) => { for (const n of [...c.data.barrels, ...c.data.police]) n.remove = true; },
    testHint: c => ({ growth: c.data.growth, tarIndex: c.data.tarIndex, barrels: c.data.barrels.map(a => a.x), radar: c.data.radarUntil > c.t, reversed: c.player.controlReverseUntil > G.clk.world }),
  });

  // ================================================================ 加尔各答街（calcutta_ch4，calcutta_street，1280 宽）
  function memberTalkCalcutta() {
    T.memberTalk({
      joseph: async S => S.say('joseph', pick('c4joA', ['加尔各答……人口一千万。这里的人比香港还多。', '钱包要贴身放。刚才那群小孩，差点把我的表也摸走了。', '再往西走，就是贝拿勒斯。'])),
      avdol: async S => S.say('avdol', pick('c4avA', ['印度就是这样——第一次来的人，不是爱上她，就是受不了她。', '今天早上的牌是『塔』。……突如其来的灾难。', '这里的气味，让我想起开罗。'])),
      kakyoin: async S => S.say('kakyoin', pick('c4kakA', ['芒果、香料、牛……感官全都被占满了。', '波鲁纳雷夫从下火车起，就一直在看人的手。'])),
      polnareff: async S => S.say('polnareff', pick('c4polA', ['那只牛舔了我一脸……我的发型！', '两只右手的男人……他就在这座城市的某个地方。我感觉得到。'])),
      jotaro: async S => S.say('jotaro', pick('c4joA', ['……吵。', '……'])),
    });
  }
  // 楼顶的牛仔帽人影：背景 pick roof_hh（走到 x 680 以后才出现）
  function setupCalcutta() {
    const st = G.STAGES.calcutta_ch4;
    st.props = []; st.triggers = [];
    st.state = Object.assign({}, st.state, { rain: 0, roof_hh: 0, sunbeam: 0 });
    const [sx, sy] = CA('spice_vendor'), [cx, cy] = CA('chai'), [kx, ky] = CA('cow'), [rx, ry] = CA('rickshaw');
    const cow = hasChar('npc_cow');
    st.npcs = [
      T.npc('npc_merchant', 'spice_vendor', sx, sy, { facing: -1, label: '香料小贩', name: '香料小贩', talk: async S => {
        await S.say('npc_merchant', pick('c4spice', ['姜黄、孜然、小豆蔻！闻一闻，不要钱！', '外国人？要不要咖喱粉？带回家就能做。']), { name: '香料小贩', actor: S.actor('spice_vendor') });
        if (S.player.cid === 'avdol') await S.say('avdol', '……这里的气味，让我想起开罗。');
      } }),
      T.npc('npc_townsfolk', 'chai_seller', cx + 10, cy - 6, { facing: -1, label: '茶摊', name: '茶摊老板', talk: async S => {
        await S.say('npc_townsfolk', pick('c4chai', ['Chai！热的奶茶！一杯一卢比！', '天要下雨了。……雨季还没过完呢。']), { name: '茶摊老板', actor: S.actor('chai_seller') });
        if (S.player.cid === 'joseph') await S.say('joseph', '这么热的天喝热奶茶……印度人真是了不起。');
      } }),
      T.npc(cow ? 'npc_cow' : 'npc_townsfolk', 'holy_cow', kx, ky, { facing: -1, label: '圣牛', name: '圣牛', talk: async (S) => {
        const me = S.actor('holy_cow'), p = S.player;
        if (p.cid === 'polnareff' || T.count('c4cow') === 1) {
          snd('cow_moo', null, { vol: .6 });
          if (me && hasAnim('npc_cow', 'lick')) S.pose(me, 'lick');
          snd('lick', null, { vol: .8 }); S.shake(1, .15);
          await S.say(p.cid === 'polnareff' ? 'polnareff' : p.cid, p.cid === 'polnareff' ? '牛舔了我一脸……Mon dieu！我的发型！' : T.by(p, { jotaro: '……', joseph: '它舔我！……这是表示欢迎吗？', avdol: '圣牛。在印度，谁也不会赶它走。', _: '牛舔了一下。' }));
          if (me) S.unpose(me);
          return;
        }
        snd('cow_moo', null, { vol: .5 });
        await sayBy(S, p, { kakyoin: '它在嚼一张纸箱。……真自在。', avdol: '圣牛。在印度，谁也不会赶它走。', _: '牛慢吞吞地嚼着什么。' });
      } }),
      T.npc('npc_townsfolk', 'rickshaw_puller', rx + 14, ry + 4, { facing: -1, label: '人力车夫', name: '人力车夫', talk: async S => {
        await S.say('npc_townsfolk', pick('c4rick', ['先生，坐车吗？去哪儿都行！', '下雨天我跑得最快，别的车都堵着呢。']), { name: '人力车夫', actor: S.actor('rickshaw_puller') });
      } }),
    ];
    st.hotspots = [
      hot('spice', CA('spice')[0], CA('spice')[1], '香料摊', [],
        async (S, h, p) => sayBy(S, p, { avdol: '这里的气味，让我想起开罗。', polnareff: '阿嚏！……这什么粉，辣死了！', kakyoin: '红的、黄的、绿的……像一盒颜料。', _: '一袋袋彩色的香料粉。' }), null, { ly: 100 }),
      hot('taxi', CA('taxi')[0], CA('taxi')[1], '黄色出租车', [],
        async (S, h, p) => sayBy(S, p, { joseph: '印度的车都这么开吗？……喇叭比刹车用得还多。', jotaro: '……', _: '一辆圆头的黄色出租车，喇叭响个不停。' }), null, { ly: 100 }),
      hot('shrine', CA('shrine')[0], CA('shrine')[1], '路边的神龛', [],
        async (S, h, p) => sayBy(S, p, { avdol: '……愿这段路平安。', polnareff: '神啊，让我先找到那个家伙。', _: '路边的小神龛，供着花环和油灯。' }), null, { ly: 100 }),
      // 楼顶：承太郎 U（细节）看得见那个人影；人影出现前查看只是普通的楼顶
      hot('roof', CA('roof')[0], 152, '楼顶', ['detail'],
        async (S, h, p) => S.say(p.cid, F().c4Roof ? '……那边楼顶上，有个戴牛仔帽的家伙。' : '旧楼的屋顶上晾满了衣服。'),
        async (S, h, p) => {
          if (!F().c4Roof) { await S.say('jotaro', '……没什么。'); return; }
          await S.say('jotaro', '那边楼顶上，有个戴牛仔帽的家伙在看我们。');
          await S.say('polnareff', '牛仔帽？……在哪？'); S.state('roof_hh', 0); await S.say('jotaro', '……不见了。');
        }, { r: 40 }),
      hot('alley_mouth', CA('alley_mouth')[0], CA('alley_mouth')[1], '巷口', [],
        async () => { F().ch4Alley = true; }, null, { ly: 96 }),
    ];
  }
  async function arrivalIntro(S) {
    calmStands();
    const [ax, ay] = CA('arrive');
    const order = [['jotaro', 60], ['joseph', 40], ['avdol', 22], ['kakyoin', 4], ['polnareff', -14]];
    for (const [cid, dx] of order) place(S, cid, ax + dx, ay - 4 + (dx % 3), 1);
    const anne = S.actor('anne') || S.spawn('anne', ax - 26, ay + 6, { id: 'anne', team: 'npc', label: '安妮', name: '安妮' });
    anne.follow = null; anne.x = ax - 26; anne.y = ay + 6; anne.facing = 1; anne.visible = true;
    S.location('calcutta');
    await S.wait(.6);
    await lines(S, [['polnareff', 'Oh la la……这么多人！'], ['joseph', '加尔各答。……这里的人比香港还多。']]);
    // 一群小孩围住乔瑟夫（规划：只做围上来、乔瑟夫撒钱跑路）
    const jos = S.actor('joseph');
    const kids = [];
    for (let i = 0; i < 3; i++) {
      const k = S.spawn('npc_kid', jos.x + 70 + i * 16, jos.y + (i - 1) * 4, { id: 'c4kid' + i, team: 'npc', name: '小孩' });
      k.facing = -1; k.standReact = false; k.talk = null; kids.push(k);
    }
    // 围在乔瑟夫跟前（站在他前面一排，别叠到承太郎身上）
    const ring = [[-12, 8], [6, 10], [22, 7], [-26, 12], [16, 14], [34, 11]];
    await Promise.all(kids.map((k, i) => S.walk(k, jos.x + ring[i][0], jos.y + ring[i][1], { speed: 120, anim: 'run' })));
    await S.say('npc_kid', '先生！先生！给一点零钱吧！', { name: '小孩', actor: kids[0] });
    S.sfx('coin'); jos.facing = 1;
    await lines(S, [['joseph', '好好好，一人一个——']]);
    for (let i = 3; i < 6; i++) {
      const k = S.spawn('npc_kid', jos.x + 120 + i * 10, jos.y + (i % 3 - 1) * 4, { id: 'c4kid' + i, team: 'npc', name: '小孩' });
      k.facing = -1; k.standReact = false; k.talk = null; kids.push(k);
      S.walk(k, jos.x + ring[i][0], jos.y + ring[i][1], { speed: 140, anim: 'run' }).catch(G.cancelIgnore);
    }
    await S.wait(.6);
    await lines(S, [['joseph', 'OH MY GOD！怎么一下子来了这么多！', 'shock']]);
    S.sfx('coin', { rate: 1.2 }); S.fx('burst', { x: jos.x + 10, y: jos.y - 30, n: 12, speed: 60, colours: ['#ffe273', '#d8b040'] });
    await lines(S, [['joseph', '……都拿去！快走快走！']]);
    for (const k of kids) S.walk(k, k.x + 40 + Math.random() * 40, k.y, { speed: 110, anim: 'run' }).catch(G.cancelIgnore);
    await S.wait(.7);
    for (const k of kids) k.remove = true;
    await lines(S, [['avdol', '印度就是这样。……第一次来的人，不是爱上她，就是受不了她。'], ['jotaro', '……呀嘞呀嘞。']]);
  }
  // 巷口：荷尔·荷斯 → 波鲁纳雷夫冲进巷子
  async function holhorseAppears(S) {
    calmStands(); S.hint(null);
    S.state('roof_hh', 0);
    const [mx, my] = CA('alley_mouth');
    const p = S.player;
    for (const cid of crew) { const a = S.actor(cid); if (a) a.follow = null; }
    const anne = S.actor('anne'); if (anne) anne.follow = null;
    const hh = S.spawn('holhorse', mx + 6, my + 6, { id: 'holhorse_cut', team: 'npc', name: '荷尔·荷斯' });
    hh.facing = -1; hh.alpha = 0; hh.standReact = false; hh.talk = null;
    S.music('tension');
    await S.animate(.6, k => { hh.alpha = k; hh.x = mx + 6 - k * 14; });
    S.nameCard('holhorse');
    await sayHH(S, '哟。可让我好等。');
    await sayHH(S, '比起当老大，我更适合当老二。');
    await sayHH(S, '我的搭档，你们应该听说过——两只手都是右手的那位。');
    const pol = S.actor('polnareff');
    if (pol) { pol.facing = 1; S.emote(pol, '！', .8); }
    await T.closeup4(S, { cid: 'polnareff', expr: 'shock', dur: 1.0 });
    await lines(S, [['polnareff', '……J·凯尔在哪？！']]);
    await sayHH(S, '就在这附近。想见他的话——一个人来。');
    hh.facing = 1; await S.walk(hh, mx + 40, my, { speed: 90 }); hh.remove = true;
    await lines(S, [['polnareff', '这是我妹妹的仇！谁都别插手！']]);
    if (pol) await S.walk(pol, mx + 30, my, { speed: 150, anim: 'run' });
    await lines(S, [['avdol', '波鲁纳雷夫！一个人去太危险了——！']]);
    const av = S.actor('avdol'); if (av) await S.walk(av, mx + 30, my, { speed: 150, anim: 'run' });
    await lines(S, [['joseph', '等等！阿布德尔！'], ['jotaro', '……下雨了。']]);
    S.state('rain', 1); amb(S, 'rain_loop', 'wind_loop', .3);
    await S.fadeOut(.5);
  }
  // 后巷：镜子里的倒吊人、荷尔·荷斯的枪、阿布德尔倒下（剪影）→ 花京院：一起去
  function setupAlley() {
    const st = G.STAGES.alley_ch4;
    st.npcs = []; st.hotspots = []; st.triggers = [];
    st.state = Object.assign({}, st.state, { rain: 1, mirror: 0, window: 0, sunbeam: 0 });
    // 过场里镜子中的倒吊人（战斗里由 drawHanged 画）
    st.props = [{ type: 'custom', id: 'mirror_hm', x: 0, y: 0, depth: 60, draw(g, ox, oy, t) {
      if (!F().c4MirrorHM || G.world.fight || !G.atlas) return;
      const b = AL('mirror_box'), A = G.atlas('hangedman');
      g.save(); g.beginPath(); g.rect(b[0] + ox, b[1] + oy, b[2] - b[0], b[3] - b[1]); g.clip();
      g.globalAlpha = .55 + .2 * Math.sin(t * 5);
      if (A && A.draw) A.draw(g, F().c4MirrorHM === 2 ? 'attack' : 'idle', 0, Math.round((b[0] + b[2]) / 2 + ox), b[3] - 4 + oy, { scale: .8 });
      g.restore();
    } }];
  }
  async function alleyAmbush(S) {
    S.party(['polnareff', 'avdol', 'kakyoin', 'jotaro', 'joseph'], { leader: 'polnareff' });
    await S.setStage('alley_ch4', { x: 100, y: 164, fade: false, music: 'tension' });
    amb(S, 'rain_loop', 'wind_loop', .35);
    for (const cid of ['jotaro', 'joseph', 'kakyoin']) { const a = S.actor(cid); if (a) a.visible = false; }
    const [mx] = AL('mirror'), [ex, ey] = AL('entrance');
    const pol = place(S, 'polnareff', mx + 40, 164, -1);
    const av = place(S, 'avdol', ex + 30, ey + 2, -1);
    await S.fadeIn(.5);
    await lines(S, [['polnareff', '出来！J·凯尔！……我知道你在这里！']]);
    const hh = S.spawn('holhorse', ex - 10, ey - 2, { id: 'holhorse_cut', team: 'npc', name: '荷尔·荷斯' });
    hh.facing = -1; hh.standReact = false; hh.talk = null;
    await sayHH(S, '他早就在你身边了哦。……看看镜子。');
    if (pol) pol.facing = -1;
    F().c4MirrorHM = 1; snd('mirror_flash', 'glint', { vol: .8 });
    await lines(S, [['polnareff', '……镜子里？！', 'shock']]);
    if (av) { await S.walk(av, (pol ? pol.x : 120) + 22, 164, { speed: 160, anim: 'run' }); av.facing = -1; }
    F().c4MirrorHM = 2; snd('mirror_flash', null, { vol: .9, rate: .8 });
    if (hasAnim('holhorse', 'shoot')) S.pose(hh, 'shoot');
    await lines(S, [['avdol', '波鲁纳雷夫，后面——！']]);
    // 〔剪影〕阿布德尔把波鲁纳雷夫推开，背对镜头，一道反光一闪，一声枪响，他慢慢倒下；不画血（规划 §6.3 节拍 3）
    const h = T.show(S, { bg: 'black', parts: [{ kind: 'sprite', cid: 'avdol', anim: 'idle', x: 160, y: 175, scale: 3, alpha: .5 }, { kind: 'sprite', cid: 'polnareff', anim: 'hurt', x: 255, y: 175, scale: 2, alpha: .3 }] });
    await S.wait(.5);
    S.fx('glint', { x: 165, y: 95, size: 22 }, { space: 'canvas' }); S.sfx('gunshot'); S.impact('invert', 1 / 24);
    await S.wait(.4);
    h.parts[0].anim = 'hurt';
    await S.animate(1.0, k => { h.parts[0].y = 175 + k * 18; h.parts[0].alpha = .5 * (1 - k * .6); });
    await S.wait(.6);
    h.close();
    F().c4MirrorHM = 0; F().c4AvdolDown = true;
    if (av) { S.pose(av, 'down'); }
    await T.closeup4(S, { cid: 'polnareff', expr: 'shock', dur: 1.2 });
    await lines(S, [['polnareff', '阿布德尔——！']]);
    await sayHH(S, '一枪搞定。……No.2 的活儿干完了，剩下的交给 J·凯尔。');
    S.pose(hh, 'idle'); hh.facing = 1; S.walk(hh, ex + 60, ey, { speed: 100 }).catch(G.cancelIgnore);
    await S.wait(.4); hh.remove = true;
    // 花京院追进来；承太郎、乔瑟夫留下照看阿布德尔（画外）
    const kak = place(S, 'kakyoin', ex + 20, ey + 4, -1);
    if (kak) await S.walk(kak, (pol ? pol.x : 120) + 26, 166, { speed: 150, anim: 'run' });
    await lines(S, [['polnareff', '……是我。是我害了他……'], ['kakyoin', '波鲁纳雷夫，冷静！……现在不是哭的时候。'],
      ['kakyoin', '承太郎和乔斯达先生在照看阿布德尔。……我们一起去。'], ['polnareff', '……花京院。'], ['polnareff', '……拜托了。']]);
    if (av) av.visible = false;
    G.party.remove('avdol', { look: 'unknown' });
    S.standCard('hangedman');
    await S.wait(1.0);
  }
  // 第 7 战之后：雨停、一道光、帽子落地 → 荷尔·荷斯拿奈娜挡剑逃走 → 奈娜抓着乔瑟夫的手臂（一滴血）
  async function afterHanged(S, c) {
    calmStands();
    // 战斗结束时把地图边界还原成开打那张图（后巷 0–320）的：在 1280 宽的加尔各答街上镜头被夹在 x 0，
    //   波鲁纳雷夫、荷尔·荷斯、奈娜全在画面外（2026-10-11 整章测试截图）——按这张图的定义还原
    { const st = G.world.stage, def = st && G.STAGES[st.id]; if (def) { st.x0 = def.x0; st.x1 = def.x1; } S.camera(null); }
    // 战斗结束会把藏起来的队员都显示出来；承太郎、乔瑟夫还在照看阿布德尔，等“大家赶到”再出场
    for (const cid of ['jotaro', 'joseph']) { const a = S.actor(cid); if (a) { a.visible = false; a.follow = null; } }
    const jx = (c && c.data && c.data.jgeilX) || 640;
    await lines(S, [['polnareff', '……为了雪莉。']]);
    // 雨停：云裂开一道口子、一道暖光照下来（背景 sunbeam；地面还是湿的）
    S.state('rain', 0); S.state('sunbeam', 1); S.ambient(null);
    S.flash(.3, .5, '#fff4d0');
    S.fx('speedlines', { cx: 180, cy: 20, colour: '#fff0bf', n: 16 }, { space: 'canvas', life: .8 });
    // J·凯尔倒在雨水里（down 帧，不画血，压暗）；规划写的“只看到帽子落地”——他原图不戴帽子，原片 s09 落下的帽子是荷尔·荷斯的（见下）
    const jg = S.spawn('jgeil', jx, 166, { id: 'jgeil_down', team: 'npc', name: 'J·凯尔' });
    jg.standReact = false; jg.talk = null; jg.alpha = .75; S.pose(jg, hasAnim('jgeil', 'down') ? 'down' : 'hurt');
    await S.title('saiki');
    await S.say(null, 'J·凯尔倒在雨水里，再也没有起来。');
    // 荷尔·荷斯 + 奈娜
    const pol = S.player;
    const hh = S.spawn('holhorse', pol.x + 90, 164, { id: 'holhorse_cut', team: 'npc', name: '荷尔·荷斯' });
    hh.facing = -1; hh.standReact = false; hh.talk = null;
    await sayHH(S, '啧……J·凯尔这个废物。');
    await lines(S, [['polnareff', '荷尔·荷斯！下一个就是你！']]);
    const nena = S.spawn('nena', hh.x + 20, 166, { id: 'nena_cut', team: 'npc', name: '奈娜' });
    nena.facing = -1; nena.standReact = false; nena.talk = null;
    await sayNena(S, '荷尔·荷斯！你答应过我的——');
    await sayHH(S, '对不起啦，宝贝。');
    nena.x = hh.x - 12; S.sfx('whoosh');
    await lines(S, [['polnareff', '——！', 'shock']]);
    hh.facing = 1;
    if (hasAnim('holhorse', 'flee')) S.pose(hh, 'flee');
    S.walk(hh, hh.x + 220, 164, { speed: 170 }).catch(G.cancelIgnore);
    await sayHH(S, 'Bye-bye～！');
    // 跑得太急，牛仔帽掉在路上（原片 s09 那顶飘落的帽子）
    T.prop(S, 'hat', hh.x - 10, 170, { id: 'hh_hat' }); S.sfx('whoosh', { vol: .4, rate: .7 });
    await S.wait(.6); hh.remove = true;
    // 大家赶到；奈娜抓着乔瑟夫的手臂哭——一滴血
    S.party(crew, { leader: 'polnareff' });
    G.party.remove('avdol', { look: 'unknown' });
    const jos = place(S, 'joseph', pol.x - 60, 166, 1), jo = place(S, 'jotaro', pol.x - 80, 160, 1), kak = place(S, 'kakyoin', pol.x - 30, 162, 1);
    for (const a of [jos, jo, kak]) if (a) S.walk(a, a.x + 30, a.y, { speed: 120 }).catch(G.cancelIgnore);
    await S.wait(.5);
    if (jos) await S.walk(nena, jos.x + 16, 166, { speed: 80 });
    nena.facing = -1;
    await sayNena(S, '他……他拿我挡剑……');
    await lines(S, [['joseph', '没事了，小姐。……你没受伤吧？']]);
    await sayNena(S, '……谢谢你，老先生。');
    S.fx('burst', { x: jos ? jos.x + 6 : pol.x, y: 140, n: 1, speed: 10, colours: ['#8a1830'] });
    await S.say(null, '奈娜抓着乔瑟夫的手臂哭了一会儿。没有人注意到，她的指尖在他的手臂上留下了一滴血。');
    nena.facing = 1; S.walk(nena, nena.x + 120, 166, { speed: 70 }).catch(G.cancelIgnore);
    await S.wait(.8); nena.remove = true;
    { const jg2 = S.actor('jgeil_down'); if (jg2) jg2.remove = true; }
    // 街角：没有葬礼
    S.music('sad'); S.state('sunbeam', 0);
    await lines(S, [['polnareff', '……都是因为我。'], ['jotaro', '……'], ['joseph', '……走吧。阿布德尔不会希望我们停下来。']]);
    await S.say(null, '乔瑟夫偷偷看了一眼怀表，什么也没说。');
    await S.fadeOut(.6);
  }
  // ================================================================ 贝拿勒斯老城（varanasi_st_ch4，varanasi_street，640）：只有乔瑟夫
  // 手臂上的女帝：自由走动时也画在乔瑟夫的左前臂上（战斗里由 d.draw 画）
  const empArm = { type: 'custom', id: 'empress_arm', x: 0, y: 0, depth: 179, draw(g, ox, oy, t) {
    const p = G.world.player;
    if (!p || p.cid !== 'joseph' || G.world.fight || !G.atlas || !F().c4EmpressArm) return;
    const A = G.atlas('empress'), lv = Math.min(2, Math.floor(F().c4EmpressLv || 0)), f = p.facing || 1;
    if (A && A.draw) A.draw(g, 'l' + lv + '_idle', Math.floor(t * 3) % 2, Math.round(p.x + ox - f * EMP_DX[lv]), Math.round(p.y + oy - (p.z || 0) - 14), { scale: EMP_SCALE[lv], flip: f < 0 });
  } };
  const growEmpress = n => { F().c4EmpressLv = Math.min(2, (F().c4EmpressLv || 0) + n); F().empressFruit = true; };
  function setupVaranasi() {
    const st = G.STAGES.varanasi_st_ch4;
    const [fx0, fy0] = VS('fruit');
    const basket = { type: 'custom', id: 'fruit_basket', x: fx0 - 6, y: fy0 + 2, depth: fy0 - 2, draw(g, sx, sy) { drawProp(g, 'fruit_basket', sx, sy, F().c4Fruit ? 1 : 0); } };
    st.props = [empArm, basket]; st.triggers = [];
    const india = hasAnim('npc_police', 'india_idle');
    const [px, py] = VS('police');
    st.npcs = [
      T.npc('npc_police', 'varanasi_police', px, py, { facing: -1, label: '警察', name: '警察', skin: india ? 'india' : null, talk: async S => {
        const me = S.actor('varanasi_police');
        if (me && india) me.skin = 'india';
        await S.say('npc_police', '外国人，你的手臂上那是什么？……肿了？', { name: '警察', actor: me, expr: india ? 'india' : undefined });
        await lines(S, [['joseph', '没、没什么！蚊子咬的！哈哈哈……']]);
        await sayEmp(S, '……嘻嘻。');
      } }),
      T.npc('npc_merchant', 'fruit_seller', VS('fruit')[0] + 18, VS('fruit')[1] + 2, { facing: -1, label: '水果摊老板', name: '水果摊老板', talk: async S => {
        await S.say('npc_merchant', '芒果、香蕉、石榴！先生，来一个？', { name: '水果摊老板', actor: S.actor('fruit_seller') });
      } }),
    ];
    st.hotspots = [
      hot('fruit', VS('fruit')[0], VS('fruit')[1], '水果摊', [],
        async S => {
          if (F().c4Fruit) { await lines(S, [['joseph', '……不能再让它吃了。']]); return; }
          F().c4Fruit = true;
          await sayEmp(S, 'Baby～肚子饿了～');
          S.sfx('teeth_crunch', { vol: .6 }); S.shake(1, .15); growEmpress(.6);
          await lines(S, [['joseph', '喂！别偷吃——！……老板，我付钱，我付钱！'], ['joseph', '……它又长大了一圈。']]);
        }, null, { ly: 100 }),
      hot('newspaper', VS('newspaper')[0], VS('newspaper')[1], '报纸摊', [],
        async S => {
          await lines(S, [['joseph', '……“通缉：手臂上长着怪物的外国老头”。'], ['joseph', 'OH MY GOD！这不就是我吗！', 'shock']]);
          await sayEmp(S, '嘻嘻嘻，通缉犯～');
        }, null, { ly: 100 }),
      hot('sweets', VS('sweets')[0], VS('sweets')[1], '甜食摊', [],
        async S => { await lines(S, [['joseph', '印度的甜食，甜得发齁。……别看了，不给你吃。']]); await sayEmp(S, '小气！'); }, null, { ly: 100 }),
      hot('temple', VS('temple')[0], VS('temple')[1], '小神庙', [],
        async S => {
          snd('temple_bell', 'ding', { vol: .7 });
          await lines(S, [['joseph', '……神啊，让这东西从我手上掉下去吧。']]);
          await sayEmp(S, '不——要～');
        }, null, { ly: 100 }),
      hot('ghat_stairs', VS('ghat_stairs')[0], VS('ghat_stairs')[1], '去河坛的台阶', [],
        async () => { F().empressArena = true; }, null, { ly: 96 }),
    ];
  }
  async function varanasiIntro(S) {
    calmStands();
    const [ax, ay] = VS('arrive');
    const jos = place(S, 'joseph', ax + 20, ay, 1);
    F().c4EmpressArm = true; F().c4EmpressLv = 0;
    S.location('varanasi');
    await S.wait(.5);
    await lines(S, [['joseph', '大家在旅馆歇着，我出来买点东西……'], ['joseph', '……手臂上这个肿块，从早上起就一直在跳。']]);
    snd('empress_voice', null, { vol: .7, rate: .9 + Math.random() * .2 }); if (jos) S.emote(jos, '！', .8);
    await sayEmp(S, 'Baby～');
    await lines(S, [['joseph', '它、它说话了？！', 'shock']]);
    F().c4EmpressLv = 1;
    S.sfx('heartbeat', { vol: .5 });
    await sayEmp(S, '我是「女帝」。从今天起，这只手归我了～');
    await lines(S, [['joseph', '……奈娜的那一滴血。是那个女人！']]);
  }
  async function policeChase(S) {
    calmStands(); S.hint(null);
    const p = S.player, me = S.actor('varanasi_police');
    await sayEmp(S, '救命啊——！杀人犯！这个外国老头是杀人犯——！');
    snd('police_whistle', 'sting_shock', { vol: .8 });
    if (me) { me.facing = p.x > me.x ? 1 : -1; S.emote(me, '！', .8); }
    await S.say('npc_police', '站住！', { name: '警察', actor: me, expr: hasAnim('npc_police', 'india_idle') ? 'india' : undefined });
    await lines(S, [['joseph', '冤枉啊——！']]);
    if (me) S.walk(me, p.x - 20, p.y, { speed: 140, anim: hasAnim('npc_police', 'india_run') ? 'run' : 'walk' }).catch(G.cancelIgnore);
    await S.walk(p, VS('ghat_stairs')[0] + 30, p.y, { speed: 150, anim: 'run' });
    await S.fadeOut(.4);
  }
  async function ghatEnding(S) {
    calmStands();
    // 念写 / 波纹的藤蔓特效默认不会自己消失（fx.js：vines 由创建者收），结尾前清掉战斗里留下的
    if (G.fx && G.fx.clear) G.fx.clear();
    G.audio.sfx('hamon');
    await S.title('saiki');
    await S.say(null, '女帝缩成了一滴血，从乔瑟夫的手臂上掉了下去。');
    F().c4EmpressArm = false;
    // 奈娜的真面目：只用剪影（规划 §6.3 克制处理）
    const h = T.show(S, { bg: 'black', parts: [{ kind: 'sprite', cid: 'nena', anim: 'true_form', x: 160, y: 170, scale: 2, o: { sil: '#24162e' } }] });
    await S.wait(.6);
    await lines(S, [['joseph', '……原来她一直戴着别人的样子。']]);
    h.close();
    // 会合
    S.party(crew, { leader: 'jotaro' });
    G.party.remove('avdol', { look: 'unknown' });
    const jos = S.actor('joseph'), jx = jos ? jos.x : 300;
    place(S, 'joseph', jx, 164, -1);
    for (const [cid, dx] of [['jotaro', -60], ['kakyoin', -80], ['polnareff', -100]]) { const a = place(S, cid, jx + dx - 60, 162, 1); if (a) S.walk(a, jx + dx, a.y, { speed: 130, anim: 'run' }).catch(G.cancelIgnore); }
    const anne = S.actor('anne') || S.spawn('anne', jx - 180, 168, { id: 'anne', team: 'npc', name: '安妮' });
    anne.visible = true; anne.follow = null; anne.x = jx - 180; S.walk(anne, jx - 120, 168, { speed: 130, anim: 'run' }).catch(G.cancelIgnore);
    await S.wait(.8);
    await lines(S, [['polnareff', '乔斯达先生！警察满城在找一个“手臂上长着怪物的外国老头”……'], ['jotaro', '……老头子，你手臂上那东西呢。'],
      ['joseph', '没了。用波纹烧掉了。……是奈娜，那个女人也是替身使者。'], ['kakyoin', '荷尔·荷斯的同伴……一个接一个地来。']]);
    S.music('sad'); amb(S, 'ghat_loop', 'sea_loop', .3);
    await lines(S, [['joseph', '……阿布德尔。']]);
    await S.say(null, '恒河的水，静静地流着。');
    await lines(S, [['polnareff', '……下一个是荷尔·荷斯。这次，我不会再一个人冲出去了。'], ['jotaro', '……呀嘞呀嘞daze。']]);
    S.sfxText('呀嘞呀嘞daze', S.actor('jotaro') || 'player');
    await J.end(S, 'ch4_tbc');
  }

  // ================================================================ 章节流程
  G.STORY.ch4 = async S => {
    T.resetCounters();
    for (const k of ['ch4Alley', 'empressArena', 'empressFruit', 'c4Roof', 'c4MirrorHM', 'c4AvdolDown', 'c4EmpressArm', 'c4EmpressLv', 'c4Fruit']) delete F()[k];
    // 安妮跟到第5章送上飞机（规划 §6.1）；从“选择章节”直接进第4章也一样
    Object.assign(F(), { anneJoined: true, anneNamed: true, anneLeft: false });
    await G.MID.ensureBg('_ch4');
    S.party(crew, { leader: 'jotaro' });
    await S.chapterCard('ch4');
    await S.setStage('map_ch4', { x: 100, y: 160, music: 'travel' });
    await S.run(s => s.route(['新加坡', '加尔各答'], { vehicle: 'train', day: 9, left: 42, cut: .6, history: ['东京', '香港', '新加坡'] }));
    // 加尔各答街：到站 → 自由走动
    setupCalcutta();
    await S.setStage('calcutta_ch4', { x: CA('arrive')[0] + 40, y: 164, music: 'daily' });
    amb(S, 'bazaar_loop', 'crowd_loop', .3);
    await S.run(arrivalIntro);
    follow(); anneFollow(S);
    memberTalkCalcutta();
    S.hint('加尔各答！往右走，逛逛这条街（E 搭话 / 调查）。', 10);
    // 走过街中间以后，楼顶出现那个人影（承太郎 U 看得出是谁）
    T.tick(() => { if (!F().c4Roof && S.player && S.player.x > 680) { F().c4Roof = true; S.state('roof_hh', 1); G.ui.hint('……楼顶上好像有人。（承太郎 U 看看）', 4); } return !!F().c4Roof; });
    T.goal(S, { x: CA('alley_mouth')[0], y: CA('alley_mouth')[1], h: 56, label: '巷口', delay: 50, every: 25, done: () => !!F().ch4Alley, text: '街的尽头有条巷子。' });
    await S.until(() => F().ch4Alley && !S.busy);
    await S.run(holhorseAppears);
    // 后巷：伏击 → 第 7 战
    setupAlley();
    await S.run(async s => {
      await alleyAmbush(s);
      let fc = null;
      const spec = G.BOSS25.hanged();
      const after0 = spec.after;
      spec.after = async (S2, es, a, c) => { fc = c; await after0(S2, es, a, c); };
      await s.fight(spec);
      await afterHanged(s, fc);
    });
    // 贝拿勒斯：地图 → 乔瑟夫一个人
    await S.setStage('map_ch4', { x: 100, y: 160, fade: false, music: 'travel' });
    await S.fadeIn(.3);
    await S.run(async s => {
      await s.route(['加尔各答', '瓦拉纳西'], { vehicle: 'car', day: 10, left: 41, cut: .6, history: ['东京', '香港', '新加坡', '加尔各答'] });
      await s.narrate('第十天，贝拿勒斯。', { pos: 'center' });
    });
    setupVaranasi();
    S.party(['joseph'], { leader: 'joseph' });
    await S.setStage('varanasi_st_ch4', { x: VS('arrive')[0] + 20, y: 164, music: 'tension' });
    amb(S, 'bazaar_loop', 'crowd_loop', .2);
    await S.run(varanasiIntro);
    S.hint('乔瑟夫一个人。女帝在手上闹……先逛逛这条街，再去河坛。', 10);
    T.goal(S, { x: VS('ghat_stairs')[0], y: VS('ghat_stairs')[1], h: 56, label: '河坛', delay: 50, every: 25, done: () => !!F().empressArena, text: '去河坛的台阶在街的尽头。' });
    await S.until(() => F().empressArena && !S.busy);
    await S.run(async s => {
      await policeChase(s);
      await s.setStage('varanasi_ch4', { x: GH('arrive')[0] + 40, y: 160, fade: false, music: 'battle' });
      amb(s, 'ghat_loop', 'sea_loop', .25);
      await s.fadeIn(.4);
      s.standCard('empress');
      await s.wait(1.0);
      await s.fight(G.BOSS25.empress());
      await ghatEnding(s);
    });
  };

  // 开发调参入口（只给 tools\dev\full\dev_fight.py 用，正常游戏不调用）
  G.DEV = G.DEV || {};
  G.DEV.ch4Hanged = async S => { await G.MID.ensureBg('_ch4'); setupAlley(); S.party(['polnareff', 'kakyoin'], { leader: 'polnareff' }); await S.setStage('alley_ch4', { x: 150, y: 164, music: 'battle' }); await S.run(async s => { await s.fight(G.BOSS25.hanged()); }); };
  G.DEV.ch4Empress = async S => { await G.MID.ensureBg('_ch4'); S.party(['joseph'], { leader: 'joseph' }); await S.setStage('varanasi_ch4', { x: 120, y: 160, music: 'battle' }); await S.run(async s => { await s.fight(G.BOSS25.empress()); }); };
})();
