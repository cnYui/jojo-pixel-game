# 复用第四部的描边字、名牌、替身卡和地点卡生成器；重定向所有输出和字体缓存，保持第四部只读。
import sys
from PIL import Image, ImageDraw
from p5_paths import REPO, ASSETS, META, P5, save_json
from p5_font import font_path

sys.path.insert(0, str(REPO / '第四部/tools/art'))
import p4_ui as UI


def build():
    UI.OUT = str(ASSETS / 'ui')
    UI.LIB.FONTS = str(P5 / 'tools/font_cache')
    UI.LIB.WQY = str(font_path())
    names = {
        'koichi': ('广濑康一', '#81b954', '来那不勒斯寻找一个少年的替身使者'),
        'giorno': ('乔鲁诺·乔巴拿', '#edc862', '十五岁｜替身：黄金体验'),
        'bucciarati': ('布加拉提', '#b9caf4', '街头干部｜替身：钢链手指'),
    }
    result = {'namecards': {cid: UI.namecard(cid, *args) for cid, args in names.items()},
              'standcards': {}, 'locations': {}, 'titles': {}, 'specials': {}, 'sfx': {}, 'map': {}, 'vs': {}}
    for sid, cn, en, fill, border, bg in [
        ('echoes3', '『回音 ACT3』', 'ECHOES ACT3', ('#f0ffe4', '#a4dc78'), '#b8ee90', '#142a18'),
        ('goldexp', '『黄金体验』', 'GOLD EXPERIENCE', ('#fff6d0', '#edc862'), '#ffe29c', '#302012'),
        ('stickyfingers', '『钢链手指』', 'STICKY FINGERS', ('#eaf3ff', '#a0b6ee'), '#b5c9f4', '#18223c'),
    ]:
        result['standcards'][sid] = UI.standcard(sid, cn, en, fill, border, bg)
    for key, cn, en in [('naples', '2001年 意大利·那不勒斯', 'NAPOLI · ITALIA'),
                        ('airport_hall', '机场到达大厅', 'NAPOLI · ARRIVI'),
                        ('airport_out', '机场出口', 'NAPOLI · TAXI'),
                        ('naples_street', '那不勒斯老城街道', 'NAPOLI · CENTRO'),
                        ('naples_cafe', '街角咖啡座', 'NAPOLI · CAFFE'),
                        ('funicular_station', '山坡缆车站', 'FUNICOLARE · STAZIONE'),
                        ('funicular_car', '缆车车厢', 'FUNICOLARE'),
                        ('station_square', '车站前广场', 'PIAZZA'),
                        ('naples_harbor', '黄昏港口', 'NAPOLI · PORTO')]:
        result['locations'][key] = UI.location(key, cn, en)
    result['specials']['koichi'] = UI.save('special/koichi', UI.big('3 FREEZE', 36, ('#f0ffe4', '#a4dc78')))
    result['titles']['b_pro1_taxi'] = UI.save('title/b_pro1_taxi', UI.big('序1 别想开走', 28, ('#fff6d0', '#edc862')))
    result['specials']['giorno'] = UI.save('special/giorno', UI.big('黄金体验 感觉失控', 32, ('#fff6d0', '#edc862')))
    for phase, label in [(1, '车厢'), (2, '拉链')]:
        key = f'b_ch1_{phase}'
        result['vs'][key] = UI.vs_card(key, '布加拉提', 'BUCCIARATI', f'ch1-{phase} {label} / 黄金体验 VS 钢链手指',
                                      ('#edf4ff', '#bac9f0'), '#b8c9f0', ['#29385d', '#16152e'])
    for i, word in enumerate(['3 FREEZE', 'ACT3', 'ACT3!']):
        result['sfx'][word] = UI.save(f'sfx/act3_{i}', UI.big(word, 26, ('#f0ffe4', '#a4dc78')))
    for i, word in enumerate(['MUDA', 'MUDA!']):
        result['sfx'][word] = UI.save(f'sfx/muda_{i}', UI.big(word, 26, ('#fff6d0', '#edc862')))
    pin = Image.new('RGBA', (11, 17))
    d = ImageDraw.Draw(pin)
    d.polygon([(5, 16), (1, 7), (9, 7)], fill='#9e242d', outline='#260d1e')
    d.ellipse((0, 0, 10, 10), fill='#e14650', outline='#260d1e')
    d.rectangle((3, 2, 5, 4), fill='#ffd2a8')
    result['map']['pin'] = UI.save('map/pin', pin, ax=5, ay=16)
    stamp_text = UI.big('2001年3月', 21, ('#de3f48', '#b92735'), edge='#6e1826', shadow=None, edge_w=1)
    stamp = Image.new('RGBA', (stamp_text.width + 12, stamp_text.height + 10))
    stamp.alpha_composite(stamp_text, (6, 5))
    ImageDraw.Draw(stamp).rectangle((1, 1, stamp.width - 2, stamp.height - 2), outline='#cf3542', width=2)
    result['map']['stamp'] = UI.save('map/stamp', stamp)
    result['map']['place'] = UI.save('map/place', UI.small('意大利 那不勒斯', '#ffe29c'))
    save_json(META / 'ui_prologue.json', result)
    print('第五部UI：3张名牌、3张替身卡、9张地点卡、2张VS卡、必杀字和地图红章')
    return result


if __name__ == '__main__':
    build()
