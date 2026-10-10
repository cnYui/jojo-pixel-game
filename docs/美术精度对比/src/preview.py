"""自查用：把手绘稿和原图并排放大，存到 _work\\（命令行参数：jotaro / starplat / portrait）。"""
import sys
sys.dont_write_bytecode = True
import os
from PIL import Image
from common import frame, nearest, WORK, xbr2x
from pixart import sheet


def run(which):
    if which == 'jotaro':
        import art_jotaro_a as A
        from palettes import JOTARO as P
        print('row length problems:', A.check_rows())
        im = A.build().image(P)
        fr, pv = frame('jotaro')
        org = fr.crop(fr.getbbox())
        sheet([org, im, org, im], [8, 4, 4, 2], bg=(185, 190, 200, 255)).save(os.path.join(WORK, 'pv_jotaro.png'))
        nearest(im, 10).save(os.path.join(WORK, 'pv_jotaro_x10.png'))
    elif which == 'starplat':
        import art_starplat_a as A
        from palettes import STARPLAT as P
        print('row length problems:', A.check_rows())
        im = A.build().image(P)
        fr, pv = frame('starplat')
        org = fr.crop(fr.getbbox())
        sheet([org, im, org, im], [8, 4, 4, 2], bg=(185, 190, 200, 255)).save(os.path.join(WORK, 'pv_starplat.png'))
        nearest(im, 8).save(os.path.join(WORK, 'pv_starplat_x8.png'))
    elif which == 'portrait':
        import art_portrait_b as B
        print('row length problems:', B.check_rows())
        im = B.build()
        sheet([im, im], [4, 2], bg=(40, 36, 70, 255)).save(os.path.join(WORK, 'pv_portrait.png'))


if __name__ == '__main__':
    run(sys.argv[1])
