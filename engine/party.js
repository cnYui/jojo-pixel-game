// 队伍（包 4）：当前队伍、换队长（复用同一批 Actor）、能不能当队长、轨迹跟随、同屏人数、替身调查的输入 / 查找 / 冷却（技术约定 §4.13）
'use strict';
(function () {
  const G = window.G;
  const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  const W = () => G.world;
  const ev = (type, data) => { if (G.dbg && G.dbg.ev) G.dbg.ev(type, data); };
  const sBusy = () => !!(G.S && G.S.busy);
  const uiBlocking = () => !!(G.ui && G.ui.blocking && G.ui.blocking());
  const hint = (text) => { if (text && G.ui && G.ui.hint) G.ui.hint(text); };
  const shortName = (a) => {
    const D = G.D || {};
    return (G.NAMES && G.NAMES[a.cid]) || (D.heroes && D.heroes[a.cid] && D.heroes[a.cid].short) || a.name || a.cid;
  };
  const LANES = [-3, 3, -5, 5, 0];
  const TRAIL_STEP = 2, TRAIL_MAX = 200, SLOT_GAP = 11, SEP = 10;
  const lockMsgShown = new WeakSet();   // 每场战斗只弹一次“这一战只能由 X 应战”

  const P = (G.party = {
    members: [],
    pool: {},
    locked: false,
    cool: 0,
    trail: [],
    lookCd: {},
    _prev: null,          // 上一任队长（rebuildFollow 排第一）
    _skipShown: {},       // cid → 跳过提示已弹过

    // ---------------- 名单
    _actor(cid) {
      let a = this.pool[cid];
      if (!a) {
        const p = W() && W().player;
        a = new G.Actor(cid, p ? p.x : 160, p ? p.y : 160, { team: 'npc', kit: cid });
        this.pool[cid] = a;
      }
      return a;
    },
    _place(a, i) {
      const Wd = W(), st = Wd && Wd.stage, p = Wd && Wd.player;
      if (!st || a === p) return;
      if (st.actors.indexOf(a) < 0) {
        if (p && p !== a) {
          a.x = clamp(p.x - (p.facing || 1) * (22 + i * 22), st.x0 + 8, st.x1 - 8);
          a.y = clamp(p.y + LANES[i % 5], st.yMin, st.yMax);
          a.facing = p.facing || 1;
        }
        a.state = 'idle'; a.script = null; a.hold = false; a.z = 0;
        a.play(a.idleAnim);
        if (a.stand) a.stand.hide();
        st.add(a);
      }
    },
    // 设定当前队伍（建或复用 Actor，team 'npc'，kit 取 G.KITS[cid]）；o.leader 指定队长
    set(ids, o = {}) {
      const Wd = W();
      const next = ids.map((id) => this._actor(id));
      for (const a of this.members) {
        if (next.indexOf(a) >= 0) continue;
        a.follow = null;
        if (a.team === 'player' || a.team === 'ally') a.team = 'npc';
        if (Wd && Wd.stage && Wd.stage.actors.indexOf(a) >= 0 && Wd.player !== a) a.remove = true;
      }
      this.members = next;
      for (const a of next) {
        a.leadable = true; a.look = null; delete a.mem.away;
        if (a.mem.partyHidden) { a.visible = true; delete a.mem.partyHidden; }
      }
      this._skipShown = {};
      let lead = o.leader ? this._actor(o.leader) : Wd && next.indexOf(Wd.player) >= 0 ? Wd.player : next[0];
      if (next.indexOf(lead) < 0) lead = next[0];
      for (const a of next) a.team = a === lead ? 'player' : Wd && Wd.combat ? 'ally' : 'npc';
      if (Wd && lead) {
        const old = Wd.player;
        if (old && old !== lead && next.indexOf(old) < 0 && Wd.stage && Wd.stage.actors.indexOf(old) >= 0) {
          lead.x = old.x; lead.y = old.y; lead.facing = old.facing;
          old.remove = true;
        }
        Wd.player = lead; lead.follow = null;
        if (Wd.stage) {
          if (Wd.stage.actors.indexOf(lead) < 0) Wd.stage.add(lead);
          next.forEach((a, i) => { if (a !== lead) this._place(a, i); });
        }
      }
      this._prev = null;
      this.rebuildFollow();
      return this.members;
    },
    // 入队 / 离队；o.notice 弹「XX 加入了队伍！」系统框
    add(cid, o = {}) {
      const a = this._actor(cid), Wd = W();
      const back = !!a.mem.away;
      if (this.members.indexOf(a) < 0) this.members.push(a);
      delete a.mem.away;
      a.leadable = true; a.look = null; a.remove = false;
      if (a !== (Wd && Wd.player)) a.team = Wd && Wd.combat ? 'ally' : 'npc';
      this._place(a, this.members.indexOf(a));
      if (o.x != null && Wd && Wd.stage) {
        a.x = clamp(o.x, Wd.stage.x0 + 8, Wd.stage.x1 - 8);
        if (o.y != null) a.y = clamp(o.y, Wd.stage.yMin, Wd.stage.yMax);
      }
      this.rebuildFollow();
      ev('party_join', { cid, back });
      if (o.notice && G.ui && G.ui.notice) {
        return G.ui.notice({ who: cid, title: (o.name || a.name) + ' 加入了队伍！', text: o.text || '', sub: o.sub || '' });
      }
      return Promise.resolve(a);
    },
    // o.drop：彻底从名单里拿掉（不留灰头像）；默认 = 离队（还在名单里，头像灰掉、不跟随、不能当队长、不随换图）
    remove(cid, o = {}) {
      const a = this.pool[cid], Wd = W();
      if (!a || this.members.indexOf(a) < 0) return false;
      a.follow = null;
      if (o.drop) this.members.splice(this.members.indexOf(a), 1);
      else { a.mem.away = true; a.leadable = false; a.look = o.look || 'gray'; }
      if (Wd && Wd.player === a) {
        const nx = this.members.find((m) => m !== a && !m.mem.away && m.state !== 'down');
        if (nx) this.setLeader(nx, { force: true, silent: true });
      }
      if (a.team === 'ally' || a.team === 'player') a.team = 'npc';
      if (!o.stay && Wd && Wd.stage && Wd.player !== a) {
        if (a.stand) a.stand.hide();
        a.remove = true;
      }
      if (a.mem.partyHidden) { a.visible = true; delete a.mem.partyHidden; }
      this.rebuildFollow();
      ev('party_leave', { cid });
      if (o.notice && G.ui && G.ui.notice) return G.ui.notice({ who: cid, title: (o.name || a.name) + ' 离开了队伍。' });
      return true;
    },
    get(cid) { const a = this.pool[cid]; return a || null; },
    leader() { const Wd = W(); return Wd && this.members.indexOf(Wd.player) >= 0 ? Wd.player : this.members[0] || null; },
    active() { return this.members.filter((m) => !m.mem.away); },

    // ---------------- 换队长（复用 Actor，只换 team 和 W.player；不用 S.setPlayer）
    setLeader(cidOrActor, o = {}) {
      const Wd = W();
      const next = typeof cidOrActor === 'string' ? this.pool[cidOrActor] || (Wd.stage && Wd.stage.find(cidOrActor)) : cidOrActor;
      const old = Wd.player;
      if (!next || next === old) return false;
      if (!o.force && (next.state === 'down' || !next.leadable || next.mem.away || this.locked)) return false;
      if (o.force && next.mem.away) return false;
      if (old) {
        old.team = Wd.combat ? 'ally' : 'npc';
        old.state = 'idle'; old.atk = null; old.focus = null; old.cool = 0.6;
        if (old.anim !== old.idleAnim && !old.hold) old.play(old.idleAnim);
      }
      next.team = 'player'; next.follow = null; next.hold = false; next.state = 'idle'; next.script = null;
      next.visible = true;
      if (next.mem.partyHidden) delete next.mem.partyHidden;
      if (Wd.stage && Wd.stage.actors.indexOf(next) < 0) {
        if (old) { next.x = old.x; next.y = old.y; next.facing = old.facing; }
        Wd.stage.add(next);
      }
      Wd.player = next; Wd.focus = null;
      this._prev = old && this.members.indexOf(old) >= 0 ? old : null;
      this.rebuildFollow();
      if (!o.silent) {
        if (G.uifx && G.uifx.leaderCard) G.uifx.leaderCard(next);
        if (next.stand) next.stand.summon({ dur: 0.2, rise: 6, sfx: false });
        const sd = G.D && G.D.stands && G.D.stands[next.standId];
        if (sd && sd.summonSfx && G.audio && G.audio.sfx) G.audio.sfx(sd.summonSfx, { vol: 0.6, x: next.x });
        ev('swap', { to: next.cid });
        if (Wd.fight && Wd.fight.emit) Wd.fight.emit('swap', { who: next });
      }
      return true;
    },
    // 不能当队长（规划 §2.2 的“灰”和“？”）：还在队里、照样跟随、能被搭话，但 Q 跳过他
    setLeadable(cid, on, o = {}) {
      const a = this.pool[cid];
      if (!a) return false;
      a.leadable = !!on;
      a.look = on ? null : o.look === undefined ? 'gray' : o.look;
      if (on) delete a.mem.leadMsg; else a.mem.leadMsg = o.msg || null;
      delete this._skipShown[cid];
      const Wd = W();
      if (!on && Wd && Wd.player === a) {
        const nx = this.members.find((m) => m !== a && m.leadable && !m.mem.away && m.state !== 'down');
        if (nx) this.setLeader(nx, { silent: true, force: true });
      }
      return true;
    },
    _skipHint(a) {
      if (this._skipShown[a.cid]) return;
      this._skipShown[a.cid] = true;
      hint(a.mem.leadMsg || null);
    },
    // 候选：自由走动 = 队伍里在场的人；swap 战 = 参战的人（lead + allies）
    _cands() {
      const Wd = W();
      if (Wd.combat) {
        const fight = Wd.fight;
        const ids = fight && fight.spec ? [fight.spec.lead].concat(fight.spec.allies || []) : null;
        return (Wd.stage ? Wd.stage.actors : []).filter((a) => !a.remove && (a.team === 'player' || a.team === 'ally') &&
          (!ids || ids.indexOf(a.cid) >= 0 || ids.indexOf(a.id) >= 0));
      }
      return this.members.filter((m) => !m.mem.away);
    },
    next(dir = 1) {
      const Wd = W(), cur = Wd.player;
      const list = Wd.combat ? this._cands() : this.members;
      const n = list.length;
      if (n < 2) return false;
      let i = list.indexOf(cur);
      for (let k = 1; k < n; k++) {
        const a = list[((i < 0 ? 0 : i) + dir * k + n * 4) % n];
        if (a === cur || a.mem.away || a.state === 'down' || a.remove) continue;
        if (!a.leadable) { this._skipHint(a); continue; }
        return this.setLeader(a);
      }
      return false;
    },
    canSwap() {
      const Wd = W();
      if (!Wd || !Wd.player) return false;
      if (Wd.combat) {
        if (!(Wd.fight && Wd.fight.swap)) return false;
        return this._cands().some((a) => a !== Wd.player && a.state !== 'down' && a.leadable);
      }
      if (this.locked) return false;
      return this.members.some((a) => a !== Wd.player && !a.mem.away && a.leadable && a.state !== 'down');
    },
    lock(on) { this.locked = !!on; },
    // 同屏人数（规划 §1.3 第 19 条）：单屏小地图（宽 ≤ 340）最多队长 + 3 人，宽地图全显示
    maxFollowers() {
      const st = W() && W().stage;
      return st && st.x1 - st.x0 <= 340 ? 3 : 5;
    },
    carryList() { const p = W() && W().player; return this.members.filter((m) => m !== p && !m.mem.away); },

    // 换队长、换图、入队离队时：清轨迹，按队伍顺序（旧队长排第一）重设 follow / followSlot，再按同屏人数挑谁“在门外”
    rebuildFollow() {
      const Wd = W(), p = Wd && Wd.player;
      this.trail = [];
      const fol = this.members.filter((m) => m !== p && !m.mem.away);
      if (this._prev && fol.indexOf(this._prev) > 0) { fol.splice(fol.indexOf(this._prev), 1); fol.unshift(this._prev); }
      fol.forEach((a, i) => { a.follow = p || null; a.followSlot = i + 1; });
      for (const m of this.members) if (m.mem.away || m === p) { m.follow = null; m.followSlot = 0; }
      this._applyVisible();
    },
    _applyVisible() {
      const Wd = W(), st = Wd && Wd.stage, p = Wd && Wd.player;
      if (!st || !p) return;
      const fol = this.members.filter((m) => m !== p && !m.mem.away && st.actors.indexOf(m) >= 0);
      const max = this.maxFollowers();
      let keep = fol;
      if (fol.length > max) keep = fol.slice().sort((a, b) => Math.hypot(a.x - p.x, a.y - p.y) - Math.hypot(b.x - p.x, b.y - p.y)).slice(0, max);
      for (const m of fol) {
        if (keep.indexOf(m) >= 0) { if (m.mem.partyHidden) { m.visible = true; delete m.mem.partyHidden; } }
        else if (m.visible) { m.visible = false; m.mem.partyHidden = true; if (m.stand) m.stand.hide(); }
      }
    },

    // ---------------- 每帧（world.update 第 3 步）：换队长输入、替身调查冷却、轨迹记录
    update(dt) {
      const Wd = W(), I = G.input;
      if (this.cool > 0) this.cool = Math.max(0, this.cool - dt);
      for (const k in this.lookCd) if (this.lookCd[k] > 0) this.lookCd[k] = Math.max(0, this.lookCd[k] - dt);
      const p = Wd.player;
      if (I && p) {
        if (Wd.combat) {
          if (I.take && I.take('swap', 0.1)) {
            const fight = Wd.fight;
            if (fight && fight.swap && !Wd.cine) {
              if (this.cool <= 0 && this.next(1)) this.cool = 1.0;
            } else if (fight && !lockMsgShown.has(fight)) {
              lockMsgShown.add(fight);
              hint(fight.lockMsg || (fight.spec && fight.spec.lockMsg) || '这一战只能由' + shortName(p) + '应战');
            }
          }
        } else if (Wd.free && !sBusy() && !uiBlocking() && !this.locked) {
          // 冷却中不取走按键：缓冲 0.1 s 内冷却结束仍能换（先 take 后判冷却会吞掉快速连按的 Q）
          if (this.cool <= 0 && I.take && I.take('swap', 0.1)) { this.next(1); this.cool = 0.3; }
          for (let n = 1; n <= 6; n++) {
            if (!(I.take && I.take('lead' + n, 0.1))) continue;
            const a = this.members[n - 1];
            if (!a || a === p || a.mem.away || this.cool > 0) break;
            if (!a.leadable) { hint(a.mem.leadMsg || null); break; }
            if (this.setLeader(a)) this.cool = 0.3;
            break;
          }
        }
      }
      // 轨迹：队长每移动 ≥ 2 px 往头部塞一个点（最多 200）
      if (p && Wd.stage) {
        const tr = this.trail, h = tr[0];
        if (!h) tr.unshift({ x: p.x, y: p.y });
        else if (Math.abs(p.x - h.x) + Math.abs(p.y - h.y) >= TRAIL_STEP) {
          tr.unshift({ x: p.x, y: p.y });
          if (tr.length > TRAIL_MAX) tr.length = TRAIL_MAX;
        }
      }
    },
    _target(a) {
      const Wd = W(), p = a.follow, st = Wd.stage, i = a.followSlot || 1;
      const tr = this.trail, idx = i * SLOT_GAP, lane = LANES[(i - 1) % 5];
      let tx, ty;
      if (tr.length > idx) { tx = tr[idx].x; ty = tr[idx].y; }
      else if (tr.length > 1) {
        // 轨迹不够长：从最后一个点往队长身后延长
        const last = tr[tr.length - 1], miss = (idx - (tr.length - 1)) * TRAIL_STEP;
        tx = last.x - (p.facing || 1) * miss; ty = last.y;
      } else { tx = p.x - (p.facing || 1) * 22 * i; ty = p.y; }
      return { x: st ? clamp(tx, st.x0 + 8, st.x1 - 8) : tx, y: st ? clamp(ty + lane, st.yMin, st.yMax) : ty + lane };
    },
    // 跟随者（world.update 第 4 步调）：离目标 > 16 px 开始走、3 px 内停；速度 min(f.speed·1.15, max(30, d·2.4))；横向差 > 220 px 瞬移
    updateFollow(a, dt) {
      const Wd = W(), f = a.follow;
      const stop = () => { if (a.state === 'walk') { a.state = 'idle'; a.play(a.idleAnim); } };
      if (!f || f.remove || a.hold || Wd.combat) {
        stop();
        if (!a.hold && a.anim !== a.idleAnim && a.state !== 'walk' && a.animDone()) a.play(a.idleAnim);
        return;
      }
      const t = this._target(a);
      if (Math.abs(f.x - a.x) > 220) { a.x = t.x; a.y = t.y; return; }
      const dx = t.x - a.x, dy = t.y - a.y, d = Math.hypot(dx, dy);
      if (d > (a.state === 'walk' ? 3 : 16)) {
        const step = Math.min(d, Math.min(f.speed * 1.15, Math.max(30, d * 2.4)) * dt);
        Wd.move(a, (dx / d) * step, (dy / d) * step, true);
        if (Math.abs(dx) > 1) a.facing = dx > 0 ? 1 : -1;
        a.state = 'walk';
        a.play('walk');
      } else {
        stop();
        if (Math.abs(f.x - a.x) > 3) a.facing = f.x > a.x ? 1 : -1;
      }
      // 不挤成一团：和别的跟随者靠得比 SEP 近就各自让开（轨迹折返时目标点会重合）
      const st = Wd.stage;
      if (!st) return;
      for (const b of st.actors) {
        if (b === a || b.follow !== f || !b.visible || b.remove || !a.visible) continue;
        let ddx = a.x - b.x, ddy = a.y - b.y;
        const dd = Math.hypot(ddx, ddy);
        if (dd >= SEP) continue;
        if (dd < 0.01) { ddx = (a.followSlot > b.followSlot ? 1 : -1) * -(f.facing || 1); ddy = 0; }
        const k = (SEP - dd) * 0.5 / Math.max(dd, 0.01);
        Wd.move(a, Math.max(-2, Math.min(2, ddx * k)), Math.max(-1, Math.min(1, ddy * k * 0.5)), true);
      }
    },

    // ---------------- 替身调查（§4.13.1）：自由走动按 U
    investigate() {
      const Wd = W(), p = Wd.player;
      if (!p) return false;
      const cid = p.cid, L = G.LOOK && G.LOOK[cid];
      if ((this.lookCd[cid] || 0) > 0) return false;
      const h = Wd.findLook();
      this.lookCd[cid] = L && L.cd != null ? L.cd : 1;
      ev('investigate', { cid, hotspot: h ? h.id || h.label || null : null });
      const st = Wd.stage;
      if (G.S && G.S.run) {
        G.S.run(async (S) => {
          if (L && L.run) await L.run(S, p, h);
          if (h) {
            if (h.look) await h.look(S, h, p);
            else { await S.say(cid, '……这里好像有什么。'); ev('look_missing', { id: h.id || h.label || null }); }
          } else if (st && st.onLook) await st.onLook(S, p);
          else if (L && L.miss) await S.say(cid, L.miss);
        }).catch(G.cancelIgnore);
      }
      return true;
    },
    // 自由走动中、冷却到了（附近有没有对得上的调查点用 G.world.findLook() 查）
    lookReady() {
      const Wd = W(), p = Wd && Wd.player;
      if (!p || !Wd.free || Wd.combat || sBusy() || uiBlocking()) return false;
      return (this.lookCd[p.cid] || 0) <= 0;
    },
    // 换章 / 回标题：清空
    reset() { this.members = []; this.pool = {}; this.locked = false; this.cool = 0; this.trail = []; this.lookCd = {}; this._prev = null; this._skipShown = {}; },
  });
})();
