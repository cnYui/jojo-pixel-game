"""dump_frames.py <orig|game> <scene> <outdir>: render every frame of a scene (UW x UH RGB) to PNG + collect sfx events."""
import sys
sys.dont_write_bytecode = True
import os
import json
GAME = r'D:\大疆\游戏素材\JoJo\游戏'
SRC = r'D:\大疆\游戏素材\JoJo\源码'
sys.path.insert(0, os.path.join(GAME, 'tools'))
sys.path.insert(0, os.path.join(SRC, 'tools'))
sys.path.insert(0, SRC)
mode, scene, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
from common import load_scene, render_frame, scene_frames
from engine.core import FPS
if mode == 'game':
    import cutscene_sprites
    r = cutscene_sprites.apply_game_redraws()
    print('atlas check bad:', cutscene_sprites.check_atlas(r))
name, mod = load_scene(scene)
n = scene_frames(mod)
ev = set()
for i in range(n):
    fr = render_frame(mod, name, i / FPS, i)
    ev.update(fr.events)
    fr.compose().convert('RGB').save(os.path.join(out, f'{i:04d}.png'))
json.dump(sorted([list(e) if isinstance(e, tuple) else e for e in ev], key=str), open(os.path.join(out, 'events.json'), 'w'), default=str)
print(mode, scene, n, 'frames')
