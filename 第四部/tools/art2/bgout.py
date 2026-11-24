# 第四部重画：户外部件（路面、围墙、树篱、电线杆、路灯、售货机、候车亭、树、整栋房子）。
#   尺寸按 第四部/docs/比例标准.md；by = 物件落地的那一行，户外默认 GROUND = 136（围墙 / 房子的墙脚），
#   再往下是人行道（人站在 y ≈ 142–176）和马路。
import math

from px import shade, mix
from bgkit import rng, dither, shadow, siding, roof_hip, window_ext

GROUND = 136


def sidewalk(cv, x0, x1, y0=GROUND + 1, y1=165, c='#b9b5ad', curb='#8f8b85', seed=2):
    """人行道：方砖缝（近大远小）+ 路沿石"""
    cv.rect(x0, y0, x1, y1, c)
    cv.hline(x0, x1, y0, shade(c, -0.25))
    dither(cv, x0, y0 + 1, x1, y0 + 2, shade(c, -0.14), 0.5)
    ys = [y0 + 5, y0 + 12, y0 + 21]
    for y in ys:
        if y < y1 - 2:
            cv.hline(x0, x1, y, shade(c, -0.12))
    step = 22
    for row, (ya, yb) in enumerate(zip([y0] + ys, ys + [y1 - 2])):
        off = (row % 2) * (step // 2)
        for x in range(x0 - step + off, x1, step + row * 3):
            if x >= x0:
                cv.vline(x, min(ya + 1, yb), yb - 1, shade(c, -0.1))
    r = rng(seed)
    for _ in range((x1 - x0) // 6):
        cv.put(r.randint(x0, x1 + 1), r.randint(y0 + 2, y1 - 2), shade(c, r.choice([-0.08, 0.08])))
    cv.rect(x0, y1 - 2, x1, y1, curb)
    cv.hline(x0, x1, y1 - 2, shade(curb, 0.3))
    cv.hline(x0, x1, y1, shade(curb, -0.3))
    for x in range(x0 + 10, x1, 28):
        cv.vline(x, y1 - 1, y1, shade(curb, -0.2))


def asphalt(cv, x0, x1, y0=166, y1=179, c='#4c4c54', line='#e6e2d6', dash=(14, 10), seed=4):
    cv.rect(x0, y0, x1, y1, c)
    r = rng(seed)
    for _ in range((x1 - x0) * (y1 - y0) // 14):
        cv.put(r.randint(x0, x1 + 1), r.randint(y0, y1 + 1), shade(c, r.choice([-0.12, 0.1, 0.16])))
    cv.hline(x0, x1, y0, shade(c, -0.3))
    if line:
        y = (y0 + y1) // 2 + 2
        if dash:
            for x in range(x0 + 4, x1, dash[0] + dash[1]):
                cv.hline(x, min(x1, x + dash[0] - 1), y, line)
        else:
            cv.hline(x0, x1, y, line)


def block_wall(cv, x0, x1, by=GROUND, h=14, c='#c9c3b5', cap=True):
    """砌块围墙：h = 14（85 cm 的矮墙）到 24（1.45 m）"""
    y0 = by - h + 1
    cv.rect(x0, y0, x1, by, c)
    for j, y in enumerate(range(y0 + (2 if cap else 0), by, 4)):
        cv.hline(x0, x1, y, shade(c, -0.14))
        for x in range(x0 + (j % 2) * 5, x1, 10):
            cv.vline(x, y + 1, min(by, y + 3), shade(c, -0.14))
    if cap:
        cv.rect(x0 - 1, y0 - 1, x1 + 1, y0, shade(c, 0.18))
        cv.hline(x0 - 1, x1 + 1, y0 + 1, shade(c, -0.25))
    cv.hline(x0, x1, by, shade(c, -0.3))


def hedge(cv, x0, x1, y_bot, h=8, seed=0, cols=('#2e5a3a', '#4a7c4a', '#6e9e5a', '#94c070')):
    r = rng(seed)
    y_top = y_bot - h + 1
    for x in range(x0, x1 + 1):
        bump = int(round(1.2 * math.sin(x * 0.55 + seed) + r.uniform(-0.6, 0.6)))
        cv.vline(x, y_top - bump, y_bot, cols[1])
    for _ in range((x1 - x0) * h // 3):
        x, y = int(r.randint(x0, x1 + 1)), int(r.randint(y_top - 1, y_bot + 1))
        if cv.solid(x, y):
            cv.put(x, y, cols[int(r.choice([0, 2, 2, 3]))] if y < y_top + h * 0.6 else cols[0])
    for x in range(x0, x1 + 1):
        cv.put(x, y_bot, cols[0])


def gate_post(cv, cx, by=GROUND, h=23, w=5, c='#b9a58c', cap='#8a7a66', plate=None):
    """门柱（140 cm）"""
    x0 = cx - w // 2
    cv.rect(x0, by - h + 1, x0 + w - 1, by, c)
    cv.vline(x0, by - h + 1, by, shade(c, 0.2))
    cv.vline(x0 + w - 1, by - h + 1, by, shade(c, -0.25))
    cv.rect(x0 - 1, by - h - 1, x0 + w, by - h, cap)
    cv.hline(x0 - 1, x0 + w, by - h - 1, shade(cap, 0.25))
    if plate:
        cv.rect(x0 + 1, by - h + 5, x0 + w - 2, by - h + 10, plate)


def gate_iron(cv, x0, x1, by=GROUND, h=19, c='#3a3a44', open_=False):
    """铁栅门（两扇）；open_ = 敞开（只在两边各留一截）"""
    if open_:
        for a, b in ((x0, x0 + 2), (x1 - 2, x1)):
            cv.rect(a, by - h + 1, b, by, c)
        return
    cv.hline(x0, x1, by - h + 1, c)
    cv.hline(x0, x1, by - 2, c)
    for x in range(x0, x1 + 1, 2):
        cv.vline(x, by - h + 1, by, c)
    cv.vline((x0 + x1) // 2, by - h + 1, by, shade(c, 0.3))


def mailbox(cv, cx, by=GROUND, c='#d0343a', h=16):
    """家门口的信箱（红色铁皮箱，立在一根杆上）"""
    cv.vline(cx, by - h + 6, by, '#5a5a62')
    cv.rect(cx - 3, by - h, cx + 3, by - h + 5, c)
    cv.hline(cx - 3, cx + 3, by - h, shade(c, 0.3))
    cv.hline(cx - 2, cx + 2, by - h + 2, shade(c, -0.45))
    cv.vline(cx + 3, by - h + 1, by - h + 5, shade(c, -0.3))


def post_box(cv, cx, by=GROUND, c='#d0343a'):
    """街上的邮筒（方形，130 cm = 22 px）"""
    cv.rect(cx - 4, by - 21, cx + 4, by - 6, c)
    cv.hline(cx - 4, cx + 4, by - 21, shade(c, 0.3))
    cv.vline(cx + 4, by - 20, by - 6, shade(c, -0.3))
    cv.hline(cx - 2, cx + 2, by - 17, '#2a1a1e')
    cv.rect(cx - 2, by - 13, cx + 2, by - 10, '#f0ece0')
    cv.rect(cx - 1, by - 5, cx + 1, by, shade(c, -0.4))


def pole(cv, x, by=GROUND, top=-6, c='#9a9488', box=True):
    """电线杆（10 m，顶在画面外）；返回挂线点 [(x, y)…]"""
    cv.rect(x - 1, top, x + 1, by, c)
    cv.vline(x - 1, top, by, shade(c, 0.22))
    cv.vline(x + 1, top, by, shade(c, -0.25))
    for y in (10, 20):
        cv.rect(x - 9, y, x + 9, y + 1, shade(c, -0.2))
        cv.hline(x - 9, x + 9, y, shade(c, 0.1))
        for dx in (-8, -4, 4, 8):
            cv.put(x + dx, y - 1, '#d8d4c8')
    if box:
        cv.rect(x - 3, 34, x + 3, 44, '#6e6a62')
        cv.hline(x - 3, x + 3, 34, '#8a867c')
        cv.vline(x + 3, 35, 44, '#4e4a44')
    cv.rect(x - 1, by - 12, x + 1, by - 8, '#e0c040')        # 警示黄带
    cv.hline(x - 1, x + 1, by - 10, '#2a2a30')
    return [(x - 8, 9), (x - 4, 9), (x + 4, 9), (x + 8, 9), (x - 8, 19), (x + 8, 19)]


def wires(cv, pts_a, pts_b, sag=7, c='#2a2a32'):
    """两根杆之间的电线（抛物线下垂）"""
    for (xa, ya), (xb, yb) in zip(pts_a, pts_b):
        n = abs(xb - xa)
        for i in range(n + 1):
            t = i / max(1, n)
            x = xa + (xb - xa) * t
            y = ya + (yb - ya) * t + sag * 4 * t * (1 - t)
            cv.put(int(round(x)), int(round(y)), c)


def street_lamp(cv, x, by=GROUND, h=76, c='#7a7e88', on=False, arm=10, side=1):
    """路灯（4.6 m）；返回灯头位置"""
    cv.rect(x, by - h, x + 1, by, c)
    cv.vline(x, by - h, by, shade(c, 0.25))
    cv.hline(x, x + side * arm, by - h, c)
    hx = x + side * arm
    cv.rect(min(hx, hx - side * 4), by - h + 1, max(hx, hx - side * 4), by - h + 2, '#fff2b0' if on else '#c8ccd4')
    cv.rect(x - 1, by - 3, x + 2, by, shade(c, -0.25))
    return hx - side * 2, by - h + 2


def vending(cv, cx, by=GROUND, body='#d8303a', w=17, h=30, seed=0):
    """自动售货机：183 × 100 cm = 30 × 17 px"""
    x0 = cx - w // 2
    x1 = x0 + w - 1
    y0 = by - h + 1
    cv.rect(x0, y0, x1, by, body)
    cv.hline(x0, x1, y0, shade(body, 0.3))
    cv.vline(x1, y0, by, shade(body, -0.3))
    cv.vline(x0, y0, by, shade(body, 0.12))
    cv.rect(x0 + 2, y0 + 2, x1 - 2, y0 + 14, '#f4f0e6')
    r = rng(seed)
    cols = ['#e04040', '#3a7ad0', '#f0b030', '#40a060', '#f08030', '#8a50c0']
    for yy in (y0 + 3, y0 + 7, y0 + 11):
        for xx in range(x0 + 3, x1 - 2, 2):
            cv.vline(xx, yy, yy + 2, cols[int(r.randint(len(cols)))])
        cv.hline(x0 + 2, x1 - 2, yy + 3, '#c8c4b8')
    cv.rect(x1 - 4, y0 + 16, x1 - 2, y0 + 20, '#2a2a30')      # 投币口
    cv.put(x1 - 3, y0 + 17, '#60e080')
    cv.rect(x0 + 2, by - 6, x1 - 2, by - 3, '#2a2a30')         # 取物口
    cv.hline(x0 + 3, x1 - 3, by - 6, '#5a5a62')
    cv.hline(x0, x1, by, shade(body, -0.45))
    shadow(cv, x0, x1 + 2, by + 1, 0.45, h=1)
    return x0, y0, x1, by


def bus_stop(cv, cx, by=GROUND, w=46, h=38, roof='#5a7a9a', bench=True):
    """公交候车亭（顶 2.3 m）+ 长椅（椅面 5）"""
    x0 = cx - w // 2
    x1 = x0 + w - 1
    y0 = by - h + 1
    cv.rect(x0 - 2, y0, x1 + 2, y0 + 2, roof)
    cv.hline(x0 - 2, x1 + 2, y0, shade(roof, 0.3))
    cv.hline(x0 - 2, x1 + 2, y0 + 3, shade(roof, -0.4))
    for x in (x0, x1):
        cv.vline(x, y0 + 3, by, '#8a8e96')
    cv.rect(x0 + 1, y0 + 5, x1 - 1, by - 12, '#b8d0dc')
    cv.line(x0 + 4, by - 14, x0 + 16, y0 + 7, '#d8e8f0')
    cv.hline(x0 + 1, x1 - 1, by - 12, '#8a8e96')
    if bench:
        cv.rect(x0 + 6, by - 6, x1 - 6, by - 5, '#b08a5a')
        cv.hline(x0 + 6, x1 - 6, by - 4, '#7a5a38')
        for x in (x0 + 8, x1 - 8):
            cv.vline(x, by - 4, by, '#5a5a62')


def sign_post(cv, x, by=GROUND, h=44, kind='bus', c='#8a8e96'):
    """立牌：bus = 公交站牌（圆牌 + 时刻表）；stop = 倒三角的停车让行；arrow = 蓝色指路牌"""
    cv.vline(x, by - h, by, c)
    if kind == 'bus':
        cv.ellipse(x, by - h - 3, 4, 4, '#3a8a5a')
        cv.ellipse(x, by - h - 3, 3, 3, '#f4f4ec')
        cv.hline(x - 2, x + 2, by - h - 3, '#3a8a5a')
        cv.rect(x - 3, by - h + 4, x + 3, by - h + 12, '#f0ece0')
        for yy in range(by - h + 5, by - h + 12, 2):
            cv.hline(x - 2, x + 2, yy, '#9a968a')
    elif kind == 'stop':
        for i in range(6):
            cv.hline(x - 5 + i, x + 5 - i, by - h - 6 + i, '#d03030')
        cv.hline(x - 3, x + 3, by - h - 5, '#f4f4ec')
    elif kind == 'arrow':
        cv.rect(x - 12, by - h - 6, x + 12, by - h + 2, '#2a6ac0')
        cv.hline(x - 8, x + 6, by - h - 2, '#f4f4ec')
        cv.put(x + 5, by - h - 3, '#f4f4ec')
        cv.put(x + 5, by - h - 1, '#f4f4ec')
        cv.put(x + 7, by - h - 2, '#f4f4ec')


LEAF = ('#2e5a3a', '#3e7a48', '#62a05a', '#8cc070')
SAKURA = ('#c86a94', '#ec98bc', '#f8bcd4', '#ffe0ec')


def tree(cv, cx, by=GROUND, h=96, w=60, seed=0, leaf=LEAF, trunk=('#5a4030', '#3e2a20')):
    """行道树 / 樱花树（换 leaf 配色）：6–8 m"""
    r = rng(seed)
    tw = max(3, w // 14)
    top = by - h
    cv.rect(cx - tw // 2, top + int(h * .45), cx + tw // 2, by, trunk[0])
    cv.vline(cx - tw // 2, top + int(h * .45), by, trunk[1])
    for s in (-1, 1):
        cv.line(cx, top + int(h * .52), cx + s * int(w * .22), top + int(h * .32), trunk[0])
    ccx, ccy, rx, ry = cx, top + h * .3, w * .46, h * .28
    blobs = []
    for _ in range(int(w / 2.6)):
        a = r.uniform(0, 2 * math.pi)
        rr = math.sqrt(r.uniform(0, 1))
        blobs.append((ccx + math.cos(a) * rx * rr, ccy + math.sin(a) * ry * rr, r.uniform(w * .11, w * .18)))
    blobs.sort(key=lambda b: b[1])
    for bx, by_, br in blobs:
        cv.ellipse(bx, by_ + 1.5, br, br, leaf[0])
    for bx, by_, br in blobs:
        cv.ellipse(bx, by_, br, br * .95, leaf[1])
    for bx, by_, br in blobs:
        cv.ellipse(bx - br * .2, by_ - br * .3, br * .62, br * .55, leaf[2])
    for bx, by_, br in blobs[: len(blobs) // 2]:
        cv.ellipse(bx - br * .3, by_ - br * .45, br * .28, br * .22, leaf[3])


def house(cv, x0, x1, by=GROUND, s=0.88, wall_c='#e6dccb', roof_c='#3e4a5e', door_x=None, door_c='#7a5a40', lit=None,
          win1=None, win2=None, floors=2, trim='#f0ece0', porch=True, big1=None):
    """两层日式民宅的正面。s = 退到围墙后面的缩放（0.85–0.9）。
    尺寸（s = 1 时）：地台 4、层高 46、门 34 × 17、一楼窗台离地 19 / 窗顶 37、二楼窗台 65 / 窗顶 83、檐口 94、屋脊 120。
    door_x = 门中心；win1 / win2 = 一 / 二楼窗的中心 x 列表（缺省自动排）；big1 = 一楼落地窗的中心 x 列表；lit = 亮灯的窗 x 集合"""
    def Sx(v):
        return int(round(v * s))
    lit = set(lit or [])
    eave = by - Sx(94 if floors == 2 else 48)
    ridge = eave - Sx(26)
    siding(cv, x0, eave, x1, by, wall_c, step=max(3, Sx(4)))
    cv.rect(x0, by - Sx(4), x1, by, shade(wall_c, -0.35))                       # 地台
    cv.hline(x0, x1, by - Sx(4), shade(wall_c, -0.15))
    ww = Sx(22)
    if win1 is None:
        win1 = [x for x in range(x0 + ww, x1 - ww // 2, max(ww + 12, (x1 - x0) // 3)) if door_x is None or abs(x - door_x) > ww]
    if win2 is None:
        win2 = list(range(x0 + ww, x1 - ww // 2, max(ww + 10, (x1 - x0) // 3)))
    for wx in win1:
        window_ext(cv, wx - ww // 2, by - Sx(37), wx + ww // 2, by - Sx(19), frame=trim, lit='#f6d98a' if wx in lit else None)
    for wx in (big1 or []):
        bw = Sx(46)
        window_ext(cv, wx - bw // 2, by - Sx(38), wx + bw // 2, by - Sx(5), frame=trim, lit='#f6d98a' if wx in lit else None, nx=2)
    if door_x is not None:
        dw, dh = max(13, Sx(17)), Sx(34)
        dy1 = by - Sx(4)
        cv.rect(door_x - dw // 2 - 2, dy1 - dh - 2, door_x + dw // 2 + 2, dy1, shade(door_c, -0.35))
        cv.rect(door_x - dw // 2, dy1 - dh, door_x + dw // 2, dy1, door_c)
        cv.vline(door_x, dy1 - dh, dy1, shade(door_c, -0.25))
        cv.put(door_x - 2, dy1 - Sx(17), '#e8c860')
        cv.put(door_x + 2, dy1 - Sx(17), '#e8c860')
        cv.rect(door_x - dw // 2 - 4, dy1 + 1, door_x + dw // 2 + 4, by, '#a8a296')    # 门前台阶
        cv.hline(door_x - dw // 2 - 4, door_x + dw // 2 + 4, dy1 + 1, '#c8c2b6')
        if porch:                                                                     # 玄关雨披
            py = dy1 - dh - Sx(8)
            cv.rect(door_x - dw // 2 - 6, py, door_x + dw // 2 + 6, py + 2, roof_c)
            cv.hline(door_x - dw // 2 - 6, door_x + dw // 2 + 6, py, shade(roof_c, 0.3))
            cv.hline(door_x - dw // 2 - 6, door_x + dw // 2 + 6, py + 3, shade(roof_c, -0.5))
    if floors == 2:
        my = by - Sx(48)                                                             # 一二楼之间的腰檐
        cv.rect(x0 - 3, my, x1 + 3, my + Sx(4), roof_c)
        cv.hline(x0 - 3, x1 + 3, my, shade(roof_c, 0.3))
        cv.hline(x0 - 3, x1 + 3, my + Sx(4) + 1, shade(roof_c, -0.5))
        for wx in win2:
            window_ext(cv, wx - ww // 2, by - Sx(83), wx + ww // 2, by - Sx(65), frame=trim, lit='#f6d98a' if wx in lit else None)
    roof_hip(cv, x0 - 5, x1 + 5, eave, ridge, roof_c, inset=Sx(22))
    return dict(eave=eave, ridge=ridge)


def car(cv, cx, by=150, c='#c8ccd4', w=72, h=23, face=1, glass='#5a7890'):
    """轿车（高 140、长 440 cm = 23 × 73 px）；by = 轮胎着地的那一行"""
    x0 = cx - w // 2
    x1 = x0 + w - 1
    # 车身下半
    cv.rect(x0, by - 14, x1, by - 4, c)
    cv.hline(x0 + 1, x1 - 1, by - 14, shade(c, 0.3))
    cv.hline(x0, x1, by - 4, shade(c, -0.35))
    cv.hline(x0, x1, by - 9, shade(c, -0.15))
    # 车顶 / 车窗
    a, b = x0 + (16 if face > 0 else 12), x1 - (12 if face > 0 else 16)
    for i in range(8):
        k = max(0, 4 - i)
        cv.hline(a + k, b - k, by - 22 + i, c if i < 1 else glass)
    cv.hline(a + 4, b - 4, by - 22, shade(c, 0.3))
    cv.vline((a + b) // 2, by - 21, by - 15, c)
    # 轮子
    for wx in (x0 + 14, x1 - 14):
        cv.ellipse(wx, by - 4, 4.5, 4.5, '#1c1c22')
        cv.ellipse(wx, by - 4, 2, 2, '#8a8e98')
    # 车灯
    hx = x1 if face > 0 else x0
    tx = x0 if face > 0 else x1
    cv.rect(hx - (1 if face > 0 else 0), by - 12, hx + (0 if face > 0 else 1), by - 10, '#fff0b0')
    cv.rect(tx - (0 if face > 0 else 1), by - 12, tx + (1 if face > 0 else 0), by - 10, '#d03a3a')
    shadow(cv, x0 + 2, x1 - 2, by + 1, 0.5, h=2)


def sakura(cv, cx, by=GROUND, h=100, w=70, seed=0):
    """樱花树：沿用旧背景库的画法（一团团粉色连成片 + 亮面 + 抖动），尺寸按新比例给（6–7 m）"""
    import numpy as np
    from bgkit import old_lib
    im = old_lib().sakura(cv.img(), cx, by, h=h, w=w, seed=seed)
    cv.a = np.array(im)
