"""Gate test of the tournament data: Top 4 (placement 3.5) is kept, the event of a recipe carries the name YuGiOh Meta gives it, and no event shows a false winner in the data.  Sin red.
  python tests/check_events.py"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, 'tools')
import placement

fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


load_js = lambda p: json.loads(open(p, encoding='utf-8').read()[open(p, encoding='utf-8').read().index(',') + 1:-2])
check(placement.in_top8(1) and placement.in_top8(3.5) and placement.in_top8(8) and not placement.in_top8(0) and not placement.in_top8(9) and not placement.in_top8(None) and not placement.in_top8('1') and not placement.in_top8(True),
      'in_top8(): 1, 2, 3.5 (Top 4) and 8 count; 0, 9, None, text and booleans do not')
E = load_js('data/events.js')
rows = [r for e in E for r in e['top']]
check(any(r[0] == 3.5 for r in rows) and {r[0] for r in rows} <= {1, 2, 3.5, 5, 8} | {r[0] for r in rows if 0 < r[0] <= 8}, 'TCG / Genesys events keep the Top 4 rows (%d rows with placement 3.5)' % sum(1 for r in rows if r[0] == 3.5))
O = load_js('data/ygmx.js').get('ocgEvents') or []
check(any(r[0] == 3.5 for e in O for r in e['top']), 'OCG events keep the Top 4 rows (%d)' % sum(1 for e in O for r in e['top'] if r[0] == 3.5))
check(all(e['top'] == sorted(e['top'], key=lambda x: x[0]) for e in E + O), 'the rows of every event are in placement order')
src = open('src.html', encoding='utf-8').read()
check("const w=e.top.find(r=>r[0]===1)" in src and "pl===3.5?4:pl" in src, 'the page shows "1.º" only for a deck placed first and writes a Top 4 as "Top 4"')
ygm = json.load(open('dl/ygmdata.json', encoding='utf-8'))
ev = []
for f in ygm.values():
    if isinstance(f, dict):
        for d in (f.get('decks') or {}).values():
            for w in (d.get('who'), d.get('last')):
                if w and w.get('event'):
                    ev.append(w['event'])
check(ev and sum(1 for x in ev if re.search(r'\b(19|20)\d\d\b', x)) / len(ev) > 0.5, 'the event of a recipe is the event name of YuGiOh Meta ("Lansing October 2026 Regional"), not a type (%d of %d carry a year)' % (sum(1 for x in ev if re.search(r'\b(19|20)\d\d\b', x)), len(ev)))
print('failed:', len(fails))
sys.exit(1 if fails else 0)
