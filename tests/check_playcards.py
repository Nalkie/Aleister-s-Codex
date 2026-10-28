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
LENIENT = '--lenient' in sys.argv      # the unattended refresh (tools/refresh.py --unattended) leaves stale sheets out: judge the ones that were published
if LENIENT:
    _t = open('data/play.js', encoding='utf-8').read()
    _pub = json.loads(_t[_t.index(',') + 1:-2])
    cards = {k: v for k, v in cards.items() if k in _pub}
    check(len(cards) == len(_pub) and len(cards) >= 40, 'unattended run: %d of the sheets are published, the rest were skipped' % len(cards))
names = {c['name'] for c in json.load(open('src/ygo_all.json', encoding='utf-8'))}
rec, pool = playcards.recipes(), playcards.pools()
check(playcards.problems(cards, names, rec, pool) == [], 'the published sheets pass the validator (%d)' % len(cards))

canon = playcards.canon_names()
check(canon.get('Maliss P Chessy Cat') == 'Maliss <P> Chessy Cat', 'Maliss: "Maliss P Chessy Cat" (YGM lists) maps to the database name "Maliss <P> Chessy Cat"')
unknown = sorted({c for f in rec.values() for d in f.values() for s in d.values() for c in s if re.search(r'Maliss [A-Z] ', c)})
check(not unknown, 'no recipe card keeps the YGM spelling of a Maliss name (%s)' % unknown[:3])
check(any(c.startswith('Maliss <P>') for d in rec['adv'].values() for c in d['main']), 'the Maliss recipe uses database names, so a sheet can name its cards')
# fuentes: cada ficha tiene las suyas, y cada URL figura como abierta y leída en src/playcards_links.json (lo escribe tools/playcards_links.py; el test no usa la red)
import playcards_links as PL
check(PL.extract_title('<meta property="og:title" content="King\'s Sarcophagus - Yugipedia">') == "King's Sarcophagus - Yugipedia", 'link checker keeps an apostrophe in the og:title')
check(PL.extract_title('<html><title> Snake-Eye\n Ash </title>') == 'Snake-Eye Ash', 'link checker falls back to <title> and trims it')
check(not PL.verified({'status': 404, 'title': 'Snake-Eye Ash'}) and not PL.verified({'status': 200, 'title': 'Just a moment...'}) and not PL.verified({'status': 200, 'title': '404 Not Found'}) and PL.verified({'status': 200, 'title': 'Snake-Eye Ash - Yugipedia'}), 'link checker rejects errors, challenges and 404 titles')
check(PL.topic_ok('Snake-Eye Ash', 'https://yugipedia.com/wiki/Snake-Eye_Ash', 'Snake-Eye Ash - Yugipedia') and not PL.topic_ok('Snake-Eye Ash', 'https://ygoprodeck.com/card/x-1', 'Frozen Rose | YGOPRODeck'), 'link checker flags a source whose name is not the page it opened')
rep = json.load(open('src/playcards_links.json', encoding='utf-8'))
few = [k for k, c in cards.items() if len(c.get('sources', [])) < 2]
check(not few, 'every sheet has at least 2 sources' + ('' if not few else ': ' + ', '.join(few[:3])))
unver = sorted({s['url'] for c in cards.values() for s in c.get('sources', []) if not PL.verified(rep.get(s['url']))})
check(not unver, 'every source URL was opened and read (run tools/playcards_links.py)' + ('' if not unver else ': ' + unver[0]))
off = sorted({s['url'] for c in cards.values() for s in c.get('sources', []) if PL.verified(rep.get(s['url'])) and not PL.topic_ok(s['name'], s['url'], rep[s['url']]['title'])})
check(not off, 'every source name matches the title of the page it points to' + ('' if not off else ': ' + off[0]))

# honestidad del cuerpo: no se nombra un sitio que la ficha no enlaza, ni se atribuye a «jugadores» lo que ninguna fuente dice, ni un límite expone una nota interna
SITES = {'yugipedia': 'yugipedia', 'ygorganization': 'ygorganization', 'ygoprodeck': 'ygoprodeck', 'master duel meta': 'masterduelmeta', 'duel links meta': 'duellinksmeta', 'cardsrealm': 'cardsrealm',
         'archetypes nexus': 'archetypesnexus', 'flipside': 'flipside', 'road of the king': 'roadoftheking', 'kotacards': 'kotacards', 'goatformat': 'goatformat', 'format library': 'formatlibrary', 'edisonformat': 'edisonformat'}
ATTR = re.compile(r'seg[uú]n (los )?jugadores|un jugador (report|cont|dijo)|according to players|a player (reported|said)|players report', re.I)
INTERNAL = re.compile(r'figura con respaldo|no pudimos|marked as tournament-backed|could not reopen|\b(abrimos|encontramos|enlazamos|usamos|comprobamos|revisamos|consultamos|confirmamos|que usamos)\b|\bwe (found|opened|linked|used|could|checked|did not|link)\b|\bwe\b.{0,20}\b(use|opened|found)\b', re.I)


def _texts(o, out):
    if isinstance(o, dict):
        if set(o) == {'es', 'en'}:
            out.extend([o['es'], o['en']])
        else:
            for k, v in o.items():
                if k not in ('sources', 'limits'):
                    _texts(v, out)
    elif isinstance(o, list):
        for v in o:
            _texts(v, out)


ghost, attr, internal = [], [], []
for k, c in cards.items():
    body = []
    _texts(c, body)
    text = ' '.join(body).lower()
    linked = ' '.join((s['name'] + ' ' + s['url']).lower().replace(' ', '').replace('-', '') for s in c.get('sources', [])) + ' ' + ' '.join(s['name'].lower() for s in c.get('sources', []))
    for nm, host in SITES.items():
        if nm in text and host not in linked.replace(' ', '') and nm not in linked:
            ghost.append(k + ': ' + nm)
    if ATTR.search(' '.join(body)):
        attr.append(k)
    if any(INTERNAL.search(l[lang]) for l in c.get('limits', []) for lang in ('es', 'en')):
        internal.append(k)
check(not ghost, 'no sheet names a site it does not link as a source' + ('' if not ghost else ': ' + '; '.join(ghost[:4])))
check(not attr, 'no sheet attributes a claim to unnamed "players"' + ('' if not attr else ': ' + ', '.join(attr[:4])))
check(not internal, 'no limit exposes an internal process note' + ('' if not internal else ': ' + ', '.join(internal[:4])))

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
bad(lambda c: c.pop('side'), 'los campos', 'a missing section')
bad(lambda c: c.update(extra={}), 'los campos', 'a fifth section')
bad(lambda c: c['win'].update(plan='aggro'), 'plan', 'an unknown plan')
bad(lambda c: c['chokepoints'][0].update(step='whenever'), 'step', 'an unknown chain step')
p = playcards.problems({'edison/no-such-deck': copy.deepcopy(base)}, names, rec, pool)
check(any('no hay un mazo' in x for x in p), 'validator rejects a sheet for a deck that is not in the ranking')
p = playcards.problems({'blackwing': copy.deepcopy(base)}, names, rec, pool)
check(any('la clave' in x for x in p), 'validator rejects a key without the format')

# nombres que las listas escriben distinto que la base, y huecos del pool de los formatos retro
check(playcards.card_name('Maliss P Chessy Cat') == 'Maliss <P> Chessy Cat' and playcards.card_name('Maliss in Underground') == 'Maliss in Underground' and playcards.card_name('Empire of Endymion') == 'Endymion Empire', 'card_name maps list spellings to database names (Maliss P -> Maliss <P>)')
check('Maliss <P> Chessy Cat' in rec['adv']['maliss']['main'] and 'Maliss <Q> Hearts Crypter' in rec['adv']['maliss']['extra'], 'Maliss recipes use the database names')
check('Blade Knight' in pool['goat'] and 'XX-Saber Gottoms' in pool['edison'], 'a card played by real decks of a retro format is legal there (Blade Knight in Goat)')
_m = copy.deepcopy(cards['adv/maliss'])
_m['starters'][0]['cards'] = ['Maliss <P> Chessy Cat']
_p = playcards.problems({'adv/maliss': _m}, names, rec, pool)
check(not any('Chessy' in x for x in _p), 'a sheet can name Maliss <P> Chessy Cat as a starter (found in the deck list)' + ('' if not any('Chessy' in x for x in _p) else ': ' + str(_p[:2])))

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
console.log(JSON.stringify([secs === 4, none === '', /<details class="pc-sec" open>/.test(html) && (html.match(/ open>/g) || []).length === 1, html.includes('Criterio editorial'), html.indexOf('Objetivo y ritmo') < html.indexOf('Plan de Side Deck'), (html.match(/<details class="pc-src"/g) || []).length === 1 && html.indexOf('Plan de Side Deck') < html.indexOf('pc-src'), html.includes('Fuentes y límites') && html.includes('<h5>Fuentes</h5>'), (html.match(/<a href="https:/g) || []).length >= 2 && (html.match(/<a href="https:/g) || []).length === (html.match(/rel="noopener noreferrer"/g) || []).length]));
'''.replace('__DATA__', json.dumps(cards)).replace('__CODE__', re.search(r'const PLAY_PLAN=.*?\n\}\n', src, re.S).group(0).replace("const PLAY_PLAN", "const PLAY_PLAN", 1)) if m else ''
if m:
    r = subprocess.run(['node', '-'], input=harness, capture_output=True, text=True, encoding='utf-8')   # por stdin: con muchas fichas la línea de comandos de Windows no alcanza
    try:
        res = json.loads(r.stdout.strip())
    except Exception:
        res = []
    labels = ['renders exactly 4 collapsible sections', 'a deck without a sheet renders an empty string', 'only the first section starts open', 'editorial basis is disclosed', 'sections are in the requested order', 'one Fuentes y límites block, after the four sections', 'the block lists the sources', 'every source link opens safely (https, noopener noreferrer)']
    check(len(res) == len(labels), 'node ran the sheet render' + ('' if len(res) == len(labels) else ': ' + (r.stderr.strip().splitlines() or ['?'])[-1][:160]))
    for ok, lab in zip(res, labels):
        check(ok, 'sheet: ' + lab)
else:
    check(False, 'playCard source found in src.html')

# Regla editorial: en español "banish" es desterrar (nunca banish, banear ni banquear). El campo en sí usa banish.
import glob
_BAD = re.compile(r'[Bb]anish|[Bb]ane[aáeo]|[Bb]anqu')
_hits = []
def _walk(o, f):
    if isinstance(o, dict):
        if set(o) == {'es', 'en'}:
            if _BAD.search(o['es']):
                _hits.append(f + ': ' + o['es'][:60])
        else:
            for v in o.values():
                _walk(v, f)
    elif isinstance(o, list):
        for v in o:
            _walk(v, f)
for _f in glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'playcards*.json')) + glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'playcards', '*.json')):
    _walk(json.load(open(_f, encoding='utf-8')), os.path.basename(_f))
check(not _hits, 'es texts say desterrar, never banish/banear' + ('' if not _hits else ': ' + _hits[0]))

# unattended refresh: stale sheets are skipped, a few at a time
_few = {'adv/a': 1, 'adv/b': 2, 'adv/c': 3, 'adv/d': 4, 'adv/e': 5, 'adv/f': 6, 'adv/g': 7, 'adv/h': 8, 'adv/i': 9, 'adv/j': 10}
_kept, _stale = playcards.skip_stale(_few, ['adv/b: side.first.in: x', 'adv/b: side.first.out: y', 'ocg/z: nope'.replace('ocg/z', 'adv/d')])
check(_stale == ['adv/b', 'adv/d'] and sorted(_kept) == sorted(set(_few) - {'adv/b', 'adv/d'}), 'unattended refresh keeps the sheets that validate and names the stale ones')
try:
    playcards.skip_stale(_few, ['adv/%s: bad' % x for x in 'abcdef'])
    _over = False
except SystemExit:
    _over = True
check(_over, 'unattended refresh still stops when most sheets are stale (something else is wrong)')
_rf = open('tools/refresh.py', encoding='utf-8').read()
check("os.path.exists('.unattended')" in _rf and "'tools/playcards.py', *(('--lenient',)" in _rf and "run('tests/check_playcards.py', *(('--lenient',)" in _rf, 'refresh.py --unattended (or a .unattended file) runs playcards and its test in lenient mode')
print('failed:', len(fails))
sys.exit(1 if fails else 0)
