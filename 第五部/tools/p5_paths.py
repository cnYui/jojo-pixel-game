# 统一第五部路径，所有生成器只在当前克隆的第五部写入，复用来源保持只读。
import json
from pathlib import Path

P5 = Path(__file__).resolve().parents[1]
REPO = P5.parent
ASSETS = P5 / 'assets'
META = ASSETS / '_meta'
GAME = P5 / '游戏'
# 固定跨部复用的角色图与工具，使第五部的构建不受第四部变更影响。
SHARED_ART = P5 / 'tools/shared_art'
SHARED_CAST = ('koichi', 'jotaro4', 'echoes3')


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
    # 新章背景保留完整画面，按章延迟加载。
    ('prison_ch2', 'p5_prison', 320, True, 'ch2'),
    ('capri_ch3', 'p5_capri', 320, False, 'ch3'),
    ('pompeii_ch4', 'p5_pompeii', 320, False, 'ch4'),
    ('train_ch5', 'p5_train', 320, True, 'ch5'),
    ('highway_ch6', 'p5_highway', 320, False, 'ch6'),
    ('venice_ch7', 'p5_venice', 320, False, 'ch7'),
    ('sardinia_ch8', 'p5_sardinia', 320, False, 'ch8'),
    ('rome_fin', 'p5_rome', 320, False, 'final'),
    ('colosseum_fin', 'p5_colosseum', 320, False, 'final'),
]
