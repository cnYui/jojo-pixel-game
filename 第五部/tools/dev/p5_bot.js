// 机器人只读快照并通过 Playwright 的真实键盘操作，不改血量、坐标、剧情标志或胜负。
'use strict';
class P5Bot {
  constructor(page, options = {}) {
    this.page = page; this.held = new Set(); this.spots = [104, 180, 255, 318, 378];
    this.spot = 0; this.hallWait = 0; this.arrowSeen = false; this.failed = false;
    this.dodged = false; this.usedU = false; this.retry = false;
    this.options = options; this.losses = new Set(); this.wins = new Set(); this.streetSpot = 0;
    this.started = false; this.finished = false; this.readUntil = 0; this.text = null;
  }
  async keys(keys = []) {
    const want = new Set(keys);
    for (const k of this.held) if (!want.has(k)) await this.page.keyboard.up(k);
    for (const k of want) if (!this.held.has(k)) await this.page.keyboard.down(k);
    this.held = want;
  }
  async tap(key) {
    await this.page.keyboard.down(key); await this.step(2);
    await this.page.keyboard.up(key); await this.step(2);
  }
  async step(frames = 8) {
    if (this.options.record) return this.page.waitForTimeout(frames * 1000 / 60);
    return this.page.evaluate(n => window.__p5step(n), frames);
  }
  async choose(s, label) {
    const idx = s.menuItems.indexOf(label);
    if (idx < 0) throw new Error('菜单没有选项：' + label);
    if (s.menuIdx !== idx) await this.tap(s.menuIdx < idx ? 'ArrowDown' : 'ArrowUp');
    else await this.tap('Enter');
  }
  async act(s) {
    if (s.menuItems) {
      await this.keys();
      if (s.scene === 'title' && this.started) { this.finished = true; return true; }
      if (s.menuItems.includes('再来一次')) {
        this.failed = true; this.retry = true; this.losses.add(s.fightId);
        await this.choose(s, '再来一次'); return false;
      }
      if (s.menuItems.includes('继续下一章')) {
        if (this.options.chapter === 'prologue') await this.choose(s, '返回标题');
        else await this.choose(s, '继续下一章');
        return false;
      }
      if (s.menuItems.includes('返回标题') && s.scene !== 'title') { await this.choose(s, '返回标题'); return false; }
      if (s.scene === 'title') {
        if (this.options.chapter === 'ch1') {
          if (s.menu?.startsWith('选择章节')) { await this.choose(s, '第1章　街头干部'); this.started = s.menuIdx === 1; }
          else await this.choose(s, '选择章节');
        } else { await this.choose(s, '从序章开始'); this.started = true; }
        return false;
      }
      await this.tap('Enter'); return false;
    }
    if (s.dlg || s.narr || s.notice) {
      await this.keys();
      const text = s.dlg || s.narr || s.notice;
      if (text !== this.text) { this.text = text; this.readUntil = s.clk + (this.options.read || .08) + (this.options.record ? text.length * .045 : 0); }
      if (s.clk >= this.readUntil && (!this.options.record || !s.dlg || s.ddone)) await this.tap('Enter');
      return false;
    }
    this.text = null;
    if (s.combat && !s.cine && s.fightId === 'b_pro1_taxi') {
      if (!this.options.record && !this.losses.has(s.fightId)) { await this.keys(); return false; }
      const q = s.taxi;
      if (!q) return false;
      if (!this.dodged && q.warnLeft > 0 && q.warnLeft <= .23) {
        await this.keys(['ArrowDown']); await this.tap('k'); this.dodged = true;
        return false;
      }
      if (!this.dodged) { await this.keys(); return false; }
      if (q.active && s.py > 170) { await this.keys(); return false; }
      if (!this.usedU) {
        await this.keys(); await this.tap('u'); this.usedU = true; return false;
      }
      const keys = [];
      if (s.py > 162) keys.push('ArrowUp');
      else if (s.py < 158) keys.push('ArrowDown');
      const dx = q.x - s.px;
      if (dx > 38) keys.push('ArrowRight');
      else if (dx < 16) keys.push('ArrowLeft');
      await this.keys(keys);
      if (Math.abs(dx) < 58 && Math.abs(s.py - 160) < 8) await this.tap('j');
      return false;
    }
    if (s.stage === 'airin_pro' && s.free && !s.busy) {
      // 等完整45秒后读回箭头，随后逐一调查，最后走出口。
      if (this.hallStart == null) this.hallStart = s.clk;
      this.hallWait = s.clk - this.hallStart;
      if (!this.options.record && this.hallWait < 46) {
        await this.keys();
        if (s.hint?.includes('出租车在右边')) this.arrowSeen = true;
        return false;
      }
      const x = this.spots[this.spot];
      if (x != null) {
        if (Math.abs(s.px - x) > 6) await this.keys([s.px < x ? 'ArrowRight' : 'ArrowLeft']);
        else { await this.keys(); await this.tap('e'); this.spot++; }
      } else await this.keys(['ArrowRight']);
      return false;
    }
    if (s.stage === 'street_ch1' && s.free && !s.busy) {
      const route = [[48, 'u'], [100, 'u'], [168, 'e'], [220, 'u'], [340, 'u'], [404, 'e']];
      const target = route[this.streetSpot];
      if (!target) await this.keys(['ArrowRight']);
      else if (Math.abs(s.px - target[0]) > 4) await this.keys([s.px < target[0] ? 'ArrowRight' : 'ArrowLeft']);
      else { await this.keys(); await this.tap(target[1]); this.streetSpot++; }
      return false;
    }
    if (s.combat && !s.cine && /^b_ch1_/.test(s.fightId)) {
      if (!this.options.record && !this.losses.has(s.fightId)) { await this.keys(); return false; }
      const q = s.fightHint;
      if (!q || q.bossHp == null) return false;
      // 每种招先实际经过一次，随后近身连打；预警末段用K离开车道。
      const ready = q.phase === 1 ? q.dives > 0 && q.jabs > 0 : q.holes > 0 && q.ankles > 0;
      const danger = q.hazards.find(h => h.phase === 'warn' && h.left < .26 && s.px >= h.x0 - 3 && s.px <= h.x1 + 3 && s.py >= h.y0 - 3 && s.py <= h.y1 + 3);
      if (danger) { await this.keys([s.py < 160 ? 'ArrowUp' : 'ArrowDown']); await this.tap('k'); return false; }
      if (!ready) { await this.keys(['l']); return false; }
      if (q.phase === 2 && !q.specials && s.energy >= 100) { await this.keys(); await this.tap('u'); return false; }
      if (q.sense > 0) { await this.keys(['l']); return false; }
      const keys = [], dx = q.bossX - s.px, dy = q.bossY - s.py;
      if (Math.abs(dx) > 22) keys.push(dx > 0 ? 'ArrowRight' : 'ArrowLeft');
      else if (Math.abs(dx) < 10) keys.push(dx > 0 ? 'ArrowLeft' : 'ArrowRight');
      if (Math.abs(dy) > 3) keys.push(dy > 0 ? 'ArrowDown' : 'ArrowUp');
      await this.keys(keys);
      if (Math.abs(dx) < 36 && Math.abs(dy) < 8 && q.hidden <= 0) {
        if (s.facing !== (dx >= 0 ? 1 : -1)) await this.tap(dx >= 0 ? 'ArrowRight' : 'ArrowLeft');
        await this.tap('j');
      }
      return false;
    }
    await this.keys(); return false;
  }
}
module.exports = { P5Bot };
