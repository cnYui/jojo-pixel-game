"""compare.py dirA dirB: per-frame pixel diff summary."""
import sys, os, json
import numpy as np
from PIL import Image
a, b = sys.argv[1], sys.argv[2]
fs = sorted(f for f in os.listdir(a) if f.endswith('.png'))
changed = []
for f in fs:
    A = np.asarray(Image.open(os.path.join(a, f)))
    B = np.asarray(Image.open(os.path.join(b, f)))
    if A.shape != B.shape:
        changed.append((f, 'shape'))
        continue
    d = np.any(A != B, axis=2)
    if d.any():
        ys, xs = np.nonzero(d)
        changed.append((f, int(d.sum()), int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())))
print(len(fs), 'frames,', len(changed), 'changed')
for c in changed:
    print(c)
ea = json.load(open(os.path.join(a, 'events.json')))
eb = json.load(open(os.path.join(b, 'events.json')))
print('events identical:', ea == eb, len(ea))
