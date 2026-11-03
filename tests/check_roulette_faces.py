"""Gate test for tools/roulette_faces.py (sin red).  Desde la raíz del proyecto:  python tests/check_roulette_faces.py"""
import os, sys, tempfile
sys.path.insert(0, 'tools')
from PIL import Image, ImageDraw
import roulette_faces as F

fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


# un dibujo de prueba: 300x500 transparente con una cabeza (círculo) arriba a la derecha y un cuerpo debajo
im = Image.new('RGBA', (400, 600), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.ellipse((200, 40, 300, 140), fill=(255, 0, 0, 255))
d.rectangle((170, 140, 330, 560), fill=(0, 0, 255, 255))
out = F.crop_face(im)
check(out.size == (F.SIZE, F.SIZE) and out.mode == 'RGBA', 'el recorte es un cuadrado %dx%d RGBA' % (F.SIZE, F.SIZE))
cx = out.getpixel((F.SIZE // 2, int(F.SIZE * 0.2)))
check(cx[0] > 200 and cx[3] == 255, 'la cabeza queda centrada horizontalmente, arriba (rojo en el centro-arriba): %s' % (cx,))
check(F.crop_face(im) .tobytes() == F.crop_face(im).tobytes(), 'mismo insumo, mismo resultado')
wide = Image.new('RGBA', (900, 300), (0, 0, 0, 0))
ImageDraw.Draw(wide).rectangle((0, 0, 899, 299), fill=(0, 255, 0, 255))
check(F.crop_face(wide).size == (F.SIZE, F.SIZE), 'un dibujo más ancho que alto también sale cuadrado')
try:
    F.crop_face(Image.new('RGBA', (50, 50), (0, 0, 0, 0)))
    check(False, 'una imagen vacía se rechaza')
except ValueError:
    check(True, 'una imagen vacía se rechaza')
check(F.slug('Misty-Tredwell') == 'misty-tredwell' and F.slug('Adrian Gecko') == 'adrian-gecko', 'el nombre del archivo se vuelve el slug del personaje')

# build() de punta a punta en carpetas temporales
src, dst = tempfile.mkdtemp(), tempfile.mkdtemp()
im.save(os.path.join(src, 'Bruno.png'))
open(os.path.join(src, 'LEEME.txt'), 'w').write('x')
check(F.build(src, dst) == ['bruno'] and os.path.exists(os.path.join(dst, 'face-bruno.webp')), 'build() escribe face-<slug>.webp y se salta lo que no es imagen')

print('failed:', len(fails))
sys.exit(1 if fails else 0)
