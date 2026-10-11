# JoJo 星尘斗士 · 像素剧情动作游戏（同人，本机自用）

把《JoJo 的奇妙冒险 第三部 星尘斗士》的像素动画素材做成的网页 2D 剧情打斗游戏：替身系统、打全部替身使者、从东京一路打到开罗 DIO 的馆。

**双击 `index.html` 就能玩**（Chrome / Edge；`file://` 直接打开，不用装东西、不用联网、不用开服务器）。

> 标题曲是用户提供的《STAND PROUD》，商业歌曲，只适合本机自己玩，不要公开分发。

## 开始

标题菜单：

- **继续**：从玩到的最远一章开始（进度自动存在浏览器里）。
- **从序章开始**。
- **选择章节**：任何一章都能直接进（3 页，每页 5 章）。
- 操作说明 / 设置（音量等）。

## 按键

| 键 | 战斗中 | 自由走动时 |
|---|---|---|
| ←→↑↓（或 WASD） | 移动 | 移动 |
| J（或 Z） | 替身出拳：三连，连按进连打（欧拉 / 火焰洪流 / 刺剑……） | 亮出替身，“伸手”碰身边的东西 / 人 |
| K（或 X） | 闪避（闪开那一下无敌；擦边闪避 = 看穿） | — |
| L（或 C） | 按住格挡；敌人出手瞬间按一下 = 精准格挡 | — |
| U（或 V） | 能量满时替身必杀 | 替身调查（每个队长看到的东西不一样） |
| Q（或 Tab）、1–6 | 个别战斗可以换人 | 随时换队长 |
| E / Enter / 空格 | — | 调查、搭话、推进对白（**J 不推进对白**） |
| Esc（或 P） | 暂停 | 暂停 |

触屏：手机 / 平板上自动显示虚拟按键；电脑上在网址后面加 `?touch=1` 可以强制显示。**真机没测过。**

## 章节

| 章 | 地点 | 内容 |
|---|---|---|
| 序章 | 东京 | 牢房（自由探索）→ 阿布德尔的试探（教学战，在铁栏外的走廊打）→ 被操纵的花京院 → 拔肉芽 → 出发去埃及 |
| 第1章 | 香港 | 灰塔（飞机）→ 迫降 → 香港街头 → 银色战车 |
| 第2章 | 南海 | 南海漂流 |
| 第3章 | 新加坡 | 新加坡的恶意 |
| 第4章 | 印度 | 两只右手的男人 |
| 第5章 | 巴基斯坦 | 公路、浓雾与卡拉奇 |
| 第6章 | 阿拉伯 | 沙漠的太阳与梦 |
| 第7章 | 红海 | 许愿与大嘴 |
| 第8章 | 埃及沙漠 | 九荣神：沙与预言 |
| 第9章 | 尼罗河 | 刀、磁铁与影子 |
| 第10章 | 开罗 | 赌局与看门鸟 |
| 第11章 | DIO 的馆 | 日落之前 |
| 终章 | DIO 的世界 | 直到黎明 |

各章自动测试的状态见下面「测试状态」。

## 测试状态（2026-10-10 下午）

- 序章：从标题打到序章章末 0 报错、300 s、帧率 60、没有缺图（`tools/_playtest/main_pro_r5`；牢房新背景、保健室的门、石阶、花京院战、卧室找苍蝇都走通）。花京院最后一段“正面挡下绿宝石水花”原来玩家绕到他身后会转圈卡住，已修。
- 第1章：正常路线 354 s 打到章末、帧率 60、没有缺图（`main_ch1_r2`，香港新背景）；故意输路线：灰塔输 2 次后有「放水再来」、银色战车输 1 次后重来，打到章末（`main_ch1_lose_r1`）。两条唯一的报错都是测试器在银色战车那场没用格挡的覆盖统计。
- 体验版包：`tools/dev/full/test_demo.py --root <包>` 9 项全过（`demo_check_release`）。
- 战斗回归：`test_combat` 14/14、`test_specials` 79/79、`test_special_visuals` 12/12（战斗美术代理最后一次烘焙之后）。
- 体验版开关：`tools/dev/full/test_demo.py` 9 项全过（开发目录和打好的包都测过）。
- 手机：Playwright 模拟横屏触屏（`tools/dev/full/test_touch_layout.py`）能从标题点到牢房自由走动、0 报错；真机没测。
- **第2章（2026-10-11 按体验版精度重做完）**：正常路线 303 s 打到章末、帧率 60、没有缺图 / 缺字 / 缺音效（`tools/_playtest/c2_flow3`）；故意输路线：暗蓝之月输 2 次后有「放水再来」、力量输 1 次后重来，打到章末，0 报错（`c2_lose1`）。设计和台词见 `docs/章节素材调研/ch2_南海_节拍表.md`。
- 其余各章：见下面「暂停中的工作」。

## 暂停中的工作（2026-10-10 起，先做序章 + 第1章 demo）

用户 2026-10-10 定：先把序章 + 第1章做成 demo 发布；下面四条线暂停，各自做到哪、没做什么、怎么接着做，都写在收尾记录里（`D:\大疆\docs\ai\context\`）：

| 线 | 收尾记录 | 一句话 |
|---|---|---|
| 第1–5章整章测试修复 | `20261010-093937-jojo-ch1-ch5-routes-wrapup_CN.md` | 第1章能打到最后一张图（含故意输重试）；~~第2章力量战管道修了没复测~~（2026-10-11 第2、3章整章重做、正常 / 故意输两条路线都打通）；第4–5章没跑 |
| 第6章–终章整章测试修复 | `20261010-093937-jojo-ch6-final-routes-wrapup_CN.md` | 第6、8章到章末；第7章审判第二段、第9章阿努比斯没打完；第10章–终章没跑；终章 DIO 4 处改动没验证 |
| 第2–6章背景重画 | `20261010-093937-jojo-bg-ch2-ch6-wrapup_CN.md` | 只拍了 24 张改前图，没动游戏文件。**第2章的四张（yacht_deck / freighter_deck / freighter_corridor / underwater）+ 新的 sea_fog、第3章的三张（singapore_street / singapore_hotel / cable_car）+ 新的 cable_view 已在 2026-10-11 重画接入**（`tools/bg_new/ch2_preview.py` / `ch3_preview.py` 出前后对照）；第4–6章没动 |
| 第7章–终章背景重画 | `20261010-093937-jojo-bg-ch7-final-wrapup_CN.md` | 只做了预览工具 `tools/bg_new/late_preview.py`，没动游戏文件 |

## 目录

| 路径 | 是什么 |
|---|---|
| `index.html`、`main.js` | 入口、标题、章节、设置、存档 |
| `engine/` | 引擎：画面、输入、声音、特效、地图、替身、战斗、剧情脚本 API、调试快照 |
| `story/` | 各章剧情（`prologue.js`、`ch01.js`…`final.js`）和地图（`stages*.js`） |
| `data/` | 构建出来的内嵌资源（图片、声音都是 base64，`file://` 也能读） |
| `assets/` | 构建用的图片 / 声音（`chars_new/`、`props_new/` 是游戏自己画的） |
| `tools/` | 构建、美术、测试脚本 |
| `规划.md`、`docs/技术约定.md` | 设计和接口约定 |
| `docs/交付/收尾_共享改动.md` | 共享引擎文件的逐条改动记录 |

原始素材在上一级的 `源码\ 角色图集\ 烘焙脚本\ 剧情分镜\ 音频\`，**只读，不能改**；游戏要改的地方都在游戏层做（见 `tools/art/` 里的 `art_holly_fix.py`、`art_npc.py` 的 `POLICE_CAP_AT` 等）。

## 改了代码以后

```powershell
# 资源构建（带锁，几个人同时改也不会互相覆盖）；看日志末尾：错误 0、警告 0、兜底 0
python -B tools\dev\full\locked_build.py art chars ui data check
# 序章路线（真实键盘，Playwright 自带的 Chromium）
python -B tools\dev\full\test_prologue.py prologue --out tools\_playtest\prologue
# 第1章路线
python -B tools\dev\full\test_ch1.py ch1
# 第2章路线（加 --lose 故意输：暗蓝之月输两次验「放水再来」）
python -B tools\dev\full\test_mid_early.py ch2 --out tools\_playtest\<名字>
# 单独打第2章某一战（调数值用，不当通关证据）
python -B tools\dev\full\dev_fight.py ch2 --entry ch2Darkmoon --out tools\_playtest\<名字>
# 第2章背景改前 / 改后预览
python -B tools\bg_new\ch2_preview.py after yacht_deck
# 第3章（新加坡）：整章路线 / 单独打一战（入口 ch3Devo、ch3Yellow）/ 背景预览
python -B tools\dev\full\test_mid_early.py ch3 --out tools\_playtest\<名字>
python -B tools\dev\full\dev_fight.py ch3 --entry ch3Yellow --out tools\_playtest\<名字>
python -B tools\bg_new\ch3_preview.py after singapore_street
# 牢房探索 / 抢漫画回归
python -B tools\dev\full\test_jail_explore.py
python -B tools\dev\full\repro_jail_grab.py
```

Python 一律带 `-B`（不写字节码）。

## 定下来的规矩（别改回去）

- K 是闪避（不做跳跃）；自由走动随时 Q 换队长；要打全部替身使者；战斗要爽、特效照原著。
- 承太郎用**重画前的卡通大头形象**（`tools/art/bake_art.py` 的 `JOTARO_ADULT = False`）。
- 五人落水时只露帽子、发型和上半张脸。
- 序章拘留所：铁栏有前后景（牢里的人在铁栏后、走廊上的人在前）；开打前掰铁栏出来，教学战在走廊打；紫色拳影墙只给白金之星。

## 记录

做了什么、为什么这么做：`D:\大疆\docs\ai\context\` 里 2026-10-08 起的 `*-jojo-*` 记录（最新的在最后）。
