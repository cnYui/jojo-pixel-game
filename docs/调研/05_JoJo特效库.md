# 05 JoJo 原工程特效库调研（fx.py / text.py / _fxdemo.py）

> 调研对象：`D:\大疆\游戏素材\JoJo\源码\engine\fx.py`（2560 行，全读）、`docs\FX.md`、`engine\text.py`（357 行）、`scenes\_fxdemo.py`（441 行），以及它们依赖的 `engine\core.py`、`engine\sprite.py`；为了查“每个替身的招牌特效”实际怎么用，还读了 s00 / s03 / s07 / s11 / s13 / s15 / s18 等场景里的相关段落。
> 写给：后面动手做 `D:\大疆\游戏素材\JoJo\游戏\` 的工程师。行号都是 2026-10-09 时的源码行号。
> 试跑：在会话 scratchpad 里跑了全部特效的耗时测试和联系表（`scratchpad\understand\fx_bench.py`、`fx_sheet_00..05.png`、`fx_timing.txt`），没在 `源码\` 留 `__pycache__`（已核对）。

---

## 0. 先看这几条（结论）

1. **原片特效 = 一组“时间的纯函数”**：`fx.xxx(fr, …, t, t0, …)` 每帧无条件调用，`t < t0` 或过了时长就什么都不画；粒子全靠 `hash01(seed, i, …)` 解析算出来，**不存任何状态**。移植到游戏时最省事的做法是保留这个模型：特效实例只存 `{fn, t0, 参数, clock}`，每帧用 `now - t0` 重算；过期就删。
2. **画在哪一层**：除了 `tbc_arrow`（画 UI 层）以外，fx.py 全部画在**底层 320×180 像素画布**（`fr.img`）上；text.py 全部画在 **UI 层 640×360**（`fr.ui`，= 底层 ×2）。合成：底层最近邻放大 ×2 → 叠 UI → 最终 ×3 出 1920×1080。
3. **像素风的三条铁律**：不抗锯齿；半透明一律用**屏幕对齐的 Bayer 4×4 有序抖动**（`_bay` / `BAYER4`），而不是平滑 alpha；颜色用有限调色板分级（`_qblend`、`_lummap`、火焰 `lvl`）。JS 里用 `ctx.globalAlpha` 直接画会破坏画风——要自己写软件光栅（见 §7）。
4. **全屏像素滤镜（时停、冲击帧、褐色定格、晕影、旋涡背景）都要读回像素**。实测：**Chromium 下 `file://` 加载的 PNG 画进 canvas 后 `getImageData` 直接抛 `SecurityError`，data URI 的图则正常**（`scratchpad\understand\taint_test.py`）。所以凡是进底层画布的图（角色图集、道具、背景、特效小图）都必须以 **data URI 内嵌进 data.js**，或者整条底层走纯软件帧缓冲。银魂没碰到这个问题是因为它从不读像素。
5. **性能不是问题**：Python + numpy 里最贵的全屏滤镜也就 1–4 ms（表见 §10）；JS 用 `Uint32Array` 帧缓冲，320×180 = 57 600 像素一趟循环约 0.1–0.5 ms。真正要预烘的只有：**所有屏上文字**（要 1-bit 字形）、**fire_ankh 的高斯热场**（原来用 scipy）、几张小纹理。
6. **原片的“战斗爽”其实已经有完整语法**：冲击帧序列（invert 1 帧 → 替身色 1 帧 → 紫色定格）、虚拟时钟定格（s18 `vt`、s15 `gem_t`）、命中火花 + 冲击环 + 震屏 + 拟声字四件套、必杀特写切入（s18 `portrait_cut`、s07 `shot_E3`、s10 `slam`）。游戏里缺的主要是**交互层面的**：命中停顿、受击闪白、闪避残影的历史轨迹、格挡、能量满提示、低血警示（配方见 §8）。

---

## 1. 原工程特效系统总览

### 1.1 坐标、图层、时间

| 项 | 值 | 出处 |
|---|---|---|
| 底层画布 | `W, H = 320, 180`（像素画，角色、背景、全部 fx） | core.py:13 |
| UI 层 | `UI = 2`，`UW, UH = 640, 360`（文字、对话框、卡片） | core.py:14-15 |
| 成片 | 640×360 再 ×3 = 1920×1080，24 fps | core.py:16-17 |
| 默认地面线 | `GROUND = 150` | core.py:18 |
| 角度约定 | 度，**0 = 向右，90 = 向上**（屏幕 y 向下，所以公式里是 `y - sin(a)·v`） | fx.py:16, FX.md:17 |
| 颜色 | `'#rrggbb'`、`(r,g,b)` 或 `core.C` 的键（`'white' 'emerald' 'yellow' 'menace'…`） | core.py:21-66 |
| 1 帧 | 场景里常写 `FT = F1 = 1/24`，冲击帧就是 `t0 ≤ t < t0 + FT` | s18:25, s13:225 |

**画的顺序 = 调用顺序**（FX.md:12-14）：背景 → 阴影 → 角色 → 命中特效 → 全屏滤镜（`impact_frame`、`timestop_world`、`sepia`、`vignette`、各种 wipe）→ 必须不受滤镜影响的东西（比如时停里还能动的 DIO / 承太郎）。

### 1.2 Frame 的相机后处理（core.py:193-298）

这些不是 fx.py 的函数，但几乎每个打击镜头都配着用（全工程 `fr.shake` 90 次、`fr.zoom` 69 次、`fr.flash` 47 次）：

| 调用 | 作用 | 公式 / 细节 |
|---|---|---|
| `fr.shake(amp, seed=0, freq=30)` | 本帧整幅底层平移 | `k = int(t·freq)`；`dx = round((hash01(k,seed,1)·2-1)·amp)`，`dy` 同理用 `…,2`。每秒换 30 次位置。常配 `tw(t, t0, t0+0.25, 3, 0)` 线性衰减 |
| `fr.zoom(z, cx, cy)` | 以底层点 (cx,cy) 为中心放大 | 取宽 `W/z`、高 `H/z` 的框（z≥1 时夹在画布内），最近邻缩放到 640×360；和 shake 叠加时框平移 |
| `fr.flash(colour, amount)` | 底层整体向某色**平滑**混合（`Image.blend`，不是抖动） | 只作用底层，UI 不变 |
| `fr.fade(a, colour)` | 最终画面（底层+UI）平滑淡到某色 | |
| `fr.dither_fade(a, colour)` | 最终画面按 Bayer（单元 2×2 UI 像素）抖动淡出 | 场景首尾默认 0.3 s |
| `compose()` 顺序 | flash → shake/zoom 裁切放大 → 叠 UI → fade → dither_fade | core.py:262-298 |

### 1.3 调色板常量（fx.py:241-254, 426-434；core.py:48-66）

```
PALETTES（暗→亮）
 fire   #5a0c1c #b8182a #e8501a #ff9820 #ffd840 #fffbe0
 blue   #101848 #2440b0 #3c88f0 #58d0f8 #b8f4ff #ffffff
 green  #08381c #15803c #28c860 #80f0a0 #e0ffe8
 purple #200838 #5a2890 #9a4ce0 #d090ff #fbe8ff
 gold   #4a2a06 #a86a10 #e0a020 #ffd83c #fff8c0
 ts_yellow #12140a #343a1c #626a34 #98a05a #cfd490 #f6f6d0   ← DIO 时停
 ts_blue   #0a0c20 #1c2856 #364e92 #6484c4 #a4c0ea #e6f0ff   ← 承太郎时停
 ts_gray   #101014 #34343c #5c5c66 #8a8a94 #bebec6 #f0f0f4
 ts_purple #120a20 #34205a #5e4094 #9270c8 #c8b0ec #f4ecff
 ts_green  #08140c #1a3a24 #34684a #5e9a72 #9cd0a8 #e0f8e4
 sepia     #1e1208 #42301a #6e5230 #9c7a4c #c8a874 #eedcae
IMPACT（冲击帧，暗→亮）
 bw #000000 #ffffff | bw3 #000000 #8a8a96 #ffffff | red #16000a #d81c38 #ffe8d8
 purple #1c0832 #8a34d0 #ffe040 | yellow #1a0c00 #e09a18 #fffbe0
 blue #040a24 #2c58e0 #d8f4ff | green #021a0c #18b060 #f0ffe0
_FIREBALL（爆炸火球冷却色带）#ffffff #fff6c0 #ffe050 #ffa820 #f06418 #c8202a #80182a #5a3040 #4a4050
C['menace'] = (170,60,220)  ← ゴゴゴ 的默认颜色
精灵通用描边 k = #1a1020（近黑紫）
```

### 1.4 无血约定

fx.py:17、FX.md:21：“NO gore”——命中只有火花、闪光、冲击星；s07 的火焰碎块特意保持橙黄（`fire_chunks` 注释“dark red read as blood”，s07:255）。游戏里也照这个来。

---

## 2. 底层公共函数（JS 移植必须先写的那一层）

### 2.1 core.py

| 函数 | 行 | 说明 / 公式 |
|---|---|---|
| `hash01(*xs)` | 165-175 | FNV 变体：`h=2166136261`；对每个参数：整数直接用，**浮点数先 `int(round(x·997))`**；`h ^= v & 0xFFFFFFFF`；`h = h·16777619 mod 2³²`；`h ^= h>>13`；`h = h·0x5BD1E995 mod 2³²`；`h ^= h>>15`；返回 `h / 2³²` ∈ [0,1) |
| `hrange(a,b,*xs)` | 178 | `a + (b-a)·hash01(*xs)` |
| `noise1(x, seed)` | 182-189 | 1D value noise ∈ [-1,1]，smoothstep 插值 |
| `ease(u, kind)` | 77-113 | `linear`；`in` u²；`out` 1-(1-u)²；`io` u²(3-2u)；`in3` u³；`out3` 1-(1-u)³；`back` s=1.70158, v=u-1, `v²((s+1)v+s)+1`；`bounce`（标准）；`elastic` `2^(-10u)·sin((10u-0.75)·2π/3)+1`；`step` |
| `prog(t,t0,t1)` | 116-120 | 夹到 [0,1] 的进度 |
| `tw(t,t0,t1,a,b,kind)` | 123-125 | `lerp(a,b,ease(prog))` |
| `keys(t, [(t,v)…])` | 128-138 | 分段关键帧 |
| `anim(t,fps,n)` | 145-148 | 帧号 `int(t·fps) % n` |
| `BAYER4` | 302-303 | `[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]/16 + 1/32` |
| `dither_blend` | 313-320 | `bayer < amount` 的像素换成颜色 |
| `paste(dst,src,x,y,alpha)` | 359-377 | **平滑** alpha 合成（alpha<1 时乘 alpha 通道）。注意：替身常以 `alpha=0.92` 用这个画，是平滑半透明，不是抖动 |
| `filt_tint / filt_invert / filt_gray / filt_map` | 380-419 | 整图调色（s03 召唤隐者之紫时 `filt_tint(fr.img,(38,12,60),0.55~0.8)` 把房间染紫） |

### 2.2 sprite.py

| 函数 | 行 | 说明 |
|---|---|---|
| `_apply_tint(im, tint, amt)` | 168-184 | `'white'`：`c + (255-c)·amt`；`'black'`：`c·(1-amt)`；`'gray'`：向亮度混；`'invert'`；或任意颜色：`c·(1-amt)+col·amt`。只改 RGB，alpha 不动 |
| `_outline(im, colour)` | 187-208 | 4 邻域外扩 1px 描边（画布四周各加 1px） |
| `render(name, frame, flip, scale, tint, amt, rot, outline)` | 242-249 | 带缓存的变体；先描边 → 染色 → 翻转 → 最近邻缩放 → 绕锚点旋转 |
| `draw(img, name, x, y, …, alpha)` | 252-265 | 锚点对齐到 (x,y) 后 `paste`（平滑 alpha） |
| `aura(img, name, x, y, frame, flip, scale, colour, t, alpha=0.55, grow=1)` | 268-285 | **替身光环**：精灵剪影 4 邻域膨胀 `grow` 次，整块涂成 colour，按 alpha 平滑贴在精灵后面；位置抖动 `jx = round(sin(23t))`、`jy = round(cos(17t))`（±1px）。**先画光环再画精灵** |

### 2.3 fx.py 内部辅助

| 函数 | 行 | 说明 |
|---|---|---|
| `_bay(x0,y0,w,h)` | 37-44 | 取屏幕对齐的 Bayer 阈值块（`_BAYF` 是预铺的大表）。抖动判断永远是 `bayer(x,y) < alpha` |
| `_comp(dst, layer, alpha)` | 83-92 | 整层按 `bayer < alpha` 抖动合成（speedlines/hamon/lightning 的半透明层用它） |
| `_paste_dither(dst, im, x, y, alpha)` | 95-106 | 贴图 + 抖动透明（残影、召唤淡入、碎片淡出） |
| `_disc_np(a, cx, cy, r, col, alpha, sq)` | 109-125 | 像素圆盘：`(x-cx)² + ((y-cy)/sq)² ≤ r² + 0.6r`（`+0.6r` 让小圆更圆润）；alpha<1 时再与 bayer 相与 |
| `_qblend(base, col, A, levels, add)` | 128-138 | 量化 + 抖动混色：`q = floor(clip(A)·levels + bayer)/levels`，结果 `base + (col-base)·q`（`add=True` 时 `base + col·q`）。glow / fog / vignette / light_beam / sand_wind 都靠它 |
| `_plot(a, xs, ys, col, alpha)` | 149-157 | 批量点，带抖动 |
| `_px(d, x, y, col, alpha)` | 160-165 | 单点，带抖动 |
| `_grid(g, pal)` | 168-182 | ASCII 网格 → RGBA（拳头、宝石、蝙蝠的程序兜底图） |
| `_figure(colour, w=26, h=44)` | 200-231 | 程序人形剪影（精灵缺失时兜底） |
| `_lum(a)` | 257-258 | `0.299R + 0.587G + 0.114B` |
| `_lummap(a, pal, strength, gamma)` | 261-271 | 亮度 → 调色板：`lum=(L/255)^gamma`；`idx = floor(lum·(L-1) + 0.5 + (bayer-0.5)·strength)`。时停 / 褐色定格的核心 |
| `_dist_field(cx,cy,sq)` / `_angle_field(cx,cy)` | 274-284 | 全屏距离 / 角度场（lru 缓存）。JS 里按中心点缓存 `Float32Array` |
| `_rmax(cx,cy)` | 287-288 | 中心到最远角的距离 +2（“盖满全屏”的半径） |
| `_noise_tex(seed, 64, 64, cells=4, octaves=3)` | 291-319 | 可平铺 value noise（numpy RNG `1000+seed`），归一化到 [0,1]；火焰 / 光环 / 安卡十字的闪烁纹理 |
| `_star_shape(d, x, y, r, col, thin)` | 322-337 | 4 角像素星：十字 + 中心小斜叉（r≥3）+ 内侧平行线（r≥5） |
| `_bolt_points(x0,y0,x1,y1,seed,k,depth,disp)` | 1119-1135 | 中点位移折线：每级在法线方向偏 `(hash-0.5)·2·amp`，`amp = L·disp` 每级减半。闪电和波纹共用 |
| `_puff(a, px, py, r, col, al)` | 715-726 | 烟团：外圈 r+1 抖动 0.45·al → 底色（混 22% 黑）r → 主体 (−0.12r,−0.2r) 0.82r → 高光 (−0.32r,−0.4r) 0.4r 亮 30%（r≥2.5） |

---

## 3. fx.py 逐函数说明

下表“时长”= 之后不再画（用于游戏里删特效实例）。“层”= 全部是底层 320×180，除非注明。

### 3.1 角色与替身

#### `shadow(fr, x, y, w=14, alpha=0.35, h=None)` — fx.py:353-366
- 样子：脚下扁椭圆，**两级**：内圈（归一化距离² ≤ 0.45）乘 `1-alpha`，外圈乘 `1-0.55·alpha`。`h` 默认 `max(2, round(w·0.28))`。
- 不是抖动，是对已有像素做乘法变暗（所以能落在任何背景上）。全工程调用 169 次。

#### `stand_summon(fr, name, x, y, t, t0, flip, frame, dur=0.35, aura_colour='#c080ff', alpha=0.92, rise=12, scale=1)` — fx.py:2383-2423
- **替身出现的全过程，之后就当作替身的常规绘制调用**（FX.md:156）。
- 召唤期 `u = (t-t0)/dur < 1`：
  - 位置：`yy = y + rise·(1 - ease_out(u))`（从下往上升 rise px 到位）。
  - 闪烁：`vis = int((t-t0)·30) % 2 == 0 or u > 0.55`（前 55% 以 30 Hz 隔帧消失）。
  - 光环：`sp.aura(..., alpha=0.7·u)`。
  - 本体：`tint='white', amt=round(1-u,2)`（由全白渐变回原色），用 `_paste_dither` 以 `alpha·min(1, 0.25+u)` 抖动透明贴上。
  - 8 条上升能量线：`sx = x + (hash01(j,3,int(t0·10))-0.5)·30`，`ph = (1.6u + hash01(j,4)) % 1`，`sy = y - 4 - 44·ph`，竖线长 `4 + int(6·hash01(j,5))`，颜色交替 aura_colour / `_light(aura_colour, 0.6)`。
- 召唤后：`sp.aura(...)`（alpha 0.55，±1px 抖动）+ `sp.draw(..., alpha=0.92)`（平滑半透明）。
- 精灵不存在时用 `_figure(aura_colour)` 兜底。
- 场景里的常用参数：慢召唤 `dur=0.3~0.35, rise=9~12`；快速出拳时 `dur=0.08~0.18, rise=0~8`（s08:220/463/528、s13:621/676）；巨大登场（愚者）`dur=T_REVEAL-T_RISE, rise=46, scale=3`（s11:544）。
- 消失：原工程没有 fx 函数，s07:152-158 的 `stand_out`：`u = prog(t,t0,t0+dur)`，`sp.render(..., 'white', u·0.8)` 再 `_paste_dither(..., 0.92·(1-u))`，`dur=0.2~0.25`。

#### `aura_flame(fr, src, x, y, t, frame, flip, colour='#c080ff', seed=0, grow=3, height=14, scale=1, intensity=1.0, fps=12)` — fx.py:2453-2485（辅助 `_aura_fields` 2426-2450）
- 样子：JoJo 式“气”——贴着精灵剪影外缘一圈 + 向上舔的火焰形轮廓，三色（`_dark(c,0.55)`、c、`_light(c,0.55)`）。**必须在画精灵之前调用**，同一锚点，精灵会盖住内部，只露出外缘火苗。
- 场：剪影 mask 4 邻域膨胀 `grow` 次 → `mf`；向上拖尾 `up[y-k] = max(up, mf[y]·(1-k/(K+1)))`，`K = height`（缓存，按 精灵名/帧/翻转/缩放）。
- 每帧：`ts = floor(t·12)/12`（12 fps 抽帧感）；噪声 `n = tex[(floor(yy·1.6 + ts·70)) % 64, (floor(xx·3.1 + seed·7)) % 64]`；`heat = max(mf·(0.55+0.5n), up·(0.2+1.2n))·intensity`；`lvl = floor(heat·3.4 + (bayer-0.5)·0.9)`，`lvl≥1` 的像素涂 `pal[min(lvl-1,2)]`。
- `aura_wisps(fr, x, y, t, …, src=None)`（2488-2493）只是别名。
- 场景用法：DIO `colour='#ffd040'`；阿布德尔走上前 `'#ff7a30', intensity: 0→0.8`（s07:554）；乔瑟夫 `'#a860f0', intensity 0.25→1`（s03:428）；必杀蓄力 `intensity=1.3`（s18:794）；伊奇 `'#e8c070', grow=2, height=10`（s13:701）。

#### `afterimage(fr, sprite_name, positions, frame=0, flip=False, colour=None, alpha0=0.3, alpha1=0.75, amt=0.45)` — fx.py:650-674
- 样子：一串幽灵副本。`positions` 从旧到新 `[(x,y) 或 (x,y,frame)]`；第 k 个副本抖动透明度 `alpha0 + (alpha1-alpha0)·k/(n-1)`。
- 给了 colour：染色 `amt`，并加一圈 `_dark(colour,0.55)` 描边；没给：向白染 0.3。
- **真身自己最后画**。
- 场景用法：冲刺 `colour='#8090ff'`（_fxdemo）；银色战车突刺 2 帧 `colour='#c8d8ff'`（s07:468）；替身互冲 `colour=AURA_SP/AURA_TW`（s18:611-614）；愚者滑翔 `'#e8c070'`（s13:681）；被打飞 `alpha0=0.2, alpha1=0.4`（s13:691）。

#### `shatter(fr, src, x, y, t, t0, pieces=40, seed=0, dur=1.2, frame, flip, scale, force=1.0, gravity=150, tint_to=None, origin=None)` — fx.py:2106-2153（`_voronoi_pieces` 2068-2093）
- 样子：精灵按 Voronoi 切成 `pieces` 块，炸开、下落、抖动淡出。时长 `dur`。
- 切块：在不透明包围盒里撒 `pieces` 个种子点（`hash01(seed,i,1/2)`），每个像素归最近的种子。
- 第 j 块：`delay = 0.06·hash01(seed,j,3)`，`e = max(0, dt-delay)`；`vx = (pcx-cxm)·2.2·force + (hash-0.5)·40·force`；`vy = (pcy-cym)·1.2·force - (30+40·hash)·force`；位移 `(vx·e, vy·e + 0.5·g·e²)`。
- 前 0.07 s 是“裂开闪白”：块向白染 0.5，只外移 8%。
- `tint_to`：块向某色染 `clamp(u·1.6)`（`'#3a3030'` 化灰、`'white'` 化光、`'#c89a50'` 化沙、`'#fff4c0'` 化金光）。透明度 `u<0.55` 时 1，之后线性到 0。
- 场景用法：灰塔被绿宝石打碎 `pieces=18, dur=0.7`（s06:396）；倒吊人像玻璃碎 `pieces=44, dur=0.9`（s09:904）；世界碎裂 `pieces=44, dur=1.0, force=1.5, gravity=90, tint_to='#fff4c0'`（s18:783）；DIO 化灰 `pieces=48, dur=1.3, force=0.8, gravity=-20（往上飘）, tint_to='#8a7a6a'`（s18:894）；愚者沙崩 `pieces=36, dur=0.55, force=0.8, gravity=260, tint_to='#c89a50'`（s13:718）。

### 3.2 拳击与冲击

#### `rush(fr, x, y, t, t0, t1, direction=1, fist='starplat.fist', spread=26, rate=30, seed=0, colour=None, reach=None, life=0.3, sparks=True)` — fx.py:584-647
- **ORA / MUDA 连打**。(x,y) = 替身胸口；`[t0,t1]` 内每秒生成 `rate` 个拳头，每个活 `life`（默认 0.3 s）。时长 `t1 + life`。先画替身的 rush 姿势再调它。
- 拳头 i：出生 `ts = t0 + (i + 0.6·hash01(seed,i,0))/rate`；`u = (t-ts)/life`；
  - 偏移：前后 `ox = spread·0.55·h1`；上下 `oy = spread·((h2+h3)/2 - 0.5)·1.3`（两个随机数平均 → 三角分布，集中在中间）；深度 `depth = h4`（按深度排序，远的先画，`depth<0.3` 的拳头压暗 30%）。
  - 出拳：`ext = ease_out(min(1, u/0.4))`；收拳 `back = max(0,(u-0.75)/0.25)`；`e = ext·(1-0.5·back)`；拳心 `fx = x + dir·(ox + e·reach)`，`reach` 默认 `spread·0.75`。
  - 速度线（u<0.7）：拳后两条（拳高的 −0.3 / +0.25 处）、长 `6 + 14(1-u) + 6·h5`，逐点抖动透明 `0.9·(1-s/L)`。
  - 残影（ext>0.25 且 u<0.75）：拳头剪影涂成 `scol`，两层（`gk=0.55, alpha 0.35`；`gk=0.3, alpha 0.6`），位置 `e-(1-gk)·0.5`。
  - 火花（0.38<u<0.62 且 h6<0.55）：拳前端 `_star_shape` 半径 `2+int(h7·2.5)` 白色 + 中心一点黄 `#ffd83c`。
- 拳头图：`starplat.fist` / `theworld.fist`（图集里各一帧 10×8，锚点在中心）；缺图时用 `_FIST_GRID`（紫色 / 金色程序拳）。残影色 `scol` 默认：含 `world` → `'#fff2a0'`，否则 `'#d8d0ff'`。
- 场景参数：s04:520 `spread=30, rate=34, reach=16`；s18:670 两边对打 `spread=26, rate=34, reach=30`；s18:789 压制 `spread=26, rate=40, reach=30+14·push`；s17:1009 压路机下 `spread=40, rate=30, reach=18`。**原片拳头只有 10×8，屏上是一小团**（联系表 fx_sheet_01 第一行），游戏里要放大，见 §8.4。

#### `hit_spark(fr, x, y, t, t0, size=12, colour='white', accent='#ffd83c', seed=0, dur=0.2)` — fx.py:465-518
- 打击点星爆，三段（`u = dt/dur`）：
  1. `u<0.22` 闪光帧：accent 圆盘 r=0.55S，colour 圆盘 r=0.42S；8 根菱形尖刺从 0.3S 到 `S·lens[i]`，宽 3/2 交替。
  2. `0.22≤u<0.5` 圆环 + 长刺：环半径 `S·(0.5 + 0.35·(u-0.22)/0.28)`，线宽 2（S≥10）否则 1；8 根 accent 刺 0.45S → `1.15·lens·S`（宽 2.2/1.4）+ 白色细线 0.5S→0.95·lens·S；中心小点 r=max(1, 0.14S)。
  3. `u≥0.5` 飞散碎线：`v=(u-0.5)/0.5`，每根 `r0 = S·(0.8+0.6v)·lens`，长 `0.35S·(1-v)`，accent/colour 交替；`v<0.5` 时外圈 16 个抖动点（半径 0.9S，alpha 0.7）。
- `lens[i] = (1.45 偶 / 0.9 奇)·(0.8+0.4·hash)`；整体旋转 `rot = hash01(sd,7)·2π`，每根角度抖 ±0.175 rad；`sd = seed·131 + int(t0·97) + int(x)·7 + int(y)`（同一位置同一时间形状固定）。
- 场景参数：普通拳 `size=10~14`；重拳 `18~22`；绿宝石命中 `size=5, dur=0.12`；必杀终结 `size=22, accent='#c080ff', dur=0.3`（s18:805）。

#### `shockwave(fr, x, y, t, t0, dur=0.4, r_max=60, colour='white', width=2, squash=1.0, echo=True)` — fx.py:521-546
- 扩散像素环：`r = r_max·ease_out3(u)`；线宽 `max(1, width·(1-0.6u))`；透明 `fade = 1 (u<0.55) → 线性到 0`（抖动）；环像素 `|dist - r| ≤ wd/2 + 0.3`。
- `echo`：r>6 时在 0.72r 处再画一道 0.6px 细环，透明度减半。
- `squash<1` 竖向压扁成地面环（0.25~0.3）。
- 场景参数：重拳 `r_max=50~90, width=2~3`；落地 / 登场 `r_max=170, squash=0.3, colour='#fff0c0'`（s00:597）；爆炸自带 `dur=0.38, r_max=1.4S, '#fff4b0', width=3`。

#### `impact_frame(fr, style='invert', threshold=None)` — fx.py:437-462
- **漫画冲击帧**，只画 1–3 帧（24 fps 下）。对已画好的整幅底层：
  - `'invert'`：RGB 取反。
  - 其它：按亮度阈值分成 2 或 3 级，换成 `IMPACT[style]` 的颜色。阈值自适应：2 色用**中位数**，3 色用 **38% / 72% 分位数**；也可传 `threshold`。
- 原片的固定组合：**先 invert 1 帧，再替身色 1 帧**（银色战车 invert→blue，s07:500-503；十字火焰 invert→red，s07:685-688；终结拳 invert 1 帧 → purple 定格 0.2 s+，s18:814-817）。白金之星的单发重拳：`purple` 1 帧（s00:445）。登场 / 大招落地：`purple` 1–2 帧（s00:600、s11:552）。爆炸压路机：`yellow` 1 帧（s18:447）。

#### `speedlines(fr, t, cx=160, cy=90, style='radial', n=48, colour='white', inner=40, seed=0, alpha=1.0, fps=12, width=(1,5), band=None)` — fx.py:369-423
- 漫画速度线，**每秒重随机 12 次**（`k = floor(t·fps)`）。
- `radial`：n 条三角楔，`hash01(seed,k,i,9)<0.12` 的跳过；角度 `2π·(i + 0.9·h1)/n`；尖端半径 `inner·(0.75+0.9·h2)`；底宽 `wd = w0 + (w1-w0)·h3²`，在半径 `R = _rmax+6` 处半宽 `wd/2·R/180`。
- `horizontal / vertical`：位置 `p = hrange(-2, span+2)`，跳过离中心 `inner/2` 以内的（`band=(a,b)` 时只在带内）；长 `L ∈ [0.12, 0.6]·along`；起点 `s ∈ [-L/2, along]`；粗 `th = w0+(w1-w0)·h4^1.6`；随机一端尖。
- `alpha<1`：先画在独立层再整层抖动合成。
- 场景参数：必杀背景 `radial, n=36~56, inner=24~62, alpha=0.4~0.55`；突进 `horizontal, n=18~30, inner=8~30, alpha=0.4~0.8`；蓄力 `horizontal, colour='#d8ccff', alpha=0.6`（s18:811）；召唤情绪 `colour='#8a50d0', inner=26, alpha=0.55`（s03:409）。

#### `crack(fr, x, y, t, t0, size=30, seed=0, dur=0.25, colour='#1a1020', hi=None)` — fx.py:2224-2230（`_crack_paths` 2156-2187、`_crack_draw` 2190-2221）
- 6 条锯齿主裂纹：每段 2.5–5.5 px，方向在主角度 ±0.55 rad 抖；长 `size·(0.55~1.0)`；每条有一根 ±0.7 rad 的分叉（2–3 段，从主裂纹中途长出）。
- `g = ease_out(prog(t, t0, t0+dur))` 控制长出比例；之后保持不消失。`hi` 给一条 (+1,+1) 偏移的亮边。
- 场景：世界身上裂开 `size=20, hi='#ffffff'`（s18:780）；DIO 化灰前 `hi='#fff4c8'` 再叠 `glow` 漏光（s18:860-866）。

### 3.3 火、烟、爆炸、粒子

#### `fire(fr, x, y, t, w=16, h=24, intensity=1.0, seed=0, palette='fire', embers=True, fps=12)` — fx.py:869-921
- 多个“泪滴舌头”的并集（`w<22` 时 3 条，否则 5 条），底部中心在 (x,y)，高约 1.35h 的区域。
- 第 j 条：`c ∈ [-1,1]`，`centre = 1-|c|`；`hj = h·(0.55+0.45·centre)·(0.82+0.3·hash(seed,j,k12))·intensity`；`rj = w/2·(0.52+0.36·centre)`；`cxj = x + c·w·0.27`；`v = (y-(yy+0.5))/hj`（0 底 → 1 尖）；摇摆 `sway = (sin(ts·6.1 + 1.7j + seed)·0.6 + (hash-0.5)·0.8)·rj·0.9`，中心 `cx_v = cxj + sway·v²`；半宽 `hw = rj·(1-v)^0.75·sqrt(clip(5v+0.35))`；`f = (1-|xx+0.5-cx_v|/hw)·(1-0.35v)`；`heat = max(f·(0.8+0.2·centre))`。
- 噪声 `heat += (tex[floor(yy·3 + ts·90 + 11seed) % 64, floor(xx·3 + 23seed) % 64] - 0.5)·0.35`；底部加热 `+clip(0.18 - vb)·1.2`。
- 上色：`lvl = floor(heat·(L+1) + (bayer-0.5)·0.9)`，`lvl≥1` → `pal[lvl-1]`。
- 余烬：`max(2, int(w/5·intensity))` 颗，周期 `0.8+0.5h`，`ey = y - h·(0.5+0.9·ph)`，透明度 `1-ph`。
- 调色板：`'fire' 'blue' 'green' 'purple' 'gold'` 或颜色列表。

#### `fire_ankh(fr, x, y, t, t0, size=40, seed=0, palette='fire', grow=0.25, t1=None)` — fx.py:960-1014（`_ankh_field` 924-957）
- **红色魔术师「十字火焰风暴」**：一个高 `size` 的燃烧安卡十字（☥），中心在 (x,y)，动画 x/y 就是投掷。
- 形状场（缓存）：`pad = max(6, 0.3S)`；上环椭圆 `lx=0.19S, ly=0.22S`，环带 `|dd-0.84|·min(lx,ly) < 0.062S`；横杆 y∈[0.44S, 0.56S]、半长 0.44S、两端外扩 `|dx|/armw·0.05S`；竖杆向下变宽 `半宽 = S·(0.075+0.07·sv)`；`core = gaussian_filter(mask, σ = 0.018S + 0.7)` 归一化（**用了 scipy**）；`up` = core 向上拖尾 K=max(3, 0.3S) 级，权重 `(1-k/(K+1))^0.8`。
- 每帧：`ts=floor(12t)/12`；两层噪声（快 `yy·2.2 + ts·110`，慢 `yy·1.1 + ts·40 + 13`）；`heat = max(core·(0.92+0.16(n2-0.5)), up·(0.3+1.3n)·0.9)`；`lvl = floor(heat·(L+0.5) + (bayer-0.5)·0.8)`。
- 出现：`s = ease_back(prog(dt,0,grow))` 最近邻缩放（会回弹）；背后 `glow('#ff7a20', 0.7·size·max(s,0.3), alpha 0.4)`；`t0` 处 24 颗火星 `burst(speed=2.2size, life 0.7, gravity=-30 往上, drag 2)`；6 颗余烬。
- 场景：s07:638 必杀切入里 `size = 34 + 4·sin(9t)` 呼吸；s07:677 飞行 `size=34, grow=0.05`，配 6 个火球拖尾（s07:671-676）。

#### `explosion(fr, x, y, t, t0, size=40, seed=0, smoke_colour='#5c5666', debris=True, ring=True)` — fx.py:760-820
- 总时长 2.2 s。层次（按画的顺序）：
  1. 烟（后）：12 团，`ts = 0.22+0.3h`，寿命 `1.3+0.6h`，上升 `S·(0.35+0.9h)·ease_out(u)`，半径 `S·(0.13+0.1h)·(0.7+0.9·ease_out(u))`，0.45 后淡出。
  2. 火球（dt<1）：13 团，环半径 `S·0.34·(0.25+0.75h)·(0.45+0.7·ease_out(min(1, dt/0.35)))`，上升 `S·0.3·ease_in(dt)`，半径 `S·(0.19+0.12h)·ease_out(dt/0.12)·(0.35+0.65·(1-(dt-0.5)/0.5))`；三层同心圆盘，颜色沿 `_FIREBALL` 按 `age = 6·dt + h` 冷却（白→黄→橙→红→烟）。
  3. 闪光（dt<0.09）：`#ffe050` r=S·(0.42+0.4k)，白 r=S·(0.34+0.34k)。
  4. 冲击环 `shockwave(dur=0.38, r_max=1.4S, '#fff4b0', width=3)`。
  5. 碎屑 `burst(t0+0.07, n=16, speed=3.2S, life=1.1, 暗色, gravity 240, size 2, spread 200)` + 火花 `burst(n=26, speed=4.2S, life=0.65, 黄/白/橙, gravity 90, drag 2.5)`。
- 场景配：`fr.shake(6→0, 0.35 s)`、`fr.flash('white', 0.7→0, 0.15 s)`、`hit_spark(size=20)`、冲击帧 invert→red（s07:681-690）。

#### `smoke(fr, x, y, t, t0, n=8, seed=0, colour='#8a8a98', life=1.6, rise=30, spread=10, size=5, loop=False, t1=None, wind=0.0)` — fx.py:823-857
- 一次性：n 团在 0.3 s 内放出；`loop=True`：每 `life/n` 秒一团直到 t1。
- 每团：`px = x + (h-0.5)·spread·(0.4+u) + wind·e + 1.5·sin(3e+j)`，`py = y - rise·ease_out(u)·(0.7+0.6h)`，`r = size·(0.35+0.9·ease_out(u))·(0.7+0.5h)`，0.35 后淡出，用 `_puff`。

#### `dust(fr, x, y, t, t0, n=10, seed=0, colour='#d8c8a8', life=0.75, speed=55, size=1.0)` — fx.py:729-753
- 落地 / 刹车 / 脚步的地面尘：左右交替；水平带阻尼 `s = (1-e^{-4.5dt})/4.5`；`py = y-1-(3+9h)·size·ease_out(u)`；`r = (1.5 + (2.5+3.5h)·ease_out(u))·size`；0.4 后淡出。再加 `n//2` 颗暗色石子 `burst(gravity 280, spread 130 向上)`。

#### `burst(fr, x, y, t, t0, n=20, speed=60, life=0.6, colours=('white',), gravity=120, size=1, seed=0, spread=360, angle=90, drag=0.0, fade=True)` — fx.py:678-712
- 通用解析粒子：寿命 `life·(0.55+0.45h)`；角度 `angle + (h-0.5)·spread`；速度 `speed·(0.35+0.65h)`；阻尼 `s = (1-e^{-drag·dt})/drag`；`px = x + cos(a)·v·s`，`py = y - sin(a)·v·s + 0.5·g·dt²`；size>1 时 u>0.6 缩 1；u>0.6 后抖动淡出。
- 场景：愚者沙柱 `n=90, speed=270, life=0.95, SAND, gravity=300, spread=38, size=3`（s11:538）；火星 `gravity=-30`（上飘）。

#### `bats(fr, t, t0, x, y, n=12, seed=0, speed=110, spread=150, angle=90, dur=2.2)` — fx.py:2528-2555
- DIO 化蝙蝠：每只延迟 `0.35h`，加速飞离 `dist = v·e + 40e²`，垂直方向扑翼摆动 `sin(9e+i)·5`，14 Hz 两帧扇翅；有 `prop.bat` 用图集，没有用 `_BAT_UP/_BAT_DN` 程序图（20% 放大 2 倍）。

### 3.4 替身能力

#### `emerald_splash(fr, x0, y0, x1, y1, t, t0, t1, n=24, seed=0, spread=20, speed=320, kind='emerald', arc=10)` — fx.py:1531-1578
- **绿宝石水花**：`[t0,t1]` 内从 (x0,y0) 依次射出 n 颗宝石，飞向 (x1,y1) 周围 ±spread 的随机点。
- 第 i 颗：`ts = t0 + (t1-t0)·(i + 0.8h)/n`；飞行时间 `T = max(0.12, L/speed)`；起点抖 ±3；轨迹是带弧度的直线：`bend = (h-0.5)·2·arc`，`pos(u) = 线性 + 法线·sin(πu)·bend`。
- 拖尾：往回取 12 个采样（`q = u - 0.015s`），颜色 `_light(main,0.5)`（s<3）→ main（s<7）→ dark，透明 `1-s/13`；s<7 时再沿法线偏 1px 画一条 dark（透明 `0.8-s/9`），形成 2px 粗的头部。
- 宝石图：`_GEM_BIG`（7×7）概率 45%，否则 `_GEM_MID`（5×5）；三套配色 `emerald / ice（佩特夏普冰锥）/ ruby`（fx.py:1495-1520）。
- 到达后 `hit_spark(size=5, accent=宝石主色, dur=0.12)`。时长 `t1 + T + 0.12`。
- 场景：开场 `n=34, spread=34, speed=380`（s00:478）；打灰塔 s06:393；半径 20 米：每个网节点各射 `n=5, spread=9, speed=L/1.0, arc=7` 汇向 HUB（s15:199-205）。

#### `tendrils(fr, pts, t, colour='emerald', glow=True, sag=None, wiggle=1.0, seed=0, grow=1.0, pulses=True)` — fx.py:1595-1631（`_sag_curve` 1581-1592）
- **法皇的发光丝线网**：`pts` 是一条折线或若干 `((x0,y0),(x1,y1))` 线段。
- 每段：下垂 `sag`（默认 `0.06L`）抛物线 `4s(1-s)`；扭动 `sin(3πs + 4t + seed)·wiggle·sin(πs)`（两端固定）；`grow` 只画前一部分（生长动画）。
- 绘制：4 邻域 dark（`_dark(c,0.45)`）抖动 0.6、距离 2 抖动 0.22 当光晕 → 实线 core → 光脉冲 `max(1, L/40)` 个沿线流动（`u = (1.2t + q/N + h) % 1`），5px 亮色 + 中心 1px 白。
- 场景：抓住白金之星 `colour='#50e890'`，`wiggle 2.0 → 0.6`（绷紧）（s04:486）；结界网 `WEB_COL='#40f0a0'`，被切断时分成两半回缩（s15:133-165）；肉芽触手 `'#e070b0', pulses=False`（s04:621-700）。

#### `vines(fr, x0, y0, x1, y1, t, t0, t1, colour='purple', thorns=True, seed=0, wiggle=2, strands=2, bend=None, sway=True)` — fx.py:1642-1698
- **隐者之紫 / 荷莉的荆棘藤**：两股绞在一起的藤沿弯曲路径在 `[t0,t1]` 内长出（`g = ease_out(prog)`），之后一直在并轻轻摆。
- 路径：采样 `n = 1.5L+2`，弯曲 `bd = (hash-0.5)·0.5L`（或传 `bend`）·`4s(1-s)`，长成后摆动 `sin(2.2t+seed)·1.2·s²`。
- 两股：`off_k = sin(s·2π·(L/14)/2 + kπ + seed)·wiggle`（双螺旋，大约每 14px 绞一圈）。
- 绘制：6 邻域（含对角）描边 → 刺（每 7 个采样一根，左右交替，2px 刺色 + 1px 描边色尖）→ 主色 → 高光（`idx%4<2`）→ 未长完时尖端 1.5px 亮色芽。
- 配色 `_VINE_COLS`（描边, 主, 亮, 刺）：`purple ('#2a0e44','#8a44d8','#d0a0ff','#5a2890')`、`green`、`holly ('#1a1030','#3aa860','#a8f090','#8a44d8')`、`dark`；或者直接传 4 元组（s00 的波纹充能色 `HAMON_VINE = ('#5a2a00','#ffb020','#fff6b0','#ffe060')`）。
- 收回：原工程没写，s03:381-399 用“缩短终点”：`r = 1 - 0.9·ease_in(retract)`，`end = start + (end-start)·r`，`r ≤ 0.12` 不画。
- 粗细技巧：s00 把藤画在 1/2 分辨率临时画布再 ×2 放大（`_Half`，s00:72-87），这样藤的像素和 ×2 的大角色同一网格。

#### `hamon(fr, x0, y0, x1, y1, t, seed=0, colour='#ffd83c', fps=16, ripples=True, strands=2)` — fx.py:1076-1116
- **波纹**：从 (x0,y0) 到 (x1,y1) 的金色电流 + 目标点的同心波纹。连续效果，16 fps 重随机。
- 电流：每股 `_bolt_points(depth=4, disp=0.14+0.06s)`；先在独立层画 3px 宽橙色 `#ff9a20` 光晕、按 0.5 抖动合成，再画 1px 芯（第一股 `_light(gold,0.7)`，其余金）；4 个之字形小火花（4px + 3px 两段）。
- 波纹：周期 0.45 s，3 圈错相，`r = 3 + 16·ph`，椭圆纵向 0.8；颜色 亮（ph<0.3）→ 金（<0.65）→ 橙；`ph>0.85` 时隔帧闪；再加 `sparkles(n=5, radius=12, period=0.35, size=2)` 和每 0.3 s 一次的 `glint(size=3)`。
- 场景：乔瑟夫指尖 `strands=2, ripples=False`（s00:457）；烤肉芽 `strands=3`（s04:764）。

#### `lightning(fr, x0, y0, x1, y1, t, seed=0, colour='white', glow_colour='#9cc8ff', fps=12, branches=3, width=1)` — fx.py:1138-1160
- 主干 `_bolt_points(depth=5, disp=0.28)` + `branches` 条分叉（从主干 20–80% 处、长 0.2–0.45L、偏 ±0.8 rad、depth 4）；光晕层 `width+2` 按 0.55 抖动合成；芯线白。
- s17:1012 压路机对拳时用作分屏中线 `glow_colour='#ffe8a0'`。

#### `void_sphere(fr, x, y, r, t, rim='#e8e0f0', rim2='#7a6a9a', dots=None)` — fx.py:1702-1733
- **奶油的虚空球**：`#2a1a3a` 圆 r+1 + 纯黑圆 r；边缘一圈爬动的点 `nd = max(8, 2πr/3.2)`，以 `ts·1.6` rad/s 旋转（12 fps），每 4 个一个 1px 半径的大点；0.8r 处反向转的暗点；6 个被吸进去的粒子。被抹掉的轨迹要场景自己画（s13 `_void` + 地毯沟）。

#### `knives(fr, items, t, frozen=False, streak=14, streak_colour='#e8ecff')` — fx.py:1770-1793
- **DIO 飞刀**：`items=[(x,y,角度)]`；角度量化到 5°，`prop.knife` 最近邻旋转（缓存 512 个）；飞行时刀尾 3 条速度线（中间全长、两侧 0.6 长、1.5px 间距，透明 `0.9·(1-…)`）；`frozen=True` 静止 + 偶尔一像素闪光。

### 3.5 时停

#### `timestop(fr, t, t0, cx, cy, dur=1.0, tint='yellow', t_end=None, resume_dur=0.6)` — fx.py:1846-1883（`_sphere_mix` 1819-1843）
- **「ZA WARUDO」**。必须在画完“被冻住的世界”之后调用，之后再画在停止时间里还能动的角色（保持全彩）。返回“已停止程度” 0..1。
- 阶段（`u = (t-t0)/dur`，`Rm = _rmax(cx,cy)+4`，`light = 调色板倒数第二色`）：
  1. `u<0.45`：反色球从 (cx,cy) 扩张 `R = Rm·ease_out(u/0.45)`；球内反色；白色实线边 2px；`R+4` 处一圈 light 色 0.6 抖动虚线。返回 0。
  2. `0.45≤u<0.55`：全屏反色。返回 0.2。
  3. `0.55≤u<1`：球收缩 `R = Rm·(1-ease_in((u-0.55)/0.45))`；**球外 = 停止色调，球内 = 停止色调再反色**；light 色边 2px。返回 `0.5 + 0.5·(u-0.55)/0.45`。
  4. `u≥1`：`timestop_world` 一直套着。返回 1。
- 传 `t_end` 时，到 `t_end` 自动转 `time_resume(…, dur=resume_dur)`。
- 场景时长：s15 `TS_DUR=0.9, RES_DUR=0.36`；s18 DIO `ZW_DUR=0.6`、承太郎 `SPW_DUR=0.7`；s17 `dur=0.8~0.9, resume_dur=0.35`。音效 `timestop` 要**提前 0.85 s** 播（反向镲片爬升，0.85 s 处才是锣响），`time_resume` 提前 1.02 s。

#### `timestop_world(fr, amount=1.0, tint='yellow')` — fx.py:1801-1816
- 停止时间的画面：整幅 `_lummap(pal, strength=0.5, gamma=0.9)` 映射到 6 色调色板（`'yellow'`=DIO、`'blue'`=承太郎、`'gray'`（s14 DIO 楼梯“回过神来在往下走”）、`'purple'`、`'green'`）。`amount<1` 时按 `BAY_SCREEN < amount` 逐像素选（抖动过渡）。

#### `time_resume(fr, t, t0, cx, cy, dur=0.6, tint='yellow')` — fx.py:1886-1899
- 颜色从 (cx,cy) 涟漪般恢复：`R = Rm·ease_in(u)`（`Rm = _rmax+10`）；球内原色、球外仍是停止色；1px 白边；边内侧 7px 一圈反色带。

#### `clock(fr, x, y, r, hour, minute, cracked=0.0, face, rim, seed, numerals)` — fx.py:1902-1934
- 钟面：描边 → 金边 → 高光 → 暗边 → 盘面；12 刻度（3 的倍数是黑色双像素）；时针 0.45r（r≥10 时 2px）、分针 0.72r、红色轴心；`cracked` 0..1 长裂纹（裁在盘面内）。s15/s16 钟楼。

### 3.6 天气、氛围、发光

| 函数 | 行 | 样子 / 关键公式 |
|---|---|---|
| `sparkles(fr, x, y, t, n=6, radius=12, colour='yellow', seed, period=0.8, size=3)` | 1018-1046 | 一群闪烁四角星：每颗周期 `period·(0.7+0.6h)`，每个周期换位置（半径 `radius·sqrt(h)`），大小 `round(sin(πf)·size)`，`s<0.12` 不画，中心白 |
| `glint(fr, x, y, t, t0, size=6, colour='white', dur=0.45, accent='#ffd83c')` | 1049-1073 | 一次性星光：`s = sin(π·min(1, 1.25u))`（u<0.8）否则 `(1-u)/0.2·0.35`；accent 长十字 r+1、白十字 r、斜叉 `max(1,r//3)`、r≥3 时中心 3×3。眼睛闪光、剑尖、星形胎记 |
| `glow(fr, x, y, r, colour, alpha=0.6, add=False, levels=3, power=1.3)` | 1937-1952 | 抖动径向光：`A = clip(1-d/r)^power·alpha` → `_qblend(levels)`；`add=True` 加法提亮（暗场景） |
| `light_beam(fr, x0, x1, top, bottom, t, colour, slant=0.45, alpha=0.5, motes=18, seed, spread=0.25)` | 1955-1990 | 斜光柱 + 浮尘；`A = edge·(1-0.75dy/H)·(0.8+0.2sin(…+1.5t))·alpha` |
| `rain(fr, t, n=120, angle=12, speed=260, seed, colour='#a8b8e8', length=7, ground=None, layers=True)` | 1164-1190 | 斜雨：每 3 根 1 根是远层（0.6 速度/长度、暗色）；`ground` 加 12 fps 溅点 |
| `sand_wind(fr, t, n=80, seed, colours=('#f0c878','#d8a050','#fbe0a0'), speed=180, direction=1, sheets=True, region=(0,H))` | 1193-1227 | 风沙：3 条抖动沙幕（`_qblend levels 3`，正弦波纹横向滚动）+ n 根 2–8px 的沙粒横线 |
| `petals` | 1238-1254 | 樱花瓣（4 种 3–4px 形状，7 fps 翻转） |
| `bubbles(fr, t, x0, y0, x1, y1, n=20, …)` | 1257-1275 | 盒内上升的气泡（暗蓝之月水下） |
| `fog(fr, t, density=0.6, colour='#c8c8d8', seed, speed=8, region, levels=3, max_alpha=0.85)` | 1307-1329 | **正义的雾**：两层 180×512 可平铺雾纹理以不同速度滚动 `0.6·tex1 + 0.4·tex2`，`A = clip((f-(1-density))·2.2)·edge·max_alpha` → `_qblend` |
| `stars` / `shooting_star` | 1333-1392 | 星空 / 流星（开场） |
| `water_splash(fr, x, y, t, t0, size=1.0, seed)` | 1396-1423 | 落水：两道压扁冲击环 + 0.7 s 水柱 + 两组水花 burst，约 1.1 s |
| `water_gush(fr, x, y, t, t0, direction=1, strength=1.0, ground=None, seed, t1=None)` | 1426-1491 | 水塔破洞喷水：抛物线水流（`v0 = 70·strength·ramp+10`，g=240）+ 40/s 水滴 + 落地溅点。**盖布神 / 水系敌人可复用** |
| `caustic_light` / `underwater_wobble` | 2034-2064 | 水下焦散网 + 整屏行扭动 |

### 3.7 滤镜、背景、转场

| 函数 | 行 | 样子 / 公式 |
|---|---|---|
| `vignette(fr, amount=0.6, colour='black', inner=0.65)` | 2001-2011 | `dist = sqrt(0.85dx² + dy²)`（归一化）；`A = clip((dist-inner)/(1.35-inner))^1.2·amount` → `_qblend(levels=3)` |
| `heat_haze(fr, t, y0, y1, amp=1, fps=12)` | 2026-2031 | 行平移 `round(amp·sin(0.45y + 9ts)·(0.6+0.4sin(0.13y-3ts)))`（沙漠热浪 / 威压） |
| `sepia(fr, amount=1.0, strength=0.5)` | 2295-2306 | 褐色 6 级 `_lummap(gamma 0.95)`；章节结尾 To Be Continued 定格 |
| **`menace_bg(fr, t, colours=('#402060','#200830'), cx, cy, arms=3, twist=0.09, speed=1.6, fps=12)`** | 2351-2366 | **JoJo 威压旋涡背景**（铺满画布）：`v = sin(arms·ang + twist·dist - speed·ts)·0.5+0.5`；`v = 0.75v + 0.25(sin(0.05dist - 1.1ts)·0.5+0.5)`；`q = floor(v·n + (bayer-0.5)·0.35)` → 第 q 色。2–4 色。12 fps |
| **`radial_burst_bg(fr, t, cx, cy, colours=('#f0c040','#e07020'), n=16, spin=0.2)`** | 2369-2379 | 旋转放射条纹（点名卡、VS 卡）：`idx = floor((ang/2π + spin·t)·n) % k`；连续时间、无抖动 |
| `iris(fr, amount, cx, cy, colour)` | 2234-2245 | 圆形转场（0 开 1 关），`R = _rmax·(1-amount)` |
| `diamond_wipe(fr, amount, cell=20, colour, reverse)` | 2258-2271 | 复古菱形扫屏：格内曼哈顿距离 `< clip(1.7·amount - 0.7·diag)` |
| `slash_wipe(fr, amount, angle=20, colour='black', edge='white', reverse)` | 2274-2292 | 斜切转场 + 2px 亮边；s00 点名卡之间 `angle=22`，并同步清掉 UI 层（`ui_slash`，s00:90-113） |
| `tbc_arrow(fr, t, t0, slide=0.4, x=None, y=None)` | 2337-2347（徽章 `_tbc_img` 2309-2334） | **UI 层**：「To Be Continued ⟵」金色箭头徽章（底层尺寸 118×22，×2 = 236×44 UI px，箭头宽 16，填 `#d8bc5c`、亮 `#f6e6a0`、暗 `#a0822e`、描边 `#24160a`；字 bold 17 `#2a1a08`），从右侧 `ease_back` 滑入到右下角 (UW-w-18, UH-h-18)。配 `sepia` + `tbc` 音效（终音在 +1.61 s） |

---

## 4. text.py：屏上文字（全部在 UI 层 640×360）

### 4.1 字体与字形渲染

```
FONT_FILES (text.py:21-26)
 'pixel' C:/Windows/Fonts/simsun.ttc   宋体，12 / 16 px 用（点阵感）——对白、旁白、地点副标题、名牌副标题
 'bold'  C:/Windows/Fonts/msyhbd.ttc   微软雅黑粗体——标题、拟声字、ゴゴゴ、替身卡、名牌大字、地点大字
 'hei'   C:/Windows/Fonts/simhei.ttf   黑体（定义了，几乎没用）
 'jp'    C:/Windows/Fonts/msgothic.ttc MS Gothic（定义了，默认不用；ゴ、ド、ズガッ 都是雅黑粗体画的）
```
- `_text_img(s, kind, size, colour, outline, owidth, shadow)`（57-80）：`d.fontmode='1'` **关闭抗锯齿**（实测输出 alpha 只有 0 / 255）；描边 = 把字在 `[-ow, ow]²` 的方形偏移上逐个盖一遍（切比雪夫方形描边）；阴影 = 同样的方形盖一遍再整体偏 (+2,+2)；`pad = ow + (2 if shadow) + 1`。有 512 项缓存。
- `text(fr, x, y, s, size, colour, kind, outline, owidth, shadow, anchor='la', alpha, scale, rot, layer)`（88-101）：`anchor` 两个字母 `[l|m|r][t|m|b|a]`；`scale`、`rot` 都是**最近邻**缩放 / 旋转（大字放大就是粗像素，这是故意的）；alpha 平滑。
- `wrap(s, width, kind, size)`（41-54）：逐字折行（中文可用），认 `\n`。

### 4.2 各组件

| 组件 | 行 | 版式（UI px） |
|---|---|---|
| **对白框 `dialogue(fr, speaker, s, t0, t1, cps=18, portrait, pframe, pos='bottom', name, colour, sound, pop=0.12)`** | 134-210 | 框 x 20→620，高 80，底部 y0=272（顶部 12）；出入场竖向压扁 `ease_out(prog(…, pop))`。`box()`（119-131）：投影 (+4,+4) `(0,0,0,160)`、底 `(16,14,40,225)`、2px 黑边、内缩 2 的 2px 白框、内缩 4 的 1px `(0,0,0,120)`。头像框在 (28, y0+8)，填 `(40,36,70)` 白边，32×32 头像 ×2；打字时 8 fps 切头像 0/1 帧。名牌：`text_img(名字,'pixel',16,'white')`，底色 = 说话人颜色，2px 白边，在 (tx-4, y0-14) 宽 = 字宽+14、高 20。正文：宋体 16，黑描边 1，最多 3 行、行距 22，从 y0+16 开始，打字机 `cps=18`（从 t0+pop 开始）；打完后右下角 (x1-18, y1-16) 白色小三角以 3 Hz 闪。音效 `blip_train`（时长 = 字数/cps）。说话人表 `SPEAKERS`（105-116）：承太郎 `#3a4a9a`、乔瑟夫 `#6a8a3a`、阿布德尔 `#c0402a`、花京院 `#2a9a5a`、波鲁纳雷夫 `#6a7ab0`、伊奇 `#707070`、荷莉 `#d0608a`、DIO `#c89a20`、旁白 `#444455` |
| **旁白 `narration(fr, s, t0, t1, pos='top', size=16, colour)`** | 213-229 | 全宽黑带 alpha 170，高 = 行数×22+16，顶部 y0=10；文字宋体 16 居中、黑描边；0.25 s 淡入淡出 |
| **地点字幕 `location(fr, place, sub, t0, t1, x=24, y=24)`** | 232-249 | 大字雅黑粗 28 白字黑描边 2；下方 6px 金条 `#f0c040`（宽 = 字宽+44）；副标题宋体 12 `#f0e0a0` 黑描边；从左 −300 px `ease_out3` 0.35 s 滑入，0.3 s 淡出 |
| **大标题 `title(fr, s, t0, t1, x=320, y=180, size=48, colour='#ffe040', outline='#2a0a3a', owidth=3, shadow='#000000', pop=0.25)`** | 252-265 | 雅黑粗；`ease_back` 弹出缩放；0.2 s 淡出 |
| **拟声字 `sfx_text(fr, s, x, y, t0, t1, size=32, colour='#ffffff', outline='#000000', owidth=2, rot=0, jitter=1.5, pop=0.12, kind='bold', drift=(0,0))`** | 268-284 | 缩放 `1.6 - 0.6·ease_out(prog(t,t0,t0+pop))`（从 1.6 倍砸到 1 倍）；每秒 24 次随机抖 ±jitter（`hash01(int(24t), x, 1/2)`）；`drift` UI px/s 漂移；最后 0.12 s 淡出；anchor 居中；最近邻放大旋转。全工程用了 146 次 |
| **ゴゴゴ `menacing(fr, t0, t1, x=520, y=180, n=4, char='ゴ', size=36, colour=None(=C['menace'] #aa3cdc), spread=90, seed=0)`** | 287-308 | 第 i 个字在 `t0+0.12i` 出现；`ph = hash01(seed,i)`；循环上升 `u = ((t-appear)·0.35 + ph) % 1`（约 2.86 s 一轮）；`xx = x + (i-(n-1)/2)·spread/(n-1)·1.6 + 3sin(5(t+ph))`，`yy = y + (0.5-u)·60 + (i%2)·18`；透明 = 0.15 s 淡入 × 顶部 20% 淡出 × 结束 0.2 s 淡出；缩放呼吸 `1 + 0.08sin(11(t+ph))`；倾斜 `-8+16ph` 度；雅黑粗、描边 `#1a0022` 2px。`char='ド'` 就是ドドド |
| **替身卡 `stand_card(fr, cn, en, t0, t1, colour='#ffe040', x, y=40, side='right')`** | 311-335 | 大字 `『cn』` 雅黑粗 26（颜色 = 替身色）黑描边 2；小字英文名 雅黑粗 14 白字黑描边 1；底板平行四边形 `[(10,0),(w,0),(w-10,h),(0,h)]`，填 `(20,10,40,220)`，1px 替身色描边；`w = max(字宽)+28`、`h = 两行高+12`；默认贴右（x = UW-w-16）；从侧面 `ease_out3` 0.3 s 滑入（偏移 w+40），0.25 s 淡出。大字在 (x+14, y+4)，小字在 (x+18, y+大字高+6) |
| **名牌 `name_card(fr, cn, sub, t0, t1, x=24, y=264, colour='#ffffff', accent='#f0c040')`** | 338-357 | 人名雅黑粗 24 白字黑描边 2；下方 4px accent 条（宽 = 字宽+30）；副标题宋体 12 accent 色；从左 −200 滑入 0.3 s |
| 点名卡名牌 `plate()` | s00:190-208 | 开场用：雅黑粗 26 人名 + 雅黑粗 12 罗马音（accent 色）+ 4px accent 条，0.13 s 从文字侧弹入 |
| VS 卡 | s10:336-359 | `radial_burst_bg` + 斜黑带 + 双方 ×3 大立绘白描边 + `VS` 雅黑粗 40 `#ff3048` 白描边 3 + 敌名 48 `#ffe040`，`ease_back` 弹 |

**拟声字的常用调色（直接照抄）**：ORA `#d8ccff` 描边 `#1a0a3a` owidth 3（s18:653）；MUDA `#ffe040` 描边 `#1a2a0a` owidth 3（s18:657）；单发 ORA! `#ffe040` 描边 `#2a0a4a` size 34 rot 8（s00:500）；终结 ORA!!! `#ffffff` 描边 `#3a0a5a` owidth 4 size 72 jitter 2.5（s18:828）；咋瓦鲁多！ `#ffe040` 描边 `#3a1a00` size 46（s18:472）；ドドド `#fff2c8` 描边 `#3a1a08`（s11:563）；ズガッ！ `#ffe070` 描边 `#3a1a08`；ガオン `#e8e0f0` 描边 `#2a1a3a`（s13:740-745）；ドゴォォン！！ `#ffb040` 描边 `#2a0a0a` size 40（s18:452）；パキッ `#fff0c0`（s18:830）；ギロッ `#5cf0d0`（s18:543）；ゴオオッ `#ffb040` 描边 `#3a0a00`（s02:548）。

---

## 5. 每个替身的招牌特效（从场景里抠出的实际参数）

### 5.1 主角团 6 + 世界

| 替身 | 光环色 / 卡片色 | 招牌特效（原片做法） | 出处 |
|---|---|---|---|
| **白金之星** | 光环 `#b090ff`（s00 `#b8a0ff`）；卡片 `#c8a8ff` 或 `#ffe040`；残影 `#d8d0ff`；冲击帧 purple | **单发重拳**：`starplat.punch` 帧 0(0.06 s)→1(0.1 s)→2；击中点 `hit_spark(size=22)` + `shockwave(r_max=50, '#e8e0ff')` + `shake(3)` 0.25 s + `impact_frame('purple')` 1 帧 + `punch_heavy` + 拟声 ORA!。**连打**：先画 `starplat.rush`（16 fps 两帧）→ `rush(spread 26~40, rate 34~40, reach 16~30)` + 背后 `speedlines(radial, alpha 0.45)` + `shake(1)` + `clash_sparks`（每秒 11 个 `hit_spark size 7~12` 散在接触点 ±10/±14）+ ORA 字左右轮流（每 0.2 s 一个，6 个固定槽位）。**终结拳**：蓄力 `aura_flame(intensity 1.3)` + 横向 `speedlines('#d8ccff')` → 出拳 2 帧残影 → `hit_spark(22, accent '#c080ff', dur 0.3)` + `shockwave(r_max 90, width 3)` + invert 1 帧 → **紫色定格**（虚拟时钟冻结）→ 世界 `crack` → `shatter(tint_to '#fff4c0')`；镜头 zoom 2.0→2.15→2.3→2.1。**时停（白金之星·世界）**：`timestop(tint='blue', dur 0.7)`，卡片「白金之星·世界」`#9cc8ff` | s00:340-347, 439-447; s18:628-658, 661-677, 742-831, 547-569 |
| **绿色法皇** | 光环 `#70ffb0` / `#60ff90`；卡片 `#70ffb0`；丝线 `#50e890`、网 `#40f0a0`；冲击帧 green 可用 | **绿宝石水花**：`hiero.cast` 帧 0→1，`emerald_splash(n 26~34, spread 24~34, speed 320~380)` + `emerald` 音效。**丝线**：`tendrils` 伸出 → 抓住后 `wiggle 2.0→0.6` 绷紧。**半径 20 米绿宝石水花**：丝线网按顺序点亮（`_seg_grow`，扇形先、外圈后，0.35 s）→ 网节点依次 `glow('#9cffc8')` + `glint` → 每个节点 `emerald_splash(n=5, spread 9, arc 7)` 汇向中心 | s00:352-357, 477-480; s04:425-486; s15:123-205 |
| **银色战车** | 光环 `#c8d8ff`（s00 `#e8f0ff`）；卡片 `#d8e4ff`；冲击帧 invert→blue | **一刺**：`chariot.thrust` 帧 0（后拉 5px）→ 2（1 帧）→ 1；2 帧残影 `afterimage(colour '#c8d8ff')`；剑尖 `hit_spark(14, accent '#9cc8ff')`；水平 `speedlines(n 30, inner 8, alpha .8)` 0.12 s；invert 1 帧 → blue 1 帧；`shake(3→0, 0.25 s)`；`slash` 音效提前 0.07 s。**剑雨乱刺**：thrust 帧 2/1 以 16 Hz 交替 + `glint(size 8)` + 4 个 `hit_spark(size 8, accent '#c8d8ff')` 每 0.06 s 一个、上下错开 10px。**斩火**：`slash_arc`（9 点弧线、0.1 s、白→`#9cc8ff`、宽 2→1）+ `fire_chunks`（切碎的火团飞散）+ `hit_spark(10, accent '#ffd040')`，三刀间隔半拍。**刺穿倒吊人**：`shatter(pieces 44, dur 0.9)` 玻璃碎 | s07:259-271, 447-513, 595-621; s00:358-365, 481-488; s09:872-920 |
| **红色魔术师** | 光环 `#ff9040`（s00 `#ffa040`）；卡片 `#ff7040`；冲击帧 invert→red | **火焰洪流**：`fire_jet`（一串 `fireball` 分层椭圆，每 3.5px 一个，半径 `(4.5+2h)·(0.75+0.45u)`，14 fps 抖动）+ 背景 `glow('#ff8a30', add)`。**十字火焰风暴**：必杀切入（`menace_bg('#5a1010','#2a0608','#a0301a', speed 2.4)` + `speedlines('#ffb070', alpha .45)` + 替身浮在后面 + 呼吸的 `fire_ankh(size 34±4)` + 对白喊招式名）→ 远景安卡飞行（`ease_in`、6 个火球拖尾、水平速度线）→ `explosion(size 64)` + `hit_spark(20)` + invert→red + `flash(white .7→0, .15 s)` + `shake(6→0, .35 s)` + 对手 `stand_out` | s07:203-256, 595-695; s00:471-476 |
| **隐者之紫** | 光环 `#c080ff` / `#a860f0`；卡片 `#c890ff`；召唤时整屏染紫 `filt_tint((38,12,60), 0.55~0.8)` + `speedlines('#8a50d0')` | **藤蔓迸出**：5–6 根 `vines(colour 'purple', 0.22 s 长出, wiggle 1.5~2, bend ±8~12)`，前后两层（身后的先画、身前的后画）。**波纹贯藤**：藤的配色切成 `HAMON_VINE` 金色 0.14 s，再以 24 Hz 金紫闪 0.2 s（`_hp_colour`，s00:321-330）；指尖 `hamon(strands 2)` + `sparkles('#ffd83c')`；每根藤尖 `hit_spark(9, '#fff8c0', accent '#ffb020')` 依次 0.03 s 炸开；`flash('#fff0a0', 0.4→0, 0.1 s)` + `shake(2)` + 身后 `glow('#ffc040', add)` 膨胀。**烤肉芽**：`hamon(strands 3)` 打到目标 + `shatter` | s00:412-470; s03:381-429; s04:732-764 |
| **愚者** | 光环 `#ffe8a8` / `#fff0b0` / `#e8c070`；卡片 `#ffe08a` / `#f0c878`；沙色 `SAND = ('#f0c878','#d8a050','#fbe0a0')`（s13 版 `('#e6c07a','#b88a4a','#f4dca0')`）；崩散 `tint_to '#c89a50'` | **沙中现身**：琥珀色 `radial_burst_bg('#9a5420','#6e3614')` + `glow('#ffc070')` → 沙柱 `smoke('#ecc880', rise 90, size 9)` + 两次 `burst(SAND, n 90/50, speed 270/200, gravity 300/260, size 3/2)` + `dust(size 1.8)` → `stand_summon(scale 3, rise 46)` → 之后每 0.8 s 从身上流沙 `burst(n 6, gravity -30, angle 150)` → 定格 `impact_frame('purple')` 2 帧 + `shake(3)` + ドドド。**滑翔 / 托人**：`fool.glide` + `afterimage('#e8c070')`；从伊奇到滑翔翼的流沙点（14 点沿路径流动）。**崩散**：`shatter(fool.glide, tint_to '#c89a50')` 或 `tint` 渐变 + `burst(SAND, n 46, gravity 260)` | s11:518-563; s13:613-745; s00:489-494 |
| **世界（DIO）** | 光环 `#ffd040` / `#ffe070`；卡片 `#ffd83c` / `#ffe070`；残影 `#fff2a0`；冲击帧 yellow | **ZA WARUDO**：`stand_summon('theworld.pose', dur .3)` + DIO 换 `dio.laugh` → `timestop(tint 'yellow', dur 0.6)` + 「咋瓦鲁多！」46 号 + 小字 ZA WARUDO + `shake(3)`。**停止时间中**：被冻住的人用 `outline='#f0e8c0'` 保持可读（s18:482）；チク…タク… 每 0.4 s 一个；飞刀 `knives(frozen=True)`。**MUDA 连打**：`rush(fist='theworld.fist')`。**压路机**：`prop.roadroller` 帧 0/1/2（干净/破损/裂纹发光） | s18:456-497; s17 全场 |

### 5.2 敌方替身 → 能复用的 fx 积木（打全部替身使者要用）

原片 21 场里出现过的敌人见 `scenes\s06~s18`；原片没打的（黄色节制、恋人本体战、女帝、黑檀恶魔、阿努比斯、巴斯泰托、塞特、次中音萨克斯等）要新做。下面是“已有积木能凑到什么程度”：

| 敌人 | 原片怎么画 | 游戏里的特效积木 |
|---|---|---|
| 灰塔 | 小甲虫高速乱飞、被绿宝石 `shatter(pieces 18)`；卡片 `#c8d8f0` | 高速残影 `afterimage`；舌针攻击用 `knives` 改色或细 `lightning(fps 0)` |
| 暗蓝之月 | 水下 + 白金之星 rush；卡片 `#58b0ff` | `bubbles`、`underwater_wobble(caustics)`、`water_splash`；藤壶 = `burst` 小方块 |
| 力量 | 船管道活过来抓人（s08 `pipe` 贝塞尔管）；卡片 `#ff9a40` | `vines(colour=(管道描边,管道色,高光,铆钉))` 当管道触手 |
| 皇帝 | 弯曲弹道（s09 `_bez` + `_draw_bullet`）；卡片 `#ffd040` | 子弹 = `prop.bullet` + 2px 拖尾（照 emerald_splash 拖尾公式）+ `gunshot` |
| 倒吊人 | 镜中 / 硬币间跳跃，被刺后玻璃碎；卡片 `#ff6a6a` | `shatter`；镜面闪光 `glint` |
| 命运之轮 | `wheel.car` 白描边；汽油线点火 | `fire` 沿地面一串、`explosion` |
| 正义 | `justice.skull` alpha 0.9 + `fog`；雾僵尸 `zombie.walk` | `fog(density 0.65)` 全程 + 骷髅半透明 |
| 恋人 | 微型替身（迷你战） | 放大镜头 `fr.zoom` + `sparkles` |
| 太阳 | `fake_sun`（s10:301-318：加法 `glow('#fff0b0', 3.6r)` + 12 根旋转光芒 + 三层圆盘） | 热浪 `heat_haze` + `light_beam`；火球 = `fire(palette 'gold')` |
| 死神13 | `death13.float`；梦境；被法皇丝线缠住后 `shatter(pieces 36)` | `menace_bg` 当梦境背景、`tendrils` |
| 审判 | 泥人 `_clay_fist`；被安卡炸 `shatter(pieces 30)` | `fire_ankh` + `explosion`；土块 `burst` |
| 女教皇 | 矿物拟态、牙齿 | `shatter` + `crack` |
| 盖布神 | `geb.claw` 水爪（可竖向压扁收回，s12:510-519） | `water_gush`、`water_splash`、`WATER = ('#ffffff','#b8f4ff','#48d8e8')` |
| 克努姆 / 托特 | 变脸、漫画预言 | 漫画格转场 `slash_wipe`；炸弹 `explosion(size 22)` |
| 奥西里斯（达比） | 扑克 | `glint`、汗滴、`menacing` |
| 荷鲁斯（佩特夏普） | `ice_spear`（s12:328-340，三角冰锥 `#a8e8ff` 描边 `#2a6a9a` + 白芯）+ `emerald_splash(kind='ice')` | 冰锥连射 = `emerald_splash(kind='ice')`；`ice` 音效 |
| 阿图姆（泰伦斯） | 游戏机对决 | 屏中屏 + `impact_frame('bw')` |
| 奶油 | `void_sphere` + 地面被抹掉的沟；卡片 `#c890ff`，光环 `#8a4ad8` | `void_sphere` 扫过 + ガオン |
| 世界 | 见 5.1 | |

### 5.3 场景里自写的招牌辅助函数（不在 fx.py，但移植时要一起写）

| 函数 | 出处 | 做什么 / 公式 |
|---|---|---|
| `fireball(d, x, y, r, heat, lift)` | s07:206-217 | 4 层同心椭圆（纵向 ×0.85），比例 1 / 0.72 / 0.45 / 0.22，颜色下标 `clamp(层号 + lift - (1-heat)·2.5, 0, 4)`，取自 `FIRE_COLS = (150,24,24) (230,80,20) (255,170,40) (255,240,150) (255,255,235)`。魔术师火焰、安卡拖尾的基本单元 |
| `fire_jet(fr, x0, x1, y, t, seed, thick)` | s07:220-239 | 每 3.5 px 一个 fireball，`wob = 2·sin(9u + 22t + seed)`，`r = (4.5+2·hash(i,int(14t),seed))·thick·(0.75+0.45u)`；6 颗火星沿火流飘 |
| `fire_chunks(fr, x, y, t, t0, seed, n=6, speed=90)` | s07:242-256 | 被剑切碎的火团：上下交替飞出（角度 25–65°），`px = x + cos(a)·v·dt·0.8 + 6dt`，`py = y - sin(a)·v·dt + 60dt²`，`r = (3.5+2h)·(1-dt/0.55)`，用 `lift=1` 保持橙黄；0.55 s |
| `slash_arc(fr, x, y, t, t0, dur=0.1, size=12, seed, flip)` | s07:259-271 | 银色战车剑光：起始角 `-60 + 40·hash01(seed,1)`，9 点覆盖 120°，`px = x + cos(a)·0.45·size·(flip?-1:1)`，`py = y - sin(a)·size`，颜色白 → `#9cc8ff`，线宽 2（前半）→ 1 |
| `stand_out` / `dim_bg` | s07:152-177 | 替身白化溶解；召唤时背景压暗到 `#140c30`（`Image.blend`，最多 0.9） |
| `clash_sparks(fr, t, t0, t1, cx, cy, seed, rate=11)` | s18:628-635 | 对拳接触点每秒 11 个 hit_spark（位置 ±10/±14，size 7–12） |
| `rush_texts(fr, t, t0, t1, ora_only_after)` | s18:638-658 | ORA / MUDA 每 0.2 s 交替一个，左右各 6 个固定槽位，字号 `38+4·(k%3)` |
| `portrait_cut(fr, t, name, x, flip, colours, …)` | s18:680-689 | 必杀特写：`radial_burst_bg(spin 0.9)` + `speedlines(inner 62, alpha .55)` + 头像 ×4 + 光环 grow 2 + `wobble` 抖 |
| `_split_mask` + `shot_K` | s18:710-739 | 双人分屏，锯齿分界线（8 段 ±7 px）+ 3px 白 / 1px 黑描线 |
| `ash(fr, t, t0, cx, cy, n, w, h, wind, life, seed, rise, spawn)` | s18:295-311 | 化灰飘散的灰点（风向漂 + 正弦摆） |
| `fake_sun(fr, x, y, t, r, glow)` | s10:301-318 | 太阳替身：加法光晕 3.6r + 12 根旋转光芒（长度 9 Hz 呼吸）+ 三层圆盘 |
| `ice_spear(fr, x, y, ang, L=18, w=2)` | s12:328-340 | 佩特夏普冰锥 |
| `claw(fr, x, y, f, flip, sy)` | s12:510-519 | 盖布水爪（`sy<1` 竖向压扁表示缩回水里） |
| `_hp_colour(u, k)` | s00:321-330 | 波纹贯藤时藤的配色时序 |
| `_Half` | s00:72-87 | 半分辨率画特效再 ×2（品红色键抠底） |
| `slam(fr, k, u)` | s10:336-359 | VS 卡：放射背景 + 斜带 + 双方大立绘 + VS + 敌名 |
| `_impact(fr, t, t0, styles)` | s13:426-429 | 按 1/24 s 一格轮播冲击帧样式 |

---

## 6. 原片的“演出语法”（游戏里直接沿用）

1. **打击四件套**（FX.md:153-154）：`hit_spark` + `shockwave` + `fr.shake(3)` ~0.2 s + 可选 1 帧 `impact_frame` + 音效 `punch_heavy`。连打：`rush` + 背后 `speedlines(alpha=0.5)` + `fr.shake(1)`。
2. **冲击帧序列**：invert 1 帧 → 替身色调 1 帧（银色战车 blue、魔术师 red、白金之星 purple、世界 yellow）；最重的一击再接一段**紫色定格**（s18 `T_FRZ = T_PUNCH + FT` 到 `T_FRZ_END`，期间特效时钟冻结）。s13 有个小工具 `_impact(fr, t, t0, styles)`（s13:426-429）按帧轮播一串样式。
3. **虚拟时钟**：s18:744-750 定格时 `vt` 停住，特效、替身姿势都用 `vt`；s15:183-195 `gem_t` 把宝石的时钟做成“正常 → 子弹时间 ×0.2 → 冻结 → 恢复”。**游戏里的命中停顿和时停就照这个做**：每个特效实例绑定一个时钟（世界时钟 / 真实时钟）。
4. **替身情绪**：召唤瞬间把背景压暗 / 染色（s07 `dim_bg('#140c30', 0.45)`；s03 染紫），然后 `menacing` + `stand_card`。
5. **必杀切入**：`menace_bg` 或 `radial_burst_bg` 满屏 + 径向 `speedlines` + 角色 / 替身放大（s18 `portrait_cut` 用 32×32 头像 ×4 + `sp.aura(grow=2)` + `wobble` 抖动）+ 招式名；s18 `shot_K` 还有双人分屏（锯齿闪电分界 + 3px 白线 + 1px 黑线，s18:710-739）。
6. **半分辨率特效**：给 ×2 大角色配特效时，先在 1/2 画布上画再 ×2 放大（s00 `_Half`），保证像素网格一致。游戏里如果镜头 zoom 2 拍特写，也要这么处理。
7. **12 fps 抽帧**：火焰、光环、旋涡、速度线都是 `floor(t·12)/12` 或 `floor(t·fps)`——手绘动画的“一拍二”味道。移植到 60 Hz 时**保留这个量化**，运动（位置）用连续时间。

---

## 7. 移植到 JS Canvas 的方案

### 7.1 画布与合成

- 建议游戏**沿用原片的 320×180 底层 + 640×360 UI 层**（所有特效参数、精灵尺寸、文字版式都是按这个定的；替身约 60 px 高 = 屏高 1/3，正适合打斗）。银魂用 384×216 是银魂原片的尺寸，JoJo 不必跟。这一条需要总负责人拍板。
- 每帧：
  1. 底层：一块 `Uint32Array(320*180)` 帧缓冲（`ImageData.data.buffer` 视图，像素 `0xAABBGGRR`）。背景、阴影、角色、特效、全屏滤镜**都用软件写进这个数组**，按调用顺序。
  2. `putImageData` 到 320×180 的离屏 canvas → 若有 `flash`，`globalAlpha=a` 填色（原片就是平滑混合）。
  3. 主 canvas 640×360（CSS `image-rendering: pixelated` 放大到窗口）：`imageSmoothingEnabled=false`，按 zoom / shake 裁框 `drawImage(base, sx, sy, W/z, H/z, 0, 0, 640, 360)`。
  4. UI 层：直接在主 canvas 上 `drawImage` 预烘的文字图（最近邻），对话框矩形用 `fillRect`。
  5. `fade`：`globalAlpha` 填色；`dither_fade`：预先做 17 张 8×8 的 Bayer 图样（阈值 k/16，单元 2×2 UI px）当 `createPattern` 填充，免读回。
- 为什么底层要软件写：抖动透明、调色板映射、冲击帧阈值、时停球、光环热场全都要逐像素判断；canvas 的 `globalAlpha` / 抗锯齿多边形会破坏画风。

### 7.2 必须注意的坑

1. **file:// 下读像素会被拦**：实测 Chromium `file://` 图片画进 canvas 后 `getImageData` → `SecurityError`；data URI 正常。因此：所有要进底层帧缓冲的图（角色图集、道具、场景专用、背景、宝石 / 拳头等小图）**在 data.js 里以 base64 data URI 内嵌**，加载后画到离屏 canvas 一次 `getImageData` 解成 `Uint32Array` 存起来（以后 blit 都是数组拷贝）。UI 层用的文字图不读回，可以是普通相对路径，但统一内嵌也行。JoJo 图集是小像素图，内嵌后体积大约 +33%，可接受；背景如果烘成长图要算一下体积。
2. **hash01 的 JS 写法**（必须用 `Math.imul` 和 `>>>0`）：
   ```js
   function hash01(...xs) {
     let h = 2166136261;
     for (const x of xs) {
       const v = Number.isInteger(x) ? x : Math.round(x * 997);   // Python: float -> int(round(x*997))
       h = (h ^ v) >>> 0;
       h = Math.imul(h, 16777619) >>> 0;
       h = (h ^ (h >>> 13)) >>> 0;
       h = Math.imul(h, 0x5BD1E995) >>> 0;
       h = (h ^ (h >>> 15)) >>> 0;
     }
     return h / 4294967296;
   }
   ```
   差异：Python 里 `3.0` 是 float 会乘 997，JS 里 `3.0` 是整数——图案会和原片不完全一样，游戏里无所谓，只要自身确定性即可。
3. **Bayer 抖动**：`const BAY = [0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5].map(v => v/16 + 1/32); const bay = (x,y) => BAY[((y&3)<<2)|(x&3)];`，判断一律 `bay(x,y) < alpha`。**抖动坐标用底层画布坐标**（震屏 / zoom 在合成阶段做），这样图样不会随震屏闪烁。
4. **PIL 的画线 / 多边形 / 椭圆**要自己写：Bresenham 线（`width>1` 用方形笔刷叠印）、三角形扫描线填充（速度线、hit_spark 尖刺（菱形 = 2 个三角）、替身卡平行四边形都是三角/四边形）、圆盘按 `_disc_np` 公式、椭圆描边（hit_spark 环、hamon 波纹、气泡）用中点椭圆。
5. **两种透明别混**：精灵 `alpha=0.92`、`paste(alpha)`、UI 文字淡入淡出 —— 原片是**平滑** alpha；`_paste_dither`、`_comp`、`_px(alpha)`、`burst` 淡出 —— 是**抖动**。软件 blit 要支持两种模式。
6. **24 fps → 60 Hz**：
   - 原片“1 帧”冲击帧 = 1/24 s ≈ 41.7 ms。游戏里按**时间窗**写（`t0 ≤ t < t0 + 1/24`，60 Hz 下约 2–3 帧），别写成“1 帧”，否则在 60 Hz 下只闪 16 ms，看不出来。
   - `floor(t·12)` 的抽帧保留；`shake` 的 30 Hz 换位保留。
   - `anim(t, fps, n)` 的精灵帧率保留原值（图集 json 里有 fps）。
7. **自适应阈值的冲击帧**要每次算亮度直方图（256 桶）求中位数 / 38%、72% 分位——一趟 57 600 像素，很便宜。
8. **`_noise_tex` 用的是 numpy RNG**，JS 复刻不出同一张图；两条路：预烘成 PNG（4 张 64×64 灰度，拼一张 256×64），或 JS 里用任意确定性 RNG 生成同算法的 value noise（视觉等价）。fog 的 180×512 纹理同理。
9. **fire_ankh 的高斯**：JS 里做 3 次盒式模糊近似高斯（σ = 0.018S+0.7，S=40 时 σ≈1.4，很小），或者在 Python 烘好几档 size（34/40/44）的 `core`/`up` 两张场存 PNG 的 R/G 通道。推荐后者，省事且与原片一致。
10. **`_aura_fields` / `_voronoi_pieces` / `_sag_curve` 这类按精灵名缓存的计算**：JS 里用 `Map`，key = `名字|帧|翻转|缩放|参数`。光环场是“剪影膨胀 + 上拖尾”，一个 80×80 的精灵算一次 < 1 ms。

### 7.3 哪些逐帧程序化、哪些预渲染

| 处理方式 | 特效 | 理由 |
|---|---|---|
| **逐帧程序化（照公式重写）** | shadow、hit_spark、shockwave、speedlines、impact_frame、rush、afterimage、burst、dust、smoke、explosion、fire、sparkles、glint、hamon、lightning、emerald_splash、tendrils、vines、void_sphere、knives、timestop / timestop_world / time_resume、clock、glow、light_beam、vignette、heat_haze、sepia、menace_bg、radial_burst_bg、iris、diamond_wipe、slash_wipe、stand_summon、aura_flame、shatter、crack、bats、rain、sand_wind、fog、water_* | 全是解析公式，参数（位置、方向、大小、颜色）每次不同；Python 版都在 0.1–4 ms，JS 更快。程序化才能跟随游戏里的命中点和方向 |
| **初始化时算一次、缓存** | `_dist_field` / `_angle_field`（按中心点；时停球、menace_bg、burst_bg、iris 用）、`_vig_field`、`_diamond_fields`、光环场、Voronoi 切块、刀的 72 个旋转角度、宝石 / 拳头兜底图、`_fog_tex` | 每个只依赖少量参数 |
| **Python 预烘成 PNG（data URI）** | ① 所有屏上文字：替身卡、名牌、地点字幕、大标题、拟声字（ORA / MUDA / ゴ / ド / ドドド / ズガッ / ガオン / バキィ / ドゴォォン / パキッ / ギロッ / 咋瓦鲁多 / 招式名…），直接 `import engine.text` 调 `text_img` 生成，保证 1-bit 字形；② 宋体 12/16 点阵字库（照银魂 `tools/build_assets.py` 716-732 的做法）给对白用；③ To Be Continued 徽章（`fx._tbc_img()` 直接导出）；④ fire_ankh 热场；⑤ `_noise_tex` ×4 | 浏览器 `fillText` 有抗锯齿且依赖系统字体；手机上没有雅黑 |
| **可选：预烘成帧序列** | 必杀切入的整段背景（menace_bg / radial_burst_bg + speedlines）如果想在手机上省电，可以烘 12 fps × 1 s 的循环；explosion 固定几档大小也能烘 | 只有手机性能吃紧时才需要；桌面不需要 |

### 7.4 特效实例队列（建议结构）

```js
// fx 实例：照原片“纯函数 + t0”
// clock: 'world'（被命中停顿 / 时停冻结）或 'real'（震屏、冲击帧、UI 一直走）
G.fxq.add({ fn: FX.hitSpark, t0: clocks.world, clock: 'world', dur: 0.2,
            args: { x, y, size: 18, colour: '#fff', accent: '#ffd83c', seed } });
// 每帧：for (const e of list) { const t = clocks[e.clock]; if (t - e.t0 > e.dur) remove; else e.fn(fb, t, e.t0, e.args, camX, camY); }
```
- 时长表（用于删实例）：hit_spark=`dur`(0.2)；shockwave=`dur`(0.4)；rush=`t1-t0+life`；burst=`life`；dust=`life`；explosion=2.2；smoke=`t1+life` 或常驻；fire_ankh=`t1`；emerald_splash=`t1-t0+max(0.12, L/speed)+0.12`；shatter=`dur`；glint=`dur`；time_resume=`dur`；water_splash=1.1；water_gush=`t1+0.6`；bats=`dur`；crack / vines / stand_summon / timestop 常驻（由所属实体或场景控制何时停）。
- **跟随实体的效果**（aura_flame、替身本体、光环、tendrils 连着两端）不进队列，在实体的 draw 里每帧调用。
- 坐标：原函数都是屏幕坐标；队列里存世界坐标，画时减相机（`x - camX`）。

### 7.5 性能注意

- 全屏滤镜每帧最多叠 2–3 个（例如 timestop_world + speedlines + vignette），JS 估计 < 2 ms。
- 避免每帧分配：帧缓冲、临时层（`_layer()` 那种用于“先画后整层抖动合成”的）各预留一块 `Uint32Array` 复用；用 `Uint8Array` 掩码代替新建图片。
- `_comp` 的“整层抖动合成”可以改成**画的时候直接带 alpha 判断**（`plot(x,y,c,alpha)`），省掉临时层。因为抖动阈值只和像素位置有关，重叠的线在同一像素上判断结果相同，和“先画层再整层抖动”**结果一致**（唯一区别：同一层里后画的颜色覆盖先画的，顺序照原函数即可）。
- 速度线 / 尖刺的多边形填充是主要 CPU 消耗，n≤60 时无压力。
- 手机：若掉帧，先降 `menace_bg` / `fog` / `sand_wind sheets` 到 30 Hz 更新（它们本来就是 12 fps 抽帧，缓存上一次结果，`ts` 没变就直接复用）。

### 7.6 关键原语的 JS 骨架（照 fx.py 的公式）

```js
const W = 320, H = 180;
const fb = new Uint32Array(W * H);                       // 0xAABBGGRR
const BAY = [0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5].map(v => v / 16 + 1 / 32);
const bay = (x, y) => BAY[((y & 3) << 2) | (x & 3)];
const pack = (r, g, b) => (0xff000000 | (b << 16) | (g << 8) | r) >>> 0;

function plot(x, y, c, a = 1) {                          // fx._px / _plot
  x = Math.round(x); y = Math.round(y);
  if (x < 0 || y < 0 || x >= W || y >= H) return;
  if (a < 1 && !(bay(x, y) < a)) return;
  fb[y * W + x] = c;
}
function disc(cx, cy, r, c, a = 1, sq = 1) {             // fx._disc_np
  if (r <= 0) return;
  cx = Math.round(cx); cy = Math.round(cy);
  const ry = r * sq, lim = r * r + r * 0.6;
  for (let y = Math.max(0, Math.floor(cy - ry - 1)); y < Math.min(H, cy + ry + 2); y++)
    for (let x = Math.max(0, Math.floor(cx - r - 1)); x < Math.min(W, cx + r + 2); x++) {
      const dx = x - cx, dy = (y - cy) / Math.max(sq, 1e-3);
      if (dx * dx + dy * dy <= lim && (a >= 1 || bay(x, y) < a)) fb[y * W + x] = c;
    }
}
// fx._lummap：整幅映射到调色板（时停 / 褐色），pal = [[r,g,b],…] 暗→亮
function lummap(pal, strength = 0.5, gamma = 0.9, amount = 1) {
  const L = pal.length, P = pal.map(p => pack(...p));
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const i = y * W + x, b = bay(x, y);
    if (amount < 1 && !(b < amount)) continue;           // timestop_world(amount<1)
    const v = fb[i], r = v & 255, g = (v >>> 8) & 255, bl = (v >>> 16) & 255;
    let lum = (0.299 * r + 0.587 * g + 0.114 * bl) / 255;
    if (gamma !== 1) lum = Math.pow(lum, gamma);
    const k = Math.floor(lum * (L - 1) + 0.5 + (b - 0.5) * strength);
    fb[i] = P[k < 0 ? 0 : k >= L ? L - 1 : k];
  }
}
// fx._qblend 的单像素版：A = 0..1 强度，levels 级，add = 加法
function qblendPx(i, x, y, col, A, levels = 3, add = false) {
  const q = Math.min(1, Math.floor(Math.min(1, Math.max(0, A)) * levels + bay(x, y)) / levels);
  if (q <= 0) return;
  const v = fb[i]; let r = v & 255, g = (v >>> 8) & 255, b = (v >>> 16) & 255;
  if (add) { r += col[0] * q; g += col[1] * q; b += col[2] * q; }
  else { r += (col[0] - r) * q; g += (col[1] - g) * q; b += (col[2] - b) * q; }
  fb[i] = pack(Math.min(255, r | 0), Math.min(255, g | 0), Math.min(255, b | 0));
}
```
- `impact_frame`：invert = 每像素 `255 - c`；其它样式先建 256 桶亮度直方图，2 色取中位数、3 色取 38% / 72% 分位作阈值（`lum > 阈值 + 0.01` 计数），再查 `IMPACT` 表。
- `_sphere_mix`（时停球）：用缓存的 `dist[]`（`Float32Array`，按 (cx,cy) 缓存）逐像素判断 `dist < R` 选 inside / outside 处理；边 `|dist - R| < rimw/2 + 0.2` 涂边色；恢复时 `R - band ≤ dist < R` 的带取反。

---

## 8. 为了“战斗爽 + 炫酷”要补的特效（照原片画风的配方）

原片是动画，没有玩家输入相关的反馈。以下每条都只用 §3 的积木 + 原片的颜色，不引入新画风。

### 8.1 命中停顿 + 受击闪白（hit-stop）

| 命中等级 | 世界时钟冻结 | 特效 | 相机 | 受击者 |
|---|---|---|---|---|
| 轻（J 第 1、2 下） | 50 ms（3 帧） | `hit_spark(size 10, accent=替身色或 '#ffd83c')` | `shake(1)` 0.1 s | 白闪 `tint white amt 0.8` 2 帧 → 0.4 1 帧；后退 4 px |
| 重（J 第 3 下、连打收尾） | 100 ms（6 帧） | `hit_spark(18)` + `shockwave(r_max 40, width 2)` + 随机拟声字（バキィ / ドゴォ / ズガッ，`sfx_text pop 0.12`） | `shake(3→0, 0.25 s)` + zoom 1.0→1.06→1.0（0.12 s，`ease_out`，s18:588 的做法） | 白闪 3 帧 + 击退 + `dust` |
| 必杀终结 / 击倒 | 0.3–0.5 s | 见 8.6 | | |

- 冻结期间：攻击者、受击者、`clock:'world'` 的粒子全停；震屏和冲击帧用 `clock:'real'` 继续。对应原片 s18 的 `vt`。
- 受击者“闪白”= 原片 `sp.render(..., tint='white', amt)`（`_apply_tint`），s13:688 被打飞时就是 `tint='white', amt=0.6·(1-u)`。
- 受击小抖：受击者精灵每 1/30 s 在 ±1 px 跳（同 `fr.shake` 的 hash 写法，只作用于这个精灵）。

### 8.2 闪避残影（K）

- 原片 `afterimage` 需要“过去的位置”，游戏里给角色加一个**环形缓冲**：闪避期间每 2 帧（≈33 ms）记一次 (x, y, 帧号)，保留 4 个。
- 画：`afterimage(主角精灵, 缓冲, colour=该角色替身光环色, alpha0 0.2, alpha1 0.55, amt 0.45)`；替身同时显形时替身也拖残影（s18:611-614 两边对冲就是这样）。
- 起步 `dust(n 6, speed 70)` 在脚下反方向；音效 `whoosh`。
- 无敌帧期间角色本体以 30 Hz 隔帧 `alpha 0.6` 闪（与 stand_summon 的 30 Hz 闪烁同一节奏）。
- 完美闪避（敌人攻击判定前 0.1 s 内按 K）：`glint(size 8)` 在角色眼睛位置 + 世界时钟 ×0.3 慢放 0.4 s（`gem_t` 式的子弹时间）+ `timestop_world(amount 0.35, tint 角色色)` 抖动淡入淡出。

### 8.3 替身格挡（L）

- 原片只有 `starplat.block` 一帧（白金之星）；其它替身用 idle 帧 + 向前 3 px + `aura_flame(intensity 1.2, height 8)`。
- 挡住时：在替身前方 `hit_spark(size 8, colour '#ffffff', accent=替身光环色)` + 一道竖长的椭圆冲击环 `shockwave(r_max 18, squash 1.6, dur 0.2)`（`squash` 是纵向倍数，>1 就是竖椭圆，像一面盾）；音效 银色战车用 `coin`（金属叮）、其他用 `punch pitch 1.4`。
- 精准格挡（0.12 s 窗口）：`impact_frame('bw3')` 0.042 s + `glint` + 反击窗口；拟声字 「キィン！」（白字 `#d8e4ff` 描边 `#1a1a3a`）。
- 格挡被破：替身 `stand_out`（白化溶解 0.2 s）+ `crack(size 12)` 画在替身胸口 0.4 s + 主角眩晕星 `sparkles(n 4, radius 8, '#ffd83c', period 0.5)`。

### 8.4 ORA 拳影墙（连按 J）

- 原片 `rush` 的拳头只有 10×8，屏上一团太小（fx_sheet_01）。游戏版加强（仍用原拳头图）：
  - 参数：`spread 36, rate 40, reach 30, life 0.3`（s18:789 最猛那段的值）；
  - **30% 的拳头用 ×2 缩放**画（最近邻），并且 `depth` 小的才放大（近大远小）；
  - 背后 `speedlines(radial, cx=接触点, n 40, inner 26, alpha 0.45)`（s18:665）；
  - 接触点 `clash_sparks`：每秒 11 个 `hit_spark(size 7~12)` 撒在 ±10/±14 内（s18:628-635）；
  - ORA 字：每 0.2 s 一个，左右槽位轮换（照 s18 `rush_texts` 的 6 个槽位和配色），字号 38–46；
  - `shake(1)` 持续；音效 `ora_rush(dur=按住时长)`；
  - 每一下拳头命中目标 → 走 8.1 的“轻”停顿但只停 1 帧（否则连打会卡），最后一下“重”。
- 其他替身的“连打”版本：
  - **银色战车**：`chariot.thrust` 帧 2/1 以 16 Hz 交替 + 每 0.06 s 一个 `hit_spark(size 8, accent '#c8d8ff')`（上下 ±15 px 错开）+ 每 0.12 s 一道 `slash_arc`（s07:259，size 15）+ 剑身 `glint` 扫过；拟声 「シュバババ」。
  - **绿色法皇**：每 0.12 s 一小波 `emerald_splash(n 4, spread 10, speed 380)`。
  - **红色魔术师**：`fire_jet`（s07:220）持续喷 + 末端 `fire_chunks`。
  - **隐者之紫**：藤鞭来回抽（`vines` 0.1 s 长出、0.1 s 缩回，交替两根）+ 每次命中 `hamon(strands 2)` 闪 0.15 s。
  - **愚者**：前方扇形沙暴 `sand_wind(region=角色前方带, sheets=True, speed 260)` + 每 0.15 s `burst(SAND, n 20, speed 160, spread 50, angle=朝向)`。
- **MUDA**（DIO 战）：同上换 `theworld.fist`、残影 `#fff2a0`、MUDA 字 `#ffe040` 描边 `#1a2a0a`。两边对打时照 s18 `shot_H`：双方 rush + 中间 clash_sparks + ORA/MUDA 交替。

### 8.5 必杀（U）特写切入

时间线（总约 1.2 s，游戏世界冻结，用真实时钟）：

| 时间 | 内容 | 依据 |
|---|---|---|
| 0.00–0.12 | 斜切转场进（`slash_wipe` 22°，颜色 = 替身面板色，白边），UI 同步清除 | s00:107-113 |
| 0.12–0.80 | 切入画面：`radial_burst_bg(colours=替身两色, n 18, spin 0.9)` 或 `menace_bg`（魔术师 `'#5a1010','#2a0608','#a0301a'`）+ `speedlines(radial, inner 62, alpha 0.55)`；替身头像 ×4 + `sp.aura(grow 2)` + `wobble(1.4, 13 Hz)` 抖；招式名用 `title` 样式（雅黑粗 48、`ease_back` 弹）或 `stand_card` 平行四边形；音效 `sting_reveal`（+0.26 s 和弦）/ `charge` | s18:680-707, s07:624-643 |
| 0.80–0.92 | 切回：`slash_wipe reverse` | |
| 0.92 起 | 招式本体（各替身见下），命中时 invert 1/24 s → 替身色 impact 1/24 s → 紫色定格 0.2 s（世界时钟冻结）→ 恢复 + `shake(4→0)` | s18:814-817 |

各替身 U 本体：
- 白金之星：终结拳（s18 `shot_LM` 全套，`ORA!!!` 72 号）；后期解锁「白金之星·世界」：`timestop(tint 'blue', dur 0.7)` + 停 2 秒内只有主角能动。
- 绿色法皇：丝线网 0.35 s 点亮（`_seg_grow`）→ 节点依次 `glow` + `glint` → 半径 20 米全方位 `emerald_splash`（s15）。
- 银色战车：盔甲脱落高速形态：本体 `afterimage` 6 个 + 斩击 `slash_arc` 8 道围成圈 + 最后一刺（s07 shot_C 的冲击帧组合 invert→blue）。
- 红色魔术师：十字火焰风暴（s07 E3+E4 全套）。
- 隐者之紫：藤蔓从地面 5 根迸出缠住敌人 + 波纹贯藤（`_hp_colour` 金紫闪）+ 每根藤尖 `hit_spark` 依次炸。
- 愚者：沙中现身（s11 `shot_fool` 全套，scale 3）+ 沙柱砸下 `burst(SAND, n 90)` + `shockwave(squash 0.3)` 地面环 + ドドド。

### 8.6 击倒 / 章节结束

- Boss 最后一击：8.5 的定格 + 敌方替身 `shatter(tint_to=替身亮色)`，敌人本体 `tint white` 闪后倒地；拟声「再起不能」（雅黑粗 40，白字黑描边，`pop`）。
- 章节结尾：`sepia(prog 0→1, 0.2 s)` + `tbc_arrow` + `tbc` 音效（+1.61 s 终音处定格）——这是 JoJo 最标志的收尾，原片就有，直接用。
- DIO 化灰：s18 `shot_N1/N2` 的 `crack + glow 漏光 + shatter(gravity -20) + ash`（ash 函数在 s18:295-311，要一起移植）。

### 8.7 能量条、低血、登场

- 替身能量攒满：主角 `aura_flame(colour 光环色, intensity 0.6→1.0 随能量)`；满的瞬间 `glint(size 7)` 在能量条右端 + `sparkles(n 5)` + `power_up` 音效；之后能量条以 2 Hz 在原色和 `_light(色,0.5)` 间闪。
- 低血（< 25%）：`vignette(amount 0.35 + 0.15·sin(2πt·1.2), colour '#5a0010')` 心跳式脉冲 + `heartbeat` 音效。
- Boss / 替身使者登场：镜头 zoom 推近 + `menacing`（ゴゴゴ，或 ドドド）+ 敌方 `stand_summon` + `stand_card(敌名, 英文名, colour=敌色)`，背景 `dim_bg` 压暗 0.45（s07:173-177）；音效 `menacing` + `sting_reveal`。
- 拾起对话 → 战斗切换：`diamond_wipe`（复古）或 `slash_wipe`。

### 8.8 时停的色调过渡（游戏机制版）

- DIO 发动：音效 `timestop` 先播 0.85 s（玩家有反应时间，是很好的预警）→ `timestop(tint 'yellow', dur 0.6)` → 停止期间画面 `timestop_world('yellow')`，**主角和其他敌人照常画在滤镜之前（被冻住、变色）**，DIO 和他的飞刀画在滤镜之后（全彩）；飞刀用 `knives(frozen=True)`，恢复时变成飞行。
- 承太郎反制（后期）：在黄色世界上再叠 `timestop(tint 'blue')` 的球（s18 `shot_E`：先 `timestop_world('yellow')` 再 `timestop(...'blue')`），过渡完成后整屏变蓝。
- 恢复：`time_resume(dur 0.36)`。
- 「チク…タク…」每 0.4 s 一个（`sfx_text size 22, '#fff0a0', jitter 0.5`，s18:494-496）；被冻住的人加 `outline '#f0e8c0'`（s18:482）保持可读。
- 游戏里时停中被冻的投射物：用 s15 `gem_t` 的做法——实例绑定“冻结时钟”。

---

## 9. 特效 ↔ 音效对照（engine\sfx.py 合成，docs\AUDIO_sfx.md）

| 特效 | 音效（名字 = sfx.make 的键） | 对齐点 |
|---|---|---|
| hit_spark 普通 / 重 | `punch` / `punch_heavy` | 命中时刻 |
| rush ORA / MUDA | `ora_rush` / `muda_rush`（`dur=` 时长） | t0 |
| 银色战车 | `slash`（提前 0.07 s）、`stab`（0.065）、`coin` | |
| 绿宝石水花 | `emerald` | t0 |
| 魔术师 | `fire_burst`、`fire(dur)`、`explosion` | |
| 隐者之紫 / 波纹 | `vine(dur 0.8)`、`hamon(dur)` | |
| 愚者 | `sand(dur)`、`dog_bark` | |
| 时停 / 恢复 | `timestop`（**提前 0.85 s**）/ `time_resume`（**提前 1.02 s**） | |
| 召唤 / 替身卡 | `zoom`（+0.47 s 峰）、`sting_reveal`（+0.26 s 和弦）、`whoosh` | |
| ゴゴゴ / ドドド | `menacing(dur)` / `dododo(dur)` | |
| 星光 / 闪光 | `glint`、`sparkle` | |
| 碎裂 | `glass_break` | |
| 定格 | `freeze` | |
| 冰 / 刀 / 枪 | `ice` / `knife_throw`（+0.08）、`knife_hit` / `gunshot` | |
| 收尾 | `tbc`（+1.61 s 终音）、`sting_comedy`、`jingle_victory` | |

---

## 10. 试跑记录

`scratchpad\understand\fx_bench.py`：每个特效在 320×180 夜景底上调用 15 次取平均（Python 3.12 + numpy，单线程），并输出 `fx_sheet_00..05.png` 联系表（第一张：速度线 / 冲击帧 / 命中火花 / 冲击环；第二张：ORA/MUDA rush、残影、爆炸各阶段；第三张：火、安卡、波纹、闪电、风沙；第四张：雾、绿宝石、丝线、藤、虚空球、飞刀、时停 5 个阶段；第五张：时间恢复、钟、光柱、碎裂、裂纹；第六张：转场、旋涡、放射背景、替身召唤 4 个阶段、气场、蝙蝠）。

```
shadow 0.09 | speedlines_radial 0.34 | speedlines_radial(alpha .5) 0.79 | speedlines_horiz 0.43
impact_invert 0.62 | impact_purple 2.21 | hit_spark 0.06 | shockwave 0.50
rush_ORA 0.79 | rush_MUDA 0.71 | afterimage 0.22 | burst 0.17 | dust 0.99 | explosion 2.14
smoke_loop 0.67 | fire_small 0.34 | fire_big 0.43 | fire_ankh 18.66（首帧含 scipy 高斯，缓存后约 1 ms）
sparkles 0.09 | glint 0.02 | hamon 0.33 | lightning 0.41 | rain 0.56 | sand_wind 1.00 | fog 2.83
emerald_splash 0.45 | tendrils 0.78 | vines 2.01 | void_sphere 0.59 | knives 0.38
timestop(进行中) 4.17 | timestop_world 1.31 | time_resume 2.89 | clock 0.50 | glow 0.26
light_beam 1.34 | vignette 1.63 | heat_haze 0.57 | shatter 0.36 | crack 0.19 | iris 0.42
slash_wipe 0.72 | sepia 1.34 | menace_bg 0.92 | radial_burst_bg 0.80 | stand_summon 0.36
aura_flame 0.26 | bats 0.25 | water_splash 0.96   （单位 ms）
```

另外两个小验证：
- `taint_test.py`：Chromium 打开 `file://` 页面，同目录 PNG 画进 canvas 后 `getImageData` → `SecurityError`；data URI → 正常（读到绿色 255）。
- `text_check.py`：四个字体文件都在；`text_img` 输出 alpha 只有 0/255（真 1-bit）；雅黑粗体能画 ゴ / ド / ズガッ 等假名（`text_sheet.png`）。
