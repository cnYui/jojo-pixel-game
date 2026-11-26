# 第五部独立加锁验收入口，避免公共构建向本任务范围之外写入产物。
import os
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
LOCK = TOOLS / 'dev/_out/build.lock'


def main():
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with LOCK.open('x') as lock:
        lock.write(str(os.getpid()))
    try:
        for step in sys.argv[1:] or ['data', 'check']:
            script = {'data': TOOLS / 'build_p5.py', 'check': TOOLS / 'dev/p5_contract.py'}[step]
            subprocess.run([sys.executable, '-B', str(script)], check=True,
                           env=dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1'))
    finally:
        LOCK.unlink()


if __name__ == '__main__':
    main()
