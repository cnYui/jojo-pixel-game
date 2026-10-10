"""包 5 行为验收：生产底座的固定 60 Hz 输入测试，保存结果与当前竞技场截图。"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
OUT=HERE/'_out'
OUT.mkdir(exist_ok=True)
errors=[]
results=[]
def check(name, ok, detail):
    results.append(dict(name=name,ok=bool(ok),detail=detail))
    print(('通过 ' if ok else '失败 ')+name+' '+json.dumps(detail,ensure_ascii=False),flush=True)
    (OUT/'test_combat.partial.json').write_text(json.dumps(dict(results=results,errors=errors),ensure_ascii=False,indent=2),encoding='utf-8')
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1280,'height':720})
    page.on('console',lambda m:errors.append(m.text) if m.type in ('warning','error') else None)
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((HERE/'arena.html').as_uri())
    page.evaluate('P5.init()')
    for method in ['combos','dodge','guards','poise','wall','special','shots','timestop','cancellation','retry','finish']:
        try:
            r=page.evaluate('async(m)=>await Promise.race([P5[m](),new Promise((_,reject)=>setTimeout(()=>reject(new Error("验收超时: "+m+" "+JSON.stringify(P5.state()))),12000))])',method)
        except Exception as e:
            check(method,False,str(e))
            continue
        if method=='combos': check('三连、连打入口、90f上限和30f冷却',r['chain']==['J1','J2','J3'] and r['entered'] and 80<=r['frames']<=90 and r['end']['cd']>.45,r)
        if method=='dodge':
            check('闪避5f无伤12f有伤、擦身3f与8f',all(v['dmg']==0 if v['n']!=12 else v['dmg']>0 for v in r['hits']) and [v['graze'] for v in r['hits']]==[1,1,0,0],r)
            check('持续火柱重复闪避不刷能量',r['persistentEnergy']==0,r)
        if method=='guards':check('四种格挡、松手弹反、10Hz连按锁和接管钩子',[v['dmg'] for v in r['values']]==[4,6,20,20] and r['firstParry'] and r['parries']==1 and r['handled'] and r['eStun']==0,r)
        if method=='poise':check('韧性90f破绽、伤害1.2与连打0.6反冲',r['broken']['state']=='broken' and abs(r['broken']['dur']-1.5)<1e-6 and r['dmg']==12 and r['healed'] and r['capped']==6 and r['counter'],r)
        if method=='wall':check('40px击退撞墙反弹',r['wall'] and r['x']<314,r)
        if method=='special':check('U100能量门槛、清零和need0剧情窗口',not r['normal']['low'] and r['normal']['done'] and r['normal']['energy']==0 and not r['outside'] and r['invoked']==1,r)
        if method=='shots':check('反射/缠住、地火不可斩、危险区预警',[v['side'] for v in r['out']]==['player','enemy'] and r['out'][1]['dead'] and r['out'][1]['root']>0 and r['ground'] and not r['cut'] and r['after']<r['before'],r)
        if method=='timestop':check('2s时停冻结、队列结算与L伤害0.3',r['frozen'] and r['queued']==2 and r['hp']-r['after']==12 and r['done'] and r['guardCleared'] and r['immune']==0,r)
        if method=='cancellation':check('切场取消必杀和战斗、不留旧后台任务',not r['value'] and r['result']['cancelled'] and r['result']['name']=='RunCancelled' and r['runChanged'],r)
        if method=='retry':check('检查点第二阶段重试、Boss身份和放水0.7',len(set(v['e'] for v in r['seen']))==1 and r['after1']['attempt']==1 and r['after1']['hp']==100 and r['after1']['speed']==88 and r['assist'] and r['assistDmg']==14 and len(r['menus'][-1])==3,r)
        if method=='finish':check('ko/draw收尾时间轴与替身退场',all(v['done'] and v['dead'] and v['standHidden'] for v in r),r)
        page.screenshot(path=str(OUT/(method+'.png')))
    diagnostics=page.evaluate('P5.diagnostics()')
    page.wait_for_timeout(100)
    check('控制台零warning/error/pageerror',not errors,errors)
    check('生产循环无异常',not diagnostics['events'],diagnostics)
    browser.close()
report=dict(ok=all(v['ok'] for v in results),results=results,errors=errors)
(OUT/'test_combat.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(f"{sum(v['ok'] for v in results)}/{len(results)} 通过",flush=True)
sys.exit(not report['ok'])
