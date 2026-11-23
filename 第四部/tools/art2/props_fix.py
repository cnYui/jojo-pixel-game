# 第四部重画：道具里尺寸不对的那几件按新比例重画（道具大多是小物件，本来就是按人物大小画的，不用动）。
#   普查结论（按 第四部/docs/比例标准.md）：电椅 44 px 高（应 24）、鞋柜 28 px（应 18）、救护车 54 × 28（应 90 × 42）偏离大，重画；
#   其余（自行车 28 × 18、摩托 36 × 22、加湿器、花盆、手套盒……）在尺子上或是手里拿的小东西，保留。
#   用法：python 第四部/tools/art2/props_fix.py
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from px import Cv, OUTLINE, shade, ASSETS, META, ensure  # noqa: E402
import bgkit as K  # noqa: E402


def save_prop(pid, frames, pivot=None, **meta):
    """frames = [Cv…]（等大）；写 assets/props/<pid>.png 并改 props*.json 里的 size / pivot / frames"""
    w, h = frames[0].w, frames[0].h
    sheet = Cv(w * len(frames), h)
    for i, f in enumerate(frames):
        sheet.blit(f, i * w, 0)
    sheet.img().save(ensure(os.path.join(ASSETS, 'props', pid + '.png')))
    for fp in sorted(glob.glob(os.path.join(META, 'props*.json'))):
        d = json.load(open(fp, encoding='utf-8'))
        e = (d.get('props') or {}).get(pid)
        if not e:
            continue
        e.update(frames=len(frames), size=[w, h], pivot=pivot or [w // 2, h], **meta)
        with open(fp, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
        print('  %-12s %d × %d × %d 帧  (%s)' % (pid, w, h, len(frames), os.path.basename(fp)))
        return
    print('  ！props 元数据里没有', pid)


def echair():
    """由花子的电椅：高背木椅（椅面 5、椅背顶 22），扶手和椅背缠着黄色电线"""
    cv = Cv(22, 26)
    by = 24
    cv.rect(4, by - 22, 6, by, '#6a4630')
    cv.rect(4, by - 22, 16, by - 20, '#7a5640')
    cv.rect(6, by - 20, 15, by - 8, '#5a3a28')
    cv.rect(4, by - 7, 18, by - 5, '#7a5640')
    cv.vline(18, by - 5, by, '#6a4630')
    cv.hline(6, 18, by - 11, '#6a4630')
    for y in range(by - 20, by - 6, 3):
        cv.hline(4, 17, y, '#e8c040')
    cv.put(3, by - 23, '#fff0a0')
    return cv.outline(OUTLINE)


def shoecab():
    """玄关的鞋柜：1.1 m 高（18 px）"""
    cv = Cv(34, 21)
    K.cabinet(cv, 2, 31, 19, 18, '#8a6240', doors=3)
    for x, col in ((6, '#3a3a44'), (16, '#8a4a3a'), (24, '#f4f4f0')):
        cv.rect(x, 4, x + 4, 6, col)
    return cv.outline(OUTLINE)


def ambulance():
    """救护车：高 2.5 m、长 5.4 m = 42 × 90 px；两帧（警灯一亮一灭）"""
    frs = []
    for on in (0, 1):
        cv = Cv(94, 46)
        by = 43
        body, band = '#f4f4f0', '#d03a3a'
        cv.rect(2, by - 36, 70, by - 6, body)                 # 车厢
        cv.rect(70, by - 28, 88, by - 6, body)                # 车头
        for i in range(8):
            cv.hline(70, 80 + i, by - 36 + i, body)           # 前挡风的斜面
        cv.rect(72, by - 27, 84, by - 18, '#6a8aa4')          # 前窗
        cv.line(73, by - 19, 77, by - 26, '#a8c8dc')
        cv.rect(54, by - 28, 66, by - 18, '#6a8aa4')          # 侧窗
        cv.hline(2, 88, by - 14, band)
        cv.hline(2, 88, by - 13, band)
        cv.rect(24, by - 30, 30, by - 18, band)               # 红十字
        cv.rect(20, by - 27, 34, by - 22, band)
        cv.vline(46, by - 34, by - 7, shade(body, -0.2))      # 车门缝
        cv.hline(2, 88, by - 36, shade(body, 0.2))
        cv.hline(2, 88, by - 6, shade(body, -0.35))
        cv.vline(2, by - 36, by - 6, shade(body, -0.15))
        cv.rect(60, by - 40, 68, by - 37, '#ff4040' if on else '#8a2a2a')   # 警灯
        if on:
            cv.put(64, by - 41, '#ffd0d0')
        cv.rect(86, by - 12, 89, by - 9, '#fff0b0')           # 车灯
        cv.rect(1, by - 12, 3, by - 9, '#d03a3a')
        cv.rect(0, by - 6, 90, by - 4, '#8a8e96')             # 保险杠
        for wx in (18, 72):
            cv.ellipse(wx, by - 4, 6, 6, '#1c1c22')
            cv.ellipse(wx, by - 4, 2.5, 2.5, '#9a9ea8')
        frs.append(cv.outline(OUTLINE))
    return frs


def main():
    save_prop('echair', [echair()])
    save_prop('shoecab', [shoecab()])
    save_prop('ambulance', ambulance())


if __name__ == '__main__':
    main()
