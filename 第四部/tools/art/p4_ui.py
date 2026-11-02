# 第四部序章的 UI 图：标题字、名牌、替身卡、地点卡、篇章卡、VS 卡文字、必杀切入字、DORA 拟声字、小卡、发型记录、日历地图零件。
#   版式和尺寸照第三部 GAME_DATA.ui（640×360 的 UI 层坐标）；大字用 Noto Sans SC Black（OFL，按字取子集），
#   小字用文泉驿点阵（和游戏里对话框同一套字）。颜色换成第四部的：疯狂钻石的粉、杜王町的暖色。
#   用法：python3 第四部/tools/art/p4_ui.py      输出 第四部/assets/ui/** + _meta/ui.json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402

OUT = os.path.join(LIB.ASSETS, 'ui')
PREV = os.path.join(LIB.ASSETS, 'preview')
INK = '#130b20'           # 第三部 UI 字的描边色
META = {}

# 用到的大字全列在这里：Google Fonts 只按这些字取一次子集
BIG_TEXT = ('不灭钻石JOJO的奇妙冒险东方仗助空条承太郎广濑康一东方朋子良平片桐安十郎（安杰罗）'
            '『疯狂钻石』水中项链CRAZYDIAMONDAQUANECKLACE1999年日本·杜王町葡萄丘高中超市东方家'
            '序章仗助登场PROLOGUEMORIOH多拉拉！DORA……误会？MISUNDERSTANDINGVS/校门那天夜里三天后，雨'
            '发型记录第次1234567890M县S市月HIGASHIKATARESIDENCEBUDOUGAOKAHIGHSCHOOLSUPERMARKET-·!')


def noto():
    return LIB.gfont('Noto Sans SC', 900, BIG_TEXT)


def save(rel, im, **extra):
    path = os.path.join(OUT, rel + '.png')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)
    d = dict(image='ui/' + rel, w=im.width, h=im.height)
    d.update(extra)
    return d


def big(text, size, fill, edge=INK, shadow='#0a0412', edge_w=2, shadow_d=(2, 2), inner=None, spacing=0):
    return LIB.styled_text(text, noto(), size, fill=fill, edge=edge, shadow=shadow, edge_w=edge_w, shadow_d=shadow_d,
                           inner=inner, spacing=spacing)


def small(text, color='#f4ecff', edge=INK, size=12):
    """点阵小字 + 1 px 描边（第三部名牌第二行那种）"""
    m = LIB.text_mask(text, LIB.WQY, size, index=1)
    w, h = m.size
    out = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
    mp = m.load()
    op = out.load()
    ec, fc = LIB.hexc(edge), LIB.hexc(color)
    for y in range(h):
        for x in range(w):
            if mp[x, y] > 127:
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    if op[x + 1 + dx, y + 1 + dy][3] == 0:
                        op[x + 1 + dx, y + 1 + dy] = ec
    for y in range(h):
        for x in range(w):
            if mp[x, y] > 127:
                op[x + 1, y + 1] = fc
    return out


def latin(text, size, color='#ffffff', edge=INK):
    """英文小标：用 Noto 的拉丁字母，白字细描边、字距拉开"""
    return big(text, size, (color, color), edge=edge, shadow=None, edge_w=1, spacing=2)


def stack(parts, gap=2, align='left', pad=0):
    w = max(p.width for p in parts) + pad * 2
    h = sum(p.height for p in parts) + gap * (len(parts) - 1) + pad * 2
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    y = pad
    for p in parts:
        x = pad if align == 'left' else (w - p.width) // 2
        out.alpha_composite(p, (x, y))
        y += p.height + gap
    return out


# ================================================================ 标题字
def logo():
    main = big('不灭钻石', 56, ('#fff0f8', '#ff8ac8', '#c8327e'), edge='#2a0a34', shadow='#12041a', edge_w=3, shadow_d=(3, 3),
               inner='#ffffff')
    sub = big('JOJO的奇妙冒险', 16, ('#f4e8ff', '#c8a8f0'), edge='#2a0a34', shadow='#12041a', edge_w=2)
    # 右上角一颗钻石闪光
    W = main.width + 18
    H = sub.height + main.height + 2
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.alpha_composite(sub, (6, 0))
    out.alpha_composite(main, (0, sub.height + 2))
    d = ImageDraw.Draw(out)
    cx, cy = W - 10, sub.height + 8
    for r, col in ((7, '#2a0a34'), (5, '#ffd0ea'), (2, '#ffffff')):
        d.polygon([(cx, cy - r - 2), (cx + r, cy), (cx, cy + r + 2), (cx - r, cy)], fill=LIB.hexc(col))
    for k in range(1, 6):
        d.point((cx - 9 - k, cy), fill=LIB.hexc('#ffd0ea'))
        d.point((cx + 9 + k, cy), fill=LIB.hexc('#ffd0ea'))
    META['logo'] = {'main': save('logo_main', out)}


# ================================================================ 名牌（左下，第三部 x 24 y 265）
NAMECARDS = {
    'josuke': ('东方仗助', '#b04a8a', '葡萄丘高中一年级｜最在意自己的发型'),
    'jotaro4': ('空条承太郎', '#5a6ab0', '28 岁 · 海洋学者｜按辈分是仗助的外甥'),
    'koichi': ('广濑康一', '#5a9a3a', '葡萄丘高中一年级｜个子小，胆子也不大'),
    'tomoko': ('东方朋子', '#c05a7a', '仗助的妈妈｜过肩摔一流'),
    'ryohei': ('东方良平', '#4a6aa0', '杜王町的警察｜仗助的外公'),
    'angelo': ('片桐安十郎（安杰罗）', '#3a8ab0', '越狱的死刑犯｜替身：水中项链'),
}


def namecards():
    out = {}
    for cid, (name, col, desc) in NAMECARDS.items():
        n = big(name, 20, ('#ffffff', '#ece6f6'), shadow=None, edge_w=2)
        s = small(desc)
        bar_w = max(n.width + 30, 120)
        W = max(bar_w, s.width) + 4
        H = n.height + 4 + 3 + 3 + s.height
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        im.alpha_composite(n, (0, 0))
        d = ImageDraw.Draw(im)
        y = n.height + 3
        d.rectangle((0, y, bar_w, y + 2), fill=LIB.hexc(col))
        d.line((0, y, bar_w, y), fill=LIB.hexc('#ffffff', 160))
        for k in range(8):                                   # 尾巴渐隐
            d.point((bar_w + 2 + k * 2, y + 1), fill=LIB.hexc(col, 200 - k * 24))
        im.alpha_composite(s, (0, y + 6))
        out[cid] = save('namecard/' + cid, im, x=24, y=265)
    META['namecards'] = out


# ================================================================ 替身卡（右上，平行四边形底）
STANDCARDS = {
    'crazyd': ('『疯狂钻石』', 'CRAZY DIAMOND', ('#ffe4f2', '#ff9ccc'), '#ffb0d8', '#24081c'),
    'aqua': ('『水中项链』', 'AQUA NECKLACE', ('#e4f6ff', '#8cd4f8'), '#a0e0ff', '#081a2a'),
}


def standcards():
    out = {}
    for sid, (cn, en, fill, border, bg) in STANDCARDS.items():
        W, H = 192, 63
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        poly = [(14, 1), (W - 1, 1), (W - 14, H - 2), (1, H - 2)]
        d.polygon(poly, fill=LIB.hexc(bg, 235))
        d.line(poly + [poly[0]], fill=LIB.hexc(border), width=2)
        n = big(cn, 22, fill, edge=INK, shadow=None, edge_w=2)
        e = latin(en, 11)
        im.alpha_composite(n, ((W - n.width) // 2, 5))
        im.alpha_composite(e, ((W - e.width) // 2, 5 + n.height + 2))
        out[sid] = save('standcard/' + sid, im, side='right', y=40)
    META['standcards'] = out


# ================================================================ 地点卡（左上）
LOCATIONS = {
    'morioh': ('1999年 日本·杜王町', 'MORIOH · M县S市'),
    'budou': ('葡萄丘高中', 'BUDOUGAOKA HIGH SCHOOL · 杜王町'),
    'market': ('超市', 'SUPERMARKET · 杜王町'),
    'higashikata': ('东方家', 'HIGASHIKATA RESIDENCE · 杜王町'),
}


def locations():
    out = {}
    for key, (cn, en) in LOCATIONS.items():
        n = big(cn, 24, ('#ffffff', '#f0eaf8'), shadow=None, edge_w=2)
        e = small(en, color='#ffe8a8')
        bar = max(n.width + 24, 130)
        W = max(bar, e.width) + 4
        H = n.height + 3 + 4 + 4 + e.height
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        im.alpha_composite(n, (4, 0))
        d = ImageDraw.Draw(im)
        y = n.height + 3
        d.rectangle((0, y, bar, y + 3), fill=LIB.hexc('#f0b838'))
        d.line((0, y, bar, y), fill=LIB.hexc('#ffe48a'))
        im.alpha_composite(e, (6, y + 7))
        out[key] = save('location/' + key, im, x=24, y=25)
    META['locations'] = out


# ================================================================ 篇章卡（640×360：粉紫漩涡 + 中间暗带 + 文字）
def chapter_prologue():
    W, H = 640, 360
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    cx, cy = W / 2, H / 2
    r = np.hypot(xx - cx, yy - cy)
    th = np.arctan2(yy - cy, xx - cx)
    band = (r / 140.0 - th / (2 * np.pi)) % 1.0
    BAY = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
    thr = BAY[(yy.astype(int)) % 4, (xx.astype(int)) % 4]
    A, B = np.array(LIB.hexc('#2a0a28')[:3]), np.array(LIB.hexc('#621e5c')[:3])
    # 两色硬边漩涡，交界 0.06 宽的一圈用 4×4 抖动过渡（第三部篇章卡同样做法）
    t = band
    k = np.clip((t - 0.47) / 0.06, 0, 1) * (t < 0.75) + np.clip((1.0 - t) / 0.06, 0, 1) * (t >= 0.75)
    k = np.where(t < 0.47, 0, k)
    k = np.where((t > 0.53) & (t < 0.94), 1, k)
    img = np.where((k > thr)[..., None], B, A).astype(np.uint8)
    im = Image.fromarray(np.dstack([img, np.full((H, W), 255, np.uint8)]), 'RGBA')
    d = ImageDraw.Draw(im)
    # 散落的钻石闪光
    rng = np.random.RandomState(7)
    for _ in range(26):
        x, y = rng.randint(10, W - 10), rng.randint(10, H - 10)
        if 100 < y < 262:
            continue
        s = rng.randint(2, 5)
        d.polygon([(x, y - s - 1), (x + s, y), (x, y + s + 1), (x - s, y)], fill=LIB.hexc('#ff8ac8', 140))
        d.point((x, y), fill=LIB.hexc('#ffffff', 220))
    # 中间暗带
    band_im = Image.new('RGBA', (W, 156), LIB.hexc('#12040e', 205))
    im.alpha_composite(band_im, (0, 102))
    d = ImageDraw.Draw(im)
    d.line((0, 102, W, 102), fill=LIB.hexc('#e8c8e0'))
    d.line((0, 257, W, 257), fill=LIB.hexc('#e8c8e0'))
    a = big('序章', 20, ('#ffffff', '#ece6f6'), shadow=None)
    b = big('杜王町', 44, ('#fff0a8', '#ffc83c', '#f08a2a'), edge='#2a0a34', shadow='#12041a', edge_w=3, shadow_d=(3, 3))
    c = big('仗助登场', 20, ('#ffffff', '#ece6f6'), shadow=None)
    e = latin('PROLOGUE · MORIOH', 11, color='#ffd860')
    gap = 22
    tw = a.width + gap + b.width
    x0 = (W - tw) // 2
    im.alpha_composite(a, (x0, 150 - a.height // 2 + 6))
    im.alpha_composite(b, (x0 + a.width + gap, 150 - b.height // 2))
    im.alpha_composite(c, ((W - c.width) // 2, 192))
    im.alpha_composite(e, ((W - e.width) // 2, 228))
    META['chapters'] = {'prologue': save('chapter/prologue', im)}


# ================================================================ VS 卡的字（人物和底色由引擎现场画）
def vs_cards():
    out = {}
    specs = {
        'aqua': ('水中项链', 'AQUA NECKLACE', 'VS 安杰罗 / 杜王町·东方家', ('#e8f8ff', '#7ccaf4', '#3a8ac8'), '#3aa0e0',
                 ['#1a5a8a', '#0a2a48']),
        'misunderstand': ('……误会？', 'MISUNDERSTANDING', 'VS 空条承太郎 / 葡萄丘高中·校门', ('#f0eaff', '#a898f0', '#6a58c8'),
                          '#7a68e0', ['#3a2a8a', '#160c40']),
    }
    for key, (cn, en, tag, fill, edge_col, cols) in specs.items():
        n = big(cn, 40, fill, edge=INK, shadow='#0a0412', edge_w=3, shadow_d=(3, 3))
        e = latin(en, 12)
        t = small(tag, color='#ffffff')
        TW, TH = t.width + 34, 34
        tag_im = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
        d = ImageDraw.Draw(tag_im)
        poly = [(12, 2), (TW - 1, 2), (TW - 13, TH - 3), (0, TH - 3)]
        d.polygon(poly, fill=LIB.hexc('#140c1e', 235))
        d.line(poly + [poly[0]], fill=LIB.hexc(edge_col), width=2)
        d.polygon([(4, 4), (10, 4), (3, TH - 5), (-2, TH - 5)], fill=LIB.hexc(edge_col))
        tag_im.alpha_composite(t, ((TW - t.width) // 2 + 2, (TH - t.height) // 2))
        out[key] = {'name': save(f'vs/{key}_name', n), 'en': save(f'vs/{key}_en', e), 'tag': save(f'vs/{key}_tag', tag_im),
                    'colours': cols}
    META['vs'] = out


# ================================================================ 必杀切入字、DORA 拟声字、小卡
def specials_and_words():
    META['specials'] = {'josuke': save('special/josuke', big('多拉拉拉拉！', 42, ('#fff4c0', '#ffd040', '#f0902a'),
                                                              edge='#3a0a3a', shadow='#12041a', edge_w=3, shadow_d=(3, 3)))}
    sfx = {}
    for i, w in enumerate(('DORA', 'DORA!', 'DORA!!', 'DORA!!!')):
        size = (26, 28, 30, 34)[i]
        im = big(w, size, ('#ffe8f4', '#ff9ccc', '#e05aa0'), edge='#2a0a34', shadow='#12041a', edge_w=3, shadow_d=(2, 2))
        sfx[w] = save('sfx/dora_%d' % i, im)
    sfx['多拉拉'] = save('sfx/dorarara', big('多拉拉！', 30, ('#ffe8f4', '#ff9ccc', '#e05aa0'), edge='#2a0a34', edge_w=3))
    META['sfx'] = sfx
    titles = {
        'night': save('title/night', big('那天夜里', 30, ('#e8ecff', '#a8b4e8'), edge='#0a0a20', edge_w=2)),
        'rain3': save('title/rain3', big('三天后，雨', 30, ('#e8f4ff', '#9cc0e0'), edge='#0a1420', edge_w=2)),
    }
    META['titles'] = titles


# ================================================================ 仗助发型记录：金色小牌 + 数字（第 N 次）
def hair_record():
    t1 = big('东方仗助 发型记录', 16, ('#5a3a0a', '#3a2406'), edge='#fff0b0', shadow=None, edge_w=1)
    W, H = t1.width + 96, 44
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W - 1, H - 1), fill=LIB.hexc('#3a2406'))
    for y in range(1, H - 1):                                       # 金色：上亮下暗的三段
        k = y / (H - 2)
        col = '#fff0a0' if k < .12 else '#f8d050' if k < .55 else '#e0a828' if k < .85 else '#b07818'
        d.line((1, y, W - 2, y), fill=LIB.hexc(col))
    d.rectangle((3, 3, W - 4, H - 4), outline=LIB.hexc('#8a5a10'))
    for x in range(8, W - 8, 9):                                    # 斜纹闪光
        d.line((x, 4, x + 4, 8), fill=LIB.hexc('#fff8d0', 120))
    im.alpha_composite(t1, (10, (H - t1.height) // 2))
    di = big('第', 18, ('#5a3a0a', '#3a2406'), edge='#fff0b0', shadow=None, edge_w=1)
    dc = big('次', 18, ('#5a3a0a', '#3a2406'), edge='#fff0b0', shadow=None, edge_w=1)
    xs = 10 + t1.width + 8
    im.alpha_composite(di, (xs, (H - di.height) // 2))
    im.alpha_composite(dc, (W - 10 - dc.width, (H - dc.height) // 2))
    slot = [xs + di.width + 2, 4, W - 10 - dc.width - 2 - (xs + di.width + 2), H - 8]
    digits = []
    for n in range(10):
        g = big(str(n), 30, ('#ff6a4a', '#d82a2a'), edge='#3a0a0a', shadow=None, edge_w=2)
        digits.append(save('hair/d%d' % n, g))
    META['hair'] = {'plate': save('hair/plate', im, slot=slot), 'digits': digits}


# ================================================================ 日历地图零件：图钉（红 / 灰）、红章「1999年4月」
def map_parts():
    def pin(col, dark):
        im = Image.new('RGBA', (9, 14), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.line((4, 7, 4, 13), fill=LIB.hexc('#6a6a74'))
        d.ellipse((0, 0, 8, 8), fill=LIB.hexc(dark))
        d.ellipse((1, 0, 7, 6), fill=LIB.hexc(col))
        d.point((3, 2), fill=LIB.hexc('#ffffff'))
        return LIB.outline(im, color=LIB.hexc('#1a1020'))
    parts = {'pin': save('map/pin', pin('#e8483c', '#9a2420'), ax=5, ay=15),
             'pin_gray': save('map/pin_gray', pin('#a8a8b0', '#6a6a74'), ax=5, ay=15)}
    # 红章：圆角方框 + 两行字，故意有点没盖实（随机掉几颗像素）
    t1 = big('1999年', 14, ('#d82a2a', '#d82a2a'), edge='#d82a2a', shadow=None, edge_w=0)
    t2 = big('4月', 20, ('#d82a2a', '#d82a2a'), edge='#d82a2a', shadow=None, edge_w=0)
    W = max(t1.width, t2.width) + 14
    H = t1.height + t2.height + 12
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, W - 1, H - 1), radius=5, outline=LIB.hexc('#d82a2a'), width=2)
    im.alpha_composite(t1, ((W - t1.width) // 2, 5))
    im.alpha_composite(t2, ((W - t2.width) // 2, 6 + t1.height))
    a = np.array(im)
    rng = np.random.RandomState(9)
    on = a[..., 3] > 0
    drop = (rng.rand(*on.shape) < .12) & on
    a[drop, 3] = 0
    a[on & ~drop, 3] = 225
    im = Image.fromarray(a, 'RGBA').rotate(-8, resample=Image.NEAREST, expand=True)
    parts['stamp'] = save('map/stamp_199904', im)
    parts['place'] = save('map/place', small('M县S市 杜王町', color='#5a4a34', edge='#f4ead2'))
    META['map'] = parts


def preview():
    files = []
    for root, _, fs in os.walk(OUT):
        for f in sorted(fs):
            files.append(os.path.join(root, f))
    ims = [Image.open(f).convert('RGBA') for f in files if 'chapter' not in f]
    W = 660
    x = y = rowh = 0
    pos = []
    for im in ims:
        if x + im.width > W:
            x, y, rowh = 0, y + rowh + 6, 0
        pos.append((x, y))
        x += im.width + 6
        rowh = max(rowh, im.height)
    can = Image.new('RGBA', (W, y + rowh + 6), (70, 64, 84, 255))
    for im, p in zip(ims, pos):
        can.alpha_composite(im, p)
    os.makedirs(PREV, exist_ok=True)
    can.save(os.path.join(PREV, 'ui.png'))


def main():
    for f in (logo, namecards, standcards, locations, chapter_prologue, vs_cards, specials_and_words, hair_record, map_parts):
        f()
    path = os.path.join(LIB.META, 'ui.json')
    LIB.save_json(path, META)
    preview()
    print('UI：', ', '.join(f'{k} {len(v) if isinstance(v, dict) else 1}' for k, v in META.items()))


if __name__ == '__main__':
    main()
