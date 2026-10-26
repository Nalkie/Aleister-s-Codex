"""Price for every card that has none: Rush Duel cards from the Yuyu-tei listings, the rest estimated. Edits data/index.js (price column + flag 16 = estimate) and the
card details (data/c<N>.js, field "pj"). Run from the project root after tools/build_db.py, tools/dltext.py and tools/fetch_rush_prices.py:  python tools/rushprice.py
Running it twice changes nothing.
  yuyu : Rush cards found in src/yuyutei_rush.json, matched through the Japanese -> English names of Yugipedia. The price is the cheapest listing of the card
         (in stock first), in yen, converted to dollars with the day's rate. It is the shop's selling price, not a market average or a last sale.
  est  : cards with no price at all (Rush cards the shop does not list, Duel Links cards that were never in the TCG): the median price of the cards with the same
         Duel Links rarity that do have one (Rush with Rush, the rest with the TCG). Shown with "≈" and its basis."""
import json, os, re, statistics, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from fetch_rush_prices import norm

FLAG_EST = 16
PRICE, FLAGS, DLRAR, DLID = 9, 8, 12, 11


def load(path):
    t = open(path, encoding='utf-8').read()
    head = t[:t.index(',') + 1]
    return head, json.loads(t[len(head):-2])


def save(path, head, obj):
    open(path, 'w', encoding='utf-8').write(head + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + ');')


def best_listings(listings, names):
    """{English name: cheapest listing} (listings in stock win over sold-out ones)."""
    best = {}
    for l in listings:
        en = names.get(norm(l['ja']))
        if not en:
            continue
        k = (l['stock'] <= 0, l['jpy'])
        if en not in best or k < best[en][0]:
            best[en] = (k, l)
    return {en: v[1] for en, v in best.items()}


def plan(rows, rush_names, best, rate, dl_rush):
    """rows: index rows. Returns {row index: (price usd, 'yuyu'|'est', detail dict)}."""
    out, by_rar = {}, {}
    for i, r in enumerate(rows):
        if r[PRICE] >= 0:
            by_rar.setdefault((False, r[DLRAR]), []).append(r[PRICE])
    for i, r in enumerate(rows):
        n = r[0]
        if r[PRICE] < 0 and n in best and n in rush_names:   # a card that also exists in the TCG keeps its TCGplayer price
            l = best[n]
            usd = round(l['jpy'] * rate, 2)
            out[i] = (usd, 'yuyu', {'k': 'yuyu', 'jpy': l['jpy'], 'usd': usd, 'no': l['no'], 'rar': l['rar'], 'url': l['url'], 'stock': l['stock']})
    for i, (usd, k, d) in out.items():
        by_rar.setdefault((True, rows[i][DLRAR]), []).append(usd)
    for i, r in enumerate(rows):
        if i in out or r[PRICE] >= 0 or not (r[FLAGS] & (2 | 4)):
            continue
        rush = bool(r[FLAGS] & 4)
        pool = by_rar.get((rush, r[DLRAR])) or by_rar.get((False, r[DLRAR])) or []
        if not pool:
            continue
        usd = round(statistics.median(pool), 2)
        out[i] = (usd, 'est', {'k': 'est', 'usd': usd, 'rar': r[DLRAR] or '?', 'rush': rush, 'n': len(pool)})
    by_cat = {}
    for i, r in enumerate(rows):
        if r[PRICE] >= 0 and not (r[FLAGS] & FLAG_EST) and i not in out:
            by_cat.setdefault(r[1], []).append(r[PRICE])
    for i, r in enumerate(rows):   # no rarity either (cards that exist only in the OCG): the median of the TCG cards of the same kind
        if i in out or r[PRICE] >= 0 or not by_cat.get(r[1]):
            continue
        usd = round(statistics.median(by_cat[r[1]]), 2)
        out[i] = (usd, 'est', {'k': 'est', 'usd': usd, 'cat': r[1], 'n': len(by_cat[r[1]])})
    return out


if __name__ == '__main__':
    os.chdir(ROOT)
    listings = json.load(open('src/yuyutei_rush.json', encoding='utf-8'))
    names = json.load(open('src/rush_names.json', encoding='utf-8'))
    fx = json.load(open('src/fx.json'))
    dl = json.load(open('src/dl_cards.json', encoding='utf-8'))
    rush_names = {c['n'] for c in dl if c.get('rush')}
    best = best_listings(listings, names)
    hi, idx = load('data/index.js')
    rows = idx['cards']
    for r in rows:   # start from the TCGplayer state so a second run gives the same result: Rush prices and estimates are always recomputed
        if r[FLAGS] & (FLAG_EST | 4):
            r[PRICE], r[FLAGS] = -1, r[FLAGS] & ~FLAG_EST
    out = plan(rows, rush_names, best, fx['JPY_USD'], None)
    for i, (usd, k, d) in out.items():
        rows[i][PRICE] = usd
        if k == 'est':
            rows[i][FLAGS] |= FLAG_EST
    save('data/index.js', hi, idx)
    pos = {r[0]: i for i, r in enumerate(rows)}
    import collections
    for f in sorted(x for x in os.listdir('data') if re.fullmatch(r'c\d+\.js', x)):
        head, det = load('data/' + f)
        ch = False
        for name, d in det.items():
            i = pos.get(name)
            new = out[i][2] if i in out else None
            if new:
                new = dict(new, rate=fx['JPY_USD'], date=fx['date'])
            if d.get('pj') != new:
                if new: d['pj'] = new
                else: d.pop('pj', None)
                ch = True
        if ch:
            save('data/' + f, head, det)
    c = collections.Counter(v[1] for v in out.values())
    print('prices added:', dict(c), '· Rush cards:', len(rush_names), '· still without price:', sum(1 for r in rows if r[PRICE] < 0))
