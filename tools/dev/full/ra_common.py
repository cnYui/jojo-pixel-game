"""routes-a（第1–5章路线）测试器共用的小工具：只读游戏状态，所有动作仍走真实键盘。

qte_guard：QTE 一结束就连按 Enter / 点击，检查 0.6 s 的确认锁有没有挡住“猛按跳过 QTE 后的第一句台词”。
父类（tools\\playtest.py）的写法是“QTE 结束后连按 0.5 s，台词变了就算跳过”：测试读状态有延迟（两路测试并行时一轮 100–200 ms），
发现 QTE 结束时锁可能只剩 0.4 s，后面几下是锁过期以后的正常推进，被误报成 qte_dialog_skipped
（ra_ch2_r1 第一次跑：鲨鱼 QTE、夺回安妮两处）。这里每按一下之前先读锁还剩多久，剩不到 0.12 s 就停手
（再按就是玩家正常推进对白了），所以只要台词在“锁还在”的时候变了，就是真的被跳过。
"""
import time

LOCK_JS = "() => (G.input && typeof G.input.okLockUntil === 'number') ? G.input.okLockUntil - G.clk.ui : 0"


def qte_guard(t, s):
    """t = Tester 实例。返回 True 表示这一轮已处理（和父类 qte_guard 同语义）。"""
    if not (t.qte_seen and not s.get('qte')):
        return False
    t.qte_seen = False
    t.hold()
    initial, page0 = s.get('dlg'), s.get('dpage')
    until = time.monotonic() + .5
    presses = 0
    t._guarding = True   # 检查期间测试器不截剧情图（截图前要等弹出动画，会把连按拖过锁）
    try:
        while time.monotonic() < until:
            left = t.page.evaluate(LOCK_JS) or 0
            if left < .12:
                break
            t.pulse('Enter', .005)
            t.page.mouse.click(640, 360)
            presses += 1
            t.page.wait_for_timeout(35)
            cur = t.st()
            if initial is None and cur.get('dlg'):
                initial, page0 = cur['dlg'], cur.get('dpage')
                continue
            if initial:
                ok = cur.get('dlg') == initial and cur.get('dpage') == page0
                t.check(ok, 'qte_dialog_skipped', before=initial, after=cur.get('dlg'), page=cur.get('dpage'), presses=presses)
                if not ok:
                    break
    finally:
        t._guarding = False
    t.marks.append([t.elapsed(), 'QTE后确认键保护', ('checked' if initial else 'no_dialog') + f' x{presses}'])
    return True
