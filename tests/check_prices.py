"""Gate test de los precios (tiendas, estimaciones y pesos al dólar blue).  Sin red.  Run from the project root:  python tests/check_prices.py

  * tools/prices.py: el precio de otra tienda solo se usa cuando TCGplayer no tiene; Cardmarket se pasa a dólares; si no, la mediana de eBay, CoolStuffInc y Amazon;
    correrlo dos veces da lo mismo; un precio de 0,00 cuenta como «sin precio».
  * Los datos generados: dólar blue y euro en data/index.js, 5 precios por carta en el detalle, y todas las cartas con algún precio (real, de otra tienda o estimado).
  * La página: pxTag / priceBlock / fArs hacen la cuenta en dólares y pesos, y el pie dice qué fuentes no están.
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, 'tools')
import prices

fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


# ---- tools/prices.py con datos de prueba ----
check(prices.store_price([1.5, 9, None, None, None], 1.1) is None, 'a card with a TCGplayer price keeps it (no other store is used)')
check(prices.store_price([None, 2.0, 5, 6, 7], 1.1) == 2.2, 'Cardmarket euros are converted to dollars first')
check(prices.store_price([None, None, 4.0, 6.0, 100.0], 1.1) == 6.0, 'without Cardmarket the median of eBay, CoolStuffInc and Amazon is used (an outlier does not move it)')
check(prices.store_price([None, None, None, None, None], 1.1) is None, 'no store has it: no price (tools/rushprice.py estimates it)')
rows = [['A', 'm', 0, 0, 0, 0, 0, 0, 0, 0.0], ['B', 'm', 0, 0, 0, 0, 0, 0, 0, 3.0], ['C', 'm', 0, 0, 0, 0, 0, 0, 16, 7.0], ['D', 'm', 0, 0, 0, 0, 0, 0, 0, -1]]
pr = {'A': [None, 1.0, None, None, None], 'B': [3.0, 1.0, None, None, None], 'C': [None, 2.0, None, None, None], 'D': [None, None, None, None, None]}
n1 = prices.apply(rows, pr, 1.2)
snap = json.dumps(rows)
n2 = prices.apply(rows, pr, 1.2)
check(n1 == n2 == 2 and json.dumps(rows) == snap, 'running prices.apply twice gives the same result')
check(rows[0][9] == 1.2 and rows[0][8] & 32, 'a 0,00 TCGplayer price is "no price": the Cardmarket one is used and flagged (32)')
check(rows[1][9] == 3.0 and not rows[1][8] & 32, 'a TCGplayer price is never replaced')
check(rows[2][9] == 2.4 and rows[2][8] & 32 and not rows[2][8] & 16, 'an old estimate is dropped when a store has a real price')
check(rows[3][9] == -1, 'a card no store lists stays without price for the estimate')

# ---- precio de cada versión: más bajo en venta, mercado, y mercado si el más bajo es de centavos ----
def vp(price, lowest, market):
    det = {'X': {'pn': [[1, 'EN001', 'C', price, 99, 0]]}}
    prices.version_prices(det, {'99': [market, lowest]})
    return det['X']['pn'][0][3], det['X']['pn'][0][5]


check(vp(0, 5.0, 8.0) == (5.0, 0), 'a version uses its lowest listing')
check(vp(0, None, 8.0) == (8.0, 1), 'no listings: the market price')
check(vp(0, 0.01, 0.49) == (0.49, 2), 'a lowest listing of 0.01 with a higher market price: the market price (source 2)')
check(vp(0, 0.02, 0.5) == (0.5, 2), 'the 0.02 limit is included')
check(vp(0, 0.03, 0.5) == (0.03, 0), 'above the limit the lowest listing stays')
check(vp(0, 0.01, 0.01) == (0.01, 0), 'if the market price is not higher there is nothing better to show')
check(vp(0, 0.01, None) == (0.01, 0), 'a cheap lowest listing with no market price is kept')
d2 = {'X': {'pn': [[1, 'EN001', 'C', 0, 99, 0]]}}
prices.version_prices(d2, {'99': [0.49, 0.01]})
check(prices.version_prices(d2, {'99': [0.49, 0.01]}) == 0, 'running it twice changes nothing')

# ---- datos generados ----
t = open('data/index.js', encoding='utf-8').read()
idx = json.loads(t[t.index(',') + 1:-2])
rws = idx['cards']
fx = idx.get('fx') or {}
check(fx.get('ars', 0) > 100 and fx.get('arsBuy', 0) > 100 and fx.get('eur', 0) > 0.5 and fx.get('date'), 'data/index.js carries the blue dollar (sell and buy) and the euro rate (%s)' % fx)
check(sum(1 for r in rws if r[9] > 0) == len(rws), 'every card has a price: real, from another store or estimated (%d cards)' % len(rws))
check(not any((r[8] & 16) and (r[8] & 32) for r in rws), 'a price is either estimated (16) or from another store (32), never both')
check(sum(1 for r in rws if r[8] & 32) > 100, 'cards without TCGplayer use another store (%d)' % sum(1 for r in rws if r[8] & 32))
c0 = open('data/c0.js', encoding='utf-8').read()
ps = [json.loads(m) for m in re.findall(r'"p":(\[[^\]]*\])', c0)]
check(len(ps) > 100 and all(len(p) == 5 for p in ps), 'each card detail has five store prices (TCGplayer, Cardmarket, eBay, CoolStuffInc, Amazon)')

# ---- la página ----
page = open('index.html', encoding='utf-8').read()
check(all(x in page for x in ('function pxTag(', 'function priceBlock(', 'function setFx(', 'function refreshFx(', 'dolarapi.com/v1/dolares/blue')), 'the page has the price helpers and asks for the blue dollar of the day')
check('Precios de las cartas' in page and 'TrollAndToad no publica una API de precios' in page, 'the footer says which sources are not available (TrollAndToad, last sold)')
core = re.search(r'const FXR=.*?function pxTag', page, re.S)
check(bool(core), 'FXR and the formatters are in index.html')
if core:
    code = core.group(0).rsplit('function pxTag', 1)[0]
    harness = r'''
const LOC = 'es-AR', render = () => {}; const esc = s => s;
%s
FXR.ars = 1575;
const out = [fArs(10) === '15.750', fUsd(9.5) === '9,50', fUsd(1234.5) === '1.235', nz('0.00') === 0 && nz('3.5') === 3.5 && nz(null) === 0];
FXR.ars = 0; out.push(setFx({ars: 0}) === undefined && FXR.ars === 0);
setFx({ars: 1600, date: '2026-10-27', src: 'x', eur: 1.2}); out.push(FXR.ars === 1600 && FXR.eur === 1.2);
console.log(JSON.stringify(out));
''' % code
    r = subprocess.run(['node', '-e', harness], capture_output=True, text=True, encoding='utf-8')
    try:
        res = json.loads(r.stdout.strip())
    except Exception:
        res = []
    labels = ['AR$ 15.750 for US$ 10 at 1575', 'US$ 9,50 with two decimals', 'US$ 1.235 without decimals from 100 up', 'nz reads "0.00", strings and null', 'setFx ignores an empty rate', 'setFx takes a new rate']
    check(len(res) == len(labels), 'node ran the price harness' + ('' if len(res) == len(labels) else ': ' + (r.stderr.strip().splitlines() or ['?'])[-1][:140]))
    for ok, lab in zip(res, labels):
        check(ok, 'price format: ' + lab)


# ---- precio de cada versión de la carta ----
check(isinstance(idx.get('vr'), dict) and len(idx['vr']) >= 5 and all(v['n'] >= 30 and v['k'] > 0 for v in idx['vr'].values()), 'data/index.js carries the typical price ratio of each rarity (only rarities with 30+ samples)')
vp = re.search(r'function verPrice\(n,d,p\)\{.*?' + chr(10) + r'\}' + chr(10), page, re.S)
check(bool(vp) and 'pxVer(' in page and 'verPrice(n,d,p)' in page, 'versions and the sets table use verPrice / pxVer')
if vp:
    harness = r'''
const nz = x => { x = Number(x); return x > 0 ? x : 0; };
const C = {PR: 8}; const DBINFO = {vr: {C: {n: 100, k: 9}, UR: {n: 100, k: 11}, ScR: {n: 100, k: 15}}};
const order = ['C', 'R', 'SR', 'UR', 'ScR', 'StR'];
const rarRank = (r) => order.indexOf(r);
const CARDS = {X: [0,0,0,0,0,0,0,0,2.0], Y: [0,0,0,0,0,0,0,0,0]};
__CODE__
const mk = (...rows) => ({pn: rows});
const t = [];
let d = mk([1,'a','C',5], [2,'b','UR',20], [3,'c','C',0]);
t.push(verPrice('X', d, d.pn[0]).est === 0 && verPrice('X', d, d.pn[0]).u === 5);
t.push(verPrice('X', d, d.pn[2]).u === 5 && verPrice('X', d, d.pn[2]).why === 'rar');
d = mk([1,'a','C',5], [2,'b','UR',20], [3,'c','ScR',0]);
const v3 = verPrice('X', d, d.pn[2]); t.push(v3.u === 20 && v3.why === 'near' && v3.est === 1);
d = mk([1,'a','R',10], [2,'b','StR',0]);
t.push(verPrice('X', d, d.pn[1]).u === 10 && verPrice('X', d, d.pn[1]).why === 'near');
d = mk([1,'a','C',0], [2,'b','UR',0]);
const v5 = verPrice('X', d, d.pn[1]); t.push(v5.why === 'card' && Math.abs(v5.u - 22) < 1e-9);
t.push(verPrice('Y', d, d.pn[0]) === null);
d = mk([1,'a','C',4], [2,'b','C',6], [3,'c','C',0]);
t.push(verPrice('X', d, d.pn[2]).u === 5);
console.log(JSON.stringify(t));
'''.replace('__CODE__', vp.group(0))
    r = subprocess.run(['node', '-e', harness], capture_output=True, text=True, encoding='utf-8')
    try:
        res = json.loads(r.stdout.strip())
    except Exception:
        res = []
    labels = ['a version with its own price keeps it', 'no price: the median of the same rarity of that card', 'no same rarity: the closest rarity of that card',
              'closest rarity picks the nearest one, not the cheapest', 'no priced version at all: card price x what that rarity usually sells for',
              'no card price either: no estimate', 'the median of an even number of same-rarity versions']
    check(len(res) == len(labels), 'node ran the version price harness' + ('' if len(res) == len(labels) else ': ' + (r.stderr.strip().splitlines() or ['?'])[-1][:140]))
    for ok, lab in zip(res, labels):
        check(ok, 'version price: ' + lab)

print('failed:', len(fails))
sys.exit(1 if fails else 0)
