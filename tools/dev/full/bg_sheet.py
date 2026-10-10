r"""把正式构建里的背景拼成一张总览图（不经剧情、不放人物），用来看美术画完没有、精度够不够。

    python -B tools\dev\full\bg_sheet.py                      # 默认：体验版（序章 + 第1章）用到的背景
    python -B tools\dev\full\bg_sheet.py jail_cell cockpit    # 指定背景键
    python -B tools\dev\full\bg_sheet.py --out tools\_playtest\bg_sheet

每张背景按地图宽度拍镜头 0 / 中间 / 最右（窄图只拍一张），前景层（fg）也画上；2 倍最近邻。
输出 <out>\sheet.png（总览）和 <out>\<key>.png（单张）。
"""
import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import base64  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
from pathlib import Path  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

GAME = Path(__file__).resolve().parents[3]
DEMO = ['jail_cell', 'kujo_house_day', 'kujo_house_night', 'kujo_house_morning', 'school_gate', 'school_stairs',
        'school_infirmary', 'kujo_bedroom_dusk', 'tatami_top', 'dusk_gate', 'world_map', 'plane_cabin_side',
        'cockpit', 'sky_day', 'sea_day', 'hongkong_night', 'hk_garden_night']

JS = r"""async ([keys]) => {
  const out = {};
  const packOf = k => { for (const [n, p] of Object.entries(G.D.packs)) if ((p.bg || []).includes(k)) return n; return null; };
  for (const k of keys) {
    const spec = G.D.bg[k];
    if (!spec) { out[k] = { err: 'no spec' }; continue; }
    const pk = packOf(k);
    if (pk && !G.res.loaded(pk)) await G.res.loadPack(pk);
    const bg = new G.Background(spec);
    const W = spec.w || spec.width || 320;
    const cams = W > 320 ? [0, Math.round((W - 320) / 2), W - 320] : [0];
    const imgs = [];
    for (const cx of cams) {
      const c = document.createElement('canvas'); c.width = 320; c.height = 180;
      const g = c.getContext('2d'); g.imageSmoothingEnabled = false;
      try { bg.draw(g, cx, 0, { state: {} }); if (bg.fg && bg.fg.length) bg.drawFg(g, cx, 0, { state: {} }); }
      catch (e) { out[k] = { err: String(e) }; }
      imgs.push(c.toDataURL('image/png'));
    }
    out[k] = Object.assign(out[k] || {}, { w: W, cams, imgs, layers: (spec.layers || []).length, fg: (spec.fg || []).length });
  }
  return out;
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('keys', nargs='*')
    ap.add_argument('--out', default=str(GAME / 'tools' / '_playtest' / 'bg_sheet'))
    a = ap.parse_args()
    keys = a.keys or DEMO
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})
        page.goto((GAME / 'index.html').as_uri() + '?autotest=1', wait_until='load')
        page.wait_for_function('() => G.booted', timeout=60000)
        res = page.evaluate(JS, [keys])
        browser.close()

    tiles = []
    for k in keys:
        r = res.get(k) or {}
        if r.get('err') and not r.get('imgs'):
            print('缺：', k, r.get('err'))
            continue
        ims = [Image.open(io.BytesIO(base64.b64decode(u.split(',', 1)[1]))).convert('RGB') for u in r['imgs']]
        row = Image.new('RGB', (len(ims) * 644 - 4, 360), (16, 16, 20))
        for i, im in enumerate(ims):
            row.paste(im.resize((640, 360), Image.NEAREST), (i * 644, 0))
        row.save(out / f'{k}.png')
        tiles.append((k, r, row))
        print(f"{k}: 宽 {r['w']}，图层 {r['layers']}（前景 {r['fg']}）" + (f"，报错 {r['err']}" if r.get('err') else ''))

    if tiles:
        wmax = max(t[2].width for t in tiles)
        sheet = Image.new('RGB', (wmax, sum(t[2].height + 26 for t in tiles)), (30, 30, 36))
        d = ImageDraw.Draw(sheet)
        y = 0
        for k, r, row in tiles:
            d.text((6, y + 6), f"{k}  (w {r['w']}, layers {r['layers']}, fg {r['fg']})", fill=(255, 230, 120))
            sheet.paste(row, (0, y + 26))
            y += row.height + 26
        sheet.save(out / 'sheet.png')
        print('总览：', out / 'sheet.png')


if __name__ == '__main__':
    main()
