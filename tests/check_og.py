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
check(og.build(decks, root) == 3, 'build() hace una página y una imagen por mazo')
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
og.build(decks[:1], root)
check(os.listdir(root + '/r') == ['kaiba-test.html'] and os.listdir(root + '/og') == ['kaiba-test.jpg'], 'un mazo que ya no existe deja de tener página e imagen')
root2 = tempfile.mkdtemp()
og.build(decks, root2)
check(open(root2 + '/r/mono-test.html', encoding='utf-8').read() == a, 'mismo insumo, misma página')
# el panel de la ruleta comparte esa página
src = open('src.html', encoding='utf-8').read()
check("new URL('r/'+encodeURIComponent(ROU.deck)+'.html',location.origin+location.pathname).href" in src and "/^https?:$/.test(location.protocol)" in src, 'el botón «Copiar enlace» comparte r/<id>.html cuando hay un mazo y servidor')
ref = open('tools/refresh.py', encoding='utf-8').read()
check("'r', 'og'" in ref and "run('tools/og.py')" in ref and "run('tools/roulette.py', 'build')" in ref, 'refresh.py arma la ruleta y las previas y las lista en files.json')

check(ref.index("run('tools/roulette_faces.py')") < ref.index("run('tests/check_build.py')") and ref.index("run('tools/roulette.py', 'build')") < ref.index("run('tests/check_build.py')"),
      'refresh.py rehace los retratos propios y data/roulette.js ANTES de las pruebas: build_db.py vacía data/ y la prueba de la ruleta los lee (falló la corrida del 2026-11-02)')

print('failed:', len(fails))
sys.exit(1 if fails else 0)
