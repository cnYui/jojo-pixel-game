"""后段玩法用真实入口、资源和键盘输入验收，不替换战斗或剧情 API。"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
GAME = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / '_out'
ROWS = []


def check(name, ok, detail=None):
    ROWS.append({'name': name, 'ok': bool(ok), 'detail': detail})
    print(('通过 ' if ok else '失败 ') + name, flush=True)
    if not ok:
        print(json.dumps(detail,ensure_ascii=False,default=str),flush=True)


def tick(p, n=1):
    # 每 10 帧让出一次宏任务：真实浏览器每个 rAF 之后都会把微任务（Promise 链）跑完；只 await 一次 Promise.resolve()
    # 时，剧情里好几跳的 await 链（例如战斗失败 → failed() → W.combat=false）会被后面 10 帧抢先，夹具看到的时序比真实游戏晚。
    p.evaluate('''async n => {
      for (let left=n;left>0;left-=10) { G.dbg.tick(Math.min(10,left)); await new Promise(r => setTimeout(r, 0)); }
    }''', n)


def press(p, key, n=1):
    p.keyboard.press(key)
    tick(p, n)


def reach(p, expression, frames=900, dialogs=False):
    for _ in range((frames + 9) // 10):
        if p.evaluate('() => !!(' + expression + ')'):
            return True
        if dialogs and p.evaluate('() => !!(G.ui.dlg || G.ui.narr || G.ui.noticeBox)'):
            press(p, 'Enter', 10)
        else:
            tick(p, 10)
    return p.evaluate('() => !!(' + expression + ')')


def prep(p, stage, leader='jotaro'):
    p.evaluate('''async ([stage,leader]) => {
      await G.goTitle(); G.cancelRun(); G.ui.reset(); S.busy=false;
      G.setScene(window.__worldScene); G.dbg.hold=true; G.fadeA=0;
      S.party(['jotaro','joseph','avdol','kakyoin','polnareff','iggy'],{leader});
      await S.setStage(stage,{fade:false}); G.input.clear();
      window.__lateResult='pending'; window.__lastMini=null;
    }''', [stage, leader])


def start(p, expression):
    p.evaluate('''expression => {
      const fn=new Function('return '+expression);
      Promise.resolve(fn()).then(r=>{window.__lateResult='resolved';window.__lateValue=r;},
        e=>{window.__lateResult=e.name; if(!G.cancelled(e)) console.error(e);});
    }''', expression)


def save_mini(p):
    p.evaluate('() => { window.__lastMini=G.lateGame; }')


def state(p):
    return p.evaluate('''() => ({result:window.__lateResult,
      mini:G.lateGame&&Object.fromEntries(Object.entries(G.lateGame).filter(([k,v])=>v==null||['number','boolean','string'].includes(typeof v))),
      qte:G.ui.qte&&{id:G.ui.qte.id,n:G.ui.qte.n,t:G.ui.qte.t,result:G.ui.qte.result},
      menu:G.ui.menu&&{title:G.ui.menu.title,options:G.ui.menu.options.map(String),t:G.ui.menu.t},
      notice:G.ui.noticeBox&&G.ui.noticeBox.text,cine:G.world.cine&&String(G.world.cine.by&&G.world.cine.by.cid||G.world.cine.by),
      fight:G.world.fight&&{id:G.world.fight.id,t:G.world.fight.t,attempt:G.world.fight.attempt,growing:G.world.fight.data.growing},
      time:{active:G.time.active,phase:G.time.phase,t:G.time.t},
      shot:G.dbg.shot, events:G.dbg.events.slice(-20).map(e=>Object.fromEntries(Object.entries(e).filter(([k,v])=>v==null||['number','boolean','string'].includes(typeof v)))),
      player:G.world.player&&{cid:G.world.player.cid,x:G.world.player.x,hp:G.world.player.hp}})''')


def battle(p, expression, stage, leader='jotaro'):
    prep(p, stage, leader)
    start(p, expression)
    assert reach(p, 'G.world.fight&&G.world.combat&&!G.world.cine', 900, True)


def inert_boss(p):
    p.evaluate('''() => {const c=G.world.fight; c.boss.brain=()=>true;
      c.boss.atk=c.boss.tele=null;c.boss.mem.locked=true;}''')


def mash(p, max_presses=50):
    for _ in range(max_presses):
        if p.evaluate('() => !G.ui.qte||G.ui.qte.result!=null'): break
        press(p, 'j', 2)
    tick(p, 50)


def test_prophecy(p):
    for index in range(3):
        battle(p, f'G.LATE.ch10.prophecy(S,{index})', 'cairo_day_ch10', 'iggy')
        inert_boss(p)
        if index==0:
            p.evaluate('() => {G.world.player.x=410;}')
            press(p,'e')
        elif index==1:
            for _ in range(3):
                p.evaluate('() => {G.world.player.x=G.world.fight.data.drumX;}')
                press(p,'e')
        else:
            p.evaluate('() => {G.world.fight.boss.x=638;}')
        tick(p,910)
        ok=reach(p,"window.__lateResult==='resolved'",180)
        check(f'第{index+1}预言真实E操作15秒后兑现',ok,state(p))
    battle(p, 'G.LATE.ch10.prophecy(S,1)', 'cairo_day_ch10','iggy')
    inert_boss(p)
    tick(p, 930)
    assert reach(p,'!!G.ui.menu',600,True)
    # 菜单打开 0.08 秒内的确认键会被忽略（防连按跳过）；等菜单真正可选再按 Enter 选「再来一次」。
    assert reach(p,'G.ui.menu&&G.ui.menu.t>0.15',60)
    press(p,'Enter',20)
    assert reach(p,'G.world.fight&&G.world.fight.attempt===1&&G.world.combat',600,True)
    r=p.evaluate('() => ({id:G.world.fight.id,attempt:G.world.fight.attempt,done:G.hud.steps.done,t:G.world.fight.t})')
    check('预言失败仅重当前预言并保留前项完成数',r['id']=='b22_prophecy2' and r['attempt']==1 and r['done']==1 and r['t']<1,r)


def test_cream(p):
    battle(p,'G.LATE.ch11.creamHidden()','hall_ch11','polnareff')
    r=p.evaluate('''() => {const c=G.world.fight,e=c.boss,p=c.player;
      const hp=e.hp;const hidden=G.combat.hit(p,e,{dmg:10,slot:'J1',push:0,guard:'none'});
      c.data.phase='expose';e.invuln=e.iframe=0;
      const shown=G.combat.hit(p,e,{dmg:10,slot:'J1',push:0,guard:'none'});
      return {hidden:hidden.dmg,shown:shown.dmg,lost:hp-e.hp};}''')
    check('奶油虚空免疫、探头40帧伤害翻倍',r=={'hidden':0,'shown':20,'lost':20},r)
    p.evaluate('''() => {const c=G.world.fight;
      c.data.phase='dash';c.data.phaseT=0;c.data.hit=false;c.data.vx=-120;
      c.boss.x=c.player.x+1;c.boss.y=c.player.y;c.data.targetY=c.player.y;
      c.player.invuln=c.player.iframe=0;window.__creamHp=c.player.hp;}''')
    tick(p,1)
    r=p.evaluate('() => ({lost:window.__creamHp-G.world.player.hp,want:Math.round(G.world.player.maxHp*.4),hit:G.world.fight.data.hit})')
    check('奶油接触虚空扣最大HP40%',r['lost']==r['want'] and r['hit'],r)
    battle(p,'G.LATE.ch11.creamSun()','hall_ch11','polnareff')
    inert_boss(p)
    p.evaluate('() => {G.world.fight.boss.hp=399;}')
    assert reach(p,'G.world.fight&&G.world.fight.data.beam&&!G.world.cine',1200,True)
    p.evaluate('() => {G.world.fight.boss.x=274;}')
    tick(p,1)
    check('奶油仅进阳光位置不能自动结束',p.evaluate('() => G.world.combat&&!G.world.fight.data.sunWin'),state(p))
    p.evaluate('() => {G.world.player.x=245;G.world.player.facing=1;}')
    press(p,'u',5)
    ok=reach(p,"window.__lateResult==='resolved'",1400,True)
    check('奶油阳光U飞踢收尾、伊奇离队',ok and p.evaluate('() => G.party.pool.iggy.mem.away'),state(p))


def test_dio_growth(p):
    battle(p,'G.LATE.final.dioFight(1)','street_fin')
    inert_boss(p)
    p.evaluate('''() => {const c=G.world.fight;c.data.stops=1;c.data.nextStop=c.t;}''')
    assert reach(p,'G.time.phase==="stopped"&&G.ui.qte',300)
    t=p.evaluate('() => G.time.t')
    tick(p,60)
    r=p.evaluate('() => ({phase:G.time.phase,t:G.time.t,q:G.ui.qte&&G.ui.qte.t,frozen:G.time.isFrozen(G.world.player)})')
    check('首次觉醒QTE在stopped内、两秒演出暂停时间轴',r['phase']=='stopped' and r['t']==t and r['q']>=1 and r['frozen'],r)
    for _ in range(8): press(p,'j',2)
    assert reach(p,'G.flags.dioGrowth&&!G.world.fight.data.growing',20)
    p.keyboard.down('ArrowRight')
    x=p.evaluate('() => G.world.player.x')
    tick(p,25)
    r=p.evaluate('() => ({x:G.world.player.x,t:G.time.t,frozen:G.time.isFrozen(G.world.player)})')
    check('8次J成功后真实移动且完整半秒免冻',r['x']>x and r['t']<.5 and not r['frozen'],r)
    tick(p,10);p.keyboard.up('ArrowRight')
    check('半秒结束重新冻结、停止段仍1.2秒',p.evaluate('() => G.time.phase==="stopped"&&G.time.isFrozen(G.world.player)&&G.time.o.dur===1.2'),state(p))
    assert reach(p,'!G.time.active',200)
    check('首次觉醒恢复时间轴结束且无遗留QTE',p.evaluate('() => !G.ui.qte&&!G.world.fight.data.growing'),state(p))
    p.evaluate('''() => {const c=G.world.fight;c.boss.hp=1;c.data.nextStop=Infinity;}''')
    check('D1达到目标HP正确退出',reach(p,"window.__lateResult==='resolved'",120),state(p))


def test_dio_knives(p):
    battle(p,'G.LATE.final.dioFight(2)','street_fin')
    inert_boss(p)
    p.evaluate('() => {G.flags.dioGrowth=true;G.world.fight.data.nextStop=G.world.fight.t;}')
    assert reach(p,'G.time.phase==="stopped"&&G.world.fight.data.stop.knives.length===16',300)
    press(p,'j')
    r=p.evaluate('() => ({n:G.world.fight.data.stop.knives.length,dead:G.world.fight.data.stop.knives.filter(k=>k.dead).length})')
    check('D2摆16刀、活动半秒内J弹开一面',r['n']==16 and 7<=r['dead']<=9,r)
    assert reach(p,'!G.time.active',180)
    tick(p,70)
    r=p.evaluate('() => ({magazines:G.world.fight.data.magazines,events:G.dbg.events.filter(e=>e.type==="magazine_block").slice(-3)})')
    check('真实飞刀前三刀由杂志抵挡',r['magazines']==0 and len(r['events'])==3,r)
    p.evaluate('''() => {const c=G.world.fight;G.time.clear();c.data.stop=null;c.data.nextStop=Infinity;
      c.player.hp=c.player.maxHp*.3;c.player.invuln=c.player.iframe=c.player.stunT=c.player.stopT=0;
      c.player.state='idle';c.boss.atk=c.boss.tele=null;G.world.shots=[];G.input.clear();}''')
    p.keyboard.down('l');p.keyboard.down('k');tick(p,170)
    check('L+K未满三秒不进入装死',p.evaluate('() => !G.world.fight.data.playDead'),state(p))
    tick(p,20);p.keyboard.up('l');p.keyboard.up('k')
    assert reach(p,'G.world.fight.data.playDead',100)
    assert reach(p,'!!G.world.fight.data.counterUntil&&!G.world.cine',1400,True)
    r=p.evaluate('() => ({dmg:G.world.player.dmgOut,window:G.world.fight.data.counterUntil-G.world.fight.t})')
    check('装死接波鲁纳雷夫助攻并给90帧双倍反击',r['dmg']==2 and 1.3<r['window']<=1.5,r)
    tick(p,100)
    check('反击90帧结束恢复正常伤害',p.evaluate('() => G.world.player.dmgOut===1'),state(p))
    p.evaluate('() => {G.world.fight.boss.hp=1;}')
    check('D2装死后目标HP正确退出',reach(p,"window.__lateResult==='resolved'",120),state(p))


def test_dio_final(p):
    battle(p,'G.LATE.final.dioFight(3)','street_fin')
    inert_boss(p)
    p.evaluate('() => {G.world.fight.boss.hp=1500;}')
    assert reach(p,'G.ui.qte&&G.ui.qte.id==="roadroller"',700,True)
    check('压路机QTE进入黄色时停与四秒对冲',p.evaluate('() => G.time.active&&G.time.o.tint==="yellow"&&G.ui.qte.time===4'),state(p))
    mash(p)
    assert reach(p,'G.time.active&&G.time.o.tint==="blue"',300,True)
    check('压路机后承太郎蓝色时停覆盖DIO',p.evaluate('() => G.time.by===G.world.player&&G.time.immune.has(G.world.player)'),state(p))
    assert reach(p,'G.flags.starWorld&&!G.world.cine',400,True)
    p.evaluate('''() => {const c=G.world.fight;c.data.nextStop=Infinity;c.player.energy=100;
      c.player.state='idle';c.player.invuln=c.player.iframe=c.player.stunT=0;}''')
    press(p,'u')
    # 时停先有 0.924 秒预警（warn，世界还没冻住、照常结算）；排队要在真正冻结的 stopped 段验证。
    assert reach(p,'G.time.active&&G.time.o.tint==="blue"&&G.time.phase==="stopped"&&!G.world.cine',250)
    p.evaluate('''() => {const c=G.world.fight,e=c.boss,p=c.player;window.__blueHP=e.hp;
      p.x=e.x-24;p.y=e.y;p.facing=1;p.atk=null;p.state='idle';G.input.clear();}''')
    press(p,'j',12)
    r=p.evaluate('''() => {const c=G.world.fight,e=c.boss,q=G.time.queue.get(e)||[];
      return {queued:q.length,hp:e.hp,old:window.__blueHP,frozen:G.time.isFrozen(e),phase:G.time.phase,
        who:G.time.by&&G.time.by.cid,dur:G.time.o&&G.time.o.dur};}''')
    check('D3真实U替换时停、冻住目标伤害排队',r['queued']>=1 and r['hp']==r['old'] and r['frozen'] and r['phase']=='stopped' and r['who']=='jotaro' and r['dur']==2,r)
    assert reach(p,'!G.time.active',240)
    tick(p,15)
    r=p.evaluate('() => ({hp:G.world.fight.boss.hp,old:window.__blueHP,left:G.time.queue.size})')
    check('D3恢复后排队伤害正确结算',r['hp']<r['old'] and r['left']==0,r)
    p.evaluate('''() => {const c=G.world.fight;c.boss.hp=300;c.player.hp=45;c.player.minHp=0;}''')
    assert reach(p,'G.ui.qte&&G.ui.qte.id==="dio_final"',120)
    tick(p,400)
    assert reach(p,'G.ui.qte&&G.ui.qte.id==="dio_final"&&G.ui.qte.result==null',900,True)
    r=p.evaluate('() => ({hp:G.world.player.hp,id:G.world.fight.id,rate:G.ui.qte.rate})')
    check('最后一拳失败扣60保底1HP、仅重QTE并降30%',r['hp']==1 and r['id']=='b28d3_dio' and r['rate']<=.14,r)
    mash(p)
    check('最后一拳重试成功正确退出终战',reach(p,"window.__lateResult==='resolved'",200),state(p))


def test_dealer(p):
    prep(p, 'cafe_ch10')
    start(p, 'G.LATE.ch10.catchCheat(S,50,0)')
    save_mini(p)
    tick(p, 40)
    press(p, 'j')
    tick(p, 27)
    press(p, 'j')
    reach(p, "window.__lateResult==='resolved'", 120)
    r=p.evaluate('() => window.__lastMini')
    check('扑克提前按 J 后窗口内再按也不能抓牌', r['tooEarly'] and not r['caught'], r)
    prep(p, 'cafe_ch10')
    start(p, 'G.LATE.ch10.catchCheat(S,50,1)')
    save_mini(p)
    tick(p, 66)
    press(p, 'j')
    reach(p, "window.__lateResult==='resolved'", 120)
    r=p.evaluate('() => window.__lastMini')
    check('扑克额外抽牌窗口内真实 J 抓出千', r['caught'] and not r['tooEarly'], r)


def test_labyrinth(p):
    prep(p, 'illusion_ch11', 'avdol')
    start(p, 'G.LATE.ch11.labyrinth()')
    assert reach(p, 'G.lateGame&&G.lateGame.type==="labyrinth"')
    press(p, 'u')
    p.evaluate('() => {G.world.player.x=G.lateGame.wallX-20;}')
    for _ in range(3): press(p, 'j', 10)
    r=p.evaluate('() => ({hits:G.lateGame.hits, enemy:G.world.stage.actors.filter(a=>a.id==="late_kennyg"&&!a.remove).length})')
    check('迷宫 U 调查、三次敲墙暴露肯尼G', r=={'hits':3,'enemy':1}, r)
    tick(p, 1250)
    r=p.evaluate('() => ({hits:G.lateGame.hits, found:G.lateGame.found, enemy:G.world.stage.actors.filter(a=>a.id==="late_kennyg"&&!a.remove).length, variant:G.lateGame.variant})')
    check('20秒幻觉循环清理旧敌人与调查状态', r['hits']==0 and not r['found'] and r['enemy']==0 and r['variant']==1, r)
    tick(p, 2500)
    check('迷宫60秒失败只进入当前机关对白', p.evaluate('() => !!G.ui.dlg&&!G.ui.menu'), state(p))
    assert reach(p, 'G.lateGame&&G.lateGame.type==="labyrinth"', 600, True)
    press(p, 'u')
    p.evaluate('() => {G.world.player.x=G.lateGame.wallX-20;}')
    for _ in range(4): press(p, 'j', 10)
    ok=reach(p, "window.__lateResult==='resolved'", 600, True)
    check('迷宫重试调查、第四次J击倒本体通关', ok, state(p))
    p.screenshot(path=str(OUT/'late_labyrinth.png'))


def test_baseball(p):
    prep(p, 'game_ch11')
    start(p, 'G.LATE.ch11.baseball()')
    for attempt in range(25):
        assert reach(p, 'G.lateGame&&G.lateGame.type==="baseball"', 600, True)
        save_mini(p)
        for ball in range(12):
            press(p, 'ArrowRight')
            press(p, 'ArrowUp')
            if ball==8: press(p, 'q')
            press(p, 'j')
            tick(p, 50)
        if reach(p, "window.__lateResult==='resolved'", 70): break
        reach(p, 'G.lateGame&&G.lateGame.type==="baseball"', 600, True)
    r=p.evaluate('() => window.__lastMini')
    events=p.evaluate('() => G.dbg.events.filter(e=>e.type==="baseball_pitch").slice(-12)')
    check('棒球真实投12球，第三局Q委托并赢下三局', p.evaluate('() => window.__lateResult==="resolved"') and r['ball']==12 and r['delegated'] and r['own']>r['enemy'], r)
    check('前两局读取自己、第三局读取藤蔓输入', len(events)==12 and all(not e['delegated'] for e in events[:8]) and all(e['delegated'] for e in events[8:]), events)
    p.screenshot(path=str(OUT/'late_baseball.png'))


def test_stairs(p):
    prep(p, 'stairs_fin','polnareff')
    start(p, 'G.LATE.final.stairs()')
    assert reach(p, 'G.lateGame&&G.lateGame.type==="stairs"', 800, True)
    save_mini(p)
    hp=p.evaluate('() => G.world.player.hp')
    p.keyboard.down('ArrowRight')
    tick(p, 250)
    p.keyboard.up('ArrowRight')
    ok=reach(p, "window.__lateResult==='resolved'", 1400, True)
    r=p.evaluate('() => ({resets:window.__lastMini.resets,hp:G.world.player.hp,combat:G.world.combat})')
    check('楼梯两次时间回退无HP损失且正常继续剧情', ok and r['resets']==2 and r['hp']==hp and not r['combat'], r)


def test_web(p):
    prep(p, 'roof_fin','kakyoin')
    start(p, 'G.LATE.final.roofWeb()')
    assert reach(p, 'G.lateGame&&G.lateGame.type==="web"', 600)
    hp=p.evaluate('() => G.world.player.hp')
    tick(p, 325)
    r=p.evaluate('() => ({hp:G.world.player.hp,kind:G.lateGame.kind})')
    check('布网5秒飞刀24帧预警后伤12', r['kind']=='knife' and abs(r['hp']-(hp-12))<.01, r)
    p.evaluate('() => {G.lateGame.nodes[0].set=true;}')
    tick(p, 275)
    press(p, 'k', 42)
    r=p.evaluate('() => ({cuts:G.lateGame.cuts,hp:G.world.player.hp})')
    check('布网切丝40帧预警内K闪避保留节点', r['cuts']==0 and r['hp']==hp-12, r)
    tick(p, 1350)
    assert reach(p, 'G.lateGame&&G.lateGame.type==="web"', 900, True)
    check('布网30秒失败重试，未倒退整章', p.evaluate('() => G.lateGame.t<1&&G.dbg.shot==="final_web"'), state(p))
    for x in [55,125,195,265,335,405,475,550]:
        p.evaluate('x => {G.world.player.x=x;}', x)
        press(p,'j',3)
    assert reach(p, 'G.lateGame&&G.lateGame.type==="clock"', 1400, True)
    press(p,'j')
    assert reach(p, 'G.lateGame&&G.lateGame.type==="clock"', 600, True)
    check('最后一发射偏只重钟面瞄准', p.evaluate('() => G.dbg.shot==="final_clock"&&G.lateGame.t<1'), state(p))
    p.keyboard.down('ArrowRight'); tick(p,92); p.keyboard.up('ArrowRight')
    p.keyboard.down('ArrowUp'); tick(p,28); p.keyboard.up('ArrowUp')
    p.screenshot(path=str(OUT/'late_clock.png'))
    press(p,'j')
    ok=reach(p, "window.__lateResult==='resolved'", 1400, True)
    check('最后一发方向键瞄准成功，花京院离队', ok and p.evaluate('() => G.party.pool.kakyoin.mem.away'), state(p))


def cancel_case(p, expression, stage='street_fin'):
    prep(p,stage)
    start(p,expression)
    tick(p,60)
    p.evaluate('async () => {await G.goTitle();}')
    tick(p,300)
    r=p.evaluate('''() => ({result:window.__lateResult,scene:G.scene.name,ticks:G.world.ticks.length,
      combat:G.world.combat,time:G.time.active,mini:G.lateGame,insert:G.world.insert,qte:G.ui.qte})''')
    check('返回标题取消 '+expression, r['result']=='RunCancelled' and r['scene']=='title' and r['ticks']==0 and not r['combat'] and not r['time'] and r['mini'] is None and r['insert'] is None and r['qte'] is None, r)


def main():
    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True,exist_ok=True)
    errors=[]
    began=time.monotonic()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=['--autoplay-policy=no-user-gesture-required'])
        p=browser.new_page(viewport={'width':1280,'height':720})
        p.on('console',lambda m: errors.append({'type':m.type,'text':m.text}) if m.type in ('warning','error') else None)
        p.on('pageerror',lambda e: errors.append({'type':'pageerror','text':str(e),'stack':getattr(e,'stack',None)}))
        p.goto((GAME/'index.html').as_uri()+'?autotest=1&touch=0')
        p.wait_for_function('G.booted&&G.ui.menu',timeout=60000)
        p.evaluate('() => {G.playFrom(10);}')
        p.wait_for_function('G.world.stage&&G.scene.name==="world"',timeout=30000)
        p.evaluate('() => {window.__worldScene=G.scene;window.S=G.S;G.dbg.hold=true;}')
        # preloadPack 只解码已经插进页面的包；第11章 / 终章的背景包要先 loadPack（插脚本 + 解码），和 G.playFrom 换章一样。
        p.evaluate('''async () => {for (const key of ['bg_common','bg_ch10','bg_ch11','bg_final']) await G.res.loadPack(key);}''')
        for fn in [test_dealer,test_labyrinth,test_baseball,test_stairs,test_web,
                   test_prophecy,test_cream,test_dio_growth,test_dio_knives,test_dio_final]:
            try:
                fn(p)
            except Exception as e:
                check(fn.__name__+'测试中断',False,{'error':str(e),'state':state(p)})
                p.screenshot(path=str(OUT/(fn.__name__+'_failure.png')))
        for expr,stage in [('G.LATE.ch11.baseball()','game_ch11'),
                           ('G.LATE.ch11.labyrinth()','illusion_ch11'),
                           ('G.LATE.final.dioFight(1)','street_fin'),
                           ('G.LATE.final.dioFight(3)','street_fin')]:
            try:
                cancel_case(p,expr,stage)
            except Exception as e:
                check('取消测试中断 '+expr,False,{'error':str(e),'state':state(p)})
        missing=p.evaluate('''() => ({image:[...G.dbg.missingImg],head:[...G.dbg.missingHead],glyph:[...G.dbg.missingGlyph],sfx:[...G.dbg.missingSfx],fallback:[...G.dbg.animFallbacks]})''')
        check('后段真实资源和动作完整',not any(missing.values()),missing)
        check('后段控制台warning/error/pageerror为零',not errors,errors)
        browser.close()
    result={'ok':all(r['ok'] for r in ROWS),'checks':len(ROWS),'results':ROWS,'console':errors,'seconds':round(time.monotonic()-began,2)}
    (OUT/'test_late.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'ok':result['ok'],'checks':result['checks'],'failed':[r['name'] for r in ROWS if not r['ok']]},ensure_ascii=False))
    return 0 if result['ok'] else 1


if __name__=='__main__':
    raise SystemExit(main())
