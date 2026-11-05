# 第四部标题曲（只在本地用）：用户指定的歌（2026-11-05 起是《Great Days》Break Down 1 分钟持续版）是商业歌曲，不随仓库分发。
#   转好的 mp3 放 第四部/assets/audio/user/title_song.mp3，打出来的 游戏/data/music/title_song.js，两样都在 .gitignore 里。
#   构建要显式加 --include-user-audio 才把它登记成标题曲（照第三部 build_audio.py 的同名开关）：默认构建的 data_meta.js
#   里没有 title_song，标题照旧放仓库里自写的芯片音乐 title，所以平时重跑 build_p4.py 提交生成文件，不会让公开版指向一个不存在的文件。
#   用法：
#     python3 第四部/tools/p4_title_song.py 源音频 [--ss 秒] [--to 秒] [--xfade 秒] [--gain dB]
#         转码成 44.1 kHz 立体声 192 kbps mp3；响度默认对齐芯片音乐 title（混好的流行歌比它响一大截，进第一章会突然变小声）。
#         整个文件就是一圈循环（引擎整首循环）：--ss / --to 取歌里重复段的整数个周期，--xfade 把 --ss 之前那一小段
#         交叉淡入到结尾，接回开头时波形是连着的，不会咔一下
#     python3 第四部/tools/build_p4.py --no-font --include-user-audio
#         打进 游戏/data/music/title_song.js，data_meta 里登记 title_song（流式），标题画面改放它
import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
P4 = os.path.normpath(os.path.join(HERE, '..'))
USER_DIR = os.path.join(P4, 'assets', 'audio', 'user')
USER_MP3 = os.path.join(USER_DIR, 'title_song.mp3')
MUSIC_DIR = os.path.join(P4, '游戏', 'data', 'music')
SONG_JS = os.path.join(MUSIC_DIR, 'title_song.js')
CHIP_JS = os.path.join(MUSIC_DIR, 'title.js')
SR, KBPS = 44100, 192
DEFAULT_ENC_DELAY = 1105             # 576（LAME 编码延迟）+ 529（解码器延迟），和第三部一样
JS_HEAD = 'window.JOJO_AUDIO=window.JOJO_AUDIO||{music:{},sfx:{}};'


def ffmpeg():
    exe = shutil.which('ffmpeg')
    if not exe:
        raise SystemExit('p4_title_song: 找不到 ffmpeg（PATH 里没有）')
    return exe


def lame_info(path):
    """读 mp3 第一帧的 Xing / Info + LAME 头 → {encDelay, samples}；读不到返回 None（同第三部 build_audio.lame_info）。"""
    with open(path, 'rb') as f:
        b = f.read(4096)
        if b[:3] == b'ID3':
            f.seek(10 + ((b[6] << 21) | (b[7] << 14) | (b[8] << 7) | b[9]))
            b = f.read(4096)
    i = 0
    while i < len(b) - 4 and not (b[i] == 0xFF and (b[i + 1] & 0xE0) == 0xE0):
        i += 1
    if i >= len(b) - 4:
        return None
    mpeg1 = ((b[i + 1] >> 3) & 3) == 3
    mono = ((b[i + 3] >> 6) & 3) == 3
    x = i + 4 + ((17 if mono else 32) if mpeg1 else (9 if mono else 17))
    if b[x:x + 4] not in (b'Xing', b'Info'):
        return None
    flags = int.from_bytes(b[x + 4:x + 8], 'big')
    p, frames = x + 8, None
    if flags & 1:
        frames = int.from_bytes(b[p:p + 4], 'big')
        p += 4
    p += (4 if flags & 2 else 0) + (100 if flags & 4 else 0) + (4 if flags & 8 else 0)
    d = b[p + 21:p + 24]
    if len(d) < 3 or not frames:
        return None
    delay, pad = (d[0] << 4) | (d[1] >> 4), ((d[1] & 0x0F) << 8) | d[2]
    return {'encDelay': delay + 529, 'samples': frames * (1152 if mpeg1 else 576) - delay - pad}


def loudness(path):
    """EBU R128 整体响度（LUFS）和真峰值（dBTP）。"""
    r = subprocess.run([ffmpeg(), '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    tail = r.stderr[r.stderr.rfind('Summary:'):]
    i = re.search(r'I:\s*(-?[\d.]+) LUFS', tail)
    pk = re.search(r'Peak:\s*(-?[\d.]+|-inf) dBFS', tail)
    if not i:
        raise SystemExit('p4_title_song: 量不出响度：' + path)
    return float(i.group(1)), (float(pk.group(1)) if pk and pk.group(1) != '-inf' else -99.0)


def chip_loudness():
    """芯片音乐 title 的响度：从 data/music/title.js 里把 base64 的 mp3 解出来量。"""
    s = open(CHIP_JS, encoding='utf-8').read()
    b64 = s[s.index(']="') + 3:s.rindex('"')]       # 格式：…JOJO_AUDIO.music["title"]="<base64>";
    with tempfile.TemporaryDirectory() as td:
        fp = os.path.join(td, 'title.mp3')
        with open(fp, 'wb') as fh:
            fh.write(base64.b64decode(b64))
        return loudness(fp)


def loop_graph(ss, to, xfade):
    """[ss, to] 这一段的结尾和 [ss - xfade, ss] 交叉淡化：长度不变，结尾的最后一刻正好接上开头。
    同一首歌前后两段是相关的信号，用线性（tri）等增益淡化，响度不会在接缝处鼓起来或塌下去。"""
    # 同一个文件读两遍（两个 -i）：用 asplit 分两路的话，短的那路先结束，ffmpeg 6.1 的 acrossfade 会什么都不输出
    return (f'[0:a]atrim=start={ss}:end={to},asetpts=PTS-STARTPTS[a];'
            f'[1:a]atrim=start={ss - xfade}:end={ss},asetpts=PTS-STARTPTS[b];[a][b]acrossfade=d={xfade}:c1=tri:c2=tri')


def convert(src, ss=None, to=None, gain=None, xfade=0.0):
    if xfade and (ss is None or to is None or ss < xfade):
        raise SystemExit('p4_title_song: --xfade 要同时给 --ss 和 --to，而且 --ss 不能小于淡化长度')
    # 不淡化：-ss / -to 放在 -i 前面直接剪；淡化：整段交给滤镜图（atrim 按样本剪）
    inp = [] if xfade else (['-ss', str(ss)] if ss is not None else []) + (['-to', str(to)] if to is not None else [])
    graph = loop_graph(ss, to, xfade) if xfade else None
    head = [ffmpeg(), '-y', '-hide_banner', '-loglevel', 'error', *inp, '-i', src, *(['-i', src] if xfade else []), '-vn']
    if gain is None:
        target, _ = chip_loudness()
        with tempfile.TemporaryDirectory() as td:
            probe = os.path.join(td, 'cut.wav')
            subprocess.run(head + (['-filter_complex', graph] if graph else []) + ['-ar', str(SR), '-ac', '2', probe], check=True)
            have, peak = loudness(probe)
        gain = target - have
        # 歌比芯片音乐轻的时候往上推，别推到削顶：真峰值留 1 dB
        gain = min(gain, -1.0 - peak)
        print(f'  响度：芯片音乐 title {target:.1f} LUFS，这首 {have:.1f} LUFS（峰值 {peak:.1f} dBTP）→ 增益 {gain:+.1f} dB')
    os.makedirs(USER_DIR, exist_ok=True)
    tmp = USER_MP3 + '.part'
    filt = ['-filter_complex', graph + f',volume={gain:.2f}dB'] if graph else ['-af', f'volume={gain:.2f}dB']
    cmd = head + filt + ['-ar', str(SR), '-ac', '2', '-c:a', 'libmp3lame', '-b:a', f'{KBPS}k', '-map_metadata', '-1',
                         '-id3v2_version', '0', '-write_id3v1', '0', '-write_xing', '1', '-f', 'mp3', tmp]
    subprocess.run(cmd, check=True)
    os.replace(tmp, USER_MP3)
    li = lame_info(USER_MP3) or {}
    print(f'  写好 {USER_MP3}（{os.path.getsize(USER_MP3) / 1024:.0f} KB，{(li.get("samples") or 0) / SR:.2f} s）')
    print('  下一步：python3 第四部/tools/build_p4.py --no-font --include-user-audio')


def register(gd):
    """build_p4.py --include-user-audio 时调：有 title_song.mp3 就写 data/music/title_song.js、登记成流式标题曲，返回 True。"""
    if not os.path.isfile(USER_MP3):
        print('  （--include-user-audio：没有 第四部/assets/audio/user/title_song.mp3，标题照旧放芯片音乐 title）')
        return False
    li = lame_info(USER_MP3)
    if li:
        samples, delay = li['samples'], li['encDelay']
    else:
        r = subprocess.run([ffmpeg(), '-hide_banner', '-loglevel', 'error', '-i', USER_MP3, '-f', 's16le', '-ac', '1',
                            '-ar', str(SR), 'pipe:1'], capture_output=True, check=True)
        samples, delay = len(r.stdout) // 2, DEFAULT_ENC_DELAY
    sec = round(samples / SR, 3)
    with open(USER_MP3, 'rb') as fh:
        b64 = base64.b64encode(fh.read()).decode('ascii')
    os.makedirs(MUSIC_DIR, exist_ok=True)
    with open(SONG_JS + '.tmp', 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(JS_HEAD + 'JOJO_AUDIO.music[' + json.dumps('title_song') + ']="' + b64 + '";\n')
    os.replace(SONG_JS + '.tmp', SONG_JS)
    # 整首循环。一分多钟的歌解码成 AudioBuffer（立体声 float，一分钟约 21 MB），循环接缝按样本对齐、没有空隙；
    #   像第三部 STAND PROUD 那样四五分钟的才走流式 <audio loop>（省内存，但每圈接回开头会有一点停顿）
    m = {'file': 'data/music/title_song.js', 'sec': sec, 'samples': int(samples), 'encDelay': delay, 'loopStart': 0, 'loopEnd': sec}
    if sec > 90:
        m['stream'] = True
    gd['audio']['music']['title_song'] = m
    gd['packs']['bg_title']['music'] = ['title_song']
    print(f'  标题曲 title_song：{sec:.2f} s（{"流式" if m.get("stream") else "解码后循环"}），'
          f'data/music/title_song.js {os.path.getsize(SONG_JS) / 1024:.0f} KB（只在本地，不进仓库）')
    return True


def main():
    ap = argparse.ArgumentParser(description='把用户给的歌转成第四部本地标题曲')
    ap.add_argument('src', help='源音频（任何 ffmpeg 读得了的格式）')
    ap.add_argument('--ss', type=float, default=None, help='从源文件第几秒开始')
    ap.add_argument('--to', type=float, default=None, help='到源文件第几秒结束')
    ap.add_argument('--xfade', type=float, default=0.0, help='循环接缝的交叉淡化秒数（要同时给 --ss / --to）')
    ap.add_argument('--gain', type=float, default=None, help='手动增益 dB（不给就对齐芯片音乐 title 的响度）')
    a = ap.parse_args()
    if not os.path.isfile(a.src):
        raise SystemExit('p4_title_song: 找不到 ' + a.src)
    convert(a.src, a.ss, a.to, a.gain, a.xfade)


if __name__ == '__main__':
    sys.exit(main())
