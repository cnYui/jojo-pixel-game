"""第4章第7战（倒吊人）机关判定回归：镜子 / 橱窗好不好打碎、水洼的照射范围和画出来的水洼对不对得上。

2026-10-19 用户反馈“打不破镜子、水洼不好操作”：原来镜窗的判定是地面上 x 一个点 + 上下 ±6 px（站偏几个像素 J 就挥空），
水洼只比横向 ±20 px、不看 y（站在水洼上方 20 多 px 也被照到）。这里用真实键盘 J 在多个站位验证：
- 镜子 / 橱窗：站在玻璃前（横向够得着）任何 y 连按 J 都能打碎；够不着的位置（隔着 90 px 以上）不会误碎。
- 水洼：水洼椭圆之内被照到，从上面绕过去（y 小 10 px 以上）或横向走开都照不到。

玩家血量设成打不死（只为隔离倒吊人的刀光和荷尔·荷斯的子弹，判定本身不受影响）；入口借 G.DEV.ch4Hanged。
用法：python -B tools\\dev\\full\\test_ch4_hanged_glass.py [--out 目录]
"""
from pathlib import Path
import argparse
import json
import sys

sys.dont_write_bytecode = True
GAME = Path(__file__).resolve().parents[3]
KEYS = ('ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown')

RESET = """() => { const w = G.world, c = w.fight;
  for (const o of w.stage.actors) if (o.id && /^reflection_/.test(o.id)) { o.hp = 20; o.dead = false; o.remove = false; }
  for (const r of c.data.reflections) if (r.kind === 'mirror' || r.kind === 'window') r.dead = false; }"""
PLACE = """([x, y, f]) => { const p = G.world.player; p.x = x; p.y = y; p.vx = 0; p.vy = 0; p.facing = f; p.atk = null; p.tele = null; p.stunT = 0; p.invuln = 0; p.state = 'idle'; }"""
GLASS = """(id) => { const o = G.world.stage.actors.find(a => a.id === id); return { hp: o.hp, dead: !!o.dead }; }"""
REFLECT = """() => (G.dbg.snapshot().fightHint.activeReflections || []).map(r => r.kind)"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=GAME / 'tools' / '_playtest' / 'ch4_hanged_glass')
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    from playwright.sync_api import sync_playwright
    errors, rows = [], []

    def check(ok, name, **detail):
        rows.append({'ok': bool(ok), 'name': name, **detail})
        print(('通过 ' if ok else '失败 ') + name + ' ' + json.dumps(detail, ensure_ascii=False), flush=True)
        if not ok:
            errors.append(name)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=['--autoplay-policy=no-user-gesture-required'])
        page = browser.new_page(viewport={'width': 1280, 'height': 720})
        page.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))
        page.goto((GAME / 'index.html').as_uri() + '?autotest=1', wait_until='load')
        page.wait_for_function('() => G.booted && G.ui.menu && G.DEV && G.DEV.ch4Hanged', timeout=40000)
        page.evaluate('() => { G.CHAPTERS[4].run = G.DEV.ch4Hanged; }')

        def key(k, hold=.05):
            page.keyboard.down(k)
            page.wait_for_timeout(int(hold * 1000))
            page.keyboard.up(k)

        def menu(label):
            opts = page.evaluate('() => G.dbg.snapshot().menuItems || []')
            n = next(i for i, v in enumerate(opts) if label in (v or ''))
            idx = page.evaluate('() => G.ui.menu ? G.ui.menu.idx : 0') or 0
            page.wait_for_timeout(150)
            for _ in range(abs(n - idx)):
                key('ArrowDown' if n >= idx else 'ArrowUp')
                page.wait_for_timeout(80)
            key('Enter')
            page.wait_for_timeout(250)

        menu('选择章节')
        menu('第4章')
        page.wait_for_function('() => G.dbg.snapshot().combat && G.world.fight && G.world.fight.data && G.world.fight.data.reflections', timeout=40000)
        page.wait_for_timeout(800)
        page.evaluate('() => { G.world.player.minHp = 999; }')

        def swing(x, y, face, glass, presses=4):
            page.evaluate(RESET)
            page.evaluate(PLACE, [x, y, face])
            page.wait_for_timeout(100)
            # 真实输入：先点一下朝向键定朝向，再 J 连点（J1 → J2 一共 20 点生命，两下碎）
            key('ArrowRight' if face > 0 else 'ArrowLeft', .01)
            for _ in range(presses):
                key('j', .02)
                page.wait_for_timeout(260)
                if page.evaluate(GLASS, glass)['dead']:
                    break
            return page.evaluate(GLASS, glass)

        # 镜子（玻璃横向 23–73）：左边 / 右边 / 正下方，任何 y 都要打得碎
        for x, face in ((14, 1), (30, 1), (60, -1), (80, -1), (100, -1)):
            for y in (146, 158, 176):
                g = swing(x, y, face, 'reflection_mirror')
                check(g['dead'], f'镜子 x={x} y={y} 打得碎', glass=g)
        # 橱窗（玻璃横向 204–292）
        for x, face in ((184, 1), (215, 1), (250, -1), (290, -1)):
            for y in (146, 158, 176):
                g = swing(x, y, face, 'reflection_window')
                check(g['dead'], f'橱窗 x={x} y={y} 打得碎', glass=g)
        # 够不着：J 最远 44 px，连打时前两下各前冲 2 px、J3 前冲 16 px，一套连招最远能够到约 64 px；
        #   站在离玻璃边缘 > 64 px 的地方不能误碎（镜子右缘 73 → x=150，橱窗左缘 204 → x=130）
        g = swing(150, 160, -1, 'reflection_mirror', presses=3)
        check(not g['dead'] and g['hp'] == 20, '镜子 x=150 够不着不误碎', glass=g)
        g = swing(130, 160, 1, 'reflection_window', presses=3)
        check(not g['dead'] and g['hp'] == 20, '橱窗 x=130 够不着不误碎', glass=g)

        # 水洼（x 92，y 172，椭圆半宽 rx = 15 + 6，半高 10）：只看 puddle 一类
        def puddle(x, y):
            page.evaluate(PLACE, [x, y, 1])
            page.wait_for_timeout(60)
            return 'puddle' in page.evaluate(REFLECT)
        check(puddle(92, 170), '水洼正上站着被照到')
        check(puddle(78, 166), '水洼左缘内被照到')
        check(not puddle(92, 150), '从水洼上方绕过去（y 150）照不到')
        check(not puddle(92, 158), '水洼上方 14 px（y 158）照不到')
        check(not puddle(120, 170), '横向走开（x 120）照不到')
        check(not puddle(60, 170), '横向走开（x 60）照不到')
        browser.close()

    (args.out / 'result.json').write_text(json.dumps({'rows': rows, 'errors': errors}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'ok': not errors, 'failed': errors}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
