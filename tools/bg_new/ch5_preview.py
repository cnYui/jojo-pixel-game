"""第5章场景预览及改前、改后对照，所有产物写工具预览目录。"""
import sys
sys.dont_write_bytecode = True

from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('late_preview', HERE / 'late_preview.py')
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)
preview.KEYS = ['desert_highway', 'mountain_road', 'fog_town', 'enya_inn', 'karachi_street', 'brain_inside']
preview.STAGE_WALK = {key: (148, 176) for key in preview.KEYS}
preview.STAGE_WALK.update(desert_highway=(152, 168), fog_town=(146, 176), brain_inside=(130, 176))
preview.OUT = str(HERE / '_preview' / 'ch5')

if __name__ == '__main__':
    raise SystemExit(preview.main() or 0)
