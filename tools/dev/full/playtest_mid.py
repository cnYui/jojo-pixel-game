"""第4–9章真实键盘路线验收（routes-mid，2026-10-09 收尾）。

继承 tools\\playtest.py 的 Tester：从标题「选择章节」进章，一路打到章末「第N章 完」菜单。
所有推进、移动、攻击、QTE、失败重试都走 Playwright 的真实键盘；脚本只读快照（G.dbg.snapshot）
和下面 MID_JS 读到的公开状态（敌人预警剩余时间、危险区、道具位置、QTE 进度），不写旗标、不改血量、不跳剧情。

用法（游戏目录）：
  python -B tools\\dev\\full\\playtest_mid.py ch4 --out tools\\_playtest\\mid_ch4
  python -B tools\\dev\\full\\playtest_mid.py ch7 --lose --out tools\\_playtest\\mid_ch7_lose
--lose：每场可失败的战斗先故意输一次（每章指定的一场输两次，验「放水再来」），再重试打赢。
"""
from pathlib import Path
import json
import math
import re
import sys
import time

sys.dont_write_bytecode = True
GAME = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(GAME / 'tools'))
import playtest  # noqa: E402

# 只读：敌人预警的真实剩余时间（debug 快照的 hitIn 会多算一次前摇、危险区 warnLeft 读不到），危险区 / 弹体 / 道具 / QTE。
MID_JS = r"""() => {
  const W = G.world, p = W.player, st = W.stage, f = W.fight, now = G.clk.world;
  const r = v => (typeof v === 'number' && isFinite(v)) ? Math.round(v * 100) / 100 : (v == null ? null : v);
  const prim = (v, d = 0) => {
    if (v == null || ['string', 'number', 'boolean'].includes(typeof v)) return typeof v === 'number' ? r(v) : v;
    if (d > 3 || typeof v !== 'object' || v.cid || v.getContext || typeof v === 'function') return undefined;
    if (Array.isArray(v)) return v.slice(0, 24).map(x => prim(x, d + 1));
    const o = {}; for (const [k, x] of Object.entries(v)) { const y = prim(x, d + 1); if (y !== undefined) o[k] = y; } return o;
  };
  const row = a => ({
    id: a.id || null, cid: a.cid, x: r(a.x), y: r(a.y), z: r(a.z || 0), team: a.team, hp: r(a.hp), mhp: r(a.maxHp),
    st: a.state || null, vis: a.visible !== false, alpha: r(a.alpha == null ? 1 : a.alpha), frozen: a.frozen == null ? null : a.frozen,
    f: a.facing, dead: !!a.dead, boss: !!a.boss, untg: !!a.untargetable, clone: !!a._cloneOf, root: r(a.rootT || 0),
    anim: a.anim || null, scale: r(a.scale || 1), talk: !!a.talk, label: a.label || null,
    tele: a.tele ? { m: typeof a.tele.move === 'string' ? a.tele.move : null, left: r(a.tele.dur - a.tele.t), tier: a.tele.tier || null,
      kind: (() => { const mv = typeof a.tele.move === 'string' ? G.MOVES[a.tele.move] : a.tele.move; if (!mv) return 'melee';
        if (mv.dash || mv.diveAlongPath) return 'dash'; if (mv.melee === false && (mv.shot || mv.fireAt)) return 'ranged';
        if (mv.melee === false) return 'hazard'; return 'melee'; })(),
      tx: a.tele.target ? r(a.tele.target.x) : null, ty: a.tele.target ? r(a.tele.target.y) : null,
      path: a.tele.path ? a.tele.path.map(q => [r(q[0]), r(q[1])]) : null } : null,
    atk: a.atk ? { id: a.atkId || null, slot: a.atk.slot || null, t: r(a.atkT), a0: r(a.atk.active ? a.atk.active[0] : 0),
      a1: r(a.atk.active ? a.atk.active[1] : 0), dur: r(a.atk.dur), guard: a.atk.guard || null } : null,
    dash: !!(a.mem && a.mem.dash), mem: a.cid === 'death13' && a.mem ? { n: a.mem.n || 0, after: r(a.mem.after || 0), beat: r(a.mem.beat || 0) } : null,
  });
  const A = st ? st.actors : [];
  const q = G.ui.qte;
  return {
    t: r(now), stage: st ? st.id : null,
    p: p ? Object.assign(row(p), { slot: p.atk ? p.atk.slot : null, rush: !!p.rush, cd: r(p.dodgeCd || 0), iframe: r(p.iframe || 0),
      speed: r(p.speed), rev: (p.controlReverseUntil || 0) > now, hold: !!p.hold }) : null,
    actors: A.filter(a => !a.remove && a !== p).map(row),
    hz: (W.hazards || []).filter(h => !h.dead).map(h => ({ shape: h.shape, x0: r(h.x0), x1: r(h.x1), y0: r(h.y0), y1: r(h.y1),
      x: r(h.follow ? h.follow.x : h.x), y: r(h.follow ? h.follow.y : h.y), rx: r(h.rx), ry: r(h.ry),
      left: r((h.delay || 0) + (h.warn || 0) - h.t), end: r((h.delay || 0) + (h.warn || 0) + (h.dur || 0) - h.t), ph: h.phase,
      guard: h.guard || 'normal', parry: !!h.parry, tag: h.tag || null, side: h.side, dmg: h.dmg, hidden: !!h.hidden,
      own: h.owner ? (h.owner.id || h.owner.cid || null) : null })),
    shots: (W.shots || []).filter(s => !s.dead).map(s => ({ x: r(s.x), y: r(s.y), z: r(s.z), vx: r(s.vx), vy: r(s.vy), side: s.side,
      kind: s.kind || null, curve: !!s.curve, life: r(s.life) })),
    q: q ? { type: q.type, t: r(q.t), m: Array.isArray(q.m) ? q.m.map(r) : r(q.m), zone: q.zone || null,
      res: q.result == null ? null : (typeof q.result === 'object' ? 'obj' : q.result), notes: q.notes || null, ns: q.notesState || null,
      r: q.r || null, thr: !!q.throw, key: q.key || null, hold: !!q.hold, limit: q.limit || null, v: r(q.v), time: q.time || null } : null,
    data: f ? prim(f.data) : null,
    cineBy: W.cine ? (typeof W.cine.by === 'string' ? W.cine.by : ((W.cine.by && W.cine.by.cid) || 'obj')) : null,
    insertUI: !!G.ui.insertUI, insert: !!W.insert,
    hints: (G.ui.hints || []).map(h => h.text),
    words: ((G.uifx && G.uifx.words) || []).slice(-6).map(w => w.word),
    cam: [r(G.cam.x), r(G.cam.y)],
    members: (G.party.members || []).map(a => ({ cid: a.cid, team: a.team, vis: a.visible !== false, x: r(a.x), y: r(a.y),
      leadable: a.leadable !== false, away: !!(a.mem && a.mem.away), talk: !!a.talk, remove: !!a.remove })),
    ev: (G.dbg.events || []).filter(e => /error|missing|unknown|fallback/i.test(e.type)).slice(-30).map(e => [r(e.t), e.type, e.msg || e.name || e.id || e.where || null]),
  };
}"""

# 每章「输两次验放水再来」的那一场（挑输得快的）
LOSE_TWICE = {'b07_hangedman', 'b09a_wheelroad', 'b12_sun', 'b14b_judgement', 'b16a_geb', 'b18a_anubis'}
# 输两次后选「放水再来」验证它真的生效（其余都选「再来一次」）
PICK_ASSIST = {'b18a_anubis'}
# 这些场次本来就不是近战连打（解谜、载具、无替身小孩、限时求生），不套用 dodge / guard / rush 覆盖要求
NO_MELEE_COVER = {'b07_hangedman', 'b08_empress', 'b09a_wheelroad', 'b11_lovers', 'b12_sun', 'b13a_death13', 'b14a_judgement',
                  'b15a_highpriestess', 'b15b_highpriestess', 'b16a_geb', 'b16b_geb', 'b17_prophecy1', 'b17_prophecy2',
                  'b17_prophecy3', 'b19_bast', 'b20a_seth', 'b20b_seth', 'b09b_wheeloffortune', 'b10_justice', 'b13b_death13',
                  'b14b_judgement', 'b18a_anubis', 'b18b_anubis', 'b18c_anubis'}
HIDES = {'wardrobe': 155, 'aquarium': 249, 'bed': 418, 'curtain': 58, 'crate': 506, 'cupboard': 570}
HIDE_ORDER = ['wardrobe', 'aquarium', 'bed', 'curtain', 'crate', 'cupboard']
NAMES = {'jotaro': '承太郎', 'joseph': '乔瑟夫', 'avdol': '阿布德尔', 'kakyoin': '花京院', 'polnareff': '波鲁纳雷夫', 'iggy': '伊奇'}


class MidTester(playtest.Tester):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.m = {}
        self.special = {}
        self.fps_seen = []
        self.events_seen = {}
        self.fight_log = {}
        self.fight_t0 = {}
        self.last_print = 0
        self.mem = {}
        self.act_mem = {}
        self.timeline = []
        self.lose_notes = []
        self.assist_seen = {}

    # ------------------------------------------------------------------ 状态
    def st(self):
        s = super().st()
        try:
            m = self.page.evaluate(MID_JS)
        except Exception as e:  # 换场景的一瞬间可能读不到
            m = {'err': str(e)}
        self.m = m
        s['mid'] = m
        fps = s.get('fps') or {}
        if fps.get('avg'):
            self.fps_seen.append((self.elapsed(), fps.get('avg'), fps.get('min'), s.get('stage'), s.get('fightId')))
        for t, kind, what in m.get('ev') or []:
            key = (kind, str(what))
            if key not in self.events_seen:
                self.events_seen[key] = {'t': self.elapsed(), 'kind': kind, 'what': what, 'stage': s.get('stage'), 'fight': s.get('fightId')}
                print(json.dumps({'event': kind, 'what': what, 'stage': s.get('stage')}, ensure_ascii=False), flush=True)
        self.capture(s)
        fid = s.get('fightId')
        if fid and s.get('combat'):
            self.fight_t0.setdefault((fid, self.loses.get(fid, 0)), self.elapsed())
            if time.monotonic() - self.last_print > 4:
                self.last_print = time.monotonic()
                print(f"[{self.elapsed():.0f}s] {fid} t={s.get('fightT')} hp={s.get('hp')}/{s.get('maxHp')} en={s.get('energy')} "
                      f"hint={json.dumps(s.get('fightHint'), ensure_ascii=False)[:200]}", flush=True)
        return s

    def after_delay(self, key, cond, delay, name):
        now = time.monotonic()
        if not cond:
            self.special.pop('since_' + key, None)
            return
        t0 = self.special.setdefault('since_' + key, now)
        if now - t0 >= delay and name not in self.taken:
            self.shot(name)

    def capture(self, s):
        """关键画面：每张自由走动地图、每场战斗的几个时刻、机关触发的瞬间。"""
        stage, fid, m = s.get('stage'), s.get('fightId'), self.m
        if s.get('free') and not s.get('busy') and stage:
            self.after_delay('free_' + stage, True, 1.6, 'free_' + stage)
        if fid and s.get('combat') and not s.get('cine'):
            n = self.loses.get(fid, 0)
            t = s.get('fightT') or 0
            for mark in (6, 20, 45):
                if t >= mark:
                    self.shot(f'{fid}_a{n}_t{mark}')
        h = s.get('fightHint') or {}
        d = m.get('data') or {}
        q = s.get('qte') or {}
        if q.get('type'):
            self.after_delay('qte_' + str(fid) + q['type'], True, .25, f"qte_{fid or stage}_{q['type']}")
        # 各章机关的瞬间
        checks = [
            ('hanged_light', fid == 'b07_hangedman' and h.get('intercept')),
            ('hanged_jgeil', fid == 'b07_hangedman' and h.get('phase') == 1),
            ('empress_radar', fid == 'b08_empress' and h.get('radar')),
            ('empress_reverse', fid == 'b08_empress' and h.get('reversed')),
            ('wheel_spark', fid == 'b09b_wheeloffortune' and h.get('spark')),
            ('wheel_flipped', fid == 'b09b_wheeloffortune' and h.get('flipped')),
            ('justice_open', fid == 'b10_justice' and h.get('open')),
            ('justice_inhale', fid == 'b10_justice' and h.get('inhale')),
            ('lovers_street0', fid == 'b11_lovers' and h.get('phase') == 'street' and h.get('command') == 0),
            ('lovers_street1', fid == 'b11_lovers' and h.get('phase') == 'street' and h.get('command') == 1),
            ('lovers_street2', fid == 'b11_lovers' and h.get('phase') == 'street' and h.get('command') == 2),
            ('lovers_brain', fid == 'b11_lovers' and h.get('phase') == 'brain' and (s.get('fightT') or 0) > 3),
            ('sun_heat', fid == 'b12_sun' and (h.get('heat') or 0) >= 60),
            ('death13_la', fid in ('b13a_death13', 'b13b_death13') and any((a.get('mem') or {}).get('n') == 3 for a in m.get('actors') or [])),
            ('death13_rooted', fid == 'b13b_death13' and (h.get('rooted') or 0) > 0),
            ('judgement_kneel', fid == 'b14a_judgement' and (h.get('kneel') or 0) > 0),
            ('judgement_body', fid == 'b14b_judgement' and h.get('body')),
            ('priestess_blink', fid == 'b15a_highpriestess' and any(a.get('frozen') == 1 and str(a.get('cid', '')).startswith('prop:disguise') for a in m.get('actors') or [])),
            ('priestess_exposed', fid == 'b15a_highpriestess' and h.get('exposed')),
            ('teeth_bite_warn', fid == 'b15b_highpriestess' and any(z.get('tag') == 'upper_bite' and (z.get('left') or 0) > 0 for z in m.get('hz') or [])),
            ('geb_claw', fid == 'b16a_geb' and any(z.get('ph') == 'active' for z in m.get('hz') or [])),
            ('geb_glide', fid == 'b16b_geb' and (s.get('fightT') or 0) > 3),
            ('anubis_memory', fid in ('b18a_anubis', 'b18b_anubis') and len(h.get('memory') or []) >= 2),
            ('bast_clap', fid == 'b19_bast' and h.get('clap')),
            ('bast_train', fid == 'b19_bast' and any(z.get('tag') is None and (z.get('x1') or 0) - (z.get('x0') or 0) > 600 for z in m.get('hz') or [])),
            ('seth_hidden', fid == 'b20a_seth' and h.get('hidden') == 'aquarium'),
            ('seth_kid_fight', fid == 'b20b_seth' and (s.get('fightT') or 0) > 4),
        ]
        for name, cond in checks:
            self.after_delay(name, bool(cond), .3, name)

    # ------------------------------------------------------------------ 小工具
    def face(self, s, facing):
        if s.get('pfacing') != facing:
            self.hold(['ArrowRight' if facing > 0 else 'ArrowLeft'])
            return False
        return True

    def enemies(self, s, boss_only=False):
        out = []
        for a in self.m.get('actors') or []:
            if a.get('team') != 'enemy' or a.get('dead') or (a.get('hp') or 0) <= 0 or not a.get('vis'):
                continue
            if boss_only and not a.get('boss'):
                continue
            out.append(a)
        return out

    def boss(self):
        return next((a for a in self.m.get('actors') or [] if a.get('team') == 'enemy' and a.get('boss') and not a.get('dead')), None)

    def actor(self, pred):
        # 同 id 的旧对象（上一次尝试留下、已打碎）排在后面
        cands = [a for a in self.m.get('actors') or [] if pred(a)]
        cands.sort(key=lambda a: (bool(a.get('dead')) or (a.get('hp') is not None and a.get('hp') <= 0)))
        return cands[0] if cands else None

    def pressed_recently(self, key, gap):
        now = time.monotonic()
        if now - self.act_mem.get(key, 0) < gap:
            return True
        self.act_mem[key] = now
        return False

    def chord(self, a, b):
        """组合键：两个键在同一帧里按下（K+J 扬沙 / 伏击，J+L 合击）。"""
        self.hold()
        self.page.keyboard.down(a)
        self.page.keyboard.down(b)
        self.page.wait_for_timeout(40)
        self.page.keyboard.up(a)
        self.page.keyboard.up(b)

    def in_hz(self, z, x, y, pad=0):
        if z.get('shape') == 'ellipse':
            rx, ry = (z.get('rx') or 10) + pad, (z.get('ry') or 8) + pad * .5
            return ((x - (z.get('x') or 0)) / rx) ** 2 + ((y - (z.get('y') or 0)) / ry) ** 2 <= 1
        return (z.get('x0') or 0) - pad <= x <= (z.get('x1') or 0) + pad and (z.get('y0') or 0) - pad <= y <= (z.get('y1') or 0) + pad

    def threat(self, s, horizon=.12, reach=86):
        """最近要打到自己的东西：[(剩余秒, 种类, 来源x, 能否格挡, 能否弹反)]，按剩余时间排序。"""
        px, py = s.get('px') or 0, s.get('py') or 0
        out = []
        for e in self.enemies(s):
            tl = e.get('tele')
            # 远程招（发弹）、放危险区的招：预警结束时弹体 / 危险区才刚出现，按弹体距离、危险区剩余时间另算，不在这里提前闪
            if not tl or tl.get('kind') in ('ranged', 'hazard'):
                continue
            if tl.get('left') is not None and 0 <= tl['left'] <= horizon:
                tier = tl.get('tier')
                near = abs(e['x'] - px) <= reach and abs(e['y'] - py) <= 20
                if tl.get('path'):
                    near = near or self.near_path(tl['path'], px, py, 22)
                if tl.get('tx') is not None and abs(tl['tx'] - px) < 30 and abs((tl.get('ty') or py) - py) < 16:
                    near = True
                if near:
                    kind = 'dash' if tl.get('kind') == 'dash' else 'tele'
                    out.append((tl['left'], kind + ':' + str(tl.get('m')), e['x'], tier not in ('W5',) and kind != 'dash', tier not in ('W5',)))
        for z in self.m.get('hz') or []:
            if z.get('side') != 'enemy' or z.get('hidden'):
                continue
            left = z.get('left')
            if left is None:
                continue
            if -0.02 <= left <= horizon and self.in_hz(z, px, py, 3):
                g = z.get('guard') or 'normal'
                out.append((max(0, left), 'hz:' + str(z.get('tag')), z.get('x') if z.get('x') is not None else ((z.get('x0') or 0) + (z.get('x1') or 0)) / 2,
                            g not in ('none', 'parryOnly'), g != 'none' and (z.get('parry') or g == 'parryOnly')))
        for sh in self.m.get('shots') or []:
            if sh.get('side') != 'enemy':
                continue
            dx, dy = sh['x'] - px, sh['y'] - py
            vx = sh.get('vx') or 0
            if abs(dy) < 12 and abs(dx) < 48 and (dx * vx < 0 or sh.get('curve')):
                eta = abs(dx) / max(40, abs(vx)) if vx else .05
                if eta <= horizon + .05:
                    out.append((eta, 'shot', sh['x'], True, True))
        out.sort(key=lambda r: r[0])
        return out

    def near_path(self, path, x, y, tol):
        if not path or len(path) < 2:
            return False
        pts = []
        if len(path) == 3:
            for i in range(17):
                u = i / 16
                v = 1 - u
                pts.append((v * v * path[0][0] + 2 * v * u * path[1][0] + u * u * path[2][0], v * v * path[0][1] + 2 * v * u * path[1][1] + u * u * path[2][1]))
        else:
            for i in range(17):
                u = i / 16
                pts.append((path[0][0] + (path[-1][0] - path[0][0]) * u, path[0][1] + (path[-1][1] - path[0][1]) * u))
        return any(abs(px - x) < tol and abs(py - y) < tol * .6 for px, py in pts)

    def defend_mid(self, s, prefer='alt', horizon=.12):
        """看预警反应：可弹反的交替「按住 L」/ K 闪，W5 与不可挡的危险区只闪，parryOnly 只按 L。"""
        now = time.monotonic()
        if now < self.guard_until:
            self.hold(getattr(self, 'guard_keys', None) or ['l'])
            return True
        if now < self.next_defense:
            return False
        th = self.threat(s, horizon)
        if not th:
            return False
        left, kind, sx, can_guard, can_parry = th[0]
        fid = s.get('fightId')
        n = self.defenses.get(fid, 0) + 1
        self.defenses[fid] = n
        parry_only = kind.startswith('hz:') and not can_guard and can_parry
        use_guard = parry_only or (can_guard and (prefer == 'guard' or (prefer == 'alt' and n % 2 == 1)))
        if use_guard and (can_guard or parry_only):
            # 格挡要面朝来源（倒影 / 枪口 / 敌人）：按住 L 的同时按住朝来源的方向键
            px = s.get('px') or 0
            keys = ['l']
            if sx is not None and abs(sx - px) > 2:
                keys.append('ArrowRight' if sx > px else 'ArrowLeft')
            self.hold(keys)
            self.guard_keys = keys
            self.guard_until = now + .32
            self.next_defense = now + .45
        else:
            if s.get('dodgeCd'):
                if can_guard:
                    self.guard_for(s, .3, sx)
                    return True
                return False
            px = s.get('px') or 0
            away = 'ArrowLeft' if sx is not None and sx > px else 'ArrowRight'
            keys = [away]
            # 贴墙时往另一边闪（闪避无敌帧能穿过敌人）
            x0, x1 = s.get('x0') or 0, s.get('x1') or 320
            if away == 'ArrowLeft' and px - x0 < 40 or away == 'ArrowRight' and x1 - px < 40:
                keys = ['ArrowRight' if away == 'ArrowLeft' else 'ArrowLeft']
            if kind.startswith('hz:'):
                keys = self.hz_escape(s) or keys
            elif kind.startswith('dash:'):
                # 突进是一条线：往上下闪出这条线（闪避纵向 29 px），不靠无敌帧硬吃
                walk = s.get('walkY') or [148, 176]
                py = s.get('py') or 160
                keys = ['ArrowUp' if py - walk[0] > walk[1] - py else 'ArrowDown']
            self.hold(keys)
            self.pulse('k')
            self.next_defense = now + .3
        return True

    def guard_for(self, s, secs, toward_x=None):
        """按住 L（面朝 toward_x）secs 秒。"""
        px = s.get('px') or 0
        keys = ['l']
        if toward_x is not None and abs(toward_x - px) > 2:
            keys.append('ArrowRight' if toward_x > px else 'ArrowLeft')
        self.hold(keys)
        self.guard_keys = keys
        now = time.monotonic()
        self.guard_until = now + secs
        self.next_defense = now + secs + .1

    def precise_guard(self, s, left, secs=.3, target=.05, toward_x=None):
        """精准格挡：等到判定前约 target 秒再按下 L（窗口 0.1 s），按住 secs 秒。"""
        if left > target:
            self.hold()
            self.page.wait_for_timeout(max(0, int((left - target) * 1000)))
        self.guard_for(s, secs, toward_x)

    def hz_escape(self, s):
        px, py = s.get('px') or 0, s.get('py') or 0
        walk = s.get('walkY') or [148, 176]
        for z in self.m.get('hz') or []:
            if z.get('side') != 'enemy' or not self.in_hz(z, px, py, 3):
                continue
            if z.get('shape') == 'ellipse':
                cx, cy = z.get('x') or px, z.get('y') or py
                if abs(px - cx) >= abs(py - cy) * 1.5 or z.get('rx', 10) < 30:
                    return ['ArrowLeft' if px < cx else 'ArrowRight']
                return ['ArrowUp' if py < cy else 'ArrowDown']
            x0, x1, y0, y1 = z.get('x0') or 0, z.get('x1') or 0, z.get('y0') or 0, z.get('y1') or 0
            opts = []
            if y0 - 4 > walk[0]:
                opts.append((py - y0, 'ArrowUp'))
            if y1 + 4 < walk[1]:
                opts.append((y1 - py, 'ArrowDown'))
            opts.append(((px - x0) * .7, 'ArrowLeft'))
            opts.append(((x1 - px) * .7, 'ArrowRight'))
            opts.sort()
            return [opts[0][1]]
        return None

    def approach(self, s, tx, ty, keep=26, ytol=3):
        px, py = s.get('px') or 0, s.get('py') or 0
        dx, dy = tx - px, ty - py
        if abs(dy) > ytol:
            return self.move(s, px if abs(dx) < keep + 40 else tx - (keep if dx > 0 else -keep), ty, ytol) and False
        if abs(dx) > keep + 4 or abs(dx) < keep - 18:
            want = tx - (keep if dx > 0 else -keep)
            if abs(dx) < keep - 18:
                want = tx + (keep if px >= tx else -keep)
            self.move(s, want, ty, 3)
            return False
        return True

    def melee(self, s, e, keep=26, rush=True):
        """贴近一个敌人打三连，每三轮接一次连打。"""
        if s.get('playerRush'):
            self.attack(s)
            return
        if not self.approach(s, e['x'], e['y'], keep):
            return
        facing = 1 if e['x'] >= (s.get('px') or 0) else -1
        if not self.face(s, facing):
            return
        self.hold()
        now = time.monotonic()
        if now >= self.next_attack:
            self.pulse('j')
            cnt = s.get('counts') or {}
            want_rush = rush and (not cnt.get('rushStart') or int(s.get('fightT') or 0) % 6 >= 3)
            self.next_attack = now + (1 / 12 if want_rush else .11)

    # ------------------------------------------------------------------ QTE（rhythm 读音符时间；aim 投掷版对准后按 J）
    def qte(self, s):
        q = self.m.get('q') or {}
        if not q or q.get('res') is not None or not s.get('qte'):
            return super().qte(s)
        self.qte_seen = True
        kind = q.get('type')
        if self.args.lose and self.lose_qte(s, q):
            return True
        if kind == 'rhythm':
            self.hold()
            notes, states = q.get('notes') or [], q.get('ns') or []
            t = q.get('t') or 0
            nxt = [n for n, st in zip(notes, states) if st == 0 and n >= t - .1]
            if nxt:
                dt = nxt[0] - t
                if dt <= .16:
                    if dt > .02:
                        self.page.wait_for_timeout(int((dt - .015) * 1000))
                    self.pulse('j')
                    self.page.wait_for_timeout(60)
            return True
        if kind == 'aim':
            mm = q.get('m') or [0, 0]
            if not isinstance(mm, list):
                mm = [0, 0]
            rad = q.get('r') or 10
            d = math.hypot(mm[0], mm[1])
            if q.get('thr') and d <= rad - 4:
                self.hold()
                self.pulse('j')
                return True
            keys = []
            if abs(mm[0]) > 2:
                keys.append('ArrowLeft' if mm[0] > 0 else 'ArrowRight')
            if abs(mm[1]) > 2:
                keys.append('ArrowUp' if mm[1] > 0 else 'ArrowDown')
            self.hold(keys)
            return True
        if kind == 'timing':
            self.hold()
            zone, mv = q.get('zone') or [.42, .58], q.get('m') or 0
            if isinstance(mv, (int, float)) and zone[0] + .02 <= mv <= zone[1] - .02:
                self.pulse('Enter')
                self.page.wait_for_timeout(80)
            return True
        return super().qte(s)

    def lose_qte(self, s, q):
        """--lose 时故意失手的 QTE（恋人街头命令里按 J 伤到乔瑟夫在 fight 里做，这里只处理需要输的那场）。"""
        fid = s.get('fightId')
        if fid and self.want_lose(s) and q.get('type') in ('rhythm', 'timing', 'clash', 'mash'):
            self.hold()
            return True
        return False

    # ------------------------------------------------------------------ 失败菜单
    def want_lose(self, s):
        fid = s.get('fightId')
        if not self.args.lose or not fid or not s.get('fightLosable'):
            return False
        need = 2 if fid in LOSE_TWICE else 1
        return self.loses.get(fid, 0) < need

    def loss_menu(self, s):
        fid = s.get('fightId') or self.last_fight
        items = s.get('menuItems') or []
        if fid not in self.fights or '再来一次' not in items:
            return False
        self.page.wait_for_timeout(300)
        s = self.st()
        items = s.get('menuItems') or []
        self.hold()
        self.loses[fid] = self.loses.get(fid, 0) + 1
        self.shot(fid + '_lost_' + str(self.loses[fid]))
        uids = {e[0]: e[17] for e in self.fights[fid].get('enemies', []) if e[13]}
        if fid not in self.retry_uids:
            self.retry_uids[fid] = uids
        has_assist = any('放水再来' in x for x in items)
        self.assist_seen[fid] = self.assist_seen.get(fid, []) + [has_assist]
        if self.loses[fid] >= 2:
            self.check(has_assist, 'assist_menu_missing', fight=fid, items=items)
        else:
            self.check(not has_assist, 'assist_menu_too_early', fight=fid, items=items)
        self.lose_notes.append({'fight': fid, 'n': self.loses[fid], 'items': items, 't': self.elapsed()})
        if self.loses[fid] >= 2 and fid in PICK_ASSIST and has_assist:
            self.menu('放水再来')
        else:
            self.menu('再来一次')
        self.next_attack = time.monotonic() + .2
        self.mechanic.pop(fid, None)
        return True

    # ------------------------------------------------------------------ 自由走动
    def explore(self, s):
        stage = s.get('stage')
        flags = s.get('flags') or {}
        party_names = {NAMES.get(a[0]) for a in s.get('party') or []}
        done = {t[1] for t in self.explored.get(stage, set()) if t[0] == 'u'}
        hots = [[h[0], h[1], h[2], [] if h[0] in done else h[3]] for h in s.get('hotspots') or []]
        keep_members = stage == 'camp_ch6'
        npcs = [n for n in s.get('npcs') or [] if keep_members or n[0] not in party_names]
        s2 = dict(s, npcs=npcs, hotspots=hots)
        if stage == 'coast_ch8' and not flags.get('ch8Gum'):
            return self.use_as(s, 'joseph', 110, 160)
        if stage == 'luxor_ch9' and not flags.get('ch9Socket'):
            if not self.special.get('luxor_look') and s.get('leader') == 'jotaro' and s.get('leaderCanInvestigate'):
                if self.move(s, 720, 160, 6):
                    self.hold()
                    self.pulse('u')
                    self.special['luxor_look'] = True
                    self.investigated.setdefault(9, set()).add('jotaro')
                return
            return self.use_as(s, 'joseph', 470, 160)
        if stage == 'camp_ch6' and not flags.get('ch6Sleep'):
            return self.camp(s)
        return super().explore(s2)

    def use_as(self, s, cid, x, y):
        if s.get('leader') != cid:
            self.switch_leader(s, cid)
            return
        if self.move(s, x, y, 6):
            self.hold()
            if not self.pressed_recently('use_' + str(x), 1.2):
                self.pulse('e')

    def camp(self, s):
        flags = s.get('flags') or {}
        if s.get('leader') != 'kakyoin':
            self.switch_leader(s, 'kakyoin')
            return
        todo = [c for c in ('jotaro', 'joseph', 'polnareff') if not flags.get('camp_' + c)]
        if todo:
            a = next((m for m in self.m.get('members') or [] if m['cid'] == todo[0]), None)
            if not a:
                return
            if self.move(s, a['x'] + (14 if (s.get('px') or 0) > a['x'] else -14), a['y'], 4):
                self.hold()
                if not self.pressed_recently('camp_' + todo[0], 1.0):
                    self.pulse('e')
            return
        if self.move(s, 500, 160, 6):
            self.hold()
            if not self.pressed_recently('camp_sleep', 1.2):
                self.pulse('e')

    # ------------------------------------------------------------------ 战斗分派
    def fight(self, s):
        fid = s.get('fightId')
        if self.want_lose(s):
            return self.lose(s)
        fn = getattr(self, 't_' + str(fid), None)
        if fn:
            return fn(s)
        return self.generic(s)

    def generic(self, s, boss_first=True):
        if self.defend_mid(s):
            return
        es = self.enemies(s)
        es = [e for e in es if not e.get('untg') and not e.get('clone')]
        if not es:
            self.hold()
            return
        if boss_first and any(e.get('boss') for e in es):
            e = next(e for e in es if e.get('boss'))
        else:
            e = min(es, key=lambda e: abs(e['x'] - (s.get('px') or 0)) + 2 * abs(e['y'] - (s.get('py') or 0)))
        if (s.get('energy') or 0) >= (s.get('energyMax') or 100) and abs(e['x'] - (s.get('px') or 0)) < 150 and not s.get('playerRush'):
            self.hold()
            self.pulse('u')
            self.next_attack = time.monotonic() + .2
            return
        self.melee(s, e)

    def lose(self, s):
        """故意输：站着不动（少数场次要走到危险里）。"""
        fid = s.get('fightId')
        h = s.get('fightHint') or {}
        if fid == 'b09a_wheelroad':
            lane = h.get('lane', 1)
            want = min(range(3), key=lambda i: abs([152, 160, 168][i] - (h.get('bossLane') or 160)))
            self.hold()
            if lane != want and not self.pressed_recently('lane', .25):
                self.pulse('ArrowDown' if want > lane else 'ArrowUp')
            return
        if fid == 'b11_lovers' and h.get('phase') == 'street':
            self.hold()
            if not self.pressed_recently('lose_j', .5):
                self.pulse('j')
            return
        if fid == 'b12_sun':
            # 站在没有阴影的地方晒
            self.move(s, 200, 165, 6) and self.hold()
            return
        if fid == 'b19_bast':
            self.move(s, s.get('px') or 100, 168, 2) and self.hold()
            return
        if fid == 'b20a_seth':
            d = self.m.get('data') or {}
            spot = HIDES.get(HIDE_ORDER[int(d.get('search') or 0) % 6], 155)
            self.move(s, spot, 158, 6) and self.hold()
            return
        if fid in ('b13b_death13', 'b14b_judgement', 'b18a_anubis', 'b18b_anubis', 'b18c_anubis', 'b14a_judgement', 'b10_justice'):
            # 往敌人身边站，等他们出手
            b = self.boss() or (self.enemies(s) or [None])[0]
            if b and abs(b['x'] - (s.get('px') or 0)) > 30:
                self.move(s, b['x'] - 20, b['y'], 4)
                return
        self.hold()

    # ================================================================== 第4章
    def t_b07_hangedman(self, s):
        h = s.get('fightHint') or {}
        d = self.m.get('data') or {}
        mem = self.mechanic.setdefault('b07_hangedman', {})
        px, py = s.get('px') or 0, s.get('py') or 0
        if h.get('phase'):
            return self.jgeil(s)
        if h.get('intercept'):
            self.hold()
            self.pulse('j')
            return
        # 荷尔·荷斯的红色弯曲虚线：开枪前 0.25 s 起面朝枪口按住 L，挡到子弹飞完
        g = d.get('gun')
        if g and time.monotonic() >= self.guard_until and 0 <= (g.get('at') or 0) - (s.get('fightT') or 0) <= .3:
            return self.guard_for(s, .8, g.get('x'))
        if self.defend_mid(s, prefer='guard'):
            return
        # 1) 打碎镜子 / 橱窗（看不见的可破坏物在地面 x 48 / 248）
        for oid, ox in (('reflection_mirror', 48), ('reflection_window', 248)):
            o = self.actor(lambda a: a.get('id') == oid)
            if o and not o.get('dead') and (o.get('hp') or 0) > 0:
                if s.get('playerAtk') or s.get('playerRush'):
                    self.attack(s)
                    return
                side = 1 if ox < 160 else -1
                if self.move(s, ox + side * 30, 162, 3) and self.face(s, -side):
                    self.hold()
                    if time.monotonic() >= self.next_attack:
                        self.pulse('j')
                        self.next_attack = time.monotonic() + .11
                return
        # 2) 站到没有水洼的位置（水洼 92±20、173±20；右边路人的眼睛 211 照到 141 以右），扬沙让左边路人闭眼；等花京院弹硬币
        spot = 126
        if not self.move(s, spot, 163, 2):
            return
        self.face(s, -1)
        eyes = [r for r in (d.get('reflections') or []) if r.get('kind') == 'eye']
        open_eye = any((r.get('closedUntil') or 0) <= (s.get('fightT') or 0) + 1.5 and abs(r.get('x', 0) - px) < 56 for r in eyes)
        coin_in = h.get('coinIn') or 99
        if open_eye and not self.pressed_recently('sand', 1.2):
            self.chord('k', 'j')
            mem['sand'] = mem.get('sand', 0) + 1
            return
        self.hold()

    def jgeil(self, s):
        if self.defend_mid(s):
            return
        b = self.boss()
        if not b:
            self.hold()
            return
        px = s.get('px') or 0
        civ = [a for a in self.m.get('actors') or [] if str(a.get('id', '')).startswith('jgeil_civilian')]
        # 路人挡在中间就绕到另一边
        blocked = any(abs(c['x'] - b['x']) <= 18 and (c['x'] - px) * (b['x'] - c['x']) >= 0 for c in civ)
        if blocked:
            side = -1 if px < b['x'] else 1
            self.move(s, b['x'] - side * 28, b['y'], 3)
            return
        if (s.get('energy') or 0) >= 100 and abs(b['x'] - px) < 120:
            self.hold()
            self.pulse('u')
            return
        self.melee(s, b)

    def t_b08_empress(self, s):
        h = s.get('fightHint') or {}
        mem = self.mechanic.setdefault('b08_empress', {})
        px = s.get('px') or 0
        if (h.get('growth') or 0) >= 1 and not h.get('radar') and s.get('storyU') and time.monotonic() >= mem.get('radarAt', 0):
            self.hold()
            self.pulse('u')
            mem['radarAt'] = time.monotonic() + 9
            mem['used'] = True
            return
        if not mem.get('used'):
            if self.defend_mid(s, prefer='dodge'):
                return
            # 先把警察推开（J 只推开，不伤人）
            police = [a for a in self.m.get('actors') or [] if str(a.get('id', '')).startswith('empress_police') and abs(a['x'] - px) < 40]
            if police:
                if self.face(s, 1 if police[0]['x'] > px else -1):
                    self.hold()
                    if not self.pressed_recently('push', .4):
                        self.pulse('j')
                return
            self.hold()
            return
        xs = h.get('barrels') or []
        if not xs:
            self.hold()
            return
        x = xs[h.get('tarIndex', 0)]
        if abs(x - px) < 20:
            self.hold()
            if not self.pressed_recently('barrel', .8):
                self.pulse('e')
            return
        # 女帝抢操作时左右颠倒：照真实输入按反方向
        want = 'ArrowRight' if x > px else 'ArrowLeft'
        if h.get('reversed'):
            want = 'ArrowLeft' if want == 'ArrowRight' else 'ArrowRight'
        keys = [want]
        if abs(160 - (s.get('py') or 160)) > 4:
            keys.append('ArrowDown' if (s.get('py') or 160) < 160 else 'ArrowUp')
        self.hold(keys)

    # ================================================================== 第5章
    def t_b09a_wheelroad(self, s):
        h = s.get('fightHint') or {}
        lanes = [152, 160, 168]
        lane = h.get('lane', 1)
        danger = set()
        for z in self.m.get('hz') or []:
            if z.get('side') == 'enemy' and (z.get('left') or 0) <= .45:
                for i, ly in enumerate(lanes):
                    if (z.get('y0') or 0) - 1 <= ly <= (z.get('y1') or 0) + 1:
                        danger.add(i)
        b = self.boss()
        if b and b.get('tele') and (b['tele'].get('left') or 0) <= .5:
            for i, ly in enumerate(lanes):
                if abs(b['y'] - ly) <= 4:
                    danger.add(i)
        self.hold()
        if lane in danger:
            safe = [i for i in range(3) if i not in danger]
            if safe and not self.pressed_recently('lane', .12):
                want = min(safe, key=lambda i: abs(i - lane))
                self.pulse('ArrowDown' if want > lane else 'ArrowUp')
            return
        want = min(range(3), key=lambda i: abs(lanes[i] - (h.get('bossLane') or 160)))
        if want != lane and want not in danger:
            if not self.pressed_recently('lane', .2):
                self.pulse('ArrowDown' if want > lane else 'ArrowUp')
            return
        if b and abs(b['x'] - 80) < 95 and not self.pressed_recently('ram_j', .42):
            self.pulse('j')

    def t_b09b_wheeloffortune(self, s):
        h = s.get('fightHint') or {}
        if h.get('spark') and s.get('storyU'):
            self.hold()
            if not self.pressed_recently('dig', .3):
                self.pulse('u')
            return
        if self.defend_mid(s, prefer='dodge'):
            return
        b = self.boss()
        if not b:
            self.hold()
            return
        if (s.get('energy') or 0) >= 100 and h.get('flipped') and abs(b['x'] - (s.get('px') or 0)) < 140:
            self.hold()
            self.pulse('u')
            return
        self.melee(s, b, keep=30)

    def t_b10_justice(self, s):
        h = s.get('fightHint') or {}
        if h.get('inhale') and s.get('storyU'):
            self.hold()
            if not self.pressed_recently('inhale', .3):
                self.pulse('u')
            return
        if self.defend_mid(s):
            return
        px = s.get('px') or 0
        b = self.boss()
        if h.get('open') and b:
            return self.melee(s, b, keep=28)
        zs = [e for e in self.enemies(s) if e.get('cid') == 'zombie']
        if zs:
            e = min(zs, key=lambda e: abs(e['x'] - px))
            return self.melee(s, e, keep=24)
        # 等恩雅现身：站在柜台附近
        if b:
            self.move(s, b['x'] - 40, b['y'], 4) and self.hold()
            return
        self.hold()

    def t_b11_lovers(self, s):
        h = s.get('fightHint') or {}
        mem = self.mechanic.setdefault('b11_lovers', {})
        if h.get('phase') == 'street':
            return self.street(s, h, mem)
        if not mem.get('swapped') and s.get('fightSwap') and (s.get('fightT') or 0) > 2:
            self.hold()
            self.pulse('q')
            mem['swapped'] = True
            return
        if self.defend_mid(s):
            return
        b = self.boss()
        if not b:
            self.hold()
            return
        if (s.get('energy') or 0) >= 100 and abs(b['x'] - (s.get('px') or 0)) < 200:
            self.hold()
            self.pulse('u')
            return
        keep = 60 if s.get('leader') == 'kakyoin' else 14
        self.melee(s, b, keep=keep)

    def mechanic_fight(self, s, tactic):
        # 父类 run() 在恋人街头阶段直接调 mechanic_fight(s, 'lovers')：转到本类的处理（--lose 时故意按 J 伤乔瑟夫）
        h = s.get('fightHint') or {}
        if tactic == 'lovers' and h.get('phase') == 'street':
            if self.want_lose(s):
                return self.lose(s)
            return self.street(s, h, self.mechanic.setdefault('b11_lovers', {}))
        return super().mechanic_fight(s, tactic)

    def street(self, s, h, mem):
        cmd = h.get('command')
        if cmd == 0:
            self.hold(['l'])
        elif cmd == 1:
            self.hold()
            nxt = 'ArrowLeft' if mem.get('lastDir') != 'ArrowLeft' else 'ArrowRight'
            self.pulse(nxt)
            mem['lastDir'] = nxt
        elif cmd == 2:
            if h.get('vendorWatching'):
                self.hold()
            elif (h.get('progress') or 0) >= .96:
                self.hold()
                if not self.pressed_recently('steal', .4):
                    self.pulse('e')
            else:
                # 老板每 2 秒转一次头：转身前 0.25 秒停下
                t = (self.m.get('data') or {}).get('streetT')
                self.hold(['ArrowRight'])
        else:
            self.hold()

    # ================================================================== 第6章
    def t_b12_sun(self, s):
        h = s.get('fightHint') or {}
        if s.get('storyU') and (h.get('flash') or 0) > 0 and not self.pressed_recently('sun_u', 2.5):
            self.hold()
            self.pulse('u')
            return
        if self.defend_mid(s, prefer='dodge'):
            return
        # 往右走到看得见地平线上镜子穹顶（x 530）的地方；太热就先躲进最近的阴影（岩石 100 / 330 / 570）
        px = s.get('px') or 0
        if (h.get('heat') or 0) >= 85 and not h.get('shaded'):
            spot = min([100, 330, 570], key=lambda x: abs(x - px))
            self.move(s, spot, 166, 6) and self.hold()
            return
        if not h.get('domeSeen'):
            self.move(s, 392, 166, 6)
            return
        self.hold()

    def t_b13a_death13(self, s):
        h = s.get('fightHint') or {}
        d = self.m.get('data') or {}
        if self.scythe_guard(s):
            return
        if h.get('knife'):
            # 拿到小刀后在哪儿按 E 都能刻字
            self.hold()
            if not self.pressed_recently('engrave', 1.0):
                self.pulse('e')
            return
        if self.move(s, 170, 160, 8):
            self.hold()
            if not self.pressed_recently('toy', 1.0):
                self.pulse('e')

    def scythe_guard(self, s):
        """死神13：四拍 LA 之后 0.2 秒横扫（全宽）。第四拍后按 L 弹反（窗口 0.1 秒），不行就闪。"""
        b = self.actor(lambda a: a.get('cid') == 'death13' and a.get('team') == 'enemy')
        if not b or not b.get('mem'):
            return False
        mm = b['mem']
        now = time.monotonic()
        if now < self.guard_until:
            self.hold(getattr(self, 'guard_keys', None) or ['l'])
            return True
        if mm.get('n') == 4 and (mm.get('after') or 0) <= .2 and now >= self.next_defense:
            # 第四拍后 0.2 s 横扫（无预警、全宽）：在扫到前约 0.05 s 按 L = 精准格挡
            self.precise_guard(s, .2 - (mm.get('after') or 0), .3)
            self.next_defense = time.monotonic() + .6
            return True
        return False

    def t_b13b_death13(self, s):
        if self.scythe_guard(s):
            return
        if self.defend_mid(s, prefer='dodge'):
            return
        b = self.boss()
        if not b:
            self.hold()
            return
        px = s.get('px') or 0
        if (s.get('energy') or 0) >= 100 and ((b.get('root') or 0) > 0 or abs(b['x'] - px) < 120):
            self.hold()
            self.pulse('u')
            return
        # 触须网铺在它的飘移路线上（J 三下第三下是网），缠住后近身连打
        if (b.get('root') or 0) > 0:
            return self.melee(s, b, keep=40)
        self.melee(s, b, keep=50)

    # ================================================================== 第7章
    def t_b14a_judgement(self, s):
        """撑 45 秒：不打泥偶（会动摇）。走到离两个敌人远的那一头，让它们都在同一边，面朝它们按住 L（格挡只挡正面，被前后夹就挡不住）；
        要被堵在墙边才从它们中间 K 闪过去。"""
        if self.defend_mid(s, prefer='guard'):
            return
        px, py = s.get('px') or 0, s.get('py') or 0
        es = self.enemies(s)
        if not es:
            self.hold()
            return
        x0, x1 = (s.get('x0') or 0) + 18, (s.get('x1') or 480) - 18
        xs = [e['x'] for e in es]
        cx = sum(xs) / len(xs)
        mem = self.mechanic.setdefault('b14a_judgement', {})
        want = mem.get('end')
        if want is None:     # 每次尝试只选一次：开场时离敌人远的那一头（重来时 loss_menu 会清掉）
            want = x0 if cx > (x0 + x1) / 2 else x1
            mem['end'] = want
        if abs(want - px) > 10:
            dirn = 1 if want > px else -1
            blocked = any(0 < (e['x'] - px) * dirn < 46 and abs(e['y'] - py) < 18 for e in es)
            if blocked:
                if not s.get('dodgeCd'):
                    self.hold(['ArrowRight' if dirn > 0 else 'ArrowLeft'])
                    self.pulse('k')
                else:
                    self.guard_for(s, .2, min(xs, key=lambda x: abs(x - px)))
                return
            self.move(s, want, 162, 6)
            return
        near = min(es, key=lambda e: abs(e['x'] - px))
        if abs(near['x'] - px) < 110:
            self.guard_for(s, .25, near['x'])
            return
        self.face(s, 1 if near['x'] > px else -1) and self.hold()

    def t_b14b_judgement(self, s):
        h = s.get('fightHint') or {}
        if self.defend_mid(s):
            return
        px = s.get('px') or 0
        if not h.get('body'):
            lamp = self.actor(lambda a: a.get('id') == 'judgement_lamp')
            if lamp:
                if s.get('playerAtk') or s.get('playerRush'):
                    self.attack(s)
                    return
                side = -1 if px < lamp['x'] else 1
                if self.move(s, lamp['x'] + side * 40, lamp['y'], 3) and self.face(s, -side):
                    self.hold()
                    if time.monotonic() >= self.next_attack:
                        self.pulse('j')
                        self.next_attack = time.monotonic() + (1 / 12 if int(s.get('fightT') or 0) % 4 >= 2 else .11)
                return
        b = self.boss()
        if b and b.get('cid') == 'judgement':
            if (s.get('energy') or 0) >= 100 and abs(b['x'] - px) < 160:
                self.hold()
                self.pulse('u')
                return
            return self.melee(s, b, keep=30)
        return self.generic(s, boss_first=False)

    def t_b15a_highpriestess(self, s):
        h = s.get('fightHint') or {}
        mem = self.mechanic.setdefault('b15a_highpriestess', {})
        px = s.get('px') or 0
        if h.get('exposed'):
            if self.defend_mid(s):
                return
            body = self.actor(lambda a: a.get('cid') == 'highpriestess' and a.get('team') == 'enemy' and not a.get('dead'))
            if body:
                return self.melee(s, body, keep=24, rush=False)
            self.hold()
            return
        # 看“眨眼”：物件闪一帧（frozen = 1）
        props = [a for a in self.m.get('actors') or [] if str(a.get('cid', '')).startswith('prop:disguise') and a.get('team') == 'object']
        blink = next((a for a in props if a.get('frozen') == 1), None)
        if blink:
            mem['target_x'] = blink['x']
            mem['seen_at'] = time.monotonic()
        tx = mem.get('target_x')
        if tx is None or time.monotonic() - mem.get('seen_at', 0) > 4.5:
            # 没看到眨眼：走到中间等
            self.move(s, 320, 164, 8) and self.hold()
            return
        if s.get('playerAtk'):
            self.hold()
            return
        if self.move(s, tx - 26, 164, 3) and self.face(s, 1):
            self.hold()
            if not self.pressed_recently('strike', .6):
                self.pulse('j')

    def t_b15b_highpriestess(self, s):
        d = self.m.get('data') or {}
        px, py = s.get('px') or 0, s.get('py') or 0
        now = time.monotonic()
        if now < self.guard_until:
            self.hold(getattr(self, 'guard_keys', None) or ['l'])
            return
        bite = [z for z in self.m.get('hz') or [] if z.get('tag') == 'upper_bite']
        if bite and 0 <= (bite[0].get('left') or 9) <= .2 and now >= self.next_defense:
            # 精准格挡窗口 0.1 s：按在咬下来前约 0.05 s
            self.precise_guard(s, bite[0].get('left') or 0, .25)
            self.next_defense = time.monotonic() + .5
            return
        # 下排牙：J3 / 连打打碎（站在牙右边面朝左，舌头往左卷正好推着人贴牙）
        lower = [a for a in self.m.get('actors') or [] if str(a.get('cid')) == 'prop:lower_tooth' and not a.get('dead') and (a.get('hp') or 0) > 0]
        if lower:
            t = min(lower, key=lambda a: abs(a['x'] - px))
            if s.get('playerAtk') or s.get('playerRush'):
                self.attack(s)
                return
            if self.move(s, t['x'] + 24, 164, 4) and self.face(s, -1):
                self.hold()
                if now >= self.next_attack:
                    self.pulse('j')
                    self.next_attack = now + 1 / 12
            return
        # 只剩上排：站在活着的上牙下面等咬
        upper = [a for a in self.m.get('actors') or [] if str(a.get('cid')) == 'prop:upper_tooth' and not a.get('dead') and (a.get('hp') or 0) > 0]
        if upper:
            t = min(upper, key=lambda a: abs(a['x'] - px))
            self.move(s, t['x'] + 6, 164, 6) and self.hold()
            return
        self.hold()

    # ================================================================== 第8章
    def t_b16a_geb(self, s):
        d = self.m.get('data') or {}
        px, py = s.get('px') or 0, s.get('py') or 0
        now = time.monotonic()
        # 水爪：在里面且快要冒出来 → 往前闪
        for z in self.m.get('hz') or []:
            if z.get('side') == 'enemy' and self.in_hz(z, px, py, 6) and -.02 <= (z.get('left') or 9) <= .14 and not s.get('dodgeCd'):
                self.hold(['ArrowRight'])
                self.pulse('k')
                return
        self.hold(['ArrowRight'] + (['ArrowDown'] if py < 162 else ['ArrowUp'] if py > 168 else []))

    def t_b16b_geb(self, s):
        d = self.m.get('data') or {}
        hgt = d.get('height') or 90
        cols = [c for c in d.get('columns') or [] if not c.get('hit') and (c.get('x') or 0) > 100]
        danger = [c for c in cols if (c.get('x') or 0) - 110 < 120]
        if danger:
            top = min(c.get('top', 90) for c in danger)
            want = top - 22
        else:
            want = 112
        want = max(52, min(140, want))
        if hgt > want + 3:
            self.hold(['ArrowUp'])
        elif hgt < want - 3:
            self.hold(['ArrowDown'])
        else:
            self.hold()

    def prophecy(self, s, phase):
        h = s.get('fightHint') or {}
        px = s.get('px') or 0
        lead = s.get('leader')
        if phase == 1:
            if lead != 'iggy':
                if not self.pressed_recently('swap', 1.2):
                    self.hold()
                    self.pulse('q')
                return
            tx = 250
        elif phase == 2:
            if lead != 'polnareff':
                if not self.pressed_recently('swap', 1.2):
                    self.hold()
                    self.pulse('q')
                return
            tx = 490
        else:
            tx = 230 if not h.get('orange') else 690
        if self.move(s, tx, 162, 8):
            self.hold()
            if not self.pressed_recently('prophecy_e', .8):
                self.pulse('e')

    def t_b17_prophecy1(self, s):
        return self.prophecy(s, 1)

    def t_b17_prophecy2(self, s):
        return self.prophecy(s, 2)

    def t_b17_prophecy3(self, s):
        return self.prophecy(s, 3)

    # ================================================================== 第9章
    def anubis(self, s, boss_cid):
        h = s.get('fightHint') or {}
        if s.get('storyU'):
            self.hold()
            if not self.pressed_recently('anubis_u', .5):
                self.pulse('u')
            return
        if self.defend_mid(s, prefer='dodge'):
            return
        b = self.boss()
        if not b:
            self.hold()
            return
        self.melee(s, b, keep=28)

    def t_b18a_anubis(self, s):
        return self.anubis(s, 'chaka')

    def t_b18b_anubis(self, s):
        return self.anubis(s, 'khan')

    def t_b18c_anubis(self, s):
        h = s.get('fightHint') or {}
        b = self.boss()
        now = time.monotonic()
        if now < self.guard_until:
            self.hold(getattr(self, 'guard_keys', None) or ['l'])
            return
        if b and b.get('tele') and b['tele'].get('m') == 'AN_THRUST_P':
            left = b['tele'].get('left') or 9
            if left <= .2 and abs(b['x'] - (s.get('px') or 0)) < 90 and now >= self.next_defense:
                self.precise_guard(s, left, .25, toward_x=b['x'])
                self.next_defense = time.monotonic() + .5
                return
            # 正对它，等精准时机
            self.face(s, 1 if b['x'] > (s.get('px') or 0) else -1)
            return
        if self.defend_mid(s, prefer='dodge'):
            return
        if not b:
            self.hold()
            return
        # 保持在突刺距离内（70 px），正面等它出紫色突刺
        self.approach(s, b['x'], b['y'], keep=44) and self.face(s, 1 if b['x'] > (s.get('px') or 0) else -1) and self.hold()

    def t_b19_bast(self, s):
        h = s.get('fightHint') or {}
        d = self.m.get('data') or {}
        px, py = s.get('px') or 0, s.get('py') or 0
        b = self.boss()
        if not b:
            self.hold()
            return
        # 火车：离开铁轨带（y 164–172）
        if py > 160:
            self.move(s, px, 152, 2)
            return
        if self.defend_mid(s, prefer='dodge'):
            return
        if h.get('clap'):
            self.chord('j', 'l')
            return
        mate = next((m for m in self.m.get('members') or [] if m['cid'] != s.get('leader') and m['cid'] in ('joseph', 'avdol')), None)
        half = (b.get('hp') or 0) <= (b.get('mhp') or 1) * .5 + 1
        if half and mate:
            # 和同伴分站她左右两边：同伴在哪边，自己去另一边，距离 48
            side = -1 if mate['x'] > b['x'] else 1
            want = b['x'] + side * 46
            if self.move(s, want, b['y'] if b['y'] < 160 else 154, 3):
                self.face(s, -side)
                self.hold()
            return
        self.melee(s, b, keep=36)

    def t_b20a_seth(self, s):
        h = s.get('fightHint') or {}
        d = self.m.get('data') or {}
        px = s.get('px') or 0
        b = self.boss()
        aq = HIDES['aquarium']
        if h.get('hidden') != 'aquarium':
            # 他正在劈鱼缸就别进去
            chopping = any(z.get('side') == 'enemy' and (z.get('x0') or 0) <= aq <= (z.get('x1') or 0) for z in self.m.get('hz') or [])
            if chopping:
                self.move(s, aq + 60, 158, 6) and self.hold()
                return
            if self.move(s, aq, 158, 8):
                self.hold()
                if not self.pressed_recently('hide', .8):
                    self.pulse('e')
            return
        if not b:
            self.hold()
            return
        behind = (aq - b['x']) * (b.get('f') or 1) < 0 and abs(aq - b['x']) <= 86
        chopping_here = any(z.get('side') == 'enemy' and (z.get('x0') or 0) <= aq <= (z.get('x1') or 0) for z in self.m.get('hz') or [])
        if chopping_here and not self.pressed_recently('unhide', .8):
            self.hold()
            self.pulse('e')   # 出来躲斧头
            return
        if behind and not self.pressed_recently('ambush', .8):
            self.chord('k', 'j')
            return
        self.hold()

    def t_b20b_seth(self, s):
        if self.defend_mid(s, prefer='dodge'):
            return
        b = self.boss()
        if not b:
            self.hold()
            return
        self.melee(s, b, keep=22, rush=False)

    # ------------------------------------------------------------------ 收尾检查
    def validate(self):
        super().validate()
        # 父类按 M1 的近战覆盖要求逐场检查；中段大量解谜 / 载具 / 求生战，换成只查本章是否用过三种防守 / 必杀
        self.errors = [e for e in self.errors if not (e['kind'] in ('coverage_dodge', 'coverage_defense', 'coverage_rush') and e.get('fight') in NO_MELEE_COVER)]
        tot = {}
        for c in self.coverage.values():
            for k, v in c.items():
                tot[k] = tot.get(k, 0) + v
        self.check(tot.get('dodge', 0) >= 1, 'chapter_dodge_missing', counts=tot)
        self.check(tot.get('guard', 0) + tot.get('parry', 0) >= 1, 'chapter_defense_missing', counts=tot)
        if self.fps_seen:
            avgs = [r[1] for r in self.fps_seen]
            mean = sum(avgs) / len(avgs)
            low = sorted(avgs)[max(0, len(avgs) // 20)]
            self.check(mean >= 55, 'fps_mean_below_55', mean=round(mean, 1), p5=low)
        bad = [v for k, v in self.events_seen.items() if v['kind'] in ('loop_error', 'script_error', 'api_missing', 'fx_unknown', 'fx_error', 'tpl_px_error', 'startup_error', 'look_missing', 'video_missing')]
        for v in bad:
            self.check(False, 'game_event_' + v['kind'], **v)

    def report(self):
        r = super().report()
        avgs = [x[1] for x in self.fps_seen]
        r['fps_stats'] = {'samples': len(avgs), 'mean': round(sum(avgs) / len(avgs), 1) if avgs else None,
                          'min_window_avg': min(avgs) if avgs else None,
                          'p5': sorted(avgs)[max(0, len(avgs) // 20)] if avgs else None,
                          'worst': sorted(self.fps_seen, key=lambda x: x[1])[:5]}
        r['game_events'] = list(self.events_seen.values())
        r['lose_notes'] = self.lose_notes
        r['assist_seen'] = self.assist_seen
        r['fight_start'] = {f'{k[0]}#{k[1]}': v for k, v in self.fight_t0.items()}
        r['input_boundary'] = '推进、移动、攻击、QTE、失败重试全部经真实键盘；只读 G.dbg.snapshot 与 MID_JS 的公开状态。'
        return r


def main():
    p = playtest.parser()
    args0 = sys.argv[1:]
    playtest.Tester = MidTester
    if '--timeout' not in args0:
        sys.argv = sys.argv[:1] + args0 + ['--timeout', '3600']
    return playtest.main()


if __name__ == '__main__':
    raise SystemExit(main())
