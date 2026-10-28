"""Gate test de las fichas tácticas de los mazos.  Sin red.  Run from the project root:  python tests/check_playcards.py

  * tools/playcards.py rechaza una ficha mala: carta que no existe o ilegal en el formato (Ash Blossom en Edison), iniciador que no está en la lista,
    side que no cuadra (entran y salen distinto número, o sale una carta que el mazo no juega), falta un idioma, secciones de más o de menos.
  * Las fichas que se publican (src/playcards.json -> data/play.js) pasan el validador y data/play.js está al día.
  * La página dibuja exactamente las 4 secciones, en el orden pedido, y no dibuja nada para un mazo sin ficha.
"""
import copy, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, 'tools')
import playcards

fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


cards = playcards.load_cards()
names = {c['name'] for c in json.load(open('src/ygo_all.json', encoding='utf-8'))}
rec, pool = playcards.recipes(), playcards.pools()
check(playcards.problems(cards, names, rec, pool) == [], 'the published sheets pass the validator (%d)' % len(cards))

canon = playcards.canon_names()
check(canon.get('Maliss P Chessy Cat') == 'Maliss <P> Chessy Cat', 'Maliss: "Maliss P Chessy Cat" (YGM lists) maps to the database name "Maliss <P> Chessy Cat"')
unknown = sorted({c for f in rec.values() for d in f.values() for s in d.values() for c in s if re.search(r'Maliss [A-Z] ', c)})
check(not unknown, 'no recipe card keeps the YGM spelling of a Maliss name (%s)' % unknown[:3])
check(any(c.startswith('Maliss <P>') for d in rec['adv'].values() for c in d['main']), 'the Maliss recipe uses database names, so a sheet can name its cards')

key = 'edison/blackwing'
base = cards[key]


def bad(mut, frag, label):
    c = copy.deepcopy(base)
    mut(c)
    p = playcards.problems({key: c}, names, rec, pool)
    check(any(frag in x for x in p), 'validator rejects: ' + label + ('' if any(frag in x for x in p) else ' (got %s)' % p[:2]))


bad(lambda c: c['chokepoints'].append({'card': 'Ash Blossom & Joyous Spring', 'step': 'activation', 'stepText': {'es': 'abc', 'en': 'abc'}, 'loss': {'es': 'abc', 'en': 'abc'}}), 'no es legal en edison', 'Ash Blossom in Edison')
bad(lambda c: c['chokepoints'].append({'card': 'Carta Inventada', 'step': 'main', 'stepText': {'es': 'abc', 'en': 'abc'}, 'loss': {'es': 'abc', 'en': 'abc'}}), 'no existe', 'a card that does not exist')
bad(lambda c: c['starters'][0].update(cards=['Sangan']), 'no está en la lista', 'a starter that is not in the list')
bad(lambda c: c['side']['first']['in'].append({'card': 'Fissure', 'qty': 1, 'why': {'es': 'abc', 'en': 'abc'}}), 'entran', 'a side where in and out counts differ')
bad(lambda c: c['side']['second']['out'].__setitem__(0, {'card': 'Mirror Force', 'qty': 3, 'why': {'es': 'abc', 'en': 'abc'}}), 'solo juega', 'taking out more copies than the deck plays')
bad(lambda c: c['side']['first']['in'].__setitem__(0, {'card': 'Mind Control', 'qty': 1, 'why': {'es': 'abc', 'en': 'abc'}}), 'Side de la lista', 'bringing in a card the Side does not have')
bad(lambda c: c['win']['bullets'][0].pop('en'), 'viñetas', 'a bullet without English')
bad(lambda c: c.pop('side'), 'secciones', 'a missing section')
bad(lambda c: c.update(extra={}), 'secciones', 'a fifth section')
bad(lambda c: c['win'].update(plan='aggro'), 'plan', 'an unknown plan')
bad(lambda c: c['chokepoints'][0].update(step='whenever'), 'step', 'an unknown chain step')
p = playcards.problems({'edison/no-such-deck': copy.deepcopy(base)}, names, rec, pool)
check(any('no hay un mazo' in x for x in p), 'validator rejects a sheet for a deck that is not in the ranking')
p = playcards.problems({'blackwing': copy.deepcopy(base)}, names, rec, pool)
check(any('la clave' in x for x in p), 'validator rejects a key without the format')

# data/play.js al día
t = open('data/play.js', encoding='utf-8').read()
check(json.loads(t[t.index(',') + 1:-2]) == cards, 'data/play.js matches src/playcards.json + src/playcards/*.json (run tools/playcards.py)')

check('data/play.js' in {f['path'] for f in json.load(open('files.json', encoding='utf-8'))}, 'files.json publishes data/play.js (otherwise the deploy has no sheets)')

# la página
page = open('index.html', encoding='utf-8').read()
src = open('src.html', encoding='utf-8').read()
order = [src.index(x) for x in ("'Objetivo y ritmo'", "'Iniciadores clave'", "'Puntos de interrupción'", "'Plan de Side Deck'")]
check(order == sorted(order), 'the four sections are in the requested order')
check(src.count('${playCard(') == 4, 'every deck view (TCG, formats, Genesys, Duel Links) draws the sheet')
check('function playCard(fmtKey,d)' in page and "loadData('play')" in page, 'the page loads data/play.js lazily')
check('if(!c) return' in src, 'a deck without a sheet draws nothing')

# render en node con datos de prueba
m = re.search(r"const PLAY_PLAN=.*?\n\}\n", src, re.S)
harness = r'''
const esc = s => String(s), LANG = 'es', deckSlug = n => String(n).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
const dmy = d => d, loadData = () => new Promise(() => {}), mode = 'tcg', render = () => {};
const PLAY = {data: __DATA__, asked: true}, playLoad = () => {};
__CODE__
const html = playCard('edison', {n: 'Blackwing'}), none = playCard('edison', {n: 'Otro mazo'});
const secs = (html.match(/<details class="pc-sec"/g) || []).length;
console.log(JSON.stringify([secs === 4, none === '', /<details class="pc-sec" open>/.test(html) && (html.match(/ open>/g) || []).length === 1, html.includes('Criterio editorial'), html.indexOf('Objetivo y ritmo') < html.indexOf('Plan de Side Deck')]));
'''.replace('__DATA__', json.dumps(cards)).replace('__CODE__', re.search(r'const PLAY_PLAN=.*?\n\}\n', src, re.S).group(0).replace("const PLAY_PLAN", "const PLAY_PLAN", 1)) if m else ''
if m:
    r = subprocess.run(['node', '-'], input=harness, capture_output=True, text=True, encoding='utf-8')   # por stdin: con muchas fichas la línea de comandos de Windows no alcanza
    try:
        res = json.loads(r.stdout.strip())
    except Exception:
        res = []
    labels = ['renders exactly 4 collapsible sections', 'a deck without a sheet renders an empty string', 'only the first section starts open', 'editorial basis is disclosed', 'sections are in the requested order']
    check(len(res) == len(labels), 'node ran the sheet render' + ('' if len(res) == len(labels) else ': ' + (r.stderr.strip().splitlines() or ['?'])[-1][:160]))
    for ok, lab in zip(res, labels):
        check(ok, 'sheet: ' + lab)
else:
    check(False, 'playCard source found in src.html')

print('failed:', len(fails))
sys.exit(1 if fails else 0)
