"""Gate test del indicador «Precio del mazo» del Constructor.  Sin red.  Run from the project root:  python tests/check_deckprice.py

Outcome: el precio que ve el usuario es la suma correcta (copias x precio de la versión más barata en TCGplayer) y se actualiza con cada carta.
  * dkPrice() en node con cartas sintéticas: suma por copias, Main + Extra + Side, estimadas contadas aparte, sin precio contadas aparte, mazo vacío = 0
  * Con los datos reales (data/cards): un mazo real del ranking da un total parecido al «Valor aproximado» que muestra la receta
  * La página: el indicador está en el Constructor, no sale en Duel Links ni Master Duel, se traduce
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


src = open('src.html', encoding='utf-8').read()
m = re.search(r'function dkPrice\(\)\{.*?\n\}\n', src, re.S)
check(bool(m), 'dkPrice() is in src.html')
if m:
    harness = r'''
const SECS = ['main', 'extra', 'side'];
const C = {PR: 8, FL: 7};
const nz = x => { x = Number(x); return x > 0 ? x : 0; };
const ALIAS = {'Alias Card': 'Real Card'};
const canon = n => ALIAS[n] || n;
const mk = (pr, fl) => { const c = []; c[8] = pr; c[7] = fl || 0; return c; };
const CARDS = {'A': mk(10), 'B': mk(2.5), 'Est': mk(4, 16), 'Real Card': mk(7), 'NoPrice': mk(0)};
let DK = {main: {A: 3, B: 2}, extra: {}, side: {}};
%s
const t = [];
let p = dkPrice();
t.push(Math.abs(p.usd - 35) < 1e-9 && p.n === 5 && p.miss === 0 && p.est === 0);                       // 3x10 + 2x2.5
DK = {main: {A: 1}, extra: {B: 1}, side: {A: 2}};
p = dkPrice(); t.push(Math.abs(p.usd - 32.5) < 1e-9 && p.n === 4);                                      // Main + Extra + Side
DK = {main: {Est: 2, A: 1}, extra: {}, side: {}};
p = dkPrice(); t.push(Math.abs(p.usd - 18) < 1e-9 && p.est === 2 && p.miss === 0);                      // las estimadas suman y se cuentan
DK = {main: {NoPrice: 3, Missing: 1, A: 1}, extra: {}, side: {}};
p = dkPrice(); t.push(p.usd === 10 && p.miss === 4 && p.n === 5);                                       // sin precio: no suma, se cuenta
DK = {main: {'Alias Card': 2}, extra: {}, side: {}};
p = dkPrice(); t.push(p.usd === 14);                                                                    // alias de carta
DK = {main: {}, extra: {}, side: {}};
p = dkPrice(); t.push(p.usd === 0 && p.n === 0);
DK = {main: {A: 3}, extra: {}, side: {}}; const before = dkPrice().usd;
DK.main.B = 1; t.push(Math.abs(dkPrice().usd - before - 2.5) < 1e-9);                                   // agregar una carta sube el total por su precio
console.log(JSON.stringify(t));
''' % m.group(0)
    r = subprocess.run(['node', '-e', harness], capture_output=True, text=True, encoding='utf-8')
    try:
        res = json.loads(r.stdout.strip())
    except Exception:
        res = []
    labels = ['copies x price, summed', 'Main + Extra + Side all count', 'estimated cards add up and are counted apart', 'cards with no price add nothing and are counted',
              'a card alias takes the real card price', 'an empty deck costs 0', 'adding a card raises the total by its price']
    check(len(res) == len(labels), 'node ran the price harness' + ('' if len(res) == len(labels) else ': ' + (r.stderr.strip().splitlines() or ['?'])[-1][:200]))
    for ok, lab in zip(res, labels):
        check(ok, 'price: ' + lab)

check("rstat('Precio del mazo'" in src and 'dkprice' in src and 'pxOn=!dl&&DK.fmt!==\'md\'' in src, 'the Constructor shows the price tile, not in Duel Links or Master Duel')
check('class="rnote dkpx"' in src and 'Sin precio:' in src and 'Estimadas con cartas parecidas' in src, 'the price note says what is missing or estimated')
en = json.load(open('tools/i18n_en.json', encoding='utf-8'))
check(en.get('Precio del mazo') == 'Deck price', 'the tile label is translated')
print('failed:', len(fails))
sys.exit(1 if fails else 0)
