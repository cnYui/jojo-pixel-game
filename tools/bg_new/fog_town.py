# -*- coding: utf-8 -*-
r"""fog_town —— 第5章「雾之镇」：巴基斯坦和伊朗边境一带的小镇，黄昏起了很重的雾（地图 fog_ch5，自由走动 + 正义战前后）。
2026-10-18 ch5-town 组按体验版精度重画（改前是 ch5_scenes.fogtown()：480 宽、一排平涂方块楼 + 一层椭圆雾）。
全镇其实都是被「正义」操纵的尸体，可看起来一切正常：窗里亮着黄灯、窗帘拉着、路灯一闪一闪，只是听不到一点声音。
整体青灰、低饱和；窗灯 / 路灯 / 煤气灯是画面里唯一的暖色。调色和画法零件在 ch5_town_parts.py（三张图共用）。

地图 640 宽、ground 160、可走带 y 146–176（石子路，压低了对比）；侧视平视，暗淡的天光从左上来（雾后面一个灰白的日影）。
竖向：楼脚 y 138；人行道石板 139–143、路缘石顶 144（亮）/ 侧面 145（暗）；146 起是石子路。路边的东西都站在 y ≤ 145。
从左到右（世界坐标）：
  x 0–42      镇外：一段塌了顶的土坯矮墙（墙头长着枯草）、歪着的木头路标、一块里程石；墙后面是雾里的荒地（中景）
  x 42–78     镇口牌坊（anchors.gate）：两根石柱（柱头线脚 + 石球）+ 铁拱（两道铁条之间一圈卷花）+ 两根短链吊着的铁牌，
              牌上的字（上一行像乌尔都文的笔画、下一行几个拉丁字母块）右半截被雾吃掉；门洞里是往雾里退远的土路 + 一排篱笆桩
  x 78–84     一小段矮墙
  x 84–152    H1 欧式两层灰泥楼：石板瓦坡顶 + 老虎窗 + 烟囱，楼角隅石，二楼三扇窗（中间那扇亮着、窗帘后面偶尔走过一个人影 strip），
              窗下的花箱里是枯花；一楼一扇亮着的窗（窗帘拉着）+ 镶板木门（两级台阶、门牌、投信口）；墙上的雨水管
  x 110       路灯（anchors.lamp）：铸铁灯柱（底座、搭梯子的横杆）+ 四面玻璃的灯笼，一闪一闪（strip，地上一圈光）
  x 152–204   H2 当地土坯两层：泥抹的圆角女儿墙、伸出墙面的木梁头两排、深窗洞（一扇亮着的木格窗）、钉铜钉的木门、
              二楼栏杆上搭着一条褪色的地毯、门边两只陶水罐（anchors.resident 在 H1 / H2 之间）
  x 204–246   井（anchors.well）：后面是一小块往里退的泥地院子（院子尽头一道篱笆，再往后是中景）；石砌井台 + 木辘轳
              （两根立柱、小坡顶、绕着绳子的轴、右边一个摇把），水桶吊在井口上方轻轻晃（strip）
  x 246–344   墓地（anchors.graves）：前面一道矮石墙（中间一个墓地门：两根石墩 + 半开的铁门），墙后的地往里退：四排新坟
              （新翻的褐土堆、土块），木十字架和圆顶石碑一排比一排小、一排比一排淡；一个挖开的坑 + 土堆 + 插着的铁锹、
              一辆装着土的独轮车；墓地尽头一道铁栅栏 + 两棵柏树
  x 344–368   公告板（anchors.board）：两根木柱、小坡顶，板上贴满了旧告示（发黄的纸、手写的行、一张画着人脸的寻人启事），
              右下角一张纸被风掀起来（strip）
  x 368–402   H3 窄两层小铺子：一楼木板门板关着、门头一块搪瓷招牌（像乌尔都文的笔画），二楼一扇亮着的窗
  x 402–440   钟楼（anchors.clock = 钟面中心）：石块砌的方塔、底下拱门、钟面（白底、刻度、停在 4 点 37 分的指针）+ 钟上的小檐，
              再往上是窄窗、钟亭（两个拱洞里看得见钟）、檐口、尖顶 + 风向标（越往上越淡进雾里）
  x 440–500   枯树（anchors.tree）：歪着的老树，树皮的裂纹、一个树洞，枝杈往上张开（树上落着几只乌鸦 strip）
  x 494–512   铸铁栅栏（矛头）；anchors.guest（荷尔·荷斯抽烟的地方）在这前面
  x 512–638   旅馆（三层 + 孟莎屋顶，镇上最气派）：一楼粗面石块、二三楼灰泥 + 壁柱 + 三道檐口；正中门廊（两根柱子，
              柱子上的横楣就是 HOTEL 招牌：深绿底金字，anchors.inn_sign），门廊顶上二楼的铁栏杆阳台；双开玻璃门（36 px 高）亮着
              （anchors.inn_door / inn），三级台阶、台阶两边两只枯了的花盆；门两边两盏铸铁煤气灯（strip 火苗跳）；
              两边各两扇一楼窗、二楼四扇带三角楣的窗、三楼五扇小窗（大多亮着）、屋顶三个老虎窗 + 两个烟囱
光：天光从左上来（雾里很散）：立面左沿亮右沿暗、檐口下一道影、地上的影子很淡；越高的地方雾越浓（屋顶、塔尖发白）。
可走带后面（y 106–145）往中间色收了 15 % 对比。

图层（从后往前）：
  sky         static           320×180 黄昏的雾天（上面暗青灰、往下发白）+ 雾后面一个灰白的日影
  far         pano   k 0.25    远景 400 宽：两道荒山的山脊、远处一片土坯平顶房（一个圆顶 + 一根宣礼塔），罩着很重的雾
  fog_far     wrap   k 0.25  vx 1.2   远处的雾墙（320 一圈）
  mid         pano   k 0.55    中景 496 宽：镇外的荒地 / 枯树 / 篱笆 / 农舍，镇里的一片屋顶（坡顶、平顶、烟囱）、
                               墓地后面的小教堂（尖塔）、两棵钻天杨、一座水塔、电线杆和电线；几点黄窗
  fog_mid     wrap   k 0.55  vx 2.0   中景前面的雾
  near        pano   k 1       整条街（640 宽，只有 0 / 255 透明度；y ≥ 130 整条不透明，上面的缺口里露中景）
  bucket      strip  k 1       井上的水桶轻轻晃（8 帧 @4 fps）
  notice      strip  k 1       公告板上被风掀起的纸角（8 帧 @4 fps）
  crows       strip  k 1       枯树上的乌鸦：转头、低头、张嘴、扑一下翅膀（8 帧 @4 fps）
  smoke       strip  k 1       H1 烟囱冒的一缕薄烟（8 帧 @4 fps）——死了的镇子看起来还在过日子
  cat         strip  k 1       墓地矮墙上坐着的黑猫，尾巴顺着墙垂下来慢慢甩（8 帧 @4 fps）
  fog_low     wrap   k 1     vx 3.0   贴着楼脚 / 街后半截的一层低雾（人物后面）
  night       tint   key 'night'      #0a1420 α 0.45：天黑（JS：数字 = α 乘数）
  night_lit   pano   k 1     key 'night'   天黑以后重新点亮的窗 + 一圈光晕（盖在夜色上面，暖光还是暖的）
  lamp        strip  k 1       一闪一闪的路灯：灯笼玻璃 + 雾里的光晕 + 地上一圈光（8 帧 @4 fps）
  gas_l/gas_r strip  k 1       旅馆门口两盏煤气灯的火苗 + 光晕（8 帧 @4 fps）
  curtain     strip  k 1       H1 二楼亮窗的窗帘：帘子轻轻动、一个人影走过去（8 帧 @4 fps）
  fg: mist_low  wrap k 1.2  vx 4.0   贴着地面飘的一层薄雾（人物前面，只在 y 156–180，很淡）
  fg: mist      wrap k 1.1  vx 6.0   key 'mist'：前景再加一层浓雾（正义战后撤掉）
光（lamp / gas / curtain / night_lit）放在夜色 tint 后面，所以天黑了灯还是亮的；其余会动的东西在 tint 前面，跟着变暗。

锚点（规格要求的名字一个不少；人站的点都在可走带里）：
  arrive [40,163]、gate [60,150]、lamp [110,149]、resident [150,160]、well [222,152]、graves [300,150]、board [356,150]、
  resident2 [380,162]、clock [420,86]（钟面中心；规格写 90，画面上钟面在 86）、tree [470,150]、guest [500,162]、
  inn [575,160]、inn_door [575,148]、inn_sign [575,89]（招牌中心；规格写 92，门加高到 36 px 后招牌上移了 3）
  另外多导出：walk_x [8,632]、lamp_light [110,85]（灯笼）、gate_box、well_box、graveyard_box、board_box、tower_box、
  clock_face [412,78,429,95]、tree_box、hotel_box、inn_door_box、sign_box、lane_back 139。
key：mist（前景浓雾）、night（夜色 + 重新点亮的窗）。
单独运行：python -B tools\bg_new\fog_town.py → tools\bg_new\_preview\ch5\fog_town_dev\*.png
"""
import sys
sys.dont_write_bytecode = True

import importlib.util  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
from functools import lru_cache  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def _parts():
    key = 'bg_new_ch5_town_parts'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, 'ch5_town_parts.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


P = _parts()

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from engine.core import gradient, hash01, hrange, mix, paste  # noqa: E402
from engine import bg_asia as A  # noqa: E402

V = P.V
C = A._c4
dk, lt, hl, vl, px, rect = P.dk, P.lt, P.hl, P.vl, P.px, P.rect
mul_box, cast_shadow, mottle, opaque = P.mul_box, P.cast_shadow, P.mottle, P.opaque
SHADOW_MUL, SOFT_MUL = P.SHADOW_MUL, P.SOFT_MUL

# ============================================================ 尺寸 / 坐标
W, H = 320, 180
PW = 640
GROUND = 160
WALK = (146, 176)
FAR_K, MID_K, FG_K = 0.25, 0.55, 1.2
FARW = P.layer_w(PW, FAR_K)       # 400
MIDW = P.layer_w(PW, MID_K)       # 496
BASE = 138                        # 楼脚
SIDE = 139                        # 人行道石板 139–143
KERB = 144                        # 路缘石顶（亮），145 侧面（暗）
STREET = 146                      # 石子路（= 可走带）
N_ANIM, FPS_ANIM = 8, 4.0

GATE = (42, 78)
H1 = (84, 152)
LAMP_X = 110
H2 = (152, 204)
YARD = (204, 246)
WELL_X = 222
GRAVE = (246, 344)
BOARD = (344, 368)
H3 = (368, 402)
TOWER = (404, 436)
CLOCK = (420, 86)
TREE_X = 470
FENCE = (494, 512)
HOTEL = (512, 640)
DOOR = (565, 585)                 # 旅馆双开门（含左、不含右）
GAS = (542, 608)                  # 两盏煤气灯的灯柱 x（站在台阶两边的人行道上）

ANCHORS = dict(
    arrive=[40, 163], gate=[60, 150], lamp=[LAMP_X, 149], resident=[150, 160], well=[WELL_X, 152],
    graves=[300, 150], board=[356, 150], resident2=[380, 162], clock=list(CLOCK), tree=[TREE_X, 150],
    guest=[500, 162], inn=[575, 160], inn_door=[575, 148], inn_sign=[575, 89],
    walk_x=[8, 632],
)
STAND = ('arrive', 'gate', 'lamp', 'resident', 'well', 'graves', 'board', 'resident2', 'tree', 'guest', 'inn',
         'inn_door')

# ============================================================ 调色
FOG = (150, 162, 166)
FOG_FAR = (146, 158, 162)
FOG_LO = (156, 166, 168)
INK = (36, 42, 48)
SKY_STOPS = [(52, 66, 76), (70, 86, 94), (96, 110, 116), (122, 136, 140), (144, 156, 158), (152, 163, 164)]
STUCCO = (164, 158, 142)          # H1 灰泥（褪了色的赭灰）
STUCCO_H = (170, 168, 156)        # 旅馆灰泥（更白一点）
TRIM = (184, 182, 170)            # 窗套 / 线脚（浅石色）
STONE = (132, 136, 132)
STONE_D = (106, 110, 108)
STONE_HI = (156, 160, 154)
ADOBE = (152, 132, 110)
ADOBE_D = (124, 106, 90)
ADOBE_HI = (172, 154, 132)
SLATE = (76, 86, 94)
SLATE_D = (60, 68, 76)
SLATE_HI = (98, 108, 116)
WOOD = (98, 82, 68)
WOOD_D = (72, 60, 52)
WOOD_HI = (126, 108, 90)
IRON = (38, 42, 46)
IRON_HI = (76, 82, 88)
GLASS_D = (52, 60, 66)
GLASS_R = (86, 98, 104)           # 暗窗玻璃上映的雾
LIT_HI = (255, 230, 158)
LIT = (240, 186, 100)
LIT_D = (198, 132, 66)
CURT = (220, 156, 86)             # 被屋里的灯照透的窗帘
CURT_D = (176, 112, 58)
SOIL = (108, 86, 66)
SOIL_D = (82, 64, 52)
SOIL_HI = (132, 108, 84)
GRASS = (92, 102, 92)
GRASS_D = (74, 84, 78)
FLAG = (128, 134, 132)            # 人行道石板
FLAG_S = (118, 124, 123)
CURB_HI = (146, 152, 150)
CURB_D = (92, 98, 100)
COB = (113, 120, 120)             # 石子路（低对比）
COB_HI = (120, 127, 126)
COB_LO = (106, 113, 114)
COB_GAP = (99, 106, 108)
GOLD = (214, 176, 92)
GOLD_D = (150, 116, 60)
NIGHT = ('#0a1420', 0.45)


def _lit_mask():
    return np.zeros((H, PW), bool)


# ============================================================ 天 / 远景 / 中景
@lru_cache(maxsize=1)
def sky_img():
    im = A._new(W, H)
    gradient(im, (0, 0, W, H), SKY_STOPS, bands=12)
    A._glow(im, 206, 30, 40, 26, (170, 180, 180), 40, rings=5)      # 雾后面的日影（不暖，灰白；不和牌坊 / 塔尖叠在一起）
    d = ImageDraw.Draw(im)
    d.ellipse((199, 23, 213, 37), fill=C((134, 148, 152)))
    d.ellipse((201, 25, 211, 35), fill=C((146, 158, 160)))
    return im


def _ridge(x, seed, base, amp):
    return base - amp * (0.5 + 0.3 * math.sin(x * 0.021 + seed) + 0.2 * math.sin(x * 0.057 + seed * 2.1)
                         + 0.12 * math.sin(x * 0.13 + seed * 0.7))


@lru_cache(maxsize=1)
def far_img():
    """远景：两道荒山的山脊 + 远处一片土坯平顶房（圆顶、宣礼塔），雾很重。"""
    im = A._new(FARW, H)
    d = ImageDraw.Draw(im)
    for x in range(FARW):                                          # 后一道山（更淡）
        y = int(round(_ridge(x, 1.3, 96, 30)))
        vl(d, x, y, 140, (118, 130, 134))
        px(d, x, y, (132, 144, 146))
    for x in range(FARW):                                          # 前一道山（矮、实一点）+ 山坡上的几道冲沟
        y = int(round(_ridge(x, 4.1, 108, 18)))
        vl(d, x, y, 140, (106, 118, 122))
        px(d, x, y, (124, 136, 138))
        if hash01(x // 7, 3) < 0.25:
            vl(d, x, y + 3, y + 3 + int(hrange(2, 8, x // 7, 4)), (98, 110, 114))
    x, i = 0, 0
    while x < FARW:                                                # 远处的平顶房
        w = int(hrange(8, 20, i, 11))
        top = int(hrange(110, 122, i, 12))
        col = ((122, 124, 120), (130, 128, 120), (116, 120, 120))[i % 3]
        rect(d, x, top, x + w - 1, 140, col)
        hl(d, x, x + w - 1, top, lt(col, 0.12))
        vl(d, x + w - 1, top, 140, dk(col, 0.9))
        for xx in range(x + 2, x + w - 2, 4):
            if hash01(i, xx, 13) < 0.5:
                px(d, xx, top + 4, dk(col, 0.82))
        x += w + (1 if i % 4 == 0 else 0)
        i += 1
    cx = 232                                                       # 圆顶 + 宣礼塔
    d.ellipse((cx - 9, 98, cx + 9, 116), fill=C((128, 134, 132)))
    rect(d, cx - 10, 108, cx + 10, 122, (124, 128, 126))
    vl(d, cx, 94, 98, (120, 126, 126))
    rect(d, cx + 16, 78, cx + 18, 122, (126, 132, 132))
    hl(d, cx + 15, cx + 19, 90, (118, 124, 124))
    d.polygon([(cx + 15, 78), (cx + 17, 72), (cx + 19, 78)], fill=C((120, 126, 126)))
    ys = np.arange(H, dtype=np.float32)[:, None]
    P.fog_wash(im, np.clip(0.42 + (130 - ys) / 140 * 0.2, 0.42, 0.6), FOG_FAR)
    a = np.array(im)
    a[141:, :, 3] = 0
    return Image.fromarray(a, 'RGBA')


def _bare_tree(d, x, base, h, seed, col, twig=None, spread=1.0):
    """光秃秃的树：一根干往上分两三杈，每杈再分小枝（斜线一段段画）。"""
    tw = twig or col

    def branch(x0, y0, ang, L, wdt, depth):
        x1 = x0 + math.cos(ang) * L
        y1 = y0 - math.sin(ang) * L
        n = max(1, int(L))
        for i in range(n + 1):
            u = i / n
            xx = x0 + (x1 - x0) * u
            yy = y0 + (y1 - y0) * u
            for k in range(max(1, int(round(wdt * (1 - 0.5 * u))))):
                px(d, round(xx) + k, round(yy), col if depth < 2 else tw)
        if depth >= 3 or L < 3:
            return
        for j in range(2 if depth else 3):
            da = hrange(-0.75, 0.75, seed, depth, j, int(x0), 1) * spread
            branch(x1, y1, ang + da, L * hrange(0.5, 0.72, seed, depth, j, 2), max(1, wdt - 1), depth + 1)

    branch(x, base, math.pi / 2 + hrange(-0.08, 0.08, seed, 9), h * 0.42, 2, 0)


@lru_cache(maxsize=1)
def mid_parts():
    """中景：镇外的荒地 / 枯树 / 篱笆 / 农舍，镇里的屋顶、小教堂、钻天杨、水塔、电线杆。返回 (图, 亮窗 mask)。"""
    im = A._new(MIDW, H)
    lit = np.zeros((H, MIDW), bool)
    d = ImageDraw.Draw(im)
    # 镇外（x 0–92）：一道地平线上的荒地、篱笆桩、两棵枯树、一间农舍的剪影
    rect(d, 0, 118, 92, 140, (98, 106, 102))
    for x in range(0, 93):
        px(d, x, 118, (112, 120, 116))
        if x % 9 == 4:
            vl(d, x, 111, 118, (84, 90, 88))
    for x in range(0, 92, 3):
        px(d, x, 113, (90, 96, 94))
    rect(d, 36, 104, 58, 118, (96, 100, 98))                        # 农舍
    d.polygon([(34, 104), (47, 95), (60, 104)], fill=C((86, 92, 92)))
    rect(d, 44, 109, 47, 118, (70, 76, 78))
    _bare_tree(d, 14, 118, 46, 3, (78, 84, 84))
    _bare_tree(d, 76, 118, 38, 5, (82, 88, 88))
    # 镇里：一排房子（坡顶 / 平顶交错），底 y 132
    pal = [(128, 128, 120), (120, 118, 110), (134, 130, 120), (116, 122, 120), (126, 116, 104)]
    x, i = 92, 0
    while x < MIDW:
        w = int(hrange(18, 34, i, 21))
        top = int(hrange(78, 100, i, 22))
        col = pal[i % len(pal)]
        if 206 <= x <= 262:                                        # 小教堂那块留出来
            x = 264
            continue
        rect(d, x, top, x + w - 1, 132, col)
        vl(d, x, top, 132, lt(col, 0.1))
        vl(d, x + w - 1, top, 132, dk(col, 0.86))
        kind = hash01(i, 23)
        if kind < 0.55:                                            # 坡顶（侧面看是一条斜线）
            rh = int(hrange(6, 12, i, 24))
            for xx in range(x - 1, x + w + 1):
                u = abs((xx - x) - w / 2) / (w / 2 + 1)
                yy = top - int(round(rh * (1 - u)))
                vl(d, xx, yy, top, (88, 96, 102))
                px(d, xx, yy, (104, 112, 118))
            if hash01(i, 25) < 0.6:                                # 烟囱
                cxx = x + int(hrange(3, w - 5, i, 26))
                rect(d, cxx, top - rh - 2, cxx + 2, top - 2, dk(col, 0.84))
        else:                                                      # 平顶 + 女儿墙
            hl(d, x - 1, x + w, top, lt(col, 0.15))
            hl(d, x - 1, x + w, top + 1, dk(col, 0.88))
        for yy in range(top + 6, 126, 10):                         # 窗
            for xx in range(x + 3, x + w - 4, 7):
                if hash01(i, xx, yy, 27) < 0.62:
                    if hash01(i, xx, yy, 28) < 0.16:
                        rect(d, xx, yy, xx + 2, yy + 3, (226, 176, 102))
                        lit[yy:yy + 4, xx:xx + 3] = True
                    else:
                        rect(d, xx, yy, xx + 2, yy + 3, dk(col, 0.7))
        x += w + (2 if hash01(i, 29) < 0.3 else 0)
        i += 1
    # 小教堂（墓地后面）：正面山墙 + 尖塔 + 一扇圆窗
    cx = 236
    rect(d, cx - 22, 92, cx + 22, 132, (132, 132, 126))
    d.polygon([(cx - 24, 92), (cx, 76), (cx + 24, 92)], fill=C((92, 100, 106)))
    rect(d, cx - 5, 60, cx + 5, 92, (138, 138, 132))
    vl(d, cx + 5, 60, 92, (118, 118, 114))
    d.polygon([(cx - 7, 60), (cx, 38), (cx + 7, 60)], fill=C((92, 100, 108)))
    vl(d, cx, 31, 38, (90, 96, 100))
    hl(d, cx - 3, cx + 3, 34, (90, 96, 100))
    rect(d, cx - 2, 66, cx + 1, 76, (84, 90, 94))
    d.ellipse((cx - 4, 98, cx + 4, 106), fill=C((92, 98, 104)))     # 圆窗（暗：教堂没点灯）
    d.ellipse((cx - 2, 100, cx + 2, 104), fill=C((76, 82, 88)))
    rect(d, cx - 4, 114, cx + 3, 132, (86, 82, 76))
    # 钻天杨（高、窄、深）+ 水塔 + 电线杆
    for (tx, top) in ((150, 40), (322, 46), (396, 52)):
        for y in range(top, 132):
            u = (y - top) / (132 - top)
            hw = 1 + int(round(4 * math.sin(math.pi * min(1, u * 1.15)) * (0.6 + 0.4 * u)))
            hl(d, tx - hw, tx + hw, y, (70, 80, 78))
            if (y + tx) % 5 == 0:
                px(d, tx - hw, y, (84, 94, 90))
    wx = 446
    rect(d, wx - 8, 62, wx + 8, 76, (110, 112, 110))
    d.polygon([(wx - 9, 62), (wx, 56), (wx + 9, 62)], fill=C((92, 96, 98)))
    for lx in (wx - 7, wx + 6):
        d.line((lx, 76, lx + (-3 if lx < wx else 3), 132), fill=C((92, 96, 96)))
    d.line((wx - 8, 96, wx + 8, 110), fill=C((96, 100, 100)))
    d.line((wx + 8, 96, wx - 8, 110), fill=C((96, 100, 100)))
    for (gx, gy) in ((120, 58), (282, 60), (372, 62), (470, 58)):
        vl(d, gx, gy, 132, (84, 90, 92))
        hl(d, gx - 4, gx + 4, gy + 3, (84, 90, 92))
    for (ax, ay, bx, by, sag) in ((0, 66, 120, 61, 6), (120, 61, 282, 63, 9), (282, 63, 372, 65, 6),
                                  (372, 65, 470, 61, 7), (470, 61, MIDW, 64, 5)):
        P.wire(d, ax, ay, bx, by, sag, (88, 94, 96))
    # 镇里的一排后墙（y 124–140），保证中景下沿是实的
    rect(d, 92, 132, MIDW - 1, 140, (110, 114, 110))
    ys = np.arange(H, dtype=np.float32)[:, None]
    P.fog_wash(im, np.clip(0.34 + (112 - ys) / 110 * 0.32, 0.34, 0.62), FOG, mask=lit)
    P.fog_wash(im, 0.22, FOG, mask=~lit)                            # 中景的黄窗也罩一点雾
    a = np.array(im)
    a[141:, :, 3] = 0
    return Image.fromarray(a, 'RGBA'), lit


def mid_img():
    return mid_parts()[0]


@lru_cache(maxsize=1)
def fogs():
    """四条雾带（都是 320 一圈、首尾相接）。"""
    far = P.fog_band(W, 72, 31, 128, prof=P.ramp(72, [(0, 0), (22, 0.7), (44, 1), (72, 0.7)]), cell=40, col=FOG_FAR)
    mid = P.fog_band(W, 72, 37, 150, prof=P.ramp(72, [(0, 0), (18, 0.55), (40, 1), (72, 0.85)]), cell=32, col=FOG)
    low = P.fog_band(W, 48, 41, 96, prof=P.ramp(48, [(0, 0), (16, 0.55), (34, 1), (48, 0.35)]), cell=32, stretch=5,
                     levels=(0, 26, 50, 74, 96), col=FOG_LO)
    thin = P.fog_band(W, 24, 45, 74, prof=P.ramp(24, [(0, 0), (8, 0.7), (16, 1), (24, 0.85)]), cell=20, stretch=3,
                      levels=(0, 24, 48, 74), col=FOG_LO)
    dense = P.fog_band(W, 140, 53, 128, prof=P.ramp(140, [(0, 0.2), (30, 0.75), (70, 1), (105, 0.8), (140, 0.5)]),
                       cell=40, stretch=4, levels=(0, 30, 56, 82, 106, 128), col=(158, 168, 170), lo=0.24, span=0.56)
    return dict(far=(far, 66), mid=(mid, 78), low=(low, 104), thin=(thin, 156), dense=(dense, 40))


# ============================================================ 近景零件
def slate_roof(im, x0, x1, eave, ridge, seed):
    """正对街的坡屋顶（看得见坡面）：一行行石板瓦（上沿亮、下沿暗、竖缝错开），檐口一道深影，屋脊一道亮线。"""
    d = ImageDraw.Draw(im)
    for y in range(ridge, eave + 1):
        u = (y - ridge) / max(1, eave - ridge)
        a, b = x0 + int(round((1 - u) * 3)), x1 - int(round((1 - u) * 3))
        r = (y - ridge) % 3
        for x in range(a, b + 1):
            c = SLATE if r == 1 else (SLATE_HI if r == 0 else SLATE_D)
            if r != 0 and (x + ((y - ridge) // 3) * 3) % 6 == 0:
                c = SLATE_D
            if hash01(seed, x, y // 3, 1) < 0.05:
                c = mix(c, (110, 104, 92), 0.5)                    # 补过的瓦 / 青苔
            px(d, x, y, c)
    hl(d, x0 + 3, x1 - 3, ridge, (124, 132, 138))
    hl(d, x0 - 1, x1 + 1, eave + 1, dk(SLATE_D, 0.8))
    hl(d, x0 - 1, x1 + 1, eave + 2, INK)


def chimney(d, x, top, w, base, col=(118, 104, 96)):
    rect(d, x, top, x + w - 1, base, col)
    vl(d, x, top, base, lt(col, 0.15))
    vl(d, x + w - 1, top, base, dk(col, 0.78))
    for y in range(top + 2, base, 3):
        hl(d, x, x + w - 1, y, dk(col, 0.86))
    rect(d, x - 1, top - 2, x + w, top - 1, lt(col, 0.1))
    hl(d, x - 1, x + w, top - 3, (90, 84, 82))
    for k in range(0, w - 1, 3):                                   # 烟囱罐
        rect(d, x + k, top - 6, x + k + 1, top - 3, (150, 110, 90))


def euro_window(im, lit, x, y, w, h, state, seed, wall, frame=TRIM, hood='flat', box=False, panes=(2, 3),
                curtain=True):
    """欧式窗：浅石窗套 + 窗台（下面一道影）+ 窗楣（flat 平 / pedi 三角 / arch 拱）；
    state：lit 亮着（暖光的玻璃 + 拉上的窗帘，中间一道缝最亮；窗棂是深色的剪影）/ dark 暗（玻璃映着雾）/ shut 关着百叶。
    box = 窗下挂一个花箱（里面是枯花）。lit 的像素记进 lit mask（夜里重新点亮、雾不罩）。"""
    d = ImageDraw.Draw(im)
    rect(d, x - 1, y - 1, x + w, y + h, frame)                       # 窗套
    vl(d, x - 1, y - 1, y + h, lt(frame, 0.2))
    vl(d, x + w, y - 1, y + h, dk(frame, 0.82))
    if state == 'lit':
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                u = abs((xx - x) - (w - 1) / 2) / max(1, (w - 1) / 2)
                c = LIT if u < 0.35 else LIT_D
                if curtain:
                    if u >= 0.28:                                  # 两片窗帘（竖褶）
                        c = CURT if (xx + seed) % 3 else CURT_D
                        if yy >= y + h - 3 and u > 0.7:
                            c = CURT_D
                    else:
                        c = LIT_HI if yy > y + 1 else LIT
                px(d, xx, yy, c)
        hl(d, x, x + w - 1, y, CURT_D if curtain else LIT_D)          # 帘头
        lit[y:y + h, x:x + w] = True
    elif state == 'dark':
        rect(d, x, y, x + w - 1, y + h - 1, GLASS_D)
        for k in range(min(w, h)):                                 # 映着雾的一道斜光
            xx, yy = x + w - 1 - k, y + k + 1
            if yy < y + h and hash01(seed, k, 4) < 0.8:
                px(d, xx, yy, GLASS_R)
        if curtain:
            vl(d, x, y, y + h - 1, (78, 80, 80))
            vl(d, x + w - 1, y, y + h - 1, (70, 72, 74))
    else:                                                          # 关着的百叶（褪色的灰绿）
        sc = (92, 110, 104)
        for yy in range(y, y + h):
            hl(d, x, x + w - 1, yy, sc if (yy - y) % 2 == 0 else dk(sc, 0.78))
        vl(d, x + w // 2, y, y + h - 1, dk(sc, 0.6))
    if state != 'shut':                                            # 窗棂
        mc = (60, 46, 36) if state == 'lit' else dk(frame, 0.7)
        nx, ny = panes
        for j in range(1, nx):
            vl(d, x + (w * j) // nx, y, y + h - 1, mc)
        for j in range(1, ny):
            hl(d, x, x + w - 1, y + (h * j) // ny, mc)
        if state == 'lit':
            for j in range(1, nx):
                lit[y:y + h, x + (w * j) // nx] = False
            for j in range(1, ny):
                lit[y + (h * j) // ny, x:x + w] = False
            lit[y, x:x + w] = False
    # 凹进去的影：上沿 + 左沿（只压暗的窗；亮窗不压，免得灯光发脏）
    if state != 'lit':
        mul_box(im, (x, y, x + w - 1, y), (0.72, 0.74, 0.8))
        mul_box(im, (x, y + 1, x, y + h - 1), (0.78, 0.8, 0.86))
    d = ImageDraw.Draw(im)
    rect(d, x - 2, y + h, x + w + 1, y + h + 1, frame)               # 窗台
    hl(d, x - 2, x + w + 1, y + h, lt(frame, 0.3))
    mul_box(im, (x - 1, y + h + 2, x + w + 2, y + h + 3), SHADOW_MUL)
    d = ImageDraw.Draw(im)
    if hood == 'flat':
        rect(d, x - 3, y - 4, x + w + 2, y - 2, frame)
        hl(d, x - 3, x + w + 2, y - 4, lt(frame, 0.3))
        mul_box(im, (x - 2, y - 1, x + w + 3, y - 1), SHADOW_MUL)
    elif hood == 'pedi':
        half = w // 2 + 3
        cx = x + (w - 1) / 2
        for k in range(half + 1):
            yy = y - 3 - int(k * 0.5)
            px(d, round(cx - half + k), yy, lt(frame, 0.25))
            px(d, round(cx + half - k), yy, frame)
        hl(d, x - 3, x + w + 2, y - 2, frame)
        mul_box(im, (x - 2, y - 1, x + w + 3, y - 1), SHADOW_MUL)
    elif hood == 'arch':
        r = w // 2 + 1
        cx = x + (w - 1) / 2
        for k in range(-r, r + 1):
            yy = y - 1 - int(round(math.sqrt(max(0, r * r - k * k)) * 0.5))
            px(d, round(cx + k), yy - 1, frame)
            px(d, round(cx + k), yy, dk(frame, 0.86))
    if box:                                                        # 花箱 + 枯花
        d = ImageDraw.Draw(im)
        rect(d, x - 1, y + h + 2, x + w, y + h + 4, (96, 78, 64))
        hl(d, x - 1, x + w, y + h + 2, (118, 98, 80))
        for k in range(w):
            if hash01(seed, k, 7) < 0.6:
                L = int(hrange(1, 4, seed, k, 8))
                vl(d, x + k, y + h + 2 - L, y + h + 1, (104, 98, 84))
                if hash01(seed, k, 9) < 0.3:
                    px(d, x + k, y + h + 1 - L, (128, 100, 96))


def panel_door(im, x, y, w, h, wood=WOOD, frame=TRIM, glass=False, lit=None, knob=True):
    """镶板木门（单 / 双开都行：w ≥ 14 时中间一道缝）：门套、上下几块凹板、门把 / 黄铜把手；glass = 上半截镶玻璃（亮）。"""
    d = ImageDraw.Draw(im)
    rect(d, x - 2, y - 2, x + w + 1, y + h - 1, frame)
    vl(d, x - 2, y - 2, y + h - 1, lt(frame, 0.2))
    vl(d, x + w + 1, y - 2, y + h - 1, dk(frame, 0.78))
    rect(d, x, y, x + w - 1, y + h - 1, wood)
    leaves = [(x, x + w // 2 - 1), (x + w // 2, x + w - 1)] if w >= 14 else [(x, x + w - 1)]
    for (a, b) in leaves:
        vl(d, a, y, y + h - 1, lt(wood, 0.15))
        vl(d, b, y, y + h - 1, dk(wood, 0.7))
        ph = (h - 6) // 3
        for j in range(3):
            py0 = y + 2 + j * (ph + 1)
            if glass and j == 0 and lit is not None:
                rect(d, a + 2, py0, b - 2, py0 + ph, LIT)
                for xx in range(a + 2, b - 1):
                    if (xx - a) % 3 == 1:
                        vl(d, xx, py0, py0 + ph, LIT_D)
                hl(d, a + 2, b - 2, py0 + ph // 2, (70, 50, 38))
                lit[py0:py0 + ph + 1, a + 2:b - 1] = True
                lit[py0 + ph // 2, a + 2:b - 1] = False
                continue
            rect(d, a + 2, py0, b - 2, py0 + ph, dk(wood, 0.88))
            hl(d, a + 2, b - 2, py0, dk(wood, 0.7))
            vl(d, a + 2, py0, py0 + ph, dk(wood, 0.74))
            hl(d, a + 2, b - 2, py0 + ph, lt(wood, 0.12))
    if knob:
        for (a, b) in leaves:
            kx = b - 2 if a == x else a + 2
            px(d, kx, y + h // 2, GOLD)
            px(d, kx, y + h // 2 + 1, GOLD_D)
    hl(d, x, x + w - 1, y + h - 1, dk(wood, 0.6))


def quoins(d, x, y0, y1, col, w=4, side='l'):
    """楼角的隅石：一大一小交替的石块（左角往右伸、右角往左伸）。"""
    for k, yy in enumerate(range(y0, y1, 4)):
        L = w if k % 2 == 0 else w - 2
        xa = x if side == 'l' else x - L + 1
        rect(d, xa, yy, xa + L - 1, min(y1, yy + 2), col)
        hl(d, xa, xa + L - 1, yy, lt(col, 0.2))
        hl(d, xa, xa + L - 1, min(y1, yy + 3), dk(col, 0.8))


# ============================================================ 近景：地面
def draw_ground(im):
    """人行道石板（139–143）+ 路缘石（144 亮 / 145 暗）+ 石子路（146–179：一行行小方石，近处大一点；对比很低，雾里有点湿）。"""
    d = ImageDraw.Draw(im)
    rect(d, 0, SIDE, PW - 1, KERB - 1, FLAG)
    mottle(im, (0, SIDE, PW - 1, KERB - 1), FLAG, FLAG_S, lt(FLAG, 0.05), 61, cell=4, lo=0.25, hi=0.75)
    d = ImageDraw.Draw(im)
    x = 0
    k = 0
    while x < PW:                                                   # 石板竖缝
        vl(d, x, SIDE, KERB - 1, dk(FLAG, 0.84))
        x += int(hrange(9, 15, k, 62))
        k += 1
    for x in range(0, PW, 2):
        px(d, x, SIDE + 2, dk(FLAG, 0.92))
    hl(d, 0, PW - 1, KERB, CURB_HI)
    hl(d, 0, PW - 1, KERB + 1, CURB_D)
    for x in range(5, PW, 16):
        px(d, x, KERB, dk(CURB_HI, 0.88))
        px(d, x, KERB + 1, dk(CURB_D, 0.85))
    a = np.array(im)
    y = STREET
    row = 0
    while y < H:
        rh = 3 if y < 160 else 4
        off = (row % 2) * 3
        for x0 in range(-off, PW, 6 if rh == 3 else 7):
            sw = (5 if rh == 3 else 6)
            f = hrange(0.975, 1.03, row, x0, 63)
            for yy in range(y, min(H, y + rh)):
                for xx in range(max(0, x0), min(PW, x0 + sw)):
                    c = COB
                    if yy == y and xx < x0 + sw - 1:
                        c = COB_HI
                    elif yy == y + rh - 2 and xx == x0 + sw - 1:
                        c = COB_LO
                    a[yy, xx, :3] = [min(255, int(v * f)) for v in c]
                    a[yy, xx, 3] = 255
                if 0 <= x0 + sw < PW:
                    a[yy, x0 + sw, :3] = COB_GAP
                    a[yy, x0 + sw, 3] = 255
            if 0 <= x0 + sw < PW and y + rh - 1 < H:
                pass
        if y + rh - 1 < H:
            a[y + rh - 1, :, :3] = np.where(np.arange(PW)[:, None] % 2 == 0, np.array(COB_GAP), np.array(COB_LO))
            a[y + rh - 1, :, 3] = 255
        y += rh
        row += 1
    im.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(im)
    for (x, y, w) in ((88, 166, 16), (262, 171, 20), (398, 158, 12), (532, 168, 18), (612, 174, 10)):  # 湿印子 / 小水洼
        for k in range(w):
            u = abs(k - w / 2) / (w / 2)
            for j in range(2 if u < 0.7 else 1):
                px(d, x + k, y + j, (104, 112, 114) if j == 0 else (110, 118, 120))
        hl(d, x + w // 3, x + w // 3 + 3, y, (126, 134, 134))
    for i in range(36):                                            # 落叶 / 纸屑 / 小石子
        x, y = int(hrange(0, PW, i, 64)), int(hrange(STREET + 2, H - 1, i, 65))
        px(d, x, y, ((118, 110, 96), (104, 108, 108), (124, 128, 126))[i % 3])


# ============================================================ 近景：镇口
def draw_outskirts(im):
    """镇外：一段塌了顶的土坯矮墙（x 0–42、78–84），墙头枯草；歪着的木头路标；一块里程石。"""
    d = ImageDraw.Draw(im)
    for (x0, x1, top) in ((0, 43, 118), (77, 85, 120)):
        for x in range(x0, x1):
            tt = top + int(round(3 * math.sin(x * 0.4) + hrange(-1.5, 1.5, x, 71)))
            if x0 == 0 and 14 < x < 26:
                tt += 5                                            # 塌了一块
            vl(d, x, tt, BASE, ADOBE)
            px(d, x, tt, ADOBE_HI)
        mottle(im, (x0, top - 3, x1 - 1, BASE), ADOBE, ADOBE_D, ADOBE_HI, 72 + x0, cell=3)
        d = ImageDraw.Draw(im)
        for yy in range(top + 6, BASE, 6):                         # 土坯砖的横缝（抹灰掉了的地方）
            for xx in range(x0 + (yy // 6 % 2) * 4, x1, 9):
                if hash01(xx, yy, 73) < 0.6:
                    hl(d, xx, xx + 5, yy, ADOBE_D)
        vl(d, x1 - 1, top, BASE, dk(ADOBE, 0.8))
    for i in range(30):                                            # 墙头的枯草
        x = int(hrange(0, 84, i, 74))
        if 43 <= x < 77:
            continue
        top = 118 + int(round(3 * math.sin(x * 0.4))) - (0 if not (14 < x < 26) else -5)
        L = int(hrange(2, 6, i, 75))
        for k in range(L):
            px(d, x + (k // 2) * (1 if i % 2 else -1), top - 1 - k, (126, 120, 98) if k < L - 1 else (146, 138, 112))
    # 路标（歪着）：一根木桩 + 两块指路板
    lay = A._new(PW, H)
    ld = ImageDraw.Draw(lay)
    for k in range(34):
        x = 30 + (k // 9)
        rect(ld, x, BASE + 4 - k, x + 1, BASE + 4 - k, WOOD if k % 5 else WOOD_D)
    rect(ld, 22, 110, 37, 114, (120, 104, 84))
    px(ld, 21, 112, (120, 104, 84))
    rect(ld, 29, 118, 42, 121, (110, 96, 78))
    px(ld, 43, 119, (110, 96, 78))
    for xx in range(24, 36, 3):
        hl(ld, xx, xx + 1, 112, (78, 68, 58))
    for xx in range(31, 41, 3):
        hl(ld, xx, xx + 1, 119, (78, 68, 58))
    P.ink(lay, INK, sides='br')
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    # 里程石（白顶红边的小石碑，褪成灰粉）
    rect(d, 6, 132, 13, KERB - 1, (168, 160, 150))
    d.pieslice((6, 128, 13, 136), 180, 360, fill=C((168, 120, 112)))
    hl(d, 7, 12, 135, (150, 104, 98))
    for xx in (8, 10):
        px(d, xx, 138, (110, 100, 96))
    vl(d, 13, 132, KERB - 1, (128, 120, 112))
    P.ground_shadow(im, 6, 13, KERB - 1, depth=2)


def draw_gate(im):
    """镇口牌坊：两根石柱 + 铁拱 + 吊着的铁牌；门洞里是往雾里退的土路。"""
    d = ImageDraw.Draw(im)
    a, b = GATE
    # 门洞里的远景（不透明，跟镜头一起走）：雾色渐变 + 土路 + 篱笆桩
    ox0, ox1 = a + 8, b - 9
    for y in range(66, BASE + 1):
        u = (y - 66) / (BASE - 66)
        c = mix((160, 170, 172), (138, 146, 146), u)
        hl(d, ox0, ox1, y, c)
    vpx, vpy = (ox0 + ox1) // 2, 110
    for y in range(vpy, BASE + 1):
        u = (y - vpy) / (BASE - vpy)
        hw = 1 + u * 7
        hl(d, round(vpx - hw), round(vpx + hw), y, mix((150, 156, 154), (128, 120, 106), u))
        if u > 0.3:
            px(d, round(vpx - hw * 0.4), y, mix((140, 144, 142), (112, 104, 92), u))
    for k in range(5):
        u = 0.15 + k * 0.2
        y = vpy + u * (BASE - vpy)
        x = vpx + (1 + u * 7) + 2 + u * 2
        vl(d, round(x), round(y - 2 - 6 * u), round(y), mix((140, 146, 146), (92, 88, 82), u))
        x2 = vpx - (1 + u * 7) - 2 - u * 2
        vl(d, round(x2), round(y - 2 - 6 * u), round(y), mix((140, 146, 146), (92, 88, 82), u))
    _bare_tree(d, vpx + 4, 108, 16, 21, (130, 138, 140))
    # 两根石柱：柱础、柱身（石块缝）、柱头线脚、石球
    lay = A._new(PW, H)
    ld = ImageDraw.Draw(lay)
    for (x0, seed) in ((a, 1), (b - 8, 2)):
        x1 = x0 + 7
        rect(ld, x0 - 1, 130, x1 + 1, BASE, STONE_D)                 # 柱础
        hl(ld, x0 - 1, x1 + 1, 130, STONE)
        rect(ld, x0, 72, x1, 129, STONE)
        for yy in range(76, 129, 6):
            hl(ld, x0, x1, yy, STONE_D)
            vl(ld, x0 + (3 if (yy // 6) % 2 else 5), yy + 1, min(128, yy + 5), STONE_D)
        vl(ld, x0, 72, 129, STONE_HI)
        vl(ld, x1, 72, 129, dk(STONE, 0.78))
        rect(ld, x0 - 1, 68, x1 + 1, 71, STONE_HI)                   # 柱头
        hl(ld, x0 - 1, x1 + 1, 71, STONE_D)
        rect(ld, x0, 66, x1, 67, STONE)
        ld.ellipse((x0 + 1, 59, x1 - 1, 66), fill=C(STONE))
        px(ld, x0 + 2, 61, STONE_HI)
        px(ld, x0 + 3, 60, STONE_HI)
        for i in range(10):                                        # 石面的斑点 / 青苔
            xx, yy = int(hrange(x0 + 1, x1, seed, i, 1)), int(hrange(74, 128, seed, i, 2))
            px(ld, xx, yy, (112, 122, 108) if i % 3 == 0 else STONE_D)
    P.ink(lay, INK, sides='all')
    im.alpha_composite(lay)
    # 铁拱：两道铁条之间一圈卷花
    lay = A._new(PW, H)
    ld = ImageDraw.Draw(lay)
    cx = (a + b) / 2 - 0.5
    span = (b - a) / 2 - 4
    for x in range(a + 4, b - 4):
        u = (x - cx) / span
        y1 = 64 - int(round(10 * math.sqrt(max(0.0, 1 - u * u))))
        px(ld, x, y1, IRON)
        px(ld, x, y1 + 5, IRON)
        if x % 4 == 0:
            ld.ellipse((x - 1, y1 + 1, x + 2, y1 + 4), outline=C(IRON))
    for x0 in (a + 3, b - 5):
        vl(ld, x0, 58, 68, IRON)
    for (xx, top) in ((a + 14, 64), (b - 15, 64)):                 # 吊牌的短链
        for k in range(0, 10, 2):
            px(ld, xx, top + k, IRON_HI)
            px(ld, xx, top + k + 1, IRON)
    rect(ld, a + 11, 74, b - 12, 85, (64, 70, 72))                 # 铁牌
    rect(ld, a + 11, 74, b - 12, 85, None, outline=IRON)
    hl(ld, a + 12, b - 13, 75, (84, 90, 92))
    P.urdu_line(ld, b - 14, a + 12, 79, (190, 186, 170), seed=5, h=3, dots=True)
    for k, xx in enumerate(range(a + 13, b - 13, 4)):              # 下一行：几个拉丁字母块
        rect(ld, xx, 81, xx + 2, 83, (190, 186, 170))
        px(ld, xx + 1, 82, (64, 70, 72))
    im.alpha_composite(lay)
    # 牌子右半截被雾吃掉（往雾色混得多）、铁拱也是越往右越淡
    a2 = np.array(im).astype(np.float32)
    for x in range(a + 8, b - 4):
        u = max(0.0, (x - (a + 18)) / 16.0)
        q = min(0.78, 0.2 + 0.7 * u)
        m = a2[56:87, x, 3] > 0
        sub = a2[56:87, x, :3]
        sub[m] = sub[m] * (1 - q) + np.array(FOG, np.float32) * q
    im.paste(Image.fromarray(np.clip(a2, 0, 255).astype(np.uint8), 'RGBA'))
    P.ground_shadow(im, a - 1, a + 8, KERB - 1, depth=3)
    P.ground_shadow(im, b - 9, b, KERB - 1, depth=3)


# ============================================================ 近景：H1 欧式两层楼 + 路灯
def draw_h1(im, lit):
    x0, x1 = H1
    slate_roof(im, x0 - 2, x1 + 1, 54, 36, 11)
    d = ImageDraw.Draw(im)
    rect(d, 104, 39, 118, 52, STUCCO)                              # 老虎窗
    d.polygon([(102, 40), (111, 33), (120, 40)], fill=C(SLATE_D))
    hl(d, 103, 119, 40, SLATE_HI)
    euro_window(im, lit, 108, 43, 7, 8, 'dark', 3, STUCCO, hood=None, panes=(2, 2), curtain=False)
    d = ImageDraw.Draw(im)
    chimney(d, 136, 26, 6, 44)
    V.facade(im, x0, x1, 55, BASE, STUCCO, 111, streaks=4)
    d = ImageDraw.Draw(im)
    quoins(d, x0, 56, BASE - 6, TRIM, side='l')
    quoins(d, x1 - 1, 56, BASE - 6, TRIM, side='r')
    K = P.K
    K.cornice(im, x0, x1 - 1, 55, TRIM, STUCCO, depth=2, dentils=True)
    K.cornice(im, x0, x1 - 1, 86, TRIM, STUCCO, depth=2, dentils=False)
    d = ImageDraw.Draw(im)
    rect(d, x0, 130, x1 - 1, BASE, STONE_D)                         # 勒脚
    hl(d, x0, x1 - 1, 130, STONE)
    for xx in range(x0 + 6, x1, 10):
        vl(d, xx, 131, BASE, dk(STONE_D, 0.86))
    for (wx, st, sd) in ((90, 'dark', 1), (110, 'lit', 2), (130, 'shut', 3)):
        euro_window(im, lit, wx, 64, 10, 15, st, sd, STUCCO, hood='flat', box=True)
    euro_window(im, lit, 90, 98, 13, 20, 'lit', 4, STUCCO, hood='flat', panes=(2, 3))
    panel_door(im, 119, 93, 14, 37, WOOD, TRIM)
    d = ImageDraw.Draw(im)
    rect(d, 116, 130, 136, 133, STONE)                              # 两级台阶
    hl(d, 116, 136, 130, STONE_HI)
    rect(d, 114, 134, 138, BASE, STONE_D)
    hl(d, 114, 138, 134, STONE)
    rect(d, 136, 98, 140, 101, (74, 84, 96))                        # 门牌（蓝搪瓷）
    px(d, 138, 99, (200, 204, 206))
    hl(d, 136, 140, 102, (120, 116, 106))
    rect(d, 123, 110, 128, 110, GOLD_D)                             # 投信口
    for (bx, c) in ((117, (214, 214, 206)), (115, (200, 202, 196))):  # 门口两只空牛奶瓶（看起来一切正常）
        rect(d, bx - 1, 127, bx, 129, c)
        px(d, bx - 1, 126, (180, 60, 50))
    for y in range(57, BASE - 2):                                  # 雨水管（右边）
        px(d, x1 - 4, y, (86, 92, 96))
        px(d, x1 - 3, y, (64, 70, 74))
        if y % 14 == 0:
            hl(d, x1 - 5, x1 - 2, y, (98, 104, 106))
    hl(d, x1 - 6, x1 - 2, BASE - 2, (86, 92, 96))
    P.K.brick_patch(im, 141, 112, 5, 4, 17)                        # 灰泥掉了一块，露出里面的砖
    P.fog_wash(im, np.where((np.arange(H)[:, None] >= 106) & (np.arange(H)[:, None] <= 118)
                            & (np.arange(PW)[None, :] >= 134) & (np.arange(PW)[None, :] <= 148), 0.45, 0.0), STUCCO)


def draw_lamp_post(im):
    """路灯：铸铁灯柱（底座、搭梯子的横杆、细柱）+ 四面玻璃的灯笼（亮的部分在 strip 里）。"""
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    x = LAMP_X
    rect(d, x - 3, 136, x + 3, KERB - 1, IRON)                      # 底座
    hl(d, x - 3, x + 3, 136, IRON_HI)
    rect(d, x - 2, 130, x + 2, 135, IRON)
    vl(d, x - 2, 130, 135, IRON_HI)
    for y in range(92, 130):
        px(d, x - 1, y, IRON_HI)
        px(d, x, y, IRON)
    hl(d, x - 5, x + 5, 95, IRON)                                  # 横杆
    px(d, x - 5, 94, IRON_HI)
    px(d, x + 5, 94, IRON)
    rect(d, x - 2, 90, x + 2, 91, IRON)                             # 灯笼底
    for y in range(79, 90):                                        # 灯笼（玻璃画暗，亮的在 strip）
        hw = 4 if y > 80 else 3
        hl(d, x - hw, x + hw, y, (70, 72, 70))
    for y in range(79, 90):
        px(d, x - 4, y, IRON)
        px(d, x + 4, y, IRON)
        px(d, x, y, IRON)
    d.polygon([(x - 5, 79), (x, 74), (x + 5, 79)], fill=C(IRON))   # 灯帽
    hl(d, x - 5, x + 5, 79, IRON_HI)
    px(d, x, 72, IRON)
    px(d, x, 73, IRON_HI)
    P.ink(lay, INK, sides='br')
    im.alpha_composite(lay)
    P.ground_shadow(im, x - 3, x + 3, KERB - 1, depth=2, slant=4)


# ============================================================ 近景：H2 土坯楼
def draw_h2(im, lit):
    x0, x1 = H2
    d = ImageDraw.Draw(im)
    for x in range(x0, x1):                                         # 泥抹的圆角女儿墙
        u = (x - x0) / (x1 - x0 - 1)
        tt = 58 - int(round(2 * math.sin(math.pi * u))) + (1 if x in (x0, x1 - 1) else 0)
        vl(d, x, tt, 62, ADOBE)
        px(d, x, tt, ADOBE_HI)
    V.facade(im, x0, x1, 62, BASE, ADOBE, 121, streaks=5, cell=4)
    d = ImageDraw.Draw(im)
    for yy in (64, 98):                                            # 木梁头两排
        for xx in range(x0 + 3, x1 - 3, 7):
            rect(d, xx, yy, xx + 2, yy + 1, WOOD)
            hl(d, xx, xx + 2, yy, WOOD_HI)
            mul_box(im, (xx + 1, yy + 2, xx + 3, yy + 3), SHADOW_MUL)
            d = ImageDraw.Draw(im)
    for (cx, cy, rx, ry, sd) in ((196, 110, 4, 3, 1), (160, 84, 3, 2, 2)):      # 掉了泥皮、露出土坯砖
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1 + hrange(-0.3, 0.2, sd, xx, yy):
                    c = ADOBE_D if (yy % 3 == 0 or (xx + (yy // 3) * 3) % 6 == 0) else (140, 116, 94)
                    px(d, xx, yy, c)
    # 二楼：两个深窗洞（一个亮着的木格窗）+ 栏杆上搭的地毯
    for (wx, on) in ((160, False), (186, True)):
        rect(d, wx - 1, 72, wx + 9, 85, ADOBE_D)
        rect(d, wx, 73, wx + 8, 84, (46, 42, 40) if not on else LIT_D)
        if on:
            for yy in range(73, 85):
                for xx in range(wx, wx + 9):
                    if (xx - wx) % 3 and (yy - 73) % 3:
                        px(d, xx, yy, LIT if (xx + yy) % 2 else LIT_HI)
                        lit[yy, xx] = True
                    else:
                        px(d, xx, yy, (88, 62, 44))
        else:
            for yy in range(73, 85, 3):
                hl(d, wx, wx + 8, yy, (70, 60, 52))
        hl(d, wx - 1, wx + 9, 72, dk(ADOBE_D, 0.8))
        vl(d, wx - 1, 72, 85, dk(ADOBE_D, 0.8))
        rect(d, wx - 2, 86, wx + 10, 87, ADOBE_HI)
    hl(d, x0 + 2, x1 - 3, 89, WOOD_D)                              # 栏杆横木
    for xx in range(x0 + 2, x1 - 2, 4):
        vl(d, xx, 89, 95, WOOD)
    rug = [(132, 74, 66), (150, 110, 70), (90, 70, 80)]
    for yy in range(89, 103):
        for xx in range(170, 183):
            c = rug[0]
            if xx in (170, 182) or yy in (101, 102):
                c = rug[1]
            elif (xx + yy) % 4 == 0:
                c = rug[2]
            elif abs(xx - 176) + abs(yy - 95) < 4:
                c = rug[1]
            px(d, xx, yy, mix(c, (150, 150, 150), 0.25))
    for xx in range(170, 183, 2):                                  # 地毯的穗
        px(d, xx, 103, (170, 156, 128))
    # 一楼：钉铜钉的木门 + 一个小暗窗 + 门边两只陶水罐
    door = (172, 100, 14, 38)
    rect(d, door[0] - 2, door[1] - 2, door[0] + door[2] + 1, BASE, ADOBE_D)
    rect(d, door[0], door[1], door[0] + door[2] - 1, BASE, (100, 76, 58))
    for xx in range(door[0], door[0] + door[2]):
        if (xx - door[0]) % 3 == 2:
            vl(d, xx, door[1], BASE, (82, 62, 48))
    vl(d, door[0] + door[2] // 2, door[1], BASE, (64, 50, 40))
    for yy in range(door[1] + 3, BASE - 2, 6):
        for xx in (door[0] + 2, door[0] + door[2] - 3):
            px(d, xx, yy, (170, 140, 80))
    px(d, door[0] + door[2] // 2 - 2, 120, (176, 146, 84))
    px(d, door[0] + door[2] // 2 + 1, 120, (176, 146, 84))
    rect(d, 157, 108, 165, 118, (52, 46, 42))
    for xx in range(158, 165, 2):
        vl(d, xx, 108, 118, (88, 72, 58))
    rect(d, 156, 119, 166, 120, ADOBE_HI)
    for (jx, jy, r) in ((191, 133, 4), (198, 134, 3)):
        d.ellipse((jx - r, jy - r, jx + r, jy + r + 1), fill=C((138, 92, 68)))
        px(d, jx - 1, jy - r + 1, (166, 118, 88))
        hl(d, jx - 1, jx + 1, jy - r - 1, (110, 72, 54))
        rect(d, jx - r + 1, BASE - 1, jx + r - 1, BASE, (110, 76, 58))
    vl(d, x1 - 1, 62, BASE, dk(ADOBE, 0.78))


# ============================================================ 近景：井院
def draw_yard(im):
    """井后面那一小块往里退的泥地院子（y 118–138），尽头一道木篱笆。"""
    d = ImageDraw.Draw(im)
    a, b = YARD
    for y in range(116, BASE + 1):
        u = (y - 116) / (BASE - 116)
        c = mix((134, 140, 136), (112, 104, 92), u ** 0.8)
        hl(d, a, b - 1, y, c)
    for i in range(40):
        x, y = int(hrange(a, b, i, 81)), int(hrange(120, BASE, i, 82))
        px(d, x, y, dk(im.getpixel((x, y))[:3], 0.9))
    for x in range(a, b, 3):                                        # 篱笆
        vl(d, x, 109, 117, (112, 108, 100))
        px(d, x, 108, (124, 120, 112))
    hl(d, a, b - 1, 111, (104, 100, 94))
    hl(d, a, b - 1, 115, (104, 100, 94))
    for x in range(a, b):                                           # 篱笆根的枯草
        if hash01(x, 83) < 0.5:
            px(d, x, 117, (120, 118, 100))


def draw_well(im):
    """石砌井台 + 木辘轳（两根柱、小坡顶、轴上缠着绳、右边摇把）；水桶在 strip 里。"""
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    cx = WELL_X
    x0, x1 = cx - 11, cx + 11
    rect(d, x0, 128, x1, 143, STONE)                                # 井身：几层石块
    for r, yy in enumerate(range(131, 144, 4)):
        hl(d, x0, x1, yy, STONE_D)
        off = 0 if r % 2 else 3
        for xx in range(x0 + off, x1, 6):
            vl(d, xx, yy + 1, min(143, yy + 3), STONE_D)
    for i in range(14):
        xx, yy = int(hrange(x0 + 1, x1, i, 91)), int(hrange(129, 143, i, 92))
        px(d, xx, yy, (112, 122, 106) if i % 2 else STONE_HI)
    vl(d, x0, 128, 143, STONE_HI)
    vl(d, x1, 128, 143, dk(STONE, 0.76))
    rect(d, x0 - 1, 125, x1 + 1, 127, STONE_HI)                     # 井口压顶 + 井口（暗）
    hl(d, x0 - 1, x1 + 1, 125, lt(STONE_HI, 0.15))
    hl(d, x0 + 1, x1 - 1, 126, (40, 44, 46))
    for (px0, sd) in ((x0 + 1, 0), (x1 - 2, 1)):                    # 立柱
        rect(d, px0, 100, px0 + 1, 124, WOOD)
        vl(d, px0, 100, 124, WOOD_HI)
    d.polygon([(x0 - 2, 101), (cx, 94), (x1 + 2, 101)], fill=C(WOOD_D))     # 小坡顶
    for k in range(x0 - 1, x1 + 2, 2):
        px(d, k, 100, WOOD)
    hl(d, x0 - 2, x1 + 2, 101, WOOD_HI)
    rect(d, x0 + 1, 107, x1 - 1, 110, WOOD)                         # 轴 + 缠着的绳（斜纹）
    for xx in range(x0 + 5, x1 - 4):
        px(d, xx, 108, (126, 116, 92) if xx % 2 else (100, 92, 76))
        px(d, xx, 109, (112, 102, 82) if xx % 2 else (92, 84, 70))
    hl(d, x0 + 1, x1 - 1, 107, WOOD_HI)
    vl(d, x0 + 4, 107, 110, WOOD_D)
    vl(d, x1 - 4, 107, 110, WOOD_D)
    rect(d, x1 + 1, 108, x1 + 3, 109, IRON)                          # 摇把
    vl(d, x1 + 3, 109, 114, IRON)
    hl(d, x1 + 3, x1 + 5, 114, WOOD_HI)
    P.ink(lay, INK, sides='all')
    im.alpha_composite(lay)
    P.ground_shadow(im, x0, x1 + 1, KERB - 1, depth=2, slant=4)


# ============================================================ 近景：墓地
GRAVE_ROWS = [(100, 0.5), (107, 0.62), (115, 0.78), (124, 0.95)]    # (坟脚 y, 大小)：从后往前


def draw_graveyard(im):
    a, b = GRAVE
    d = ImageDraw.Draw(im)
    # 墓地的地：往里退（y 94–129），越远越淡
    for y in range(94, 130):
        u = (y - 94) / 35
        c = mix((138, 146, 144), GRASS, u ** 0.7)
        hl(d, a, b - 1, y, c)
    for i in range(160):
        x, y = int(hrange(a, b, i, 101)), int(hrange(96, 129, i, 102))
        u = (y - 94) / 35
        px(d, x, y, mix((134, 142, 140), GRASS_D if i % 2 else (104, 112, 100), u))
    # 尽头：铁栅栏 + 两棵柏树
    for x in range(a, b, 3):
        vl(d, x, 86, 95, (112, 120, 122))
        px(d, x, 85, (124, 132, 134))
    hl(d, a, b - 1, 88, (112, 120, 122))
    for (tx, top) in ((a + 6, 50), (b - 8, 56)):
        for y in range(top, 96):
            u = (y - top) / (96 - top)
            hw = int(round(1 + 4.5 * math.sin(math.pi * min(1.0, u * 1.05)) ** 0.8))
            for x in range(tx - hw, tx + hw + 1):
                c = (92, 104, 100) if (x + y) % 3 else (102, 114, 110)
                if x == tx + hw:
                    c = (84, 96, 94)
                px(d, x, y, c)
    # 四排坟：每座 = 后面一个十字架 / 石碑 + 前面一个新翻的土堆
    lay = A._new(PW, H)
    ld = ImageDraw.Draw(lay)
    for ri, (yb, s) in enumerate(GRAVE_ROWS):
        step = int(round(16 * s)) + 2
        x = a + 4 + (ri % 2) * (step // 2)
        k = 0
        while x < b - 6:
            if 286 <= x <= 302 and ri == 3:                         # 门口那条路空着
                x += step
                continue
            sd = ri * 50 + k
            kind = hash01(sd, 1)
            mh = max(2, int(round(3 * s)))
            mw = max(4, int(round(11 * s)))
            # 墓碑 / 十字架（在土堆后面）
            if kind < 0.62:
                ch = int(round(hrange(11, 16, sd, 2) * s))
                cw = max(3, int(round(7 * s)))
                tilt = 1 if hash01(sd, 3) < 0.25 else 0
                for j in range(ch):
                    px(ld, x + (j * tilt) // 6, yb - mh - j, WOOD if j % 4 else WOOD_D)
                    px(ld, x + 1 + (j * tilt) // 6, yb - mh - j, WOOD_D)
                yy = yb - mh - ch + max(2, int(round(4 * s)))
                hl(ld, x - cw // 2 + ch * tilt // 6, x + cw // 2 + 1 + ch * tilt // 6, yy, WOOD_HI)
                hl(ld, x - cw // 2 + ch * tilt // 6, x + cw // 2 + 1 + ch * tilt // 6, yy + 1, WOOD_D)
            else:
                sh = int(round(hrange(8, 12, sd, 4) * s))
                sw = max(3, int(round(8 * s)))
                ld.rectangle((x - sw // 2, yb - mh - sh + sw // 2, x + sw // 2, yb - mh), fill=C(STONE))
                ld.pieslice((x - sw // 2, yb - mh - sh, x + sw // 2, yb - mh - sh + sw), 180, 360, fill=C(STONE))
                vl(ld, x + sw // 2, yb - mh - sh + sw // 2, yb - mh, STONE_D)
                for j in range(2):
                    hl(ld, x - sw // 2 + 2, x + sw // 2 - 2, yb - mh - sh + sw // 2 + 2 + j * 2, STONE_D)
            # 新翻的土堆
            for yy in range(yb - mh, yb + 1):
                u = (yy - (yb - mh)) / max(1, mh)
                hw = int(round(mw / 2 * (0.55 + 0.45 * math.sqrt(u))))
                hl(ld, x - hw, x + hw, yy, SOIL if yy > yb - mh else SOIL_HI)
            for j in range(int(5 * s)):
                xx = x + int(hrange(-mw / 2 + 1, mw / 2 - 1, sd, j, 5))
                yy = yb - int(hrange(0, mh, sd, j, 6))
                px(ld, xx, yy, SOIL_D if j % 2 else SOIL_HI)
            hl(ld, x - mw // 2, x + mw // 2, yb + 1, SOIL_D)
            x += step + int(hrange(-1, 3, sd, 7))
            k += 1
    # 挖开的坑 + 土堆 + 铁锹；装着土的独轮车
    gx, gy = 322, 121
    rect(ld, gx - 6, gy, gx + 6, gy + 3, (34, 30, 30))
    hl(ld, gx - 6, gx + 6, gy, SOIL_D)
    for yy in range(gy - 5, gy + 1):
        hw = 4 + (yy - gy + 5)
        hl(ld, gx + 8 - hw // 2, gx + 8 + hw // 2 + 2, yy, SOIL if yy > gy - 5 else SOIL_HI)
    for k in range(10):
        px(ld, gx + 10 + k // 4, gy - 5 - k, WOOD_HI if k < 8 else WOOD)
    rect(ld, gx + 8, gy - 3, gx + 10, gy - 1, (110, 114, 118))
    wx, wy = 262, 126
    ld.polygon([(wx, wy - 6), (wx + 12, wy - 6), (wx + 10, wy - 2), (wx + 2, wy - 2)], fill=C((92, 96, 100)))
    hl(ld, wx + 1, wx + 11, wy - 7, SOIL_HI)
    hl(ld, wx + 2, wx + 10, wy - 8, SOIL)
    ld.ellipse((wx - 1, wy - 3, wx + 3, wy + 1), outline=C(IRON))
    ld.line((wx + 11, wy - 5, wx + 17, wy - 2), fill=C(WOOD))
    ld.line((wx + 6, wy - 2, wx + 8, wy + 1), fill=C(WOOD_D))
    P.ink(lay, (54, 58, 60), sides='br')
    # 后排更淡（往雾里退）
    la = np.array(lay).astype(np.float32)
    for y in range(80, 130):
        u = max(0.0, min(1.0, (126 - y) / 30))
        q = 0.12 + 0.42 * u
        m = la[y, :, 3] > 0
        la[y, m, :3] = la[y, m, :3] * (1 - q) + np.array(FOG, np.float32) * q
    im.alpha_composite(Image.fromarray(np.clip(la, 0, 255).astype(np.uint8), 'RGBA'))
    # 前面的矮石墙（y 129–138）+ 门口两根石墩 + 半开的铁门
    d = ImageDraw.Draw(im)
    for x in range(a, b):
        if 288 <= x <= 300:
            continue
        top = 129 + (1 if hash01(x // 5, 103) < 0.3 else 0)
        vl(d, x, top, BASE, STONE)
        px(d, x, top, STONE_HI)
        px(d, x, top + 1, lt(STONE, 0.08))
    for yy in (132, 135):
        for x in range(a + (yy % 2) * 3, b, 6):
            if not (288 <= x <= 300):
                hl(d, x, x + 4, yy, STONE_D)
    for i in range(40):
        x, y = int(hrange(a, b, i, 104)), int(hrange(130, BASE, i, 105))
        if not (288 <= x <= 300):
            px(d, x, y, (112, 124, 108) if i % 3 == 0 else STONE_HI)
    for x in range(288, 301):                                       # 门口：墓地的土路一直接到人行道
        for y in range(124, BASE + 1):
            px(d, x, y, mix(GRASS, (112, 104, 92), (y - 124) / 14))
    lay = A._new(PW, H)
    ld = ImageDraw.Draw(lay)
    for px0 in (284, 301):
        rect(ld, px0, 119, px0 + 3, BASE, STONE)
        rect(ld, px0 - 1, 117, px0 + 4, 118, STONE_HI)
        vl(ld, px0 + 3, 119, BASE, STONE_D)
        vl(ld, px0, 119, BASE, STONE_HI)
    for k in range(9):                                             # 半开的铁门（往里斜着打开）
        x = 288 + k
        top = 121 - k // 3
        vl(ld, x, top, 136 - k // 3, IRON if k % 2 == 0 else (60, 64, 68))
        px(ld, x, top - 1, IRON_HI)
    hl(ld, 288, 296, 125, IRON)
    hl(ld, 288, 296, 132, IRON)
    P.ink(lay, INK, sides='br')
    im.alpha_composite(lay)
    vl(ImageDraw.Draw(im), b - 1, 129, BASE, dk(STONE, 0.76))


# ============================================================ 近景：公告板 / H3
NOTICE = (362, 116)                       # 被风掀起来的那张纸（左上角）


def draw_board_wall(im):
    """公告板后面一段刷灰的矮院墙（y 124–138），墙头一道压顶。"""
    d = ImageDraw.Draw(im)
    a, b = BOARD
    col = (136, 140, 134)
    rect(d, a, 124, b - 1, BASE, col)
    mottle(im, (a, 124, b - 1, BASE), col, dk(col, 0.92), lt(col, 0.06), 171, cell=3)
    d = ImageDraw.Draw(im)
    hl(d, a, b - 1, 123, lt(col, 0.2))
    hl(d, a, b - 1, 124, dk(col, 0.86))
    for i in range(6):
        x = int(hrange(a, b, i, 172))
        vl(d, x, 128, 128 + int(hrange(2, 7, i, 173)), dk(col, 0.84))


def draw_lot(im):
    """钟楼和旅馆之间一块往里退的空地（y 120–138）：泥地、枯草，尽头一道矮土墙。"""
    d = ImageDraw.Draw(im)
    a, b = TOWER[1] + 3, HOTEL[0]
    for y in range(118, BASE + 1):
        u = (y - 118) / (BASE - 118)
        hl(d, a, b - 1, y, mix((136, 142, 138), (110, 106, 94), u ** 0.8))
    for x in range(a, b):
        tt = 117 + int(round(1.5 * math.sin(x * 0.3)))
        vl(d, x, tt, 120, (128, 126, 116))
        px(d, x, tt, (140, 138, 128))
    for i in range(60):
        x, y = int(hrange(a, b, i, 181)), int(hrange(121, BASE, i, 182))
        L = int(hrange(1, 4, i, 183))
        for k in range(L):
            px(d, x, y - k, (126, 122, 100) if k < L - 1 else (140, 136, 112))


def draw_board(im):
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    a, b = BOARD
    for xx in (a + 2, b - 3):                                       # 两根柱子
        rect(d, xx, 100, xx + 1, KERB - 1, WOOD)
        vl(d, xx, 100, KERB - 1, WOOD_HI)
    d.polygon([(a - 1, 103), (a + 12, 96), (b, 103)], fill=C(WOOD_D))   # 小坡顶
    for xx in range(a, b, 2):
        px(d, xx, 102, WOOD)
    hl(d, a - 1, b, 103, WOOD_HI)
    rect(d, a, 104, b - 1, 129, (110, 92, 72))                      # 板
    rect(d, a, 104, b - 1, 129, None, outline=WOOD_D)
    hl(d, a + 1, b - 2, 105, (126, 106, 84))
    papers = [(a + 2, 106, 7, 9, (198, 190, 166)), (a + 10, 107, 6, 8, (212, 210, 200)),
              (a + 3, 117, 6, 10, (188, 176, 156)), (a + 9, 116, 8, 6, (176, 182, 184)),
              (a + 16, 106, 6, 7, (204, 196, 176)), (a + 10, 123, 7, 5, (196, 180, 170)),
              (a + 17, 114, 4, 6, (214, 206, 186))]
    for i, (x, y, w, h, c) in enumerate(papers):
        rect(d, x, y, x + w - 1, y + h - 1, c)
        hl(d, x, x + w - 1, y + h - 1, dk(c, 0.84))
        vl(d, x + w - 1, y, y + h - 1, dk(c, 0.9))
        for yy in range(y + 2, y + h - 1, 2):                      # 手写的行
            for xx in range(x + 1, x + w - 1):
                if hash01(i, xx, yy, 111) < 0.62:
                    px(d, xx, yy, (112, 104, 96))
        px(d, x + w // 2, y, ((180, 60, 50), (60, 90, 150), (200, 170, 60))[i % 3])   # 图钉
        if i == 0:                                                 # 寻人启事：一张人脸
            rect(d, x + 1, y + 1, x + w - 2, y + 5, (216, 210, 196))
            d.ellipse((x + 2, y + 1, x + 4, y + 4), fill=C((96, 88, 82)))
            hl(d, x + 1, x + 5, y + 5, (96, 88, 82))
    for (x, y) in ((a + 15, 121), (a + 5, 113)):                    # 撕剩下的纸角
        px(d, x, y, (196, 190, 172))
        px(d, x + 1, y, (196, 190, 172))
        px(d, x, y + 1, (196, 190, 172))
    P.ink(lay, INK, sides='br')
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    rect(d, 352, KERB - 2, 357, KERB - 1, (190, 184, 166))          # 掉在人行道上的一张
    px(d, 356, KERB - 3, (176, 170, 152))
    P.ground_shadow(im, a + 1, b - 1, KERB - 1, depth=2)


def draw_h3(im, lit):
    x0, x1 = H3
    col = (140, 150, 140)
    V.facade(im, x0, x1, 60, BASE, col, 131, streaks=3)
    d = ImageDraw.Draw(im)
    V.parapet(im, x0, x1 - 1, 57, col, 'plain')
    d = ImageDraw.Draw(im)
    rect(d, x0 + 22, 46, x0 + 23, 56, (70, 70, 72))                 # 屋顶的铁皮烟管
    hl(d, x0 + 21, x0 + 24, 46, (90, 90, 92))
    euro_window(im, lit, x0 + 11, 70, 11, 15, 'lit', 7, col, hood='flat')
    P.K.cornice(im, x0, x1 - 1, 93, TRIM, col, depth=2, dentils=False)
    d = ImageDraw.Draw(im)
    sx0, sx1 = x0 + 4, x1 - 5                                       # 搪瓷招牌（像乌尔都文的笔画）
    rect(d, sx0, 97, sx1, 104, (66, 98, 112))
    rect(d, sx0, 97, sx1, 104, None, outline=(206, 204, 192))
    P.urdu_line(d, sx1 - 2, sx0 + 2, 101, (220, 216, 196), seed=31, h=3)
    for (cx, cy) in ((sx0 + 6, 103), (sx1 - 9, 98)):                # 掉了瓷的黑斑
        px(d, cx, cy, (40, 44, 48))
    for yy in range(106, BASE - 1):                                 # 一楼的木门板（竖板）
        for xx in range(x0 + 3, x1 - 3):
            c = WOOD if (xx - x0) % 4 else WOOD_D
            if yy == 106:
                c = WOOD_HI
            px(d, xx, yy, c)
    hl(d, x0 + 3, x1 - 4, 121, (64, 54, 46))                        # 门闩 + 挂锁
    rect(d, x0 + 16, 122, x0 + 18, 124, (150, 140, 110))
    rect(d, x0 + 1, BASE - 1, x1 - 2, BASE, STONE_D)


# ============================================================ 近景：钟楼
def clock_hand(d, cx, cy, ang, L, col):
    for k in range(1, L + 1):
        px(d, round(cx + math.sin(ang) * k), round(cy - math.cos(ang) * k), col)


def draw_tower(im):
    a, b = TOWER
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    cx, cy = CLOCK
    rect(d, a - 3, 128, b + 2, BASE, STONE_D)                       # 塔基
    hl(d, a - 3, b + 2, 128, STONE)
    hl(d, a - 3, b + 2, 129, STONE_HI)
    rect(d, a, 26, b - 1, 127, STONE)                               # 塔身：一层层石块
    for r, yy in enumerate(range(30, 128, 4)):
        hl(d, a, b - 1, yy, STONE_D)
        off = 0 if r % 2 else 4
        for xx in range(a + off, b, 8):
            vl(d, xx, yy + 1, min(127, yy + 3), STONE_D)
    for i in range(60):
        xx, yy = int(hrange(a + 1, b - 1, i, 121)), int(hrange(28, 127, i, 122))
        px(d, xx, yy, (114, 126, 110) if i % 4 == 0 else (STONE_HI if i % 2 else dk(STONE, 0.9)))
    for side, x in (('l', a), ('r', b - 1)):
        quoins(d, x, 28, 126, STONE_HI, w=4, side=side)
    vl(d, b - 1, 26, 127, dk(STONE, 0.74))
    # 拱门（底下）
    dx0, dx1, dtop = cx - 7, cx + 6, 100
    for x in range(dx0, dx1 + 1):
        u = (x - (dx0 + dx1) / 2) / ((dx1 - dx0) / 2 + 0.5)
        top = dtop + 5 - int(round(5 * math.sqrt(max(0, 1 - u * u))))
        vl(d, x, top, 127, (78, 64, 54))
        px(d, x, top - 1, STONE_HI)
    for x in range(dx0 + 1, dx1):
        if (x - dx0) % 3 == 0:
            vl(d, x, dtop + 4, 127, (64, 52, 46))
    for yy in (108, 120):
        hl(d, dx0 + 1, dx1 - 1, yy, IRON)
    px(d, dx1 - 3, 114, GOLD_D)
    # 钟：石圈 + 白钟面 + 刻度 + 停在 4 点 37 分的指针 + 钟上的小檐
    d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=C(STONE_HI))
    d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), outline=C(STONE_D))
    d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=C((214, 212, 200)))
    d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), outline=C(IRON))
    for k in range(12):
        ang = k * math.tau / 12
        r = 7 if k % 3 else 6
        for rr in range(r, 8):
            px(d, round(cx + math.sin(ang) * rr), round(cy - math.cos(ang) * rr), (60, 60, 64))
    clock_hand(d, cx, cy, (4 + 37 / 60) / 12 * math.tau, 4, IRON)   # 时针
    clock_hand(d, cx, cy, 37 / 60 * math.tau, 6, IRON)              # 分针
    px(d, cx, cy, (150, 120, 60))
    d.polygon([(cx - 12, cy - 12), (cx, cy - 17), (cx + 12, cy - 12)], fill=C(SLATE))
    hl(d, cx - 12, cx + 12, cy - 12, SLATE_HI)
    # 窄窗、钟亭、檐口、尖顶、风向标
    for wy in (52, 34):
        rect(d, cx - 1, wy, cx, wy + 7, (60, 62, 64))
        hl(d, cx - 2, cx + 1, wy - 1, STONE_HI)
    rect(d, a - 1, 22, b, 25, STONE_HI)                             # 檐口
    hl(d, a - 1, b, 25, STONE_D)
    for (ax0, ax1) in ((a + 4, a + 13), (b - 14, b - 5)):           # 钟亭两个拱洞（压在檐口下面的塔身上：y 28–46）
        for x in range(ax0, ax1 + 1):
            u = (x - (ax0 + ax1) / 2) / ((ax1 - ax0) / 2 + 0.5)
            top = 30 - int(round(3 * math.sqrt(max(0, 1 - u * u))))
            vl(d, x, top + 3, 46, (44, 48, 52))
        bx = (ax0 + ax1) // 2
        d.pieslice((bx - 3, 34, bx + 3, 42), 180, 360, fill=C((110, 96, 70)))
        hl(d, bx - 3, bx + 3, 38, (90, 78, 58))
        for x in range(ax0, ax1 + 1, 2):                           # 百叶
            hl(d, x, x, 44, (70, 72, 74))
    d.polygon([(a - 1, 22), (cx - 0.5, 0), (b, 22)], fill=C(SLATE))     # 尖顶
    for y in range(4, 22, 3):
        u = y / 22
        hw = (b - a + 1) / 2 * u
        hl(d, round(cx - hw), round(cx + hw), y, SLATE_D)
    vl(d, cx, 0, 4, IRON)
    P.ink(lay, INK, sides='all')
    im.alpha_composite(lay)
    P.ground_shadow(im, a - 3, b + 2, KERB - 1, depth=3, slant=5)


# ============================================================ 近景：枯树 / 栅栏
CROW_WANT = [(452, 66, 1), (460, 56, -1), (486, 48, 1), (494, 62, -1), (478, 76, 1)]   # 想让乌鸦落的大概位置（x, 脚 y, 朝向）


@lru_cache(maxsize=1)
def tree_layer():
    """枯树（单独一层，透明底，描好墨线）：歪着的树干、树洞、露在地上的根、四根大枝一路分杈。"""
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    tx = TREE_X
    BK = ((112, 106, 98), (86, 82, 78), (64, 62, 60))
    for y in range(80, BASE + 1):                                   # 树干（往右歪一点、根部张开）
        u = (BASE - y) / (BASE - 80)
        w = int(round(7 + 6 * (1 - u) ** 4))
        x0 = tx - w // 2 + int(round(3 * u * u))
        for k in range(w):
            v = k / max(1, w - 1)
            c = BK[0] if v < 0.25 else (BK[1] if v < 0.7 else BK[2])
            if (k * 3 + y // 3) % 7 == 0:
                c = dk(c, 0.82)
            px(d, x0 + k, y, c)
    d.ellipse((tx - 1, 104, tx + 2, 110), fill=C((38, 34, 34)))     # 树洞
    for (x0_, y0_, x1_, y1_) in ((tx - 8, BASE, tx - 13, 142), (tx + 6, BASE, tx + 12, 141)):   # 露在地上的根
        d.line((x0_, y0_, x1_, y1_), fill=C(BK[1]), width=2)

    def limb(x0_, y0_, ang, L, wdt, depth, seed):
        x1_ = x0_ + math.cos(ang) * L
        y1_ = y0_ - math.sin(ang) * L
        n = max(1, int(L))
        for i in range(n + 1):
            u = i / n
            xx = x0_ + (x1_ - x0_) * u + math.sin(u * 3 + seed) * 1.2
            yy = y0_ + (y1_ - y0_) * u
            for k in range(max(1, int(round(wdt * (1 - 0.45 * u))))):
                px(d, round(xx) + k, round(yy), BK[1] if k == 0 else BK[2])
        if depth >= 3:
            return
        for j in range(2):
            da = hrange(0.25, 0.8, seed, depth, j, 1) * (1 if j else -1)
            limb(x1_, y1_, ang + da, L * hrange(0.5, 0.7, seed, depth, j, 2), max(1, wdt - 1), depth + 1, seed * 3 + j)

    limb(tx + 1, 82, math.radians(118), 26, 4, 0, 1)
    limb(tx + 3, 84, math.radians(62), 30, 4, 0, 2)
    limb(tx + 2, 96, math.radians(150), 18, 3, 1, 3)
    limb(tx + 5, 92, math.radians(28), 20, 3, 1, 4)
    P.ink(lay, (46, 46, 48), sides='br')
    return lay


@lru_cache(maxsize=1)
def crow_spots():
    """乌鸦落脚的地方：在想要的位置附近找一个真的树枝像素，上面 6 行是空的（乌鸦衬着天，看得清）。返回 [(x, 脚 y, 朝向)]。"""
    m = np.array(tree_layer())[..., 3] > 0
    out = []
    for (wx, wy, face) in CROW_WANT:
        best = None
        for y in range(wy - 10, wy + 11):
            for x in range(wx - 10, wx + 11):
                if not m[y, x] or m[y - 1, x]:
                    continue
                if m[y - 5:y - 1, x - 2:x + 2].any() or any(abs(x - o[0]) < 6 and abs(y - 1 - o[1]) < 5 for o in out):
                    continue
                dd = (x - wx) ** 2 + (y - wy) ** 2
                if best is None or dd < best[0]:
                    best = (dd, x, y - 1)
        if best:
            out.append((best[1], best[2], face))
    return out


def draw_tree(im):
    im.alpha_composite(tree_layer())
    P.ground_shadow(im, TREE_X - 8, TREE_X + 10, KERB - 1, depth=3, slant=6)


def draw_fence(im):
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    a, b = FENCE
    for x in range(a, b, 3):
        vl(d, x, 120, BASE, IRON)
        d.polygon([(x - 1, 120), (x, 116), (x + 1, 120)], fill=C(IRON))
    hl(d, a, b - 1, 124, IRON)
    hl(d, a, b - 1, 135, IRON)
    rect(d, a - 2, 116, a, BASE, STONE)
    rect(d, a - 3, 114, a + 1, 115, STONE_HI)
    P.ink(lay, INK, sides='br')
    im.alpha_composite(lay)


def draw_props(im):
    """街边的生活小物件（都贴着墙脚、站在人行道上，不进可走带）：H1 墙边靠着的一辆旧自行车、H2 门边的扫帚、
    H3 门口的长木凳（凳上一张叠好的报纸）、H2 屋顶的晾衣绳——看起来就是一个正常过日子的小镇。"""
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    bx, by = 136, 137                                              # 自行车（朝左，靠墙）
    for wx in (bx, bx + 13):
        d.ellipse((wx - 5, by - 5, wx + 5, by + 5), outline=C((44, 46, 50)))
        px(d, wx, by, (120, 124, 126))
    BK = (52, 56, 60)
    d.line((bx, by, bx + 5, by - 8), fill=C(BK))
    d.line((bx + 5, by - 8, bx + 11, by - 7), fill=C(BK))
    d.line((bx + 6, by - 5, bx + 10, by), fill=C(BK))
    d.line((bx + 10, by, bx + 13, by), fill=C(BK))
    d.line((bx + 11, by - 7, bx + 13, by), fill=C(BK))
    hl(d, bx + 9, bx + 13, by - 9, (70, 56, 48))
    d.line((bx + 5, by - 8, bx + 3, by - 11), fill=C(BK))
    hl(d, bx + 1, bx + 5, by - 11, (90, 92, 96))
    rect(d, bx - 3, by - 7, bx + 1, by - 4, (104, 88, 70))         # 车把前的小筐
    for (x0, y0, x1, y1) in ((168, 112, 165, 137),):                # 扫帚
        d.line((x0, y0, x1, y1 - 6), fill=C(WOOD_HI))
        for k in range(5):
            d.line((x1 - 2 + k, y1 - 6, x1 - 3 + k + (k - 2), y1), fill=C((150, 130, 92)))
    rect(d, 374, 133, 396, 134, WOOD_HI)                             # 长木凳 + 报纸
    hl(d, 374, 396, 135, WOOD_D)
    for lx in (376, 394):
        vl(d, lx, 136, 142, WOOD_D)
    rect(d, 380, 131, 386, 132, (190, 186, 172))
    hl(d, 381, 385, 131, (150, 146, 136))
    P.ink(lay, INK, sides='br')
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    V.tv_antenna(d, 194, 40, 16, (78, 82, 86))                      # H2 屋顶：电视天线 + 两只晒着的陶罐
    for (jx, r) in ((160, 3), (167, 2)):
        d.ellipse((jx - r, 55 - 2 * r, jx + r, 55), fill=C((132, 98, 78)))
        px(d, jx - 1, 55 - 2 * r + 1, (156, 120, 96))
    for (x0, x1) in ((134, 152), (372, 398)):
        P.ground_shadow(im, x0, x1, KERB - 1, depth=2)


# ============================================================ 近景：旅馆
def rustic(im, x0, x1, y0, y1, seed):
    """一楼粗面石块：8×4 的石块、深缝、每块左上亮右下暗。"""
    d = ImageDraw.Draw(im)
    rect(d, x0, y0, x1 - 1, y1, STONE)
    for r, yy in enumerate(range(y0, y1 + 1, 5)):
        hl(d, x0, x1 - 1, yy, STONE_D)
        off = 0 if r % 2 else 4
        for xx in range(x0 + off, x1, 9):
            vl(d, xx, yy + 1, min(y1, yy + 4), STONE_D)
            if xx + 1 < x1:
                vl(d, xx + 1, yy + 1, min(y1, yy + 4), STONE_HI)
        if yy + 1 <= y1:
            hl(d, x0, x1 - 1, yy + 1, lt(STONE, 0.1))
    mottle(im, (x0, y0, x1 - 1, y1), STONE, dk(STONE, 0.93), lt(STONE, 0.05), seed, cell=3)


def draw_hotel(im, lit):
    x0, x1 = HOTEL
    d = ImageDraw.Draw(im)
    # 孟莎屋顶 + 老虎窗 + 烟囱
    for y in range(8, 29):
        u = (y - 8) / 20
        a, b = x0 + 4 - int(u * 4), x1 - 4 + int(u * 4)
        for x in range(a, b):
            c = SLATE if (y % 3) else SLATE_HI
            if (y % 3) and (x + (y // 3) * 4) % 8 == 0:
                c = SLATE_D
            px(d, x, y, c)
    hl(d, x0 + 3, x1 - 4, 7, (118, 126, 132))
    for xx in range(x0 + 4, x1 - 4, 3):                             # 屋脊上的铸铁花边
        px(d, xx, 6, IRON)
        px(d, xx + 1, 5, IRON)
    for cxx in (536, 614):
        chimney(d, cxx, 0, 7, 8, col=(122, 108, 98))
    for (dx_, on) in ((528, True), (560, False), (590, True), (620, False)):
        rect(d, dx_ - 5, 13, dx_ + 5, 27, STUCCO_H)
        d.polygon([(dx_ - 7, 14), (dx_, 8), (dx_ + 7, 14)], fill=C(SLATE_D))
        euro_window(im, lit, dx_ - 3, 17, 6, 8, 'lit' if on else 'dark', dx_, STUCCO_H, hood=None, panes=(2, 2),
                    curtain=on)
        d = ImageDraw.Draw(im)
    # 楼身
    V.facade(im, x0, x1, 29, 97, STUCCO_H, 141, streaks=6)
    rustic(im, x0, x1, 98, BASE, 142)
    d = ImageDraw.Draw(im)
    for px_ in (x0, 552, 597, x1 - 4):                              # 壁柱
        P.K.pilaster(im, px_, 32, 96, TRIM, w=4)
    d = ImageDraw.Draw(im)
    P.K.cornice(im, x0 - 1, x1, 28, TRIM, STUCCO_H, depth=3, dentils=True)
    P.K.cornice(im, x0 - 1, x1, 58, TRIM, STUCCO_H, depth=2, dentils=False)
    P.K.cornice(im, x0 - 1, x1, 95, TRIM, STUCCO_H, depth=2, dentils=False)
    # 三楼五扇小窗、二楼四扇带三角楣的窗（中间是阳台门）
    for (wx, st) in ((522, 'lit'), (538, 'dark'), (571, 'lit'), (604, 'lit'), (620, 'shut')):
        euro_window(im, lit, wx, 38, 8, 13, st, wx, STUCCO_H, hood='flat', panes=(2, 2))
    for (wx, st) in ((521, 'lit'), (537, 'lit'), (604, 'dark'), (620, 'lit')):
        euro_window(im, lit, wx, 66, 10, 18, st, wx + 1, STUCCO_H, hood='pedi', panes=(2, 3))
    euro_window(im, lit, 568, 63, 14, 18, 'lit', 9, STUCCO_H, hood='arch', panes=(2, 3))     # 阳台门
    # 一楼两边各两扇窗
    for (wx, st) in ((518, 'lit'), (535, 'dark'), (603, 'lit'), (620, 'lit')):
        euro_window(im, lit, wx, 104, 11, 20, st, wx + 2, STONE_HI, frame=STONE_HI, hood='flat', panes=(2, 3))
    # 门廊：两根柱子 + 横楣（HOTEL 招牌）+ 门廊顶上的铁栏杆阳台
    d = ImageDraw.Draw(im)
    for cx_ in (556, 594):
        rect(d, cx_ - 2, 97, cx_ + 2, 133, TRIM)
        vl(d, cx_ - 2, 97, 133, lt(TRIM, 0.25))
        vl(d, cx_ + 2, 97, 133, dk(TRIM, 0.78))
        vl(d, cx_, 99, 131, dk(TRIM, 0.92))
        rect(d, cx_ - 3, 95, cx_ + 3, 96, lt(TRIM, 0.1))
        rect(d, cx_ - 3, 132, cx_ + 3, 133, dk(TRIM, 0.9))
        mul_box(im, (cx_ + 3, 97, cx_ + 4, 133), SHADOW_MUL)
        d = ImageDraw.Draw(im)
    rect(d, 552, 83, 598, 94, TRIM)                                 # 横楣
    hl(d, 552, 598, 83, lt(TRIM, 0.3))
    hl(d, 552, 598, 94, dk(TRIM, 0.7))
    sb = (556, 85, 594, 93)                                         # 招牌：深绿底金字 HOTEL
    rect(d, sb[0], sb[1], sb[2], sb[3], (40, 60, 54))
    rect(d, sb[0], sb[1], sb[2], sb[3], None, outline=GOLD_D)
    P.text_px(d, sb[0] + 3, sb[1] + 1, 'HOTEL', GOLD, gap=2, shadow=(24, 34, 30))
    for k in range(5):                                             # 金字上的亮点
        px(d, sb[0] + 3 + k * 7, sb[1] + 1, (240, 214, 140))
    mul_box(im, (553, 95, 598, 97), SHADOW_MUL)
    d = ImageDraw.Draw(im)
    P.K.iron_balcony(im, 552, 598, 82, rail_h=7, trim=TRIM)
    # 门（双开，上半截玻璃亮着）+ 门里的光落在门廊地上
    d = ImageDraw.Draw(im)
    rect(d, 560, 96, 590, 133, dk(STONE, 0.7))                      # 门廊里（暗）
    panel_door(im, DOOR[0], 97, DOOR[1] - DOOR[0], 36, (90, 62, 46), (150, 130, 110), glass=True, lit=lit)
    d = ImageDraw.Draw(im)
    for x in range(DOOR[0], DOOR[1]):                               # 门缝透出来的一线光
        px(d, x, 133, LIT_D)
    # 台阶（三级，越往下越宽）
    for (yy, h, ext) in ((133, 3, 4), (136, 3, 7), (139, 5, 10)):
        rect(d, 556 - ext, yy, 594 + ext, yy + h - 1, STONE)
        hl(d, 556 - ext, 594 + ext, yy, STONE_HI)
        vl(d, 594 + ext, yy, yy + h - 1, STONE_D)
    for (ux, sd) in ((548, 1), (601, 2)):                            # 台阶两边枯了的花盆
        rect(d, ux - 3, 126, ux + 3, 132, (122, 104, 92))
        hl(d, ux - 4, ux + 4, 125, (140, 122, 108))
        for k in range(6):
            L = int(hrange(2, 6, sd, k, 1))
            vl(d, ux - 3 + k, 125 - L, 124, (110, 104, 88))
    vl(d, x1 - 1, 29, BASE, dk(STUCCO_H, 0.7))
    # 墙上的水渍、裂缝
    for (sx, sy, L) in ((530, 60, 22), (612, 32, 26), (584, 60, 18)):
        for k in range(L):
            if hash01(sx, k, 151) < 0.85:
                px(d, sx + (k // 7), sy + k, dk(STUCCO_H, 0.86))


def draw_gas_lamps(im):
    """旅馆门口两盏铸铁煤气灯的灯柱和灯罩（火苗在 strip）。"""
    lay = A._new(PW, H)
    d = ImageDraw.Draw(lay)
    for x in GAS:
        rect(d, x - 2, 138, x + 2, KERB - 1, IRON)
        hl(d, x - 2, x + 2, 138, IRON_HI)
        for y in range(108, 138):
            px(d, x, y, IRON)
            px(d, x - 1, y, IRON_HI if y % 9 else IRON)
        rect(d, x - 3, 106, x + 2, 107, IRON)
        for y in range(97, 106):
            hw = 3 if y > 98 else 2
            hl(d, x - hw, x + hw - 1, y, (78, 76, 70))
            px(d, x - hw, y, IRON)
            px(d, x + hw - 1, y, IRON)
        d.polygon([(x - 4, 97), (x - 0.5, 93), (x + 3, 97)], fill=C(IRON))
        px(d, x - 1, 92, IRON)
    P.ink(lay, INK, sides='br')
    im.alpha_composite(lay)
    for x in GAS:
        P.ground_shadow(im, x - 2, x + 2, KERB - 1, depth=2, slant=4)


# ============================================================ 组装近景
@lru_cache(maxsize=1)
def near_parts():
    """返回 (近景, 亮窗 mask)。"""
    im = A._new(PW, H)
    lit = _lit_mask()
    draw_ground(im)
    draw_outskirts(im)
    draw_gate(im)
    draw_h1(im, lit)
    draw_h2(im, lit)
    draw_yard(im)
    draw_graveyard(im)
    draw_board_wall(im)
    draw_board(im)
    draw_h3(im, lit)
    draw_tower(im)
    draw_lot(im)
    draw_fence(im)
    draw_hotel(im, lit)
    draw_tree(im)
    draw_lamp_post(im)
    draw_well(im)
    draw_gas_lamps(im)
    draw_props(im)
    # 楼和天 / 中景交界的地方描一圈墨线（剪影清楚；后面罩雾时一起变淡）
    a = np.array(im)
    m = a[..., 3] > 0
    up = np.zeros_like(m)
    up[1:] = m[:-1]
    lf = np.zeros_like(m)
    lf[:, 1:] = m[:, :-1]
    rt = np.zeros_like(m)
    rt[:, :-1] = m[:, 1:]
    edge = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & lf & rt)
    edge[:, 0] = False
    edge[:, -1] = False
    edge[BASE:] = False
    a[edge, :3] = (a[edge, :3].astype(np.float32) * 0.62).astype(np.uint8)
    im = Image.fromarray(a, 'RGBA')
    # 光：亮窗在雾里的一圈暖光（往暖色混）
    for (cx, cy, rx, ry) in _glows(lit):
        P.add_light(im, cx, cy, rx, ry, (236, 180, 104), 0.32, steps=3, mode='mix', power=1.6)
    # 雾：越高越浓；整体先罩一层
    ys = np.arange(H, dtype=np.float32)[:, None]
    amt = 0.1 + 0.4 * np.clip((96 - ys) / 90, 0, 1)
    P.fog_wash(im, amt, FOG, mask=lit)
    P.fog_wash(im, np.clip(0.04 + (96 - ys) / 90 * 0.18, 0, 0.22), FOG, mask=~lit)   # 亮窗也罩一点（远处的更淡）
    P.compress_band(im, 106, KERB + 1, 0.85, (122, 128, 128))
    pre = np.array(im)
    im = A._grade(im, sat=0.9, val=1.0)
    a = np.array(im)
    a[lit] = pre[lit]                                              # 亮窗不降饱和（画面里唯一的暖色）
    return opaque(Image.fromarray(a, 'RGBA')), lit


def _glows(lit):
    """按亮窗的连通块给光晕：每块中心 + 半径（窗越大光越大）。"""
    from scipy import ndimage
    lab, n = ndimage.label(ndimage.binary_dilation(lit, iterations=1))
    out = []
    for sl in ndimage.find_objects(lab):
        if sl is None:
            continue
        ys, xs = sl
        h, w = ys.stop - ys.start, xs.stop - xs.start
        if h * w < 6:
            continue
        out.append(((xs.start + xs.stop) / 2, (ys.start + ys.stop) / 2, w * 0.9 + 4, h * 0.7 + 4))
    return out


def near_img():
    return near_parts()[0]


@lru_cache(maxsize=1)
def night_lit_img():
    """天黑以后重新点亮的窗：近景里亮窗的像素原样 + 一圈半透明的暖光（夜色 tint 后面画，暖光不被压暗）。"""
    near, lit = near_parts()
    a = np.array(near)
    out = np.zeros_like(a)
    out[lit] = a[lit]
    lay = Image.fromarray(out, 'RGBA')
    g = A._new(PW, H)
    for (cx, cy, rx, ry) in _glows(lit):
        gl = A._new(PW, H)
        A._glow(gl, cx, cy, rx + 3, ry + 3, (232, 170, 92), 70, rings=3)
        ga = np.array(gl)
        bay = A._bayer(PW, H)
        ga[..., 3] = np.where(ga[..., 3] > bay * 90, ga[..., 3], 0)
        g.alpha_composite(Image.fromarray(ga, 'RGBA'))
    g.alpha_composite(lay)
    ga = np.array(g)
    ga[lit] = a[lit]
    return Image.fromarray(ga, 'RGBA')


# ============================================================ 会动的（strip，世界坐标，k 1）
LAMP_BOX = (90, 66, 132, 156)
LAMP_LV = (1.0, 0.82, 1.0, 0.3, 0.95, 0.0, 0.62, 0.86)            # 8 帧的亮度：一闪一闪、有一帧灭了


def lamp_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    lv = LAMP_LV[f]
    x = LAMP_X
    bay = A._bayer(PW, H)
    if lv > 0.05:                                                   # 雾里的光晕（半透明，Bayer 抖动）
        R = 9 + 9 * lv
        for yy in range(int(84 - R), int(84 + R) + 1):
            for xx in range(int(x - R), int(x + R) + 1):
                r = math.hypot(xx - x, (yy - 84) * 1.15) / R
                if r < 1:
                    q = (1 - r) ** 1.5 * lv
                    if q > bay[yy, xx] * 0.9:
                        d.point((xx, yy), fill=(255, 220, 150, int(36 + 70 * q)))
        for yy in range(SIDE, 156):                                 # 地上一圈光
            for xx in range(x - 20, x + 21):
                r = math.hypot((xx - x - 2) / 20.0, (yy - 146) / 9.0)
                if r < 1 and (1 - r) * lv > bay[yy, xx] * 0.8:
                    d.point((xx, yy), fill=(255, 214, 140, int(30 + 40 * (1 - r) * lv)))
    gc = mix((70, 72, 70), LIT_HI, lv) if lv > 0.05 else (64, 66, 64)
    for y in range(80, 90):                                         # 灯笼玻璃（三格）
        for xx in (x - 3, x - 2, x - 1, x + 1, x + 2, x + 3):
            c = gc if lv < 0.5 else (LIT_HI if abs(xx - x) < 3 and 81 < y < 89 else mix(LIT, gc, 0.4))
            px(d, xx, y, c)
    if lv > 0.05:
        px(d, x, 86, (255, 250, 220))                              # 灯芯
    for y in range(80, 90):
        px(d, x - 4, y, IRON)
        px(d, x + 4, y, IRON)
        px(d, x, y, IRON if lv < 0.5 else (90, 70, 50))
    return im


GAS_BOXES = [('gas_l', (GAS[0] - 12, 86, GAS[0] + 11, 112)), ('gas_r', (GAS[1] - 12, 86, GAS[1] + 11, 112))]


def gas_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    bay = A._bayer(PW, H)
    for j, x in enumerate(GAS):
        ph = math.tau * f / N_ANIM + j * 2.1
        fl = (0, 1, 1, 0, -1, 0, 1, -1)[(f + j * 3) % 8]
        R = 9 + 1.5 * math.sin(ph)
        cy = 101
        for yy in range(int(cy - R), int(cy + R) + 1):
            for xx in range(int(x - R), int(x + R) + 1):
                r = math.hypot(xx + 0.5 - x, (yy - cy) * 1.2) / R
                if r < 1 and (1 - r) ** 1.4 > bay[yy, xx] * 0.85:
                    d.point((xx, yy), fill=(255, 214, 140, int(40 + 60 * (1 - r))))
        for y in range(98, 106):                                    # 灯罩玻璃（被火照亮）
            hw = 2 if y > 98 else 1
            hl(d, x - hw, x + hw - 2, y, LIT if y > 100 else LIT_D)
        top = 99 + (1 if fl < 0 else 0)
        vl(d, x - 1, top, 104, LIT_HI)                              # 火苗
        px(d, x - 1 + fl, top - 1, (255, 248, 210))
        px(d, x - 1, 105, (150, 170, 230))                          # 火苗根上一点蓝
        for y in range(97, 106):
            px(d, x - 3, y, IRON)
            px(d, x + 2, y, IRON)
    return im


CURTAIN_BOX = (110, 64, 120, 79)


def curtain_frame(t):
    """H1 二楼中间那扇亮窗：窗帘下摆轻轻动；第 2–5 帧一个人影从左往右走过窗帘后面。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    x, y, w, h = 110, 64, 10, 15
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            u = abs((xx - x) - (w - 1) / 2) / ((w - 1) / 2)
            sway = (1 if (yy + f) % 4 == 0 else 0) if yy > y + h - 6 else 0    # 每帧下摆鼓起来的行都不一样
            if u >= 0.28 + 0.1 * sway:
                c = CURT if (xx + 2 + f // 4) % 3 else CURT_D
            else:
                c = LIT_HI if yy > y + 1 else LIT
            px(d, xx, yy, c)
    hl(d, x, x + w - 1, y, CURT_D)
    sx = {2: x + 1, 3: x + 3, 4: x + 6, 5: x + 8}.get(f)
    if sx is not None:                                              # 人影（头 + 肩）
        for yy in range(y + 4, y + h):
            hw = 1 if yy < y + 7 else (2 if yy < y + 9 else 3)
            for xx in range(sx - hw, sx + hw + 1):
                if x <= xx < x + w:
                    c = im.getpixel((xx, yy))[:3]
                    px(d, xx, yy, dk(c, 0.62))
    mc = (60, 46, 36)
    vl(d, x + w // 2, y, y + h - 1, mc)
    for j in (1, 2):
        hl(d, x, x + w - 1, y + (h * j) // 3, mc)
    return im


CROW_BOX = (440, 34, 506, 86)


def crow(d, x, y, face, pose):
    """一只乌鸦（站着，脚 y）：pose 0 站 / 1 转头 / 2 低头 / 3 张嘴 / 4 扑翅膀。"""
    B, Bh = (30, 32, 36), (58, 62, 70)
    rect(d, x - 2, y - 3, x + 1, y - 1, B)
    px(d, x - 3 * face if face > 0 else x + 2, y - 2, B)            # 尾巴
    px(d, x - 3 * face if face > 0 else x + 2, y - 1, B)
    fc = -face if pose == 1 else face
    hx, hy = (x + 1 * fc, y - 2) if pose == 2 else (x + 1 * fc, y - 4)
    rect(d, hx - 1, hy, hx, hy + 1, B)
    px(d, hx + fc + (0 if fc > 0 else -1), hy + 1, (70, 70, 74))
    if pose == 3:
        px(d, hx + fc + (0 if fc > 0 else -1), hy, (70, 70, 74))
    px(d, x - 1, y - 3, Bh)
    vl(d, x - 1, y, y, (60, 56, 50))
    vl(d, x, y, y, (60, 56, 50))
    if pose == 4:
        hl(d, x - 4, x - 2, y - 5, B)
        hl(d, x + 1, x + 3, y - 5, B)
        px(d, x - 5, y - 6, B)
        px(d, x + 4, y - 6, B)


def crows_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    seqs = [(0, 0, 1, 1, 0, 2, 2, 0), (0, 3, 0, 0, 1, 1, 0, 0), (2, 2, 0, 0, 0, 1, 1, 0), (0, 0, 0, 4, 0, 0, 3, 0),
            (1, 0, 0, 2, 0, 0, 0, 1)]
    for i, (x, y, face) in enumerate(crow_spots()):
        crow(d, x, y, face, seqs[i % len(seqs)][f])
    return im


BUCKET_BOX = (WELL_X - 8, 109, WELL_X + 9, 127)


def bucket_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    dx = (0, 1, 2, 1, 0, -1, -2, -1)[f]
    x = WELL_X
    for y in range(111, 119):                                        # 绳子（上端在轴上不动）
        u = (y - 111) / 8
        px(d, round(x + dx * u), y, (150, 140, 112))
    bx = x + dx
    rect(d, bx - 3, 119, bx + 3, 124, WOOD)                          # 木桶
    hl(d, bx - 3, bx + 3, 119, WOOD_HI)
    hl(d, bx - 3, bx + 3, 121, IRON)
    hl(d, bx - 3, bx + 3, 124, WOOD_D)
    vl(d, bx + 3, 119, 124, WOOD_D)
    d.arc((bx - 3, 115, bx + 3, 121), 180, 360, fill=C(IRON))
    px(d, bx, 125, (120, 140, 150) if f % 2 else (100, 120, 130))    # 滴下来的水
    return im


NOTICE_BOX = (NOTICE[0] - 1, NOTICE[1] - 1, NOTICE[0] + 9, NOTICE[1] + 12)


def notice_frame(t):
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    lift = (0, 1, 2, 3, 2, 1, 0, 1)[f]
    x, y = NOTICE
    c = (206, 200, 182)
    for r in range(8):                                               # 一张纸：上沿钉着，下半截被风掀起来
        u = r / 7
        dy = -round(lift * u * u)
        dxx = round(lift * u * 0.6)
        w = 6 - (1 if r > 5 and lift > 1 else 0)
        for k in range(w):
            cc = c if not (r > 4 and lift > 1) else dk(c, 0.84)
            if r % 2 == 1 and 0 < k < w - 1 and hash01(k, r, 161) < 0.6:
                cc = (112, 104, 96)
            px(d, x + k + dxx, y + r + dy, cc)
    px(d, x + 3, y, (180, 60, 50))
    if lift >= 2:                                                    # 掀起来露出的纸背（更暗）
        hl(d, x + 1, x + 5, y + 8 - lift, (150, 144, 128))
    return im


SMOKE_BOX = (128, 0, 162, 24)


def smoke_frame(t):
    """H1 烟囱冒的一缕薄烟（半透明、Bayer 抖动）：一团团往上、往右飘，越往上越淡、越散。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    bay = A._bayer(PW, H)
    for i in range(6):
        u = ((f / N_ANIM) + i / 6) % 1.0
        cx = 139 + u * 14 + 2 * math.sin(u * 5 + i)
        cy = 19 - u * 20
        r = 1.5 + u * 3.5
        for yy in range(int(cy - r), int(cy + r) + 1):
            for xx in range(int(cx - r), int(cx + r) + 1):
                q = 1 - math.hypot(xx - cx, (yy - cy) * 1.3) / r
                if q > 0 and 0 <= yy < H and q * (1 - u) > bay[yy, xx] * 0.7:
                    d.point((xx, yy), fill=(176, 184, 186, int(60 + 70 * (1 - u))))
    return im


CAT = (334, 128)                          # 墓地矮墙上坐着的黑猫（脚 y）
CAT_BOX = (CAT[0] - 6, CAT[1] - 9, CAT[0] + 8, CAT[1] + 10)


def cat_frame(t):
    """墓地矮墙上一只黑猫（背朝左坐着、耳朵竖着），尾巴从墙沿垂下来慢慢甩；第 5 帧转一下头。"""
    im = A._new(PW, H)
    d = ImageDraw.Draw(im)
    f = P.frame_of(t, FPS_ANIM, N_ANIM)
    x, y = CAT
    B, Bh = (30, 30, 34), (58, 60, 66)
    rect(d, x - 2, y - 5, x + 2, y - 1, B)                          # 身子
    px(d, x - 3, y - 2, B)
    px(d, x + 3, y - 2, B)
    hx = x + (1 if f != 5 else -1)
    rect(d, hx - 1, y - 8, hx + 1, y - 6, B)                        # 头 + 耳朵
    px(d, hx - 1, y - 9, B)
    px(d, hx + 1, y - 9, B)
    px(d, hx + (1 if f != 5 else -1), y - 7, (190, 200, 120))     # 眼睛（一点黄绿）
    px(d, x - 2, y - 5, Bh)
    sw = (0, 1, 2, 3, 2, 1, 0, -1)[f]                             # 相邻两帧都不一样
    for k in range(9):                                             # 尾巴：顺着墙往下垂、末端甩
        u = k / 8
        px(d, x + 2 + round(sw * u * u), y + k, B)
    px(d, x + 3 + sw, y + 8, Bh)
    return im


# ============================================================ 组装
@lru_cache(maxsize=1)
def build():
    fg_ = fogs()
    near, lit = near_parts()
    layers = [
        P.L_static('sky', sky_img()),
        P.L_pano('far', far_img(), FAR_K),
        P.L_wrap('fog_far', fg_['far'][0], W, FAR_K, fg_['far'][1], 1.2),
        P.L_pano('mid', mid_img(), MID_K),
        P.L_wrap('fog_mid', fg_['mid'][0], W, MID_K, fg_['mid'][1], 2.0),
        P.L_pano('near', near, 1.0),
        P.L_strip('bucket', BUCKET_BOX, N_ANIM, FPS_ANIM, bucket_frame),
        P.L_strip('notice', NOTICE_BOX, N_ANIM, FPS_ANIM, notice_frame),
        P.L_strip('crows', CROW_BOX, N_ANIM, FPS_ANIM, crows_frame),
        P.L_strip('smoke', SMOKE_BOX, N_ANIM, FPS_ANIM, smoke_frame),
        P.L_strip('cat', CAT_BOX, N_ANIM, FPS_ANIM, cat_frame),
        P.L_wrap('fog_low', fg_['low'][0], W, 1.0, fg_['low'][1], 3.0),
        P.L_tint(NIGHT[0], NIGHT[1], key='night'),
        P.L_pano('night_lit', night_lit_img(), 1.0, key='night'),
        P.L_strip('lamp', LAMP_BOX, N_ANIM, FPS_ANIM, lamp_frame),
    ] + [P.L_strip(n, b, N_ANIM, FPS_ANIM, gas_frame) for (n, b) in GAS_BOXES] + [
        P.L_strip('curtain', CURTAIN_BOX, N_ANIM, FPS_ANIM, curtain_frame),
    ]
    fg = [
        P.L_wrap('mist_low', fg_['thin'][0], W, FG_K, fg_['thin'][1], 4.0),
        P.L_wrap('mist', fg_['dense'][0], W, 1.1, fg_['dense'][1], 6.0, key='mist'),
    ]
    return dict(layers=layers, fg=fg, near=near, lit=lit)


def compose(camX, t=0.5, state=None, fg=True):
    R = build()
    return P.compose(R['layers'], R['fg'], camX, t, state, with_fg=fg)


def extra_anchors():
    return dict(
        lamp_light=[LAMP_X, 85], lane_back=SIDE,
        gate_box=[GATE[0] - 1, 56, GATE[1] + 1, BASE + 1], well_box=[WELL_X - 12, 94, WELL_X + 18, KERB],
        graveyard_box=[GRAVE[0], 86, GRAVE[1], BASE + 1], board_box=[BOARD[0] - 1, 96, BOARD[1] + 1, KERB],
        tower_box=[TOWER[0] - 3, 0, TOWER[1] + 3, BASE + 1], clock_face=[CLOCK[0] - 8, CLOCK[1] - 8, CLOCK[0] + 9, CLOCK[1] + 9],
        tree_box=[440, 36, 502, BASE + 1], hotel_box=[HOTEL[0], 0, HOTEL[1], KERB],
        inn_door_box=[DOOR[0], 97, DOOR[1], 134], sign_box=[556, 85, 595, 94],
    )


# ============================================================ 导出
def export(ex, BJ):
    R = build()
    anchors = dict(ANCHORS)
    anchors.update(extra_anchors())
    st = P.export_stage(ex, PW, GROUND, WALK, R['layers'], R['fg'], anchors)
    if ex.check_on:
        _checks(ex, BJ, st, R)
    return st


def _checks(ex, BJ, st, R):
    keys = P.keys_of(R['layers'], R['fg'])
    allon = {k: True for k in keys}
    P.check_no_black(ex, BJ, st, PW, '雾之镇', [{}, allon])
    P.check_alpha01(ex, R['near'], '近景')
    P.check_opaque(ex, R['near'], (0, 130, PW, H), '近景 楼脚往下 + 人行道 + 石子路')
    P.check_opaque(ex, sky_img(), (0, 0, W, H), '天空底图')
    for name, img in (('远景', far_img()), ('中景', mid_img())):
        a = np.array(img)[..., 3]
        ex.checked('%s 下沿 y 132–140 整条不透明（近景的缺口里不会露天）' % name, int((a[132:141] != 255).sum()))
    P.check_strips(ex, BJ, P.strips_of(R['layers'], R['fg']))
    P.check_wraps(ex, BJ, st)
    out = P.check_anchors(ex, st['anchors'], PW, WALK, STAND, ANCHORS['walk_x'])
    ex.checked('锚点都在地图里、站人的锚点在可走带 / walk_x 里（不满足的条数）', out)
    need = ('arrive', 'gate', 'lamp', 'resident', 'well', 'graves', 'resident2', 'board', 'clock', 'tree', 'guest', 'inn',
            'inn_door', 'inn_sign')
    ex.checked('规格要求的 14 个锚点名都在', sum(k not in st['anchors'] for k in need))
    # 剧情要看的东西真的画在锚点上
    a = np.array(R['near']).astype(int)
    cx, cy = CLOCK
    face = a[cy - 5:cy + 6, cx - 5:cx + 6, :3]
    ex.checked('钟面在 clock 锚点上（中心 11×11 里亮的像素 ≥ 50）', 0 if int((P.lum(face) > 150).sum()) >= 50 else 1)
    sb = a[85:94, 556:595, :3]
    gold = int(((sb[..., 0] > 150) & (sb[..., 0] > sb[..., 2] + 40)).sum())
    ex.checked('HOTEL 招牌在 inn_sign 锚点上（金字像素 ≥ 60，= %d）' % gold, 0 if gold >= 60 else 1)
    post = a[95:136, LAMP_X, :3]
    ex.checked('路灯柱在 lamp 锚点的 x 上（y 95–135 都是深色铁柱）', int((P.lum(post) > 90).sum()))
    nlit = int(R['lit'].sum())
    ex.checked('亮着的窗玻璃 ≥ 900 px（窗灯是画面里唯一的暖色，= %d）' % nlit, 0 if nlit >= 900 else 1)
    warm = np.array(R['near']).astype(int)
    hot = (warm[..., 0] > warm[..., 2] + 60) & ~R['lit']
    ex.checked('亮窗以外没有大块的暖色（R − B > 60 的像素 ≤ 400，= %d）' % int(hot.sum()), 0 if hot.sum() <= 400 else 1)
    mean, std = P.check_walk_flat(ex, R['near'], WALK, '雾之镇')
    ex.note('可走带 y146–176 亮度均值 %.0f 标准差 %.1f' % (mean, std))
    nm = P.lum(np.array(R['near'])[..., :3].astype(np.float32))
    ex.note('可走带后面 y106–145 亮度均值 %.0f 标准差 %.1f' % (nm[106:146].mean(), nm[106:146].std()))
    P.check_export_vs_compose(ex, BJ, st, R['layers'], R['fg'], '雾之镇', (0, 160, 320), (0.0, 1.25),
                              [{}, {'night': True}, {'mist': True}, allon])


def _nblobs(m):
    from scipy import ndimage
    return int(ndimage.label(m)[1])


# ============================================================ 单独预览
if __name__ == '__main__':
    od = os.path.join(HERE, '_preview', 'ch5', 'fog_town_dev')
    os.makedirs(od, exist_ok=True)
    for camX in (0, 160, 320):
        compose(camX, 0.5).convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(
            os.path.join(od, 'solo_%d.png' % camX))
    world = Image.new('RGBA', (PW, H), (0, 0, 0, 255))
    world.alpha_composite(near_img())
    world.convert('RGB').resize((PW * 2, H * 2), Image.NEAREST).save(os.path.join(od, 'near.png'))
    print('ok')
