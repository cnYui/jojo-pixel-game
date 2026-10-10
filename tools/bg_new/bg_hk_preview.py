r"""bg-hk 代理的前后对比预览（2026-10-10）：
    python -B tools\bg_new\bg_hk_preview.py [hongkong_night] [hk_garden_night]
原导出函数（bg_jojo.exp_*）和新模块（tools\bg_new\<key>.py）各导一遍（图层写到 _preview\bg_hk\layers\，
不写 assets\bg\），用 §3.6 公式（bg_jojo.ref_render）拍几个镜头位置，贴上剧情道具，拼成前 / 后对比图
→ tools\bg_new\_preview\bg_hk\<key>_before_after.png（2 倍）。自检结果照常打印。
"""
import sys
sys.dont_write_bytecode = True

import os  # noqa: E402

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import bg_jojo as BJ  # noqa: E402

OUT = os.path.join(HERE, '_preview', 'bg_hk')
W, H = 320, 180


def _prop(name):
    p = os.path.join(os.path.dirname(TOOLS), 'assets', 'props', name + '.png')
    return Image.open(p).convert('RGBA') if os.path.exists(p) else None


# 剧情放的道具（ch01.js）：(名, x, y, z, 帧宽, 帧)
PROPS = {
    'hongkong_night': [('hk_table', 500, 164, 0, 48, 0), ('hk_table', 548, 164, 0, 48, 0), ('tv', 660, 152, 0, 34, 0),
                       ('kite', 860, 150, 80, 8, 0)],
    'hk_garden_night': [],
}
CAMS = {'hongkong_night': [0, 230, 400, 520, 640], 'hk_garden_night': [0]}


def shots(key, exporter, tag, props=True, state=None):
    c = BJ.standalone_c(os.path.join(OUT, 'layers_' + tag))
    ex = BJ.Ex(c, check=True)
    ex.begin(key)
    print('[%s] %s' % (tag, key))
    st = exporter(ex)
    out = []
    for cam in CAMS[key]:
        im = BJ.ref_render(st, ex.images, cam, 1.0, state or {}).convert('RGBA')
        if props:
            for name, x, y, z, fw, f in PROPS.get(key, []):
                pim = _prop(name)
                if pim is None:
                    continue
                fr = pim.crop((f * fw, 0, f * fw + fw, pim.height))
                BJ.paste(im, fr, x - fw // 2 - cam, y - z - fr.height)
        out.append((cam, im.convert('RGB')))
    bad = [ch for ch in ex.report[key]['checks'] if not ch['ok']]
    print('  自检 %d 项，没过 %d 项' % (len(ex.report[key]['checks']), len(bad)))
    return st, out, ex


def sheet(key, before, after, extra=None):
    try:
        f = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 14)
    except Exception:
        f = ImageFont.load_default()
    n = len(before)
    sc = 2
    im = Image.new('RGB', (n * (W * sc + 8) + 8, 2 * (H * sc + 24) + 8), (24, 24, 30))
    d = ImageDraw.Draw(im)
    for row, (lab, shots_) in enumerate((('before', before), ('after', after))):
        for i, (cam, s) in enumerate(shots_):
            x, y = 8 + i * (W * sc + 8), 8 + row * (H * sc + 24)
            d.text((x, y), '%s  %s  camX=%d' % (key, lab, cam), font=f, fill=(255, 230, 120))
            im.paste(s.resize((W * sc, H * sc), Image.NEAREST), (x, y + 20))
    p = os.path.join(OUT, key + '_before_after.png')
    im.save(p)
    print('  →', p)


def main(keys):
    os.makedirs(OUT, exist_ok=True)
    for key in keys:
        old = {'hongkong_night': BJ.exp_hongkong_night, 'hk_garden_night': BJ.exp_hk_garden_night}[key]
        _, before, _ = shots(key, old, 'before')
        st, after, ex = shots(key, lambda e: BJ.exp_new(e, key), 'after')
        sheet(key, before, after)
        for cam, s in after:
            s.save(os.path.join(OUT, '%s_after_cam%d.png' % (key, cam)))
        for cam, s in before:
            s.save(os.path.join(OUT, '%s_before_cam%d.png' % (key, cam)))


if __name__ == '__main__':
    main([a for a in sys.argv[1:] if not a.startswith('--')] or ['hongkong_night', 'hk_garden_night'])
