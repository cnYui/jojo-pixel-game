// 第五部共用角色参数与地图盖章，叠加层的生命周期沿用第四部，回标题立即清理。
'use strict';
(function () {
  const G = window.G;
  const P = G.P5 = { layers: [], clearOverlays() { this.layers.length = 0; } };
  P.overlay = fn => {
    const h = { fn, run: G.runId, dead: false, t0: G.clk.ui, close() { this.dead = true; } };
    P.layers.push(h); return h;
  };
  const oldMarks = G.hud.drawMarks;
  G.hud.drawMarks = function (g) {
    if (oldMarks) oldMarks.call(this, g);
    P.layers = P.layers.filter(h => !h.dead && h.run === G.runId);
    for (const h of P.layers) h.fn(g, G.clk.ui - h.t0);
  };
  P.calendar = async S => {
    const m = G.D.ui.map;
    const ease = u => 1 - Math.pow(1 - G.clamp(u, 0, 1), 3);
    const h = P.overlay((g, t) => {
      const place = G.image(m.place.image);
      g.drawImage(place, 640 - m.place.w - 14, 12);
      for (const [i, x, y, label] of [[0, 213, 66, '机场'], [1, 116, 114, '老城区']]) {
        const u = (t - .5 - i * .45) / .3;
        if (u < 0) continue;
        const dy = -60 * (1 - ease(u));
        const pin = G.image(m.pin.image);
        g.drawImage(pin, x * 2 - 10, y * 2 - 32 + dy, 22, 34);
        if (u >= 1) G.f12.draw(g, label, x * 2 + 14, y * 2 - 30, '#fff4d6', { outline: '#2a0a1a' });
      }
      if (t >= 1.65) {
        const sc = 1.9 - .9 * ease((t - 1.65) / .14), sm = m.stamp;
        const w = sm.w * sc, hh = sm.h * sc;
        g.drawImage(G.image(sm.image), 510 - w / 2, 275 - hh / 2, w, hh);
      }
    });
    await S.fadeIn(.5);
    await S.wait(1.65, 'ui');
    S.sfx('thud'); S.shake(2, .2); S.mark('p5_map_stamp');
    await S.wait(1.8, 'ui');
    await S.fadeOut(.4); h.close();
  };
  for (const [cid, hp, standId] of [['giorno', 120, 'goldexp'], ['bucciarati', 140, 'stickyfingers'], ['koichi', 100, 'echoes3']]) {
    G.KITS[cid] = { hp, speed: 66, standId };
  }
  // ACT3 的拳和连打使用公共战斗管线，替身动作映射由导出器统一适配。
  for (const slot of ['J1', 'J2', 'J3', 'FIN']) {
    G.MOVES['P5_KO_' + slot] = Object.assign({}, G.MOVES['SP_' + slot], {
      word: slot === 'FIN' ? 'ACT3!' : null, accent: '#b6e88c', push: 0, launch: null,
    });
  }
  Object.assign(G.KITS.koichi, {
    combo: ['P5_KO_J1', 'P5_KO_J2', 'P5_KO_J3'],
    rush: { tick: 4 / 60, dmg: 4, push: 0, reach: [0, 52], depth: 12,
      word: 'ACT3', hitSfx: 'punch', finisher: 'P5_KO_FIN' },
    guard: { pose: 'block' }, dodge: {}, parry: {},
  });
  G.P5.openShell = async (S, chapter, stage, leader) => {
    await S.chapterCard(chapter);
    S.party([leader], { leader });
    await S.setStage(stage, { x: 80, y: 160, facing: 1 });
    S.free(true);
    S.hint('方向键 / WASD 移动　Esc 暂停', 8);
    // 空壳停在自由走动，不触发假通关；回标题由既有暂停菜单取消本次流程。
    await S.until(() => false);
  };
})();
