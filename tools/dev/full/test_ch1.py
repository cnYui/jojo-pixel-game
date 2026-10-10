"""第1章真实键盘路线验收，记录坐姿、毛毯、漂浮、雕像和失败重试证据。

灰塔段 B 的打法只读快照里公开的信息（红线预警的起点 / 控制点 / 终点、Boss 是否被缠住、能量），
动作全部经键盘：红线出现 → 走到灰塔旁边、面朝它连按三下 J 铺网；缠住 → 对准连按 J，能量满按 U。
"""
from pathlib import Path
import math
import random
import sys
import time

sys.dont_write_bytecode = True
GAME = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(GAME / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import playtest
import ra_common

NAMES = {'jotaro': '承太郎', 'joseph': '乔瑟夫', 'avdol': '阿布德尔', 'kakyoin': '花京院', 'polnareff': '波鲁纳雷夫', 'iggy': '伊奇'}
# 关键剧情画面：对白里出现这些字时截一张，人工逐张看构图 / 道具 / 人物是否出画
STORY_SHOTS = {'不是普通的虫子': 'tg_intro', '连白金之星都抓不住': 'tg_card', '飞机在往下掉': 'cabin_masks', '被灰塔下了手': 'cockpit',
               '人生第三次坠机': 'sea_float', '有渔船': 'sea_boat', '能帮我看看菜单吗': 'pol_enter', '青蛙': 'dishes', '剑术天下第一': 'coin_trick',
               '火焰时钟': 'fire_clock', '来吧，占卜师': 'garden_duel', '从……地底下': 'pol_char', 'YES I AM': 'yes_i_am', '额头上': 'bud',
               '两只手都是右手': 'sherry', '这把剑，借给你们': 'pol_join', '驶向新加坡': 'ending'}
KAK_SPEED = 66          # 花京院走速 px/s
NET_DELAY = 0.5         # 连按三下 J 到第三下铺出网的时间（8 + 8 + 9 f ≈ 0.42 s，留余量）
DIVE_SPEED = 300        # 灰塔俯冲 px/s
REACT = 0.2             # 银色战车：看到预警（「！」/ 红线）以后多久才反应——按普通玩家的反应时间打，不读帧
RNG = random.Random(20261009)
LOSE_TWICE = {'b1b_towergray'}   # --lose：这一场输两次，第二次输后菜单要有「放水再来」
# 银色战车当前招式的公开进度（出招计时、最后一段判定的结束时刻）：测试只读，用来决定什么时候松开 L 还手
CHARIOT_JS = """() => { const f = G.world.fight, b = f && f.boss; if (!b) return null; const m = b.atk;
  return { atk: b.atkId || null, atkT: b.atkT || 0, lastHit: m ? (m.windows ? m.windows[m.windows.length - 1][1] : m.active[1]) : 0 }; }"""


def bezier(p0, p1, p2, t):
    v = 1 - t
    return (v * v * p0[0] + 2 * v * t * p1[0] + t * t * p2[0], v * v * p0[1] + 2 * v * t * p1[1] + t * t * p2[1])


class Ch1Tester(playtest.Tester):
    def st(self):
        s = super().st()
        self.special = getattr(self, 'special', {})
        stage = s.get('stage')
        data = self.page.evaluate("""() => (G.world.stage ? G.world.stage.actors : []).map(a=>({id:a.id,cid:a.cid,anim:a.anim,
            hold:a.hold,frozen:a.frozen,remove:a.remove,hp:a.hp,maxHp:a.maxHp,z:a.z}))""")
        if stage == 'plane_ch1' and 'seated' not in self.special:
            seats = [a for a in data if str(a.get('id', '')).startswith('passenger')]
            if len(seats) == 8:
                self.special['seated'] = seats
                self.shot('passengers_seated')
        if s.get('flags', {}).get('blanket') and 'blanket' not in self.special:
            self.special['blanket'] = True
            self.shot('blanket_reach')
        if stage == 'sea_ch1' and 'float' not in self.special:
            crew = [a for a in data if a.get('cid') in ('jotaro', 'joseph', 'avdol', 'kakyoin')]
            if len(crew) == 4 and all(a.get('anim') == 'float' for a in crew):
                self.special['float'] = crew
                self.shot('crew_float')
        text = (s.get('dlg') or '') + (s.get('narr') or '')
        for key, name in STORY_SHOTS.items():
            if getattr(self, '_guarding', False):   # QTE 后的确认锁检查期间不截剧情图（截图要等弹出动画）
                break
            if key in text and name not in self.special:
                self.special[name] = True
                self.page.wait_for_timeout(260)   # 对话框弹出动画放完再截
                self.shot('story_' + name)
        # 每张自由走动地图进来 1.5 s 后截一张（看去向箭头、道具、人物站位）
        if s.get('free') and not s.get('busy') and stage and ('free_' + stage) not in self.special:
            first = self.special.setdefault('free_at_' + stage, time.monotonic())
            if time.monotonic() - first > 1.5:
                self.special['free_' + stage] = True
                self.shot('free_' + stage)
        statue = next((a for a in data if a.get('id') == 'mr_statue'), None)
        if statue:
            key = 'statue_' + str(statue.get('frozen'))
            if key not in self.special:
                self.special[key] = statue
                self.shot(key)
        # 灰塔段 B：第一次缠住、第一次红线各截一张，便于人工看机制是否看得懂
        fid = s.get('fightId')
        if fid == 'b1b_towergray' and s.get('combat'):
            hint = s.get('fightHint') or {}
            if hint.get('rooted') and 'tg_rooted' not in self.special:
                self.special['tg_rooted'] = True
                self.shot('b1b_towergray_rooted')
            if any(w[0] == 'W4' for w in s.get('warns') or []) and 'tg_line' not in self.special:
                self.special['tg_line'] = True
                self.shot('b1b_towergray_redline')
            n = int((s.get('fightT') or 0) // 8)
            if 1 <= n <= 6:
                self.shot(f'b1b_towergray_a{self.loses.get(fid, 0)}_t{n * 8}')
        return s

    # QTE 后的确认键保护检查：每按一下前先读确认锁还剩多久（ra_common.qte_guard）
    def qte_guard(self, s):
        return ra_common.qte_guard(self, s)

    # 跟随的队友也挂了搭话，追着他们按 E 会原地打转；自由走动时只找固定的 NPC 和调查点
    def explore(self, s):
        names = {NAMES.get(a[0]) for a in s.get('party') or []}
        # 父类按“(调查点, 队长)”记已调查：换了队长，别的调查点又算没做，会在两个需要不同队长的点之间来回换人。
        # 任何一位队长 U 过的调查点就当作完成（仍保留 E 交互）。
        done = {t[1] for t in self.explored.get(s.get('stage'), set()) if t[0] == 'u'}
        hots = [[h[0], h[1], h[2], [] if h[0] in done else h[3]] for h in s.get('hotspots') or []]
        s = dict(s, npcs=[n for n in s.get('npcs') or [] if n[0] not in names], hotspots=hots)
        if s.get('stage') == 'plane_ch1':
            flags = s.get('flags', {})
            if not flags.get('blanket'):
                if s.get('leader') != 'kakyoin':
                    self.switch_leader(s, 'kakyoin')
                elif self.move(s, 192, 140, 4):
                    self.hold()
                    self.pulse('u')
                    self.investigated.setdefault(1, set()).add('kakyoin')
                return
            if not flags.get('sensed'):
                if s.get('leader') != 'avdol':
                    self.switch_leader(s, 'avdol')
                elif self.move(s, 250, 160, 4):
                    self.hold()
                    self.pulse('u')
                    self.investigated.setdefault(1, set()).add('avdol')
                return
            if (flags.get('planeTalk') or 0) < 3:
                if s.get('leader') != 'jotaro':
                    self.switch_leader(s, 'jotaro')
                elif self.move(s, 300, 140, 4):
                    self.hold()
                    self.pulse('u')
                    self.investigated.setdefault(1, set()).add('jotaro')
                return
        return super().explore(s)

    # 失败菜单有 0.12 s 弹出动画，立刻截图只会拍到空框；等动画放完再截。
    # 第二次输（LOSE_TWICE 那一场）时菜单里要有「放水再来」（仍选「再来一次」）
    def loss_menu(self, s):
        fid = s.get('fightId') or self.last_fight
        if fid in self.fights and '再来一次' in (s.get('menuItems') or []):
            self.page.wait_for_timeout(260)
            s = self.st()
            n = self.loses.get(fid, 0) + 1
            items = s.get('menuItems') or []
            self.assist_seen = getattr(self, 'assist_seen', {})
            self.assist_seen.setdefault(fid, []).append(any('放水再来' in (x or '') for x in items))
            if n >= 2:
                self.check(self.assist_seen[fid][-1], 'assist_menu_missing', fight=fid, items=items)
            else:
                self.check(not self.assist_seen[fid][-1], 'assist_menu_too_early', fight=fid, items=items)
        return super().loss_menu(s)

    def fight(self, s):
        fid = s.get('fightId')
        if self.args.lose and s.get('fightLosable'):
            need = 2 if fid in LOSE_TWICE else 1
            if self.loses.get(fid, 0) < need:   # 故意输：站着不动
                self.hold()
                return
        if fid == 'b1b_towergray':
            return self.towergray(s)
        if fid == 'b02_chariot':
            return self.chariot(s)
        return super().fight(dict(s, fightLosable=False) if self.args.lose else s)

    def chariot(self, s):
        """银色战车，按“普通玩家”的打法（每个预警晚 REACT 秒才反应）：
        架剑（光弧 / 银边）时站在 55–120 px 按住 L 再按 J 放地火；他头上冒「！」时贴身来得及就打断，来不及就在第一刺前
        新按下 L（弹反机会，弹不到也在格挡），挡到第三刺结束马上松开还手；红线（突进刺）上下让开，他冲过头收招时贴上去打；
        他挨打 / 被弹开 / 卡住（open）时连按 J 打满三下接连打。阶段 2 站到石像左边引他刺石像；阶段 3 只打真身；
        阶段 4 地火 + 弹反攒能量，满了按 U。全部经键盘；只读快照和 Boss 的公开状态（预警剩余、出招进度）。"""
        mem = self.mechanic.setdefault('b02_chariot', {})
        b = next((e for e in s.get('enemies') or [] if e[13]), None)
        if not b:
            self.hold()
            return
        info = self.page.evaluate(CHARIOT_JS) or {}
        h = s.get('fightHint') or {}
        ph = h.get('phase', 1)
        px, py, now = s['px'], s['py'], time.monotonic()
        bx, by, state = b[1], b[2], b[6]
        dx, dy = bx - px, by - py
        adx, toward = abs(dx), (1 if dx >= 0 else -1)
        tele, left = b[10], (b[7] if b[7] is not None else -1)
        full = (s.get('energy') or 0) >= (s.get('energyMax') or 100)
        atk, atk_t = info.get('atk'), info.get('atkT') or 0
        is_open = bool(h.get('open')) or state in ('hurt', 'broken', 'down')
        key = (tele, b[17]) if tele else None
        if key != mem.get('teleKey'):
            # 普通玩家不是每次都打得断 / 弹得开：每个预警掷一次（固定种子，可复现）——六成试着打断、一半试着弹反，其余直接按住 L 挡
            mem['teleKey'], mem['teleSeen'] = key, now
            mem['tryInterrupt'], mem['tryParry'] = RNG.random() < .6, RNG.random() < .5
        noticed = bool(tele) and now - mem.get('teleSeen', now) >= REACT
        if h.get('statueUsed'):
            mem['statueUsed'] = True
        # 阶段 2：照提示先用石像。石像用掉之前不追击、不放 U，只防守、站到石像左边等他刺进石像——
        #   一套追击（J1–J3 + 连打 ≈ 130）就能把他从 60% 打过 40%，石像诱饵整个被跳过（ra_ch1_r1 就是这样）
        statue_wait = ph == 2 and not mem.get('statueUsed') and bx > 50
        if s.get('playerRush') and not statue_wait:   # 连打中：继续按 J（阶段 2 刚开始、石像还没用：停手去石像那边）
            self.attack(s)
            return
        # 0. 能量满：阶段 4 直接按 U（地底下的十字火焰风暴）；之前只在他挨打 / 收招时放（架剑时安卡会被劈开）
        if full and not statue_wait and (ph >= 4 or (state in ('hurt', 'broken') and adx <= 150)):
            self.hold()
            self.pulse('u')
            return
        # 1. 三连刺 / 横斩的「！」：贴身来得及先打断（J1 6f 出手）；否则第一刺前新按下 L，一直挡到这一招打完
        if tele in ('SC_TRIPLE', 'SC_SLASH') and noticed and adx <= 72 and abs(dy) <= 10:
            if mem.get('tryInterrupt') and left > .14 and adx <= 46 and abs(dy) <= 6 and not s.get('playerAtk') and ph < 4:
                if self.face(s, toward):
                    self.hold()
                    self.pulse('j')
                return
            if not mem.get('tryParry'):
                self.hold(['l'] if s.get('pfacing') == toward else ['ArrowRight' if toward > 0 else 'ArrowLeft'])
                return
            if left <= .07:
                self.hold(['l'])   # 刚按下 = 弹反窗口；没弹到也是格挡（刺穿只漏 30%）
            elif s.get('pfacing') != toward:
                self.hold(['ArrowRight' if toward > 0 else 'ArrowLeft'])   # 先转身（格挡只挡正面）
            else:
                self.hold([])      # 松开 L 等最后一刻再按（一直按住没有弹反）
            return
        if atk in ('SC_TRIPLE', 'SC_SLASH') and adx <= 80 and abs(dy) <= 12:
            last = info.get('lastHit') or 0
            if atk_t < last + .02:
                self.hold(['l'])
                return
            # 第三刺（横斩）打完：收招还有 0.4–0.5 s，松开 L 还手（阶段 2 等石像时不还手，回石像那边）
            if statue_wait:
                self.hold()
            elif self.face(s, toward):
                self.attack(s)
            return
        # 2. 突进刺的红线：上下让开；冲过头收招时贴上去打
        if tele == 'SC_LUNGE' and left >= 0:
            if abs(dy) <= 10:
                up = py > 158
                if left <= .2 and not s.get('dodgeCd'):
                    self.hold(['ArrowUp' if up else 'ArrowDown'])
                    self.pulse('k')
                else:
                    self.move(s, px, py + (-16 if up else 16), 1)
            else:
                self.hold()
            return
        if atk == 'SC_LUNGE' and atk_t >= (info.get('lastHit') or 0) and not statue_wait:
            return self.punish(s, b)
        # 阶段 3 的残像也会出招（伤害减半）：它的「！」快到了就举 L 挡住
        for e in s.get('enemies') or []:
            if not e[13] and e[10] and 0 <= (e[7] or 0) <= .25 and abs(e[1] - px) <= 70 and abs(e[2] - py) <= 10:
                self.hold(['l'])
                return
        # 3. 阶段 2：站到石像（x 44）左边 10 px（金色箭头处），石像挡在中间，等他突进刺进石像；
        #    卡住以后照常追击（is_open）。眼前这一套追击打完再过去（他没挨打、没破绽时才走）
        if statue_wait:
            if self.move(s, 34, by, 2):
                self.face(s, 1)
            return
        # 4. 他挨打 / 被弹开 / 卡住：贴上去连按 J（三连 → 连打）
        if is_open and adx <= 110:
            return self.punish(s, b)
        # 5. 其余时候（多半在架剑）：保持 55–120 px 放地火
        return self.pillar(s, b, mem, now)

    def punish(self, s, b):
        px, py = s['px'], s['py']
        dx, dy = b[1] - px, b[2] - py
        toward = 1 if dx >= 0 else -1
        if s.get('playerAtk') or s.get('playerRush'):
            self.attack(s)
            return
        if abs(dy) > 4:
            self.move(s, px if abs(dx) > 20 else b[1] - toward * 24, b[2], 2)
            return
        if abs(dx) > 40:
            self.move(s, b[1] - toward * 28, b[2], 4)
            return
        if self.face(s, toward):
            self.attack(s)

    def pillar(self, s, b, mem, now):
        px, py = s['px'], s['py']
        dx = b[1] - px
        toward = 1 if dx >= 0 else -1
        if not 55 <= abs(dx) <= 120 or abs(b[2] - py) > 5:
            # 留在自己这一边退到 85 px；退不开（墙角）就闪身穿过他，换到空间大的那边
            side = -toward
            want_x = b[1] + side * 85
            lo, hi = 20, 256
            if (want_x < lo or want_x > hi) and abs(dx) < 55:
                if not s.get('dodgeCd'):
                    self.hold(['ArrowRight' if toward > 0 else 'ArrowLeft'])
                    self.pulse('k')
                return
            self.move(s, max(lo, min(hi, want_x)), b[2], 3)
            return
        if not self.face(s, toward):
            return
        self.hold(['l'])
        if now >= mem.get('pillarAt', 0):
            self.pulse('j')
            mem['pillarAt'] = now + 1.55

    def face(self, s, facing):
        if s.get('pfacing') != facing:
            self.hold(['ArrowRight' if facing > 0 else 'ArrowLeft'])
            return False
        return True

    def towergray(self, s):
        mem = self.mechanic.setdefault('b1b_towergray', {})
        boss = next((e for e in s.get('enemies') or [] if e[13]), None)
        if not boss:
            self.hold()
            return
        px, py = s['px'], s['py']
        walk = s.get('walkY') or [156, 166]
        now = time.monotonic()
        if boss[15] > 0:   # 缠住：掉在过道上，对准连按 J；能量满按 U
            mem.pop('plan', None)
            if (s.get('energy') or 0) >= (s.get('energyMax') or 100) and boss[15] > 0.5:
                self.hold()
                self.pulse('u')
                self.next_attack = now + .2
                return
            side = -1 if px < boss[1] else 1
            want_x = boss[1] + side * 44
            if abs(boss[2] - py) > 2 or abs(want_x - px) > 30:
                self.move(s, want_x, boss[2], 2)
                return
            if self.face(s, 1 if boss[1] > px else -1):
                self.attack(s)
            return
        dives = [w for w in s.get('warns') or [] if w[0] == 'W4' and len(w) >= 9]
        if dives:
            w = dives[0]
            if mem.get('plan_for') != (w[2], w[3], w[4], w[5]):
                mem['plan_for'] = (w[2], w[3], w[4], w[5])
                mem['plan'] = self.plan_net(s, w)
                mem['pressed'] = 0
            plan = mem.get('plan')
            if plan:
                x, y, facing = plan
                if s.get('playerAtk') or s.get('playerRush'):
                    self.attack(s)
                    return
                if not self.move(s, x, y, 3):
                    return
                if self.face(s, facing):
                    self.attack(s)
                return
        mem.pop('plan', None)
        # 针刺：预警剩余 ≤ 0.08 s 时轮流格挡 / 闪避（debug 快照的 hitIn 多加了一次前摇，这里直接读预警剩余时间）
        if boss[10] == 'TG_NEEDLE_B' and 0 <= (boss[7] or 0) <= .08 and abs(boss[1] - px) < 56 and now >= mem.get('defAt', 0):
            mem['defN'] = mem.get('defN', 0) + 1
            mem['defAt'] = now + .4
            if mem['defN'] % 2:
                self.guard_until = now + .3
                self.hold(['l'])
            else:
                self.hold(['ArrowLeft' if boss[1] > px else 'ArrowRight'])
                self.pulse('k')
            return
        if now < self.guard_until:
            self.hold(['l'])
            return
        # 平时：待在灰塔旁边、和它同一条线上，隔一会儿面朝它预铺一张网（它刺过来会撞进网里）。
        # 覆盖检查要求这一战真的格挡 / 闪避过一次：还没有时贴近到 40 px 内等它出针，由 defend() 处理。
        cnt = s.get('counts') or {}
        need_cover = not cnt.get('dodge') or not (cnt.get('guard') or cnt.get('parry'))
        side = -1 if px < boss[1] else 1
        want_x = max(24, min(616, boss[1] + side * (34 if need_cover else 60)))
        if abs(want_x - px) > (12 if need_cover else 40) or abs(160 - py) > 3:
            self.move(s, want_x, 160, 3)
            return
        if need_cover:
            if self.face(s, 1 if boss[1] > px else -1):
                self.hold()
            return
        if now >= mem.get('netAt', 0) and self.face(s, 1 if boss[1] > px else -1):
            self.attack(s)
            if (s.get('playerAtk') or '') == 'J3':
                mem['netAt'] = now + 2.5
            return
        self.hold()

    def plan_net(self, s, w):
        """在红线上挑一个来得及铺网的点：站位离那一点 40 px、面朝它；灰塔预警时停在起点不动，起点最好铺。"""
        px, py = s['px'], s['py']
        walk = s.get('walkY') or [156, 166]
        p0, p2, p1 = (w[2], w[3]), (w[4], w[5]), (w[7], w[8])
        left = w[6] or 0
        pts = [bezier(p0, p1, p2, i / 20) for i in range(21)]
        length = sum(math.dist(pts[i], pts[i + 1]) for i in range(20))
        best = None
        for i, (bx, by) in enumerate(pts[:-2]):
            bug_t = left + (length * i / 20) / DIVE_SPEED
            for facing in (1, -1):
                sx = max(24, min(616, bx - facing * 40))
                sy = max(walk[0], min(walk[1], by))
                if abs(sy - by) > 10:
                    continue
                d = math.hypot(sx - px, (sy - py) * 1.6)
                need = d / KAK_SPEED + NET_DELAY
                ok = need < bug_t
                key = (not ok, d)
                if best is None or key < best[0]:
                    best = (key, (sx, sy, facing))
        return best[1] if best else None

    def validate(self):
        super().validate()
        self.check(len(self.special.get('seated', [])) == 8, 'ch1_seated_missing')
        self.check(bool(self.special.get('blanket')), 'ch1_blanket_missing')
        self.check(len(self.special.get('float', [])) == 4, 'ch1_float_missing')
        self.check('statue_1' in self.special, 'ch1_statue_carved_missing')
        self.check('statue_2' in self.special, 'ch1_statue_broken_missing')
        if self.args.lose:
            for fid in LOSE_TWICE & set(self.fights):
                self.check(self.loses.get(fid, 0) >= 2, 'lose_twice_missing', fight=fid)

    def report(self):
        marks = {m[1]: m[0] for m in self.marks if m[2] == 'fight'}
        return {**super().report(), 'chapter1_visual_contract': getattr(self, 'special', {}),
                'assist_seen': getattr(self, 'assist_seen', {}), 'fight_start': marks,
                'input_boundary': '所有推进、移动、攻击、QTE、失败重试均走真实键盘；只读 snapshot 和 actors。'}


if __name__ == '__main__':
    playtest.Tester = Ch1Tester
    raise SystemExit(playtest.main())
