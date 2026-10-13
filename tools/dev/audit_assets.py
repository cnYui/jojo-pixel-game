"""逐文件记录素材哈希和来源线索；技术核对不等同于版权许可证明。"""
from collections import Counter
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess

GAME = Path(__file__).resolve().parents[2]
MEDIA = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp3", ".wav", ".m4a", ".ogg", ".mp4", ".webm", ".ttf", ".ttc", ".otf"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="报告输出目录")
    parser.add_argument("--excluded-audio", type=Path, help="仅本地用于核对已排除歌曲的内容指纹")
    args = parser.parse_args()
    names = subprocess.check_output(["git", "-C", str(GAME), "ls-files", "-z"]).decode("utf-8").split("\0")
    audio = args.excluded_audio.read_bytes() if args.excluded_audio else None
    # 用去掉文件头的长片段核对二进制和内嵌 base64，减少误报。
    signatures = [audio[8192:12288], base64.b64encode(audio)[8192:12288]] if audio else []
    counts, rows, excluded_hits = Counter(), [], []
    for name in sorted(n for n in names if n):
        path = GAME / name
        if not path.is_file():
            continue
        data = path.read_bytes()
        if any(sig and sig in data for sig in signatures):
            excluded_hits.append(name)
        suffix = path.suffix.lower()
        if suffix in MEDIA:
            category = "媒体文件"
        elif name.startswith("data/") or "fixture" in name or name.startswith("tools/dev/p1/_gen/"):
            category = "内嵌资源或测试数据"
        elif suffix == ".json" and name.startswith(("assets/", "tools/art/", "tools/_meta/")):
            category = "素材元数据"
        else:
            category = "代码或文档"
        origin = "本仓库文件；未提供逐项分发授权证明"
        if "/font/" in name:
            origin = "构建器使用 Microsoft SimSun 生成的字形；许可待核实"
        elif name.startswith(("assets/audio/music/", "assets/audio/sfx/", "data/music/")) or name == "data/sfx.js":
            origin = "build_audio.py 及 game_music.py/game_sfx.py 的合成导出线索；原作表达权利另行核实"
        elif name.startswith("assets/video/"):
            origin = "render_cutscene.py 从仓库外动画工程导出的过场；内容权利待核实"
        elif name.startswith(("assets/chars/", "assets/props/", "assets/scene/")):
            origin = "build_assets.py 从原图集导出；包含同人角色和原作表达，分发权利待核实"
        elif name.startswith(("assets/chars_new/", "assets/props_new/", "assets/bg/")):
            origin = "仓库内美术配方或背景工具提供来源线索；同人表达和第三方权利待核实"
        counts[category] += 1
        rows.append({"文件": name, "字节数": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                     "类别": category, "来源线索": origin,
                     "授权状态": "仅原创代码可适用 MIT" if category == "代码或文档" else "待核实"})
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "文件清单.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    summary = {"核对文件数": len(rows), "类别": dict(counts), "已排除歌曲内容命中": excluded_hits,
               "边界": "逐文件清单、哈希及构建配方来源线索；没有逐幅人工鉴别及逐项版权许可证明。"}
    (args.out / "核对摘要.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if excluded_hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
