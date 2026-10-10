"""art_joseph -- 二乔（乔瑟夫）：脸对齐对话框头像、手臂分段、隐者之紫普通攻击帧（用户 2026-10-09 晚）。

用户反馈：①“二乔手臂奇怪”——指人 / 挥鞭的手臂没有肩、上臂、肘、前臂、拳的分段，手套和前臂连成一条细线；
普通攻击一直定在一张 point（指人）上；②“为什么他左下角的脸和游戏里出现的脸不一样呢？五官是不是也拼错了？”——
游戏里的眼睛只有一行（白 / 蓝 / 黑，像眯眼），对话框头像是“黑眼线 + 两行白蓝眼睛”。

做法：保持原工程的卡通大头比例和轮廓，直接用 sprites_jojo 的部件（JO_HAT / JO_TORSO / 靴子 / GLOVE / FIST / 调色板）
和 class G 画法（同 art_npc.h_frame2 复制 h_frame 的思路，这里复制 jo_frame → jo_frame2），只改：
  * 脸 JO_FACE2：照头像的结构缩到精灵大小——帽檐阴影那一行改成黑眼线，下面两行是白 + 蓝眼睛（原来一行灰眉 + 一行眯眼）；
    胡子、嘴、鼻子不动。指人用的坏笑脸 JO_FACE2_SMUG 同样改（左眼睁开、右眼眨眼、咧嘴）。
    惊吓 / 受击 / 躺倒三张脸本来就和头像对应（白眼 / 闭眼），不改。
  * 手臂 jo_arm2：上臂袖子 → 卷起的袖口（深一像素）→ 露出的上臂 → 肘 → 前臂 → 手套 / 拳。
    攻击时伸出去的是远侧（左手、棕手套）：躯干盖上去时描一道分隔线（肩缝），袖子用暗一档的颜色、前臂 3 像素宽，
    手套 / 拳比手腕大一圈，读得出“肩—上臂—肘—前臂—拳”。
新动作（新名字，D12；都在 import 时注册）：
  joseph.vine_atk   4 帧 15 fps 一次：蓄力（手套收到肩前）→ 甩出 → 命中（手臂伸直、张开手套）→ 收势（屈肘握拳拽藤）
                    —— 逻辑 cmd（J1 / J2 / 收尾 / 连打）；藤蔓本身由 engine/stand.js 从肩前 (pivot+6, −30) 长出
  joseph.vine_heavy 4 帧 10 fps 一次：举臂过肩 → 猛抽（手臂上缠藤蔓）→ 定住 → 收势 —— 逻辑 cmd2（J3）
  joseph.vine_hold  2 帧 6 fps 循环：手臂伸直握拳拽住藤蔓、轻微抖动 —— 逻辑 cmd_hold / special（波纹疾走）
  joseph.whip / joseph.guard：重画（原来由 art_later_existing 用通用拉线手臂生成，躯干右半边被挖掉）
apply()（bake_art 在 D12 原名审计之后调，同 art_holly_fix）：用新脸重画原图集的 idle / walk / run / camera / point
（point 顺带修手臂分段），再用新的 idle 重算 float（落水半头，水线同 art_later_existing）和 dodge。
所有帧仍是原 36×52 身体 + 向右 / 向上加宽的画布，锚点 = 两脚中点（18, 52 + top），图集 cell 82×57、pivot [30, 54] 不变。
"""
import sys
sys.dont_write_bytecode = True

import art_common as AC                       # noqa: F401  （设好 sys.path）
from engine import sprite                     # noqa: E402
from engine.sprite import g_lines             # noqa: E402
from assets import sprites_jojo as SJ         # noqa: E402

NEW = []
ONESHOT = {'vine_atk', 'vine_heavy', 'whip'}
STATIC_STATES = set()
CHAR_INFO = {}
ACTION_ZH = {'vine_atk': '隐者之紫·甩藤', 'vine_heavy': '隐者之紫·猛抽', 'vine_hold': '隐者之紫·拽藤'}

G = SJ.G
edits = SJ.edits

# ============================================================================ 脸（照对话框头像）
# 原 JO_FACE（24 宽，盖在 (6, 12)；行 = y12..y20）：r0 帽檐阴影、r1 灰眉、r2 一行眼睛 WUk、r3 鼻、r4 八字胡、r5 嘴、r6–8 胡子。
# 头像 JO_PORT：灰眉 → 黑眼线 kkkk → 两行眼睛 WWwUk / WWUUk。精灵只有 9 行脸：r0 = 黑眼线（帽檐压着眉），r1–r2 = 两行白蓝眼睛。
EYES = [(10, 0, 'kkk'), (16, 0, 'kkk'), (10, 1, 'WUk'), (16, 1, 'WUk'), (10, 2, 'WUU'), (16, 2, 'WUU')]
JO_FACE2 = edits(SJ.JO_FACE, *EYES)
# 坏笑（指人 “your next line is…”）：左眼同上，右眼眨眼（两行弯线），咧嘴露牙（同原 JO_FACE_SMUG 的嘴）
JO_FACE2_SMUG = edits(SJ.JO_FACE, (10, 0, 'kkk'), (10, 1, 'WUk'), (10, 2, 'WUU'),
                      (16, 0, 'SSS'), (16, 1, 'Skk'), (16, 2, 'kkS'), (7, 5, 'zzzzkwwwkz'))
# 攻击用：咬牙（嘴里一排牙），眼睛同 JO_FACE2
JO_FACE2_GRIT = edits(JO_FACE2, (7, 5, 'zzzzkwwwkz'))

# ============================================================================ 手
GLOVE_FIST = """
.hhh.
hhhhh
hhhhH
Hhhh.
.HH..
"""
GLOVE_OPEN = """
.h.h.
.hhhh
hhhhh
hhhhH
.HHH.
"""

# 远侧手臂（攻击用）：暗一档的袖子、3 像素前臂；近侧手臂照原工程
SLEEVE_F_ATK = 'iIII'
FORE_F_ATK = 'ssS'
SLEEVE_N_PT = 'iIII'          # 指人：袖子压在同色衬衫上，暗一档才分得开
FORE_N_PT = 'ssS'


def jo_arm2(g, pts, sleeve, skin, hand=None, off=(0, 0), sep='k', vines=False, fore=None, cuff='I'):
    """SJ.jo_arm 的分段版：袖子 a→b、卷起的袖口（深一像素，在 2/3 处）、露出的上臂 2/3→b、前臂 b→c（可另给色带 fore）、手。"""
    (a, b, c) = pts
    g.limb(a, b, sleeve, sep=sep)
    g.limb(b, c, fore or skin, sep=sep)
    mx, my = (a[0] + b[0] * 2) / 3, (a[1] + b[1] * 2) / 3
    g.limb((round(mx), round(my)), b, skin)
    if cuff:
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = max(abs(dx), abs(dy), 1)
        p = (round(mx - dx / L), round(my - dy / L))
        g.limb(p, p, cuff * len(sleeve))
    if hand:
        hw, hh = len(g_lines(hand)[0]), len(g_lines(hand))
        g.stamp(hand, c[0] - hw // 2 + off[0], c[1] - hh // 2 + off[1], sep=sep)
    if vines:
        SJ.hermit(g, pts, amp=2.2, strands=1)    # 原工程 camera 帧的画法（导演：两股会把手臂糊成一团紫）


def jo_frame2(legs=None, arm_n=None, arm_f=None, face=JO_FACE2, dy=0, k=0.0, hat_dy=0, hat_dx=0, extra=None,
              w=36, top=0, atk=False):
    """SJ.jo_frame 的副本（36×52 身体，脚在最底行，身体中线 x=18）。w = 画布加宽（向右伸手）、top = 头顶上加空行。
    arm_f / arm_n = dict(pts=[肩, 肘, 手], hand=, off=, vines=, orig=True 时照原工程画法)。
    atk=True：远侧手臂用攻击画法（暗袖、细前臂），躯干和脸盖上去时描肩缝。"""
    H = 52 + top
    g = G(w, H)
    legs = legs or ([(15, 34), (15, 47), 'flat'], [(21, 34), (22, 47), 'flat'])
    SJ.legs2(g, legs[0], legs[1], cols_n='llllL', cols_f='LllLL', shoe=SJ.JO_BOOT, shoe_toe=SJ.JO_BOOT_TOE, dy=top)
    up = G(w, H)

    def T(pts):
        return [(x, y + top) for x, y in pts]

    arm_f = arm_f if arm_f is not None else dict(pts=[(26, 23), (29, 28), (28, 33)], hand=SJ.GLOVE, orig=True)
    arm_n = arm_n if arm_n is not None else dict(pts=[(11, 23), (8, 28), (9, 33)], hand=SJ.FIST, orig=True)
    if arm_f:
        if arm_f.get('orig'):
            SJ.jo_arm(up, T(arm_f['pts']), SJ.JO_SLEEVE_F, SJ.JO_ARM_F, arm_f.get('hand', SJ.GLOVE),
                      arm_f.get('off', (0, 0)), sep=None)
        else:
            jo_arm2(up, T(arm_f['pts']), SLEEVE_F_ATK if atk else SJ.JO_SLEEVE_F, SJ.JO_ARM_F,
                    arm_f.get('hand', GLOVE_FIST), arm_f.get('off', (0, 0)), sep=None, vines=arm_f.get('vines', False),
                    fore=FORE_F_ATK if atk else None)
    sep = 'k' if atk else None
    up.stamp(SJ.JO_TORSO, 0, 20 + top, sep=sep)
    up.stamp(face, 6, 12 + top, sep=sep)
    up.stamp(SJ.JO_HAT, 6 + hat_dx, 5 + hat_dy + top)
    if arm_n:
        if arm_n.get('orig'):
            SJ.jo_arm(up, T(arm_n['pts']), SJ.JO_SLEEVE, SJ.JO_ARM, arm_n.get('hand', SJ.FIST), arm_n.get('off', (0, 0)),
                      vines=arm_n.get('vines', False))
        else:
            jo_arm2(up, T(arm_n['pts']), arm_n.get('sleeve', SJ.JO_SLEEVE), SJ.JO_ARM, arm_n.get('hand', SJ.FIST),
                    arm_n.get('off', (0, 0)), vines=arm_n.get('vines', False), fore=arm_n.get('fore'))
    if k:
        SJ.lean(up, k, 34 + top, rigid=21 + top)
    up.shift(0, dy)
    g.stamp(up.s(), 0, 0)
    if extra:
        extra(g)
    return g.outline().s()


def _anchor(top=0):
    return (18, 52 + top)


def _def(name, frames, desc, fps=None, top=0):
    sprite.define(name, frames, pal=SJ.JOPAL, anchor=_anchor(top), fps=fps, desc=desc)
    NEW.append(name)


# ============================================================================ 新动作
W_ATK = 60                                    # 画布宽：手套最远到 x≈46，lean 再往右推 2–3 px，留余量
BACK_N = dict(pts=[(11, 23), (7, 27), (6, 31)], hand=SJ.FIST)          # 近侧手臂往后摆（配合出手）
REST_N = dict(pts=[(11, 23), (8, 28), (8, 32)], hand=SJ.FIST)
L_SET = ([(15, 34), (13, 47), 'flat'], [(21, 34), (24, 47), 'flat'])   # 站定、重心在后
L_STEP = ([(15, 34), (12, 47), 'flat'], [(21, 34), (26, 47), 'flat'])  # 前脚踏出
L_LUNGE = ([(15, 34), (11, 47), 'flat'], [(21, 34), (27, 47), 'flat'])
L_BIG = ([(15, 34), (10, 47), 'flat'], [(21, 34), (28, 47), 'flat'])
L_BACK = ([(15, 34), (12, 47), 'flat'], [(21, 34), (25, 47), 'flat'])


def vine_atk_frames():
    return [
        # 蓄力：屈肘、手套收到肩前（和 stand.js 藤蔓起点同高），身子微微后仰
        jo_frame2(w=W_ATK, atk=True, k=-0.05, face=JO_FACE2,
                  arm_f=dict(pts=[(26, 23), (29, 28), (31, 21)], hand=GLOVE_FIST), arm_n=REST_N, legs=L_SET),
        # 甩出：手臂向前上方甩，手套张开
        jo_frame2(w=W_ATK, atk=True, k=0.06, face=JO_FACE2_GRIT,
                  arm_f=dict(pts=[(26, 23), (32, 21), (37, 20)], hand=GLOVE_OPEN), arm_n=BACK_N, legs=L_STEP),
        # 命中：手臂伸直到肩高、手套张开（藤蔓从这里继续往前），前脚踏出
        jo_frame2(w=W_ATK, atk=True, k=0.09, face=JO_FACE2_GRIT,
                  arm_f=dict(pts=[(26, 23), (33, 23), (40, 21)], hand=GLOVE_OPEN), arm_n=BACK_N, legs=L_LUNGE),
        # 收势：屈肘握拳往回拽（连打时一直停在这帧 = 拽住藤蔓）
        jo_frame2(w=W_ATK, atk=True, k=0.03, face=JO_FACE2,
                  arm_f=dict(pts=[(26, 23), (32, 27), (36, 22)], hand=GLOVE_FIST), arm_n=REST_N, legs=L_BACK),
    ]


TOP_H = 2                                     # 重击举臂过帽子：头顶加 2 行


def vine_heavy_frames():
    return [
        # 举臂过肩：手套举到帽檐右上方，近侧拳护在胸前，后仰
        jo_frame2(w=W_ATK, top=TOP_H, atk=True, k=-0.08, face=JO_FACE2_GRIT,
                  arm_f=dict(pts=[(26, 23), (31, 17), (33, 10)], hand=GLOVE_FIST),
                  arm_n=dict(pts=[(11, 23), (14, 28), (19, 27)], hand=SJ.FIST), legs=L_SET),
        # 猛抽：手臂向前甩到肩高，藤蔓缠满手臂，大步前冲
        jo_frame2(w=W_ATK, top=TOP_H, atk=True, k=0.12, face=JO_FACE2_GRIT,
                  arm_f=dict(pts=[(26, 23), (34, 22), (42, 23)], hand=GLOVE_OPEN, vines=True), arm_n=BACK_N, legs=L_BIG),
        # 定住：手臂略压低，藤蔓还缠着
        jo_frame2(w=W_ATK, top=TOP_H, atk=True, k=0.10, face=JO_FACE2_GRIT,
                  arm_f=dict(pts=[(26, 23), (34, 24), (42, 25)], hand=GLOVE_OPEN, vines=True), arm_n=BACK_N, legs=L_BIG),
        # 收势：屈肘握拳收回
        jo_frame2(w=W_ATK, top=TOP_H, atk=True, k=0.03, face=JO_FACE2,
                  arm_f=dict(pts=[(26, 23), (31, 27), (34, 24)], hand=GLOVE_FIST), arm_n=REST_N, legs=L_BACK),
    ]


def vine_hold_frames():
    return [
        jo_frame2(w=W_ATK, atk=True, k=0.07, face=JO_FACE2_GRIT,
                  arm_f=dict(pts=[(26, 23), (33, 23), (40, 22)], hand=GLOVE_FIST), arm_n=BACK_N, legs=L_LUNGE),
        jo_frame2(w=W_ATK, atk=True, k=0.07, face=JO_FACE2_GRIT, dy=1,
                  arm_f=dict(pts=[(26, 23), (33, 22), (40, 22)], hand=GLOVE_FIST), arm_n=BACK_N, legs=L_LUNGE),
    ]


def guard_frames():
    # 挡：棕手套的前臂竖在脸前（藤蔓 block 从肩前斜着往上长），近侧拳护胸，微微后仰
    return [jo_frame2(w=44, atk=True, k=-0.04, face=JO_FACE2_GRIT,
                      arm_f=dict(pts=[(26, 23), (32, 23), (31, 14)], hand=GLOVE_FIST),
                      arm_n=dict(pts=[(11, 23), (13, 29), (20, 25)], hand=SJ.FIST), legs=L_BACK)]


def register():
    _def('joseph.vine_atk', vine_atk_frames(), 'Hermit Purple throw: wind-up (glove cocked at the shoulder), '
         'fling, full extension (open glove; the vine itself is drawn by the stand), pull back', fps=15)
    _def('joseph.vine_heavy', vine_heavy_frames(), 'Hermit Purple heavy lash: arm raised over the hat, '
         'lash forward with vines wrapped on the arm, hold, recover', fps=10, top=TOP_H)
    _def('joseph.vine_hold', vine_hold_frames(), 'holding the vine taut: arm extended, fist clenched, slight tremble',
         fps=6)
    _def('joseph.whip', [vine_heavy_frames()[0], vine_heavy_frames()[1]],
         'whip: raise / lash with vines on the arm (same art as vine_heavy f0-f1)', fps=8, top=TOP_H)
    _def('joseph.guard', guard_frames(), 'block: gloved forearm raised in front of the face, other fist at the chest')


register()


# ============================================================================ 原图集同名重画（D12 审计之后）
def _orig_params():
    """和原工程 sprites_jojo.py 里 joseph.idle / walk / run / camera / point 的 jo_frame 参数逐条相同（脸除外）。"""
    J = SJ
    return {
        'joseph.idle': [dict(), dict(dy=1, arm_n=dict(pts=[(11, 23), (8, 28), (9, 32)], hand=J.FIST),
                                     arm_f=dict(pts=[(26, 23), (29, 28), (28, 32)], hand=J.GLOVE))],
        'joseph.walk': [dict(k) for k in J.JO_WALK],
        'joseph.run': [dict(k) for k in J.JO_RUN],
        'joseph.camera': [
            dict(arm_f=dict(pts=[(26, 23), (30, 17), (30, 12)], hand=J.GLOVE),
                 arm_n=dict(pts=[(11, 23), (5, 21), (4, 15)], hand=J.HAND_OPEN),
                 extra=J._cam(27, 6), legs=([(15, 34), (12, 47), 'flat'], [(21, 34), (25, 47), 'flat'])),
            dict(arm_f=dict(pts=[(26, 23), (29, 28), (30, 27)], hand=J.GLOVE),
                 arm_n=dict(pts=[(11, 23), (16, 27), (24, 23)], hand=J.HAND_OPEN, vines=True),
                 extra=J._cam(24, 24, broken=True), k=0.06,
                 legs=([(15, 34), (12, 47), 'flat'], [(21, 34), (25, 47), 'flat'])),
        ],
        'joseph.point': [dict(face=J.JO_FACE_SMUG,
                              arm_n=dict(pts=[(11, 23), (19, 24), (27, 23)], hand=J.HAND_POINT, off=(3, 0)),
                              legs=([(15, 34), (13, 47), 'flat'], [(21, 34), (24, 47), 'flat']))],
    }


# 指人修手臂：手臂抬高一像素到口袋上面、前臂微微上扬，袖子暗一档（不再和同色衬衫糊在一起）、卷起的袖口、3 像素前臂
POINT_ARM = dict(pts=[(11, 22), (18, 23), (27, 21)], hand=SJ.HAND_POINT, off=(3, 0), sleeve=SLEEVE_N_PT, fore=FORE_N_PT)


def _orig_frame(p, face):
    """原参数 → 原工程画法（手臂照原 jo_arm），只换脸。"""
    q = dict(p)
    for key in ('arm_f', 'arm_n'):
        if key in q and q[key] is not None:
            q[key] = dict(q[key], orig=True)
    q['face'] = face
    return jo_frame2(**q)


_ORIG = {}                                    # apply() 换掉之前的原精灵（scene_overrides 先用原 idle 复现原场景图做比对）


def apply():
    import art_later_existing as LE
    names = []
    for name, plist in _orig_params().items():
        old = sprite.get(name)
        _ORIG.setdefault(name, old)
        if len(plist) != len(old.frames):
            raise ValueError(f'{name} 参数帧数 {len(plist)} ≠ 原 {len(old.frames)}')
        # 先确认副本骨架放在原位置、用原脸时和原工程逐字一致（参数抄对了、jo_frame2 没走样），再换脸 / 改手臂
        if [_orig_frame(p, p.get('face', SJ.JO_FACE)) for p in plist] != [SJ.jo_frame(**p) for p in plist]:
            raise ValueError(f'{name}：jo_frame2 原样重画和原工程不一致')
        if name == 'joseph.point':
            p = dict(plist[0])
            frames = [jo_frame2(face=JO_FACE2_SMUG, arm_n=POINT_ARM, legs=p['legs'])]
        else:
            frames = [_orig_frame(p, JO_FACE2) for p in plist]
        sprite.define(name, frames, pal=SJ.JOPAL, anchor=old.anchor, fps=old.fps,
                      desc=(old.desc or '') + '（游戏层：脸照对话框头像' + ('、手臂分段' if name == 'joseph.point' else '') + '）')
        names.append(name)
    # 由 idle 派生的帧跟着换脸：落水半头（水线、锚点同 art_later_existing）、闪避（同一个剪切公式）
    for act, n in (('float', 2), ('dodge', 1)):
        name = 'joseph.' + act
        old = sprite.get(name)
        frames = [LE.action('joseph', act, i) for i in range(n)]
        sprite.define(name, frames, pal=None, anchor=old.anchor, fps=old.fps, desc=(old.desc or '') + '（随新脸重算）')
        names.append(name)
    return names


# ============================================================================ 场景专用图换新脸（2026-10-10）
# 原工程场景脚本用 joseph.idle 现做了三张场景专用图（序章荷莉病床前跪坐 / 伸手、终章机场挥手），游戏直接从只读的
# 角色图集\场景专用\ 拷，还是旧脸（眯缝眼）。这里不碰原图：调用原场景模块自己的生成函数，先用原 idle 复现一遍、
# 和原 PNG 逐像素比对（必须一致 = 做法和原工程一模一样），再换成新脸的 idle 重做，写到 assets\props_new\scene\<文件名>；
# build_assets 的 props 步见到同名替换图就用它（显式钩子，只这一个目录）。
SCENE_POSES = ('s05_joseph_kneel', 's05_joseph_reach', 's20_joseph_wave')


def _scene_build():
    """用当前登记的 joseph.idle 跑原场景脚本的生成函数（参数抄自 s05_holly._define_sprites / s20_farewell._define_sprites）。"""
    from scenes import s05_holly as S05, s20_farewell as S20
    S05._mk_kneel('joseph.idle', 's05.joseph_kneel', 35, 7, 30, '#6e6a3c', '#48452a', '#8a8650')
    S05._mk_reach()
    S20._mk_joseph_wave()
    return {'s05_joseph_kneel': sprite.get('s05.joseph_kneel'), 's05_joseph_reach': sprite.get('s05.joseph_reach'),
            's20_joseph_wave': sprite.get('s20.joseph_wave')}


def _strip(sd):
    """同 烘焙脚本 bake_strips：帧从左到右紧挨的横向帧条（每帧 = 第 0 帧的尺寸）。"""
    from PIL import Image
    frames = [f.convert('RGBA') for f in sd.frames]
    w, h = frames[0].size
    out = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        out.paste(f, (i * w, 0))
    return out


def scene_overrides(out_dir):
    """必须在 apply() 之后调；返回写出的文件名列表。原 idle 复现不出原 PNG 就抛错（不写任何文件）。"""
    import os
    import numpy as np
    from PIL import Image
    if 'joseph.idle' not in _ORIG:
        raise ValueError('scene_overrides 要在 apply() 之后调')
    new_idle = sprite.get('joseph.idle')
    sprite._REG['joseph.idle'] = _ORIG['joseph.idle']
    try:
        old = {k: _strip(sd) for k, sd in _scene_build().items()}
    finally:
        sprite._REG['joseph.idle'] = new_idle
    src_dir = os.path.join(AC.ATLAS_DIR, '场景专用')
    for fid, im in old.items():
        ref = np.asarray(Image.open(os.path.join(src_dir, fid + '.png')).convert('RGBA'))
        if ref.shape != np.asarray(im).shape or not np.array_equal(ref, np.asarray(im)):
            raise ValueError(f'{fid}：用原 idle 复现的场景图和 角色图集\\场景专用 的原图不一致，不能替换')
    new = {k: _strip(sd) for k, sd in _scene_build().items()}
    os.makedirs(out_dir, exist_ok=True)
    files = []
    for fid, im in new.items():
        if im.size != old[fid].size:
            raise ValueError(f'{fid}：新脸版尺寸 {im.size} ≠ 原图 {old[fid].size}')
        path = os.path.join(out_dir, fid + '.png')
        im.save(path, optimize=True)
        if not np.array_equal(np.asarray(Image.open(path).convert('RGBA')), np.asarray(im)):
            raise ValueError(f'{fid}：回读不一致')
        files.append(fid + '.png')
    return files
