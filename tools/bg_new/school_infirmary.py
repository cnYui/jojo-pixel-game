"""保健室：按规划的床、药柜、医生桌坐标新画；花瓣与台灯四秒闭合。"""
import sys
sys.dont_write_bytecode = True

import math
import os
from functools import lru_cache

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '源码')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import numpy as np
from PIL import Image, ImageDraw
from engine import bg_asia as A, bg_egypt as E
from engine.core import hash01

W, H = 320, 180
N, FPS = 32, 8
WINDOW = (153, 43, 208, 88)
LAMP = (213, 94, 255, 151)
C = A._c4


def bed(d, x0, x1):
    d.rectangle((x0 + 5, 142, x0 + 7, 151), fill=C((102, 112, 126)))
    d.rectangle((x1 - 7, 142, x1 - 5, 151), fill=C((102, 112, 126)))
    d.rectangle((x0, 133, x1, 143), fill=C((186, 194, 198)), outline=C((100, 112, 126)))
    d.polygon([(x0+2,130),(x1-4,130),(x1-1,140),(x0+2,140)],
              fill=C((246, 246, 240)), outline=C((158, 168, 184)))
    d.line((x0+5,132,x1-7,132), fill=C((255, 255, 250)))
    for x in range(x0+18, x1-7, 12):
        d.line((x,134,x+1,138), fill=C((218, 226, 232)))
    d.rounded_rectangle((x0+3,129,x0+17,135), radius=2,
                        fill=C((140, 178, 218)), outline=C((86, 120, 166)))
    d.line((x0+5,130,x0+15,130), fill=C((180, 208, 236)))
    d.line((x0,126,x0,147), fill=C((128, 142, 154)), width=2)
    d.line((x1,129,x1,147), fill=C((128, 142, 154)), width=2)


@lru_cache(maxsize=1)
def static():
    im = A._new(W, H, (238, 238, 228))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 120, W, 140), fill=C((182, 208, 186)))
    d.line((0,120,W,120), fill=C((116, 152, 138)))
    d.rectangle((0,141,W,H), fill=C((200, 204, 202)))
    for y in (146,155,166,179):
        d.line((0,y,W,y), fill=C((172, 180, 182)))
    for row,(ya,yb) in enumerate(((141,146),(146,155),(155,166),(166,180))):
        for x in range(-20 + row*9, W, 40):
            d.line((x,ya,x+2,yb), fill=C((180, 186, 188)))
    A._tex_noise(im, (0,0,W,140), 0.04, 79)
    d = ImageDraw.Draw(im)
    # 原 far 没有樱花；用相同学校底层叠其 near 的樱花，保证窗外季节与校门一致。
    far, near = A._school_layers()
    outside = far.copy()
    outside.alpha_composite(near.crop((0,0,400,180)))
    view = outside.crop((112,28,182,92)).resize((55,45), Image.Resampling.NEAREST)
    im.alpha_composite(view, (153,43))
    d = ImageDraw.Draw(im)
    d.rectangle((150,40,210,90), outline=C((92, 112, 126)), width=3)
    d.line((180,42,180,88), fill=C((226, 230, 222)), width=2)
    d.line((152,68,208,68), fill=C((226, 230, 222)), width=2)
    d.rectangle((148,90,212,93), fill=C((182, 190, 184)), outline=C((130, 144, 144)))
    d.rectangle((20,20,64,150), fill=C((240, 242, 232)), outline=C((172, 184, 188)))
    d.line((18,19,68,19), fill=C((104, 120, 134)), width=2)
    for x in range(23,65,7):
        d.line((x,22,x,147), fill=C((208, 216, 212)))
        d.line((x+2,23,x+2,145), fill=C((252, 252, 240)))
        d.rectangle((x,18,x+2,21), fill=C((114, 130, 146)))
    bed(d,70,130)
    bed(d,150,210)
    d.rectangle((250,50,300,130), fill=C((184, 198, 194)), outline=C((90, 112, 122)), width=2)
    for xa, xb in ((253,273),(277,297)):
        d.rectangle((xa,54,xb,119), fill=C((150, 180, 188)), outline=C((112, 140, 146)))
        for y in (72,94,116):
            d.line((xa,y,xb,y), fill=C((210, 222, 214)))
            for i,x in enumerate(range(xa+3,xb-2,6)):
                col = ((158, 110, 70),(212, 224, 206),(86, 142, 126))[i%3]
                d.rectangle((x,y-12,x+3,y-1), fill=C(col), outline=C((90, 108, 114)))
                d.rectangle((x,y-14,x+3,y-12), fill=C((216, 218, 206)))
                d.line((x+1,y-8,x+2,y-8), fill=C((240, 240, 226)))
        d.line((xa+2,57,xa+2,116), fill=C((188, 212, 214)))
    d.rectangle((271,83,273,91), fill=C((92, 106, 118)))
    d.rectangle((277,83,279,91), fill=C((92, 106, 118)))
    d.rectangle((254,123,296,127), fill=C((154, 174, 168)), outline=C((92, 112, 116)))
    d.rectangle((220,124,250,130), fill=C((182, 140, 100)), outline=C((102, 86, 80)))
    d.rectangle((223,131,227,150), fill=C((144, 114, 86)), outline=C((92, 86, 86)))
    d.rectangle((243,131,247,150), fill=C((144, 114, 86)), outline=C((92, 86, 86)))
    d.rectangle((226,132,242,143), fill=C((176, 140, 104)), outline=C((108, 94, 82)))
    d.line((232,137,236,137), fill=C((70, 76, 82)))
    d.rectangle((224,121,235,123), fill=C((240, 234, 210)), outline=C((156, 158, 158)))
    # 门保留在可行走区右端，锚点在门前地面。
    d.rectangle((304,47,319,146), fill=C((200, 208, 194)), outline=C((122, 140, 140)), width=2)
    d.rectangle((309,61,317,86), fill=C((160, 190, 198)), outline=C((130, 152, 156)))
    d.rectangle((307,111,309,114), fill=C((110, 124, 136)))
    return im


def render(t):
    # 与浏览器 strip 采样时钟一致，闭合不会因浮点三角函数跨像素而偏一格。
    fi = int(math.floor(t * FPS + 1e-8)) % N
    im = static().copy()
    petal = Image.new('RGBA', (WINDOW[2]-WINDOW[0], WINDOW[3]-WINDOW[1]))
    pd = ImageDraw.Draw(petal)
    for i in range(6):
        phase = (fi + i*5) % N
        x = 3 + (i*9 + round(3*math.sin(math.tau*phase/N))) % 49
        y = 1 + (phase*43//N)
        pd.point((x,y), fill=C((250, 190, 214)))
        pd.point((x+1,y), fill=C((255, 228, 234)))
    im.alpha_composite(petal, (WINDOW[0],WINDOW[1]))
    d = ImageDraw.Draw(im)
    d.line((180,42,180,88), fill=C((226,230,222)), width=2)
    d.line((152,68,208,68), fill=C((226,230,222)), width=2)
    E._glow_at(im, 240,116,14,(255,236,156),0.10+0.025*math.sin(math.tau*fi/N),ry=18,levels=3)
    d = ImageDraw.Draw(im)
    d.line((241,124,241,112,237,107), fill=C((96, 126, 120)), width=2)
    d.polygon([(233,106),(240,106),(244,111),(229,111)], fill=C((94, 142, 132)), outline=C((58,94,92)))
    d.line((232,112,241,112), fill=C((255,240,178)))
    d.ellipse((237,123,245,125), fill=C((106,132,124)), outline=C((68,94,96)))
    return im


def export(ex, BJ):
    layers = [dict(type='static', image=ex.img('static', render(0)))]
    layers.append(ex.bake('petals', WINDOW, N, FPS, render))
    layers.append(ex.bake('lamp', LAMP, N, FPS, render))
    st = ex.stage(320,156,(148,176),layers,
                  anchors=dict(bed1=[100,152],bed2=[180,152],desk=[236,156],door=[300,156],walk_x=[40,290]))
    if ex.check_on:
        for t in (0,0.125,1.75,3.875,4,12.25):
            ex.checked('保健室 t=%.3f 导出与直接绘制一致' % t,
                       BJ.ndiff_rgba(BJ.ref_render(st,ex.images,0,t),render(t)))
        a = np.array(render(0))
        ex.checked('整幅保健室不透明且没有露黑',int((a[:,:,3]!=255).sum()+(a[:,:,:3].sum(-1)==0).sum()))
        ex.checked('花瓣与台灯四秒严格闭合',BJ.ndiff_rgba(render(0),render(4)))
    return st


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__),'_preview','school_infirmary_solo.png')
    os.makedirs(os.path.dirname(out),exist_ok=True)
    render(0).resize((W*4,H*4),Image.Resampling.NEAREST).save(out)
    print(out)
