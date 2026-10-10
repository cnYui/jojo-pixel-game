"""六名主角逐帧抽帧 + 联系表（正式入口 index.html、生产战斗代码、真实按键时钟）。

用法：python -B tools\\dev\\p5\\capture_moves.py --out tools\\dev\\p5\\_out\\review_<时间> [--only avdol,jotaro] [--scen J3,rush]
输出：<out>\\<cid>_<场景>.png（每格 = 世界层 320×180 裁剪放大；叠加：红 = 弹体（竖线连到地面影子）、
黄 = 当前近战判定的地面带、品红 = 替身身前点 standFront、橙 = 危险区）+ report.json（每格的状态快照）。
"""
import argparse
import base64
import json
import sys
from io import BytesIO
from pathlib import Path

sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
GAME = HERE.parents[2]
FONT = 'C:/Windows/Fonts/msyh.ttc'
HEROES = ['jotaro', 'avdol', 'kakyoin', 'polnareff', 'joseph', 'iggy']
CN = {'jotaro': '承太郎·白金之星', 'avdol': '阿布德尔·红色魔术师', 'kakyoin': '花京院·绿色法皇',
      'polnareff': '波鲁纳雷夫·银色战车', 'joseph': '乔瑟夫·隐者之紫', 'iggy': '伊奇·愚者'}


def scenarios(cid):
    shooter = cid in ('avdol', 'kakyoin')
    near = 70 if cid == 'kakyoin' else 40          # 近战角色把木桩放在判定里，才看得到命中反馈
    out = [
        dict(name='J1', frames=24, every=2, dx=near, events=[[1, 'tap', 'attack']]),
        dict(name='J123', frames=110, every=3, dx=near, combo=dict(hits=3), events=[[1, 'tap', 'attack']], minFrames=40,
             stopWhen="p.state==='idle' && !W.shots.length && !p.atk"),
        dict(name='rush', frames=170, every=4, dx=near, combo=dict(hits=3, rushFrames=36), events=[[1, 'tap', 'attack']], minFrames=60,
             stopWhen="p.state==='idle' && !W.shots.length && !p.atk && p.rushCdT<=0.3"),
        dict(name='U', frames=260, every=5, dx=70, energy=100, events=[[1, 'tap', 'special']], screenAt=[30, 70],
             minFrames=70, stopWhen="p.state==='idle' && !W.cine && !W.shots.length"),
        dict(name='guard', frames=34, every=3, dx=40, events=[[1, 'down', 'guard'], [14, 'poke', {'dmg': 10}], [30, 'up', 'guard']]),
        # 真人点一下 L 也会按住 5–6 帧：down / up 模拟，替身才摆得出格挡姿势
        dict(name='parry', frames=22, every=2, dx=40, events=[[1, 'down', 'guard'], [3, 'poke', {'dmg': 10}], [7, 'up', 'guard']]),
        dict(name='dodge', frames=18, every=2, events=[[1, 'tap', 'dodge']]),
        dict(name='explore_J', mode='explore', bg='kujo_house_day', noEnemy=True, frames=110, every=4,
             combo=dict(hits=3), events=[[1, 'tap', 'attack']], minFrames=40, stopWhen="p.state==='idle' && !W.shots.length && !p.atk"),
        dict(name='explore_U', mode='explore', bg='kujo_house_day', noEnemy=True, frames=120, every=6,
             events=[[2, 'tap', 'special']]),
    ]
    if cid == 'avdol':
        out.append(dict(name='guardAttack', frames=110, every=5, events=[[1, 'down', 'guard'], [6, 'tap', 'attack'], [100, 'up', 'guard']]))
    if shooter:
        out.append(dict(name='J3_far', frames=90, every=4, dx=150, full=True, combo=dict(hits=3), events=[[1, 'tap', 'attack']], minFrames=40,
                        stopWhen="p.state==='idle' && !W.shots.length && !p.atk"))
        out.append(dict(name='J3_out', frames=110, every=4, dx=215, full=True, combo=dict(hits=3), events=[[1, 'tap', 'attack']], minFrames=40,
                        at=list(range(60, 90, 2)), x=120, stopWhen="p.state==='idle' && !W.shots.length && !p.atk && !G.fx.list.some(e=>e.name==='smoke'&&!G.fx.expired(e))"))
    return out


def decode(data):
    return Image.open(BytesIO(base64.b64decode(data.split(',', 1)[1]))).convert('RGBA')


def cell(pic, crop_w=240, crop_h=130, scale=2, full=False):
    st = pic['st']
    im = decode(pic['png'])
    cx, cy = st['cam']['x'], st['cam']['y']
    px = st['x'] - cx
    fc = st['facing'] or 1
    if full:
        crop_w, scale = 320, 1.5
    x0 = int(px - 70) if fc > 0 else int(px - (crop_w - 70))
    x0 = max(0, min(320 - crop_w, x0))
    y0 = 180 - crop_h
    big = im.crop((x0, y0, x0 + crop_w, y0 + crop_h)).resize((int(crop_w * scale), int(crop_h * scale)), Image.Resampling.NEAREST)
    d = ImageDraw.Draw(big, 'RGBA')
    S = lambda wx, wy: ((wx - cx - x0) * scale, (wy - cy - y0) * scale)
    b = st.get('box')
    if b:
        if b.get('circle'):
            r = b['circle']
            a, c = S(st['x'] - r, b['y'] - r * 0.5), S(st['x'] + r, b['y'] + r * 0.5)
            d.ellipse([a, c], outline=(255, 230, 40, 230), width=2)
        else:
            a, c = S(b['x0'], b['y'] - b['depth']), S(b['x1'], b['y'] + b['depth'])
            d.rectangle([a, c], fill=(255, 230, 40, 60), outline=(255, 230, 40, 230), width=2)
    for h in st['hazards']:
        if h['shape'] == 'ellipse' and h.get('x') is not None:
            a, c = S(h['x'] - h['rx'], h['y'] - h['ry']), S(h['x'] + h['rx'], h['y'] + h['ry'])
            d.ellipse([a, c], outline=(255, 150, 40, 220), width=2)
        elif h.get('x0') is not None:
            a, c = S(h['x0'], h['y0']), S(h['x1'], h['y1'])
            d.rectangle([a, c], outline=(255, 150, 40, 220), width=2)
    if st.get('front'):
        f = st['front']
        fx, fy = S(f['x'], f['y'] - f['z'])
        d.ellipse([fx - 4, fy - 4, fx + 4, fy + 4], outline=(255, 60, 255, 255), width=2)
    for s in st['shots']:
        if s['dead']:
            continue
        sx, sy = S(s['x'], s['y'] - s['z'])
        gx, gy = S(s['x'], s['y'])
        d.line([gx, gy, sx, sy], fill=(255, 40, 40, 160), width=1)
        d.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], outline=(255, 30, 30, 255), width=2)
        d.ellipse([gx - 3, gy - 1, gx + 3, gy + 1], fill=(255, 30, 30, 200))
    return big


def sheet(cid, scen, res, out):
    pics = res['pics']
    if not pics:
        return None
    font = ImageFont.truetype(FONT, 15)
    head = ImageFont.truetype(FONT, 22)
    cols = 5
    cw, ch = 480, 260
    rows = (len(pics) + cols - 1) // cols
    W, H = cols * (cw + 8) + 16, 64 + rows * (ch + 66)
    canvas = Image.new('RGB', (W, H), '#101119')
    d = ImageDraw.Draw(canvas)
    d.text((14, 8), f"{CN[cid]} — {scen['name']}   伤害 {res['dmg']}   连打开始 f{res['rushStart']}   错误 {len(res['errors'])}   缺图 {len(res['missing'])}",
           fill='#ffe070', font=head)
    d.text((14, 38), '红=弹体(竖线连地面影子) 黄=近战判定地面带 品红=替身身前点 橙=危险区', fill='#9aa3b8', font=font)
    for k, pic in enumerate(pics):
        r, c = divmod(k, cols)
        x, y = 12 + c * (cw + 8), 64 + r * (ch + 66)
        canvas.paste(cell(pic, full=scen.get('full', False)), (x, y))
        st = pic['st']
        sd = st['stand']
        l1 = f"{pic['label']} {st['state']} {st['atk'] or ''} t{st['atkT'] if st['atkT'] is not None else ''} 本体 {st['body']}"
        l2 = (f"替身 {sd['act']}[{sd['frame']}] {sd['mode']} x{sd['x']} z{sd['z']}" if sd else '无替身') + \
             (f" | 弹 {len([s for s in st['shots'] if not s['dead']])} z{[s['z'] for s in st['shots']][:3]}" if st['shots'] else '')
        l3 = f"hp {st['enemy']['hp'] if st['enemy'] else '-'} fx {','.join(sorted(set(st['fx'])))[:58]}"
        d.text((x, y + ch + 2), l1[:64], fill='#e6dfd2', font=font)
        d.text((x, y + ch + 22), l2[:64], fill='#9dc0dc', font=font)
        d.text((x, y + ch + 42), l3[:64], fill='#a8a8a8', font=font)
    path = out / f"{cid}_{scen['name']}.png"
    canvas.save(path)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--only', default='')
    ap.add_argument('--scen', default='')
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    only = [x for x in a.only.split(',') if x] or HEROES
    want = [x for x in a.scen.split(',') if x]
    errors, report = [], {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=['--autoplay-policy=no-user-gesture-required'])
        page = browser.new_page(viewport={'width': 1280, 'height': 720})
        page.on('pageerror', lambda e: errors.append({'msg': str(e), 'stack': getattr(e, 'stack', None)}))
        page.goto((GAME / 'index.html').as_uri() + '?autotest=1', wait_until='load')
        page.wait_for_function('window.G && G.booted', timeout=120000)
        page.add_script_tag(path=str(HERE / 'capture_moves.js'))
        print('setup', page.evaluate('CAP.setup()'), flush=True)
        for cid in only:
            report[cid] = {}
            for scen in scenarios(cid):
                if want and scen['name'] not in want:
                    continue
                spec = dict(scen, cid=cid)
                res = page.evaluate('s => CAP.run(s)', spec)
                path = sheet(cid, scen, res, a.out)
                for p in res['pics']:
                    p.pop('png', None)
                    if p.get('screen'):
                        im = decode(p['screen'])
                        sp = a.out / f"{cid}_{scen['name']}_screen_f{p['i']}.png"
                        im.save(sp)
                        p['screen'] = sp.name
                report[cid][scen['name']] = res
                print(cid, scen['name'], 'dmg', res['dmg'], 'pics', len(res['pics']), 'err', len(res['errors']), 'missing', res['missing'], '->', path and path.name, flush=True)
        browser.close()
    (a.out / 'report.json').write_text(json.dumps(dict(report=report, pageerrors=errors), ensure_ascii=False, indent=1), encoding='utf-8')
    print('pageerrors', len(errors))
    for e in errors[:5]:
        print(e['msg'])
        print((e['stack'] or '')[:800])


if __name__ == '__main__':
    main()
