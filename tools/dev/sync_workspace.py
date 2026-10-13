"""比较本地游戏与发布克隆，按公开文件清单同步，默认只预览差异。"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def public_path(name):
    path = Path(name)
    return not (name.startswith("assets/audio/user/")
                or path.name == "title_song.js"
                or name.startswith("docs/ai/context/")
                or name.startswith("tools/art/") and path.name == "AGENTS.md")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="本地游戏仓库")
    parser.add_argument("--target", required=True, type=Path, help="公开仓库的发布克隆")
    parser.add_argument("--include", action="append", default=[], help="允许同步的新增文件，可重复传入")
    parser.add_argument("--apply", action="store_true", help="复制变更；不会提交、推送或删除文件")
    args = parser.parse_args()
    source, target = args.source.resolve(), args.target.resolve()
    if source == target or source in target.parents or target in source.parents:
        parser.error("源和目标必须是两个独立目录")
    remote = git(target, "remote", "get-url", "origin").decode().strip()
    if remote not in ("https://github.com/cnYui/jojo-pixel-game.git", "git@github.com:cnYui/jojo-pixel-game.git"):
        parser.error("目标 origin 不是 cnYui/jojo-pixel-game")
    if args.apply and git(target, "status", "--porcelain").strip():
        parser.error("目标存在未提交改动，请先收口，避免覆盖工作")
    names = set(git(source, "ls-files", "-z").decode("utf-8").split("\0")) - {""}
    for name in args.include:
        names.add(Path(name).as_posix())
    changed, blocked, missing = [], [], []
    for name in sorted(names):
        src, dst = (source / name).resolve(), (target / name).resolve()
        if not src.is_relative_to(source) or not dst.is_relative_to(target) or any(part.lower() == ".git" for part in Path(name).parts):
            parser.error("路径超出游戏目录：" + name)
        if not public_path(name):
            blocked.append(name)
            continue
        if not src.is_file():
            missing.append(name)
            continue
        if dst.is_file() and digest(src) == digest(dst):
            continue
        changed.append(name)
    # 先校验全部路径，避免后面的非法路径让同步只完成一半。
    if args.apply:
        for name in changed:
            src, dst = source / name, target / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
    print(json.dumps({"已复制" if args.apply else "待复制": changed,
                      "排除": blocked, "源文件缺失，需手动判断删除": missing}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
