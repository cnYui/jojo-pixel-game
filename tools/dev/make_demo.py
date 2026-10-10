r"""打 demo（体验版）发布包：默认序章 + 第1章。

    python -B tools\dev\make_demo.py                # 输出 游戏素材\JoJo\发布\JoJo星尘斗士_体验版_<日期-时间>\ + 同名 .zip
    python -B tools\dev\make_demo.py --last 1       # 开放到第几章（0 = 只有序章，1 = 到第1章）
    python -B tools\dev\make_demo.py --no-zip

做的事：
  1. 只拷游戏运行要用的文件：index.html、main.js、engine\*.js、story\*.js、data\*.js、data\music\*.js、assets\video\*
     （tools\、docs\、assets\ 其他、规划.md、README.md 这些开发文件都不拷）
  2. 不拷 data\music\title_song.js——那是用户给的《STAND PROUD》，商业歌曲，只能本机自己玩；
     体验版标题曲用原工程自带的 title（main.js 在体验版里自动换）
  3. index.html 在 main.js 前插 window.JOJO_DEMO = { last: N }，网页标题加「体验版」
  4. 写一份给玩家看的 说明.txt
  5. 打 zip（解压出来是一个同名文件夹）
不删、不覆盖任何东西：输出目录已存在就加序号。拷完自检：必需文件都在、title_song 不在、index.html 打好补丁。
"""
import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
import time  # noqa: E402
import zipfile  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))     # tools\dev
GAME = os.path.dirname(os.path.dirname(HERE))         # 游戏
JOJO = os.path.dirname(GAME)                          # 游戏素材\JoJo
OUT_ROOT = os.path.join(JOJO, '发布')

EXCLUDE_MUSIC = {'title_song.js'}                     # STAND PROUD：不随发布包分发
MAIN_TAG = '<script src="main.js"></script>'

README = """JoJo的奇妙冒险 星尘斗士 · 像素同人游戏　体验版（{span}）

【怎么玩】
解压后双击 index.html，用电脑上的 Chrome 或 Edge 打开就能玩。不用安装，不用联网。
手机 / 平板会显示虚拟按键，但还没在真机上测过。

【按键】
方向键 / WASD　移动
J　替身出拳（三连；一直按进连打）
K　闪避
L　按住格挡；敌人出手瞬间按一下 = 精准格挡
U　能量满时放必杀；自由走动时 = 替身调查
Q　换队长
E / Enter / 空格　调查、搭话、推进对白（J 不推进对白）
Esc　暂停（里面有设置：音量、减少闪烁等）

【存档】
进度自动存在浏览器里，标题画面选「继续」接着玩。

【说明】
同人作品，免费，非商业用途。
《JoJo的奇妙冒险》的角色与故事版权归原作者荒木飞吕彦 / 集英社及动画制作方所有。
"""


def span_of(last):
    return '序章' if last == 0 else '序章 + 第1章' if last == 1 else '序章到第%d章' % last


def collect():
    """(相对路径, 源文件) 列表。"""
    files = [('index.html', os.path.join(GAME, 'index.html')), ('main.js', os.path.join(GAME, 'main.js'))]
    for sub in ('engine', 'story', 'data'):
        d = os.path.join(GAME, sub)
        for n in sorted(os.listdir(d)):
            p = os.path.join(d, n)
            if os.path.isfile(p) and n.endswith('.js'):
                files.append((sub + '/' + n, p))
    md = os.path.join(GAME, 'data', 'music')
    for n in sorted(os.listdir(md)):
        if n.endswith('.js') and n not in EXCLUDE_MUSIC:
            files.append(('data/music/' + n, os.path.join(md, n)))
    vd = os.path.join(GAME, 'assets', 'video')
    for n in sorted(os.listdir(vd)):
        if n.endswith(('.mp4', '.webm')):
            files.append(('assets/video/' + n, os.path.join(vd, n)))
    return files


def game_data():
    s = open(os.path.join(GAME, 'data', 'data_meta.js'), encoding='utf-8').read()
    return json.loads(s[s.find('{'):s.rfind('}') + 1])


def patch_index(html, last):
    if MAIN_TAG not in html:
        raise SystemExit('index.html 里找不到 ' + MAIN_TAG)
    if 'JOJO_DEMO' in html:
        raise SystemExit('index.html 已经有 JOJO_DEMO（源文件不该有）')
    html = html.replace(MAIN_TAG, '<script>window.JOJO_DEMO = { last: %d };</script>\n%s' % (last, MAIN_TAG), 1)
    html = html.replace('像素游戏</title>', '像素游戏 体验版</title>', 1)
    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--last', type=int, default=1, help='开放到第几章（0 = 序章）')
    ap.add_argument('--no-zip', action='store_true')
    ap.add_argument('--out-root', default=OUT_ROOT, help=r'输出到哪个文件夹（默认 游戏素材\JoJo\发布）')
    a = ap.parse_args()

    gd = game_data()
    music = (gd.get('audio') or {}).get('music') or {}
    if 'title' not in music:
        raise SystemExit('data_meta 里没有 title 配乐（体验版标题曲要用它）')
    for v in (gd.get('video') or {}).values():
        for k in ('src', 'webm'):
            if v.get(k) and not os.path.exists(os.path.join(GAME, v[k])):
                raise SystemExit('视频缺文件：' + v[k])

    stamp = time.strftime('%Y%m%d-%H%M')
    name = 'JoJo星尘斗士_体验版_' + stamp
    out = os.path.join(a.out_root, name)
    n = 2
    while os.path.exists(out) or os.path.exists(out + '.zip'):
        out = os.path.join(a.out_root, '%s_%d' % (name, n)); n += 1
    name = os.path.basename(out)

    files = collect()
    total = 0
    for rel, src in files:
        dst = os.path.join(out, *rel.split('/'))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if rel == 'index.html':
            open(dst, 'w', encoding='utf-8', newline='\n').write(patch_index(open(src, encoding='utf-8').read(), a.last))
        else:
            shutil.copy2(src, dst)
        total += os.path.getsize(dst)
    with open(os.path.join(out, '说明.txt'), 'w', encoding='utf-8-sig', newline='\r\n') as f:
        f.write(README.format(span=span_of(a.last)))

    # 自检
    bad = []
    if os.path.exists(os.path.join(out, 'data', 'music', 'title_song.js')):
        bad.append('title_song.js 被拷进去了')
    html = open(os.path.join(out, 'index.html'), encoding='utf-8').read()
    if 'window.JOJO_DEMO = { last: %d }' % a.last not in html:
        bad.append('index.html 没打上 JOJO_DEMO')
    for rel in ('main.js', 'data/data_meta.js', 'data/img_core.js', 'data/sfx.js', 'data/music/title.js', 'engine/core.js', 'story/prologue.js', 'story/ch01.js'):
        if not os.path.exists(os.path.join(out, *rel.split('/'))):
            bad.append('缺 ' + rel)
    for p in (gd.get('packs') or {}).values():
        if p.get('file') and not os.path.exists(os.path.join(out, *p['file'].split('/'))):
            bad.append('缺图片包 ' + p['file'])
    if bad:
        raise SystemExit('自检没过：' + '；'.join(bad))

    print('输出：' + out)
    print('文件 %d 个，%.1f MB（不含 STAND PROUD）' % (len(files) + 1, total / 1e6))
    if not a.no_zip:
        zp = out + '.zip'
        with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for root, _, fs in os.walk(out):
                for fn in sorted(fs):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(name, os.path.relpath(p, out)))
        print('zip：%s（%.1f MB）' % (zp, os.path.getsize(zp) / 1e6))


if __name__ == '__main__':
    main()
