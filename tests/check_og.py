"""Gate test for tools/og.py (sin red: los mazos de prueba no tienen retrato remoto).  Desde la raíz del proyecto:  python tests/check_og.py"""
import os, re, sys, tempfile
sys.path.insert(0, 'tools')
from PIL import Image
import og

fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


def deck(i, **kw):
    d = {'id': i, 'series': 'dm', 'character': 'Seto Kaiba', 'arc': 'Battle City', 'name': 'Blue-Eyes & "Thunder" <Dragon>', 'blurb': "El mazo de Kaiba. Usa 'dados' & más.", 'face': None,
         'kind': 'anime', 'anime': 98, 'main': [['Blue-Eyes White Dragon', 3, 0], ['Pot of Greed', 1, 0]], 'extra': []}
    d.update(kw)
    return d


root = tempfile.mkdtemp()
decks = [deck('kaiba-test'), deck('mono-test', series='av', kind='thematic', character='Yuya Sakaki', arc='Decks'), deck('own-test', series='5d', face='data/face-bruno.webp')]
nofetch = lambda n: None      # sin red: el dorso en lugar de cada carta
check(og.build(decks, root, nofetch) == 3, 'build() hace una página y una imagen por mazo')
check(sorted(os.listdir(root + '/r')) == ['kaiba-test.html', 'mono-test.html', 'own-test.html'] and sorted(os.listdir(root + '/og')) == ['kaiba-test.jpg', 'mono-test.jpg', 'own-test.jpg'], 'r/<id>.html y og/<id>.jpg')
im = Image.open(root + '/og/kaiba-test.jpg')
check(im.size == (1200, 630) and im.mode == 'RGB', 'la tarjeta mide 1200x630')
check(os.path.getsize(root + '/og/kaiba-test.jpg') < 400_000, 'la tarjeta pesa menos de 400 KB (la mayoría de los servicios descartan imágenes más grandes)')
h = open(root + '/r/kaiba-test.html', encoding='utf-8').read()
check('property="og:image" content="https://aleisters-codex.pages.dev/og/kaiba-test.jpg"' in h and 'name="twitter:card" content="summary_large_image"' in h, 'og:image absoluta y twitter:card grande')
check('property="og:url" content="https://aleisters-codex.pages.dev/r/kaiba-test.html"' in h and 'rel="canonical"' in h, 'og:url y canonical apuntan a la página del mazo')
check('http-equiv="refresh" content="0;url=../?mode=roulette&amp;deck=kaiba-test"' in h and 'location.replace("../?mode=roulette&deck=kaiba-test"+location.hash)' in h, 'lleva a la ruleta con el mazo (meta refresh + JS)')
check('<Dragon>' not in h and 'Blue-Eyes &amp; &quot;Thunder&quot; &lt;Dragon&gt;' in h, 'el texto del mazo va escapado (sin romper el HTML)')
check(re.search(r'<title>Seto Kaiba · .* · Ruleta de decks</title>', h) is not None, 'título: personaje · mazo · Ruleta de decks')
check(h.count('og:image"') == 1 and len(re.search(r'og:description" content="([^"]*)"', h).group(1)) <= 400, 'una sola og:image y descripción corta')
# determinista y limpia lo que sobra
a = open(root + '/r/mono-test.html', encoding='utf-8').read()
og.build(decks[:1], root, nofetch)
check(os.listdir(root + '/r') == ['kaiba-test.html'] and os.listdir(root + '/og') == ['kaiba-test.jpg'], 'un mazo que ya no existe deja de tener página e imagen')
root2 = tempfile.mkdtemp()
og.build(decks, root2, nofetch)
check(open(root2 + '/r/mono-test.html', encoding='utf-8').read() == a, 'mismo insumo, misma página')
# la tarjeta muestra el Main completo, una carta por copia (reportado el 2026-11-03: "muestra pocas cartas, deberia mostrar la cantidad exacta")
big = deck('big', main=[['Card %d' % i, 1 + (i % 3 == 0) * 2, 0] for i in range(1, 25)])      # 24 distintas, 8 de ellas x3 = 40 cartas
total = sum(c for _, c, *_ in big['main'])
pk = og.pick_cards(big)
check(len(pk) == total == 40 and pk[:4] == ['Card 1', 'Card 2', 'Card 3', 'Card 3'] and pk.count('Card 9') == 3, 'pick_cards: una carta por copia, en el orden de la lista')
check(og.pick_cards(deck('few', main=[['A', 1, 0], ['B', 3, 0]])) == ['A', 'B', 'B', 'B'], 'pick_cards: respeta las copias y el orden de la lista')
asked = []
og.card_image(big, lambda n: asked.append(n))
check(sorted(asked) == sorted(set(pk)) and len(asked) == len(set(pk)), 'card_image pide cada imagen una sola vez aunque la carta tenga 3 copias')
for n, ne in ((40, 0), (40, 15), (45, 8), (60, 15), (50, 12)):
    cols, cw, chh = og.layout(n, ne)
    rows = len(og.balance(n, cols)) + len(og.balance(ne, cols))
    a = og.AREA
    check(cols * cw + (cols - 1) * og.GAP <= a[2] - a[0] and rows * chh + (rows - 1) * og.GAP + og.LAB + ((og.SEP + og.LAB) if ne else 0) <= a[3] - a[1] and cw >= 48, 'layout(%d, %d): %d columnas, %d filas de %dx%d entran en la franja de cartas y se leen' % (n, ne, cols, rows, cw, chh))
# Main + Extra completos: se cuentan las cartas dibujadas (una celda blanca por cada una)
bigx = deck('bigx', main=[['Card %d' % i, 1 + (i % 3 == 0) * 2, 0] for i in range(1, 25)], extra=[['Ex %d' % i, 1 + (i == 1), 0] for i in range(1, 9)])      # 40 del Main + 9 del Extra
check(og.pick_extra(bigx) == ['Ex 1', 'Ex 1', 'Ex 2', 'Ex 3', 'Ex 4', 'Ex 5', 'Ex 6', 'Ex 7', 'Ex 8'] and og.pick_extra(deck('noex')) == [], 'pick_extra: una carta por copia del Extra, en el orden de la lista')
white = lambda n: Image.new('RGB', (168, 246), (250, 250, 250))
im2 = og.card_image(bigx, white)
cols, cw, chh = og.layout(40, 9)
ax0, ay0, ax1, ay1 = og.AREA
cells = 0
y = ay0
while y < ay1:
    if any(im2.getpixel((x, y)) == (250, 250, 250) for x in range(ax0, ax1)):
        row = 0
        x = ax0
        while x < ax1:
            if im2.getpixel((x, y)) == (250, 250, 250):
                row += 1
                while x < ax1 and im2.getpixel((x, y)) == (250, 250, 250):
                    x += 1
            x += 1
        cells += row
        y += chh
    else:
        y += 1
check(im2.size == (1200, 630) and cells == 49, 'la tarjeta dibuja Main + Extra completos: 40 + 9 = 49 cartas, ni más ni menos: %d' % cells)
im3 = og.card_image(deck('mainonly', extra=[]), white)
check(im3.size == (1200, 630), 'un mazo sin Extra también sale')
# el panel de la ruleta comparte esa página
src = open('src.html', encoding='utf-8').read()
check("new URL('r/'+encodeURIComponent(ROU.deck)+'.html',location.origin+location.pathname).href" in src and "/^https?:$/.test(location.protocol)" in src, 'el botón «Copiar enlace» comparte r/<id>.html cuando hay un mazo y servidor')
ref = open('tools/refresh.py', encoding='utf-8').read()
check("'r', 'og'" in ref and "run('tools/og.py')" in ref and "run('tools/roulette.py', 'build')" in ref, 'refresh.py arma la ruleta y las previas y las lista en files.json')

check(ref.index("run('tools/roulette_faces.py')") < ref.index("run('tests/check_build.py')") and ref.index("run('tools/roulette.py', 'build')") < ref.index("run('tests/check_build.py')"),
      'refresh.py rehace los retratos propios y data/roulette.js ANTES de las pruebas: build_db.py vacía data/ y la prueba de la ruleta los lee (falló la corrida del 2026-11-02)')

# justificado: filas parejas, de borde a borde, y el Extra separado del Main con su rótulo (pedido el 2026-11-03)
check(og.balance(40, 14) == [14, 13, 13] and og.balance(60, 20) == [20, 20, 20] and og.balance(3, 14) == [3] and og.balance(0, 5) == [], 'balance(): las filas quedan parejas (14/13/13), la última no queda a medias')
check(all(max(og.balance(n, c)) - min(og.balance(n, c)) <= 1 and sum(og.balance(n, c)) == n and max(og.balance(n, c)) <= c for n in range(1, 76) for c in range(1, 30)), 'balance(): para todo n y columnas las filas difieren en una carta como mucho, suman n y no pasan de las columnas')
xs = og.row_xs(13, 14, 62, 30, 1170)
check(xs[0] == 30 and xs[-1] + 62 == 1170 and all(b > a for a, b in zip(xs, xs[1:])), 'row_xs(): una fila justificada empieza en el borde izquierdo y termina en el derecho')
xf = og.row_xs(14, 14, 62, 30, 1170)
check(og.row_xs(6, 14, 62, 30, 1170, justify=False)[:6] == xf[:6] and og.row_xs(1, 14, 62, 30, 1170) == [30], 'row_xs(): el Extra a medias usa las columnas de una fila llena, desde la izquierda')
pix = lambda im, x, y: im.getpixel((x, y))
im3 = og.card_image(bigx, white)
ax0, ay0, ax1, ay1 = og.AREA
edge = lambda im: [y for y in range(ay0, ay1) if pix(im, ax0 + 2, y) == (250, 250, 250)]
check(edge(im3) and all(any(pix(im3, x, y) == (250, 250, 250) for y in edge(im3)) for x in (ax0 + 2, ax1 - 3)), 'la tarjeta justifica el Main: hay carta pegada al borde izquierdo y al derecho de la franja')
rows_y = sorted({y for y in range(ay0, ay1) if pix(im3, ax0 + 2, y) == (250, 250, 250) and pix(im3, ax0 + 2, y - 1) != (250, 250, 250)})
cols, cw, chh = og.layout(40, 9)
gaps = [b - a - chh for a, b in zip(rows_y, rows_y[1:])]
check(len(rows_y) == len(og.balance(40, cols)) + len(og.balance(9, cols)) and len(set(gaps[:len(og.balance(40, cols)) - 1])) == 1 and gaps[len(og.balance(40, cols)) - 1] > og.GAP + 8,
      'el Extra queda separado del Main por más que la separación entre filas (rótulo y línea): filas %s, huecos %s' % (rows_y, gaps))

print('failed:', len(fails))
sys.exit(1 if fails else 0)
