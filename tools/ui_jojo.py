# -*- coding: utf-8 -*-
r"""UI 预渲染（包 6，技术约定 §3.7 / §5.6）：名牌 / 替身卡 / 地点卡 / 篇章卡 / 大标题 / 必杀名 / 拟声字 / ゴゴゴ /
VS 元素 / 面板 / 坠毁章 / TBC / 标题 logo，全部用原工程 源码\engine\text.py（雅黑粗体、不抗锯齿）画好存 PNG，
JS 只负责贴图、滑入、弹出、抖动。

被 build_assets.py 的 ui 步调用：build(c, texts, stands) → ui 元数据（§3.7 的结构）。
texts = tools\registry\ui_texts.json（包 8）合并在本文件的 DEFAULT_UI_TEXTS 之上（登记表有的条目优先）；
stands = tools\registry\stands.json 合并在 DEFAULT_STANDS 之上。

单独跑（只出预览联系表，不写 assets）：
    python -B tools\ui_jojo.py --preview C:\...\ui_preview.png
"""
import sys
sys.dont_write_bytecode = True

import copy  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(os.path.dirname(HERE)), "源码")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from PIL import Image, ImageDraw  # noqa: E402
import numpy as np  # noqa: E402

# ============================================================ 内置登记表（M1 最少条目，§3.14 E；文字照规划）
# 替身表（技术约定 §3.14 E 的表；fist 由 chars 步按图集算）
DEFAULT_STANDS = {
    "starplat": dict(cn="白金之星", en="STAR PLATINUM", owner="jotaro", aura="#b090ff", card="#c8a8ff",
                     ghost="#d8d0ff", impact="purple", kind="humanoid", idle=dict(dx=-6, z=6), link=None,
                     summonSfx="stand_summon_star"),
    "hermit": dict(cn="隐者之紫", en="HERMIT PURPLE", owner="joseph", aura="#c080ff", card="#c890ff",
                   ghost="#d0a0ff", impact="purple", kind="vine", idle=None, link=None,
                   summonSfx="stand_summon_purple"),
    "magred": dict(cn="红色魔术师", en="MAGICIAN'S RED", owner="avdol", aura="#ff7a30", card="#ff7040",
                   ghost="#ffb070", impact="red", kind="humanoid", idle=dict(dx=-6, z=6), link=None,
                   summonSfx="stand_summon_red"),
    "hiero": dict(cn="绿色法皇", en="HIEROPHANT GREEN", owner="kakyoin", aura="#70ffb0", card="#70ffb0",
                  ghost="#90ffc0", impact="green", kind="humanoid", idle=dict(dx=-4, z=10), link="tendril",
                  summonSfx="stand_summon_hiero"),
    "chariot": dict(cn="银色战车", en="SILVER CHARIOT", owner="polnareff", aura="#c8d8ff", card="#d8e4ff",
                    ghost="#c8d8ff", impact="blue", kind="humanoid", idle=dict(dx=-6, z=6), link=None,
                    summonSfx="stand_summon_chariot"),
    "fool": dict(cn="愚者", en="THE FOOL", owner="iggy", aura="#e8c070", card="#ffe08a", ghost="#fff0b0",
                 impact="yellow", kind="sand", idle=dict(dx=-8, z=4), link=None, summonSfx="stand_summon_fool"),
    "towergray": dict(cn="灰塔", en="TOWER OF GRAY", owner="grayfly", aura="#c8d8f0", card="#c8d8f0",
                      ghost="#e0e8f8", impact="bw", kind="object", idle=None, link=None, summonSfx=None),
    "theworld": dict(cn="世界", en="THE WORLD", owner="dio", aura="#ffd040", card="#ffd83c", ghost="#fff2a0",
                     impact="yellow", kind="humanoid", idle=dict(dx=-6, z=6), link=None,
                     summonSfx="stand_summon_world"),
}

_CH_COLOURS = {
    "prologue": ["#402060", "#200830"], "ch1": ["#6a1a4a", "#140828"], "ch2": ["#1a4a8a", "#0a1a3a"],
    "ch3": ["#4a1a3a", "#1a0812"], "ch4": ["#8a6a1a", "#3a1a08"], "ch5": ["#4a5a4a", "#1a2018"],
    "ch6": ["#d08a1a", "#6a3008"], "ch7": ["#3a6a8a", "#0a2030"], "ch8": ["#c8a050", "#5a3a10"],
    "ch9": ["#2a6a6a", "#0a2020"], "ch10": ["#6a4a2a", "#201008"], "ch11": ["#5a2a8a", "#140620"],
    "final": ["#c89a20", "#3a2a08"],
}


def _sfx(size=32, colour="#ffffff", outline="#000000", owidth=2):
    return dict(size=size, colour=colour, outline=outline, owidth=owidth)


DEFAULT_UI_TEXTS = {
    "namecards": {   # 规划 §5.1 / §5.2 名牌表
        "jotaro": dict(cn="空条承太郎", sub="不良高中生｜沉默寡言·身上有“恶灵”", accent="#3a4a9a"),
        "joseph": dict(cn="乔瑟夫·乔斯达", sub="承太郎的外公｜从纽约连夜赶来", accent="#6a8a3a"),
        "avdol": dict(cn="穆罕默德·阿布德尔", sub="乔瑟夫的老朋友｜开罗的占卜师", accent="#c0402a"),
        "kakyoin": dict(cn="花京院典明", sub="转学生｜DIO 的刺客？", accent="#2a9a5a"),
        "holly": dict(cn="空条荷莉", sub="承太郎的妈妈｜永远开朗", accent="#d0608a"),
        "grayfly": dict(cn="格雷·弗莱", sub="灰塔的替身使者｜把杀人伪装成事故", accent="#8a9ab0"),
        "polnareff": dict(cn="让·皮埃尔·波鲁纳雷夫", sub="JEAN PIERRE POLNAREFF", accent="#6a7ab0"),
    },
    "locations": {
        "tokyo": dict(place="1987年 日本·东京", sub="TOKYO · JAPAN"),
        "kujo": dict(place="空条家", sub="KUJO RESIDENCE · 东京"),
        "school": dict(place="东京·高中", sub="TOKYO · HIGH SCHOOL"),
        "plane": dict(place="飞往开罗的客机", sub="FLIGHT TO CAIRO"),
        "hongkong": dict(place="香港", sub="HONG KONG"),
        "garden": dict(place="香港·虎豹别墅", sub="TIGER BALM GARDEN · HONG KONG"),
    },
    "chapters": {    # no + title = D5 章名（技术约定 §2.8）；name = 规划 §2.1 副标题；en 第三行
        "prologue": dict(no="序章", title="东京", name="替身之名", en="PROLOGUE · TOKYO"),
        "ch1": dict(no="第1章", title="香港", name="灰塔与银色战车", en="CHAPTER 1 · HONG KONG"),
        "ch2": dict(no="第2章", title="南海", name="南海漂流", en="CHAPTER 2 · SOUTH CHINA SEA"),
        "ch3": dict(no="第3章", title="新加坡", name="新加坡的恶意", en="CHAPTER 3 · SINGAPORE"),
        "ch4": dict(no="第4章", title="印度", name="两只右手的男人", en="CHAPTER 4 · INDIA"),
        "ch5": dict(no="第5章", title="巴基斯坦", name="公路、浓雾与卡拉奇", en="CHAPTER 5 · PAKISTAN"),
        "ch6": dict(no="第6章", title="阿拉伯", name="沙漠的太阳与梦", en="CHAPTER 6 · ARABIA"),
        "ch7": dict(no="第7章", title="红海", name="许愿与大嘴", en="CHAPTER 7 · RED SEA"),
        "ch8": dict(no="第8章", title="埃及沙漠", name="九荣神：沙与预言", en="CHAPTER 8 · EGYPTIAN DESERT"),
        "ch9": dict(no="第9章", title="尼罗河", name="刀、磁铁与影子", en="CHAPTER 9 · THE NILE"),
        "ch10": dict(no="第10章", title="开罗", name="赌局与看门鸟", en="CHAPTER 10 · CAIRO"),
        "ch11": dict(no="第11章", title="DIO的馆", name="日落之前", en="CHAPTER 11 · DIO'S MANSION"),
        "final": dict(no="终章", title="DIO的世界", name="直到黎明", en="FINAL CHAPTER · DIO'S WORLD"),
    },
    "titles": {
        "stand": dict(text="替身", size=64, colour="#ffe040", outline="#2a0a3a", sub="S T A N D"),
        "egypt": dict(text="目标——埃及！", size=48, colour="#ffe040", outline="#2a0a3a"),
        "day50": dict(text="50", size=72, colour="#ff3048", outline="#1a0008"),
        "day_unit": dict(text="天", size=40, colour="#ff3048", outline="#1a0008"),
        "saiki": dict(text="再起不能", size=40, colour="#ffffff", outline="#000000", owidth=3),
        "draw": dict(text="胜负已分", size=40, colour="#ffffff", outline="#000000", owidth=3),
        "w6_hg_splash": dict(text="绿宝石水花——！", size=40, colour="#70ffb0", outline="#0a3a20"),
    },
    "sfx": {   # 拟声字 / 小字（§3.14 E；颜色照报告 05 §4.2 末尾的调色）
        "ORA": _sfx(40, "#ffe040", "#2a0a4a", 3), "ORA!": _sfx(42, "#ffe040", "#2a0a4a", 3),
        "ORA!!": _sfx(48, "#ffe040", "#2a0a4a", 3), "ORA!!!": _sfx(64, "#ffffff", "#3a0a5a", 4),
        "オラオラ": _sfx(40, "#ffe040", "#2a0a4a", 3), "HORA": _sfx(40, "#d8e4ff", "#1a1a3a", 3),
        "ドゴォ": _sfx(40, "#ffb040", "#2a0a0a", 3), "バキィ": _sfx(40, "#fff0c0", "#2a0a0a", 3),
        "ズガッ": _sfx(40, "#ffe070", "#3a1a08", 3), "キィン！": _sfx(36, "#d8e4ff", "#1a1a3a", 3),
        "ドドド": _sfx(40, "#fff2c8", "#3a1a08", 3), "ガシッ": _sfx(32, "#ffffff", "#1a1020", 2),
        "ギュルッ": _sfx(32, "#90ffc0", "#0a3a20", 2), "ズルッ": _sfx(32, "#90ffc0", "#0a3a20", 2),
        "メキメキッ": _sfx(34, "#fff0c0", "#2a0a0a", 2), "ギギギ…": _sfx(32, "#e0e0e8", "#202028", 2),
        "ゴオッ": _sfx(40, "#ffb040", "#3a0a00", 3), "ゴオオッ": _sfx(44, "#ffb040", "#3a0a00", 3),
        "シュッ": _sfx(28, "#ffffff", "#1a1a3a", 2), "シュバッ": _sfx(32, "#ffffff", "#1a1a3a", 2),
        "シュバババ": _sfx(36, "#d8e4ff", "#1a1a3a", 3), "バチバチッ": _sfx(32, "#ffe060", "#3a2a00", 2),
        "バキッ!!": _sfx(44, "#fff0c0", "#2a0a0a", 3), "ジュウウ": _sfx(32, "#ff9040", "#3a0a00", 2),
        "ドクン": _sfx(40, "#ff5070", "#2a0008", 3), "ドサッ": _sfx(32, "#ffffff", "#1a1020", 2),
        "ギュッ": _sfx(30, "#ffffff", "#1a1020", 2), "ガキッ": _sfx(34, "#d8e4ff", "#1a1a3a", 2),
        "砰！！": _sfx(40, "#ffb040", "#2a0a0a", 3), "OH MY GOD!": _sfx(36, "#ffe040", "#3a2a00", 3),
        "拉起来——！！": _sfx(32, "#ffffff", "#2a0a4a", 2), "呜哇啊啊啊——！！": _sfx(32, "#ffffff", "#000000", 2),
        "扑通——！！": _sfx(36, "#a0d8ff", "#0a1a3a", 3), "嗡嗡嗡——": _sfx(30, "#e0e8f8", "#202838", 2),
        "YES I AM!": _sfx(40, "#ffb040", "#3a0a00", 3), "チッチッ": _sfx(32, "#ffffff", "#3a0a00", 2),
        "呀嘞呀嘞daze": _sfx(30, "#e0e0ff", "#1a1a3a", 2), "绿宝石水花！": _sfx(36, "#70ffb0", "#0a3a20", 3),
        "十字火焰风暴！": _sfx(36, "#ffb040", "#3a0a00", 3), "！？": _sfx(40, "#ffffff", "#000000", 3),
        "看穿！": _sfx(32, "#ffffff", "#2050c0", 3), "破绽！": _sfx(32, "#ffe040", "#3a0a00", 3),
        "残像！": _sfx(32, "#d8e4ff", "#1a1a3a", 3), "它躲开了！": _sfx(28, "#ffffff", "#000000", 2),
        "被劈开了！": _sfx(28, "#ffffff", "#000000", 2), "……没用": _sfx(28, "#ffffff", "#000000", 2),
        "咚": _sfx(36, "#ffffff", "#000000", 3), "？": _sfx(32, "#ffffff", "#000000", 2),
        "U!": _sfx(28, "#ffe040", "#3a1a60", 3),
    },
    "specials": {
        "jotaro": dict(text="欧拉欧拉欧拉！", size=48, colour="#ffe040", outline="#2a0a4a"),
        "kakyoin": dict(text="绿宝石水花！", size=48, colour="#70ffb0", outline="#0a3a20"),
        "avdol": dict(text="十字火焰风暴！", size=48, colour="#ffb040", outline="#3a0a00"),
        "jail_bars": dict(text="……别小看我。", size=40, colour="#ffe040", outline="#2a0a4a"),
        "avdol_sp": dict(text="十字火焰风暴·Special！", size=44, colour="#ffb040", outline="#3a0a00"),
        "polnareff": dict(text="银色战车——卸甲！", size=44, colour="#d8e4ff", outline="#1a1a3a"),
        # 后段剧情专用 U 的切入大字（第11章 creamSun 的 name、终章 D3 的 title）。登记表 ui_texts.json 的 specials 节
        # 归战斗负责人维护，这两条放在内置表：登记表以后写了同名条目就以登记表为准（merge_texts 按条目合并）。
        "jotaro_ts": dict(text="白金之星·世界！", size=44, colour="#c8e4ff", outline="#1a1a5a"),
        "阳光飞踢": dict(text="阳光飞踢！", size=44, colour="#fff2b9", outline="#3a2a08"),
        # 第5章正义吸雾的切入（ch05.js 用主角切入 + title，查的是 specials）
        "正义 · 吸雾": dict(text="正义 · 吸雾！", size=40, colour="#d8e4d8", outline="#1a2018"),
    },
    "vs": {   # 规划 §4.1 表
        "hiero": dict(name="绿色法皇", en="HIEROPHANT GREEN", tag="VS 绿色法皇 / 东京·校门",
                      colours=["#1c6a40", "#0a3a20"]),
        "towergray": dict(name="灰塔", en="TOWER OF GRAY", tag="VS 灰塔 / 飞往开罗的客机",
                          colours=["#5a6a80", "#2a3040"]),
        "chariot": dict(name="银色战车", en="SILVER CHARIOT", tag="VS 银色战车 / 香港·虎豹别墅",
                        colours=["#5a6aa0", "#22284a"]),
    },
    "panels": {
        "tissue_note": dict(w=240, h=120, kind="note", text="空条承太郎。\n今天之内，我的替身会取你性命。",
                            ink="#2a1a40", paper="#f4efe2"),
    },
    "crash": {
        "plate": dict(text="乔瑟夫坠毁记录", size=16, colour="#3a2400", fill="#f0c040", border="#fff4c0"),
        "digits": dict(size=24, colour="#3a2400"),
    },
}
for _k, _v in DEFAULT_UI_TEXTS["chapters"].items():
    _v["colours"] = _CH_COLOURS[_k]

MENACE_CHARS = ["ゴ", "ド"]


def merge_texts(reg):
    """登记表（包 8）合并在内置表之上：每一节按条目合并，登记表有的条目优先；条目是字典时按字段合并
    （登记表写了的字段优先，没写的字段——例如篇章卡的 colours——用内置表的，免得漏写一个字段就丢了配色）。"""
    out = copy.deepcopy(DEFAULT_UI_TEXTS)
    for sec, v in (reg or {}).items():
        if not isinstance(v, dict):
            continue
        base = out.setdefault(sec, {})
        for k, e in v.items():
            if isinstance(e, dict) and isinstance(base.get(k), dict):
                base[k] = dict(base[k], **e)
            else:
                base[k] = e
    return out


# ============================================================ 画图
def _mods():
    from engine import text as TX, fx as FX
    from engine.core import Frame, rgb, mix, UW, UH, C
    return TX, FX, Frame, rgb, mix, UW, UH, C


def _crop(im):
    bb = im.getchannel("A").getbbox()
    if bb is None:
        return None, (0, 0)
    return im.crop(bb), (bb[0], bb[1])


def _lum(c):
    r, g, b = c
    return 0.299 * r + 0.587 * g + 0.114 * b


def _vstack(imgs, gap=2, align="center"):
    imgs = [i for i in imgs if i is not None]
    w = max(i.width for i in imgs)
    h = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = 0
    for i in imgs:
        x = (w - i.width) // 2 if align == "center" else 0
        out.alpha_composite(i, (x, y))
        y += i.height + gap
    return out


def _round_rect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def render_namecard(e):
    TX, FX, Frame, rgb, mix, UW, UH, C = _mods()
    fr = Frame(1.0, 24, 10.0, "ui")
    acc = rgb(e.get("accent", "#f0c040"))
    # 名牌的副标题用强调色；强调色太暗（规划给的名牌色都偏深）时副标题字提亮一半，横条仍用原色
    sub_col = mix(acc, (255, 255, 255), 0.55) if _lum(acc) < 140 else acc
    TX.name_card(fr, e["cn"], e.get("sub", ""), 0, 9, colour=e.get("colour", "#ffffff"), accent=sub_col)
    big = TX.text_img(e["cn"], "bold", 24, e.get("colour", "#ffffff"), outline=(0, 0, 0), owidth=2)
    bar = Image.new("RGBA", (big.width + 30, 4), acc + (255,))
    fr.ui.alpha_composite(bar, (24, UH - 96 + big.height + 1))
    im, (x, y) = _crop(fr.ui)
    return im, dict(x=x, y=y)


def render_standcard(st):
    TX, FX, Frame, rgb, mix, UW, UH, C = _mods()
    fr = Frame(1.0, 24, 10.0, "ui")
    TX.stand_card(fr, st["cn"], st["en"], 0, 9, colour=st.get("card", "#ffe040"), side="right")
    im, (x, y) = _crop(fr.ui)
    return im, dict(side="right", y=y)


def render_location(e):
    TX, FX, Frame, rgb, mix, UW, UH, C = _mods()
    fr = Frame(1.0, 24, 10.0, "ui")
    TX.location(fr, e["place"], e.get("sub", ""), 0, 9)
    im, (x, y) = _crop(fr.ui)
    return im, dict(x=x, y=y)


def render_chapter(e):
    """整屏 640×360：menace_bg 章节色 ×2 当底 + 第一行「序章　东京」（no 小一号）+ 第二行规划章名 + 小字英文。"""
    TX, FX, Frame, rgb, mix, UW, UH, C = _mods()
    cols = list(e.get("colours") or ["#402060", "#200830"])
    fr = Frame(0.0, 0, 10.0, "ui")
    FX.menace_bg(fr, 0.0, colours=tuple(cols))
    base = fr.img.convert("RGBA").resize((UW, UH), Image.NEAREST)
    d = ImageDraw.Draw(base)
    band = Image.new("RGBA", (UW, 150), (0, 0, 0, 120))
    base.alpha_composite(band, (0, 106))
    edge = mix(rgb(cols[0]), (255, 255, 255), 0.6) + (255,)
    d.rectangle((0, 104, UW, 105), fill=edge)
    d.rectangle((0, 256, UW, 257), fill=edge)
    title = TX.text_img(e.get("title", ""), "bold", 60, "#ffe040", outline="#2a0a3a", owidth=3, shadow="#000000")
    no = TX.text_img(e.get("no", ""), "bold", 30, "#ffffff", outline="#2a0a3a", owidth=2, shadow="#000000")
    gap = 18
    tw = no.width + gap + title.width
    x0 = (UW - tw) // 2
    yb = 182                                  # 第一行底边
    base.alpha_composite(no, (x0, yb - no.height - 6))
    base.alpha_composite(title, (x0 + no.width + gap, yb - title.height))
    if e.get("name"):
        nm = TX.text_img(e["name"], "bold", 28, "#ffffff", outline="#000000", owidth=2)
        base.alpha_composite(nm, ((UW - nm.width) // 2, 192))
    if e.get("en"):
        en = TX.text_img(e["en"], "bold", 14, "#f0e0a0", outline="#000000", owidth=1)
        base.alpha_composite(en, ((UW - en.width) // 2, 232))
    return base, {}


def render_title(e):
    TX = _mods()[0]
    im = TX.text_img(e["text"], "bold", int(e.get("size", 48)), e.get("colour", "#ffe040"),
                     outline=e.get("outline", "#2a0a3a"), owidth=int(e.get("owidth", 3)),
                     shadow=e.get("shadow", "#000000"))
    if e.get("sub"):
        sub = TX.text_img(e["sub"], "bold", max(14, int(e.get("size", 48)) // 4), e.get("subColour", "#ffffff"),
                          outline=e.get("outline", "#2a0a3a"), owidth=2)
        im = _vstack([im, sub], gap=0)
    return im, {}


def render_sfx(word, e):
    TX = _mods()[0]
    e = e or {}
    im = TX.text_img(word, "bold", int(e.get("size", 32)), e.get("colour", "#ffffff"),
                     outline=e.get("outline", "#000000"), owidth=int(e.get("owidth", 2)),
                     shadow=e.get("shadow"))
    return im, {}


def render_menace(ch):
    TX, FX, Frame, rgb, mix, UW, UH, C = _mods()
    return TX.text_img(ch, "bold", 36, C["menace"], outline="#1a0022", owidth=2), {}


def render_special(e):
    TX = _mods()[0]
    im = TX.text_img(e["text"], "bold", int(e.get("size", 48)), e.get("colour", "#ffe040"),
                     outline=e.get("outline", "#2a0a4a"), owidth=int(e.get("owidth", 3)),
                     shadow=e.get("shadow", "#000000"))
    return im, {}


def render_vs_mark():
    TX = _mods()[0]
    return TX.text_img("VS", "bold", 40, "#ff3048", outline="#ffffff", owidth=3, shadow="#000000"), {}


def render_vs(e):
    TX, FX, Frame, rgb, mix, UW, UH, C = _mods()
    name = TX.text_img(e["name"], "bold", 48, "#ffe040", outline="#2a0a3a", owidth=3)
    en = TX.text_img(e.get("en", ""), "bold", 14, "#ffffff", outline=(0, 0, 0), owidth=1)
    txt = TX.text_img(e.get("tag", "VS " + e["name"]), "bold", 16, "#ffffff", outline=(0, 0, 0), owidth=1)
    cols = e.get("colours") or ["#5a6a80", "#2a3040"]
    w, h = txt.width + 34, txt.height + 10
    tag = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(tag)
    d.polygon([(10, 0), (w - 1, 0), (w - 11, h - 1), (0, h - 1)], fill=(20, 10, 40, 230),
              outline=rgb(cols[0]) + (255,))
    d.polygon([(10, 0), (16, 0), (6, h - 1), (0, h - 1)], fill=rgb(cols[0]) + (255,))
    tag.alpha_composite(txt, (18, (h - txt.height) // 2))
    return name, en, tag


def render_panel(e):
    TX, FX, Frame, rgb, mix, UW, UH, C = _mods()
    w, h = int(e.get("w", 240)), int(e.get("h", 120))
    kind = e.get("kind", "note")
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    text = e.get("text", "")
    if kind == "note":
        paper = rgb(e.get("paper", "#f4efe2"))
        ink = e.get("ink", "#2a1a40")
        _round_rect(d, (3, 3, w - 1, h - 1), 4, fill=(0, 0, 0, 90))            # 浅阴影
        _round_rect(d, (0, 0, w - 4, h - 4), 4, fill=paper + (255,))
        # 纸巾的纤维纹理：Bayer 抖动出的浅色斑点（确定性）
        a = np.array(im)
        yy, xx = np.mgrid[0:h, 0:w]
        bay = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])[yy % 4, xx % 4] / 16.0
        noise = (np.sin(xx * 0.37 + yy * 0.11) * np.sin(yy * 0.29 - xx * 0.07) + 1) / 2
        m = (a[..., 3] == 255) & (noise * 0.35 > bay + 0.12)
        shade = np.array(mix(paper, (180, 170, 150), 0.25), np.uint8)
        a[m, :3] = shade
        im = Image.fromarray(a, "RGBA")
        size = int(e.get("size", 18))
        while True:
            lines = []
            for para in text.split("\n"):
                lines += TX.wrap(para, w - 28, "bold", size)
            imgs = [TX.text_img(ln or " ", "bold", size, ink) for ln in lines]
            th = sum(i.height for i in imgs) + 4 * (len(imgs) - 1)
            if th <= h - 20 or size <= 12:
                break
            size -= 2
        y = (h - 4 - th) // 2
        for i, li in enumerate(imgs):
            x = 12 + (i % 2) * 3                   # 手写的错落感
            im.alpha_composite(li, (x, y))
            y += li.height + 4
    else:   # plain：G.ui.box 同款底 + 宋体白字
        TX.box(im, 0, 0, w - 5, h - 5)
        y = 10
        for para in text.split("\n"):
            for ln in TX.wrap(para, w - 28, "pixel", 16):
                li = TX.text_img(ln or " ", "pixel", 16, "#ffffff", outline=(0, 0, 0))
                im.alpha_composite(li, (12, y))
                y += 22
    return im, dict(w=w, h=h)


def render_crash(e):
    TX, FX, Frame, rgb, mix, UW, UH, C = _mods()
    pe = e.get("plate", {})
    de = e.get("digits", {})
    digits = [TX.text_img(str(i), "bold", int(de.get("size", 24)), de.get("colour", "#3a2400"),
                          outline="#fff4c0", owidth=2) for i in range(10)]
    dw, dh = max(i.width for i in digits), max(i.height for i in digits)
    padded = []
    for i in digits:
        p = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
        p.alpha_composite(i, ((dw - i.width) // 2, (dh - i.height) // 2))
        padded.append(p)
    title = TX.text_img(pe.get("text", "乔瑟夫坠毁记录"), "bold", int(pe.get("size", 16)), pe.get("colour", "#3a2400"))
    sw, sh = dw + 12, dh + 6
    w = 12 + title.width + 12 + sw + 8
    h = max(title.height, sh) + 14
    plate = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(plate)
    fill = rgb(pe.get("fill", "#f0c040"))
    _round_rect(d, (0, 0, w - 1, h - 1), 6, fill=fill + (255,), outline=rgb(pe.get("border", "#fff4c0")) + (255,),
                width=2)
    d.line((6, 3, w - 7, 3), fill=mix(fill, (255, 255, 255), 0.5) + (255,))
    plate.alpha_composite(title, (12, (h - title.height) // 2))
    sx, sy = w - 8 - sw, (h - sh) // 2
    _round_rect(d, (sx, sy, sx + sw - 1, sy + sh - 1), 4, fill=mix(fill, (90, 60, 0), 0.25) + (255,),
                outline=mix(fill, (60, 40, 0), 0.5) + (255,))
    return plate, padded, dict(slot=[sx + 6, sy + 3, dw, dh]), dw, dh


def render_logo():
    from scenes import s00_opening as S0
    TX = _mods()[0]
    main = S0.logo_img("星尘斗士", 60)[0]
    sub = S0.logo_img("JOJO的奇妙冒险", 22, fills=("#ffffff", "#f0e8ff", "#d8c8ff"), outline="#3a1466",
                      rim="#12001e", edge="#12001e", shadow="#12001e")[0]
    subtitle = TX.text_img(S0.SUBTITLE, "bold", 16, "#f4e8ff", outline="#1a0630", owidth=2)
    return main, sub, subtitle


def render_tbc():
    from engine import fx as FX
    return FX._tbc_img()


# ============================================================ 主入口
def build(c, texts, stands):
    save = c["save_png"]
    meta = {}

    def put(key, im, extra=None):
        k = save(im, key, "core")
        d = dict(image=k, w=im.width, h=im.height)
        if extra:
            d.update(extra)
        return d

    main, sub, subtitle = render_logo()
    meta["logo"] = dict(main=put("ui/logo_main", main), sub=put("ui/logo_sub", sub),
                        subtitle=put("ui/subtitle", subtitle))
    meta["namecards"] = {}
    for k, e in texts.get("namecards", {}).items():
        im, ex = render_namecard(e)
        meta["namecards"][k] = put(f"ui/namecard/{k}", im, ex)
    meta["standcards"] = {}
    for k, st in stands.items():
        if not st.get("cn"):
            continue
        im, ex = render_standcard(st)
        meta["standcards"][k] = put(f"ui/standcard/{k}", im, ex)
    meta["locations"] = {}
    for k, e in texts.get("locations", {}).items():
        im, ex = render_location(e)
        meta["locations"][k] = put(f"ui/location/{k}", im, ex)
    meta["chapters"] = {}
    for k, e in texts.get("chapters", {}).items():
        im, ex = render_chapter(e)
        meta["chapters"][k] = put(f"ui/chapter/{k}", im, ex)
    meta["titles"] = {}
    for k, e in texts.get("titles", {}).items():
        im, ex = render_title(e)
        meta["titles"][k] = put(f"ui/title/{k}", im, ex)
    meta["sfx"] = {}
    for word, e in texts.get("sfx", {}).items():
        im, ex = render_sfx(word, e)
        meta["sfx"][word] = put(f"ui/sfx/{word}", im, ex)
    meta["menace"] = {}
    for ch in MENACE_CHARS:
        im, ex = render_menace(ch)
        meta["menace"][ch] = put(f"ui/menace/{ch}", im, ex)
    meta["specials"] = {}
    for k, e in texts.get("specials", {}).items():
        im, ex = render_special(e)
        meta["specials"][k] = put(f"ui/special/{k}", im, ex)
    mark, _ = render_vs_mark()
    meta["vs"] = {"mark": put("ui/vs/mark", mark)}
    for k, e in texts.get("vs", {}).items():
        name, en, tag = render_vs(e)
        meta["vs"][k] = dict(name=put(f"ui/vs/{k}_name", name), en=put(f"ui/vs/{k}_en", en),
                             tag=put(f"ui/vs/{k}_tag", tag), colours=list(e.get("colours") or []))
    meta["panels"] = {}
    for k, e in texts.get("panels", {}).items():
        im, ex = render_panel(e)
        meta["panels"][k] = put(f"ui/panel/{k}", im)
    plate, digits, pex, dw, dh = render_crash(texts.get("crash", {}))
    meta["crash"] = dict(plate=put("ui/crash/plate", plate, pex),
                         digits=[save(im, f"ui/crash/d{i}", "core") for i, im in enumerate(digits)], dw=dw, dh=dh)
    meta["tbc"] = put("ui/tbc", render_tbc())
    return meta


def _preview(path):
    """不写 assets：把全部预渲染图排成一张联系表（深色底）给人看。"""
    sys.path.insert(0, HERE)
    items = []

    def save_png(img, key, pack, sub=None):
        items.append((key, img.convert("RGBA")))
        return key

    texts = merge_texts(json.load(open(os.path.join(HERE, "registry", "ui_texts.json"), encoding="utf-8"))
                        if os.path.exists(os.path.join(HERE, "registry", "ui_texts.json")) else {})
    stands = copy.deepcopy(DEFAULT_STANDS)
    sp = os.path.join(HERE, "registry", "stands.json")
    if os.path.exists(sp):
        for k, v in json.load(open(sp, encoding="utf-8")).items():
            stands[k] = dict(stands.get(k, {}), **v)
    build(dict(save_png=save_png), texts, stands)
    W_ = 1280
    x = y = 0
    rowh = 0
    pos = []
    for key, im in items:
        if x + im.width > W_:
            x, y, rowh = 0, y + rowh + 6, 0
        pos.append((x, y))
        x += im.width + 6
        rowh = max(rowh, im.height)
    sheet = Image.new("RGBA", (W_, y + rowh + 6), (40, 44, 60, 255))
    d = ImageDraw.Draw(sheet)
    for i, ((key, im), (px, py)) in enumerate(zip(items, pos)):
        d.rectangle((px, py, px + im.width - 1, py + im.height - 1), fill=(60 + (i % 2) * 14, 64, 84, 255))
        sheet.alpha_composite(im, (px, py))
    sheet.convert("RGB").save(path)
    print(f"{len(items)} 张 → {path}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", required=True, help="联系表输出路径（PNG）")
    _preview(ap.parse_args().preview)
