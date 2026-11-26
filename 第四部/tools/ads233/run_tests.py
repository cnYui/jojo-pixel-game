"""在系统临时副本运行广告与通关验收；不修改第四部游戏源码，不安装依赖。"""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import overlay


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    env = dict(os.environ, PYTHONUTF8='1', NODE_PATH='D:/CodeWorkSpace/honglou-juan2/node_modules')
    before = hashes(overlay.SOURCE)
    work = Path(tempfile.mkdtemp(prefix='p4-ads233-'))
    game = work / '第四部/游戏'
    dev = work / '第四部/tools/dev'
    print('验收目录：' + str(work), flush=True)
    shutil.copytree(overlay.SOURCE, game)
    shutil.copytree(overlay.HERE.parent / 'dev', dev)
    try:
        subprocess.run([sys.executable, '-B', str(overlay.HERE / 'test_overlay.py')], env=env, check=True)
        overlay.apply(game)
        subprocess.run(['node', str(overlay.HERE / 'test_ads.js'), str(game), str(work / 'ads')], env=env, check=True)
        for chapter in ('prologue', 'ch5'):
            cmd = ['node', str(dev / 'p4_play.js'), '--out', str(work / chapter), '--no-shots']
            if chapter != 'prologue':
                cmd.extend(['--chapter', chapter])
            subprocess.run(cmd, env=env, check=True)
    finally:
        if before != hashes(overlay.SOURCE):
            raise RuntimeError('第四部游戏源码字节发生变化')
    print('通过；报告保留在系统临时目录：' + str(work), flush=True)


if __name__ == '__main__':
    main()
