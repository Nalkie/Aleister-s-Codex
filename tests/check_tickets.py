"""Gate test for data/tickets.js (Dream and normal tickets). Run from the project root after tools/tickets.py: python tests/check_tickets.py. Deterministic, no network."""
import json, sys
sys.path.insert(0, 'tools')
import tickets

fails = []
def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c: fails.append(m)

txt = open('data/tickets.js', encoding='utf-8').read()
d = json.loads(txt[txt.index(',') + 1:-2])
sets = json.load(open('src/dl_sets.json', encoding='utf-8'))
import collections
rawcards = json.load(open('src/dl_cards.json', encoding='utf-8'))
bynm = collections.defaultdict(list)   # one name can be both a Speed and a Rush card
for c in rawcards:
    bynm[c['n']].append(c)
box = {x['name']: x for x in sets}
idx = open('data/index.js', encoding='utf-8').read()
names = {r[0] for r in json.loads(idx[idx.index(',') + 1:-2])['cards']}

check(d['cuts']['speed'] == '2025-11-25' and d['cuts']['rush'] == '2026-05-11' and d['cuts']['farm'] == '2026-05-11', 'cut-offs: Predator of the Abyss (2025-11-25), Eternal Genesis and farmable cards (2026-05-11)')
check(all(len(d['dream'][m][r]) > 100 for m in ('speed', 'rush') for r in ('UR', 'SR')), 'every Dream pool has more than 100 cards')
check(all(len(d['farm'][m][r]) > 20 for m in ('speed', 'rush') for r in ('UR', 'SR', 'R')), 'every normal ticket pool has more than 20 cards')
check(all(n in names for k in ('dream', 'farm') for m in d[k].values() for l in m.values() for n in l), 'every card in a pool is in the page index')
def firstbox(c, rush):
    return min(((box[o[1]].get('release') or '9')[:10] for o in c['ob'] or [] if o[0] == 'sets' and o[1] in box and bool(box[o[1]].get('rush')) == rush), default='9')
check(all(any(c['r'] == r for c in bynm[n]) for k in ('dream', 'farm') for m in d[k].values() for r, l in m.items() for n in l), 'every card has the rarity of its pool')
check(all(any(firstbox(c, m == 'rush') <= d['cuts'][m] for c in bynm[n]) for m in ('speed', 'rush') for l in d['dream'][m].values() for n in l), 'no Dream card first came in a box after the cut-off')
check(all(any((c.get('rel') or '9') <= '2026-05-11' for c in bynm[n]) for m in d['farm'].values() for l in m.values() for n in l), 'no farmable card is newer than 2026-05-11')
rushnames = {n for n, cs in bynm.items() if all(c.get('rush') for c in cs)}
check(not set(d['dream']['speed']['UR']) & rushnames, 'Speed Dream pool holds no Rush-only card')
newer = [n for n, cs in bynm.items() if n in names and all(c['r'] == 'UR' and not c.get('rush') and firstbox(c, False) > d['cuts']['speed'] for c in cs)]
check(newer and not set(newer) & set(d['dream']['speed']['UR']), f'{len(newer)} Speed UR cards with no box up to Predator of the Abyss are left out')
out = tickets.build(sets, rawcards, names)
check(out == d, 'data/tickets.js matches what tools/tickets.py builds now')
print('failed:', len(fails)); sys.exit(1 if fails else 0)
