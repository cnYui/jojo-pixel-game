# 第四部美术脚本共用的小工具：路径、读写图集元数据、描边、像素文字。
#   第四部的素材全部由这些脚本在仓库里生成（云端没有第三部的原动画工程），产物写进 第四部/assets/。
import json
import os
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
P4 = os.path.normpath(os.path.join(HERE, '..', '..'))          # 第四部/
REPO = os.path.normpath(os.path.join(P4, '..'))                 # 仓库根（第三部）
ASSETS = os.path.join(P4, 'assets')
META = os.path.join(ASSETS, '_meta')
FONTS = os.path.join(HERE, 'fonts')
P3_CHARS = os.path.join(REPO, 'assets', 'chars_new')            # 第三部的全尺寸图集（只读，拿来改）

OUTLINE = (26, 16, 32, 255)                                      # 第三部精灵统一的描边色 #1a1020
WQY = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'


def ensure(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def load_json(path, dflt=None):
    if not os.path.exists(path):
        return dflt
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def save_json(path, obj):
    ensure(path)
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.write('\n')


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def outline(im, color=OUTLINE, diag=False):
    """给不透明像素外面描一圈 1 px 边（只描在透明处）。"""
    im = im.convert('RGBA')
    w, h = im.size
    src = im.load()
    out = im.copy()
    o = out.load()
    nb = [(-1, 0), (1, 0), (0, -1), (0, 1)] + ([(-1, -1), (1, -1), (-1, 1), (1, 1)] if diag else [])
    for y in range(h):
        for x in range(w):
            if src[x, y][3] > 0:
                continue
            for dx, dy in nb:
                xx, yy = x + dx, y + dy
                if 0 <= xx < w and 0 <= yy < h and src[xx, yy][3] > 0:
                    o[x, y] = color
                    break
    return out


def gfont(family, weight, text, name=None):
    """Google Fonts 按字取子集（只取用到的字，几十 KB）：缓存在 tools/art/fonts/，第二次起不联网。
    这些字体都是 SIL OFL，只用来烘焙 UI 图片。"""
    os.makedirs(FONTS, exist_ok=True)
    chars = ''.join(sorted(set(text)))
    key = name or (family.replace(' ', '') + '-' + str(weight))
    path = os.path.join(FONTS, key + '.ttf')
    have = os.path.join(FONTS, key + '.chars.txt')
    old = open(have, encoding='utf-8').read() if os.path.exists(have) else ''
    if os.path.exists(path) and set(chars) <= set(old):
        return path
    allc = ''.join(sorted(set(old) | set(chars)))
    q = urllib.parse.urlencode({'family': f'{family}:wght@{weight}', 'text': allc})
    css = urllib.request.urlopen('https://fonts.googleapis.com/css2?' + q, timeout=60).read().decode('utf-8')
    url = css.split('url(')[1].split(')')[0]
    data = urllib.request.urlopen(url, timeout=120).read()
    with open(path, 'wb') as fh:
        fh.write(data)
    with open(have, 'w', encoding='utf-8') as fh:
        fh.write(allc)
    return path


def gfont_full(family, weight):
    """整套字体（不取子集）：缓存在 tools/art/fonts/，不进仓库（十几 MB）。
    按字取子集的话，子集一变（各章加了新名字、新标题）同一个字画出来会差一两个像素，几条分支各画各的就会互相改到对方的图；
    整套字体每个环境下载的是同一份，画出来一模一样。"""
    os.makedirs(FONTS, exist_ok=True)
    path = os.path.join(FONTS, family.replace(' ', '') + '-' + str(weight) + '-full.ttf')
    if os.path.exists(path):
        return path
    q = urllib.parse.urlencode({'family': f'{family}:wght@{weight}'})
    css = urllib.request.urlopen('https://fonts.googleapis.com/css2?' + q, timeout=60).read().decode('utf-8')
    url = css.split('url(')[1].split(')')[0]
    data = urllib.request.urlopen(url, timeout=300).read()
    with open(path + '.tmp', 'wb') as fh:
        fh.write(data)
    os.replace(path + '.tmp', path)
    return path


def text_mask(text, font_path, size, index=0, bold=0, spacing=0):
    """一行文字的 1 bit 蒙版（不抗锯齿）；bold = 往右 / 下各加粗几 px。"""
    f = ImageFont.truetype(font_path, size, index=index)
    w = int(sum(f.getlength(c) for c in text) + spacing * max(0, len(text) - 1)) + 8 + bold
    asc, desc = f.getmetrics()
    h = asc + desc + 8 + bold
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    d.fontmode = '1'
    x = 4
    for c in text:
        for bx in range(bold + 1):
            for by in range((bold + 1) if bold > 1 else 1):
                d.text((x + bx, 4 + by), c, font=f, fill=255)
        x += f.getlength(c) + spacing
    bb = m.getbbox()
    return m.crop(bb) if bb else m


def styled_text(text, font_path, size, fill=('#ffe070', '#f0a020'), edge='#2a1050', shadow='#140828', index=0,
                bold=0, spacing=0, edge_w=2, shadow_d=(2, 2), inner=None, pad=2):
    """第三部那种 UI 大字：渐变填色 + 粗描边 + 投影。fill 两色 = 上下渐变；inner = 内描一圈亮边。"""
    m = text_mask(text, font_path, size, index=index, bold=bold, spacing=spacing)
    w, h = m.size
    E = edge_w
    W, H = w + 2 * (E + pad) + abs(shadow_d[0]), h + 2 * (E + pad) + abs(shadow_d[1])
    ox, oy = E + pad, E + pad
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    mp = m.load()

    def stamp(color, dx, dy, grow):
        c = hexc(color) if isinstance(color, str) else color
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        lp = layer.load()
        for y in range(h):
            for x in range(w):
                if mp[x, y] > 127:
                    for gy in range(-grow, grow + 1):
                        for gx in range(-grow, grow + 1):
                            if abs(gx) + abs(gy) > grow + (1 if grow >= 2 else 0):
                                continue
                            X, Y = ox + x + dx + gx, oy + y + dy + gy
                            if 0 <= X < W and 0 <= Y < H:
                                lp[X, Y] = c
        out.alpha_composite(layer)

    if shadow:
        stamp(shadow, shadow_d[0], shadow_d[1], E)
    stamp(edge, 0, 0, E)
    # 渐变填色
    top, bot = hexc(fill[0]), hexc(fill[1] if len(fill) > 1 else fill[0])
    ys = [y for y in range(h) if any(mp[x, y] > 127 for x in range(w))]
    y0, y1 = (min(ys), max(ys)) if ys else (0, h)
    op = out.load()
    for y in range(h):
        k = 0 if y1 == y0 else (y - y0) / (y1 - y0)
        k = min(1, max(0, k))
        # 两段式：上半亮、下半暗，中间一条硬分界（像素风常见的“金属字”）
        if len(fill) >= 3:
            c = hexc(fill[0]) if k < 0.45 else (hexc(fill[1]) if k < 0.75 else hexc(fill[2]))
        else:
            c = tuple(int(top[i] + (bot[i] - top[i]) * (0 if k < 0.5 else 1)) for i in range(3)) + (255,)
        for x in range(w):
            if mp[x, y] > 127:
                op[ox + x, oy + y] = c
    if inner:
        ic = hexc(inner)
        for y in range(h):
            for x in range(w):
                if mp[x, y] > 127 and (y == 0 or mp[x, y - 1] <= 127):
                    op[ox + x, oy + y] = ic
    bb = out.getbbox()
    return out.crop(bb) if bb else out
