"""打击感验收（重击闪白 / 全局顿帧冻结 + 缓出 / 击退缓出 + 受击压扁）：固定 60 Hz 逐步推进，页面用生产的时钟、输入、战斗、角色。

    python -B tools/dev/p5/test_hitfeel.py              # 第三部引擎（engine/）和第四部引擎（第四部/游戏/engine/）各跑一遍
    python -B tools/dev/p5/test_hitfeel.py --engine third

“legacy”模式 = G.HITSTOP.freeze 设成 1 = 旧的二值冻结，用来和缓出模式并排比窗口（基线 779ed40 上跑同一份页面脚本，legacy 的数字和基线逐项一致）。
输出：tools/dev/p5/_out/test_hitfeel_<engine>.json
"""
import sys
sys.dont_write_bytecode = True
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / '_out'
OUT.mkdir(exist_ok=True)
results = []


def check(name, ok, detail=''):
    results.append({'name': name, 'ok': bool(ok), 'detail': detail})
    print(('  ok   ' if ok else '  FAIL ') + name + ((' — ' + json.dumps(detail, ensure_ascii=False)[:300]) if detail != '' else ''), flush=True)


def run_engine(pw, which):
    html = HERE / ('arena_hf.html' if which == 'third' else 'arena4_hf.html')
    print('== 引擎：' + ('第三部 engine/' if which == 'third' else '第四部 第四部/游戏/engine/'))
    b = pw.chromium.launch(headless=True)
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errors = []
    pg.on('console', lambda m: errors.append(m.text) if m.type in ('warning', 'error') else None)
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.set_default_timeout(300000)
    pg.goto(html.as_uri())
    pg.evaluate('HF.init()')
    tag = which + '：'
    raw = {}

    # ---- ② 顿帧曲线
    hs = pg.evaluate('HF.hitstop()')
    raw['hitstop'] = hs
    ok_steps = all(h['steps'] == h['n'] for h in hs)
    check(tag + '顿帧每档总步数不变（1…30 帧，冻结 + 缓出和旧的二值冻结都是 n 步）', ok_steps, [(h['n'], h['mode'], h['steps']) for h in hs if h['steps'] != h['n']])
    check(tag + 'legacy（freeze=1）整段倍率 0，和旧行为一致', all(h['sum'] == 0 and h['frozen'] == h['n'] for h in hs if h['mode'] == 'legacy'), '')
    cv = [h for h in hs if h['mode'] == 'curve']
    check(tag + '缓出模式：第一步一定冻结、最后一步倍率 < 1、缓出段单调上升、顿帧后第一步回到 1',
          all(h['mul'][0] == 0 and h['mul'][-1] < 1 and h['after'] == 1 and
              all(h['mul'][i] <= h['mul'][i + 1] + 1e-9 for i in range(len(h['mul']) - 1)) for h in cv), '')
    five = {h['n']: (h['frozen'], h['sum']) for h in cv if h['n'] in (6, 8, 12, 18)}
    check(tag + '常用档的冻结帧数：6 帧 = 冻 4 + 缓 2、8 = 冻 5 + 缓 3、12 = 冻 7 + 缓 5、18 = 冻 11 + 缓 7',
          [five[6][0], five[8][0], five[12][0], five[18][0]] == [4, 5, 7, 11], five)
    check(tag + '缓出段带走的世界时间（帧）：6 帧顿帧 < 1.1、8 帧 < 1.5、12 帧 < 2.3（窗口多走的上限）', five[6][1] < 1.1 and five[8][1] < 1.5 and five[12][1] < 2.3, five)

    # ---- ① 闪白 + 抖动 + 压扁
    tl = {}
    for key, expr in (('J3', 'HF.timeline("SP_J3")'), ('FIN', 'HF.timeline("SP_FIN")'), ('J1', 'HF.timeline("SP_J1")'), ('J3_reduce', 'HF.timeline("SP_J3", {reduce: true})'),
                      ('J3_legacy', 'HF.timeline("SP_J3", {legacy: true})')):
        tl[key] = pg.evaluate(expr)
    raw['timeline'] = tl
    for key in ('J3', 'FIN'):
        fr = tl[key]['frames']
        fl = [x['flash'] for x in fr[:12]]
        check(tag + key + ' 重击闪白：alpha 1.0 满亮 ≥ 3 帧再衰减到 0（≥ 2/60 s 一帧闪铁律）', fl[:3] == [1, 1, 1] and fl[3] < 1 and all(fl[i] >= fl[i + 1] for i in range(2, 11)) and fl[8] == 0, fl)
        sq = [x['i'] for x in fr if x['squash']]
        check(tag + key + ' 命中后头 2 帧压扁 / 倾斜（只这 2 帧）', sq == [0, 1], sq)
        sh = [x['shake'] for x in fr[:tl[key]['stopAll'] and int(round(tl[key]['stopAll'] * 60)) + 1] if x['shake'] is not None]
        check(tag + key + ' 全局顿帧期间目标 ±1 px 受击抖动（出现 +1 和 -1）', 1 in sh and -1 in sh and all(abs(v) <= 1 for v in sh), sh)
    check(tag + 'reduceFlash 开启：重击闪白峰值压低到 0.35、仍保持 3 帧', [x['flash'] for x in tl['J3_reduce']['frames'][:4]] == [0.35, 0.35, 0.35, 0.28], [x['flash'] for x in tl['J3_reduce']['frames'][:6]])
    j1 = tl['J1']['frames']
    check(tag + '轻击不变：J1 闪白 0.9 保持 4 帧再按 7/s 衰减，不压扁', [x['flash'] for x in j1[:5]] == [0.9, 0.9, 0.9, 0.9, 0.783] and not any(x['squash'] for x in j1), [x['flash'] for x in j1[:6]])
    check(tag + '全局顿帧期间 legacy 模式（freeze=1）也有新的闪白 / 抖动（闪白 / 抖动 / 压扁不依赖缓出）', tl['J3_legacy']['frames'][0]['flash'] == 1, '')

    # ---- ③ 击退
    pu = pg.evaluate('HF.push()')
    raw['push'] = pu
    check(tag + '击退总位移和 push 完全一致（4/8/12/24/30/40/60 px）', all(abs(p['total'] - p['push']) < 1e-3 for p in pu['profile']), [(p['push'], p['total']) for p in pu['profile']])
    check(tag + '击退先快后慢：每帧位移单调下降，首帧 > 恒速的 2.5 倍', all(all(p['rows'][i] >= p['rows'][i + 1] - 1e-9 for i in range(10)) and p['rows'][0] > 2.5 * p['push'] / 10.8 for p in pu['profile']), [(p['push'], p['rows'][:3]) for p in pu['profile']])
    slam = {}
    for s in pu['slam']:
        slam.setdefault(s['P'], []).append(s)
    exp = {40: 38, 60: 58}
    for P in (40, 60):
        got = [s['d'] for s in slam[P] if s['slam']]
        check(tag + '撞墙触发边界不变：%d px 击退，墙离目标 ≤ %d px 撞墙（和基线一致）' % (P, exp[P]), got == list(range(0, exp[P] + 1)), got[-3:])

    # ---- 窗口：弹反 / 连打入口
    Ss = [12, 20]
    pl = pg.evaluate('HF.parry("legacy", [6, 8], %s)' % json.dumps(Ss))
    pc = pg.evaluate('HF.parry("curve", [6, 8], %s)' % json.dumps(Ss))
    raw['parry'] = {'legacy': pl, 'curve': pc}
    check(tag + '精准格挡窗口宽度不变（世界时间 6 帧）：legacy 和缓出都是 6 个按键帧', all(a['width'] == 6 and b['width'] == 6 for a, b in zip(pl, pc)), [(a['n'], a['S'], a['width'], b['width']) for a, b in zip(pl, pc)])
    check(tag + '弹反：缓出让这一击在真实时间里早到 ≤ 2 帧，窗口跟着一起早（窗口前沿和打击帧的距离不变）', all(0 <= a['strike'] - b['strike'] <= 2 and (a['strike'] - a['lo']) == (b['strike'] - b['lo']) for a, b in zip(pl, pc)), [(a['n'], a['S'], a['strike'], b['strike'], a['lo'], b['lo']) for a, b in zip(pl, pc)])
    zs = list(range(1, 60))
    rl = pg.evaluate('HF.rushEntry("legacy", %s)' % json.dumps(zs))
    rc = pg.evaluate('HF.rushEntry("curve", %s)' % json.dumps(zs))
    raw['rush'] = {'legacy': rl, 'curve': rc}
    ol, oc = rl['ok'], rc['ok']
    check(tag + '连打入口窗口：legacy 下限 / 上限（真实帧，J3 出招帧起算）= 9…33；缓出下限不变、上限最多早 2 帧', ol[0] == 9 and ol[-1] == 33 and oc[0] == 9 and 0 <= ol[-1] - oc[-1] <= 2, {'legacy': [ol[0], ol[-1], len(ol)], 'curve': [oc[0], oc[-1], len(oc)]})
    check(tag + '没有控制台 warning / error / pageerror', not errors, errors[:5])
    (OUT / ('test_hitfeel_%s_raw.json' % which)).write_text(json.dumps(raw, ensure_ascii=False), encoding='utf-8')
    b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', choices=['third', 'fourth', 'both'], default='both')
    a = ap.parse_args()
    with sync_playwright() as pw:
        for which in (['third', 'fourth'] if a.engine == 'both' else [a.engine]):
            run_engine(pw, which)
    fails = [r for r in results if not r['ok']]
    (OUT / 'test_hitfeel.json').write_text(json.dumps({'ok': not fails, 'results': results}, ensure_ascii=False, indent=1), encoding='utf-8')
    print('\n%s：%d / %d' % ('全部通过' if not fails else '有失败', len(results) - len(fails), len(results)))
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
