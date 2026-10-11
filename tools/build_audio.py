"""JoJo 游戏的音频构建（包 1；技术约定 §5.9、§3.10、§3.14 F / G）。

    python -B tools\\build_audio.py                 # 增量（缓存命中的跳过）
    python -B tools\\build_audio.py --force         # 全部重做
    python -B tools\\build_audio.py --only punch0 battle title_song

也被 tools\\build_assets.py 的 audio 步调用：build_audio.run(args, c)。

做的事：
  1. 原工程 10 首配乐（engine.music）→ ffmpeg libmp3lame 128 kbps → assets\\audio\\music\\<名>.mp3 → data\\music\\<名>.js
  2. 原工程 64 个音效（engine.sfx，按 SFX_EXPORT 带参数 / 变体导出）+ tools\\game_sfx.py 的新合成音效
     → 96 kbps（单声道保持单声道）→ assets\\audio\\sfx\\<名>.mp3 → 全部合进 data\\sfx.js
  3. 用户给的 STAND PROUD：剪有效段 0.54–273.6 s → 192 kbps → assets\\audio\\user\\title_song.mp3 → data\\music\\title_song.js
  4. 元数据 tools\\_meta\\audio.json = { music: {…}, sfx: {…} }（data 步读进 GAME_DATA.audio）
编码延迟 encDelay 从 mp3 的 LAME 头读（读不到写 1105 并提醒）。缓存：assets\\audio\\.cache.json（配方 + 源码内容的哈希）。
受保护目录（源码 / 音频）只读：脚本第一句 dont_write_bytecode，不写任何东西进去。
"""
import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import base64  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402

import numpy as np  # noqa: E402

TOOLS = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(TOOLS)
SRC = os.path.normpath(os.path.join(GAME, '..', '源码'))
USER_SRC = os.path.normpath(os.path.join(GAME, '..', '音频', '用户提供'))
STAND_PROUD = os.path.join(USER_SRC, 'STAND_PROUD.m4a')

OUT_MUSIC = os.path.join(GAME, 'assets', 'audio', 'music')
OUT_SFX = os.path.join(GAME, 'assets', 'audio', 'sfx')
OUT_USER = os.path.join(GAME, 'assets', 'audio', 'user')
CACHE = os.path.join(GAME, 'assets', 'audio', '.cache.json')
DATA = os.path.join(GAME, 'data')
DATA_MUSIC = os.path.join(DATA, 'music')
META = os.path.join(TOOLS, '_meta', 'audio.json')
REPORT = os.path.join(TOOLS, 'dev', 'p1', '_out', 'audio_report.json')

SR = 44100
MUSIC_KBPS, SFX_KBPS, TITLE_KBPS = 128, 96, 192
TITLE_CUT = (0.54, 273.6)            # STAND PROUD 有效段（原文件上的时间）
DEFAULT_ENC_DELAY = 1105             # 576（LAME 编码延迟）+ 529（解码器延迟）
JS_HEAD = 'window.JOJO_AUDIO=window.JOJO_AUDIO||{music:{},sfx:{}};'


# ---------------------------------------------------------------- 导出清单
def _v(name, n, **kw):
    """带 seed 的变体组：<名>0..n-1，group = 原名。"""
    return [(f'{name}{i}', name, dict(kw, seed=i), name) for i in range(n)]


def _e(out, src=None, **kw):
    return (out, src or out, kw, None)


# (输出名, 原名, kwargs, group)。原工程 64 个全部导出（技术约定 §3.14 G 列出的 + 后面章节要的 8 个）。
SFX_EXPORT = (
    _v('punch', 4)
    + [_e('punch_heavy'), _e('whoosh')]
    + _v('slash', 2)
    + [
        _e('stab'), _e('thud'), _e('fire', dur=1.5), _e('fire_burst'), _e('emerald'), _e('vine'), _e('hamon'),
        _e('glass_break'), _e('menacing', dur=2.0), _e('menacing4', 'menacing', dur=4.0), _e('dododo', dur=2.0),
        _e('sting_reveal'), _e('sting_shock'), _e('sting_comedy'), _e('jingle_victory'), _e('tbc'),
        _e('blip'), _e('blip_train', dur=1.0), _e('glint'), _e('sparkle'), _e('zoom'), _e('freeze'), _e('pop'),
        _e('ding'), _e('heartbeat'), _e('charge'), _e('power_up'), _e('coin'),
    ]
    + _v('footstep', 4)
    + [
        _e('door'), _e('plane_engine', dur=3.0), _e('wind', dur=3.0), _e('crowd', dur=3.0), _e('explosion'),
        _e('crash'), _e('splash'), _e('water_gush', dur=1.6), _e('rumble', dur=2.0), _e('rero'),
        _e('camera_shutter'), _e('dog_bark'), _e('clock_tick'), _e('timestop'),
        _e('timestop_sp', 'timestop', pitch=0.92), _e('time_resume'), _e('knife_throw'), _e('knife_hit'),
        _e('roar'), _e('gunshot'), _e('drain'), _e('bubbles'), _e('car_engine', dur=3.0), _e('sand'),
        _e('ora_rush', dur=1.5),
        # 原工程其余 8 个（规划 §7.3 的 P1，后面章节用；一起导出，64 个全有）
        _e('muda_rush', dur=1.5), _e('ice'), _e('card_flip'), _e('bird_screech'), _e('tv_game'),
        _e('heli', dur=3.0), _e('thunder'), _e('bat_flap'),
    ]
)

# tools\game_sfx.py 新合成的（技术约定 §3.14 G「新合成」+「喊声」，外加 3 个环境音的无缝循环版）
NEW_EXPORT = (
    [_e(n) for n in ('metal_scrape', 'metal_crunch', 'water_splash', 'teeth_crunch', 'clay_crumble',
                     'lalala', 'water_jet', 'sand_storm', 'magnet_clack', 'train_horn', 'axe_chop',
                     'sub_alarm', 'genie_appear', 'roadroller', 'drip', 'baseball_hit', 'sax_melody',
                     'void_eat', 'knife_freeze', 'knife_volley', 'flatline', 'clang')]
    +
    [_e(n) for n in ('ora_loop', 'muda_loop', 'rapier_loop', 'timestop_hum', 'heartbeat_loop', 'insect_buzz_loop',
                     'fire_loop', 'crowd_loop', 'wind_loop', 'plane_engine_loop')]
    + [_e(n) for n in ('dodge', 'dodge_perfect', 'guard', 'parry', 'guard_break', 'crit', 'ko_hit', 'wall_slam',
                       'skid')]
    + [_e('stand_summon_' + k, 'stand_summon', kind=k) for k in ('star', 'hiero', 'red', 'chariot', 'purple',
                                                                 'fool', 'world')]
    + [_e(n) for n in ('stand_recall', 'meter_tick', 'meter_full', 'super_start', 'game_over_jingle',
                       'menu_move', 'menu_confirm', 'menu_cancel', 'menu_error',
                       'emerald_shot', 'hiero_tentacle', 'crossfire', 'armor_off')]
    + [_e('ora_voice', n=1), _e('muda_voice', n=1), _e('hora_voice', n=1)]
    + [_e('grunt_' + v, 'grunt', voice=v) for v in ('jotaro', 'kakyoin', 'polnareff', 'avdol', 'joseph', 'enemy', 'dio')]
    # 2026-10-10 晚第2章（南海）：猩猩叫、货轮汽笛、漩涡、海浪环境音（循环）、海鸥、船体吱嘎、打火机（tools\game_sfx.py）
    + [_e(n) for n in ('ape_screech', 'ship_horn', 'whirlpool', 'sea_loop', 'gulls', 'creak', 'lighter')]
    # 2026-10-11 第3章（新加坡）：剃刀、玩偶怪笑 / 窜动、冰箱、黏液 / 吸收、吊扇 / 街道 / 缆车 / 火车环境音（循环）（tools\game_sfx.py）
    + [_e(n) for n in ('razor', 'doll_voice', 'doll_scurry', 'fridge', 'slime', 'slime_absorb',
                       'fan_loop', 'city_loop', 'cable_loop', 'train_loop')]
)

ALL_SFX = SFX_EXPORT + NEW_EXPORT


def is_loop(name):
    return name.endswith('_loop') or name.endswith('_hum')


# ---------------------------------------------------------------- 工具
def log(*a):
    print(*a, flush=True)


def ffmpeg_bin():
    exe = shutil.which('ffmpeg')
    if not exe:
        raise SystemExit('build_audio: 找不到 ffmpeg（PATH 里没有）')
    return exe


def file_hash(*paths):
    h = hashlib.sha1()
    for p in paths:
        if os.path.exists(p):
            with open(p, 'rb') as f:
                h.update(f.read())
        h.update(b'|')
    return h.hexdigest()[:16]


def recipe_key(*parts):
    return hashlib.sha1(json.dumps(parts, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()[:20]


def encode_mp3(pcm, kbps, out_path, ff):
    """float32 PCM (N,) / (N, 2) → mp3（LAME，带 Xing/LAME 头，不写 ID3）。"""
    pcm = np.asarray(pcm, np.float32)
    ch = 1 if pcm.ndim == 1 else pcm.shape[1]
    data = np.ascontiguousarray(np.clip(pcm, -1.0, 1.0), dtype='<f4').tobytes()
    tmp = out_path + '.part'
    cmd = [ff, '-y', '-hide_banner', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', str(ch),
           '-i', 'pipe:0', '-c:a', 'libmp3lame', '-b:a', f'{kbps}k', '-map_metadata', '-1',
           '-id3v2_version', '0', '-write_id3v1', '0', '-write_xing', '1', '-f', 'mp3', tmp]
    r = subprocess.run(cmd, input=data, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'ffmpeg 失败 {out_path}: {r.stderr.decode("utf-8", "replace")[-400:]}')
    os.replace(tmp, out_path)


_BITRATES = {  # (MPEG1, layer3) / (MPEG2/2.5, layer3)
    1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0],
    2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0],
}


def lame_info(path):
    """读 mp3 第一帧的 Xing / Info + LAME 头 → {encDelay, padding, frames, samples}；读不到返回 None。
    encDelay = LAME 记的编码延迟 + 529（解码器延迟）= 不认 gapless 头的浏览器开头多出来的样本数。"""
    with open(path, 'rb') as f:
        b = f.read(4096)
    i = 0
    if b[:3] == b'ID3':
        sz = (b[6] << 21) | (b[7] << 14) | (b[8] << 7) | b[9]
        with open(path, 'rb') as f:
            f.seek(10 + sz)
            b = f.read(4096)
    while i < len(b) - 4 and not (b[i] == 0xFF and (b[i + 1] & 0xE0) == 0xE0):
        i += 1
    if i >= len(b) - 4:
        return None
    ver = (b[i + 1] >> 3) & 3          # 3 = MPEG1, 2 = MPEG2, 0 = MPEG2.5
    mode = (b[i + 3] >> 6) & 3         # 3 = 单声道
    mpeg1 = ver == 3
    side = (17 if mode == 3 else 32) if mpeg1 else (9 if mode == 3 else 17)
    x = i + 4 + side
    tag = b[x:x + 4]
    if tag not in (b'Xing', b'Info'):
        return None
    flags = int.from_bytes(b[x + 4:x + 8], 'big')
    p = x + 8
    frames = None
    if flags & 1:
        frames = int.from_bytes(b[p:p + 4], 'big')
        p += 4
    if flags & 2:
        p += 4
    if flags & 4:
        p += 100
    if flags & 8:
        p += 4
    if b[p:p + 4] not in (b'LAME', b'Lavc', b'Lavf') and not b[p:p + 4].isalnum():
        return None
    d = b[p + 21:p + 24]
    delay = (d[0] << 4) | (d[1] >> 4)
    pad = ((d[1] & 0x0F) << 8) | d[2]
    spf = 1152 if mpeg1 else 576
    samples = frames * spf - delay - pad if frames else None
    return {'encDelay': delay + 529, 'padding': pad, 'frames': frames, 'samples': samples}


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.part'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    os.replace(tmp, path)


def b64_of(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')


def seam_pct(x):
    """循环接缝的跳变落在全段相邻采样差的第几百分位（越小越好；< 95 就听不出接缝）。"""
    m = x if x.ndim == 1 else x.mean(axis=1)
    d = np.abs(np.diff(m))
    s = abs(float(m[0]) - float(m[-1]))
    return round(float((d < s).mean() * 100), 1)


# ---------------------------------------------------------------- 主流程
def build(force=False, only=None):
    t0 = time.time()
    from engine import music, sfx       # noqa: E402  （SRC 已在 sys.path；import 约 5 s）
    import game_sfx                      # noqa: E402,F401  登记新音效
    import game_music                    # noqa: E402       登记新曲（M1 为空）
    t_imp = time.time() - t0
    ff = ffmpeg_bin()
    for d in (OUT_MUSIC, OUT_SFX, OUT_USER, DATA_MUSIC, os.path.dirname(META), os.path.dirname(REPORT)):
        os.makedirs(d, exist_ok=True)
    try:
        with open(CACHE, encoding='utf-8') as f:
            cache = json.load(f)
    except (OSError, ValueError):
        cache = {}
    ver_sfx = file_hash(os.path.join(SRC, 'engine', 'sfx.py'), os.path.join(TOOLS, 'game_sfx.py'))
    ver_mus = file_hash(os.path.join(SRC, 'engine', 'music.py'), os.path.join(TOOLS, 'game_music.py'))
    want = set(only or [])

    def needed(name, key, path):
        if force or (want and name in want):
            return True
        c = cache.get(name)
        return not (c and c.get('key') == key and os.path.exists(path))

    pool = ThreadPoolExecutor(max_workers=max(2, min(8, (os.cpu_count() or 4))))
    jobs = []           # (name, future, finisher)
    meta_music, meta_sfx, report = {}, {}, {}
    n_render = 0

    # -------- 1. 配乐
    tracks = list(music.TRACKS) + [n for n in getattr(game_music, 'EXPORT', []) if n not in music.TRACKS]
    for name in tracks:
        mp3 = os.path.join(OUT_MUSIC, name + '.mp3')
        key = recipe_key('music', name, MUSIC_KBPS, ver_mus)
        if not needed(name, key, mp3):
            meta_music[name] = cache[name]['meta']
            continue
        x = np.asarray(music.track(name), np.float32)
        info = music.info(name)
        n_render += 1
        m = {'file': f'data/music/{name}.js', 'sec': round(len(x) / SR, 6), 'samples': int(len(x)),
             'encDelay': DEFAULT_ENC_DELAY, 'loopStart': 0, 'loopEnd': round(len(x) / SR, 6),
             'bpm': round(float(info['bpm']), 4), 'beatSec': round(float(info['beat_sec']), 6),
             'barSec': round(float(info['bar_sec']), 6)}
        report[name] = {'kind': 'music', 'seam_pct': seam_pct(x), 'peak': round(float(np.abs(x).max()), 3)}

        def fin(name=name, m=m, mp3=mp3, key=key):
            li = lame_info(mp3)
            if li:
                m['encDelay'] = li['encDelay']
                if li['samples'] is not None and li['samples'] != m['samples']:
                    log(f'  ! {name}: LAME 头算出 {li["samples"]} 样本，原长 {m["samples"]}')
            else:
                log(f'  ! {name}: 读不到 LAME 头，encDelay 写 {DEFAULT_ENC_DELAY}')
            meta_music[name] = m
            cache[name] = {'key': key, 'meta': m}
        jobs.append((name, pool.submit(encode_mp3, x, MUSIC_KBPS, mp3, ff), fin))

    # -------- 2. 音效
    for out, src, kw, group in ALL_SFX:
        mp3 = os.path.join(OUT_SFX, out + '.mp3')
        key = recipe_key('sfx', out, src, kw, SFX_KBPS, ver_sfx)
        if not needed(out, key, mp3):
            meta_sfx[out] = cache[out]['meta']
            if 'report' in cache[out]:
                report[out] = cache[out]['report']
            continue
        x = np.asarray(sfx.make(src, **kw), np.float32)
        n_render += 1
        pitch = float(kw.get('pitch', 1.0) or 1.0)
        m = {'sec': round(len(x) / SR, 4), 'ch': 1 if x.ndim == 1 else 2,
             'hit': round(float(sfx.HIT.get(src, 0.0)) / pitch, 4), 'loop': is_loop(out),
             'samples': int(len(x)), 'encDelay': DEFAULT_ENC_DELAY}
        if group:
            m['group'] = group
        rep = {'kind': 'new' if src in game_sfx.GAME else 'orig', 'src': src, 'kw': kw,
               'la': round(float(sfx.loudness(x)), 1), 'peak': round(float(np.abs(x).max()), 3)}
        if m['loop']:
            rep['seam_pct'] = seam_pct(x)
        report[out] = rep

        def fin(out=out, m=m, mp3=mp3, key=key, rep=rep):
            li = lame_info(mp3)
            if li:
                m['encDelay'] = li['encDelay']
            meta_sfx[out] = m
            cache[out] = {'key': key, 'meta': m, 'report': rep}
        jobs.append((out, pool.submit(encode_mp3, x, SFX_KBPS, mp3, ff), fin))

    # -------- 3. 标题曲 STAND PROUD（只在没有或 --force 时转）
    title_mp3 = os.path.join(OUT_USER, 'title_song.mp3')
    if force or ('title_song' in want) or not os.path.exists(title_mp3):
        if not os.path.exists(STAND_PROUD):
            log(f'  ! 找不到 {STAND_PROUD}，跳过标题曲')
        else:
            def conv():
                tmp = title_mp3 + '.part'
                cmd = [ff, '-y', '-hide_banner', '-loglevel', 'error', '-ss', str(TITLE_CUT[0]), '-to', str(TITLE_CUT[1]),
                       '-i', STAND_PROUD, '-vn', '-ar', str(SR), '-ac', '2', '-c:a', 'libmp3lame',
                       '-b:a', f'{TITLE_KBPS}k', '-map_metadata', '-1', '-id3v2_version', '0', '-write_id3v1', '0',
                       '-write_xing', '1', '-f', 'mp3', tmp]
                r = subprocess.run(cmd, capture_output=True)
                if r.returncode != 0:
                    raise RuntimeError('标题曲转码失败: ' + r.stderr.decode('utf-8', 'replace')[-400:])
                os.replace(tmp, title_mp3)
            n_render += 1
            jobs.append(('title_song', pool.submit(conv), lambda: None))

    # -------- 等编码
    for name, fut, fin in jobs:
        fut.result()
        fin()
    pool.shutdown()

    # -------- 用户提供的曲子（assets\audio\user\*.mp3）→ 音乐（长的走流式）
    for fn in sorted(os.listdir(OUT_USER)):
        if not fn.lower().endswith('.mp3'):
            continue
        name = os.path.splitext(fn)[0]
        p = os.path.join(OUT_USER, fn)
        li = lame_info(p) or {}
        samples = li.get('samples')
        if not samples:
            samples = count_samples(p, ff)
        sec = round(samples / SR, 3)
        m = {'file': f'data/music/{name}.js', 'sec': sec, 'samples': int(samples),
             'encDelay': li.get('encDelay', DEFAULT_ENC_DELAY), 'loopStart': 0, 'loopEnd': sec}
        if name == 'title_song' or sec > 60:
            m['stream'] = True
        meta_music[name] = m
        report[name] = {'kind': 'user', 'sec': sec, 'bytes': os.path.getsize(p)}

    # -------- 写运行时文件
    sizes = {}
    for name, m in meta_music.items():
        src_mp3 = os.path.join(OUT_USER if m.get('stream') or os.path.exists(os.path.join(OUT_USER, name + '.mp3'))
                               else OUT_MUSIC, name + '.mp3')
        js = os.path.join(DATA_MUSIC, name + '.js')
        if (force or not os.path.exists(js) or os.path.getmtime(js) < os.path.getmtime(src_mp3)
                or (want and name in want)):
            write_text(js, JS_HEAD + 'JOJO_AUDIO.music[' + json.dumps(name) + ']="' + b64_of(src_mp3) + '";\n')
        sizes['music/' + name] = os.path.getsize(js)
    parts = []
    for out, _src, _kw, _g in ALL_SFX:
        parts.append(json.dumps(out) + ':"' + b64_of(os.path.join(OUT_SFX, out + '.mp3')) + '"')
    sfx_js = os.path.join(DATA, 'sfx.js')
    write_text(sfx_js, JS_HEAD + 'Object.assign(JOJO_AUDIO.sfx,{' + ',\n'.join(parts) + '});\n')
    sizes['sfx'] = os.path.getsize(sfx_js)

    meta = {'music': {k: meta_music[k] for k in sorted(meta_music)},
            'sfx': {out: meta_sfx[out] for out, _s, _k, _g in ALL_SFX}}
    write_text(META, json.dumps(meta, ensure_ascii=False, indent=1) + '\n')
    write_text(CACHE, json.dumps(cache, ensure_ascii=False, indent=0, sort_keys=True))
    write_text(REPORT, json.dumps(report, ensure_ascii=False, indent=1, sort_keys=True) + '\n')

    dt = time.time() - t0
    log(f'build_audio: 配乐 {len(meta["music"])} 首、音效 {len(meta["sfx"])} 个（新合成 '
        f'{sum(1 for o, s, k, g in NEW_EXPORT)} 个）；本次渲染 {n_render} 个；import {t_imp:.1f} s，总 {dt:.1f} s')
    log(f'  data\\sfx.js {sizes["sfx"] / 1e6:.2f} MB；data\\music\\ 合计 '
        f'{sum(v for k, v in sizes.items() if k.startswith("music/")) / 1e6:.2f} MB')
    return meta, report


def count_samples(path, ff):
    """解码数样本（ffmpeg 自己会认 gapless 头）。只在读不到 LAME 头时用。"""
    r = subprocess.run([ff, '-hide_banner', '-loglevel', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(SR),
                        'pipe:1'], capture_output=True)
    return len(r.stdout) // 2


def print_report(report):
    rows = [(k, v) for k, v in sorted(report.items()) if v.get('kind') == 'new']
    log('新合成音效的感知响度（sfx.loudness，A 计权 100 ms 最大值，dB）：')
    for k, v in rows:
        extra = f'  接缝 {v["seam_pct"]} 百分位' if 'seam_pct' in v else ''
        log(f'  {k:20s} LA {v["la"]:6.1f}  峰值 {v["peak"]:.2f}{extra}')
    loops = [(k, v) for k, v in sorted(report.items()) if v.get('kind') == 'music']
    for k, v in loops:
        log(f'  配乐 {k:10s} 接缝 {v["seam_pct"]} 百分位  峰值 {v["peak"]}')


def run(args, c=None):
    """build_assets.py 的 audio 步入口。args：命令行参数列表（同下）；c 不用（路径都按本文件位置算）。"""
    ap = argparse.ArgumentParser(prog='build_audio.py', description='JoJo 游戏音频构建（包 1）')
    ap.add_argument('--force', action='store_true', help='忽略缓存，全部重做')
    ap.add_argument('--only', nargs='*', default=None, help='只重做这些名字（音乐 / 音效 / title_song）')
    ap.add_argument('--report', action='store_true', help='打印新音效响度和接缝表')
    a = ap.parse_args(list(args or []))
    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    if TOOLS not in sys.path:
        sys.path.append(TOOLS)
    meta, report = build(force=a.force, only=a.only)
    if a.report:
        print_report(report)
    return meta


if __name__ == '__main__':
    run(sys.argv[1:])
