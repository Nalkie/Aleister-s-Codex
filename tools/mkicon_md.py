"""art/line-md.png: the Master Duel button icon as a line drawing, used as a colour mask like art/line-dl.png (the page paints it with the Master Duel accent).
Source: a neon line drawing of the game's icon on a transparent ground (kept outside the repo, it is 2 MB).  The lines are the opaque part of its alpha channel; the glow
and the outer frame are cut away.  Deterministic, no network.
Run from the project root:  python tools/mkicon_md.py path/to/source.png"""
import os, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZE = 320
LOW, HIGH = 105, 190        # alpha below LOW is fill or glow, above HIGH is a full line
CROP = (0.135, 0.135, 0.865, 0.865)       # inside the rounded frame: the button draws its own


def convert(src):
    im = Image.open(src).convert('RGBA')
    w, h = im.size
    im = im.crop((int(CROP[0] * w), int(CROP[1] * h), int(CROP[2] * w), int(CROP[3] * h))).resize((SIZE, SIZE), Image.LANCZOS)
    a = np.asarray(im.getchannel('A')).astype('float32')
    m = np.clip((a - LOW) / (HIGH - LOW), 0, 1)
    out = np.zeros((SIZE, SIZE, 4), dtype='uint8')
    out[..., :3] = 255
    out[..., 3] = (m * 255).astype('uint8')
    return Image.fromarray(out, 'RGBA')


def main():
    os.chdir(ROOT)
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    img = convert(sys.argv[1])
    img.save('art/line-md.png', optimize=True)
    print('art/line-md.png', img.size, os.path.getsize('art/line-md.png'), 'bytes')


if __name__ == '__main__':
    main()
