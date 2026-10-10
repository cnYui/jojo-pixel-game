"""荷莉的头往前挪（用户 2026-10-09 看拘留所截图：“妈妈的头是不是也错位了”）。

原工程 SJ.h_frame 把 15 px 宽的头盖在 x 5（身体中线 x 16）：头发团整体落在身体后面约 4 px，
游戏里看着像头没放在肩膀上。这里在 D12 原名审计之后显式替换 holly.idle / walk / wave
（和 art_jotaro_redraw.apply 同样的做法；只读的原图集、原工程都不动）：
用游戏层的 h_frame2（SJ.h_frame 的副本）按原参数重画，只把头往右挪 HEAD_DX 像素。
倒下 / 被褥 / 头像不动。借 h_frame2 的女性 NPC 在 art_npc 里用 head_dx=NPC_HEAD_DX 同样挪 2 px（2026-10-09 晚）；
h_frame2 的默认参数（head_xy=(5, 9)、head_dx=0）仍和原工程逐字相同，下面的断言照旧成立。
"""
import art_common as AC                       # noqa: F401  （设好 sys.path：原工程源码）
from engine import sprite                     # noqa: E402
from assets import sprites_jojo as SJ         # noqa: E402
import art_npc as N                           # noqa: E402

HEAD_DX = 2


def _params():
    """和原工程 sprites_jojo.py 里 holly.idle / walk / wave 的 h_frame 参数逐条相同。"""
    return {
        'holly.idle': [dict(), dict(dy=1, arm_n=[(12, 24), (10, 29), (10, 32)], arm_f=[(21, 24), (23, 29), (22, 32)])],
        'holly.walk': [dict(k) for k in SJ.H_WALK],
        'holly.wave': [
            dict(head=SJ.H_HEAD_HAPPY, arm_f=[(21, 24), (26, 20), (26, 13)], hand_f=SJ.H_HAND_UP),
            dict(head=SJ.H_HEAD_HAPPY, arm_f=[(21, 24), (26, 20), (29, 14)], hand_f=SJ.H_HAND_UP, dy=-1, hem=1),
        ],
    }


def apply():
    names = []
    for name, plist in _params().items():
        old = sprite.get(name)
        if len(plist) != len(old.frames):
            raise ValueError(f'{name} 参数帧数 {len(plist)} ≠ 原 {len(old.frames)}')
        # 先确认副本骨架放在原位置时和原工程逐字一致（参数抄对了），再挪头
        if [N.h_frame2(**p) for p in plist] != [SJ.h_frame(**p) for p in plist]:
            raise ValueError(f'{name}：h_frame2 原位置重画和原工程不一致，参数没抄对')
        frames = [N.h_frame2(head_xy=(5 + HEAD_DX, 9), **p) for p in plist]
        sprite.define(name, frames, pal=SJ.HPAL, anchor=old.anchor, fps=old.fps,
                      desc=(old.desc or '') + f'（游戏层：头往前挪 {HEAD_DX} px）')
        names.append(name)
    return names
