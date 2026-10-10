// 包 4 自测用桩：combat.js / timestop.js / moves.js 的 KITS / script.js 的 G.S / story 的 G.LOOK / ui.js / ui_cards.js 的最小实现。集成时换成真文件。
'use strict';
(function () {
  const G = window.G;

  // ---------------- 时停（§4.15 的查询接口；测试直接设 phase / immune）
  G.time = {
    active: false, phase: null, immune: new Set(), by: null,
    isFrozen(a) { return this.active && (this.phase === 'burst' || this.phase === 'stopped') && !this.immune.has(a); },
    flowScale() { return this.active && (this.phase === 'burst' || this.phase === 'stopped') ? 0 : 1; },
    overActive() { return this.active && (this.phase === 'burst' || this.phase === 'stopped' || this.phase === 'resume') && this.immune.size > 0; },
    visual() { return null; }, update() {}, clear() { this.active = false; this.phase = null; this.immune.clear(); },
    __set(phase, immune) { this.active = !!phase; this.phase = phase || null; this.immune = new Set(immune || []); },
  };

  // ---------------- 招式组（规划 §3.2 的 HP / 走速；替身 id）
  G.KITS = {
    jotaro: { hp: 130, speed: 64, standId: 'starplat', explore: { pose: 'idle' } },
    joseph: { hp: 110, speed: 64, standId: 'hermit', explore: { pose: 'idle' } },
    avdol: { hp: 120, speed: 60, standId: 'magred', explore: { pose: 'idle' } },
    kakyoin: { hp: 100, speed: 66, standId: 'hiero', explore: { pose: 'idle' } },
    polnareff: { hp: 110, speed: 70, standId: 'chariot', explore: { pose: 'idle' } },
    iggy: { hp: 80, speed: 84, standId: 'fool', explore: { pose: 'idle' } },
  };
  G.MOVES = {};

  // ---------------- 战斗桩：只有自由走动（方向键走、J 亮替身 + 打可破坏物）
  const hitLog = [];
  G.combat = {
    hitLog,
    updatePlayer(p, dt) {
      const W = G.world, I = G.input, can = W.free && !G.S.busy;
      if (p.state === 'cmd') { if (p.stateT > 0.3) { p.state = 'idle'; p.play(p.idleAnim); } return; }
      if (p.state !== 'idle' && p.state !== 'walk') return;
      let mx = 0, my = 0;
      if (can) { if (I.isDown('left')) mx -= 1; if (I.isDown('right')) mx += 1; if (I.isDown('up')) my -= 1; if (I.isDown('down')) my += 1; }
      if (mx || my) {
        p.state = 'walk';
        if (mx) p.facing = mx;
        const k = mx && my ? 0.8 : 1;
        W.move(p, mx * p.speed * k * dt, my * p.speed * 0.6 * k * dt);
        p.play('walk');
      } else { p.state = 'idle'; if (p.anim === 'walk') p.play(p.idleAnim); }
      if (can && !W.combat && I.take('attack', 0.2)) {
        p.state = 'cmd'; p.stateT = 0; p.play('cmd', { restart: true });
        if (p.stand) { p.stand.summon({ dur: 0.18, rise: 6 }); p.stand.act('punch'); }
        // 自由走动的 J 只对 team 'object' 且 free 的可破坏物判定一次（替身原点、前方 6–40、纵深 ±8）
        const o = p.stand ? p.stand.origin() : p;
        for (const t of W.objects()) {
          const b = t.breakable;
          if (!b || !b.free || t.state === 'broken') continue;
          const dx = (t.x - (p.x + p.facing * 14)) * p.facing;
          if (dx < 6 - t.bodyW - 14 || dx > 40 + t.bodyW || Math.abs(t.y - o.y) > 8 + 4) continue;
          hitLog.push(t.id);
          t.flash = 1;
          t.hp = Math.max(0, t.hp - 10);
          const broken = t.hp <= 0;
          if (broken) { t.state = 'broken'; t.frozen = (b.frames || [0, 1])[1]; }
          // 命中与破坏属于一次事件，避免桩的 busy 锁吞掉同帧第二个回调。
          if (b.onHit || broken && b.onBreak) G.S.run(async (S) => {
            if (b.onHit) await b.onHit(S, b, { slot: 'J1' });
            if (broken && b.onBreak) await b.onBreak(S, b);
          });
        }
      }
    },
    updateAlly() {}, updateEnemy() {}, updateShots() {}, updateHazards() {}, drawPixel() {}, drawShot() {},
  };

  // ---------------- 剧情 API 桩
  const log = [];
  G.flags = {};
  G.S = {
    busy: false, talker: null, flags: G.flags, log,
    async run(fn) {
      if (this.busy) return;
      this.busy = true;
      const W = G.world, wasFree = W.free;
      W.free = false;
      try { await fn(this); } catch (e) { log.push(['error', String(e)]); }
      this.busy = false;
      W.free = wasFree;
    },
    say(who, text) { log.push(['say', who, text]); return G.wait(0.05); },
    wait(sec) { return G.wait(sec); },
    zoom() { return Promise.resolve(); }, eyeStrip() { return G.wait(0.1); }, photo() { return G.wait(0.1); },
  };

  // ---------------- 替身调查演出表桩（标签照 §4.13.1）
  const mk = (tags, cd, miss) => ({ tags, cd, miss, run: async (S, leader, h) => { log.push(['look', leader.cid, h ? h.id : null]); await G.wait(0.05); } });
  G.LOOK = {
    jotaro: mk(['detail', 'grab'], 1, '……没什么特别的。'),
    joseph: mk(['nensha'], 2, '……再来一次！'),
    avdol: mk(['life'], 2, '周围没有可疑的生命。'),
    kakyoin: mk(['reach', 'peek'], 1, '这里没有需要伸手的东西。'),
    polnareff: mk(['cut'], 1, 'Voilà～'),
    iggy: mk(['scent', 'hole'], 1, null),
    onStandDefault: async (S, npc, leader) => { log.push(['onStandDefault', npc.id, leader.cid]); npc.emote = { text: '？', t: 1 }; await S.say(null, '……起风了？'); },
  };

  // ---------------- 界面桩
  G.ui = {
    hints: [], notices: [],
    hint(t) { this.hints.push(t); }, notice(o) { this.notices.push(o); return Promise.resolve(); }, blocking() { return false; },
  };
  G.uifx = { cards: [], standCards: [], leaderCard(a) { this.cards.push(a.cid); }, standCard(id) { this.standCards.push(id); } };

  // ---------------- 世界场景（§2.3 的场景接口）+ 调试 UI（只在自测页上画：名字、互动提示、队伍条）
  G.NAMES = {};
  G.__ui = { labels: true };
  G.worldScene = {
    name: 'world', frozen: false,
    update(dt, worldAdv, wdt) { if (worldAdv) G.world.update(wdt); },
    drawWorld(wg) { G.world.draw(wg); },
    hasPixel() { return G.world.hasPixel(); },
    drawPixel(P, layer) { G.world.drawPixel(P, layer); },
    hasOver() { return G.world.hasOver(); },
    drawOver(wg) { G.world.drawOver(wg); },
    drawUI(ug) {
      const W = G.world;
      if (!W.stage || W.insert || !G.__ui.labels) return;
      ug.font = '12px SimSun, monospace'; ug.textBaseline = 'top';
      const P = G.party;
      if (P && P.members.length > 1) {
        P.members.forEach((m, i) => {
          const x = 8 + 32 * i, y = 8;
          ug.fillStyle = m === W.player ? '#ffd040' : m.look === 'gray' ? '#555' : m.look === 'unknown' ? '#111' : '#9aa';
          ug.fillRect(x, y, 28, 28);
          ug.fillStyle = '#000'; ug.fillText(m.look === 'unknown' ? '？' : m.cid.slice(0, 3), x + 2, y + 9);
        });
      }
      if (W.near) {
        const pos = G.cam.w2u(W.near.x, W.near.top, 0);
        const ux = pos.x == null ? pos[0] : pos.x, uy = pos.y == null ? pos[1] : pos.y;
        ug.fillStyle = 'rgba(14,16,28,0.85)'; ug.fillRect(ux - 30, uy - 26, 60, 16);
        ug.fillStyle = '#fff'; ug.fillText(String(W.near.label || ''), ux - 26, uy - 24);
      }
      for (const a of W.stage.actors) {
        if (!a.emote || !a.visible) continue;
        const pos = G.cam.w2u(a.x, a.headY(), 0);
        const ux = pos.x == null ? pos[0] : pos.x, uy = pos.y == null ? pos[1] : pos.y;
        ug.fillStyle = '#ffe14a'; ug.fillText(a.emote.text, ux - 4, uy - 30);
      }
    },
  };
})();
