# -*- coding: utf-8 -*-
r"""《JoJo 第三部 星尘斗士》网页游戏 · 资源构建总入口（包 6，技术约定 §5）。

用法（PowerShell 先 $env:PYTHONDONTWRITEBYTECODE = 1）：
    python -B tools\build_assets.py                    # 默认：art chars props bg ui fx font audio data check（不含视频）
    python -B tools\build_assets.py font data check    # 改了台词 / 登记表的文字
    python -B tools\build_assets.py ui font data       # 改了 tools\registry\ui_texts.json / stands.json
    python -B tools\build_assets.py art chars data     # 补了帧
    python -B tools\build_assets.py bg data            # 改了背景
    python -B tools\build_assets.py video data         # 过场视频 op / coffin（约 1 分钟）
    python -B tools\build_assets.py --skip art,audio   # 并行阶段包 6 自测用（art / audio 的产物不归包 6 写）
    加 --force：忽略缓存全部重做

每步把元数据写 tools\_meta\<步>.json，图片登记在 tools\_meta\img_index.json（key → PNG → 包），
最后 data 步合成 data\data_meta.js、data\img_core.js、data\img_bg_<短名>.js。

别的包的“配方”模块（都可能晚到；导入失败 / 抛错时打印原因，这一步用兜底继续）：
    art   tools\art\bake_art.py  run(out_dir, c)         （包 7A）——兜底：跳过
    chars tools\art\amap.py      AMAP / BODYW            （包 7A）——兜底：内置 §3.14 A 的最少 amap（只留图集里有的真名）
    bg    tools\bg_jojo.py       build_all(stages, c)    （包 7B）——兜底：§3.14 D 每个 key 用 snap(name, t=0) 出一张 static
    ui    tools\registry\ui_texts.json / stands.json      （包 8）——兜底：ui_jojo.py 内置的 M1 最少条目（登记表有的条目优先）
    audio tools\build_audio.py   run(args, c)            （包 1）——兜底：跳过（读已有的 _meta\audio.json）
"""
import sys
sys.dont_write_bytecode = True                       # 必须在 import 原工程之前（技术约定 §0.2 第 3 条）

import argparse  # noqa: E402
import base64  # noqa: E402
import glob  # noqa: E402
import importlib  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402
import zlib  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))     # 游戏\tools
GAME = os.path.dirname(HERE)                          # 游戏
from source_workspace import WORK as SOURCE_WORK
WORK = str(SOURCE_WORK)
SRC = os.path.join(WORK, "源码")
ATLAS = os.path.join(WORK, "角色图集")
BAKE = os.path.join(WORK, "烘焙脚本")
STORYBOARD = os.path.join(WORK, "剧情分镜")
AUDIO_SRC = os.path.join(WORK, "音频")
PROTECTED = [SRC, ATLAS, BAKE, STORYBOARD, AUDIO_SRC]

ASSETS = os.path.join(GAME, "assets")
META = os.path.join(HERE, "_meta")
DATA = os.path.join(GAME, "data")
REGISTRY = os.path.join(HERE, "registry")
ART_DIR = os.path.join(HERE, "art")

sys.path.insert(0, SRC)
sys.path.insert(1, os.path.join(SRC, "tools"))
if HERE not in sys.path:
    sys.path.insert(2, HERE)
# 不 os.chdir(SRC)：JoJo 源码不需要（报告 03 §7.0）

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

# 发布包的画布尺寸固定；打包已有资源不应要求原动画工程存在。
W, H, UW, UH, FPS = 320, 180, 640, 360, 24


def Frame(*args, **kwargs):
    from engine.core import Frame as SourceFrame
    return SourceFrame(*args, **kwargs)

# ====================================================================== 人物比例（2026-10-11）
# 全游戏人物 / 替身 / 道具统一缩小到 CK 倍（《银魂》主角占画布高 15.7%，JoJo 原来 26%）。
# 缩放在构建时做（art\shrink.py：多数色 + 描边优先，保持像素风），引擎不再运行时缩放。
# 已经按缩小后尺寸画好的图集（art_chibi 画的六个主角）在自己的 json 里写 "k": 0.625，这里就不再缩。
# 环境变量 JOJO_CK 可以临时换系数做对比（1 = 不缩）。
CK = float(os.environ.get("JOJO_CK", "0.625"))
SHRINK_PROP_KEEP = {"card", "coin", "chip", "photo", "photo_crew", "photo_ape_helm", "manga", "tv", "camera",
                    "magazine", "magazine_vest", "tissue"}          # 特写 / 卡片 / 小游戏里用的，不缩
SHRINK_SCENE_CATS = {"prop", "pose", "part", "npc"}                  # 场景专用里只缩“长在世界里”的；fx / portrait / icon 不缩


def _shrink_mod():
    return import_file("art_shrink", os.path.join(ART_DIR, "shrink.py"))


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

STEP_ORDER = ["art", "chars", "props", "bg", "ui", "fx", "font", "audio", "video", "data", "check"]
DEFAULT_STEPS = ["art", "chars", "props", "bg", "ui", "fx", "font", "audio", "data", "check"]

# ====================================================================== 写死的表
# 场景专用里 category == 'portrait' 的全部 17 张 → (cid, emotion)（技术约定 §5.3）
SCENE_PORTRAITS = {
    "s04_kak_evil": ("kakyoin", "evil"),
    "s04_kak_face": ("kakyoin", "faint"),
    "s05_avdol_grave": ("avdol", "grave"),
    "s05_joseph_grave": ("joseph", "grave"),
    "s05_jotaro_talk": ("jotaro", "glare"),
    "s12_telence_shock": ("telence", "shock"),
    "s14_face": ("polnareff", "shock_big"),
    "s15_kak_look": ("kakyoin", "weak"),
    "s15_kak_rest": ("kakyoin", "rest"),
    "s15_kak_smile": ("kakyoin", "weak_smile"),
    "s18_final2_dio_shock": ("dio", "shock"),
    "s18_final2_dio_shock_tall": ("dio", "shock_tall"),
    "s18_final2_dio_smug_tall": ("dio", "smug_tall"),
    "s19_jp_closed": ("joseph", "closed_tall"),
    "s19_jp_evil": ("joseph", "evil_tall"),
    "s19_jp_open": ("joseph", "open_tall"),
    "s20_jotaro_smile": ("jotaro", "smile"),
}

# 规划 §3.2 的体宽（tools\art\amap.py 的 BODYW 有就以它为准）
BODYW_DEFAULT = {"jotaro": 7, "joseph": 7, "avdol": 7, "kakyoin": 6, "polnareff": 6, "iggy": 5}

# tools\art\amap.py 还没有时的兜底：§3.14 A 的 amap（chars 步只留图集里真有的真名，其余交给运行时通用回退）
AMAP_FALLBACK = {
    "jotaro": {"cmd": "point", "cmd2": "point", "cmd_hold": "point", "guard": "guard", "dodge": "dodge",
               "down": "down", "hurt": "hurt", "special": "pose", "win": "pose", "talk": "idle"},
    "starplat": {"punch": "punch", "punch2": "punch", "punch_heavy": "upper", "rush": "rush", "block": "block",
                 "hurt": "hurt", "special": "rush"},
    "kakyoin": {"cmd": "cast", "cmd2": "cast", "cmd_hold": "cast", "special": "cast", "guard": "guard",
                "dodge": "dodge", "hurt": "hurt", "down": "down"},
    "hiero": {"punch": "cast", "punch2": "cast", "rush": "cast", "special": "cast", "punch_heavy": "whip",
              "block": "block", "hurt": "hurt"},
    "avdol": {"cmd": "cast", "cmd2": "cast", "cmd_hold": "cast", "special": "cast", "win": "yes",
              "guard": "guard", "dodge": "dodge", "hurt": "hurt", "down": "down"},
    "magred": {"punch": "punch", "punch2": "punch", "punch_heavy": "cast", "rush": "cast", "special": "cast",
               "block": "block", "hurt": "hurt"},
    "polnareff": {"cmd": "fight", "cmd2": "fight", "down": "down", "hurt": "hurt"},
    "chariot": {"punch": "thrust", "punch2": "thrust", "punch_heavy": "thrust", "rush": "thrust",
                "attack": "thrust", "slash": "slash", "block": "parry", "hurt": "hurt",
                "bare_idle": "bare_idle", "bare_punch": "bare_thrust", "bare_punch2": "bare_thrust",
                "bare_punch_heavy": "bare_thrust", "bare_rush": "bare_thrust", "bare_attack": "bare_thrust",
                "bare_block": "bare_idle"},
    "towergray": {"idle": "fly", "attack": "needle"},
    "joseph": {"cmd": "point", "cmd2": "point", "down": {"a": "lie", "flip": True}},
}

STAND_CIDS = {"chariot", "cream", "darkbluemoon", "death13", "fool", "geb", "hangedman", "hermit", "hiero",
              "highpriestess", "judgement", "justice", "magred", "starplat", "strength", "theworld",
              "towergray", "wheel"}
ANIMAL_CIDS = {"iggy", "petshop"}

# 主角表补充（技术约定 §3.5；打字音 规划 §1.4 第 5 条）
HERO_EXTRA = {
    "jotaro": dict(short="承太郎", stand="starplat", blipHz=440, grunt="grunt_jotaro"),
    "joseph": dict(short="乔瑟夫", stand="hermit", blipHz=520, grunt="grunt_joseph"),
    "avdol": dict(short="阿布德尔", stand="magred", blipHz=400, grunt="grunt_avdol"),
    "kakyoin": dict(short="花京院", stand="hiero", blipHz=560, grunt="grunt_kakyoin"),
    "polnareff": dict(short="波鲁纳雷夫", stand="chariot", blipHz=620, grunt="grunt_polnareff"),
    "iggy": dict(short="伊奇", stand="fool", blipHz=900, grunt=None),
}
SPEAKER_BLIP = {"holly": 800, "dio": 420, "grayfly": 360}

# §3.14 D：背景 key → 包短名、来源（兜底 snap 用）、建议地图宽、可走纵深带（规划 §5.1 / §5.2 地图表、报告 06 §2.1）
BG_SPEC = {
    "title_pyramids": dict(pack="title", fn="pyramids", kw=dict(time="sunrise"), w=320, walk=[148, 178], pri="P0"),
    "world_map": dict(pack="common", fn="world_map", kw={}, w=320, walk=[140, 176], pri="P0"),
    "sky_day": dict(pack="common", fn="sky_day", kw={}, w=320, walk=[140, 176], pri="P0"),
    "sea_day": dict(pack="common", fn="sea_day", kw=dict(island=True), w=320, walk=[140, 176], pri="P0"),
    "jail_cell": dict(pack="prologue", fn="jail_cell", kw={}, w=320, walk=[122, 138], pri="P0"),
    "kujo_house_day": dict(pack="prologue", fn="kujo_house", kw=dict(variant="day"), w=320, walk=[148, 176], pri="P0"),
    "kujo_house_night": dict(pack="prologue", fn="kujo_house", kw=dict(variant="night"), w=320, walk=[148, 176], pri="P0"),
    "kujo_house_morning": dict(pack="prologue", fn="kujo_house", kw=dict(variant="morning"), w=320, walk=[148, 176], pri="P0"),
    "kujo_bedroom_dusk": dict(pack="prologue", fn="kujo_bedroom", kw=dict(variant="dusk"), w=320, walk=[150, 176], pri="P0"),
    "school_gate": dict(pack="prologue", fn="school_gate", kw={}, w=480, walk=[140, 176], pri="P0"),
    "school_infirmary": dict(pack="prologue", fn="kujo_bedroom", kw=dict(variant="day"), w=320, walk=[148, 176],
                             ground=156, pri="P0", stand_in=True),
    "dusk_gate": dict(pack="prologue", fn="@dusk_gate", kw={}, w=460, walk=[146, 172], pri="P0"),
    "tatami_top": dict(pack="prologue", fn="@tatami_top", kw={}, w=320, walk=[140, 176], pri="P0"),
    "plane_cabin_side": dict(pack="ch1", fn="plane_cabin", kw={}, w=640, walk=[156, 166], ground=160, pri="P0",
                             stand_in=True),
    "plane_cabin": dict(pack="ch1", fn="plane_cabin", kw={}, w=320, walk=[150, 170], pri="fallback"),
    "cockpit": dict(pack="ch1", fn="@cockpit", kw={}, w=320, walk=[160, 178], ground=170, pri="P0"),
    "hongkong_night": dict(pack="ch1", fn="hongkong_night", kw={}, w=960, walk=[150, 176], pri="P0"),
    "hk_garden_night": dict(pack="ch1", fn="hk_garden", kw=dict(night=True), w=320, walk=[140, 176], pri="P0"),
}

DEFAULT_PACKS = {
    "title": {"bg": ["title_pyramids"], "music": ["title"]},
    "common": {"bg": ["world_map", "sky_day", "sea_day"], "music": []},
    "prologue": {"bg": ["jail_cell", "kujo_house_day", "kujo_house_night", "kujo_house_morning",
                        "kujo_bedroom_dusk", "school_gate", "school_infirmary", "dusk_gate", "tatami_top"],
                 "music": []},
    "ch1": {"bg": ["plane_cabin_side", "plane_cabin", "cockpit", "hongkong_night", "hk_garden_night"], "music": []},
}

# ---------------------------------------------------------------- §3.14 清单（check 用）
M1_A = {   # cid → (新动作真名, amap 至少要有的逻辑名)
    "jotaro": (["guard", "dodge", "down"],
               ["cmd", "cmd2", "cmd_hold", "guard", "dodge", "down", "hurt", "special", "win", "talk"]),
    "starplat": (["upper", "hurt", "reach"], ["punch", "punch2", "punch_heavy", "rush", "block", "hurt", "special"]),
    "kakyoin": (["guard", "dodge"], ["cmd", "cmd2", "cmd_hold", "special", "guard", "dodge", "hurt", "down"]),
    "hiero": (["whip", "hurt", "block"], ["punch", "punch2", "rush", "special", "punch_heavy", "block", "hurt"]),
    "avdol": (["guard", "dodge"], ["cmd", "cmd2", "cmd_hold", "special", "win", "guard", "dodge", "hurt", "down"]),
    "magred": (["punch", "block", "hurt"], ["punch", "punch2", "punch_heavy", "rush", "special", "block", "hurt"]),
    "polnareff": (["down"], ["cmd", "cmd2", "down", "hurt"]),
    "chariot": (["slash", "parry", "hurt", "bare_idle", "bare_thrust"],
                ["punch", "punch2", "punch_heavy", "rush", "attack", "slash", "block", "hurt", "bare_idle",
                 "bare_punch", "bare_punch2", "bare_punch_heavy", "bare_rush", "bare_attack", "bare_block"]),
    "towergray": (["needle"], ["idle", "attack"]),
    "joseph": ([], ["cmd", "cmd2", "down"]),
}
M1_B = {   # 新 cid → (优先级, 动作, 头像 emotion)
    "grayfly": ("P0", ["idle", "seated", "hurt", "down"], ["normal", "scared"]),
    "npc_nurse": ("P0", ["idle", "walk", "possessed", "stab", "faint"], ["normal", "possessed"]),
    "npc_passenger_a": ("P0", ["seated", "slump"], []),
    "npc_passenger_b": ("P0", ["seated", "slump"], []),
    "npc_passenger_c": ("P0", ["seated", "slump"], []),
    "npc_passenger_d": ("P0", ["seated", "slump"], []),
    "npc_police": ("P1", ["idle", "walk", "read", "shock"], ["normal"]),
    "npc_student_f_a": ("P1", ["idle", "walk", "cheer", "down"], ["normal"]),
    "npc_student_f_b": ("P1", ["idle", "walk", "cheer", "down"], ["normal"]),
    "npc_stewardess": ("P1", ["idle", "walk"], ["normal"]),
    "npc_hk_owner": ("P1", ["idle", "walk"], ["normal"]),
    "npc_hk_granny": ("P1", ["idle", "walk"], ["normal"]),
    "npc_hk_passer_a": ("P1", ["idle", "walk"], []),
    "npc_hk_passer_b": ("P1", ["idle", "walk"], []),
    "npc_fortune": ("P1", ["idle"], ["normal"]),
    "npc_student_m": ("P2", ["idle", "walk", "bow"], ["normal"]),
}
M1_C = {"magazine": "P0", "jail_pipe": "P0", "tissue": "P0", "pen": "P0", "pinky": "P0", "hk_table": "P0",
        "mr_statue": "P0", "chariot_armor": "P0", "dish": "P2", "kite": "P2"}
M1_C_FRAMES = {"jail_pipe": 2, "hk_table": 2, "mr_statue": 3, "chariot_armor": 4, "dish": 3}
M1_PROPS_ORIG = ["camera", "photo", "fleshbud", "coin", "tv", "map_plane", "plane_crash"]
M1_E = {
    "namecards": ["jotaro", "joseph", "avdol", "kakyoin", "holly", "grayfly", "polnareff"],
    "standcards": ["starplat", "hermit", "magred", "hiero", "chariot", "fool", "towergray", "theworld"],
    "locations": ["tokyo", "kujo", "school", "plane", "hongkong", "garden"],
    "chapters": ["prologue", "ch1"],
    "titles": ["stand", "egypt", "day50", "day_unit", "saiki", "draw", "w6_hg_splash"],
    "specials": ["jotaro", "kakyoin", "avdol", "jail_bars", "avdol_sp"],
    "sfx": ["ORA", "ORA!", "ORA!!", "ORA!!!", "オラオラ", "HORA", "ドゴォ", "バキィ", "ズガッ", "キィン！", "ドドド",
            "ガシッ", "ギュルッ", "ズルッ", "メキメキッ", "ギギギ…", "ゴオッ", "ゴオオッ", "シュッ", "シュバッ", "シュバババ",
            "バチバチッ", "バキッ!!", "ジュウウ", "ドクン", "ドサッ", "ギュッ", "ガキッ", "砰！！", "OH MY GOD!",
            "拉起来——！！", "呜哇啊啊啊——！！", "扑通——！！", "嗡嗡嗡——", "YES I AM!", "チッチッ", "呀嘞呀嘞daze",
            "绿宝石水花！", "十字火焰风暴！", "！？", "看穿！", "破绽！", "残像！", "它躲开了！", "被劈开了！", "……没用",
            "咚", "？", "U!"],
    "menace": ["ゴ", "ド"],
    "vs": ["hiero", "towergray", "chariot"],
    "panels": ["tissue_note"],
}
M1_F = ["title", "daily", "travel", "battle", "tension", "sad", "ominous"]
M1_G = ("punch punch_heavy whoosh slash stab thud fire fire_loop fire_burst emerald vine hamon glass_break menacing "
        "menacing4 dododo sting_reveal sting_shock sting_comedy jingle_victory tbc blip blip_train glint sparkle zoom "
        "freeze pop ding heartbeat charge power_up coin footstep door plane_engine wind crowd explosion crash splash "
        "water_gush rumble rero camera_shutter dog_bark clock_tick timestop timestop_sp time_resume knife_throw "
        "knife_hit roar gunshot drain bubbles car_engine sand ora_rush "
        "ora_loop muda_loop rapier_loop timestop_hum heartbeat_loop insect_buzz_loop dodge dodge_perfect guard parry "
        "guard_break crit ko_hit wall_slam skid stand_summon_star stand_summon_hiero stand_summon_red "
        "stand_summon_chariot stand_summon_purple stand_summon_fool stand_summon_world stand_recall meter_tick "
        "meter_full super_start game_over_jingle menu_move menu_confirm menu_cancel menu_error emerald_shot "
        "hiero_tentacle crossfire armor_off "
        "ora_voice muda_voice hora_voice grunt_jotaro grunt_kakyoin grunt_polnareff grunt_avdol grunt_joseph "
        "grunt_enemy grunt_dio").split()
M1_H = ["op", "coffin"]

FONT_EXTRA = "…—「」『』（）！？，。、：；“”‘’·～＋－×÷■□▼▲★☆"

IMG_KEY_RE = re.compile(r"^(chars|heads|props|scene|bg|ui|font|fx)/")


# ====================================================================== 小工具
def safe_seg(seg):
    """key 的一段 → Windows 上能建的文件名（技术约定 §3.2）。"""
    return re.sub(r"[^0-9A-Za-z_.\-]", lambda m: "~%04x" % ord(m.group()), seg)


def jsonable(o):
    """numpy / tuple → JSON 内置类型（背景 info 里有这些）。"""
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        v = float(o)
        return int(v) if v.is_integer() else round(v, 4)
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    if isinstance(o, float):
        return int(o) if o.is_integer() else round(o, 4)
    if isinstance(o, (str, int, bool)) or o is None:
        return o
    return str(o)


def crop_rgba(im):
    """裁到不透明区域，返回 (图, (x0, y0))；全透明返回 (None, (0, 0))。"""
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    bb = im.getchannel("A").getbbox()
    if bb is None:
        return None, (0, 0)
    return im.crop(bb), (bb[0], bb[1])


def matte(draw_fn, w=W, h=H):
    """只会往 RGB 上画的函数 → 准确的 RGBA（黑底 / 白底各画一次反解透明度，银魂 _matte）。
    draw_fn(img) 在给定的 RGBA 图上画（img 不透明）。"""
    blk = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    wht = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw_fn(blk)
    draw_fn(wht)
    b = np.asarray(blk.convert("RGB"), np.float32)
    wv = np.asarray(wht.convert("RGB"), np.float32)
    alpha = 255.0 - np.max(wv - b, axis=2)
    alpha = np.clip(alpha, 0, 255)
    safe = np.maximum(alpha, 1.0)
    rgb = np.clip(b * 255.0 / safe[..., None], 0, 255)
    out = np.dstack([rgb, alpha]).astype(np.uint8)
    out[alpha < 1] = 0
    return Image.fromarray(out, "RGBA")


def strip(frames):
    """N 帧（同尺寸）横向拼成一张帧条。"""
    if not frames:
        return None
    w, h = frames[0].size
    im = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        im.paste(f.convert("RGBA"), (i * w, 0))
    return im


def snap(bgname, t=0.0, **kw):
    """调原背景函数画一帧 → (RGB 图, info)。原函数调用约定：fr = Frame(t, int(t*FPS), 60.0, 'bake')。"""
    from engine import bg
    scroll = kw.pop("scroll", 0.0)
    fr = Frame(t, int(t * FPS), 60.0, "bake")
    info = getattr(bg, bgname)(fr, scroll=scroll, **kw)
    return fr.img.convert("RGB"), jsonable(info or {})


def newest_mtime(paths):
    """一组文件 / 目录（递归）里最新的 mtime；不存在的跳过。"""
    best = 0.0
    for p in paths:
        if not p:
            continue
        if os.path.isfile(p):
            best = max(best, os.path.getmtime(p))
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in ("__pycache__", "_preview")]
                for f in files:
                    try:
                        best = max(best, os.path.getmtime(os.path.join(root, f)))
                    except OSError:
                        pass
                try:
                    best = max(best, os.path.getmtime(root))
                except OSError:
                    pass
    return best


def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return default
    except Exception as e:                      # 坏 JSON：说清楚是哪个文件
        print(f"  !! 读不了 {path}: {e}")
        return default


def import_file(name, path):
    """按路径 import 一个模块（配方模块、amap.py）。失败抛异常。"""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def amap_target(v):
    return v if isinstance(v, str) else (v or {}).get("a")


def protected_snapshot():
    """受保护目录：最新 mtime、文件数、有没有 __pycache__ / out\\（技术约定 §5.12）。"""
    snap_ = {}
    for d in PROTECTED:
        newest, n, bad = 0.0, 0, []
        if os.path.isdir(d):
            for root, dirs, files in os.walk(d):
                for dd in dirs:
                    if dd == "__pycache__" or (dd == "out" and os.path.normcase(root) == os.path.normcase(SRC)):
                        bad.append(os.path.join(root, dd))
                for f in files:
                    n += 1
                    try:
                        newest = max(newest, os.path.getmtime(os.path.join(root, f)))
                    except OSError:
                        pass
        snap_[d] = dict(newest=newest, n=n, bad=bad)
    return snap_


# ====================================================================== 构建状态
class Build:
    """一次构建的上下文：输出目录、图片索引、警告 / 错误。fixture.py 用另一套目录复用同样的步骤。"""

    def __init__(self, assets=ASSETS, meta=META, data=DATA, force=False, skip=(), label="build",
                 registry=REGISTRY, game=GAME):
        self.assets, self.meta, self.data = assets, meta, data
        self.registry, self.game = registry, game
        self.force, self.skip, self.label = force, set(skip), label
        self.img_index = load_json(os.path.join(meta, "img_index.json"), {}) or {}
        self.cur_step = None
        self.warnings, self.errors, self.todo = [], [], []
        self.fallbacks = {}               # 步 → 用了兜底的说明
        self.ran, self.cached_steps, self.failed = [], [], []
        self.fixture_mode = False

    # ---------------------------------------------------------------- 路径
    def out(self, *p):
        path = os.path.join(self.assets, *p)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    def rel(self, path):
        """相对游戏目录、正斜杠（data 里给运行时用的相对路径，例如视频）。"""
        return os.path.relpath(path, self.game).replace("\\", "/")

    def warn(self, msg):
        self.warnings.append((self.cur_step, msg))
        print(f"  ! {msg}")

    def error(self, msg):
        self.errors.append((self.cur_step, msg))
        print(f"  !! {msg}")

    def fallback(self, msg):
        self.fallbacks.setdefault(self.cur_step, []).append(msg)
        print(f"  ~ 兜底：{msg}")

    # ---------------------------------------------------------------- 元数据
    def save_meta(self, name, obj):
        os.makedirs(self.meta, exist_ok=True)
        with open(os.path.join(self.meta, name + ".json"), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, separators=(",", ":"))

    def load_meta(self, name, default=None):
        return load_json(os.path.join(self.meta, name + ".json"), default)

    def save_index(self):
        self.save_meta("img_index", self.img_index)

    # ---------------------------------------------------------------- 图片登记
    def reg_img(self, key, path, pack):
        """登记 key → PNG → 包（data 步只认这个索引）。"""
        relp = os.path.relpath(path, self.assets).replace("\\", "/")
        old = self.img_index.get(key)
        if old and old.get("step") != self.cur_step:
            self.warn(f"图片 key 重复登记：{key}（{old.get('step')} 步已登记，{self.cur_step} 步覆盖）")
        self.img_index[key] = dict(file=relp, pack=pack, step=self.cur_step)
        return key

    def save_png(self, img, key, pack, sub=None):
        """存 PNG（文件名按 §3.2 的安全名规则转，不直接用 key）并登记，返回 key。"""
        segs = key.split("/")
        d = sub if sub else "/".join(segs[:-1])
        parts = [safe_seg(s) for s in d.replace("\\", "/").split("/") if s]
        path = os.path.join(self.assets, *parts, safe_seg(segs[-1]) + ".png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if img.mode not in ("RGBA", "RGB", "L", "P", "LA"):
            img = img.convert("RGBA")
        img.save(path, optimize=True)
        return self.reg_img(key, path, pack)

    def copy_png(self, src, key, pack, dst_parts):
        """原样拷 PNG（不重新压缩）并登记。"""
        dst = self.out(*dst_parts)
        shutil.copyfile(src, dst)
        return self.reg_img(key, dst, pack)

    def drop_step_images(self, step):
        for k in [k for k, e in self.img_index.items() if e.get("step") == step]:
            del self.img_index[k]

    def img_path(self, key):
        e = self.img_index.get(key)
        return os.path.join(self.assets, *e["file"].split("/")) if e else None

    # ---------------------------------------------------------------- 缓存
    def cached(self, step, inputs):
        """输出（_meta\\<步>.json 和这一步登记的 PNG）都在、且比全部输入新 → 跳过。"""
        if self.force:
            return False
        mp = os.path.join(self.meta, step + ".json")
        if not os.path.exists(mp):
            return False
        if newest_mtime(list(inputs) + [os.path.abspath(__file__)]) > os.path.getmtime(mp):
            return False
        for k, e in self.img_index.items():
            if e.get("step") == step and not os.path.exists(self.img_path(k)):
                return False
        self.cached_steps.append(step)
        print("  （缓存：输入没变，跳过）")
        return True

    # ---------------------------------------------------------------- 给配方模块的 c
    def c(self):
        return dict(
            out=self.out, rel=self.rel, reg_img=self.reg_img, save_png=self.save_png, crop_rgba=crop_rgba,
            matte=matte, strip=strip, snap=snap, Frame=Frame, W=W, H=H, UW=UW, UH=UH, FPS=FPS,
            jsonable=jsonable, warn=self.warn, GAME=self.game, SRC=SRC, ATLAS=ATLAS, ASSETS=self.assets,
            META=self.meta, REGISTRY=self.registry, packs=self.packs(), force=self.force,
            out_chars_new=os.path.join(self.assets, "chars_new"),
            out_props_new=os.path.join(self.assets, "props_new"),
            preview_dir=os.path.join(ART_DIR, "_preview"),
        )

    # ---------------------------------------------------------------- 登记表
    def packs(self):
        """packs.json（短名 → {bg, music}）；没有就用 §3.14 D 的默认表。"""
        p = load_json(os.path.join(self.registry, "packs.json"))
        if not isinstance(p, dict) or not p:
            return json.loads(json.dumps(DEFAULT_PACKS))
        return p

    def stands(self):
        """stands.json（包 8）合并在内置 §3.14 E 表之上：登记表有的条目优先。"""
        import ui_jojo
        reg = load_json(os.path.join(self.registry, "stands.json"))
        out = json.loads(json.dumps(ui_jojo.DEFAULT_STANDS))
        if isinstance(reg, dict):
            for k, v in reg.items():
                if isinstance(v, dict):
                    out[k] = dict(out.get(k, {}), **v)
        return out

    def ui_texts(self):
        import ui_jojo
        reg = load_json(os.path.join(self.registry, "ui_texts.json"))
        return ui_jojo.merge_texts(reg if isinstance(reg, dict) else {})


# ====================================================================== art
def step_art(B):
    """包 7A 的 bake_art.run(out_dir, c)：补帧 / 新角色 / 新道具 → assets\\chars_new\\、assets\\props_new\\。"""
    path = os.path.join(ART_DIR, "bake_art.py")
    if not os.path.exists(path):
        B.fallback("tools\\art\\bake_art.py 还没有（包 7A），art 步跳过")
        return
    cwd = os.getcwd()                    # bake_characters.load_registry() 会 chdir（§5.1），这里兜一下
    try:
        mod = import_file("bake_art", path)
        rep = mod.run(os.path.join(B.assets, "chars_new"), B.c())
        print(f"  bake_art.run → {str(rep)[:300]}")
    except Exception:
        B.fallback("bake_art.run 抛错，art 步跳过：\n" + traceback.format_exc(limit=6))
    finally:
        os.chdir(cwd)


# ====================================================================== chars
def load_amap(B):
    path = os.path.join(ART_DIR, "amap.py")
    if not os.path.exists(path):
        B.fallback("tools\\art\\amap.py 还没有（包 7A）：用内置 §3.14 A 的最少 amap")
        return None, {}
    try:
        mod = import_file("jojo_amap", path)
        return dict(getattr(mod, "AMAP", {}) or {}), dict(getattr(mod, "BODYW", {}) or {})
    except Exception:
        B.fallback("amap.py 导入失败，用内置 amap：\n" + traceback.format_exc(limit=4))
        return None, {}


def _idle_bbox(sheet, m):
    """idle 第 0 帧（没有就第一个动作）的不透明 bbox（相对格子）。"""
    anims = m["animations"]
    a = anims.get("idle") or (anims[next(iter(anims))] if anims else None)
    if not a:
        return None
    cw, ch = m["cell"]
    cell = sheet.crop((0, a["row"] * ch, cw, (a["row"] + 1) * ch))
    return cell.getchannel("A").getbbox()


def step_chars(B):
    inputs = [ATLAS, os.path.join(B.assets, "chars_new"), os.path.join(ART_DIR, "amap.py"), os.path.join(ART_DIR, "shrink.py"),
              os.path.join(B.registry, "stands.json"), os.path.join(B.registry, "ui_texts.json"),
              os.path.join(HERE, "ui_jojo.py")]
    if B.cached("chars", inputs):
        return
    B.drop_step_images("chars")
    amap_mod, bodyw_mod = load_amap(B)
    stands = B.stands()

    atlases = {}
    for jp in sorted(glob.glob(os.path.join(ATLAS, "*", "*.json"))):
        m = load_json(jp)
        if not isinstance(m, dict) or "cell" not in m:       # 道具目录 / 场景专用目录没有 cell
            continue
        atlases[m["id"]] = (m, os.path.dirname(jp), "atlas")
    n_orig = len(atlases)
    new_ids = []
    for jp in sorted(glob.glob(os.path.join(B.assets, "chars_new", "*", "*.json"))):
        m = load_json(jp)
        if not isinstance(m, dict) or "cell" not in m:
            continue
        atlases[m["id"]] = (m, os.path.dirname(jp), "new")    # 按 cid 整体覆盖（技术约定 §3.3）
        new_ids.append(m["id"])
    if not new_ids:
        B.fallback("assets\\chars_new\\ 里还没有新图集（包 7A 的 art 步）")

    chars, report = {}, dict(amap_dropped=[], too_big=[], new=new_ids)
    for cid, (m, d, src) in sorted(atlases.items()):
        png = os.path.join(d, m["image"])
        if not os.path.exists(png):
            B.error(f"{cid}: 图集 PNG 不存在 {png}")
            continue
        sheet = Image.open(png).convert("RGBA")
        cell, pivot = list(m["cell"]), list(m["pivot"])
        ck = float(m.get("k") or 1.0)                  # json 里写了 k = 已经画成缩小后的尺寸，不再缩
        if m.get("k") is None and CK != 1.0:
            sheet, cell, pivot = _shrink_mod().shrink_sheet(sheet, cell, pivot, CK)
            ck = CK
            B.save_png(sheet, "chars/" + cid, "core", sub="chars")
        else:
            B.copy_png(png, "chars/" + cid, "core", ["chars", safe_seg(cid) + ".png"])
        if sheet.width > 4096 or sheet.height > 4096:
            report["too_big"].append(cid)
            B.error(f"{cid}: 图集 {sheet.width}×{sheet.height} 超过 4096（银魂坑 A11）")
        anims = {k: dict(row=v["row"], frames=v["frames"], fps=v.get("fps", 6), kind=v.get("kind", "loop"))
                 for k, v in m["animations"].items()}
        aliases = dict(m.get("aliases") or {})
        heads, alias, hsize = {}, {}, {}
        for ex in m.get("expressions", []):
            emo = ex["emotion"]
            keys = []
            for k, f in enumerate(ex.get("files", [])):
                fp = os.path.join(d, f)
                if not os.path.exists(fp):
                    B.warn(f"{cid}: 头像文件不存在 {fp}")
                    continue
                keys.append(B.copy_png(fp, f"heads/{cid}/{emo}_{k}", "core",
                                       ["chars", safe_seg(cid) + "_heads", safe_seg(f"{emo}_{k}") + ".png"]))
            if not keys:
                continue
            if emo in heads:
                B.warn(f"{cid}: 表情 {emo} 重复（{ex['id']}），保留先出现的")
            else:
                heads[emo] = keys
            alias[ex["id"]] = emo
            size = list(ex.get("size") or Image.open(os.path.join(d, ex["files"][0])).size)
            if size != [32, 32]:
                hsize[emo] = size
        chars[cid] = dict(name=m.get("name", cid), image="chars/" + cid, cell=cell,
                          pivot=pivot, animations=anims, aliases=aliases, heads=heads,
                          headAlias=alias, headSize=hsize, k=round(ck, 4), _sheet=sheet, _src=src)

    # 场景专用的 17 张说话头像并进来（§5.3）
    scat = load_json(os.path.join(ATLAS, "场景专用", "场景专用目录.json"), {}) or {}
    seen = set()
    for s in scat.get("sprites", []):
        if s.get("category") != "portrait":
            continue
        seen.add(s["id"])
        if s["id"] not in SCENE_PORTRAITS:
            B.warn(f"场景专用头像 {s['id']} 不在映射表里（技术约定 §5.3 要补）")
            continue
        cid, emo = SCENE_PORTRAITS[s["id"]]
        if cid not in chars:
            B.warn(f"场景专用头像 {s['id']} 的角色 {cid} 没有图集")
            continue
        im = Image.open(os.path.join(ATLAS, "场景专用", s["file"])).convert("RGBA")
        w, h = s["size"]
        keys = []
        for k in range(int(s.get("frames", 1))):
            fr_ = im.crop((k * w, 0, (k + 1) * w, h))
            keys.append(B.save_png(fr_, f"heads/{cid}/{emo}_{k}", "core", sub=f"chars/{cid}_heads"))
        ch = chars[cid]
        if emo in ch["heads"]:
            B.warn(f"{cid}: 场景头像 {s['id']} 的表情 {emo} 和图集重名，保留图集的")
        else:
            ch["heads"][emo] = keys
        ch["headAlias"][s["id"]] = emo
        if [w, h] != [32, 32]:
            ch["headSize"][emo] = [w, h]
    missing_sp = set(SCENE_PORTRAITS) - seen
    if missing_sp:
        B.warn(f"映射表里这些场景头像在目录里没找到：{sorted(missing_sp)}")

    # amap / top / bodyW / kind
    amap_src = amap_mod if amap_mod is not None else AMAP_FALLBACK
    bodyw_src = dict(BODYW_DEFAULT, **bodyw_mod)
    stand_ids = set(stands) | STAND_CIDS
    for cid, ch in chars.items():
        names = set(ch["animations"]) | set(ch["aliases"])
        am = {}
        for lg, v in (amap_src.get(cid) or {}).items():
            tgt = amap_target(v)
            if tgt in names:
                am[lg] = v
            else:
                report["amap_dropped"].append(f"{cid}.{lg} → {tgt}")
        ch["amap"] = am
        bb = _idle_bbox(ch["_sheet"], {"animations": ch["animations"], "cell": ch["cell"]})
        if bb:
            ch["top"] = int(ch["pivot"][1] - bb[1])
            wpx = bb[2] - bb[0]
        else:
            ch["top"], wpx = int(ch["cell"][1]), 10
        if cid in bodyw_src:        # 表里写的是原尺寸的判定体宽，跟着图一起缩
            ch["bodyW"] = max(3, int(round(bodyw_src[cid] * ch.get("k", 1.0))))
        else:
            ch["bodyW"] = max(3, int(round(wpx * 0.3)))
        ch["kind"] = "stand" if cid in stand_ids else ("animal" if cid in ANIMAL_CIDS else "char")
        del ch["_sheet"]
        del ch["_src"]
    if report["amap_dropped"]:
        msg = (f"amap 里 {len(report['amap_dropped'])} 条指向图集里没有的真名，已从运行时数据里去掉"
               f"（等包 7A 的新帧烘出来再出现）：{', '.join(report['amap_dropped'][:12])}"
               + (" …" if len(report["amap_dropped"]) > 12 else ""))
        if amap_mod is None:
            print("  （内置兜底 amap）" + msg)
        else:
            B.warn(msg)

    # 主角表 / 说话人（§3.5）
    heroes, speakers = {}, {}
    try:
        from scenes import s00_opening as S0
        from engine import text as TX
        for card in S0.CARDS:
            cid = card["hero"].split(".")[0]
            ex = HERO_EXTRA.get(cid, {})
            heroes[cid] = dict(cid=cid, cn=card["cn"], short=ex.get("short", card["cn"]), rn=card["rn"],
                               stand=ex.get("stand"), burst=list(card["burst"]), panel=card["panel"],
                               accent=card["accent"], nameColor=TX.SPEAKERS.get(cid, ("", "#555566"))[1],
                               blipHz=ex.get("blipHz", 600), grunt=ex.get("grunt"))
        for k, (nm, col, _p) in TX.SPEAKERS.items():
            if k in heroes or k == "narrator":
                continue
            speakers[k] = dict(short=nm, nameColor=col, blipHz=SPEAKER_BLIP.get(k, 600))
    except Exception:
        B.error("主角表（s00_opening.CARDS / text.SPEAKERS）读取失败：\n" + traceback.format_exc(limit=4))
    # 有名牌、但 text.SPEAKERS 里没有的说话人（格雷·弗莱等）：名字取名牌、名字色取名牌强调色
    try:
        for k, e in (B.ui_texts().get("namecards") or {}).items():
            if k in heroes or k in speakers or not isinstance(e, dict) or not e.get("cn"):
                continue
            speakers[k] = dict(short=e.get("short") or e["cn"], nameColor=e.get("accent", "#555566"),
                               blipHz=SPEAKER_BLIP.get(k, 600))
    except Exception:
        B.warn("从名牌补说话人失败：\n" + traceback.format_exc(limit=3))

    # 替身表：fist 按图集算
    for sid, st in stands.items():
        if "fist" not in st or st.get("fist") is None:
            st["fist"] = bool(sid in chars and "fist" in chars[sid]["animations"])

    B.save_meta("chars_report", report)
    B.save_meta("chars", dict(chars=chars, heroes=heroes, speakers=speakers, stands=stands, ck=CK))
    print(f"  chars: {len(chars)} 个图集（原 {n_orig}，新 / 覆盖 {len(new_ids)}），"
          f"头像 {sum(len(c['heads']) for c in chars.values())} 种表情，heroes {len(heroes)}，stands {len(stands)}")


# ====================================================================== props
def _shrink_ok(pid, size, scene_cat=None):
    """道具 / 场景小图要不要跟着人物缩：太小的（缩了就糊成点）和特写 / 卡片里用的不缩。"""
    if CK == 1.0 or pid in SHRINK_PROP_KEEP or pid.startswith("map_"):
        return False
    if scene_cat is not None and scene_cat not in SHRINK_SCENE_CATS:
        return False
    return size[1] >= 10 or size[0] >= 24


def _put_strip(B, src_png, key, sub, size, pivot, frames, do_shrink):
    """存一条横向帧条（道具 / 场景小图）；do_shrink 时按 CK 缩。返回 (size, pivot, k)。"""
    if do_shrink:
        strip = Image.open(src_png).convert("RGBA")
        new, nsize, npiv = _shrink_mod().shrink_strip(strip, size, pivot, int(frames), CK)
        B.save_png(new, key, "core", sub=sub)
        return nsize, npiv, CK
    B.copy_png(src_png, key, "core", sub.split("/") + [safe_seg(key.split("/")[-1]) + ".png"])
    return list(size), list(pivot), 1.0


def step_props(B):
    pnew = os.path.join(B.assets, "props_new")
    inputs = [os.path.join(ATLAS, "道具"), os.path.join(ATLAS, "场景专用"), pnew, os.path.join(ART_DIR, "shrink.py")]
    if B.cached("props", inputs):
        return
    B.drop_step_images("props")
    props, scene = {}, {}
    cat = load_json(os.path.join(ATLAS, "道具", "道具目录.json"), {}) or {}
    for s in cat.get("sprites", []):
        key = "props/" + s["id"]
        sz, pv, k = _put_strip(B, os.path.join(ATLAS, "道具", s["file"]), key, "props", s["size"], s["pivot"],
                               s["frames"], _shrink_ok(s["id"], s["size"]))
        props[s["id"]] = dict(image=key, frames=s["frames"], size=sz, pivot=pv,
                              fps=s.get("fps", 0), kind=s.get("kind", "static"), k=k)
    orig = set(props)
    nj = os.path.join(pnew, "props_new.json")
    pn = load_json(nj)
    if pn is None:
        B.fallback("assets\\props_new\\props_new.json 还没有（包 7A 的新道具）")
    else:
        for s in pn.get("props", []):
            pid = s["id"]
            if pid in orig:
                B.error(f"新道具 {pid} 和原 35 个道具重名（技术约定 §3.4 禁止）")
                continue
            fp = os.path.join(pnew, s.get("file") or (pid + ".png"))
            if not os.path.exists(fp):
                B.error(f"新道具 {pid} 的图不存在：{fp}")
                continue
            key = "props/" + pid
            piv0 = list(s.get("pivot", [s["size"][0] // 2, s["size"][1]]))
            # 新道具 json 里自己写了 "k" = 已经按缩小后的尺寸画好
            sz, pv, k = _put_strip(B, fp, key, "props", s["size"], piv0, s.get("frames", 1),
                                   s.get("k") is None and _shrink_ok(pid, s["size"]))
            props[pid] = dict(image=key, frames=s.get("frames", 1), size=sz, pivot=pv,
                              fps=s.get("fps", 0), kind=s.get("kind", "static"), isNew=True,
                              k=k if s.get("k") is None else float(s["k"]))
            for extra in ("type", "hp", "anchor"):
                if extra in s:
                    props[pid][extra] = s[extra]
            if "anchor" in s and k != 1.0 and s.get("k") is None:      # 锚点是原图像素，跟着缩
                props[pid]["anchor"] = [int(round(v * k)) for v in s["anchor"]]
    scat = load_json(os.path.join(ATLAS, "场景专用", "场景专用目录.json"), {}) or {}
    for s in scat.get("sprites", []):
        key = "scene/" + s["id"]
        # 游戏层替换图：assets\props_new\scene\<同名文件> 存在就用它（tools\art 生成，原图只读不动；二乔场景特写换新脸，2026-10-10）
        src_png = os.path.join(pnew, "scene", s["file"])
        if not os.path.exists(src_png):
            src_png = os.path.join(ATLAS, "场景专用", s["file"])
        sz, pv, k = _put_strip(B, src_png, key, "props/scene", s["size"], s["pivot"], s["frames"],
                               _shrink_ok(s["id"], s["size"], s.get("category")))
        scene[s["id"]] = dict(image=key, frames=s["frames"], size=sz, pivot=pv,
                              fps=s.get("fps", 0), kind=s.get("kind", "static"), character=s.get("character"),
                              category=s.get("category"), scene=s.get("scene"), k=k)
    B.save_meta("props", dict(props=props, scene=scene))
    print(f"  props: 原 {len(orig)} + 新 {len(props) - len(orig)}；scene {len(scene)}")


# ====================================================================== bg
def _bg_fallback_image(key, spec):
    """§3.14 D 的兜底快照：原函数 t=0 一帧；新画 / 场景自绘的用最接近的现成函数。"""
    fn = spec["fn"]
    if fn == "@dusk_gate":
        try:
            import assets as _A
            _A.load_all()
            from scenes import s05_holly
            fr = Frame(0.0, 0, 60.0, "bake")
            info = s05_holly.dusk_gate(fr, 0.0)
            return fr.img.convert("RGB"), jsonable(info or {}), "s05_holly.dusk_gate(scroll 0)"
        except Exception:
            im, info = snap("school_gate")
            return im, info, "school_gate（dusk_gate 自绘函数调用失败）"
    if fn == "@cockpit":
        try:
            import assets as _A
            _A.load_all()
            from scenes import s06_plane
            fr = Frame(0.0, 0, 60.0, "bake")
            fr.img.paste(s06_plane._cockpit_bg(), (0, 0))
            s06_plane._ws_view(fr, 0.0, 0, 64)
            return fr.img.convert("RGB"), {"ground": 170}, "s06_plane._cockpit_bg + _ws_view(t 0)"
        except Exception:
            im, info = snap("plane_cabin")
            return im, info, "plane_cabin（驾驶舱自绘函数调用失败）"
    if fn == "@tatami_top":
        try:
            from engine import bg_asia
            im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
            d = ImageDraw.Draw(im)
            bg_asia._tatami(d, im, 0, H, [[40, 120, 200, 280], [80, 160, 240]], seed=1)
            a = np.asarray(im.convert("RGB"), np.float32)
            yy, xx = np.mgrid[0:H, 0:W]
            r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
            a *= (1 - 0.5 * np.clip(r - 0.35, 0, 1))[..., None]
            return Image.fromarray(a.astype(np.uint8), "RGB"), {"ground": 150}, "bg_asia._tatami 俯视 + 暗角"
        except Exception:
            im, info = snap("kujo_house", variant="day")
            return im, info, "kujo_house(day)（_tatami 调用失败）"
    im, info = snap(fn, **dict(spec.get("kw") or {}))
    how = f"{fn}({', '.join(f'{k}={v!r}' for k, v in (spec.get('kw') or {}).items())})"
    if spec.get("stand_in"):
        how += " 顶替（新画背景还没有）"
    return im, info, how


def bg_fallback_stage(B, key, pack):
    spec = BG_SPEC[key]
    im, info, how = _bg_fallback_image(key, spec)
    k = B.save_png(im, f"bg/{key}/base", pack)
    ground = int(spec.get("ground") or info.get("ground") or 150)
    anchors = {a: v for a, v in info.items() if a != "ground"}
    return dict(pack=pack, w=spec["w"], ground=ground, walk=list(spec["walk"]), anchors=anchors,
                layers=[dict(type="static", image=k)], fg=[]), how


def _img_refs(o):
    if isinstance(o, str):
        return [o] if IMG_KEY_RE.match(o) else []
    if isinstance(o, dict):
        return [r for v in o.values() for r in _img_refs(v)]
    if isinstance(o, (list, tuple)):
        return [r for v in o for r in _img_refs(v)]
    return []


def _salvage_stages(B, stages):
    """bg_jojo.build_all 中途抛错时：只留“有图层、引用的图全都登记了”的背景，其余（含半截的）丢掉，
    这一步登记的、没被留下的背景引用的图也一并去掉；丢掉的 key 后面由兜底快照补。"""
    keep = {}
    for key, st in list(stages.items()):
        refs = _img_refs(st) if isinstance(st, dict) else []
        if isinstance(st, dict) and st.get("layers") and refs and all(r in B.img_index for r in refs):
            keep[key] = st
    used = {r for st in keep.values() for r in _img_refs(st)}
    for k in [k for k, e in B.img_index.items() if e.get("step") == "bg" and k not in used]:
        del B.img_index[k]
    return keep


def step_bg(B):
    inputs = [os.path.join(HERE, "bg_jojo.py"), os.path.join(HERE, "bg_new"), os.path.join(B.registry, "packs.json"),
              os.path.join(SRC, "engine", "bg_asia.py"), os.path.join(SRC, "engine", "bg_egypt.py")]
    if B.cached("bg", inputs):
        return
    B.drop_step_images("bg")
    packs = B.packs()
    key_pack = {}
    for short, p in packs.items():
        for k in p.get("bg", []):
            key_pack[k] = short
    stages, report = {}, dict(fallback={}, recipe=None)
    path = os.path.join(HERE, "bg_jojo.py")
    if os.path.exists(path):
        cwd = os.getcwd()
        try:
            mod = import_file("bg_jojo", path)
            mod.build_all(stages, B.c())
            report["recipe"] = "bg_jojo.build_all"
        except Exception:
            tb = traceback.format_exc(limit=6)
            stages = _salvage_stages(B, stages)
            report["recipe"] = "bg_jojo.build_all（中途抛错，保留了完整导出的部分）" if stages else None
            report["recipe_error"] = tb.strip().splitlines()[-1]
            B.fallback(f"bg_jojo.build_all 抛错：保留已经完整导出的 {len(stages)} 个"
                       f"（{', '.join(sorted(stages)) or '无'}），其余用兜底快照：\n" + tb)
        finally:
            os.chdir(cwd)
    else:
        B.fallback("tools\\bg_jojo.py 还没有（包 7B）：§3.14 D 每个 key 用 snap(name, t=0) 出一张 static")
    for key, st in stages.items():
        if not st.get("pack"):
            st["pack"] = key_pack.get(key) or BG_SPEC.get(key, {}).get("pack") or "common"
            if key not in key_pack:
                B.warn(f"背景 {key} 没在 packs.json 登记，归进 {st['pack']}")
    want = list(BG_SPEC)
    for short, p in packs.items():
        want += [k for k in p.get("bg", []) if k not in want]
    for key in want:
        if key in stages:
            continue
        if key not in BG_SPEC:
            B.error(f"packs.json 里的背景 {key} 没有导出，兜底表里也没有它")
            continue
        pack = key_pack.get(key) or BG_SPEC[key]["pack"]
        try:
            stages[key], how = bg_fallback_stage(B, key, pack)
            report["fallback"][key] = how
        except Exception:
            B.error(f"背景 {key} 兜底快照失败：\n" + traceback.format_exc(limit=4))
    if report["fallback"] and report["recipe"]:
        B.fallback(f"bg_jojo 没导出这些 key，用兜底快照补上：{sorted(report['fallback'])}")
    B.save_meta("bg_report", report)
    B.save_meta("bg", jsonable(stages))
    print(f"  bg: {len(stages)} 张（配方 {len(stages) - len(report['fallback'])}，兜底快照 {len(report['fallback'])}）")


# ====================================================================== ui
def step_ui(B):
    inputs = [os.path.join(HERE, "ui_jojo.py"), os.path.join(B.registry, "ui_texts.json"),
              os.path.join(B.registry, "stands.json"), os.path.join(SRC, "engine", "text.py"),
              os.path.join(SRC, "engine", "fx.py"), os.path.join(SRC, "scenes", "s00_opening.py")]
    if B.cached("ui", inputs):
        return
    B.drop_step_images("ui")
    import ui_jojo
    if not os.path.exists(os.path.join(B.registry, "ui_texts.json")):
        B.fallback("tools\\registry\\ui_texts.json 还没有（包 8）：用 ui_jojo.py 内置的 M1 最少条目")
    if not os.path.exists(os.path.join(B.registry, "stands.json")):
        B.fallback("tools\\registry\\stands.json 还没有（包 8）：替身卡用内置 §3.14 E 表")
    meta = ui_jojo.build(B.c(), B.ui_texts(), B.stands())
    B.save_meta("ui", meta)
    n = sum(1 for e in B.img_index.values() if e.get("step") == "ui")
    print(f"  ui: {n} 张预渲染图")


# ====================================================================== fx
def step_fx(B):
    inputs = [os.path.join(HERE, "fx_tex.py"), os.path.join(SRC, "engine", "fx.py")]
    if B.cached("fx", inputs):
        return
    B.drop_step_images("fx")
    import fx_tex
    meta = fx_tex.build(B.c())
    B.save_meta("fxtex", meta)
    B.save_meta("fx", {"ok": True})
    print(f"  fx: noise ×{len(meta['noise'])}，ankh ×{len(meta['ankh'])}")


# ====================================================================== font
def _strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield str(k)
            yield from _strings(v)
    elif isinstance(o, (list, tuple)):
        for v in o:
            yield from _strings(v)


def strip_js_comments(txt):
    """去掉 JS 的 // 和 /* */ 注释（认得 '…' "…" `…` 字符串；正则字面量不认——正则里写了 // 的那一行后半截会被当注释，
    台词不会写在那种行上，可以接受）。
    注释里的说明文字（− ≤ ⟵ 之类）不会画到屏幕上，不进字库、不算缺字（偏离 §5.8“所有码点 > 127 的字符”，见交付说明）。"""
    out, i, n = [], 0, len(txt)
    while i < n:
        ch = txt[i]
        if ch in "'\"`":
            j = i + 1
            while j < n and txt[j] != ch:
                if txt[j] == "\\":
                    j += 1
                elif ch != "`" and txt[j] == "\n":      # 普通字符串不跨行：坏引号就此打住
                    break
                j += 1
            out.append(txt[i:j + 1])
            i = j + 1
        elif txt.startswith("//", i):
            j = txt.find("\n", i)
            i = n if j < 0 else j
        elif txt.startswith("/*", i):
            j = txt.find("*/", i + 2)
            i = n if j < 0 else j + 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def collect_font_chars(B, extra_text=""):
    """字库收字（技术约定 §5.8）→ {字: 出处}。JS 文件先去掉注释再收（strip_js_comments）。"""
    src = {}

    def add(s, where):
        for ch in s:
            if ch not in src:
                src[ch] = where

    for pat in ("story/*.js", "engine/*.js", "main.js"):
        for f in sorted(glob.glob(os.path.join(B.game, pat))):
            try:
                txt = strip_js_comments(open(f, encoding="utf-8").read())
            except Exception as e:
                B.warn(f"读不了 {f}: {e}")
                continue
            add("".join(ch for ch in txt if ord(ch) > 127), os.path.relpath(f, B.game))
    for f in sorted(glob.glob(os.path.join(B.registry, "*.json"))):
        add("".join(_strings(load_json(f, {}))), os.path.relpath(f, B.game))
    cm = B.load_meta("chars", {}) or {}
    for cid, ch in (cm.get("chars") or {}).items():
        add(ch.get("name", ""), "chars[*].name")
    for k, h in (cm.get("heroes") or {}).items():
        add(h.get("cn", "") + h.get("short", ""), "heroes")
    for k, s in (cm.get("speakers") or {}).items():
        add(s.get("short", ""), "speakers")
    for k, s in (cm.get("stands") or {}).items():
        add(s.get("cn", ""), "stands")
    import ui_jojo
    add("".join(_strings(ui_jojo.DEFAULT_UI_TEXTS)), "ui_jojo 内置登记表")
    add("".join(chr(i) for i in range(32, 127)), "ASCII")
    add(FONT_EXTRA, "标点表")
    add("\u3000", "全角空格")
    if extra_text:
        add(extra_text, "extra")
    return src


def build_font_atlas(B, chars, fixture_skip_missing=False):
    from fontTools.ttLib import TTCollection
    path = "C:/Windows/Fonts/simsun.ttc"
    cmap = TTCollection(path).fonts[0].getBestCmap()
    missing = {ch: w for ch, w in chars.items()
               if not ch.isspace() and ch != "\u3000" and ord(ch) not in cmap}
    glyph_chars = sorted(ch for ch in chars if ch not in "\n\r\t" and (ch not in missing)
                         and (ch.isprintable() or ch == "\u3000"))
    meta = {}
    for size in (12, 16):
        f = ImageFont.truetype(path, size)
        asc, desc = f.getmetrics()
        lh = asc + desc
        cols, cell = 64, size + 1
        rows = (len(glyph_chars) + cols - 1) // cols
        atlas = Image.new("RGBA", (cols * cell, max(1, rows) * (lh + 1)), (0, 0, 0, 0))
        d = ImageDraw.Draw(atlas)
        d.fontmode = "1"
        glyphs = {}
        for i, ch in enumerate(glyph_chars):
            r, c = divmod(i, cols)
            x, y = c * cell, r * (lh + 1)
            adv = int(round(f.getlength(ch))) or size // 2
            d.text((x, y + asc), ch, font=f, fill=(255, 255, 255, 255), anchor="ls")
            glyphs[ch] = [x, y, adv]
        if atlas.height > 4096:
            B.error(f"字库 {size}px 图集高 {atlas.height} 超过 4096")
        key = B.save_png(atlas, f"font/simsun{size}", "core", sub="font")
        meta[str(size)] = dict(image=key, lh=lh, asc=asc, glyphs=glyphs)
    return meta, missing, len(glyph_chars)


def step_font(B):
    inputs = [os.path.join(B.game, "story"), os.path.join(B.game, "engine"), os.path.join(B.game, "main.js"),
              B.registry, os.path.join(B.meta, "chars.json"), os.path.join(HERE, "ui_jojo.py")]
    if B.cached("font", inputs):
        return
    B.drop_step_images("font")
    chars = collect_font_chars(B)
    meta, missing, n = build_font_atlas(B, chars)
    if missing:
        lines = [f"    {ch!r} U+{ord(ch):04X}  出处 {w}" for ch, w in sorted(missing.items())]
        B.error(f"字库缺字 {len(missing)} 个（simsun 没有；台词 / UI 字符串里不许出现，§3.8）：\n" + "\n".join(lines))
    B.save_meta("font", meta)
    B.save_meta("font_report", dict(n=n, missing={ch: w for ch, w in missing.items()}))
    print(f"  font: {n} 字 × 2 档（12 / 16 px）" + (f"，缺字 {len(missing)}" if missing else ""))


# ====================================================================== audio
def step_audio(B):
    path = os.path.join(HERE, "build_audio.py")
    if not os.path.exists(path):
        B.fallback("tools\\build_audio.py 还没有（包 1）：audio 步跳过" +
                   ("" if os.path.exists(os.path.join(B.meta, "audio.json")) else "（也没有 _meta\\audio.json）"))
        return
    cwd = os.getcwd()
    try:
        mod = import_file("build_audio", path)
        args = ["--force"] if B.force else []
        mod.run(args, B.c())
    except Exception:
        B.fallback("build_audio.run 抛错，audio 步跳过：\n" + traceback.format_exc(limit=6))
    finally:
        os.chdir(cwd)


# ====================================================================== video
VIDEO_JOBS = [("op", "s00"), ("coffin", "s01")]       # ending（s20）终章里程碑再加


def step_video(B):
    out_dir = os.path.join(B.assets, "video")
    os.makedirs(out_dir, exist_ok=True)
    rc = os.path.join(HERE, "render_cutscene.py")
    meta = B.load_meta("video", {}) or {}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    for name, scene in VIDEO_JOBS:
        mp4, webm = os.path.join(out_dir, name + ".mp4"), os.path.join(out_dir, name + ".webm")
        # 2026-10-10：片头换上游戏重画的角色（tools/cutscene_sprites.py 读 tools/art），角色美术改了也要重渲
        src_mt = newest_mtime([rc, os.path.join(SRC, "scenes"), os.path.join(SRC, "engine"), os.path.join(SRC, "assets"),
                               os.path.join(HERE, "cutscene_sprites.py"), os.path.join(HERE, "art")])
        if (not B.force and os.path.exists(mp4) and os.path.exists(webm)
                and min(os.path.getmtime(mp4), os.path.getmtime(webm)) > src_mt):
            print(f"  {name}: 已是最新，跳过")
        else:
            cmd = [sys.executable, "-B", rc, "--scenes", scene, "--out", out_dir, "--name", name, "--scale", "2"]
            print("  $ " + " ".join(cmd[1:]))
            r = subprocess.run(cmd, env=env)
            if r.returncode:
                B.error(f"视频 {name} 渲染失败（返回 {r.returncode}）")
                continue
        if os.path.exists(mp4):
            dur = probe_duration(mp4)                 # mp4 的容器时长是准的（webm 的 Opus 预滚会多出约 10 ms）
            meta[name] = dict(src=f"assets/video/{name}.mp4", duration=dur)
            if os.path.exists(webm):
                meta[name]["webm"] = f"assets/video/{name}.webm"
            print(f"  {name}: {dur:.2f} s，mp4 {os.path.getsize(mp4) / 1e6:.2f} MB" +
                  (f"，webm {os.path.getsize(webm) / 1e6:.2f} MB" if os.path.exists(webm) else ""))
    meta = {k: v for k, v in meta.items() if os.path.exists(os.path.join(B.assets, "video", k + ".mp4"))}
    B.save_meta("video", meta)


def probe_duration(path):
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                            "default=nk=1:nw=1", path], capture_output=True, text=True)
        return round(float(r.stdout.strip()), 3)
    except Exception:
        return 0.0


# ====================================================================== data
def runtime_pack(short):
    return "core" if short == "core" else "bg_" + short


def assemble(B, data_dir, file_prefix="data/", packs_override=None, extra_meta=None, write=True,
             alias_packs=None):
    """把 _meta 合成运行时文件。返回 (GAME_DATA dict, {文件名: 字节数})。
    alias_packs：{实际文件包名: [这个文件同时充当的包名…]}（fixture 用一个背景文件顶全部背景包）。"""
    cm = B.load_meta("chars", {}) or {}
    pm = B.load_meta("props", {}) or {}
    bgm = B.load_meta("bg", {}) or {}
    packs_reg = packs_override if packs_override is not None else B.packs()
    gd = dict(v=1, built=time.strftime("%Y-%m-%dT%H:%M:%S"), img={}, packsLoaded={}, packKeys={})
    # 图片分包：背景图片跟着 bg.<key>.pack 走（防止配方模块 save_png 时给错包名）
    groups = {}
    for key, e in sorted(B.img_index.items()):
        pack = e.get("pack") or "core"
        if key.startswith("bg/"):
            bk = key.split("/")[1]
            if bk in bgm and bgm[bk].get("pack"):
                pack = bgm[bk]["pack"]
        rp = runtime_pack(pack)
        groups.setdefault(rp, []).append(key)
    shorts = set(packs_reg) | {st.get("pack") for st in bgm.values() if st.get("pack")}
    packs = {"core": {"file": file_prefix + "img_core.js"}}
    for short in sorted(s for s in shorts if s and s != "core"):
        p = dict(file=f"{file_prefix}img_bg_{short}.js",
                 bg=sorted([k for k, st in bgm.items() if st.get("pack") == short]))
        if isinstance(packs_reg.get(short), dict) and packs_reg[short].get("music") is not None:
            p["music"] = list(packs_reg[short]["music"])
        packs["bg_" + short] = p
        groups.setdefault("bg_" + short, [])
    gd["packs"] = packs
    gd["ck"] = cm.get("ck", 1.0)          # 人物缩小系数（引擎里要按它调的几处常数：血条高度、招式前伸距离……）
    gd["chars"] = cm.get("chars", {})
    gd["heroes"] = cm.get("heroes", {})
    gd["speakers"] = cm.get("speakers", {})
    gd["stands"] = cm.get("stands", {})
    gd["props"] = pm.get("props", {})
    gd["scene"] = pm.get("scene", {})
    gd["bg"] = bgm
    gd["ui"] = B.load_meta("ui", {}) or {}
    gd["font"] = B.load_meta("font", {}) or {}
    gd["fxtex"] = B.load_meta("fxtex", {}) or {}
    gd["audio"] = B.load_meta("audio", {"music": {}, "sfx": {}}) or {"music": {}, "sfx": {}}
    # 用户音频可被主动移除，元数据不能继续要求加载不存在的文件。
    title_song = gd["audio"].get("music", {}).get("title_song")
    if title_song and not os.path.isfile(os.path.join(B.game, title_song["file"])):
        del gd["audio"]["music"]["title_song"]
    if "bg_title" in gd["packs"]:
        gd["packs"]["bg_title"]["music"] = ["title_song" if "title_song" in gd["audio"].get("music", {}) else "title"]
    gd["video"] = B.load_meta("video", {}) or {}
    if extra_meta:
        gd.update(extra_meta)
    sizes = {}
    if write:
        os.makedirs(data_dir, exist_ok=True)
        js = "window.GAME_DATA = " + json.dumps(gd, ensure_ascii=False, separators=(",", ":")) + ";\n"
        write_text(os.path.join(data_dir, "data_meta.js"), js)
        sizes["data_meta.js"] = len(js.encode("utf-8"))
        for rp, keys in sorted(groups.items()):
            fname = "img_core.js" if rp == "core" else f"img_{rp}.js"
            if packs_override is not None and rp not in packs:
                continue
            parts = []
            for key in keys:
                fp = B.img_path(key)
                if not fp or not os.path.exists(fp):
                    B.error(f"图片文件不见了：{key} → {fp}")
                    continue
                with open(fp, "rb") as fh:
                    b64 = base64.b64encode(fh.read()).decode("ascii")
                parts.append(json.dumps(key, ensure_ascii=False) + ':"data:image/png;base64,' + b64 + '"')
            names = [rp] + list((alias_packs or {}).get(rp, []))
            tail = "".join(f"D.packKeys[{json.dumps(n)}]={json.dumps(keys, ensure_ascii=False)};"
                           f"D.packsLoaded[{json.dumps(n)}]=true;" for n in names)
            js = ("(function(){var D=window.GAME_DATA;Object.assign(D.img,{" + ",".join(parts) + "});"
                  + tail + "})();\n")
            write_text(os.path.join(data_dir, fname), js)
            sizes[fname] = len(js.encode("utf-8"))
    return gd, sizes


def write_text(path, s):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(s)
    os.replace(tmp, path)


def step_data(B):
    metas = [os.path.join(B.meta, n + ".json") for n in
             ("chars", "props", "bg", "ui", "font", "fxtex", "audio", "video", "img_index")]
    out = os.path.join(B.data, "data_meta.js")
    files = [B.img_path(k) for k in B.img_index]
    if (not B.force and os.path.exists(out) and os.path.exists(os.path.join(B.data, "img_core.js"))
            and newest_mtime(metas + files + [os.path.join(B.registry, "packs.json"), os.path.abspath(__file__)])
            <= os.path.getmtime(out)):
        B.cached_steps.append("data")
        print("  （缓存：输入没变，跳过）")
        sizes = {os.path.basename(f): os.path.getsize(f) for f in glob.glob(os.path.join(B.data, "*.js"))}
    else:
        _gd, sizes = assemble(B, B.data)
    tot = 0
    for f, n in sorted(sizes.items()):
        tot += n
        print(f"  {f:28s} {n / 1e6:7.2f} MB")
        if f == "img_core.js" and n > 12e6:
            B.warn(f"img_core.js {n / 1e6:.1f} MB > 12 MB（手机加载慢）")
        if f.startswith("img_bg_") and n > 8e6:
            B.warn(f"{f} {n / 1e6:.1f} MB > 8 MB（手机加载慢）")
    print(f"  合计 {tot / 1e6:.2f} MB")


# ====================================================================== check
def step_check(B, snap0):
    errs, todo = [], []

    def bad(msg, skipped_by=None, pri="P0"):
        if skipped_by and skipped_by in B.skip:
            todo.append(f"[{pri}，{skipped_by} 步本轮跳过] {msg}")
        elif pri in ("P1", "P2", "fallback"):
            todo.append(f"[{pri}] {msg}")
        else:
            errs.append(msg)

    # 1. 受保护目录
    snap1 = protected_snapshot()
    for d in PROTECTED:
        a, b = snap0.get(d, {}), snap1.get(d, {})
        if b.get("bad"):
            errs.append(f"受保护目录出现了 __pycache__ / out：{b['bad'][:5]}")
        if b.get("n", 0) != a.get("n", 0):
            errs.append(f"受保护目录文件数变了：{d}（{a.get('n')} → {b.get('n')}）")
        if b.get("newest", 0) > a.get("newest", 0) + 1e-6:
            errs.append(f"受保护目录里有文件被改过：{d}")

    cm = B.load_meta("chars", {}) or {}
    chars = cm.get("chars", {})
    pm = B.load_meta("props", {}) or {}
    props = pm.get("props", {})
    bgm = B.load_meta("bg", {}) or {}
    ui = B.load_meta("ui", {}) or {}
    audio = B.load_meta("audio")
    video = B.load_meta("video", {}) or {}
    font_rep = B.load_meta("font_report", {}) or {}

    # 2. 引用的图片 key 都在索引里
    def walk(o, where):
        if isinstance(o, str):
            if IMG_KEY_RE.match(o) and o not in B.img_index:
                errs.append(f"{where} 引用的图片 key 不在 img_index：{o}")
        elif isinstance(o, dict):
            for k, v in o.items():
                walk(v, where)
        elif isinstance(o, list):
            for v in o:
                walk(v, where)
    for name, sec in (("chars", chars), ("props", pm), ("bg", bgm), ("ui", ui),
                      ("font", B.load_meta("font", {})), ("fxtex", B.load_meta("fxtex", {}))):
        walk(sec, name)
    for k, e in B.img_index.items():
        if not os.path.exists(B.img_path(k)):
            errs.append(f"img_index 里的文件不存在：{k}")

    # 3. amap → animations，headAlias → heads
    for cid, ch in chars.items():
        names = set(ch.get("animations", {})) | set(ch.get("aliases", {}))
        for lg, v in ch.get("amap", {}).items():
            if amap_target(v) not in names:
                errs.append(f"{cid}.amap.{lg} → {amap_target(v)} 不在 animations")
        for al, emo in ch.get("headAlias", {}).items():
            if emo not in ch.get("heads", {}):
                errs.append(f"{cid}.headAlias.{al} → {emo} 不在 heads")
    rep = B.load_meta("chars_report", {}) or {}
    for d in rep.get("amap_dropped", []):
        cid = d.split(".")[0]
        pri = "P0" if cid in M1_A else "P1"
        bad(f"amap 指向的真名还没有图（已从数据里去掉）：{d}", "art", pri)

    # 4. §3.14 A：补帧 + amap 条目
    for cid, (acts, need_amap) in M1_A.items():
        ch = chars.get(cid)
        if not ch:
            errs.append(f"§3.14 A：图集 {cid} 不存在")
            continue
        for a in acts:
            if a not in ch["animations"]:
                bad(f"§3.14 A：{cid}.{a}（新动作）还没有", "art")
        for lg in need_amap:
            if lg not in ch.get("amap", {}):
                bad(f"§3.14 A：{cid}.amap 缺 {lg}", "art")
    # §3.14 B：新角色
    orig_names = set()
    for jp in glob.glob(os.path.join(ATLAS, "*", "*.json")):
        m = load_json(jp, {}) or {}
        if "cell" in m:
            orig_names.add(m["id"])
    for cid, (pri, acts, emos) in M1_B.items():
        if cid in orig_names:
            errs.append(f"§3.14 B：新 cid {cid} 和原图集重名")
        ch = chars.get(cid)
        if not ch:
            bad(f"§3.14 B：新角色 {cid} 还没有", "art", pri)
            continue
        for a in acts:
            if a not in ch["animations"] and a not in ch.get("amap", {}):
                bad(f"§3.14 B：{cid}.{a} 还没有", "art", pri)
        for e in emos:
            if e not in ch.get("heads", {}):
                bad(f"§3.14 B：{cid} 头像 {e} 还没有", "art", pri)
    # §3.14 C：新道具 + 用到的原道具
    for pid, pri in M1_C.items():
        if pid == "magazine" and "magazine" not in props and "manga" in props:
            continue                                        # 原 manga 合用就不画（§3.4）
        if pid not in props:
            bad(f"§3.14 C：新道具 {pid} 还没有", "art", pri)
        elif pid in M1_C_FRAMES and props[pid].get("frames") != M1_C_FRAMES[pid]:
            bad(f"§3.14 C：道具 {pid} 帧数 {props[pid].get('frames')}，清单要 {M1_C_FRAMES[pid]}", "art", pri)
    for pid in M1_PROPS_ORIG:
        if pid not in props:
            errs.append(f"§3.14 C：原道具 {pid} 不存在")
    # §3.14 D：背景
    bgrep = B.load_meta("bg_report", {}) or {}
    for key, spec in BG_SPEC.items():
        if key not in bgm:
            bad(f"§3.14 D：背景 {key} 没导出", None, spec["pri"])
        elif key in (bgrep.get("fallback") or {}):
            todo.append(f"[{spec['pri']}，兜底快照] 背景 {key} 现在是静态快照：{bgrep['fallback'][key]}（包 7B 导出后自动替换）")
    for short, p in B.packs().items():
        for k in p.get("bg", []):
            if k not in bgm:
                errs.append(f"packs.json 的背景 {k}（{short}）没导出")
    # §3.14 E：UI
    for sec, keys in M1_E.items():
        have = ui.get(sec) or {}
        for k in keys:
            if k not in have:
                errs.append(f"§3.14 E：ui.{sec}.{k} 没有")
    if "mark" not in (ui.get("vs") or {}):
        errs.append("§3.14 E：ui.vs.mark 没有")
    if not (ui.get("crash") or {}).get("plate") or len((ui.get("crash") or {}).get("digits") or []) != 10:
        errs.append("§3.14 E：ui.crash 的 plate / digits 0–9 不全")
    for k in ("logo", "tbc"):
        if k not in ui:
            errs.append(f"ui.{k} 没有")
    # §3.14 F / G：音频
    if audio is None:
        bad("§3.14 F / G：_meta\\audio.json 不存在（包 1 的 audio 步）", "audio")
    else:
        mus, sfx = audio.get("music", {}), audio.get("sfx", {})
        groups = {v.get("group") for v in sfx.values() if isinstance(v, dict)}
        for n in M1_F:
            if n not in mus:
                bad(f"§3.14 F：音乐 {n} 没有", "audio")
        for n in M1_G:
            if n not in sfx and n not in groups:
                bad(f"§3.14 G：音效 {n} 没有", "audio")
        for n, m in mus.items():
            f = m.get("file") if isinstance(m, dict) else None
            if f and not os.path.exists(os.path.join(B.game, f)):
                errs.append(f"音乐 {n} 的数据文件不存在：{f}")
        sfxjs = os.path.join(B.data, "sfx.js")
        if sfx and not os.path.exists(sfxjs):
            errs.append("data\\sfx.js 不存在")
        elif sfx:
            txt = open(sfxjs, encoding="utf-8").read()
            for n in sfx:
                if json.dumps(n, ensure_ascii=False) not in txt:
                    errs.append(f"音效 {n} 在 sfx.js 里没有数据")
    # §3.14 H：视频
    for n in M1_H:
        if n not in video:
            bad(f"§3.14 H：视频 {n} 还没渲（video 步不在默认步骤里，集成包跑 video data）", "video", "P1")
        else:
            for k in ("src", "webm"):
                if not video[n].get(k) or not os.path.exists(os.path.join(B.game, video[n][k])):
                    errs.append(f"视频 {n}.{k} 文件不存在")
    # 字库缺字
    if font_rep.get("missing"):
        errs.append(f"字库缺字 {len(font_rep['missing'])} 个：{''.join(sorted(font_rep['missing']))}")
    # 运行时文件
    for f in ("data_meta.js", "img_core.js"):
        if not os.path.exists(os.path.join(B.data, f)):
            errs.append(f"data\\{f} 不存在（先跑 data 步）")
    if os.path.exists(os.path.join(B.data, "img_core.js")):
        txt = open(os.path.join(B.data, "img_core.js"), encoding="utf-8").read()
        if 'D.packKeys["core"]' not in txt:
            errs.append("img_core.js 没写 packKeys.core")
    for short in B.packs():
        if not os.path.exists(os.path.join(B.data, f"img_bg_{short}.js")):
            errs.append(f"data\\img_bg_{short}.js 不存在")

    B.todo = todo
    B.save_meta("check", dict(errors=errs, todo=todo, warnings=[m for _s, m in B.warnings],
                              fallbacks=B.fallbacks, time=time.strftime("%Y-%m-%dT%H:%M:%S")))
    if todo:
        print(f"  待办（不算失败）{len(todo)} 条：")
        for t in todo:
            print("    - " + t.replace("\n", "\n      "))
    if errs:
        print(f"  ✗ check 失败 {len(errs)} 条：")
        for e in errs:
            print("    - " + e.replace("\n", "\n      "))
        B.errors.extend(("check", e) for e in errs)
        return False
    print("  ✓ check 通过")
    return True


# ====================================================================== 入口
STEP_FUNCS = dict(art=step_art, chars=step_chars, props=step_props, bg=step_bg, ui=step_ui, fx=step_fx,
                  font=step_font, audio=step_audio, video=step_video, data=step_data)


def main(argv=None):
    ap = argparse.ArgumentParser(description="JoJo 游戏资源构建（技术约定 §5）")
    ap.add_argument("steps", nargs="*", help="art chars props bg ui fx font audio video data check（不写 = 默认，不含 video）")
    ap.add_argument("--skip", default="", help="逗号分隔，例：--skip art,audio（并行阶段包 6 自测用）")
    ap.add_argument("--force", action="store_true", help="忽略缓存全部重做")
    a = ap.parse_args(argv)
    steps = a.steps or list(DEFAULT_STEPS)
    for s in steps:
        if s not in STEP_ORDER:
            ap.error(f"不认识的步骤：{s}（可选 {' '.join(STEP_ORDER)}）")
    skip = {s.strip() for s in a.skip.split(",") if s.strip()}
    source_steps = set(steps) - {"font", "data", "check"} - skip
    if source_steps and not os.path.isfile(os.path.join(SRC, "engine", "core.py")):
        ap.error("原素材工程不在公开仓库内。请将 JOJO_WORKSPACE 设置为包含 源码/角色图集/烘焙脚本 的目录；仅重新打包已有资源可运行 data check。")
    B = Build(force=a.force, skip=skip)
    return run_steps(B, steps)


def run_steps(B, steps):
    """按 STEP_ORDER 跑这些步（B.skip 里的跳过）；每步出错只记下来、接着跑下一步。返回码 0 = 没有错误、check 通过。
    tools\\dev\\p6\\test_build.py 用另一套输出目录和桩配方模块调它。"""
    skip = B.skip
    steps = [s for s in STEP_ORDER if s in steps]
    T0 = time.time()
    snap0 = protected_snapshot()
    print(f"JoJo build_assets：{' '.join(steps)}" + (f"（跳过 {','.join(sorted(skip))}）" if skip else "")
          + ("（--force）" if B.force else ""))
    ok = True
    for s in steps:
        if s in skip:
            print(f"[{s}] 跳过（--skip）")
            continue
        t0 = time.time()
        print(f"[{s}]")
        B.cur_step = s
        try:
            if s == "check":
                ok = step_check(B, snap0) and ok
            else:
                STEP_FUNCS[s](B)
                B.ran.append(s)
        except Exception:
            B.error(f"{s} 步出错：\n" + traceback.format_exc())
            B.failed.append(s)
        finally:
            B.save_index()
        print(f"  [{s}] {time.time() - t0:.1f}s")
    nerr = len([e for e in B.errors if e[0] != "check"])
    print("=" * 60)
    print(f"完成 {time.time() - T0:.1f}s；错误 {len(B.errors)}，警告 {len(B.warnings)}，"
          f"兜底 {sum(len(v) for v in B.fallbacks.values())}，缓存跳过 {B.cached_steps}")
    if B.fallbacks:
        for st, msgs in B.fallbacks.items():
            for m in msgs:
                print(f"  ~ [{st}] {m.splitlines()[0]}")
    return 1 if (nerr or not ok or B.failed) else 0


if __name__ == "__main__":
    sys.exit(main())
