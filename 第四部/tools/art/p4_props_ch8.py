# 第8章的道具（第四部/docs/分章开发约定.md 第 2 节：props_ch8）。写法照 p4_props.py：字符图，一个字母一种颜色，外面描 1 px 深色边。
#   polaroid 拍立得（吉广的相机，第 12 战承太郎拿来拍他）、ghost_photo 吉广的照片（0 平的 / 1 对折贴胶带）、
#   arrow2 第二支弓与箭（躺在长木箱里那一套）、teacup 吉广从相框里扔出来的茶杯、jk 猜拳的三种手（0 石头 1 剪刀 2 布）、
#   jk_big 同样三种手的大号（第 13 战画面中间对拳用）、mug 早人房间的录像带（结尾特写用）。
#   用法：python3 第四部/tools/art/p4_props_ch8.py     输出 assets/props/<id>.png + _meta/props_ch8.json
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4lib as LIB  # noqa: E402
import p4_props as P  # noqa: E402

PROPS = {}


def save(pid, frames, **kw):
    P.PROPS.clear()
    P.save(pid, frames, **kw)
    PROPS.update(P.PROPS)


CAM = dict(W='#f4f0e6', w='#c8c2b4', K='#2a2830', k='#4a4852', L='#7ab8e8', l='#3a6a9a', R='#e04848', Y='#f0c040')


def polaroid():
    rows = ["..KKK.......",
            "WWWWWWWWWWWW",
            "WwKKKKWWRWWW",
            "WKkLLkKWWWYW",
            "WKLllLKWWWWW",
            "WKkLLkKWWWWW",
            "WwKKKKWwwwwW",
            "wwwwwwwwwwww",
            ".KKKKKKKKKK."]
    save('polaroid', [P.grid(rows, CAM)])


PH = dict(W='#f8f4e8', w='#d8d0bc', S='#b89a72', s='#8a6e4c', H='#e8e4dc', F='#e6ae7e', B='#5a4a3a', T='#dce8f0', t='#a8bccc')


def ghost_photo():
    # 拍立得相片：白边 + 褐色的照片面，里面一个老人的上半身（白发、开衫）
    flat = ["WWWWWWWWWW",
            "WSSSSSSSSW",
            "WSSHHHSSSW",
            "WSHFFFHSSW",
            "WSSFFFSSSW",
            "WSBBBBBSSW",
            "WsBBBBBBsW",
            "WssBBBBssW",
            "WWWWWWWWWW",
            "WWWWWWWWWW",
            "wwwwwwwwww"]
    folded = ["....TTT...",
              "WWWWTTTWWW",
              "WSSSTTTSSW",
              "WsSSSSSSsW",
              "wwwwTTTwww",
              "....TTT..."]
    save('ghost_photo', [P.grid(flat, PH), P.grid(folded, PH)], pivot=None, align='center')


AR = dict(G='#e8c050', g='#a07a28', Y='#fff0a0', B='#6a4a2a', b='#3e2a16', S='#d8d8e0', s='#8a8a98', R='#c03838')


def arrow2():
    # 第二支弓与箭：弓躺着，箭横在上面（箭头是金色的甲虫形）
    rows = ["........................",
            "..bbbb..............bbbb",
            "...bBBbbbbbbbbbbbbbbBb..",
            "...................GG...",
            "SSSSSSSSSSSSSSSSSSGYGg..",
            "R..................GG...",
            "...bBBbbbbbbbbbbbbbbBb..",
            "..bbbb..............bbbb"]
    save('arrow2', [P.grid(rows, AR)])


TC = dict(W='#f4f0e6', w='#c8c2b4', B='#6a9ac8', b='#3a6a9a', T='#8a5a30')


def teacup():
    rows = [".WWWWW.",
            "WBBBBBWw",
            "WwwwwwW.w",
            ".WwwwW.w",
            "..www..."]
    save('teacup', [P.grid(rows, TC)], align='center')


JK = dict(F='#f6c49a', f='#d8946c', d='#a8684a', N='#fff0e0')


def jk_hands():
    rock = ["..ffff..",
            ".fFFFFf.",
            "fFfFfFFf",
            "fFFFFFFf",
            "fFFFFFFf",
            ".fFFFFf.",
            "..ffff.."]
    scissors = ["f....f..",
                "Ff..fF..",
                ".Ff.F...",
                ".fFFf...",
                "fFFFFFf.",
                "fFFFFFf.",
                ".fffff.."]
    paper = [".f.f.f..",
             ".F.F.F.f",
             ".F.F.FfF",
             "fFFFFFFf",
             "fFFFFFFf",
             ".fFFFFf.",
             "..ffff.."]
    frs = [P.grid(r, JK) for r in (rock, scissors, paper)]
    save('jk', frs, align='center')
    save('jk_big', [f.resize((f.width * 4, f.height * 4), Image.NEAREST) for f in frs], align='center')


TP = dict(K='#2a2830', k='#4a4852', W='#f4f0e6', R='#e04848')


def tape():
    rows = ["KKKKKKKKKK",
            "KWWWWWWWWK",
            "KkKkkkkKkK",
            "KkkkkkkkkK",
            "KKKKKKKKKK"]
    save('vtape', [P.grid(rows, TP)])


def main():
    for f in (polaroid, ghost_photo, arrow2, teacup, jk_hands, tape):
        f()
    path = os.path.join(LIB.META, 'props_ch8.json')
    LIB.save_json(path, {'props': PROPS})
    print('道具', len(PROPS), '个：', ' '.join(PROPS))


if __name__ == '__main__':
    main()
