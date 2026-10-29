"""art/line-dayl.png and art/line-dayr.png: the day-mode side figures as line masks, so the page paints them with the colour of the section (like the night figures).
Source: the two black-on-white drawings (src/day/day-left.jpg, src/day/day-right.jpg).  White becomes transparent, black opaque.  Deterministic, no network.
Run from the project root:  python tools/mkday.py"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIDTH = 760
LOW, HIGH = 25, 215      # luminance at or below LOW is solid line, at or above HIGH is paper


def convert(src):
    im = Image.open(src).convert('L')
    im = im.resize((WIDTH, round(WIDTH * im.size[1] / im.size[0])), Image.LANCZOS)
    a = np.clip((HIGH - np.asarray(im).astype('float32')) / (HIGH - LOW), 0, 1)
    out = np.full(a.shape + (2,), 255, dtype='uint8')      # white + alpha: the page only reads the alpha
    out[..., 1] = (a * 255).astype('uint8')
    return Image.fromarray(out, 'LA')


def main():
    os.chdir(ROOT)
    for src, dst in (('src/day/day-left.jpg', 'art/line-dayl.png'), ('src/day/day-right.jpg', 'art/line-dayr.png')):
        img = convert(src)
        img.save(dst, optimize=True)
        print(dst, img.size, os.path.getsize(dst), 'bytes')


if __name__ == '__main__':
    main()
