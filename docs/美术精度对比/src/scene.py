"""同一个场景（校门：承太郎 + 身后的白金之星 + 花京院）按各方案合成 1280x720 屏幕图。"""
import sys
sys.dont_write_bytecode = True
from PIL import Image
from common import frame, bg_school, put, aura, nearest, scale2x, xbr2x

# 世界坐标（320x180 世界层），和游戏一样：脚点 = pivot
JO_X, JO_Y = 120, 160
KA_X, KA_Y = 186, 161
STAND_DX, STAND_Z = -6, 6          # tools\registry\stands.json starplat.idle
AURA = '#b090ff'                    # starplat 光环色
STAND_ALPHA = 0.92                  # engine\stand.js this.alpha

UPSCALERS = {
    'scale2x': scale2x,
    'xbr': lambda im: xbr2x(im, blend=True),
    'xbr_noblend': lambda im: xbr2x(im, blend=False),
}


def _chars_world(s, jo, sp, ka):
    """jo / sp / ka = (图, pivot)，已经是该世界分辨率下的图。s = 世界层倍数（1 = 320x180，2 = 640x360）。"""
    layer = Image.new('RGBA', (320 * s, 180 * s), (0, 0, 0, 0))
    sx, sy = (JO_X + STAND_DX) * s, (JO_Y - STAND_Z) * s
    # 替身：光环剪影（膨胀 s 像素、0.55）+ 本体 0.92
    a = aura(sp[0], AURA, grow=s, alpha=0.55)
    put(layer, a, (sp[1][0] + s, sp[1][1] + s), sx, sy)
    put(layer, sp[0], sp[1], sx, sy, alpha=STAND_ALPHA)
    put(layer, jo[0], jo[1], JO_X * s, JO_Y * s)
    put(layer, ka[0], ka[1], KA_X * s, KA_Y * s, flip=True)
    return layer


def screen(world):
    """世界层 → 1280x720 屏幕（最近邻整数倍）。"""
    return nearest(world, 1280 // world.width).convert('RGB')


def scene_now():
    bg = bg_school()
    jo, sp, ka = frame('jotaro'), frame('starplat'), frame('kakyoin')
    w = bg.copy()
    w.alpha_composite(_chars_world(1, jo, sp, ka))
    return screen(w)


def scene_algo(name='xbr'):
    f = UPSCALERS[name]
    bg = f(bg_school())

    def up(cid):
        im, pv = frame(cid)
        return f(im), (pv[0] * 2, pv[1] * 2)
    w = bg.copy()
    w.alpha_composite(_chars_world(2, up('jotaro'), up('starplat'), up('kakyoin')))
    return screen(w)


def scene_redraw(bg_mode='nearest'):
    """方案 A：世界层 640x360；承太郎、白金之星用手绘 2 倍稿，花京院用算法放大（对照），背景先沿用原图（最近邻 2 倍）。"""
    import art_jotaro_a as AJ
    import art_starplat_a as AS
    from palettes import JOTARO, STARPLAT
    bg = bg_school()
    bg = nearest(bg, 2) if bg_mode == 'nearest' else xbr2x(bg, blend=True)
    jo = (AJ.build().image(JOTARO), AJ.PIVOT)
    sp = (AS.build().image(STARPLAT), AS.PIVOT)
    im, pv = frame('kakyoin')
    ka = (xbr2x(im, blend=True), (pv[0] * 2, pv[1] * 2))
    w = bg.copy()
    w.alpha_composite(_chars_world(2, jo, sp, ka))
    return screen(w)
