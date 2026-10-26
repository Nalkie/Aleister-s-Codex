"""Gate test for the ticket sources in Cajas y sets > Duel Links > Otras vías (data/sets-dl.js) and in each card's detail (data/c<N>.js).
Run from the project root after tools/tickets.py: python tests/check_tickets.py. Deterministic, no network."""
import collections, json, os, re, sys
sys.path.insert(0, 'tools')
import tickets

fails = []
def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c: fails.append(m)

def load(path):
    t = open(path, encoding='utf-8').read()
    return json.loads(t[t.index(',') + 1:-2])

sets_dl = load('data/sets-dl.js')
idx = load('data/index.js')['cards']
names = [r[0] for r in idx]
sets = json.load(open('src/dl_sets.json', encoding='utf-8'))
raw = json.load(open('src/dl_cards.json', encoding='utf-8'))
bynm = collections.defaultdict(list)   # one name can be both a Speed and a Rush card
for c in raw:
    bynm[c['n']].append(c)
box = {x['name']: x for x in sets}
src = {(s['n'], bool(s['rush'])): [names[k[0]] for k in s['k']] for s in sets_dl if s['kind'] == 'other'}
S = lambda n, rush=False: src.get((n, rush), [])

check(not tabs_exist if (tabs_exist := os.path.exists('data/tickets.js')) else True, 'there is no separate Tickets data file: tickets live in Otras vías')
check(all(len(S(f'Dream {r} Ticket', rush)) > 100 for r in ('UR', 'SR') for rush in (False, True)), 'Dream UR and SR have more than 100 cards in Speed and in Rush')
check(all(len(S(f'{r} Ticket · cartas farmeables', rush)) > 20 for r in ('UR', 'SR', 'R') for rush in (False, True)), 'farmable UR, SR and R tickets have more than 20 cards in Speed and in Rush')
check(not [k for k in src if k[0] in tickets.STALE], 'the stale "Acquirable with ... Tickets" lists are gone')
check(all(n in names for l in src.values() for n in l), 'every card of a ticket source is in the page index')
def rar(n, r): return any(c['r'] == r for c in bynm[n])
check(all(rar(n, k[0].split()[1] if k[0].startswith('Dream') else k[0].split()[0]) for k, l in src.items() if k[0] in {s[0] for s in tickets.SOURCES} for n in l), 'every card has the rarity of its ticket')
cutS, cutR = box[tickets.DREAM_SPEED_UNTIL]['release'][:10], box[tickets.DREAM_RUSH_UNTIL]['release'][:10]
def firstbox(c, rush): return min(((box[o[1]].get('release') or '9')[:10] for o in c['ob'] or [] if o[0] == 'sets' and o[1] in box and bool(box[o[1]].get('rush')) == rush), default='9')
check((cutS, cutR) == ('2025-11-25', '2026-05-11'), 'cut-offs: Predator of the Abyss 2025-11-25 and Eternal Genesis 2026-05-11')
check(all(any(firstbox(c, rush) <= (cutR if rush else cutS) for c in bynm[n]) for (k, rush), l in src.items() if k.startswith('Dream') for n in l), 'no Dream card first came in a box after its cut-off')
check(all(any((c.get('rel') or '9') <= tickets.FARM_UNTIL for c in bynm[n]) for (k, rush), l in src.items() if 'farmeables' in k for n in l), 'no farmable card is newer than 2026-05-11')
rushonly = {n for n, cs in bynm.items() if all(c.get('rush') for c in cs)}
check(not set(S('Dream UR Ticket')) & rushonly, 'the Speed Dream pool holds no Rush-only card')
out, _ = tickets.pools(sets, raw, set(names))
check(all(sorted(S(k, r)) == sorted(v) for (k, r), v in out.items()), 'the page lists match what tools/tickets.py builds now')
det = {}
for f in os.listdir('data'):
    if re.fullmatch(r'c\d+\.js', f):
        det.update(load('data/' + f))
n0 = S('Dream UR Ticket')[0]
check(any(o[0] == 'o' and o[1] == 'Dream UR Ticket' for o in det[n0]['dl']['ob']), f'{n0}: its detail lists the Dream UR Ticket as a way to get it')
check(not any(o[1] in tickets.STALE for d in det.values() if d.get('dl') for o in d['dl']['ob']), 'no card detail still lists a stale ticket source')
print('failed:', len(fails)); sys.exit(1 if fails else 0)
