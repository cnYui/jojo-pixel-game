"""统一只读素材根目录，避免发布克隆把产物写回旧工作区。"""
import os
from pathlib import Path

GAME = Path(__file__).resolve().parent.parent
WORK = Path(os.environ.get("JOJO_WORKSPACE", GAME.parent)).resolve()
SRC = WORK / "源码"
