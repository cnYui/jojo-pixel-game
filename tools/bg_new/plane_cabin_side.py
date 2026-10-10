# -*- coding: utf-8 -*-
r"""plane_cabin_side —— 侧剖客舱（第1章 灰塔战，规划 §5.2.5、报告 06 §6 ⑥）。包 7B 新画；2026-10-10 scenes-early 按人的比例重画。

用户 2026-10-09 晚：“乘客并没有坐在椅子上（画图有问题），半个身子都在地下。”原来的座椅只有 24×17 px、乘客头肩
（16×18）站在过道地面上。重画后：
  · 座椅按站着的人（约 46 px）的比例：远侧一排靠窗座椅（3/4 后视、朝机头），椅脚落在远侧地板 y 150，
    椅面 y 138–143，椅背顶 y 127（白头巾套 127–131），每 32 px 一排（紧急出口那一段空着）；
  · 坐着的乘客 / 格雷·弗莱：头肩精灵画在 x = 座位中心、脚底 y 150、z 13（头肩下沿 y 137，头顶 y 119），
    椅背把肩膀以下挡住——椅背另外导出一张 seats（和舱内层里的座椅一模一样），剧情在地图 props 里用
    type 'image'、depth 150.5 画在乘客前面、过道上的人后面（world._collect 按 depth 排序）；
  · 舱壁：一排圆角舷窗 y 92–119（透明洞，窗外天空自己卷）、行李架 y 50–84、下沿的服务面板（阅读灯、
    氧气面罩舱口 y 84–89）、弧形天花板和灯带；中段紧急出口门（圆窗 (300,104)）；两头：x 0–22 洗手间门、
    x 618–640 驾驶舱门 + 出口灯；过道地毯 y 150–180（过道 y 156–166）；
  · 前景：近侧一排座椅的椅背顶 + 扶手（y 167–180，背光偏暗），挡住过道上人的脚下一点。
层：sky（wrap k 0.2 vx 60）→ cabin（pano 640，窗户是洞）；fg：front（pano）。另存 seats（剧情 props 用）。
锚点：seats [64,128,192,256,352,416,480,544]（规划 1-2 的 8 个乘客槽）、grayfly_seat 584、rows（全部座椅排）、
      sit {y: 150, z: 13}（坐姿）、seats_img_y（seats 图贴在哪一行）、toilet (20,150)、cockpit_door (620,150)、
      window (300,104)、bin (192,66)、masks（面罩舱口 x）、mask_y 89。
单独运行：python -B tools\bg_new\plane_cabin_side.py → tools\bg_new\_preview\plane_cabin_side_solo.png
"""
import sys
sys.dont_write_bytecode = True

import math  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from engine.core import W, H, gradient, hash01, hrange, mix  # noqa: E402
from engine import bg_asia as A  # noqa: E402

PW = 640                                         # 全景宽（不循环）
SEATS = [64, 128, 192, 256, 352, 416, 480, 544]  # 规划 1-2：乘客座位槽
GRAYFLY = 584
ROWS = [64, 96, 128, 160, 192, 224, 256, 352, 384, 416, 448, 480, 512, 544, 584]   # 全部远侧座椅排（中心 x）
EXIT_X = 304                                     # 紧急出口门中心
FLOOR = 150                                      # 远侧地板 / 过道地毯起点
SIT_Y, SIT_Z = 150, 15                           # 坐着的人：脚底 y、z（头肩下沿 y 135，头顶 y 117，脸露在椅背上面）
SEAT_TOP = 131                                   # 椅背顶（白头巾套上沿）
WIN_Y0, WIN_Y1 = 92, 119                         # 舷窗框
BIN_Y0, BIN_Y1 = 50, 84                          # 行李架
PSU_Y = 84                                       # 服务面板（阅读灯 / 面罩舱口）y 84–89
GROUND = 160
SEATS_Y0 = 124                                   # seats 图从这一行开始（到 FLOOR + 1）

C_CEIL = (226, 222, 212)
C_CEIL_D = (196, 192, 182)
C_LIGHT = (255, 248, 222)
C_BIN = (234, 230, 220)
C_BIN_D = (204, 200, 190)
C_BIN_LN = (172, 168, 160)
C_WALL = (216, 210, 196)
C_WALL_D = (188, 182, 170)
C_FRAME = (178, 172, 162)
C_SEAT = (46, 70, 140)
C_SEAT_O = (20, 30, 64)
C_SEAT_D = (34, 54, 112)
C_SEAT_HI = (84, 110, 184)
C_COVER = (238, 238, 242)
C_ARM = (150, 150, 158)
C_CARPET = (70, 84, 130)
C_CARPET_LN = (60, 72, 114)
C_DOOR = (198, 194, 186)
C_DOOR_O = (120, 116, 110)
C_SIGN = (36, 36, 42)
C_GREEN = (90, 220, 120)


def c4(c, a=255):
    return A._c4(c, a)


def window_xs():
    """每排座椅上方一扇窗（窗中心在座位中心左边 2 px），紧急出口门那一段不开窗。"""
    return [s - 2 for s in ROWS if abs(s - 2 - EXIT_X) > 24 and 24 < s - 2 < PW - 26]


# ============================================================ 座椅
def draw_seat(d, s, dim=1.0):
    """远侧一张座椅（3/4 后视、朝右 = 朝机头），中心 x = s。
    椅背 x s−10…s+7、y 127–143（白头巾套 127–131、椅背口袋、右侧面），椅面 + 扶手往右伸到 s+17，椅脚落在 y 150。"""
    def k(c):
        return tuple(int(v * dim) for v in c)
    x0, x1 = s - 10, s + 7
    # 椅脚、横梁（最先画，被椅面挡住上半）
    d.line((s - 6, 143, s - 7, FLOOR), fill=c4(k((92, 94, 104))))
    d.line((s + 12, 143, s + 13, FLOOR), fill=c4(k((92, 94, 104))))
    d.line((s - 6, FLOOR - 2, s + 13, FLOOR - 2), fill=c4(k((78, 80, 90))))
    d.point((s + 13, FLOOR), fill=c4(k((60, 62, 70))))
    # 椅面（朝右伸出去）
    d.rounded_rectangle((s - 2, 138, s + 17, 144), radius=2, fill=c4(k(C_SEAT_D)), outline=c4(k(C_SEAT_O)))
    d.line((s, 139, s + 15, 139), fill=c4(k(C_SEAT_HI)))
    d.line((s - 1, 143, s + 16, 143), fill=c4(k((26, 40, 84))))
    # 椅背（靠我们这一面是背面：口袋、小桌板）
    d.rounded_rectangle((x0, SEAT_TOP, x1, 144), radius=3, fill=c4(k(C_SEAT)), outline=c4(k(C_SEAT_O)))
    d.rectangle((x1 - 3, SEAT_TOP + 4, x1 - 1, 142), fill=c4(k(C_SEAT_D)))          # 右侧面（朝右转过去的厚度）
    d.line((x0 + 1, SEAT_TOP + 5, x0 + 1, 141), fill=c4(k(C_SEAT_HI)))             # 左边缘高光
    d.rectangle((x0 + 2, SEAT_TOP + 1, x1 - 3, SEAT_TOP + 4), fill=c4(k(C_COVER)))  # 白头巾套
    d.line((x0 + 2, SEAT_TOP + 4, x1 - 3, SEAT_TOP + 4), fill=c4(k((196, 198, 210))))
    d.point((x0 + 3, SEAT_TOP + 1), fill=c4(k((255, 255, 255))))
    d.rectangle((x0 + 2, SEAT_TOP + 6, x1 - 4, SEAT_TOP + 8), fill=c4(k((38, 58, 120))))    # 小桌板
    d.point(((x0 + x1) // 2 - 1, SEAT_TOP + 5), fill=c4(k((170, 170, 180))))              # 小桌板卡扣
    d.line((x0 + 2, 141, x1 - 4, 141), fill=c4(k((30, 46, 98))))                          # 椅背口袋
    d.line((x0 + 3, 140, x0 + 6, 138), fill=c4(k((236, 228, 190))))                       # 口袋里的杂志 / 安全须知
    d.point((x0 + 4, 139), fill=c4(k((200, 60, 60))))
    # 扶手（靠过道这一侧，离我们最近：画在最上面）
    d.rectangle((s + 3, 136, s + 18, 138), fill=c4(k(C_ARM)), outline=c4(k((88, 88, 98))))
    d.line((s + 4, 136, s + 17, 136), fill=c4(k((196, 196, 204))))
    d.line((s + 16, 138, s + 16, 141), fill=c4(k((110, 110, 120))))


def seats_img(rows=ROWS):
    """全部远侧座椅（透明底），剧情用 depth 150.5 画在坐着的人前面；舱内层里也画了同样一份。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    for s in rows:
        draw_seat(d, s)
    return im


# ============================================================ 舱内层
def _cabin(holes_out):
    img = A._new(PW, H, C_WALL)
    d = ImageDraw.Draw(img)
    # ---------- 天花板 0–50：弧形面板（越往上越暗 = 往我们这边弯过来）+ 中间灯带 + 安全带 / 禁烟灯 + 出风口
    gradient(img, (0, 0, PW, 46), [mix(C_CEIL_D, (150, 146, 138), 0.5), C_CEIL_D, C_CEIL], bands=6)
    d = ImageDraw.Draw(img)
    for x in range(16, PW, 64):                                      # 面板缝
        d.line((x, 0, x - 4, 45), fill=c4((180, 176, 168)))
    d.rectangle((0, 20, PW, 22), fill=c4(C_LIGHT))                   # 隐藏灯带（暖光）
    d.line((0, 23, PW, 23), fill=c4((236, 230, 212)))
    d.line((0, 19, PW, 19), fill=c4((204, 200, 190)))
    for x in range(48, PW - 30, 128):                                # 安全带 / 禁烟指示灯（小黑盒 + 两个图标）
        d.rectangle((x - 9, 26, x + 9, 32), fill=c4((48, 48, 56)), outline=c4((30, 30, 36)))
        d.rectangle((x - 7, 28, x - 2, 30), fill=c4((236, 236, 236)))
        d.line((x - 6, 29, x - 3, 29), fill=c4((60, 60, 60)))
        d.rectangle((x + 2, 28, x + 7, 30), fill=c4((236, 236, 236)))
        d.line((x + 3, 28, x + 6, 30), fill=c4((200, 60, 60)))
    for x in range(30, PW - 20, 32):                                 # 出风口
        d.ellipse((x - 2, 38, x + 2, 41), fill=c4((180, 176, 168)), outline=c4((150, 146, 138)))
        d.point((x, 39), fill=c4((90, 90, 96)))
    d.rectangle((0, 45, PW, 49), fill=c4((210, 206, 196)))
    d.line((0, 45, PW, 45), fill=c4((236, 232, 222)))
    # ---------- 行李架 y 50–84：舱门（每 64 px 一扇，门缝 + 把手）+ 下沿服务面板
    d.rectangle((0, BIN_Y0, PW, BIN_Y1), fill=c4(C_BIN))
    gradient(img, (0, BIN_Y0 + 1, PW, BIN_Y1 - 2), [C_BIN, mix(C_BIN, C_BIN_D, 0.6)], bands=5)
    d = ImageDraw.Draw(img)
    d.line((0, BIN_Y0, PW, BIN_Y0), fill=c4((248, 246, 238)))
    d.line((0, BIN_Y1 - 1, PW, BIN_Y1 - 1), fill=c4(C_BIN_LN))
    for x in range(48, PW, 64):
        d.line((x, BIN_Y0 + 1, x, BIN_Y1 - 2), fill=c4(C_BIN_LN))
        d.line((x + 1, BIN_Y0 + 1, x + 1, BIN_Y1 - 2), fill=c4((246, 244, 236)))
    for x in range(80, PW, 64):                                      # 把手（舱门中间偏下）
        d.rectangle((x - 5, BIN_Y1 - 9, x + 5, BIN_Y1 - 7), fill=c4((150, 146, 140)))
        d.line((x - 5, BIN_Y1 - 9, x + 5, BIN_Y1 - 9), fill=c4((200, 196, 188)))
    for x in range(16, PW, 64):                                      # 行李架上的座位号小牌
        d.rectangle((x, BIN_Y0 + 4, x + 6, BIN_Y0 + 7), fill=c4((70, 80, 110)))
        d.point((x + 2, BIN_Y0 + 5), fill=c4((240, 240, 240)))
        d.point((x + 4, BIN_Y0 + 5), fill=c4((240, 240, 240)))
    d.rectangle((0, PSU_Y, PW, PSU_Y + 5), fill=c4((200, 196, 186)))  # 服务面板
    d.line((0, PSU_Y + 5, PW, PSU_Y + 5), fill=c4((150, 146, 138)))
    for s in ROWS:                                                   # 每排：阅读灯 ×2、呼叫铃、面罩舱口
        d.point((s - 4, PSU_Y + 2), fill=c4((252, 246, 220)))
        d.point((s - 1, PSU_Y + 2), fill=c4((252, 246, 220)))
        d.point((s + 2, PSU_Y + 2), fill=c4((240, 120, 60)))
        d.rectangle((s + 5, PSU_Y + 1, s + 11, PSU_Y + 4), fill=c4((184, 180, 170)), outline=c4((156, 152, 144)))
    # ---------- 舱壁：窗带（上亮下暗）+ 窗台 + 下半护墙板
    gradient(img, (0, PSU_Y + 6, PW, 121), [mix(C_WALL, (176, 170, 160), 0.4), C_WALL, mix(C_WALL, (232, 226, 214), 0.5)],
             bands=5)
    gradient(img, (0, 123, PW, FLOOR), [mix(C_WALL_D, (210, 204, 192), 0.3), mix(C_WALL_D, (150, 144, 136), 0.5)], bands=5)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 120, PW, 123), fill=c4((226, 220, 208)))          # 窗台
    d.line((0, 120, PW, 120), fill=c4((244, 240, 230)))
    d.line((0, 123, PW, 123), fill=c4((160, 154, 146)))
    for x in range(48, PW, 64):                                       # 板缝 + 铆钉
        d.line((x, PSU_Y + 6, x, 119), fill=c4((200, 194, 182)))
        d.line((x, 124, x, FLOOR - 1), fill=c4((168, 162, 152)))
    for s in ROWS:                                                    # 护墙板上的暖风口（座位前面）
        for kk in range(3):
            d.line((s + 20, 140 + kk * 2, s + 25, 140 + kk * 2), fill=c4((150, 144, 136)))
    # ---------- 舷窗（圆角洞，3 px 窗框，有几扇遮光板拉下一截）+ 窗下透进来的一小片日光
    for i, x in enumerate(window_xs()):
        A._dither_rect(img, (x - 6, 121, x + 8, 128), mix(C_WALL, (255, 250, 232), 0.0), mix(C_WALL, (255, 250, 232), 0.6),
                       0.4)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x - 8, WIN_Y0, x + 8, WIN_Y1), radius=7, fill=c4(C_FRAME), outline=c4((150, 144, 136)))
        d.rounded_rectangle((x - 6, WIN_Y0 + 2, x + 6, WIN_Y1 - 2), radius=6, fill=c4((200, 194, 184)))
        shade = int(hash01(i, 7) * 3) * 4 if hash01(i, 8) < 0.4 else 0
        holes_out.append((x - 5, WIN_Y0 + 4 + shade, x + 5, WIN_Y1 - 4))
        if shade:
            d.rectangle((x - 5, WIN_Y0 + 4, x + 5, WIN_Y0 + 4 + shade), fill=c4((232, 228, 220)))
            d.line((x - 5, WIN_Y0 + 4 + shade, x + 5, WIN_Y0 + 4 + shade), fill=c4((176, 170, 160)))
            d.point((x, WIN_Y0 + 5 + shade), fill=c4((150, 146, 140)))
    # ---------- 紧急出口门（中段）：门框、把手、圆窗、红色说明条、上方出口灯
    ex0, ex1 = EXIT_X - 16, EXIT_X + 16
    d.rounded_rectangle((ex0, BIN_Y0 + 2, ex1, FLOOR - 1), radius=8, fill=c4(C_DOOR), outline=c4(C_DOOR_O))
    d.line((ex0 + 2, BIN_Y0 + 8, ex0 + 2, FLOOR - 3), fill=c4((228, 224, 216)))
    d.line((ex1 - 2, BIN_Y0 + 8, ex1 - 2, FLOOR - 3), fill=c4((170, 166, 158)))
    d.rectangle((EXIT_X + 6, 120, EXIT_X + 13, 125), fill=c4((120, 120, 128)), outline=c4((80, 80, 88)))
    d.line((EXIT_X + 7, 122, EXIT_X + 12, 122), fill=c4((170, 170, 178)))
    for yy in (130, 132):
        d.line((EXIT_X - 9, yy, EXIT_X + 9, yy), fill=c4((214, 60, 50)))
    d.ellipse((EXIT_X - 9, 95, EXIT_X + 9, 113), fill=c4(C_FRAME), outline=c4((150, 144, 136)))
    holes_out.append((EXIT_X - 6, 98, EXIT_X + 6, 110))
    d.rectangle((EXIT_X - 9, BIN_Y0 - 9, EXIT_X + 9, BIN_Y0 - 2), fill=c4(C_SIGN))
    d.rectangle((EXIT_X - 7, BIN_Y0 - 8, EXIT_X + 7, BIN_Y0 - 3), fill=c4(C_GREEN))
    for xx in range(EXIT_X - 5, EXIT_X + 6, 3):
        d.point((xx, BIN_Y0 - 6), fill=c4((235, 255, 235)))
    # ---------- 远侧地板（座椅脚下）+ 座椅
    d.rectangle((0, FLOOR - 4, PW, FLOOR - 1), fill=c4((96, 100, 116)))
    d.line((0, FLOOR - 4, PW, FLOOR - 4), fill=c4((120, 124, 140)))
    # （座椅最后贴上去：build() 里把调好色的 seats 图叠在舱内层上，和剧情 props 用的是同一张）
    # 座椅之间、出口前面的小东西：第一排前面的杂志架
    d.rectangle((26, 112, 46, FLOOR - 1), fill=c4((176, 170, 160)), outline=c4((128, 122, 114)))
    for kk, col in enumerate(((200, 60, 60), (60, 90, 170), (230, 200, 70), (70, 150, 90))):
        d.rectangle((28 + kk * 4, 106, 31 + kk * 4, 114), fill=c4(col))
    d.line((26, 115, 46, 115), fill=c4((140, 134, 126)))
    # ---------- 过道地毯 y 150–180
    gradient(img, (0, FLOOR, PW, H), [C_CARPET, mix(C_CARPET, (40, 48, 82), 0.45)], bands=5)
    d = ImageDraw.Draw(img)
    d.line((0, FLOOR, PW, FLOOR), fill=c4((120, 130, 170)))
    d.line((0, FLOOR + 1, PW, FLOOR + 1), fill=c4((96, 108, 152)))
    for y in range(FLOOR + 5, H, 6):
        off = (y // 6) % 2 * 4
        for x in range(off, PW, 8):
            d.point((x, y), fill=c4(C_CARPET_LN))
    for x in range(0, PW, 32):                                        # 过道引导灯
        d.point((x + 10, FLOOR + 2), fill=c4((176, 196, 236)))
    # ---------- 两头：左 洗手间门，右 驾驶舱门
    _bulkhead(d, img, 0, 22, toilet=True)
    _bulkhead(d, img, PW - 22, PW, toilet=False)
    A._tex_noise(img, (0, PSU_Y + 6, PW, FLOOR - 4), 0.03, 41)
    img = A._grade(img, sat=0.86, val=0.96)
    a = np.array(img)
    m = Image.new('L', (PW, H), 0)
    md = ImageDraw.Draw(m)
    for (x0, y0, x1, y1) in holes_out:
        if x0 == EXIT_X - 6:
            md.ellipse((x0, y0, x1, y1), fill=255)
        else:
            md.rounded_rectangle((x0, y0, x1, y1), radius=4, fill=255)
    a[np.array(m) > 0, 3] = 0
    return Image.fromarray(a, 'RGBA')


def _bulkhead(d, img, x0, x1, toilet):
    gradient(img, (x0, 24, x1, FLOOR), [mix(C_WALL_D, (176, 170, 160), 0.3), mix(C_WALL_D, (150, 144, 136), 0.5)], bands=4)
    d = ImageDraw.Draw(img)
    if toilet:
        d.line((x1 - 1, 24, x1 - 1, FLOOR), fill=c4((140, 134, 126)))
        d.rectangle((x0, 62, x1 - 4, FLOOR - 1), fill=c4((176, 172, 166)), outline=c4(C_DOOR_O))
        d.rectangle((x0 + 2, 64, x1 - 6, FLOOR - 3), fill=c4((186, 182, 176)))
        d.rectangle((x1 - 10, 104, x1 - 6, 110), fill=c4((110, 110, 118)))         # 把手
        d.rectangle((x1 - 13, 72, x1 - 6, 76), fill=c4(C_SIGN))                    # 有人 / 无人
        d.point((x1 - 9, 74), fill=c4((230, 70, 60)))
        d.point((x1 - 11, 74), fill=c4((230, 70, 60)))
        d.rectangle((x0 + 2, 46, x1 - 6, 56), fill=c4((70, 90, 150)))              # 洗手间标牌（男 / 女小人）
        d.point((x0 + 6, 48), fill=c4((240, 240, 240)))
        d.line((x0 + 6, 49, x0 + 6, 54), fill=c4((240, 240, 240)))
        d.point((x0 + 11, 48), fill=c4((240, 240, 240)))
        d.polygon([(x0 + 11, 49), (x0 + 9, 54), (x0 + 13, 54)], fill=c4((240, 240, 240)))
    else:
        d.line((x0, 24, x0, FLOOR), fill=c4((232, 228, 218)))
        d.rectangle((x0 + 4, 56, x1 - 1, FLOOR - 1), fill=c4((170, 166, 160)), outline=c4(C_DOOR_O))
        d.rectangle((x0 + 6, 58, x1 - 2, FLOOR - 3), fill=c4((182, 178, 172)))
        d.rectangle((x0 + 8, 76, x1 - 4, 86), fill=c4((40, 44, 56)))               # 门上的观察窗
        d.point((x0 + 9, 77), fill=c4((120, 130, 160)))
        d.ellipse((x0 + 10, 92, x0 + 13, 95), fill=c4((60, 60, 68)))               # 门镜
        d.rectangle((x0 + 7, 106, x0 + 10, 112), fill=c4((110, 110, 118)))         # 把手
        d.rectangle((x0 + 4, 38, x1 - 2, 46), fill=c4(C_SIGN))                     # 出口灯
        d.rectangle((x0 + 6, 40, x1 - 4, 44), fill=c4(C_GREEN))
        d.point((x0 + 9, 42), fill=c4((235, 255, 235)))
        d.point((x0 + 12, 42), fill=c4((235, 255, 235)))
        d.point((x0 + 15, 42), fill=c4((235, 255, 235)))


def _front():
    """前景：近侧一排座椅的椅背顶 + 扶手（y 167–180，比远侧大、背光偏暗），框住画面下沿。"""
    img = A._new(PW, H)
    d = ImageDraw.Draw(img)
    for s in [40 + 64 * i for i in range(10)]:
        if s < 30 or s > PW - 24:
            continue
        x0, x1 = s - 16, s + 14
        d.rounded_rectangle((x0, 167, x1, 190), radius=5, fill=c4((28, 42, 88)), outline=c4((12, 18, 40)))
        d.rectangle((x0 + 5, 168, x1 - 6, 174), fill=c4((170, 172, 182)))        # 头巾套（背光，偏灰）
        d.line((x0 + 5, 174, x1 - 6, 174), fill=c4((130, 132, 146)))
        d.line((x0 + 1, 171, x0 + 1, 180), fill=c4((54, 72, 130)))
        d.rectangle((x1 - 3, 172, x1 - 1, 180), fill=c4((20, 30, 64)))
        d.rectangle((x1 + 1, 175, x1 + 22, 178), fill=c4((66, 68, 80)), outline=c4((40, 40, 50)))   # 扶手
        d.line((x1 + 2, 175, x1 + 21, 175), fill=c4((112, 114, 126)))
    a = np.array(img)
    a[:166, :, 3] = 0
    return Image.fromarray(a, 'RGBA')


def build():
    holes = []
    cabin = _cabin(holes)
    front = _front()
    sky = A._cabin_sky()
    seats = A._grade(seats_img(), sat=0.86, val=0.96)       # 和舱内层同一套调色
    cabin.alpha_composite(seats)
    return cabin, front, sky, holes, seats


def export(ex, BJ):
    cabin, front, sky, holes, seats = build()
    fcrop = front.crop((0, 166, PW, H))
    scrop = seats.crop((0, SEATS_Y0, PW, FLOOR + 1))
    layers = [dict(type='wrap', image=ex.img('sky', sky), period=640, k=0.2, y=0, vx=60.0),
              dict(type='pano', image=ex.img('cabin', cabin), k=1.0, x=0, y=0)]
    fg = [dict(type='pano', image=ex.img('front', fcrop), k=1.0, x=0, y=166, alpha=1)]
    seats_key = ex.img('seats', scrop)
    anchors = dict(seats=list(SEATS), grayfly_seat=GRAYFLY, rows=list(ROWS), sit=dict(y=SIT_Y, z=SIT_Z),
                   seats_img=seats_key, seats_img_y=SEATS_Y0, seat_depth=SIT_Y + 0.5, seat_top=SEAT_TOP,
                   toilet=[20, 150], cockpit_door=[620, 150], window=[EXIT_X, 104], bin=[192, 66],
                   masks=[s + 8 for s in ROWS], mask_y=PSU_Y + 5, exit_door=[EXIT_X - 16, BIN_Y0, EXIT_X + 16, FLOOR],
                   windows=[[h[0], h[1], h[2], h[3]] for h in holes], walk_x=[16, 624], walls=[[0, 22], [618, 640]])
    st = ex.stage(PW, GROUND, (156, 166), layers, fg, anchors)
    if ex.check_on:
        a = np.array(cabin)[..., 3]
        hole_px = int((a == 0).sum())
        ex.checked('舱内层只有窗洞是透明的（%d 个洞）' % len(holes), int(((a > 0) & (a < 255)).sum()))
        ex.note('窗洞透明像素 %d' % hole_px)
        bad = 0
        for camX in (0, 80, 160, 240, 320):
            im = np.array(BJ.ref_render(st, ex.images, camX, 1.3).convert('RGB'))
            bad += int((im.sum(-1) == 0).sum())
        ex.checked('camX 0…320 整屏都有画（没有露黑）', bad)
        ex.checked('两头是墙（左 0–20 / 右 620–640 舱内层全不透明）', int((a[:, :20] < 255).sum() + (a[:, -20:] < 255).sum()))
        # seats 图和舱内层里的座椅逐像素一样（剧情 props 画在乘客前面时不会和背景错位）
        sa = np.array(seats)
        m = sa[..., 3] == 255
        ca = np.array(cabin)
        ex.checked('seats 图和舱内层里的座椅逐像素一致', int((np.abs(ca[m][:, :3].astype(int) - sa[m][:, :3].astype(int)).max(-1) > 0).sum())
                   + int((sa[..., 3] % 255 != 0).sum()))
        ex.checked('乘客槽都在座椅排上、在 16…624 之间', 0 if all(s in ROWS and 16 < s < 624 for s in SEATS + [GRAYFLY]) else 1)
    return st


if __name__ == '__main__':
    cabin, front, sky, holes, seats = build()
    out = Image.new('RGBA', (PW, H))
    out.alpha_composite(sky.crop((0, 0, PW, H)))
    out.alpha_composite(cabin)
    out.alpha_composite(front)
    os.makedirs(os.path.join(HERE, '_preview'), exist_ok=True)
    out.convert('RGB').resize((PW * 2, H * 2), Image.NEAREST).save(os.path.join(HERE, '_preview', 'plane_cabin_side_solo.png'))
    print('ok', len(holes), 'holes')
