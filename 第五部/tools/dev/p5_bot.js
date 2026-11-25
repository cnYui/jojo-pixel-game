// 机器人只读快照并通过 Playwright 的真实键盘操作，不改血量、坐标、剧情标志或胜负。
'use strict';
class P5Bot {
  constructor(page) {
    this.page = page; this.held = new Set(); this.spots = [104, 180, 255, 318, 378];
    this.spot = 0; this.hallWait = 0; this.arrowSeen = false; this.failed = false;
    this.dodged = false; this.usedU = false; this.retry = false;
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
  async step(frames = 8) { return this.page.evaluate(n => window.__p5step(n), frames); }
  async act(s) {
    if (s.stage === 'street_ch1' && s.free) { await this.keys(); return true; }
    if (s.menuItems) {
      await this.keys();
      if (s.menuItems.includes('再来一次')) { this.failed = true; this.retry = true; }
      await this.tap('Enter'); return false;
    }
    if (s.dlg || s.narr || s.notice) {
      await this.keys(); await this.tap('Enter'); return false;
    }
    if (s.combat && !s.cine && s.fightId === 'b_pro1_taxi') {
      if (!this.failed) { await this.keys(); return false; }
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
      if (this.hallWait < 46) {
        await this.keys(); this.hallWait += 8 / 60;
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
    await this.keys(); return false;
  }
}
module.exports = { P5Bot };
