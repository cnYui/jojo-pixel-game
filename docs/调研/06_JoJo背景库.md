# 06 · JoJo 背景库调研（engine/bg.py · bg_asia.py · bg_egypt.py）

> 调研对象：`D:\大疆\游戏素材\JoJo\源码\engine\bg.py`（19 行）、`bg_asia.py`（3815 行）、`bg_egypt.py`（3206 行）、`源码\docs\BG_asia.md`、`BG_egypt.md`；顺带看了用到背景的场景 `scenes\s00–s20` 和场景里自绘的背景。
> 只读调研，没有改任何源文件。所有试跑脚本和出图都在会话 scratchpad：`C:\Users\yui\AppData\Local\Temp\claude\D----\dd592801-8a86-495b-83a0-71d863169d18\scratchpad\understand\bg06\`（第 9 节列了每个文件是什么）。试跑全程 `PYTHONDONTWRITEBYTECODE=1`，源码目录没有留下 `__pycache__`（跑完用 `find` 核对过）。

---

## 0. 结论速览

1. **33 个背景函数**（bg_asia 17 个 + bg_egypt 16 个）+ 7 个“画在角色前面”的覆盖层 / 辅助函数。全部是 **320×180** 基础画布，签名统一 `name(fr, scroll=0.0, **kw) -> info`，`info['ground']` = 建议脚底线。逐个实测过尺寸、耗时、返回值（第 2 节）。
2. **能横向卷动的有 14 个**：循环的 13 个——周期 640 的 hongkong_night / calcutta_street / underwater / sky_day / sea_day（云层）/ sea_storm_night（天空；浪按列算，任意 scroll）/ desert / pyramids / egypt_town / cairo_rooftops / sunset_walk / desert_highway，周期 960 的 cairo_street（侧视）；再加 school_gate 这张 480 宽的**不循环**全景（只能卷 0–160）。s05 自绘的 dusk_gate（460 宽）也不循环。其余 19 个是**单屏 320 固定镜头**（房间、甲板、宅邸等；train_interior / plane_cabin 只有窗外风景自己卷）。
3. **可卷动背景都是“分层 + 每层一个视差系数 k”**，静态层全部 `lru_cache` 缓存成 PIL 图：可以**原样导出每一层的 PNG**，在 JS 里用银魂引擎现成的 `wrap` 图层（`o = floor(camX·k + t·vx) mod period`）拼回去。已验证：egypt_town 用导出的 3 层重建，在 5 个镜头位置和原函数**逐像素一致**（比较 y 62–180，避开云、鸟、太阳这些逐帧画的东西，0 个像素不同）；calcutta_street 全帧只差 10 个像素（就是逐帧画的 10 粒灰尘）。
4. **想要更长、不重复的街**：不改源码也能做——导出脚本在独立进程里先改模块常量（`E._TOWN_P = 1600`、`E._ST_P = 1920`、`A._CA_W = 1280`）再调建图函数，已实测出 1600 宽埃及小镇、1920 宽开罗街、1280 宽加尔各答（加尔各答的电线 / 晾衣绳只画在前 640，要导出脚本补）。埃及几个建图函数还带 `seed` 参数，换种子就是另一座城（阿斯旺 / 卢克索 / 埃德富各用一个）。
5. **发现一个原片 bug + 两处文档错误**：bg_asia 的 `_wrap_paste` 层是 scroll 越大**画面往右走**（镜头往左），而同一背景里逐帧画的东西（香港霓虹亮灯、加尔各答出租车、海草……）往左走，所以 **scroll≠0 时香港霓虹亮版和灯箱底板错位**（s07 用了 scroll=236/520，原片就是错的）。bg_egypt 和 school_gate 则是 scroll 越大画面往左（镜头往右），和文档一致。导出时统一按“世界坐标 + 镜头往右为正”处理就自然修好了（第 7.7 节）。
6. **对照第三部完整旅程**（第 5 节 37 段）：东京、飞机、香港、海上、印度、巴基斯坦、阿拉伯沙漠、红海、埃及、DIO 宅邸、开罗决战基本都有背景。**完全没有背景、必须新画的（P0）5 个**：新加坡酒店房间（恶魔）、新加坡街道（黄色节制）、瓦拉纳西恒河河坛（女帝）、潜艇内部（女教皇）、埃及神殿柱厅（阿努比斯 / 塞特神）。另有 8 个 P1（能凑合但不像）、9 个 P2（锦上添花）。神殿柱厅我用原工程的辅助函数做了原型，约 120 行出 3 层 640 循环，效果见 `proto\egypt_temple_proto.png`（第 6 节）。
7. **画布尺寸要总负责人拍板**：JoJo 背景全是 320×180，**建议新游戏内部画布就用 320×180**（×4 = 1280×720，×6 = 1920×1080，整数放大）。如果沿用银魂的 384×216，19 个单屏背景都得重画加宽加高（坐标是写死的），代价很大（第 7.1 节）。

---

## 1. 文件结构与通用约定

### 1.1 bg.py（门面）

`engine/bg.py` 只做两件事：`from .bg_asia import *`、`from .bg_egypt import *`，再把两个模块的 `BACKGROUNDS`（名字 → 一句话说明）合并成 `bg.BACKGROUNDS`。场景里一律写 `bg.<名字>(fr, ...)`。
注意：docstring 里提到的 `docs/BG.md` **不存在**（只有 BG_asia.md、BG_egypt.md）；bg_asia 的 docstring 提到的覆盖层 `cabin_seats_front(fr)` **代码里没有**。

### 1.2 函数约定（两个模块一样）

- 签名 `name(fr, scroll=0.0, **kw) -> dict`。每次调用**画满整张** `fr.img`（RGBA 320×180），是 `fr.t`、`scroll`、kwargs 的纯函数（可乱序、并行渲染）。
- 只用到 `fr` 的这些属性：`fr.t`（秒）、`fr.img`、`fr.d`（`ImageDraw.Draw(fr.img)`）；只有 `world_map` / `draw_route` 还会往 `fr.ui`（640×360 文字层）写城市名和「第N天」。导出脚本直接 `from engine.core import Frame; fr = Frame(t, 0, 10.0, 'x')` 即可调用。
- 返回 dict：`ground` 一定有（44–46 px 高角色的脚底 y），其余是锚点（门、桌子、镜子、水塔……都是屏幕坐标，随 scroll 变）。
- 静态层用 `functools.lru_cache` 缓存；首次调用 3–42 ms 建缓存，之后每帧 0.02–8 ms（第 2 节有逐个实测）。
- 画在**角色前面**的东西是单独的函数，场景在画完角色后再调：
  - bg_asia：`jail_bars(fr, bend=0.0, x0=6, x1=314, cx=160, top=0, bottom=146)`（2128 行）、`sea_storm_front(fr, scroll=0, lightning=0)`（1400）、`freighter_rail(fr, y=168)`（3280）
  - bg_egypt：`cafe_table(fr)`（1870）、`stairs_rail(fr, alpha=1.0)`（2498）、`fog_front(fr, amount=1.0, speed=9.0)`（1057）
- 其它辅助：`storm_wave_y(t, x, scroll=0, layer=4)`（1273，暴风浪某层在 x 处的水面 y，用来让船上下颠）、`draw_reflection(fr, box, name, x, y, ...)`（3758，把精灵裁进镜子 / 玻璃 / 水洼里，倒吊人用）、`world_map` + `draw_route` + `CITIES` + `map_xy(lon, lat)`（地图）。
- 依赖：PIL、numpy；**bg_asia 还 import 了 `scipy.ndimage`**（地图海岸线、膨胀运算），本机 scipy 1.16.3 有。
- 风格（BG_egypt.md 第 43–50 行、STYLE.md 第 2 节）：天空用 `core.gradient` 分段 + Bayer 抖动；灯光、太阳、蜡烛的光晕是分级抖动的径向透明度，不做抗锯齿；大块形体（房子、金字塔、宅邸）有 1 px 同色系深色描边；背景整体比角色精灵**略灰、略暗、对比低**，画面中间留空让角色突出；人物站在 y 105–160 这一带最清楚。

### 1.3 卷动（scroll）的方向——两个模块不一样（实测）

`scroll_dir.py` 量了 scroll 从 100 加到 120 时近景内容的水平位移：

| 背景 | 内容位移 | 含义 |
|---|---|---|
| hongkong_night / calcutta_street / underwater（`_wrap_paste` 层） | **+20（往右）** | 镜头往**左** |
| sea_day 浪花 | +16 | 同上 |
| sky_day 云（y 100–150 这一带量到的是 k 0.4 的中层云） | +8 | 同上；随时间（speed=30）也往右漂，文档写“往左”是错的 |
| school_gate | −20（往左） | 镜头往右 |
| egypt_town / cairo_street / desert（bg_egypt 全部） | −20 | 镜头往右，和文档一致 |

原因：`bg_asia._wrap_paste`（160 行）取 `x = -floor(off) % sw` 作为裁切起点，而 `bg_egypt._scroll`（66 行）取 `floor(off) % P`。bg_asia 里逐帧画的东西（香港亮灯霓虹 `x = (sx - off) % 640`、加尔各答出租车 `(250 - scroll) % 640`、海草 `(hrange - scroll) % 640`、香港路面标线、天线红灯）却是镜头往右的写法，所以 **scroll≠0 时它们和图层错位**。`hk_neon_scroll100.png` 能直接看到：亮的霓虹和暗的灯箱底板分家了。导出后统一用一个公式就没这个问题（7.7 节）。

已验证：bg_asia 的层用 `scroll = -camX` 调原函数，与 JS 公式 `o = floor(camX·k) mod P` 的重建**完全一致**（`asia_dir_check` 的结果：camX = 0/250/900/1235，都只差 10 个灰尘像素）。

---

## 2. 33 个背景逐个说明

### 2.1 总表（实测：t=1.0，`render_all.py`；`_sheet_all.png` 是全部 33 张的拼图）

“可走带”是我按地面几何给的**建议**脚底 y 范围（2.5D 走位用，类似银魂的 `yMin..yMax`），不是源码里的值。

| 名称（模块:def 行） | 场景内容 | 卷动 / 宽度 | ground / 建议可走带 | 首次 / 每帧 ms | 原片用在 |
|---|---|---|---|---|---|
| world_map（A:868） | 羊皮纸旅行地图（埃及→日本） | 不卷；`view=(cx,cy,zoom)` 放大 | — | 30 / 4.2 | s06 s08 s11 |
| sea_storm_night（A:1369） | 1983 年暴风雨夜的大西洋 | 天空 640 循环，浪按列计算，任意 scroll | 150；海面，不能走 | 19 / 8.2 | s01 |
| ship_hold（A:1542） | 木船货舱，摇晃的油灯 | 单屏 | 152；154–176 | 7 / 2.6 | s01 |
| sky_day（A:1645） | 飞机外的蓝天 + 云海 | 4 层（640/640/960/640）循环 | 150；不能走 | 14 / 0.3 | s06 |
| sea_day（A:1690） | 平静海面，地平线 y100 | 云层 640 循环，浪按行计算 | 150；不能走 | 5 / 0.5 | s06 s08 |
| underwater（A:1787） | 海底：光柱、海草、气泡 | 远景 + 海床 640 循环 | 160；158–178 | 10 / 1.2 | s08 |
| jail_cell（A:2039） | 1987 年东京拘留所（走廊视角） | 单屏 | 166（走廊）/ 130（牢内）；走廊 150–176，牢内 120–140 | 8 / 0.1 | s02 |
| kujo_house（A:2334） | 空条家和室：壁龛、金云纸门、庭院 | 单屏，4 个时段 | 160；148–176（左前方矮桌挡路） | 4 / 0.1 | s03 s05 |
| kujo_bedroom（A:2441） | 荷莉的卧室：发光的障子窗、屏风、行灯 | 单屏，4 个时段 | 158；150–176 | 9 / 0.1 | s05 s19 |
| school_gate（A:2598） | 春天早上的高中校门、樱花 | 480 全景，**不循环**，scroll 被夹在 0..160 | 150；140–176 | 15 / 0.2 | s04 |
| plane_cabin（A:2745） | 客机客舱，**一点透视**看向过道 | 单屏（窗外云在动） | 156；只有过道 x 112–208，不适合横走 | 15 / 0.9 | s06 |
| hongkong_night（A:2963） | 霓虹香港夜街，湿路面倒影 | 天空 + 3 层 640 循环 | 154；150–176 | 30 / 1.2 | s07 |
| hk_garden（A:3141） | 虎豹别墅式园林：白塔、虎像 | 单屏，日 / 夜 | 150；140–176 | 11 / 0.02 | s07 |
| freighter_deck（A:3258） | 生锈货轮甲板：吊车、集装箱、舰桥 | 单屏 | 152；140–176 | 9 / 0.05 | s08 |
| train_interior（A:3395） | 印度火车车厢，窗外风景飞驰 | 单屏（窗外 3 层自动卷） | 160（站）/ 124（座位）；154–178 | 13 / 0.7 | s08 |
| calcutta_street（A:3611） | 拥挤的加尔各答街道 | 天空 + 2 层 640 循环 | 154；152–176 | 26 / 0.6 | s09 s10 |
| india_alley（A:3729） | 印度小巷：镜子、玻璃窗、水洼 | 单屏 | 156；154–178 | 8 / 0.02 | s09 |
| desert（E:499） | 视差沙丘，5 个时段 | 3 层 640 循环 | 150；148–178 | 41 / 0.3 | s10 s12 |
| pyramids（E:611） | 吉萨三座金字塔 + 狮身人面像 | 4 层 640 循环（狮身人面像只有 1 个） | 150；148–178 | 42 / 0.4 | s00 |
| desert_highway（E:784） | 沙漠公路（飙车） | 6 层，**自动卷** speed=360 px/s | 160；车道 152 / 168 | 21 / 0.4 | s10 |
| fog_town（E:1028） | 正义的雾之镇：歪房子、墓碑 | 单屏（雾带在动） | 152；146–176 | 12 / 0.3 | s10 |
| dream_carnival（E:1246） | 死神13的梦：旋涡天空、摩天轮 | 单屏 | 152；140–176 | 11 / 6.5 | s10 |
| island_beach（E:1375） | 海滩：`redsea` 红海小岛 / `egypt` 埃及海岸 | 单屏 | 152；140–176 | 8 / 2.5 | s10 s11 |
| egypt_town（E:1726） | 阿斯旺 / 卢克索泥砖街 | 3 层 640 循环 | 152；146–176 | 25 / 0.4 | s12 |
| cafe_interior（E:1875） | 达比的烟雾咖啡馆 / 赌场 | 单屏 | 156；148–176 | 3 / 0.7 | s12 |
| game_room（E:2036） | 泰伦斯的游戏室，CRT 赛车游戏 | 单屏 | 156；148–176 | 3 / 0.8 | s12 |
| mansion_exterior（E:2179） | DIO 哥特宅邸剪影、满月、蝙蝠 | 单屏，dusk / night | 156；150–176 | 6 / 0.5 | s12 s14 |
| mansion_hall（E:2327） | 宅邸石厅：柱子、蜡烛、DIO 画像 | 单屏 | 154；150–176 | 8 / 0.3 | s13 |
| mansion_stairs（E:2465） | 大楼梯，DIO 站在平台上 | 单屏 | 166；15 级台阶另给 | 4 / 0.1 | s14 |
| cairo_rooftops（E:2638） | 开罗夜晚屋顶：水塔、钟楼 | 3 层 640 循环 + 2 个单独道具 | 156；148–176 | 13 / 0.6 | s15 |
| cairo_street（E:2837） | 决战街道：`side` 侧视 / `end` 一点透视 | side：3 层（640/960/480）循环；end：单屏 | side 160；150–176（end 170） | 27 / 0.6 | s12 s16–s19 |
| airport（E:3005） | 开罗机场白天：航站楼、塔台、客机 | 单屏 | 156；146–176 | 6 / 0.1 | s20 |
| sunset_walk（E:665） | 片尾：巨大落日、暗色山脊 | 2 层 640 循环 | 132（山脊）；只走剪影 | 9 / 0.3 | s20 |

（“A”= bg_asia.py，“E”= bg_egypt.py；行号是 `def` 所在行。ms 是本机 Python 实测，导出成 PNG 后游戏里不再跑 Python。）

### 2.2 bg_asia 逐个细节

**world_map(fr, scroll=0, view=None)**（868）
- 静态层 `_map_layer(phase)`（680），phase = `int(t/0.6) % 2`：两张 320×180，只差海面浪纹位置 → 导出 2 张交替显示。
- 画了：海岸线墨线、等深环、沙漠点（`_DESERTS`）、森林点、山脉（`_draw_mountain`）、河流（尼罗河绿谷 3 px）、富士山 / 宝塔 / 泰姬陵 / 金字塔图标、帆船、海蛇、罗盘 `_compass(img, 292, 124)`、烧焦边框 `_map_frame`。
- 投影 `map_xy(lon, lat)`（306）：经度 22–147E 按分段线性 `_LONK` 映射到 x 8–312（埃及 / 阿拉伯被拉宽），纬度 47N–5S 映射到 y 8–172。
- `CITIES`（545，实测）：东京 (298,44)、香港 (248,86)、新加坡 (227,152)、加尔各答 (195,85)、瓦拉纳西 (180,76)、卡拉奇 (138,78)、阿拉伯沙漠 (88,84)、红海 (56,75)、阿斯旺 (46,81)、卢克索 (45,73)、开罗 (40,61)。其它地点用 `map_xy`：阿布扎比 (106,79)、康翁波 (46,79)、埃德富 (45,77)。
- `view=(cx,cy,zoom)`：最近邻放大，例如 `view=(52,72,2.0)` 看埃及（`variants\_sheet_variants.png` 里有）。
- `draw_route(fr, stops, t, t0, t1, vehicle='plane'|'ship'|'train'|'car'|'sub', day=None, history=None, arc=0.14, ...)`（1041）：每段是二次贝塞尔（`_route_path`，966 行：法线偏移 `arc·L`，每 px 采 3 个点），红色虚线（周期 5、亮 3，2 px 粗，右下 1 px 暗描边，颜色 (204,32,40)）按缓动长出来；城市点（`_city_dot`）到达时扩一圈；交通工具图标优先用精灵 `prop.map_<vehicle>`（角色图集\道具\map_*.png 都有），飞机有地面影子、船有尾迹；`day` 盖红章「第N天」。
- 动的元素：海面浪纹两帧交替、路线生长、交通工具上下颠。

**sea_storm_night(fr, scroll=0, lightning=0, bolt_x=226, seed=0, front=True)**（1369）
- 天空是 640×92 的**调色板索引图** `_storm_sky_idx()`（1219，fbm 噪声分 7 级天空 + 4 级云：本体 / 深 / 边光 / 底），每帧按 `off = int(t·4 + scroll·0.15)` 横移，再叠 640×92 的低空碎云索引 `_storm_scud_idx()`（1344，`t·11 + scroll·0.3`）；`lightning` 0..1 在两套 11 色调色板之间插值（`_storm_lut`，1245）；>0.35 时画分叉闪电 `_bolt`（1321）。
- 海：y 92 以下渐变 + 6 层浪 `_STORM_WAVES`（1252：基线 97/104/115/131/152/175，振幅 3–18，波长 11–97，速度 5–31，视差 0.25–1.3），**12 fps 跳帧**（`stepped(t, 12)`），按列算浪顶（`_storm_edge`，1262），再画浪面、条纹、浪尖、白沫、飞沫。`front=False` 时不画最近一层，留给 `sea_storm_front` 盖在船身上。
- 返回 horizon 92、ground 150、swell 152。纯过场用（DIO 棺材被捞起）。

**ship_hold(fr, scroll=0, swing=1.0, lamp=1.0)**（1542）
- 静态 `_hold_layers()`（1440）：船板墙（每 7 px 一条）、4 根弯肋骨 + 铁箍、甲板梁、舱口格栅 (206–246, 0–15)、通往舱口的梯子、地板、左右木箱 `_crate`（1408）、木桶 `_barrel`（1427）、绳圈、3 根吊链。
- 每帧：油灯摆动 `θ = 0.30·swing·sin(1.7t)`，支点 (150,16)、绳长 34；**逐像素光照**：`I = clip(1 - dist/215, 0, 1)^1.15 · fl`，按 Bayer 量化成 6 级，颜色 = 环境光 (0.16,0.17,0.27) + I·暖光 (1.2,0.92,0.6) 乘到底图上；舱口月光柱（多边形，抖动一半像素混色）；灯罩、链条、10 粒灰尘。
- 摆动周期 2π/1.7 = 3.696 s，可以烘焙成一个循环（7.2 节）。

**sky_day(fr, scroll=0, speed=30)**（1645）
- 渐变天空 + 太阳 (40,30)（`_sky_grad('day')`）；4 层 `_sky_layers()`（1607）：远云 640（k 0.15）、中云 640（0.4）、云海 640（0.7）、近云 960（1.0），偏移 = `(scroll + t·speed)·k`。全部用 `_cloud_sprite`（247，带下右阴影的蓬松像素云）+ `_cloud_strip`（1593）。

**sea_day(fr, scroll=0, island=False)**（1690）
- 静态 `_sea_day_static(island)`（1665）：天空、太阳 (236,34)、可选远岛（x 34–92）、海面渐变、地平线 y 100。
- 每帧：云带 640×96（`t·2 + scroll·0.1`）；22 行浪花短线（越近越长越密，8 fps 跳帧）；太阳下面 36 个闪光点。

**underwater(fr, scroll=0)**（1787）
- `_uw_layers()`（1729）：base 渐变 320、远处礁石剪影 640（`scroll·0.35 + t·1.5`）、海床 640（沙 + 9 块岩石 + 8 丛珊瑚，k 1）。
- 每帧：水面波纹（y≈4）、6 道半透明光柱（alpha 22–40 呼吸）、远处 9 条小鱼、10 根海草摆动、16 个气泡上升。可走：海床 158–178（暗蓝之月、女教皇的海底战都能用）。

**jail_cell(fr, scroll=0, bars=False, bulb=1.0)** + **jail_bars(fr, bend)**（2039 / 2128）
- 一点透视（灭点 `_JVP = (160,70)`，后墙 `_JBW = (64,30,256,114)`），奶油色上墙 + 绿色护墙、天花板水管、高窗 (206–236, 38–56) 带阳光、墙上划的「正」字、摇滚海报、行军床（承太郎坐 `bunk_feet (148,124)`）、成堆杂志、收音机（LED 1 Hz 闪）、啤酒罐；牢外走廊地面 y 146–180 带栏杆影子。
- 每帧：窗口光束（alpha 30）、灯泡偶尔闪（12 fps 下 4% 概率暗到 0.55）。
- `jail_bars`：栏杆层按 `bend` 0..1 分 51 级缓存（`_bars_layer`，2084）；bend=1 时中间拉开约 40 px、上横梁断开、有受力高光（白金之星掰栏杆）。画序：jail_cell → 牢内角色 → jail_bars → 走廊角色。

**kujo_house(fr, scroll=0, variant='day'|'morning'|'dusk'|'night')**（2334）
- `_kujo_static(variant)`（2210）：左边壁龛（富士山挂轴、插花，x 14–86）、中间两扇金云纸门（x 90–204，角色站这里）、右边敞开的障子 → 走廊 → 庭院（松树 `_pine`、石灯笼 `_lantern`、池塘、院墙，garden 框 (206,34,318,134)）、左前矮桌 + 茶具 (14–82, 146–170)。时段只是整体调色（`_KJ` 字典 2137：天空渐变、色调、亮度）。
- 每帧：晨 / 昏两道斜光（alpha 随 sin 呼吸）、风铃 `_furin` 摇摆、黄昏 3 只乌鸦 / 其它时段 2 片落叶。

**kujo_bedroom(fr, scroll=0, variant='dusk')**（2441）
- `_bedroom_static(variant)`（2368）：大障子窗 (118,38,300,112) + 松枝影子、金屏风 + 梅花、花瓶架、脸盆托盘、行灯 (296–314,132–158)；中间空出的榻榻米放 `holly.bed`（`futon (150,166)`）。
- 每帧：黄昏 / 夜晚行灯闪烁光晕；早晨 / 白天窗下光斑 + 8 粒灰尘。

**school_gate(fr, scroll=0)**（2598）
- `_school_layers()`（2500）：far 400 宽（天空、远处城市、带钟楼的校舍 + 台阶，k 0.5）、near 480 宽（围墙、门柱 + 校名牌、半开铁门、4 棵樱花 `_sakura`、人行道、落花点）。scroll 夹在 0..160，**不循环**。
- 每帧：26 片飘落花瓣。返回 `gate` = 门洞屏幕 x 范围 (206−s, 294−s)。

**plane_cabin(fr, scroll=0, speed=60)**（2745）
- `_cabin_static()`（2633）：透视函数 `_pcp(X,Y,z)`（灭点 (160,66)，焦距 114）画天花板灯、行李架、两侧各 9 扇窗、8 排蓝座椅（白头巾套）、远排乘客后脑勺、驾驶舱门 + 出口灯、过道地毯；**两侧窗户是透明洞**，返回图层 + 左右两张窗户遮罩。
- 每帧：窗外 640 宽天空 `_cabin_sky()` 左窗往一个方向卷、右窗往反方向卷（`t·speed + scroll`）。
- 过道 x 112–208（y 156 处），不适合横向走位 → 灰塔战建议另画侧视客舱（第 6 节 P1）。

**hongkong_night(fr, scroll=0)**（2963）
- `_hk_layers()`（2847）：sky 320（紫色渐变 + 26 颗星）；far 640（天际线 22 栋楼、亮窗点，k 0.25，另 `t·0.5` 自己漂）；mid 640（唐楼 + 空调，k 0.6）；near 640（临街楼面、亮窗、橱窗 + 店主剪影、条纹雨篷、4 条小巷 `_HK_GAPS` 带红灯笼、17 块**不亮**的灯箱底板、人行道 y 146–152，k 1）。
- 每帧：17 块霓虹亮版（`_neon_sign(kind, n, col_i, seed, lit=True)`，2797：竖 / 横、大 / 小，5×5 或 10×10 伪汉字 `_GLYPHS`，7 种霓虹色 `_NEON`），其中 5 块会闪（`hash01` 在 10 fps 下判断）；天际线天线红灯 0.75 Hz 闪；**湿路面倒影**：y 153–180 取上方 54 行压成 27 行、上下翻转、每行按 `1.8·sin(r·1.3 + 6t)` 横向晃、亮度从 0.62 衰减到 0.27、减 30、每 4 行一条暗线；路面黄线每 40 px 一段（y 170）。

**hk_garden(fr, scroll=0, night=False)**（3141）
- `_hk_garden_static(night)`（3072）：山 + 树、7 层白塔 `_pagoda(d, 250, 104)`（3047）+ 台阶、彩绘假山洞 + 神像龛、橙色虎像 `_tiger_statue(d, 44, 132)`（3024）、两只金狮、红绿栏杆、地砖广场 (y 131–180)、两侧棕榈。夜版整体调暗 + 蓝色调 + 星星。
- 每帧：只有 2 只飞鸟。

**freighter_deck(fr, scroll=0)** + **freighter_rail(fr, y=168)**（3258 / 3280）
- `_freighter_static()`（3172）：灰天 + 云、海、黄色吊车（吊钩 (190,78)）、集装箱 `_container`（3161）、白色舰桥 + 烟囱 + 锈迹、舱盖、栏杆 y 116–132、救生圈、带铆钉的锈甲板 (y 130–180)、系缆桩、绳圈。
- 每帧：14 个海面闪光、2 只海鸥。（docstring 写“吊钩摇晃”，代码里吊钩是静止的。）
- `freighter_rail` 是最下方前景栏杆（可选）。

**train_interior(fr, scroll=0, speed=90)**（3395）
- `_train_static()`（3294）：奶油色上墙 + 绿色下墙、行李架 + 箱子、两扇窗 `_TR_WIN`（半拉的木百叶 + 窗栏，窗洞透明）、紫色长条座椅（seat_y 124）、木地板。
- 窗外 `_train_scenery()`（3357）：天空 320 + 远山 640（k 0.08）+ 中景 640（棕榈、茅屋、寺庙，0.35）+ 近景稻田 640（1.0），偏移 `t·speed + scroll`；电线杆 k 1.6（周期 600）；每 1.25 s 颠一下（整体下移 1 px）；2 个吊扇旋转（20 rad/s）。

**calcutta_street(fr, scroll=0, taxi=True)**（3611）
- `_calcutta_layers()`（3454）：sky 320（暖白天空 + 太阳）；far 640（褪色楼群，k 0.4）；near 640（粉彩殖民地楼、拱窗 + 绿百叶、阳台、伪天城文招牌 `_devanagari`（3434）、条纹雨篷、水果香料摊、晾衣绳、乱电线、40 个低饱和人群剪影（纱丽 / 头巾）、电车轨道 y 164/172，k 1）。
- 每帧：黄色大使牌出租车 `_ambassador(d, x, 170)`（3594，可关）、10 粒灰尘。

**india_alley(fr, scroll=0)**（3729）+ **draw_reflection**（3758）
- `_alley_static()`（3643）：老灰泥墙露砖、电线、小阳台晾衣、中间木门、左边金框大镜子 `_IA_MIRROR = (26,44,70,112)`、右边商店大玻璃窗 `_IA_WINDOW = (206,62,290,116)`、3 个水洼 `_IA_PUDDLES`。
- 每帧：水洼波纹、镜面扫光。返回 mirrors / windows / puddles 三组框 → **倒吊人“只在倒影里出现”的玩法可以直接用这三组坐标**。

### 2.3 bg_egypt 逐个细节

通用：所有横卷层都用 `_wrapped(P, h, drawfn)`（56 行）生成，**图宽 = 周期 P + 320**（多出来的 320 是开头的复制，裁切永远不会越界）；`_scroll(dst, im, off, y)`（66）按 `floor(off) mod P` 裁。

**desert(fr, scroll=0, time='day'|'noon'|'sunset'|'night'|'sunrise', sun=None)**（499；'dusk' = sunset、'dawn' = sunrise）
- 天空 + 太阳 / 月亮 `_sky_and_sun`（466）：各时段的渐变和日月位置在 `_TOD`（324）和 466–496 行（day 太阳 (256,30) r9、noon (168,16) r11、sunset (236,104) r16、sunrise (82,106) r14、night 月亮 (248,34) r10 + 90 颗星）。
- 层：far 沙丘 `_desert_far(time, seed=3)`（368，960×90，k 0.12，y 66）、mid `_desert_mid(time, seed=7)`（376，960×64，k 0.4，y 90）、near 沙地 `_desert_near(time, top=141, seed=11)`（394，960×47，k 1，y 133，有起伏、沙纹、石子、草丛、一个牛头骨）。沙丘都是 `_dunes_img`（269）画的：一座座重叠的新月形沙丘，背风面有阴影、迎风面有沙纹。
- 每帧：白天 3 朵云漂 + 2 只鸟；正午热浪扭曲（y 90–132 逐行横移）+ 2 只秃鹫盘旋。

**pyramids(fr, scroll=0, time='day'|'sunset'|'sunrise')**（611）
- far 沙丘（seed 5，k 0.05，y 76）→ 金字塔层 `_pyramid_layer(time)`（562，960×100，5 座金字塔，卡夫拉金字塔保留石灰岩尖顶，带石层纹理 + 1 px 描边，k 0.1，y 18）→ mid 沙丘（seed 13，k 0.4，y 82）→ 狮身人面像 `_sphinx_img`（604，48×23 的 ASCII 像素图，**只画一个**，屏幕 x = 22 − scroll·0.4，脚线 132）→ near 沙地（seed 17，k 1，y 133）。2 朵云。

**desert_highway(fr, scroll=0, speed=360)**（784）
- 总偏移 `s = scroll + speed·t`（自动卷）：方山 `_mesas()`（693，k 0.03，y 84）、far 沙丘（seed 9，k 0.08，y 78）、mid（seed 19，k 0.2，y 72）、电线杆 + 下垂电线 `_poles()`（712，周期 480，k 0.55，y 58）、路面静态 `_road_static()`（738）、黄色中线 + 碎石 + 路边草 `_road_marks()`（757，周期 480，k 1）。返回车道 lanes (152,168)、路面 (141,171)。

**fog_town(fr, scroll=0)** + **fog_front**（1028 / 1057）
- `_fog_town_static()`（924）：墨绿天空、远处尖顶房子剪影、4 栋歪房子 `_FOG_HOUSES`（带描边）、石板路 (y 140–180)、墓碑、枯树。
- 每帧：病态的月亮光晕 (160,34)、3 条雾带（`_fog_tex` 抖动雾纹理，y 20/84/120，速度 3/5/−7）、6 扇窗随机闪、2 盏路灯闪 `_FOG_LAMPS`。`fog_front` 是挡在角色前面的低雾（y 130，高 50）。

**dream_carnival(fr, scroll=0)**（1246）
- 旋涡天空 `_carnival_sky(phase)`（1125，12 个相位，`int(t·4) % 12`）、透视棋盘地板 `_checker_img(...)`（1214，48 个相位，慢慢往镜头方向滚）、静态层 `_carnival_static()`（1151：戴睡帽的弯月、摩天轮支架、条纹马戏帐篷、拐杖糖柱子）。
- 每帧：14 颗星闪、帐篷旗子飘、摩天轮旋转（中心 (70,84)、R 38、0.35 rad/s、16 盏追逐灯、8 个车厢）、6 个玩具（气球 ×3、小黄鸭、积木、星星）上下浮动。每帧 5–6.5 ms，是最贵的之一。

**island_beach(fr, scroll=0, variant='redsea'|'egypt')**（1375）
- `_beach_static(variant)`（1311）：天空、远岸（redsea = 红色岩石小岛；egypt = 白房子 + 宣礼塔 + 小棕榈 `_tiny_palm`）、青绿海面（y 100–134）、沙滩 + 贝壳 + 海星。中间沙地空着（直升机降落）。
- 每帧：3 朵云、埃及版一叶白帆漂、46 个海面闪光、一条滚动的浪线 (y≈124)、**海岸线逐列涨退**（湿沙带）、2–3 棵棕榈摇（`_palm`，4 帧 3 fps）、螃蟹横走。

**egypt_town(fr, scroll=0)**（1726）
- 天空渐变 + 太阳 (280,22) + 2 朵云 + 3 只鸟；far 天际线 `_town_far(seed=9)`（1667，圆顶、宣礼塔、小棕榈，k 0.3，y 0）；房子 + 棕榈 `_town_layers(seed=5)`（1628，k 1，y 0）；街道 `_town_ground(seed=5)`（1699，k 1，y 140，车辙）。
- 房子规划 `_town_plan(seed)`（1449）：每栋 54–96 宽、44–88 高，风格 house / shop / tall / nubian（努比亚彩带 + 蓝门），30% 有圆顶、40% 有垛口；窗户三种（百叶 / 拱窗 / 木格窗 mashrabiya）；商店有条纹雨篷 + 铜灯 + 货摊（橘子堆 / 香料锥 / 陶罐）+ 挂毯；墙根陶罐、篮子；屋顶上有一只猫和鸽子。注意：**图层里的棕榈是静止的第 0 帧**，不摇。

**cafe_interior(fr, scroll=0)** + **cafe_table(fr)**（1875 / 1870）
- `_cafe_static()`（1746）：烟熏灰泥墙、木护墙、拱窗外的开罗夜景 + 木格窗、酒瓶架、水烟壶、金字塔画、地砖。
- 每帧：绿罩吊灯 (160,60) 的光锥（闪）、光晕、桌面重画、吊扇、两股烟（桌上烟灰缸 (196,116)、水烟 (280,104)）。返回 table (104,118,216,132)、seats (82,150)/(238,150)。`cafe_table` 把桌子再画一遍，让坐着的人在桌子后面 → **达比的扑克小游戏桌面坐标现成**。

**game_room(fr, scroll=0)**（2036）
- `_game_static()`（1933）：深色房间、地毯、左右街机柜、“灵魂”玩偶架、海报、大 CRT 电视、地上的游戏机手柄。
- 每帧：CRT 蓝光闪烁的大光晕、**CRT 屏幕里在跑一个伪 3D 赛车游戏** `_game_screen(t)`（2002，74×52，带扫描线）、街机屏幕闪。返回 screen (122,58,196,110) → 泰伦斯的赛车小游戏可以把自己的画面贴在这个框里。

**mansion_exterior(fr, scroll=0, time='dusk'|'night')**（2179）
- 天空（dusk 紫红渐变 + 大月亮 (236,40) r22；night 深蓝 + 星 + 月 r24）、宅邸剪影 `_mansion_img(time)`（2069，两座尖塔、陡屋顶月光描边，返回窗户矩形表）、地面 + 铁栅栏 + 小路 + 枯树 `_mansion_ground(time)`（2129，栅栏在角色后面）。
- 每帧：55% 的窗户亮且偶尔闪、门口暖光、9 只蝙蝠绕两座塔飞（`_bat`）。

**mansion_hall(fr, scroll=0, breach=0..1, beam=0..1)**（2327）
- `_hall_static()`（2223）：石块墙、护墙、红丝绒窗帘窗（2、3 号柱之间）、DIO 画像、小画像、透视黑白大理石地面、红地毯 (y 150–162)、4 根柱子 `_PILLARS = (30,118,202,290)` 带烛台。
- 每帧：4 支蜡烛火苗 + 光晕；`breach` 在 (256,90) 开一个正圆洞（半径到 30，虚线边，洞里是白天开罗，`_breach_img(r)` 2299）→ 克林姆；`beam` 从洞口打下阳光柱 + 灰尘到地面 `beam_floor`（瓦尼拉·艾斯被晒死）。

**mansion_stairs(fr, scroll=0)** + **stairs_rail(fr, alpha)**（2465 / 2498）
- `_stairs_static()`（2381）：15 级台阶（`_ST_N, _ST_W, _ST_H = 15, 12, 6`，从 (34,166) 往右上到平台 (214,76)）、红地毯 + 金压条、远侧扶手、墙上一路往上的画像、平台后面拱窗里的满月（DIO 剪影站这里，`top (266,76)`）、烛台、平台下拱门。
- 每帧：3 支蜡烛。返回每级台阶的脚点 `steps`（实测 (40,160)…(208,76)）。`stairs_rail` 是近侧扶手 + 柱头，盖在爬楼梯的人前面。**“上楼梯却在往下走”的梗**直接用台阶下标。

**cairo_rooftops(fr, scroll=0, props=True)**（2638）
- 天空 + 110 颗星 + 月亮 (70,40) r20 + 城市雾光；far 天际线 `_roof_far()`（2539，圆顶 / 宣礼塔 / 亮窗，k 0.1）；mid `_roof_mid()`（2545，k 0.35）；**钟楼** `_clocktower_img()`（2551，30×118，单独一个，屏幕 x = 252 − scroll·0.35，底 136，钟面 (cx,62) r7 发光）；near 屋顶 `_roof_near()`（2593，屋面 y 146–180、女儿墙 138–146、天线、楼梯间小屋（周期内 x 420）、晾衣绳，k 1）；**水塔** `_watertower_img()`（2567，38×62，单独一个，屏幕 x = 58 − scroll，底 146）。
- `props=False` 不画钟楼 / 水塔，场景改用 `prop.clocktower` / `prop.watertower` 精灵（s15 就是这样，方便做碎裂、喷水）。返回 `watertower_tank` = 水箱框（花京院绿宝石水花的目标）。

**cairo_street(fr, scroll=0, time='night'|'dawn'|'sunrise', rise=None, view='side'|'end')**（2837）
- side：天空（夜：月 (262,30) r12 + 星；黎明 / 日出：太阳在 (160, 118 − rise·100)，rise 默认 dawn 0.15 / sunrise 0.9）；far 天际线 `_street_far(time)`（2800，周期 640，k 0.3）；楼面 `_street_graded(time)`（2774，周期 960，k 1）= 白天配色的楼面条 `_street_day(seed=121)`（2698：2–4 层殖民地楼、百叶、铁阳台、檐口、店招“字”、玻璃橱窗）按 `_GRADE`（2766）做乘 + 加调色，再随机点亮窗户（夜 45%、黎明 25%、日出 6%）；地面 `_street_ground(time)`（2809，周期 480：人行道 142–152、路缘、车道 156–180、虚线、电车轨）；路灯 `_LAMPS_X = (40,200,…,840)`（每 160 px 一盏，日出不亮）。
- end：一点透视（灭点 (160,92)，`_proj(X,Y,Z)` 3034），`_street_end_static(time)`（3040）两侧楼房往远处收，太阳正好从灭点升起，路灯往远处排；日出时沿街洒光。适合决战对峙、日出镜头，不适合走位。
- **没有白天版**，但 `_street_day()` 本身就是白天配色的楼面条（第 6 节 P1 #12 直接用它）。

**airport(fr, scroll=0)**（3005）
- `_airport_static()`（2895）：玻璃航站楼 + 波浪顶棚 + 登机廊桥、塔台、棕榈、停着的客机（无涂装，绿红条）+ 舷梯车、停机坪黄线、行李车。
- 每帧：2 朵云、太阳、远处起飞的小飞机、跑道热浪、塔台红灯 1 Hz 闪。返回 plane_door (238,112)。

**sunset_walk(fr, scroll=0)**（665）
- 天空 h 140（橙到紫的条带）、巨大落日 (160,116) r30 + 光晕、5 条横穿太阳的云带（自己漂）、4 只鸟；远处红沙丘 `_sunset_far()`（633，k 0.3，y 90）；暗色山脊 `_sunset_ridge()`（639，k 1，y 120，脊线 y≈132，有边光和枯草）。下面 48 px 是暗的，留给片尾字幕。角色画成黑剪影（`tint='black', amt≈0.9`）。

---

## 3. 场景里自绘的背景（不在 bg 模块）

| 场景 | 函数（文件:行） | 内容 | 尺寸 / 能否复用 |
|---|---|---|---|
| s05 | `dusk_gate(fr, scroll)`（s05_holly.py:645） | **空条家门口的黄昏**：大落日 (212,120)、紫橙天空、远处东京剪影（`_dusk_far` 400 宽，k 0.25）、电线杆 + 电线（`_poles`）、中景 440 宽（k 0.6）、近景门 + 院墙 + 松树（`_dusk_near` 460 宽，`NEAR_OX = 40`）、乌鸦、路面反光 | **不循环**，有效 scroll −40..100（`variants\_sheet_variants.png` 里 scroll=200 右下角已经露黑）。可以当“空条家门外”的小地图（约 460 宽） |
| s06 | `_cockpit_bg()`（s06_plane.py:433）+ `_ws_view` | 驾驶舱侧视（机头朝右），挡风玻璃里的天空逐帧画 | 单屏；可做“灰塔杀了机长”的插入镜头 |
| s16 | `_red_sky()` / `_bloodify(...)`（s16_joseph_fall.py:187 / 255） | 把 cairo_street 的天空换成**血红天空 + 血月**，其余画面往红色调 | 是个后处理：任何背景 + 天空遮罩都能用（DIO 吸血、时停的氛围） |
| s17 | 月夜天空 + 压路机腾空（`fx.stars` + 月亮 + `prop.roadroller`） | 压路机砸下来的镜头 | 过场 |
| s00 | `draw_space`（深空星野）、`fx.radial_burst_bg` + 斜色块 | 片头点名卡底板 | 标题 / 替身卡界面可借用 |
| s12 | `_frieze()`（s12_montage2.py:419） | 金徽章 + 象形文字壁饰（用了 `场景专用\s12_g_ankh/eye/ibis/sun/wave.png`） | 神殿背景可直接借这 5 个象形文字精灵 |

还有个镜头技巧值得沿用：`s10_montage1.py:154 bg_zoom(fr, fn, z, cx, cy, **kw)`——把背景画到临时 Frame，再整数倍最近邻放大中间一块当特写背景（s10 的正义 / 恋人 / 太阳 / 死神13 / 审判特写都这么做）。游戏里放必杀特写时同理：背景图 ×2 裁一块即可。

可当场景布景的现成精灵（角色图集\道具、场景专用）：`clocktower`、`watertower`、`s15_clock_n`、`s15_wtower_n`、`plane`、`plane_crash`、`ship`、`boat`、`submarine`、`heli`、`camel`、`car`、`roadroller`、`coffin`、`tv`、`s08_dinghy`（救生艇）、`s10_car`、`s12_car_blue/red`、`map_car/plane/ship/sub/train`、`s11_map_heli`。

---

## 4. 原片怎么用这些背景（参数取值，供复刻镜头）

（`grep bg\.` 全部场景的结果，节选有参数的）
- s06：`world_map(view=...)` + `draw_route(['东京','香港'], t, 0.35, 1.7, vehicle='plane', day=1, day_pos='br')`；`plane_cabin(speed=70)`；`sky_day(scroll=u*300, speed=40)`；`sea_day(island=True)`
- s07：`hongkong_night(scroll=236)`、`scroll=520+38*e`；`hk_garden(night=True)`
- s08：`draw_route(['香港','新加坡'], vehicle='ship')`、`draw_route(['新加坡'] + TRAIN_WP + ['加尔各答'])`；`train_interior(speed=110)`
- s09：`calcutta_street(scroll=60+cam, taxi=False)`；`india_alley` + `draw_reflection`
- s10：`desert_highway(scroll=0, speed=360)` / `(scroll=137, speed=0)`；`fog_town` + `fog_front(amount=0.9)`；`calcutta_street(scroll=380)`（恋人，卡拉奇）；`desert(scroll=40, time='noon')`（太阳）；`dream_carnival`；`island_beach(variant='redsea')`（审判）
- s11：`world_map(view=(cx,cy,z))` + `draw_route(['红海', SUB_WP, '阿斯旺'], ...)`；`island_beach(variant='egypt')`
- s12：`desert(time='day')`（盖布神）；`egypt_town(scroll=0)`（奥因哥·波因哥）；`cafe_interior` + `cafe_table`；`cairo_street(time='sunrise')`（宠物店）；`game_room`；`mansion_exterior(time='dusk')`
- s13：`mansion_hall(breach=..., beam=...)`；s14：`mansion_stairs` + `stairs_rail`；s15：`cairo_rooftops(scroll, props=False)`
- s16–s19：`cairo_street(time='night')`、`view='end'`、`time='dawn'/'sunrise', rise=r`；s19：`kujo_bedroom(variant='morning')`；s20：`airport`、`sunset_walk(scroll=dt*WALK_SPEED+40)`

---

## 5. 对照第三部完整旅程：已有 / 缺口

优先级：**P0** = 这场战斗现在没有像样的背景，必须画；**P1** = 现有背景能凑合但不像；**P2** = 锦上添花。

| # | 地点 | 剧情 / 敌人（替身） | 已有背景 | 缺口 |
|---|---|---|---|---|
| 1 | 东京·警局拘留所 | 承太郎 vs 阿布德尔（红色魔术师，教学战） | jail_cell + jail_bars | 警局走廊（P2，可不做） |
| 2 | 东京·空条家 | 荷莉、乔瑟夫念写 DIO | kujo_house ×4 时段、kujo_bedroom ×4、s05 dusk_gate | — |
| 3 | 东京·学校 | 花京院（绿色法皇） | school_gate（480 全景） | 校内石阶 / 保健室（P2） |
| 4 | 成田机场 | 出发 | airport（开罗机场，有棕榈） | 去掉棕榈的变体（P2） |
| 5 | 飞机 | 格雷·弗莱（灰塔） | plane_cabin（纵深透视）、s06 驾驶舱、sky_day | **侧视客舱 plane_cabin_side（P1）** |
| 6 | 坠海 → 香港 | — | sea_day(island)、world_map | — |
| 7 | 香港·街 | 遇波鲁纳雷夫 | hongkong_night | 粥店内景（P2） |
| 8 | 香港·虎豹别墅 | 波鲁纳雷夫（银色战车） | hk_garden 日 / 夜 | — |
| 9 | 海上·游艇 | 冒牌船长（暗蓝之月） | sea_day、underwater | **游艇甲板 yacht_deck（P1）** |
| 10 | 海上·货轮 | 猩猩（力量） | freighter_deck(+rail)、s08 救生艇 | **货轮船舱走廊 freighter_corridor（P1）**，船体变成肉的变体（P2） |
| 11 | 新加坡·酒店 | 诅咒的德波（恶魔） | 无 | **酒店房间 singapore_hotel（P0）** |
| 12 | 新加坡·街 / 缆车 | 橡胶灵魂（黄色节制） | 无 | **新加坡街道 singapore_street（P0）**、缆车 cable_car（P1） |
| 13 | 火车 | — | train_interior | — |
| 14 | 加尔各答 | 荷尔·荷斯 & J·盖尔（皇帝 & 倒吊人） | calcutta_street、india_alley + draw_reflection | — |
| 15 | 瓦拉纳西 | 妮娜（女帝） | 只能拿 india_alley / calcutta 凑 | **恒河河坛 ganges_ghat（P0）**；瓦拉纳西街（P2：calcutta 调色） |
| 16 | 印巴边境山路 | ZZ（命运之车） | desert_highway | 山路变体 mountain_road（P2） |
| 17 | 巴基斯坦·雾之镇 | 恩雅婆婆（正义） | fog_town + fog_front | 恩雅的旅馆内景（P2） |
| 18 | 巴基斯坦·卡拉奇 | 钢铁·丹（恋人） | calcutta_street（原片 s10 就这么凑的） | **脑内微观世界 brain_inside（P1）**；卡拉奇街调色（P2） |
| 19 | 阿拉伯沙漠 | 阿拉伯·法兹（太阳） | desert(noon) + 自画假太阳 | 阿联酋小镇 / 绿洲（P2） |
| 20 | 沙漠·小飞机 / 梦里 | 曼尼许·男孩（死神13） | dream_carnival | 小飞机机舱（P2） |
| 21 | 红海·小岛 | 卡梅奥（审判） | island_beach(redsea) | — |
| 22 | 红海·潜艇 / 海底 | 米德拉（女教皇） | underwater | **潜艇内部 submarine（P0）**；海底牙床变体（P1） |
| 23 | 埃及海岸 | 伊奇乘直升机加入 | island_beach(egypt)、prop.heli | — |
| 24 | 埃及沙漠 | 恩多尔（盖布神） | desert(day) | — |
| 25 | 阿斯旺 | 奥因哥 & 波因哥（克努姆神 / 托特神） | egypt_town（seed 5） | — |
| 26 | 康翁波 / 卢克索神殿、尼罗河岸 | 恰卡 / 凯恩（阿努比斯神） | 无 | **神殿柱厅 egypt_temple（P0，已出原型）**；尼罗河岸 nile_bank（P1） |
| 27 | 埃及小镇·铁路 / 电塔（具体城镇说法不一） | 玛丽亚（芭丝特女神） | egypt_town | **铁路 + 电塔 egypt_rail（P1）** |
| 28 | 卢克索 | 阿雷西（塞特神） | egypt_town（换 seed）+ egypt_temple | — |
| 29 | 开罗·咖啡馆 | 丹尼尔·J·达比（奥西里斯神） | cafe_interior + cafe_table | — |
| 30 | 开罗·白天街道 | 宠物店（荷鲁斯神） | cairo_street（只有夜 / 黎明 / 日出） | **白天开罗街（P1，几乎不用画）** |
| 31 | DIO 宅邸外 / 游戏室 | 泰伦斯·T·达比（阿图姆神） | mansion_exterior、game_room | — |
| 32 | 宅邸幻象 | 肯尼·G（次中音萨克斯） | 无 | 幻象走廊（P2） |
| 33 | 宅邸内 | 瓦尼拉·艾斯（克林姆） | mansion_hall（breach / beam） | **宅邸走廊 mansion_corridor（P1）** |
| 34 | 宅邸楼梯 | DIO 初现（波鲁纳雷夫的楼梯梗） | mansion_stairs + stairs_rail | — |
| 35 | 开罗夜街 / 屋顶 | DIO（世界）；花京院之死；乔瑟夫被吸血 | cairo_street side / end、cairo_rooftops、s16 血红天空 | 开罗桥 / 尼罗河夜景（P2） |
| 36 | 黎明 | 最终战、乔瑟夫复活 | cairo_street dawn / sunrise（rise 可调） | — |
| 37 | 尾声 | 机场告别、片尾、荷莉醒来 | airport、sunset_walk、kujo_bedroom(morning) | — |
| — | 旅途过场 | 每章之间 | world_map + draw_route | 地图上加阿布扎比等点：`map_xy(54.4, 24.5)` → (106,79) |

---

## 6. 缺的背景怎么画（照原工程的画法）

通用做法：新背景写成和原来一样的形式——`_xxx_static()` / `_xxx_layers()` 用 `lru_cache` 出静态层，`xxx(fr, scroll=0, **kw)` 每帧只画会动的小东西，返回 `{'ground': ..., 锚点...}`。**写在游戏仓库里**（例如 `游戏\tools\bg_new\*.py`），`import engine.bg_asia as A, engine.bg_egypt as E` 借用它们的私有辅助函数，不改源码目录。导出时和旧背景走同一条流程（第 7 节）。

可借的辅助函数（行号 = def 行）：
- bg_egypt：`_sky(fr, stops, h, bands)` 52、`_wrapped(P, h, drawfn)` 56、`_scroll` 66、`_ext` 77、`_outline(im, col)` 86（1 px 描边）、`_glow_at(img, cx, cy, rx, col, strength, ry, levels)` 119、`_disc` 125、`_grid(ascii, pal)` 134、`_dither_rect` 147、`_stars` 175、`_moon` 214、`_sun` 222、`_cloud_img` / `_clouds` 232 / 259、`_dunes_img` 269、`_TOD` 324、`_shimmer` 439、`_birds` 449、`_palm_img(h, lean, frame, pal, flen, seed)` 817、`_tiny_palm` 868、`_palm` 881、`_fog_tex` / `_fog` 889 / 910、`_house` 1471、`_skyline(d, ox, P, base, seed, col, hmin, hmax, lit, win_col, minaret_p, dome_p)` 2504、`_gothic_window` 2062、`_bat` 2169、`_breach_img(r)` 2299、`_proj` 3034。
- bg_asia：`_vnoise` / `_fbm` 62 / 84、`_vnoise_wrap` / `_fbm_wrap` 1166 / 1189（横向可循环的噪声）、`_grade(img, sat, val, tint, tint_amt)` 94、`_mul_tint` 110、`_dither_rect` 118、`_tex_noise(img, box, amt, seed, cell)` 1859、`_wrap_paste` / `_hscroll` 160 / 170、`_glow` 221、`_blend_poly` / `_blend_rect` 232 / 238、`_cloud_sprite` 247、`_cloud_strip` 1593、`_sun` 1628、`_bolt` 1321（分叉线，也能画神经 / 树根）、`_crate` / `_barrel` 1408 / 1427、`_post` / `_shoji` / `_pine` / `_lantern` 2171–2198、`_tatami` 2149、`_sakura` 2472、`_pcp` 2628、`_neon_sign` 2797、`_glyph` / `_glyph2` 2782 / 2789（伪汉字）、`_pagoda` 3047、`_container` 3161、`_devanagari` 3434、`_ambassador` 3594。
- core：`gradient(img, box, stops, vertical=True, dither=True, bands=None)` 323、`paste(dst, src, x, y, alpha)` 359、`_bayer_tile` 307、`hash01` / `hrange` 165 / 178（确定性随机，导出结果每次都一样）、`mix`。

### P0（必须画）

**① singapore_hotel（恶魔·德波）** 单屏 320×180，ground 156，可走带 148–176。
- 照 `_bedroom_static`（A:2368）的写法：天花板 0–12（深木色），墙 12–140 用浅青灰墙纸 + 每 8 px 一道 `mix` 竖纹 + `_tex_noise(img, (0,12,W,140), 0.06, seed)`；踢脚线 138–142。
- 右边窗户 (206,34,306,110)：窗里贴**真像素**——裁 `A._hk_layers()` 的 far 层（640 宽夜景天际线）一段贴进窗框，再 `_grade(val=0.8)`；窗帘两片（竖条 + 下摆）。
- 中左一张床（床头板、白床单、两个枕头，床底留一条黑缝——恶魔娃娃躲在床底）；右前方小冰箱 26×32（德波本人躲在冰箱里），门把手高光；床头柜 + 台灯（`_glow_at(..., (255,200,120), 0.3)`）；地毯用 `_dither_rect` 做两色暗纹；吊扇（直接抄 `train_interior` 3418–3426 的三叶扇）。
- 动：台灯 `noise1` 闪、吊扇转、窗帘 `sin` 微摆、窗外城市灯随机闪。

**② singapore_street（橡胶灵魂·黄色节制）** 640 循环，ground 154，可走带 150–176。
- 结构抄 `_calcutta_layers`（A:3454）：sky 320 + far 640（k 0.4：现代高楼，矩形 + 蓝玻璃窗点阵）+ near 640（k 1）。
- near 改成**新加坡骑楼（shophouse）**：粉彩配色换成土生华人配色（薄荷绿、粉、鹅黄、白），二楼百叶窗保留（抄 3493–3507 的拱窗 + 百叶），一楼改成“五脚基”连续拱廊（`pieslice` 拱形暗洞，y 112–148）；招牌用 `_glyph2` 画 2 倍伪汉字，或者 `_neon_sign(kind, n, col, seed, lit=False)` 的不亮版（白天）；楼与楼之间种棕榈 `E._palm_img(h=70, lean=6, frame, pal='day', flen=26)`。路面 148–180 + 黄色路缘。
- 动：棕榈 4 帧摇、云漂、行人剪影（抄 calcutta 3566–3589 的人群，换成短袖、遮阳帽）。
- 缆车（P1）：上半 `sky_day` 层 + 下半 `sea_day` 静态，前面盖一张缆车厢内框（窗框、座椅、扶杆），整体随时间轻微晃（y ±1）。

**③ ganges_ghat（女帝·妮娜，瓦拉纳西）** 640 循环，ground 158，可走带 146–168（河坛最上面的平台）。
- 天空：清晨薄雾渐变 [(236,206,170),(250,226,190),(214,200,190)]，bands 8；低太阳 `E._sun(img, 70, 60, 10)`。
- far（k 0.25）：对岸平沙线 + 几条小船剪影。
- mid（k 0.6）：河坛上的建筑——**锡卡拉式寺庙尖塔**（叠梯形，每层加横肋，顶上一个葫芦形尖顶 kalasha）、老砖楼（calcutta 楼的画法换成赭石 / 砖红 + `_tex_noise`）、`_devanagari` 横幅、彩色旗子。
- near（k 1）：**石阶**从 y 120 往下到 150（每 4 px 一级，亮暗两色 + 断裂缝）、草编阳伞（`pieslice` 180–360 的稻草色伞面 + 竹竿）、坐着的苦行僧剪影；y 150–180 是恒河水：浪花短线照 `sea_day` 1700–1710 的写法缩小，水里的倒影照 `hongkong_night` 2997–3013 的写法（取上方石阶压扁翻转、逐行横晃）；岸边系着的木船。
- 动：水波、倒影晃、木船上下颠、鸽子（`E._birds`）、火葬河坛冒烟（抄 `cafe_interior` 3013 附近的烟缕算法）、水面漂的万寿菊点。

**④ submarine（女教皇·米德拉）** 单屏 320（或 640 循环的走廊版），ground 156，可走带 150–176。
- 侧剖钢壳：墙 `gradient((0,0,W,150), [(40,52,60),(28,36,44)], bands=6)`，每 8 px 一颗铆钉（`point` 两色）；横向水管（宽 3 的线 + 1 px 高光，抄 `ship_hold` 铁箍的配色 (70,72,80)/(150,150,160)）；阀门轮（圆 + 十字）；压力表（圆盘 + 指针，每帧小幅抖）；**舷窗**：圆形遮罩里贴 `A._uw_layers()` 的 base + far 层（真海底像素，气泡照 `underwater` 1834–1845 画）；中间潜望镜；舱口 + 梯子抄 `ship_hold` 1483–1497；地板是格栅（网格线）。
- 动：红色警报灯旋转（`_glow` 红色，alpha 按 sin），压力表指针，漏水滴，舷窗气泡。
- 变体 `teeth=0..1`（P1）：女教皇变成机器零件 / 墙里长牙——在墙上叠两排白色三角牙（多边形 + 深色描边），按 teeth 从墙里伸出来。海底版同理：`underwater` 上叠一排巨大牙床。

**⑤ egypt_temple（阿努比斯神、塞特神）** 640 循环，ground 156，可走带 146–176。**已做原型**：`scratchpad\…\bg06\proto_temple.py`，出图 `proto\egypt_temple_proto.png`。
- 天空 `E._sky(fr, E._tod('day')['sky'], h=H, bands=16)`；far（k 0.3）：塔门（两个梯形）+ 方尖碑 + 小棕榈 `_tiny_palm`；near（k 1）：每 80 px 一根纸莎草柱（柱身左亮右暗、开花形柱头、彩带 + 象形文字点阵）+ 顶上横梁，整层 `E._outline(..., (110,80,66))`；地面（y 140，40 高）砂岩石板 + 积沙。原型约 120 行，3 层都是 `_wrapped`，跟原背景同一套接口。
- 原型还要补：far 层下沿 y 120–140 露出天空，要用 `E._desert_far('day')` 垫一层沙丘；太阳被横梁挡住，挪到 y 10 左右或去掉横梁的一段；象形文字可以换成 `场景专用\s12_g_*.png` 那 5 个精灵；夜版用 `_TOD['night']` 配色 + `_moon`。
- 变体：公羊头狮身像大道（一排 `_grid` 画的卧像，参考 `_SPHINX` 576 行的 ASCII 画法）。

### P1（能凑合但不像）

**⑥ plane_cabin_side（灰塔）** 640 循环，ground 160。侧剖客舱：窗户一排（y 40–70，挖透明洞，窗后 `A._cabin_sky()` 自己卷）、行李架（y 20–38）、侧面座椅每 40 px 一排（蓝 (46,70,140) + 白头巾套，配色取自 `_cabin_static`）、乘客后脑勺（发色表同 2716 行）、过道地毯 (70,84,130)。氧气面罩掉下来可以用 `场景专用\s06_mask.png`。（应急方案：plane_cabin 当固定竞技场，玩家只在过道 x 112–208 里躲虫子。）

**⑦ yacht_deck（暗蓝之月）** 单屏。背景 `A._sea_day_static(False)` + 浪花；白色游艇甲板（柚木条 (176,130,84)，木纹照 `_hold_layers` 1499–1506 地板的画法）、白色舱房 + 舷窗、栏杆 + 救生圈（抄 `_freighter_static` 3222–3230）、桅杆。动：整层随浪上下 ±1 px（`sin`）、海鸥、海面闪光。（应急：freighter_deck 直接用。）

**⑧ freighter_corridor（力量）** 640 循环，ground 156。锈红船舱走廊（货轮配色 (122,74,56)）、水管、带转轮的舱门、铁笼灯 + `_glow`、`_container`；变体 `flesh=0..1`：用 `A._fbm_wrap(640, 180, 32, seed)` 阈值出血管纹，墙面按 flesh 往肉粉色混（猩猩的替身就是整艘船）。

**⑨ brain_inside（恋人·微观战）** 单屏或 640。粉红有机隧道：渐变 [(90,20,40),(160,50,70),(220,120,130)]；神经元 = 软团 + `A._bolt` 画的分叉树突（淡粉）；地面是波动的膜（照 `_desert_near` 403 行的起伏上沿）。动：整体随心跳 `sin` 调色、电信号光点沿树突跑、细胞上下浮（抄 `dream_carnival` 玩具浮动 1297–1305）。花京院和波鲁纳雷夫缩小后在乔瑟夫脑里打，很有“战斗爽”的看点。

**⑩ nile_bank（阿努比斯：恰卡、理发师凯恩）** 640 循环，ground 152。天空 + 对岸绿带 + `_tiny_palm`；河面 y 100–130：闪光照 `island_beach` 1389–1397，白帆船照 1385–1387 放大；近岸芦苇、泥滩、`E._palm`；一个露天理发摊（椅子 + 镜子 + 遮阳布）。

**⑪ egypt_rail（芭丝特女神·玛丽亚）** 640 循环，ground 152。沙丘 `E._desert_far('day')` + `_desert_mid`；车站站台（混凝土板 y 140–150）+ 站房（`E._house` 画法 + 招牌）；铁轨两条 + 每 6 px 一根枕木（y 160–176）；**电塔**：抄 `_poles`（E:712）的结构，杆子换成 X 形格构塔，k 0.55。磁力梗（被吸到电塔上）直接在电塔坐标上演。

**⑫ 白天开罗街（荷鲁斯神·宠物店）**：几乎不用画——`E._street_day(seed=121)` 返回的就是未调色的白天楼面条（960 周期，带窗户矩形表）；天空用 `E._TOD['day']['sky']`；`_street_far` 只有 night / dawn / sunrise 配色 → 导出脚本里自己调 `_wrapped(640, 130, lambda img, d, ox: E._skyline(d, ox, 640, 126, 141, (196,186,176,255), 14, 44, minaret_p=0.3, dome_p=0.25))`；`_street_ground` 同理配一套白天色（人行道 (206,190,170)、路面 (110,104,110)、碎石 (90,86,96)），照抄 2809–2831 行的画法即可。

**⑬ mansion_corridor（克林姆·瓦尼拉、肯尼·G 幻象）** 640 循环，ground 154。拆 `_hall_static`（E:2223）的零件：石块墙 + 护墙 + 柱子（每 160 一根，带烛台）+ 画像 + 红地毯 + 透视棋盘地面，`_gothic_window` 窗。克林姆打洞直接复用 `E._breach_img(r)`（r 2..30 各导一张）。幻象版（P2）：整层水平翻转 + 色调偏紫 + 走到尽头无缝回到开头。

### P2（锦上添花，一句话）

- 成田机场：导出 `airport` 时把 3 棵棕榈的区域用航站楼 / 天空的像素盖掉（导出脚本里改图，不动源码）。
- 校内石阶 / 保健室：保健室照 kujo_bedroom 写法（白墙、两张病床、拉帘、药柜）。
- mountain_road（命运之车）：`desert_highway` 的 `_mesas` 换成 `_dunes_img` 灰绿配色、hmin/hmax 加大当山，加悬崖前景。
- 恩雅旅馆内景：fog_town 配色的室内（木墙、吊灯、壁炉）。
- 卡拉奇 / 瓦拉纳西街：`A._grade(near, sat=0.7, tint=(220,190,140), tint_amt=0.25)` 给 calcutta 的 near 层调成沙尘色。
- 阿联酋小镇 / 绿洲：egypt_town 换 seed + 棕榈 + 骆驼（`prop.camel`）。
- 小飞机机舱（死神13）：plane_cabin_side 缩成 2 排座位。
- 开罗桥 / 尼罗河夜景：cairo_street 的 far 天际线 + 钢桁架桥 + 河面倒影（hongkong 倒影算法）。

---

## 7. 导出成游戏地图的方案

### 7.1 先定画布尺寸（需要总负责人拍板）

- JoJo 背景、角色（44–46 px 高）、UI（640×360 = ×2）全部以 **320×180** 为基准。银魂游戏是 384×216。
- **建议新游戏 `G.W = 320, G.H = 180`**，CSS 放大 ×4（1280×720）或 ×6（1920×1080），整数倍最近邻，画面和原片完全一致。
- 如果坚持 384×216：14 个横卷背景横向不成问题（层本来就比 320 宽），但高度只有 180，上面要补 36 px 天空或下面补地面；19 个单屏背景的坐标全是写死的（`_JBW`、`_TABLE`、`_PILLARS`、楼梯 `_ST_*`……），都要重画。不划算。
- 银魂引擎里写死 384 / 216 的地方要改成读 `G.W / G.H`（例如 `gfx.js` 的 `terminal` 层用了 192、150，`world.js` 的默认 `yMin = 158`、`yMax = 198`）。

### 7.2 三种导出方式，按背景选

| 方式 | 做法 | 适用 |
|---|---|---|
| A. 分层导出 | 调私有建图函数拿到每一层 PIL 图 → 裁到一个周期 → 存 PNG；JS 用 `wrap` 层按 k 拼；会动的小东西在 JS 里重写 | 全部 14 个横卷背景 |
| B. 静态底图 + JS 动画 | 导出 `_xxx_static()` 那张底图（1 张 PNG），灯光闪烁、风铃、蝙蝠、烛火、烟这些少量动画在 JS 里照 Python 公式重写；前景覆盖层另导一张 | 大多数单屏房间 |
| C. 烘焙帧循环 | Python 按固定 fps 渲 N 帧（只渲会动的那一块），存成横向帧条，JS 按时间取帧 | 逐像素运算重的：sea_storm_night 的浪、ship_hold 的油灯光照、dream_carnival 的旋涡天空 / 棋盘地、game_room 的 CRT 画面、jail_bars 的弯曲 |

体积：实测导出的层 PNG 1–9 KB / 张（例如埃及小镇 far 1.4 KB、房子 8.7 KB、地面 1.3 KB），单屏底图 25–55 KB / 张；全套估计 3–5 MB，`file://` 用 `<img>` 加载没问题（银魂就是这么做的）。

### 7.3 导出脚本放哪、怎么写

- 新建 `D:\大疆\游戏素材\JoJo\游戏\tools\build_bg.py`（或在将来的 `build_assets.py` 里加 `build_bg()`），输出到 `游戏\assets\bg\<地图id>\*.png`，元数据写进 `data.js` 的 `G.D.bg[<id>]`（照银魂 `build_assets.py:143 build_bg()` 的格式：`stages[...] = dict(layers=[...])` → `save_meta("bg", stages)`）。
- 脚本头：

```python
import os, sys
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True
SRC = r'D:\大疆\游戏素材\JoJo\源码'
sys.path.insert(0, SRC)
from engine.core import Frame, W, H
from engine import bg, bg_asia as A, bg_egypt as E
# 用到场景里自绘的背景（s05 dusk_gate 等）时，先 import assets; assets.load_all()，否则场景模块 import 时找不到精灵会报错

def crop_period(im, P):            # bg_egypt 的 _wrapped 图宽 = P + 320；裁成一个周期，或整张原样导出也行
    return im.crop((0, 0, P, im.height))
```

- 每个横卷背景要导出的层（调用 → 周期 / k / y）。**JS 里每层的偏移 `o = floor(camX·k + t·vx) mod P`**，和银魂 `gfx.js:239` 的 `wrap` 层同一个公式：

| 地图 | 层（调用） | P | k | y | 备注 |
|---|---|---|---|---|---|
| hongkong_night | sky = `A._hk_layers()[0]` | — | 0 | 0 | 静态 |
| | far = `[1]` / mid = `[2]` / near = `[3]` | 640 | 0.25 / 0.6 / 1 | 0 | far 另有 vx = 0.5 |
| | 17 块亮霓虹 `A._neon_sign(kind, n, ci, sd, True)` | — | 1 | — | 世界坐标 x = `sx − pad`，y = `sy − pad`（pad 大 7 / 小 5），表 `A._HK_SIGNS` 2835；flicker 那 5 块在 JS 里随机闪 |
| | 倒影 | — | — | 153 | 用银魂已有的 `reflect` 层（base 152，n 27，alpha 0.62→0.27） |
| calcutta_street | sky / far / near = `A._calcutta_layers()` | 640 | 0 / 0.4 / 1 | 0 | 出租车 `_ambassador` 画进 52×32 透明图当道具 |
| school_gate | far / near = `A._school_layers()` | 不循环 400 / 480 | 0.5 / 1 | 0 | 地图 x0 = 0，x1 = 480 |
| sky_day | grad = `A._sky_grad('day')`；`A._sky_layers()` 返回顺序是 [far, mid, near, sea] | far 640 / mid 640 / near 960 / sea 640 | 0.15 / 0.4 / 1 / 0.7 | 0 | 画序 far → mid → sea → near；每层 vx = speed·k（原式 `(scroll + t·speed)·k`） |
| underwater | base / far / bed = `A._uw_layers()` | 640 | 0 / 0.35 / 1 | 0 | far vx 1.5 |
| train_interior | sky / hills / mid / near = `A._train_scenery()`；盖 `A._train_static()` | 640 | 镜头不动 | 0 | 每层 vx = speed·k（k 0.08 / 0.35 / 1）；电线杆 k 1.6、周期 600 |
| plane_cabin | 窗外 `A._cabin_sky()`；盖 `A._cabin_static()[0]` | 640 | — | 0 | 左半屏往一个方向卷、右半屏反方向（x < 160 裁切） |
| desert（每个时段） | 天空 + 日月：新 Frame 上调 `E._sky_and_sun(fr, time)` 截图；far `E._desert_far(time)`；mid `E._desert_mid(time)`；near `E._desert_near(time)[0]` | 640 | 0.12 / 0.4 / 1 | 66 / 90 / 133 | 换 seed 就是另一片沙漠 |
| pyramids | far `E._desert_far(t, seed=5)`；`E._pyramid_layer(t)`；mid `E._desert_mid(t, seed=13)`；near `E._desert_near(t, seed=17)[0]` | 640 | 0.05 / 0.1 / 0.4 / 1 | 76 / 18 / 82 / 133 | 狮身人面像 `E._sphinx_img(t)` 单个道具：世界 x 22、k 0.4、脚线 132 |
| desert_highway | `E._mesas()`；far（seed 9）；mid（seed 19）；`E._poles()`；`E._road_static()`；`E._road_marks()` | 640 / 640 / 640 / 480 / — / 480 | 0.03 / 0.08 / 0.2 / 0.55 / 0 / 1 | 84 / 78 / 72 / 58 / 0 / 0 | 自动卷：每层 vx = 360·k |
| egypt_town | `E._town_far(seed=9)`；`E._town_layers(seed=5)`；`E._town_ground(seed=5)` | 640 | 0.3 / 1 / 1 | 0 / 0 / 140 | 已验证与原函数逐像素一致 |
| cairo_rooftops | `E._roof_far()`；`E._roof_mid()`；`E._roof_near()` | 640 | 0.1 / 0.35 / 1 | 0 | 钟楼（世界 x 252，k 0.35，底 136）、水塔（世界 x 58，k 1，底 146）当单独道具 |
| cairo_street（每个时段） | `E._street_far(time)`；`E._street_graded(time)`；`E._street_ground(time)` | 640 / 960 / 480 | 0.3 / 1 / 1 | 0 | 路灯世界 x = 40 + 160n；光晕 `_glow_at` 两个（(x,106) r30×26、(x,150) r26×5，夜 0.32 / 黎明 0.18） |
| sunset_walk | 天空截图；`E._sunset_far()`；`E._sunset_ridge()[0]` | 640 | 0 / 0.3 / 1 | 0 / 90 / 120 | 落日 + 云带在 JS 画 |

- 单屏背景要导出的：`A._jail_static()`、`A._bars_layer(bq, 6, 314, 160, 0, 146)`（bq 取 0、10、20…50 共 6 张，或全 51 张）、`A._kujo_static(v)` ×4、`A._bedroom_static(v)` ×4、`A._hk_garden_static(night)` ×2、`A._freighter_static()`、`A._alley_static()`、`A._hold_layers()[0]`（未打光的底色数组）+ 光照烘焙帧、`E._fog_town_static()` + 4 条雾 `E._fog_tex(640, h, seed, col, alpha, 3, 6, thick)`、`E._carnival_static()` + `E._carnival_sky(0..11)` + 棋盘 48 帧、`E._beach_static(v)` ×2 + 棕榈 `E._palm_img(h, lean, frame, 'day', flen, seed)` 每棵 4 帧、`E._cafe_static()` + 前景 `E._cafe_table_img()`、`E._game_static()` + CRT 画面帧、`E._mansion_img(time)`（图 + 窗户表）+ `E._mansion_ground(time)`、`E._hall_static()` + `E._breach_img(r)`、`E._stairs_static()` + 前景 `E._rail_img()`、`E._airport_static()`、`E._street_end_static(time)`、地图 `A._map_layer(0/1)`。
- 锚点（门、桌子、镜子框、水箱框、台阶……）原样写进地图 JSON，给剧情 / 互动热点 / 战斗机关用。

### 7.4 地图 JSON 例子（沿用银魂的 Stage / Background 结构）

```js
G.D.bg.cairo_night = {
  layers: [
    { type: 'static', image: 'assets/bg/cairo_night/sky.png' },               // 天空 + 月亮 + 星（星星闪烁另加）
    { type: 'wrap', image: 'assets/bg/cairo_night/far.png',  period: 640, k: 0.3, y: 0 },
    { type: 'wrap', image: 'assets/bg/cairo_night/bldg.png', period: 960, k: 1,   y: 0 },
    { type: 'wrap', image: 'assets/bg/cairo_night/road.png', period: 480, k: 1,   y: 0 },
    { type: 'lamps', xs: [40, 200, 360, 520, 680, 840], period: 960, glow: 'assets/bg/cairo_night/lamp_glow.png' },  // 新层类型
  ],
  fg: [],
  ground: 160,
};
G.STAGES.cairo_ch20 = { id: 'cairo_ch20', bg: 'cairo_night', x0: 0, x1: 1920, yMin: 150, yMax: 176 };
```

银魂 `gfx.js` 现成能直接用的层类型：`static`、`wrap`（带 k、vx、blend）、`image`（单个道具，带 k、flicker）、`glow`（相加光晕）、`reflect`（湿路面倒影）、`tint`（整屏罩色）、`clouds`、`birds`、`gulls`、`dust`、`shaftmotes`、`mlines`。要新加的：`frames`（烘焙帧条按 fps 播放）、`neon`（亮版贴图 + 闪烁）、`lamps`（周期性路灯 + 光晕）、`palms`（4 帧摇摆）、`fog`（雾纹理按速度卷）、`waves` / `shore`（如果不烘焙）。

### 7.5 地图宽度、重复与种子

- 周期就是“多宽开始重复”：香港 / 加尔各答 / 埃及小镇 / 沙漠 / 屋顶 640，开罗街 960。地图宽度建议 ≤ 周期的 1.5–2 倍，再宽就能看出重复（17 块霓虹、同一排楼）。
- 要更长又不重复，导出脚本在**独立进程**里先改模块常量再调建图函数（lru 缓存这时还是空的），不用改源码。已实测（`wide_period.py`，出图 `wide\`、`_wide.png`）：
  - `E._TOWN_P = 1600` → `E._town_layers(seed=5)` 1920 宽（周期 1600），房子不重复；
  - `E._ST_P = 1920` → `E._street_day()` 2240 宽（周期 1920，239 个窗户）；路灯 `_LAMPS_X` 是固定的 6 个，宽了以后要在 JSON 里自己补；
  - `A._CA_W = 1280` → 加尔各答 near 1280 宽，但**电线（6 条，每条间隔 110）和晾衣绳（5 条，间隔 128）只画在前 640**，导出脚本要在后半段补画同样的线；
  - `A._HK_W` 改宽同理：楼面会接着生成，但 17 块灯箱和 4 条小巷只在前 640，要自己补。
- 种子：`E._town_layers(seed)`、`_town_plan(seed)`、`_town_far(seed)`、`_town_ground(seed)`、`_desert_far(time, seed)`、`_desert_mid(time, seed)`、`_desert_near(time, top, seed)`、`_street_day(seed)` 都带 seed。建议阿斯旺 seed 5、卢克索 6、埃德富 / 玛丽亚小镇 11（`wide\egypt_town_seed6.png`、`seed11.png` 看过了，风格一致、房子不同）。bg_asia 的建图函数**没有 seed 参数**（种子写死），要变样只能调色或在导出时补画。
- 单屏房间做“可走动区域”的办法：不硬拉宽，而是**多屏用门连起来**（银魂的地图切换）。例如空条家：kujo_house（客厅）↔ kujo_bedroom ↔ s05 dusk_gate（门外 460 宽），不用画新图就是一个能逛的小区域；DIO 宅邸：mansion_exterior → mansion_corridor（新）→ mansion_hall → mansion_stairs。

### 7.6 每个背景要在 JS 里重写的动画（照 Python 公式）

- 香港：亮霓虹 5 块闪（10 fps：12% 灭一帧，另 15% 概率进入隔帧闪）；天线红灯 `int(t·1.5) % 2`；倒影逐行晃 `round(1.8·sin(r·1.3 + 6t)·(0.3 + r/27))`；路面黄线每 40 px（y 170，长 16）。
- 加尔各答：10 粒灰尘（往右上漂）；出租车可做成会开的道具。
- 校门：26 片花瓣（周期 4–7 s，从上往左下飘，`sin(2.3t + i)·6` 左右摆）。
- 和室 / 卧室：晨昏光束 alpha `la·(0.85 + 0.15·sin(0.8t))`；风铃摆角 `0.25·sin(2.1t) + 0.1·sin(3.7t + 1)`；乌鸦 / 落叶；行灯闪 `0.85 + 0.15·noise1(3t)`；窗下灰尘 8 粒。
- 拘留所：灯泡 12 fps 下 4% 概率暗到 0.55；收音机 LED 1 Hz。
- 货舱：油灯（建议烘焙 44 帧 = 一个摆动周期 3.696 s @12 fps）。
- 海：sea_day 22 行浪花（8 fps 跳帧，`per = 18 + 3·row`，`ln = 2 + row//3`）+ 36 个闪光；暴风浪建议烘焙 48 帧（4 s @12 fps，只渲 y 92–180 那一块），闪电用调色板插值（两套 11 色在 1208–1215 行）+ `_bolt` 现画。
- 海底：水面波纹、6 道光柱 alpha `22 + 18·(0.5 + 0.5·sin(1.3t + 1.7i))`、9 条鱼、10 根海草（`sin(1.6t + i + 0.12k)·(k/h)·6`）、16 个气泡。
- 火车：窗外 3 层自动卷 + 电线杆 + 每 1.25 s 颠 1 px + 两个吊扇（20 rad/s，3 叶，叶长 14）。
- 沙漠：云漂（1.5 px/s 量级）、鸟；正午逐行热浪 `round(sin(0.85y + 7t)·(0.5 + 0.5·sin(0.23y − 2.1t)))`（y 90–132）+ 秃鹫绕 (150,38) 转（半径 26×6，0.6 rad/s）。
- 雾之镇：3 条雾带速度 3 / 5 / −7、前景雾 9；窗户随机灭；路灯闪 `0.3 + 0.12·sin(13t + 2i)`。
- 梦境：天空 12 相位（`int(4t) % 12`，4 fps，3 s 一圈）、棋盘 48 相位（`(0.9t) mod 2`，约 2.2 s 一圈）、摩天轮（中心 (70,84)、R 38、0.35 rad/s、16 灯每 6 fps 追一格）、6 个玩具浮动。
- 海滩：海岸线逐列涨退（`134 + 2·sin(1.1t)` 加两个空间 sin）、46 个闪光、浪线、棕榈 4 帧、螃蟹。
- 咖啡馆：光锥 alpha 抖（`0.03·sin(9t) + 0.02·sin(23t)`）、吊扇（7 rad/s）、两股烟（22 点/股，往上 70 px）。
- 游戏室：CRT 光晕 `0.28 + 0.05·sin(17t) + 0.03·sin(41t)`、屏幕赛车（烘焙）、街机闪。
- 宅邸外：窗户闪、门口光、9 只蝙蝠绕 (70,40) / (236,34)。宅邸厅：4 支蜡烛、破洞 r = 30·breach、阳光柱 alpha 110·beam + 24 粒灰尘。楼梯：3 支蜡烛。
- 屋顶：星星闪（12 颗）、钟面。开罗街：路灯光晕微闪 `+0.03·sin(7t + i)`；日出 `rise` 控制太阳高度 `118 − 100·rise`。
- 机场：远处起飞小飞机、热浪、塔台灯。片尾：5 条云带、4 只鸟。
- 原片里会动的随机数都来自 `core.hash01`（165 行，FNV 式散列）。JS 不需要逐位复刻：**静态的随机位置在 Python 里算好写进 JSON**，只有时间相关的闪烁在 JS 里用自己的伪随机就行。

### 7.7 镜头方向统一

- JS 里统一：世界坐标 x 向右为正，镜头 camX 向右为正，每层 `o = floor(camX·k) mod P`。
- 导出的层就是“全景图”本身，在 JS 里不分 bg_asia / bg_egypt，一律用上面的公式。逐帧的东西（霓虹、出租车、海草、路灯）一律按**全景里的世界坐标**放 → 自动和图层对齐，顺带修好了原片 scroll≠0 时霓虹错位的 bug。
- 验证脚本对 bg_asia 要用 `scroll = −camX` 调原函数来比（1.3 节已验证一致），bg_egypt 用 `scroll = camX`。

### 7.8 前景覆盖层（画在角色前面）

放进地图的 `fg` 列表：`jail_bars`（随剧情 bend 变，按帧条取）、`cafe_table`（桌子）、`stairs_rail`（扶手）、`fog_front`（低雾，`amount` 控制 alpha）、`freighter_rail`（最下方栏杆）、`sea_storm_front`（最近一层浪）。注意银魂 `Background.drawFg` 默认给前景 0.5 透明度（`gfx.js:213`），这几个要设 `alpha: 1`（雾按 0.47 左右，原式 `120·amount/255`）。

### 7.9 导出自检

照 `export_proto.py` 的做法，每个横卷背景在 3–5 个镜头位置把“导出层重建”和“原函数输出”逐像素比较，只比没有逐帧动画的那几行（例如 egypt_town 比 y 62–180，避开云和鸟）。实测 egypt_town 5 个位置 0 像素不同；calcutta 全帧只差 10 个灰尘像素。把这个比较写进 `build_bg.py` 末尾，导出出错一眼就能发现。

---

## 8. 坑 / 风险

1. **画布尺寸**（7.1）：384×216 会让所有单屏背景重画，强烈建议 320×180。
2. **bg_asia 卷动方向反了**（1.3）：直接照抄原片的 scroll 数值复刻镜头会方向相反；香港霓虹错位是原片 bug，不要当“设计”照搬。
3. **文档和代码不一致**：BG_asia.md 说 sky_day 的云往左漂，实际往右；freighter_deck 的 docstring 说吊钩会晃，实际不动；bg.py 提到的 `docs/BG.md`、bg_asia 提到的 `cabin_seats_front` 都不存在。以代码为准。
4. **单个道具不循环**：pyramids 的狮身人面像、cairo_rooftops 的钟楼 / 水塔、school_gate 整张图都**不循环**，地图做宽了它们只出现一次（这反而是想要的地标效果，但要记得在 JSON 里当道具放）。
5. **egypt_town 的棕榈不摇**（图层里烘的是第 0 帧）；想要摇就把棕榈从房子层拆出来单独导 4 帧（`_town_layers` 里 `draw_palms` 的位置算法照抄）。
6. **改模块常量拉长周期**时，写死数量的装饰（加尔各答电线 / 晾衣绳、香港灯箱 / 小巷、开罗路灯）只覆盖前一个原周期，要导出脚本补。
7. **调用场景里自绘的背景**（s05 dusk_gate 等）要先 `import assets; assets.load_all()`，否则场景模块 import 时 `KeyError: unknown sprite 'joseph.idle'`（试跑踩过）。
8. **plane_cabin 是透视图**，横版走位用不了；灰塔战要么画侧视客舱，要么把它当只能在过道里躲闪的特殊竞技场。
9. **逐像素重的背景**（暴风浪、货舱光照、梦境天空）不要在 JS 里每帧硬算，先烘焙帧条；烘焙会有循环接缝（浪本身不是周期运动），4 s 循环在乱浪里基本看不出来。
10. 原片好几处背景是**时段调色**出来的（kujo 的 `_KJ`、开罗街的 `_GRADE`）。要给埃及小镇等做夜景，直接拿 `_GRADE['night']` 的乘数 (0.26,0.28,0.50) + 加数 (6,6,20) 调色再随机点亮窗户，风格和原片统一。
11. 缺口里的 P0 五张（酒店、新加坡街、恒河、潜艇、神殿）没有原片参考画面，需要按原作印象画；神殿原型已证明“借原工程辅助函数 + 3 层 640 循环”这条路走得通，大约 100–200 行 / 张。

---

## 9. 试跑记录（都在 scratchpad，没有写进项目）

目录：`C:\Users\yui\AppData\Local\Temp\claude\D----\dd592801-8a86-495b-83a0-71d863169d18\scratchpad\understand\bg06\`

| 文件 | 做了什么 / 看什么 |
|---|---|
| `render_all.py` → `_sheet_all.png`、每个背景一张 `<name>.png`、`_report.json` | 33 个背景 t=1.0 各渲一张，记尺寸 / 首次与每帧耗时 / 返回值 |
| `probe_layers.py` → `strips\*.png`、`_strips_a.png`、`_strips_b.png` | 打印所有缓存层的尺寸；scroll 0/320/640/960 四帧横拼（近景连续、远景和天空当然不连续）；循环自检（埃及小镇 / 开罗街 / 加尔各答 / 沙漠按周期 diff = 0） |
| `export_proto.py` → `export_proto\` | 分层导出原型 + JS 公式重建 + 逐像素比较（egypt_town 0 差异；calcutta 只差灰尘） |
| `scroll_dir.py` → `hk_neon_scroll0/100.png`、`calc_taxi_scroll0/100.png` | 量各背景卷动方向；霓虹错位截图 |
| `asia_dir_check.py` | bg_asia 用 `scroll = −camX` 调原函数 vs JS 公式重建：camX 0/250/900/1235 都只差 10 个灰尘像素 |
| `scene_bgs.py` → `variants\_sheet_variants.png` | s05 dusk_gate（scroll 0 / 200）、s06 驾驶舱、s16 血红天空、各背景的时段 / 变体 / 覆盖层 |
| `wide_period.py` → `wide\*.png`、`_wide.png` | 改模块常量拉长周期（1600 埃及小镇、1920 开罗街、1280 加尔各答）+ 换 seed |
| `proto_temple.py` → `proto\egypt_temple_proto.png` | 缺口 P0 神殿柱厅的原型（3 层 640 循环） |

跑法：`cd <上面目录>`，`PYTHONDONTWRITEBYTECODE=1 python <脚本>.py`（脚本里也设了 `sys.dont_write_bytecode = True`，路径用 `sys.path.insert(0, r'D:\大疆\游戏素材\JoJo\源码')`）。
