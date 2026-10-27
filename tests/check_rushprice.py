"""Gate test: every card on the page has a price (TCGplayer, Yuyu-tei or an estimate marked with ≈), and each kind of price is where it belongs. No network.
Run from the project root after tools/rushprice.py:  python tests/check_rushprice.py"""
import json, os, re, sys
sys.path.insert(0, 'tools')
import rushprice as rp

fails = []
def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c: fails.append(m)

def load(p):
    t = open(p, encoding='utf-8').read()
    return json.loads(t[t.index(',') + 1:-2])

rows = load('data/index.js')['cards']
det = {}
for f in os.listdir('data'):
    if re.fullmatch(r'c[0-9]+\.js', f):
        det.update(load('data/' + f))
fx = json.load(open('src/fx.json'))
est = [r for r in rows if r[8] & rp.FLAG_EST]
yuyu = [r for r in rows if (det.get(r[0]) or {}).get('pj', {}).get('k') == 'yuyu']
check(all(r[9] >= 0 for r in rows), f'all {len(rows)} cards have a price')
check(len(yuyu) > 1000 and len(est) > 500, f'{len(yuyu)} Rush cards priced from Yuyu-tei, {len(est)} estimated')
check(all((det[r[0]].get('pj') or {}).get('k') == 'est' for r in est), 'every estimate carries its basis (pj.k = est)')
check(all(abs(det[r[0]]['pj']['usd'] - r[9]) < 0.005 for r in yuyu + est), 'the price shown is the one of the detail')
check(all(abs(det[r[0]]['pj']['jpy'] * fx['JPY_USD'] - r[9]) < 0.01 for r in yuyu), 'Yuyu-tei prices are yen x the rate of the day')
store = json.load(open('src/prices.json', encoding='utf-8'))
has_tcg = lambda n: bool((store.get(n) or [None])[0])
check(not [r for r in rows if r[8] & 1 and has_tcg(r[0]) and (det[r[0]].get('pj') or r[8] & (rp.FLAG_EST | 32))], 'cards that exist in the TCG and have a TCGplayer price keep it (no Yuyu-tei, other store or estimate)')
check(not [r for r in rows if r[8] & 1 and r[8] & rp.FLAG_EST and any((store.get(r[0]) or []))], 'a TCG card is only estimated when no store lists it (otherwise it uses the price of another store)')

check(rp.best_listings([{'ja': 'ＡＢＣ', 'jpy': 500, 'stock': 0}, {'ja': 'abc', 'jpy': 900, 'stock': 2}, {'ja': 'abc', 'jpy': 700, 'stock': 3}], {'abc': 'ABC'})['ABC']['jpy'] == 700, 'the cheapest listing in stock wins')
print('failed:', len(fails)); sys.exit(1 if fails else 0)
