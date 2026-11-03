"""Retratos de la ruleta que Duel Links Meta no tiene.   Desde la raíz del proyecto:  python tools/roulette_faces.py
Lee src/roulette_faces/<Personaje>.(png|webp|jpg) (arte con fondo transparente, cuerpo entero o medio cuerpo) y escribe data/face-<slug>.webp: un cuadrado de 192x192 con la cabeza
centrada, listo para que el círculo de la ruleta lo muestre entero (sin marco).  Mismo insumo, mismo resultado.  tools/roulette.py usa esos archivos como `face` del personaje.
El recorte se calcula del arte: el cuadro mide HEAD_K veces el alto del dibujo (cabeza y hombros) y se centra en la cabeza (el centro de masa de la franja de arriba).  Si una
cara queda mal, se ajusta en OVERRIDE: slug -> (k, dx), con k el lado como fracción del alto y dx el corrimiento horizontal en fracciones del lado."""
import glob, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZE, HEAD_K, HEAD_ROWS = 192, 0.62, 0.2
OVERRIDE = {}


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def crop_face(im, k=HEAD_K, dx=0.0):
    """Cuadrado SIZE x SIZE (RGBA) de la cabeza de un dibujo con fondo transparente."""
    im = im.convert('RGBA')
    bb = im.getchannel('A').point(lambda a: 255 if a > 24 else 0).getbbox()
    if not bb:
        raise ValueError('imagen vacía')
    im = im.crop(bb)
    w, h = im.size
    side = max(8, min(round(h * k), w if w >= h * 0.3 else h))
    a = im.getchannel('A').point(lambda v: 255 if v > 24 else 0)
    band = a.crop((0, 0, w, max(1, round(h * HEAD_ROWS))))
    xs = [x for x in range(w) for y in range(band.size[1]) if band.getpixel((x, y))]
    cx = sum(xs) / len(xs) if xs else w / 2
    left = round(cx - side / 2 + dx * side)
    left = max(min(left, w - side), 0) if w >= side else (w - side) // 2
    box = (left, 0, left + side, side)
    out = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    out.alpha_composite(im, (-box[0], -box[1])) if box[0] >= 0 else out.alpha_composite(im, (-box[0], 0))
    return out.resize((SIZE, SIZE), Image.LANCZOS)


def build(src=None, dst=None):
    src = src or os.path.join(ROOT, 'src/roulette_faces')
    dst = dst or os.path.join(ROOT, 'data')
    made = []
    for f in sorted(glob.glob(os.path.join(src, '*'))):
        base, ext = os.path.splitext(os.path.basename(f))
        if ext.lower() not in ('.png', '.webp', '.jpg', '.jpeg'):
            continue
        s = slug(base)
        k, dx = OVERRIDE.get(s, (HEAD_K, 0.0))
        crop_face(Image.open(f), k, dx).save(os.path.join(dst, 'face-%s.webp' % s), 'WEBP', quality=88, method=6)
        made.append(s)
    return made


if __name__ == '__main__':
    made = build()
    print('data/face-*.webp: %d retratos' % len(made), made)
