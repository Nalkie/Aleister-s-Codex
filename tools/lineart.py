"""Minimal line art from the card artwork (used as side decoration of the page).
Extended difference of Gaussians (XDoG) on the luminance, thresholded to thin lines, written as a white PNG whose alpha is the line:
the page uses it as a CSS mask, so the colour follows the theme. Run from build/:  python tools/lineart.py"""
import io, os, urllib.request
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

UA = {'User-Agent': 'Mozilla/5.0'}
JOBS = [('aleister', 86120751, 'Aleister the Invoker (original art)'), ('ecclesia', 60303688, 'Dogmatika Ecclesia, the Virtuous')]


def xdog(im, s=1.7, k=1.8, p=20.0, eps=0.03, phi=12.0):
    g = np.asarray(im.convert('L'), dtype=np.float32) / 255.0
    a = np.asarray(Image.fromarray((g * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(s)), dtype=np.float32) / 255.0
    b = np.asarray(Image.fromarray((g * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(s * k)), dtype=np.float32) / 255.0
    d = (1 + p) * a - p * b
    return np.where(d >= eps, 1.0, 1.0 + np.tanh(phi * (d - eps)))   # 1 = paper, <1 = ink


os.makedirs('art', exist_ok=True)
for key, pw, label in JOBS:
    url = f'https://images.ygoprodeck.com/images/cards_cropped/{pw}.jpg'
    im = Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read())).convert('RGB')
    ink = 1.0 - xdog(im)                       # 0 paper .. 1 ink
    ink = np.clip((ink - 0.45) / 0.45, 0, 1)   # drop faint texture: minimal, not a painting
    lab, n = ndimage.label(ink > 0.3, structure=np.ones((3, 3)))
    size = ndimage.sum(np.ones_like(ink), lab, range(1, n + 1))
    keep = np.zeros(n + 1, dtype=bool); keep[1:] = size >= 140     # specks are texture, not drawing
    ink = ink * keep[lab]
    # soft fade towards the edges so the drawing dissolves into the page
    h, w = ink.shape
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    fade = np.clip((1.0 - d) / 0.4, 0, 1)
    alpha = (ink * fade * 255).astype('uint8')
    out = np.zeros((h, w, 4), dtype='uint8')
    out[..., :3] = 255
    out[..., 3] = alpha
    Image.fromarray(out, 'RGBA').resize((560, 560), Image.LANCZOS).save(f'art/line-{key}.png', optimize=True)
    print(key, label, os.path.getsize(f'art/line-{key}.png'))
