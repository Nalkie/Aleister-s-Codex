"""What the exchange tickets can get, inside "Cajas y sets > Duel Links > Otras vías" (data/sets-dl.js) and in each card's "cómo conseguirla" (data/c<N>.js).
Run from the project root after tools/build_db.py and tools/dltext.py:  python tools/tickets.py   (running it twice changes nothing)
  Dream UR / Dream SR (Speed Duel): UR / SR cards that come in a box released up to DREAM_SPEED_UNTIL
  Dream UR / Dream SR (Rush Duel):  same, Rush boxes up to DREAM_RUSH_UNTIL
  UR / SR / R tickets (cartas farmeables): cards that can be farmed (character levels, Gate drops, character decks, events, missions, Card Trader...)
                       released up to FARM_UNTIL; Speed and Rush apart. They replace Duel Links Meta's own "Acquirable with ... Tickets" lists, which stop in 2022.
The cut-offs are the game's rule as given by the project owner, not something the sources publish: change them here when the game moves them.
The dates of the boxes come from Duel Links Meta (src/dl_sets.json), the sources of each card from src/dl_cards.json."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DREAM_SPEED_UNTIL = 'Predator of the Abyss'
DREAM_RUSH_UNTIL = 'Eternal Genesis'
FARM_UNTIL = '2026-05-11'
FARM_KINDS = ('characters', 'otherSources')
STALE = ('Acquirable with Tickets', 'Acquirable with SR Tickets', 'Acquirable with UR Tickets')   # superseded by the farmable pools
SOURCES = [('Dream UR Ticket', 'dream', 'UR'), ('Dream SR Ticket', 'dream', 'SR'), ('UR Ticket · cartas farmeables', 'farm', 'UR'),
           ('SR Ticket · cartas farmeables', 'farm', 'SR'), ('R Ticket · cartas farmeables', 'farm', 'R')]


def pools(sets, cards, names):
    """{(source name, rush): [card names, newest first]}"""
    box = {s['name']: s for s in sets}
    cut = {False: box[DREAM_SPEED_UNTIL]['release'][:10], True: box[DREAM_RUSH_UNTIL]['release'][:10]}
    out = {(n, rush): [] for n, _, _ in SOURCES for rush in (False, True)}
    for c in sorted(cards, key=lambda c: (c.get('rel') or '', c['n']), reverse=True):
        n, r = c['n'], c.get('r')
        if n not in names or r not in ('UR', 'SR', 'R'):
            continue
        ob = c.get('ob') or []
        for rush in (False, True):
            if r in ('UR', 'SR') and any(o[0] == 'sets' and o[1] in box and bool(box[o[1]].get('rush')) == rush
                                          and (box[o[1]].get('release') or '9')[:10] <= cut[rush] for o in ob):
                out[('Dream %s Ticket' % r, rush)].append(n)
        rush = bool(c.get('rush'))
        if (c.get('rel') or '9') <= FARM_UNTIL and any(o[0] in FARM_KINDS for o in ob):
            out[('%s Ticket · cartas farmeables' % r, rush)].append(n)
    return out, cut


def load(path):
    t = open(path, encoding='utf-8').read()
    head = t[:t.index(',') + 1]
    return head, json.loads(t[len(head):-2])


def save(path, head, obj):
    open(path, 'w', encoding='utf-8').write(head + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + ');')


def apply_sets(sets_dl, pool, pos):
    """Replace the stale and previous ticket entries of the list of sources with the current ones."""
    ours = {n for n, _, _ in SOURCES}
    keep = [s for s in sets_dl if not (s['kind'] == 'other' and (s['n'] in STALE or s['n'] in ours))]
    new = [{'n': n, 'kind': 'other', 't': 'Otra vía', 'rel': '', 'k': [[pos[c], 1] for c in pool[(n, rush)]], 'rush': rush}
           for n, _, _ in SOURCES for rush in (False, True) if pool[(n, rush)]]
    return keep + new


def apply_details(det, pool):
    """Add the ticket sources to each card's way to get it, and drop the stale ones."""
    ours = {n for n, _, _ in SOURCES}
    mine = {}
    for (n, rush), cs in pool.items():
        for c in cs:
            mine.setdefault((c, rush), []).append(n)
    for name, d in det.items():
        dl = d.get('dl')
        if not dl:
            continue
        ob = [o for o in dl['ob'] if not (o[0] == 'o' and (o[1] in STALE or o[1] in ours))]
        ob += [['o', n, '', 1, ''] for n in mine.get((name, bool(dl.get('rush'))), [])]
        dl['ob'] = ob


if __name__ == '__main__':
    os.chdir(ROOT)
    idx = open('data/index.js', encoding='utf-8').read()
    names = [r[0] for r in json.loads(idx[idx.index(',') + 1:-2])['cards']]
    pos = {n: i for i, n in enumerate(names)}
    pool, cut = pools(json.load(open('src/dl_sets.json', encoding='utf-8')), json.load(open('src/dl_cards.json', encoding='utf-8')), set(names))
    head, sets_dl = load('data/sets-dl.js')
    save('data/sets-dl.js', head, apply_sets(sets_dl, pool, pos))
    for f in sorted(x for x in os.listdir('data') if re.fullmatch(r'c\d+\.js', x)):
        head, det = load('data/' + f)
        apply_details(det, pool)
        save('data/' + f, head, det)
    if os.path.exists('data/tickets.js'):
        os.remove('data/tickets.js')
    print('Dream Speed until', DREAM_SPEED_UNTIL, cut[False], '· Dream Rush until', DREAM_RUSH_UNTIL, cut[True], '· farmable until', FARM_UNTIL)
    print({f'{n}{" (Rush)" if r else ""}': len(v) for (n, r), v in pool.items() if v})
