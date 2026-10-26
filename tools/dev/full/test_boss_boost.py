"""Boss 难度系数冒烟：从「力量」单场 Boss 战直接开打，在页面里改 CFG.bossHpMul / bossDmgMul 对比伤害。

不跑整章，也不当通关证据：只验证系数 1 时伤害回到原值、系数 1.5 时玩家打 Boss 等效血量约 ×1.5、
Boss 打玩家约 ×1.5、小怪伤害不变，以及 Boss 战里 att 为空的机关伤害也吃到 bossDmgMul。
两条线的默认系数不同（用户 2026-10-25 定的）：小红书线（游戏源码）默认 1，233 线默认 1.5，所以默认值用 --expect 对：
  小红书线（游戏源码）：python -B tools\\dev\\full\\test_boss_boost.py
  233 线：先 python -B 233乐园\\overlay.py --make-dev 做一份 233 变体，再
         python -B tools\\dev\\full\\test_boss_boost.py --root <那份变体> --expect 1.5
选项：[--headed] [--out tools\\_playtest\\boss_boost]
"""
from pathlib import Path
import argparse
import json
import sys
import traceback

sys.dont_write_bytecode = True
GAME = Path(__file__).resolve().parents[3]
OUT = GAME / 'tools' / '_playtest' / 'boss_boost'

# 固定 120 点探针招：不经过命中判定，直接走 G.combat.hit 的同一串伤害乘积，避免 Boss AI / 站位波动干扰对比。
PROBE_JS = r"""() => {
  const G = window.G, C = G.combat, W = G.world, c = W.fight, p = W.player, boss = c && c.boss;
  if (!p || !boss) return { error: '没有找到玩家或 Boss' };
  const cfg = { hp: C.CFG.bossHpMul, dmg: C.CFG.bossDmgMul };
  const probe = { dmg: 120, slot: 'special', guard: 'none', push: 0, poiseDmg: 0, stop: 0, sfxHit: null, word: null };
  const hazard = { dmg: 120, slot: 'enemy', guard: 'none', push: 0, poiseDmg: 0, stop: 0, sfxHit: null, word: null };
  // 关掉 AI、阶段停帧和受击钩子；dmgScale / 放水也归 1，避免章节自带的难度缩放混进 Boss 系数对比。
  boss.brain = () => false; boss.moves = []; boss.cool = 1e9;
  c.assist = false; c.assistLevel = 0; c.spec.dmgScale = 1;
  const resetP = () => {
    p.hp = 9999; p.dead = false; p.remove = false; p.state = 'idle'; p.stunT = 0; p.iframe = 0; p.invuln = 0;
    p.parryUntil = -Infinity; p.breakT = 0; p.chainT = 0; p.nextMul = 1; p.dmgMul = 1; p.dmgIn = 1;
    p.dmgOut = 1; p.atk = null; p.tele = null; p.rush = null; p.onHitBy = () => null;
  };
  const resetE = e => {
    e.hp = 9999; e.dead = false; e.remove = false; e.state = 'idle'; e.stunT = 0; e.iframe = 0; e.invuln = 0;
    e.parryUntil = -Infinity; e.breakT = 0; e.chainT = 0; e._lastHit = null; e.nextMul = 1; e.dmgMul = 1;
    e.dmgIn = 1; e.dmgOut = 1; e.armor = false; e.atk = null; e.tele = null; e.onHitBy = () => null;
  };
  resetP(); resetE(boss);
  // 真实生成一只 team=enemy、boss=false 的小怪：用它打玩家、也让玩家打它。
  const mob = new G.Actor('strength', p.x + 80, p.y, { team: 'enemy', boss: false, hp: 9999, kit: 'e_strength', speed: 0 });
  mob.brain = () => false; mob.atk = null; mob.onHitBy = () => null; W.stage.actors.push(mob);
  resetE(mob);

  const measure = (hpMul, dmgMul) => {
    C.CFG.bossHpMul = hpMul; C.CFG.bossDmgMul = dmgMul;
    resetP(); resetE(boss);
    let before = boss.hp; const rBoss = C.hit(p, boss, probe, { first: true }); const bossLoss = before - boss.hp;
    resetP();
    before = p.hp; const rPlayer = C.hit(boss, p, probe, { first: true }); const playerHit = before - p.hp;
    resetP();
    before = p.hp; const rMinion = C.hit(mob, p, probe, { first: true }); const minionHit = before - p.hp;
    resetE(mob);
    before = mob.hp; const rMob = C.hit(p, mob, probe, { first: true }); const minionLoss = before - mob.hp;
    resetP();
    before = p.hp; const rHazard = C.hit(null, p, hazard, { hazard: true, first: true, parryAllowed: false }); const hazardHit = before - p.hp;
    return { bossLoss, playerHit, minionHit, minionLoss, hazardHit,
      returned: { boss: rBoss.dmg, player: rPlayer.dmg, minion: rMinion.dmg, mob: rMob.dmg, hazard: rHazard.dmg } };
  };
  const base = measure(1, 1);
  // 加强机制固定按 1.5 验：默认值不论是 1（小红书线）还是 1.5（233 线），机制本身都得对；默认值另有一条检查。
  const boosted = measure(1.5, 1.5);
  // 放水中系数不生效：只剩 assistTotal 的减伤（第 1 档 0.7），加强不能叠在放水上。
  c.assist = true; c.assistLevel = 1;
  const assisted = measure(1.5, 1.5);
  c.assist = false; c.assistLevel = 0;
  return { cfg, probeDmg: probe.dmg, base, boosted, assisted, assistK: C.assistTotal(1),
    boss: { cid: boss.cid, hp: boss.maxHp, boss: !!boss.boss },
    mob: { cid: mob.cid, boss: !!mob.boss, team: mob.team } };
}"""


def close_enough(actual, expected, tolerance=1):
    return abs(actual - expected) <= tolerance


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--headed', action='store_true', help='显示浏览器窗口，方便现场看')
    parser.add_argument('--out', type=Path, default=OUT, help='报告和截图目录')
    parser.add_argument('--root', type=Path, default=GAME, help='游戏文件夹（默认开发目录 = 小红书线；233 变体用 233乐园\\overlay.py --make-dev 做）')
    parser.add_argument('--expect', type=float, default=1.0, help='这份游戏 CFG.bossHpMul / bossDmgMul 的默认值：小红书线 1（默认），233 线 1.5')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    report = {'ok': False, 'checks': [], 'values': {}, 'errors': [], 'warnings': []}

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=not args.headed, args=['--autoplay-policy=no-user-gesture-required'])
            page = browser.new_page(viewport={'width': 1280, 'height': 720}, device_scale_factor=1)
            page.on('pageerror', lambda e: report['errors'].append({'kind': 'pageerror', 'text': str(e)}))
            # 控制台 warning 只记录（无头音频等环境差异不应让数值测试失败），真正的脚本错误才算失败。
            page.on('console', lambda m: (report['errors'] if m.type == 'error' else report['warnings']).append(
                {'kind': 'console_' + m.type, 'text': m.text}) if m.type in ('error', 'warning') else None)
            page.goto((args.root / 'index.html').as_uri() + '?autotest=1', wait_until='load')
            page.wait_for_function('() => G.booted && G.playFrom && G.CHAPTERS && G.DEV && G.DEV.ch2Strength', timeout=30000)
            # 和 dev_fight.py 一样把第 2 章的入口换成单场 Boss 战；直接 playFrom 省掉菜单按键，但仍走正式章节启动流程。
            page.evaluate('() => { G.CHAPTERS[2].run = G.DEV.ch2Strength; G.playFrom(2); }')
            page.wait_for_function(
                '() => { const w = G.world; return !!(w && w.fight && w.fight.id === "b04_strength" && '
                'w.fight.boss && w.player && w.combat && !w.cine); }', timeout=90000)
            page.screenshot(path=str(args.out / 'boss_start.png'))
            values = page.evaluate(PROBE_JS)
            report['values'] = values
            browser.close()
    except Exception:
        report['errors'].append({'kind': 'tester_error', 'text': traceback.format_exc()})

    values = report['values']
    if values and not values.get('error'):
        try:
            cfg, base, boosted = values['cfg'], values['base'], values['boosted']
            dmg = values['probeDmg']
            checks = [
                ('默认系数是 %g / %g（小红书线 1，233 线 1.5）' % (args.expect, args.expect),
                 cfg['hp'] == args.expect and cfg['dmg'] == args.expect, cfg),
                ('系数 1 时玩家打 Boss 伤害回到原值', base['bossLoss'] == dmg, base['bossLoss']),
                ('系数 1 时 Boss 打玩家伤害回到原值', base['playerHit'] == dmg, base['playerHit']),
                ('系数 1.5 时玩家打 Boss 的损失约为原值 1/1.5',
                 close_enough(boosted['bossLoss'], dmg / 1.5) and 0.6 <= boosted['bossLoss'] / dmg <= 0.72,
                 boosted['bossLoss']),
                ('系数 1.5 时 Boss 打玩家伤害约为 1.5 倍',
                 close_enough(boosted['playerHit'], dmg * 1.5) and 1.4 <= boosted['playerHit'] / dmg <= 1.6,
                 boosted['playerHit']),
                ('小怪打玩家伤害不受影响', base['minionHit'] == boosted['minionHit'] == dmg,
                 [base['minionHit'], boosted['minionHit']]),
                ('玩家打小怪伤害不受影响', base['minionLoss'] == boosted['minionLoss'] == dmg,
                 [base['minionLoss'], boosted['minionLoss']]),
                ('Boss 战里无攻击方的机关伤害吃到 bossDmgMul',
                 close_enough(boosted['hazardHit'], dmg * 1.5) and 1.4 <= boosted['hazardHit'] / dmg <= 1.6,
                 [base['hazardHit'], boosted['hazardHit']]),
                ('放水中玩家打 Boss 不再除以 bossHpMul（回到原伤害）', values['assisted']['bossLoss'] == dmg, values['assisted']['bossLoss']),
                ('放水中 Boss 打玩家只剩放水减伤、没有 bossDmgMul',
                 close_enough(values['assisted']['playerHit'], dmg * values['assistK']), [values['assisted']['playerHit'], values['assistK']]),
                ('放水中 Boss 战机关伤害同样只剩放水减伤（放水只作用于有攻击方的伤害，机关保持原值）',
                 values['assisted']['hazardHit'] == dmg, values['assisted']['hazardHit']),
                ('探针实际走的是同一招式的伤害乘积',
                 all(v == dmg for v in (base['returned']['boss'], base['returned']['player'],
                                        base['returned']['minion'], base['returned']['mob'], base['returned']['hazard'])),
                 base['returned']),
                ('目标确实是真 Boss、小怪不是 Boss',
                 values['boss']['boss'] and values['boss']['cid'] == 'strength'
                 and not values['mob']['boss'] and values['mob']['team'] == 'enemy',
                 {'boss': values['boss'], 'mob': values['mob']}),
            ]
            for name, ok, detail in checks:
                report['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})
                print(('通过 ' if ok else '失败 ') + name + ' ' + json.dumps(detail, ensure_ascii=False), flush=True)
        except Exception:
            report['errors'].append({'kind': 'check_error', 'text': traceback.format_exc()})
    elif values:
        report['errors'].append({'kind': 'probe_error', 'text': values['error']})

    report['ok'] = bool(report['checks']) and all(c['ok'] for c in report['checks']) and not report['errors']
    (args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'ok': report['ok'], 'errors': len(report['errors']), 'out': str(args.out)}, ensure_ascii=False))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
