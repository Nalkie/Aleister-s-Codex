"""art/icon-md.jpg: the Master Duel button icon, in the spirit of the game's own icon (Blue-Eyes White Dragon facing Dark Magician on a red and blue ground).
Built from the card art the project already has (raw/89631139.jpg, art/46986414.jpg): each figure is cut out by colour, the dragon is mirrored so the two face each other.
Deterministic, no network.  Run from the project root:  python tools/mkicon_md.py"""
import os
import numpy as np
from PIL import Image, ImageFilter, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = 160


def hsv(im):
    a = np.asarray(im.convert('RGB'), dtype=np.float32) / 255
    mx, mn = a.max(2), a.min(2)
    d = mx - mn + 1e-6
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return h, d / (mx + 1e-6), mx


def soft(m, grow=3, blur=1.6):
    im = Image.fromarray((m * 255).astype('uint8'))
    im = im.filter(ImageFilter.MaxFilter(grow * 2 + 1)).filter(ImageFilter.MinFilter(grow * 2 - 1 if grow > 1 else 1))
    return im.filter(ImageFilter.GaussianBlur(blur))


def dragon_mask(im):
    h, s, v = hsv(im)
    return soft((v > 0.52) & (s < 0.6))


def magician_mask(im):
    h, s, v = hsv(im)
    warm = ((h < 50) | ((h > 235) & (h < 345))) & (s > 0.18)
    staff = (h > 130) & (h < 175) & (s > 0.35) & (v > 0.35)
    return soft(warm | staff)


def gradient():
    y, x = np.mgrid[0:S, 0:S].astype('float32') / (S - 1)
    t = np.clip((x * 0.7 + y * 0.3 - 0.15) / 0.7, 0, 1)
    red, blue = np.array([186, 36, 58]), np.array([40, 64, 190])
    g = red[None, None, :] * (1 - t[..., None]) + blue[None, None, :] * t[..., None]
    return Image.fromarray(g.astype('uint8'))


def main():
    os.chdir(ROOT)
    bg = gradient()
    dragon = Image.open('raw/89631139.jpg').convert('RGB').resize((200, 200), Image.LANCZOS).transpose(Image.FLIP_LEFT_RIGHT)
    magic = Image.open('art/46986414.jpg').convert('RGB').resize((118, 118), Image.LANCZOS)
    dm, mm = dragon_mask(dragon), magician_mask(magic)
    out = bg.copy()
    out.paste(dragon, (-34, 10), dm)
    out.paste(magic, (S - 118 + 12, S - 118 + 10), mm)
    vignette = Image.new('L', (S, S), 0)
    out = Image.blend(out, ImageChops.multiply(out, Image.new('RGB', (S, S), (235, 235, 245))), 0.5)
    out.save('art/icon-md.jpg', quality=88, optimize=True)
    print('art/icon-md.jpg', out.size, os.path.getsize('art/icon-md.jpg'), 'bytes')


if __name__ == '__main__':
    main()
