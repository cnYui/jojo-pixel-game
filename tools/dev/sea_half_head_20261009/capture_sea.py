"""从正式入口捕获落水形象，检查真实背景、动作映射及朝向。"""
import sys
sys.dont_write_bytecode = True

import json
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
GAME = HERE.parents[2]


def main():
    errors = []
    shots = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 720}, device_scale_factor=1)
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if m.type in ('warning', 'error') else None)
        page.goto((GAME / 'index.html').as_uri() + '?autotest=1&touch=0')
        page.wait_for_function('window.G && G.booted', timeout=60000)
        page.evaluate("""async () => {
            G.dbg.hold = true;
            G.cancelRun(); G.ui.reset(); G.party.reset(); G.post.clear(); G.fx.clear();
            G.world.stage = null; G.world.player = null; G.world.insert = null;
            G.world.combat = false; G.world.free = false; G.S.busy = true;
            G.setScene({
                name: '落水验收', frozen: true,
                update: dt => G.ui.update(dt),
                drawWorld: g => G.world.draw(g), drawUI: g => G.ui.draw(g),
                drawTop: g => G.ui.drawTop(g),
                hasPixel: () => G.world.hasPixel(),
                drawPixel: (P, layer) => G.world.drawPixel(P, layer)
            });
            await G.res.loadPack('bg_common'); await G.res.loadPack('bg_ch2');
            G.S.party(['jotaro', 'joseph', 'avdol', 'kakyoin'], {leader: 'joseph'});
            await G.S.setStage('sea_ch1', {x: 160, y: 156, music: null, fade: false});
            ['jotaro', 'joseph', 'avdol', 'kakyoin'].forEach((cid, i) => {
                const a = G.S.actor(cid);
                a.x = 90 + i * 46; a.y = 156; a.follow = null; a.facing = 1;
                G.S.pose(a, 'float', {freeze: 0});
            });
            G.fadeA = 0; G.flashA = 0;
            G.S.say('joseph', '这是我人生第三次坠机了！', {pos: 'top'}).catch(G.cancelIgnore);
            G.dbg.tick(90);
        }""")
        for fi in range(2):
            page.evaluate("""fi => {
                G.world.stage.actors.forEach(a => G.S.pose(a, 'float', {freeze: fi}));
                G.render();
            }""", fi)
            filename = f'第一幕海面_第{fi + 1}帧.png'
            page.locator('#screen').screenshot(path=str(HERE / filename))
            shots.append(filename)

        # 五人的两个朝向都使用正式打包资源，能发现图集更新后锚点不一致的问题。
        page.evaluate("""async () => {
            G.cancelRun(); G.ui.reset(); G.party.reset();
            G.world.stage = null; G.world.player = null;
            const ids = ['jotaro', 'joseph', 'avdol', 'kakyoin', 'polnareff'];
            G.S.party(ids, {leader: 'jotaro'});
            await G.S.setStage('sea_ch1', {x: 160, y: 156, music: null, fade: false});
            ids.forEach((cid, i) => {
                const a = G.S.actor(cid);
                a.x = 52 + i * 54; a.y = 156; a.follow = null;
                // 单屏队伍默认只显示四人，验收需要把第五人的落水帧也呈现出来。
                a.visible = true;
                G.S.pose(a, 'float', {freeze: 0});
            });
        }""")
        for facing in (1, -1):
            for fi in range(2):
                page.evaluate("""({facing, fi}) => {
                    G.world.stage.actors.forEach(a => {
                        a.facing = facing; G.S.pose(a, 'float', {freeze: fi});
                    });
                    G.render();
                }""", {'facing': facing, 'fi': fi})
                filename = f'五人海面_向{"右" if facing == 1 else "左"}_第{fi + 1}帧.png'
                page.locator('#screen').screenshot(path=str(HERE / filename))
                shots.append(filename)

        runtime = page.evaluate("""() => ({
            入口: location.href,
            舞台: G.world.stage.id,
            图片缺失: [...G.dbg.missingImg],
            动作回退: [...G.dbg.animFallbacks],
            角色: G.world.stage.actors.map(a => ({
                id: a.cid, 动作: a.anim, 帧数: a.atlas.frames('float'),
                x: a.x, y: a.y, 锚点: a.atlas.m.pivot,
                图集: a.atlas.key, 已解码: a.atlas.ready()
            })),
            异常: G.dbg.events.filter(e => /error|missing/.test(e.type))
        })""")
        browser.close()

    # 放大局部仅用最近邻，便于确认眼线以下确实没有人物像素。
    shot = Image.open(HERE / shots[0]).convert('RGB')
    crop = shot.crop((60 * 4, 128 * 4, 256 * 4, 164 * 4))
    crop.resize((crop.width * 2, crop.height * 2), Image.Resampling.NEAREST).save(HERE / '第一幕海面_局部放大.png')
    result = {'运行资源': runtime, '控制台异常': errors, '截图': shots}
    (HERE / '海面运行验收.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors or runtime['图片缺失'] or runtime['动作回退'] or runtime['异常']:
        raise RuntimeError('海面运行验收发现异常，详见海面运行验收.json')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
