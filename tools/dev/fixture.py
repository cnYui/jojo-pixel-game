# -*- coding: utf-8 -*-
r"""给各包自测用的最小数据包（包 6，技术约定 §7.6 / §7.0 第 3 条）。

产物（生成物，别手改）：
    tools\dev\fixture\data_meta.js        window.GAME_DATA（格式 = 技术约定 §3.1–§3.12）
    tools\dev\fixture\img_core.js         全部角色图集（原 41 个 + assets\chars_new\ 里已有的新图集）、头像（含 17 张场景头像 + headAlias）、
                                          道具（原 35 个 + assets\props_new\ 里已有的）、场景专用 97 个、UI 预渲染（名牌 / 替身卡 / 地点 / 篇章 /
                                          大字 / 拟声字 / ゴゴゴ / 必杀名 / VS / 面板 / 坠毁章 / TBC / logo）、字库、特效纹理
    tools\dev\fixture\img_bg_fixture.js   §3.14 D 的全部背景（每个 key 一张 t=0 静态快照，图层 = 一个 static）
    tools\dev\fixture\_build\             中间 PNG 和 _meta（缓存用）

在自测页面里（页面放在 tools\dev\pN\ 下）这样加载：
    <script src="../fixture/data_meta.js"></script>
    <script src="../fixture/img_core.js"></script>
    <script src="../../../data/sfx.js"></script>          <!-- 有音频时（包 1 的产物；没有就别加） -->
  - GAME_DATA.packs 里每个背景包（bg_title / bg_common / bg_prologue / bg_ch1 / bg_fixture）的 file 都是
    "../fixture/img_bg_fixture.js"（相对 tools\dev\pN\ 的页面）。G.res.loadPack('bg_ch1') 之类照常用；
    这一个文件加载后，全部背景包都标成已加载（packKeys 按各包自己的 key 列表写）。
  - GAME_DATA.audio = tools\_meta\audio.json（包 1）的内容，音乐的 file 改成 "../../../data/music/<名>.js"；
    GAME_DATA.video 同理（只有已经渲出来的）。
  - GAME_DATA.fixture = { built, gameRoot: '../../../', pageDir: 'tools/dev/pN/', note } —— 页面不在 tools\dev\pN\ 一层时，
    自己把 packs[*].file、audio.music[*].file 前面的相对路径换掉（或者用 --prefix 重新生成）。
  - 字库收的字 = 游戏里已有的全部字 + GB2312 全部（6763 个汉字和符号）+ 假名，测试文本基本不会缺字。

用法（PowerShell 先 $env:PYTHONDONTWRITEBYTECODE = 1）：
    python -B tools\dev\fixture.py              # 有缓存的步骤跳过（约 10–40 s）
    python -B tools\dev\fixture.py --force      # 全部重做
    python -B tools\dev\fixture.py --prefix ../fixture/ --game-root ../../../
只读：源码、角色图集、assets\chars_new\、assets\props_new\、tools\registry\、tools\_meta\audio.json；只写 tools\dev\fixture\。
"""
import sys
sys.dont_write_bytecode = True

import argparse  # noqa: E402
import base64  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402

DEV = os.path.dirname(os.path.abspath(__file__))       # 游戏\tools\dev
TOOLS = os.path.dirname(DEV)                            # 游戏\tools
GAME = os.path.dirname(TOOLS)
FIX = os.path.join(DEV, "fixture")
BUILD = os.path.join(FIX, "_build")

if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import build_assets as BA  # noqa: E402   （import 时会把 源码 放进 sys.path）


def gb2312_chars():
    """GB2312 全部可打印字符（区 1–9 符号 / 假名 / 希腊 / 俄文，区 16–87 汉字）。"""
    out = []
    for hi in range(0xA1, 0xF8):
        for lo in range(0xA1, 0xFF):
            try:
                ch = bytes([hi, lo]).decode("gb2312")
            except UnicodeDecodeError:
                continue
            out.append(ch)
    return "".join(out)


def step_bg_fixture(B):
    """§3.14 D 的每个 key：t=0 静态快照（不调包 7B 的配方，fixture 要稳定、和别人的进度无关）。"""
    if B.cached("bg", [os.path.join(BA.SRC, "engine", "bg_asia.py"), os.path.join(BA.SRC, "engine", "bg_egypt.py"),
                       os.path.join(BA.SRC, "engine", "bg.py")]):
        return
    B.drop_step_images("bg")
    stages, rep = {}, {}
    for key, spec in BA.BG_SPEC.items():
        try:
            stages[key], how = BA.bg_fallback_stage(B, key, spec["pack"])
            rep[key] = how
        except Exception:
            B.error(f"背景 {key} 快照失败：\n" + traceback.format_exc(limit=3))
    B.save_meta("bg_report", dict(fallback=rep, recipe=None))
    B.save_meta("bg", BA.jsonable(stages))
    print(f"  bg: {len(stages)} 张静态快照")


def step_font_fixture(B):
    if B.cached("font", [os.path.join(GAME, "story"), os.path.join(GAME, "engine"), os.path.join(GAME, "main.js"),
                         B.registry, os.path.join(B.meta, "chars.json"), os.path.join(TOOLS, "ui_jojo.py"),
                         os.path.abspath(__file__)]):
        return
    B.drop_step_images("font")
    chars = BA.collect_font_chars(B, extra_text=gb2312_chars())
    meta, missing, n = BA.build_font_atlas(B, chars)
    real_missing = {ch: w for ch, w in missing.items() if w != "extra"}
    if real_missing:
        B.warn("游戏文本里有 simsun 没有的字（正式构建会报错）：" + "".join(sorted(real_missing)))
    B.save_meta("font", meta)
    B.save_meta("font_report", dict(n=n, missing=real_missing))
    print(f"  font: {n} 字 × 2 档")


def write_js(path, s):
    BA.write_text(path, s)
    return len(s.encode("utf-8"))


def img_entry(B, key):
    fp = B.img_path(key)
    with open(fp, "rb") as fh:
        return json.dumps(key, ensure_ascii=False) + ':"data:image/png;base64,' + base64.b64encode(fh.read()).decode("ascii") + '"'


def assemble_fixture(B, prefix, game_root):
    gd, _ = BA.assemble(B, FIX, file_prefix=prefix, write=False)
    bgm = gd["bg"]
    bg_file = prefix + "img_bg_fixture.js"
    # 所有背景包都指向同一个文件
    pack_keys = {}
    for name, p in gd["packs"].items():
        if name == "core":
            continue
        p["file"] = bg_file
        keys = []
        for bk in p.get("bg", []):
            keys += [k for k, e in B.img_index.items() if k.startswith(f"bg/{bk}/")]
        pack_keys[name] = sorted(keys)
    all_bg = sorted(k for k in B.img_index if k.startswith("bg/"))
    gd["packs"]["bg_fixture"] = dict(file=bg_file, bg=sorted(bgm))
    pack_keys["bg_fixture"] = all_bg
    # 音频 / 视频：路径改成相对 tools\dev\pN\ 页面
    au = BA.load_json(os.path.join(BA.META, "audio.json"))
    if isinstance(au, dict):
        au = json.loads(json.dumps(au))
        for m in (au.get("music") or {}).values():
            if isinstance(m, dict) and m.get("file"):
                m["file"] = game_root + m["file"]
        gd["audio"] = au
    vi = BA.load_json(os.path.join(BA.META, "video.json"))
    if isinstance(vi, dict):
        vi = json.loads(json.dumps(vi))
        for m in vi.values():
            for k in ("src", "webm"):
                if m.get(k):
                    m[k] = game_root + m[k]
        gd["video"] = vi
    gd["built"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    gd["fixture"] = dict(built=gd["built"], gameRoot=game_root, pageDir="tools/dev/pN/", prefix=prefix,
                         sfxFile=game_root + "data/sfx.js",
                         note="包 6 tools\\dev\\fixture.py 生成；背景是 t=0 静态快照；页面不在 tools\\dev\\pN\\ 一层时改 prefix")
    sizes = {}
    sizes["data_meta.js"] = write_js(os.path.join(FIX, "data_meta.js"),
                                     "window.GAME_DATA = " + json.dumps(gd, ensure_ascii=False, separators=(",", ":")) + ";\n")
    core = sorted(k for k in B.img_index if not k.startswith("bg/"))
    sizes["img_core.js"] = write_js(
        os.path.join(FIX, "img_core.js"),
        "(function(){var D=window.GAME_DATA;Object.assign(D.img,{" + ",".join(img_entry(B, k) for k in core) + "});"
        + f"D.packKeys.core={json.dumps(core, ensure_ascii=False)};D.packsLoaded.core=true;}})();\n")
    tail = "".join(f"D.packKeys[{json.dumps(n)}]={json.dumps(ks, ensure_ascii=False)};D.packsLoaded[{json.dumps(n)}]=true;"
                   for n, ks in sorted(pack_keys.items()))
    sizes["img_bg_fixture.js"] = write_js(
        os.path.join(FIX, "img_bg_fixture.js"),
        "(function(){var D=window.GAME_DATA;Object.assign(D.img,{" + ",".join(img_entry(B, k) for k in all_bg) + "});"
        + tail + "})();\n")
    return gd, sizes


def main(argv=None):
    ap = argparse.ArgumentParser(description="生成 tools\\dev\\fixture\\（各包自测用的最小数据包）")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--prefix", default="../fixture/", help="packs[*].file 的前缀（相对自测页面）")
    ap.add_argument("--game-root", default="../../../", help="自测页面到游戏根目录的相对路径（音乐 / 视频文件用）")
    a = ap.parse_args(argv)
    T0 = time.time()
    os.makedirs(FIX, exist_ok=True)
    B = BA.Build(assets=os.path.join(BUILD, "assets"), meta=os.path.join(BUILD, "meta"), data=FIX,
                 force=a.force, label="fixture")
    B.fixture_mode = True
    steps = [("chars", BA.step_chars), ("props", BA.step_props), ("bg", step_bg_fixture), ("ui", BA.step_ui),
             ("fx", BA.step_fx), ("font", step_font_fixture)]
    for name, fn in steps:
        t0 = time.time()
        print(f"[{name}]")
        B.cur_step = name
        try:
            fn(B)
        except Exception:
            B.error(f"{name} 步出错：\n" + traceback.format_exc())
        finally:
            B.save_index()
        print(f"  [{name}] {time.time() - t0:.1f}s")
    B.cur_step = "data"
    gd, sizes = assemble_fixture(B, a.prefix, a.game_root)
    for f, n in sizes.items():
        print(f"  {f:22s} {n / 1e6:6.2f} MB")
    print(f"fixture：{len(B.img_index)} 张图（角色 {len(gd['chars'])}、道具 {len(gd['props'])}、场景 {len(gd['scene'])}、"
          f"背景 {len(gd['bg'])}），字库 {len(gd['font'].get('16', {}).get('glyphs', {}))} 字，"
          f"音效 {len((gd.get('audio') or {}).get('sfx', {}))}，用时 {time.time() - T0:.1f}s；"
          f"错误 {len(B.errors)}，警告 {len(B.warnings)}")
    return 1 if B.errors else 0


if __name__ == "__main__":
    sys.exit(main())
