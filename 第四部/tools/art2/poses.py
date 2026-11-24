# 第四部重画：表情变体 + 所有人共用的姿势表。
#   姿势只写“手脚放哪、身体怎么歪”（骨架坐标：+x 朝前、+y 朝上，单位 px），具体的人按自己的躯干长、腿长套进去。
#   手臂：aN / aF = (手相对肩的 dx, dy) 或 ((肘 dx, dy), (手 dx, dy))；N = 靠镜头的一侧，F = 远侧（朝右站时在前面）。
#   腿：lN / lF = (脚相对默认落点的 dx, 抬高) 或 ((膝相对胯 dx, dy), (脚 dx, 抬高))。
#   dy = 上身起伏，drop = 胯下沉，lean = 肩相对胯前倾（负数后仰），bx = 整体前后移，head = 表情变体，lie = 放倒。
from px import rows


def variants(head, pal):
    """从正常的头自动派生表情：t = 张嘴说话，h = 闭眼吃痛，s = 瞪眼吃惊，r = 怒吼。
    认字符：e = 瞳孔、w = 眼白、m = 嘴、s / d = 皮肤、b = 眉 / 深色线。个别人不合适就在定义里自己写那一张。"""
    hd = [list(r) for r in (rows(head) if isinstance(head, str) else head)]
    pal.setdefault('M', '#7a2030')
    pal.setdefault('b', '#1a1438')
    H, W = len(hd), len(hd[0])
    eyes = [(x, y) for y in range(H) for x in range(W) if hd[y][x] in 'ew']
    mouth = [(x, y) for y in range(H) for x in range(W) if hd[y][x] == 'm']

    def clone():
        return [r[:] for r in hd]

    def open_mouth(g, tall):
        for x, y in mouth:
            g[y][x] = 'M'
        if not mouth:
            return
        if tall:
            for x, y in mouth:
                if y + 1 < H and g[y + 1][x] in 'sd':
                    g[y + 1][x] = 'M'
        else:
            x, y = mouth[0]
            if y + 1 < H and g[y + 1][x] in 'sd':
                g[y + 1][x] = 'M'

    def txt(g):
        return [''.join(r) for r in g]

    out = {'n': txt(hd)}
    g = clone()
    open_mouth(g, False)
    out['t'] = txt(g)
    g = clone()
    if eyes:
        ybot = max(y for _, y in eyes)
        for x, y in eyes:
            g[y][x] = 'b' if y == ybot else 's'
    open_mouth(g, False)
    out['h'] = txt(g)
    g = clone()
    if eyes:
        ytop = min(y for _, y in eyes)
        for x, y in eyes:
            if y == ytop and g[y][x] == 'e':
                g[y][x] = 'w'
    open_mouth(g, True)
    out['s'] = txt(g)
    g = clone()
    open_mouth(g, True)
    out['r'] = txt(g)
    return out


def poses(B):
    """返回 {动作名: (帧列表, fps, kind)}。各人可以在自己的定义里覆盖 / 加动作。"""
    A = B.arm_len
    L = B.LH - B.shoe_h                   # 胯到脚踝
    kn = max(2, (L + 1) // 2)             # 大腿长
    st = 3 if B.LH >= 7 else 2            # 步幅
    P = {}
    P['idle'] = ([dict(), dict(dy=-1, aN=(0, -A + 1), aF=(0, -A + 1))], 2, 'loop')
    P['walk'] = ([dict(lN=(st, 0), lF=(-st, 0), aN=(-2, -A + 1), aF=(2, -A + 1)),
                  dict(dy=1, lF=((1, -kn + 1), (-1, 2)), aN=(-1, -A), aF=(1, -A)),
                  dict(lN=(-st, 0), lF=(st, 0), aN=(2, -A + 1), aF=(-2, -A + 1)),
                  dict(dy=1, lN=((1, -kn + 1), (-1, 2)), aN=(1, -A), aF=(-1, -A))], 8, 'loop')
    P['run'] = ([dict(lean=1, lN=((2, -kn + 1), (st + 1, 1)), lF=((-1, -kn), (-st - 1, 2)), aN=((-2, -2), (-4, -1)), aF=((2, -2), (4, -1))),
                 dict(lean=1, dy=1, lN=(0, 0), lF=((2, -kn + 1), (0, 3)), aN=((-1, -3), (1, -3)), aF=((1, -3), (3, -3))),
                 dict(lean=1, lN=((-1, -kn), (-st - 1, 2)), lF=((2, -kn + 1), (st + 1, 1)), aN=((2, -2), (4, -1)), aF=((-2, -2), (-4, -1))),
                 dict(lean=1, dy=1, lF=(0, 0), lN=((2, -kn + 1), (0, 3)), aN=((1, -3), (3, -3)), aF=((-1, -3), (1, -3)))], 10, 'loop')
    P['point'] = ([dict(aF=(A + 1, 0), aN=((-1, -2), (1, -A + 2))), dict(aF=(A + 1, 1), aN=((-1, -2), (1, -A + 2)), dy=-1)], 4, 'loop')
    P['pose'] = ([dict(aN=((-2, -2), (-1, -A + 2)), aF=((2, 1), (0, 4))), dict(aN=((-2, -2), (-1, -A + 2)), aF=((2, 2), (0, 5)), dy=-1)], 3, 'oneshot')
    P['shock'] = ([dict(head='s', lean=-1, aN=((-2, -1), (-3, 2)), aF=((2, -1), (3, 2)), lN=(-1, 0), lF=(1, 0))], 1, 'static')
    P['hurt'] = ([dict(head='h', lean=-2, bx=-1, aN=((-1, -2), (2, -3)), aF=((2, -1), (4, 1)), lN=(-1, 0), lF=((2, -kn + 1), (2, 2)))], 1, 'static')
    P['dodge'] = ([dict(lean=-2, bx=-2, drop=1, aN=((-2, -2), (-3, -1)), aF=((1, -2), (3, -1)), lN=(-2, 0), lF=(2, 0))], 1, 'static')
    P['guard'] = ([dict(drop=1, aF_front=True, aF=((2, -2), (1, 2)), aN=((1, -3), (3, 1)), lN=(-1, 0), lF=(2, 0))], 1, 'static')
    P['kick'] = ([dict(lean=-1, lF=((3, 0), (2, L - 2)), aN=((-2, -2), (-3, -1)), aF=((1, -3), (2, -1))),
                  dict(lean=-2, bx=-1, head='r', lF=(L + 2, B.LH - 1 - B.shoe_h), aN=((-2, -2), (-4, 0)), aF=((1, -3), (2, -1)))], 8, 'oneshot')
    # sit = 坐在地上（屈膝、手搭膝盖）；sit_chair = 坐椅子（椅面按 Q 版小腿长 5 px，见比例标准）
    gd = B.LH - 1 - B.shoe_h
    P['sit'] = ([dict(drop=gd, lean=-1, lN=(L + 1, 0), lF=(L + 2, 0), aN=((-1, -2), (-2, -A + 2)), aF=((1, -2), (3, -A + 2))),
                 dict(drop=gd, lean=-1, dy=-1, lN=(L + 1, 0), lF=(L + 2, 0), aN=((-1, -2), (-2, -A + 3)), aF=((1, -2), (3, -A + 3)))], 1.5, 'loop')
    cd = max(0, B.LH - 7)
    P['sit_chair'] = ([dict(drop=cd, lN=((4, 0), (4, 0)), lF=((4, 0), (5, 0)), aN=((0, -3), (3, -A + 3)), aF=((0, -3), (3, -A + 3))),
                       dict(drop=cd, dy=-1, lN=((4, 1), (4, 0)), lF=((4, 1), (5, 0)), aN=((0, -3), (3, -A + 4)), aF=((0, -3), (3, -A + 4)))], 1.5, 'loop')
    P['down'] = ([dict(head='h', lie='back', aN=(0, -A), aF=(0, -A))], 1, 'static')
    P['talk'] = ([dict(), dict(head='t', aF=((1, -3), (3, -1)))], 4, 'loop')
    P['cmd'] = ([dict(aF=(A + 1, 1), aN=((-1, -2), (1, -A + 2))), dict(aF=(A + 1, 2), head='t', aN=((-1, -2), (1, -A + 2)))], 6, 'loop')
    P['wave'] = ([dict(aF=((1, 2), (2, A)), head='t'), dict(aF=((2, 2), (4, A - 1)))], 4, 'loop')
    P['cheer'] = ([dict(aF=((1, 2), (2, A)), aN=((-1, 2), (-2, A)), head='t'),
                   dict(dy=1, aF=((2, 2), (3, A)), aN=((-2, 2), (-3, A)), lN=(0, 1), lF=(0, 1))], 4, 'loop')
    P['cry'] = ([dict(head='h', aF_front=True, aF=((2, -1), (0, 3)), aN=((0, -2), (3, 2)), dy=-1),
                 dict(head='h', aF_front=True, aF=((2, -1), (0, 2)), aN=((0, -2), (3, 1)), dy=-2)], 3, 'loop')
    P['bow'] = ([dict(lean=3, dy=-1, hx=2, hy=-3, head='h', aN=(1, -A + 1), aF=(1, -A + 1))], 1, 'static')
    P['laugh'] = ([dict(head='t', lean=-1, aN=((-2, -2), (-1, -A + 2))), dict(head='r', lean=-1, dy=1, aN=((-2, -2), (-1, -A + 2)))], 4, 'loop')
    P['throw'] = ([dict(lean=-1, aF=((-1, 1), (-3, 3)), aN=((-1, -2), (1, -A + 2))),
                   dict(lean=1, aF=(A + 1, 1), aN=((-2, -2), (-3, -1)), lF=(1, 0))], 6, 'oneshot')
    P['punch'] = ([dict(lean=-1, aF=((-1, -1), (1, 0)), aN=((-1, -2), (1, -A + 2)), fistF=3),
                   dict(lean=1, head='r', aF=(A + 2, 0), fistF=3, aN=((-2, -2), (-3, -1)), lF=(1, 0))], 8, 'oneshot')
    P['attack'] = P['punch']
    P['kneel'] = ([dict(drop=L - 2, lN=((1, -kn), (-kn + 1, 0)), lF=((kn, 0), (kn, 0)), head='h', aN=(1, -A + 1), aF=(2, -A + 1), lean=1)], 1, 'static')
    P['crawl'] = ([dict(lie='front', aN=(0, -A), aF=((1, 1), (1, A - 2)), head='h'),
                   dict(lie='front', aN=((1, 1), (1, A - 2)), aF=(0, -A), head='h')], 4, 'loop')
    P['fall'] = ([dict(head='s', lean=-2, bx=-1, dy=2, aN=((-2, 1), (-3, 3)), aF=((2, 1), (3, 3)),
                       lN=((1, -kn + 1), (2, 3)), lF=((2, -kn + 1), (4, 3)))], 1, 'static')
    P['jump'] = ([dict(dy=3, aN=((-2, 1), (-3, 3)), aF=((2, 1), (3, 3)), lN=((0, -kn + 1), (-1, 3)), lF=((1, -kn + 1), (1, 3)))], 1, 'static')
    return P


def stand_poses(B):
    """人形替身共用的动作（浮在半空：膝盖微屈、脚尖朝后）。帧数 / fps 和旧图集一致（招式表按时间卡帧）。"""
    A = B.arm_len
    L = B.LH - B.shoe_h
    kn = max(3, (L + 1) // 2)
    fl = dict(lN=((1, -kn), (-1, 1)), lF=((2, -kn), (1, 2)))            # 悬浮时的腿
    rest = dict(aN=((-1, -4), (2, -6)), aF=((2, -3), (5, -4)), fistN=4, fistF=4)

    def F(**kw):
        d = dict(fl)
        d.update(rest)
        d.update(kw)
        return d

    P = {}
    P['idle'] = ([F(), F(dy=1), F(dy=2, aF=((2, -3), (5, -3))), F(dy=1)], 6, 'loop')
    P['punch'] = ([F(lean=-1, aF=((-2, -1), (1, 1)), aN=((0, -3), (3, -3))),
                   F(lean=2, bx=1, head='r', aF=(A + 5, 0), fistF=5, aN=((-2, -3), (-3, -1)), lF=((3, -kn), (4, 1))),
                   F(lean=1, aF=((4, -1), (8, 0)), aN=((-1, -3), (0, -2)))], 12, 'oneshot')
    P['rush'] = ([F(lean=2, head='r', aF=(A + 6, 1), fistF=5, aN=((3, -1), (A + 1, -3)), blur=0, lF=((3, -kn), (4, 1))),
                  F(lean=2, head='r', aF=((3, -2), (A + 2, -3)), fistF=5, aN=((4, 0), (A + 5, 1)), blur=1, lF=((3, -kn), (4, 1)))], 16, 'loop')
    P['block'] = ([F(drop=1, aF_front=True, aF=((3, -2), (1, 3)), aN=((2, -4), (5, 0)))], 1, 'static')
    P['pose'] = ([F(aN=((-3, 0), (-2, 5)), aF=((3, 0), (4, 5))), F(dy=1, aN=((-3, 1), (-2, 6)), aF=((3, 1), (4, 6)), head='r')], 4, 'loop')
    P['hurt'] = ([F(head='h', lean=-3, bx=-1, aN=((-2, -2), (1, -4)), aF=((2, 0), (5, 2)), lF=((3, -kn + 1), (3, 3)))], 1, 'static')
    P['finger'] = ([F(lean=1, aF=(A + 4, 2), fistF=3, item='finger', aN=((-2, -3), (-3, -1)))], 1, 'static')
    P['fist'] = ([F(lean=2, bx=1, head='r', aF=(A + 5, 0), fistF=6, aN=((-2, -3), (-3, -1)), lF=((3, -kn), (4, 1)))], 1, 'static')
    P['reach'] = ([F(lean=1, aF=(A + 4, -1), fistF=3, item='palm', aN=((-1, -3), (1, -5)))], 1, 'static')
    P['upper'] = ([F(drop=2, lean=1, aF=((1, -5), (3, -7)), aN=((-1, -3), (2, -3))),
                   F(lean=1, head='r', aF=((4, 0), (5, 6)), fistF=5, aN=((-2, -3), (-3, -1))),
                   F(dy=2, lean=-1, head='r', aF=((3, 3), (4, A + 1)), fistF=5, aN=((-2, -3), (-3, -1)))], 12, 'oneshot')
    P['kick'] = ([F(lean=-1, lF=((4, 0), (3, L - 3))), F(lean=-2, bx=-1, head='r', lF=(L + 3, B.LH - 1 - B.shoe_h))], 8, 'oneshot')
    P['erase'] = ([F(lean=-1, aF=((2, 3), (3, A)), fistF=4, item='palm'),
                   F(lean=1, head='r', aF=((5, 2), (A + 1, 3)), fistF=4, item='swipe'),
                   F(lean=2, aF=((4, -4), (7, -A + 1)), fistF=4, item='swipe2')], 12, 'oneshot')
    P['pull'] = ([F(lean=1, aF=(A + 4, 0), fistF=4, item='palm'), F(lean=-1, aF=((2, -2), (3, 1)), fistF=4)], 10, 'oneshot')
    P['crack'] = ([F(aF=((3, -1), (6, 3)), fistF=4), F(aF=((3, -1), (6, 2)), fistF=4, item='click', head='r')], 6, 'oneshot')
    P['cast'] = ([F(aF=((3, 1), (6, 5)), fistF=3, item='palm'), F(aF=(A + 3, 2), fistF=3, item='palm', head='r')], 8, 'oneshot')
    P['write'] = ([F(lean=1, aF=(A + 2, 1), fistF=3), F(lean=1, aF=(A + 2, -1), fistF=3)], 8, 'loop')
    return P
