"""包 4 验收：隔离页与真 core/res/input 各跑一次，同一组行为断言，保存截图和 JSON。

python -B tools/dev/p4/test_world.py
真底座模式仍隔离 combat/UI/story，不能替代全游戏集成验收。
"""
import sys

sys.dont_write_bytecode = True

import argparse
import base64
import json
import os
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
GAME = HERE.parents[2]
OUT = HERE / '_out'
RESULTS = []
ERRORS = []


def check(name, ok, detail=None):
    RESULTS.append({'name': name, 'ok': bool(ok), 'detail': detail})
    print(('通过 ' if ok else '失败 ') + name, flush=True)


def runtime_page():
    target = HERE / '_gen' / 'runtime.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    scripts = [
        '../_fixture/data_meta.js', '../_fixture/img_core.js', '../_fixture/img_bg_fixture.js',
        '../../../../engine/core.js', '../../../../engine/res.js', '../../../../engine/input.js',
        '../../../../engine/px.js', '../stub_fx.js', '../../../../engine/atlas.js', '../../../../engine/bg.js',
        '../../../../engine/world.js', '../../../../engine/stand.js', '../../../../engine/party.js',
        '../stub_game.js', '../runtime_adapter.js', '../demo.js',
    ]
    target.write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>包4真底座联接</title>'
                      '<body style="margin:0;background:#000"><canvas id="screen"></canvas>'
                      + ''.join(f'<script src="{s}"></script>' for s in scripts) + '</body></html>', encoding='utf-8')
    return target


def run(browser, mode, target):
    ctx = browser.new_context(viewport={'width': 1280, 'height': 720}, device_scale_factor=1)
    page = ctx.new_page()
    page.on('console', lambda msg: ERRORS.append({'mode': mode, 'type': msg.type, 'text': msg.text}) if msg.type in ('warning', 'error') else None)
    page.on('pageerror', lambda err: ERRORS.append({'mode': mode, 'type': 'pageerror', 'text': str(err)}))
    page.goto(target.as_uri() + '?autotest=1')
    page.wait_for_function('window.P4 && window.G && G.party')
    page.evaluate('() => P4.init()')
    detail = {}

    def case(method):
        result = page.evaluate('(name) => P4[name]()', method)
        shot = result.pop('sheet', None)
        if shot:
            path = OUT / f'{mode}_{method}.png'
            path.write_bytes(base64.b64decode(shot.split(',', 1)[1]))
            result['screenshot'] = str(path.relative_to(GAME))
        detail[method] = result
        return result

    r = case('resolveTable')
    check(f'{mode}：15角色逻辑动作解析与 bare 变体', len(r['table']) == 17 and all('undefined' not in x for vals in r['table'].values() for x in vals.values()), r)
    check(f'{mode}：跨场景头像与缺头像诊断', all(v > 0 for k, v in r['heads'].items() if 'size' not in k) and 'kakyoin:no_such_face' in r['missingHead'], r['heads'])

    r = case('walk30')
    check(f'{mode}：30秒轨迹跟随与地图边界', r['inBounds'] and r['minPair'] >= 4 and r['maxLag'] < 221, r)
    check(f'{mode}：单屏4人与宽地图全员显示', len(r['visibleSmall']) == 4 and r['maxSmall'] == 3 and len(r['visibleWide']) == 5, r)

    r = case('swap5')
    check(f'{mode}：5次换人保留 HP/能量/Actor/替身', r['same'] and len(set(r['leaders'])) == 4, r)
    check(f'{mode}：镜头缓动且禁队长只提示一次', r['maxCamStep'] < 20 and 'kakyoin' not in r['skipSeq'] and len(r['hints']) == 1 and r['afterLead4'] != 'kakyoin' and r['afterLead4b'] == 'kakyoin', r)

    r = case('standFrames')
    check(f'{mode}：替身召唤收回/时停/站位/自动收回', r['modes'] == ['hidden'] * 4 and r['frozenOk'] and r['kaFront'] == 20 and r['autoRecall'][0] == 'idle' and r['autoRecall'][-1] == 'hidden', r)

    r = case('effects')
    check(f'{mode}：像素透明缓存与残影', r['ditherHitRate'] >= .88 and r['ghosts'] == 4, r)

    r = case('zoomShake')
    check(f'{mode}：W6推镜/收镜与操作角色取景', abs(r['ks'][-1] - 1.3) < .02 and abs(r['during'] - 1.3) < .02 and abs(r['back'][-1] - 1) < .02 and 64 <= r['playerScreenX'] <= 256, r)

    r = case('interact')
    check(f'{mode}：E调查与 U标签/冷却/换队长', r['near1'] == '杂志' and 'use:mag:jotaro' in r['used'] and r['ready1'] and r['look1'] == 'fly' and 'fly:jotaro' in r['looked'] and 'vent:kakyoin' in r['looked'] and r['ev1'] == 1 and 0 < r['cd1'] < 1, r)
    check(f'{mode}：NPC亮替身/触发一次/可破坏物', r['stood'] == ['holly<jotaro'] and len(r['defaultReact']) == 1 and r['trig'] == ['tz'] and r['breaks'] == ['pipe'] and r['pipe']['team'] == 'object' and r['pipe']['hp'] == 0 and r['pipe']['frozen'] == 1, r)

    r = case('bgTypes')
    check(f'{mode}：背景类型全部有实现', not r['badTypes'], r)
    case('overPass')
    r = case('perf')
    check(f'{mode}：30角色 canvas pass 平均小于5ms', r['canvasAvgMs'] < 5, r)
    r = case('invariants')
    for key in ['entryBound', 'freeBound', 'stopStep', 'stopTimers', 'resumed', 'frozenSeparation', 'frozenTimers', 'movableSeparation', 'kitInherited', 'objectKitInherited', 'override']:
        check(f'{mode}：回归 {key}', r[key], r)
    check(f'{mode}：自由移动绕过战斗锁保留地图边界', [r['battleLeft'], r['battleRight'], r['freeLeft']] == [110, 210, 8], r)
    check(f'{mode}：W.slow只慢敌人且 ticks 保留world dt', all(abs(v - (1 / 240 if i == 1 else 1 / 60)) < .00001 for i, v in enumerate(r['clockDelta'])) and abs(r['tickDt'] - 1 / 60) < .00001, r)
    diagnostics = page.evaluate('() => P4.dbg()')
    check(f'{mode}：图片零缺失和无剧情异常', not diagnostics['missingImg'] and not any(x[0] == 'error' for x in diagnostics['log']), diagnostics)
    page.wait_for_timeout(100)
    ctx.close()
    return detail


def main():
    ap = argparse.ArgumentParser(description='包4世界验收')
    ap.add_argument('--mode', choices=['all', 'isolated', 'runtime'], default='all')
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, '-B', str(HERE / 'make_fixture.py')], check=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    from playwright.sync_api import sync_playwright
    start = time.time()
    detail = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        if args.mode in ('all', 'isolated'):
            detail['isolated'] = run(browser, 'isolated', HERE / 'world_demo.html')
        if args.mode in ('all', 'runtime'):
            detail['runtime'] = run(browser, 'runtime', runtime_page())
        browser.close()
    check('控制台零 warning/error/pageerror', not ERRORS, ERRORS)
    fails = [r for r in RESULTS if not r['ok']]
    output = {'ok': not fails, 'results': RESULTS, 'fails': fails, 'console': ERRORS, 'detail': detail, 'sec': round(time.time() - start, 2)}
    (OUT / 'test_world.json').write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"{len(RESULTS) - len(fails)}/{len(RESULTS)} 通过，用时 {output['sec']} 秒，结果 {OUT / 'test_world.json'}")
    sys.exit(bool(fails))


if __name__ == '__main__':
    main()
