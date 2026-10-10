"""后段（第10章、第11章、终章）真实键盘路线验收。

继承 tools/playtest.py 的 Tester：推进对白、移动、攻击、QTE、失败重试全部经键盘（Playwright 自带 Chromium）。
只读 G.dbg.snapshot()、G.lateGame 和战斗的公开状态（c.data 的计时 / 位置、Boss 的位置和出招、时停阶段），
不写血量、伤害、时间、剧情旗标，也不调剧情 API。

用法（在游戏目录）：
    python -B tools/dev/full/test_late_routes.py ch10  --out tools/_playtest/late_ch10
    python -B tools/dev/full/test_late_routes.py ch11  --out tools/_playtest/late_ch11
    python -B tools/dev/full/test_late_routes.py final --out tools/_playtest/late_final
    加 --lose：每场可失败的战斗先主动输一次（再来一次）；扑克 / 布网 / 钟面 / 迷宫也各故意失败一次，验证只重来当前机关。
"""
from pathlib import Path
import json
import math
import sys
import time

sys.dont_write_bytecode = True
GAME = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(GAME / 'tools'))
import playtest  # noqa: E402

NAMES = {'jotaro': '承太郎', 'joseph': '乔瑟夫', 'avdol': '阿布德尔', 'kakyoin': '花京院', 'polnareff': '波鲁纳雷夫', 'iggy': '伊奇'}
# 对白里出现这些字时截一张（等对话框弹出动画放完），人工逐张看构图 / 卡片 / 人物是否出画
STORY_SHOTS = {
    # 第10章
    '你们愿意赌上灵魂吗': 'c10_darby', '你的选择，我早就知道': 'c10_soul_pol', '就算你发现这一处': 'c10_soul_jos',
    '到底有什么把握': 'c10_poker_sweat', '他到底换了什么牌': 'c10_poker_crack', '开牌啊': 'c10_poker_win',
    '你的呼吸很平稳': 'c10_flashback', '十五秒后，镜子前': 'c10_prophecy1', '十五秒后，油桶旁': 'c10_prophecy2',
    '十五秒后，路口正中': 'c10_prophecy3', '当 No.2 果然最好': 'c10_holhorse_out', '它追进了下水道': 'c10_to_sewer',
    '那只鸟再也没有飞起来': 'c10_bird_down', '找到了 DIO 的馆': 'c10_mansion',
    # 第11章
    '我说过会在这里等你们': 'c11_kakyoin_back', '我的一切都可以献出': 'c11_vanilla_kneel', '起来吧，瓦尼拉': 'c11_dio_voice',
    '欢迎光临。主人还在休息': 'c11_telence', '这里是游戏室': 'c11_game_room', '最后一个弯道': 'c11_race_lost',
    '读得到我的灵魂': 'c11_baseball_win', '阿布德尔——！！': 'c11_avdol_gone', '为了 DIO 大人……': 'c11_cream_card',
    '腿又复原了': 'c11_vampire', '伊奇——！！': 'c11_iggy_gone', '好好晒晒太阳吧': 'c11_sun_kick', '阿布德尔……伊奇……': 'c11_mourn',
    '你的脸和身体': 'c11_nukesaku', '我带路': 'c11_guide', '一顶帽子的空镜': 'c11_coffin', '醒得正好': 'c11_end',
    # 终章
    '再上一步，就到我这边来了': 'fin_stairs', '回过神来却在下楼': 'fin_stairs_back', '不会对着我的伙伴': 'fin_refuse',
    '不够记在 SPW': 'fin_truck', '开车，追上那辆卡车': 'fin_senator', '上议员没能逃出来': 'fin_crash', '可以不算吗': 'fin_crash6',
    '半径20米': 'fin_splash', '所有的丝同时断开': 'fin_cut', '替身的秘密': 'fin_kakyoin_msg', '时间……是时间': 'fin_joseph_time',
    '别靠近他': 'fin_joseph_fall', '你竟然主动靠近我': 'fin_approach', '心跳真的停了': 'fin_play_dead', '赶上了！': 'fin_polnareff',
    '最高哒': 'fin_saikou', '我是……DIO': 'fin_dio_end', '你惹我生气了': 'fin_jotaro_back', '黎明的阳光中化灰': 'fin_dawn',
    '是我 DIO 哒': 'fin_joke', '承太郎……': 'fin_holly', 'Holly 已经醒了': 'fin_airport_joseph', '替我跟阿布德尔和伊奇说声谢谢': 'fin_airport_pol',
    '星尘斗士的旅途': 'fin_credits',
}
# 只看机关解法、不以近战连打为主的战斗：覆盖检查里不要求连打（闪避 / 格挡照常要求）
NO_RUSH_COVERAGE = {'b22_prophecy1', 'b22_prophecy2', 'b22_prophecy3', 'b23a_petshop', 'b23b_petshop', 'b26b_cream'}

EXTRA_JS = r'''(s) => {
  const W = G.world, c = W.fight, p = W.player, T = G.time;
  s.uiFx = { vs: G.uifx.vsCur ? G.uifx.vsCur.key : null,
    cards: (G.uifx.cards || []).filter(k => k.m && k.m.image).map(k => k.m.image),
    titles: (G.uifx.titles || []).map(t => t.key), chapterCard: G.uifx.chapter ? G.uifx.chapter.key : null };
  s.choiceIdx = G.ui.choiceBox ? G.ui.choiceBox.idx : null;
  s.choiceT = G.ui.choiceBox ? G.ui.choiceBox.t : null;
  s.menuT = G.ui.menu ? G.ui.menu.t : null;
  const prim = o => { const r = {}; for (const k in o || {}) { const v = o[k];
      if (v == null || ['number', 'boolean', 'string'].includes(typeof v)) r[k] = v;
      else if (Array.isArray(v) && v.length <= 64 && v.every(x => typeof x === 'number')) r[k] = v.slice(); } return r; };
  const e = c ? c.boss : null;
  s.fx2 = {
    data: c ? prim(c.data) : null,
    p: p ? { bodyW: p.bodyW || 6, immune: !!(T.active && T.immune.has(p)), frozen: !!T.isFrozen(p),
      hold: p._chordHold && p._chordHold['guard+dodge'] ? p._chordHold['guard+dodge'].t : 0 } : null,
    e: e ? { x: e.x, y: e.y, z: e.z || 0, hp: e.hp, maxHp: e.maxHp, state: e.state, atkId: e.atk ? (e.atkId || null) : null,
      atkT: e.atkT || 0, perch: !!(e.mem && e.mem.perch), alpha: e.alpha,
      tele: e.tele ? { move: e.tele.move, t: e.tele.t, dur: e.tele.dur } : null,
      dash: e.mem && e.mem.dash ? { pts: e.mem.dash.pts, t: e.mem.dash.t, dur: e.mem.dash.dur } : null } : null,
    ts: T.active ? { phase: T.phase, t: T.t, by: T.by ? T.by.cid : null, dur: T.o ? T.o.dur : null } : null,
  };
  return s;
}'''
playtest.STATE_JS = '() => (' + EXTRA_JS + ')((' + playtest.STATE_JS + ')())'

DASH_JS = '''() => { const c = G.world.fight, e = c && c.boss, p = G.world.player;
  return e && e.mem && e.mem.dash && p ? { dash: { pts: e.mem.dash.pts, t: e.mem.dash.t, dur: e.mem.dash.dur },
    px: p.x, py: p.y, facing: p.facing, bodyW: p.bodyW || 6 } : null; }'''
LATE_JS = '''() => { const q = G.lateGame, p = G.world.player;
  if (!q) return null;
  const o = {}; for (const k in q) { const v = q[k]; if (v == null || ['number','boolean','string'].includes(typeof v)) o[k] = v; }
  if (q.nodes) o.nodes = q.nodes.map(n => [n.x, !!n.set]);
  if (q.cars) o.cars = q.cars.map(c => [c.x, c.lane, c.warn, !!c.hit]);
  o.px = p ? p.x : null; o.py = p ? p.y : null; o.leader = p ? p.cid : null; o.facing = p ? p.facing : 1;
  return o; }'''


def bez(pts, u):
    u = max(0.0, min(1.0, u))
    if len(pts) == 2:
        (x0, y0), (x1, y1) = pts
        return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
    (x0, y0), (x1, y1), (x2, y2) = pts[0], pts[1], pts[2]
    v = 1 - u
    return v * v * x0 + 2 * v * u * x1 + u * u * x2, v * v * y0 + 2 * v * u * y1 + u * u * y2


def seg_dist(px, py, a, b):
    # combat.dashTick 的判定：y 方向 ×1.5 的线段距离
    dx, dy = b[0] - a[0], b[1] - a[1]
    u = max(0.0, min(1.0, ((px - a[0]) * dx + (py - a[1]) * dy) / (dx * dx + dy * dy or 1)))
    return math.hypot(px - (a[0] + dx * u), (py - (a[1] + dy * u)) * 1.5)


def contact_time(dash, px, py, rad, horizon=0.6, step=1 / 120):
    """俯冲路径（与 combat.beginDash 同一条二次贝塞尔，u = t / dur）多久后扫到玩家；扫不到返回 None。"""
    pts, t0, dur = dash['pts'], dash['t'], max(dash['dur'], 1e-6)
    prev = bez(pts, t0 / dur)
    if math.hypot(px - prev[0], (py - prev[1]) * 1.5) <= rad:
        return 0.0
    tau = 0.0
    while tau < horizon and t0 + tau < dur:
        tau += step
        cur = bez(pts, (t0 + tau) / dur)
        if seg_dist(px, py, prev, cur) <= rad:
            return tau
        prev = cur
    return None


class LateTester(playtest.Tester):
    def __init__(self, page, args, out):
        super().__init__(page, args, out)
        self.special = {}
        self.fps_log = []
        self.late = {}
        self.talked = set()
        self.next_fps = 0
        self._ranged = None

    # ------------------------------------------------------------------ 观察（只读）
    def st(self):
        s = super().st()
        now = time.monotonic()
        if now >= self.next_fps and s.get('scene') == 'world':
            self.next_fps = now + 5
            fps = s.get('fps') or {}
            self.fps_log.append([self.elapsed(), fps.get('avg'), fps.get('min'), s.get('stage')])
        text = (s.get('dlg') or '') + (s.get('narr') or '') + (s.get('notice') or '')
        if '看牌反而暴露了想法' in text and not self.late.get('poker_lost'):
            self.late['poker_lost'] = True
            self.marks.append([self.elapsed(), 'poker_lost_retry', 'mini'])
        for key, name in STORY_SHOTS.items():
            if key in text and name not in self.special:
                self.special[name] = True
                self.page.wait_for_timeout(280)
                self.shot('story_' + name)
        fx = s.get('uiFx') or {}
        for item in ([('vs', fx.get('vs'))] if fx.get('vs') else []) + [('card', c) for c in fx.get('cards') or []] + \
                [('title', t) for t in fx.get('titles') or []] + ([('chapter', fx['chapterCard'])] if fx.get('chapterCard') else []):
            name = item[0] + '_' + str(item[1]).split('/')[-1]
            if name not in self.special:
                self.special[name] = True
                self.page.wait_for_timeout(420 if item[0] in ('card', 'vs') else 250)
                self.shot(name)
        lg = s.get('lateGame') or {}
        if lg.get('type'):
            k = 'mini_' + lg['type']
            if k not in self.special and (lg.get('t') or 0) > 1.2:
                self.special[k] = True
                self.shot(k)
        f2 = s.get('fx2') or {}
        ts = f2.get('ts')
        if ts and ts.get('phase') == 'stopped':
            k = 'ts_' + str(s.get('fightId') or s.get('stage')) + '_' + str(ts.get('by'))
            if k not in self.special:
                self.special[k] = True
                self.shot(k)
        if s.get('free') and not s.get('busy') and s.get('stage') and ('free_' + s['stage']) not in self.special:
            first = self.special.setdefault('free_at_' + s['stage'], time.monotonic())
            if time.monotonic() - first > 1.5:
                self.special['free_' + s['stage']] = True
                self.shot('free_' + s['stage'])
        return s

    # ------------------------------------------------------------------ 推进：选项、小游戏
    def advance(self, s):
        if s.get('choice') and not s.get('qte'):
            return self.choose(s)
        if super().advance(s):
            return True
        lg = s.get('lateGame')
        if lg and lg.get('type') and not s.get('combat'):
            self.mini(s, lg)
            return True
        return False

    def choose(self, s):
        opts = s['choice']
        want = 0
        if any('我已经换过牌了' in o or '押母亲的灵魂' in o for o in opts):
            if self.args.lose and not self.late.get('poker_lost'):
                want = 0                       # 连续两轮看牌 = 被达比逼输（主动失败一次，验证只重来这一手）
            else:
                want = next((i for i, o in enumerate(opts) if '我已经换过牌了' in o), None)
                if want is None:
                    want = next(i for i, o in enumerate(opts) if '押母亲的灵魂' in o)
        elif any('发牌小哥' in o for o in opts):
            want = opts.index('发牌小哥')
        self.hold()
        idx = s.get('choiceIdx') or 0
        key = 'ArrowDown' if want >= idx else 'ArrowUp'
        for _ in range(abs(want - idx)):
            self.pulse(key)
            self.page.wait_for_timeout(70)
        self.page.wait_for_timeout(150)
        cur = self.page.evaluate('() => G.ui.choiceBox ? G.ui.choiceBox.idx : null')
        if cur is not None and cur != want:
            return True                         # 下一轮再对齐
        self.marks.append([self.elapsed(), 'choice:' + opts[want], 'choice'])
        self.pulse('Enter')
        self.page.wait_for_timeout(150)
        return True

    def mini(self, s, lg):
        kind = lg.get('type')
        fn = getattr(self, 'mini_' + kind, None)
        if fn is None:
            self.note('mini_unhandled', type=kind)
            self.hold()
            return
        fn(s, lg)

    def late_state(self):
        return self.page.evaluate(LATE_JS)

    def mini_dealer(self, s, lg):
        # 盯住发牌的手：额外抽牌那 0.21 秒内按 J（提前按会打草惊蛇）
        self.hold()
        until = time.monotonic() + 2.5
        while time.monotonic() < until:
            q = self.late_state()
            if not q or q.get('type') != 'dealer':
                return
            if q.get('caught') or q.get('tooEarly'):
                break
            if q.get('extra'):
                self.pulse('j', .012)
                self.marks.append([self.elapsed(), 'dealer_catch', 'mini'])
                break
            self.page.wait_for_timeout(8)
        self.page.wait_for_timeout(60)

    def mini_stairs(self, s, lg):
        self.hold(['ArrowRight'])

    def mini_message(self, s, lg):
        self.hold()
        now = time.monotonic()
        if now >= self.next_attack:
            self.pulse('j')
            self.next_attack = now + 1 / 10

    def mini_baseball(self, s, lg):
        self.hold()
        if lg.get('phase') != 'select':
            return
        if (lg.get('inning') or 1) >= 3 and not lg.get('delegated'):
            self.pulse('q')
            self.page.wait_for_timeout(90)
        self.pulse('j')
        self.page.wait_for_timeout(120)

    def mini_web(self, s, lg):
        if self.args.lose and not self.late.get('web_lost'):
            self.hold()                         # 30 秒什么都不做：布网失败，只重来这张网
            if (lg.get('t') or 0) > 29:
                self.late['web_lost'] = True
            return
        q = self.late_state() or lg
        px = q.get('px') or 0
        if (q.get('warn') or 0) > 0 and not q.get('evaded') and abs(px - (q.get('targetX') or -999)) < 26:
            left_free = px - 42 >= 20
            go_left = px > 560 or (left_free and not any(not n[1] and n[0] > px for n in q.get('nodes') or []))
            self.hold(['ArrowLeft' if go_left else 'ArrowRight'])
            self.pulse('k')
            self.marks.append([self.elapsed(), 'web_dodge', 'mini'])
            self.hold()
            return
        todo = [n[0] for n in q.get('nodes') or [] if not n[1]]
        if not todo:
            self.hold()
            return
        x = min(todo, key=lambda v: abs(v - px))
        if abs(x - px) <= 12:
            self.hold()
            self.pulse('j')
            self.page.wait_for_timeout(40)
        else:
            self.hold(['ArrowRight' if x > px else 'ArrowLeft'])

    def mini_clock(self, s, lg):
        if self.args.lose and not self.late.get('clock_lost'):
            self.hold()
            self.pulse('j')                     # 直接开枪：射偏，只重试这一发
            self.late['clock_lost'] = True
            self.page.wait_for_timeout(200)
            return
        until = time.monotonic() + 8
        while time.monotonic() < until:
            q = self.late_state()
            if not q or q.get('type') != 'clock':
                self.hold()
                return
            dx, dy = q['tx'] - q['x'], q['ty'] - q['y']
            keys = []
            if abs(dx) > 3:
                keys.append('ArrowRight' if dx > 0 else 'ArrowLeft')
            if abs(dy) > 3:
                keys.append('ArrowDown' if dy > 0 else 'ArrowUp')
            if keys:
                self.hold(keys)
                self.page.wait_for_timeout(15)
                continue
            self.hold()
            if abs(dx) > 1.2:
                self.pulse('ArrowRight' if dx > 0 else 'ArrowLeft', .012)
                self.page.wait_for_timeout(30)
                continue
            if abs(dy) > 1.2:
                self.pulse('ArrowDown' if dy > 0 else 'ArrowUp', .012)
                self.page.wait_for_timeout(30)
                continue
            self.shot('clock_aim')
            self.pulse('j')
            self.page.wait_for_timeout(200)
            return

    def mini_labyrinth(self, s, lg):
        if self.args.lose and not self.late.get('lab_lost'):
            self.hold()                         # 60 秒不找假墙：幻觉送回原处，只重来这段走廊
            if (lg.get('t') or 0) > 59:
                self.late['lab_lost'] = True
            return
        q = self.late_state() or lg
        px, leader = q.get('px') or 0, q.get('leader')
        if not q.get('found'):
            if leader not in ('avdol', 'iggy'):
                self.hold()
                self.pulse('q')
                self.page.wait_for_timeout(150)
                return
            self.hold()
            self.pulse('u')
            self.page.wait_for_timeout(120)
            return
        wall = q.get('wallX') or 285
        want = wall - 22 if px < wall else wall + 22
        if abs(px - want) > 6:
            self.hold(['ArrowRight' if want > px else 'ArrowLeft'])
            return
        facing = 1 if wall > px else -1
        if q.get('facing') != facing:
            self.pulse('ArrowRight' if facing > 0 else 'ArrowLeft', .012)
            return
        self.hold()
        self.pulse('j')
        self.page.wait_for_timeout(260)

    def mini_lanes(self, q, free_keys, race):
        lane = q.get('lane', 1)
        danger = lambda ln: any(c[1] == ln and 40 < c[0] < (190 if race else 170) and not c[3] for c in q.get('cars') or [])
        if danger(lane):
            for cand in (lane - 1, lane + 1) if lane else (lane + 1, lane - 1):
                if 0 <= cand <= 2 and not danger(cand):
                    self.pulse(free_keys[0] if cand < lane else free_keys[1])
                    return True
        return False

    def mini_race(self, s, lg):
        q = self.late_state() or lg
        self.hold(['j'])                       # 按住 J 加速
        if self.mini_lanes(q, ('ArrowLeft', 'ArrowRight'), True):
            self.page.wait_for_timeout(60)

    def mini_chase(self, s, lg):
        q = self.late_state() or lg
        self.hold()
        t = q.get('t') or 0
        cyc = t % 8
        if cyc >= 6.6 and (q.get('slow') or 0) <= 0:
            self.pulse('j')                     # 绿宝石水花：后车减速两秒，躲过每 8 秒一次的撞击
            return
        if self.mini_lanes(q, ('ArrowUp', 'ArrowDown'), False):
            self.page.wait_for_timeout(60)

    # ------------------------------------------------------------------ 战斗
    def ranged_moves(self):
        if self._ranged is None:
            self._ranged = self.page.evaluate('''() => Object.fromEntries(Object.entries(G.MOVES).map(([k, m]) =>
              [k, !!(m && (m.melee === false || m.shot || m.fireAt || m.diveAlongPath))]))''') or {}
        return self._ranged

    def defend(self, s, force_guard=False):
        """debug.js 的 hitIn 修正后（预警剩余 + 剩下的前摇）父类会在“预警结束”那一刻闪避 / 格挡；对远程招式那只是出手，
        弹体还在 100–160 px 外，闪避的无敌帧在弹体到之前就结束了（主代理在序章火球一步碰到）。这里：近战招式照父类按 hitIn
        反应；远程 / 俯冲招式不看 hitIn，只按场上弹体的距离反应（44 px 内、正在靠近）——面朝来向就按住 L，否则上下闪避。"""
        ranged = self.ranged_moves()
        melee_only = dict(s, enemies=[e for e in s.get('enemies') or [] if not (e[10] and ranged.get(e[10]))], shots=[])
        if super().defend(melee_only, force_guard):
            return True
        now = time.monotonic()
        if now < self.next_defense:
            return False
        for sh in s.get('shots') or []:
            dx, dy, vx, side = sh[0], sh[1], sh[2], sh[3]
            if side not in ('enemy', None) or abs(dy) >= 12 or abs(dx) >= 44 or dx * vx > 0:
                continue
            fid = s.get('fightId')
            self.defenses[fid] = self.defenses.get(fid, 0) + 1
            toward = 1 if dx > 0 else -1
            if s.get('pfacing') == toward or abs(dx) < 10:
                self.hold(['l'])
                self.guard_until = now + .3
                self.next_defense = now + .4
            else:
                self.hold(['ArrowUp' if s['py'] > 162 else 'ArrowDown'])
                self.pulse('k')
                self.next_defense = now + .3
            return True
        return False

    def losing(self, s):
        fid = s.get('fightId')
        return self.args.lose and s.get('fightLosable') and self.loses.get(fid, 0) < 1

    def fight(self, s):
        fid = s.get('fightId') or ''
        if self.losing(s):
            self.hold()
            return
        if fid.startswith('b22_prophecy'):
            return self.prophecy(s, int(fid[-1]) - 1)
        if fid in ('b23a_petshop', 'b23b_petshop'):
            return self.petshop(s)
        if fid == 'b26b_cream':
            return self.cream_hidden(s)
        if fid == 'b26c_sunlight':
            return self.cream_sun(s)
        if fid.startswith('b28d'):
            return self.dio(s, int(fid[4]))
        return super().fight(s)

    def face(self, s, facing):
        if s.get('pfacing') != facing:
            self.hold()
            self.pulse('ArrowRight' if facing > 0 else 'ArrowLeft', .012)
            return False
        return True

    def prophecy(self, s, idx):
        d = (s.get('fx2') or {}).get('data') or {}
        px = s['px']
        if self.defend(s):
            return
        if idx == 0 and not d.get('rotated'):
            if abs(px - 410) > 14:
                self.move(s, 410, 162, 4)
            else:
                self.hold()
                self.pulse('e')
                self.page.wait_for_timeout(120)
            return
        if idx == 1 and not d.get('oil'):
            drum = d.get('drumX') or 520
            if not (6 <= drum - px <= 28):
                self.move(s, drum - 18, 162, 3)
            else:
                self.hold()
                self.pulse('e')
                self.page.wait_for_timeout(160)
            return
        if idx == 2:
            # 他保持离玩家 65 px：玩家站 x≈578，他会停在发光路口（638 ± 35）
            if abs(px - 578) > 6 or abs(s['py'] - 162) > 4:
                self.move(s, 578, 162, 3)
                return
        # 等预言兑现；顺手向荷尔·荷斯出几拳（打不动他，练连打 / 保持面朝子弹来向）
        boss = next((e for e in s.get('enemies') or [] if e[13]), None)
        if boss:
            self.face(s, 1 if boss[1] > px else -1)
        self.hold()

    def petshop(self, s):
        f2 = s.get('fx2') or {}
        e, pinfo = f2.get('e'), f2.get('p') or {}
        fid = s.get('fightId')
        mem = self.mechanic.setdefault(fid, {})
        px, py = s['px'], s['py']
        if not e:
            self.hold()
            return
        rad = 8 + (pinfo.get('bodyW') or 6)
        if e.get('dash') and e.get('atkId') == 'PS_DIVE':
            key = json.dumps(e['dash']['pts'])
            if mem.get('parried') != key:
                side = 1 if e['dash']['pts'][0][0] >= px else -1
                if self.tight_parry(rad, side):
                    mem['parried'] = key
                    mem['parries'] = mem.get('parries', 0) + 1
                    self.shot(f'{fid}_parry_{mem["parries"]}')
            self.hold()
            return
        if e.get('tele') and e['tele'].get('move') == 'PS_DIVE':
            self.hold()
            self.face(s, 1 if e['x'] >= px else -1)
            return
        if self.defend(s):
            return
        # 站位：离墙、离冰墙远一点；下水道避开水面（y > 168）和冻住 / 将要冻住的平台
        arena = (300, 700) if fid == 'b23a_petshop' else (20, 610)
        frozen = (f2.get('data') or {}).get('frozen') or []
        warn_x = (f2.get('data') or {}).get('warningX')
        bad = [x for x in frozen] + ([warn_x] if warn_x is not None else [])
        want_x = max(arena[0] + 60, min(arena[1] - 60, e['x'] + (-70 if e['x'] > (arena[0] + arena[1]) / 2 else 70)))
        for _ in range(8):
            if any(x - 6 <= want_x <= x + 51 for x in bad):
                want_x += 56 if want_x < (arena[0] + arena[1]) / 2 else -56
        if abs(px - want_x) > 18 or abs(py - 160) > 4:
            self.move(s, want_x, 160, 4)
            return
        self.hold()
        self.face(s, 1 if e['x'] >= px else -1)

    def tight_parry(self, rad, side):
        """俯冲已经起飞：高频读位置，预计 ≈0.09 s 后撞上时新按下 L（伊奇这一战精准格挡窗口 8 帧）。"""
        until = time.monotonic() + 3.0
        while time.monotonic() < until:
            info = self.page.evaluate(DASH_JS)
            if not info:
                return False
            tc = contact_time(info['dash'], info['px'], info['py'], 8 + info['bodyW'])
            if tc is None:
                if info['dash']['t'] >= info['dash']['dur'] - 1e-3:
                    return False
                self.page.wait_for_timeout(10)
                continue
            if info['facing'] != side and tc > .12:
                self.pulse('ArrowRight' if side > 0 else 'ArrowLeft', .01)
                continue
            if tc <= .095:
                self.pulse('l', .02)
                self.marks.append([self.elapsed(), 'parry_press tc=%.3f' % tc, 'mechanic'])
                return True
            self.page.wait_for_timeout(6)
        return False

    def cream_hidden(self, s):
        f2 = s.get('fx2') or {}
        d, e = f2.get('data') or {}, f2.get('e') or {}
        px, py = s['px'], s['py']
        phase = d.get('phase')
        ex, ey = e.get('x', 160), e.get('y', 160)
        walk = s.get('walkY') or [148, 174]
        mid = (walk[0] + walk[1]) / 2
        if s.get('playerAtk') or s.get('playerRush'):
            if phase == 'expose':
                self.attack(s)
                return
        if phase == 'expose':
            full = (s.get('energy') or 0) >= (s.get('energyMax') or 100)
            if full:
                self.hold()
                self.pulse('u')
                return
            dx = ex - px
            if abs(ey - py) > 5 or abs(dx) > 52:
                self.move(s, ex - (28 if dx > 0 else -28), ey, 3)
                return
            if self.face(s, 1 if dx >= 0 else -1):
                self.attack(s)
            return
        if phase == 'dash':
            vx = d.get('vx') or 0
            ty = d.get('targetY', ey)
            ahead = (px - ex) * (1 if vx > 0 else -1)          # 玩家在虚空前方多远
            band = abs(py - ey) < 14 or abs(py - ty) < 14
            if band and -10 <= ahead <= 16 + abs(vx) * .14 and not s.get('dodgeCd'):
                up = ty >= mid
                self.hold(['ArrowUp' if up else 'ArrowDown'])
                self.pulse('k')
                self.marks.append([self.elapsed(), 'void_dodge ahead=%d' % ahead, 'mechanic'])
                self.hold()
                return
            if band and ahead > 0:
                self.move(s, px, walk[0] if ty >= mid else walk[1], 1)
                return
            self.hold()
            return
        # warn / 其他：和虚空保持横向距离，回到中线（冲刺开始后再上下让开）
        if abs(px - ex) < 90:
            away = px - (60 if ex > px else -60)
            away = max(30, min(290, away))
            if abs(away - px) < 8:                             # 墙边退不开：换到另一边
                away = ex + (100 if px < ex else -100)
            self.move(s, away, mid, 3)
            return
        if abs(py - mid) > 3:
            self.move(s, px, mid, 2)
            return
        self.hold()

    def cream_sun(self, s):
        d = (s.get('fx2') or {}).get('data') or {}
        if not d.get('beam'):
            return super().fight(s)
        if s.get('storyU'):
            self.hold()
            self.pulse('u')
            self.page.wait_for_timeout(120)
            return
        if self.defend(s):
            return
        px = s['px']
        if abs(px - 238) > 8 or abs(s['py'] - 160) > 4:
            self.move(s, 238, 160, 3)
            return
        boss = next((e for e in s.get('enemies') or [] if e[13]), None)
        if boss and abs(boss[1] - px) < 40 and boss[1] < px:
            # 他在左边：从他左侧 J3 把他往光柱推
            self.move(s, boss[1] - 26, boss[2], 3)
            return
        self.hold()
        if boss:
            self.face(s, 1 if boss[1] > px else -1)

    def dio(self, s, phase):
        f2 = s.get('fx2') or {}
        ts, pinfo, d, e = f2.get('ts'), f2.get('p') or {}, f2.get('data') or {}, f2.get('e') or {}
        mem = self.mechanic.setdefault(s.get('fightId'), {})
        px = s['px']
        toward = (['ArrowRight'] if e and e.get('x', px) > px else ['ArrowLeft']) if e else []
        # DIO 的时停：预警（黄光、反向镲）里按住 L，burst 第一帧还按着 → 这次排队伤害 ×0.3；停止中一直按着
        #   （冻住时输入不生效，解冻那一刻就在格挡）；第二段的刀阵在恢复时飞来，判定按 DIO 的位置算正面 → 面朝 DIO 按住 L 全挡
        if ts and ts.get('by') == 'dio':
            ph = ts.get('phase')
            if ph == 'stopped' and pinfo.get('immune'):
                if phase == 2 and not mem.get('deflected_' + str(d.get('stops'))):
                    mem['deflected_' + str(d.get('stops'))] = True
                    self.hold()
                    self.pulse('j')               # 半秒里打掉一面飞刀
                    self.marks.append([self.elapsed(), 'knife_deflect', 'mechanic'])
                    return
                if e and abs(e.get('x', 0) - px) < 60:
                    if self.face(s, 1 if e['x'] >= px else -1):
                        self.attack(s)
                    return
            self.hold(['l'] + toward)
            return
        if ts and ts.get('phase') in ('burst', 'stopped'):
            self.hold()
            return
        # 第二段：HP 低于 35% 或 DIO 只剩 1 HP 时按住 L + K 三秒装死
        if phase == 2 and not d.get('playDead') and e:
            low = (s.get('hp') or 0) < .35 * (s.get('maxHp') or 1)
            if low or (e.get('hp') or 9) <= 1:
                self.hold(['l', 'k'])
                if 'play_dead_hold' not in self.special:
                    self.special['play_dead_hold'] = True
                    self.page.wait_for_timeout(1500)
                    self.shot('b28d2_play_dead_hold')
                return
        if phase == 3 and s.get('storyU'):
            self.hold()
            self.pulse('u')
            self.next_attack = time.monotonic() + .2
            return
        return super().fight(s)

    # ------------------------------------------------------------------ 失败菜单：连输两次就选「放水再来」（玩家可选项）
    def loss_menu(self, s):
        fid = s.get('fightId') or self.last_fight
        items = s.get('menuItems') or []
        if fid in self.fights and '再来一次' in items:
            self.page.wait_for_timeout(260)
            s = self.st()
            items = s.get('menuItems') or []
        if fid in self.fights and '放水再来' in items and self.loses.get(fid, 0) >= 2 and not self.args.lose:
            self.hold()
            self.loses[fid] = self.loses.get(fid, 0) + 1
            self.shot(fid + '_lost_' + str(self.loses[fid]))
            self.note('assist_chosen', fight=fid)
            self.menu('放水再来')
            return True
        return super().loss_menu(s)

    # ------------------------------------------------------------------ 自由走动：队友的告别对白按 E（站着等他们走近），不追着跑
    def explore(self, s):
        names = {NAMES.get(a[0]) for a in s.get('party') or []}
        near = s.get('near')
        if near in names and near not in self.talked and s.get('stage') == 'airport_fin':
            self.talked.add(near)
            self.hold()
            self.pulse('e')
            return
        if s.get('stage') == 'airport_fin' and len(self.talked) < 2 and not self.special.get('airport_wait'):
            self.special['airport_wait'] = True
            self.hold()
            self.page.wait_for_timeout(1500)
            return
        done = {t[1] for t in self.explored.get(s.get('stage'), set()) if t[0] == 'u'}
        hots = [[h[0], h[1], h[2], [] if h[0] in done else h[3]] for h in s.get('hotspots') or []]
        s = dict(s, npcs=[n for n in s.get('npcs') or [] if n[0] not in names], hotspots=hots)
        return super().explore(s)

    # ------------------------------------------------------------------ 验收
    def validate(self):
        keep = self.coverage
        self.coverage = {k: v for k, v in keep.items() if k not in NO_RUSH_COVERAGE}
        try:
            super().validate()
        finally:
            self.coverage = keep
        for fid in NO_RUSH_COVERAGE & set(keep):
            c = keep[fid]
            self.check(c.get('dodge', 0) + c.get('guard', 0) + c.get('parry', 0) >= 1, 'coverage_defense', fight=fid, counts=c)
        fps = [r[1] for r in self.fps_log if r[1]]
        if fps:
            self.check(min(fps) >= 55, 'fps_sample_below_55', low=[r for r in self.fps_log if r[1] and r[1] < 55][:10])
        # 动作回退（图集里没有这个动作、画成了别的）父类不查：后段新动作多，这里一并要求为空
        self.check(not self.last_s.get('fallbacks'), 'anim_fallbacks', items=self.last_s.get('fallbacks'))

    def report(self):
        fps = [r[1] for r in self.fps_log if r[1]]
        return {**super().report(), 'late_visual_contract': self.special, 'fps_log': self.fps_log,
                'fps_summary': {'samples': len(fps), 'min': min(fps) if fps else None, 'avg': round(sum(fps) / len(fps), 1) if fps else None},
                'input_boundary': '所有推进、移动、攻击、QTE、选项、失败重试均走真实键盘；只读 snapshot、G.lateGame 和战斗公开状态。'}


if __name__ == '__main__':
    playtest.Tester = LateTester
    raise SystemExit(playtest.main())
