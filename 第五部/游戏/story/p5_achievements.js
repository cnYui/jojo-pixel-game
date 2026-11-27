// 第五部成就的定义、判定和独立存档。战斗与探索按实际完成的事件记账。
'use strict';
(function () {
  const G = window.G;
  const KEY = 'p5-achievements';
  const enabled = !G.dbg.autotest && !/[?&]debug=1(?:&|$)/.test(location.search);
  const defs = [];
  const chapterBadges = new Map(), battleBadges = new Map();
  const queue = [];
  const clues = new Set(), lifeForms = ['vine', 'butterfly'];
  const LIFE = 'life_pair', EVIDENCE = 'three_clues', ALL_CHAPTERS = 'all_chapters';
  let state;

  function define(id, cat, name, desc, tier, hidden = false) {
    const def = { id, cat, name, desc, tier, hidden };
    defs.push(def);
    return def;
  }

  function read() {
    const saved = G.store.get(KEY, null);
    if (!saved || saved.v !== 1 || !saved.got || typeof saved.got !== 'object' || Array.isArray(saved.got)) return null;
    const got = Object.create(null);
    for (const { id } of defs) {
      const when = saved.got[id];
      if (Number.isSafeInteger(when) && when >= 0 && when <= 864e13) got[id] = when;
    }
    return {
      v: 1, got,
      life: Array.isArray(saved.life) ? [...new Set(saved.life.filter(id => lifeForms.includes(id)))] : [],
      evidence: Array.isArray(saved.evidence) ? [...new Set(saved.evidence.filter(id => clues.has(id)))] : [],
    };
  }

  const has = id => state.got[id] !== undefined;
  function unlock(def, notify = true, when = Date.now()) {
    if (!def || has(def.id)) return false;
    state.got[def.id] = when;
    if (notify) queue.push(def);
    return true;
  }
  function unlockId(id, notify, when) { return unlock(defs.find(def => def.id === id), notify, when); }
  function collect(def, values, id, goal) {
    if (values.includes(id)) return false;
    values.push(id);
    if (values.length >= goal) unlockId(def);
    return true;
  }
  function checkJourney(notify = true) {
    return [...chapterBadges.values()].every(def => has(def.id)) &&
      unlockId(ALL_CHAPTERS, notify, notify ? Date.now() : 0);
  }
  function update(fn) {
    if (!enabled || !state) return;
    // 同源多标签页在写之前合并记录，避免覆盖另一个标签页刚取得的成就。
    const latest = read();
    if (latest) {
      Object.assign(state.got, latest.got);
      state.life = [...new Set([...latest.life, ...state.life])];
      state.evidence = [...new Set([...latest.evidence, ...state.evidence])];
    }
    if (fn()) G.store.set(KEY, state);
  }

  G.ach = {
    enabled,
    init(chapters, oldProgress) {
      for (const [i, chapter] of chapters.entries()) {
        const tier = i < 3 ? 'bronze' : i < chapters.length - 1 ? 'silver' : 'gold';
        const def = define('chapter_' + chapter.key, 'story', chapter.sub, '完成' + chapter.title + '。', tier, i >= 7);
        chapterBadges.set(chapter.key, def);
      }
      for (const [id, name, desc] of [
        ['b_pro1_taxi', '别想开走', '拦下出租车，追回行李。'],
        ['b_ch1_1', '车厢里的拉链', '撑过布加拉提在车厢中的攻击。'],
        ['b_ch1_2', '街头对决', '在站前广场战胜布加拉提。'],
      ]) battleBadges.set(id, define(id, 'battle', name, desc, 'bronze'));
      for (const [key, ep] of Object.entries(G.P5_EPISODES)) {
        for (const [i, scene] of ep.scenes.entries()) {
          const sceneId = key + '_' + (i + 1);
          if (scene.explore) clues.add(sceneId);
          if (scene.fight) {
            const id = 'b_p5_' + sceneId, name = scene.fight.name;
            const hidden = (key === 'ch7' && scene.fight.enemy === 'diavolo') || key === 'ch8' || key === 'final';
            battleBadges.set(id, define(id, 'battle', name, '在战斗中击败' + name + '。', key === 'final' ? 'gold' : 'silver', hidden));
          }
        }
      }
      define('taxi_freeze', 'skill', '原地停住', '用回音 ACT 3 压住出租车并赢下追车战。', 'bronze');
      define('parry_win', 'skill', '正中时机', '在获胜的一次尝试中成功弹反。', 'bronze');
      define('no_damage', 'skill', '无伤制胜', '在可战败的战斗中，无伤且未用放水获胜。', 'gold');
      define('retry_win', 'skill', '再来一次', '选择重试并赢下一场战斗。', 'silver');
      define(LIFE, 'explore', '生命的形状', '在第1章用黄金体验赋予藤蔓和蝴蝶生命。', 'silver');
      define(EVIDENCE, 'explore', '沿途的线索', '主动调查三处不同的后续章节线索。', 'silver');
      define(ALL_CHAPTERS, 'story', '黄金精神', '完成从序章到终章的全部章节。', 'gold');

      state = read();
      if (state) return;
      state = { v: 1, got: Object.create(null), life: [], evidence: [] };
      update(() => {
        if (oldProgress) {
          // 第1章本来就可单独进入，因此 max 无法证明玩家打完序章。
          for (const chapter of chapters.slice(1, oldProgress.max)) unlock(chapterBadges.get(chapter.key), false, 0);
          if (oldProgress.clear) unlock(chapterBadges.get('final'), false, 0);
        }
        checkJourney(false);
        // 新玩家打开标题时不建立空存档，以免容器把它当作已有本机进度。
        return Object.keys(state.got).length > 0;
      });
    },
    chapterDone(key) {
      update(() => {
        const changed = unlock(chapterBadges.get(key));
        return checkJourney() || changed;
      });
    },
    battleWon(id, { attempt, assist, hurt, parry, losable, freezes }) {
      const def = battleBadges.get(id);
      if (!def) return;
      update(() => {
        let changed = unlock(def);
        if (id === 'b_pro1_taxi' && freezes > 0) changed = unlockId('taxi_freeze') || changed;
        if (parry > 0) changed = unlockId('parry_win') || changed;
        if (losable && hurt === false && !assist) changed = unlockId('no_damage') || changed;
        if (attempt > 0) changed = unlockId('retry_win') || changed;
        return changed;
      });
    },
    life(id) {
      if (lifeForms.includes(id)) update(() => collect(LIFE, state.life, id, lifeForms.length));
    },
    investigate(id) {
      if (clues.has(id)) update(() => collect(EVIDENCE, state.evidence, id, 3));
    },
    list(cat) { return defs.filter(def => !cat || def.cat === cat); },
    has,
    date(id) { return state.got[id]; },
    count() { return defs.filter(def => has(def.id)).length; },
    progress(id) {
      if (id === LIFE) return [state.life.length, lifeForms.length];
      if (id === EVIDENCE) return [Math.min(state.evidence.length, 3), 3];
      return null;
    },
    nextToast() { return queue.shift(); },
  };
})();
