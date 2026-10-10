# 08 JoJo 角色画法：精灵骨架、补帧、画新角色、烘焙到游戏图集

> 调研范围：`源码\engine\sprite.py`、`源码\assets\sprites_*.py`（jojo / crew / stands / dio / enemies / props）、`源码\CATALOG.md`、`源码\STYLE.md`、`烘焙脚本\bake_characters.py`、`角色图集\README.md`、`角色图集\catalog.json`、`角色图集\场景专用\场景专用目录.json`。
> 本轮只读。原型代码与预览图都在会话 scratchpad：`C:\Users\yui\AppData\Local\Temp\claude\D----\dd592801-8a86-495b-83a0-71d863169d18\scratchpad\understand\cv_*.py / cv_*.png`（临时目录，可能被清掉，关键代码已抄进本文第 6、7 节）。
> 文中 `SJ` = `assets.sprites_jojo`，`sc` = `assets.sprites_crew`，`SS` = `assets.sprites_stands`，`SE` = `assets.sprites_enemies`，`SD` = `assets.sprites_dio`。

---

## 0. 结论速览

1. **一帧 = 一段 ASCII 字符网格**（一字符一像素，`.` 透明），字符经调色板（全局 `PAL` + 每个精灵自己的 `pal` 覆盖）映射成颜色，`sprite.define(name, [帧...], pal, anchor, desc, fps)` 注册进全局表 `_REG`。所有帧朝右，默认锚点 `mb` = 脚底中点。
2. **没有统一的“骨架”**：6 个素材模块各写了一套自己的小工具，任务里说的“G 类”只存在于 `sprites_jojo.py`（承太郎 / 乔瑟夫 / 荷莉）。其余：`sprites_crew` 用 numpy 字符数组 + `compose()`；`sprites_dio` 用字符串网格 + 每个部件自动描边；`sprites_stands` 用 `_Pix` 画笔（形状遮罩→自动三阶明暗→自动描边）+ **姿势表**；`sprites_enemies` 用另一个同名但不同的 `_Pix`（矩形/椭圆/粗线 + `shade()`）。补帧时**必须用该角色原来那套工具**，才能保证同画风。
3. **不改源码就能补帧**：新建自己的 `.py`，`sys.path` 指向 `源码`，`from assets import sprites_jojo as SJ` 之类直接拿原模块里的部件、调色板、组装函数（模块级函数和常量都能 import），调用 `sprite.define()` / `sc.define()` / `SS._register()` 注册新名字（如 `jotaro.punch`）。原工程的场景脚本 `scenes\s07_polnareff.py:74`、`s13_vanilla.py:93`、`s19_revival.py:264` 就是这么干的，有先例。
4. **已实测可行**：用原骨架给承太郎补了 `punch`(2 帧) / `guard` / `dodge` / `down`，给白金之星补了 `upper` / `hurt`，给花京院补了 `dodge`、波鲁纳雷夫补了 `down`，4 倍预览自查同画风；再用 `bake_characters.py` 的函数把它们烘焙成与 `角色图集` 同格式的图集，**回读逐像素校验 97 帧 0 错误、与原引擎 `sprite.draw` 比对 168 次（含翻转）0 不一致**；源码目录没有留下 `__pycache__`。
5. **工作量**：已有部件重新摆姿势的帧 ≈ 5–15 分钟/帧（第一次渲染基本就对，最多改一次坐标）；要画新部件的帧（倒地躯干、新手臂网格）≈ 20–40 分钟/帧；一个新人类角色全套（调色板 + 头/躯干/四肢部件 + idle/walk/攻击/受击/倒地 + 头像）≈ 3–5 小时；一个人形替身走 `_brute_frame` 规格表 ≈ 2–3 小时；非人形替身 1–3 小时。见第 8 节。
6. **最大缺口**：主角团本体缺 出招指令 / 格挡 / 闪避（花京院、阿布德尔、波鲁纳雷夫、乔瑟夫、伊奇都缺），倒地缺 承太郎 / 波鲁纳雷夫（乔瑟夫是 `lie`，头朝右）；主角团替身除白金之星外每个只有 2 个动作；**敌人方 27 个角色/替身里 20 个只有 1 个非头像动作（基本就是 idle）**；第三部还有十几个替身使者**完全没画**（黄色节制、女帝、乌木恶魔、阿努比斯、次中音萨克斯、塞特神、奥西里斯、阿图姆、恋人的替身本体，以及灰塔/暗蓝之月/命运之轮/死神13/审判/女教皇的使用者等）。

---

## 1. 引擎层：`源码\engine\sprite.py`（385 行）——“一帧”是什么

| 位置 | 内容 |
|---|---|
| `PAL` 22–64 | 全局调色板，42 个字符。必记：`k #1a1020` **描边（近黑紫，不是纯黑）**、`K #000000`、`w #ffffff`、`W #efe6d2`、`1/2/3` 三级灰、`s #f6c49a / S #d8946c` 肤色/肤影、`d/D` 深肤色（阿布德尔、恩多尔）、`r/R` 红、`o/O` 橙、`y/Y` 黄/金、`g/G` 绿、`l` 浅绿、`c/C` 青、`b/B` 蓝/藏青、`u/U` 浅蓝、`p/P` 紫、`v/V` 白金之星紫肤、`m/M` 品红、`h/H` 棕（头发/木/皮）、`t/T` 卡其、`z/Z` 银、`f` 腮红/唇、`e` 瞳孔。`.` 和空格 = 透明。 |
| `_parse` 83–104 | 网格字符串 → RGBA：`textwrap.dedent`、去尾空行；**遇到调色板里没有的字符直接 `KeyError`**。也接受 PIL 图（直接 `convert('RGBA')`），所以可以把后处理过的 PIL 图注册成精灵（`s13_vanilla._pol_kick` 就是这样）。 |
| `define` 107–129 | `define(name, frames, pal=None, anchor='mb', desc='', fps=None)`：`p = dict(PAL); p.update(pal)`；**同一精灵各帧尺寸不同时按左下角对齐补齐**到最大宽高（所以不同尺寸的帧要么统一画布，要么用显式锚点）；**同名再 define 会直接覆盖**原精灵并清缓存。 |
| `_anchor_px` 160–165 | 锚点：`'mb'` 底边中点（默认，脚点）、`'mm'` 中心、`'lm'` 左中、`'lt'` 左上，或 `(ax, ay)` 像素坐标。奇数宽的 `mb` 会得到 `.5`。 |
| `_variant` 211–239 / `render` 242 / `draw` 252–265 | 运行时变体（`lru_cache` 4096）：`flip`（绕锚点 x 翻）、`scale`（最近邻）、`tint`（`'white'/'black'/'gray'/'invert'/颜色` + `amt`）、`rot`（绕锚点旋转，最近邻）、`outline`（外扩 1px 某色描边，画布 +2）。**这些都不在图集里，游戏 JS 要自己实现**：受击闪白 = `tint='white'`，替身光边 = `outline=颜色`。 |
| `aura` 268–285 | 替身光环：剪影向外膨胀 `grow` 像素、填 `colour`、按 `sin(t*23)`/`cos(t*17)` 抖 ±1px、`alpha=0.55`，先画光环再画本体（替身本体常用 `alpha≈0.9`）。 |
| `sheet` 288 | 联系表（`tools/spritesheet.py` 用）。**注意 `tools/spritesheet.py` 会把图写到 `源码\out\sheets\`，不要跑**；要看图就在自己脚本里调 `sprite.sheet(prefix)` 存到别处。 |
| `g_lines / g_stamp / g_shift / g_pad / g_flip / g_recolor` 329–385 | 字符串网格小工具：`g_lines` 把空格换成 `.` 并补齐宽度；`g_stamp(base, part, x, y)` 以 part 左上角盖到 (x,y)，`.` 透明、出界裁掉；`g_recolor(grid, {'r':'b'})` 换字符（换色 = 换字母）。 |

**一帧的完整生命周期**：部件网格（字符串/数组）→ 组装函数按坐标盖章（后盖的在前面）→ 盖“在前面”的部件时在重叠处画 1px 分隔线 → 整张剪影外围自动加 1px `k` 描边 → `define()` 用 `pal` 映射成 RGBA → `draw()` 在 (x, y) 按锚点贴图。

---

## 2. 六个模块、五套骨架（补哪个角色就用哪套）

| 模块 | 角色 | 骨架 | 组装入口 | 姿势怎么表达 |
|---|---|---|---|---|
| `sprites_jojo.py` (1319 行) | 承太郎、乔瑟夫、荷莉 | `class G`（可变字符网格） | `j_frame()` 366 / `jo_frame()` 753 / `h_frame()` 1073 | **关节坐标**：腿 `[(髋),(膝),(踝),'flat'/'toe'/'toeb']`、手臂 `dict(pts=[(肩),(肘),(手)], hand=手型网格, cols=袖子色带)`、`k` 前后倾、`dy` 上下 |
| `sprites_crew.py` (2057 行) | 阿布德尔、花京院、波鲁纳雷夫、伊奇 | numpy `'<U1'` 字符数组：`G(s)` 14、`put()` 34、`compose()` 80、`fit()` 94、`define()` 114 | `_av()` 465 / `_ka()` 947 / `_po()` 1399 / `_ig()` 1616 | **预画好的部件网格**（`AV_ARM_F_CAST`、`KA_LEGS_STRIDE_A`…）+ 摆放坐标 |
| `sprites_dio.py` (1558 行) | DIO、瓦尼拉、奶油、佩特夏普、达比、泰伦斯、恩多尔、盖布、僵尸 | 字符串网格：`_ol()` 12（每个部件先加描边）、`_st()` 32、`_compose()` 39、`_shear()` 50 | `_dio_idle/_walk/_pose/_laugh/_throw/_jump/_hurt` 314–462 | 部件 + `_leg(kind)` 261 用**按行错位**生成各种腿（`stand/out_l/out_r/fwd/back/stride_*/wide_*/lift/tuck`），`FAR` 104 换色表把远侧肢体整体压暗 |
| `sprites_stands.py` (1580 行) | 白金之星、世界、红色魔术师、绿色法皇、银色战车、愚者、隐者之紫藤蔓 | `_Pix` 62（形状遮罩画笔：`ell/cap/poly/rect/lmask` → `paint(mask, tones)` 自动三阶明暗 + 外描边） | `_brute_frame(spec, pose, ph, bob)` 473（白金/世界/红魔共用）、`_hg_frame` 1122、`_ch_frame` 1280、`_fool_frame` 1454 | **姿势表**：`SP_POSES` 419、`TW_POSES` 701、`MR_POSES` 1047、`HG_ARMS` 1201、`CH_POSES` 1355 |
| `sprites_enemies.py` (1805 行) | 荷尔荷斯、J·凯尔、倒吊人、恩雅、正义、奥因哥/波因哥、灰塔、力量、暗蓝之月、死神13、审判、斯蒂利丹、命运之轮、女教皇、玛丽亚、阿莱西 | 另一个 `_Pix` 30（`rect/ell/poly/line/seg/dot/stamp/paste(ring)/shade/outline`） | 每个角色一个函数 `_hol_body(pose, frame, w)` 258、`_geil(frame, hurt)` 505、`_strength(frame)` 1187 … | 函数内部写死坐标，只有 `frame` / 少数开关参数 |
| `sprites_props.py` | `prop.*` 35 个道具 | `Cv` 62 | — | 不是角色，略 |

### 2.1 `sprites_jojo.py`：`class G`（任务里说的“G 类”）

`class G` 24–137，`G(w, h)` 建一张全 `.` 的网格，方法都返回 self 可链式：

| 方法 | 行 | 作用 |
|---|---|---|
| `_apply(pix, sep)` | 38–53 | 写入像素字典。**分隔线**：`sep` 不为空时，先找新形状的 4 邻域外圈，凡外圈落在**已经不透明**的像素上就涂成 `sep`，再写新形状 → 前面的部件和后面的部件之间自动出现 1px 线。 |
| `stamp(part, x, y, sep=None, flip=False)` | 55 | 盖章一个字符串部件（`.` 透明）。 |
| `limb(p0, p1, cols, sep=None)` | 66–87 | 粗直线肢体，`cols` = 横截面的颜色带：竖向肢体从左到右（如 `'qnnN'` = 高光/底色/底色/阴影），横向肢体从上到下。宽度 = `len(cols)`。 |
| `poly(pts, fill, left, right, bottom, top, sep)` | 89–112 | 填充多边形，可给每行最左/最右像素、最底/最顶像素单独上色（衣服的高光边、阴影边就靠它）。 |
| `outline(c='k')` | 114–125 | **最终描边**：所有透明且 4 邻域有像素的格子涂 `k`。**画布不会扩大**，所以剪影要离边留 ≥1px。 |
| `shift(dx, dy)` | 127 | 整体平移。 |
| `s()` | 136 | 输出字符串网格给 `define()`。 |

配套函数：`lean(g, k, pivot, rigid)` 140（按行剪切：`pivot` 行以上每行右移 `round(k*(pivot-y))`，`rigid` 行以上的头部整体平移不变形；**k>0 前倾、k<0 后仰**）、`edit/edits(grid, (x,y,'字符串')...)` 157/166（在网格上改几行像素做表情差分，`.` = 保留）、手型 `FIST` `FIST_L` `HAND_OPEN` `HAND_POINT` `HAND_GRIP` 173–199、`arm(g, pts, cols, hand, hand_off, sep='k')` 202（两段手臂 + 手居中盖在最后一点）。

**承太郎一帧 `j_frame(legs, coat, arm_n, arm_f, head, dy, k, hx, hy, extra, pre)`（366–394）**，画布 36×52：
1. `legs2()` 332：先远腿（`LEG_F='XxxXX'`，不加分隔线），再近腿（`LEG_N='xxxxX'`，`sep='k'`）；默认 `([(16,35),(16,47),'flat'], [(22,35),(22,47),'flat'])`，鞋 `J_SHOE` 盖在踝下 1 行；`'toe'` = 踮脚、`'toeb'` = 脚尖朝后。
2. `j_coat()` 348：外套下摆两片多边形（腰线第 33 行到 `hem=42`），`tail=(x,y)` 让后摆飞起、`ftail` 前襟、`back/front` 下摆外张。
3. 上半身另开一层 `up`：远臂（`'pocket'` = 插兜部件 `J_FARARM_POCKET` 盖在 (26,22)；或 `dict(pts, hand, cols=SLEEVE_F)`，`sep=None` 藏在躯干后）→ 躯干 `J_TORSO` (0,19) → 头 `J_HEAD` (hx=5, hy=6) → 近臂（`'pocket'` = `J_ARM_POCKET` (0,21)；或 dict，`sep='k'`，肩在 (12,23)，**近臂 = 画面左侧肩、横过躯干在前**）。
4. `lean(up, k, 34, rigid=21)`、`up.shift(0, dy)`、把 `up` 盖到下半身上、`extra(g)` 钩子（加道具）、最后 `g.outline()`。
5. 头部差分：`J_HEAD` 226（23×16，帽子+发尾在左、帽檐+金徽章在右）、`J_HEAD_SHOCK` 245、`J_HEAD_HURT` 252、`J_HEAD_LOW` 259（帽檐压低）；调色板 `JPAL` 213（`n/N/q` 外套三阶、`j/J` 内衫、`x/X` 裤、`E` 青绿瞳）。
6. 已有动作的参数表就是现成范例：`J_WALK` 401、`J_RUN` 415（`k=0.14` 前倾、拳 `FIST`）、`J_POINT_ARM` 437、`J_CAP_ARM` 446、`hurt` 457（`k=-0.18`）、`shock` 465、坐姿 `j_sit` 487（另画）。

乔瑟夫 `jo_frame()` 753 同理（36×52，`hat_dy/hat_dx` 帽子弹起、`face=JO_FACE_*`、`jo_arm(..., vines=True)` 会沿手臂画隐者之紫 `hermit()` 722），躺倒 `jo_lie()` 907 是专门画的 60×20（**头朝右**）；荷莉 `h_frame()` 1073（32×48，近臂分隔线用 `'S'` 而不是 `'k'`：“director: S reads cleanest”）。

### 2.2 `sprites_crew.py`：部件网格 + `compose`

- `G(s)` 14 是**函数**（不是类）：把多行字符串解析成 numpy 字符数组。
- `put(base, part, x, y, ol=None)` 34：盖章，`ol='k'` 时在重叠处画分隔线（同 G 类 `sep`）。
- `compose(w, h, parts, line=True)` 80：`parts = [(grid, x, y[, 'k']), ...]` 从后往前，坐标是名义画布 w×h 上的，内部在**左右各加 `PAD=12`、顶上加 12** 的大画布上画（姿势不会被裁），最后 `outline()`。
- `define(name, frames, pal, desc, anchor='mb', fps=None, size=None)` 114：自动识别 `NOMINAL=[(32,48),(36,56),(28,22)]` 三种名义尺寸，用 `fit()` 94 裁成“保留脚底行 + 以名义中心为轴左右对称”的最小公共尺寸 → 锚点 `mb` 永远是身体中线。**用别的名义尺寸调 `compose()` 必须传 `size=(w,h)`**，否则帧会带着 PAD 注册进去。
- 组装函数：`_av(head, braids, farm, barm, hem, legs, dy, dx, hdx, hdy, extra)` 465（阿布德尔：腿 (0,41) → 下摆 → 后臂 → 躯干 (dx,16+dy) → 头 (8,2) → 辫子带 `'k'` → 前臂带 `'k'`）；`_ka(...)` 947（花京院，`dy += 1` 让脚贴底）；`_po(face, farm, barm, legs, dy, dx, hdx, hdy, extra, hair_dy)` 1399（波鲁纳雷夫 36×56，头发柱 `PO_HAIR` 单独一层）；`_ig(...)` 1616（伊奇 28×22）。
- 部件库（可直接 import 复用）：`AV_HEAD/AV_HEAD_SMUG/AV_HEAD_PAIN`、`AV_ARM_F_DOWN/FWD/BACK/CAST/FLING`、`AV_ARM_B_DOWN/CAST`、`AV_LEGS_STAND/STRIDE_A/B/PASS_A/B/BRACE`、`AV_HEM_*`；`KA_*`、`PO_*`、`IG_*` 同构（完整名单：`grep -n "^[A-Z_]* = " sprites_crew.py`）。
- 倒地 `build_down()` 2018：**站立头部（闭眼版 `AV_HEAD_KO` 1887 / `KA_HEAD_KO` 1925）`rot_ccw` 转 90°** + 专门画的侧卧身体 `AV_LYING` 1904 / `KA_LYING` 1942（10 行高），头朝左、脸朝上。

### 2.3 `sprites_dio.py`：每个部件先描边再拼

- `_ol(grid)` 12：给部件四周补 1px 再加 `k` 外圈；`_st(base, part, x, y)` 32：盖“带描边的部件”（部件填充色的左上角落在 (x,y)）；`_compose(w, h, items, dy)` 39：`items=[(part, x, y[, outline=True])]`。效果：**每个部件之间都有描边线**（DIO 系角色比 G 类角色线更多）。
- `_shear(grid, offs)` 50 按行错位；`_leg(kind, far)` 261 用同一条 `LEG` 网格错位出 12 种腿；`FAR` 104 是远侧肢体换色表（`'x'→'X'` 等）。
- **换调色板复用部件**：瓦尼拉 `_van_idle()` 740 用的是 DIO 的 `ARM/PELVIS/_upper/_place_leg`，只是 `VAN_PAL` 692 把同样的字母映射成紫色系；泰伦斯 `_telence()` 1248 也复用 `LEG/PELVIS`。画新的“普通人体型”敌人时这是最省事的路线。

### 2.4 `sprites_stands.py`：`_Pix` 画笔 + 姿势表

- `_Pix(w, h, m)` 62：逻辑尺寸 w×h，四周再留 `m` 像素余量（`_M=8`）防止飘带/剑/火被裁；坐标都是逻辑坐标。
- 形状 → 布尔遮罩：`ell(cx,cy,rx,ry)`、`cap(x0,y0,x1,y1,r0,r1)`（锥形胶囊，肌肉四肢）、`poly(pts)`、`rect`、`lmask(pts,width)`。
- `paint(mask, tones, outline='k', hi=0.26, sh=0.64, rim=True)` 106–138：**自动明暗**。`tones` = `'b'` 平涂 / `'hbs'` 高光-底色-阴影 / `'hbsd'` 再加最深阴影；按像素在横/竖“行程”里的相对位置 u 决定：`u>sh` → 阴影，靠左/上边缘且 `u<hi` → 高光，`hbsd` 的第 4 色只上在右/下边缘 → **光从左上来是写死在算法里的**。先在遮罩外圈涂 `outline`（覆盖已有像素 = 分隔线）再填色。
- 其它：`fill / keep(mask, ch, only)`（只改某些字符，金色护腕就是 `keep` 把肤色换金色）、`line(pts, ch, only)`、`stamp(grid, x, y)`（手画的脸）、`_clean_outline()` 230（去掉孤立的描边小刺）。
- `_register(name, grids, pal, anchor, desc, fps)` 202–227：把同一动作的各帧裁到公共包围盒 + 2px 透明边（给 aura 留地方），**逻辑锚点 (20,56)** 换算成裁后坐标传给 `define()`。所以白金之星 `idle/punch/rush/block/pose` 画布宽不同（50/65/74/47/44），但锚点都对应同一个地面点，可在同一 (x,y) 互换。
- `_brute_frame(S, pose, ph, bob)` 473–527：肌肉人形替身通用帧。`S` = 规格字典（`SP_SPEC` 539：`w=40, bx=20, skin='avVx', fist, band, poses, back(头发+围巾), head, head_shout, pad(护肩), belt, neck, ghost(连打残影)`，世界 `TW_SPEC` 708 加了 `leg_deco/torso_deco`，红魔 `MR_SPEC` 1056 加了 `arm_deco`（手上火球）/`front`（喷火））。`pose` 查 `S['poses'][pose]`：
  ```
  dict(lean=前倾px, far=(肩x,肩y, 肘x,肘y, 拳x,拳y), near=(...),      # 都是相对 (cx=胸口中心x, ty=躯干顶y)
       legs=((髋x,髋y,膝x,膝y,脚x,脚y)远腿, (...)近腿),
       shout=True 换张嘴头, near_front/far_front 手臂画在身体前, far_fist/near_fist=False 不画拳,
       sy=整体下沉, w=画布宽(出拳要 64), bx=身体x, hy=头的y偏移, fire=(x,y) 红魔喷火点)
  ```
  **加新姿势 = 往姿势表里加一条字典**（见 6.2，零新像素）。
- 绿色法皇 `_hg_frame(pose, ph, bob)` 1122 查 `HG_ARMS` 1201（手臂六元组）、触手 `_hg_tendril`；银色战车 `_ch_frame` 1280 查 `CH_POSES` 1355（`far/near/legs` 是三点元组 + `ang` 剑角度 + `blade` 剑长 + `lean`）；愚者 `_fool_frame(ph, bob)` 1454 **没有姿势参数**，要新姿势只能复制函数改坐标。

### 2.5 `sprites_enemies.py`：另一个 `_Pix`

`_Pix(w, h)` 30：`rect/ell(盒子坐标)/poly/line/seg(粗折线, 半径 r)/dot/stamp('_' 擦除)`；`paste(o, x, y, ring='k')` 105 先把图层轮廓画到下层再贴（= 分隔线）；`shade(base, shade, d=(1,1), n=1)` 141：base 色里**朝 d 方向的邻居出了材质**的像素换成 shade —— `d=(1,1)` 右下阴影、`d=(-1,-1)` 左上高光；`outline('k')` 127。每个角色一个函数，内部按 后臂 → 身体 → 头 → 前臂 分图层 `paste(..., ring='k')`，最后 `outline`。例：`_hol_body(pose='idle'|'shoot', frame, w)` 258、`_strength(frame)` 1187、`_death13(frame)` 1342。坐标全写死在函数体里，**加姿势 = 在自己模块里复制这个函数改坐标**（`_hol_head/_hol_hat/PAL_HOL/_Pix` 都能 import）。

### 2.6 场景脚本里的先例（证明“外部模块补帧”可行）

- `scenes\s07_polnareff.py:69–138`：`from assets import sprites_crew as sc`，用 `sc._po(...)` + 新画的手臂网格造 `s07.pol_flick`、`pol_kneel`，换调色板造被烤焦的 `pol_char`。
- `scenes\s13_vanilla.py:93–166`：对已有帧做**像素后处理**：`_pol_kick()` 把 `polnareff.idle` 上半身按行剪切 + PIL 画腿 → 飞踢；`_van_hurt()` 把 `vanilla.idle` 上半身按 `(HIP-y)*0.30` 后仰剪切 → 受击；然后重新描边。
- `scenes\s19_revival.py:264–269`：把 8×11 的拳头小图 `alpha_composite` 到 `jotaro.idle` 上 → `s19.jot_fist`。
- 这些都已烘焙在 `角色图集\场景专用\`（见 4.1 表里的“场景专用可用”列）。

---

## 3. 画风规范（STYLE.md + 实测）

### 3.1 尺寸、比例（实测 frame 0 不透明包围盒）

| 类别 | 画布 | 实测身高（含描边） | 例 |
|---|---|---|---|
| 普通人 | 32×48 | 39–48 | 阿布德尔 47、花京院 42、荷莉 40、荷尔荷斯 48、恩雅 39（驼背）、斯蒂利丹 48 |
| 高个 | 36×52 | 47–48 | 承太郎 47、乔瑟夫 48、DIO 47、瓦尼拉 47、J·凯尔 50 |
| 超高发型 | 36×56 | 54 | 波鲁纳雷夫（头发柱高出头顶约 11px） |
| 动物 | 28×22 / 26×20 / 40×40 | 22 / 17 / 40 | 伊奇、佩特夏普、力量 |
| 替身（人形） | 逻辑 40×56，裁后 41–74 宽 | 52–55 | 白金之星、世界、红魔、法皇、战车；**脚悬空约 3px**，锚点在脚下地面 |
| 大型 | 80×80 | 78 | 正义（骷髅雾） |
| 头像 | 32×32 | — | 帧 0 闭嘴、帧 1 张嘴；底边不描边（`SJ.port_outline` 553：肩膀出画） |

- **头身比约 3 头身**：头宽 14–16、头高 13–16（承太郎头网格含帽 23×16），眼睛 2px 高、带 1px 高光（`W`/`w` + 虹膜色 + `k`）。3/4 侧脸朝右：远侧眼被部分遮挡，鼻子在右缘凸 1px。
- **脚**：最后一行是描边，鞋底在倒数第 2 行；锚点 `mb` = 两脚之间。倒地/躺卧帧锚点也是 `mb`（地面），**头朝左**（`avdol.down`、`kakyoin.down`；`joseph.lie` 例外头朝右，用时翻转）。
- 每帧颜色数实测 13–25（替身 8–16）。

### 3.2 调色、描边、光照、分隔线

- **描边**：外轮廓 1px `k` `#1a1020`；四种工具都有“最后整体描一圈”的步骤（`G.outline` / `sc.outline` / `_Pix.silhouette_outline`+`_clean_outline` / 敌人 `P.outline`）。DIO 系每个部件都有描边。
- **分隔线**：“在前面”的部件与已有像素重叠的边界画 1px 线：jojo 用 `sep='k'`（荷莉用 `'S'`），crew 用部件元组第 4 项 `'k'`，dio 自动，stands 是 `paint(outline='k')`，enemies 是 `paste(ring='k')`。**在身后的部件（远臂、远腿）不加分隔线**，靠更暗的色带区分。
- **光照**：光从左上。手画的部件 = 左列高光、右列阴影（`SLEEVE='qnnN'`、`LEG_N='xxxxX'`、`poly(left='q', right='N', bottom='N')`）；远侧肢体整体暗一档（`LEG_F='XxxXX'`、`SLEEVE_F='nnNN'`、DIO 的 `FAR` 换色表、阿布德尔后臂 `AV_ARM_B_DOWN` 全用阴影色 `A`）。替身/敌人靠算法（`paint` 的 hi/sh、`shade(d=(1,1))` 阴影 / `d=(-1,-1)` 高光）。
- **调色板**：优先用全局 `PAL` 字母（`k`、`s/S`、`w/W`、`y/Y`），角色专属颜色在 `pal={...}` 里覆盖，**每种材质 2–3 阶**（高光/底/阴影，偶尔加最深阴影）。各角色调色板位置：`JPAL` jojo:213、`JOPAL` 590、`HPAL` 998；`AV_PAL` crew:138、`KA_PAL` 560、`PO_PAL` 1004、`IG_PAL` 1496；`SP_PAL` stands:254、`TW_PAL` 556、`MR_PAL` 936、`HG_PAL` 1079、`CH_PAL` 1223、`FO_PAL` 1384、`HP_PAL` 1517；`DIO_PAL` dio:80、`VAN_PAL` 692、`CREAM_PAL` 783、`PS_PAL` 921、`DAR_PAL` 1017、`TEL_PAL` 1199、`ND_PAL` 1301、`GEB_PAL` 1380、`ZOM_PAL` 1499；敌人 `PAL_HOL` 182、`PAL_GEIL` 483、`PAL_HANGED` 638、`PAL_ENYA` 721、`PAL_JUSTICE` 849、`PAL_OB` 936、`PAL_TOWER` 1140、`PAL_STR` 1180、`PAL_DBM` 1252、`PAL_D13` 1332、`PAL_JUDGE` 1418、`PAL_DAN` 1496、`PAL_WHEEL` 1565、`PAL_HP` 1639、`PAL_MAR` 1691、`PAL_ALE` 1750。
- **同一个字母在不同角色里颜色不同**（`n` 在承太郎是外套藏青、在阿布德尔是肤色高光、在 DIO 是黑绿上衣）。**把 A 角色的部件盖到 B 角色帧里会被 B 的调色板重新上色**——拿 `SJ.FIST`（`s/S` 是全局肤色）给阿布德尔用就会变成浅肤色拳头，要先 `g_recolor`。
- 不要抗锯齿、不要渐变、不要半透明像素（替身透明度、光环、残影都是运行时效果）；STYLE.md 要求“JoJo pop”的高饱和色。
- 替身：比本体大一圈（逻辑 40×56）、用更亮/发光的色，场景里 `alpha≈0.9` + `sp.aura`（白金 `#b090ff`、银车 `#c8d8ff`、红魔 `#ff9040`，见 `scenes\s07_polnareff.py:63–65`）。

---

## 4. 现有动作与缺口

图集格式里：`f` = 帧数。`场景专用` 是 `角色图集\场景专用\` 里能借用的一次性姿势（锚点/尺寸各异，详见 `场景专用目录.json`）。

### 4.1 可操作的主角团 6 人 + 替身

| 角色 | 已有（catalog） | 场景专用可借 | 战斗还缺（建议补） | 补法 |
|---|---|---|---|---|
| 承太郎 `jotaro` 36×52 | idle2 walk4 run4 sit2 point2 pose2 shock1 hurt1 + 头像 normal/angry | `s19_jot_fist` 举拳 2f、`s18_final2_jotaro_back` 背影 4f、`s03_jotaro_back` 3f、`s05_jotaro_talk`/`s20_jotaro_smile` 头像 | **出招指令 punch2、guard1、dodge1、down1**（本次已做原型）；可选：被打飞（用 hurt + 运行时旋转） | `j_frame` 关节坐标；down 需新画躯干 |
| 白金之星 `starplat` | idle4 punch3 rush2 block1 pose2 fist + 头像 | `s17_spup` 双拳高举蓄力 4f（锚点 (27,72)）、`s04_sphand` | **upper/重击1、hurt1**（已做原型）；可选 kick1、星之指 1（姿势 + 代码画伸长的手指）、时停姿势用 `pose` | `SP_POSES` 加条目 |
| 乔瑟夫 `joseph` 36×52 | idle2 walk4 run4 point1 camera2 shock2 hurt1 lie1(60×20, **头朝右**) + 头像 normal/shock | 跪坐 2f、跪伸手 2f、挥手 4f、头像 grave/closed/evil | **藤蔓出招 2（举手 → 前甩）、guard1、dodge1**；down 用 `lie` 翻转 | `jo_frame`，`arm_n.vines=True` 已能在手臂上画藤蔓 |
| 隐者之紫 `hermit` | 只有 `vine` 16×9 平铺片 | — | 没有“本体”，攻击就是运行时画藤蔓（原引擎 `fx.vines` fx.py:1642、`fx.hamon` 1076 波纹电光）；不用补帧 | JS 里沿折线平铺 `hermit.vine` |
| 阿布德尔 `avdol` 32×48 | idle2 walk4 cast2 yes2 hurt1 down1 + 头像 | 跪坐 2f、头像 grave | **guard1、dodge1** | `_av` 换部件，几乎零新像素 |
| 红色魔术师 `magred` | idle2 cast2 | — | **punch2（近身）、hurt1、block1**；十字火焰风暴 = `fx.fire_ankh` 960、红色束缚 = 代码画 | `MR_POSES` 加条目。注意 `_mr_arm_deco` 1022 会在每只拳头上画火球（`P.get('fire')` 时才不画），出拳姿势要么接受火拳（挺好看），要么复制 spec 把 `arm_deco` 换掉 |
| 花京院 `kakyoin` 32×48 | idle2 walk4 cast2 cherry2 possessed2 hurt1 down1 + 头像 normal/hurt | 坐地、附身头像、负伤/微笑头像多张 | **guard1、dodge1**（dodge 已做原型） | `_ka` 换部件 |
| 绿色法皇 `hiero` | idle2 cast2 | — | **触手鞭/缠绕 1–2、hurt1、block1**；绿宝石水花 = `fx.emerald_splash` 1531、20m 结界 = `fx.tendrils` 1595 | `HG_ARMS` 加条目 + `_hg_tendril` |
| 波鲁纳雷夫 `polnareff` 36×56 | idle2 walk4 crawl2 fight2 wave2 shock2 cry2 hurt1 + 头像 normal/shock | `s13_pol_kick` 飞踢 1f（锚点=髋 (24,47)）、单膝跪、弹硬币 2f、`s14_face` 64×68 大头像 | **down1（已做原型）、guard1、dodge1** | `_po` + 倒地需新画躯干 |
| 银色战车 `chariot` | idle2 thrust3（含残影乱刺） | — | **横斩 1–2、格挡/弹剑 1、hurt1**；可选卸甲高速形态（换部件颜色 + 运行时残影） | `CH_POSES` 加条目 |
| 伊奇 `iggy` 28×22 | idle2 run4 sit1 bite2 down1 + 头像 | — | **hurt1、闪避跳 1**；出招指令用 `bite[0]` 低吼 | `_ig` 换头/偏移；跳 = `run[0]` 抬高 |
| 愚者 `fool` | idle2 glide1 | — | **沙爪攻击 1–2、沙壁防御 1**；受击 = 运行时抖散 | `_fool_frame` 无姿势参数，复制函数改坐标 |

### 4.2 已有的敌人（DIO 阵营 + 敌人）

| 角色 | 已有 | 说明 / 建议补 |
|---|---|---|
| DIO `dio` 36×52 | idle2 walk4 jump1 throw2 pose2 laugh2 hurt1 coffin_rise2 crumble4 + 头像 normal/rage | 最全；可补 punch（本体近战）、`s01_dio_dim/lit`、`s18_final2_dio_shock*` 头像可用 |
| 世界 `theworld` | idle4 punch3 rush2 pose2 crack2 fist + 头像 | 最终 BOSS 够用；可补 hurt、kick |
| 瓦尼拉 `vanilla` | idle2 + 头像 | `s13_van_hurt` 后仰受击；缺攻击（召唤奶油的姿势）、down |
| 奶油 `cream` | idle2、void2（24×24 虚空球） | 吞噬/隐身 = 运行时；缺张嘴吞自己的过渡帧（可选） |
| 荷尔荷斯 `holhorse` | idle2 flee2 shoot2 + 头像 | 子弹 `prop.bullet`；`s09_hh_nogun`、`s09_flee_nohat`；缺 hurt |
| J·凯尔 `jgeil` / 倒吊人 `hangedman` | idle2 hurt1 + 头像 / idle2 | 倒吊人缺攻击（腕刃前刺）1–2 |
| 恩雅 `enya` / 正义 `justice` / 僵尸 `zombie` | idle2 + 头像 / skull2 / walk2 | 正义缺攻击（骷髅手抓）；僵尸缺攻击、倒地 |
| 恩多尔 `ndoul` / 盖布神 `geb` | idle2 / claw3 | 盖布够用（水爪 3 帧 oneshot） |
| 奥因哥 `oingo` / 波因哥 `boingo` | idle2 boom1 / idle2 | `s12_fake_jotaro`、`s12_oingo_morph`（克努姆变脸）可用 |
| 达比 `darby` | sit2 + 头像 2 种 | 赌局 = 小游戏，不需打斗帧 |
| 泰伦斯 `telence` | idle2 + 头像 | 游戏对决 = 小游戏；阿图姆神本体未画 |
| 佩特夏普 `petshop` | fly4 perch1 | 冰锥 = 代码；缺俯冲/受击 |
| 力量 `strength` | idle2 | 猩猩；缺攻击/受击 |
| 灰塔 `towergray` | fly2（16×12） | 虫子够用；缺使用者 |
| 暗蓝之月 `darkbluemoon` | swim2 | 缺攻击；缺使用者（假船长） |
| 命运之轮 `wheel` | car2（64×32） | 车战；缺使用者 ZZ |
| 死神13 `death13` | float2 | 缺镰刀挥击；缺使用者（婴儿） |
| 审判 `judgement` | idle2 | 缺攻击；缺使用者 |
| 斯蒂利丹 `steelydan` | idle2 | 恋人替身本体（微型）没画 |
| 女教皇 `highpriestess` | idle2 | 缺攻击；缺使用者 |
| 玛丽亚 `mariah` / 阿莱西 `alessi` | idle1 / idle1 | 只有 1 帧；巴斯特女神（插座）画在玛丽亚手里；塞特神（影子）没画 |

**每个敌人做成 BOSS 建议最少帧**：idle 2 + 攻击预兆 1 + 攻击 1–2 + hurt 1 + 倒地/败北 1。其中 hurt 和倒地可以先用第 6.4 节的**自动后处理**兜底，攻击帧手画。

### 4.3 第三部里完全没有精灵的替身使者 / 替身（需要“画新角色”）

分镜总表里一次都没出现（已 grep 确认 0 次）：黄色节制（橡皮灵魂）、女帝（妮娜）、乌木恶魔（迪波 + 玩偶）、阿努比斯（妖刀 + 被附身的人）、次中音萨克斯（肯尼 G）、曼尼什男孩（死神13 的婴儿使用者）、卡梅欧（审判）、米德勒（女教皇）、灰塔使用者、命运之轮使用者 ZZ、暗蓝之月使用者、塞特神本体、奥西里斯神本体、阿图姆神本体、恋人本体、努肯萨库等。最终名单以剧情调研为准；画法见第 5 节，工作量见第 8 节。可借现成的：太阳的使用者 `场景专用\s10_sunguy`（npc）、太阳本体原片是代码画的火球（`scenes\s10_montage1.py`）。

---

## 5. 不改源码补帧 / 画新角色：做法与规则

### 5.1 目录建议

```
游戏\tools\art\
  art_common.py          sys.path / 不写字节码 / rot_ccw / crop / reoutline / auto_hurt 等公共工具
  art_heroes.py          主角团本体补帧（承太郎/乔瑟夫/荷莉 用 SJ；阿布德尔/花京院/波鲁/伊奇 用 sc）
  art_stands.py          替身补帧（SS 姿势表扩展、复制改写 _fool_frame 等）
  art_enemies.py         已有敌人补帧（SE/SD 函数复制改写 + 自动后处理）
  art_new_<名字>.py      每个新角色一个文件
  bake_game_chars.py     烘焙（复用 烘焙脚本\bake_characters.py 的函数，输出到 游戏\assets\chars\）
  _preview\              自己的 4 倍预览图（不要往 源码\out 写）
```

### 5.2 模块模板（关键行）

```python
import sys
sys.dont_write_bytecode = True                      # 必须在 import assets 之前
SRC = r'D:\大疆\游戏素材\JoJo\源码'
if SRC not in sys.path:
    sys.path.insert(0, SRC)
from engine import sprite
from engine.sprite import g_lines, g_join, g_recolor
from assets import sprites_jojo as SJ               # import 即注册该模块全部原精灵，同时拿到骨架
from assets import sprites_crew as sc
from assets import sprites_stands as SS
from assets import sprites_dio as SD
from assets import sprites_enemies as SE
```

运行时也设 `PYTHONDONTWRITEBYTECODE=1`，跑完 `find 源码 -name __pycache__` 应为空（本次实测为空）。只 import `assets.sprites_*` 不需要 `os.chdir`；全部 6 个模块 import 约 1.1 秒（stands 0.57 秒最慢）。

### 5.3 规则（保证同画风、不踩坑）

1. **用该角色原来的骨架和部件**（第 2 节表），调色板直接引用原模块常量（`SJ.JPAL`、`sc.PO_PAL`、`SS.SP_PAL`、`SE.PAL_HOL`），不要另抄一份颜色。
2. **新名字 = `<角色id>.<新动作>`**（如 `jotaro.punch`），这样烘焙时自动归进该角色图集。**不要重新 define 已有名字**（会覆盖原精灵，烘焙出来的就不是原片了）；确实要改原帧时用新动作名。
3. 画布与原动作一致（承太郎 36×52、花京院 32×48 名义尺寸），锚点 `mb`；替身用 `SS._register(..., anchor=(20, 56))`，**同一动作的各帧放进同一次 `_register`**。倒地帧画布加宽（50–60 × 20–24），头朝左。
4. G 类画布不会自动扩大，`outline()` 前剪影离四边至少 1px；crew 的 `compose()` 有 12px 余量，非 `NOMINAL` 尺寸要传 `size=`。
5. 手臂方向约定：G 类 / crew 都是“近臂 = 画面左侧肩、画在躯干前（带分隔线）”，“远臂 = 右侧肩、躯干后（不带线、颜色更暗）”。出拳通常用近臂横过身体（原 `point` 就是这样），远臂收在胸前。
6. 表情差分用 `SJ.edits(grid, (x, y, '字符'), ...)` 或 numpy 数组切片赋值（`sc` 的头是数组：`face[3, 6:8] = 'k'`，见 `build_polnareff` 1445–1453）。
7. 跨角色借部件先 `g_recolor` 换字母（3.2 节的“同字母不同色”坑）。
8. **预览自查**：每画一个动作就出 4–8 倍最近邻预览（第 6.5 节脚本），和该角色 idle 并排看头身、描边、光向；原工程规范原话：“Always look at your output PNGs with the Read tool and iterate until it genuinely looks good.”
9. 不跑 `源码\tools\*.py`（会写 `源码\out\`），不在 `源码\` 下建任何文件。

---

## 6. 原型验证（本次实际做的）

### 6.1 承太郎：4 个新动作 5 帧（`j_frame` + 一个手画倒地）

```python
G, j_frame = SJ.G, SJ.j_frame
FIST, HAND_OPEN, SLEEVE_H, JPAL = SJ.FIST, SJ.HAND_OPEN, SJ.SLEEVE_H, SJ.JPAL

PUNCH = [   # 0 蓄力：近拳收在腰、远拳护胸；1 直拳：近臂横伸、弓步、前倾、后摆飞起
    j_frame(arm_n=dict(pts=[(12, 23), (8, 27), (11, 31)], hand=FIST),
            arm_f=dict(pts=[(26, 23), (29, 27), (31, 23)], hand=FIST),
            legs=([(16, 35), (12, 47), 'flat'], [(22, 35), (26, 47), 'flat']),
            coat=dict(back=2, front=2), k=-0.05),
    j_frame(arm_n=dict(pts=[(12, 23), (21, 23), (31, 22)], hand=FIST, cols=SLEEVE_H, off=(1, 0)),
            arm_f=dict(pts=[(26, 23), (27, 28), (24, 30)], hand=FIST),
            legs=([(16, 35), (10, 47), 'toe'], [(22, 35), (27, 47), 'flat']),
            coat=dict(tail=(2, 40), front=3), k=0.12),
]
sprite.define('jotaro.punch', PUNCH, pal=JPAL, fps=12, desc='0 wind-up, 1 straight punch with lunge')

GUARD = j_frame(head=SJ.J_HEAD_LOW,                       # 帽檐压低 + 双拳交叉护在下巴前
                arm_n=dict(pts=[(12, 23), (16, 30), (25, 22)], hand=FIST),
                arm_f=dict(pts=[(26, 23), (31, 28), (29, 21)], hand=FIST),
                legs=([(16, 35), (12, 47), 'flat'], [(22, 35), (26, 47), 'flat']),
                coat=dict(back=2, front=2), k=-0.04, dy=1)
sprite.define('jotaro.guard', [GUARD], pal=JPAL, desc='forearms crossed in front of the chin')

DODGE = j_frame(arm_n=dict(pts=[(12, 23), (7, 27), (3, 30)], hand=HAND_OPEN),   # 后撤步、后仰、外套飞起
                arm_f=dict(pts=[(26, 23), (30, 25), (33, 23)], hand=HAND_OPEN),
                legs=([(16, 35), (9, 46), 'toe'], [(22, 35), (23, 41), (21, 47), 'flat']),
                coat=dict(tail=(0, 39), front=1), k=-0.20, dy=1)
sprite.define('jotaro.dodge', [DODGE], pal=JPAL, desc='quick back-step')

def rot_ccw(grid):          # 同 SJ.rot_ccw（1139，定义在荷莉段，也可直接用 SJ.rot_ccw）
    ls = g_lines(grid); h, w = len(ls), len(ls[0])
    return g_join(''.join(ls[x][w - 1 - y] for x in range(h)) for y in range(w))

def j_down():               # 58×24，仰躺、头朝左、闭眼咬牙；锚点 mb = 地面
    g = G(58, 24); gy = 22
    g.limb((33, gy - 4), (43, gy - 7), 'XxxX'); g.limb((43, gy - 7), (52, gy - 4), 'XxxX')     # 远腿屈膝
    g.stamp('hh.|hhh|hhh|HHh'.replace('|', '\n'), 52, gy - 8)
    g.limb((33, gy - 1), (51, gy - 1), 'xxxX', sep='k')                                    # 近腿平放
    g.stamp('hh|hh|hh|hh|HH'.replace('|', '\n'), 52, gy - 4, sep='k')
    g.poly([(30, gy - 9), (38, gy - 8), (42, gy), (28, gy)], 'n', top='q', bottom='N')     # 下摆铺地
    g.poly([(15, gy - 10), (31, gy - 9), (31, gy), (15, gy)], 'n', top='q', bottom='N', sep='k')  # 躯干
    g.poly([(19, gy - 9), (29, gy - 8), (29, gy - 6), (19, gy - 7)], 'j')                  # 内衫
    g.limb((29, gy - 8), (29, gy - 1), 'H'); g.put(29, gy - 5, 'y')                        # 腰带扣
    for x, y in ((18, gy - 9), (19, gy - 8), (21, gy - 8), (22, gy - 7)):
        g.put(x, y, 'y')                                                                   # 金链
    head = rot_ccw(g_join(r[3:23] for r in g_lines(SJ.J_HEAD_HURT)))   # 去掉最左 3 列发尾 → 16×20
    g.stamp(head, 1, gy - 19, sep='k')
    g.limb((19, gy - 4), (29, gy - 3), 'qnnN', sep='k'); g.stamp(FIST, 29, gy - 5, sep='k')  # 手臂贴身
    return g.outline().s()
sprite.define('jotaro.down', [j_down()], pal=JPAL, desc='knocked down, head LEFT (58x24)')
```

结果（`cv_zoom_j.png`、`cv_proto_sheet.png`）：punch/dodge 第一次渲染就成立；guard 第一版双臂太高挡住眼睛，把拳头降到下巴（y≈21–22）后成立；down 第一版即可读（头部是旋转后的 3/4 脸，和 `kakyoin.down`、`avdol.down` 同一套处理）。5 帧生成耗时 7.6 ms。

### 6.2 白金之星：姿势表加两条（零新像素）

```python
SP_POSES2 = dict(SS.SP_POSES)
SP_POSES2['upper'] = dict(lean=1, far=(8, 3, 12, 9, 14, 3), near=(-7, 4, 6, 6, 15, -9),
                          legs=((3, 19, 6, 26, 4, 35), (-3, 19, -7, 26, -11, 33)),
                          shout=True, near_front=True, sy=-1)
SP_POSES2['hurt'] = dict(lean=-3, far=(8, 3, 14, 7, 20, 3), near=(-8, 4, -15, 6, -19, 2),
                         legs=((3, 19, 7, 26, 9, 34), (-3, 19, -7, 27, -12, 35)), sy=1)
SP_SPEC2 = dict(SS.SP_SPEC, poses=SP_POSES2)          # 不改原字典
SS._register('starplat.upper', [SS._brute_frame(SP_SPEC2, 'upper', 0, 0)], pal=SS.SP_PAL,
             anchor=(20, 56), desc='rising uppercut')
SS._register('starplat.hurt', [SS._brute_frame(SP_SPEC2, 'hurt', 1, 0)], pal=SS.SP_PAL,
             anchor=(20, 56), desc='recoil, arms flung back')
```

`upper` 第一版拳头 `(7,-12)` 正好挡住脸，改成 `(15,-9)`（拳在脸前上方）后成立；`hurt` 一次成立。坐标单位是相对 (胸口中心, 躯干顶)；`far`/`near` 的第 5、6 个数就是拳头位置，出拳越远画布要越宽（`w=64`）。世界 `TW_POSES`、红魔 `MR_POSES` 用法完全一样。2 帧 23 ms。

### 6.3 crew：花京院闪避（零新像素）+ 波鲁纳雷夫倒地（新画躯干 + 旋转原头部）

```python
dodge = sc._ka(dx=-2, hdx=-1, hdy=1, farm=(sc.KA_ARM_F_FLING, 18, 14),
               legs=sc.KA_LEGS_STRIDE_A, tail=sc.KA_TAIL_WIND)
sc.define('kakyoin.dodge', [dodge], sc.KA_PAL, 'back-step dodge')       # 自动 fit 回 32x48

PO_LYING = sc.G("""
...................................HH
..ssss.............................hH
.TTtttttttttsssshhppppppppppppppp..hH
TTtttttttttttsssshhpppppppppppppppphH
ttttttttttttttSSShhppppppppppppppppHH
tttttsstttttttSSShhpppppppppppppppp..
ttttsSsttttttttSShhPPPPPPPPPPPPPPPP..
tttttttttttttttttthPPPPPPPPPPPPPPP...
.ttttttttttttttttthPPPPPPPPPPPPPPP...
""")
face = sc.PO_FACE_PAIN.copy()
face[3, 5:8] = list('sss'); face[4, 5:8] = list('kkk')        # 闭眼
face[3, 12:15] = list('sss'); face[4, 12:15] = list('kkk')
head = sc.put(sc.put(sc.blank(16, 21), sc.PO_HAIR, 0, 0), face, 0, 11)
head = sc.rot_ccw(sc.crop(head))                               # 发柱朝左平放、脸朝上
d = sc.put(sc.put(sc.blank(60, 22), PO_LYING, 21, 11), head, 1, 3)
sc.define('polnareff.down', [sc.outline(d)], sc.PO_PAL, 'knocked down, head LEFT (60x22)')
```

两者第一版即成立（`cv_zoom_crew.png` 里和原 `kakyoin.down`、`avdol.down` 并排对比，粗细、描边一致）。

### 6.4 给“只有 idle”的敌人自动出 hurt / 倒地（兜底方案）

`cv_auto_frames.py`：先剥掉外圈 `k` 描边，再
- `auto_hurt`：髋线（默认 0.68×高）以上每行左移 `round(0.30*(hip-y))`（`s13_vanilla._van_hurt` 的配方），重新描边 → 后仰受击；
- `auto_lunge`：系数 −0.18 → 前倾（攻击预兆）；
- `auto_down`：`np.rot90(a, 1)`（头朝左）+ 重新描边。

荷尔荷斯 / 瓦尼拉 / 斯蒂利丹 / 死神13 / 恩多尔 / 恩雅实测（`cv_auto_sheet.png`）：后仰和前倾在游戏尺寸下可读（剪切会出现 1px 台阶，可接受）；**自动倒地偏厚**（站立宽度 = 倒地厚度，约 28–34px，正经倒地帧只有 18–22px），只适合小怪，BOSS 的倒地/败北建议手画或改用运行时演出（受击帧 + 旋转 + `fx.shatter` 碎裂 / 抖动淡出，原片 s13 瓦尼拉化灰就是这么做的）。旋转正好 90° 时最近邻无损，JS 里 `ctx.rotate(Math.PI/2)` 同样无损。

### 6.5 预览脚本要点

`cv_zoom.py`：`sprite.get(name).frames[i]`（PIL RGBA）→ `resize((w*S, h*S), Image.NEAREST)` → 贴到棋盘格底上、底边对齐、标名字。也可直接用 `sprite.sheet(prefix, scale)` 拿联系表（存到自己的 `_preview\`）。

---

## 7. 烘焙到游戏图集

### 7.1 复用 `烘焙脚本\bake_characters.py`（不改它）

脚本的 `main()` 只在 `__main__` 下运行，模块级函数都能 import。关键函数：`load_registry(src, with_scene)` 311（**会 `os.chdir(src)`**，之后一律用绝对路径）、`Spr(name, sd, module)` 292、`build_actions(base)` 849、`classify(spr)` 366（播放方式：查 `ONESHOT` 122 / `STATIC_STATES` 138 两个集合，否则多帧=loop、单帧=static）、`bake_character(cid, acts, portraits, extras, out_dir, scale)` 379（算 cell/pivot、去重、写 `<out>/<cid>/<cid>.png`、`.json`、`头像\`、`_预览.png`）、`verify(...)` 867（回读逐像素比对）、`verify_engine(baked)` 923（与 `engine.sprite.draw` 含翻转逐像素比对）。

实测可用的包装脚本（`cv_bake_test.py` 精简版）：

```python
import sys, os, importlib
sys.dont_write_bytecode = True
ROOT = r'D:\大疆\游戏素材\JoJo'
SRC = os.path.join(ROOT, '源码')
GAME = os.path.join(ROOT, '游戏')
OUT = os.path.join(GAME, 'assets', 'chars')               # 游戏自己的图集目录（不要写回 角色图集\）
sys.path.insert(0, os.path.join(ROOT, '烘焙脚本'))
sys.path.insert(0, os.path.join(GAME, 'tools', 'art'))
import bake_characters as B

base, _ = B.load_registry(SRC, with_scene=False)          # 166 个原精灵
before = set(base)
for m in ('art_heroes', 'art_stands', 'art_enemies'):     # 我们的模块：import 即注册新精灵
    importlib.import_module(m)
from engine import sprite
base.update({n: B.Spr(n, sprite.get(n), 'game.' + n.split('.')[0])
             for n in sprite.names() if n not in before})
B.ONESHOT |= {'jotaro.punch', 'starplat.upper'}           # 新动作的播放方式（否则多帧默认 loop）
B.ACTION_ZH.update(guard='格挡', dodge='闪避', upper='上勾拳')   # 预览图标签（可选）
B.CHAR_INFO['rubbersoul'] = dict(zh='橡皮灵魂', en='Rubber Soul', cat='敌人·人物', typ='人物')  # 新角色名字
chars, props = B.build_actions(base)
baked = [B.bake_character(cid, *chars[cid], [], B.ensure_dir(OUT), 4) for cid in chars]
errors, n = B.verify(OUT, baked, [], {}, [], {})
eng_n, eng_bad, _ = B.verify_engine(baked)
assert errors == 0 and eng_bad == 0
```

本次只烘了 jotaro / starplat / kakyoin / polnareff 到 scratch：`jotaro` 变成 14 行（多了 punch/down/dodge/guard），**cell 从 40×52 变成 58×52、pivot 从 (20,52) 变成 (29,52)**（被 58 宽的 down 撑大）；starplat cell 79×62→80×63、pivot (29,58)→(30,59)；polnareff 50×56→60×56。校验：97 帧回读 0 错误，与引擎绘制比对 168 次 0 不一致。

### 7.2 输出格式与游戏怎么用

- 格式与 `角色图集\README.md` 完全相同：`<id>.png` 一行一个动作、帧紧挨、cell 统一；`<id>.json` 里 `cell / pivot / animations{row, frames, fps, kind, seamless, desc} / aliases / expressions` + `头像\*.png`。绘制：`drawImage(img, i*cw, row*ch, cw, ch, round(x-px), round(y-py), cw, ch)`，朝左绕 pivot 翻转（README “HTML canvas” 一节）。
- 银魂游戏 `游戏素材\银魂\游戏\tools\build_assets.py` 的 `build_chars()`（69–108）就是：先拷 `角色图集\*\*.json`，再扫游戏自己烘好的 `assets\chars\s*\*.json`（同格式）合进 `data.js`。JoJo 照搬即可，**规则：游戏自己烘的同名 id 覆盖 `角色图集` 里的**（因为它包含原有全部行 + 新行）。
- **游戏代码必须从 json 读 cell/pivot/row，不能写死**：补一个宽帧就会让整张图集的 cell 和 pivot 变。
- 替身光环、受击闪白、残影、半透明、阴影都不在图集里：JS 端按原引擎实现（`sprite.aura` 268、`_apply_tint` 168、`fx.afterimage` fx.py:650：残影 = 白色 30% 着色 + 抖动透明度 0.3→0.75）。

---

## 8. 工作量估计（按本次原型的实际迭代次数推算，单位：代理工作时间）

| 类型 | 每单位 | 说明 |
|---|---|---|
| 换部件/改关节坐标的帧（G 类 `j_frame`、crew `_ka/_po/_av`、替身姿势表） | 5–15 分钟/帧 | 本次 7 帧里 5 帧一次成立、2 帧改了一次坐标 |
| 需要新画部件的帧（倒地躯干、新手臂/腿网格、新表情） | 20–40 分钟/帧 | `jotaro.down` ≈ 30 行代码一次成立；`polnareff.down` 新画 9 行网格 |
| 自动后处理帧（auto_hurt / auto_lunge / auto_down） | 几乎为 0（写好一次） | 只适合小怪 / 占位 |
| 已有敌人补成 BOSS（攻击 2 + hurt 1 + 倒地 1，需复制改写其函数） | 1–2 小时/个 | enemies 模块的函数坐标写死，复制后改 |
| 新人类角色全套（调色板 + 头/躯干/四肢部件 + idle2 walk4 攻击2–3 hurt1 down1 + 头像2） | 3–5 小时/个 | 复用 DIO 或承太郎的身体部件、只换调色板 + 新画头部 → 接近 3 小时；体型特殊（婴儿、胖子、女性长裙）→ 5 小时 |
| 新人形替身（走 `_brute_frame` 规格：调色板 + 头网格 + back/pad/belt/装饰函数 + 姿势表 idle/punch/hurt） | 2–3 小时/个 | 审判、阿图姆神、奥西里斯神、塞特神等 |
| 新非人形替身（史莱姆、玩偶、刀、萨克斯、影子） | 1–3 小时/个 | 帧少，主要靠运行时特效 |

粗算全量：主角团本体补帧约 20 帧（≈3–4 h）+ 替身补帧约 25 帧（≈5–6 h）+ 已有敌人 BOSS 化约 15 个（≈20 h）+ 新角色/新替身约 15–20 个（≈40–60 h）。建议先做第一章用到的（承太郎+白金之星全套、花京院+法皇、灰塔），走通“补帧 → 烘焙 → data.js → 游戏里打一场”的整条链，再批量。

---

## 9. 风险 / 需要定的事

1. **补宽帧会改 cell / pivot**（实测 jotaro 40×52→58×52）：游戏必须读 json；若嫌浪费，可把倒地这类宽帧烘成单独的 `<id>__down` 小图集（`bake_character` 传不同 cid 即可），代价是游戏里多一个查表。
2. **同名覆盖**：新模块里 `define` 了已有名字会悄悄替换原帧；包装脚本里建议加检查：新注册的名字不得与 `before` 重名。
3. **倒地方向不统一**：`avdol.down`/`kakyoin.down`/新做的 `jotaro.down`/`polnareff.down` 头朝左，`joseph.lie` 头朝右，`iggy.down` 是趴着。游戏里按“朝右时头朝左（向后倒）”统一，乔瑟夫的 `lie` 绘制时额外翻转。
4. 自动倒地帧偏厚，BOSS 败北建议用演出（碎裂/化灰/飞出画面）代替倒地帧。
5. 新角色的造型（尤其完全没画过的十几个使用者）是原创像素画，要符合原著辨识特征：建议每个新角色先出 idle + 头像给用户过目再做全套（银魂项目里“三版新风格被否”的教训）。
6. 画面尺寸：这些精灵是按 320×180 画布、1× 设计的（站立约占屏高 26%）；游戏若改用别的内部分辨率，只能整数倍放大，不要非整数缩放。
7. 原工程音乐/背景/特效是代码生成的，与本报告无关，但替身攻击很多是“特效不是精灵”（隐者之紫藤蔓、绿宝石、十字火焰、时停球、太阳火球），这部分要在 JS 里重写，工作量不在第 8 节里。
