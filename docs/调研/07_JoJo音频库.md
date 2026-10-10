# 07 JoJo 音频库调研：配乐 + 音效（给实现工程师）

> 2026-10-09，只读调研。读了 `源码\engine\music.py`（1301 行）、`sfx.py`（1911 行）、`core.py`（音频只有 `Frame.sfx`）、`tools\render.py` 的混音段、`docs\AUDIO_music.md`、`docs\AUDIO_sfx.md`。
> 所有试跑都在会话 scratchpad：`C:\Users\yui\AppData\Local\Temp\claude\D----\dd592801-8a86-495b-83a0-71d863169d18\scratchpad\understand\audio07\`（会话删了就没了，关键代码已抄进本文附录）。源码目录没有留下 `__pycache__`（跑完查过）。

---

## 0. 结论速览

1. **原工程的声音全是现场合成，磁盘上没有一个音频文件。** 10 首原创芯片音乐（`engine/music.py`，tracker 式文本记谱 + numpy 合成）+ 64 个音效（`engine/sfx.py`，numpy/scipy 合成）。要给网页游戏用，必须先用 Python 离线渲染成文件。
2. **实测可行，而且很快**：`import` 约 5 s（scipy）；10 首全部渲染 15.9 s（单首 0.74–2.94 s）；64 个音效全部 1.9 s。输出都是 44100 Hz float32；配乐 `(N, 2)` 立体声，音效单声道 `(N,)` 或立体声 `(N, 2)`。没有削波、没有直流、音效首尾都是 0。
3. **配乐每首就是一整段无缝循环**：循环点 = 整段（loopStart 0，loopEnd = N 个样本），尾巴（音符余音、乒乓延迟、混响）都已经折回开头。实测接缝处的跳变只落在普通相邻采样差的 21–84 百分位，等于没有接缝。
4. **网页接入要走 WebAudio + base64 内嵌 .js**：`file://` 双击打开时 `fetch()` 本地文件会失败（Chromium 实测 `TypeError: Failed to fetch`），但把 mp3 base64 写进 `<script src>` 加载的 .js、再 `decodeAudioData` 完全可行。Chromium 实测 mp3 / ogg / opus / m4a 解码后的长度和原 wav **一个样本都不差**（编码延迟被剥掉，起点偏移 0），所以 `AudioBufferSourceNode.loop = true` 能做到无缝循环。银魂用的是 HTMLAudio + mp3（`银魂\游戏\engine\core.js` 第 128–188 行），JoJo 这边欧拉连打每秒 16 下、要变速变调、时停要把 BGM “拖停”，HTMLAudio 做不了，建议换 WebAudio。
5. **缺的音效约 40 个**。其中 17 个（按变体算 30 个文件）已经只用 `sfx.py` 现成的辅助函数在 scratch 做出原型、测了响度和循环接缝（附录 A 是完整代码，可以直接搬进 `游戏\tools\game_sfx.py`）：欧拉 / 木大 / 银色战车刺击的无缝循环、时停“嗡”声循环、闪避、格挡、完美格挡、暴击、KO、替身召唤（7 种替身配色）、能量满、必杀启动、菜单 4 个、受伤喊声（7 种声线）、合成“O-RA!”人声。
6. **新曲也能加**：在游戏侧写 `music.Song(...)` 的构建函数，运行时塞进 `music._BUILDERS`，不用改源码。试写了一首 16 小节的埃及风战斗曲 `battle_egypt`（E 弗里几亚，160 bpm），渲染 1.94 s，记谱的小节校验全部通过（附录 B）。

---

## 1. 文件与入口（行号以 2026-10-09 的源码为准）

| 文件 | 位置 | 内容 |
|---|---|---|
| `源码\engine\music.py` | L41 `SR = 44100`；L42 `_PAD = 4 s`（渲染时多留 4 s 给尾巴）；L45 `TRACKS` | 曲目说明字典 |
|  | L168–321 振荡器：`_blep` `_pulse` `_saw` `_tri`（NES 4-bit 阶梯三角）`_table`（叠加方波“管风琴”波表）`_osc` `_adsr` `_note` | 合成器 |
|  | L324–448 `_lfsr` `_lnoise` `_drum(name)` `_KIT` | LFSR 噪声鼓组 |
|  | L451–508 `_pan` `_fold`（尾巴折回）`_tone`（零相位圆周 HP/LP/低架）`_pingpong`（`np.roll` 圆周延迟）`_reverb`（圆周 FFT 卷积混响） | 循环安全的效果器 |
|  | L554–901 `class Song`：`chords` `parse` `bass` `arp` `stabs` `pad` `harmonize` `voice` `drums` `render` | 记谱 + 渲染 |
|  | L905–925 乐器预设：`LEAD` `LEAD50` `HARM` `CHIP` `STAB` `PLUCK` `TRIBASS` `FMBASS` `ORGAN` `PAD` `BELL` `TRILEAD` `BRASS` | |
|  | L933–1263 十首曲子的构建函数 `_t_title` … `_t_ending`；L1266 `_BUILDERS` | 乐谱 |
|  | L1273 `_rendered`（`lru_cache`）；L1283 `info(name)`；L1290 `track(name)`；L1295 `song(name)`；L1300 `render_all()` | 对外 API |
| `源码\engine\sfx.py` | L35 `SR = 44100`；L44 `_reg`；L53 `make(name, **kw)`；L71 `_LA`（感知响度目标）；L87 `_PUSH_MAX`；L91 `_SAT_OK`；L105 `_level`；L131 `_build`；L152 `HIT`（同步点） | 对外 API + 响度体系 |
|  | L162–632 辅助函数（见 §3.6 速查表） | 合成积木 |
|  | L634–1911 64 个音效生成函数，每个用 `@_reg('名字', '说明')` 注册 | |
| `源码\engine\core.py` | L209 `self.events`；L217–220 `Frame.sfx(name, at, **kw)` | 影片里每帧登记音效（去重），游戏不需要 |
| `源码\tools\render.py` | L57–182 `build_audio()` | 影片的混音器（游戏要照抄它的参数，见 §3.7） |

注意：两份 docs 里提到的校验脚本 `out/tmp/music/check.py`、`out/tmp/sfx/check.py`、`seamtest.py`、`loud.py` **不在源码里**（没有 `out\` 目录）。本次用 scratch 里自己写的脚本代替（§4、附录 C）。

依赖：numpy 2.5.3、scipy 1.16.3（本机都有）。`music.py` 只有 `_reverb` 用 scipy；`sfx.py` 顶层就 `import scipy.signal / scipy.ndimage`。

---

## 2. 配乐 `engine/music.py`

### 2.1 API

```python
import sys; sys.dont_write_bytecode = True          # 别在源码里留 __pycache__
sys.path.insert(0, r'D:\大疆\游戏素材\JoJo\源码')
from engine import music
music.SR             # 44100
music.TRACKS         # {name: 英文说明}
x = music.track('battle')   # float32 (N, 2)，一整段无缝循环，只读（setflags(write=False)），进程内缓存
music.info('battle')        # {'bpm','beats_per_bar','bars','bar_sec','beat_sec','loop_sec','key'}，不渲染音频，很便宜
S = music.song('battle')    # 渲染后的 Song 对象（voices / prog / step_n …）
```

### 2.2 一首曲子是怎么渲染出来的（`Song.render`，L836–901）

1. 每个声部（`voice`）的每个音符用 `_note(inst, pitches, dur, vel)` 合成（ADSR、揉弦 `vib`、滑音 `bend`、芯片琶音 `arp_rate`、`trem`、`detune`），按 `Song.time(step)` 放进长 `L + 4 s` 的缓冲；`swing` 只影响 `time()`。
2. 鼓：`drums()` 的字符串一格一个 16 分音符，查 `_KIT` 表，每下随机 ±6 % 力度。
3. `_fold(…, L)` 把超出 `L` 的尾巴加回开头 → 再做乒乓延迟（`np.roll`，圆周）和 FFT 圆周混响 → 所以首尾天然相接。
4. 母带 `_tone(hp=38, lp=15500, shelf_db=low_shelf)`（零相位圆周滤波，110 Hz 以下 −4 dB，boss −6 dB）→ RMS 拉到 `rms_target`（0.165–0.21）→ 软膝限幅（膝点 0.72，天花板 0.9）→ 减均值去直流。
5. 速度微调：`step_n = _smooth(60*SR/bpm/4)`，让一个 16 分音符正好是整数个样本、且质因数只有 2/3/5/7，所以循环长度 `L = 小节数 × 16 × step_n` 精确落在样本上。真实 bpm 见下表 `bpm_exact`。

### 2.3 十首曲子（实测，scratch `out\report_all.json`）

| 名字 | 调式 / 拍号 | bpm_exact | 小节 | 每小节 s | 每拍 s | **循环长度 s** | **循环样本数** | RMS | 峰值 | 渲染 s | 影片用在 | 游戏建议用途 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `title` | E 小调 4/4 | 143.555 | 24 | 1.6718 | 0.4180 | 40.124 | 1769472 | 0.200 | 0.898 | 1.77 | s00 | 标题曲用户指定 STAND PROUD，这首改作“出发 / 章节开场 / 地图界面”；含英雄动机 |
| `ominous` | C 和声小调 4/4 | 71.777 | 12 | 3.3437 | 0.8359 | 40.124 | 1769472 | 0.170 | 0.896 | 2.21 | s01 s03 s14 s16 | DIO 登场、DIO 馆探索、敌方阴谋剧情 |
| `daily` | G 大调 swing | 132.300 | 16 | 1.8141 | 0.4535 | 29.025 | 1280000 | 0.180 | 0.864 | 0.86 | s02 | 城镇 / 搞笑剧情 / 和 NPC 闲聊 |
| `travel` | D 大调→D 小调 | 120.536 | 16 | 1.9911 | 0.4978 | 31.858 | 1404928 | 0.190 | 0.892 | 1.32 | s06 s08 s11 | 大地图移动、旅途剧情（B 段异域风可当中东段） |
| `battle` | A 小调 4/4 | 168.750 | 20 | 1.4222 | 0.3556 | 28.444 | 1254400 | 0.200 | 0.899 | 1.18 | s04 s07 s10 s12 | 普通替身战 |
| `tension` | D 多利亚 4/4 | 108.000 | 16 | 2.2222 | 0.5556 | 35.556 | 1568000 | 0.180 | 0.883 | 1.43 | s09 s13 s15 | 敌人地盘探索、调查、悬疑剧情、战前对峙 |
| `sad` | A 小调 3/4 | 75.617 | 16 | 2.3804 | 0.7935 | 38.087 | 1679616 | 0.165 | 0.670 | 1.91 | s05 s13 s15 | 同伴牺牲（阿布德尔 / 伊奇 / 花京院）、回忆 |
| `boss` | C 小调 4/4 | 172.266 | 24 | 1.3932 | 0.3483 | 33.437 | 1474560 | 0.210 | 0.895 | 1.53 | s17 s18 | 最终战 DIO（也可给瓦尼拉·艾斯） |
| `victory` | E 大调 4/4 | 132.300 | 12 | 1.8141 | 0.4535 | 21.769 | 960000 | 0.200 | 0.883 | 0.74 | s19 | 章节通关结算画面（战斗赢了的短号角用音效 `jingle_victory`） |
| `ending` | D 大调 4/4 | 91.875 | 16 | 2.6122 | 0.6531 | 41.796 | 1843200 | 0.175 | 0.807 | 2.94 | s20 | 结局、制作人员表 |

- 合计 340.2 s 音频；10 首串行渲染 15.89 s（不含 ~5 s 的 import）。
- 英雄动机 `E5. B4 E5 F#5 | G5 – F#5 E5`：`title` 第 3 小节、`boss` 第 11 小节（承太郎反击）、`victory` 第 1 小节、`ending` 第 1 小节。DIO 动机：`ominous` 第 1 小节、`boss` 第 3 小节。做剧情演出可以按 `bar_sec` 卡点：第 k 小节在 `k × bar_sec` 秒，第 k 拍在 `k × beat_sec` 秒。
- **每首都从第 1 小节开始就是主旋律**（影片只播前 8–16 秒，作者专门这样编的），游戏里从头循环正好。

### 2.4 循环点与接缝实测

`循环 = 整段`：WebAudio 里 `src.loop = true; src.loopStart = 0; src.loopEnd = buf.duration`（或干脆不设 loopStart/End，默认就是整段）。

接缝实测（首样本与末样本之差 vs. 全曲相邻采样差的分布）：

| 曲 | 接缝跳变 | 落在百分位 | 全曲 p99 |
|---|---|---|---|
| battle | 0.0563 | 74.0 | 0.236 |
| boss | 0.0741 | 76.2 | 0.285 |
| tension | 0.0451 | 83.7 | 0.215 |
| 其余 7 首 | 0.009–0.014 | 21–59 | 0.054–0.240 |

结论：接缝就是一次普通的采样步进，无咔哒声。**不要**想当然地把 loopStart 设到第 3 小节（跳过前奏）——尾巴是折回第 1 小节的，从别处起循环会丢掉那段混响尾巴，曲子末尾的乐句也是写来接回第 1 小节的。

### 2.5 渲染成 wav（试跑代码，scratch `render_test.py`）

```python
import wave, numpy as np
x = music.track(name)                                   # float32 (N, 2)
pcm = (np.clip(x, -1, 1) * 32767).astype('<i2')
with wave.open(path, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(44100); w.writeframes(pcm.tobytes())
```
然后 `ffmpeg -i x.wav -c:a libmp3lame -b:a 128k x.mp3`。不用装 soundfile。

### 2.6 加新曲（不改源码）

```python
from engine import music
from engine.music import Song, LEAD, HARM, BRASS, CHIP, PLUCK, TRIBASS, FMBASS
def _t_battle_egypt():
    S = Song('battle_egypt', bpm=160, bars=16, key='E', mode='phrygian', seed=123)
    S.chords('E:16 | F:8 E:8 | ...')         # 和弦进行，总长必须正好 = 小节数 × 16 步，否则 ValueError
    S.voice(S.parse(melody), LEAD, pan=-0.08, dly=0.18, rev=0.08, name='lead')
    ...
    S.drums('c...k.t.k.k.t...' * …)          # 每小节 16 个字符
    S.rms_target = 0.2
    return S
music._BUILDERS['battle_egypt'] = _t_battle_egypt
music.TRACKS['battle_egypt'] = '...'
music.track('battle_egypt')                  # 1.94 s 渲染，23.89 s 循环，峰值 0.890，RMS 0.200
```
完整可跑的版本见附录 B。记谱规则见 `docs\AUDIO_music.md` 第 67–89 行：时值以 16 分音符为单位且“粘滞”、`r` 休止、`~` 延音、`[..]` 和弦、`!` 重音、`?` 弱音、`|` 小节线会被校验。可用调式：`major minor hminor dorian mixolydian phrygian`（L95）。

**版权红线**（`源码\STYLE.md` 第 10 行）：只用原创旋律，不要抄动画 OST / Roundabout / 任何现成歌曲。STAND PROUD 是用户自己指定、自己下的，放 `assets\audio\user\` 一类目录，不进合成流程。

---

## 3. 音效 `engine/sfx.py`

### 3.1 API 与通用参数

```python
from engine import sfx
x = sfx.make('punch')                  # float32，单声道 (N,) 或立体声 (N, 2)，44100 Hz；每次返回副本
x = sfx.make('ora_rush', dur=2.0)      # 时长型音效按 dur 生成，输出长度 = round(dur*44100) 精确
x = sfx.make('punch', pitch=0.9, seed=3)
sfx.NAMES      # {name: 英文一句话说明}（64 个）
sfx.HIT        # 同步点：从开头到主击打点的秒数
sfx.loudness(x)  # 感知响度 dB（A 计权、100 ms 窗最大值）
```

| 参数 | 含义 |
|---|---|
| `dur` | 时长型（连打、环境音…）按 `dur` 生成；固定长度型补零 / 截断到 `dur`（截断带 30 ms 淡出）。**坑**：`_fit()`（L186）只要传了 `dur` 就会把最后 30 ms 淡出，哪怕长度刚好相等——做无缝循环的音效绝对不能走 `dur`。 |
| `pitch` | 播放速度倍数：1.2 = 更高更短，0.8 = 更低更沉（`_speed()` 线性插值重采样，在响度平衡之后做）。时长型音效输出仍是 `dur`。**同步点要除以 pitch**：`timestop` 用 `pitch=0.92`（影片 s18 白金之星版）时击打点在 0.85/0.92 = 0.924 s。 |
| `seed` | 变体编号（punch、footstep、whoosh、ora_rush…）。随机数是 `_rng(name, seed)`（L171，crc32(name) 定种子），**同参数每次渲染逐样本一致**，适合做构建缓存。 |
| `vol`, `pan` | `make()` 收下但忽略，由混音器处理。其他未知参数也忽略；未知名字抛 `KeyError`。 |

缓存：`_CACHE[(name, sorted(kw))]`，进程内无上限。

### 3.2 `make()` 内部流程（`_build`，L131–147）

`生成函数(**只传它签名里有的参数)` → `_level(name, x)`（按 `_LA` 拉响度）→ 若 `pitch≠1` 且函数不吃 pitch：`_speed(x, pitch)` → 若有 `dur`：`_fit(x, dur)` → `nan_to_num` → float32。
时长型 + `pitch`：先把 `dur × pitch` 传进生成函数，变速后正好回到 `dur`。

### 3.3 响度体系

- 每个生成函数最后调 `_fin(x, peak, fi, fo, dc=True, trim=True)`（L466）：18 Hz 高通去直流 → `_trim`（尾巴低于峰值 −56 dB 就切，留 30 ms）→ 首尾淡入淡出 → 峰值归一到 `peak`（打击 0.75–0.92、UI 0.25–0.3、环境 0.3）。
- `_LA`（L71）：每个音效的感知响度目标（dB）。比目标响就整体压下来；比目标轻就用前瞻限幅器 `_limit()` 往上推，最多推 `_PUSH_MAX[name]` dB（默认 10，punch 3、explosion 6、环境音 0）；在 `_SAT_OK` 里的还能再软削波 6 dB。
- 结果：`vol=1` 时 punch ≈ −13 dB、重击 −11~−16、挥空和音效短乐句 −15~−18、小拟音 −20~−26、环境 −26~−31、blip −23。
- **新加音效要同时给 `_LA[name]`（和必要时的 `_PUSH_MAX[name]`）**，否则 `_level` 直接跳过、只剩峰值归一，响度会和老音效对不齐。可以在游戏侧模块里直接改这两个 dict（附录 A 的 `reg()` 就是这么做的），不用改源码。

### 3.4 同步点 `sfx.HIT`（L152）

| 音效 | 击打点 s | 用法 |
|---|---|---|
| `timestop` | 0.85 | 反向镲片上冲之后才是锣：要让“锣”落在画面反色那一帧，提前 0.85 s 播 |
| `time_resume` | 1.02 | 结尾的“啵”声 = 时间恢复那一帧 |
| `sting_reveal` | 0.26 | 琶音之后的和弦重击 = 替身名字砸出来那一帧 |
| `tbc` | 1.607 | To Be Continued 定格点 |
| `door` | 0.62 | 吱呀之后“咚” |
| `zoom` | 0.47 | 推进声的峰 |
| `stab` / `slash` / `knife_throw` | 0.065 / 0.07 / 0.08 | 刀尖命中 |
| `camera_shutter` | 0.0 | |

### 3.5 全部 64 个音效（实测，scratch `out\report_all.json`；“专属参数”不含通用的 dur/pitch/seed/vol/pan）

长度带“=dur”的是时长型，括号里是默认 dur。st = 立体声。LA = 感知响度 dB（vol=1）。耗时 = 单个首次构建时间。

| 名字 | 中文说明 | 时长 s | 声道 | 峰值 | LA | 专属参数（默认） | 同步点 | 耗时 ms |
|---|---|---|---|---|---|---|---|---|
| `punch` | 实打一拳：下滑音高的拳身 + 中频“咚” + 噪声拍击 | 0.320 | 单 | 0.85 | −12.8 | | | 3 |
| `punch_heavy` | KO 重拳：更低的拳身 + 次低八度 + 碎裂声 + 房间尾音 | 1.277 | st | 0.90 | −11.5 | | | 26 |
| `ora_rush` | 欧拉连打：约 14 拳/秒、左右交替、越打越响，末尾一记重的 | =dur(1.5) | st | 0.88 | −14.4 | `dur=1.5` | | 43 |
| `muda_rush` | 木大连打：更低更暗 + E1/F1 锯齿低鸣 | =dur(1.5) | st | 0.88 | −15.1 | `dur=1.5` | | 41 |
| `whoosh` | 挥空：带通噪声先升后降 | 0.430 | 单 | 0.51 | −17.0 | | | 3 |
| `slash` | 剑斩：短挥 + 金属“铮”（银色战车） | 0.500 | 单 | 0.65 | −15.0 | | 0.07 | 2 |
| `stab` | 刺入：短挥 + 湿闷声 | 0.320 | 单 | 0.75 | −17.0 | | 0.065 | 3 |
| `gunshot` | 手枪（皇帝）：爆裂 + 枪身 + 户外回声 | 1.110 | st | 0.90 | −13.1 | | | 25 |
| `explosion` | 大爆炸：爆裂、低频轰、8-bit 碎响、长尾 | 3.070 | st | 0.92 | −14.7 | | | 91 |
| `crash` | 车 / 金属撞毁：轰、金属叮当、碎片 | 2.301 | st | 0.90 | −12.9 | | | 78 |
| `thud` | 倒地 / 重物落地闷响 | 0.427 | 单 | 0.77 | −17.0 | | | 3 |
| `knife_throw` | 飞刀破空：下降的多普勒哨声 | 0.320 | 单 | 0.43 | −17.0 | | 0.08 | 3 |
| `knife_hit` | 飞刀扎入 + 金属颤音 | 0.450 | 单 | 0.75 | −16.9 | | | 6 |
| `glass_break` | 玻璃碎：裂声 + 约 70 片碎玻璃 | 1.119 | st | 0.80 | −16.4 | | | 62 |
| `fire` | 持续火焰 + 噼啪 | =dur(1.5) | 单 | 0.53 | −22.0 | `dur=1.5` | | 17 |
| `fire_burst` | 红色魔术师放火 FWOOSH：上升火焰 + 低沉“噗” | 1.379 | st | 0.85 | −15.1 | | | 32 |
| `emerald` | 绿宝石水花：12 发晶体“啾” + 风铃 | 1.195 | st | 0.66 | −15.0 | | | 21 |
| `hamon` | 波纹：金色电流嗡、火花、上升光泽 | =dur(1.0) | 单 | 0.36 | −16.0 | `dur=1.0` | | 10 |
| `vine` | 隐者之紫藤蔓窜出：鞭声 + 吱吱 + 沙沙 | =dur(0.8) | 单 | 0.56 | −18.0 | `dur=0.8` | | 7 |
| `sand` | 沙子流动（愚者） | =dur(1.2) | 单 | 0.50 | −23.4 | `dur=1.2` | | 10 |
| `ice` | 结冰 / 冰裂（荷鲁斯） | 1.267 | st | 0.70 | −18.6 | | | 31 |
| `splash` | 大水花 | 1.245 | st | 0.80 | −16.3 | | | 42 |
| `water_gush` | 水塔爆裂喷水 | =dur(1.6) | 单 | 0.65 | −19.0 | `dur=1.6` | | 21 |
| `bubbles` | 水下气泡 | =dur(1.0) | 单 | 0.35 | −21.0 | `dur=1.0` | | 7 |
| `timestop` | ZA WARUDO：反向镲片上冲 → 锣 + 钟 → 磁带减速拖尾 | 3.300 | st | 0.92 | −15.1 | | 0.85 | 142 |
| `time_resume` | 时间恢复：磁带起转的上升呼啸 + “啵” | 1.500 | st | 0.80 | −16.4 | | 1.02 | 48 |
| `clock_tick` | 钟表滴答 | 0.130（n=1） | 单 | 0.60 | −23.1 | `n=1, rate=1.0` | | 2 |
| `menacing` | ゴゴゴ：低沉嗡鸣 + 每秒 3.6 个低吼“GO” | =dur(2.0) | 单 | 0.80 | −21.0 | `dur=2.0` | | 55 |
| `dododo` | ドドド：每秒 6 下战鼓，渐强 | =dur(2.0) | 单 | 0.75 | −16.5 | `dur=2.0` | | 19 |
| `roar` | 吸血鬼咆哮 WRYYYY | 2.313 | st | 0.85 | −14.7 | | | 91 |
| `drain` | DIO 吸血：脉动的低频吸吮 + 下沉嗡鸣 | =dur(1.6) | 单 | 0.60 | −22.1 | `dur=1.6` | | 20 |
| `heartbeat` | 心跳“扑通” | 0.630（n=1） | 单 | 0.90 | −22.5 | `n=1, bpm=72` | | 6 |
| `charge` | 蓄力：阶梯上升的芯片音 + 渐强噪声 | =dur(1.2) | 单 | 0.52 | −16.0 | `dur=1.2` | | 13 |
| `power_up` | 芯片 power-up 快速上行琶音 + 回声 | 0.651 | 单 | 0.26 | −17.0 | | | 3 |
| `sparkle` | 魔法闪烁：高音琶音 + 光泽 | 1.420 | st | 0.38 | −19.0 | | | 31 |
| `glint` | 单颗星闪“kiran” | 0.700 | 单 | 0.32 | −19.0 | | | 2 |
| `zoom` | 镜头推进“shwiing” | 0.550 | 单 | 0.53 | −17.0 | | 0.47 | 4 |
| `freeze` | 定格：闪光“咔” + 低沉 whump | 1.384 | st | 0.80 | −16.8 | | | 24 |
| `pop` | 喜剧“啵” | 0.150 | 单 | 0.60 | −20.0 | | | 2 |
| `sting_reveal` | 替身名揭示：A 小调琶音 → 和弦重击 + 镲 | 2.079 | st | 0.80 | −14.5 | | 0.26 | 72 |
| `sting_shock` | 震惊重击：低轰 + 不协和高音和弦 + 镲 | 2.346 | st | 0.90 | −15.5 | | | 63 |
| `sting_comedy` | 搞笑失败“哇-哇-哇-哇~”弱音铜管 | 2.661 | st | 0.60 | −17.0 | | | 85 |
| `jingle_victory` | 原创芯片胜利号角（C 大调） | 2.364 | 单 | 0.60 | −18.9 | | | 47 |
| `tbc` | To Be Continued：原创放克拍弦贝斯 riff + 鼓 | 2.782 | st | 0.75 | −17.5 | | 1.607 | 105 |
| `blip` | 单个 RPG 对话 / 菜单 blip，30 ms 25 % 方波 | 0.030 | 单 | 0.30 | −23.3 | `freq=660` | | 0.5 |
| `blip_train` | 打字机连发 blip | =dur(1.0) | 单 | 0.25 | −22.5 | `dur=1.0, cps=18, freq=600` | | 1.5 |
| `tv_game` | 复古游戏串烧（泰伦斯的电玩） | 1.908 | 单 | 0.25 | −18.0 | | | 7 |
| `card_flip` | 弹牌 + 拍桌（达比） | 0.130 | 单 | 0.60 | −24.7 | | | 2 |
| `coin` | 弹硬币“叮” | 0.700 | 单 | 0.46 | −18.0 | | | 3 |
| `ding` | 明亮铃声 G6 | 1.200 | 单 | 0.27 | −17.0 | | | 4 |
| `camera_shutter` | 拍立得快门 + 出片马达（念写） | 0.459 | 单 | 0.60 | −24.8 | | 0.0 | 4 |
| `footstep` | 一步脚步声（换 seed 出变化） | 0.115 | 单 | 0.62 | −26.0 | | | 2 |
| `door` | 吱呀门 / 棺盖 + “咚” | 1.000 | 单 | 0.70 | −17.2 | | 0.62 | 10 |
| `dog_bark` | 小狗“汪!”（伊奇） | 0.300（n=1） | 单 | 0.33 | −15.0 | `n=1`（每 0.26 s 一声） | | 3 |
| `bird_screech` | 隼鸣“KYAAA”（Pet Shop） | 0.900 | 单 | 0.22 | −15.0 | | | 7 |
| `bat_flap` | 蝙蝠群振翅 + 吱吱 | =dur(0.9) | st | 0.60 | −22.8 | `dur=0.9` | | 37 |
| `rero` | 花京院舔樱桃“rero rero” | =dur(1.0) | 单 | 0.50 | −21.8 | `dur=1.0` | | 10 |
| `rumble` | 低频大地隆隆 / 逼近的威胁 | =dur(2.0) | 单 | 0.50 | −28.4 | `dur=2.0` | | 18 |
| `thunder` | 雷：撕裂声 + 长滚雷 | 3.841 | st | 0.85 | −16.3 | | | 100 |
| `wind` | 沙漠风 | =dur(3.0) | st | 0.30 | −29.1 | `dur=3.0` | | 66 |
| `crowd` | 街头人群嘈杂（18 个合成人声） | =dur(3.0) | st | 0.30 | −26.0 | `dur=3.0` | | 77 |
| `plane_engine` | 客机引擎 | =dur(3.0) | st | 0.30 | −30.3 | `dur=3.0` | | 62 |
| `car_engine` | 汽车引擎轰油门 | =dur(3.0) | 单 | 0.30 | −31.2 | `dur=3.0` | | 42 |
| `heli` | 直升机 | =dur(3.0) | 单 | 0.30 | −30.7 | `dur=3.0` | | 33 |

- 64 个合计 89.1 s 音频，全部构建 1.91 s。`clip`（≥0.999 的样本）全部 0；首尾样本全部 0。
- 影片里用得最多的：`whoosh`（≈127 处）、`thud`、`heartbeat`、`punch`、`glint`、`footstep`、`pop`、`menacing`、`wind`、`punch_heavy`、`sparkle`、`zoom`。
- 影片里的固定搭配（游戏可照搬）：替身登场 `sting_reveal`(+`zoom`)；时停 `menacing` 垫底 → `timestop` 提前 0.85 s → 停止期间 `clock_tick` → `time_resume` 提前 1.02 s（`s15_kakyoin_last.py` L847–867、`s17_final1.py` L85–106、`s18_final2.py` L932–961）；欧拉对木大 `ora_rush` + `muda_rush` 左右声像 ±0.4，收尾 `punch_heavy`。

### 3.6 合成辅助函数速查（做新音效就用这些，全在 `sfx.py`）

| 函数（行号） | 签名 / 作用 |
|---|---|
| `_n(sec)` L163、`_t(n)` L167 | 秒→样本数；样本时间轴 |
| `_rng(name, seed)` L171 | 确定性随机数 |
| `osc(freq, n, kind, duty, ph0)` L236 | 振荡器，freq 可以是逐样本数组；kind = `sine` `tri` `saw`（polyBLEP）`square`（polyBLEP，去直流）`chip`（不抗混叠的 8-bit 方波） |
| `noise(n, rng, color)` L259 | `white` / `pink` / `brown` |
| `snh(n, rate, rng)` L274 | 采样保持噪声（NES 粗噪声），rate Hz |
| `lfo_noise(n, rate, rng)` L281 | 平滑随机控制信号 [−1, 1] |
| `env_exp(n, tau, attack)` L298、`env_pts(n, [(s, v)…])` L306、`fade(x, fi, fo)` L312 | 包络 |
| `lp/hp/bp(x, f…, order)` L335–344 | Butterworth（sos 缓存） |
| `sweep(x, freq, kind, q, block)` L361 | 时变双二阶滤波（lp/hp/bp），freq 可为数组 → 扫频呼啸的核心 |
| `sat(x, drive)` L379、`norm(x, peak)` L383 | tanh 饱和、峰值归一 |
| `verb(x, wet, sec, tau, lpf, seed, pre)` L407 | 立体声噪声卷积混响，返回 `(len+尾, 2)` |
| `delay(x, sec, fb, taps, lpf)` L420 | 回声（做残影很好用） |
| `loudness(x)` L452 | A 计权 100 ms 最大响度 |
| `_fin(x, peak, fi, fo, dc, trim, la)` L466 | 收尾（去直流、切尾、淡入淡出、归一） |
| `nf('A4')` L491 | 音名→Hz |
| `_warp(x, speed)` L501 | 磁带式变速（speed 逐样本），时停“拖停”就靠它 |
| `_dsig(n, a, b)` L511 | 指数滑音 a→b |
| `_hit(f0, f1, drop, tau, dur, rng, bright, smack, slap, slap_lp, slap_tau, drive, sub, tri, knock)` L518 | **打击声核心**：下滑音高的身体 + 3 倍频“knock” + 两层噪声拍击 + 饱和 |
| `_metal(n, freqs, taus, amps, rng, detune)` L538 | 非谐金属分音（每个分音一对微失谐 → 拍频）：锣、钟、剑鸣、硬币 |
| `_ping(n, f, tau, attack, partials)` L551 | 衰减正弦“叮” |
| `_chirp(n, f0, f1, tau, kind, duty, attack)` L562 | 滑音短音（激光、“啾”） |
| `_clicks(n, rate, rng, dur_ms, f_lo, amp_env)` L567 | 泊松噼啪（火、碎片、火花） |
| `_note(freq, dur, kind, duty, a, d, s, r, vib…)`、`_seq([(start, dur, freq, gain)], total, …)` L582/599 | 芯片音符 / 音序（UI 音、短乐句） |
| `_cymbal(n, rng, tau, f_lo)`、`_kick()`、`_snare()`、`_hat()` L607–632 | 镲 / 底鼓 / 军鼓 / 踩镲 |
| `_rush(dur, name, dark, seed)` L658 | 连打生成器（ora/muda 共用） |
| `_formant(src, [(freq, q, gain)])` L1261 | 共振峰滤波组 → 合成“人声”（狗叫、WRYYY、GO、rero 都靠它） |
| `_bubble_train(n, rate, rng, f_lo, f_hi)` L863 | 气泡串 |
| `_place(dst, src, at, gain)` L198、`_pan(x, p)` L212、`_st(x)` L218 | 叠放、恒功率声像、转立体声 |
| `_limit(x, drive_db)` L94 | 前瞻限幅器 |
| `_blip_wave(freq, sec, duty)` L887、`_slap_bass(freq, dur, pop, rng)` L1515、`_amb_env(n, dur)` L1129 | 其他 |

### 3.7 影片的混音参数（`tools\render.py` `build_audio`，游戏照抄比例）

- 音乐段：每段从第 1 小节起平铺循环；段首 0.08 s 淡入、段尾 0.45 s 淡出；场景音量 `MUSIC_VOL` 变化用 50 ms 平滑（L116–120）。
- 音效：`vol` 线性增益，`pan` 是简单的左右衰减（不是恒功率）。
- **闪避压低（ducking）**：`env` = 音效总线 |峰值| 的 120 ms 滑动平均；`duck = 1 − 0.35·clip(env×2, 0, 1)`；`out = 音乐×0.62×duck + 音效×0.85`（L154–159）。即音乐基础增益 0.62，大音效时最多再压 35 %（约 −3.7 dB）。
- 总响度：0.4 s 块 RMS，门限 −45 dB，拉到 −17 dBFS RMS（L163–170）；软膝限幅膝点 0.62、天花板 0.8（L172–175）；int16 × 32000。

---

## 4. 试跑记录（scratch `audio07\`）

| 试什么 | 命令 / 脚本 | 结果 |
|---|---|---|
| 渲 1 首 | `PYTHONDONTWRITEBYTECODE=1 python render_test.py music battle` | 进程总 6.6 s，其中渲染 1.39 s；`out\music\battle.wav` 1254400 样本 = 28.444 s，峰值 0.899，RMS 0.200，直流 2.8e‑10，削波 0 |
| 渲全部 | `python render_test.py all` | 10 首 15.89 s + 64 个音效 1.91 s，进程总 19.6 s；wav 共 58 MB（音乐）+ 12 MB（音效） |
| API | 同上 | `ora_rush dur=2.0` → 88200 样本；`punch pitch=1.2` → 11760；`punch dur=0.5 pitch=0.8` → 22050，都和文档一致 |
| 循环接缝 | 见 §2.4 | 10 首都无缝 |
| 浏览器解码 | `python browser_loop_test.py battle`（Playwright Chromium，file:// 页面 + base64 .js） | 见下表 |
| 音效 mp3 | `python browser_sfx_test.py` | punch 14112 = 14112、timestop 145530 = 145530、ora_rush 66150 = 66150 样本，长度一致（同步点不漂） |
| 真 AudioContext | `python browser_ctx_test.py` | 本机默认 `sampleRate = 48000`，解码出的 buffer 被重采样（3.3 s 的 timestop → 158400 样本）；`playbackRate` 范围不限；`fetch('d.js')` 在 file:// 下 → `TypeError: Failed to fetch` |
| 新音效原型 | `python proto_test.py`（附录 A） | 见 §6 各表“实测”列；循环接缝都在普通步进范围内 |
| 新曲原型 | `python game_music_proto.py`（附录 B） | 1.94 s，16 小节 23.893 s，峰值 0.890，RMS 0.200 |

battle（28.44 s）编码后在 Chromium 里 `decodeAudioData` 的结果：

| 格式 | 文件大小 | 解码长度 | 原长 | 起点偏移 | 与原波形相关 | 解码耗时 | `<audio>` file:// 播放 |
|---|---|---|---|---|---|---|---|
| mp3 128k（libmp3lame） | 456,036 B | 1254400 | 1254400 | 0 | 0.989 | 76 ms | 可以 |
| ogg q4（libvorbis） | 495,053 B | 1254400 | 1254400 | 0 | 0.992 | 36 ms | 可以 |
| opus 96k | 445,362 B | 1254400 | 1254400 | 0 | 0.983 | 95 ms | 可以 |
| m4a aac 128k | 481,111 B | 1254400 | 1254400 | 0 | 0.963 | 33 ms | 可以 |

体积估算：10 首 340 s → mp3 128k 约 5.4 MB（base64 后约 7.3 MB）；64 个音效 89 s → mp3 约 1.4 MB。单个音效 mp3：punch 6.3 KB、ora_rush 25 KB、timestop 54 KB。

---

## 5. 接进网页游戏的建议

### 5.1 构建：`游戏\tools\build_audio.py`（建议新写，仿银魂 `tools\build_assets.py` L613–660）

1. `sys.dont_write_bytecode = True`；`sys.path.insert(0, 源码)`；`from engine import music, sfx`；再 `import game_sfx, game_music`（游戏侧模块，用 `sfx._reg` / `music._BUILDERS` 注册新东西，附录 A / B 就是雏形）。
2. 配乐：`music.track(name)` → wav → `ffmpeg -c:a libmp3lame -b:a 128k` → 每首一个 `assets\audio\music\<name>.js`：`(window.JOJO_MUSIC ||= {})['battle'] = {b64: "...", loopSec: 28.444444, bpm: 168.75, barSec: 1.42222, beatSec: 0.35556};`。每首单独一个 .js，进章节时插 `<script>` 懒加载，避免开场一次解析 7 MB。
3. 音效：用清单 `[(输出名, 音效名, kwargs)]`，例如 `('punch0','punch',{'seed':0})`…`('punch3',…)`、`('timestop_sp','timestop',{'pitch':0.92})`、`('grunt_jotaro','grunt',{'voice':'jotaro'})`。`sfx.make()` → wav → mp3 96–128k → 合并进一个 `assets\audio\sfx_data.js`：`{name: {b64, sec, ch, hit, loop}}`，`hit = sfx.HIT.get(name, 0) / pitch`。
4. 缓存：wav 已存在且 `engine\*.py` / 游戏侧模块 mtime 没变就跳过（同参数渲染逐样本一致）。全量构建预计 < 30 s。
5. STAND PROUD 等用户提供的 mp3 也走第 2 步转 base64 .js（标题界面用，循环点用户没给就整首循环）。

### 5.2 运行时：WebAudio（替代银魂的 HTMLAudio）

```
master: DynamicsCompressorNode(threshold −10 dB, knee 6, ratio 8, attack 0.003, release 0.15) → destination
musicBus: GainNode(0.62) → BiquadFilter(lowpass, 20000 Hz) → master      // 时停时把滤波关小
duckGain: GainNode(1.0) 串在 musicBus 前                                   // 大音效时压低
sfxBus:  GainNode(0.85) → master
每个音效: AudioBufferSourceNode(playbackRate = rate) → GainNode(vol) → StereoPannerNode(pan) → sfxBus
```

要点：
- `new AudioContext({sampleRate: 44100})`：避免 48 kHz 设备上解码重采样（实测默认 48000），循环点按秒设 `loopEnd = buf.duration`。
- 浏览器自动播放策略：第一次 keydown / pointerdown 时 `ctx.resume()`（银魂 `G.audio.unlock()` 的位置照搬）。
- base64 → ArrayBuffer：`Uint8Array.from(atob(s), c => c.charCodeAt(0)).buffer` → `ctx.decodeAudioData()`（Promise）。音效在加载画面一次解码完（89 s × 44100 × 2 声道 × 4 B ≈ 31 MB 内存，可接受）；配乐**用到才解码、换章节释放**——10 首全部解码要 ≈ 120 MB。
- API 建议保持和银魂一样的名字，方便剧情脚本照抄：`G.audio.music(name, fade)`、`G.audio.stopMusic(fade)`、`G.audio.sfx(name, vol=1, rate=1, pan=0)`；新增 `G.audio.loop(name, vol)` 返回 `{stop(fade)}`（欧拉连打、时停嗡声、火焰、风）、`G.audio.timeStop(on)`（§5.3）、`G.audio.cue(name, atHit)`（自动减 `hit`，例如 `cue('timestop')` 让锣落在当下 0.85 s 之后的画面帧上 → 剧情脚本里先播声音、再等 `hit` 秒出画面）。
- 同一音效最多同时 4 个实例（欧拉连打期间的 punch），超了掐掉最老的；UI 音不受限。
- 声像：按屏幕 x 算，`pan = clamp((x − 160) / 160 × 0.6, −0.6, 0.6)`（320 宽画布）。

### 5.3 时停的 BGM 处理（不需要额外素材，符合原著“世界静止”）

1. `cue('timestop')`（DIO 用原版；承太郎“白金之星·世界”用 `timestop_sp` = `pitch 0.92`，击打点 0.924 s）。
2. 击打那一刻：音乐 source `playbackRate.setTargetAtTime(0.05, t, 0.25)`、滤波 `frequency.setTargetAtTime(300, t, 0.3)`、`duckGain.setTargetAtTime(0, t + 0.6, 0.2)` → 像磁带被按停；同时 `loop('timestop_hum', 1.5)` 淡入 0.5 s。
3. 停止期间：脚步 `footstep`、`clock_tick`（数秒）、`knife_freeze` 等照常播，但所有战斗音效 `rate × 0.9`、走 −3 dB。
4. 恢复：`cue('time_resume')`（“啵”在恢复帧）；“啵”那一刻 hum 0.1 s 淡出、音乐 `playbackRate` 0.3→1.0 线性 0.4 s、滤波拉回 20000、增益恢复。

### 5.4 “战斗爽”的声音规则（实现时逐条做）

- **分层**：每次命中 = 拳身（`punch` seed 0–3 轮换）+ 受击者喊声（`grunt_*`，30 ms 后，只在掉血 ≥ 一定量或被击飞时）+ 暴击 / 破防时再叠 `crit` / `guard_break`。
- **随机化**：每下 `rate` 抖 0.94–1.08，`vol` 抖 0.85–1.0，避免“机关枪感”。
- **顿帧对齐**：命中帧立刻出声（不要等顿帧结束），重击顿帧 4–6 帧时让音乐 duck −3.7 dB（照 §3.7 的 0.35）。
- **慢动作**：KO / 完美闪避的子弹时间里，所有非 UI 音效 `rate × timeScale`，音乐 `playbackRate` 同步 0.6 左右，结束时回 1.0。
- **低血**：血量 < 25 % 时循环 `heartbeat_loop`（§6.1），音乐 `playbackRate 1.06`（+1 半音、+6 % 速度，免费的“危机变奏”）。
- **必杀**：`super_start` 的 0.5 s 上冲期间冻结画面 + 立绘切入，0.5 s 处和弦砸下时开打；整段音乐 duck 到 0.4。

---

## 6. 缺口清单 + 合成配方

记号：✅ = 已在 scratch 做出原型（代码见附录 A，“实测”是 `proto_test.py` 的输出）；配方里的函数都在 `sfx.py`，参数就是建议值。优先级 P0 = 第一个可玩版本必须有，P1 = 主角招式 / 主要敌人，P2 = 锦上添花。

### 6.1 战斗核心（P0）

| 新音效 | 用在哪 | 现有能凑合 | 配方 | 原型实测 |
|---|---|---|---|---|
| `ora_loop` ✅ | 连按 J 的欧拉连打（循环） | `ora_rush(dur)`：但它渐强 + 末尾重击，不能循环 | 8 个 `_hit` 模板，参数照 `_rush` 亮版：`f0=260 f1=75 drop=.022 tau=.042 bright=5200 smack=.9 slap=1.2 slap_lp=3200 slap_tau=.022 drive=2.6 tri=.2 knock=.8`，±14 % 音高；16 拳/秒、**偶数拳**（左右交替跨接缝不乱）、时间抖 ±12 % 周期、声像 ±0.35；拳风底噪 = 圆周 FFT 带通 500–3200 Hz × (0.55+0.45·sin²(π·16·t))；超出 1.0 s 的尾巴 `_fold` 回开头；`_fin_loop` 只减均值 + 归一 0.88，不切尾不淡出 | 1.0 s、立体声、峰 0.88、LA −14.5、接缝在 10 百分位、11.7 ms |
| `muda_loop` ✅ | DIO / 黑暗系敌人的连打 | `muda_rush(dur)` 同上问题 | 同上暗版：`f0=175 f1=58 drop=.03 tau=.05 bright=1700 smack=.6 slap=1.7 slap_lp=1900 slap_tau=.028 drive=3.4 tri=.4 knock=1.2`；底噪 150–900 Hz；低鸣锯齿 41.2/43.7 Hz **吸附成整数周期**（`_per(f, L)`）再圆周低通 260 Hz | 1.0 s、LA −14.9、接缝 70 百分位 |
| 连段第 1/2/3 下 | J 三连击 | `punch` seed 0/1，运行时 rate 1.0 / 1.08；第 3 下 `punch_heavy` vol 0.8 | 若要专门的第 3 下 `punch_mid`：`_hit(200, 50, .04, .10, .45, rng, bright=4000, smack=1.0, slap=1.5, slap_lp=2800, slap_tau=.045, drive=3.0, sub=.2, knock=1.0)` → `_fin(x, .88, .0005, .06)`，`_LA=-12` | — |
| `crit` ✅ | 暴击 / 连打终结 | `punch_heavy` + `glint` | `_hit(210, 46, .045, .14, .6, sub=.3, knock=1.1, drive=3.4, slap=1.6)` + 高通噪声爆裂 `hp(noise,3000)·env_exp(.006)` ×0.6 + `_metal([1900,2870,4100], [.2,.15,.1])` ×0.35 + `bp(snh(6000),300,5000)·env_exp(.04)` ×0.5 → `sat 1.6` → `verb(wet .2, sec .7)`；`_LA=-11, _PUSH_MAX=7` | 1.15 s、LA −13.9（想更响就再加 drive） |
| `ko_hit` ✅ | 击倒最后一击（配慢动作） | `punch_heavy` + `explosion` | `_hit(150, 32, .07, .35, 2.2, sub=.6, knock=1.2, drive=4)` + 碎响 + D2 锣分音 `_metal(73.4×[1,2,2.41,2.98,4.07])` ×0.5 → `_warp` 速度 1.0（前 15 %）→ 0.45（慢动作下沉）→ **先 `fade(…, 0, .5)` 再进混响**（不淡出会在 2.2 s 处硬切，第一版原型就踩了）→ `verb(wet .3, sec 1.6, tau .45)` | 3.26 s、LA −13.6 |
| `guard` ✅ | L 替身格挡（挡住时） | `knife_hit` | `_hit(320, 140, .01, .03, .45, bright=5000, smack=.9, slap=.5, slap_lp=2500, slap_tau=.015, drive=2.2, knock=.4)` + `_metal([520,1180,1730,2650], [.12,.09,.07,.05])` ×0.6 + 2–6 kHz 噪声咔 → `verb(wet .12, sec .4)`；挡住时运行时再叠 `punch` rate 0.8 vol 0.4 | 0.57 s、LA −17.2（目标 −15，可提 drive 到 3） |
| `guard_break` | 破防 | `glass_break` | `glass_break(pitch=.8)` + `thud` + `_metal([300,700,1100], [.3,.2,.15])` ×0.5，0.9 s | — |
| `parry` ✅ | 完美格挡“KIIN” | `slash` 的金属声 | `_metal([2093,3140,4400,5870], [.45,.3,.2,.12])` ×0.8 + `_ping(4186, .25, partials ((1,1),(1.5,.3)))` ×0.35 + 噪声咔 + `osc(_dsig(160→70))` 小咚 → `verb(wet .2, sec .8, lpf 9000)` | 1.54 s、LA −15.8 |
| `dodge` ✅ | K 闪避（带残影） | `whoosh` | 0.22 s 带通噪声 `sweep(bp, q 1.5)`，中心 700→6000→ 回落；开头叠 40 ms `_chirp(1800→900, 'square', duty .25)`；**`delay(x, .045, fb .45, taps 3, lpf 5000)` 做残影回声** | 0.355 s、LA −17.4 |
| `dodge_perfect` | 完美闪避 → 子弹时间 | `dodge` + `zoom` | `dodge` + 0.3 s 反向镲 `_cymbal(_n(.4), rng, .3, 3000)[::-1]` × `exp((t−.3)/.1)` + `osc(_dsig(90→40))·env_exp(.2)` ×0.6 → `verb .3`；同步点 0.3 s | — |
| `wall_slam` | 被打飞撞墙 / 砸地 | `thud` + `crash` | `_hit(120, 40, .05, .2, .6, sub=.5, knock=.8, drive=3)` + `_clicks(60/s, (1,5) ms, f_lo 900, amp_env=env_exp(.3))` 碎石 + `rumble(dur=.6)` ×0.4 | — |
| `skid` | 被击退在地上滑 | — | `sweep(noise, _dsig(2500→700), 'bp', q=2)` × `env_pts([(0,0),(.02,1),(dur,0)])` + `_clicks(40/s)`；`dur=0.4` | — |
| `stand_summon(kind)` ✅ | 替身召唤 / 换队长时替身亮相（同步点 0.25 s） | `sting_reveal` + `zoom`（影片的搭配） | 0–0.25 s：带通噪声 400→6000 Hz 上冲 + 和弦前 3 音的锯齿滑音（从低八度滑上来）；0.25 s：5 音锯齿和弦 `sweep lp 700+5000·e^(−t/.15)` + `_kick(.4, 140, 40, .13)` + 镲 ×0.25 + **每个替身的“配色层”**：`star`=E 大调 + 一记 `_hit` 拳；`hiero`=G + `_metal` 风铃（3136/3951/4699/6272）；`chariot`=A + 剑鸣（2210/3470/5130/7020）；`red`=D + `fire_burst`；`purple`=C + `vine`；`fool`=F + `sand`；`world`=C 小调 + D2 锣 | 7 种都做了，1.95–2.09 s，LA −16.1~−17.4（目标 −14：峰值提到 .9 或 push 6） |
| `stand_recall` | 收替身 | 无 | 0.35 s：`sweep(bp, 6000→400)` 下冲 + 和弦下滑 `osc(f·2^(−u))` + 末尾 `pop` ×0.5 | — |
| `meter_tick` | 替身能量 +1 格 | `blip` | `blip(freq=1320)`，运行时 `rate = 1 + 0.5·能量比例`（越满越高） | — |
| `meter_full` ✅ | 能量攒满（U 可用） | `power_up` + `glint` | `_seq` E6-G#6-B6-E7 每音 30 ms、方波 duty .125 + 0.12 s 处 `_ping(E7, .22)` 带 24 Hz 颤 + 0–0.15 s `_chirp(1200→2400)` ×0.25 → `delay(.06, .3, 2)` | 0.87 s、LA −19.3 |
| `super_start` ✅ | U 必杀启动（同步点 0.5 s） | `freeze` + `zoom` + `sting_reveal` 三个叠 | 0 s：闪光“咔”（hp 噪声 + `osc(_dsig(110→45))`）；0–0.5 s：带通噪声 300→8000 + 锯齿 150→1200 Hz 上冲（切入立绘）；0.5 s：A 小调锯齿和弦重击 + `_kick` + 镲 → `verb(.2, .9)` | 2.21 s、LA −15.2 |
| `battle_start` | 遭遇战开场 | `menacing(dur=1.6)` + 1.4 s 处 `sting_shock` | 不用新素材，剧情脚本里组合 | — |
| `heartbeat_loop` | 低血警告（循环） | `heartbeat(n=…, bpm=110)` 但不能循环 | 照 `_heartbeat` 的 `beat()`（L1199）：lub 65→40 Hz / dub 78→48 Hz，loop = 60/110 s × 2 拍，两拍放好后 `_fold` 回开头，`_fin_loop(.9)`，运行时 vol 0.6 | — |
| `game_over_jingle` | 战败（从这场战斗重来之前） | `sting_comedy`（太搞笑，不合适） | `_seq` 方波 duty .25：E5 D5 C5 B4 每音 0.18 s，A4 1.0 s（带 vib .012）；三角波低音 A2→E2→A1；开头 `thud`；`delay(.15, .25, 2)` + `verb(.2, 1.0)`，约 2.5 s，`_LA=-17` | — |
| 胜利 | 战斗胜利 | `jingle_victory`（2.36 s） | 现成 | — |

### 6.2 时停（P0，DIO 和承太郎都要）

| 新音效 | 配方 | 原型实测 |
|---|---|---|
| 锣（时停开始） | 现成 `timestop`（DIO 原版，hit 0.85）；承太郎版 `timestop_sp = make('timestop', pitch=0.92)`（影片 s18 L946 就这么用，hit 0.924 s，长 3.587 s） | 现成 |
| `timestop_hum` ✅“嗡” | 停止期间的循环底音：锣的 5 个分音（D2 × 1/2/2.41/2.98/4.07，幅度 1/.55/.4/.3/.18）各一对 ±0.3 % 失谐的正弦——**频率吸附成循环内整数周期**，每循环 2 次起伏；+ 36.7 Hz 次低音 ×0.8；+ 圆周带通 2.5–6 kHz 空气声 ×0.25（每循环 1 次起伏）；右声道相位错开 1/3 循环；`_fin_loop(.5)` | 4.0 s 循环、峰 0.5、LA −34.8（很轻，运行时 vol 1.5–2；音乐那时是停的，不需要更响），接缝 26 百分位 |
| 恢复 | 现成 `time_resume`（“啵”在 1.02 s）；承太郎版也可 `pitch=0.92` | 现成 |
| 读秒 | 现成 `clock_tick(n=1)`，每秒播一次；最后两秒 `rate=2` | 现成 |
| `knife_freeze` | 飞刀在停住的时间里悬停：`knife_throw` 前 0.12 s → `_warp(x, speed 1→0 线性 0.15 s)` 磁带停转 + 0.15 s 处 `glint` ×0.6 | — |
| `knife_volley` | 时停里扔一圈飞刀：8 × `knife_throw`（pitch 0.95–1.1、间隔 0.035 s、声像 ±0.6），约 0.6 s；恢复瞬间配 `knife_rain_hit` = 8 × `knife_hit` 在 0.25 s 内散开 | — |
| `roadroller` | 压路机：`crash` + `menacing` 垫底；“木大木大打压路机”= `muda_loop` + 每 2 拳叠一次 `_metal([180,410,690,1050], [.4,.3,.25,.2])` ×0.4 钢板声（做成 `muda_steel_loop`，同样走圆周循环） | — |

### 6.3 主角团 6 人的替身招式（P1）

| 角色·替身 | J 出拳 | 连按 J | L 格挡 | U 必杀 | 其他 |
|---|---|---|---|---|---|
| 承太郎·白金之星 | `punch` seed 轮换 | `ora_loop` ✅ + 收尾 `crit` | `guard` | 白金之星·世界：`super_start` → `timestop_sp` → 停止中 `ora_loop` → `time_resume` → 收尾 `ko_hit`；或“流星指刺”`star_finger`：`knife_throw(pitch=1.5)` 前 0.1 s + `stab`（0.08 s 后） | 喊声 `grunt_jotaro` |
| 花京院·绿色法皇 | `emerald_shot`（新）：`emerald` 里的一发——`_chirp(m=.11 s, f0 2000–2800, ×0.3, tau .04, 'square', .25)` + `lp 9000` + `_metal` 风铃 ×0.2，0.3 s | `emerald`（12 连发现成） | 触手缠绕 `hiero_tentacle`（新）：`vine` 的鞭声 + `rero` 的湿润共振峰 ×0.6，0.5 s | 半径 20 m 绿宝石水花 `emerald_barrier`（新）：0–0.8 s 每 30 ms 一个高音 `_ping`（2–6 kHz，tau .05–.12，声像随机）像绷紧的丝线 + 上行竖琴滑奏（`_seq` 三角波 G4→G6 五声音阶 20 ms/音），0.8 s 处两次 `emerald` 叠放 + `sparkle` | `rero`（樱桃彩蛋） |
| 波鲁纳雷夫·银色战车 | `slash` seed 轮换 | `rapier_loop` ✅（18 刺/秒：35 ms 带通噪声 2000→7500 + 3200/4700/6100 Hz 金属“叮”；1.0 s、LA −18.7，可 push 到 −15） | `guard` + `slash` 金属声 ×0.3 | 卸甲 `armor_off`（新）：6–8 个 `_metal([400–1200 Hz 随机 3 分音], tau .1–.2)` 在 0.5 s 内落地 + `whoosh` + 结尾 `slash` 铮；之后残影快刺 = `rapier_loop` rate 1.2 | 剑身射出 `rapier_launch`（新）：`_chirp(300→900, 'tri')` 弹簧“嘣” + `knife_throw` + 0.25 s 后 `knife_hit` |
| 阿布德尔·红色魔术师 | `fire_burst` 前 0.5 s（`dur=0.5`） | `fire(dur)` 循环底 + 每 0.12 s 一次 `fire_burst(pitch=1.3)` vol 0.5 | `guard` + `fire` 噼啪 ×0.3 | 十字火焰风暴 `crossfire`（新）：`fire_burst` + 0–0.6 s 带通噪声 `sweep 400→3000` 的同时声像从 −0.8 绕到 +0.8（逐块 `_pan`）+ 0.6 s 处 `explosion` ×0.5；Special 版 = 3 发错开 0.15 s | 红色绑缚：`fire(dur)` + `door` 前 0.6 s 的吱呀（绷紧） |
| 乔瑟夫·隐者之紫 | `vine(dur=.4)` | `vine(dur)` 连续 + `hamon(dur)` ×0.5 | `guard` | 波纹疾走 `hamon_overdrive`（新）：`hamon(dur=.8)` 上冲 + 0.8 s 处 `punch_heavy` + `sparkle`（同步点 0.8 s） | 念写（调查道具时）`camera_shutter` + `glint`；喊声 `grunt_joseph` |
| 伊奇·愚者 | 沙拳 `sand(dur=.3)` + `thud` | `sand(dur)` + 每 0.1 s `thud(pitch 1.3)` vol 0.4 | 沙墙 `sand(dur=.5)` + `guard` ×0.5 | 沙暴 `sand_storm`（新）：`sand(dur=2)` + `wind(dur=2)` ×0.6 + `rumble(dur=2)` ×0.4，声像慢摆 | 叫 `dog_bark(n=2)`；受伤 `dog_bark(pitch=1.4)`（实测 0.214 s、LA −15.2，像“嗷”）；滑翔 `wind(dur=1)` + `sand` |

### 6.4 敌方替身使者（P1/P2，按第三部顺序；“现成”的直接用）

| 敌人（替身） | 招牌音效 | 现成 / 新做配方 |
|---|---|---|
| 灰塔 Gray Fly（towergray） | 甲虫嗡嗡 + 舌头穿刺 | 新 `insect_buzz(dur)`：`osc(220·(1+0.05·lfo_noise), 'square', .3)` × (0.6+0.4·sin(2π·30·t)) → `bp 400–3000`，靠近 / 远离用 `sweep` 中心频率 + 音量包络；穿刺 = `stab` |
| 暗蓝之月（darkbluemoon） | 水下、鳞片刃、漩涡 | 现成 `bubbles` `splash` `water_gush`；鳞片 = `slash(pitch=.8)`；新 `whirlpool(dur)`：`sweep(noise, 300+200·sin(2π·1.5·t), 'bp', q 3)` + `_bubble_train(30/s)` |
| 力量 Strength（strength） | 船体吱嘎、猩猩尖叫 | 船体 = `door` 前 0.62 s 吱呀（`pitch .7`）；新 `ape_screech`：照 `bird_screech` 但 f0 900→1400→700、`bp 600–4000`、rasp 0.6，0.6 s |
| 恶魔 Ebony Devil / 黄色节制 / 女帝（图集里没有角色，若做） | 玩偶怪叫、黏液、肉瘤 | 黏液 = `drain(dur)` + `rero` 湿声；玩偶 = `grunt(voice='enemy', pitch 1.8)` |
| 倒吊人 J·凯尔（hangedman / jgeil） | 镜面光速移动 | 新 `mirror_flash`：`glint` + 0.03 s 后 `whoosh(pitch 1.6)` + `stab` |
| 皇帝 荷尔·荷斯（holhorse） | 枪 + 弹道拐弯 | 现成 `gunshot`；新 `ricochet`：`knife_throw(pitch 1.8)` + `coin(pitch 1.3)` ×0.5 |
| 命运之轮（wheel） | 车、汽油、点火 | 现成 `car_engine` `crash` `splash` `fire_burst` |
| 正义 恩亚婆婆（justice / enya / zombie） | 浓雾、丧尸呻吟 | 雾 = `wind(dur)` `pitch .6`；新 `zombie_moan`：`_formant(osc(90, 'saw') + 0.4·noise, [(420,5,1),(700,6,.6)])`，f0 90→75、2 s、`sat 2` |
| 恋人 钢铁之丹（steelydan） | 脑内微小替身 | `insect_buzz` `pitch 2.2`；钢铁之丹挨揍 `grunt_enemy` |
| 太阳（图集里没有） | 热浪、光束 | 新 `heat_beam`：`_chirp(2400→600, 'chip', .5)` × 3 层失谐 + `fire(dur)` ×0.4 |
| 死神 13（death13） | 梦境、镰刀 | 镰刀 = `slash(pitch .7)` + `whoosh(pitch .6)`；梦境垫底可借 `ending` 的 music box 声部思路：`_seq` 方波 duty .125 在 C6–C7 慢弹 + `pitch .9` 走音 |
| 审判（judgement） | 灯神许愿、泥偶 | 许愿 = `sparkle` + `ding`；泥偶出现 = `thud` + `sand` |
| 女教皇 米德拉（highpriestess） | 金属变形、牙齿 | `knife_hit` + `slash`；咬 = `_hit(400,200,…)` + `crash` 的金属 ×0.3 |
| 盖布神 恩多尔（geb / ndoul） | 水刃、手杖探地 | 新 `water_jet`：`hp(noise, 3000)` × `env_pts([(0,0),(.02,1),(.3,0)])` + `sweep(bp, 6000→1500)` + `splash` ×0.4；手杖 = `clock_tick(pitch .8)` |
| 克努姆 / 托特（oingo / boingo） | 变脸、漫画翻页、橘子炸弹 | 现成 `pop` `sting_comedy` `explosion`；翻页 = `card_flip(pitch .7)` |
| 阿努比斯（图集里没有） | 妖刀 | `slash` + `parry` 的金属鸣 |
| 芭丝泰托 玛莉亚（mariah） | 磁力吸附 | `knife_hit`（金属吸住）+ `hamon(dur)` ×0.4 当电磁嗡 |
| 赛特 亚历克西（alessi） | 影子返老还童 | 现成 `time_resume` 反着放（`x[::-1]`）+ `drain` |
| 奥西里斯神 达比（darby） | 赌魂 | 现成 `card_flip` `coin`；收魂 = `drain(dur=1)` + `sparkle(pitch .7)` |
| 荷鲁斯神 Pet Shop（petshop） | 隼鸣、冰锥 | 现成 `bird_screech` `ice`；冰锥飞出 = `knife_throw(pitch 1.3)` + `ice` |
| 阿图姆神 泰伦斯（telence） | 电玩、读心 | 现成 `tv_game`；读心“YES/NO” = `ding` / `menu_error` |
| 奶油 瓦尼拉·艾斯（cream / vanilla） | 亚空间吞噬 | 新 `void_eat(dur)`：`sweep(noise, 3000→150, 'lp', q 2)` 下沉吸入 + `osc(55·(1−0.5u))` 次低音 + 边缘碎屑 `_clicks(80/s, f_lo 1500)` ×0.6 + 反向 `whoosh`；靠近时整体 `lp` 随距离变 |
| DIO·世界（dio / theworld） | 木大、时停、飞刀、WRYYY、压路机 | `muda_loop` ✅、`timestop`、`time_resume`、`timestop_hum` ✅、`knife_volley`、`roar`、`roadroller`、`drain`（吸血回血） |

### 6.5 UI / 剧情 / 探索（菜单 P0，其余 P1）

| 新音效 | 配方 | 原型实测 |
|---|---|---|
| `menu_move` ✅ | `_seq` A5 一个音 25 ms、`'chip'` duty .25 → `_fin(peak .25, dc=False)` | 0.066 s、LA −24.0 |
| `menu_confirm` ✅ | E6→B6 两音各 45 ms 方波 duty .25 + `delay(.05, .25, 1)` | 0.178 s、LA −21.0 |
| `menu_cancel` ✅ | B5→E5 下行 | 0.128 s、LA −22.0 |
| `menu_error` ✅ | 110 Hz + 116.5 Hz 两个 `'chip'` 方波失谐“嗡” 0.16 s → `lp 3000` | 0.16 s、LA −25.8 |
| 对话打字 | 现成 `blip`；每个角色不同音高：运行时 `rate = freq/660`（30 ms 的音，变速带来的变短可忽略）。建议：承太郎 440、阿布德尔 400、乔瑟夫 520、花京院 560、波鲁纳雷夫 620、伊奇 900、DIO 420（文字更慢）、荷莉 800（影片 docs 里 DIO=420、荷莉=800）、普通 NPC 600 | — |
| 换队长 | `stand_summon(kind=新队长)` 的前 0.9 s（`dur=0.9`），或 `sting_reveal` vol 0.6 | — |
| 调查 / 互动 | 有东西：`glint`；没东西：`pop` vol 0.5；拿到线索：`ding` | 现成 |
| 章节标题 | `sting_reveal`；章节结束 `tbc`（To Be Continued 定格在 1.607 s） | 现成 |
| 场景切换 / 进门 | `door`、`footstep` seed 轮换（走路每 0.32 s 一步，vol 0.5） | 现成 |
| 大地图交通 | `plane_engine` `car_engine` `heli` `wind` `bubbles`（潜艇）`splash`（船） | 现成 |
| `pause` | 打开暂停：`menu_confirm` + 音乐 lowpass 800 Hz、增益 0.5 | 运行时 |

### 6.6 人声替代（没有配音，全部共振峰合成）

| 新音效 | 配方 | 原型实测 |
|---|---|---|
| `grunt(voice)` ✅ 受伤喊声 | 源 = `osc(f0,'saw') + 0.5·rasp·osc(f0/2,'square',.4) + rasp·noise`，f0 起点×1.15 → 起点 → 终点（0.3 s）；包络 0→1（12 ms）→ .85（80 ms）→ .25（220 ms）→ 0；共振峰 `_formant`：F1 380→680→560、F2 900→1150→1050、F3 2500（都乘声线缩放）；`sat(y·3, drive)`。声线表 `(f0 起, f0 止, 共振峰缩放, rasp, drive)`：jotaro (110,82,.92,.25,2.2)、kakyoin (150,112,1.0,.2,2.0)、polnareff (140,100,1.0,.3,2.2)、avdol (95,72,.9,.3,2.4)、joseph (135,95,1.0,.5,2.0)、enemy (100,70,.88,.45,2.8)、dio (115,80,.95,.4,3.0) | 7 种都 0.3 s、LA −16.0；**听感偏“芯片机器人”**，没人耳确认 |
| `ora_voice(n)` ✅ 合成“O-RA!” | 每音节 1/7 s：f0 165 Hz（±3 %，句中上扬 8 %），前 40 % 是 o（F1 450 / F2 800），45 % 处幅度掉到 .25 当“r”闪音，之后 a（F1 800 / F2 1250），`sat 2`；奇偶音节 1.0 / 0.85 交替 | n=4：0.62 s、LA −15.0；**实验性**，可能很怪，先给用户听再决定用不用（不用的话就只靠画面上的 ORA 字） |
| `muda_voice(n)` | 同上，元音换 u→a：F1 300→800、F2 800→1250，f0 130 Hz | — |
| DIO“WRYYY” | 现成 `roar`（影片 s17 也用 `pitch 1.1`） | 现成 |
| 伊奇 | 现成 `dog_bark`；受伤 `dog_bark(pitch=1.4)` | 现成 |

### 6.7 音乐缺口（P2）

- 一首普通战斗曲 `battle` 撑 25 场以上替身战会腻：建议埃及篇（九荣神）换 `battle_egypt`（附录 B 已能渲），DIO 手下中 boss 可用 `boss` 的前 10 小节（但不能用 loopStart 截，§2.4；要截就新写一首）。
- 危机变奏不用新曲：`playbackRate 1.06`（§5.4）。
- 战败用音效 `game_over_jingle`（§6.1），不用整首曲子。
- 标题界面 = 用户提供的 STAND PROUD。

---

## 7. 风险 / 坑 / 需要拍板的事

1. **`dur` 会毁掉循环**：`sfx._fit()` 只要收到 `dur` 就淡出最后 30 ms。所有循环音效用别的参数名（附录 A 用 `loop`），并且用 `_fin_loop`（只减均值 + 归一），不能用 `_fin`（它会切尾 + 淡入淡出 + 非圆周高通）。
2. **循环里的滤波和振荡器要“圆周”**：普通 `bp/lp/hp` 是 IIR，开头有瞬态、首尾接不上 → 用附录 A 的 `_cband`（FFT 圆周滤波）；持续音的频率要吸附成循环内整数周期（`_per(f, L)`），否则接缝有相位跳。
3. **新音效要登记 `_LA`**，否则响度和老音效对不齐；几个原型（`guard` −17.2、`stand_summon` −16.x、`crit` −13.9）离目标还差 1–3 dB，正式做时再调 drive / push。
4. **pitch 会移动同步点**：`hit_实际 = HIT[name] / pitch`，构建脚本要写进 meta。
5. **file:// 限制**：`fetch` / XHR 本地文件都不行，WebAudio 只能吃 base64 内嵌的 .js；HTMLAudio 能直接播 file:// 但做不到无缝循环、低延迟密集触发和变速拖停。若坚持用 HTMLAudio（银魂方案），欧拉连打只能放预渲好的 `ora_rush(dur)` 长段、时停只能硬切 BGM。
6. **内存**：配乐全部解码约 120 MB（44.1 kHz）/ 131 MB（48 kHz），必须懒解码 + 换章节释放；音效全解码约 30 MB。
7. **手机（银魂有触屏版）没测**：iOS Safari 的 `decodeAudioData` 对 mp3 是否也剥编码延迟没验证；若有循环咔哒，改用 m4a（AAC）或在 meta 里记原始样本数、运行时 `loopStart = (buf.length − 原长)/sr` 兜底。
8. **合成人声的听感**没人耳确认（`grunt_*`、`ora_voice`）；做成可开关（设置里“喊声 开 / 关”），先给用户试听。
9. **版权**：所有合成旋律必须原创（`STYLE.md` 第 10 行）；不要用动画原声、不要采样配音。STAND PROUD 由用户自行提供，只在标题界面播放，打包时放 `assets\audio\user\`。
10. 构建时 `import engine` 会在 `源码\engine\` 生成 `__pycache__`，脚本开头必须 `sys.dont_write_bytecode = True`（或环境变量 `PYTHONDONTWRITEBYTECODE=1`）。

---

## 附录 A：新音效原型 `game_sfx_proto.py`（scratch 里跑通的完整代码，可直接改名为 `游戏\tools\game_sfx.py`）

```python
"""Prototype: new game sounds built ONLY from engine/sfx.py helpers, registered at runtime
with sfx._reg (源码 is not modified).  Pattern for the real tools/game_sfx.py.

    import game_sfx_proto            # registers the new names into engine.sfx
    from engine import sfx
    sfx.make('ora_loop')

Loops (names ending in _loop / _hum) must NOT take a `dur` kwarg: sfx._build() runs
_fit(x, dur) whenever `dur` is passed, and _fit always fades the last 30 ms, which breaks
the seam.  They take `loop` (seconds) instead and are finished with _fin_loop (circular).
"""
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, r'D:\大疆\游戏素材\JoJo\源码')
from engine import sfx  # noqa: E402
from engine.sfx import (SR, _TAU, _chirp, _clicks, _cymbal, _dsig, _fin, _formant, _hit, _kick,  # noqa: E402
                        _metal, _n, _pan, _ping, _place, _reg, _rng, _seq, _st, _t, _warp, bp, delay,
                        env_exp, env_pts, fade, hp, loudness, lp, nf, noise, norm, osc, sat, snh, sweep, verb)

GAME = {}            # name -> desc (only the new ones)
LOOP = {}            # name -> loop seconds (for the build tool / runtime loopStart/loopEnd)


def reg(name, desc, la=None, push=None, loop=None):
    def deco(f):
        _reg(name, desc)(f)
        GAME[name] = desc
        if la is not None:
            sfx._LA[name] = la
        if push is not None:
            sfx._PUSH_MAX[name] = push
        if loop:
            LOOP[name] = loop
        return f
    return deco


# ------------------------------------------------------------ circular (loop) helpers
def _fold(x, L):
    """Wrap everything past sample L back onto the start (tails of a loop)."""
    y = x[:L].copy()
    r = x[L:]
    while len(r):
        m = min(L, len(r))
        y[:m] += r[:m]
        r = r[m:]
    return y


def _cband(x, lo=None, hi=None):
    """Circular (FFT) Butterworth-magnitude band filter: keeps a loop seamless."""
    L = len(x)
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(L, 1 / SR)
    f[0] = 1e-6
    H = np.ones_like(f)
    if lo:
        H /= np.sqrt(1 + (lo / f) ** 4)
    if hi:
        H /= np.sqrt(1 + (f / hi) ** 4)
    H[0] = 0
    return np.fft.irfft(X * (H[:, None] if x.ndim == 2 else H), L, axis=0)


def _fin_loop(x, peak):
    """Loop finish: remove DC exactly (mean), normalise. No trim / fades."""
    x = np.asarray(x, np.float64)
    x = x - x.mean(axis=0)
    return norm(x, peak)


def _per(f, L):
    """Snap a frequency so it has a whole number of cycles in L samples (seamless)."""
    return max(1, round(f * L / SR)) * SR / L


# ============================================================ barrages (loops)
def _barrage_loop(name, loop, rate, dark, seed):
    rng = _rng(name, seed)
    L = _n(loop)
    k = max(2, int(round(loop * rate)))
    k += k % 2                                   # even count -> L/R alternation survives the seam
    per = L / k
    if dark:
        base = dict(f0=175, f1=58, drop=0.03, tau=0.05, bright=1700, smack=0.6, slap=1.7,
                    slap_lp=1900, slap_tau=0.028, drive=3.4, tri=0.4, knock=1.2)
    else:
        base = dict(f0=260, f1=75, drop=0.022, tau=0.042, bright=5200, smack=0.9, slap=1.2,
                    slap_lp=3200, slap_tau=0.022, drive=2.6, tri=0.2, knock=0.8)
    temps = []
    for _ in range(8):
        v = rng.uniform(0.86, 1.14)
        temps.append(_hit(dur=0.16, rng=rng, **dict(base, f0=base['f0'] * v, f1=base['f1'] * v)))
    out = np.zeros((L + _n(0.3), 2))
    for i in range(k):
        at = int(i * per + rng.uniform(-0.12, 0.12) * per)
        pan = (0.35 if i % 2 else -0.35) + rng.uniform(-0.12, 0.12)
        _place(out, _pan(temps[rng.integers(8)], pan), max(0, at), rng.uniform(0.82, 1.0))
    out = _fold(out, L)
    t = _t(L)
    fr = k / (L / SR)                                        # bed pulses exactly k times per loop
    bed = _cband(noise(L, rng), 150, 900) if dark else _cband(noise(L, rng), 500, 3200)
    bed *= 0.55 + 0.45 * np.sin(np.pi * fr * t) ** 2
    out += _st(bed) * (0.18 if dark else 0.14)
    if dark:
        dr = osc(_per(41.2, L), L, 'saw') + osc(_per(43.7, L), L, 'saw')
        out += _st(_cband(dr, None, 260)) * 0.07
    return _fin_loop(out, 0.88)


@reg('ora_loop', 'ORA barrage, seamless loop while J is mashed (loop=1.0 s, 16 hits/s, stereo)', loop=1.0)
def _ora_loop(loop=1.0, rate=16.0, seed=0):
    return _barrage_loop('ora_loop', float(loop), float(rate), False, seed)


@reg('muda_loop', 'MUDA barrage loop (DIO / dark enemies), seamless (loop=1.0 s, stereo)', loop=1.0)
def _muda_loop(loop=1.0, rate=16.0, seed=0):
    return _barrage_loop('muda_loop', float(loop), float(rate), True, seed)


@reg('rapier_loop', 'Silver Chariot thrust barrage: swish + tink 18/s, seamless (loop=1.0 s, stereo)', loop=1.0)
def _rapier_loop(loop=1.0, rate=18.0, seed=0):
    rng = _rng('rapier_loop', seed)
    L = _n(loop)
    k = int(round(loop * rate))
    k += k % 2
    per = L / k
    out = np.zeros((L + _n(0.3), 2))
    for i in range(k):
        sn = _n(0.035)
        sw = sweep(noise(sn, rng), _dsig(sn, 2000, 7500), 'bp', q=1.6) * np.sin(np.pi * np.linspace(0, 1, sn)) ** 2
        tk = _metal(_n(0.12), np.array([3200, 4700, 6100]) * rng.uniform(0.94, 1.06), [0.03, 0.022, 0.015],
                    [1, .6, .4], rng, 0.004)
        one = np.zeros(_n(0.16))
        _place(one, sw, 0, 0.9)
        _place(one, tk, _n(0.03), 0.45)
        at = int(i * per + rng.uniform(-0.1, 0.1) * per)
        _place(out, _pan(one, (0.3 if i % 2 else -0.3) + rng.uniform(-0.1, 0.1)), max(0, at), rng.uniform(0.8, 1))
    return _fin_loop(_fold(out, L), 0.7)


@reg('timestop_hum', 'Stopped-time drone "嗡": frozen gong partials + sub + airy shimmer, seamless (loop=4 s, stereo)',
     loop=4.0)
def _timestop_hum(loop=4.0, seed=0):
    rng = _rng('timestop_hum', seed)
    L = _n(loop)
    t = _t(L)
    f = 73.4
    x = np.zeros(L)
    for r, a in zip([1.0, 2.0, 2.41, 2.98, 4.07], [1.0, 0.55, 0.4, 0.3, 0.18]):
        for d in (0.997, 1.003):                   # slow beating, snapped to whole cycles
            x += a * osc(_per(f * r * d, L), L, ph0=rng.uniform())
    x *= 0.8 + 0.2 * np.sin(_TAU * (2 / (L / SR)) * t)            # 2 swells per loop
    sub = osc(_per(36.7, L), L) * 0.8
    air = _cband(noise(L, rng), 2500, 6000) * (0.5 + 0.5 * np.sin(_TAU * (1 / (L / SR)) * t) ** 2) * 0.25
    left = x + sub + air
    right = np.roll(x, L // 3) + sub + np.roll(air, L // 2)
    return _fin_loop(np.stack([left, right], -1), 0.5)


# ============================================================ hits / defence / movement
@reg('dodge', 'Dodge dash: tight swish + afterimage echoes (0.35 s)', la=-17)
def _dodge(seed=0):
    rng = _rng('dodge', seed)
    n = _n(0.22)
    u = np.linspace(0, 1, n)
    c = 700 * (6000 / 700) ** (np.sin(np.pi * np.clip(u / 0.8, 0, 1)) ** 1.2)
    x = sweep(noise(n, rng), c, 'bp', q=1.5) * np.sin(np.pi * u) ** 1.6
    m = _n(0.04)
    x[:m] += 0.25 * _chirp(m, 1800, 900, 0.015, 'square', 0.25, 0.001)
    x = delay(x, 0.045, fb=0.45, taps=3, lpf=5000)                   # 残影 echoes
    return _fin(x, 0.55, 0.002, 0.03)


@reg('guard', 'Stand guard: dull metallic clank + short ring (0.5 s)', la=-15)
def _guard(seed=0):
    rng = _rng('guard', seed)
    n = _n(0.45)
    x = _hit(320, 140, 0.01, 0.03, 0.45, rng, bright=5000, smack=0.9, slap=0.5, slap_lp=2500,
             slap_tau=0.015, drive=2.2, knock=0.4)
    ring = _metal(n, [520, 1180, 1730, 2650], [0.12, 0.09, 0.07, 0.05], [1, .8, .6, .4], rng, 0.006)
    x = x + 0.6 * ring + 0.4 * bp(noise(n, rng), 2000, 6000) * env_exp(n, 0.01, 0.0003)
    x = verb(x, wet=0.12, sec=0.4, tau=0.08, lpf=6000, seed=21)
    return _fin(x, 0.75, 0.0005, 0.04)


@reg('parry', 'Perfect guard "KIIN": bright long metal ring + snap (0.9 s)', la=-15)
def _parry(seed=0):
    rng = _rng('parry', seed)
    n = _n(0.9)
    ring = _metal(n, [2093, 3140, 4400, 5870], [0.45, 0.3, 0.2, 0.12], [1, .7, .5, .3], rng, 0.002)
    ring *= np.minimum(_t(n) / 0.001, 1)
    x = 0.8 * ring + 0.35 * _ping(n, 4186, 0.25, 0.001, ((1, 1), (1.5, 0.3)))
    x += 0.7 * hp(noise(n, rng), 3000) * env_exp(n, 0.006, 0.0002)
    x += 0.5 * osc(_dsig(n, 160, 70), n) * env_exp(n, 0.04, 0.001)
    x = verb(x, wet=0.2, sec=0.8, tau=0.2, lpf=9000, seed=22)
    return _fin(x, 0.7, 0.0005, 0.1)


@reg('crit', 'Critical hit: heavy body + glassy crack + ring (0.9 s, stereo)', la=-11, push=7)
def _crit(seed=0):
    rng = _rng('crit', seed)
    n = _n(0.6)
    x = _hit(210, 46, 0.045, 0.14, 0.6, rng, bright=4500, smack=1.1, slap=1.6, slap_lp=3000,
             slap_tau=0.05, drive=3.4, sub=0.3, knock=1.1)
    x += 0.6 * hp(noise(n, rng), 3000) * env_exp(n, 0.006, 0.0002)
    x += 0.35 * _metal(n, [1900, 2870, 4100], [0.2, 0.15, 0.1], [1, .7, .5], rng, 0.004)
    x += 0.5 * bp(snh(n, 6000, rng), 300, 5000) * env_exp(n, 0.04, 0.0005)
    x = verb(sat(x, 1.6), wet=0.2, sec=0.7, tau=0.15, lpf=5000, seed=23)
    return _fin(x, 0.9, 0.0005, 0.08)


@reg('ko_hit', 'KO finisher: huge punch + gong + boom, slow-motion warped tail (2.6 s, stereo)', la=-11, push=7)
def _ko_hit(seed=0):
    rng = _rng('ko_hit', seed)
    n = _n(2.2)
    x = _hit(150, 32, 0.07, 0.35, 2.2, rng, bright=3500, smack=1.2, slap=2.0, slap_lp=2800,
             slap_tau=0.08, drive=4.0, sub=0.6, knock=1.2)
    x += 0.6 * bp(snh(n, 5500, rng), 300, 5000) * env_exp(n, 0.06, 0.0005)
    g = _metal(n, [73.4 * r for r in (1.0, 2.0, 2.41, 2.98, 4.07)], [1.2, 0.8, 0.7, 0.5, 0.4],
               [1.0, .7, .55, .5, .4], rng, 0.0025)
    x += 0.5 * g * np.minimum(_t(n) / 0.004, 1)
    spd = np.interp(np.linspace(0, 1, n), [0, 0.15, 1], [1.0, 1.0, 0.45])     # slow-mo sag
    x = fade(_warp(sat(x, 1.5), spd), 0.0, 0.5)          # fade the warped dry before the reverb
    x = verb(x, wet=0.3, sec=1.6, tau=0.45, lpf=3500, seed=24)
    return _fin(x, 0.92, 0.0005, 0.3)


# ============================================================ stand / meter / super
_SUMMON = {   # chord (saw), colour layer
    'star': (('E2', 'B2', 'E3', 'G#3', 'B3'), 'punch'),
    'hiero': (('G3', 'D4', 'G4', 'B4', 'D5'), 'chime'),
    'chariot': (('A2', 'E3', 'A3', 'C#4', 'E4'), 'shing'),
    'red': (('D2', 'A2', 'D3', 'F#3', 'A3'), 'fire'),
    'purple': (('C3', 'G3', 'C4', 'E4', 'G4'), 'vine'),
    'fool': (('F2', 'C3', 'F3', 'A3', 'C4'), 'sand'),
    'world': (('C2', 'G2', 'C3', 'Eb3', 'G3'), 'gong'),
}


@reg('stand_summon', 'Stand appears: rising swish + glide -> chord stab + colour layer at +0.25 s (kind=star..world)',
     la=-14)
def _stand_summon(kind='star', seed=0):
    rng = _rng('stand_summon_' + str(kind), seed)
    notes, colour = _SUMMON.get(kind, _SUMMON['star'])
    hit = 0.25
    n = _n(1.4)
    x = np.zeros(n)
    pn = _n(hit)
    u = np.linspace(0, 1, pn)
    sw = sweep(noise(pn, rng), 400 * (6000 / 400) ** u, 'bp', q=1.3) * u ** 2
    gl = sum(osc(nf(s) * 0.5 * 2 ** u, pn, 'saw') for s in notes[:3]) * u ** 2 * 0.25
    _place(x, sw + lp(gl, 3000), 0)
    m = n - pn
    ch = sum(osc(nf(s) * rng.uniform(0.998, 1.002), m, 'saw') for s in notes) * 0.3
    ch = sweep(ch, 700 + 5000 * np.exp(-_t(m) / 0.15), 'lp', q=1.0) * env_exp(m, 0.4, 0.003)
    _place(x, ch, pn, 0.9)
    _place(x, _kick(0.4, 140, 40, 0.13), pn, 0.9)
    if colour == 'punch':
        _place(x, _hit(230, 62, 0.03, 0.07, 0.3, rng, knock=0.8, slap=1.2), pn, 0.5)
    elif colour == 'chime':
        _place(x, _metal(m, [3136, 3951, 4699, 6272], [.3, .25, .2, .15], [1, .8, .6, .4], rng, 0.002), pn, 0.35)
    elif colour == 'shing':
        _place(x, _metal(m, [2210, 3470, 5130, 7020], [.25, .18, .12, .08], [1, .7, .5, .35], rng, 0.004), pn, 0.4)
    elif colour == 'fire':
        _place(x, sfx.make('fire_burst')[:, 0] * 0.6, pn - _n(0.05))
    elif colour == 'vine':
        _place(x, sfx.make('vine', dur=0.6) * 0.6, pn)
    elif colour == 'sand':
        _place(x, sfx.make('sand', dur=0.8) * 0.7, pn)
    elif colour == 'gong':
        _place(x, _metal(m, [73.4 * r for r in (1, 2, 2.41, 2.98)], [1.2, .8, .7, .5], [1, .7, .5, .4], rng), pn, 0.5)
    _place(x, _cymbal(m, rng, 0.5, 4500), pn, 0.25)
    x = verb(x, wet=0.22, sec=0.9, tau=0.2, lpf=6000, seed=25)
    return _fin(x, 0.8, 0.001, 0.15)


@reg('meter_full', 'Stand energy full: quick chip arpeggio + shimmer ping (0.8 s)', la=-17)
def _meter_full(seed=0):
    seq = [(k * 0.03, 0.028, nf(s), 0.8) for k, s in enumerate(['E6', 'G#6', 'B6', 'E7'])]
    x = _seq(seq, 0.8, 'square', 0.125, a=0.001, d=0.04, s=0.6, r=0.02)
    pn = _n(0.6)
    pg = _ping(pn, nf('E7'), 0.22, 0.001, ((1, 1.0), (2.0, 0.25)))
    pg *= 1 + 0.4 * np.sin(_TAU * 24 * _t(pn))
    _place(x, pg, _n(0.12), 0.5)
    sn = _n(0.15)
    _place(x, _chirp(sn, 1200, 2400, 0.08, 'sine', attack=0.01), 0, 0.25)
    return _fin(delay(x, 0.06, 0.3, 2), 0.45, 0.0005, 0.08)


@reg('super_start', 'Super move start: flash snap + rising cut-in swish -> minor stab at +0.5 s (1.8 s, stereo)',
     la=-13)
def _super_start(seed=0):
    rng = _rng('super_start', seed)
    hit = 0.5
    n = _n(1.6)
    x = np.zeros(n)
    fn = _n(0.4)
    snap = hp(noise(fn, rng), 3000) * env_exp(fn, 0.04, 0.0005) * 0.7 + osc(_dsig(fn, 110, 45), fn) * env_exp(fn, 0.15)
    _place(x, snap, 0)
    rn = _n(hit)
    u = np.linspace(0, 1, rn)
    rise = sweep(noise(rn, rng), 300 * (8000 / 300) ** u, 'bp', q=1.6) * u ** 2
    rise += lp(osc(150 * (1200 / 150) ** u, rn, 'saw'), 4000) * 0.2 * u ** 2
    _place(x, rise, 0, 0.9)
    m = n - rn
    st = sum(osc(nf(s), m, 'saw') for s in ('A2', 'E3', 'A3', 'C4', 'E4')) * 0.35
    st = sweep(st, 800 + 5000 * np.exp(-_t(m) / 0.12), 'lp', q=1.0) * env_exp(m, 0.35, 0.003)
    _place(x, st, rn)
    _place(x, _kick(0.4, 150, 40, 0.14), rn)
    _place(x, _cymbal(m, rng, 0.45, 4000), rn, 0.3)
    x = verb(x, wet=0.2, sec=0.9, tau=0.2, lpf=6000, seed=26)
    return _fin(x, 0.85, 0.001, 0.15)


# ============================================================ UI
def _ui_notes(notes, step, kind='square', duty=0.25):
    seq = [(k * step, step * 0.9, nf(s), 1.0) for k, s in enumerate(notes)]
    return _seq(seq, step * len(notes) + 0.06, kind, duty, a=0.001, d=0.03, s=0.7, r=0.015)


@reg('menu_move', 'Menu cursor move: 25 ms chip tick (A5)', la=-24)
def _menu_move():
    return _fin(_ui_notes(['A5'], 0.025, 'chip', 0.25), 0.25, 0.0005, 0.004, dc=False)


@reg('menu_confirm', 'Menu confirm: E6 -> B6 two-note chip (0.12 s)', la=-21)
def _menu_confirm():
    return _fin(delay(_ui_notes(['E6', 'B6'], 0.045), 0.05, 0.25, 1), 0.3, 0.0005, 0.01, dc=False)


@reg('menu_cancel', 'Menu cancel / back: B5 -> E5 descending (0.12 s)', la=-22)
def _menu_cancel():
    return _fin(_ui_notes(['B5', 'E5'], 0.045), 0.28, 0.0005, 0.01, dc=False)


@reg('menu_error', 'Not allowed buzz: detuned low square (0.16 s)', la=-22)
def _menu_error():
    n = _n(0.16)
    x = (osc(110, n, 'chip', 0.5) + osc(116.5, n, 'chip', 0.5)) * env_pts(n, [(0, 0), (0.005, 1), (0.13, 0.8), (0.16, 0)])
    return _fin(lp(x, 3000, 1), 0.25, 0.0005, 0.01, dc=False)


# ============================================================ voices (no real voices: formant synth)
_VOICE = {   # f0 start, f0 end, formant scale, noise (rasp), drive
    'jotaro': (110, 82, 0.92, 0.25, 2.2), 'kakyoin': (150, 112, 1.0, 0.2, 2.0),
    'polnareff': (140, 100, 1.0, 0.3, 2.2), 'avdol': (95, 72, 0.9, 0.3, 2.4),
    'joseph': (135, 95, 1.0, 0.5, 2.0), 'enemy': (100, 70, 0.88, 0.45, 2.8), 'dio': (115, 80, 0.95, 0.4, 3.0),
}


@reg('grunt', 'Hurt grunt "UGH" by formant synthesis (voice=jotaro/kakyoin/polnareff/avdol/joseph/enemy/dio, 0.3 s)',
     la=-16)
def _grunt(voice='jotaro', seed=0):
    rng = _rng('grunt_' + str(voice), seed)
    f0a, f0b, fs, rasp, drive = _VOICE.get(voice, _VOICE['jotaro'])
    n = _n(0.3)
    t = _t(n)
    f0 = np.interp(t, [0, 0.03, 0.3], [f0a * 1.15, f0a, f0b]) * (1 + 0.02 * np.sin(_TAU * 30 * t))
    src = osc(f0, n, 'saw') + 0.5 * osc(f0 * 0.5, n, 'square', 0.4) * rasp + rasp * noise(n, rng)
    src *= np.interp(t, [0, 0.012, 0.08, 0.22, 0.3], [0, 1, 0.85, 0.25, 0])
    F1 = np.interp(t, [0, 0.05, 0.3], [380, 680, 560]) * fs
    F2 = np.interp(t, [0, 0.05, 0.3], [900, 1150, 1050]) * fs
    y = _formant(src, [(F1, 5, 1.0), (F2, 6, 0.7), (2500 * fs, 7, 0.25)])
    return _fin(sat(y * 3, drive), 0.6, 0.002, 0.03)


@reg('ora_voice', 'Synthetic "O-RA!" chant syllables at ~7/s (n syllables; formant o->a; experimental)', la=-15)
def _ora_voice(n=4, rate=7.0, f0=165.0, seed=0):
    rng = _rng('ora_voice', seed)
    k = max(1, int(n))
    per = 1.0 / float(rate)
    out = np.zeros(_n(per * k + 0.1))
    m = _n(per)
    t = _t(m)
    for i in range(k):
        f = float(f0) * rng.uniform(0.97, 1.05) * np.interp(t, [0, per * 0.4, per], [1.0, 1.08, 0.95])
        src = osc(f, m, 'saw') + 0.4 * osc(f * 0.5, m, 'square', 0.4) + 0.2 * noise(m, rng)
        a = np.interp(t, [0, 0.01, per * 0.38, per * 0.45, per * 0.52, per * 0.85, per], [0, 1, 0.9, 0.25, 1, 0.7, 0])
        F1 = np.interp(t, [0, per * 0.4, per * 0.5, per], [450, 450, 800, 780])
        F2 = np.interp(t, [0, per * 0.4, per * 0.5, per], [800, 800, 1250, 1200])
        y = _formant(src * a, [(F1, 5, 1.0), (F2, 6, 0.7), (2600, 7, 0.2)])
        _place(out, sat(y * 3, 2.0), _n(i * per), 1.0 if i % 2 == 0 else 0.85)
    return _fin(out, 0.65, 0.002, 0.03)
```

原型实测（`proto_test.py` 输出，44.1 kHz）：

| 名字 | 时长 s | 声道 | 峰值 | LA dB | 构建 ms | 循环接缝 |
|---|---|---|---|---|---|---|
| ora_loop | 1.000 | 2 | 0.88 | −14.5 | 11.7 | 0.0052（10 百分位） |
| muda_loop | 1.000 | 2 | 0.88 | −14.9 | 13.2 | 0.0281（70 百分位） |
| rapier_loop | 1.000 | 2 | 0.70 | −18.7 | 6.0 | 0.0417（53 百分位） |
| timestop_hum | 4.000 | 2 | 0.50 | −34.8 | 73.2 | 0.0050（26 百分位） |
| dodge | 0.355 | 1 | 0.55 | −17.4 | 2.4 | |
| guard | 0.570 | 2 | 0.75 | −17.2 | 13.0 | |
| parry | 1.541 | 2 | 0.70 | −15.8 | 38.2 | |
| crit | 1.150 | 2 | 0.90 | −13.9 | 19.7 | |
| ko_hit | 3.260 | 2 | 0.92 | −13.6 | 79.8 | |
| stand_summon（star/hiero/chariot/red/purple/fool/world） | 1.95–2.09 | 2 | 0.80 | −16.1 ~ −17.4 | 47–69 | |
| meter_full | 0.866 | 1 | 0.45 | −19.3 | 5.6 | |
| super_start | 2.209 | 2 | 0.85 | −15.2 | 54.7 | |
| menu_move / confirm / cancel / error | 0.066 / 0.178 / 0.128 / 0.160 | 1 | 0.21–0.25 | −24.0 / −21.0 / −22.0 / −25.8 | ≤ 1.3 | |
| grunt（7 种声线） | 0.300 | 1 | 0.36–0.47 | −16.0 | ~3 | |
| ora_voice（n=4） | 0.622 | 1 | 0.48 | −15.0 | 6.2 | |
| dog_bark pitch 1.4（伊奇受伤） | 0.214 | 1 | 0.33 | −15.2 | 2.2 | |

---

## 附录 B：新曲原型 `game_music_proto.py`（渲染通过）

```python
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, r'D:\大疆\游戏素材\JoJo\源码')
from engine import music
from engine.music import (BRASS, CHIP, FMBASS, HARM, LEAD, PLUCK, TRIBASS, Song)


def _t_battle_egypt():
    S = Song('battle_egypt', bpm=160, bars=16, key='E', mode='phrygian', seed=123)
    S.chords('''E:16 | F:8 E:8 | Dm:16 | E:8 F:8 |
                E:16 | F:8 E:8 | G:8 F:8 | E:16 |
                Am:16 | G:16 | F:16 | E:16 |
                Am:8 G:8 | F:8 E:8 | Dm:8 F:8 | E:16 |''')
    A = '''E5:2 F5:2 G#5:2 A5:2 G#5:3 F5:1 E5:4 | F5:3 E5:1 D5:2 C5:2 B4:4 r:4 |
           D5:2 E5:2 F5:2 A5:2 G5:4 F5:2 E5:2 | G#5:4 F5:2 E5:2 D5:4 E5:4 |
           E5:2 F5:2 G#5:2 A5:2 B5:3 A5:1 G#5:4 | C6:3 B5:1 A5:2 G#5:2 F5:4 E5:4 |
           D5:4 G5:4 F5:2 E5:2 D5:2 F5:2 | E5:12 r:4 |'''
    B = '''A5:3 C6:1 E6:4 D6:2 C6:2 B5:4 | G5:3 B5:1 D6:4 C6:2 B5:2 A5:4 |
           F5:3 A5:1 C6:4 B5:2 A5:2 G#5:4 | E5:2 F5:2 G#5:2 B5:2 E6:8 |
           C6:4 B5:2 A5:2 B5:4 A5:2 G5:2 | A5:4 G#5:2 F5:2 E5:8 |
           D5:2 F5:2 A5:2 D6:2 C6:2 A5:2 F5:2 A5:2 | G#5:4 B5:4 E6:4 E5:4 |'''
    S.voice(S.parse(A + B), LEAD, pan=-0.08, dly=0.18, rev=0.08, name='lead', role='lead')
    S.voice(S.parse(B, bar0=8, tr=-12, vel=0.7), dict(BRASS, gain=0.26), pan=0.3, rev=0.1, name='brass')
    S.voice(S.harmonize(S.parse(A, vel=0.6), -2), HARM, pan=0.38, dly=0.1, rev=0.08, name='harm')
    S.voice(S.arp('0:1 1 2 1 0 1 2 3 0 1 2 1 0 1 2 3', 52, 71, bars=(8, 16), vel=0.7), PLUCK, pan=0.42,
            dly=0.2, rev=0.08, name='arp')
    S.voice(S.stabs('x--x--x-x--x--x-', 52, 69, 3, bars=(0, 8)), CHIP, pan=-0.3, rev=0.08, name='chip')
    bass = S.bass('R:2 R O R R O R O', lo=40)
    S.voice(bass, TRIBASS, name='tri')
    S.voice(bass, dict(FMBASS, gain=0.24), name='fm', pan=0.05)
    S.drums('c...k.t.k.k.t...' + 'k...k.t.k.k.t...' * 6 + 'k...k.t.T.m.t.tt'
            + 'c...s..kk.k.s...' + 'k...s..kk.k.s...' * 6 + 'k...s...T.m.t.sS')
    S.drums('h.h.h.h.h.h.h.h.' * 8 + 'hhHhhhHhhhHhhhHh' * 8, gain=0.8)
    S.drums('..z...z...z...z.' * 8 + '................' * 8, gain=0.7)
    S.rms_target = 0.2
    return S


music._BUILDERS['battle_egypt'] = _t_battle_egypt
music.TRACKS['battle_egypt'] = 'Egypt battle. E phrygian-dominant, 160 bpm, 16 bars.'
# music.track('battle_egypt') -> 1.94 s, (1053696, 2), bpm 160.714, bar_sec 1.4933, loop 23.893 s, 峰 0.890, RMS 0.200
```
（旋律只是验证记谱和渲染能跑通的占位稿，没有经过作曲审听；正式用之前要再写、再听。）

---

## 附录 C：试跑脚本（scratch `audio07\`，会话删了就没了）

| 脚本 | 作用 |
|---|---|
| `render_test.py [all \| music 名… \| sfx 名…]` | 渲染配乐 / 音效到 `out\music\*.wav`、`out\sfx\*.wav`，打印耗时、长度、峰值、RMS、直流、削波、接缝，写 `out\report_*.json` |
| `browser_loop_test.py battle` | 编码 mp3/ogg/opus/m4a → base64 .js → Playwright Chromium 打开 file:// 页面解码，比长度和起点偏移，并试 `<audio>` 播放 |
| `browser_sfx_test.py` | 同上，测短音效 mp3 的长度 |
| `browser_ctx_test.py` | 真 AudioContext：采样率、解码长度、loop、file:// 下 fetch 是否可用 |
| `game_sfx_proto.py` + `proto_test.py` | 附录 A 的原型及测量，输出 `out\proto\*.wav`、`*_x4.wav`（循环音效重复 4 遍，方便试听接缝）、`proto.json` |
| `grid.py out\proto` | 原型的波形 + 频谱总览图 `out\proto\grid.png` |
| `game_music_proto.py` | 附录 B，输出 `out\music\battle_egypt.wav` |

运行前都要 `PYTHONDONTWRITEBYTECODE=1`；Python 3.12.10、numpy 2.5.3、scipy 1.16.3、ffmpeg 8、playwright（Chromium）。
