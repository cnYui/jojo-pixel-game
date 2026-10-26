r"""星尘试炼失败后的「看广告·全员复活」冒烟：用假 G.ads 走三条分支，不依赖 233 SDK。

    python -B tools\dev\full\test_trial_revive.py [--out tools\_playtest\trial_revive]

每条分支都新开一个浏览器上下文（存档互不影响）：编队承太郎 + 波鲁纳雷夫，第 1 关让波鲁纳雷夫先倒、
再让承太郎倒下触发失败，然后按假广告的返回检查菜单 / 复活 / 存档。战斗本身不靠 autowin，直接改 hp。
"""
import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import json  # noqa: E402
from pathlib import Path  # noqa: E402

GAME = Path(__file__).resolve().parents[3]
SQUAD = ['jotaro', 'polnareff']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(GAME / 'tools' / '_playtest' / 'trial_revive'))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    url = (GAME / 'index.html').as_uri() + '?autotest=1'

    checks, errors, shots = [], [], []

    def check(ok, what, **kw):
        checks.append({'ok': bool(ok), 'what': what, **kw})
        print(('ok  ' if ok else 'BAD ') + what + ('  ' + json.dumps(kw, ensure_ascii=False) if kw and not ok else ''), flush=True)

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=['--autoplay-policy=no-user-gesture-required'])

        def new_page(tag):
            ctx = browser.new_context(viewport={'width': 1280, 'height': 720}, device_scale_factor=1)
            page = ctx.new_page()
            page.on('console', lambda m: errors.append({'case': tag, 'kind': 'console_' + m.type, 'text': m.text})
                    if m.type in ('error', 'warning') else None)
            page.on('pageerror', lambda e: errors.append({'case': tag, 'kind': 'pageerror', 'text': str(e)}))
            page.goto(url, wait_until='load')
            page.wait_for_function('() => G.booted && G.ui && G.ui.menu', timeout=60000)
            page.evaluate('''() => { G.store.set('progress', { v: 1, max: 12, last: 12, clear: true,
              done: [0,1,2,3,4,5,6,7,8,9,10,11,12], play: 100, at: Date.now() }); G.store.reload(); }''')
            # 统计试炼事件 / 广告调用，后面直接读
            page.evaluate('''() => {
              window.__trialEvents = [];
              const orig = G.ach.emit.bind(G.ach);
              G.ach.emit = (type, data) => { window.__trialEvents.push(type); return orig(type, data); };
              window.__adCalls = 0;
            }''')
            return ctx, page

        def key(page, k, wait=90):
            page.keyboard.press(k)
            page.wait_for_timeout(wait)

        def snap(page):
            return page.evaluate('''() => {
              const T = G.TRIAL, run = T.run, pa = G.party.get('polnareff');
              return {
                active: T.active, stage: run && run.stage, alive: run && run.alive.slice(),
                downs: run && run.downs, revives: run && run.revives, fails: T.save.fails,
                menu: G.ui.menu ? { options: G.ui.menu.options.slice(), idx: G.ui.menu.idx } : null,
                notice: G.ui.noticeBox ? (G.ui.noticeBox.text || G.ui.noticeBox.title || '') : null,
                events: window.__trialEvents.slice(), adCalls: window.__adCalls,
                adScene: window.__adScene || null,
                polnareff: pa ? { inParty: G.party.members.indexOf(pa) >= 0, hp: pa.hp, maxHp: pa.maxHp,
                  remove: !!pa.remove, alpha: pa.alpha, dead: !!pa.dead } : null,
                r: window.__r || null,
              };
            }''')

        def start_trial(page):
            page.evaluate('(sq) => { window.__r = null; G.playTrial(sq).then(() => { window.__r = "done"; },'
                          ' (e) => { window.__r = "err:" + (e && e.message); }); }', SQUAD)
            page.wait_for_function('() => G.world && G.world.combat && !G.world.cine && G.world.fight && G.TRIAL.run'
                                   ' && G.TRIAL.run.stage === 1', timeout=60000)

        def fail_stage(page):
            # 波鲁纳雷夫先倒（_fall 会把他从 alive / party 名单摘掉），再让承太郎倒下触发试炼失败。
            page.evaluate('() => { const a = G.party.get("polnareff"); if (a) a.hp = 0; }')
            page.wait_for_function('() => G.TRIAL.run && G.TRIAL.run.alive.indexOf("polnareff") < 0', timeout=15000)
            page.evaluate('() => { const a = G.party.get("jotaro"); if (a) a.hp = 0; }')
            page.wait_for_function('() => G.ui.noticeBox && /试炼失败/.test(G.ui.noticeBox.title || "")', timeout=20000)

        def close_notice(page, min_t=0.7):
            page.wait_for_function('(t) => G.ui.noticeBox && G.ui.noticeBox.t >= t', arg=min_t, timeout=20000)
            key(page, 'Enter', 120)
            page.wait_for_function('() => !G.ui.noticeBox', timeout=10000)

        def wait_menu(page, n):
            page.wait_for_function('(n) => G.ui.menu && G.ui.menu.options && G.ui.menu.options.length === n',
                                   arg=n, timeout=15000)
            return page.evaluate('() => ({ options: G.ui.menu.options.slice(), idx: G.ui.menu.idx })')

        def pick(page, label):
            page.wait_for_timeout(120)
            m = page.evaluate('() => G.ui.menu ? { options: G.ui.menu.options.slice(), idx: G.ui.menu.idx } : null')
            hit = [i for i, v in enumerate(m['options']) if label in v]
            if not hit:
                raise AssertionError('菜单里找不到 %r：%r' % (label, m['options']))
            idx = m['idx']
            for _ in range(abs(hit[0] - idx)):
                key(page, 'ArrowDown' if hit[0] > idx else 'ArrowUp', 80)
            key(page, 'Enter', 200)

        # ---------------------------------------------------------------- 1. 广告可用 + 看完：复活并重打第 1 关
        ctx, page = new_page('rewarded')
        try:
            page.evaluate('''() => {
              G.ads = { supported: async () => true,
                watch: async (scene) => { window.__adCalls++; window.__adScene = scene;
                  return { success: true, reason: 'rewarded', technical: false }; } };
            }''')
            start_trial(page)
            fail_stage(page)
            close_notice(page, 1.25)
            m = wait_menu(page, 4)
            check(m['options'] == ['重新开始', '看广告·全员复活', '重新编队', '回到标题'], '广告可用时菜单四项，复活在第二项', options=m['options'])
            check(m['idx'] == 0, '菜单光标默认停在「重新开始」', idx=m['idx'])
            before = snap(page)
            check(before['alive'] == [], '失败时全员已倒下（alive 为空）', alive=before['alive'])
            check(before['fails'] == 0 and 'trial_over' not in before['events'], '选复活前没有提前记失败', fails=before['fails'], events=before['events'])
            pick(page, '看广告·全员复活')
            page.wait_for_function('() => G.TRIAL.run && G.TRIAL.run.revives === 1', timeout=15000)
            page.wait_for_function('''() => { const a = G.party.get('polnareff');
              return !!a && G.party.members.indexOf(a) >= 0 && !a.remove && a.hp === a.maxHp; }''', timeout=20000)
            s = snap(page)
            check(s['alive'] == SQUAD, '复活后 alive 回到两人', alive=s['alive'])
            check(s['stage'] == 1, '复活仍从第 1 关重打（关卡号不错乱）', stage=s['stage'])
            check(s['fails'] == 0, '复活不增加 save.fails', fails=s['fails'])
            check('trial_over' not in s['events'], '复活不触发 trial_over', events=s['events'])
            check('trial_revive' in s['events'], '复活触发 trial_revive', events=s['events'])
            check(s['downs'] == 2, '倒下人数未被复活洗白', downs=s['downs'])
            check(s['adCalls'] == 1 and s['adScene'] == 'trial_revive', '广告按 trial_revive 场景调用', calls=s['adCalls'], scene=s['adScene'])
            check(s['polnareff'] and s['polnareff']['inParty'] and not s['polnareff']['remove']
                  and s['polnareff']['hp'] == s['polnareff']['maxHp'] and s['polnareff']['alpha'] == 1,
                  '波鲁纳雷夫重新出现在队伍里且满血', polnareff=s['polnareff'])
            page.screenshot(path=str(out / '1_rewarded_revive.png'))
            shots.append('1_rewarded_revive.png')
        finally:
            ctx.close()

        # ---------------------------------------------------------------- 2. 广告可用 + 玩家关掉：回菜单，不复活
        ctx, page = new_page('closed')
        try:
            page.evaluate('''() => {
              G.ads = { supported: async () => true,
                watch: async (scene) => { window.__adCalls++; window.__adScene = scene;
                  return { success: false, reason: 'closed', technical: false }; } };
            }''')
            start_trial(page)
            fail_stage(page)
            close_notice(page, 1.25)
            wait_menu(page, 4)
            pick(page, '看广告·全员复活')
            page.wait_for_function('() => G.ui.noticeBox && /广告没有看完/.test(G.ui.noticeBox.text || "")', timeout=15000)
            s = snap(page)
            check('广告没有看完，没有复活' in (s['notice'] or ''), '关掉广告后提示没有复活', notice=s['notice'])
            check(s['alive'] == [], '关掉广告不复活', alive=s['alive'])
            check(not s['revives'], '关掉广告不增加 revives', revives=s['revives'])
            check(s['fails'] == 0 and 'trial_over' not in s['events'], '关掉广告不记失败', fails=s['fails'], events=s['events'])
            close_notice(page)
            m = wait_menu(page, 4)
            check(m['idx'] == 0, '回到菜单时光标仍在第一项', idx=m['idx'])
            check(snap(page)['alive'] == [] and not snap(page)['revives'], '回菜单后仍没复活')
            page.screenshot(path=str(out / '2_closed_back_to_menu.png'))
            shots.append('2_closed_back_to_menu.png')
        finally:
            ctx.close()

        # ---------------------------------------------------------------- 3. 没有 G.ads：菜单还是三项，选回标题才记失败
        ctx, page = new_page('no_ads')
        try:
            page.evaluate('() => { G.ads = undefined; }')
            start_trial(page)
            fail_stage(page)
            close_notice(page, 1.25)
            m = wait_menu(page, 3)
            check(m['options'] == ['重新开始', '重新编队', '回到标题'], '没有广告时菜单保持三项', options=m['options'])
            check(m['idx'] == 0, '没有广告时光标仍在第一项', idx=m['idx'])
            s = snap(page)
            check(s['fails'] == 0 and 'trial_over' not in s['events'], '打开失败菜单时还没记失败', fails=s['fails'], events=s['events'])
            pick(page, '回到标题')
            page.wait_for_function('() => window.__r === "done" || (window.__r || "").startsWith("err:")', timeout=20000)
            s = snap(page)
            check(s['r'] == 'done', '回标题流程正常结束', r=s['r'])
            check(s['fails'] == 1, '最终放弃才把 save.fails 加一', fails=s['fails'])
            check('trial_over' in s['events'], '最终放弃才触发 trial_over', events=s['events'])
        finally:
            ctx.close()

        browser.close()

    ok = all(c['ok'] for c in checks) and not [e for e in errors if e['kind'] == 'pageerror']
    res = {'url': url, 'checks': checks, 'errors': errors, 'shots': shots}
    (out / 'result.json').write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'checks': len(checks), 'bad': [c['what'] for c in checks if not c['ok']],
                      'pageerrors': [e for e in errors if e['kind'] == 'pageerror'], 'out': str(out)}, ensure_ascii=False))
    for e in errors[:10]:
        print(' ', e['kind'], e['text'][:300])
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
