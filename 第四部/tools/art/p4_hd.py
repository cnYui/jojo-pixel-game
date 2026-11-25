# 天堂之门（Heaven's Door）——按官方形象画：银白色礼服 + 金色滚边和袖口、金色格栅的高礼帽、绿眼睛、
#   橙色领结、橙色鞋。人朝右（3/4 侧），全尺寸格 48×48、脚点 (20, 45)，之后和别的人物一样用 shrink 缩成 5/8。
#   画法：每个部件用字符格子 / 胶囊笔画逐像素画，不靠抗锯齿。调色板键：
#     W w s d D = 银白 → 银灰 → 暗银（高光到阴影）  y g G = 金（亮 / 中 / 暗）
#     e E = 绿眼（亮 / 暗）  k = 近黑  o O = 橙（亮 / 暗）
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as L  # noqa: E402

PAL = {
    'W': (252, 253, 255), 'w': (228, 234, 242), 's': (190, 198, 212), 'd': (140, 148, 168), 'D': (94, 100, 122),
    'y': (255, 234, 134), 'g': (238, 192, 62), 'G': (182, 130, 34),
    'e': (72, 222, 106), 'E': (22, 118, 56), 'k': (36, 26, 42),
    'o': (244, 148, 44), 'O': (178, 94, 28),
}
OUTLINE = (26, 16, 32, 255)
CW, CH = 48, 48
PIVOT = (20, 45)


class Grid:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = [['.'] * w for _ in range(h)]

    def put(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y][x] = ch

    def hline(self, x0, x1, y, ch):
        for x in range(x0, x1 + 1):
            self.put(x, y, ch)

    def vline(self, x, y0, y1, ch):
        for y in range(y0, y1 + 1):
            self.put(x, y, ch)

    def rect(self, x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            self.hline(x0, x1, y, ch)

    def capsule(self, p0, p1, r, shade=True, light='W', mid='s', dark='d', side=-1):
        """粗细 2r 的圆头线段。shade：沿线一侧亮、另一侧暗（光从右上来）。"""
        (x0, y0), (x1, y1) = p0, p1
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy) or 1.0
        ux, uy = dx / ln, dy / ln
        for y in range(int(min(y0, y1) - r - 1), int(max(y0, y1) + r + 2)):
            for x in range(int(min(x0, x1) - r - 1), int(max(x0, x1) + r + 2)):
                t = ((x - x0) * ux + (y - y0) * uy)
                t = max(0.0, min(ln, t))
                px, py = x0 + ux * t, y0 + uy * t
                dist = math.hypot(x - px, y - py)
                if dist <= r:
                    n = ux * (y - y0) - uy * (x - x0)          # <0：线的“上 / 右”侧
                    if not shade:
                        self.put(x, y, mid)
                    elif n < -r * 0.25:
                        self.put(x, y, light)
                    elif n > r * 0.55:
                        self.put(x, y, dark)
                    else:
                        self.put(x, y, mid)

    def image(self):
        im = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        px = im.load()
        for y in range(self.h):
            for x in range(self.w):
                ch = self.a[y][x]
                if ch != '.':
                    px[x, y] = (*PAL[ch], 255)
        return im


# ============================================================ 部件
def head_grid(eyes='open', mouth='closed'):
    """帽子 + 头（24×20）：帽身是金色格栅（3×2 个窗），金色帽带，银色宽檐；脸银白，绿眼，眼下两道金线。"""
    g = Grid(24, 20)
    # 帽顶口沿（后沿暗、前沿亮）
    g.hline(6, 18, 0, 'G')
    g.hline(5, 19, 1, 'g')
    g.hline(7, 17, 1, 'y')
    # 格栅帽身（官方图里帽身是镂空的金色细条框 + 大块银白的窗）：横条 y=2 / 5，竖条 x=6 / 10 / 14 / 18，
    #   窗 3 格宽，窗里银白（每扇窗上沿被横条压出一行暗银的阴影，最左一扇整体更暗）
    for y in range(2, 8):
        g.hline(7, 17, y, 'W')
    for y in (3, 6):
        g.hline(7, 17, y, 's')
    for y in range(3, 8):
        g.hline(7, 9, y, 'w' if y in (4, 7) else 'd')
    g.hline(6, 18, 2, 'g')
    g.hline(6, 18, 5, 'g')
    for x, ch in ((6, 'G'), (10, 'g'), (14, 'g'), (18, 'y')):
        g.vline(x, 2, 7, ch)
    g.hline(7, 17, 2, 'y')
    g.hline(7, 17, 5, 'y')
    g.put(6, 2, 'G')
    # 帽带
    g.hline(5, 19, 8, 'g')
    g.hline(8, 17, 8, 'y')
    g.put(5, 8, 'G')
    g.put(19, 8, 'G')
    # 宽檐：上面一行亮、侧面一行、下面阴影一行
    g.hline(2, 21, 9, 'W')
    g.put(2, 9, 's')
    g.put(21, 9, 's')
    g.hline(1, 22, 10, 'w')
    g.hline(1, 3, 10, 'd')
    g.put(22, 10, 's')
    g.hline(2, 21, 11, 'd')
    g.hline(2, 5, 11, 'G')      # 檐的外沿有一圈金边（官方图里檐是银白 + 细金边）
    g.hline(18, 21, 11, 'G')
    g.put(1, 10, 'G')
    g.put(22, 10, 'G')
    # 脸：檐下阴影 → 脸 → 下巴；后脑偏暗、前面亮
    g.hline(8, 18, 12, 'd')
    for y in range(13, 18):
        g.hline(7, 18, y, 'W')
        g.hline(7, 9, y, 's')
        g.put(7, y, 'd')
        g.put(18, y, 'w')
    g.hline(8, 18, 18, 'W')
    g.hline(8, 10, 18, 's')
    g.hline(9, 17, 19, 'w')
    g.hline(9, 10, 19, 's')
    g.put(18, 18, 'w')
    # 脸上的金线（官方图里从太阳穴沿着脸颊描到下巴）：远侧 x=10、近侧 x=17，各一段
    g.vline(10, 13, 16, 'g')
    g.vline(17, 13, 15, 'g')
    # 鼻子：往前凸一格
    g.put(19, 16, 'w')
    g.put(19, 17, 's')
    # 眼睛（远侧 x=12–13，近侧 x=16–17）
    if eyes == 'open':
        for ex in (12, 16):
            g.hline(ex, ex + 1, 14, 'E')
            g.hline(ex, ex + 1, 15, 'e')
        g.put(13, 15, 'W')
        g.put(17, 15, 'W')
        # 眼下的金线
        g.hline(12, 13, 16, 'g')
        g.hline(16, 17, 16, 'g')
    else:       # 紧闭：两道暗线
        for ex in (12, 16):
            g.hline(ex, ex + 1, 15, 'k')
            g.put(ex, 14, 'k')
        g.hline(12, 13, 16, 'g')
        g.hline(16, 17, 16, 'g')
    # 嘴
    if mouth == 'closed':
        g.hline(14, 16, 18, 'G')
    else:
        g.hline(14, 16, 18, 'k')
        g.hline(14, 16, 19, 'k')
    return g


def torso_grid():
    """礼服（16×14）：银白色长上衣，正中一条金色拉链线，下摆金边外翻；领口橙色领结。"""
    g = Grid(16, 14)
    # 肩 → 腰 → 下摆（越往下越宽）
    for y in range(0, 14):
        if y == 0:
            x0, x1 = 3, 12
        elif y < 9:
            x0, x1 = 2, 13
        elif y < 11:
            x0, x1 = 2, 14
        else:
            x0, x1 = 1, 14
        g.hline(x0, x1, y, 'W')
        g.hline(x0, x0 + 1, y, 'd')
        g.put(x0 + 2, y, 's')
        g.put(x1, y, 'w')
    # 拉链线 + 两粒金扣（在 x=9）
    g.vline(9, 2, 12, 'g')
    for y in (4, 7, 10):
        g.put(9, y, 'y')
        g.put(8, y, 'g')
    # 领口金线
    g.hline(4, 12, 1, 'g')
    g.put(3, 0, 'g')
    g.put(12, 0, 'g')
    # 下摆金边
    g.hline(1, 14, 13, 'g')
    g.hline(1, 3, 13, 'G')
    # 橙色领结：两翼 + 中间结
    for x in (5, 6, 11, 12):
        g.put(x, 0, 'o')
    g.hline(5, 7, 1, 'o')
    g.hline(10, 12, 1, 'o')
    g.hline(8, 9, 0, 'O')
    g.hline(8, 9, 1, 'O')
    g.put(7, 0, 'O')
    g.put(10, 0, 'O')
    return g


# ============================================================ 拼一帧
def paint(base, part, x, y):
    """把部件格子盖到 base 格子上（'.' 不盖）"""
    for yy in range(part.h):
        for xx in range(part.w):
            ch = part.a[yy][xx]
            if ch != '.':
                base.put(x + xx, y + yy, ch)


def arm(g, shoulder, ang, sleeve=6, cuff=2, hand=2, far=False, r=1.55, bend=None):
    """一条胳膊：银袖 + 金袖口 + 银手。ang 度数（0 向右、90 向下、-90 向上）；bend = (肘角, 前臂角)。"""
    sx, sy = shoulder
    if far:
        light, mid, dark = 's', 'd', 'D'
    else:
        light, mid, dark = 'w', 's', 'd'      # 比礼服（W）暗一档，胳膊挂在身前才分得出来
    cur = (sx, sy)

    def go(a, n):
        nonlocal cur
        nx, ny = cur[0] + math.cos(math.radians(a)) * n, cur[1] + math.sin(math.radians(a)) * n
        return (nx, ny)

    if bend:
        elbow = go(bend[0], sleeve * 0.55)
        g.capsule(cur, elbow, r, True, light, mid, dark)
        cur = elbow
        a2 = bend[1]
        wrist = go(a2, sleeve * 0.45)
        g.capsule(cur, wrist, r, True, light, mid, dark)
        cur = wrist
        ang = a2
    else:
        wrist = go(ang, sleeve)
        g.capsule(cur, wrist, r, True, light, mid, dark)
        cur = wrist
    c1 = go(ang, cuff)
    g.capsule(cur, c1, r + 0.1, False, mid='g')
    g.capsule((cur[0] + math.cos(math.radians(ang)) * 0.2, cur[1]), (c1[0], c1[1]), r + 0.1, False, mid='g')
    cur = c1
    h1 = go(ang, hand)
    g.capsule(cur, h1, r + 0.2, True, 'W', 'w', 's')
    return h1


def shoe(g, fx, fy=43):
    """橙色鞋：脚尖朝右，两行"""
    g.hline(fx - 1, fx + 4, fy, 'o')
    g.hline(fx - 1, fx + 4, fy + 1, 'O')
    g.put(fx + 4, fy, 'O')


def leg(g, hip, foot, back=False):
    light, mid, dark = ('s', 'd', 'D') if back else ('W', 's', 'd')
    g.capsule(hip, (foot[0], 42), 1.85, True, light, mid, dark)
    shoe(g, foot[0] - (0 if foot[0] >= hip[0] else 0))


PAGE_ROWS = ['wwwwwww', 'WddddWw', 'WWWWWWw', 'WddddWw', 'WWWWWWw', 'WdddWWw', 'WWWWWWw']


def page(g, x, y, flip=0):
    """一页纸（天堂之门把人翻成书页）：白纸 + 几行字"""
    for yy, row in enumerate(PAGE_ROWS):
        for xx, ch in enumerate(row):
            g.put(x + xx, y + yy + flip, ch)


POSES = {
    #        头身前倾  头上下  近臂                        远臂                 腿           眼       嘴
    'idle':   dict(lean=0, dy=0, near=(9, 3, 86, 6), far=(3, 3, 104, 6), legs='stand', eyes='open', mouth='closed'),
    'wind':   dict(lean=-2, dy=0, near=(9, 3, 150, 6), far=(3, 3, 100, 6), legs='stand', eyes='open', mouth='closed'),
    'punch':  dict(lean=2, dy=0, near=(9, 3, 8, 9), far=(3, 3, 120, 6), legs='lunge', eyes='open', mouth='open'),
    'punch2': dict(lean=3, dy=0, near=(9, 3, 0, 13), far=(3, 3, 130, 6), legs='lunge', eyes='open', mouth='open'),
    'upper':  dict(lean=1, dy=1, near=(9, 3, -58, 11), far=(3, 3, 110, 6), legs='lunge', eyes='open', mouth='open'),
    'rush':   dict(lean=3, dy=1, near=(9, 3, 150, 7), far=(3, 3, 25, 8), legs='stride', eyes='open', mouth='open'),
    'rush2':  dict(lean=3, dy=0, near=(9, 3, 25, 8), far=(3, 3, 150, 7), legs='stride2', eyes='open', mouth='open'),
    'block':  dict(lean=-1, dy=1, near=(9, 3, None, 7), far=(3, 3, 100, 6), legs='stand', eyes='open', mouth='closed', block=True),
    'hurt':   dict(lean=-3, dy=1, near=(9, 3, 135, 7), far=(3, 3, 20, 7), legs='wide', eyes='shut', mouth='open'),
    'write':  dict(lean=1, dy=0, near=(9, 3, -6, 11), far=(3, 3, 105, 6), legs='stand', eyes='open', mouth='closed', page=True),
}


def frame(pose='idle', t=0.0):
    p = POSES[pose]
    bob = int(round(math.sin(t * 2 * math.pi))) if pose == 'idle' else 0
    lean = p['lean']
    ty = 24 + p['dy'] + bob
    tx = 12 + lean
    hx = tx - 5
    hy = ty - 20
    g = Grid(CW, CH)
    # 远侧胳膊（在身子后面）
    sx, sy, ang, ln = p['far']
    arm(g, (tx + sx, ty + sy), ang, ln, far=True)
    # 腿（髋在下摆下沿；脚点在地上）
    hipy = 24 + p['dy'] + 13
    kind = p['legs']
    back_hip, front_hip = (12 + lean + 5, hipy), (12 + lean + 10, hipy)
    feet = {'stand': ((16, 20), (24, 26)), 'lunge': ((10, 14), (26, 32)), 'stride': ((7, 12), (24, 30)),
            'stride2': ((16, 20), (14, 22)), 'wide': ((10, 14), (26, 30))}[kind]
    leg(g, back_hip, (feet[0][0] + 1, 42), back=True)
    leg(g, front_hip, (feet[1][0] + 1, 42))
    # 礼服 + 头
    paint(g, torso_grid(), tx, ty)
    paint(g, head_grid(p['eyes'], p['mouth']), hx, hy)
    # 近侧胳膊
    sx, sy, ang, ln = p['near']
    if p.get('block'):
        arm(g, (tx + sx, ty + sy), 0, ln, bend=(40, -80), r=1.7)
    else:
        end = arm(g, (tx + sx, ty + sy), ang, ln)
        if p.get('page'):
            f = 0 if t < 0.5 else -1
            page(g, int(end[0]) + 1, int(end[1]) - 5, f)
    im = g.image()
    if pose in ('rush', 'rush2'):                  # 冲刺：身后三道速度线
        px = im.load()
        for k in range(3):
            for x in range(1 + k * 2, 9 + k * 2):
                px[x, 16 + k * 6] = (*PAL['w'], 255)
    return L.outline(im, OUTLINE)


def portrait():
    """说话头像 32×32：帽子 + 脸 + 领结"""
    g = Grid(32, 32)
    paint(g, torso_grid(), 9, 21)          # 礼服的中线对着脸的中线（和整身图一样，头比身子左 5 格）
    paint(g, head_grid('open', 'closed'), 4, 1)
    # 下面超出的下摆裁掉（只留肩）
    im = g.image().crop((0, 0, 32, 32))
    return L.outline(im, OUTLINE)


if __name__ == '__main__':
    # 预览：python p4_hd.py <输出目录>  → 全部姿势 6 倍放大排一张
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    names = ['idle', 'wind', 'punch', 'punch2', 'upper', 'rush', 'rush2', 'block', 'hurt', 'write']
    sheet = Image.new('RGBA', (CW * 5, CH * 2), (0, 0, 0, 0))
    for i, n in enumerate(names):
        sheet.alpha_composite(frame(n, 0.0), ((i % 5) * CW, (i // 5) * CH))
    bg = Image.new('RGBA', sheet.size, (104, 136, 172, 255))
    bg.alpha_composite(sheet)
    bg.resize((bg.width * 4, bg.height * 4), Image.NEAREST).save(os.path.join(out, 'hd_poses.png'))
    pb = Image.new('RGBA', (32, 32), (104, 136, 172, 255))
    pb.alpha_composite(portrait())
    pb.resize((256, 256), Image.NEAREST).save(os.path.join(out, 'hd_portrait.png'))
    print('ok')
