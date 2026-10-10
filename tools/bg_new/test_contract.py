"""核对M1背景的独立地图清单、层类型、锚点与实际PNG闭合报告。"""
import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
import numpy as np
from PIL import Image

KEYS = {'title_pyramids','world_map','sky_day','sea_day','jail_cell','kujo_house_day',
        'kujo_house_night','kujo_house_morning','kujo_bedroom_dusk','school_gate',
        'school_infirmary','dusk_gate','tatami_top','plane_cabin_side','plane_cabin',
        'cockpit','hongkong_night','hk_garden_night','school_stairs'}

def run():
    folder=Path(__file__).parent/'_preview'
    stages=json.loads((folder/'_stages.json').read_text(encoding='utf8'))
    report=json.loads((folder/'_report.json').read_text(encoding='utf8'))
    assert KEYS<=set(stages)
    assert all(c['ok'] for r in report['report'].values() for c in r['checks'])
    assert all(s['closure']==0 for r in report['report'].values() for s in r['strips'])
    for image,m in report['files'].items():
        im=Image.open(folder/m['file'])
        assert im.size==tuple(m['size']) and im.width<=8192 and im.getbbox(), image
    hk=stages['hongkong_night']
    assert hk['w']==960 and sum(l['type']=='wrap' and l['period']==640 for l in hk['layers'])==3
    assert any(l['type']=='wrap' and l['period']==40 for l in hk['layers'])
    assert {'neon','reflect'}<={l['type'] for l in hk['layers']}
    cabin=stages['plane_cabin_side']
    assert cabin['w']==640
    assert sum(l['type']=='pano' for l in cabin['layers'])==1
    assert cabin['fg'][0]['type']=='pano'
    assert set(('seats','grayfly_seat','toilet','cockpit_door'))<=set(cabin['anchors'])
    wall=Image.open(folder/report['files']['bg/plane_cabin_side/cabin']['file'])
    alpha=np.asarray(wall)[:,:,3]
    assert (alpha[:,:20]==255).all() and (alpha[:,620:]==255).all()
    infirmary=stages['school_infirmary']
    assert infirmary['ground']==156 and infirmary['walk']==[148,176]
    assert {'bed1','bed2','desk','door'}<=set(infirmary['anchors'])
    assert len([l for l in infirmary['layers'] if l['type']=='strip'])==2
    assert stages['tatami_top']['anchors']['fleshbud']==[160,70]
    print(f'M1背景契约通过：{len(KEYS)}地图、香港960宽分层、客舱640宽非循环、全部帧条严格闭合')

if __name__=='__main__':
    run()
