# 第五部替身：画法照第三部、第四部原版（stand5.py 的画笔）。定义分在 stands_*.py 里，这里按出场顺序汇总。
import importlib
import os
import sys

from castlib import make_build, main

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ['goldexp', 'stickyfingers', 'moodyblues', 'sexpistols', 'aerosmith', 'purplehaze', 'spicegirl', 'requiem',
         'kingcrimson', 'metallica', 'littlefeet', 'mirrorman', 'gratefuldead', 'beachboy', 'babyface', 'whitealbum',
         'clash', 'talkinghead', 'greenday', 'oasis', 'softmachine', 'kraftwork', 'blacksabbath']
_all, ACTION_NAMES = {}, {}
for _m in ('stands_a', 'stands_a2', 'stands_b', 'stands_c'):
    if os.path.exists(os.path.join(HERE, _m + '.py')):
        _mod = importlib.import_module(_m)
        _all.update(_mod.STANDS)
        ACTION_NAMES.update(getattr(_mod, 'ACTION_NAMES', {}))

CAST = {k: _all[k] for k in ORDER if k in _all}
CAST.update({k: v for k, v in _all.items() if k not in CAST})
build = make_build(CAST, kind='stand')

if __name__ == '__main__':
    main(CAST, build, sys.argv)
