"""带锁的资源构建：多个代理同时修剧情时，避免两个 build_assets.py 同时写 data\\。

用法：python -B tools\\dev\\full\\locked_build.py ui font data check
拿不到锁就每 3 秒重试，最多等 15 分钟；锁文件超过 20 分钟视为残留，自动接管。
"""
import sys

sys.dont_write_bytecode = True
import os
import subprocess
import time
from pathlib import Path

GAME = Path(__file__).resolve().parents[3]
LOCK = GAME / 'tools' / '_build.lock'


def acquire():
    t0 = time.time()
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f'{os.getpid()} {time.time():.0f}'.encode())
            os.close(fd)
            return
        except FileExistsError:
            try:
                if time.time() - LOCK.stat().st_mtime > 20 * 60:
                    LOCK.unlink()
                    continue
            except FileNotFoundError:
                continue
            if time.time() - t0 > 15 * 60:
                raise SystemExit('locked_build: 等锁超过 15 分钟，放弃')
            time.sleep(3)


def main():
    acquire()
    try:
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        r = subprocess.run([sys.executable, '-B', str(GAME / 'tools' / 'build_assets.py'), *sys.argv[1:]], cwd=GAME, env=env)
        return r.returncode
    finally:
        try:
            LOCK.unlink()
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    sys.exit(main())
