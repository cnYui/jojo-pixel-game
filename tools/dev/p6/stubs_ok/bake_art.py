# -*- coding: utf-8 -*-
# 包 6 自测用的桩（不是包 7A 的真配方）：只测 build_assets 的 art → chars / props 合并流程。
# 新角色 grayfly = 借荷尔·荷斯的图集改 id（再加一个 portrait_scared 表情）；新道具 jail_pipe（2 帧）、tissue（1 帧）。
import json
import os
import shutil

from PIL import Image, ImageDraw


def run(out_dir, c):
    src = os.path.join(c["ATLAS"], "holhorse")
    m = json.load(open(os.path.join(src, "holhorse.json"), encoding="utf-8"))
    d = os.path.join(out_dir, "grayfly")
    os.makedirs(os.path.join(d, "头像"), exist_ok=True)
    m["id"], m["name"], m["image"] = "grayfly", "格雷·弗莱（桩）", "grayfly.png"
    shutil.copyfile(os.path.join(src, "holhorse.png"), os.path.join(d, "grayfly.png"))
    for e in m["expressions"]:
        for f in e["files"]:
            shutil.copyfile(os.path.join(src, f), os.path.join(d, f))
    shutil.copyfile(os.path.join(src, "头像", "portrait_0.png"), os.path.join(d, "头像", "portrait_scared_0.png"))
    m["expressions"].append(dict(id="portrait_scared", emotion="scared", frames=1, size=[32, 32],
                                 files=["头像/portrait_scared_0.png"]))
    json.dump(m, open(os.path.join(d, "grayfly.json"), "w", encoding="utf-8"), ensure_ascii=False)

    pdir = c["out_props_new"]
    os.makedirs(pdir, exist_ok=True)
    pipe = Image.new("RGBA", (32, 48), (0, 0, 0, 0))
    dr = ImageDraw.Draw(pipe)
    dr.rectangle((5, 0, 10, 47), fill=(120, 120, 130, 255))
    dr.rectangle((21, 20, 26, 47), fill=(120, 120, 130, 255))
    pipe.save(os.path.join(pdir, "jail_pipe.png"))
    tissue = Image.new("RGBA", (10, 8), (240, 236, 226, 255))
    tissue.save(os.path.join(pdir, "tissue.png"))
    json.dump(dict(props=[dict(id="jail_pipe", file="jail_pipe.png", frames=2, size=[16, 48], pivot=[8, 48], fps=0,
                               kind="static"),
                          dict(id="tissue", file="tissue.png", frames=1, size=[10, 8], pivot=[5, 8], fps=0,
                               kind="static")]),
              open(os.path.join(pdir, "props_new.json"), "w", encoding="utf-8"), ensure_ascii=False)
    return dict(stub=True, cids=["grayfly"], props=["jail_pipe", "tissue"])
