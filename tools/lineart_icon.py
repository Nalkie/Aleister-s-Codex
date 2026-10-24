"""Duel Links app icon (Yugi, App Store artwork) as green-able line art for the mode button: crop of the face (without the 'Update!' and KONAMI banners),
XDoG lines, white PNG whose alpha is the line (CSS mask).  Run from build/:  python tools/lineart_icon.py"""
import io, json, urllib.parse, urllib.request
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

r = json.load(urllib.request.urlopen('https://itunes.apple.com/search?term=' + urllib.parse.quote('Yu-Gi-Oh! Duel Links') + '&entity=software&limit=1', timeout=30))
im = Image.open(io.BytesIO(urllib.request.urlopen(r['results'][0]['artworkUrl512'], timeout=30).read())).convert('RGB')
im = im.crop((60, 0, 452, 322))
g = Image.fromarray(np.asarray(im.convert('L')))
a = np.asarray(g.filter(ImageFilter.GaussianBlur(1.4)), dtype=np.float32) / 255
b = np.asarray(g.filter(ImageFilter.GaussianBlur(2.6)), dtype=np.float32) / 255
d = 21 * a - 20 * b
ink = 1 - np.where(d >= 0.02, 1.0, 1 + np.tanh(10 * (d - 0.02)))
ink = np.clip((ink - 0.35) / 0.4, 0, 1)
lab, n = ndimage.label(ink > 0.3, structure=np.ones((3, 3)))
size = ndimage.sum(np.ones_like(ink), lab, range(1, n + 1))
keep = np.zeros(n + 1, dtype=bool); keep[1:] = size >= 60
ink = ink * keep[lab]
ink = ndimage.grey_dilation(ink, size=(2, 2))             # thicker: it is shown at 46 px
out = np.zeros(ink.shape + (4,), dtype='uint8'); out[..., :3] = 255; out[..., 3] = (np.clip(ink, 0, 1) * 255).astype('uint8')
Image.fromarray(out, 'RGBA').save('art/line-dl.png', optimize=True)
bg = Image.new('RGB', (392, 322), (11, 16, 48)); bg.paste(Image.new('RGB', (392, 322), (61, 220, 151)), (0, 0), Image.fromarray(out[..., 3]))
bg.save('C:/Users/adria/AppData/Local/Temp/claude/D--Proyectos-YugiOh/ff050213-0a93-4a7e-82e4-fbb70f11a4f3/scratchpad/dl_prev.png')
print('ok')
