# 统一第五部路径，所有生成器只在当前克隆的第五部写入，复用来源保持只读。
import json
from pathlib import Path

P5 = Path(__file__).resolve().parents[1]
REPO = P5.parent
ASSETS = P5 / 'assets'
META = ASSETS / '_meta'
GAME = P5 / '游戏'


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def load_json(path, default=None):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default


# 地图规格同开发脚本第2节，背景与校验共用，避免宽度和分包各写一份后漂移。
BACKGROUNDS = [
    ('map_pro', 'naples_map', 320, False, 'prologue'),
    ('airin_pro', 'airport_hall', 480, True, 'prologue'),
    ('airout_pro', 'airport_out', 640, False, 'prologue'),
    ('street_ch1', 'naples_street', 480, False, 'ch1'),
    ('cafe_ch1', 'naples_cafe', 480, False, 'ch1'),
    ('station_ch1', 'funicular_station', 480, False, 'ch1'),
    ('car_ch1', 'funicular_car', 320, True, 'ch1'),
    ('square_ch1', 'station_square', 640, False, 'ch1'),
    ('harbor_ch1', 'naples_harbor', 640, False, 'ch1'),
    ('title', 'p5_title', 320, False, 'title'),
]
