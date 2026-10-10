# -*- coding: utf-8 -*-
r"""把原工程的场景渲成游戏过场视频（包 6，技术约定 §5.10 / 报告 09 附录 A）：mp4（H.264）+ webm（VP9），
**不往 源码\ 写任何东西**（源码\tools\render.py 会写 源码\out\，所以不调它的 main() / _encode_scene，
只复用 common.load_scene / render_frame / scene_frames 逐帧出图、render.build_audio 出混音）。

用法（PowerShell 先 $env:PYTHONDONTWRITEBYTECODE = 1）：
    python -B tools\render_cutscene.py --scenes s00 --name op --scale 2              # 片头（原芯片乐 title）
    python -B tools\render_cutscene.py --scenes s01 --name coffin --scale 2          # DIO 复活（原曲 ominous）
    python -B tools\render_cutscene.py --scenes s20 --name ending --scale 2          # 终章里程碑
    python -B tools\render_cutscene.py --scenes s02 --range 10.55 15.90 --name s02_action --no-music --gain -6
默认输出到 游戏\assets\video\；中间文件（无声视频、整段混音 wav）写到系统临时目录，用完删掉。

--scale   640×360 合成图的整数倍最近邻放大（1 → 640×360，2 → 1280×720，3 → 1920×1080）；游戏用 2（报告 09 §6.4）
--range   在拼接后的时间轴上截 [t0, t1)（秒；最好给 k/24 的帧格时刻）
--no-music  只混音效（插片：游戏 BGM 继续放）
--gain    整体增益 dB（插片叠在 BGM 上偏响时用，例 -6）
--orig-sprites  用原工程的精灵渲（只给前后对照用；正式视频别加）
剪辑点：每个场景内部的切点本来就踩着它自己的原曲节拍（s00 = title 143.55 bpm），这里原样保留原混音，所以不会错拍（D9）。

角色形象（2026-10-10，用户：“片头动画里乔瑟夫还是旧脸”）：渲染前先调 tools\cutscene_sprites.apply_game_redraws()，
在内存里照 tools\art\bake_art 的顺序导入 art_* 模块并做原名重画（二乔新脸 + 指人手臂分段、荷莉头前移；
承太郎按 bake_art.JOTARO_ADULT = False 保持原卡通大头），再把被换掉的精灵和游戏图集 assets\chars_new 逐像素核对，
不一致（= 图集没重烘）就报错退出、不出视频。镜头、时间、混音、其他角色都不动。
"""
import sys
sys.dont_write_bytecode = True                       # 在 import 原工程之前

import argparse  # noqa: E402
import os  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(HERE)
SRC = os.path.join(os.path.dirname(GAME), "源码")
sys.path.insert(0, os.path.join(SRC, "tools"))
sys.path.insert(0, SRC)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def ffmpeg(args, **kw):
    return subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + args, **kw)


def main(argv=None):
    ap = argparse.ArgumentParser(description="原工程场景 → 游戏过场视频（mp4 + webm）")
    ap.add_argument("--scenes", default="s00", help="逗号分隔，按前缀匹配 scenes.ORDER（s00 → s00_opening）")
    ap.add_argument("--out", default=os.path.join(GAME, "assets", "video"))
    ap.add_argument("--name", default="op")
    ap.add_argument("--scale", type=int, default=2)
    ap.add_argument("--range", type=float, nargs=2, metavar=("T0", "T1"))
    ap.add_argument("--no-webm", action="store_true")
    ap.add_argument("--no-music", action="store_true", help="只混音效（插片）")
    ap.add_argument("--gain", type=float, default=0.0, help="整体增益 dB")
    ap.add_argument("--crf", type=int, default=16, help="H.264 crf（webm 固定 VP9 crf 30）")
    ap.add_argument("--orig-sprites", action="store_true", help="用原工程精灵（只给前后对照用）")
    a = ap.parse_args(argv)

    from common import load_scene, render_frame, scene_frames  # noqa: E402  源码\tools\common.py（只读）
    from render import build_audio  # noqa: E402                         源码\tools\render.py（只用 build_audio）
    from engine.core import FPS, UW, UH  # noqa: E402

    T0 = time.time()
    if not a.orig_sprites:                           # 游戏层形象：必须在 import 场景模块之前（见 cutscene_sprites）
        import cutscene_sprites
        redrawn = cutscene_sprites.apply_game_redraws()
        bad = cutscene_sprites.check_atlas(redrawn)
        if bad:
            for name, fi, why in bad:
                print(f"  {name} 帧 {fi}：{why}")
            print("游戏层形象和 assets\\chars_new 图集不一致（先跑 art chars 重烘），不出视频")
            return 5
    os.makedirs(a.out, exist_ok=True)
    scenes, start = [], 0.0
    for nm in a.scenes.split(","):
        name, mod = load_scene(nm.strip())
        if a.no_music:
            mod.MUSIC = None                         # 只改内存里的模块对象，不碰源码文件
        n = scene_frames(mod)
        scenes.append([name, mod, start, n, set()])
        start += n / FPS
    total = start
    r0, r1 = (a.range if a.range else (0.0, total))
    r1 = min(r1, total)
    ow, oh = UW * a.scale, UH * a.scale

    tmp = tempfile.mkdtemp(prefix="jojo_cut_")
    vtmp = os.path.join(tmp, a.name + "_v.mp4")
    wav = os.path.join(tmp, a.name + "_full.wav")
    mp4 = os.path.join(a.out, a.name + ".mp4")
    webm = os.path.join(a.out, a.name + ".webm")
    try:
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{UW}x{UH}", "-r", str(FPS), "-i", "-", "-vf", f"scale={ow}:{oh}:flags=neighbor",
               "-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf), "-tune", "animation",
               "-pix_fmt", "yuv420p", "-g", "48", vtmp]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        nf = 0
        for name, mod, st, n, ev in scenes:
            for i in range(n):
                tg = st + i / FPS
                fr = render_frame(mod, name, i / FPS, i)
                ev.update(fr.events)                # 整场的音效提示都要收（截片时也一样）
                if r0 - 1e-6 <= tg < r1 - 1e-6:
                    p.stdin.write(fr.compose().convert("RGB").tobytes())
                    nf += 1
        p.stdin.close()
        if p.wait():
            print("ffmpeg 视频编码失败")
            return 2
        tv = time.time() - T0

        ok = build_audio([(s[0], s[1], s[2], s[3], sorted(s[4])) for s in scenes], wav)
        ta = time.time() - T0 - tv
        af = ["-af", f"volume={a.gain}dB"] if a.gain else []
        if ok:
            r = ffmpeg(["-i", vtmp, "-ss", f"{r0:.3f}", "-t", f"{r1 - r0:.3f}", "-i", wav, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy"] + af + ["-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                                                "-shortest", mp4])
        else:
            print("  （没有混音：只出画面）")
            r = ffmpeg(["-i", vtmp, "-c:v", "copy", "-movflags", "+faststart", mp4])
        if r.returncode:
            print("ffmpeg 合成 mp4 失败")
            return 3
        if not a.no_webm:
            r = ffmpeg(["-i", mp4, "-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0", "-deadline", "good",
                        "-cpu-used", "4", "-row-mt", "1", "-pix_fmt", "yuv420p", "-c:a", "libopus", "-b:a", "128k", webm])
            if r.returncode:
                print("ffmpeg 转 webm 失败")
                return 4
    finally:
        for f in (vtmp, wav):                       # 只删自己建的临时文件
            try:
                os.remove(f)
            except OSError:
                pass
        try:
            os.rmdir(tmp)
        except OSError:
            pass
    print(f"{a.name}: {nf} 帧 {ow}×{oh}（{nf / FPS:.3f} s），画面 {tv:.1f}s，混音 {ta:.1f}s，共 {time.time() - T0:.1f}s")
    for f in (mp4, webm):
        if os.path.exists(f):
            print(f"  {f}  {os.path.getsize(f) / 1e6:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
