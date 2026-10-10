# -*- coding: utf-8 -*-
r"""包 6 自测：build_assets 对“晚到 / 写坏的配方模块”能兜底继续（技术约定 §7.6 依赖一栏）。

用 tools\dev\p6\stubs_ok\（能用的桩）、stubs_bad\（抛错 / 半截的桩）、一个空目录（模块都不存在）分别顶替
tools\art\bake_art.py、tools\art\amap.py、tools\bg_jojo.py、tools\build_audio.py，跑全部步骤（不含 video），
输出写到 scratchpad（不碰 assets\ data\ tools\_meta\），逐条断言结果。

    python -B tools\dev\p6\test_build.py [--out 临时目录]
返回码 0 = 全部断言通过。
"""
import sys
sys.dont_write_bytecode = True

import argparse  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
import tempfile  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, TOOLS)
import build_assets as BA  # noqa: E402

STEPS = ["art", "chars", "props", "bg", "ui", "fx", "font", "audio", "data", "check"]
RESULTS = []


def expect(cond, msg):
    RESULTS.append((bool(cond), msg))
    print(("  ✓ " if cond else "  ✗ ") + msg)


def run_variant(name, recipe_dir, out_root):
    print("=" * 70)
    print(f"变体 {name}：配方模块目录 = {recipe_dir}")
    root = tempfile.mkdtemp(prefix=name + "_", dir=out_root)     # 每次新目录，不删旧的（在系统临时目录里）
    os.makedirs(os.path.join(root, "meta"))
    au = os.path.join(BA.META, "audio.json")
    if os.path.exists(au):                        # 包 1 的音频元数据只读拷一份，check 才能核对音效清单
        shutil.copyfile(au, os.path.join(root, "meta", "audio.json"))
    # 模块路径换成桩目录（只改本进程内存里的模块变量）
    BA.ART_DIR = recipe_dir
    BA.HERE = recipe_dir
    for m in ("bake_art", "jojo_amap", "bg_jojo", "build_audio"):
        sys.modules.pop(m, None)
    B = BA.Build(assets=os.path.join(root, "assets"), meta=os.path.join(root, "meta"), data=os.path.join(root, "data"),
                 force=True, label="test-" + name)
    rc = BA.run_steps(B, STEPS)
    cm = B.load_meta("chars", {})
    pm = B.load_meta("props", {})
    bg = B.load_meta("bg", {})
    return B, rc, cm, pm, bg, root


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(tempfile.gettempdir(), "jojo_p6_test_build"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    real_art, real_here = BA.ART_DIR, BA.HERE

    # ---------------------------------------------------------------- 1. 能用的桩
    B, rc, cm, pm, bg, root = run_variant("ok", os.path.join(HERE, "stubs_ok"), a.out)
    ch = cm.get("chars", {})
    expect(not B.failed, f"没有哪一步整步失败（failed = {B.failed}）")
    expect("grayfly" in ch, "chars_new 的新角色 grayfly 合并进 chars")
    g = ch.get("grayfly", {})
    expect(set(g.get("heads", {})) >= {"normal", "scared"}, "grayfly 头像 normal / scared 都在")
    expect(g.get("headAlias", {}).get("portrait_scared") == "scared", "headAlias：portrait_scared → scared")
    expect(g.get("amap", {}).get("hurt") == "flee", "amap.py（桩）的 grayfly.hurt → flee 生效")
    expect(g.get("bodyW") == 5, "BODYW（桩）生效：grayfly.bodyW = 5")
    j = ch.get("jotaro", {})
    expect("guard" not in j.get("amap", {}), "指向不存在真名的 jotaro.guard 被去掉")
    expect(isinstance(j.get("amap", {}).get("down"), dict), "对象写法的 amap（down → {a:hurt, rot:-90}）保留")
    expect(j.get("headAlias", {}).get("s05_jotaro_talk") == "glare", "场景头像映射：s05_jotaro_talk → glare")
    expect("grayfly" in cm.get("speakers", {}), "名牌里的 grayfly 补进 speakers")
    pr = pm.get("props", {})
    expect(pr.get("jail_pipe", {}).get("isNew") and pr["jail_pipe"].get("frames") == 2, "props_new 的 jail_pipe 合并（isNew、2 帧）")
    expect("tissue" in pr and "coin" in pr, "新道具 tissue 和原道具 coin 都在")
    expect([ly.get("type") for ly in bg.get("sky_day", {}).get("layers", [])] == ["wrap", "wrap"], "bg_jojo（桩）导出的 sky_day 用上了")
    expect(bg.get("test_extra", {}).get("pack") == "common", "没登记的背景 test_extra 归进 common")
    expect(all(k in bg for k in BA.BG_SPEC), "§3.14 D 其余 key 用兜底快照补齐")
    expect(sys.modules.get("build_audio") and sys.modules["build_audio"].CALLS == [["--force"]], "build_audio.run（桩）被调用，--force 透传")
    dj = os.path.join(root, "data")
    expect(os.path.exists(os.path.join(dj, "img_core.js")) and os.path.exists(os.path.join(dj, "img_bg_common.js")),
           "data 步写出 img_core.js、img_bg_common.js")
    txt = open(os.path.join(dj, "img_bg_common.js"), encoding="utf-8").read()
    expect('"bg/sky_day/far"' in txt and 'D.packKeys["bg_common"]' in txt, "背景图进了 bg_common 包、写了 packKeys")
    chk = B.load_meta("check", {})
    expect(any("grayfly" in e for e in chk.get("errors", [])), "check 把 grayfly 缺的 P0 动作（seated / down）报成错误（art 没跳过）")
    expect(not any("受保护目录" in e for e in chk.get("errors", [])), "受保护目录没被写")

    # ---------------------------------------------------------------- 2. 抛错 / 半截的桩
    B, rc, cm, pm, bg, root = run_variant("bad", os.path.join(HERE, "stubs_bad"), a.out)
    expect(not B.failed, f"配方模块抛错时没有整步失败（failed = {B.failed}）")
    fb = B.fallbacks
    expect("art" in fb and "bake_art.run 抛错" in fb["art"][0], "art：bake_art 抛错 → 兜底跳过")
    expect("chars" in fb and any("amap.py 导入失败" in m for m in fb["chars"]), "chars：amap.py 导入失败 → 内置 amap")
    expect(cm.get("chars", {}).get("jotaro", {}).get("amap", {}).get("cmd") == "point", "内置 amap 生效（jotaro.cmd → point）")
    expect("bg" in fb and any("bg_jojo.build_all 抛错" in m for m in fb["bg"]), "bg：build_all 抛错 → 兜底继续")
    expect(bg.get("world_map", {}).get("layers", [{}])[0].get("image") == "bg/world_map/stub",
           "抛错前已经完整导出的 world_map 保留了配方的结果")
    expect("bg/sky_day/half_done" not in B.img_index, "抛错前登记的半截背景图（sky_day）被丢掉")
    expect([ly.get("type") for ly in bg.get("sky_day", {}).get("layers", [])] == ["static"]
           and bg["sky_day"]["layers"][0]["image"] == "bg/sky_day/base", "sky_day 换成兜底快照")
    expect("audio" in fb and "build_audio.run 抛错" in fb["audio"][0], "audio：run 抛错 → 跳过")
    expect(len(cm.get("chars", {})) >= 40 and "jail_pipe" not in pm.get("props", {}), "chars / props 照常出（没有新道具）")

    # ---------------------------------------------------------------- 3. 模块都不存在
    empty = os.path.join(a.out, "_empty_recipes")
    os.makedirs(empty, exist_ok=True)
    B, rc, cm, pm, bg, root = run_variant("missing", empty, a.out)
    expect(not B.failed, f"模块都不存在时没有整步失败（failed = {B.failed}）")
    expect({"art", "chars", "bg", "audio"} <= set(B.fallbacks), f"四个配方都走了兜底（{sorted(B.fallbacks)}）")
    expect(all(k in bg for k in BA.BG_SPEC), "背景全部是兜底快照")

    BA.ART_DIR, BA.HERE = real_art, real_here
    bad = [m for ok, m in RESULTS if not ok]
    print("=" * 70)
    print(f"断言 {len(RESULTS)} 条，失败 {len(bad)} 条")
    for m in bad:
        print("  ✗ " + m)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
