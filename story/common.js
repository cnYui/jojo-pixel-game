// 跨章节的剧情小工具：替身调查演出 G.LOOK（技术约定 §4.13.1）、特写模板与剧情小零件 G.TPL（规划 §4.3）、
//   旅行地图 S.route 的实现、拔肉芽的画面、NPC / 队员搭话的小帮手。
//   画面零件全部按“有就画、没有就跳过”写：别的包的函数（G.FX.* / G.atlas / G.head …）在画的那一刻才去取。
'use strict';
(function () {
  const G = window.G;
  const fn = (o, k) => !!(o && typeof o[k] === 'function');
  const clk = () => (G.clk ? G.clk : { ui: 0, world: 0, flow: 0 });

  // ================================================================ 底层画法小工具
  // 在画布绘制阶段里临时开一次像素会话（技术约定 §2.5 嵌套规则：软件画的东西要垫在画布元素下面时这么用）
  function px(wg, f) {
    if (!G.px || !fn(G.px, 'begin') || G.px.cur) return;
    const P = G.px.begin(wg);
    try { f(P); } catch (e) { if (G.dbg && G.dbg.ev) G.dbg.ev('tpl_px_error', { msg: String(e && e.message) }); } finally { G.px.end(); }
  }
  const FX = (name) => (G.FX && fn(G.FX, name) ? G.FX[name] : null);
  // 目标指引的像素箭头（UI 层 640×360）：金色、深色描边；(x, y) = 箭头尖
  function arrowDown(g, x, y) {
    for (const [c, d] of [['#1a1020', 1], ['#ffd34a', 0]]) {
      g.fillStyle = c;
      g.fillRect(x - 3 - d, y - 22 - d, 7 + 2 * d, 12 + 2 * d);                                  // 杆
      for (let r = 0; r < 9; r++) g.fillRect(x - (8 - r) - d, y - 10 + r - (r === 0 ? d : 0), (8 - r) * 2 + 1 + 2 * d, 1 + (r === 8 ? d : 0));
    }
    g.fillStyle = 'rgba(255,255,255,0.55)'; g.fillRect(x - 2, y - 21, 2, 10);
  }
  function arrowSide(g, x, y, dir) {
    for (const [c, d] of [['#1a1020', 1], ['#ffd34a', 0]]) {
      g.fillStyle = c;
      const sx = dir > 0 ? x - 22 : x + 10;
      g.fillRect(sx - d, y - 3 - d, 12 + 2 * d, 7 + 2 * d);                                       // 杆
      for (let r = 0; r < 9; r++) {
        const cx = x - dir * (10 - r), half = 8 - r;
        g.fillRect(cx - d, y - half - d, 1 + 2 * d, half * 2 + 1 + 2 * d);
      }
    }
  }
  function headImg(cid, expr, talking, t) {
    if (!fn(G, 'head')) return null;
    const h = G.head(cid, expr || 'normal');
    if (!h || !h.length) return null;
    const f = talking && h[1] ? (Math.floor((t || 0) * 8) % 2) : 0;
    const im = h[f] || h[0];
    return G.ready && !G.ready(im) ? null : im;
  }
  function headSize(cid, expr, im) {
    if (fn(G, 'headSize')) { const s = G.headSize(cid, expr || 'normal'); if (s) return s; }
    return im ? [im.naturalWidth || im.width || 32, im.naturalHeight || im.height || 32] : [32, 32];
  }
  // 画一个精灵：ref = cid / 'scene:xxx' / 'prop:xxx'
  function sprite(wg, ref, anim, frame, x, y, o = {}) {
    if (!fn(G, 'atlas')) return;
    const A = G.atlas(ref);
    if (!A || !fn(A, 'draw')) return;
    let f = frame;
    if (f == null && fn(A, 'frameAt')) f = A.frameAt(anim || 'idle', o.t || 0);
    A.draw(wg, anim || 'idle', f || 0, Math.round(x), Math.round(y), o);
  }
  const bgCache = {};
  function bgObj(key) {
    if (bgCache[key] !== undefined) return bgCache[key];
    const spec = G.D && G.D.bg && G.D.bg[key];
    bgCache[key] = spec && G.Background ? new G.Background(spec) : null;
    return bgCache[key];
  }
  // state：背景 pick / tint 图层读的键（和 stage.state 一样），插入画面要换图层时传（第3章缆车外景的 win 碎窗）
  function drawBg(wg, key, t, camX = 0, state = {}) {
    const b = bgObj(key);
    if (!b) return false;
    try { b.draw(wg, camX, t, state); if (fn(b, 'drawFg')) b.drawFg(wg, camX, t, state); } catch (e) { return false; }
    return true;
  }
  // 插入画面的底：'menace' / 'radial' / 'black' / '#rrggbb' / 背景 key（'tatami_top'） / 函数 (P, t)
  function paintBase(wg, t, o) {
    const bg = o.bg || 'menace';
    wg.fillStyle = '#000';
    wg.fillRect(0, 0, 320, 180);
    if (typeof bg === 'string' && bg[0] === '#') { wg.fillStyle = bg; wg.fillRect(0, 0, 320, 180); }
    else if (bg === 'black') { /* 已经是黑的 */ }
    else if (typeof bg === 'string' && bg !== 'menace' && bg !== 'radial') {
      if (!drawBg(wg, bg, t, 0, o.bgState || {})) { wg.fillStyle = '#2a2018'; wg.fillRect(0, 0, 320, 180); }
    }
    px(wg, (P) => {
      if (typeof bg === 'function') bg(P, t);
      else if (bg === 'menace' && FX('menace_bg')) FX('menace_bg')(P, t, { colours: o.colours || ['#402060', '#200830'], speed: o.speed || 1.6 });
      else if (bg === 'radial' && FX('radial_burst_bg')) FX('radial_burst_bg')(P, t, { colours: o.colours || ['#5a2aa0', '#34146a'], n: o.n || 18, spin: o.spin != null ? o.spin : 0.6 });
      if (o.lines && FX('speedlines')) FX('speedlines')(P, t, { style: 'radial', n: 36, inner: o.inner || 60, alpha: 0.45, colour: o.lineColour || '#ffffff' });
      if (o.vignette && FX('vignette')) FX('vignette')(P, o.vignette, { colour: '#000000' });
    });
  }
  function drawPart(wg, p, t) {
    if (p.hidden) return;
    const jx = p.jitter ? Math.round(Math.sin(t * 23 + (p.seed || 0)) * p.jitter) : 0;
    const jy = p.jitter ? Math.round(Math.cos(t * 17 + (p.seed || 0)) * p.jitter) : 0;
    const x = (p.x || 0) + jx, y = (p.y || 0) + jy, sc = p.scale || 1;
    if (p.kind === 'head') {
      const im = headImg(p.cid, p.expr, p.talk, t);
      if (!im) return;
      const [w, h] = headSize(p.cid, p.expr, im);
      const dx = Math.round(x - w * sc / 2), dy = Math.round(y - h * sc / 2);
      wg.save();
      wg.imageSmoothingEnabled = false;
      if (p.alpha != null) wg.globalAlpha = p.alpha;
      if (p.flip) { wg.translate(dx + w * sc, dy); wg.scale(-1, 1); wg.drawImage(im, 0, 0, w * sc, h * sc); }
      else wg.drawImage(im, dx, dy, w * sc, h * sc);
      wg.restore();
    } else if (p.kind === 'image') {
      const im = fn(G, 'image') ? G.image(p.image) : null;
      if (!im || (G.ready && !G.ready(im))) return;
      wg.save(); wg.imageSmoothingEnabled = false;
      if (p.alpha != null) wg.globalAlpha = p.alpha;
      wg.drawImage(im, Math.round(x), Math.round(y), im.width * sc, im.height * sc);
      wg.restore();
    } else {
      sprite(wg, p.cid, p.anim, p.frame, x, y, Object.assign({ scale: sc, flip: !!p.flip, t }, p.o || {},
        p.alpha != null ? { alpha: p.alpha } : {}, p.aura ? { aura: { color: p.aura, alpha: 0.55, grow: p.auraGrow || 2, jitter: true, t } } : {}));
    }
  }

  // ================================================================ 统计（快照的 lookStats 读它）
  const stats = { total: 0, hits: 0, by: {} };
  //   调查点写了 lookOnly: true 的，演出由它自己的 look 来演（比如序-6 的相机：念写过场里自己砸相机），这里跳过
  const mk = (cid, run) => async (S, leader, h) => {
    stats.total++; stats.by[cid] = (stats.by[cid] || 0) + 1; if (h) stats.hits++;
    if (h && h.lookOnly) return;
    await run(S, leader, h);
  };
  // 调查点 / 目标点的世界坐标
  const spot = (h) => (h ? { x: h.lx != null ? h.lx : h.x, y: h.ly != null ? h.ly : h.y } : null);
  // 找乔瑟夫念写要砸的相机 / 电视：h.cameraAt → 地图里最近的 camera / tv 道具 → 身前的地面
  function findCamera(leader, h) {
    if (h && h.cameraAt) return { x: h.cameraAt.x, y: h.cameraAt.y, z: h.cameraAt.z || 0 };
    const st = G.world.stage;
    let best = null, bd = 1e9;
    for (const a of (st && st.actors) || []) {
      if (a.remove || a.visible === false) continue;
      if (a.cid !== 'prop:camera' && a.cid !== 'prop:tv') continue;
      const d = Math.abs(a.x - leader.x) + Math.abs(a.y - leader.y);
      if (d < bd && d < 140) { bd = d; best = { x: a.x, y: a.y, z: a.z || 0, actor: a }; }
    }
    return best || { x: leader.x + leader.facing * 26, y: leader.y, z: 0, ground: true };
  }

  // ================================================================ 替身调查（自由走动按 U；规划 §3.1 表）
  G.LOOK = {
    stats,
    // 星之眼：0.4 s 眼部条带 → 镜头推到调查点 z 2.5 停 1 s
    jotaro: {
      tags: ['detail', 'grab'], cd: 1, miss: '……没什么特别的。',
      run: mk('jotaro', async (S, leader, h) => {
        S.sfx('glint', 0.7);
        await S.eyeStrip('jotaro', { dur: 0.4 });
        if (h) {
          const p = spot(h);
          await S.zoom(2.5, p.x, p.y, 0.22);
          S.fx('glint', { x: p.x, y: p.y, size: 7 }, { tag: 'look' });
          await S.wait(1.0);
          await S.zoom(1, null, null, 0.2);
        }
      }),
    },
    // 念写：藤蔓砸附近的相机 / 电视（没有就砸地面）→ 拍立得飞出 → 照片（对不上时是乔瑟夫自己的大脸）
    joseph: {
      tags: ['nensha'], cd: 2, miss: '……再来一次！',
      run: mk('joseph', async (S, leader, h) => {
        const c = findCamera(leader, h);
        const hx = leader.x + leader.facing * 6, hy = leader.y - 30;
        S.pose(leader, 'point');
        const v = S.fx('vines', { x0: hx, y0: hy, x1: c.x, y1: c.y - (c.z || 0) - 6, t1: 0.25, colour: 'purple', strands: 2, thorns: true }, { life: 0.8 });
        S.sfx('vine', 0.8);
        await S.wait(0.25);
        // crack 默认不会自己消失（由创建者 kill）：给 1.2 s，不然地板 / 墙上会一直留着一道裂纹，直到换图
        S.fx('crack', { x: c.x, y: c.y - (c.z || 0) - 4, size: 14 }, { life: 1.2 });
        S.fx('hit_spark', { x: c.x, y: c.y - (c.z || 0) - 6, size: 10, accent: '#d0a0ff' });
        S.sfx('crash', 0.6); S.sfx('punch', { vol: 0.7, seed: 0 });
        S.shake(2, 0.2);
        await S.wait(0.2);
        S.sfx('camera_shutter');
        S.killFx(v);
        S.unpose(leader);
        const ph = h && h.photo ? h.photo : null;
        if (h) await S.photo(Object.assign({ hold: 1.2 }, ph || {}));
        else {
          const heads = G.D && G.D.chars && G.D.chars.joseph && G.D.chars.joseph.heads;
          const img = heads && (heads.shock || heads.normal) ? (heads.shock || heads.normal)[0] : null;
          await S.photo(img ? { image: img, hold: 1.0 } : { hold: 1.0 });
        }
      }),
    },
    // 生命探测：6 团小火焰绕身一圈后排成指针飞向生命体方向，停 1.2 s（对不上时在原地熄掉）
    avdol: {
      tags: ['life'], cd: 2, miss: '周围没有可疑的生命。',
      run: mk('avdol', async (S, leader, h) => {
        const p = spot(h);
        const kw = { x: leader.x, y: leader.y - 22, n: 6, colour: '#ff7a30', dur: 1.2 };
        if (p) kw.angle = Math.atan2(-((p.y) - (leader.y - 22)), p.x - leader.x) * 180 / Math.PI;
        else kw.fizzle = true;
        S.fx('flame_pointer', kw, { life: 1.4 });
        S.sfx('fire_burst', { vol: 0.35, rate: 1.4 });
        await S.wait(p ? 1.2 : 0.8);
      }),
    },
    // 法皇触须：绿色触须从脚下沿地面伸出，0.3 s 长到 96 px（对不上时缩回）
    kakyoin: {
      tags: ['reach', 'peek'], cd: 1, miss: '这里没有需要伸手的东西。',
      run: mk('kakyoin', async (S, leader, h) => {
        const p = spot(h) || { x: leader.x + leader.facing * 96, y: leader.y };
        const pts = [[leader.x, leader.y - 2], [(leader.x + p.x) / 2, leader.y - 4], [p.x, p.y]];
        const tn = S.fx('tendrils', { pts, colour: '#50e890', grow: 0.3, wiggle: 1.0 }, { tag: 'look' });
        S.sfx('hiero_tentacle', 0.7);
        await S.wait(h ? 1.0 : 0.6);
        S.killFx(tn);
      }),
    },
    // 银色战车·剑：出剑一闪
    polnareff: {
      tags: ['cut'], cd: 1, miss: 'Voilà～',
      run: mk('polnareff', async (S, leader, h) => {
        S.standAct(leader, 'punch', { dx: 16, dur: 0.3 });
        const p = spot(h) || { x: leader.x + leader.facing * 22, y: leader.y };
        S.fx('slash_arc', { x: p.x, y: p.y - 24, size: 15 }, { life: 0.3 });
        S.sfx('slash', { seed: 0, vol: 0.8 });
        await S.wait(0.45);
      }),
    },
    // 嗅探：地上出现一条黄色气味虚线，3 s 渐隐（对不上时打个喷嚏）
    iggy: {
      tags: ['scent', 'hole'], cd: 1, miss: null,
      run: mk('iggy', async (S, leader, h) => {
        const p = spot(h);
        if (p) {
          S.fx('scent_line', { pts: [[leader.x, leader.y], [p.x, p.y]], colour: '#e8c070', dur: 3 }, { life: 3 });
          await S.wait(0.8);
        } else {
          S.emote(leader, '！？', 0.6);
          S.sfx('dog_bark', { vol: 0.4, rate: 1.4 });
          await S.wait(0.5);
        }
      }),
    },
    // 没写 onStand 的普通人看见有人亮替身：看不见替身，只觉得起风了
    async onStandDefault(S, npc, leader) {
      if (npc.cid && String(npc.cid).indexOf('passenger') >= 0) return;   // 坐着的乘客不打扰
      S.emote(npc, '？', 1.2);
      const lines = ['……起风了？', '咦？刚才好像有什么东西……', '……是我眼花了吗。'];
      const k = (G.TPL.count('onStandDefault') - 1) % lines.length;
      await S.say(npc.cid, lines[k], { name: npc.name || S.nameOf(npc.cid), actor: npc });
    },
  };

  // ================================================================ 城市坐标（world_map 的底图像素，照 源码\engine\bg_asia.py 的 map_xy / _CITY_LL）
  const LONK = [[22, 8], [40, 70], [70, 146], [92, 204], [147, 312]];
  function mapXY(lon, lat) {
    let i = 0;
    while (i < LONK.length - 2 && lon > LONK[i + 1][0]) i++;
    const [a, xa] = LONK[i], [b, xb] = LONK[i + 1];
    return [xa + (lon - a) * (xb - xa) / (b - a), 8 + (47 - lat) * (172 - 8) / (47 + 5)];
  }
  const CITY_LL = {
    '东京': [139.7, 35.7], '香港': [114.2, 22.3], '新加坡': [103.8, 1.3], '加尔各答': [88.4, 22.6], '瓦拉纳西': [83.0, 25.3],
    '卡拉奇': [67.0, 24.85], '阿拉伯沙漠': [47.0, 23.0], '红海': [35.9, 25.6], '阿斯旺': [32.95, 23.9], '卢克索': [32.65, 26.3], '开罗': [31.25, 30.05],
  };
  const CITIES = {};
  for (const k in CITY_LL) { const [x, y] = mapXY(CITY_LL[k][0], CITY_LL[k][1]); CITIES[k] = [Math.round(x), Math.round(y)]; }
  const LABEL = { '东京': [0, 4, 'center'], '香港': [3, 1, 'left'], '新加坡': [0, 4, 'center'], '加尔各答': [3, 2, 'left'], '瓦拉纳西': [-2, 3, 'right'],
    '卡拉奇': [-3, 2, 'right'], '阿拉伯沙漠': [0, 4, 'center'], '红海': [3, 0, 'left'], '阿斯旺': [-3, 1, 'right'], '卢克索': [-3, -1, 'right'], '开罗': [2, -2, 'left'] };
  const cityXY = (s) => (Array.isArray(s) ? s : CITIES[s] || [160, 90]);

  // ================================================================ 特写模板与剧情零件
  const counters = {};
  G.TPL = {
    CITIES,
    px, sprite, headImg, drawBg,
    count(key) { counters[key] = (counters[key] || 0) + 1; return counters[key]; },
    // 每隔 sec 秒（世界时钟）调一次 f，stop() 为真、换了地图或回了标题就停
    every(sec, f, stop) {
      const runId = G.runId, sid = G.world.stage && G.world.stage.id;
      let acc = 0;
      G.world.ticks.push((dt) => {
        if (runId !== G.runId || !G.world.stage || G.world.stage.id !== sid || (stop && stop())) return true;
        acc += dt;
        if (acc >= sec) { acc -= sec; try { f(); } catch (e) { console.error(e); return true; } }
        return false;
      });
    },
    // 每帧调 f(dt)，返回 true 就停（同样换图 / 回标题自动停）
    tick(f) {
      const runId = G.runId, sid = G.world.stage && G.world.stage.id;
      G.world.ticks.push((dt) => {
        if (runId !== G.runId || !G.world.stage || G.world.stage.id !== sid) return true;
        try { return !!f(dt); } catch (e) { console.error(e); return true; }
      });
    },
    // 按队长分支取文字 / 函数：map = { jotaro: …, joseph: …, _: 默认 }
    by(leader, map) { const c = leader && leader.cid; return map[c] !== undefined ? map[c] : map._; },
    // 章节开始时清计数（main.js 每章开头调）
    resetCounters() { for (const k in counters) delete counters[k]; },

    // ---------------------------------------------------------------- 通用插入画面：底 + 一组零件（零件是普通对象，调用方可以改它的 x / frame / alpha 做动画）
    //   o = { bg, colours, lines, vignette, parts: [{ kind: 'head'|'sprite'|'image', cid, expr, anim, frame, x, y, scale, flip, alpha, jitter, talk, aura }],
    //         draw(wg, t) 额外画, shake, letterbox }
    // 插入画面里自己控制画的顺序时用（o.draw 里先画背景件、再画前景件）：零件格式同 parts
    part(wg, p, t) { drawPart(wg, p, t); },
    show(S, o = {}) {
      const parts = o.parts || [];
      const h = {
        parts, o, closed: false,
        close() { if (!h.closed) { h.closed = true; S.insert(null); if (o.letterbox) S.letterbox(false); } },
      };
      if (o.letterbox) S.letterbox(o.letterbox);
      S.insert({
        clock: o.clock || 'world',
        draw: (wg, t) => {
          paintBase(wg, t, o);
          for (const p of parts) drawPart(wg, p, t);
          if (o.draw) o.draw(wg, t);
        },
      });
      return h;
    },
    // 〔特写·头像×4〕：32×32 头像 ×4 贴在 menace / radial 底上 + 放射集中线 + 1.5 px 抖 + 首帧冲击帧 + 推镜 1.0→1.1 + shake 2
    async closeup4(S, o = {}) {
      o = Object.assign({ bg: 'menace', lines: true, dur: 1.2, impact: true, scale: 4 }, o);
      const parts = (o.heads || [{ cid: o.cid, expr: o.expr }]).map((hd, i, all) => ({
        kind: 'head', cid: hd.cid, expr: hd.expr, talk: hd.talk, scale: o.scale, jitter: 1.5, seed: i * 3,
        x: all.length > 1 ? 80 + i * 160 : 160, y: o.y || 92, flip: hd.flip,
      }));
      const h = this.show(S, Object.assign({}, o, { parts }));
      if (o.impact) S.impact('invert', 1 / 24);
      S.shake(2, 0.25);
      if (o.sfx) S.sfx(o.sfx);
      if (o.hold) return h;          // 调用方自己 close
      await S.wait(o.dur);
      h.close();
      return h;
    },
    // 〔特写·全身×3〕：角色精灵 ×3 + 放射 / 迷幻底 + 光环 + glint；o.cap = 压帽阴影（承太郎 pose 帧 1），o.behind = 身后半透明的替身
    async fullbody3(S, o = {}) {
      o = Object.assign({ bg: 'radial', anim: 'pose', frame: null, scale: 3, dur: 1.6, x: 160, y: 172 }, o);
      const parts = [];
      if (o.behind) parts.push({ kind: 'sprite', cid: o.behind.cid, anim: o.behind.anim || 'pose', frame: o.behind.frame, scale: o.scale - 1, x: o.x + (o.behind.dx || 40), y: o.y - 8, alpha: o.behind.alpha != null ? o.behind.alpha : 0.62, flip: o.flip });
      const me = { kind: 'sprite', cid: o.cid, anim: o.anim, frame: o.frame, scale: o.scale, x: o.x, y: o.y, flip: o.flip, aura: o.aura || null };
      parts.push(me);
      const h = this.show(S, Object.assign({}, o, {
        parts,
        draw: (wg, t) => {
          if (o.cap && t > (o.capAt || 0.45)) px(wg, (P) => { const f = FX('cap_shadow'); if (f) f(P, o.x, o.y, t, o.capAt || 0.45, { scale: o.scale, amount: 1 }); });
          if (o.draw) o.draw(wg, t);
        },
      }));
      if (o.glint) G.defer(o.glintAt || 0.5, () => S.fx('glint', { x: o.glint[0], y: o.glint[1], size: 9 }, { space: 'canvas', tag: 'insert' }));
      if (o.hold) return h;
      await S.wait(o.dur);
      h.close();
      return h;
    },
    punchIn(S, a, o) { return S.punchIn(a, o); },
    eyeBand(S, cid, o) { return S.eyeStrip(cid, o); },
    // 〔局部 insert〕：场景局部精灵 ×2–×3（手、前臂、小道具）+ 迷幻底或俯视地面；返回句柄（零件可动）
    insert(S, o = {}) { return this.show(S, Object.assign({ bg: 'menace' }, o)); },
    // 〔POV〕：镜头 z 2.5–3.3 对准物件 + glint
    async pov(S, o = {}) {
      await S.zoom(o.k || 3, o.x, o.y, 0.25);
      S.fx('glint', { x: o.gx != null ? o.gx : o.x, y: o.gy != null ? o.gy : o.y, size: 8 });
      S.sfx('glint', 0.7);
      await S.wait(o.dur || 1.0);
      if (!o.keep) await S.zoom(1, null, null, 0.2);
    },
    nightFace(S, o = {}) { return this.closeup4(S, Object.assign({ bg: '#0a0c24', lines: false, impact: false }, o)); },
    bossCutin(o = {}) { return G.uifx && fn(G.uifx, 'cutin') ? G.uifx.cutin(Object.assign({ enemy: true }, o)) : Promise.resolve(); },
    // 〔替身对轰〕（终章才用）：两边替身头像 ×4 + 光环 + 放射底，各 0.4 s
    async standClash(S, o = {}) {
      for (const side of [o.a, o.b]) {
        if (!side) continue;
        const h = this.show(S, { bg: 'radial', colours: side.colours, spin: 0.9, parts: [{ kind: 'head', cid: side.cid, expr: side.expr, scale: 4, x: 160, y: 92, jitter: 1.5 }] });
        await S.wait(0.4);
        h.close();
      }
    },

    // ---------------------------------------------------------------- 飘起来的小东西（音符、爱心、汗滴、Z）：生成道具角色，上升 + 淡出后删掉
    floater(S, ref, x, y, o = {}) {
      if (!S.exists(ref)) return Promise.resolve();
      const a = S.spawn(ref, x, y, { id: 'fl' + this.count('floater'), z: o.z || 0, shadow: false, standReact: false });
      if (o.frame != null) a.frozen = o.frame;
      const z0 = a.z, dx = o.dx || 0;
      return S.animate(o.dur || 1.0, (k) => {
        a.z = z0 + (o.rise != null ? o.rise : 14) * k;
        a.x = x + dx * k + (o.wave ? Math.sin(k * 7) * o.wave : 0);
        if (k > 0.6) a.alpha = Math.max(0, 1 - (k - 0.6) / 0.4);
        if (k >= 1) a.remove = true;
      });
    },
    // 给“角色身上”放一个跟着走的小符号（怒筋、汗滴）：持续 dur 秒
    stick(S, ref, a, o = {}) {
      a = S.actor(a);
      if (!a || !S.exists(ref)) return Promise.resolve();
      const s = S.spawn(ref, a.x, a.y + 0.5, { id: 'st' + this.count('stick'), shadow: false, standReact: false });
      const top = a.top || 46;
      return S.animate(o.dur || 1.0, (k, dt) => {
        s.x = a.x + (o.dx || 6) * a.facing + (o.shake ? Math.round(Math.sin(k * 60)) : 0);
        s.y = a.y + 0.5;
        s.z = (a.z || 0) + top + (o.dz || -4);
        if (k >= 1) s.remove = true;
      });
    },
    // 道具角色（会动、会被剧情挪的道具）：S.spawn('prop:xxx') 的包装；frame = 状态帧
    prop(S, id, x, y, o = {}) {
      const ref = id.indexOf(':') >= 0 ? id : 'prop:' + id;
      if (!S.exists(ref)) { if (o.alt && S.exists(o.alt)) return this.prop(S, o.alt, x, y, Object.assign({}, o, { alt: null })); return null; }
      // o.alt 只是“这张道具缺图时用哪张顶上”，别传给 Actor（Actor 的 alt 是候选图集数组；2026-10-09 抢漫画因此卡死）
      const so = Object.assign({ id: o.id || id + this.count('prop'), shadow: false, standReact: false }, o);
      delete so.alt;
      const a = S.spawn(ref, x, y, so);
      if (o.frame != null) a.frozen = o.frame;
      if (o.z != null) a.z = o.z;
      a.hold = true;
      return a;
    },
    setFrame(a, n) { if (a) { a.frozen = n; a.hold = true; } },

    // ---------------------------------------------------------------- 说话的小帮手
    // 让地图上的某个角色（NPC）说话：名字取它的 name / G.NAMES
    say(S, a, text, o = {}) {
      a = S.actor(a);
      const cid = a ? a.cid : o.cid;
      return S.say(cid, text, Object.assign({ name: (a && a.name) || S.nameOf(cid), actor: a }, o));
    },
    // 给队伍里的人挂搭话（换图后要重挂）：map = { cid: talk(S, me) }；队长自己不会被搭话
    memberTalk(map) {
      const mem = (G.party && G.party.members) || [];
      for (const a of mem) {
        if (map[a.cid]) { a.talk = map[a.cid]; a.label = a.label || G.S.nameOf(a.cid); } else a.talk = null;
      }
    },
    // NPC 定义的简写
    npc(cid, id, x, y, o = {}) { return Object.assign({ cid, id, x, y, facing: o.facing || -1, label: o.label || G.NAMES[cid] || id }, o); },

    // ---------------------------------------------------------------- 自由走动的目标指引：提示框 + 金色箭头（真人玩家知道下一步去哪）
    //   o = { x, y（目标的世界坐标，地面）, text（提示框文字）, label（箭头旁小字，可省）, done: () => bool,
    //         every: 15（没做到、提示框也没在显示时，隔多少秒再弹一次）, delay: 0（多少秒后才出提示和箭头）, h: 44（箭头离地多高）, dur: 8,
    //         when: () => bool（可省：为真之后才开始计 delay，用来排在前一个目标后面） }
    //   箭头画在 UI 插入层（G.ui.insertUI 空着才占用；剧情演出、对话、战斗、插入画面时不画）：
    //   目标在画面里 = 目标头顶上下跳的 ▼；在画面外 = 屏幕左右边缘的 ► / ◄。done() 为真、换图、回标题都会自己收掉；返回 { stop() }
    goal(S, o = {}) {
      o = Object.assign({ every: 15, delay: 0, h: 44, dur: 8 }, o);
      const runId = G.runId, W = G.world, sid = W.stage && W.stage.id;
      const h = { stopped: false, stop() { this.stopped = true; } };
      const dead = () => h.stopped || runId !== G.runId || !W.stage || W.stage.id !== sid || (o.done && o.done());
      const calm = () => W.free && !(G.S && G.S.busy) && !W.combat && !W.insert && !(G.ui && G.ui.blocking && G.ui.blocking());
      let el = 0, lastHint = -1e9, shown = false, cut = null;
      const mine = {
        t0: clk().ui,
        draw: (g, t) => {
          if (dead()) { if (G.ui && G.ui.insertUI === mine) G.ui.insertUI = null; return; }
          if (!shown || !calm() || !G.cam || !fn(G.cam, 'w2u')) return;
          const p = G.cam.w2u(o.x, o.y - o.h, 0);
          const bob = Math.round(Math.abs(Math.sin(t * 5)) * 4);
          const on = p.x >= 12 && p.x <= 628;
          const F = G.f12;
          g.save();
          if (on) {
            const x = Math.round(p.x), y = Math.round(Math.max(26, p.y)) - bob;
            arrowDown(g, x, y);
            if (o.label && F) F.draw(g, o.label, x, y - 30, '#ffe9a8', { align: 'center', outline: '#1a1020' });
          } else {
            const right = p.x > 628, pl = W.player;
            const py = pl ? G.cam.w2u(pl.x, pl.y - 64, 0).y : 150;      // 比队长头顶再高一点：别和路边的 NPC 叠在一起
            const y = Math.round(G.clamp(py, 40, 300)), x = right ? 626 - bob : 14 + bob;
            arrowSide(g, x, y, right ? 1 : -1);
            if (o.label && F) F.draw(g, o.label, right ? x - 22 : x + 22, y - 7, '#ffe9a8', { align: right ? 'right' : 'left', outline: '#1a1020' });
          }
          g.restore();
        },
      };
      this.tick((dt) => {
        if (dead()) {
          if (G.ui && G.ui.insertUI === mine) G.ui.insertUI = null;
          // 目标达成就收起自己弹的提示（不然接下来的过场里还挂着“去××”）
          const hs = G.ui && G.ui.hints;
          if (o.text && hs && hs.length && hs[0].text === o.text) G.ui.hint(null);
          return true;
        }
        if (o.when && !o.when()) return false;
        el += dt;
        if (el < o.delay) return false;
        if (!shown) { shown = true; if (o.text && calm()) { S.hint(o.text, o.dur); lastHint = el; } }
        if (G.ui && !G.ui.insertUI) { mine.t0 = clk().ui; G.ui.insertUI = mine; }
        const hs = G.ui && G.ui.hints;
        const showing = hs && hs.length && hs[0].t < hs[0].dur;
        const ours = showing && hs[0].text === o.text;
        // 剧情演出 / 对话时收起自己的提示（不然“去××”会挂在过场画面上），回到自由走动 0.8 s 后再弹回来
        if (ours && !calm()) { G.ui.hint(null); cut = el; }
        if (o.text && calm()) {
          if (cut != null && el - cut >= 0.8) { S.hint(o.text, o.dur); lastHint = el; cut = null; }
          else if (cut == null && !showing && el - lastHint >= o.every) { S.hint(o.text, o.dur); lastHint = el; }
        }
        return false;
      });
      return h;
    },

    // ---------------------------------------------------------------- 旅行地图（S.route 的实现，报告 09 §2.6）
    //   stops = ['东京', '香港']；o = { vehicle, day, dur: 2.0, history, left（右上「距离期限：还剩 N 天」）, cut（飞机只走到这个进度就切镜）, view: { k, x, y } }
    async route(S, stops, o = {}) {
      o = Object.assign({ vehicle: 'plane', dur: 2.0, t0: 0.35, t1: 1.7 }, o);
      const W = G.world;
      const cut = o.cut != null ? o.cut : 1;
      const tEnd = o.t0 + (o.t1 - o.t0) * cut;
      S.sfx(o.vehicle === 'plane' ? 'plane_engine' : o.vehicle === 'car' ? 'car_engine' : 'wind', 0.5);
      let popped = false, dinged = false;
      S.insert({
        clock: 'world',
        draw: (wg, t) => {
          wg.fillStyle = '#7ca6aa'; wg.fillRect(0, 0, 320, 180);
          drawBg(wg, 'world_map', t);
          px(wg, (P) => {
            const f = FX('draw_route');
            if (f) f(P, stops, Math.min(t, tEnd), o.t0, o.t1, { vehicle: o.vehicle, history: o.history || null, day: null, labels: false });
          });
          if (!popped && t >= o.t0) { popped = true; S.sfx('pop', 0.6); }
          if (!dinged && cut >= 1 && t >= o.t1 + 0.02) { dinged = true; S.sfx('ding', 0.7); }
        },
      });
      S.insertUI((ug, t) => {
        if (!G.f12) return;
        const toU = (x, y) => (G.cam && fn(G.cam, 's2u') ? G.cam.s2u(x, y) : [x * 2, y * 2]);
        const names = new Set([].concat(stops, ...(o.history ? [].concat(o.history) : [])));
        for (const n of names) {
          if (typeof n !== 'string' || !CITIES[n]) continue;
          const [x, y] = CITIES[n], L = LABEL[n] || [3, 0, 'left'];
          const u = toU(x + L[0], y + L[1]);
          const ux = Array.isArray(u) ? u[0] : u.x, uy = Array.isArray(u) ? u[1] : u.y;
          G.f12.draw(ug, n, ux, uy, '#482a18', { align: L[2], outline: '#e2cd98' });
        }
        if (o.day != null && t >= o.t0) {
          const s = typeof o.day === 'number' ? `第${o.day}天` : String(o.day);
          if (G.f16) G.f16.draw(ug, s, 610, 300, '#cc2028', { align: 'right', outline: '#fff0d0' });
        }
        if (o.left != null && G.f12) G.f12.draw(ug, `距离期限：还剩 ${o.left} 天`, 628, 10, '#ffffff', { align: 'right', outline: '#2a1a10' });
      });
      if (o.view) {
        const camx = G.cam ? G.cam.x : 0, camy = G.cam ? G.cam.y : 0;
        S.zoom(o.view.k || 1.9, (o.view.x != null ? o.view.x : 264) + camx, (o.view.y != null ? o.view.y : 66) + camy, o.dur);
      }
      await S.wait(o.dur);
      S.insert(null);
      S.insertUI(null);
      W.zoom = null;
    },

    // ---------------------------------------------------------------- 拔肉芽（序-13；规则 = QTE pluck，画面 = 这里，规划 §5.1.4）
    //   q.m = 准星（白金之星的捏点）相对肉芽的偏移；q.budPos = 肉芽当前的绝对位置（含抖动）；q.pull / q.drill 0..1
    pluckDraw(wg, q) {
      const t = clk().world;
      wg.fillStyle = '#5a4a2a'; wg.fillRect(0, 0, 320, 180);
      if (!drawBg(wg, 'tatami_top', t)) { wg.fillStyle = '#8a7a4a'; wg.fillRect(0, 0, 320, 180); }
      // 肉芽的当前位置 = q.budPos（ui.js 的 pluck 每帧算好的绝对坐标，含抖动和跳）；q.bud 是它的基准点 [160, 70]，
      //   以前把 q.bud 当成偏移再加一次 160 / 70，肉芽和白金之星的手都画到了画面外（只剩准星）
      //   肉芽、手用 G.ui.sheet 按图集 pivot 画（和 ui.js 的兜底画法同一套坐标）：肉芽中心 = budPos，手的捏点 = 准星 aim
      const m = (q && Array.isArray(q.m)) ? q.m : [0, 0];
      const bx = q && q.budPos ? q.budPos.x : 160, by = q && q.budPos ? q.budPos.y : 70;
      const sheet = G.ui && fn(G.ui, 'sheet') ? G.ui.sheet : null;
      sprite(wg, 'scene:s04_kak_face', 'idle', 0, 160, 174, { scale: 4 });
      if (sheet) sheet(wg, 'prop:fleshbud', Math.floor(clk().ui * 8) % 3, bx, by, 3);
      else sprite(wg, 'prop:fleshbud', 'idle', null, bx, by + 31, { scale: 3, t });
      const pinch = q && q.holding != null ? !!q.holding : !!(G.input && fn(G.input, 'isDown') && G.input.isDown('attack'));
      const drill = q ? q.drill || 0 : 0;
      px(wg, (P) => {
        if (drill > 0.01) {
          const f = FX('tendrils');
          const hx = bx + m[0], hy = by + m[1];
          if (f) f(P, [[hx, hy], [hx + 30 * drill, hy + 30 * drill], [hx + 60 * drill, hy + 50 * drill]], t, { colour: '#e070b0', pulses: false, grow: 1 });
          const v = FX('vignette');
          if (v) v(P, drill * 0.6, { colour: '#5a0010' });
        }
      });
      if (sheet) sheet(wg, 'scene:s04_sphand', pinch ? 1 : 0, bx + m[0] + 2, by + m[1] + 22, 2);
      else sprite(wg, 'scene:s04_sphand', 'idle', pinch ? 1 : 0, bx + m[0], by + m[1] + 23, { scale: 2 });
    },
    // 拔肉芽整段（含失败重来时乔瑟夫的那句）
    async pluck(S) {
      return S.pluck({
        draw: (wg, q) => G.TPL.pluckDraw(wg, q),
        onReset: () => { S.sfx('heartbeat', 0.8); S.hint('乔瑟夫：「别慌！再来一次！」', 2.0); },
      });
    },
  };
})();
