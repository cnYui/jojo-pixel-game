# 第四部重画：房间内景的“壳”——天花、后墙（上下两段）、两头的侧墙。
#   2026-11-23 用户看了第一版（一楼剖开、上面画二楼外墙和屋顶）后要求：镜头放在房间里，画成一个个房间的内景当游戏背景，
#   不要从大房子外面看进去。所以室内改成：地板（y 139–179）+ 后墙（墙脚 138 → 天花线 CL）+ 天花（CL 以上，往镜头方向延伸）。
#   家具、门窗仍按 第四部/docs/比例标准.md（门 34、椅面 5、桌面 11、台面 14）；画面有 180 高，所以后墙画到 72 px 高，
#   在门头高度（墙脚上 46 px）压一条挂镜线，把墙分成“人用的下段”和“上段”，门、窗、家具都收在下段里，比例关系就清楚。
from px import shade, mix
from bgkit import FLOOR, dither, rng

CL = 66                      # 天花线（后墙顶）
RAIL = FLOOR - 46            # 挂镜线 / 长押：比门头高一点


def ceiling(cv, x0, x1, cl=CL, c='#e8dcc0', beam=None, boards=True, y0=0):
    """天花：从后墙顶往镜头方向延伸，板缝越靠上（越近）越稀；beam = 梁的颜色（横梁两道）"""
    cv.rect(x0, y0, x1, cl - 1, c)
    if boards:
        y = cl - 3
        step = 3
        while y > y0:
            cv.hline(x0, x1, y, shade(c, -0.1))
            step += 2
            y -= step
    # 越靠近镜头越暗一点（灯在下面）
    for i, yy in enumerate(range(y0, min(cl, y0 + 18))):
        if i < 18:
            dither(cv, x0, yy, x1, yy, shade(c, -0.3), max(0.0, 0.55 - i * 0.03))
    if beam:
        for by_ in (cl - 14, cl - 40):
            if by_ > y0 + 2:
                h = 4 if by_ == cl - 14 else 6
                cv.rect(x0, by_, x1, by_ + h - 1, beam)
                cv.hline(x0, x1, by_, shade(beam, 0.25))
                cv.hline(x0, x1, by_ + h, shade(beam, -0.4))
    cv.rect(x0, cl - 1, x1, cl, shade(c, -0.35))                 # 天花和墙的交线
    cv.hline(x0, x1, cl + 1, shade(c, -0.5))


def back_wall(cv, x0, x1, c, cl=CL, rail=RAIL, upper=None, rail_c='#8a6a44', stripes=None, wains=None, base='#7a5a3c', floor=FLOOR):
    """后墙：下段（墙脚 → 挂镜线）可带竖条壁纸和护墙板；上段（挂镜线 → 天花线）素色，默认比下段暗一档"""
    up = upper or shade(c, -0.08)
    cv.rect(x0, cl + 2, x1, rail - 1, up)
    cv.rect(x0, rail, x1, floor, c)
    if stripes:
        step, sc = stripes
        for x in range(x0 + step // 2, x1, step):
            cv.vline(x, rail + 2, floor, sc)
    if wains:
        h, wc = wains
        cv.rect(x0, floor - h, x1, floor, wc)
        cv.hline(x0, x1, floor - h, shade(wc, 0.25))
        cv.hline(x0, x1, floor - h + 1, shade(wc, -0.2))
        for x in range(x0 + 6, x1, 12):
            cv.vline(x, floor - h + 2, floor - 2, shade(wc, -0.12))
    if rail_c:
        cv.rect(x0, rail, x1, rail + 1, rail_c)
        cv.hline(x0, x1, rail, shade(rail_c, 0.25))
        cv.hline(x0, x1, rail + 2, shade(c, -0.25))
    if base:
        cv.rect(x0, floor - 1, x1, floor, base)
        cv.hline(x0, x1, floor - 1, shade(base, 0.2))
    dither(cv, x0, cl + 2, x1, cl + 4, shade(up, -0.25), 0.5)    # 天花线下面一条暗影


def side_wall(cv, x0, x1, c, cl=CL, left=True, floor=FLOOR):
    """房间两头的侧墙（斜着看过去，颜色压暗；墙脚线和天花线往镜头方向斜开）"""
    w = x1 - x0 + 1
    for i in range(w):
        x = x0 + i if left else x1 - i
        k = (w - 1 - i) / max(1, w - 1)          # 0 = 贴着后墙，1 = 最靠镜头
        yt = int(round(cl - k * 10))
        yb = int(round(floor + k * 12))
        cv.vline(x, 0, 179, mix(c, '#5a4030', 0.28))
        cv.vline(x, 0, yt, mix(c, '#5a4030', 0.42))
        cv.vline(x, yb, 179, mix(c, '#3a2a20', 0.55))
    xe = x1 if left else x0
    cv.vline(xe, cl, floor, mix(c, '#3a2a20', 0.5))


def pendant(cv, cx, cl=CL, drop=22, c='#f8f0c8', w=10, shade_c=None, on=True):
    """吊灯：从天花垂下来（灯罩落在墙的上段）"""
    top = cl - 8
    cv.vline(cx, top, cl + drop - 4, '#4a4a50')
    cv.hline(cx - 2, cx + 2, top, '#6a6a70')
    sc = shade_c or c
    y = cl + drop - 3
    cv.hline(cx - w // 2 + 2, cx + w // 2 - 2, y - 1, shade(sc, -0.25))
    cv.rect(cx - w // 2, y, cx + w // 2, y + 2, sc)
    cv.hline(cx - w // 2, cx + w // 2, y + 2, shade(sc, -0.3))
    if on:
        cv.hline(cx - w // 2 + 1, cx + w // 2 - 1, y + 3, '#fff8d8')


def transom(cv, x0, x1, y0, y1, frame='#6a4a2c', glass='#c8dce4'):
    """门上的气窗 / 栏间"""
    cv.rect(x0, y0, x1, y1, frame)
    cv.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, glass)
    cv.vline((x0 + x1) // 2, y0, y1, frame)
