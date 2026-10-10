"""序章真实键盘路线验收：从标题打到序章章末（进入第1章前的「完」菜单）。

和 playtest.Tester 的区别（都只读快照、所有操作走真实键盘）：
- 空条家 / 校门 / 保健室 / 卧室按序章的路线逐项做（基类的“替身调查任务按队长记账”会在两个调查点之间来回换人，测试自己的错）；
- 跟着走的女生：真人转身朝她走过去时她会站住，这里照真人的走法去搭话，核对两人都能搭上话；
- 多截几张检查画面：教学战每一步的提示、各张自由地图的目标箭头、失败菜单（弹出动画结束后再截）。
用法：python -B tools\\dev\\full\\test_prologue.py prologue [--lose] --out tools\\_playtest\\fix_prologue
"""
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
GAME = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(GAME / 'tools'))
import playtest

GOAL_JS = "() => !!(G.ui && G.ui.insertUI)"


class ProTester(playtest.Tester):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.done_steps = set()        # 路线步骤（一次性）
        self.step_seen = {}            # 教学战：第几步 → 首次看到的时间
        self.free_at = {}              # 地图 → 第一次自由走动的时间
        self.special_shots = set()
        self.goal_seen = set()         # 哪些地图出现过目标箭头
        self.talked = set()

    # ------------------------------------------------------------ 截图钩子
    def shot_once(self, name):
        if name in self.special_shots:
            return
        self.special_shots.add(name)
        self.shot(name)

    def st(self):
        s = super().st()
        now = time.monotonic()
        stage, fid = s.get('stage'), s.get('fightId')
        if fid == 'b00_avdol_test' and s.get('combat'):
            step = (s.get('fightHint') or {}).get('step')
            if step and step not in self.step_seen:
                self.step_seen[step] = now
            if step and now - self.step_seen.get(step, now) > 0.7:
                self.shot_once(f'teach_step{step}')
        if fid == 'b00_avdol_test' and s.get('combat'):
            # 教学战 coverage:false 不进基类的覆盖统计；但闪避 / 格挡 / 连打 / 必杀都是在这里用真实按键做的，算进本章覆盖
            self.coverage[fid] = dict(s.get('counts') or {})
        if not fid and self.last_fight in self.coverage and self.last_fight != 'b00_avdol_test':
            # 战斗最后一下（序2 按住 L 挡下全力水花）发生在 ctx.end() 前一两帧，打完那一刻的快照常常采不到；
            #   下一场战斗开始前计数不会清零，所以战后再并一次（取各项最大值）
            cov = self.coverage[self.last_fight]
            for k, v in (s.get('counts') or {}).items():
                cov[k] = max(cov.get(k, 0), v)
        if fid == 'b01_kakyoin' and (s.get('fightHint') or {}).get('phase') == 3:
            self.shot_once('kakyoin_phase3')
        if s.get('free') and not s.get('busy') and not s.get('combat') and stage:
            self.free_at.setdefault(stage, now)
            if self.page.evaluate(GOAL_JS):
                self.goal_seen.add(stage)
                self.goal_at = getattr(self, 'goal_at', {})
                self.goal_at.setdefault(stage, now)
                # 提示框有 0.25 s 淡入：箭头出现 0.6 s 后再截
                if s.get('hint') and now - self.goal_at[stage] > .6:
                    self.shot_once('goal_' + stage)
        # 序-8 石阶：走到一半（还没出事）拍一张，看人是不是踩在台阶上
        if stage == 'stairs_pro' and s.get('free') and not (s.get('flags') or {}).get('p8b') and 214 <= (s.get('px') or 0) <= 250:
            self.shot_once('stairs_descending')
        q = s.get('qte')
        if q and q.get('type') == 'pluck' and (q.get('pull') or 0) > .3:
            self.shot_once('pluck_progress')
        if q and q.get('type') == 'press' and (q.get('t') or 0) > .15:
            self.shot_once('qte_press_mid')
        flags = s.get('flags') or {}
        for key, who in (('girlA', '女生A'), ('girlB', '女生B'), ('boy', '男生'), ('girlC', '女生C')):
            if flags.get(key) and who not in self.talked:
                self.talked.add(who)
                self.shot_once('talk_' + key)
        return s

    def qte(self, s):
        # 拔肉芽最后的连按：游戏里是 q.phase == 'final'（基类按 state == 'finalMash' 判断，永远对不上，一直按住 J 不算连按）
        q = s.get('qte')
        if q and q.get('type') == 'pluck' and q.get('phase') == 'final' and q.get('result') is None:
            self.qte_seen = True
            self.shot_once('pluck_final')
            self.hold()
            now = time.monotonic()
            if now >= self.next_attack:
                self.pulse('j')
                self.next_attack = now + 1 / 12
            return True
        return super().qte(s)

    def fight(self, s):
        try:
            return super().fight(s)
        except Exception as e:
            import json, traceback
            (self.out / 'tester_crash.json').write_text(json.dumps({'trace': traceback.format_exc(), 'state': s},
                ensure_ascii=False, indent=1), encoding='utf-8')
            raise

    def teach(self, s):
        # 第 2 步躲火球：只看飞过来的火球本身（40 px 内、朝人飞）再按 K。基类 defend() 也看敌人预警读秒，
        #   debug.js 的 teleLeft 修正以后，它会在阿布德尔刚出手（火球还在 160 px 外）就闪，闪完火球才到，永远躲不开
        hint = s.get('fightHint') or {}
        if hint.get('step') == 2 and not (self.args.teach_fail and 2 not in self.relaxed):
            now = time.monotonic()
            shot = next((q for q in s.get('shots') or [] if q[3] == 'enemy' and abs(q[1]) < 12
                         and q[0] * q[2] < 0 and abs(q[0]) < 40), None)
            self.hold()
            if shot and now >= self.next_defense:
                self.pulse('k')
                self.next_defense = now + .5
            return
        return super().teach(s)

    def loss_menu(self, s):
        # 失败菜单有 0.12 s 的弹出动画：动画中只有空框，等动画走完再截，才看得出菜单有没有字
        fid = s.get('fightId') or self.last_fight
        if fid in self.fights and '再来一次' in (s.get('menuItems') or []):
            self.page.wait_for_timeout(350)
        return super().loss_menu(s)

    # ------------------------------------------------------------ 路线小工具
    def act(self, s, key, x, y, press, leader=None, radius=5):
        """换到 leader（需要的话）→ 走到 (x, y) → 按一次 press；按下去了返回 True。"""
        if leader and s.get('leader') != leader:
            self.switch_leader(s, leader)
            return False
        # 卧室中间荷莉的被褥是障碍（x 122–178、y 160–174）：要横穿时先走到被褥上面那条空道（y 154），横过去再下来
        if s.get('stage') == 'bedroom_pro':
            px, py = s.get('px', x), s.get('py', y)
            if min(px, x) < 184 and max(px, x) > 116 and abs(px - x) > 8:
                if py > 156:
                    self.move(s, px, 154, 3)
                    return False
                if not self.move(s, x, 154, 4):
                    return False
        if not self.move(s, x, y, radius):
            return False
        if press == 'u' and not s.get('leaderCanInvestigate'):
            self.hold()
            return False
        self.hold()
        self.pulse(press)
        self.done_steps.add(key)
        if press == 'u' and s.get('leader'):
            self.investigated.setdefault(0, set()).add(s['leader'])
        return True

    def npc_at(self, s, label):
        return next((n for n in s.get('npcs') or [] if n[0] == label), None)

    def settle(self, s):
        if time.monotonic() - self.free_at.get(s.get('stage'), 0) < .6:
            self.hold()
            return True
        return False

    # ------------------------------------------------------------ 各张自由地图的路线
    def explore(self, s):
        stage, flags = s.get('stage'), s.get('flags') or {}
        if stage in ('kujo_pro', 'stairs_pro', 'school_pro', 'infirmary_pro', 'bedroom_pro') and self.settle(s):
            return
        if stage == 'kujo_pro' and not flags.get('p7'):
            # 相机在矮桌上（x 64），墙在 x 90：站到 x 100 按 U（调查半径够得着）
            plan = [('k_furin', 'avdol', 214, 152, 'u'), ('k_garden', 'jotaro', 270, 152, 'u'),
                    ('k_holly', None, 170, 160, 'e'), ('k_camera', 'joseph', 100, 162, 'u')]
            for key, who, x, y, press in plan:
                if key not in self.done_steps:
                    if key == 'k_camera' and stage not in self.goal_seen:
                        self.hold()          # 像第一次玩的人一样：逛完一圈，等目标提示出来再去相机
                        return
                    if key == 'k_holly':
                        n = self.npc_at(s, '荷莉')
                        if n:
                            x, y = n[1], n[2]
                    self.act(s, key, x, y, press, who)
                    return
            self.hold()
            return
        # 序-8（2026-10-10 起）：坡顶小路先和跟着走的两个女生搭话，再往右走下石阶（走到第 8 级出事：序-8b 过场）
        if stage == 'stairs_pro' and not flags.get('p8b'):
            for key, label in (('s_girlA', '女生A'), ('s_girlB', '女生B')):
                if key in self.done_steps:
                    continue
                n = self.npc_at(s, label)
                self.step_t0 = getattr(self, 'step_t0', {})
                t0 = self.step_t0.setdefault(key, time.monotonic())
                if not n or time.monotonic() - t0 > 30:      # 30 s 还搭不上话：记下来往下走（validate 会报 school_followers_not_talkable）
                    self.done_steps.add(key)
                    continue
                # 跟着走的女生会站住等人搭话。两人挨得近时，从“她比另一个人更近”的那一侧走过去
                #   （头顶的互动提示写着名字，真人也是看着名字挪到对的人跟前），挨到她跟前按 E
                other = self.npc_at(s, '女生B' if label == '女生A' else '女生A') if label.startswith('女生') else None
                if s.get('near') == label:            # 头顶提示正指着她：按 E
                    self.hold()
                    self.pulse('e')
                    self.done_steps.add(key)
                    return
                side = (1 if n[1] >= other[1] else -1) if other and abs(other[1] - n[1]) < 30 else (1 if s['px'] > n[1] else -1)
                if not 24 <= n[1] + side * 12 <= 616:  # 外侧贴墙走不到：换另一侧
                    side = -side
                tx, ty = n[1] + side * 12, n[2]
                if self.move(s, tx, ty, 3):
                    self.hold(['ArrowRight' if side < 0 else 'ArrowLeft'])   # 到位了还没指着她：转身朝她
                return
            self.hold(['ArrowRight'])
            return
        if stage == 'stairs_pro' and flags.get('p8b'):
            self.hold(['ArrowRight'])          # 滚下来以后：往右走到头去学校
            return
        if stage == 'school_pro' and flags.get('p8b') and not flags.get('p9go'):
            # 校门：先和男生搭一次话，再走到校门口（x 236）往上走进去
            if 's_boy' not in self.done_steps:
                n = self.npc_at(s, '男生')
                if n and self.act(s, 's_boy', n[1] - 14, n[2], 'e', radius=6):
                    return
                if n:
                    return
                self.done_steps.add('s_boy')
            if self.move(s, 236, 141, 3):
                self.hold(['ArrowUp'])
            return
        if stage == 'infirmary_pro' and not flags.get('noteRead'):
            if 'i_girlC' not in self.done_steps:
                n = self.npc_at(s, '女生C')
                if n and self.act(s, 'i_girlC', n[1] + 14, n[2], 'e', radius=6):
                    return
                if n:
                    return
                self.done_steps.add('i_girlC')
            if not flags.get('sat'):
                n = self.npc_at(s, '校医')
                if n:
                    self.act(s, 'i_nurse', n[1] - 14, n[2], 'e', radius=6)
                return
            self.hold()
            self.pulse('e')
            self.page.wait_for_timeout(200)
            return
        if stage == 'bedroom_pro' and not flags.get('p17'):
            if not flags.get('flyFound'):
                if 'b_joseph' not in self.done_steps:
                    self.act(s, 'b_joseph', 236, 170, 'u', 'joseph')
                    return
                if self.act(s, 'b_fly', 236, 170, 'u', 'jotaro'):
                    self.fly_input_at = self.elapsed()
                return
            if 'b_avdol_life' not in self.done_steps:
                self.act(s, 'b_avdol_life', 200, 158, 'u', 'avdol')
                return
            self.act(s, 'b_avdol_e', 236, 170, 'e', 'avdol')
            return
        return super().explore(s)

    def validate(self):
        super().validate()
        if any(t.get('stage') == 'stairs_pro' for t in self.trace):
            self.check({'女生A', '女生B'} <= self.talked, 'school_followers_not_talkable', talked=sorted(self.talked))
        for stage in ('kujo_pro', 'stairs_pro', 'school_pro', 'infirmary_pro', 'bedroom_pro'):
            if any(t.get('stage') == stage for t in self.trace):
                self.check(stage in self.goal_seen, 'goal_arrow_missing', stage=stage)
        if any(t.get('stage') == 'jail_pro' for t in self.trace):
            self.check(set(self.step_seen) >= set(range(1, 7)), 'teach_steps_missing', steps=sorted(self.step_seen))

    def report(self):
        return {**super().report(), 'route_steps': sorted(self.done_steps), 'goal_seen': sorted(self.goal_seen),
                'talked': sorted(self.talked), 'teach_steps': sorted(self.step_seen),
                'input_boundary': '所有推进、移动、攻击、QTE、失败重试均走真实键盘；只读 snapshot 与 G.ui.insertUI 是否存在。'}


if __name__ == '__main__':
    playtest.Tester = ProTester
    raise SystemExit(playtest.main())
