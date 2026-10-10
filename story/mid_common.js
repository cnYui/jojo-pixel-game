// 中段章节共用场景工具；胜负仍由各章节机关决定，避免把解谜战降成血量拉锯。
'use strict';
(function () {
  const G = window.G, W = G.world, T = G.TPL;
  const M = G.MID = {};
  M.crew = ['jotaro', 'joseph', 'kakyoin', 'polnareff'];
  M.lines = async (S, rows) => { for (const [who, text] of rows) await S.say(who, text); };
  M.hot = (id, x, label, tags, text, use, look, y = 160) => ({ id, x, y, label, tags, r: 24, ry: 90,
    use: use || (async (S, h, p) => S.say(p.cid === 'iggy' ? null : p.cid, p.cid === 'iggy' ? '（伊奇嗅了嗅。）' : text)),
    look: look || (async (S, h, p) => S.say(p.cid === 'iggy' ? null : p.cid, p.cid === 'iggy' ? '（伊奇对着这里低吼。）' : text)) });
  M.exit = (id, x, label, flag) => M.hot(id, x, label, ['detail', 'nensha', 'life', 'peek', 'cut', 'scent'], '继续前进。',
    async S => { S.flags[flag] = true; });
  M.npc = (cid, id, x, label, text, y = 156) => T.npc(cid, id, x, y, { label, talk: async (S, a, p) => {
    if (p && p.cid === 'iggy') { S.sfx('dog_bark'); await S.say(null, '哪来的小狗？……别咬我的鞋！'); }
    else await S.say(cid, text, { name: label });
  } });
  M.scene = async (S, id, setup, x = 72, lead) => {
    const st = G.STAGES[id]; st.props = []; st.npcs = []; st.hotspots = []; st.triggers = []; st.onLook = null;
    if (setup) setup(st);
    if (lead) S.setLeader(lead, { force: true, silent: true });
    await S.setStage(id, { x, y: st.yMin + 10 });
    T.memberTalk({});
  };
  M.explore = async (S, flag, hint) => { S.free(true); S.hint(hint, 12); await S.until(() => !!S.flags[flag] && !S.busy); S.free(false); };
  M.prop = (S, id, x, y = 160, o = {}) => T.prop(S, id, x, y, o);
  M.pixel = (id, draw) => { const p = { type: 'pixel', id, x: 0, y: 0, draw, _midFight: W.fight && W.fight.id }; W.stage.props.push(p); return p; };
  M.ui = (S, draw) => S.insertUI((g, t) => draw(g, t, W.fight));
  M.text = (g, text, x, y, color = '#ffe3a0') => G.f12.draw(g, text, x, y, color, { outline: '#181025' });
  // 战斗里的机关说明：画在右上（Boss 条下面、计时 / 环境槽右侧的下方），不压左上的队长血条和同伴栏
  M.hud = (g, lines, y = 44) => {
    lines.filter(Boolean).forEach((s, i) => G.f12.draw(g, s, 630, y + i * 15, i ? '#ffe3a0' : '#fff4d6', { outline: '#181025', align: 'right' }));
  };
  M.damage = (c, dmg, guard = 'none') => G.combat.hit(null, c.player, { dmg, slot: 'enemy', guard, push: 0, sfxHit: 'thud' });
  // 热量和氧气是持续损耗；受击无敌帧不能用来抵销环境计时。
  M.drain = (c, dmg) => { c.player.hp = Math.max(c.player.minHp || 0, c.player.hp - dmg * (c.assist ? .7 : 1)); };
  M.every = (d, key, dt, seconds, fn) => { d[key] = (d[key] || 0) + dt; if (d[key] >= seconds) { d[key] %= seconds; fn(); } };
  M.busy = async (c, fn) => { const data = c.data; if (data.cine) return; data.cine = true; const old = W.cine, run = G.runId; W.cine = { by: '机关' };
    try { await fn(); } finally { if (G.runId === run && W.fight === c && c.data === data) { W.cine = old; data.cine = false; } } };
  M.task = (c, fn) => M.busy(c, fn).catch(G.cancelIgnore);
  M.objectFight = async (S, spec, init) => {
    const tick = spec.tick, stage = W.stage;
    const clean = () => { stage.props = stage.props.filter(p => p._midFight !== spec.id); };
    try {
      return await S.fight(Object.assign({ waves: [], energy: { start: 100 } }, spec, { tick(c, dt) {
        if (!c.data.ready) {
          clean(); c.data.ready = true;
          if (!G.party.members.includes(c.player)) { G.combat.resetActor(c.player); c.player.energy = 100; }
          init(c); G.midGame = c.data;
        }
        if (tick) tick(c, dt);
      } }));
    } finally { clean(); if (W.stage === stage) S.insertUI(null); G.midGame = null; }
  };
  M.toothHit = (c, a) => { if (!a || a.dead) return; a.hp = 0; G.combat.ko(a, c.player); G.S.sfx('teeth_crunch'); c.data.broken++; };
  // 背景图包按“第一次登记的章节”分包（calcutta_street 在 bg_ch5、desert_night / egypt_coast 在 bg_ch8），
  //   main.js 进章时只载 bg_common + 本章包：本章用到别的包里的背景时先补载，不然地图是一片黑。
  M.ensureBg = async (suffix) => {
    const D = G.D || {}, need = new Set();
    for (const [id, st] of Object.entries(G.STAGES)) {
      if (!id.endsWith(suffix) || !st || !st.bg) continue;
      const b = D.bg && D.bg[st.bg];
      if (b && b.pack && !G.res.loaded('bg_' + b.pack)) need.add('bg_' + b.pack);
    }
    for (const name of need) await G.res.loadPack(name);
  };
  M.end = async (S, mark) => { S.mark(mark); await S.tbc(); };
})();
