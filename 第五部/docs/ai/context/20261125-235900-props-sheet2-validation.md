# 第二张道具图集接入验收

props_p5.py 按 1 行 3 列读取 props_sheet2.png，生成 gravel 14×7、bench 34×14、key 11×5 及元数据。透明阈值为 128，输出 alpha 仅为 0/255；钥匙保留源图深色轮廓，避免额外外描边挤掉齿和匙环。

街道碎石、长椅与钥匙改用道具 Actor。长椅脚底仍为 (340,160)，与钥匙共用纵深；钥匙图像仍覆盖原来的局部位置。赋予生命的时机、蝴蝶飞行路线和交互逻辑保留，碎石变青蛙时隐藏碎石，钥匙变蝴蝶时隐藏钥匙。

已执行 export_p5.py → bg_p5.py → build_p5.py → p5_play.js，序章和第1章均通关并回标题，控制台、资源请求、缺图缺字均为零。locked_build.py data check 通过 82 项资源合同，p5_pipeline_checks.py 通过 5 项，p5_regression.js 通过 89 项公共战斗与六人大招回归。

补充真实键盘侧面调查路线，最终报告与截图保存在 tools/dev/_out/props2/。已查看花盆、碎石、长椅钥匙各自 before/after 共六张截图，以及 bench_front_occlusion 截图，确认转化和主角站在椅前的遮挡。截图按现有约定保留本地，不加入 Git。

检查游戏/story/ 全部脚本后，没有发现其他代码绘制的场景道具。剩余几何绘制为 common.js 的目标箭头、背景底色及回退填色，p5_ch1_fights.js 的感觉失控闪光；p5_ch1.js 的矩形仅用于裁剪花盆图像。
