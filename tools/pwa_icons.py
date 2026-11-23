"""Íconos de la app instalable (art/icon-*.png), dibujados con el mismo diseño del favicon (círculo cian + hexagrama violeta).
Correr desde la raíz del proyecto:  python tools/pwa_icons.py   (determinista: mismos píxeles cada vez)"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG, CY, VI = (11, 16, 48), (78, 225, 255), (183, 139, 255)
STAR = [(24, 8), (37.9, 32), (10.1, 16), (24, 40), (37.9, 16), (10.1, 32)]


def draw(size, rounded, scale=1.0):
    k = 8                                     # se dibuja 8 veces más grande y se reduce: bordes suaves
    n = size * k
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if rounded:
        d.rounded_rectangle([0, 0, n - 1, n - 1], radius=int(n * 12 / 48), fill=BG)
    else:
        d.rectangle([0, 0, n, n], fill=BG)    # maskable: el sistema recorta, el fondo llega al borde
    u = n / 48 * scale
    off = n * (1 - scale) / 2
    p = lambda x, y: (off + x * u, off + y * u)
    d.ellipse([off + 5 * u, off + 5 * u, off + 43 * u, off + 43 * u], outline=CY, width=max(1, int(1.8 * u)))
    pts = [p(*q) for q in STAR]
    d.line(pts + [pts[0], pts[1]], fill=VI, width=max(1, int(2.6 * u)), joint='curve')
    return im.resize((size, size), Image.LANCZOS)


def build():
    out = {}
    for name, size, rounded, scale in [('icon-192.png', 192, True, 1.0), ('icon-512.png', 512, True, 1.0), ('icon-maskable-512.png', 512, False, 0.72), ('icon-180.png', 180, False, 0.86)]:
        p = os.path.join(ROOT, 'art', name)
        t = p + '.tmp'
        draw(size, rounded, scale).save(t, 'PNG', optimize=True)
        os.replace(t, p)
        out[name] = os.path.getsize(p)
    return out


if __name__ == '__main__':
    print(build())
