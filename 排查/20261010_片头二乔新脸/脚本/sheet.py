"""sheet.py dirA dirB out.png frame:x0,y0,x1,y1:zoom ...  -> rows of [A | B] crops with labels."""
import sys, os
from PIL import Image, ImageDraw, ImageFont
a, b, out = sys.argv[1], sys.argv[2], sys.argv[3]
specs = sys.argv[4:]
try:
    font = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 18)
except Exception:
    font = ImageFont.load_default()
la = os.environ.get('LA', '旧（原精灵）')
lb = os.environ.get('LB', '新（游戏层）')
rows = []
for s in specs:
    f, box, z = s.split(':')
    x0, y0, x1, y1 = map(int, box.split(','))
    z = int(z)
    ims = []
    for d in (a, b):
        p = os.path.join(d, f'{int(f):04d}.png') if not f.endswith('.png') else os.path.join(d, f)
        im = Image.open(p).convert('RGB').crop((x0, y0, x1, y1))
        ims.append(im.resize((im.width * z, im.height * z), Image.NEAREST))
    w, h = ims[0].size
    row = Image.new('RGB', (w * 2 + 30, h + 28), (30, 30, 30))
    row.paste(ims[0], (0, 28)); row.paste(ims[1], (w + 30, 28))
    dr = ImageDraw.Draw(row)
    import re
    fn = int(re.findall(r'\d+', f)[-1])
    dr.text((4, 3), f'{la}  第 {fn} 帧  t={fn / 24:.3f}s', fill=(255, 220, 120), font=font)
    dr.text((w + 34, 3), lb, fill=(140, 220, 255), font=font)
    rows.append(row)
W = max(r.width for r in rows)
H = sum(r.height for r in rows) + 8 * len(rows)
sheet = Image.new('RGB', (W, H), (20, 20, 20))
y = 0
for r in rows:
    sheet.paste(r, (0, y)); y += r.height + 8
sheet.save(out)
print(out, sheet.size)
