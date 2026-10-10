"""生成全部对比图：python -B make_all.py（只往 docs\\美术精度对比\\ 写）。"""
import sys
sys.dont_write_bytecode = True
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont
from common import OUT, GAME, Font, ui_box, rect, glyph_next, nearest, frame, xbr2x
import scene as SC

FONT_B = 'C:/Windows/Fonts/Dengb.ttf'
FONT_R = 'C:/Windows/Fonts/Deng.ttf'


def tf(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


F16 = Font(16)
NAME_COLOR = (0x3a, 0x4a, 0x9a, 255)        # GAME_DATA.heroes.jotaro.nameColor
LINES = ['呀嘞呀嘞daze。……你就是花京院典明？', '你身上的气息，和我的“它”一样。']


def wrap(text, maxw):
    out, line, w = [], '', 0
    for ch in text:
        a = F16.adv(ch)
        if w + a > maxw and line:
            if ch in '，。、！？…”）':
                line += ch; w += a; continue
            out.append(line); line, w = '', 0
        line += ch; w += a
    out.append(line)
    return out


def name_tag(ui, tx, y0, name):
    tw = F16.width(name) + 14
    ty = max(0, y0 - 14)
    x = tx - 4
    rect(ui, x, ty, tw + 1, 21, (255, 255, 255, 255))
    rect(ui, x + 2, ty + 2, tw - 3, 17, NAME_COLOR)
    F16.draw(ui, name, tx + 3, ty + 2, '#ffffff')


def dialog_text(ui, tx, y0):
    lines = []
    for t in LINES:
        lines += wrap(t, 620 - tx - 16)
    ly = y0 + 16
    for ln in lines[:3]:
        F16.draw(ui, ln, tx, ly, '#ffffff', outline='#000000')
        ly += 22
    glyph_next(ui, 620 - 18, y0 + 80 - 16)


def dialog_now():
    """现在的对话框（engine\\ui.js drawDialog）：32x32 头像 ×2 + 白框。"""
    ui = Image.new('RGBA', (640, 360), (0, 0, 0, 0))
    y0 = 272
    ui_box(ui, 20, y0, 620, y0 + 80)
    head = Image.open(os.path.join(GAME, 'assets', 'chars', 'jotaro_heads', 'normal_0.png')).convert('RGBA')
    px, py = 28, y0 + 8
    rect(ui, px - 2, py - 2, 68, 68, (255, 255, 255, 255))
    rect(ui, px - 1, py - 1, 66, 66, (0x28, 0x24, 0x46, 255))
    ui.alpha_composite(nearest(head, 2), (px, py))
    tx = px + 64 + 14
    name_tag(ui, tx, y0, '承太郎')
    dialog_text(ui, tx, y0)
    return ui


def dialog_b():
    """方案 B：128x128 高清立绘按 UI 层 1:1 画（屏幕上 256 px），半身压在对话框左边、头探出框外。"""
    import art_portrait_b as PB
    ui = Image.new('RGBA', (640, 360), (0, 0, 0, 0))
    y0 = 272
    ui_box(ui, 20, y0, 620, y0 + 80)
    por = PB.build()
    top = y0 + 80 - 2 - 128 + 1          # 底边贴着框内底线
    # 立绘后面垫一块亮一点的底（框内那一段），深色外套才不会和框底糊在一起
    rect(ui, 22, y0 + 4, 134, 80 - 7, (0x3a, 0x34, 0x7a, 255))
    rect(ui, 22, y0 + 4, 134, 2, (0x4c, 0x46, 0x9c, 255))
    rect(ui, 156, y0 + 4, 1, 80 - 7, (0x5a, 0x52, 0xb0, 255))
    ui.alpha_composite(por, (24, top))
    tx = 24 + 128 + 10
    name_tag(ui, tx, y0, '承太郎')
    dialog_text(ui, tx, y0)
    return ui


def with_ui(scr, ui):
    s = scr.convert('RGBA')
    s.alpha_composite(nearest(ui, 2))
    return s.convert('RGB')


# ------------------------------------------------------------------ 必杀切入（世界层 320x180，照 ui_cards.js renderCutin 的版式）
def burst_bg(seed=5):
    cols = [(0x24, 0x1c, 0x6a), (0x3e, 0x32, 0xa8), (0x5a, 0x4a, 0xd0)]   # heroes.jotaro.burst
    im = Image.new('RGBA', (320, 180), cols[0] + (255,))
    px = im.load()
    for y in range(180):
        for x in range(320):
            a = math.atan2(y - 90, x - 160)
            k = int((a + math.pi) / (2 * math.pi) * 18) % 2
            r = math.hypot(x - 160, y - 90)
            px[x, y] = (cols[1] if k else cols[2]) + (255,) if r > 18 else cols[0] + (255,)
    d = ImageDraw.Draw(im)
    rnd = random.Random(seed)
    for _ in range(40):
        a = rnd.random() * 2 * math.pi
        r0 = 62 + rnd.random() * 30
        d.line([(160 + math.cos(a) * r0, 90 + math.sin(a) * r0), (160 + math.cos(a) * 260, 90 + math.sin(a) * 260)],
               fill=(255, 255, 255, 140), width=1)
    return im


def white_outline(spr, ow):
    from common import aura
    return aura(spr, '#ffffff', grow=ow, alpha=1.0)


def cutin(level):
    w = burst_bg()
    if level == 'now':
        hd = Image.open(os.path.join(GAME, 'assets', 'chars', 'jotaro_heads', 'angry_1.png')).convert('RGBA')
        big = nearest(hd, 4)
    else:
        import art_portrait_b as PB
        big = PB.build()
    ol = white_outline(big, 2)
    w.alpha_composite(ol, (20 - 2, 26 - 2))
    w.alpha_composite(big, (20, 26))
    return nearest(w, 4).convert('RGB')


# ------------------------------------------------------------------ 角色对照
def sprite_sheet(titled=True):
    import art_jotaro_a as AJ
    import art_starplat_a as AS
    from palettes import JOTARO, STARPLAT
    jo0, _ = frame('jotaro'); sp0, _ = frame('starplat')
    jo0 = jo0.crop(jo0.getbbox()); sp0 = sp0.crop(sp0.getbbox())
    jo1 = AJ.build().image(JOTARO); sp1 = AS.build().image(STARPLAT)
    jo1 = jo1.crop(jo1.getbbox()); sp1 = sp1.crop(sp1.getbbox())
    items = [('现在（每像素 ×8）', nearest(jo0, 8)), ('方案 A（每像素 ×4）', nearest(jo1, 4)),
             ('现在（每像素 ×8）', nearest(sp0, 8)), ('方案 A（每像素 ×4）', nearest(sp1, 4))]
    gap, m = 40, (30 if titled else 0)
    top = 80 if titled else 0
    W = m * 2 + sum(i.width for _, i in items) + gap * 3
    H = top + 34 + max(i.height for _, i in items) + m
    out = Image.new('RGB', (W, H), (232, 230, 236) if titled else (238, 236, 242))
    d = ImageDraw.Draw(out)
    if titled:
        d.text((30, 18), '方案 A：承太郎 / 白金之星 逐像素重画（这里放大 2 倍看，屏幕上实际只有一半大）', font=tf(28, True), fill=(30, 26, 50))
    x = m
    for lab, im in items:
        d.text((x, top), lab, font=tf(20), fill=(70, 66, 90))
        bgc = Image.new('RGBA', im.size, (196, 200, 214, 255)); bgc.alpha_composite(im)
        out.paste(bgc.convert('RGB'), (x, top + 34))
        x += im.width + gap
    return out


def portrait_sheet(titled=True):
    import art_portrait_b as PB
    hd = Image.open(os.path.join(GAME, 'assets', 'chars', 'jotaro_heads', 'normal_0.png')).convert('RGBA')
    por = PB.build()
    a, b = nearest(hd, 8), nearest(por, 2)
    m = 30 if titled else 0
    top = 62 if titled else 0
    gap = 30 if titled else 20
    out = Image.new('RGB', (m * 2 + a.width + b.width + gap, top + 30 + max(a.height, b.height) + m),
                    (232, 230, 236) if titled else (238, 236, 242))
    d = ImageDraw.Draw(out)
    if titled:
        d.text((30, 16), '方案 B：对话头像 32×32 → 128×128 高清像素立绘（同样占 256×256 屏幕像素）', font=tf(26, True), fill=(30, 26, 50))
    for i, (lab, im) in enumerate((('现在 32×32（每像素 ×8）', a), ('方案 B 128×128（×2）', b))):
        x = m + i * (a.width + gap)
        d.text((x, top), lab, font=tf(18), fill=(70, 66, 90))
        bgc = Image.new('RGBA', im.size, (40, 36, 70, 255)); bgc.alpha_composite(im)
        out.paste(bgc.convert('RGB'), (x, top + 30))
    return out


PUNCT = '，。、！？；：）”…'


def wrap_px(text, font, maxw):
    out, line = [], ''
    for ch in text:
        if font.getlength(line + ch) > maxw and line and ch not in PUNCT:
            out.append(line); line = ''
        line += ch
    out.append(line)
    return out


def para(d, x, y, text, font, maxw, fill, lh):
    for ln in wrap_px(text, font, maxw):
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def overview(s0, sc, sa, sb, dnow, cnow, cb):
    W = 1920
    INK, SUB, LAB = (26, 22, 48), (80, 76, 100), (110, 106, 130)
    box = (78 * 4, 92 * 4, 228 * 4, 178 * 4)          # 600x344：三个角色的区域，1:1
    hbox = (96 * 4, 92 * 4, 171 * 4, 134 * 4)         # 300x168：两个头，放大 2 倍看
    cols = [('方案 0 · 现在', '原样：世界层 320×180，每个像素在屏幕上放大成 4×4。', s0),
            ('方案 C · 算法放大', 'xBR 算法把角色和背景放大 2 倍再 ×2 显示：边缘圆一些，细节没有变多。', sc),
            ('方案 A · 精度翻倍重画', '世界层改 640×360，承太郎和白金之星按 2 倍分辨率逐像素重画；花京院仍是算法放大，作对照。', sa)]
    sheet = sprite_sheet(titled=False)
    psheet = portrait_sheet(titled=False)
    H = 3400
    out = Image.new('RGB', (W, H), (238, 236, 242))
    d = ImageDraw.Draw(out)
    d.text((30, 24), 'JoJo 游戏 · 角色美术精度 4 个方案', font=tf(46, True), fill=INK)
    d.text((32, 88), '同一组角色（空条承太郎 + 身后的白金之星 + 花京院）、同一块背景（校门）。标“1:1”的都是 1280×720 屏幕上的实际像素大小，没有缩放。',
           font=tf(22), fill=SUB)
    # ---- 第一 / 二排：三个方案的场景（1:1）+ 头部放大 2 倍
    gx, gw, y = 30, 600, 150
    for i, (t, desc, scr) in enumerate(cols):
        x = gx + i * (gw + 30)
        d.text((x, y), t, font=tf(30, True), fill=INK)
        para(d, x, y + 42, desc, tf(19), gw, SUB, 26)
        out.paste(scr.crop(box), (x, y + 100))
        out.paste(scr.crop(hbox).resize((600, 336), Image.NEAREST), (x, y + 100 + 344 + 46))
    d.text((gx, y + 100 + 344 + 12), '↑ 1:1 屏幕截取        ↓ 同一位置放大 2 倍看头部', font=tf(20), fill=LAB)
    # ---- 第三排：方案 A 单个角色
    y = 150 + 100 + 344 + 46 + 336 + 40
    d.line([(30, y - 18), (W - 30, y - 18)], fill=(200, 196, 210), width=2)
    d.text((30, y), '方案 A 的手绘稿单独看（白金之星在场景里大半身被承太郎挡住，这里看全身）', font=tf(26, True), fill=INK)
    out.paste(sheet, (30, y + 44))
    nx = 30 + sheet.width + 40
    notes = ['· 原调色板不换色，每种材质只在明暗阶里补 1 级（帽子 / 外套多一级中间调和一级反光、皮肤多一级深影和高光等）。',
             '· 描边从 2px 削成 1px，同样大小里能放下五官、帽徽、鬓角、耳朵、金链每一节、纽扣、袖口插进口袋、裤缝。',
             '· 白金之星：手画胸肌下沿、腹白线、三排腹肌、肩、大腿和膝盖的分界线，再按“光从左上来”统一做受光边和背光边；头发加了发束。',
             '· 尺寸、脚点、身高比例和原图完全一致（2 倍坐标），碰撞框 / 站位数值乘 2 就能沿用。']
    yy = y + 70
    for n in notes:
        yy = para(d, nx, yy, n, tf(20), W - 30 - nx, SUB, 30) + 14
    # ---- 第四排：方案 B 对话框
    y = y + 44 + sheet.height + 40
    d.line([(30, y - 18), (W - 30, y - 18)], fill=(200, 196, 210), width=2)
    d.text((30, y), '方案 B · 场景小人不变 + 高清立绘', font=tf(30, True), fill=INK)
    d.text((30, y + 42), '世界层不动；对话头像、必杀切入换成 128×128 高清像素立绘（对话框里按 UI 层 1:1 画，屏幕上每个像素 2×2）。',
           font=tf(19), fill=SUB)
    yb = y + 84
    crop_d = (0, 420, 1280, 720)
    d.text((30, yb), '现在的对话框（1:1）', font=tf(20, True), fill=LAB)
    out.paste(dnow.crop(crop_d), (30, yb + 28))
    yb2 = yb + 28 + 300 + 16
    d.text((30, yb2), '方案 B 的对话框（1:1）', font=tf(20, True), fill=LAB)
    out.paste(sb.crop(crop_d), (30, yb2 + 28))
    rx = 30 + 1280 + 30
    d.text((rx, yb), '头像本身（同一屏幕大小）', font=tf(20, True), fill=LAB)
    out.paste(psheet, (rx, yb + 28))
    # ---- 第五排：必杀切入
    y = yb2 + 28 + 300 + 50
    d.line([(30, y - 18), (W - 30, y - 18)], fill=(200, 196, 210), width=2)
    d.text((30, y), '方案 B · 必杀切入（左半屏的头像，1:1）', font=tf(26, True), fill=INK)
    cbox = (64, 88, 64 + 540, 88 + 540)
    out.paste(cnow.crop(cbox), (30, y + 44))
    out.paste(cb.crop(cbox), (30 + 540 + 20, y + 44))
    d.text((30, y + 44 + 548), '现在：32×32 头像在世界层放大 4 倍 → 屏幕上每个像素 16×16', font=tf(18), fill=LAB)
    d.text((30 + 560, y + 44 + 548), '方案 B：128×128 立绘 → 每个像素 4×4，和场景一样细', font=tf(18), fill=LAB)
    nx = 30 + 540 * 2 + 20 + 40
    para(d, nx, y + 60, '现在游戏里最粗的其实是这里：必杀切入把 32×32 的头像放大到半个屏幕，一个像素在屏幕上是 16×16 的方块。'
         '换成 128×128 的立绘后同样大小、密度和场景小人一致。右半边的替身头像也要照这个尺寸重画（本样稿没画）。',
         tf(20), W - 30 - nx, SUB, 30)
    fy = y + 44 + 548 + 50
    d.text((30, fy), '图都由 docs\\美术精度对比\\src\\make_all.py 生成；角色原图来自 assets\\chars\\（idle 第 0 帧），背景 assets\\bg\\school_gate。',
           font=tf(18), fill=(130, 126, 150))
    return out.crop((0, 0, W, fy + 44))


def main():
    s0 = SC.scene_now()
    sc = SC.scene_algo('xbr')
    sa = SC.scene_redraw()
    dnow = with_ui(s0, dialog_now())
    sb = with_ui(s0, dialog_b())
    cnow, cb = cutin('now'), cutin('b')
    save = lambda im, n: im.save(os.path.join(OUT, n))
    save(s0, '方案0_现在.png')
    save(sc, '方案C_算法放大.png')
    save(sa, '方案A_精度翻倍重画.png')
    save(sb, '方案B_高清立绘对话框.png')
    save(dnow, '方案0_现在的对话框.png')
    both = Image.new('RGB', (1290, 720), (238, 236, 242))
    both.paste(cnow.crop((0, 0, 640, 720)), (0, 0)); both.paste(cb.crop((0, 0, 640, 720)), (650, 0))
    save(both, '方案B_必杀切入对比.png')
    save(sprite_sheet(), '方案A_角色对照.png')
    save(portrait_sheet(), '方案B_立绘对照.png')
    save(overview(s0, sc, sa, sb, dnow, cnow, cb), '对比总图.png')
    if F16.missing:
        print('missing glyphs:', F16.missing)
    print('ok')


if __name__ == '__main__':
    main()
