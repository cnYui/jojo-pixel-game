// 宋体点阵字（UI 层 12 / 16 px）：照搬银魂 gfx.js Font，图从 key 取；缺字记 G.dbg.missingGlyph（不 warn）、fillText 兜底（技术约定 §4.8）
'use strict';
(function () {
  const G = window.G;

  // 行首禁则（这些字不放在行首，挂在上一行行尾）
  const NO_HEAD = '，。、！？…」』）～—：；,.!?)';
  const WS = ' 　\t';
  const OUT8 = [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, -1], [-1, 1], [1, 1]];
  const MAX_TINT = 24;     // 每个字号最多缓存几种颜色的着色图集
  const MAX_BAKE = 160;    // bake() 缓存的整串文字图

  function noteMissing(ch) {
    const d = G.dbg;
    if (d && d.missingGlyph && !d.missingGlyph.has(ch)) d.missingGlyph.add(ch);
  }

  class Font {
    constructor(size) {
      const m = (G.D && G.D.font && G.D.font[String(size)]) || null;
      this.size = size;
      this.meta = m;
      this.img = m ? G.image(m.image) : null;
      this.lh = m ? m.lh : size + 1;
      this.asc = m ? m.asc : size - 2;
      this.glyphs = (m && m.glyphs) || {};
      this.tints = new Map();      // color → 着色后的整张字库画布（LRU）
      this.bakes = new Map();      // key → 整串文字画布（LRU）
    }
    // 整张字库按颜色着色一次（source-in），之后逐字 drawImage
    tinted(color) {
      let c = this.tints.get(color);
      if (c) { this.tints.delete(color); this.tints.set(color, c); return c; }
      if (!G.ready(this.img)) return null;
      c = G.mkCanvas(this.img.naturalWidth, this.img.naturalHeight);
      const x = c.g;
      x.imageSmoothingEnabled = false;
      x.drawImage(this.img, 0, 0);
      x.globalCompositeOperation = 'source-in';
      x.fillStyle = color;
      x.fillRect(0, 0, c.width, c.height);
      x.globalCompositeOperation = 'source-over';
      this.tints.set(color, c);
      if (this.tints.size > MAX_TINT) this.tints.delete(this.tints.keys().next().value);
      return c;
    }
    has(ch) { return !!this.glyphs[ch]; }
    adv(ch) {
      const gl = this.glyphs[ch];
      if (gl) return gl[2];
      if (ch === '　') return this.size;
      return ch.charCodeAt(0) < 128 ? this.size / 2 : this.size;
    }
    width(str) {
      let w = 0;
      for (const ch of String(str)) w += this.adv(ch);
      return w;
    }
    raw(g, str, x, y, color) {
      const atlas = this.tinted(color);
      let cx = Math.round(x);
      const cy = Math.round(y);
      for (const ch of String(str)) {
        const gl = this.glyphs[ch];
        if (gl && atlas) g.drawImage(atlas, gl[0], gl[1], gl[2], this.lh, cx, cy, gl[2], this.lh);
        else if (!gl && WS.indexOf(ch) < 0) {
          noteMissing(ch);
          g.fillStyle = color;
          g.font = this.size + 'px SimSun, "NSimSun", serif';
          g.textBaseline = 'top';
          g.fillText(ch, cx, cy);
        }
        cx += this.adv(ch);
      }
      return cx;
    }
    // (x, y) = 行顶左上；o = { align: 'left'|'center'|'right', outline, shadow }；返回字宽
    draw(g, str, x, y, color = '#fff', o = {}) {
      str = String(str);
      const w = this.width(str);
      if (o.align === 'center') x -= w / 2;
      else if (o.align === 'right') x -= w;
      x = Math.round(x); y = Math.round(y);
      if (o.shadow) this.raw(g, str, x + 1, y + 1, o.shadow);
      if (o.outline) for (const [dx, dy] of OUT8) this.raw(g, str, x + dx, y + dy, o.outline);
      this.raw(g, str, x, y, color);
      return w;
    }
    // 整串文字画成一张小画布（带描边留 1 px、带投影再留 1 px），给要缩放的 HUD 大字用；缓存
    bake(str, color = '#fff', o = {}) {
      str = String(str);
      const key = str + '|' + color + '|' + (o.outline || '') + '|' + (o.shadow || '');
      let c = this.bakes.get(key);
      if (c) { this.bakes.delete(key); this.bakes.set(key, c); return c; }
      const pad = (o.outline ? 1 : 0), sh = o.shadow ? 1 : 0;
      const w = Math.max(1, Math.ceil(this.width(str)) + pad * 2 + sh);
      const h = this.lh + pad * 2 + sh;
      c = G.mkCanvas(w, h);
      c.g.imageSmoothingEnabled = false;
      this.draw(c.g, str, pad, pad, color, o);
      this.bakes.set(key, c);
      if (this.bakes.size > MAX_BAKE) this.bakes.delete(this.bakes.keys().next().value);
      return c;
    }
    // 逐字折行（中文可用），认 \n；行首禁则
    wrap(str, maxW) {
      const lines = [];
      for (const para of String(str).split('\n')) {
        let line = '';
        let w = 0;
        for (const ch of para) {
          const a = this.adv(ch);
          if (w + a > maxW && line) {
            if (NO_HEAD.indexOf(ch) >= 0) { line += ch; w += a; continue; }
            lines.push(line);
            line = '';
            w = 0;
            if (ch === ' ') continue;
          }
          line += ch;
          w += a;
        }
        lines.push(line);
      }
      return lines;
    }
  }

  G.Font = Font;
  G.initFonts = () => { G.f12 = new Font(12); G.f16 = new Font(16); };
})();
