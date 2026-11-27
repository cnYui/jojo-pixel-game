# 第四部重画：各章人物定义共用的小零件（基础调色板、常见上衣的字符稿、统一的 build / 检查入口）。
from px import Cv, OUTLINE, shade, rows
from rig import Body, Sheet, draw, poses, variants, grid_part, chain, X, Y, CW, CH, OX, OY
from poses import stand_poses

SKIN, SKIN_D = '#f6c49a', '#d8946c'
BASE = {'s': SKIN, 'd': SKIN_D, 'w': '#ffffff', 'm': '#a04e44', 'b': '#1a1438'}


def P_(**kw):
    p = dict(BASE)
    p.update(kw)
    p.setdefault('S', p['s'])      # 字符稿里的大写 S = 皮肤
    return p


def H(txt):
    """头的字符稿里用大写 S 标“这格本来是皮肤、留着对齐用”，这里换回 s"""
    return txt.replace('S', 's')


# 立领校服（8 宽 × 9 高）：q 背侧暗边、j 衣身、g 金扣
GAKURAN8x9 = '''
qjjjjjjj
qjjjjgjj
qjjjjjjj
qjjjjgjj
qjjjjjjj
qjjjjgjj
qjjjjjjj
qjjjjgjj
qjjjjjjj
'''
GAKURAN8x8 = '\n'.join(GAKURAN8x9.strip().split('\n')[:8])
GAKURAN7x7 = '''
qjjjjjj
qjjjgjj
qjjjjjj
qjjjgjj
qjjjjjj
qjjjgjj
qjjjjjj
'''


def raw_frame(txt, pal, dx=0, dy=0, outline=True):
    """整帧手画的小东西（动物、小替身）：字符稿底边落在脚底线、左右居中，再按 dx / dy 挪"""
    g = rows(txt)
    cv = Cv(CW, CH)
    cv.grid(g, OX - len(g[0]) // 2 + dx, OY - len(g) + 1 - dy, pal)
    return cv.outline(OUTLINE) if outline else cv


def make_build(CAST, kind='char'):
    """各章文件共用的 build(cid)：CAST[cid] = (名字, 函数)；函数返回 Sheet 或 (Body, 姿势表, 动作清单)"""
    def build(cid):
        name, fn = CAST[cid]
        r = fn()
        if isinstance(r, Sheet):
            r.cid, r.name = cid, name
            return r
        B, P, names = r
        sh = Sheet(cid, name, kind='stand' if B.kind == 'stand' else kind)
        sh.add_pose(B, P, names)
        sh.body = B
        return sh
    return build


def main(CAST, build, argv):
    """python cast_xxx.py 输出目录 [cid…]：每人一张全帧检查图 + 一张身高对比图"""
    from view import compact, lineup
    out = argv[1]
    ids = argv[2:] or list(CAST)
    stand = []
    for cid in ids:
        sh = build(cid)
        compact(sh, k=5, per_row=10, crop=(-22, -44, 30, 4), title=cid + ' ' + sh.name).save('%s/z_%s.png' % (out, cid))
        stand.append(sh.rows[0][1][0])
    lineup(stand, ids, k=5, ref_h=[(30, '180cm'), (34, '门 204'), (15, '窗台 90')], crop=(-18, -44, 22, 2)).save(out + '/lineup.png')
