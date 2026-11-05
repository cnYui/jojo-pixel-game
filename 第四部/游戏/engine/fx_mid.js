// 镰刀、泥拳与磁力合击各有可辨的像素轮廓，让预警与实际命中同源。
'use strict';
(function () {
  const G = window.G, px = G.px, F = G.FX;
  F.clay_fist = (P, x, y, t, t0) => {
    const k = Math.min(1, (t - t0) * 8), h = Math.round(k * 34);
    px.rect(P, x - 12, y - h, 24, h, '#8b593f');
    px.rect(P, x - 15, y - h - 8, 30, 15, '#c3956a');
    for (let i = 0; i < 4; i++) px.rect(P, x - 12 + i * 7, y - h - 10, 5, 7, '#e2bc8a');
  };
  F.scythe_sweep = (P, x, y, t, t0) => {
    const a = Math.min(1, (t - t0) * 7);
    for (let i = 0; i < 40; i++) {
      const ang = (-.8 + i / 40 * 2.2) * Math.PI;
      const r = 45 + a * 90;
      px.line(P, x + Math.cos(ang) * (r - 8), y + Math.sin(ang) * 16,
        x + Math.cos(ang) * r, y + Math.sin(ang) * 18, i % 3 ? '#ffffdf' : '#e685fe', 2, 1 - a * .6);
    }
  };
  F.magnet_junk = (P, x, y, t, t0) => {
    const k = Math.min(1, (t - t0) * 2);
    for (let i = 0; i < 20; i++) {
      const a = i * 2.399 + k * 4, r = 55 * (1 - k) + i % 4;
      const xx = x + Math.cos(a) * r, yy = y + Math.sin(a) * r * .5;
      px.rect(P, xx - 2, yy - 1, 5, 3, i % 2 ? '#e3e4ef' : '#737b8f');
      px.line(P, xx, yy, x, y, '#c0b0fa', 1, .25);
    }
  };
  F.sun_ray = (P, x, y, t, t0, kw = {}) => {
    const w = kw.w || 20, h = kw.h || 36, a = .65 + .25 * Math.sin((t - t0) * 36);
    px.rect(P, x - w / 2, y - h / 2, w, h, '#ff9a30', a);
    for (let i = -2; i <= 2; i++) px.line(P, x + i * w / 6, y - h / 2, x + i * w / 6, y + h / 2, i % 2 ? '#ffcb58' : '#fff4af', 2, a);
  };
  F.geb_claw = (P, x, y, t, t0) => {
    const k = Math.min(1, (t - t0) * 12), h = 28 * k;
    px.ellipse(P, x - 20, y - 5, x + 20, y + 6, '#458ab8', '#b5f6ff');
    const pts = [[x - 13, y], [x - 10, y - h], [x, y - h - 5], [x + 11, y - h], [x + 15, y]];
    px.poly(P, pts, '#66d1ef');
    for (let i = 0; i < pts.length; i++) { const a = pts[i], b = pts[(i + 1) % pts.length]; px.line(P, a[0], a[1], b[0], b[1], '#e3ffff', 1); }
    for (let i = 0; i < 4; i++) px.line(P, x - 9 + i * 6, y - h, x - 12 + i * 8, y - h - 11, '#e9ffff', 2);
  };
  F.geb_column = (P, x, y, t, t0, kw = {}) => {
    const top = kw.top == null ? y - 100 : kw.top, h = y - top;
    px.rect(P, x - 9, top, 18, h, '#3186bb', .8);
    for (let i = 0; i < 5; i++) px.line(P, x - 8 + i * 4, top + Math.sin(t * 25 + i) * 3, x - 8 + i * 4, y, i % 2 ? '#9feeff' : '#e5ffff', 1);
    px.ellipse(P, x - 14, top - 5, x + 14, top + 5, '#99eaff', '#ffffff');
  };
  F.train_pass = (P, x, y, t, t0, kw = {}) => {
    const k = G.clamp((t - t0) / (kw.dur || .45), 0, 1), xx = 480 - k * 800;
    px.rect(P, xx, y - 45, 210, 36, '#293544');
    px.rect(P, xx, y - 47, 210, 4, '#c3cad1');
    for (let i = 0; i < 7; i++) px.rect(P, xx + 7 + i * 28, y - 39, 20, 13, '#efd9a0');
    for (let i = 0; i < 5; i++) px.disc(P, xx + 18 + i * 42, y - 8, 7, '#11131c');
    px.line(P, 0, y + 1, 320, y + 1, '#d3dae4', 2);
  };
  // 贴地的绿色触须线（hazard 的 fxActive：序2 花京院的触须陷阱、第1章花京院 J3 铺的触须网）。以前没有这个 FX，
  //   陷阱 / 网生效后完全看不见（fx_unknown）。kw = { w（宽）, colour, alpha（藏起来的网 .3） }；0.12 s 从左往右长出来
  //   kw.rows / kw.spread（2026-10-09 晚）：花京院 J3 明网铺几排（纵深上下错开 spread px），每排相位不同；默认 1 排（序2 陷阱照旧）
  F.tendrils_line = (P, x, y, t, t0, kw = {}) => {
    if (kw.hz && kw.hz.dead) return;              // 陷阱被踩掉（consume）/ 网缠住人以后就不再画
    const w = Math.max(8, kw.w || 40), a = kw.alpha == null ? 1 : kw.alpha, c = kw.colour || '#50e890';
    const n = Math.round(w * Math.min(1, Math.max(0, (t - t0) / 0.12))), x0 = Math.round(x - w / 2), sh = Math.floor(t * 20);
    const rows = Math.max(1, kw.rows | 0), sp = kw.spread || 0;
    for (let r = 0; r < rows; r++) {
      const dy = rows > 1 ? Math.round((r / (rows - 1) - 0.5) * 2 * sp) : 0, ph = r * 1.7;
      for (let i = 0; i <= n; i++) {
        const yy = Math.round(y + dy + Math.sin(i * 0.45 + t * 6 + ph) * 1.5);
        px.plot(P, x0 + i, yy + 1, '#0c3a20', 0.55 * a);
        px.plot(P, x0 + i, yy - 1, '#0c3a20', 0.3 * a);
        px.plot(P, x0 + i, yy, (i + sh + r * 3) % 9 === 0 ? '#d8ffe8' : c, a);
      }
    }
  };
  for (const n of ['clay_fist', 'scythe_sweep', 'magnet_junk', 'sun_ray', 'geb_claw', 'geb_column', 'train_pass', 'tendrils_line']) F._SIG[n] = ['x', 'y', 't', 't0'];
})();
