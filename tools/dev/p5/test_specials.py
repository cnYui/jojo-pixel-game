"""六人大招的方向、距离、边界及剧情地火回归，保存独立证据。"""
import argparse
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--out', type=Path, default=HERE / '_specials_out')
parser.add_argument('--baseline', action='store_true')
args = parser.parse_args()
args.out.mkdir(parents=True, exist_ok=True)
errors = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type in ('warning', 'error') else None)
    page.goto((HERE / 'specials.html').as_uri())
    page.evaluate('Specials.init()')
    matrix = page.evaluate('Specials.matrix()')
    extras = page.evaluate('Specials.extras()')
    boundaries = page.evaluate('Specials.boundaries()')
    for cid, frames in [('jotaro', 40), ('kakyoin', 24), ('avdol', 28), ('polnareff', 30), ('joseph', 18), ('iggy', 26)]:
        page.evaluate('(cid)=>Specials.start(cid,{dx:-80,facing:1})', cid)
        page.evaluate('(n)=>Specials.step(n)', frames)
        page.screenshot(path=str(args.out / (cid + '.png')))
    browser.close()

checks = []
for r in matrix:
    # 安卡改为水平直飞后，纵深偏离 35 像素的目标应躲开。
    depth_miss = r['cid'] == 'avdol' and r['mode'] == 'depth'
    damage_ok = r['damage'] == 0 if depth_miss else r['damage'] > 0
    ok = damage_ok and r['done'] and r['result'] and r['energy'] == 0 and not r['cine'] and not r['liveShots'] and not r['fx'] and not r['errors']
    checks.append({'name': f"{r['cid']} {r['side']} {r['mode']}", 'ok': bool(ok), 'damage': r['damage']})
checks.extend([
    {'name': '平面最近目标', 'ok': extras['pick']['intended']},
    {'name': '零速度弹体保持原地', 'ok': extras['speedZero'] == {'dx': 0, 'dy': 0}},
    {'name': '剧情四道安卡被斩、地火命中且不可斩', 'ok': extras['crossfire']['cut'] == 4 and extras['crossfire']['result'] and extras['crossfire']['damage'] > 0 and not extras['crossfire']['groundCut'] and extras['crossfire']['groundDx'] == 0},
    {'name': '空场释放后恢复、弹体清空', 'ok': all(r['done'] and r['result'] and not r['cine'] and not r['liveShots'] and not r['errors'] for r in extras['noTargets'])},
    {'name': '切场取消后无旧任务和弹体', 'ok': extras['cancel']['done'] and not extras['cancel']['result'] and not extras['cancel']['liveShots']},
    {'name': '控制台和绘制无异常', 'ok': not errors},
])
for r in boundaries['walls']:
    checks.append({'name': f"{r['cid']} 贴墙 {r['side']}", 'ok': 8 <= r['lo'] <= r['hi'] <= 632 and r['damage'] > 0 and r['done'] and r['result'] and not r['cine'] and not r['fx'] and not r['errors']})
for r in boundaries['outOfRange']:
    checks.append({'name': f"{r['cid']} 超出射程不强制命中", 'ok': r['damage'] == 0 and r['done'] and r['result'] and not r['cine'] and not r['liveShots'] and not r['errors']})
checks.extend([
    {'name': '追踪弹体保持原目标', 'ok': boundaries['locked']},
    {'name': '原目标移除后重新追踪', 'ok': boundaries['retargeted']},
    {'name': '伊奇范围伤害保留高度判定', 'ok': boundaries['heightHits'] == 0},
    {'name': 'Boss免伤阶段保留', 'ok': boundaries['immune']['damage'] == 0},
])
report = {'ok': all(r['ok'] for r in checks), 'checks': checks, 'matrix': matrix, 'extras': extras, 'boundaries': boundaries, 'errors': errors}
(args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
for r in checks:
    if not r['ok']:
        print('失败 ' + json.dumps(r, ensure_ascii=False))
print(f"{sum(r['ok'] for r in checks)}/{len(checks)} 通过", flush=True)
sys.exit(0 if args.baseline or report['ok'] else 1)
