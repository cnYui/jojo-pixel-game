"""核对技术约定§3.14的独立资源清单、实际画布和PNG完整性。"""
import sys
sys.dont_write_bytecode = True
import importlib
import json
import os
from pathlib import Path
import numpy as np
from PIL import Image
import art_common as AC
import bake_characters as B
import amap

ACTIONS = {
    'jotaro': {'guard':(1,None,'static'),'dodge':(1,None,'static'),'down':(1,None,'static')},
    # 2026-10-10：上勾拳 1 帧 → 3 帧（蓄力 / 上冲 / 收势），红色魔术师加重拳 heavy 2 帧（战斗抽帧审查的精灵问题）
    'starplat': {'upper':(3,12,'oneshot'),'hurt':(1,None,'static'),'reach':(1,None,'static')},
    'kakyoin': {'guard':(1,None,'static'),'dodge':(1,None,'static')},
    'hiero': {'whip':(2,12,'oneshot'),'hurt':(1,None,'static'),'block':(1,None,'static')},
    'avdol': {'guard':(1,None,'static'),'dodge':(1,None,'static')},
    'magred': {'punch':(2,18,'oneshot'),'heavy':(2,10,'oneshot'),'block':(1,None,'static'),'hurt':(1,None,'static')},
    'polnareff': {'down':(1,None,'static')},
    'chariot': {'slash':(2,16,'oneshot'),'parry':(1,None,'static'),'hurt':(1,None,'static'),
                'bare_idle':(2,4,'loop'),'bare_thrust':(3,12,'oneshot')},
    'towergray': {'needle':(1,None,'static')},
    # 2026-10-10：愚者沙爪 / 砸地按原工程 _fool_frame 重画（各 2 帧），伊奇闪避 = 4 帧翻滚
    'fool': {'claw':(2,8,'oneshot'),'slam':(2,8,'oneshot')},
    'iggy': {'dodge':(4,16,'oneshot')},
}
NEW = {
    'grayfly':{'idle':2,'seated':1,'hurt':1,'down':1,'portrait':2,'portrait_scared':1},
    'npc_nurse':{'idle':2,'walk':4,'possessed':2,'stab':2,'faint':1,'portrait':2,'portrait_possessed':1},
    **{f'npc_passenger_{k}':{'seated':1,'slump':1} for k in 'abcd'},
    'npc_police':{'idle':2,'walk':4,'read':2,'shock':1,'portrait':2},
    **{f'npc_student_f_{k}':{'idle':2,'walk':4,'cheer':2,'down':1,'portrait':2} for k in 'ab'},
    **{f'npc_{k}':{'idle':2,'walk':4,'portrait':2} for k in ('stewardess','hk_owner','hk_granny')},
    **{f'npc_hk_passer_{k}':{'idle':2,'walk':4} for k in 'ab'},
    'npc_fortune':{'idle':2,'portrait':2},
    'npc_student_m':{'idle':2,'walk':4,'bow':1,'portrait':1},
}
PROPS = {'magazine':(1,10,7),'jail_pipe':(2,16,48),'tissue':(1,10,8),'pen':(1,9,3),
         'pinky':(1,4,5),'hk_table':(2,48,20),'mr_statue':(3,24,40),
         'chariot_armor':(4,8,8),'dish':(3,8,5),'kite':(1,8,8)}

def run():
    root = Path(AC.GAME)
    report = json.loads((Path(AC.PREVIEW)/'bake_report.json').read_text(encoding='utf8'))
    assert report['verify']['errors']==report['verify']['engine_bad']==0
    assert not report['amap_errors']
    count = 0
    for cid in set(ACTIONS)|set(NEW):
        folder=root/'assets/chars_new'/cid
        meta=json.loads((folder/(cid+'.json')).read_text(encoding='utf8'))
        sheet=Image.open(folder/meta['image']).convert('RGBA')
        w,h=meta['cell']
        assert sheet.width % w == sheet.height % h == 0, cid
        for act,need in ACTIONS.get(cid,{}).items():
            got=meta['animations'][act]
            assert (got['frames'],got['kind'])==(need[0],need[2]), (cid,act,got)
            assert need[1] is None or got['fps']==need[1], (cid,act,got)
        for act,n in NEW.get(cid,{}).items():
            assert meta['animations'][act]['frames']==n, (cid,act)
        if cid in NEW:
            for logic in ('idle','walk','talk','hurt'):
                assert logic in amap.AMAP[cid], (cid,logic)
                assert amap.target(amap.AMAP[cid][logic]) in meta['animations'], (cid,logic)
        for act,info in meta['animations'].items():
            for i in range(info['frames']):
                a=np.asarray(sheet.crop((i*w,info['row']*h,(i+1)*w,(info['row']+1)*h)))[:,:,3]
                assert a.any() and set(np.unique(a))<={0,255}, (cid,act,i)
                count+=1
        for exp in meta['expressions']:
            assert len(exp['files'])==exp['frames'], (cid,exp['id'])
            for file in exp['files']:
                assert Image.open(folder/file).size==tuple(exp['size'])
    props=json.loads((root/'assets/props_new/props_new.json').read_text(encoding='utf8'))['props']
    indexed={p['id']:p for p in props}
    assert set(PROPS)<=set(indexed)
    for id,(n,w,h) in PROPS.items():
        p=indexed[id]
        assert (p['frames'],*p['size'])==(n,w,h), id
        assert p['kind']=='static' and p['fps']==0, id
        im=Image.open(root/'assets/props_new'/p['file'])
        assert im.size==(n*w,h), id
        for i in range(n):
            a=np.asarray(im.crop((i*w,0,(i+1)*w,h)))[:,:,3]
            assert a.any() and set(np.unique(a))<={0,255}, (id,i)
    cwd=os.getcwd()
    try:
        B.load_registry(AC.SRC,with_scene=False)
    finally:
        os.chdir(cwd)
    for module in ('art_heroes','art_stands','art_enemies','art_npc','art_new_grayfly'):
        importlib.import_module(module)
    from engine import sprite
    for name,need in {'jotaro.guard':(36,52),'jotaro.down':(58,22),'polnareff.down':(60,22),
                      'towergray.needle':(26,12),'starplat.reach':(74,None),'magred.punch':(64,None)}.items():
        w,h=sprite.get(name).size
        assert w==need[0] and (need[1] is None or h==need[1]), (name,w,h,need)
    assert amap.AMAP['joseph']['down']=={'a':'lie','flip':True}
    print(f'M1资源契约通过：{count}角色帧、{len(NEW)}新角色、{len(PROPS)}道具；回读和原绘制误差均为0')

if __name__=='__main__':
    run()
