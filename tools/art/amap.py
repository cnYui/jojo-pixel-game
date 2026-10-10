"""amap -- 逻辑动作名 → 图集真名（技术约定 §3.3、§3.14 A / B、§5.2）+ 判定体宽 BODYW（规划 §3.2）。

纯数据模块（不 import 原工程），build_assets.py 的 chars 步读进 `chars[cid].amap / bodyW`。

值的写法（技术约定 §3.3）：
  字符串            = 图集真名
  {'a': 真名, 'f': 定格帧 | None, 'rot': 顺时针角度（度）, 'flip': bool, 'dy': 像素}
解析顺序在 atlas.js：amap → animations → aliases → G.FALLBACK → idle → 第一个动作。
这里写的条目 = §3.14 的最少条目（一条不少）+ 让常用逻辑名不走通用回退（不进 G.dbg.animFallbacks）的补充。
换装前缀：`skin + '_' + 逻辑名` 先按 amap 查（银色战车脱甲 `skin: 'bare'`）。
自检：tools\\dev\\p7a\\test_art.py 会核对每个真名都在该图集的 animations 里。
"""
import sys
sys.dont_write_bytecode = True


def _same(*names):
    return {n: n for n in names}


def _many(target, *names):
    return {n: target for n in names}


AMAP = {
    # ------------------------------------------------------------------ 主角团本体（§3.14 A）
    'jotaro': {
        **_many('point', 'cmd', 'cmd2', 'cmd_hold'),
        **_same('guard', 'dodge', 'down', 'hurt'),
        **_many('pose', 'special', 'win'),
        'talk': 'idle', 'getup': 'hurt',
    },
    'joseph': {                                   # whip / guard / dodge 第4章才补（规划 §7.1）
        # 2026-10-09 晚：普通攻击不再定在一张 point 上（art_joseph）：cmd = 甩藤四段（J1 / J2 / 收尾 / 连打）、
        # cmd2 = 猛抽（J3 的 body 改成 cmd2）、cmd_hold = 伸臂拽藤；special 照规划 §3 仍是 point（波纹从指尖出）
        'cmd': 'vine_atk', 'cmd2': 'vine_heavy', 'cmd_hold': 'vine_hold', 'special': 'point',
        'down': {'a': 'lie', 'flip': True},        # lie 头朝右，翻过来 = 朝右时头朝左（报告 08 §9.3）
        'talk': 'idle', 'getup': 'hurt', 'win': 'idle',
    },
    'avdol': {
        **_many('cast', 'cmd', 'cmd2', 'cmd_hold', 'special'),
        'win': 'yes',
        **_same('guard', 'dodge', 'hurt', 'down'),
        'talk': 'idle', 'getup': 'hurt', 'shock': 'hurt',
    },
    'kakyoin': {
        **_many('cast', 'cmd', 'cmd2', 'cmd_hold', 'special'),
        **_same('guard', 'dodge', 'hurt', 'down'),
        'talk': 'idle', 'getup': 'hurt', 'shock': 'hurt', 'win': 'idle',
        # 序2 敌方花京院的待机写在 S.fight 的敌人 spec（idle: 'possessed'），不在这里改 idle（§8.2 第 48 条）
    },
    'polnareff': {                                # guard / dodge 第3章才画，M1 走通用回退（§3.14 A）
        **_many('fight', 'cmd', 'cmd2', 'cmd_hold', 'special'),
        **_same('down', 'hurt'),
        'talk': 'idle', 'getup': 'hurt', 'win': 'wave',
    },
    'iggy': {
        'walk': 'run', 'talk': 'idle',
        **_many({'a': 'bite', 'f': 0}, 'cmd', 'cmd2', 'cmd_hold'),   # 报告 08 §4.1：出招指令用 bite[0] 低吼
        'special': 'bite', 'down': 'down',
    },
    'holly': {
        'talk': 'idle', 'win': 'wave', 'shock': 'idle',
        'hurt': {'a': 'faint', 'f': 0}, 'down': {'a': 'faint', 'f': 1},
    },

    # ------------------------------------------------------------------ 主角团替身（§3.14 A）
    'starplat': {
        **_many('punch', 'punch', 'punch2'),
        'punch_heavy': 'upper',
        **_same('rush', 'block', 'hurt'),
        'special': 'rush',
    },
    'magred': {
        **_many('punch', 'punch', 'punch2'),
        # 2026-10-10：重拳有了自己的帧 magred.heavy（蓄火 → 直拳出火球；J3 火球、连打终结用）；地火柱 / 大招照旧用 cast
        'punch_heavy': 'heavy',
        **_many('cast', 'rush', 'special'),
        **_same('block', 'hurt'),
        'pose': 'idle',
    },
    'hiero': {
        **_many('cast', 'punch', 'punch2', 'rush', 'special'),
        'punch_heavy': 'whip',
        **_same('block', 'hurt'),
        'pose': 'idle',
    },
    'chariot': {
        **_many('thrust', 'punch', 'punch2', 'punch_heavy', 'rush', 'attack', 'special'),
        'slash': 'slash', 'block': 'parry', 'hurt': 'hurt', 'pose': 'idle',
        # 脱甲（stand.skin = 'bare'）：bare_<逻辑名>
        'bare_idle': 'bare_idle',
        **_many('bare_thrust', 'bare_punch', 'bare_punch2', 'bare_punch_heavy', 'bare_rush', 'bare_attack',
                'bare_special', 'bare_slash'),
        'bare_block': 'bare_idle', 'bare_hurt': 'bare_idle', 'bare_pose': 'bare_idle',
    },
    'fool': {'fly': 'glide', 'block': 'idle', 'pose': 'idle'},
    'hermit': {'idle': 'vine'},                   # kind 'vine'：运行时不画图集（§4.12）

    # ------------------------------------------------------------------ DIO 阵营 / 敌人（M1 之后的章节再细化）
    'dio': {
        'talk': 'idle', 'attack': 'throw', 'shoot': 'throw', 'windup': {'a': 'throw', 'f': 0},
        'cmd': 'pose', 'special': 'pose', 'win': 'laugh', 'fly': 'jump',
    },
    'theworld': {
        **_many('punch', 'punch', 'punch2'),
        'punch_heavy': {'a': 'punch', 'f': 2},
        **_same('rush'), 'special': 'rush', 'block': 'idle',
    },
    'vanilla': {'talk': 'idle', 'attack': 'idle'},
    'cream': {'attack': 'void', 'fly': 'void', 'pose': 'idle'},
    'holhorse': {
        'talk': 'idle', 'run': 'flee', 'attack': 'shoot', 'shoot': 'shoot',
        'windup': {'a': 'shoot', 'f': 0}, 'cmd': {'a': 'shoot', 'f': 0},
    },
    'jgeil': {'talk': 'idle', 'hurt': 'hurt'},
    'enya': {'talk': 'idle', **_many({'a': 'idle', 'f': 1}, 'cmd', 'attack', 'special')},   # f1 举手
    'ndoul': {'talk': 'idle'},
    'oingo': {'talk': 'idle', 'hurt': 'boom'},
    'boingo': {'talk': 'idle'},
    'darby': {'idle': 'sit', 'talk': 'sit'},
    'telence': {'talk': 'idle'},
    'steelydan': {'talk': 'idle'},
    'mariah': {'talk': 'idle'},
    'alessi': {'talk': 'idle'},
    'petshop': {'idle': 'perch', 'fly': 'fly', 'attack': 'fly'},
    'strength': {'talk': 'idle'},
    'hangedman': {'talk': 'idle'},
    'justice': {'idle': 'skull', 'attack': 'skull'},
    'geb': {'idle': {'a': 'claw', 'f': 0}, 'attack': 'claw'},
    'towergray': {                                # §3.14 A：idle → fly、attack → needle
        'idle': 'fly', 'attack': 'needle', 'fly': 'fly',
        'windup': 'fly', 'hurt': 'fly', 'shoot': 'needle',
    },
    'darkbluemoon': {'idle': 'swim', 'attack': 'swim', 'fly': 'swim'},
    'wheel': {'idle': 'car', 'walk': 'car', 'attack': 'car'},
    'death13': {'idle': 'float', 'attack': 'float', 'fly': 'float'},
    'judgement': {'talk': 'idle'},
    'highpriestess': {'talk': 'idle'},
    'zombie': {'idle': 'walk', 'attack': 'walk'},

    # ------------------------------------------------------------------ 新角色（§3.14 B）
    'grayfly': {
        'walk': 'idle', 'talk': 'idle', 'hurt': 'hurt', 'down': 'down', 'shock': 'hurt',
        'getup': 'hurt', 'sit': 'seated', 'cmd': 'idle',
    },
    'npc_nurse': {
        'talk': 'idle', 'hurt': 'idle', 'shock': 'idle', 'down': 'faint',
        'attack': 'stab', 'cmd': 'stab', 'windup': 'possessed',
    },
    **{f'npc_passenger_{k}': {
        'idle': 'seated', 'talk': 'seated', 'walk': 'seated', 'shock': 'seated',
        'hurt': 'slump', 'down': 'slump', 'sit': 'seated', 'seated': 'seated',
    } for k in 'abcd'},
    'npc_police': {'talk': 'idle', 'hurt': 'shock', 'shock': 'shock'},
    **{f'npc_student_f_{k}': {
        'talk': 'idle', 'hurt': 'idle', 'shock': 'idle', 'down': 'down', 'win': 'cheer',
    } for k in 'ab'},
    'npc_stewardess': {'talk': 'idle', 'hurt': 'idle'},
    'npc_hk_owner': {'talk': 'idle', 'hurt': 'idle'},
    'npc_hk_granny': {'talk': 'idle', 'hurt': 'idle'},
    'npc_hk_passer_a': {'talk': 'idle', 'hurt': 'idle'},
    'npc_hk_passer_b': {'talk': 'idle', 'hurt': 'idle'},
    'npc_fortune': {'walk': 'idle', 'talk': 'idle', 'hurt': 'idle'},
    'npc_student_m': {'talk': 'idle', 'hurt': 'idle'},
}

# 新角色显式覆盖基础逻辑动作，避免完整资源仍进入运行时通用回退。
for _cid in ('grayfly', 'npc_nurse', 'npc_police', 'npc_student_f_a', 'npc_student_f_b',
             'npc_stewardess', 'npc_hk_owner', 'npc_hk_granny', 'npc_hk_passer_a',
             'npc_hk_passer_b', 'npc_fortune', 'npc_student_m'):
    AMAP[_cid].setdefault('idle', 'idle')
    AMAP[_cid].setdefault('walk', 'walk')

# 判定用身体半宽（px），规划 §3.2；其余 cid 由 chars 步按 idle 第 0 帧宽 × 0.3（最小 3）算
BODYW = {'jotaro': 7, 'joseph': 7, 'avdol': 7, 'kakyoin': 6, 'polnareff': 6, 'iggy': 5}

# 后续章节的完整动作接线；动作确有自己的帧，逻辑动作不会隐式退回第一张图。
_LATER_PEOPLE = ('fake_tennille','anne','devo','rubbersoul','nena','zz','cameo','chaka','khan',
    'kennyg','nukesaku','wilson','npc_sailor','npc_kid','npc_townsfolk','npc_villager_f',
    'npc_islander','npc_dealer','polnareff_kid','jotaro_kid','polnareff_possessed',
    'clay_sherry','clay_gold','clay_pol','atum','npc_spw','npc_merchant')
for _cid in _LATER_PEOPLE:
    AMAP[_cid] = _same('idle','walk','talk','hurt','down','portrait')
    AMAP[_cid].update(shock='hurt',getup='hurt')
for _cid in ('devo_doll','empress','lovers','mannish','npc_cat','midler_back'):
    AMAP[_cid] = _same('idle','walk','talk','hurt','down')
AMAP['mannish'].update(_same('laugh','cry','portrait'))
AMAP['devo_doll'].update(attack='slash',**_same('slash','run'))
AMAP['empress'].update(attack='bite',**_same('bite',*[f'l{s}_{act}' for s in range(4) for act in ('idle','bite')]))
AMAP['lovers'].update(_same('split'))
AMAP['npc_cat'].update(_same('eat'))
AMAP['rubbersoul'].update(_same('slime_idle','slime_attack'))
for _cid in ('khan','atum','empress','lovers','mannish','npc_cat'):
    AMAP[_cid]['talk']='idle'
AMAP['empress'].update(walk='idle',l3_idle='idle',l3_bite='bite')
AMAP['midler_back'].update(_many('idle','walk','talk','hurt','down'))
_EXISTING = {
 'joseph':('whip','guard','dodge'), 'polnareff':('guard','dodge','kid','possessed','kneel','kick'),
 'jotaro':('kid','kick'), 'avdol':('push',), 'iggy':('hurt','dodge','limp_walk'), 'starplat':('finger',),
 'darkbluemoon':('attack','hurt'), 'strength':('walk','attack','hurt','down'),
 'hangedman':('attack',), 'holhorse':('hurt','down'), 'jgeil':('walk',),
 'wheel':('climb','spray'), 'enya':('cast','hurt','down'), 'zombie':('attack',),
 'steelydan':('hurt','down','fly','command'), 'death13':('swing','hurt'),
 'judgement':('attack',), 'highpriestess':('attack',), 'fool':('claw','slam','wall'),
 'ndoul':('hurt','down'), 'boingo':('scared',), 'mariah':('walk','kick','hurt','down'),
 'alessi':('walk','axe','hurt','down','beg'), 'petshop':('dive',),
 'vanilla':('walk','kick','stomp','hurt','kneel'), 'theworld':('hurt','kick'), 'dio':('punch',),
 'telence':('walk','punch','hurt','down')
}
for _cid,_acts in _EXISTING.items(): AMAP.setdefault(_cid,{}).update(_same(*_acts))
for _cid in ('jotaro','joseph','avdol','kakyoin','polnareff'):
    AMAP[_cid]['float']='float'
AMAP['grayfly']['seated']='seated'
_PERSON_SPECIALS={
 'anne':('run','wave','angry','portrait_angry'), 'devo':('slash',),
 'fake_tennille':('grab','reveal','portrait_reveal'), 'chaka':('slash',), 'khan':('slash',),
 'clay_gold':('attack',), 'clay_pol':('attack',), 'clay_sherry':('attack',),
 'jotaro_kid':('run','punch'), 'kennyg':('attack','sax'), 'nena':('true_form',),
 'npc_dealer':('deal',), 'npc_kid':('run',), 'nukesaku':('attack','reverse','portrait_reverse'),
 'polnareff_kid':('run','hide'), 'polnareff_possessed':('slash','attack'), 'rubbersoul':('beg',),
}
for _cid,_acts in _PERSON_SPECIALS.items(): AMAP[_cid].update(_same(*_acts))
AMAP['polnareff_possessed']['slash']='attack'
for _cid in ('osiris','horus'):
    AMAP[_cid]={**_same('idle','attack','hurt','down'),**_many('idle','walk','talk','fly','block','pose','cmd'),
      **_many('attack','punch','punch2','punch_heavy','rush','special','cast')}


def target(v):
    """amap 值 → 图集真名。"""
    return v['a'] if isinstance(v, dict) else v


def targets(cid):
    return sorted({target(v) for v in AMAP.get(cid, {}).values()})
