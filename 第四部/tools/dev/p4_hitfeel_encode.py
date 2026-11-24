"""把 p4_hitfeel_record.js 录出来的逐帧画面拼成对比视频 + 整理统计 + 导帧条。

    python -B 第四部/tools/dev/p4_hitfeel_encode.py --frames-dir 逐帧目录的上一层 --out D:\\CodeWorkSpace\\jojo-hitfeel-compare

输入：<frames-dir>/frames_before/、frames_after/（f00000.png …，1280×720）和 <frames-dir>/stats_before.json、stats_after.json
输出：before.mp4、after.mp4（1280×720，60 fps，H.264 yuv420p，faststart，无声，两条帧数时长一样）、
      stats_before.json、stats_after.json（逐次命中 + 每段全局顿帧的逐帧数字）、framestrip_*.png（重击命中前 2 帧到后 14 帧）
"""
import sys
sys.dont_write_bytecode = True
import argparse
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument('--frames-dir', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--crf', type=int, default=19)
ap.add_argument('--no-video', action='store_true')
a = ap.parse_args()
SRC = Path(a.frames_dir)
OUT = Path(a.out)
OUT.mkdir(parents=True, exist_ok=True)
WIN = 17           # 命中那一帧起往后记多少帧


def r3(v):
    return None if v is None else round(v, 3)


def build_stats(tag):
    raw = json.loads((SRC / ('stats_%s.json' % tag)).read_text(encoding='utf-8'))
    fr = raw['frames']
    # 全局顿帧段：hs > 0 的连续帧（hs 是这一步开始时的顿帧剩余帧数）
    stops, i = [], 0
    while i < len(fr):
        if fr[i]['hs'] > 0:
            j = i
            while j < len(fr) and fr[j]['hs'] > 0:
                j += 1
            stops.append({'start': fr[i]['i'], 'frames': j - i, 'round': fr[i]['round'], 'worldMul': [r3(f['wm']) for f in fr[i:j]], 'worldFramesDuringStop': r3(sum(f['wm'] for f in fr[i:j]))})
            i = j
        else:
            i += 1
    hits = []
    for h in raw['hits']:
        F = h['frame']
        seg = fr[F:F + WIN]
        stop = next((s for s in stops if F <= s['start'] <= F + 3), None)
        hits.append({
            'hitFrame': F, 'round': h['round'], 'move': h['slot'], 'dmg': h['dmg'], 'push': h['push'],
            'declaredStopAllFrames': round(h['stopAll'] * 60), 'hitStop': stop,
            'targetFlashAlpha': [f['flash'] for f in seg],
            'targetX': [r3(f['x'] - fr[F - 1]['x']) for f in seg],              # 相对命中前一帧的累计位移（击退曲线）
            'targetDX': [r3(f['dx']) for f in seg],                             # 每帧位移
            'targetShakePx': [f['shake'] for f in seg],                         # 画面上 ±1 px 受击抖动（压扁那 2 帧画在小画布上，记 null）
            'targetSquash': [bool(f['squash']) for f in seg],                   # 倾斜 / 压扁（新分支才有）
            'targetState': [f['st'] for f in seg],
            'worldMulPerFrame': [r3(f['wm']) for f in seg],
        })
    wall = [{'frame': s['frame']} for s in raw['sfx']]
    out = {'tag': tag, 'root': raw['root'], 'seed': raw['seed'], 'input': raw['input'], 'geometry': raw['geo'], 'frames': len(fr),
           'hits': hits, 'globalHitStops': stops, 'wallSlamFrames': wall, 'errors': raw['errors']}
    (OUT / ('stats_%s.json' % tag)).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    return raw, out


def encode(tag, name):
    src = SRC / ('frames_%s' % tag)
    n = len(list(src.glob('f*.png')))
    dst = OUT / name
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '60', '-i', str(src / 'f%05d.png'), '-c:v', 'libx264', '-preset', 'slow', '-crf', str(a.crf),
           '-pix_fmt', 'yuv420p', '-r', '60', '-movflags', '+faststart', '-an', str(dst)]
    subprocess.run(cmd, check=True)
    print(name, n, '帧', round(dst.stat().st_size / 1e6, 2), 'MB')
    return n


def strip(tag, raw, F, pre=2, post=14, box=(384, 288), scale=0.75):
    """第 F 帧（命中帧）前 pre 帧到后 post 帧，每帧一格：围着木桩切一块"""
    fr = raw['frames']
    cells = []
    # 切块位置按命中帧的木桩画面位置定，前后两条用同一个位置（用 before 的）
    for k in range(F - pre, F + post + 1):
        im = Image.open(SRC / ('frames_%s' % tag) / ('f%05d.png' % k)).convert('RGB')
        cx, cy = STRIP_CENTER
        x0 = max(0, min(im.width - box[0], int(cx - box[0] / 2)))
        y0 = max(0, min(im.height - box[1], int(cy - box[1] / 2)))
        c = im.crop((x0, y0, x0 + box[0], y0 + box[1])).resize((int(box[0] * scale), int(box[1] * scale)), Image.NEAREST)
        d = ImageDraw.Draw(c)
        d.rectangle((0, 0, 58, 14), fill=(0, 0, 0))
        d.text((3, 1), ('F%+d' % (k - F)) if k != F else 'HIT', fill=(255, 255, 255))
        cells.append(c)
    return cells


def sheet(rows, labels, path):
    cw, ch = rows[0][0].size
    cols = len(rows[0])
    pad = 18
    im = Image.new('RGB', (cols * cw, len(rows) * (ch + pad)), (20, 20, 24))
    d = ImageDraw.Draw(im)
    for ri, (cells, lab) in enumerate(zip(rows, labels)):
        y = ri * (ch + pad)
        d.text((4, y + 3), lab, fill=(255, 220, 120))
        for ci, c in enumerate(cells):
            im.paste(c, (ci * cw, y + pad))
    im.save(path)
    print(path.name, im.size)


rawb, sb = build_stats('before')
rawa, sa = build_stats('after')
if not a.no_video:
    nb = encode('before', 'before.mp4')
    na = encode('after', 'after.mp4')
    assert nb == na, '两条帧数不一样 %d %d' % (nb, na)

# 帧条：第一轮的 J3（重击）命中帧；前后两条的命中帧号要一样才能上下对齐
def first(raw, slot, rnd=0):
    return next(h for h in raw['hits'] if h['slot'] == slot and h['round'] == rnd)

for slot in ('J3', 'fin'):
    hb, ha = first(rawb, slot), first(rawa, slot)
    # 切块中心：按命中帧木桩的画面位置（取 before 的；after 的前后两条用同一个中心）
    fb = rawb['frames'][hb['frame']]
    STRIP_CENTER = (fb['sx'] * 4 + 40, fb['sy'] * 4 - 60)
    cb = strip('before', rawb, hb['frame'])
    ca = strip('after', rawa, ha['frame'])
    sheet([cb], ['BEFORE  ' + slot + ' hit@frame %d' % hb['frame']], OUT / ('framestrip_before_%s.png' % slot))
    sheet([ca], ['AFTER   ' + slot + ' hit@frame %d' % ha['frame']], OUT / ('framestrip_after_%s.png' % slot))
    sheet([cb, ca], ['BEFORE  ' + slot + ' hit@frame %d' % hb['frame'], 'AFTER   ' + slot + ' hit@frame %d' % ha['frame']], OUT / ('framestrip_compare_%s.png' % slot))
print('done')
