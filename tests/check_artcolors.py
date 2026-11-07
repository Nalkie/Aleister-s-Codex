"""Gate: the colours behind the card in the deck rows (tools/artcolors.py).  No network, <2 s.  python tests/check_artcolors.py
Outcome: every deck row with art carries two colours of its picture (--k1, --k2) instead of the plain tier colour; the page ships ARTCOL for at least 80% of the deck arts."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, 'tools')
from PIL import Image
import artcolors as A
fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


red = Image.new('RGB', (40, 40), (220, 30, 30))
c = A.colors_of(red)
check(c and c[0].startswith('#') and int(c[0][1:3], 16) > 200 and int(c[0][3:5], 16) < 90, 'a red picture gives a red first colour (%s)' % (c,))
check(A.colors_of(Image.new('RGB', (40, 40), (120, 120, 120))) is None, 'a grey picture has no colour (the row keeps the tier colour)')
two = Image.new('RGB', (40, 40), (30, 60, 230))
two.paste((240, 190, 20), (0, 20, 40, 40))
c = A.colors_of(two)
check(c and c[0] != c[1], 'a blue and gold picture gives two different colours (%s)' % (c,))
page = open('index.html', encoding='utf-8').read()
m = re.search(r'const ARTCOL = (\{.*?\});', page)
col = json.loads(m.group(1)) if m else {}
names = A.names_in_data()
ids = A._ids()
known = {n for n in names if n in ids}
check(len(col) >= 0.8 * len(known) and all(re.fullmatch(r'#[0-9a-f]{6}', x) for v in col.values() for x in v), 'ARTCOL covers %d of %d deck arts that have a card id' % (len(col), len(known)))
src = open('src.html', encoding='utf-8').read()
check(src.count('${artTint(d.art)}') == 2 and 'const ARTCOL = /*__ARTCOL__*/{}' in src, 'both deck row templates use artTint()')
check('artcolors.cached_names()' in open('tools/build_db.py', encoding='utf-8').read(), 'build_db colours the cached names too (it empties data/ before the roulette is rebuilt, which once left only 68 of 148)')
print('failed:', len(fails))
sys.exit(1 if fails else 0)
