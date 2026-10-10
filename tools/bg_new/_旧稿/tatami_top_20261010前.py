"""拔肉芽插入画面的榻榻米底图，复用原织纹和半强度像素暗角。"""
import sys
sys.dont_write_bytecode = True

import os
import numpy as np
from PIL import Image, ImageDraw

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '源码')
if SRC not in sys.path:
    sys.path.insert(0,SRC)
from engine import bg_asia as A


def build():
    im = A._new(320,180)
    A._tatami(ImageDraw.Draw(im),im,0,180,([],[]),seed=43)
    # 旧函数固定在38%处画横缝；用相邻织纹填平，避免俯视图保留透视分块。
    im.paste(im.crop((0,66,320,68)),(0,68))
    # 原函数的纵缝向下扩张；插入画面是俯视，因此保留织纹，边缝改为正交。
    d = ImageDraw.Draw(im)
    d.line((0,90,319,90),fill=(44,60,44,255),width=2)
    for x,y0,y1 in ((80,0,90),(240,0,90),(160,90,179)):
        d.line((x,y0,x,y1),fill=(44,60,44,255),width=2)
    a = np.array(im)
    ys,xs = np.mgrid[0:180,0:320]
    radius = ((xs-159.5)/159.5)**2 + ((ys-89.5)/89.5)**2
    # 四档亮度维持像素图案；边缘最大压暗50%，中央的脸和肉芽仍清晰。
    shade = 1 - np.minimum(1,np.floor(radius*4)/4)*0.5
    a[:,:,:3] = np.round(a[:,:,:3]*shade[:,:,None]).astype(np.uint8)
    return Image.fromarray(a,'RGBA')


def export(ex,BJ):
    im = build()
    st = ex.stage(320,156,(148,176),[dict(type='static',image=ex.img('static',im))],
                  anchors=dict(center=[160,90],fleshbud=[160,70]))
    if ex.check_on:
        ex.checked('榻榻米导出和原织纹加暗角一致',BJ.ndiff_rgba(BJ.ref_render(st,ex.images,0,0),im))
        ex.checked('榻榻米全幅不透明',int((np.array(im)[:,:,3]!=255).sum()))
    return st


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__),'_preview','tatami_top_solo.png')
    os.makedirs(os.path.dirname(out),exist_ok=True)
    build().resize((1280,720),Image.Resampling.NEAREST).save(out)
    print(out)
