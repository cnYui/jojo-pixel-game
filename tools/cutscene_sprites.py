# -*- coding: utf-8 -*-
r"""cutscene_sprites -- 过场视频用游戏现在的角色形象（用户 2026-10-10：“片头动画里乔瑟夫还是旧脸”）。

render_cutscene.py 直接调原工程的 render_frame，精灵从原工程的注册表 engine.sprite._REG 取；游戏里改过的形象
（二乔新脸 + 指人手臂分段、荷莉头前移……）只在 tools\art\bake_art 烘图集时、在内存里替换注册表，原工程文件没变，
所以片头 op（s00 点名卡 joseph.point、结尾剪影 joseph.idle / point）一直是旧脸。

apply_game_redraws() 在内存里做和 bake_art.run 第 1–2 步 + “原名重画”一模一样的事（不写任何文件）：
  1. assets.load_all()：原工程全部精灵；
  2. 按 bake_art.ART_MODULES 的顺序 import 我们的 art_* 模块（import 即注册新名字；art_joseph.apply 要用
     art_later_existing，后者又要 art_stands 等先注册，所以整串照烘焙顺序导入）；
  3. 原名重画，顺序同 bake_art：JOTARO_ADULT 为真才 art_jotaro_redraw.apply()（现在 False = 承太郎保持原卡通大头，
     开关从 bake_art 读，不另写一份）→ art_holly_fix.apply() → art_joseph.apply()。
  之后 sprite.get('joseph.point') 等就和游戏图集 assets\chars_new\joseph\joseph.png 里的格子逐像素相同
  （check_atlas() 核对；render_cutscene 每次渲染前都核对，不一致就报错退出）。

**必须在 import 场景模块之前调**：场景脚本可能在 import / 首帧时拿 joseph.idle 现做场景专用精灵（s05、s20）。
sys.path 只在导入期间临时加 tools\art（art_common 会再加 烘焙脚本、源码），结束后恢复原样。
"""
import sys
sys.dont_write_bytecode = True

import importlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(HERE)
ART = os.path.join(HERE, "art")

_DONE = []


def apply_game_redraws(log=print):
    """返回被替换的原精灵名列表（重复调用直接返回第一次的结果）。"""
    if _DONE:
        return list(_DONE)
    import assets                                    # 源码\assets（调用方已把 源码 放进 sys.path）
    assets.load_all()
    saved = list(sys.path)
    try:
        sys.path.insert(0, ART)
        import bake_art                              # 只为读 ART_MODULES / JOTARO_ADULT（import 时不做事）
        for mn in bake_art.ART_MODULES:
            if os.path.exists(os.path.join(ART, mn + ".py")):
                importlib.import_module(mn)
        redrawn = []
        if bake_art.JOTARO_ADULT:
            import art_jotaro_redraw
            redrawn += art_jotaro_redraw.apply()
        import art_holly_fix
        redrawn += art_holly_fix.apply()
        import art_joseph
        redrawn += art_joseph.apply()
    finally:
        sys.path[:] = saved
    _DONE.extend(redrawn)
    if log:
        log(f"  游戏层形象（同 bake_art，JOTARO_ADULT={bake_art.JOTARO_ADULT}）：替换 {len(redrawn)} 个原精灵 "
            f"{', '.join(redrawn)}")
    return redrawn


def check_atlas(names, chars_dir=None):
    r"""names 里每个精灵的每一帧按锚点放进游戏图集的格子，和 assets\chars_new\<cid>\<cid>.png 逐像素比；
    返回不一致的 [(名字, 帧号, 原因)]（图集里没有这个 cid / 动作 = 游戏用的就是原图集，跳过）。"""
    import numpy as np
    from PIL import Image
    from engine import sprite
    chars_dir = chars_dir or os.path.join(GAME, "assets", "chars_new")
    bad, cache = [], {}
    for name in names:
        cid, act = name.split(".", 1)
        mp = os.path.join(chars_dir, cid, cid + ".json")
        if not os.path.exists(mp):
            continue
        if cid not in cache:
            meta = json.load(open(mp, encoding="utf-8"))
            cache[cid] = (meta, Image.open(os.path.join(chars_dir, cid, meta["image"])).convert("RGBA"))
        meta, atlas = cache[cid]
        if act not in meta["animations"]:
            continue
        cw, ch = meta["cell"]
        px, py = meta["pivot"]
        row = meta["animations"][act]["row"]
        sd = sprite.get(name)
        if len(sd.frames) != meta["animations"][act]["frames"]:
            bad.append((name, -1, f"帧数 {len(sd.frames)} ≠ 图集 {meta['animations'][act]['frames']}"))
            continue
        for i, f in enumerate(sd.frames):
            ax, ay = sprite._anchor_px(sd.anchor, *f.size)
            cell = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            cell.paste(f, (int(round(px - ax)), int(round(py - ay))))
            ref = atlas.crop((i * cw, row * ch, (i + 1) * cw, (row + 1) * ch))
            if not np.array_equal(np.asarray(cell), np.asarray(ref)):
                bad.append((name, i, "和游戏图集不一致"))
    return bad
