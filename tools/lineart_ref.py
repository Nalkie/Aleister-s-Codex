"""Side decoration from the hand-made line art (white background, blue lines): luminance becomes the alpha of a white PNG,
used as a CSS mask so the colour follows the theme. Run from build/:  python tools/lineart_ref.py <aleister> <ecclesia>"""
import sys
import numpy as np
from PIL import Image

for key, src in zip(('aleister', 'ecclesia'), sys.argv[1:3]):
    g = np.asarray(Image.open(src).convert('L'), dtype=np.float32) / 255.0
    a = np.clip((0.97 - g) / 0.55, 0, 1)            # white paper -> 0, blue ink -> 1
    out = np.zeros(g.shape + (4,), dtype='uint8'); out[..., :3] = 255; out[..., 3] = (a * 255).astype('uint8')
    Image.fromarray(out, 'RGBA').resize((720, 720), Image.LANCZOS).save(f'art/line-{key}.png', optimize=True)
    print(key, 'ok')
