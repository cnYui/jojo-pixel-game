# 第四部的主角表 / 说话人 / 替身表（数值照设计文档 3.2：HP、走速、光环色、打字音）。
#   格式照第三部 GAME_DATA.heroes / speakers / stands。
HEROES = {
    'josuke': dict(cid='josuke', cn='东方仗助', short='仗助', rn='HIGASHIKATA JOSUKE', stand='crazyd',
                   burst=['#6a1a4a', '#a8306e', '#e060a0'], panel='#2a0a20', accent='#ff8ac0', nameColor='#b04a8a',
                   blipHz=480, grunt='grunt_jotaro'),
    'jotaro4': dict(cid='jotaro4', cn='空条承太郎', short='承太郎', rn='KUJO JOTARO', stand='starplat',
                    burst=['#241c6a', '#3e32a8', '#5a4ad0'], panel='#0e0a2c', accent='#ffe040', nameColor='#5a6ab0',
                    blipHz=440, grunt='grunt_jotaro'),
    'koichi': dict(cid='koichi', cn='广濑康一', short='康一', rn='HIROSE KOICHI', stand=None,
                   burst=['#2a5a1a', '#4a8a2a', '#9be070'], panel='#0e200a', accent='#9be070', nameColor='#5a9a3a',
                   blipHz=660, grunt=None),
}
SPEAKERS = {
    'tomoko': dict(short='朋子', nameColor='#c05a7a', blipHz=720),
    'ryohei': dict(short='良平', nameColor='#4a6aa0', blipHz=400),
    'angelo': dict(short='安杰罗', nameColor='#5a8a9a', blipHz=380),
    'milkman': dict(short='送奶工', nameColor='#6a7a8a', blipHz=380),
    'aqua': dict(short='水中项链', nameColor='#3a9ac8', blipHz=520),
    'thug_a': dict(short='学长A', nameColor='#8a5a3a', blipHz=420),
    'thug_b': dict(short='学长B', nameColor='#6a5a7a', blipHz=460),
    'robber': dict(short='劫匪', nameColor='#7a6a3a', blipHz=420),
    'clerk': dict(short='店员', nameColor='#3a8a6a', blipHz=760),
    'fan_a': dict(short='女生', nameColor='#d0608a', blipHz=820),
    'fan_b': dict(short='女生', nameColor='#a060c0', blipHz=860),
    'flirt': dict(short='搭讪的男人', nameColor='#7a7a6a', blipHz=500),
    'granny': dict(short='老奶奶', nameColor='#9a7a5a', blipHz=640),
    'kid': dict(short='小学生', nameColor='#d08a3a', blipHz=900),
    'crazyd': dict(short='疯狂钻石', nameColor='#d0609a', blipHz=480),
}
STANDS = {
    'crazyd': dict(cn='疯狂钻石', en='CRAZY DIAMOND', owner='josuke', aura='#ff8ac0', card='#ffb0d8', ghost='#ffd0e8',
                   impact='pink', kind='humanoid', idle={'dx': -6, 'z': 6}, link=None, summonSfx='stand_summon_star', fist=True),
    'aqua': dict(cn='水中项链', en='AQUA NECKLACE', owner='angelo', aura='#60c8f0', card='#a0e0ff', ghost='#c0f0ff',
                 impact='blue', kind='humanoid', idle={'dx': 0, 'z': 8}, link=None, summonSfx=None, fist=False),
}


def fill(meta):
    meta['heroes'] = dict(HEROES)
    meta['speakers'] = dict(SPEAKERS)
    meta['stands'] = dict(STANDS)
    meta['ck'] = 0.625
    return meta
