// 世界层软件光栅（包 2）：像素会话、屏幕对齐 Bayer 4×4 抖动、点线面圆（照 PIL 的取整规则）、贴精灵（翻转/缩放/旋转/染色/剪影/描边）、亮度映射
'use strict';
(function () {
  const G = window.G;
  const px = {};
  G.px = px;

  // ------------------------------------------------------------------ 常量
  const TAU = Math.PI * 2;
  const BAY = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map(v => v / 16 + 1 / 32);
  px.BAY = BAY;
  px.bay = (x, y) => BAY[((y & 3) << 2) | (x & 3)];
  const SW = () => (G.W || 320), SH = () => (G.H || 180);

  // core.py 的颜色表（包 1 的 G.C 有就用它，没有用这一份）
  const C0 = {
    black: [0, 0, 0], ink: [26, 16, 32], white: [255, 255, 255], cream: [239, 230, 210],
    night0: [8, 6, 22], night1: [20, 16, 52], night2: [40, 30, 90], night3: [70, 50, 130],
    dusk0: [60, 20, 70], dusk1: [150, 40, 90], dusk2: [240, 110, 80], dusk3: [255, 190, 90],
    sky0: [60, 120, 220], sky1: [110, 170, 240], sky2: [180, 220, 255],
    sea0: [10, 40, 90], sea1: [20, 80, 150], sea2: [60, 140, 200],
    sand0: [180, 110, 50], sand1: [225, 160, 80], sand2: [250, 210, 130],
    grass0: [30, 90, 50], grass1: [60, 150, 70],
    stone0: [60, 55, 70], stone1: [110, 100, 115], stone2: [170, 160, 165],
    red: [224, 48, 60], dred: [144, 24, 40], orange: [245, 144, 42],
    yellow: [255, 216, 60], gold: [200, 154, 32], green: [60, 192, 96],
    dgreen: [30, 122, 60], emerald: [40, 230, 140], cyan: [72, 216, 232],
    blue: [60, 100, 220], navy: [30, 40, 96], purple: [154, 76, 224],
    dpurple: [90, 40, 144], magenta: [240, 88, 180], pink: [255, 150, 200],
    menace: [170, 60, 220],
  };

  // ------------------------------------------------------------------ 颜色
  // 打包格式 0xAABBGGRR（小端 Uint32 视图），alpha 恒 255
  const pack = (r, g, b) => ((0xff000000 | ((b & 255) << 16) | ((g & 255) << 8) | (r & 255)) >>> 0);
  px.pack = pack;
  const colCache = new Map();
  function parseHex(s) {
    let h = s.charAt(0) === '#' ? s.slice(1) : s;
    if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    const n = parseInt(h.slice(0, 6), 16);
    if (!(n >= 0)) return null;
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  // c：'#rrggbb' / '#rgb' / [r,g,b] / G.C 的名字 / 已打包的整数 → [r,g,b]
  function rgbArr(c) {
    if (c == null) return [255, 255, 255];
    if (typeof c === 'number') return [c & 255, (c >>> 8) & 255, (c >>> 16) & 255];
    if (Array.isArray(c) || ArrayBuffer.isView(c)) return [c[0] | 0, c[1] | 0, c[2] | 0];
    if (typeof c === 'string') {
      const tab = G.C || C0;
      const v = tab[c] || C0[c];
      if (v) return [v[0], v[1], v[2]];
      const a = parseHex(c);
      if (a) return a;
    }
    return [255, 0, 255];
  }
  px.rgbArr = rgbArr;
  px.rgb = function (c) {
    if (typeof c === 'number') return c >>> 0;
    if (typeof c === 'string') {
      let v = colCache.get(c);
      if (v === undefined) { const a = rgbArr(c); v = pack(a[0], a[1], a[2]); colCache.set(c, v); }
      return v;
    }
    const a = rgbArr(c);
    return pack(a[0], a[1], a[2]);
  };
  px.unpack = v => [v & 255, (v >>> 8) & 255, (v >>> 16) & 255, (v >>> 24) & 255];
  // fx.py 的 _light / _dark（int 截断）、core.py 的 mix（四舍五入）
  px.light = (c, k = 0.5) => {
    const v = px.rgb(c), r = v & 255, g = (v >>> 8) & 255, b = (v >>> 16) & 255;
    return pack((r + (255 - r) * k) | 0, (g + (255 - g) * k) | 0, (b + (255 - b) * k) | 0);
  };
  px.dark = (c, k = 0.5) => {
    const v = px.rgb(c);
    return pack(((v & 255) * k) | 0, (((v >>> 8) & 255) * k) | 0, (((v >>> 16) & 255) * k) | 0);
  };
  px.mix = (c1, c2, u) => {
    const a = px.rgb(c1), b = px.rgb(c2);
    u = u < 0 ? 0 : u > 1 ? 1 : u;
    const ar = a & 255, ag = (a >>> 8) & 255, ab = (a >>> 16) & 255;
    return pack(Math.round(ar + ((b & 255) - ar) * u), Math.round(ag + (((b >>> 8) & 255) - ag) * u),
      Math.round(ab + (((b >>> 16) & 255) - ab) * u));
  };

  // ------------------------------------------------------------------ 会话
  px.cur = null;
  px.begin = function (ctx) {
    if (px.cur) throw new Error('G.px.begin: pixel session already open');
    const c = ctx.canvas, w = c.width, h = c.height;
    const img = ctx.getImageData(0, 0, w, h);
    const P = { u32: new Uint32Array(img.data.buffer), w, h, img, ctx };
    px.cur = P;
    return P;
  };
  px.end = function () {
    const P = px.cur;
    if (!P) return;
    px.cur = null;
    P.ctx.putImageData(P.img, 0, 0);
  };
  // 离屏缓冲当会话用（测试、缓存计算）：{u32, w, h}
  px.buffer = (w, h) => ({ u32: new Uint32Array(w * h), w, h });

  // ------------------------------------------------------------------ 取整（照 Pillow Draw.c）
  const RUP = f => (f >= 0 ? Math.floor(f + 0.5) : -Math.floor(-f + 0.5));   // ROUND_UP
  const RDN = f => (f >= 0 ? Math.ceil(f - 0.5) : -Math.ceil(-f - 0.5));     // ROUND_DOWN
  px.RUP = RUP; px.RDN = RDN;

  // ------------------------------------------------------------------ 点、矩形
  function plot(P, x, y, c, a = 1) {
    x = Math.round(x); y = Math.round(y);
    if (x < 0 || y < 0 || x >= P.w || y >= P.h) return;
    if (a < 1 && !(BAY[((y & 3) << 2) | (x & 3)] < a)) return;
    P.u32[y * P.w + x] = c;
  }
  // 整数坐标点（调用方已取整），c 已打包
  function dot(P, x, y, c) {
    if (x < 0 || y < 0 || x >= P.w || y >= P.h) return;
    P.u32[y * P.w + x] = c;
  }
  px.plot = (P, x, y, c, a = 1) => plot(P, x, y, typeof c === 'number' ? c : px.rgb(c), a);
  px.dot = dot;
  // [x, x+w) × [y, y+h)
  px.rect = function (P, x, y, w, h, c, a = 1) {
    c = typeof c === 'number' ? c : px.rgb(c);
    let x0 = Math.round(x), y0 = Math.round(y), x1 = x0 + Math.round(w), y1 = y0 + Math.round(h);
    if (x0 < 0) x0 = 0; if (y0 < 0) y0 = 0; if (x1 > P.w) x1 = P.w; if (y1 > P.h) y1 = P.h;
    const u = P.u32, W = P.w;
    for (let yy = y0; yy < y1; yy++) {
      const row = yy * W, br = (yy & 3) << 2;
      if (a >= 1) for (let xx = x0; xx < x1; xx++) u[row + xx] = c;
      else for (let xx = x0; xx < x1; xx++) if (BAY[br | (xx & 3)] < a) u[row + xx] = c;
    }
  };
  // PIL rectangle((x0,y0,x1,y1))：两端都包含
  px.box = (P, x0, y0, x1, y1, c, a = 1) => px.rect(P, Math.round(x0), Math.round(y0),
    Math.round(x1) - Math.round(x0) + 1, Math.round(y1) - Math.round(y0) + 1, c, a);
  function hline(P, x0, x1, y, c, a) {
    if (y < 0 || y >= P.h) return;
    if (x0 < 0) x0 = 0;
    if (x1 >= P.w) x1 = P.w - 1;
    const u = P.u32, row = y * P.w, br = (y & 3) << 2;
    if (a >= 1) for (let x = x0; x <= x1; x++) u[row + x] = c;
    else for (let x = x0; x <= x1; x++) if (BAY[br | (x & 3)] < a) u[row + x] = c;
  }
  px.hline = hline;

  // ------------------------------------------------------------------ 线
  // Bresenham（端点按 PIL 的 (int) 截断）
  function line1(P, x0, y0, x1, y1, c, a) {
    x0 = Math.trunc(x0); y0 = Math.trunc(y0); x1 = Math.trunc(x1); y1 = Math.trunc(y1);
    const W = P.w, Hh = P.h, u = P.u32;
    let dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0);
    const sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1;
    let err = dx + dy;
    // 完全在画面外的长线快速跳过
    if ((x0 < 0 && x1 < 0) || (y0 < 0 && y1 < 0) || (x0 >= W && x1 >= W) || (y0 >= Hh && y1 >= Hh)) return;
    for (let guard = 0; guard < 4096; guard++) {
      if (x0 >= 0 && y0 >= 0 && x0 < W && y0 < Hh && (a >= 1 || BAY[((y0 & 3) << 2) | (x0 & 3)] < a)) u[y0 * W + x0] = c;
      if (x0 === x1 && y0 === y1) break;
      const e2 = 2 * err;
      if (e2 >= dy) { err += dy; x0 += sx; }
      if (e2 <= dx) { err += dx; y0 += sy; }
    }
  }
  // PIL ImagingDrawWideLine：宽线 = 一个四边形
  const _wq = new Float64Array(8);
  function lineWide(P, x0, y0, x1, y1, c, a, width) {
    x0 = Math.trunc(x0); y0 = Math.trunc(y0); x1 = Math.trunc(x1); y1 = Math.trunc(y1);
    const dx = x1 - x0, dy = y1 - y0;
    if (dx === 0 && dy === 0) { plot(P, x0, y0, c, a); return; }
    const big = Math.hypot(dx, dy), small = (width - 1) / 2;
    const rmax = RUP(small) / big, rmin = RDN(small) / big;
    const dxmin = RDN(rmin * dy), dxmax = RDN(rmax * dy), dymin = RDN(rmin * dx), dymax = RDN(rmax * dx);
    _wq[0] = x0 - dxmin; _wq[1] = y0 + dymax; _wq[2] = x1 - dxmin; _wq[3] = y1 + dymax;
    _wq[4] = x1 + dxmax; _wq[5] = y1 - dymin; _wq[6] = x0 + dxmax; _wq[7] = y0 - dymin;
    fillPoly(P, _wq, 4, c, a, false);
  }
  px.line = function (P, x0, y0, x1, y1, c, a = 1, width = 1) {
    c = typeof c === 'number' ? c : px.rgb(c);
    if (width > 1) lineWide(P, x0, y0, x1, y1, c, a, Math.round(width));
    else line1(P, x0, y0, x1, y1, c, a);
  };
  // 折线：pts = [[x,y],…] 或扁平 [x0,y0,x1,y1,…]（PIL d.line(pts) 逐段画）
  px.lines = function (P, pts, c, a = 1, width = 1) {
    c = typeof c === 'number' ? c : px.rgb(c);
    const flat = typeof pts[0] === 'number';
    const n = flat ? pts.length >> 1 : pts.length;
    for (let i = 0; i < n - 1; i++) {
      const ax = flat ? pts[2 * i] : pts[i][0], ay = flat ? pts[2 * i + 1] : pts[i][1];
      const bx = flat ? pts[2 * i + 2] : pts[i + 1][0], by = flat ? pts[2 * i + 3] : pts[i + 1][1];
      if (width > 1) lineWide(P, ax, ay, bx, by, c, a, Math.round(width));
      else line1(P, ax, ay, bx, by, c, a);
    }
  };

  // ------------------------------------------------------------------ 多边形（照 Pillow polygon_generic）
  const _ex0 = new Float64Array(64), _ey0 = new Float64Array(64), _edx = new Float64Array(64);
  const _eymin = new Int32Array(64), _eymax = new Int32Array(64);
  const _xx = new Float64Array(160);
  const _vx = new Int32Array(64), _vy = new Int32Array(64);
  // flat：扁平坐标数组；n：顶点数；round：顶点是否先取整（Pillow 会取整，内部宽线已是整数）
  function fillPoly(P, flat, n, c, a, round = true) {
    if (n < 2 || n > 60) return;
    for (let i = 0; i < n; i++) {
      _vx[i] = round ? RUP(flat[2 * i]) : flat[2 * i];
      _vy[i] = round ? RUP(flat[2 * i + 1]) : flat[2 * i + 1];
    }
    let ne = 0, ymin = 1 << 30, ymax = -(1 << 30);
    for (let i = 0; i < n; i++) {
      const j = i + 1 < n ? i + 1 : 0;
      if (j === 0 && n > 1 && _vx[i] === _vx[0] && _vy[i] === _vy[0]) continue;
      const x0 = _vx[i], y0 = _vy[i], x1 = _vx[j], y1 = _vy[j];
      const emin = y0 < y1 ? y0 : y1, emax = y0 < y1 ? y1 : y0;
      if (emin < ymin) ymin = emin;
      if (emax > ymax) ymax = emax;
      if (y0 === y1) { hline(P, x0 < x1 ? x0 : x1, x0 < x1 ? x1 : x0, y0, c, a); continue; }
      _ex0[ne] = x0; _ey0[ne] = y0; _edx[ne] = (x1 - x0) / (y1 - y0); _eymin[ne] = emin; _eymax[ne] = emax; ne++;
    }
    if (ymin < 0) ymin = 0;
    if (ymax > P.h - 1) ymax = P.h - 1;
    for (let y = ymin; y <= ymax; y++) {
      let k = 0;
      for (let i = 0; i < ne; i++) {
        if (y >= _eymin[i] && y <= _eymax[i]) {
          _xx[k++] = (y - _ey0[i]) * _edx[i] + _ex0[i];
          if (y === _eymax[i] && y < ymax) { _xx[k] = _xx[k - 1]; k++; }
        }
      }
      // 插入排序（k 很小）
      for (let i = 1; i < k; i++) {
        const v = _xx[i]; let j = i - 1;
        while (j >= 0 && _xx[j] > v) { _xx[j + 1] = _xx[j]; j--; }
        _xx[j + 1] = v;
      }
      for (let i = 1; i < k; i += 2) {
        const xs = RUP(_xx[i - 1]), xe = RDN(_xx[i]);
        if (xe < xs) continue;
        hline(P, xs, xe, y, c, a);
      }
    }
  }
  const _pf = new Float64Array(128);
  px.poly = function (P, pts, c, a = 1) {
    c = typeof c === 'number' ? c : px.rgb(c);
    const flat = typeof pts[0] === 'number';
    const n = Math.min(60, flat ? pts.length >> 1 : pts.length);
    for (let i = 0; i < n; i++) {
      _pf[2 * i] = flat ? pts[2 * i] : pts[i][0];
      _pf[2 * i + 1] = flat ? pts[2 * i + 1] : pts[i][1];
    }
    fillPoly(P, _pf, n, c, a, true);
  };
  px.tri = function (P, x0, y0, x1, y1, x2, y2, c, a = 1) {
    c = typeof c === 'number' ? c : px.rgb(c);
    _pf[0] = x0; _pf[1] = y0; _pf[2] = x1; _pf[3] = y1; _pf[4] = x2; _pf[5] = y2;
    fillPoly(P, _pf, 3, c, a, true);
  };
  px.quad = function (P, x0, y0, x1, y1, x2, y2, x3, y3, c, a = 1) {
    c = typeof c === 'number' ? c : px.rgb(c);
    _pf[0] = x0; _pf[1] = y0; _pf[2] = x1; _pf[3] = y1; _pf[4] = x2; _pf[5] = y2; _pf[6] = x3; _pf[7] = y3;
    fillPoly(P, _pf, 4, c, a, true);
  };
  px.fillPoly = fillPoly;

  // ------------------------------------------------------------------ 圆、环、椭圆
  // fx._disc_np：dx² + (dy/sq)² ≤ r² + 0.6r，圆心先取整
  px.disc = function (P, cx, cy, r, c, a = 1, sq = 1) {
    if (!(r > 0)) return;
    c = typeof c === 'number' ? c : px.rgb(c);
    cx = Math.round(cx); cy = Math.round(cy);
    const ry = r * sq;
    let x0 = Math.trunc(cx - r - 1), y0 = Math.trunc(cy - ry - 1), x1 = Math.trunc(cx + r + 2), y1 = Math.trunc(cy + ry + 2);
    if (x0 < 0) x0 = 0; if (y0 < 0) y0 = 0; if (x1 > P.w) x1 = P.w; if (y1 > P.h) y1 = P.h;
    if (x1 <= x0 || y1 <= y0) return;
    const lim = r * r + r * 0.6, isq = 1 / Math.max(sq, 1e-3), u = P.u32, W = P.w;
    for (let y = y0; y < y1; y++) {
      const dy = (y - cy) * isq, dy2 = dy * dy, row = y * W, br = (y & 3) << 2;
      for (let x = x0; x < x1; x++) {
        const dx = x - cx;
        if (dx * dx + dy2 <= lim && (a >= 1 || BAY[br | (x & 3)] < a)) u[row + x] = c;
      }
    }
  };
  // 环：|dist − r| ≤ wd/2 + 0.3（shockwave 同款），圆心先取整
  px.ring = function (P, cx, cy, r, wd, c, a = 1, sq = 1) {
    c = typeof c === 'number' ? c : px.rgb(c);
    cx = Math.round(cx); cy = Math.round(cy);
    const sqv = Math.max(sq, 0.05);
    let x0 = Math.trunc(cx - r - wd - 2), y0 = Math.trunc(cy - (r + wd) * sqv - 2);
    let x1 = Math.trunc(cx + r + wd + 3), y1 = Math.trunc(cy + (r + wd) * sqv + 3);
    if (x0 < 0) x0 = 0; if (y0 < 0) y0 = 0; if (x1 > P.w) x1 = P.w; if (y1 > P.h) y1 = P.h;
    const tol = wd / 2 + 0.3, u = P.u32, W = P.w;
    for (let y = y0; y < y1; y++) {
      const dy = (y - cy) / sqv, dy2 = dy * dy, row = y * W, br = (y & 3) << 2;
      for (let x = x0; x < x1; x++) {
        const dx = x - cx, d = Math.sqrt(dx * dx + dy2);
        if (Math.abs(d - r) <= tol && (a >= 1 || BAY[br | (x & 3)] < a)) u[row + x] = c;
      }
    }
  };
  // PIL ellipse((x0,y0,x1,y1), fill, outline, width)：外框两端包含
  px.ellipse = function (P, x0, y0, x1, y1, fill, outline, width = 1, a = 1) {
    if (x1 < x0 || y1 < y0) return;
    const fc = fill == null ? null : (typeof fill === 'number' ? fill : px.rgb(fill));
    const oc = outline == null ? null : (typeof outline === 'number' ? outline : px.rgb(outline));
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    const ra = (x1 - x0) / 2 + 0.5, rb = (y1 - y0) / 2 + 0.5;
    const ia = ra - width, ib = rb - width;
    let bx0 = Math.floor(x0), by0 = Math.floor(y0), bx1 = Math.ceil(x1), by1 = Math.ceil(y1);
    if (bx0 < 0) bx0 = 0; if (by0 < 0) by0 = 0; if (bx1 > P.w - 1) bx1 = P.w - 1; if (by1 > P.h - 1) by1 = P.h - 1;
    const u = P.u32, W = P.w;
    for (let y = by0; y <= by1; y++) {
      const ny = (y - cy) / rb, ny2 = ny * ny, iy = ib > 0 ? (y - cy) / ib : 0, iy2 = iy * iy, br = (y & 3) << 2;
      for (let x = bx0; x <= bx1; x++) {
        const nx = (x - cx) / ra;
        if (nx * nx + ny2 > 1) continue;
        if (a < 1 && !(BAY[br | (x & 3)] < a)) continue;
        let inner = false;
        if (ia > 0 && ib > 0) { const jx = (x - cx) / ia; inner = jx * jx + iy2 <= 1; }
        if (oc != null && !inner) u[y * W + x] = oc;
        else if (fc != null) u[y * W + x] = fc;
      }
    }
  };

  // ------------------------------------------------------------------ 混色
  // fx._qblend 单像素版：q = floor(clip(A)·levels + bayer)/levels
  px.qblend = function (P, x, y, col, A, levels = 3, add = false) {
    if (x < 0 || y < 0 || x >= P.w || y >= P.h) return;
    const cv = typeof col === 'number' ? col : px.rgb(col);
    qblendI(P.u32, y * P.w + x, x, y, cv & 255, (cv >>> 8) & 255, (cv >>> 16) & 255, A, levels, add);
  };
  function qblendI(u, i, x, y, cr, cg, cb, A, levels, add) {
    if (A <= 0) return;
    let q = Math.floor((A > 1 ? 1 : A) * levels + BAY[((y & 3) << 2) | (x & 3)]) / levels;
    if (q <= 0) return;
    if (q > 1) q = 1;
    const v = u[i];
    let r = v & 255, g = (v >>> 8) & 255, b = (v >>> 16) & 255;
    if (add) { r += cr * q; g += cg * q; b += cb * q; } else { r += (cr - r) * q; g += (cg - g) * q; b += (cb - b) * q; }
    u[i] = pack(r > 255 ? 255 : r | 0, g > 255 ? 255 : g | 0, b > 255 ? 255 : b | 0);
  }
  px.qblendI = qblendI;
  // 平滑混色（Image.blend / 平滑 alpha）：dst + (c − dst)·k
  px.blendI = function (u, i, cr, cg, cb, k) {
    const v = u[i], r = v & 255, g = (v >>> 8) & 255, b = (v >>> 16) & 255;
    u[i] = pack(r + (cr - r) * k + 0.5, g + (cg - g) * k + 0.5, b + (cb - b) * k + 0.5);
  };

  // ------------------------------------------------------------------ 精灵变体（outline → tint → flip → scale → rotate，同 sprite._variant）
  const idMap = new WeakMap();
  let idSeq = 1;
  const srcId = o => { let v = idMap.get(o); if (!v) { v = idSeq++; idMap.set(o, v); } return v; };
  const varCache = new Map();
  const VAR_MAX = 600;
  function tintKey(t) {
    if (!t) return '';
    if (typeof t === 'string') return t;
    return (typeof t.c === 'number' ? t.c : String(t.c)) + ':' + (Math.round((t.k == null ? 1 : t.k) * 1000) / 1000);
  }
  // 取出区域 → {u32, w, h, ax, ay}（ax/ay = 锚点在区域里的位置）
  function crop(src, sx, sy, sw, sh) {
    const out = new Uint32Array(sw * sh), s = src.u32, SWd = src.w;
    for (let y = 0; y < sh; y++) {
      const yy = sy + y;
      if (yy < 0 || yy >= src.h) continue;
      for (let x = 0; x < sw; x++) {
        const xx = sx + x;
        if (xx >= 0 && xx < SWd) out[y * sw + x] = s[yy * SWd + xx];
      }
    }
    return out;
  }
  function doOutline(u, w, h, col) {
    const W2 = w + 2, H2 = h + 2, out = new Uint32Array(W2 * H2);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) out[(y + 1) * W2 + x + 1] = u[y * w + x];
    const c = col;
    for (let y = 0; y < H2; y++) for (let x = 0; x < W2; x++) {
      const i = y * W2 + x;
      if (out[i] >>> 24) continue;
      const l = x > 0 && (out[i - 1] >>> 24) && !isRing(out, i - 1), r = x < W2 - 1 && (out[i + 1] >>> 24) && !isRing(out, i + 1);
      const t = y > 0 && (out[i - W2] >>> 24) && !isRing(out, i - W2), b = y < H2 - 1 && (out[i + W2] >>> 24) && !isRing(out, i + W2);
      if (l || r || t || b) out[i] = (c & 0x00ffffff) | 0x01000000;   // 先标记（alpha 1），免得新描边被当成本体
    }
    for (let i = 0; i < out.length; i++) if ((out[i] >>> 24) === 1) out[i] = (c | 0xff000000) >>> 0;
    return out;
  }
  const isRing = (u, i) => (u[i] >>> 24) === 1;
  function doTint(u, tint) {
    let mode = tint, k = 1, cr = 255, cg = 255, cb = 255;
    if (typeof tint === 'object') { mode = tint.c; k = tint.k == null ? 1 : tint.k; }
    if (k <= 0) return;
    if (mode !== 'white' && mode !== 'black' && mode !== 'silhouette' && mode !== 'gray' && mode !== 'invert') {
      const v = px.rgb(mode); cr = v & 255; cg = (v >>> 8) & 255; cb = (v >>> 16) & 255; mode = 'col';
    }
    for (let i = 0; i < u.length; i++) {
      const v = u[i]; if (!(v >>> 24)) continue;
      let r = v & 255, g = (v >>> 8) & 255, b = (v >>> 16) & 255;
      if (mode === 'white') { r += (255 - r) * k; g += (255 - g) * k; b += (255 - b) * k; }
      else if (mode === 'black' || mode === 'silhouette') { r *= 1 - k; g *= 1 - k; b *= 1 - k; }
      else if (mode === 'gray') { const l = r * 0.299 + g * 0.587 + b * 0.114; r = r * (1 - k) + l * k; g = g * (1 - k) + l * k; b = b * (1 - k) + l * k; }
      else if (mode === 'invert') { r = r * (1 - k) + (255 - r) * k; g = g * (1 - k) + (255 - g) * k; b = b * (1 - k) + (255 - b) * k; }
      else { r = r * (1 - k) + cr * k; g = g * (1 - k) + cg * k; b = b * (1 - k) + cb * k; }
      // np.clip(...).astype(uint8)：截断
      u[i] = ((v & 0xff000000) | ((b > 255 ? 255 : b < 0 ? 0 : b | 0) << 16) | ((g > 255 ? 255 : g < 0 ? 0 : g | 0) << 8) | (r > 255 ? 255 : r < 0 ? 0 : r | 0)) >>> 0;
    }
  }
  function doRotate(u, w, h, ax, ay, deg) {
    // deg：顺时针为正（Canvas 约定）；绕图中心旋转并扩大画布（PIL rotate(expand=True) 的做法）
    const th = deg * Math.PI / 180, cs = Math.cos(th), sn = Math.sin(th);
    const cx = w / 2, cy = h / 2;
    const cw = Math.abs(w * cs) + Math.abs(h * sn), ch = Math.abs(w * sn) + Math.abs(h * cs);
    const W2 = Math.ceil(cw - 1e-6), H2 = Math.ceil(ch - 1e-6);
    const out = new Uint32Array(W2 * H2), ncx = W2 / 2, ncy = H2 / 2;
    for (let y = 0; y < H2; y++) for (let x = 0; x < W2; x++) {
      const dx = x + 0.5 - ncx, dy = y + 0.5 - ncy;
      const sx = Math.floor(dx * cs + dy * sn + cx), sy = Math.floor(-dx * sn + dy * cs + cy);
      if (sx >= 0 && sy >= 0 && sx < w && sy < h) out[y * W2 + x] = u[sy * w + sx];
    }
    const dx = ax - cx, dy = ay - cy;
    return { u32: out, w: W2, h: H2, ax: ncx + dx * cs - dy * sn, ay: ncy + dx * sn + dy * cs };
  }
  function doScale(u, w, h, s) {
    const W2 = Math.max(1, Math.round(w * s)), H2 = Math.max(1, Math.round(h * s)), out = new Uint32Array(W2 * H2);
    for (let y = 0; y < H2; y++) {
      const sy = Math.min(h - 1, Math.floor((y + 0.5) * h / H2));
      for (let x = 0; x < W2; x++) out[y * W2 + x] = u[sy * w + Math.min(w - 1, Math.floor((x + 0.5) * w / W2))];
    }
    return { u32: out, w: W2, h: H2 };
  }
  function dilate(u, w, h, grow) {
    let m = new Uint8Array(w * h);
    for (let i = 0; i < u.length; i++) m[i] = (u[i] >>> 24) ? 1 : 0;
    for (let g = 0; g < grow; g++) {
      const n = m.slice();
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        const i = y * w + x;
        if (m[i]) continue;
        if ((x > 0 && m[i - 1]) || (x < w - 1 && m[i + 1]) || (y > 0 && m[i - w]) || (y < h - 1 && m[i + w])) n[i] = 1;
      }
      m = n;
    }
    return m;
  }
  px.dilate = dilate;
  // 变体：o = { flip, scale, rotDeg, tint, sil, outline, grow, ax, ay }
  function variant(src, sx, sy, sw, sh, o) {
    const flip = !!o.flip, scale = o.scale || 1, rot = o.rotDeg ? Math.round(o.rotDeg / 5) * 5 % 360 : 0;
    const tk = tintKey(o.tint), sil = o.sil == null ? '' : px.rgb(o.sil), ol = o.outline == null ? '' : px.rgb(o.outline);
    const grow = o.grow | 0, ax0 = o.ax || 0, ay0 = o.ay || 0;
    const key = srcId(src) + '|' + sx + ',' + sy + ',' + sw + ',' + sh + '|' + (flip ? 1 : 0) + '|' + scale + '|' + rot + '|' + tk +
      '|' + sil + '|' + ol + '|' + grow + '|' + ax0 + ',' + ay0;
    let v = varCache.get(key);
    if (v) { varCache.delete(key); varCache.set(key, v); return v; }
    let u = crop(src, sx, sy, sw, sh), w = sw, h = sh, ax = ax0, ay = ay0;
    if (grow > 0) {                        // sprite.aura：剪影 4 邻域膨胀（画布四周加 grow）
      const W2 = w + 2 * grow, H2 = h + 2 * grow, big = new Uint32Array(W2 * H2);
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) big[(y + grow) * W2 + x + grow] = u[y * w + x];
      const m = dilate(big, W2, H2, grow);
      for (let i = 0; i < big.length; i++) big[i] = m[i] ? 0xffffffff : 0;
      u = big; w = W2; h = H2; ax += grow; ay += grow;
    }
    if (ol !== '') { u = doOutline(u, w, h, ol); w += 2; h += 2; ax += 1; ay += 1; }
    if (tk) doTint(u, o.tint);
    if (sil !== '') { const c = (sil | 0xff000000) >>> 0; for (let i = 0; i < u.length; i++) if (u[i] >>> 24) u[i] = c; }
    if (flip) {
      const out = new Uint32Array(w * h);
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) out[y * w + (w - 1 - x)] = u[y * w + x];
      u = out; ax = w - ax;
    }
    if (scale !== 1) { const r = doScale(u, w, h, scale); u = r.u32; ax *= r.w / w; ay *= r.h / h; w = r.w; h = r.h; }
    if (rot) { const r = doRotate(u, w, h, ax, ay, rot); u = r.u32; w = r.w; h = r.h; ax = r.ax; ay = r.ay; }
    v = { u32: u, w, h, ax, ay };
    varCache.set(key, v);
    if (varCache.size > VAR_MAX) varCache.delete(varCache.keys().next().value);
    return v;
  }
  px.variant = variant;

  // 把变体 v 的锚点放到 (x, y) 贴上；alpha = 抖动透明，opacity = 平滑透明（替身 0.92、光环 0.55）
  function stamp(P, v, x, y, alpha = 1, opacity = 1) {
    if (alpha <= 0 || opacity <= 0) return;
    const ox = Math.round(x - v.ax), oy = Math.round(y - v.ay);
    let x0 = 0, y0 = 0, x1 = v.w, y1 = v.h;
    if (ox + x0 < 0) x0 = -ox;
    if (oy + y0 < 0) y0 = -oy;
    if (ox + x1 > P.w) x1 = P.w - ox;
    if (oy + y1 > P.h) y1 = P.h - oy;
    if (x1 <= x0 || y1 <= y0) return;
    const s = v.u32, u = P.u32, W = P.w, sw = v.w;
    for (let yy = y0; yy < y1; yy++) {
      const Y = oy + yy, row = Y * W, br = (Y & 3) << 2, srow = yy * sw;
      for (let xx = x0; xx < x1; xx++) {
        const c = s[srow + xx], ca = c >>> 24;
        if (!ca) continue;
        const X = ox + xx;
        if (alpha < 1 && !(BAY[br | (X & 3)] < alpha)) continue;
        const k = opacity * (ca / 255);
        if (k >= 0.999) u[row + X] = c | 0xff000000;
        else {
          const d = u[row + X], dr = d & 255, dg = (d >>> 8) & 255, db = (d >>> 16) & 255;
          u[row + X] = pack(dr + ((c & 255) - dr) * k + 0.5, dg + (((c >>> 8) & 255) - dg) * k + 0.5, db + (((c >>> 16) & 255) - db) * k + 0.5);
        }
      }
    }
  }
  px.stamp = stamp;

  // 软件贴图：src = {u32, w, h}（G.pix / Atlas.pix 的结果）；(dx, dy) = 区域左上角（有 o.ax/o.ay 时 = 该锚点减去 ax/ay）
  // o = { flip, scale, rotDeg（顺时针，5° 量化缓存）, alpha（抖动）, opacity（平滑，扩展）, tint: {c, k} | 'white', sil, outline, grow, ax, ay }
  px.blit = function (P, src, sx, sy, sw, sh, dx, dy, o = {}) {
    if (!src || !src.u32) return;
    sx = sx | 0; sy = sy | 0;
    sw = sw == null ? src.w : sw | 0; sh = sh == null ? src.h : sh | 0;
    const v = variant(src, sx, sy, sw, sh, o);
    stamp(P, v, dx + (o.ax || 0), dy + (o.ay || 0), o.alpha == null ? 1 : o.alpha, o.opacity == null ? 1 : o.opacity);
  };
  // 从角色图集取帧按 pivot 贴到 (x, y)（Atlas.pix；cid 可写 'scene:xxx' / 'prop:xxx'）
  px.framePix = function (cid, logical, frame, flip) {
    let A = null;
    if (typeof cid === 'string' && cid.indexOf('prop:') === 0) A = G.propAtlas ? G.propAtlas(cid.slice(5)) : null;
    else if (typeof cid === 'string' && cid.indexOf('scene:') === 0) A = G.propAtlas ? G.propAtlas(cid) : null;
    else A = G.atlas ? G.atlas(cid) : null;
    if (!A || !A.pix) return null;
    const p = A.pix(logical, frame | 0, false);
    return p && p.u32 ? p : null;
  };
  px.blitFrame = function (P, cid, logical, frame, x, y, o = {}) {
    const p = px.framePix(cid, logical, frame);
    if (!p) return false;
    const v = variant(p, 0, 0, p.w, p.h, Object.assign({}, o, { ax: p.ox || 0, ay: p.oy || 0 }));
    stamp(P, v, x, y, o.alpha == null ? 1 : o.alpha, o.opacity == null ? 1 : o.opacity);
    return true;
  };

  // ------------------------------------------------------------------ 全屏滤镜
  const lutCache = new Map();
  // 调色板（打包色数组）→ LUT[bayer 16][lum 256] 直接给输出色
  function lumLUT(pal, strength, gamma) {
    const key = pal.join(',') + '|' + strength + '|' + gamma;
    let L = lutCache.get(key);
    if (L) return L;
    L = new Uint32Array(16 * 256);
    const n = pal.length;
    for (let b = 0; b < 16; b++) for (let l = 0; l < 256; l++) {
      let lum = l / 255;
      if (gamma !== 1) lum = Math.pow(lum, gamma);
      let k = Math.floor(lum * (n - 1) + 0.5 + (BAY[b] - 0.5) * strength);
      if (k < 0) k = 0; else if (k > n - 1) k = n - 1;
      L[b * 256 + l] = pal[k];
    }
    lutCache.set(key, L);
    if (lutCache.size > 48) lutCache.delete(lutCache.keys().next().value);
    return L;
  }
  px.lumLUT = lumLUT;
  const lum8 = v => ((299 * (v & 255) + 587 * ((v >>> 8) & 255) + 114 * ((v >>> 16) & 255) + 500) / 1000) | 0;
  px.lum8 = lum8;
  // fx._lummap：pal = 颜色数组（暗→亮）；amount < 1 时只换 bayer < amount 的像素；box = [x0,y0,x1,y1]
  px.lummap = function (P, pal, strength = 0.5, gamma = 0.9, amount = 1, box = null) {
    if (amount <= 0) return;
    const pp = pal.map(c => px.rgb(c));
    const L = lumLUT(pp, strength, gamma), u = P.u32, W = P.w;
    let x0 = 0, y0 = 0, x1 = P.w, y1 = P.h;
    if (box) { x0 = Math.max(0, box[0] | 0); y0 = Math.max(0, box[1] | 0); x1 = Math.min(P.w, box[2] | 0); y1 = Math.min(P.h, box[3] | 0); }
    for (let y = y0; y < y1; y++) {
      const row = y * W, br = (y & 3) << 2;
      for (let x = x0; x < x1; x++) {
        const b = br | (x & 3);
        if (amount < 1 && !(BAY[b] < amount)) continue;
        const v = u[row + x];
        u[row + x] = L[(b << 8) | lum8(v)];
      }
    }
  };
  px.invert = function (P, box = null) {
    const u = P.u32, W = P.w;
    let x0 = 0, y0 = 0, x1 = P.w, y1 = P.h;
    if (box) { x0 = Math.max(0, box[0] | 0); y0 = Math.max(0, box[1] | 0); x1 = Math.min(P.w, box[2] | 0); y1 = Math.min(P.h, box[3] | 0); }
    for (let y = y0; y < y1; y++) for (let x = x0, i = y * W + x0; x < x1; x++, i++) u[i] = (u[i] ^ 0x00ffffff) >>> 0;
  };
  // core.filt_gray（平滑，可带 tint）
  px.gray = function (P, amount = 1, tint = null) {
    if (amount <= 0) return;
    const u = P.u32, tv = tint == null ? null : px.rgb(tint);
    const tr = tv == null ? 1 : (tv & 255) / 255, tg = tv == null ? 1 : ((tv >>> 8) & 255) / 255, tb = tv == null ? 1 : ((tv >>> 16) & 255) / 255;
    for (let i = 0; i < u.length; i++) {
      const v = u[i], r = v & 255, g = (v >>> 8) & 255, b = (v >>> 16) & 255, l = r * 0.299 + g * 0.587 + b * 0.114;
      u[i] = pack(r * (1 - amount) + l * tr * amount, g * (1 - amount) + l * tg * amount, b * (1 - amount) + l * tb * amount);
    }
  };
  // core.filt_tint（平滑混向 c）
  px.tint = function (P, c, amount) {
    if (amount <= 0) return;
    const cv = px.rgb(c), cr = cv & 255, cg = (cv >>> 8) & 255, cb = (cv >>> 16) & 255, u = P.u32, k = Math.min(1, amount);
    for (let i = 0; i < u.length; i++) {
      const v = u[i], r = v & 255, g = (v >>> 8) & 255, b = (v >>> 16) & 255;
      u[i] = pack(r * (1 - k) + cr * k, g * (1 - k) + cg * k, b * (1 - k) + cb * k);
    }
  };

  // ------------------------------------------------------------------ 距离 / 角度场（按中心缓存）
  const fieldCache = new Map();
  function cachePut(key, v) {
    fieldCache.set(key, v);
    if (fieldCache.size > 24) fieldCache.delete(fieldCache.keys().next().value);
    return v;
  }
  // w / h 默认世界画布尺寸；给离屏缓冲用时传它的尺寸
  px.dist = function (cx, cy, sq = 1, w = 0, h = 0) {
    cx = Math.round(cx); cy = Math.round(cy);
    const W = w || SW(), H = h || SH(), key = 'd' + W + 'x' + H + '|' + cx + '|' + cy + '|' + sq;
    let f = fieldCache.get(key);
    if (f) { fieldCache.delete(key); fieldCache.set(key, f); return f; }
    f = new Float32Array(W * H);
    for (let y = 0; y < H; y++) { const dy = (y - cy) / sq; for (let x = 0; x < W; x++) { const dx = x - cx; f[y * W + x] = Math.sqrt(dx * dx + dy * dy); } }
    return cachePut(key, f);
  };
  px.angle = function (cx, cy, w = 0, h = 0) {
    cx = Math.round(cx); cy = Math.round(cy);
    const W = w || SW(), H = h || SH(), key = 'a' + W + 'x' + H + '|' + cx + '|' + cy;
    let f = fieldCache.get(key);
    if (f) { fieldCache.delete(key); fieldCache.set(key, f); return f; }
    f = new Float32Array(W * H);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) f[y * W + x] = Math.atan2(y - cy, x - cx);
    return cachePut(key, f);
  };
  // 中心到最远角的距离 + 2（fx._rmax）
  px.rmax = (cx, cy, w = 0, h = 0) => Math.hypot(Math.max(cx, (w || SW()) - cx), Math.max(cy, (h || SH()) - cy)) + 2;
  px.TAU = TAU;
})();
