"""第2章（南海）、第3章（新加坡）真实键盘路线验收：从「选择章节」进章，一路打到章末菜单（「第N章 … 完」）。

和 test_ch1.py 一样只读 G.dbg.snapshot() 和公开的战斗状态，所有推进、移动、攻击、QTE、选项、失败重试都走真实键盘：
- 关键剧情台词出现时截图（人工看构图、遮挡、站位）；每张自由走动地图进来 1.5 s 后截一张（看提示、箭头、NPC）。
- --lose：每场可失败的战斗故意输一次再来；每章第一场可失败的战斗输两次，第二次输后断言菜单里有「放水再来」（仍选「再来一次」）。

用法：python -B tools\\dev\\full\\test_mid_early.py ch2 --out tools\\_playtest\\early_ch2 [--lose]
      python -B tools\\dev\\full\\test_mid_early.py ch3 --out tools\\_playtest\\early_ch3 [--lose]
"""
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
GAME = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(GAME / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import playtest
import ra_common

NAMES = {'jotaro': '承太郎', 'joseph': '乔瑟夫', 'avdol': '阿布德尔', 'kakyoin': '花京院', 'polnareff': '波鲁纳雷夫', 'iggy': '伊奇', 'anne': '安妮'}
STORY_SHOTS = {
    # 第2章（2026-10-10 晚重做后的台词）
    '甲板上禁止吸烟。……把烟掐了': 'captain_intro', '谁要被你们关起来': 'anne_found', '这片海有鲨鱼': 'shark', '鲨鱼冲过来了': 'shark_qte',
    '我要去新加坡，找我爸爸': 'anne_join', '我叫安妮': 'anne_name', '滤嘴上有很深的牙印': 'clue_cigarette', '绑着电线，在滴答响': 'clue_hatch',
    '你摸了鼻子': 'captain_caught', '这丫头就去喂鲨鱼': 'hostage', '我接住她了': 'anne_saved', '承太郎被拖下去了': 'dragged',
    '我的暗蓝之月': 'captain_ko', '是炸弹！': 'bomb', '这次可不算我的': 'explosion', '我爸爸在新加坡': 'drift_night',
    '像是在等我们': 'freighter_fog', '它在看报纸': 'ape_cage', '刚才还在吊车下面': 'sailor_gone', '这艘船……就是替身': 'strength_reveal',
    '替身使者是你吗': 'hold_intro', '船……变小了': 'freighter_end', '这回总该能到新加坡了': 'ch2_end',
    # 第3章（2026-10-11 重做后的台词）
    '终于踩到不晃的地面了': 'arrival', '你的护照呢': 'police', '我要单人间': 'hotel_single', '先把房间检查一遍': 'hotel_room',
    '冰箱门，自己开了': 'fridge_open', '想不到我会在冰箱里吧': 'devo_appear', '恨够了': 'devo_doll', '再也没有醒来': 'devo_end',
    '这房间是被台风刮过吗': 'devo_after', '第六天，早上': 'morning', '……吃完了': 'fake_cherry', '连核一起嚼得': 'clue_cherry',
    '生命之火……是两层的': 'clue_life', '影子，边缘在蠕动': 'clue_shadow', '那我们去买票了': 'split', '海是绿色的': 'cable_in',
    '你不是花京院': 'yellow_reveal', '真正的花京院，这会儿': 'yellow_name', '你的拳头……只会被我吃掉': 'yellow_vs',
    '我投降': 'rubbersoul_beg', '两只手，都是右手': 'jgeil_hint', '两只右手？': 'pol_shock', '再陪你们一段': 'anne_stays',
    'rerorero': 'rero', '这是我的自由': 'ch3_end',
}
LOSE_TWICE = {'b03_darkbluemoon', 'b05_devo'}   # 每章第一场可失败的战斗：输两次，验「放水再来」


MOVE_KINDS_JS = """() => { const r = { ranged: [], dash: [] };
  for (const [k, m] of Object.entries(G.MOVES || {})) { if (m.shot && m.melee === false) r.ranged.push(k); if (m.dash || m.diveAlongPath) r.dash.push(k); }
  return r; }"""


class EarlyTester(playtest.Tester):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.special, self.fight_t0, self.fight_secs, self.assist_seen = {}, {}, {}, {}
        self.kinds = None

    def defend(self, s, force_guard=False):
        """父类在预警结束那一刻闪 / 挡（debug.js 的 teleLeft 修正以后算得准了）：近战没问题，但飞行道具这时才刚出手、
        还在 100–160 px 外，闪避的无敌帧在弹到之前就结束了。这里飞行道具改看弹体距离（< 40 px 且朝自己飞），
        冲刺招等他真的冲到 70 px 内再上下闪；近战照父类。"""
        if self.kinds is None:
            self.kinds = self.page.evaluate(MOVE_KINDS_JS) or {'ranged': [], 'dash': []}
        ranged, dash = set(self.kinds['ranged']), set(self.kinds['dash'])
        now = time.monotonic()
        if now < self.guard_until:
            self.hold(['l'])
            return True
        if now < self.next_defense:
            return False
        px, py = s['px'], s['py']
        for shot in s.get('shots') or []:
            if shot[3] == 'enemy' and abs(shot[0]) < 40 and abs(shot[1]) < 10 and shot[0] * shot[2] < 0:
                self.defenses[s.get('fightId')] = n = self.defenses.get(s.get('fightId'), 0) + 1
                if force_guard or n % 2:
                    self.hold(['l'])
                    self.guard_until, self.next_defense = now + .3, now + .45
                else:
                    self.hold(['ArrowUp' if py > 160 else 'ArrowDown'])
                    self.pulse('k')
                    self.next_defense = now + .3
                return True
        for e in s.get('enemies') or []:
            if e[6] == 'attack' and e[10] is None and abs(e[1] - px) < 70 and abs(e[2] - py) < 14 and getattr(self, '_dash_of', {}).get(e[17]) in dash:
                if not s.get('dodgeCd'):
                    self.hold(['ArrowUp' if py > 160 else 'ArrowDown'])
                    self.pulse('k')
                    self.next_defense = now + .3
                    return True
        self._dash_of = getattr(self, '_dash_of', {})
        for e in s.get('enemies') or []:
            if e[10]:
                self._dash_of[e[17]] = e[10]
        melee = [e for e in s.get('enemies') or [] if not e[10] or (e[10] not in ranged and e[10] not in dash)]
        return super().defend(dict(s, enemies=melee, shots=[]), force_guard)

    # QTE 后的确认键保护检查：每按一下前先读确认锁还剩多久，剩不到 0.12 s 就停（见 ra_common.qte_guard 的说明；
    #   父类按墙钟连按 0.5 s，测试读状态慢一点就会按到锁过期以后，误报 qte_dialog_skipped）
    def qte_guard(self, s):
        return ra_common.qte_guard(self, s)

    def st(self):
        s = super().st()
        stage, fid = s.get('stage'), s.get('fightId')
        text = (s.get('dlg') or '') + (s.get('narr') or '')
        for key, name in STORY_SHOTS.items():
            if getattr(self, '_guarding', False):
                break
            if key in text and name not in self.special:
                self.special[name] = True
                self.page.wait_for_timeout(260)   # 对话框弹出动画放完再截
                self.shot('story_' + name)
        if s.get('free') and not s.get('busy') and stage and ('free_' + stage) not in self.special:
            first = self.special.setdefault('free_at_' + stage, time.monotonic())
            if time.monotonic() - first > 1.5:
                self.special['free_' + stage] = True
                self.shot('free_' + stage)
        if fid and s.get('combat'):
            self.fight_t0.setdefault(fid, self.elapsed())
            self.fight_secs[fid] = round(self.elapsed() - self.fight_t0[fid], 1)
            h = s.get('fightHint') or {}
            tag = None
            if fid == 'b03_darkbluemoon':
                tag = 'vortex' if h.get('vortex') else 'starwin' if h.get('starWindow') else None
            elif fid == 'b04_strength':
                tag = f"eyes{h.get('eyes', 0)}"
            elif fid == 'b05_devo':
                tag = f"wave{h.get('phase', 0)}" + ('_hidden' if h.get('hidden') else '')
            elif fid == 'b06_yellowtemperance':
                tag = 'water' if h.get('water') else f"slime{min(3, int(h.get('slime') or 0))}"
            if tag:
                self.shot(f'{fid}_a{self.loses.get(fid, 0)}_{tag}')
        return s

    # 跟随的队友 / 安妮也挂了搭话，追着他们按 E 会原地打转；自由走动只找固定的 NPC 和调查点。
    # 任何一位队长 U 过的调查点就算做过（父类按“调查点 + 队长”记，换了队长又会回头再查）。
    def explore(self, s):
        names = {NAMES.get(a[0]) for a in s.get('party') or []} | {'安妮'}
        done = {t[1] for t in self.explored.get(s.get('stage'), set()) if t[0] == 'u'}
        hots = [[h[0], h[1], h[2], [] if h[0] in done else h[3]] for h in s.get('hotspots') or []]
        s = dict(s, npcs=[n for n in s.get('npcs') or [] if n[0] not in names], hotspots=hots)
        return super().explore(s)

    def loss_menu(self, s):
        fid = s.get('fightId') or self.last_fight
        if fid in self.fights and '再来一次' in (s.get('menuItems') or []):
            self.page.wait_for_timeout(260)   # 失败菜单有 0.12 s 弹出动画
            s = self.st()
            n = self.loses.get(fid, 0) + 1
            if n >= 2:
                self.assist_seen[fid] = any('放水再来' in (x or '') for x in s.get('menuItems') or [])
                self.check(self.assist_seen[fid], 'assist_menu_missing', fight=fid, items=s.get('menuItems'))
        return super().loss_menu(s)

    def fight(self, s):
        fid = s.get('fightId')
        if self.args.lose and s.get('fightLosable'):
            need = 2 if fid in LOSE_TWICE else 1
            if self.loses.get(fid, 0) < need:
                self.hold()
                return
        return super().fight(dict(s, fightLosable=False) if self.args.lose else s)

    def validate(self):
        super().validate()
        if self.args.lose:
            for fid in LOSE_TWICE & set(self.fights):
                self.check(self.loses.get(fid, 0) >= 2, 'lose_twice_missing', fight=fid)

    def report(self):
        return {**super().report(), 'early_visual_contract': self.special, 'fight_seconds': self.fight_secs,
                'assist_seen': self.assist_seen,
                'input_boundary': '所有推进、移动、攻击、QTE、选项、失败重试均走真实键盘；只读 snapshot 和公开战斗状态。'}


if __name__ == '__main__':
    playtest.Tester = EarlyTester
    raise SystemExit(playtest.main())
