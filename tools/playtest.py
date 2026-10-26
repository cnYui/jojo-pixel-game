"""用真实键盘试玩入口，核验正常路线、失败重试、教学放宽与闲置保护。"""
from __future__ import annotations

import argparse
import json
import os
import math
from pathlib import Path
import re
import sys
import time
import traceback

STATE_JS = "() => ({...G.dbg.snapshot(),walkY:G.world.stage?[G.world.stage.yMin,G.world.stage.yMax]:null,playerAtk:G.world.player?.atk?.slot||null,playerAtkT:G.world.player?.atkT||0,playerRush:!!G.world.player?.rush,playerCanCancel:!G.world.player?.atk||G.world.player.atkT>=(G.world.player.atk.cancel??G.world.player.atk.active[1])})"
GAME = Path(__file__).resolve().parent.parent
KEYS = {"guard": "l", "dodge": "k", "attack": "j", "special": "u"}
LOOK = {"jotaro": {"detail", "grab"}, "joseph": {"nensha"}, "avdol": {"life"},
        "kakyoin": {"reach", "peek"}, "polnareff": {"cut"}, "iggy": {"scent", "hole"}}
TACTICS = {"b00_avdol_test": "teach", "b01_kakyoin": "kakyoin", "b1a_towergray_jotaro": "fail_segment",
           "b1b_towergray": "towergray", "b02_chariot": "chariot", "b03_darkbluemoon": "darkmoon",
           "b04_strength": "strength", "b05_devo": "devo", "b06_yellowtemperance": "yellow",
           "b07_hangedman": "hanged", "b08_empress": "empress", "b09a_wheelroad": "road",
           "b09b_wheeloffortune": "wheel", "b10_justice": "justice", "b11_lovers": "lovers"}
BAD_NOTES = {"advance_timeout", "fight_timeout", "npc_missing", "npc_not_near", "stuck_investigate"}


def autowin_ids(args):
    """把 --autowin 拆成 id 列表：URL、报告和提示共用同一份解析，避免三处各拆一遍出现偏差。"""
    return [x for x in (getattr(args, "autowin", "") or "").split(",") if x]


def chapter_of(stage):
    m = re.search(r"_(pro|fin|ch\d+[a-z]?)$", stage or "")
    if not m:
        return None
    return 0 if m[1] == "pro" else 12 if m[1] == "fin" else int(re.search(r"\d+", m[1])[0])


def chapter_index(name):
    return 0 if name == "prologue" else 12 if name in ("final", "fin") else int(name[2:])


class Tester:
    def __init__(self, page, args, out):
        self.page, self.args, self.out = page, args, out
        self.started = time.monotonic()
        self.errors, self.notes, self.shots, self.lines = [], [], [], []
        self.trace, self.marks, self.coverage = [], [], {}
        self.taken, self.held = set(), set()
        self.last_stage, self.last_fight, self.last_mark = None, None, None
        self.last_s, self.fights, self.defenses = {}, {}, {}
        self.loses, self.retry_uids, self.relaxed = {}, {}, set()
        self.explored, self.swapped, self.investigated = {}, set(), {}
        self.next_attack, self.next_defense = 0, 0
        self.guard_until = 0
        self.free_since, self.pending_qte, self.qte_seen = None, False, False
        # 自由走动「多久没新进展」的计时器：旧写法用进图时间，进图 40 s 之后每一帧都会把调查清单清空，
        # 一张要走很久的图（第11章游戏室）就永远走不到出口。改成只在「40 s 没有新完成的调查点」时才重来。
        self.last_task_t = 0
        self.hot_try = {}
        # 「直奔出口」每张图最多按 2 次：有的出口要先做完别的事才放行（第1章香港街头「先去大排档」），
        # 无限重按只会反复弹同一句拦路台词、把整章卡死在这张图里
        self.exit_first = {}
        self.fly_input_at, self.idle_started, self.idle_completed = None, None, False
        self.fly_found = False
        self.mem, self.contract_missing = {}, set()
        self.mechanic = {}
        self.next_live = 0

    def elapsed(self):
        return round(time.monotonic() - self.started, 2)

    def note(self, kind, **data):
        row = {"kind": kind, "t": self.elapsed(), **data}
        if row not in self.notes:
            self.notes.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)

    def check(self, ok, kind, **data):
        if not ok:
            self.errors.append({"kind": kind, "t": self.elapsed(), **data})

    def hold(self, keys=()):
        want = set(keys)
        for k in self.held - want:
            self.page.keyboard.up(k)
        for k in want - self.held:
            self.page.keyboard.down(k)
        self.held = want

    def pulse(self, key, gap=0.018):
        if key in self.held:
            self.page.keyboard.up(key)
            self.held.remove(key)
        self.page.keyboard.down(key)
        self.page.wait_for_timeout(gap * 1000)
        self.page.keyboard.up(key)

    def shot(self, name):
        name = re.sub(r'[<>:"/\\|?*]', "_", str(name))
        if self.args.shots_off or name in self.taken:
            return
        self.taken.add(name)
        p = self.out / f"{len(self.shots) + 1:02d}_{name}.png"
        self.page.screenshot(path=str(p))
        self.shots.append(str(p))

    def st(self):
        s = self.page.evaluate(STATE_JS)
        required = ("scene", "stage", "fightId", "fightHint", "fightLosable", "leaderCanInvestigate", "counts", "fps")
        for key in required:
            if key not in s and key not in self.contract_missing:
                self.contract_missing.add(key)
                self.check(False, "snapshot_contract", field=key)
        if s.get("stage") != self.last_stage:
            self.last_stage = s.get("stage")
            # 返回同一张地图时，剧情可能已替换调查点；旧清单不能替玩家跳过新线索。
            self.explored.pop(self.last_stage, None)
            self.trace.append({"t": self.elapsed(), "stage": self.last_stage, "leader": s.get("leader")})
            print(f"[{self.elapsed():.1f}s] 地图 {self.last_stage}", flush=True)
            self.free_since = None
        if s.get("dbgShot") and s["dbgShot"] != self.last_mark:
            self.last_mark = s["dbgShot"]
            self.marks.append([self.elapsed(), self.last_mark, "story"])
            self.shot(self.last_mark)
        for key in ("dlg", "narr", "notice"):
            if s.get(key) and (not self.lines or self.lines[-1] != s[key]):
                self.lines.append(s[key])
        fid = s.get("fightId")
        if fid and s.get("combat"):
            self.fights[fid] = s
            if fid != self.last_fight:
                self.last_fight = fid
                self.marks.append([self.elapsed(), fid, "fight"])
                self.shot(fid + "_start")
            if s.get("fightCoverage"):
                self.coverage[fid] = dict(s.get("counts") or {})
            hint = s.get("fightHint") or {}
            if fid == "b00_avdol_test" and hint.get("relax"):
                self.relaxed.add(hint.get("step"))
        self.last_s = s
        self.fly_found = self.fly_found or bool(s.get("flags", {}).get("flyFound"))
        if self.elapsed() >= self.next_live:
            (self.out / "live.json").write_text(json.dumps({"seconds": self.elapsed(), "state": s,
                "errors": self.errors, "notes": self.notes, "coverage": self.coverage}, ensure_ascii=False, indent=2), encoding="utf-8")
            self.next_live = self.elapsed() + 5
        return s

    def menu(self, label):
        self.hold()
        s = self.st()
        opts = s.get("menuItems") or []
        matches = [i for i, v in enumerate(opts) if label in (v or "")]
        if not matches:
            self.check(False, "menu_item_missing", label=label, options=opts)
            return False
        # 只读当前高亮，操作仍由方向键完成，避免重试菜单的默认项变化影响路线。
        idx = self.page.evaluate("() => G.ui.menu ? G.ui.menu.idx : 0") or 0
        n = matches[0]
        self.page.wait_for_timeout(125)
        key = "ArrowDown" if n >= idx else "ArrowUp"
        for _ in range(abs(n - idx)):
            self.pulse(key)
            self.page.wait_for_timeout(60)
        self.pulse("Enter")
        self.page.wait_for_timeout(180)
        return True

    def enter(self):
        self.page.wait_for_function("() => G.booted && G.ui.menu", timeout=30000)
        self.shot("title")
        self.mem["title"] = self.page.evaluate("() => G.audio.mem()")
        if self.args.chapter in ("prologue", "all"):
            return self.menu("从序章开始")
        if not self.menu("选择章节"):
            return False
        idx = chapter_index(self.args.chapter)
        for _ in range(idx // 5):
            if not self.menu("下一页"):
                return False
        return self.menu("第" + str(idx) + "章" if idx != 12 else "终章")

    def move(self, s, x, y, radius=3):
        keys = []
        # 墙上、船舱顶的互动点按地面范围靠近，角色不能走到绘图锚点的高度。
        if s.get("walkY"):
            y = max(s["walkY"][0], min(s["walkY"][1], y))
        dx, dy = x - s.get("px", x), y - s.get("py", y)
        if abs(dy) > radius:
            keys.append("ArrowDown" if dy > 0 else "ArrowUp")
        if abs(dx) > radius:
            keys.append("ArrowRight" if dx > 0 else "ArrowLeft")
        self.hold(keys)
        return not keys

    def switch_leader(self, s, cid=None):
        party = s.get("party") or []
        cands = [a[0] for a in party if a[6] and a[3] != "down"]
        if len(cands) < 2 or cid == s.get("leader"):
            return False
        self.hold()
        before = s.get("leader")
        for _ in range(len(party)):
            self.pulse("q")
            self.page.wait_for_timeout(240)
            after = self.st()
            if after.get("leader") != before:
                self.check(after["leader"] in cands, "unleadable_selected", leader=after["leader"], party=party)
                self.swapped.add(s.get("stage"))
                if cid is None or after["leader"] == cid:
                    return True
            if not after.get("free") or after.get("busy"):
                return False
        self.check(False, "swap_failed", before=before, target=cid)
        return False

    def qte(self, s):
        q = s.get("qte")
        if not q or q.get("result") is not None:
            return False
        self.qte_seen = True
        kind = q.get("type")
        self.shot("qte_" + str(kind))
        now = time.monotonic()
        if kind in ("mash", "clash") or kind == "pluck" and q.get("state") == "finalMash":
            self.hold()
            if now >= self.next_attack:
                self.pulse("j")
                self.next_attack = now + 1 / 12
        elif kind == "timing":
            self.hold()
            zone, m = q.get("zone") or [.42, .58], q.get("m") or 0
            if isinstance(m, (int, float)) and zone[0] + .015 <= m <= zone[1] - .015:
                self.pulse("Enter")
        elif kind == "press":
            self.hold()
            self.pulse(KEYS.get(q.get("key"), q.get("key") or "Enter"))
        elif kind == "rhythm":
            self.hold()
            states = q.get("state") if isinstance(q.get("state"), list) else []
            for n, status in zip(q.get("notes") or [], states):
                target = n if isinstance(n, (int, float)) else n.get("t", 0)
                if status == 0 and abs((q.get("t") or 0) - target) < .065:
                    self.pulse("j")
                    break
        elif kind in ("pluck", "aim"):
            m = q.get("m") or [0, 0]
            if not isinstance(m, list):
                m = [0, 0]
            keys = ["j"] if kind == "pluck" else []
            if abs(m[0]) > 3:
                keys.append("ArrowLeft" if m[0] > 0 else "ArrowRight")
            if abs(m[1]) > 3:
                keys.append("ArrowUp" if m[1] > 0 else "ArrowDown")
            self.hold(keys)
            # aim 分两种收尾：不 throw 的靠「在准星圈里累计 3 秒」，throw 的必须自己按 J 射出去。
            #   只挪方向键不按 J，throw 型会一直等到超时判失败（终章最后一发就是这么卡住的）。
            if kind == "aim" and len(keys) <= 1 and m[0] * m[0] + m[1] * m[1] <= 16:
                self.pulse("j")
        return True

    def qte_guard(self, s):
        if self.qte_seen and not s.get("qte"):
            self.qte_seen = False
            self.hold()
            initial = s.get("dlg")
            until = time.monotonic() + .5
            while time.monotonic() < until:
                cur = self.st()
                if cur.get("dlg"):
                    if initial is None:
                        initial = cur["dlg"]
                    # 看到对白就停手：继续按 Enter 会把这一页翻过去，那是玩家自己按的，
                    # 不是引擎把 QTE 的确认键漏给了对白（终章最后一发后面紧跟一句台词，就是这么误报的）
                    self.check(cur.get("dpage") == 0, "qte_dialog_skipped",
                               before=initial, after=cur.get("dlg"), page=cur.get("dpage"))
                    break
                self.pulse("Enter", .005)
                self.page.mouse.click(640, 360)
                self.page.wait_for_timeout(35)
            self.marks.append([self.elapsed(), "QTE后确认键保护", "checked" if initial else "no_dialog"])
            return True
        return False

    def advance(self, s):
        if self.qte(s):
            return True
        if self.qte_guard(s):
            return True
        if s.get("qte"):
            self.hold()
            return True
        if s.get("dlg") or s.get("narr") or s.get("notice") or s.get("choice"):
            self.hold()
            if not s.get("nauto"):
                self.pulse("Enter")
                self.page.wait_for_timeout(125)
            return True
        return False

    def loss_menu(self, s):
        fid = s.get("fightId") or self.last_fight
        if fid not in self.fights or "再来一次" not in (s.get("menuItems") or []):
            return False
        self.hold()
        self.loses[fid] = self.loses.get(fid, 0) + 1
        self.shot(fid + "_lost_" + str(self.loses[fid]))
        uids = {e[0]: e[17] for e in self.fights[fid].get("enemies", []) if e[13]}
        if fid not in self.retry_uids:
            self.retry_uids[fid] = uids
        else:
            self.check(self.retry_uids[fid] == uids, "retry_boss_recreated", fight=fid, before=self.retry_uids[fid], after=uids)
        if fid == "b01_kakyoin" and self.loses[fid] == 2:
            self.check(any("放水再来" in x for x in s.get("menuItems") or []), "assist_menu_missing", fight=fid)
        # Boss 加强（bossHpMul / bossDmgMul = 1.5）以后，测试器的固定打法在个别战斗里一直输；真人靠放水过关，
        # 所以同一场输满 3 次后改选「放水再来」，之后每再输 2 次叠一档（放水中系数不生效，回到原版强度再减伤）。
        n_lose = self.loses[fid]
        if n_lose >= 3 and (n_lose - 3) % 2 == 0 and any("放水再来" in (x or "") for x in s.get("menuItems") or []):
            self.menu("放水再来")
        else:
            self.menu("再来一次")
        self.next_attack = time.monotonic() + .2
        return True

    def defend(self, s, force_guard=False):
        now, fid = time.monotonic(), s.get("fightId")
        if now < self.guard_until:
            self.hold(["l"])
            return True
        if now < self.next_defense:
            return False
        threat = None
        for e in s.get("enemies") or []:
            target = e[11] or [e[1], e[2]]
            near = abs(target[0] - s["px"]) < 48 and abs(target[1] - s["py"]) < 16
            if 0 <= e[12] <= (.16 if fid == 'b05_devo' else .10) and near:
                threat = (e, e[8] == "W5")
                break
        for shot in s.get("shots") or []:
            if abs(shot[0]) < 36 and abs(shot[1]) < 10 and shot[0] * shot[2] < 0:
                threat = (None, False)
        for h in s.get("hazards") or []:
            if h[0] <= s["px"] <= h[1] and h[2] <= s["py"] <= h[3] and 0 <= (h[4] or 0) <= .06:
                threat = (None, h[7] != "parryOnly")
        if not threat:
            return False
        n = self.defenses.get(fid, 0) + 1
        self.defenses[fid] = n
        self.hold()
        if force_guard or n % 2 == 1 and not threat[1]:
            self.hold(["l"])
            self.guard_until = now + .3
            self.next_defense = now + .45
        else:
            e = threat[0]
            keys = ["ArrowLeft" if e and e[1] > s["px"] else "ArrowRight"]
            if e and e[8] == "W4":
                keys = ["ArrowDown" if s["py"] < 164 else "ArrowUp"]
            self.hold(keys)
            self.pulse("k")
            self.next_defense = now + .3
        return True

    def attack(self, s, facing=None):
        now = time.monotonic()
        if facing is not None and s.get("pfacing") != facing:
            self.hold(["ArrowRight" if facing > 0 else "ArrowLeft"])
            return
        self.hold()
        if now >= self.next_attack:
            self.pulse("j")
            self.next_attack = now + (1 / 12 if int(s.get("fightT") or 0) % 6 >= 3 else .11)

    def teach(self, s):
        hint = s.get("fightHint") or {}
        step = hint.get("step", 0)
        if self.args.teach_fail and step not in self.relaxed:
            self.hold()
            return
        if step == 1:
            self.hold(["ArrowRight" if s["px"] < 225 else "ArrowLeft"])
        elif step == 2:
            if not self.defend(s):
                self.hold()
        elif step == 3:
            self.hold(["l"])
        elif step == 4:
            if not self.defend(s, force_guard=True):
                self.hold()
        elif step == 5:
            obj = next((o for o in s.get("objects") or [] if o[0] == "pipe"), None)
            if obj:
                if s.get('playerAtk') or s.get('playerRush') or self.move(s, obj[1] + 25, obj[2], 3):
                    self.attack(s, -1)
            else:
                self.note("npc_missing", object="pipe", fight=s.get("fightId"))
        elif step == 6:
            self.hold()
            self.pulse("u")

    def fight(self, s):
        fid, hint = s.get("fightId"), s.get("fightHint") or {}
        if self.args.lose and s.get("fightLosable"):
            need = 2 if fid == "b01_kakyoin" else 1
            if self.loses.get(fid, 0) < need:
                self.hold()
                return
        tactic = TACTICS.get(fid)
        if tactic == "teach":
            return self.teach(s)
        if tactic == "fail_segment":
            return self.attack(s)
        if tactic == "kakyoin" and hint.get("phase") == 3:
            self.hold(["l"])
            return
        if self.mechanic_fight(s, tactic):
            return
        if self.defend(s):
            return
        enemies = [e for e in s.get("enemies") or [] if e[4] > 0 and not e[14]]
        if not enemies:
            self.hold()
            return
        enemy = min(enemies, key=lambda e: abs(e[1] - s["px"]) + 2 * abs(e[2] - s["py"]))
        if tactic == 'devo':
            dx = enemy[1] - s['px']
            # 能量满了、贴着它：U 千本刺（第3章提示：J3 / U 把藏着的玩偶逼出来）
            if (s.get('energy') or 0) >= (s.get('energyMax') or 100) and abs(dx) < 40 and abs(enemy[2] - s['py']) < 10:
                self.hold()
                self.pulse('u')
                return
            if abs(dx) < 19 and s.get('playerCanCancel') and not s.get('rootT') and not s.get('dodgeCd'):
                self.hold(['ArrowLeft' if dx >= 0 else 'ArrowRight'])
                self.pulse('k')
                return
            if s.get('playerAtk') or s.get('playerRush'):
                self.attack(s)
                return
            if abs(enemy[2] - s['py']) > 3:
                self.move(s, s['px'], enemy[2])
                return
            if abs(dx) > 50:
                self.move(s, enemy[1] - (42 if dx >= 0 else -42), enemy[2], 3)
                return
            self.attack(s, 1 if dx >= 0 else -1)
            return
        rooted = enemy[15] > 0
        if tactic == "towergray" and not rooted:
            lines = [w for w in s.get("warns") or [] if w[0] == "W4"]
            if lines:
                w = lines[0]
                y = 160
                t = max(0, min(1, (y - w[3]) / (w[5] - w[3]))) if w[5] != w[3] else .5
                x = w[2] + t * (w[4] - w[2])
                if self.move(s, x, y, 3):
                    self.attack(s, 1 if enemy[1] >= s["px"] else -1)
            else:
                self.move(s, s["px"], 160)
            return
        if tactic == "chariot":
            if hint.get("phase") == 2:
                statue = next((o for o in s.get("objects") or [] if "statue" in o[0]), None)
                if statue and not self.move(s, statue[1] - 18, statue[2], 3):
                    return
            if hint.get("stance"):
                dist = abs(enemy[1] - s["px"])
                if not 70 <= dist <= 120:
                    self.move(s, enemy[1] - (95 if s["px"] < enemy[1] else -95), enemy[2])
                    return
                self.hold(["l"])
                if time.monotonic() >= self.next_attack:
                    self.pulse("j")
                    self.next_attack = time.monotonic() + .5
                return
        if (s.get("energy") or 0) >= (s.get("energyMax") or 100) or s.get("storyU"):
            if tactic != "towergray" or rooted:
                self.hold()
                self.pulse("u")
                self.next_attack = time.monotonic() + .15
                return
        if s.get("fightSwap") and (s.get("hp") or 0) < .4 * (s.get("maxHp") or 1):
            self.hold()
            self.pulse("q")
            return
        if s.get("timer") and len(enemies) == 1 and enemy[4] >= 900:
            self.hold(["l"])
            return
        dx, dy = enemy[1] - s["px"], enemy[2] - s["py"]
        if abs(dy) > 3:
            self.move(s, s["px"], enemy[2])
        elif abs(dx) > 29:
            self.move(s, enemy[1] - (25 if dx > 0 else -25), enemy[2])
        else:
            self.attack(s, 1 if dx >= 0 else -1)

    def mechanic_fight(self, s, tactic):
        """只读取可见机关信息；所有动作仍经键盘，不改生命、伤害或时间。"""
        h, fid = s.get("fightHint") or {}, s.get("fightId")
        mem = self.mechanic.setdefault(fid, {})
        if tactic == "darkmoon":
            if h.get("starWindow") or h.get("barnacles", 0) >= 3:
                self.hold()
                self.pulse("u")
                return True
            if h.get("barnacles", 0) >= 2:
                self.hold(["l"])
                return True
            if h.get("bubbleActive") and h.get("oxygen", 100) < 45:
                self.move(s, h["bubbleX"], 165, 5)
                return True
        elif tactic == "strength" and h.get("eyes", 0) < 3:
            eye = next((o for o in s.get("objects") or [] if o[0].startswith("ship_eye_") and not o[5]), None)
            if eye:
                if self.defend(s):
                    return True
                if self.move(s, eye[1], eye[2], 3):
                    self.attack(s)
                return True
        elif tactic == "yellow" and not h.get("water"):
            # 2026-10-11 第3章重做：黏液吸收伤害但吸收不了冲力——站在他离窗远的那一侧打（J3 把他往窗户推），
            #   被逼到窗边（公开提示 window）就贴近按 U；身上黏液 ≥ 3 层按 K 甩掉；掉海的外景演出期间不动
            boss = next((e for e in s.get("enemies") or [] if e[13]), None)
            if boss:
                if h.get('falling'):
                    self.hold()
                    return True
                # 首次沾黏液就实测一次 K，避免快速推窗路线漏掉甩黏液覆盖。
                slime = h.get('slime') or 0
                first_dodge = not self.coverage.get(s.get('fightId'), {}).get('dodge', 0)
                if (slime >= 3 or slime > 0 and first_dodge) and not s.get('dodgeCd'):
                    self.hold()
                    self.pulse('k')
                    return True
                if h.get('window') and abs(boss[1] - s["px"]) < 31 and abs(boss[2] - s["py"]) < 12:
                    self.hold()
                    self.pulse("u")
                    return True
                if self.defend(s):
                    return True
                # 已经在出招 / 连打：接着按 J（J 三连接连按 = 欧拉连打，挪位置会把连段打断）
                if (s.get('playerAtk') or s.get('playerRush')) and abs(boss[1] - s['px']) < 40:
                    self.attack(s)
                    return True
                wx = h.get('winL', 60) if boss[1] < 160 else h.get('winR', 260)
                side = 1 if wx < boss[1] else -1          # 站到他远离窗户的那一侧
                if self.move(s, boss[1] + side * 20, boss[2], 4):
                    self.attack(s, -side)
                return True
        elif tactic == "hanged" and not h.get("phase"):
            if h.get("intercept"):
                self.hold()
                self.pulse("j")
                return True
            mirrors = [o for o in s.get("objects") or [] if o[0].startswith("reflection_") and not o[5]]
            if mirrors:
                m = mirrors[0]
                if self.move(s, m[1] + (18 if m[1] < 160 else -18), m[2], 3):
                    self.attack(s, 1 if m[1] > s["px"] else -1)
                return True
            if not self.move(s, 140, 163, 2):
                return True
            if time.monotonic() >= mem.get("sandAt", 0):
                self.hold(["k"])
                self.pulse("j")
                self.hold()
                mem["sandAt"] = time.monotonic() + 3
            elif not self.defend(s):
                self.hold()
            return True
        elif tactic == "empress":
            if h.get("growth", 0) >= 1 and not mem.get("radarUsed"):
                self.hold()
                self.pulse("u")
                mem["radarUsed"] = True
                return True
            if h.get("growth", 0) < 1:
                if not self.defend(s):
                    self.hold()
                return True
            xs = h.get("barrels") or []
            if xs:
                x = xs[h.get("tarIndex", 0)]
                if s.get("px", 0) and abs(x - s["px"]) < 22:
                    self.hold()
                    self.pulse("e")
                else:
                    # 抢操作时按相反方向，依然通过游戏公开输入。
                    self.move(s, x if not h.get("reversed") else s["px"] - (x - s["px"]), 164, 5)
                return True
        elif tactic == "road":
            want = min(range(3), key=lambda i: abs([152, 160, 168][i] - h.get("bossLane", 160)))
            self.hold()
            if h.get("lane", 1) != want:
                self.pulse("ArrowDown" if want > h.get("lane", 1) else "ArrowUp")
            else:
                self.pulse("j")
            return True
        elif tactic == "wheel" and h.get("spark"):
            self.hold()
            self.pulse("u")
            return True
        elif tactic == "justice" and h.get("inhale"):
            self.hold()
            self.pulse("u")
            return True
        elif tactic == "lovers":
            if h.get("phase") == "street":
                command = h.get("command")
                if command == 0:
                    self.hold(["l"])
                elif command == 1:
                    self.hold()
                    nxt = "ArrowLeft" if mem.get("lastDir") != "ArrowLeft" else "ArrowRight"
                    self.pulse(nxt)
                    mem["lastDir"] = nxt
                elif command == 2:
                    # 老板转头前留一个采样间隔余量；避免沿用前一帧按住的方向键。
                    if h.get("vendorWatching"):
                        self.hold()
                    elif h.get("progress", 0) >= .96:
                        self.hold()
                        self.pulse("e")
                    else:
                        self.hold(["ArrowRight"])
                return True
            if not mem.get("swapped"):
                self.hold()
                self.pulse("q")
                mem["swapped"] = True
                return True
        return False

    def press_hot(self, s, h, key, tasks, now, radius=2, blind_after=2.5):
        # 走到调查点旁按 E。热点会互相重叠（第11章游戏室的门口 `门` 和 `街机` 只差 12 px，
        # 站在两点之间按 E 会按到街机、把出口记成“已完成”，人就永远出不了门）。
        # 所以先贴到「游戏自己说最近的就是它」再按；锚点落在可走带外面贴不到时，才兜底盲按。
        if s.get("near") == h[0]:
            self.hot_try.pop(key, None)
            self.hold()
            self.pulse("e")
            tasks.add(key)
            self.last_task_t = now
            return True
        # 兜底盲按必须**先走到**锚点附近再开始计时：原来一挂上任务就开始数 2.5 s，
        #   横跨半张图（>200 px）的锚点在路上就被盲按、E 打空、任务记成完成，
        #   第5章卡拉奇「问路」（x232，人从 x632 往回走）就是这么整章卡死的。
        arrived = self.move(s, h[1], h[2], radius)
        if not arrived:
            self.hot_try.pop(key, None)
            return False
        since = self.hot_try.get(key)
        if since is None:
            self.hot_try[key] = now
        elif now - since > blind_after:
            self.hot_try.pop(key, None)
            self.hold()
            self.pulse("e")
            tasks.add(key)
            self.last_task_t = now
            return True
        return False

    def explore(self, s):
        stage, chap = s.get("stage"), chapter_of(s.get("stage"))
        now = time.monotonic()
        if self.free_since is None:
            self.free_since = now
            self.last_task_t = now
        if stage == self.args.idle_at and not self.idle_completed:
            if self.idle_started is None:
                self.idle_started = now
                self.hold()
                self.shot("idle_start_" + stage)
            if s.get("flags", {}).get("flyFound"):
                took = now - self.idle_started
                self.check(took <= 70, "idle_protection_late", sec=round(took, 2))
                self.note("idle_protection_done", sec=round(took, 2))
                self.idle_completed = True
            elif now - self.idle_started > 90:
                self.check(False, "idle_protection_timeout", sec=90)
                raise RuntimeError("闲置保护 90 秒未推进")
            return
        if now - self.free_since < .5:
            self.hold()
            return
        party = [a for a in s.get("party") or [] if a[6] and a[3] != "down"]
        if len(party) > 1 and stage not in self.swapped:
            self.switch_leader(s)
            return
        tasks = self.explored.setdefault(stage, set())
        investigated = self.investigated.setdefault(chap, set())
        hots = s.get("hotspots") or []
        # 在一张图里兜转太久（调查点特别多、走位又长）时，先直奔出口类热点：
        # 第11章游戏室有 5 个带全标签的调查点，逐个队长 U 一遍要跨图来回十几趟，
        # 一直排在出口前面会把整章卡死在这里。真人也是先看完再出门，这里只是把「出门」提前。
        EXIT_WORDS = ("门", "出口", "楼梯", "出发", "继续", "往前", "去")
        if now - self.free_since > 45 and not s.get("busy") and self.exit_first.get(stage, 0) < 2:
            exits = [h for h in hots if any(w in h[0] for w in EXIT_WORDS)]
            if exits:
                ex = min(exits, key=lambda h: abs(h[1] - s["px"]) + abs(h[2] - s["py"]))
                tasks.discard(("e", ex[0]))          # 之前按过但没反应：允许再按一次
                if self.press_hot(s, ex, ("e", ex[0]), tasks, now):
                    self.exit_first[stage] = self.exit_first.get(stage, 0) + 1
                return
        tagged = [h for h in hots if h[3] and ("u", h[0], s.get("leader")) not in tasks]
        # 苍蝇必须在保护提示前由承太郎亲自发现，发现后换阿布德尔辨识。
        if stage == "bedroom_pro":
            photo = next((h for h in hots if "照片" in h[0]), None)
            target = "avdol" if s.get("flags", {}).get("flyFound") else "jotaro"
            if photo:
                if s.get("leader") != target:
                    self.switch_leader(s, target)
                    return
                tagged = [photo]
        if tagged:
            h = min(tagged, key=lambda h: abs(h[1] - s["px"]) + abs(h[2] - s["py"]))
            matches = [a[0] for a in party if LOOK.get(a[0], set()) & set(h[3])]
            if matches and s.get("leader") not in matches:
                self.switch_leader(s, matches[0])
                return
            if self.move(s, h[1], h[2], 5):
                if s.get("leaderCanInvestigate"):
                    self.hold()
                    self.pulse("u")
                    tasks.add(("u", h[0], s["leader"]))
                    self.last_task_t = now
                    investigated.add(s["leader"])
                    if stage == "bedroom_pro" and s["leader"] == "jotaro":
                        self.fly_input_at = self.elapsed()
            return
        if len(investigated) < 3 and len(party) >= 3:
            cid = next((a[0] for a in party if a[0] not in investigated), None)
            if cid and s.get("leader") != cid:
                self.switch_leader(s, cid)
                return
            if s.get("leaderCanInvestigate"):
                self.hold()
                self.pulse("u")
                self.last_task_t = now
                investigated.add(s["leader"])
                return
        for h in hots + (s.get("npcs") or []):
            key = ("e", h[0])
            if key in tasks:
                continue
            self.press_hot(s, h, key, tasks, now)
            return
        self.hold(["ArrowRight"])
        # 全部调查点都做完、只剩往右走时，40 s 没新完成项才重来一遍（旧写法按进图时间算，
        # 一张要走超过 40 s 的图会被反复清空清单，永远走不到出口）
        if now - self.last_task_t > 40:
            tasks.clear()
            self.last_task_t = now

    def run(self):
        if not self.enter():
            return
        target = chapter_index(self.args.until or ("final" if self.args.chapter == "all" else self.args.chapter))
        last_progress, state_key = time.monotonic(), None
        while self.elapsed() < self.args.timeout:
            s = self.st()
            chap = chapter_of(s.get("stage"))
            if s.get("scene") == "end" or s.get("menu") and "完" in s["menu"]:
                done = chap if chap is not None else self.page.evaluate("() => G.curChapter")
                self.shot("chapter_complete_" + str(done))
                self.mem["chapter_" + str(done)] = self.page.evaluate("() => G.audio.mem()")
                self.marks.append([self.elapsed(), str(done), "chapter_complete"])
                if done >= target:
                    self.note("route_complete", chapter=done)
                    break
                if not self.menu("继续下一章"):
                    break
            elif s.get("menuItems"):
                if not self.loss_menu(s):
                    self.note("unexpected_menu", items=s["menuItems"])
                    break
            elif self.idle_started is not None and not self.idle_completed:
                # 纯闲置模式在目标地图不推进提示对白或 QTE。
                self.hold()
                if s.get("flags", {}).get("flyFound"):
                    took = time.monotonic() - self.idle_started
                    self.check(took <= 70, "idle_protection_late", sec=round(took, 2))
                    self.note("idle_protection_done", sec=round(took, 2))
                    self.idle_completed = True
                elif time.monotonic() - self.idle_started > 90:
                    self.check(False, "idle_protection_timeout")
                    break
            elif self.advance(s):
                pass
            elif s.get("combat") and (s.get("fightHint") or {}).get("phase") == "street":
                self.mechanic_fight(s, "lovers")
            elif s.get("combat") and not s.get("cine"):
                self.fight(s)
            elif s.get("free") and not s.get("busy"):
                self.explore(s)
            else:
                self.hold()
            key = (s.get("stage"), s.get("dlg"), s.get("narr"), s.get("fightId"),
                   json.dumps(s.get("fightHint"), sort_keys=True), s.get("px"), s.get("py"), s.get("hp"))
            if key != state_key:
                state_key, last_progress = key, time.monotonic()
            if time.monotonic() - last_progress > (180 if self.args.teach_fail else 90) and not self.idle_started:
                self.note("fight_timeout" if s.get("combat") else "advance_timeout", state=s)
                break
            self.page.wait_for_timeout(50)
        else:
            self.note("route_timeout", limit=self.args.timeout)
        self.hold()
        self.validate()

    def validate(self):
        s = self.st()
        self.check(any(n["kind"] == "route_complete" for n in self.notes), "chapter_not_completed")
        for name in ("missingImg", "missingSfx", "missingGlyph", "missingHead"):
            self.check(not s.get(name), name, items=s.get(name))
        evs = s.get("evTotals") or {}
        self.check(not evs.get("look_missing"), "look_missing", count=evs.get("look_missing"))
        self.check(not evs.get("api_missing"), "api_missing", items=evs.get("api_missing"))
        for name in ("fx_unknown", "fx_error", "script_error"):
            self.check(not evs.get(name), name, count=evs.get(name))
        fps = s.get("fps") or {}
        self.check(fps.get("avg", 0) >= 55, "fps_below_55", fps=fps)
        for fid, c in self.coverage.items():
            # 换车道、躲倒影和柏油 QTE 有自己的胜利输入，不能套用近战连打覆盖要求。
            if fid in ("b07_hangedman", "b08_empress", "b09a_wheelroad"):
                continue
            # 第2章力量：主要是机关（管道要闪、吊钩紫边不可挡、打眼睛），格挡只对扔东西有用，测试器常常一次都用不上——只查闪避和连打
            # 第3章黄色节制（2026-10-11 重做）：车厢里是把他推到窗边撞出去、K 甩黏液，水里限时乱打，格挡不是解法——同样只查闪避和连打
            if fid in ("b04_strength", "b06_yellowtemperance"):
                self.check(c.get("dodge", 0) >= 1, "coverage_dodge", fight=fid, counts=c)
                self.check(c.get("rush", c.get("rushStart", 0)) >= 1, "coverage_rush", fight=fid, counts=c)
                continue
            self.check(c.get("dodge", 0) >= 1, "coverage_dodge", fight=fid, counts=c)
            # 格挡、弹反和闪避都是防御行为；随机路线可能只触发其中一种。
            self.check(c.get("guard", 0) + c.get("parry", 0) + c.get("dodge", 0) >= 1, "coverage_defense", fight=fid, counts=c)
            self.check(c.get("rush", c.get("rushStart", 0)) >= 1, "coverage_rush", fight=fid, counts=c)
        self.check(sum(c.get("special", 0) for c in self.coverage.values()) >= 1, "coverage_special")
        for chap, cids in self.investigated.items():
            self.check(len(cids) >= 3, "coverage_investigate", chapter=chap, leaders=sorted(cids))
        self.check(bool(self.swapped), "coverage_swap")
        if self.args.teach_fail:
            self.check(self.relaxed == set(range(1, 7)), "teach_relax_incomplete", steps=sorted(self.relaxed))
        if self.args.idle_at:
            self.check(self.idle_completed, "idle_not_completed")
        elif any(t.get("stage") == "bedroom_pro" for t in self.trace):
            self.check(self.fly_input_at is not None and self.fly_found, "fly_not_investigated")
        for fid, before in self.retry_uids.items():
            after = {e[0]: e[17] for e in self.fights[fid].get("enemies", []) if e[13]}
            # 最后一张战斗快照可能正好是 Boss 被打倒移除的那一帧（第2章暗蓝之月：after 是空的）——空的说明这场已经打完，
            #   没东西可比；重来时有没有重建 Boss 已经在每次 loss_menu 里比过了
            if after:
                self.check(before == after, "retry_boss_recreated", fight=fid, before=before, after=after)
        if self.args.lose:
            expected = [f for f, st in self.fights.items() if st.get("fightLosable")]
            for fid in expected:
                self.check(self.loses.get(fid, 0) >= (2 if fid == "b01_kakyoin" else 1), "lose_route_missing", fight=fid)
        ids = autowin_ids(self.args)
        if ids:
            # 自动判胜跳过了真实战斗过程，这里只留提示、不算错误，但必须让报告读者看到。
            self.note("debug_autowin_used", ids=ids)
        for n in self.notes:
            if n["kind"] in BAD_NOTES or n["kind"] == "route_timeout":
                self.check(False, n["kind"])

    def report(self):
        ids = autowin_ids(self.args)
        if ids:
            # 自动判胜直达后面的战斗，路线不能当通关证据；stdout 用醒目告警，避免只在 JSON 深处才看得到。
            print("⚠ 本次路线用了 --autowin：不是通关证据", flush=True)
        return {"errors": self.errors, "shots": self.shots, "notes": self.notes, "dialog_lines": self.lines,
                "trace": self.trace, "marks": self.marks, "coverage": self.coverage,
                "fallbacks": self.last_s.get("fallbacks", []), "final": self.last_s,
                "loses": self.loses, "relaxed": sorted(self.relaxed), "audio_memory": self.mem,
                "debug_autowin": ids,
                "investigated": {str(k): sorted(v) for k, v in self.investigated.items()}, "seconds": self.elapsed()}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("chapter", choices=["prologue", "all", "final"] + [f"ch{i}" for i in range(1, 12)])
    p.add_argument("--until", choices=["prologue", "final"] + [f"ch{i}" for i in range(1, 12)])
    p.add_argument("--lose", action="store_true", help="可失败战故意输后重试")
    p.add_argument("--autowin", default="", metavar="ID1,ID2",
                   help="调试：这些战斗开打 1 s 后自动判胜，直达后面的战斗；跑出来的路线不是通关证据")
    p.add_argument("--teach-fail", action="store_true", help="教学每步先等放宽再完成")
    p.add_argument("--idle-at", help="在指定探索地图纯闲置，验证保护")
    p.add_argument("--shots-off", action="store_true", help="不截画面")
    p.add_argument("--timeout", type=float, default=1800, help="路线总超时秒数")
    p.add_argument("--out", type=Path, help="证据输出目录，默认按路线区分")
    return p



CONTAINER_CSP = ("default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; "
                 "font-src 'self'; media-src 'self'; connect-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'")


def serve_pkg(root):
    """起一个本地静态服务打开发布包目录（响应头带容器同款 CSP），返回 base url（以 / 结尾）。进程退出时随线程结束。"""
    import functools
    import http.server
    import socketserver
    import threading

    class H(http.server.SimpleHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def end_headers(self):
            self.send_header("Content-Security-Policy", CONTAINER_CSP)
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def log_message(self, *a):
            pass

    class S(socketserver.ThreadingTCPServer):
        request_queue_size = 256
        daemon_threads = True
        allow_reuse_address = True

        def handle_error(self, *a):
            pass

    srv = S(("127.0.0.1", 0), functools.partial(H, directory=root))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return "http://127.0.0.1:%d/" % srv.server_address[1]


def main():
    args = parser().parse_args()
    autowin = (args.autowin or "").strip()
    # 调试参数会直接拼进 URL，先在这里卡死字符集，避免逗号/问号等把查询串拼坏。
    if autowin and not re.fullmatch(r"[A-Za-z0-9_]+(?:,[A-Za-z0-9_]+)*", autowin):
        raise SystemExit("--autowin 只允许字母、数字、下划线和逗号分隔的战斗 id")
    args.autowin = autowin
    from playwright.sync_api import sync_playwright
    suffix = "_lose" if args.lose else "_teach_fail" if args.teach_fail else "_idle" if args.idle_at else ""
    out = args.out or GAME / "tools" / "_playtest" / (args.chapter + suffix)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
        page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
        t = Tester(page, args, out)
        page.on("console", lambda m: t.errors.append({"kind": "console_" + m.type, "text": m.text}) if m.type in ("error", "warning") else None)
        page.on("pageerror", lambda e: t.errors.append({"kind": "pageerror", "text": str(e), "stack": getattr(e, "stack", None)}))
        try:
            # autowin 只在 autotest=1 时由游戏侧生效，这里两个参数一起带，真实路线才能直达后面的战斗。
            url = (GAME / "index.html").as_uri() + "?autotest=1"
            # 调试：JOJO_SERVE_ROOT=<打好的发布包目录> 时改成用本地 http 服务打开那个包（带容器同款 CSP：脚本只许外链、不许 eval），
            #   同一套真实键盘路线就能对「打包后的代码」再跑一遍（全部章节开放的小红书包用这个验收）。
            serve_root = os.environ.get("JOJO_SERVE_ROOT")
            if serve_root:
                url = serve_pkg(serve_root) + "index.html?autotest=1"
            if autowin:
                url += "&autowin=" + autowin
            page.goto(url, wait_until="load")
            t.run()
        except Exception as e:
            # 失败路线要能定位测试器自身的异常；保留完整 Python 栈，不把单独的
            # IndexError / Playwright 错误压成无法行动的数字字符串。
            t.errors.append({"kind": "tester_error", "text": str(e), "traceback": traceback.format_exc()})
            try:
                t.st()
                t.shot("exception")
            except Exception:
                pass
        report = t.report()
        (out / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "dialog_seen.txt").write_text("\n\n".join(t.lines), encoding="utf-8")
        browser.close()
    print(json.dumps({"ok": not t.errors, "errors": len(t.errors), "sec": report["seconds"], "out": str(out)}, ensure_ascii=False))
    return 1 if t.errors else 0


if __name__ == "__main__":
    sys.exit(main())
