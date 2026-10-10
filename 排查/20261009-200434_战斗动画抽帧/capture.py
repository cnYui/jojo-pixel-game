"""用当前成品入口和生产战斗代码逐帧取证，隔离剧情与敌方反击。"""
from __future__ import annotations

import base64
from collections import Counter
from io import BytesIO
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
GAME = OUT.parents[1]
NAMES = {"joseph": "二乔（乔瑟夫）", "jotaro": "承太郎", "kakyoin": "花京院", "avdol": "阿布德尔", "polnareff": "波鲁纳雷夫"}
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"

SETUP = r"""async () => {
  G.dbg.hold = true;
  window.auditEntry = G.playFrom(1);
  await G.res.loadPack('bg_common');
  await G.res.loadPack('bg_ch1');
  G.cancelRun();
  await Promise.resolve();
  G.ui.reset(); G.S.busy = false; G.S.cardOn = false;
  G.S.ambient(null); G.S._filters.clear();
  return {scene: G.scene.name, chars: Object.keys(G.D.chars).length};
}"""

CAPTURE = r"""async ({cid, scenario}) => {
  const W = G.world;
  G.cancelRun(); G.ui.reset(); G.S.busy = false; G.S.cardOn = false;
  G.time.clear(); G.input.clear(); G.fx.clear(); G.post.clear();
  G.hitStopAll_t = 0; G.slowAllT = 0; G.slowAllK = 1; G.fadeA = 0;
  W.cine = W.insert = null; W.slow = 1; W._combatSlowT = 0;
  W.anims = []; W.ticks = []; W.zoom = null;
  G.cam.zoom = null; G.cam.x = G.cam.y = 0; G.cam.shakeDur = 0;
  G.party.reset(); G.party.set([cid], {leader: cid});
  const p = G.party.leader(); G.combat.resetActor(p);
  W.setStage({id:'animation_audit', bg:'hongkong_night', x0:0, x1:320,
    yMin:150, yMax:176}, {player:p, x:100, y:163});
  const e = new G.Actor('avdol', scenario === 'single_hit' ? 153 : 270, 163,
    {team:'enemy', hp:10000, minHp:1, stand:null, brain:()=>true, noCharge:true});
  W.stage.actors.push(e); W.combat = true; W.free = false;
  W.fight = {spec:{arena:[0,320], kitOverride:{}, dmgScale:1, playerMinHp:0}, emit(){}};
  p.facing = 1; e.facing = -1;
  p.stand?.summon({instant:true, sfx:false});
  // 召唤的短暂藤蔓先消失，避免把召唤效果误认成攻击效果。
  for (let i=0; i<60; i++) { G.dbg.tick(1, 1/60); await Promise.resolve(); }
  const t0 = G.clk.ui, trace = [], pictures = [];
  let rushStart = null;
  const requested = new Set();
  const snap = (i) => {
    const s = p.stand, at = p.atlasFor(p.anim), br = at.resolve(p.anim, p.skin);
    const sr = s?.atlas?.resolve(s.pose, s.skin);
    return {frame:i, seconds:G.clk.ui-t0, state:p.state,
      attack:p.atkId, attackSlot:p.atk?.slot || null, attackT:p.atkT,
      bodyLogical:p.anim, bodyAction:br.name, bodyFrame:p.frameIndex(), bodyT:p.animT,
      bodyKind:br.a.kind, bodyFrames:br.a.frames,
      standMode:s?.mode || null, standLogical:s?.pose || null,
      standAction:sr?.name || null, standFrame:s?.frame() ?? null,
      standT:s?.poseT || 0, standKind:sr?.a.kind || null,
      vine:s?._vine ? {...s._vine} : null, rushT:p.rush?.t || null,
      hp:e.hp, hitstop:G.hitStopAll_t, x:p.x, enemyX:e.x};
  };
  const capture = (i, state, label) => pictures.push({frame:i, label, state,
    png:G.wv.toDataURL('image/png')});
  G.render(); const before=snap(0); trace.push(before); capture(0,before,'出招前');
  for (let i=1; i <= (scenario === 'single_hit' ? 60 : 190); i++) {
    if (i===1) G.input.inject('attack');
    // 各角色的窗口不同，按实际招式时钟输入，避免固定节奏漏掉合法连招。
    if (scenario !== 'single_hit' && p.atk && rushStart===null && !requested.has(p.atk)) {
      const m=p.atk, threshold=m.slot==='J3' ? (m.active[0]+m.active[1])/2
        : Math.max(m.active[0]+G.combat.CFG.comboBufFrom, m.link-2/60);
      if (p.atkT >= threshold) { G.input.inject('attack'); requested.add(m); }
    }
    if (p.state==='rush' && rushStart !== null && (i-rushStart)%6===0) G.input.inject('attack');
    G.dbg.tick(1, 1/60); await Promise.resolve();
    const state = snap(i); trace.push(state);
    if (state.state==='rush' && rushStart===null) rushStart=i;
    if (scenario === 'single_hit' && [1,5,9,13,17,21,29,37,45].includes(i))
      capture(i,state,`${i} 帧 / ${Math.round(i/60*1000)} 毫秒`);
    if (scenario !== 'single_hit' && [1,9,19,30].includes(i)) capture(i,state,`连招第 ${i} 帧`);
    if (rushStart !== null && [0,6,12,24,36,60,90].includes(i-rushStart))
      capture(i,state,`连打 +${i-rushStart} 帧`);
  }
  return {cid, scenario, trace, pictures, rushStart,
    events:[...new Map(G.dbg.events.filter(x=>x.type==='loop_error')
      .map(x=>[x.where+'|'+x.msg,{type:x.type,msg:x.msg,where:x.where}])).values()]};
}"""

SPRITES = r"""() => {
  const at=G.atlas('joseph'), result=[];
  for (const [logical, frame] of [['point',0],['whip',0],['whip',1]]) {
    const p=at.pix(logical, frame), c=G.mkCanvas(p.w,p.h,true), g=c.g;
    const im=g.createImageData(p.w,p.h); new Uint32Array(im.data.buffer).set(p.u32);
    g.putImageData(im,0,0);
    result.push({logical,frame,meta:at.resolve(logical),png:c.toDataURL('image/png')});
  }
  return result;
}"""


def decode(data):
    return Image.open(BytesIO(base64.b64decode(data.split(",", 1)[1]))).convert("RGBA")


def contact_sheet(rows, title, subtitle, path, crop=(60, 89, 226, 177), scale=2):
    font = ImageFont.truetype(FONT_PATH, 19)
    small = ImageFont.truetype(FONT_PATH, 16)
    head = ImageFont.truetype(FONT_PATH, 28)
    tw, th = (crop[2]-crop[0])*scale, (crop[3]-crop[1])*scale
    cols = max(len(pics) for _, pics in rows)
    cell_w, row_h = tw+14, th+83
    canvas = Image.new("RGB", (cols*cell_w+32, 98+len(rows)*row_h), "#11121a")
    d = ImageDraw.Draw(canvas)
    d.text((18, 12), title, fill="#ffe070", font=head)
    d.text((18, 57), subtitle, fill="#d0d3df", font=small)
    for ri, (name, pictures) in enumerate(rows):
        top = 98+ri*row_h
        d.text((18, top), name, fill="#ffffff", font=font)
        for ci, item in enumerate(pictures):
            x, y = 18+ci*cell_w, top+32
            src = decode(item["png"]).crop(crop).resize((tw, th), Image.Resampling.NEAREST)
            canvas.paste(src, (x,y), src)
            d.text((x,y+th+5), item["label"], fill="#e2dcd0", font=small)
            s=item["state"]
            action = f"本体 {s['bodyAction']}[{s['bodyFrame']}]"
            if s['standAction']: action += f" · 替身 [{s['standFrame']}]"
            d.text((x,y+th+27), action, fill="#9db6cc", font=small)
    canvas.save(path)


def main():
    errors, results = [], []
    (OUT / "frames").mkdir(exist_ok=True)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
        page=browser.new_page(viewport={"width":1280,"height":720})
        page.on("pageerror", lambda e: errors.append({"消息":str(e),"调用栈":getattr(e,'stack',None)}))
        page.goto((GAME / "index.html").as_uri()+"?autotest=1", wait_until="load")
        page.wait_for_function("window.G && G.booted", timeout=120000)
        setup=page.evaluate(SETUP)
        if setup["scene"] != "world":
            raise RuntimeError(f"未进入生产世界场景：{setup}")
        for cid in NAMES:
            for scenario in ("single_hit", "combo_rush"):
                item=page.evaluate(CAPTURE,{"cid":cid,"scenario":scenario})
                results.append(item)
                for picture in item["pictures"]:
                    decode(picture["png"]).save(OUT/"frames"/f"{cid}_{scenario}_{picture['frame']:03}.png")
            print(f"已抽帧：{NAMES[cid]}", flush=True)
        sprites=page.evaluate(SPRITES)
        browser.close()

    singles = [(NAMES[r['cid']], [p for p in r['pictures'] if p['frame'] in [1,5,9,13,17,21]])
               for r in results if r['scenario']=='single_hit']
    contact_sheet(singles, "普通攻击：当前游戏的实际抽帧", "每格间隔 4 帧；生产入口、角色素材与战斗代码；敌人不反击。", OUT/"普通攻击_角色对照.png")
    rushes=[(NAMES[r['cid']], [p for p in r['pictures'] if p['label'].startswith('连打 +') and p['label']!='连打 +90 帧'])
             for r in results if r['scenario']=='combo_rush']
    if any(not pics for _,pics in rushes):
        raise RuntimeError(f"有角色未触发连打：{[(n,len(p)) for n,p in rushes]}")
    contact_sheet(rushes, "持续连打：替身是否真的重复动作", "在空处打完三连后持续按 J；以各角色进入连打的时刻对齐。", OUT/"持续连打_角色对照.png")
    joseph=next(r for r in results if r['cid']=='joseph' and r['scenario']=='single_hit')
    contact_sheet([(NAMES['joseph'],[p for p in joseph['pictures'] if p['frame'] in [0,1,5,9,13,17]])],
                  "二乔普通攻击：出招后只有同一张指人图", "原始像素放大 3 倍；下方附当前运行素材中的挥鞭动作。", OUT/"二乔_普通攻击.png", scale=3)
    body=Image.open(OUT/"二乔_普通攻击.png").convert("RGB")
    combined=Image.new('RGB',(body.width,body.height+300),'#11121a')
    combined.paste(body,(0,0)); d=ImageDraw.Draw(combined)
    font=ImageFont.truetype(FONT_PATH,22)
    d.text((18,body.height+8),"当前素材：point 1 帧（正在用） · whip 2 帧（普通攻击没有调用）",font=font,fill='#ffe070')
    for i,item in enumerate(sprites):
        src=decode(item['png']).resize((328,228),Image.Resampling.NEAREST)
        x=18+i*390; y=body.height+48
        combined.paste(src,(x,y),src)
        d.text((x,y+232),f"{item['logical']} 第 {item['frame']+1} 帧",font=font,fill='#d0d3df')
    combined.save(OUT/"二乔_抽帧与素材.png")

    summary=[]
    for r in results:
        active=[s for s in r['trace'] if s['state'] in ('attack','rush','rushEnd')]
        rush=[s for s in r['trace'] if s['state']=='rush']
        summary.append({"角色":NAMES[r['cid']],"场景":r['scenario'],
          "攻击时本体图":sorted({f"{s['bodyAction']}[{s['bodyFrame']}]" for s in active}),
          "连打时替身图":sorted({f"{s['standAction']}[{s['standFrame']}]" for s in rush}),
          "连打替身帧计数":dict(Counter(str(s['standFrame']) for s in rush)),
          "连打进入帧":r['rushStart'],"敌人扣血":10000-r['trace'][-1]['hp'],
          "普通攻击有藤蔓":any(s['vine'] is not None for s in active) if r['scenario']=='single_hit' else None,
          "引擎异常":r['events']})
    for r in results:
        for p in r['pictures']: p.pop('png')
    for s in sprites: s.pop('png')
    report={"入口":str(GAME/'index.html'),"步长秒":1/60,"setup":setup,
      "浏览器异常":errors,"summary":summary,"results":results,"二乔运行素材":sprites}
    (OUT/"抽帧记录.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({"输出目录":str(OUT),"浏览器异常":errors,"summary":summary},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
